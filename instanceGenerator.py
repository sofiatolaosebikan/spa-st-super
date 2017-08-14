import sys
import random
import math
from copy import deepcopy


class SPASTIG:
    def __init__(self, students, lower_bound, upper_bound):

        self.students = students
        self.projects = int(math.ceil(0.5*self.students))
        self.lecturers = int(math.ceil(0.2*self.students))  # assume number of lecturers <= number of projects
        self.tpc = int(math.ceil(1.5*self.students))  # assume total project capacity >= number of projects #
        self.tlc = int(math.ceil(1.2*self.students))  # assume total lecturer capacity >= number of lecturers
        self.li = lower_bound  # lower bound of the student's preference list
        self.lj = upper_bound  # int(sys.argv[3])  # upper bound of the student's preference list
        # self.infile = filename  # sys.argv[4]
        #self.student_tie_threshold = stie_threshold  # float(sys.argv[5])
        #self.lecturer_tie_threshold = ltie_threshold  # float(sys.argv[6])

        self.sp = {}
        self.plc = {}
        self.lp = {}

    def instance_generator_no_tie(self):
        """
        A program that generates a random instance for the student project allocation problem with ties.
        :return: a random instance of SPA-ST

        This program writes a random instance of the Student-Project Allocation problem with Ties to a text file.
        It takes input separated STRICTLY by SPACE as follows:
            number of students
            lower bound of the student's preference list
            upper bound of the student's preference list
            #the file name to write the instance with a .txt extension.
            #threshold for student tie -- a floating number between 0 and 1 -- [the closer the threshold is to 1, the more the ties]
            #threshold for lecturer tie
        """
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------        ====== PROJECTS =======                    -----------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # projects have [at least capacity 1, empty string to assign lecturer, empty list to store students]
        self.plc = {'p'+str(i): [1, '', []] for i in range(1, self.projects+1)}
        project_list = list(self.plc.keys())
        # randomly assign the remaining project capacities
        for i in range(self.tpc - self.projects):  # range(9 - 8) = range(1) = 1 iteration. Okay!
            self.plc[random.choice(project_list)][0] += 1
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------        ====== STUDENTS =======                    -----------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        self.sp = {'s' + str(i): [] for i in range(1, self.students + 1)}  # stores randomly selected projects
        for student in self.sp:
            length = random.randint(self.li, self.lj)  # randomly decide the length of each student's preference list
            #  based on the length of their preference list, we provide projects at random
            projects_copy = project_list[:]
            for i in range(length):
                p = random.choice(projects_copy)
                projects_copy.remove(p)  # I did this to avoid picking the same project 2x. This could also be achieved by shuffling and popping?
                self.sp[student].append(p)
                self.plc[p][2].append(student)

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------        ====== LECTURERS =======                    ----------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # lecturers have [capacity set to 0, empty list to store projects, empty list to store students, max c_j: p_j \in P_K, \sum_{p_j \in P_k} c_j]
        self.lp = {'l' + str(i): [0, [], [], 0, 0] for i in range(1, self.lecturers + 1)}  # we assign l1:[p1], l2:[p2], ..., l30:[p30]
        lecturer_list = list(self.lp.keys())
        upper_bound = math.floor(self.projects / self.lecturers)
        projects_copy = project_list[:]  # deep copy all the projects
        for lecturer in self.lp:
            # the number of projects a lecturer can offer is firstly bounded below by 1 and above by ceil(total_projects/total_lecturers)
            # to ensure projects are evenly distributed among lecturers
            number_of_projects = random.randint(1, upper_bound)
            for i in range(number_of_projects):
                p = random.choice(projects_copy)
                projects_copy.remove(p)  # I did this to avoid picking the same project 2x. This could also be achieved by shuffling and popping?
                self.plc[p][1] = lecturer  # take note of the lecturer who is offering the project
                self.lp[lecturer][1].append(p)
                self.lp[lecturer][2].extend(self.plc[p][2])  # keep track of students who have chosen this project for the lecturer
                self.lp[lecturer][4] += self.plc[p][0]  # increment the total project capacity for each lecturer
                if self.plc[p][0] > self.lp[lecturer][3]:  # keep track of the project with the highest capacity
                    self.lp[lecturer][3] = self.plc[p][0]
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # if at this point some projects are still yet to be assigned to a lecturer
        while projects_copy:
            p = projects_copy.pop()  # remove a project from end of the list
            lecturer = random.choice(lecturer_list)  # pick a lecturer at random
            self.plc[p][1] = lecturer  # take note of the lecturer who is offering the project
            self.lp[lecturer][1].append(p)
            self.lp[lecturer][2].extend(self.plc[p][2])  # keep track of students who have chosen this project for the lecturer
            self.lp[lecturer][4] += self.plc[p][0]  # increment the total project capacity for each lecturer
            if self.plc[p][0] > self.lp[lecturer][3]:
                self.lp[lecturer][3] = self.plc[p][0]
        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  Now we decide the ordered preference for each lecturer. We convert to set and back to list because set removes duplicate.
        #  There will be duplicates in the lecture --> students list since we add a student to a lecturer's list for every project the student
        #  has in common with the lecturer, which could be more than 1.
        # capacity for each lecturer can also be decided here..
        for lecturer in self.lp:
            self.lp[lecturer][2] = list(set(self.lp[lecturer][2]))
            random.shuffle(self.lp[lecturer][2])  # this line shuffles the final preference list for each lecturer. Hence ordered.
            self.lp[lecturer][0] = random.randint(self.lp[lecturer][3], self.lp[lecturer][4])  # capacity for each lecturer

        # -----------------------------------------------------------------------------------------------------------------------------------------

    def instance_generator_with_ties(self, student_tie_threshold, lecturer_tie_threshold):

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- ========= CONSTRUCT STUDENTS TIE ========= --------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        for student in self.sp:
            preference = self.sp[student]
            all_but_last = preference[:-1]
            tie_successor = []  # to decide if a project will be tied with its successor..
            for project in all_but_last:
                if random.uniform(0,1) < (student_tie_threshold):
                    tie_successor.append(True)
                else:
                    tie_successor.append(False)
            if len(preference) == 1:
                self.sp[student] = [[preference]]
            else:
                preference_with_ties = []
                counter = 0
                while counter != len(preference):
                    temp = [preference[counter]]
                    while counter < len(preference)-1 and tie_successor[counter] != False:
                        counter += 1
                        temp.append(preference[counter])
                    preference_with_ties.append(temp)
                    counter += 1
                self.sp[student] = [preference, tie_successor, preference_with_ties]
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- ========= CONSTRUCT LECTURERS TIE ========= --------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        for lecturer in self.lp:
            preference = self.lp[lecturer][2]
            all_but_last = preference[:-1]
            tie_successor = []
            for student in all_but_last:
                if random.uniform(0,1) < lecturer_tie_threshold:
                    tie_successor.append(True)
                else:
                    tie_successor.append(False)
            if len(preference) == 1:  # a lecturer having just one student on their preference list -- I doubt this will happen during the random distribution
                self.lp[lecturer].append([preference])
            else:
                self.lp[lecturer].append(tie_successor)
                preference_with_ties = []
                counter = 0
                while counter != len(preference):
                    temp = [preference[counter]]
                    while counter < len(preference) - 1 and tie_successor[counter] != False:
                        counter += 1
                        temp.append(preference[counter])
                    preference_with_ties.append(temp)
                    counter += 1

                self.lp[lecturer].append(preference_with_ties)



    def write_instance_no_tie(self, filename):  # writes the SPA instance to a txt file

        if __name__ == '__main__':
            with open(filename, 'w') as I:

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ...write number of student (n) number of projects (m) number of lecturers (k) ---- for convenience, they are all separated by space
                I.write(str(self.students) + ' ' + str(self.projects) + ' ' + str(self.lecturers) + '\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the students index and their corresponding preferences ---- 1 2 3 1 7
                for n in range(1, self.students + 1):
                    preference = self.sp['s'+str(n)]
                    sliced = [p[1:] for p in preference]
                    I.write(str(n) + ' ')
                    I.writelines('%s ' % p for p in sliced)
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ..write the projects index, its capacity and the lecturer who proposed it ------- 1 5 1
                for m in range(1, self.projects + 1):
                    project = 'p'+str(m)
                    capacity = self.plc[project][0]
                    lecturer = self.plc[project][1][1:]
                    I.write(str(m) + ' ' + str(capacity) + ' ' + str(lecturer))
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the lecturers index, their capacity and their corresponding preferences ---- 1 2 3 1 7
                for k in range(1, self.lecturers + 1):
                    lecturer = 'l'+str(k)
                    capacity = self.lp[lecturer][0]
                    preference = self.lp[lecturer][2]
                    sliced = [p[1:] for p in preference]
                    I.write(str(k) + ' ' + str(capacity) + ' ')
                    I.writelines('%s ' % p for p in sliced)
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------
                I.close()

    def write_instance_with_ties(self, filename):  # writes the SPA instance to a txt file

        if __name__ == '__main__':
            with open(filename, 'w') as I:

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ...write number of student (n) number of projects (m) number of lecturers (k) ---- for convenience, they are all separated by space
                I.write(str(self.students) + ' ' + str(self.projects) + ' ' + str(self.lecturers) + '\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the students index and their corresponding preferences ---- 1 2 3 1 7
                for n in range(1, self.students + 1):
                    preference = self.sp['s'+str(n)][-1]
                    I.write(str(n) + ' ')
                    for tie in preference:
                        if len(tie) == 1:
                            I.write(str(tie[0][1:]) + ' ')
                        else:
                            I.write('(')
                            #print(preference)
                            #print(tie)
                            sliced = [i[1:] for i in tie]
                            #print(sliced)
                            for j in range(len(sliced)-1):
                                I.write(str(sliced[j])+':')
                            I.write(str(sliced[-1])+')' + ' ')
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ..write the projects index, its capacity and the lecturer who proposed it ------- 1 5 1
                for m in range(1, self.projects + 1):
                    project = 'p'+str(m)
                    capacity = self.plc[project][0]
                    lecturer = self.plc[project][1][1:]
                    I.write(str(m) + ' ' + str(capacity) + ' ' + str(lecturer))
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the lecturers index, their capacity and their corresponding preferences ---- 1 2 (3:1) 7
                for k in range(1, self.lecturers + 1):
                    lecturer = 'l'+str(k)
                    capacity = self.lp[lecturer][0]
                    I.write(str(k) + ' ' + str(capacity) + ' ')
                    preference_with_ties = self.lp[lecturer][-1]
                    for tie in preference_with_ties:
                        if len(tie) == 1:
                            I.write(str(tie[0][1:]) + ' ')
                        else:
                            I.write('(')
                            # print(preference)
                            # print(tie)
                            sliced = [i[1:] for i in tie]
                            # print(sliced)
                            for j in range(len(sliced) - 1):
                                I.write(str(sliced[j]) + ':')
                            I.write(str(sliced[-1]) + ')' + ' ')
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------
                I.close()

students = 1000
lower_bound = 50
upper_bound = 50
S = SPASTIG(students, lower_bound, upper_bound)
for i in range(0, 51):
    for j in range(0, 51):
        S.instance_generator_no_tie()
        stie_threshold = 0.005*i
        ltie_threshold = 0.005*j
        filename = '/home/sofiat/Dropbox/Glasgow/projects/spa-st-super-stability/experiments/2a/instance_'
        S.instance_generator_with_ties(stie_threshold, ltie_threshold)
        S.write_instance_with_ties(filename+str(i)+'_'+str(j)+'.txt')




# Experiment 1
# lower_bound = 50
# upper_bound = 50
# stie_threshold = 0.005
# ltie_threshold = 0.005
# for students in range(100, 3100, 100):
#     S = SPASTIG(students, lower_bound, upper_bound)
#     S.instance_generator_no_tie()
#     filename = '/home/sofiat/Dropbox/Glasgow/projects/spa-st-super-stability/experiments/1a/instance_'
#     S.instance_generator_with_ties(stie_threshold, ltie_threshold)
#     S.write_instance_with_ties(filename+str(students)+'.txt')
