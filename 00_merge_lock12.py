# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#this program takes Lock1 and Lock2 data, checks for outliers in each file and 
# merges all "clean" data in one single file)

#major updates list:
#2022-06-17
#It also calculates average frequency and short-term stability and cycle time from the actual data, storing them
# into a file called "prefix_SIGMA.dat". Keep "fixed_tau0 = True" if you want fixed cycle times
# otherwise in each file is calculated as from the the first 20 timestams

#2022-06-17
#found a bug, it was calculating sigma(1s) on data with outliers NOT removed!!!

#2022-07-01
#Elaborates data only if Mag file has at least 4 data
#It also calculates average TOF and TOF stability for each file, storing
#   the results into a file called "prefix_TOF.dat"
#Before I was taking TOF1 and TOF2 only from the left interrogation now I take
#   TOF1 = (TOF1(left)+TOF1(right))/2    TOF2 = (TOF2(left)+TOF2(right))/2



fixed_tau0 = False
show_plot = False

lock1 = True  #put False if measurement are done only in lock2
lock2 = False  #put False if measurement are done only in lock1

tau0 = [2.45, 2.85]

# import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
# import os
from datetime import datetime
from find_outliers import find_outliers

from calc_sig1s import sig1s
from calc_TOF import TOFm

#remove outliers?
rem_out = 'True'

#import files list (one file each day)
files_list = []

cwd = Path.cwd() 
data_dir = cwd / 'raw_data'

for file in data_dir.iterdir():
    if file.name.endswith("Lock1.txt"):
        files_list.append(file.name) 
    if file.name.endswith("Lock2.txt"):
        files_list.append(file.name) 
    if file.name.endswith("Mag.txt"):
        files_list.append(file.name) 

#sort files
files_list.sort(key = lambda date: datetime.strptime(date[:16], '%Y-%m-%d_%H-%M'))

#find dates and prefixes    
days = []
prefixs = []

for file in files_list:
        day = file[:10]
        if file.endswith("Mag.txt"):
             prefix = file[:-7]
        else:
             prefix = file[:-9]
        #prefix = file[:32]
        days.append(day)
        prefixs.append(prefix)

#remove duplicates
days = list(dict.fromkeys(days))  
prefixs = list(dict.fromkeys(prefixs))    


#merge data into a subfolder
subfolder = Path('01_merged_data')

try:
    subfolder.mkdir()
    print ('subfolder ' + subfolder.name  + ' created')    
except:
    print ('subfolder ' + subfolder.name  + ' already existed') 


elaborate_data = True  #this enables elaboration of Lock1 and lock2

