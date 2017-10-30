from spastsuper import SPASTSUPER
import sys
import os
import csv


def run():

    if __name__ == '__main__':
        for i in range(0, 11):
            for j in range(0, 11):
                folder_path = '2/' + str(i) + '_' + str(j) + '/'  # experiments/2/0_0/
                for student in range(100, 1100, 100):
                    instance_path = folder_path + str(student) + '/'  # experiments/2/0_0/100/
                    output = instance_path + 'output3.csv'   # experiments/2/0_0/100/output2.csv
                    with open(output, 'w', newline='') as csvfile:
                        O = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        for k in range(1, 1001):
                            filename = 'instance' + str(k)
                            input_file = instance_path + filename + '.txt'  # experiments/2/0_0/100/instance1.txt
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

run()