# -*- coding: utf-8 -*-
#2022-06-17
#to eliminate a bug of 00_merge_lock12 (it was calculating sigma(1s) on data with outliers NOT removed!!!)
#now the function accepts x, y data instead of the original file

import matplotlib.pyplot as plt
import numpy as np
import allantools
from scipy.optimize import curve_fit

def noise(x, y1):
    y = y1*x**-0.5 #WN model
    return y
    

def sig1s(t, y, fname, tau0, calculate_tau0=False, show_plot=True):   #calculate ADEv and fits the noise to have 
    

    #checks for invalid values
    Ninv = np.argwhere(np.isnan(y))
    if len(Ninv) > 0:   
        print('!!! ' + str(len(Ninv)) + 'invalid y values at position:')
        print(Ninv)
        
    #calculate average frequency
    valid = ~np.isnan(y)
    avg_y = np.mean(y[valid])
    
    
    if calculate_tau0:    #calculate tau0 from first 20th-24th data
        tau0_c = np.average(np.diff(t[20:25])*86400.)
    else:
        tau0_c = tau0     #(default) take a fixed cycle time
    print('Tc = ', tau0_c)
    
    #calculate ADEV and fit to extrapolate sigma(1s)
    (taus_used, oadev, oadev_error, oadev_n) = allantools.oadev(y[valid], data_type='freq', rate=1./tau0_c, taus='all')
    
    first = 2
    last = 12
    
    taus_fit = taus_used[first:last]
    oadev_fit = oadev[first:last]
    err_fit = oadev_error[first:last]
    #fit noise
    popt, pcov = curve_fit(noise, taus_fit, oadev_fit, p0=1.5e-13, sigma=err_fit, absolute_sigma=True)
    
    sig_1s = popt[0]
    print('sig(1s) = ', sig_1s)

    
    
    #plot
    if show_plot:
        
        fig, ax = plt.subplots()
        xplot = np.logspace(0, 4)
        yplot = noise(xplot, *popt)
        ax.errorbar(taus_used, oadev, yerr=oadev_error)
        ax.errorbar(taus_fit, oadev_fit, yerr=err_fit, c='b', label='data used for fit')
        ax.loglog(xplot, yplot, c='r')
    
        plt.title(fname)
        
        textstr = '\n'.join((
        r'$\sigma_y(\mathrm{1 s}) = $%.2e' % (sig_1s,),
        r'$T_{c}=  %.2f $ s' % (tau0_c, )))
        
        if fname[-5]=='1':
            if sig_1s>3e-13 or tau0_c > 2.5: #yellow box for strange values of stability or cycle time
                props = dict(boxstyle="square", facecolor='y', ec='y', lw=2, alpha=0.8)
            else:
                props = dict(boxstyle="square", facecolor='w', ec='r', lw=2)

        if fname[-5]=='2':
            if sig_1s>3e-13 or tau0_c > 2.9:  #yellow box for strange values of stability or cycle time
                props = dict(boxstyle="square", facecolor='y', ec='y', lw=2, alpha=0.8)
            else:
                props = dict(boxstyle="square", facecolor='w', ec='r', lw=2)
        
        # place a text box in lower left in axes coords
        ax.text(0.05, 0.25, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)
    
        plt.grid(which='minor', ls=':')
        plt.grid()
    
    return tau0_c, avg_y, sig_1s

#%%
# #test
# fname_test = '2022-06-16_00-00-10_diff200-500_Lock2.txt'
    # t, y = np.genfromtxt(fname, usecols=[0,1], unpack=True, skip_header=15, comments='**') 
#sig1s(t, y, fname_test)
