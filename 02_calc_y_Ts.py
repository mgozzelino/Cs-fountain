# -*- coding: utf-8 -*-

###
#this program takes Lock1 and Lock2 data (already merged in one single file)
#takes short term stability, cycle times and k_coll (collisional coeff) as inputs to be inserted manually
#bins data with bin size Ts (usually Ts=864 s)
#it takes magnetic field data, interpolates them with sampling rate 1/Ts, and applies all sistematic corrections to the data

#major updates list:
#"01_calc_y_Ts" uses fixed sigma(1s) for HD and LD, for mixed bins it conservately assumes the stability in LD
#"01_calc_y_Ts_experimental" uses a weigthed uncertainty for bins with mixed "Lock1 and Lock2" data
#2022/06/15:
#"01_calc_y_Ts experimental1" takes sig_LD and sig_HD and cycle times from acual data, fitting the ADEV and differentiating timestamps
#2022/06/16:
#'Moved the flag from exported data to elaborated data
#2022/10/28

#'Added zeeman shift and TOF to the monitor data in folder "monitor"

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
# import os
from datetime import datetime
from bin_data_revSD import resample_F2
# from find_outliers import find_outliers


#update k_coll at each new_file?
rolling_k = False

#correct_PC_clock??
correction_PC_vecchio = False

#correct offset detection???
correction_TOF = False

scale_TF_LD = 1./1.22
scale_TF_HD = 1./1.3

#differential
differential = False  #put False if measurement are done only in HD

flag = 1


#soglia dead time
th = 0.5 #from 0 to 1. Default 0.5. If measurement_time < th*Ts discards the point

#New sampling rate
Ts = 0.01  #MJD (864s)
# Tc1, Tc2 = 2.41, 2.85   #cicle time in LD and HD /s

# sig_LD = 2.2e-13  #sig_y(1s) LD   (HD are weighted in the same manner)
# sig_HD = 2.1e-13  #sig_y(1s) LD   (HD are weighted in the same manner)

plt.close('all')

#parametri fissi
# shift_f = 257.75e-16    #gravity, microwave + BBR
shift_f = 253.0389E-16    #gravity, microwave + BBR   #updated after new evaluation of uW leakage (feb-mar 2023)



#magnetic field correction
def Majo(f_MAJO):
    k_MAJO = 1.987808    #coeff estimated from latest C-field map (03-feb-2023)
    shift_Z = (427.45e8/((7008400000)**2)*((f_MAJO*k_MAJO)**2)/9192631770)
    return shift_Z

Majo = np.vectorize(Majo)
#%%
cwd = Path.cwd()

#import hystorical collisional data
file_coll_in = 'collisional_hyst.dat'
coll0 = np.loadtxt(file_coll_in)    #MJD(last), k, sig_k, sum k_i*w_i, sum w_i

k_coll0 = coll0[1]
kiwi0 = coll0[3]
wi0 = coll0[4]

#if collisoinal already updated, load the latest estimate
file_coll_out = 'collisional_updated.dat'
coll = np.loadtxt(file_coll_out)    #MJD(last), k, sig_k, sum k_i*w_i, sum w_i

k_coll = coll[1]
sig_k = coll[2]
#%%
#import files list (one file each day)

#data folder
data_folder = cwd / '01_merged_data'

files_list = []

for file in data_folder.iterdir():
    if file.name.endswith("ALL.dat"):
        files_list.append(file.name) 
    if file.name.endswith("Mag.dat"):
        files_list.append(file.name) 
    if file.name.endswith("SIGMA.dat"):
        files_list.append(file.name) 
        
#sort files
files_list.sort(key = lambda date: datetime.strptime(date[:16], '%Y-%m-%d_%H-%M'))

#find dates and prefixes    
days = []
prefixs = []

for file in files_list:
    if file.endswith("Mag.dat"):
        prefix = file[:-7]
        day = file[:10]
        days.append(day)
        prefixs.append(prefix)

#remove duplicates
days = list(dict.fromkeys(days))  
prefixs = list(dict.fromkeys(prefixs))    