for prefix in prefixs:
    
    #Copy Majorana data
    fname_m = prefix + 'Mag.dat'
    path_m = cwd / subfolder / fname_m   #path where magnetic data are copied

    if path_m.is_file():
        # print (prefix, 'Majorana data already copied')
        print ('...\n')
    else:        
        mag = data_dir / (prefix + 'Mag.txt')     #path to raw data 
        try:
            data = np.genfromtxt(mag, usecols=[0,1,2], skip_header=12, skip_footer=0)  
            if np.size(data)==0:
                print ('!!!  ', mag.name, ' is empty, not exported')
                elaborate_data = False
            elif np.size(data) < 12:   #checking that Mag file has at least 4 data
                print (np.size(data))
                print ('!!!  ', mag.name, 'has less than 4 data, data not exported')
                elaborate_data = False
            else: 
                elaborate_data = True  #this enables elaboration of Lock1 and lock2

                filo_m = open(path_m, 'w')
                header = '#MJD \t nu \t sig_nu \n'
                np.savetxt(filo_m, data, delimiter='\t', header=header)
                print (path_m.name,  '   created')
                filo_m.close()
        except: 
            print(mag, ' missing !!!!!!!!!')
            raise

    
    
    #Merge Lock1 and Lock2 data
    if elaborate_data:
        
        fname = prefix + 'ALL.dat'
        fname_sig = prefix + 'SIGMA.dat'
        fname_tof = prefix + 'TOF.dat'
        path = cwd / subfolder / fname 
        path_sig = cwd / subfolder / fname_sig
        path_tof = cwd / subfolder / fname_tof
    
        if path.is_file():
            #print (prefix, 'Lock data already merged')
            print ('...\n')
        else:
            if lock1:
                lock1 = data_dir / (prefix + 'Lock1.txt')
                try:
                    data = np.genfromtxt(lock1, usecols=[0,1,4,5,7,8], skip_header=15, comments='**')  
                    if np.size(data)==0:   #checking that file data is not empty
                        print ('!!!  ', lock1.name, ' is empty, not exported')                  
                    else:
                        #remove outliers
                        if rem_out:                
                            nu = data[:,1]
                            out_i = find_outliers(nu)
                            data = np.delete(data, out_i, 0)
                            filoo = open('outliers.txt', 'a')
                            string1 = '!!!!! in ' + prefix + 'Lock1   '
                            string2 = str(len(out_i)) + ' outliers removed' + '\n'
                            filoo.write('#'+string1+string2)
                            print (string1)
                            print (string2)
                            filoo.close()
                        #average TOF left and right
                        TOF1_L=data[:,2]
                        TOF2_L=data[:,3]
                        TOF1_R=data[:,4]
                        TOF2_R=data[:,5]
                        TOF1 = (TOF1_L + TOF1_R)/2
                        TOF2 = (TOF2_L + TOF2_R)/2
                        data[:,2] = TOF1   #I substitute TOF left with avg TOF 
                        data[:,3] = TOF2   #I substitute TOF left with avg TOF
                        #export data into new file                  
                        filo = open(path, 'w')
                        nl = '\t' + str(1) + '\t' + '\n'
                        header = '#MJD \t nu \t (T0F1(left)+TOF1(right)/2 \t (T0F2(left)+TOF2(right)/2 \n'
                        # print(len(data[:,1]))
                        np.savetxt(filo, data[:,:4], newline=nl, delimiter='\t', header=header)
                        filo.close()
                        
                        #calculate y avg and sig_y(1s) 
                        t = data[:,0]
                        nu = data[:,1]
                        if fixed_tau0:
                            Tc, ym, sig_1s = sig1s(t, nu, lock1.name, tau0[0], show_plot=show_plot)
                        else:
                            Tc, ym, sig_1s = sig1s(t, nu, lock1.name, tau0[0], show_plot=show_plot, calculate_tau0=True)
                        
                        #calculate sig_y
                        Ty = Tc *len(nu) #measurement time
                        sig_y = sig_1s*Ty**-0.5  #sig_y(Ty)
                        
                        #calculate MJD_medio
                        MJDm = (t[0] + t[-1])/2
                        
                        #calculate TOF medio medio (sum of TOF1 and TOF2) and its uncertainty
                        avgTOF1, sig_TOF1 = TOFm(t, TOF1, Tc)  #!!!!!!OSS: it uses the same cycle time as y, fixed or not
                        avgTOF2, sig_TOF2 = TOFm(t, TOF2, Tc)
                        avgTOF = avgTOF1 + avgTOF2
                        sig_TOF = np.sqrt(sig_TOF1**2 + sig_TOF2**2)
    
                        #export avg MJD, avg y and stability data into new file
                        filo = open(path_sig, 'w')
                        header = '#MJD medio, Tc/s, y_avg, sigma_y(1s), sig_y(T)\n #first row = lock1 \n #second row = lock2 \n'
                        filo.write(header)
                        filo.write(str(MJDm) + '\t' + str(Tc) + '\t' + str(ym) + '\t' +  str(sig_1s) + '\t' +  str(sig_y) + '\n')
                        filo.close()
                       
                        #export TOF and its stability data into new file
                        filo = open(path_tof, 'w')
                        header = '#TOFmedio, sigma_TOF \n #first row = lock1 \n #second row = lock2 \n'
                        filo.write(header)
                        filo.write( str(avgTOF) + '\t' + str(sig_TOF) + '\n' )
                        filo.close()
                        
                except: 
                    print(lock1, ' missing !!!!!!!!!')
                    print ('!!!!!!!!!!!!!!!1')
                    raise
            
            if lock2:
                lock2 = data_dir / (prefix + 'Lock2.txt')
                try:
                    data = np.genfromtxt(lock2, usecols=[0,1,4,5,7,8], skip_header=15, comments='**')  
                    if np.size(data)==0:
                        print ('!!!  ', lock2.name, ' is empty, not exported')
                    elif lock2==False:
                            print ('\n!!!  not differential, lock1 data not exported !!!!')  
                    else:
                        #remove outliers
                        if rem_out:                
                            nu = data[:,1]
                            out_i = find_outliers(nu)
                            data = np.delete(data, out_i, 0)
                            filoo = open('outliers.txt', 'a')
                            string1 = '!!!!! in ' + prefix+ 'Lock2   '
                            string2 = str(len(out_i)) + ' outliers removed' + '\n'
                            filoo.write('#'+string1+string2)
                            print (string1)
                            print (string2)
                            filoo.close()
    
                        #average TOF left and right
                        TOF1_L=data[:,2]
                        TOF2_L=data[:,3]
                        TOF1_R=data[:,4]
                        TOF2_R=data[:,5]
                        TOF1 = (TOF1_L + TOF1_R)/2
                        TOF2 = (TOF2_L + TOF2_R)/2
                        data[:,2] = TOF1   #I substitute TOF left with avg TOF 
                        data[:,3] = TOF2   #I substitute TOF left with avg TOF
                        
                        #export data into new file                  
                        filo = open(path, 'a')
                        nl = '\t' + str(2) + '\t' + '\n'
                        # print(len(data[:,1]))
                        np.savetxt(filo, data[:,:4], newline=nl, delimiter='\t')
                        print (path.name,  '   created')
                        filo.close()
                        
                        #calculate sigma 
                        t = data[:,0]
                        nu = data[:,1]
                        if fixed_tau0:
                            Tc, ym, sig_1s = sig1s(t, nu, lock2.name, tau0[1], show_plot=show_plot)
                        else:
                            Tc, ym, sig_1s = sig1s(t, nu, lock2.name, tau0[1], show_plot=show_plot, calculate_tau0=True)
                        
                        #calculate sig_y
                        Ty = Tc *len(nu) #measurement time
                        sig_y = sig_1s*Ty**-0.5  #sig_y(Ty)
                        
                        #calculate MJD_medio
                        MJDm = (t[0] + t[-1])/2                    
                        
                        #calculate TOF medio (sum of TOF1 and TOF2) and its uncertainty
                        avgTOF1, sig_TOF1 = TOFm(t, TOF1, Tc)
                        avgTOF2, sig_TOF2 = TOFm(t, TOF2, Tc)
                        avgTOF = avgTOF1 + avgTOF2
                        sig_TOF = np.sqrt(sig_TOF1**2 + sig_TOF2**2)
                        
                        #export MJD, stability data into new file
                        filo = open(path_sig, 'a')
                        filo.write(str(MJDm) + '\t' + str(Tc) + '\t' + str(ym) + '\t' +  str(sig_1s) + '\t' +  str(sig_y) + '\n')
                        filo.close()
                        print (path_sig.name,  '   created')
                        
                        #export TOF and its stability data into new file
                        filo = open(path_tof, 'a')
                        filo.write( str(avgTOF) + '\t' + str(sig_TOF) + '\t' )
                        filo.close()
                        print (path_tof.name,  '   created')
                        
                except: 
                    print(lock2, ' missing !!!!!!!!!')
                    raise
                

