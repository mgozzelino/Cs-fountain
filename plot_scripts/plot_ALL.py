# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt 
import os
from datetime import datetime, timedelta, date
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
import uncertainties as unc


save_data = True
save_fig = True

#%%
#import data from multiple files
#import files list (one file each day)

#data folder
# data_folder = 'daily_data/'
data_folder = '01_merged_data/'

files_list = []

ts, nus, sigs = [],[],[]

for file in os.listdir(os.path.join(os.getcwd(), data_folder)):
    print (file)
    if file.endswith("ALL.dat"):
        files_list.append(file) 


ts, nus, sigs = [],[],[]
for file in files_list:
    t, nu = np.loadtxt(data_folder+file, unpack=True, usecols=[0,1])
    ts.append(t)
    nus.append(nu)
    # sigs.append(sig)

ts = np.concatenate(ts, 0)
nus = np.concatenate(nus, axis=0)
# sigs = np.concatenate(sigs, axis=0)


#import matlab data
for file in os.listdir(os.getcwd()):
    # print (file)
    if file.endswith("Giovanni.txt"):
        filename = file
        tm, ym, sigym =  np.loadtxt(filename, unpack=True)
        ym = ym
    elif  file.endswith("Valerio.txt"):
        filename = file
        tm, ym, sigym =  np.loadtxt(filename, unpack=True)
        ym = -ym


pivot = 0 #np.round((min(ts)+max(ts))/2, 1)     #59529.

# #import Marco's data
# tM, yM =  np.loadtxt('2021-10-27_INRIM_HM-INRIM_IT-CsF2.dat', unpack=True, usecols=[0,1])

#%%

###export data to file.dat
savename = 'daily_data' 

if save_data:
    
    filo = open(savename + '.dat', 'w')

    filo.write('#MJD \t nu  \n')
    for t, nu in zip(ts, nus):
        filo.write(str(t) + '\t' + str(nu)  + '\n')
        filo.flush()
    filo.close()

#%%
#plot
##plot raw data
plt.figure()

#plt.plot(t, y, '.', c='k')

plt.plot(ts, nus*1e15, ls='',  marker='.', label='elab python')
# plt.errorbar(ts-pivot, nus*1e15, yerr=sigs*1e15, ls='',  marker='.', ecolor = '0.4', elinewidth=0.5, mec='k', mfc='k', label='elab python')
# plt.errorbar(tm-pivot, ym, yerr=sigym, ls='',  marker='o', ecolor = 'r', mec='r', mfc='r', label='elab matlab')
# plt.plot(tM-59499., -yM*1e15, '.', c='b', label='elab Marco', zorder=10)

#plt.title(title ,fontsize = 12)
# plt.xlabel('MJD', fontsize = 14)
plt.xlabel('MJD - '+str(pivot) + ' MJD', fontsize = 14)
plt.ylabel(r'y(M4-F2) $\times 10^{15}$', fontsize = 14)

plt.grid(True)
plt.tight_layout()
plt.legend()

plt.show()

if save_fig:
    plt.savefig(savename + '.png')