#subfolder where elaborated data are saved 
subfolder = Path('00_elaborated_data')
sub_subfolder = Path('monitor')
sub_subfolder1 = Path('confronto')
path = subfolder / sub_subfolder
path1 = subfolder / sub_subfolder1

try:
    subfolder.mkdir()
    print ('subfolder ' + subfolder.name  +  ' created')    
except:
    print ('subfolder ' + subfolder.name  +  ' already existed \n') 
    
try:
    path.mkdir()
    print ('subfolder ' + path.name +  ' created')    
except:
    print ('subfolder ' + path.name + ' already existed \n') 
    
try:
    path1.mkdir()
    print ('subfolder ' + path1.name +  ' created')    
except:
    print ('subfolder ' + path1.name + ' already existed \n') 
        
for prefix in prefixs:
    
    #check if output file already exists
    fname = prefix + 'elab.dat'
    fname1 = prefix + 'confronto.dat'
    filepath = path / fname
    filepath1 = path1 / fname1
    
    if filepath.is_file() and filepath1.is_file():
        print (prefix, ' data already elaborated \n')
        print('...\n')
    else:
        print (fname)

        #import freq data (Lock1 and Lock2 already merged)
        fdata =  prefix + 'ALL.dat'
        pathdata = data_folder / fdata

        MJD_nu, nu, TF1, TF2, lock = np.genfromtxt(pathdata, unpack=True)  
        if correction_PC_vecchio:
            t_correction = 59705.42
            correction = -0.0833333333
            MJD_nu[MJD_nu<t_correction] += correction
            print ('!!! MJD prior to ', str(t_correction), 'corrected by ', str(correction))
          
        #import Majorana data
        Mdata = prefix + 'Mag.dat'
        Mpath = data_folder / Mdata
        MJD_M, nu_M, sig_nuM = np.genfromtxt(Mpath, unpack=True)  
        if correction_PC_vecchio:
            MJD_M[MJD_M<t_correction] += correction
            print ('!!!MJD Majorana prior to ', str(t_correction), 'corrected by ', str(correction), '\n')

        #import cycle time and stability
        sigdata = prefix + 'SIGMA.dat'
        sigpath = data_folder / sigdata
        
        if differential:
            Tcs = np.genfromtxt(sigpath, usecols=[1])  
            sigs = np.genfromtxt(sigpath, usecols=[3])  
            Tc1 = Tcs[0]
            Tc2 = Tcs[1]
            sig_LD = sigs[0]
            sig_HD = sigs[1]
        else:      #in case only HD data were taken
            Tc1 = 2.85  #typical values (they will not be used)
            sig_LD = 2.3e-13
            Tc2 = float(np.genfromtxt(sigpath, usecols=[1]))
            sig_HD = float(np.genfromtxt(sigpath, usecols=[3]))

            
        #convert into Zeeman shift
        s_Z = Majo(nu_M)
        
        #interpolate Zeeman shift
        Zeeman = np.interp(MJD_nu, MJD_M, s_Z)
        
        #plot Zeeman
        # plt.figure()
        # plt.plot(MJD_M, s_Z, 'o', ls='', c='b', label='original data')
        # plt.plot(MJD_nu, Zeeman, '.', c='r', label='interpolation')
        # plt.title(prefix)
        # plt.grid(True)
        # plt.legend()
        # plt.tight_layout()
        
        #update collisional coefficient (or keep the one loaded from file)
        if rolling_k:
            k_coll = k_coll0
            
            #..... finish routine
        
        #correct for all systematic shifts
        if correction_TOF:
            y_corr = nu -k_coll*(TF1*scale_TF_LD + TF2*scale_TF_HD) - shift_f - Zeeman
        else:
            y_corr = nu -k_coll*(TF1 + TF2) - shift_f - Zeeman        
        
        #decimate data with new sampling rate Ts 
        #returns also number of points in LD and HD (Lock1 <--> LD)
        MJD_Z, Zeeman_a, N1, N2 = resample_F2(MJD_nu, Zeeman, lock, Tc1, Tc2, Ts, thr_DT=th)
        MJD_a, y_corr_a, N1, N2 = resample_F2(MJD_nu, y_corr, lock, Tc1, Tc2, Ts, thr_DT=th)
        
        MJD_Z, Zeeman_a, N1, N2 = resample_F2(MJD_nu, Zeeman, lock, Tc1, Tc2, Ts, thr_DT=th)
        
        #calculate measurement time
        T1 = N1*Tc1
        T2 = N2*Tc2
        T = T1 + T2
        
        # #calculate type A uncertainty. If N2(HD) data is more than 80% assign sigma(HD), otherwise as if all data where in LD (conservative)
        # if N2/(N1+N2)>0.8:    
        #     sig_y_a = sig_HD/np.sqrt(T)       
        # else: 
        #     sig_y_a = sig_LD/np.sqrt(T) 
        
        #calculate type A uncertainty based on how many time is in HD or LD
        sig_y_a = ((sig_LD*T1 + sig_HD*T2)/T) /np.sqrt(T)  #sig(tau) = weighted average of sig(1s)/radq(tau)
        
        #adds quadratically the uncertainty contribution from collisional
        MJD_TF1a, TF1a, N1_TF1a, N2_TF1a = resample_F2(MJD_nu, TF1, lock, Tc1, Tc2, Ts, thr_DT=th)
        MJD_TF2a, TF2a, N1_TF2a, N2_TF2a = resample_F2(MJD_nu, TF2, lock, Tc1, Tc2, Ts, thr_DT=th)

        # TOF = np.average(TF1) + np.average(TF2)
        if correction_TOF:
            TOFa = TF1a*scale_TF_LD + TF2a*scale_TF_HD
        else:
            TOFa = TF1a + TF2a

        sig_y_a = np.sqrt(sig_y_a**2 + sig_k**2*(TOFa)**2)
        
        #export data to output file
        header1 = 'sampling time = ' + str(Ts) + ' MJD (' + str(Ts*86400) + ' s) \n' 
        header2_e = 'MJD \t y(M4-F2) \t sig_y(type A) \t N1 \t N2 \t T \t TOF \t Z \t flag'  + '\n'
        # header2_e = 'MJD \t y(M4-F2) \t sig_y(type A) \t N1 \t N2 \t T \t sig_y(type B)'  + '\n'
        header2_c = 'MJD \t y(M4-F2) \t sig_y(type A) \t flag'  + '\n'
        header3 = 'N1,2 = number of points from lock1,2. T=measurement time/s' + '\n' + 'TOF=(TOF1+TOF2)/a.u., Z = Zeeman shift (rel units)' + '\n'
        header4 = 'T1 = ' + str(Tc1) + ' s \t T2 = ' + str(Tc2) + 's \t k =' + '{:.3e}'.format(k_coll)
        header_e = header1 + header2_e + header3 + header4
        header_c = header1 + header2_c 
        
        elab_data = np.column_stack([MJD_a, -y_corr_a, sig_y_a, N1, N2, T, TOFa, Zeeman_a])
        # elab_data = np.column_stack([MJD_a, -y_corr_a, sig_y_a, N1, N2, T, sig_y_B])
        confronto_data = np.column_stack([MJD_a, -y_corr_a, sig_y_a])
        
        #add flag '0'= discard, '1'=experimental, '2'=validated
        nl = '\t' + str(flag) + '\t' + '\n'

        if len(MJD_a)>1:
            np.savetxt(filepath, elab_data,  fmt=('%.3f','%.8e','%.8e','%.0f','%.0f','%.3f', '%.8e', '%.8e'), delimiter='\t', header=header_e, newline=nl)
            np.savetxt(filepath1, confronto_data,fmt=('%.3f', '%.8e', '%.8e'), delimiter='\t', header=header_c, newline=nl)
            print ('"', fname,  '"   created \n')
            print ('"', fname1,  '"   created \n')
        else:
            print(len(MJD_a))
            print(prefix, "discarded, not enough data")
    
        
    
        # #plot y_corr
        # plt.figure()
        # plt.plot(MJD_nu, y_corr*1e15, '.', ls='', c='k', label='original data')
        # plt.plot(MJD_a, y_corr_a*1e15, 'o', c='r', label='average Ts=864 s')
        # plt.grid(True)
        # plt.legend()
        # plt.tight_layout()
        # print (np.average(y_corr))
        # print (np.average(y_corr_a))
