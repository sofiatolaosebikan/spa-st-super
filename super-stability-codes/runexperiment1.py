import matplotlib.pyplot as plt
from spastsuper import SPASTSUPER
import numpy as np
import sys
import os
import csv


def run():

    if __name__ == '__main__':
        for students in range(100, 1100, 100):
            directory = '/scratch1/sofiato/experiments/1/' + str(students)
            output = directory + '/output3.csv'
            with open(output, 'w', newline='') as csvfile:
                O = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for i in range(1, 1001):
                    filename = '/instance' + str(students) + '_' + str(i)
                    input_file = directory + filename + '.txt'
                    s = SPASTSUPER(input_file)
                    s.algorithm()
                    s.check_stability()
                    # ---------------------------------------------------------------------------------------------------------------------------------------------
                    # WRITE THE FILENAME<SPACE>TIME TAKEN<SPACE>Y/N SIGNIFYING IF A SUPER-STABLE MATCHING EXISTS<SPACE>CARDINALITY OF SUCH MATCHING AND 0 OTHERWISE
                    # ---------------------------------------------------------------------------------------------------------------------------------------------

                    if s.multiple_assignment is True or s.lecturer_capacity_checker is True or s.project_capacity_checker is True:
                        O.writerow([filename, s.time_taken, 'N', 0])

                    else:
                        if s.blockingpair is True:
                            O.writerow([filename, s.time_taken, 'U', 0])

                    if s.multiple_assignment is False and s.lecturer_capacity_checker is False and s.project_capacity_checker is False and s.blockingpair is False:
                        O.writerow([filename, s.time_taken, 'Y', s.assigned])

                csvfile.close()

# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances(filename):
    is_super_stable = []
    time_taken = 0
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[2] == 'Y':
                is_super_stable.append(int(row[3]))
                time_taken += float(row[1])  # we only care about the average time taken for soluble instances
    return is_super_stable, time_taken
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# =================================== The proportion of these instances -- 1000 instances in all ===================================
def proportion(value):
    return round((value/1000)*100, 2)
#  ---------------------------------------------------------------------------------------------------------------------------------


def write_statistics(write_to, write_from):
    proportion_matching = []
    av_time_taken = []
    mean_matching = []
    min_matching = []
    max_matching = []
    median_matching = []
    with open(write_to, 'w', newline='') as write_csvfile:
        O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        O.writerow(['n1', 'proportion', 'time_taken', 'mean', 'min', 'max', 'median'])
        for i in range(100, 1100, 100):
            filename = write_from + str(i) + '/output3.csv'
            is_super_stable, time_taken = get_soluble_instances(filename)
            p = proportion(len(is_super_stable))
            average_time_taken = time_taken/len(is_super_stable)
            me = np.mean(is_super_stable)
            mi = min(is_super_stable)
            ma = max(is_super_stable)
            med = np.median(is_super_stable)

            proportion_matching.append(p)
            av_time_taken.append(average_time_taken)
            mean_matching.append(me)
            min_matching.append(mi)
            max_matching.append(ma)
            median_matching.append(med)
            O.writerow([i, p, average_time_taken, me, mi, ma, med])
        write_csvfile.close()
    return proportion_matching, av_time_taken, min_matching, max_matching

#run()

write_to_1 = '1/experiment1.csv'
write_from_1 = '1/'
instances = list(range(100, 1100, 100))
proportion_matching, av_time_taken, min_matching, max_matching = write_statistics(write_to_1, write_from_1)

plt.figure()
#plt.grid()
plt.plot(instances, proportion_matching, color='r', marker='o')
plt.xlabel('number of students')
plt.ylabel('percentage of solvable instances')
#plt.title('Proportion of instances that admits a super-stable matching')
#plt.legend(loc='upper right')
plt.savefig('1/experiment1_proportion.png')

plt.figure(figsize=(6,6))
plt.plot(instances, av_time_taken, color='r', marker='^')
plt.xlabel('number of students')
plt.ylabel('average time taken')
plt.savefig('1/experiment1_time.png')


plt.figure(figsize=(6,6))
plt.plot(instances, min_matching, marker='^', label='min')
plt.plot(instances, max_matching, marker='s', label='max')
plt.xlabel('number of students')
plt.ylabel('size of super-stable matching')
plt.legend(loc='upper left')
plt.savefig('1/experiment1_min_max.png')

