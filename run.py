#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:33:25 2021

@author: michele
"""

import subprocess

program_list = ['02_calc_y_Ts.py', '03_export_daily.py']

for program in program_list:
    subprocess.call(['python', program])
    print("\n ...Finished:" + program + '\n')
    
    
print('Aggiornato collisionale???????????')
# print('Aggiornato incertezze???????????')
print('Corretto clock PC vecchio?????????')