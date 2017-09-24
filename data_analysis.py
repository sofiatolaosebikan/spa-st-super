import matplotlib.pyplot as plt
import numpy as np
from time import *
import sys
import os
import csv


# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances(filename):
    is_super_stable = []
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[1] == 'Y':
                is_super_stable.append(int(row[2]))
    return is_super_stable
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# =================================== The proportion of these instances -- 1000 instances in all ===================================
def proportion(value):
    return round((value/1000)*100, 2)
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# def write_statistics_1_005():
#     instances_1_005 = []
#     proportion_matching_1_005 = []
#     mean_matching_1_005 = []
#     min_matching_1_005 = []
#     max_matching_1_005 = []
#     median_matching_1_005 = []
#     write_to = '/home/sofiat/Documents/Glasgow/research/spa-st-super-stability/experiments/1_005/experiment1_005.csv'
#     with open(write_to, 'w', newline='') as write_csvfile:
#         O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
#         f = 'experiments/1_005/'
#         for i in range(100, 1100, 100):
#             instances_1_005.append(i)
#             filename = f + str(i) + '/output.csv'
#             is_super_stable = get_soluble_instances(filename)
#             p = proportion(len(is_super_stable))
#             me = np.mean(is_super_stable)
#             mi = min(is_super_stable)
#             ma = max(is_super_stable)
#             med = np.median(is_super_stable)
#
#             proportion_matching_1_005.append(p)
#             mean_matching_1_005.append(me)
#             min_matching_1_005.append(mi)
#             max_matching_1_005.append(ma)
#             median_matching_1_005.append(med)
#             O.writerow([i, p, me, mi, ma, med])
#         write_csvfile.close()
#     return instances_1_005, proportion_matching_1_005, mean_matching_1_005, min_matching_1_005, max_matching_1_005, median_matching_1_005


# ================================= Perform basic statistics on these instances =================================
def write_statistics(write_to, write_from):
    proportion_matching = []
    #mean_matching = []
    #min_matching = []
    #max_matching = []
    #median_matching = []
    with open(write_to, 'w', newline='') as write_csvfile:
        O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
        for i in range(100, 1100, 100):
            filename = write_from + str(i) + '/output.csv'
            is_super_stable = get_soluble_instances(filename)
            p = proportion(len(is_super_stable))
            #me = np.mean(is_super_stable)
            #mi = min(is_super_stable)
            #ma = max(is_super_stable)
            #med = np.median(is_super_stable)

            proportion_matching.append(p)
            #mean_matching.append(me)
            #min_matching.append(mi)
            #max_matching.append(ma)
            #median_matching.append(med)
            O.writerow([i, p])
        write_csvfile.close()
    return proportion_matching
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================
instances = list(range(100, 1100, 100))
write_to_3a = 'experiments/3/length5/experiment3a.csv'
write_to_3b = 'experiments/3/length10/experiment3b.csv'
write_to_3c = 'experiments/3/length/experiment3c.csv'
#write_to_1_05 = 'experiments/1_05/experiment1_05.csv'

write_from_3a = 'experiments/3/length5/'
write_from_3b = 'experiments/3/length10/'
write_from_3c = 'experiments/3/length/'
#write_from_1_05 = 'experiments/1_05/'

#instances_1_005, proportion_matching_1_005, mean_matching_1_005, min_matching_1_005, max_matching_1_005, median_matching_1_005 = write_statistics_1_005()
proportion_matching_3a = write_statistics(write_to_3a, write_from_3a)
proportion_matching_3b = write_statistics(write_to_3b, write_from_3b)
proportion_matching_3c = write_statistics(write_to_3c, write_from_3c)

plt.figure()
plt.grid()

#plt.plot(instances, proportion_matching_3a, color='r', label='pref_length = 5')
plt.plot(instances, proportion_matching_3b, color='b', label='pref_length = 10')
plt.plot(instances, proportion_matching_3c, color='r', label='pref_length = quarter(n1) to half(n1)')
#plt.plot(instances, proportion_matching_1_05, color='b', label='0.05')

plt.xlabel('instance size')
plt.ylabel('proportion of soluble instances')
plt.title('Proportion of instances that admits a super-stable matching with tie density fixed at 0.005 for students and lecturers')

plt.legend(loc='upper right')
plt.show()
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------



#
