#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 18:50:47 2019

@author: michele
"""
import matplotlib.pyplot as plt
import numpy as np
import sys

def resample(x, y, dx):
    #x=frequencies, y=PSD values, N = di
    x, y = np.asarray(x),  np.asarray(y) 
        
    start, stop = x[0], x[-1]+dx
    bin_edges = np.arange(start, stop, dx)
    #print (bin_edges[:20], bin_edges[-20:])
    #print(xnew)
    #xnew[0], xnew[-1] = start, stop
    ynew = []
    xnew = []
    
    for i in range(len(bin_edges)-1):
      cond = (x>=bin_edges[i])
      cond = cond & (x<bin_edges[i+1])
      if np.any(cond):
        ynew.append(np.mean(y[cond]))
        xnew.append(np.mean(x[cond]))
        #print (len(x[cond]))
      else:
        ynew.append(np.nan)
        xnew.append(np.nan)
      
    ynew = np.array(ynew)
    xnew = np.array(xnew)
    valid = ~np.isnan(ynew)
    
    
    return xnew[valid], ynew[valid]

def resample_F2(x, y, F, Tc1, Tc2, dx, thr_DT=0.5):
    #x=MJD, y= freq, F=flag (==1 for lock1, ==2 for lock2, dx=intervallo di campionamento
    #Tc1 = Tempo ciclo lock1, Tc2 = tempo ciclo lock2
    #thr_DT = T_misura/dx (from 0 to 1). DEFAULT: Se tempo di misura < dx/2 scarta il punto
    #
    #returns decimated y values
    #x is taken as the center of the bin
    #x0 is rounded as the beginning of each day (integer MJD)
    #if measurement time is < Ts/2 excludes the data
    x, y = np.asarray(x),  np.asarray(y) 
        
    #find number of decimals to round bin edges
    dec = abs(int(np.log10(dx)+0.5))
    start = np.round(min(x), dec)
    stop = np.round(max(x), dec)+dx
    bin_edges = np.arange(start, stop, dx)
    # print (bin_edges[:20], bin_edges[-20:])
    ynew = []
    xnew = []
    L1 = []
    L2 = []
    
    for i in range(len(bin_edges)-1):
      cond = (x>=bin_edges[i])
      cond = cond & (x<bin_edges[i+1])
      cond1 = cond & (F==1)
      cond2 = cond & (F==2)
      t_i = (bin_edges[i]+bin_edges[i+1])/2.

      if np.any(cond):
        N1 = F[cond1]
        N2 = F[cond2]
        T = (len(N1)*Tc1+len(N2)*Tc2)/86400.  #measurement time in MJD
        # print(T)
        if T > thr_DT*dx:           #checks that dead time is < 50%
            ynew.append(np.mean(y[cond]))
            xnew.append(t_i)
            L1.append(len(N1))
            L2.append(len(N2))
      else:
        print('MJD', t_i, 'point discarded')
        ynew.append(np.nan)
        xnew.append(np.nan)
        L1.append(np.nan)
        L2.append(np.nan)
   
    ynew = np.array(ynew)
    xnew = np.array(xnew)
    L1 = np.array(L1)
    L2 = np.array(L2)
    valid = ~np.isnan(ynew)
    
    
    return xnew[valid], ynew[valid], L1[valid], L2[valid]

#%%testing

# L0 = 1000   #Number of points of the initial array
# avg = 10   #number of points of the final array

# x = np.arange(3, L0)
# y = np.random.rand(L0-3)
# xbin, ybin = resample1(x, y, avg)

    
# plt.close('all')
# plt.figure()
# plt.plot(x, y)
# plt.plot(xbin, ybin)
        
