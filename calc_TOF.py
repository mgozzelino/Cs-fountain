# -*- coding: utf-8 -*-
#2022-06-17
#to eliminate a bug of 00_merge_lock12 (it was calculating sigma(1s) on data with outliers NOT removed!!!)
#now the function accepts x, y data instead of the original file

import matplotlib.pyplot as plt
import numpy as np
import allantools

    

def TOFm(t, TOF, tau0, calculate_tau0=False):   #calculate TOF ADEv and average TOF
    

    # t, y = np.genfromtxt(fname, usecols=[0,1], unpack=True, skip_header=15, comments='**') 
    
    if calculate_tau0:    #calculate tau0 from first 20 data
        tau0_c = np.average(np.diff(t[:20])*86400.)
    else:
        tau0_c = tau0     #(default) take a fixed cycle time
    # print(tau0_c)
    
    #check for invalid values
    #calculate average TOF
    Ninv = np.argwhere(np.isnan(TOF))
    if len(Ninv) > 0:
        print('!!! ' + str(len(Ninv)) + ' invalid TOF values at position:')
        print(Ninv, '   ignored')
    
    valid = ~np.isnan(TOF)
    avgTOF = np.mean(TOF[valid])  #ignores nan

    #calculate ADEV
    (taus_used, oadev, oadev_error, oadev_n) = allantools.oadev(TOF[valid], data_type='freq', rate=1./tau0_c, taus='octave')
    
    
        
    sig_TOF = oadev[-2]    
    
    return avgTOF, sig_TOF

