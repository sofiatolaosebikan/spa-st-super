import matplotlib.pyplot as plt
import numpy as np
from spastsuper import SPASTSUPER
import sys
import os
import csv


def run(folder):

    if __name__ == '__main__':
        folder_path = '/scratch1/sofiato/experiments/3/' + folder + '/'
        for student in range(100, 1100, 100):
            instance_path = folder_path + str(student) + '/'  # experiments/3/length10/100/
            output = instance_path + 'output3.csv'   # experiments/3a/100/output.csv
            with open(output, 'w', newline='') as csvfile:
                O = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for k in range(1, 1001):
                    filename = 'instance' + str(k)
                    input_file = instance_path + filename + '.txt'  # experiments/3a/100/instance1.txt
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

#run('length5')
#run('length10')
#run('lengthquatertohalf')



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
            #mean_matching.append(me)
            #min_matching.append(mi)
            #max_matching.append(ma)
            #median_matching.append(med)
            O.writerow([i, p, average_time_taken, me, mi, ma, med])
        write_csvfile.close()
    return proportion_matching

#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================
instances = list(range(100, 1100, 100))
write_to_3a = '../experiments/3/length5/experiment3a_new.csv'
write_to_3b = '../experiments/3/length10/experiment3b_new.csv'
write_to_3c = '../experiments/3/length/experiment3c_new.csv'


write_from_3a = '../experiments/3/length5/'
write_from_3b = '../experiments/3/length10/'
write_from_3c = '../experiments/3/length/'

proportion_matching_3a = write_statistics(write_to_3a, write_from_3a)
proportion_matching_3b = write_statistics(write_to_3b, write_from_3b)
proportion_matching_3c = write_statistics(write_to_3c, write_from_3c)

plt.figure()

plt.plot(instances, proportion_matching_3a, color='g', label='pref_length = 5')
plt.plot(instances, proportion_matching_3b, color='r', label='pref_length = 10')
plt.plot(instances, proportion_matching_3c, color='b', label='pref_length = 0.25(n1) to 0.5(n1)')

plt.xlabel('n1 - number of students')
plt.ylabel('percentage of solvable instances')
#plt.title('Proportion of instances that admits a super-stable matching with tie density fixed at 0.005 for students and lecturers')
plt.legend(loc='upper right')
plt.savefig('../experiments/3/experiment3_new.png')
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
