#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:33:25 2021

@author: michele
"""

import subprocess

program_list = ['00_merge_lock12', '01_collisional', '02_calc_y_Ts.py', '03_export_daily.py']

for program in program_list:
    subprocess.call(['python', program])
    print("\n ...Finished:" + program + '\n')
    
    
print('Did you check initial collisional coefficient ???????????')
