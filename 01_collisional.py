# -*- coding: utf-8 -*-

###
#this program takes Lock1 and Lock2 data (already merged and outliers-removed)
#takes hystorical collisional-shift data from "collisional_hyst.dat"
#calculates k_coll for each Lock1-Lock2 pair
#saves k_coll data in a file called "collisional_data.dat"
#updates the mean collisional coefficient and stores it in a file called "collisional_updated.dat"


#major updates list:
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from pathlib import Path

def calc_k(yL, yH, TOFL, TOFH):
    k = (yH - yL)/(TOFH-TOFL)
    return k
    
def calc_sig_k(yL, yH, TL, TH, sig_L, sig_H, sig_TL, sig_TH):
    sig2 = (1./(TH-TL)**2)*(sig_L**2 + sig_H**2) + ((yL-yH)/(TL-TH)**2)**2 *(sig_TL**2 + sig_TH**2)
    sig = np.sqrt(sig2)
    return sig
    
def cum_k(ki, sigi, kiwi0=0, wi0=0):   #update collisional weighted average value, considering also previous data
    wi = 1./sigi**2
    kiwi = kiwi0 + ki*wi
    wi = wi + wi0
    k = kiwi/wi
    sig_k = np.sqrt(1./wi)
    return k, sig_k, kiwi, wi

#%%
cwd = Path.cwd()

#import hystorical collisional data
file_coll_in = 'collisional_hyst.dat'
coll0 = np.loadtxt(file_coll_in)    #MJD(last), k, sig_k, sum k_i*w_i, sum w_i

k_coll0 = coll0[1]
kiwi0 = coll0[3]
wi0 = coll0[4]

#%%
#import files list (one file each day)

#data folder
#data folder
data_folder = cwd / '01_merged_data'

files_list = []

for file in data_folder.iterdir():
    if file.name.endswith("ALL.dat"):
        files_list.append(file.name) 
    if file.name.endswith("SIGMA.dat"):
        files_list.append(file.name) 
        
#sort files
files_list.sort(key = lambda date: datetime.strptime(date[:16], '%Y-%m-%d_%H-%M'))

#find dates and prefixes    

prefixs = []

for file in files_list:
        prefix = file[:32]
        prefixs.append(prefix)

#remove duplicates
prefixs = list(dict.fromkeys(prefixs))    

#check if collisional data already elaborated
savepath = Path('collisional_data.dat')
savepath1 = Path('collisional_updated.dat')

#initializa file
# if savepath.is_file() or savepath1.is_file():
    # print ("'" + savepath.name + "'" +' or ' + "'" + savepath1.name + "'" + ' already exist, do you want to overwrite?')
if savepath.is_file():
    print ("'" + savepath.name + "'" + ' already exist, do you want to overwrite?')
else:
    filo = open(savepath, 'w')
    filo.write('# previous collisional data:\n')
    filo.write('# SUM(Ki*wi) = ' + '{:.6e}'.format(kiwi0) + '\n')
    filo.write('# SUM(wi) = ' + '{:.6e}'.format(wi0) + '\n#'+ '\n#\n' )
    filo.write('# MJD medio \t k \t sig_k \t ki*wi \t wi \t sum(ki*wi) \t sum(wi)\n')
    filo.close()
    
    filo = open(savepath, 'a')
    
    for prefix in prefixs:

        #import cycle times, y mean and stability
        sigdata = prefix + 'SIGMA.dat'
        sigpath = data_folder / sigdata
        MJDs, Tcs, ys, sig_ys = np.genfromtxt(sigpath, usecols=[0,1,2,4], unpack=True)
        
        #import average TOFs and their uncertainty
        tofdata = prefix + 'TOF.dat'
        tofpath = data_folder / tofdata
        TOFs, sig_TOFs = np.genfromtxt(tofpath, usecols=[0,1], unpack=True) 
        
        #calculate mean MJD
        MJD_m = (MJDs[0] + MJDs[1]) /2
        
        #calculate k_coll
        ki = calc_k(ys[0], ys[1], TOFs[0], TOFs[1])
        
        #calculate uncertainty k_coll
        sig_ki = calc_sig_k(ys[0], ys[1], TOFs[0], TOFs[1], sig_ys[0], sig_ys[1], sig_TOFs[0], sig_TOFs[1])
        
        #update k_coll
        k_coll, sig_k, kiwi, wi = cum_k(ki, sig_ki, kiwi0, wi0)
        kiwi0 = kiwi
        wi0 = wi
        #save collisional value at i-th day
        stringa = '%5.6f\t%.6e\t%.6e\t%.6e\t%.6e\t%.6e\t%.6e'    %(MJD_m, k_coll, sig_k, ki/sig_ki**2, 1./sig_ki**2, kiwi, wi) 
        filo.write(stringa + '\n')        
        
    filo.close()
    print(savepath.name + ' created \n')

#save final collisional data
if savepath1.is_file():
    print ("'" + savepath1.name + "'" + ' already exist, do you want to overwrite?')
else:
    filo = open(savepath1, 'w')
    filo.write('# updated collisional data:\n')
    filo.write('#last MJD \t k \t sig_k \t sum(ki*wi) \t sum(wi)\n')
    stringa = '%5.6f\t%.6e\t%.6e\t%.6e\t%.6e'    %(MJD_m, k_coll, sig_k, kiwi, wi) 
    filo.write(stringa)
    
    filo.close()
    print(savepath1.name + ' created \n')