# -*- coding: utf-8 -*-
##This files takes elaborated data and merges them to have 1 file per day
#version updates:
#03_export_daily.py moved suffix and headers to a single variable, to avoid mistakes when making changes to the filename


import numpy as np
import matplotlib.pyplot as plt 
# import os
from datetime import datetime 
import matplotlib.dates as mdates
from pathlib import Path


save_data = True

#%%
#import data from multiple files
#import files list (one file each day)

file_suffix = '_INRIM_HM-INRIM_ITCsF2.dat'
file_header = '(MJDstart+MJDstop)/2 \t y(M4-ITCsF2) \sigma_y(type A) \t flag'
# file_suffix = '_INRIM_USOYb-INRIM_ITCsF2.dat'
# file_header = '(MJDstart+MJDstop)/2 \t y(USOYb-ITCsF2) \sigma_y(type A) \t flag'


#subfolder
save_folder = Path('00_elaborated_data/confronto/daily_data')
data_folder = Path('00_elaborated_data/confronto')

cwd = Path.cwd()
path_s = cwd / save_folder
path_d = cwd / data_folder

try:
    path_s.mkdir()
    print ('subfolder ' + save_folder.name  + ' created')    
except:
    print ('subfolder ' + save_folder.name  + ' already existed') 
    
#%%    
#import file list    
files_list = []

ts, nus, sigs = [],[],[]

for file in path_d.iterdir():
    if file.name.endswith("confronto.dat"):
        files_list.append(file.name) 

#sort files
files_list.sort(key = lambda date: datetime.strptime(date[:10], '%Y-%m-%d'))

#find dates and prefixes    
days = []
# prefixs = []

for file in files_list:
        day = file[:10]
        # prefix = file[:32]
        days.append(day)
        # prefixs.append(prefix)

#remove duplicates in days
days = list(dict.fromkeys(days))  

#group files with same day
files_list1 = []

for day in days:
    fday = []
    for file in path_d.iterdir():
        if file.name.startswith(day):
            fday.append(file.name)
    files_list1.append(fday)
    
#export files into subfolder

for l in files_list1:
    if np.size(l)==1:
        # print(l[0])
        data = np.genfromtxt(path_d / l[0])
        # MJD = int(np.floor(data[1,0]))  #takes the MJD from the second timetag of the file

        savename = l[0][:10] + file_suffix
        path = path_s / savename
        if path.is_file():
            print ('...\n')
            #print (l[0], 'data already exported')
        else:
            np.savetxt(path, data, fmt=('%.3f', '%.8e','%.8e', '%.0f'), header=file_header, delimiter='\t')
            print(path.name, 'exported')
    else:
        l.sort(key = lambda date: datetime.strptime(date[:19], '%Y-%m-%d_%H-%M-%S'))
        #print(l)
        data = []
        for f in l:
            # print (f)
            data_i = np.genfromtxt(path_d / f)
            MJD = int(np.floor(data_i[1,0]))  #takes the MJD from the second timetag of the file
            data.append(data_i)
        
        data = np.concatenate(data, axis=0)
    
        savename = f[:10] + file_suffix
        path = path_s / savename
        if path.is_file():
            print ('...\n')
            #print (l, 'data already exported')
        else: 

            np.savetxt(path, data, fmt=('%.3f', '%.8e','%.8e', '%.0f'), header=file_header, delimiter='\t')

            print(savename, 'exported')
    

