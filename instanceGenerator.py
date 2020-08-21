import random
import math


class SPAST:
    def __init__(self, students, pref_list_length_lb=2, pref_list_length_ub=2, student_tie_density=0, lecturer_tie_density=0):
        """
        A program that writes to a .txt file, a randomly-generated instance of the student project allocation problem 
        with students preferences over projects, lecturers preferences over students, and with ties.
        
        
        It takes argument as follows:
            number of students
            lower bound of the students' preference list length
            upper bound of the students' preference list length
            the density of tie in the students preference list 
            the density of tie in the lecturers preference list
        
        * the density of tie in the preference lists is a number between 0 and 1 (inclusive)
        if the tie density is 0 on both sides, then the program writes an instance of SPA-S without ties
        if the tie density is 1 on both sides, then the program writes an instance of SPA-ST, where 
        each preference list is a single tie of length 1....
        
        * the tie density given is the probability (decided at random) that a project (or student) will be tied
        with its successor.
        
        """
        self.students = students
        self.projects = int(math.ceil(0.5*self.students))
        self.lecturers = int(math.ceil(0.2*self.students))  # assume number of lecturers <= number of projects
        self.tpc = int(math.ceil(1.2*self.students))  # assume total project capacity >= number of projects #        
        self.li = pref_list_length_lb  # lower bound of the student's preference list
        self.lj = pref_list_length_ub  # int(sys.argv[3])  # upper bound of the student's preference list
        self.student_tie_density = student_tie_density
        self.lecturer_tie_density = lecturer_tie_density
        
        self.sp = {}
        self.plc = {}
        self.lp = {}

    def instance_generator_no_ties(self):

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------        ====== PROJECTS =======                    -----------------------------------------------
        # here we decide the capacity for each project, in such a way that each project has capacity >= 1
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # projects have [at least capacity 1, empty string to assign lecturer, empty list to store students]
        self.plc = {'p'+str(i): [1, '', []] for i in range(1, self.projects+1)}
        project_list = list(self.plc.keys())
        # randomly assign the remaining project capacities
        for i in range(self.tpc - self.projects):  # range(9 - 8) = range(1) = 1 iteration. Okay!
            self.plc[random.choice(project_list)][0] += 1
            
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------        ====== STUDENTS =======                    -----------------------------------------------
        # here we decide the length l of each student's preference list
        # we also choose l projects at random, which forms the student's preference list
        # -----------------------------------------------------------------------------------------------------------------------------------------
        self.sp = {'s' + str(i): [[]] for i in range(1, self.students + 1)}  # stores randomly selected projects
        for student in self.sp:
            length = random.randint(self.li, self.lj)  # randomly decide the length of each student's preference list
            #  based on the length of their preference list, we provide projects at random
            projects_copy = project_list[:]            
            for i in range(length):
                random.shuffle(projects_copy)
                p = projects_copy.pop()
                #projects_copy.remove(p)  # I did this to avoid picking the same project 2x. This could also be achieved by shuffling and popping?
                self.sp[student][0].append(p)
                self.plc[p][2].append(student)

        # the next for loop ensures that each project is ranked by at least one student
        student_list = [s for s in self.sp.keys()]
        for project in self.plc:
            if self.plc[p][2] == []:
                random.shuffle(student_list)
                random_student = student_list.pop() # since students > projects, we will not run out of students
                random_project = self.sp[random_student][0].pop()
                self.plc[random_project][2].remove(random_student)
                
                self.sp[random_student][0].append(project)
                self.plc[project][2].append(random_student)
                
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
            for _ in range(number_of_projects):
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

    def instance_generator_with_ties(self):

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- ========= TIES IN STUDENTS LIST ========= --------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        for student in self.sp:            
            preference = self.sp[student][0][:]            
            # to decide if a project will be tied with its successor..
            # if student_tie_density = 0, no tie in the preference list
            # if student_tie_density = 1, the preference list is a single tie
            preference_with_ties = [[preference[0]]]
            for project in preference[1:]:
                if random.uniform(0,1) <= self.student_tie_density:
                    preference_with_ties[-1].append(project)
                else:
                    preference_with_ties.append([project])
            self.sp[student].append(preference_with_ties)
                
           
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- ========= TIES IN LECTURERS LIST ========= --------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------
        for lecturer in self.lp:
            preference = self.lp[lecturer][2][:]
            # if len(preference) == 0:
            #     print(self.lp, '\n', lecturer, preference)
            preference_with_ties = [[preference[0]]]
            for student in preference[1:]:
                if random.uniform(0,1) <= self.lecturer_tie_density:
                    preference_with_ties[-1].append(student)
                else:
                    preference_with_ties.append([student])
            self.lp[lecturer].append(preference_with_ties)
            



    def write_instance_no_ties(self, filename):  # writes the SPA-S instance to a txt file

        if __name__ == '__main__':
            
            self.instance_generator_no_ties()
            
            with open(filename, 'w') as I:

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ...write number of student (n) number of projects (m) number of lecturers (k) ---- for convenience, they are all separated by space
                I.write(str(self.students) + ' ' + str(self.projects) + ' ' + str(self.lecturers) + '\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the students index and their corresponding preferences ---- 1 2 3 1 7
                for n in range(1, self.students + 1):
                    preference = self.sp['s'+str(n)][0]
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

    def write_instance_with_ties(self, filename):  # writes the SPA-ST instance to a txt file

        if __name__ == '__main__':
            
            self.instance_generator_no_ties()
            self.instance_generator_with_ties()
            
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



students = 10
pref_list_length = 3
s_tie_density, l_tie_density = 0.05, 0.25
for k in range(1, 10001):
    S = SPAST(students, pref_list_length, pref_list_length, s_tie_density, l_tie_density)    
    file = 'instance'+str(k)+'.txt'
    filename = 'rg_instances/'+ file
    S.write_instance_with_ties(filename)
