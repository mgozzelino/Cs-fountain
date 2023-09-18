# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt 

from pathlib import Path
from datetime import datetime, timedelta, date
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
import uncertainties as unc


save_data = True
save_fig = True


#%%

#search paths to folders named "monitor"
path = Path.cwd()

paths = []
for p in path.rglob("*"):
    if p.is_dir():
        if p.name == 'monitor':
            paths.append(p)


#import data            
mjds, Zs = [],[]
mjdas, Zas = [],[]


for folder in paths:
    for file in folder.iterdir():
        
        mjd, z = np.loadtxt(file, unpack=True, usecols=[0,7])
        mjds.append(mjd)
        Zs.append(z)
        
        #calculate daily averages
        mjda = np.average(mjd)
        Za = np.average(z)
        
        #append
        mjdas.append(mjda)
        Zas.append(Za)
                

#join data
mjds = np.concatenate(mjds, axis=0)
Zs = np.concatenate(Zs, axis=0)


#reorder daily averages
ind = np.argsort(mjdas)
mjdas = np.array(mjdas)[ind]
Zas = np.array(Zas)[ind]




#%%

###export data to file.dat
savename = 'Zeeman_shift' 

if save_data:
    
    filo = open(savename + '.dat', 'w')

    filo.write('#MJD \t Z \n')
    for t, z  in zip(mjds, Zs):
        filo.write(str(t) + '\t' + str(z)  + '\n')
        filo.flush()
    filo.close()
    
savename1 = 'avg_daily_Zeeman' 

if save_data:
    
    filo = open(savename1 + '.dat', 'w')

    filo.write('#MJD \t Z \n')
    for ta, za in zip(mjdas, Zas):
        filo.write(str(ta) + '\t' + str(za)   + '\n')
        filo.flush()
    filo.close() 


#%%
plt.close('all')
#%%
#plot
##plot raw data
plt.figure()

#plt.plot(t, y, '.', c='k')

plt.plot(mjds, Zs, ls='',  marker='.', mec='tab:blue', mfc='tab:blue', label='Z')
# plt.errorbar(tm, ym, yerr=sigym, ls='',  martab:blueer='o', ecolor = 'r', mec='r', mfc='r', label='elab matlab')
plt.errorbar(mjdas, Zas, ls='',  marker='s', mec='b', mfc='b', label='daily avg')


# plt.plot(tM-59499., -yM*1e15, '.', c='b', label='elab Marco', zorder=10)

#plt.title(title ,fontsize = 12)
plt.xlabel('MJD', fontsize = 14)
plt.ylabel(r'Z /a.u.', fontsize = 14)

plt.grid(True)
plt.tight_layout()
plt.legend()

plt.show()

if save_fig:
    plt.savefig(savename + '.png')
    plt.savefig(savename + '.pdf')

# #%%
# #plot differences
# diffs = TOFas*1e15 - ym
# sig_diffs = np.sqrt(sigym**2 + (sigas*1e15)**2 )
# t_diff = (tm+tas)/2

# plt.figure()
# plt.errorbar(t_diff, diffs, yerr=sig_diffs, ls='',  marker='o', ecolor = 'k', mec='k', mfc='k', label='y(py)-y(matlab)')

# plt.axhline(c='r')

# #plt.title(title ,fontsize = 12)
# plt.xlabel('MJD', fontsize = 14)
# plt.ylabel(r'dy $\times 10^{15}$', fontsize = 14)

# plt.grid(True)
# plt.tight_layout()
# plt.legend()

# plt.show()

# if save_fig:
#     plt.savefig('differences' + '.png')
#     plt.savefig('differences' + '.pdf')
