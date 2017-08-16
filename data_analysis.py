import numpy as np
from time import *
import sys
import os
import csv

# -------------------------------------------------------------------------------------------------------------------------------
#  -------------------- Writes the matching to a text file, the first line verifies that that the matching is stable / not :|
# -------------------------------------------------------------------------------------------------------------------------------
def proportion(value):
    return round((value/1000)*100, 2)

def get_soluble_instances(filename):
    is_super_stable = []
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[1] == 'Y':
                is_super_stable.append(int(row[2]))
    return is_super_stable

def write_statistics():

    write_to = '/home/sofiat/Dropbox/Glasgow/projects/spa-st-super-stability/experiments/1_005/experiment1_005.csv'
    with open(write_to, 'w', newline='') as write_csvfile:
        O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
        f = 'experiments/1_005/'
        for i in range(100, 1100, 100):
            filename = f + str(i) + '/output.csv'
            is_super_stable = get_soluble_instances(filename)
            print(i, proportion(len(is_super_stable)), np.mean(is_super_stable), min(is_super_stable), max(is_super_stable), np.median(is_super_stable))
            O.writerow([i, proportion(len(is_super_stable)), np.mean(is_super_stable), min(is_super_stable), max(is_super_stable), np.median(is_super_stable)])
        write_csvfile.close()
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
write_statistics()