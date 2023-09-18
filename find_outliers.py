#From stable32
#A simple, yet effective, technique for finding outliers is to compare each frequency data point 
#yi with the median value, m, of the data set plus or minus some multiple of the absolute median deviation (MAD): 
#MAD = Median { | yi - m | / 0.6745} 
#where m = Median { yi }, and the factor 0.6745 makes the MAD equal 
#to the standard deviation for normally distributed data [16]. 
#These median statistics are more robust because they are insensitive to the size of the outliers.

import numpy as np

def find_outliers(y, n=4):
    m = np.median(y)
    MAD = np.median(np.abs(y-m)/0.6745)
    
    cond = abs(y-m) > n*MAD
    out_i = np.where(cond)[0]

    return out_i


#
#test
# a = np.random.standard_normal(100) 
# a[20] = 3
# a[88] = -10

# i = find_outliers(a, 4)
# print(i)