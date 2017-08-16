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
def experiment():

    if __name__ == '__main__':
        write_to = '/home/sofiat/Dropbox/Glasgow/projects/spa-st-super-stability/experiments/1_005/experiment1_005.csv'
        with open(write_to, 'w', newline='') as write_csvfile:
            O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
            d = 'experiments/1_005/'
            for i in range(100, 700, 100):
                is_super_stable = []
                directory = d+str(i)+'/output.csv'
                with open(directory, 'r') as read_csvfile:
                    I = list(csv.reader(read_csvfile, delimiter=' '))
                    for row in I:
                        if row[1] == 'Y':
                            is_super_stable.append(int(row[2]))
                print(i, proportion(len(is_super_stable)), np.mean(is_super_stable), min(is_super_stable), max(is_super_stable), np.median(is_super_stable))
                O.writerow([i, proportion(len(is_super_stable)), np.mean(is_super_stable), min(is_super_stable), max(is_super_stable), np.median(is_super_stable)])
            write_csvfile.close()

# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
experiment()