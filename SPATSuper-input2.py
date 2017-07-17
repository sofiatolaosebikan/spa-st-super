import sys
import random
from copy import deepcopy


class SPATSUSM:
    def __init__(self):
        """
        Command line input is as follows
        1 - name of the text file to read the instance

        NOTE:
            Pre-designed input works as follows
                ::: tie-oddnumber.txt has no super stable matching
                ::: tie-evennumber.txt has a super stable matching
        """

        self.students = 0
        self.projects = 0
        self.lecturers = 0  # assume number of lecturers <= number of projects
        self.ck = 0  # assume ck >= number of projects
        self.dk = 0  # assume dk >= number of lecturers
        self.infile = sys.argv[1]
        #self.outfile = sys.argv[2]
        self.sp = {}
        self.sp_copy = {}
        self.lp_copy = {}
        self.sp_no_tie = {}
        self.sp_no_tie_deletions = {}
        self.plc = {}
        self.lp = {}
        self.M = {}
        self.project_wstcounter = {}
        self.lecturer_wstcounter = {}
        self.blockingpair = False
        self.multiple_assignment = False
        self.lecturer_capacity_checker = False  # if a lecturer's capacity was full during some iteration and subsequently became under-subscribed
        self.project_capacity_checker = False
        self.full_projects = set()
        self.run_algorithm = True


    def read_file(self):  # reads the SPA instance
        """
        # !* changed type of tie from tuple to list -- tuple does not support item assignment -- at the point we will replace some projects as dp
        The entries in the file is read and it returns the format below which is consequently used to find a matching

        student_preferences = {'s1': [[['p1'], ['p7']], {'p7': (1, 0), 'p1': (0, 0)}],
                                's7': [[['p5', 'p3'], ['p8']], {'p3': (0, 1), 'p5': (0, 0), 'p8': (1, 0)}],
                                's3': [[['p2', 'p1'], ['p4']], {'p2': (0, 0), 'p1': (0, 1), 'p4': (1, 0)}],
                                's4': [[['p2']], {'p2': (0, 0)}],
                                's6': [[['p2', 'p3'], ['p4'], ['p5', 'p6']], {'p3': (0, 1), 'p5': (2, 0), 'p2': (0, 0), 'p6': (2, 1), 'p4': (1, 0)}],
                                's2': [[['p1'], ['p2'], ['p3'], ['p4', 'p5'], ['p6']],
                                    {'p5': (3, 1), 'p6': (4, 0), 'p2': (1, 0), 'p3': (2, 0), 'p1': (0, 0), 'p4': (3, 0)}],
                                's5': [[['p1'], ['p2', 'p3'], ['p4']], {'p3': (1, 1), 'p2': (1, 0), 'p1': (0, 0), 'p4': (2, 0)}]}


        lecturer_preference = {'l1': [3, [['s7'], ['s4', 's1'], ['s2'], ['s3', 's5', 's6']],
                                {'p3': [['s7'], ['s2'], ['s5', 's6']],
                                'p2': [['s4'], ['s2'], ['s3', 's5', 's6']],
                                'p1': [['s1'], ['s2'], ['s3', 's5']]}],

                            'l2': [2, [['s3'], ['s2'], ['s6', 's7'], ['s5']],
                                {'p6': [['s2'], ['s6']],
                                'p5': [['s2'], ['s6', 's7']],
                                'p4': [['s3'], ['s2'], ['s6'], ['s5']]}]}

                            'l3': [2, [['s1'], ['s7']],
                                {'p7': [['s1']],
                                'p8': [['s7']]}],





        project_lecturer_capacity = {'p4': ['l2', 1], 'p1': ['l1', 1], 'p2': ['l1', 1], 'p3': ['l1', 1]}
        """

        with open(self.infile) as t:
            t = t.readlines()
        entry1 = t[0].rstrip(' \n').split(' ')
        self.students, self.projects, self.lecturers = int(entry1[0]), int(entry1[1]), int(entry1[2])

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the student's dictionary

        for i in range(1, self.students+1):
            entry = t[i].rstrip(' \n').split(' ')
            self.sp['s'+str(entry[0])] = []
            self.sp_no_tie['s' + str(entry[0])] = []
            self.sp_no_tie_deletions['s' + str(entry[0])] = set()  # because removing from a set is constant time
            #print(entry[1:])
            for k in entry[1:]:
                if k[0] == '(':
                    split_tie = k.rstrip(')').lstrip('(').split(':')
                    #print(split_tie)
                    tie = ['p'+str(j) for j in split_tie]
                    self.sp['s' + str(entry[0])].append(tie)
                    for j in tie:
                        self.sp_no_tie['s' + str(entry[0])].append(j)
                        self.sp_no_tie_deletions['s' + str(entry[0])].add(j)
                else:
                    self.sp['s' + str(entry[0])].append(['p'+str(k)])
                    self.sp_no_tie['s' + str(entry[0])].append('p' + str(k))
                    self.sp_no_tie_deletions['s' + str(entry[0])].add('p' + str(k))

        # -------------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the projects's dictionary

        for i in range(self.students+1, self.students+1+self.projects):
            entry = t[i].rstrip(' \n').split(' ')
            self.plc['p'+str(entry[0])] = ['l'+str(entry[2]), int(entry[1])]
            self.ck += int(entry[1])
            # -------------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the lecturer's dictionary

        for i in range(self.students+1+self.projects, self.students+1+self.projects+self.lecturers):
            entry = t[i].rstrip(' \n').split(' ')
            self.lp['l' + str(entry[0])] = [int(entry[1]), []]

            for k in entry[2:]:
                if k[0] == '(':
                    split_tie = k.rstrip(')').lstrip('(').split(':')
                    tie = ['s'+str(j) for j in split_tie]
                    self.lp['l' + str(entry[0])][1].append(tie)
                else:
                    self.lp['l' + str(entry[0])][1].append(['s' + str(k)])
            self.dk += int(entry[1])

        # -------------------------------------------------------------------------------------------------------------------
        #  another useful dictionary is created here and attached to the lecturer's dictionary -
        #  the lecturer's ranked preference list according to each project they offer
        #  !*** could it be the case that a lecturer puts two or more student offering different projects in one tie ...?


        """

        """
        for lecturer in self.lp:
            # I am trying to create L_k_j in this for loop..

            d = {}
            s = self.lp[lecturer][1]  # the students preferred by this lecturer   ------ [['s3'], ['s2'], ['s6', 's7'], ['s5']] for lecturer 1
            for project in self.plc:
                if self.plc[project][0] == lecturer:
                    d[project] = []
                    for tie in s:  # Is it the case that a student will not be on the ranked preference of a lecturer - same project in common
                        student_tie = []
                        for student in tie:
                            if project in self.sp_no_tie[student]:
                                student_tie.append(student)
                        if len(student_tie) == 0:
                            continue
                        else:
                            d[project].append(student_tie)
            self.lp[lecturer].append(d)
            self.lp[lecturer].append(False)  # set the capacity checker for all lecturers to False
        # -------------------------------------------------------------------------------------------------------------------

    def algorithm_SPA_S(self):

        self.read_file()

        # -------------------------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------------
        self.project_wstcounter = {'p' + str(i): '' for i in range(1, len(self.plc)+1)}  # worst student pointer for project
        for project in self.project_wstcounter:
            self.project_wstcounter[project] = len(self.lp[self.plc[project][0]][2][project]) - 1  # p1: 2 = 0,1,2
            self.plc[project].append(False)
            self.plc[project].append(set())

        self.lecturer_wstcounter = {'l' + str(i): '' for i in range(1, len(self.lp)+1)}  # worst student pointer for lecturer
        for lecturer in self.lecturer_wstcounter:
            self.lecturer_wstcounter[lecturer] = len(self.lp[lecturer][1]) - 1  # l1: 7

        self.project_length = deepcopy(self.project_wstcounter)  # length of the preferred students for p_j according to l_k
        self.lecturer_length = deepcopy(self.lecturer_wstcounter)  # length of the preferred students for l_k :::::: 0-based

        student_l = len(self.sp)
        student_progress = {'s'+str(i): 0 for i in range(1, student_l+1)}  # keeps track of whether a student's preference list is empty,
        # using a pointer
        student_length = {'s' + str(i): '' for i in range(1, student_l+1)}  # stores the length of each students' preference list
        for student in self.sp:
            rank = {}   # store the index of each project on each student's preference list, for ease of deletion later on in the allocation
            preferences = self.sp[student]  # s7 : [['p5', 'p3'], ['p8']]
            self.sp[student] = []
            length = len(preferences)
            student_length[student] = length - 1  # s7: 2 - 1 = 1 because we are using 0-based index
            for i in range(length):
                pref = preferences[i]
                count_tie = 0
                for p in pref:
                    rank[p] = (i, count_tie)
                    count_tie += 1
            self.sp[student].append(preferences)
            self.sp[student].append(rank)

        self.sp_copy = deepcopy(self.sp)

        """
        print('PROJECT')
        print(self.plc)
        print()
        print('PROJECT-worst-counter')
        print(self.project_wstcounter)
        print()
        print('LECTURER')
        print(self.lp)
        print()
        print('LECTURER-worst-counter')
        print(self.lecturer_wstcounter)
        print()
        print('STUDENT')
        print(self.sp)
        print()
        print('STUDENT-NOTIE')
        print(self.sp_no_tie)
        print()
        """

        self.M = {'s' + str(i): set() for i in range(1, student_l+1)}  # assign all students to free
        unassigned = ['s'+str(i) for i in range(1, student_l+1)]  # keep track of which student is yet to be assigned
        # ------------------------------------------------------------------------------------------------------------------------
        #  -------------------------------------------------ALGORITHM STARTS HERE -------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------
        print(self.project_wstcounter)
        while self.run_algorithm is True:
            while unassigned:  # while some student is unassigned

                student = unassigned.pop(0)  # the student at the tail of the list
                s_preference = self.sp[student][0]  # the projected preference list for this student.. this changes during the allocation process.
                #index = student_progress[student]  # serves as the preference list counter -- to identify the head of the list.

                if student_progress[student] <= student_length[student]:  # if the preference list counter has not been exceeded
                    # store the projects at the head of the list in the variable tie, could be length 1 or more
                    tie = s_preference[student_progress[student]]
                    student_progress[student] += 1  # move the pointer to the next tie on the ordered preference list

                    for first_project in tie:
                        if first_project == 'dp':
                            continue
                        else:
                            lecturer = self.plc[first_project][0]
                            self.M[student].add(first_project) # temporarily assign that student to their first project
                            self.plc[first_project][1] -= 1  # reduce the capacity of the project
                            self.lp[lecturer][0] -= 1  # reduce the lecturer's quota

                            # a lecturer could be full at this point, but the algorithm will not take note of that because if the conditional
                            # statement of a project being oversubscribed is true, then the lecturer could end up undersubscribed before it gets
                            # to line 41 of the pseudocode.
                            #  --------------- I keep track of any lecturer or project that is full at this point before any deletions happen
                            if self.lp[lecturer][0] == 0:  # lecturer is full
                                self.lp[lecturer][3] = True  # set the lecturer's capacity checker to True
                            if self.plc[first_project][1] == 0:  # project is full  ---
                                self.full_projects.add(first_project)
                                self.plc[first_project][2] = True
                            ##### ################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            ###############################################################################################################
                            ###############################################################################################################
                            #  ------------------------------------- IF PROJECT IS OVERSUBSCRIBED -----------------------------------------
                            ###############################################################################################################
                            if self.plc[first_project][1] < 0:  # project is oversubscribed

                                # ----- get the (TAIL) tie of the worst student assigned to this project according to the lecturer offering it----
                                fp_students = self.lp[lecturer][2][first_project]  # students who chose p_j according to Lk -
                                found = False
                                while found is False:  # exit the loop as soon as a worst student assigned to p_j in the tail is found
                                    worst_student_tie = fp_students[self.project_wstcounter[first_project]]  # students who chose p_j according to Lk -
                                    for find_worst_student in worst_student_tie:
                                        if first_project in self.M[find_worst_student]:
                                            found = True
                                            # worst_student = find_worst_student
                                            break  # exit the for loop as soon as a worst student assigned to p_j is found
                                    # if no worst assigned student is found, we decrement the project worst counter and repeat the process again..
                                    if found is False:
                                        self.project_wstcounter[first_project] -= 1

                                # -------- next we delete p_j on the preference list of students contained in the tail of L_k_j --------
                                # what we do is replace p_j with a dummy project dp, to avoid the complexity of .remove from the list.
                                index = self.project_wstcounter[first_project]  # stores the position of the tail in L_k_j
                                tail = fp_students[index]
                                print(tail, index)
                                P_k = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                                for worst_student in tail:
                                    try:
                                        # get the rank of pj on the student's list
                                        # say (2, 0) - 2 is position of strict_successor_tie in L_k_j. 0 is that of successor in strict_successor_tie
                                        p_rank = self.sp[worst_student][1][first_project]
                                        self.sp[worst_student][0][p_rank[0]][p_rank[1]] = 'dp' # we replace the project in this position by a dummy project
                                        self.sp_no_tie_deletions[worst_student].remove(first_project)
                                        self.plc[first_project][3].add(worst_student) # keep track of students who were rejected from first_project
                                    except:
                                        pass
                                    # ---- if the student is provisionally assigned to that project, we break the assignment..
                                    if first_project in self.M[worst_student]:
                                        self.M[worst_student].remove(first_project)  # data structure in use is set to make remove faster..
                                        self.plc[first_project][1] += 1  # increment the project capacity
                                        self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                    # ---- note that if worst_student no longer has any provisional projects, and non-empty preference list
                                    # we add them back to the unassigned list..
                                    if self.M[worst_student] == set() and student_progress[worst_student] <= student_length[worst_student]:
                                        unassigned.append(worst_student)

                                    # if the student no longer has any project in common with the lecturer, we delete all the students in the tail
                                    # and their strict successors on l_k's list.
                                    A_s = self.sp_no_tie_deletions[worst_student]  # the student's altered preference list without ties..
                                    remaining_projects = P_k.intersection(A_s)  # projects the student has in common with the lecturer
                                    print('worst student', worst_student, remaining_projects)
                                    #print(self.project_wstcounter)
                                    #print(self.lecturer_wstcounter)
                                    #print(self.lecturer_length)
                                    print()

                                    #  extra deletions occurs if the next condition is true
                                    # that is, if the student no longer has any project in common with the lecturer
                                    if len(remaining_projects) == 0:
                                        new_index = self.lecturer_wstcounter[lecturer]  # stores the position of worst_student in L_k
                                        lp_students = self.lp[lecturer][1]
                                        print(new_index, self.lecturer_length[lecturer])
                                        while new_index <= self.lecturer_length[lecturer]:  # if that position is exactly the length of L_k's list, we are done..
                                            successor_tie = lp_students[new_index]
                                            print('successors', successor_tie)

                                            for successor in successor_tie:
                                                A_s = set(self.sp_no_tie_deletions[successor])  # the student's unaltered preference list without ties..
                                                common_projects = list(P_k.intersection(A_s))
                                                for project in common_projects:
                                                    try:
                                                        # get the rank of pj on the student's list
                                                        # say (2, 0) - 2 is position of strict_successor_tie in L_k_j. 0 is that of successor in strict_successor_tie
                                                        p_rank = self.sp[successor][1][project]
                                                        self.sp[successor][0][p_rank[0]][p_rank[1]] = 'dp'
                                                        self.sp_no_tie_deletions[successor].remove(project)
                                                    except:
                                                        pass
                                                    if project in self.M[successor]:
                                                        self.M[successor].remove(project)  # data structure in use is set to make remove faster..
                                                        self.plc[project][1] += 1  # increment the project capacity
                                                        self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                                # ---- note that if worst_student no longer has any provisional projects, we add them back to the unassigned list..
                                                if self.M[successor] == set() and student_progress[successor] <= student_length[successor]:
                                                    unassigned.append(successor)
                                            new_index += 1
                                        break

                                # ------- we move the worst student pointer from the tail by decrementing the counter

                            ##############################################################################################################

                            ###############################################################################################################
                            #  ------------------------------------- IF LECTURER IS OVERSUBSCRIBED ---------------------------------------------------
                            ###############################################################################################################
                            elif self.lp[lecturer][0] < 0:  # lecturer is oversubscribed
                                lp_students = self.lp[lecturer][1]  # students who are preferred by
                                # ----- get the (TAIL) tie of the worst student assigned to this lecturer according to L_k
                                found = False
                                while found is False:  # exit the loop as soon as a worst student assigned to l_k is found
                                    worst_student_tie = lp_students[self.lecturer_wstcounter[lecturer]]  # students who chose projects offered by l_k -
                                    for find_worst_student in worst_student_tie:
                                        if self.M[find_worst_student] != set():  # if the student has at least one assigned project
                                            for assigned_project in self.M[find_worst_student]:
                                                if self.plc[assigned_project][0] == lecturer:  # if assigned_project is offered by lecturer
                                                    found = True
                                                    break  # exit the for loop as soon as a worst student assigned to a project offered by l_k is found
                                    # if no worst assigned student is found, we decrement the lecturer's worst counter and repeat the process again..
                                    if found is False:
                                        self.lecturer_wstcounter[lecturer] -= 1
                                # ---------- for each stdent in the tail, delete all the projects they have in common with l_k-------
                                P_k = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                                index = self.lecturer_wstcounter[lecturer]  # stores the position of worst_student in L_k
                                tail = lp_students[index]
                                for worst_student in tail:
                                    A_s = set(self.sp_no_tie[worst_student])  # the student's unaltered preference list without ties..
                                    common_projects = list(P_k.intersection(A_s))
                                    for project in common_projects:
                                        try:
                                            # get the rank of pj on the student's list
                                            # say (2, 0) - 2 is position of strict_successor_tie in L_k_j. 0 is that of successor in strict_successor_tie
                                            p_rank = self.sp[worst_student][1][project]
                                            self.sp_no_tie_deletions[worst_student].remove(project)
                                            self.sp[worst_student][0][p_rank[0]][p_rank[1]] = 'dp'
                                        except:
                                            pass
                                        # ---- if the student is provisionally assigned to that project, we break the assignment..
                                        if project in self.M[worst_student]:
                                            self.M[worst_student].remove(project)  # data structure in use is set to make remove faster..
                                            self.plc[project][1] += 1  # increment the project capacity
                                            self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                    # ---- note that if worst_student no longer has any provisional projects, we add them back to the unassigned list..
                                    if self.M[worst_student] == set() and student_progress[worst_student] <= student_length[worst_student]:
                                        unassigned.append(worst_student)
                                # ------- we move the worst student pointer from the tail by decrementing the counter
                                self.lecturer_wstcounter[lecturer] -= 1
                            ##############################################################################################################

                            ###############################################################################################################
                            #  ------------------------------------- IF PROJECT IS FULL ---------------------------------------------------
                            ###############################################################################################################
                            if self.plc[first_project][1] == 0:  # project is full  ---
                                #self.plc[first_project][2] = True  # keep track of this
                                # get the pointer for the worst student assigned to this project according to the lecturer offering it.
                                fp_students = self.lp[lecturer][2][first_project]  # students who chose p_j according to Lk -
                                found = False
                                while found is False:   # exit the loop as soon as a worst student assigned to p_j is found
                                    worst_student_tie = fp_students[self.project_wstcounter[first_project]]  # students who chose p_j according to Lk -
                                    for find_worst_student in worst_student_tie:
                                        if first_project in self.M[find_worst_student]:
                                            found = True
                                            #worst_student = find_worst_student
                                            break   # exit the for loop as soon as a worst student assigned to p_j is found
                                    # if no worst assigned student is found, we decrement the project worst counter and repeat the process again..
                                    if found is False:
                                        self.project_wstcounter[first_project] -= 1

                                #  next we delete p_j on the preference of students who comes after find_worst_student on p_j's according to L_k
                                # what we do is replace p_j with a dummy project dp
                                index = self.project_wstcounter[first_project]  # stores the position of worst_student in L_k_j
                                while index < self.project_length[first_project]:  # if that position is exactly the length of L_k_j, we are done..
                                    index += 1  # shifts the counter to the strict successors of worst_student
                                    strict_successor_tie = fp_students[index]
                                    for successor in strict_successor_tie:
                                        try:
                                            # get the rank of pj on the student's list
                                            # say (2, 0) - 2 is position of strict_successor_tie in L_k_j. 0 is that of successor in strict_successor_tie
                                            p_rank = self.sp[successor][1][first_project]
                                            self.sp[successor][0][p_rank[0]][p_rank[1]] = 'dp'  # we replace the project in this position by a dummy project
                                            self.sp_no_tie_deletions[successor].remove(first_project)
                                        except:
                                            pass

                            ###############################################################################################################

                            ###############################################################################################################
                            #  ------------------------------------- IF LECTURER IS FULL ---------------------------------------------------
                            ###############################################################################################################
                            if self.lp[lecturer][0] == 0:  # lecturer is full
                                #self.lp[lecturer][3] = True  # set the lecturer's capacity checker to True
                                lp_students = self.lp[lecturer][1]  # students who are preferred by

                                found = False
                                while found is False:  # exit the loop as soon as a worst student assigned to l_k is found
                                    worst_student_tie = lp_students[self.lecturer_wstcounter[lecturer]]  # students who chose projects offered by l_k -
                                    for find_worst_student in worst_student_tie:
                                        if self.M[find_worst_student] != set():  # if the student has at least one assigned project
                                            for assigned_project in self.M[find_worst_student]:
                                                if self.plc[assigned_project][0] == lecturer:  # if assigned_project is offered by lecturer
                                                    found = True
                                                    break  # exit the for loop as soon as a worst student assigned to p_j is found
                                    # if no worst assigned student is found, we decrement the lecturer's worst counter and repeat the process again..
                                    if found is False:
                                        self.lecturer_wstcounter[lecturer] -= 1

                                P_k = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                                index = self.lecturer_wstcounter[lecturer]  # stores the position of worst_student in L_k
                                while index < self.lecturer_length[lecturer]:  # if that position is exactly the length of L_k's list, we are done..
                                    index += 1
                                    strict_successor_tie = lp_students[index]
                                    for successor in strict_successor_tie:
                                        A_s = set(self.sp_no_tie[successor])  # the student's unaltered preference list without ties..
                                        common_projects = list(P_k.intersection(A_s))
                                        for project in common_projects:
                                            try:
                                            # get the rank of pj on the student's list
                                            # say (2, 0) - 2 is position of strict_successor_tie in L_k_j. 0 is that of successor in strict_successor_tie
                                                p_rank = self.sp[successor][1][project]
                                                self.sp[successor][0][p_rank[0]][p_rank[1]] = 'dp'
                                                self.sp_no_tie_deletions[successor].remove(project)
                                            except:
                                                pass
                            ##############################################################################################################

                #########################################################################################################################################
                # !* remember to move to the end
                # !* if the current student is unassigned in the matching, with a non-empty preference list, we re-add the student to the unassigned list
                if self.M[student] == set() and student_progress[student] <= student_length[student]:
                    unassigned.append(student)
                #########################################################################################################################################
            for project in self.full_projects:
                if self.plc[project][0] > 0:
                    # Is l_k's worst assignee strictly worse or no better than s_i (a student who applied to p_j)
                    lecturer = self.plc[project][0]
                    position_worst_tie = self.lecturer_wstcounter[lecturer]
                    # next 4 lines are for debugging purpose
                    worst_students = self.lp[lecturer][1][position_worst_tie][:]
                    # the worst students assigned to l_k in M
                    worst_assignee = [w for w in worst_students if project in self.M[w]]
                    if worst_assignee:
                        worst = worst_assignee.pop()
                    else:
                        worst = None
                    rejected_students = self.plc[project][3]  # rejected students
                    student = rejected_students.pop()
                    # print(student)
                    rejected_students.add(student)
                    # print(rejected_students)
                    # print(self.lp[lecturer])
                    while position_worst_tie >= 0:  # check all the ties of/before the worst assigned tie to see if student is contained there
                        if student in self.lp[lecturer][1][position_worst_tie]:
                            self.project_capacity_checker = True
                            print(project + ' was full but subsequently became under-subscribed.')
                            print('The worst assignee of', lecturer, '(lecturer who offers', project,
                                  '), is strictly worse/no better than', student, '- a student who was denied', project, '!')
                            break  # breaks out of the while loop as soon as 1 student is found!
                        # print(position_worst_tie)
                        position_worst_tie -= 1

        # -------------------------------------------------------------------------------------------------------------------------------
        #   --------------------- No super stable matching exists if A STUDENT IS MULTIPLY ASSIGNED happens -----------------------------
        # -------------------------------------------------------------------------------------------------------------------------------
        for student in self.M:
            if len(self.M[student]) > 1:
                print(student + ' is assigned to ' + str(len(self.M[student])) + ' projects.')
                self.multiple_assignment = True
                break

        # -------------------------------------------------------------------------------------------------------------------------------
        #   --------------------- No super stable matching exists if a LECTURER WAS FULL and subsequently UNDER-SUBSCRIBED --------------
        # -------------------------------------------------------------------------------------------------------------------------------
        if self.multiple_assignment is False:
            for lecturer in self.lp:
                if self.lp[lecturer][0] > 0 and self.lp[lecturer][3] is True:  # lecturer's capacity is under-subscribed but was previously full
                    self.lecturer_capacity_checker = True
                    #print(lecturer + ' was full but subsequently ends up under-subscribed.')
                    P_k = [i for i in self.lp[lecturer][2].keys()]  # all the projects that lecturer is offering
                    for project in P_k:
                        if self.plc[project][1] > 0 and self.plc[project][2] is True:
                            self.project_capacity_checker = True
                            print(lecturer + ' and ' + project + ' was full but subsequently ends up under-subscribed.')
                            break
                    break




# -------------------------------------------------------------------------------------------------------------------------------
#   --------------------- BLOCKING PAIR CRITERIA ----------------------
# -------------------------------------------------------------------------------------------------------------------------------
    def blockingpair1(self, project, lecturer): ##################
        #  project and lecturer are both under-subscribed
        if self.plc[project][1] > 0 and self.lp[lecturer][0] > 0:
            self.blockingpair = True

    def blockingpair2a(self, student, project, lecturer, matched_project):
        #  project is under-subscribed, lecturer is full and s_i is in M(l_k)
        #  that is, student is matched to a project offered by l_k
        if self.plc[project][1] > 0 and self.lp[lecturer][0] == 0 and self.plc[matched_project][0] == lecturer:
            self.blockingpair = True

    def blockingpair2b(self, student, project, lecturer): #####################
        #  project is under-subscribed, lecturer is full and l_k strictly prefers s_i to its worst student in M(l_k) or is indifferent between them
        if self.plc[project][1] > 0 and self.lp[lecturer][0] == 0:
            # check if s_i's tie is in a position with/before l_k's worst assigned student's tie
            position_worst_tie = self.lecturer_wstcounter[lecturer]
            while position_worst_tie >= 0: # check all the ties of/before the worst assigned tie to see if student is contained there
                if student in self.lp[lecturer][1][position_worst_tie]:
                    self.blockingpair = True
                    break  # breaks out of the while loop as soon as 1 student is found!
                position_worst_tie -= 1

    def blockingpair3(self, student, project, lecturer):
        #  project is full and lecturer prefers s_i to the worst student assigned to M(p_j) or is indifferent between them
        if self.plc[project][1] == 0:
            position_worst_tie = self.project_wstcounter[project]
            while position_worst_tie >= 0:  # check all the ties of/before the worst assigned tie to see if student is contained there
                if student in self.lp[lecturer][2][project][position_worst_tie]:
                    self.blockingpair = True
                    break  # breaks out of the while loop as soon as 1 student is found!
                position_worst_tie -= 1


# -------------------------------------------------------------------------------------------------------------------------------
#   ----------------- FIND BLOCKING PAIR ---------- If one exist, self.blockingpair is set to True and this bit halts .. ---
# -------------------------------------------------------------------------------------------------------------------------------

    def check_stability(self):
        for student in self.M:
            if self.M[student] == set():  # if student s_i is not assigned in M, we check if it forms a blocking pair with all the projects in A(s_i).
                p = self.sp_no_tie[student]  # list of pj's wrt to s_i s6 = ['p2', 'p3', 'p4', 'p5', 'p6']
                for project in p:
                    lecturer = self.plc[project][0]  # l_k

                    self.blockingpair1(project, lecturer)  #project and lecturer is under-subscribed
                    if self.blockingpair is True:
                        break

                    self.blockingpair2b(student, project, lecturer) #project is under-subscribed lecturer is full
                    if self.blockingpair is True:
                        break

                    self.blockingpair3(student, project, lecturer)
                    if self.blockingpair is True:
                        break

            else:  # if student s_i is matched to a project in M
                matched_project = self.M[student].pop()  # get the matched project
                self.M[student].add(matched_project)
                rank_matched_project = self.sp_copy[student][1][matched_project]  # find its rank on s_i's preference list A(s_i)
                p_list = self.sp_copy[student][0]  # list of pj's wrt to s_i      # a copy of A(s_i)
                temp = rank_matched_project[0]  #position of the tie of the matched project in the list
                preferred_projects = set()  # projects that student strictly prefers to her matched project or indifferent between..
                while temp >= 0:
                    keep = set([p for p in p_list[temp] if p is not matched_project])
                    preferred_projects.update(keep)
                    temp -= 1

                for project in preferred_projects:
                    lecturer = self.plc[project][0]  # l_k

                    self.blockingpair1(project, lecturer)   # project and lecturer is under-subscribed
                    if self.blockingpair is True:
                        break

                    self.blockingpair2a(student, project, lecturer, matched_project)  # project is under-subscribed lecturer is full
                    if self.blockingpair is True:
                        break

                    self.blockingpair2b(student, project, lecturer)  # project is under-subscribed lecturer is full
                    if self.blockingpair is True:
                        break

                    self.blockingpair3(student, project, lecturer)
                    if self.blockingpair is True:
                        break

# -------------------------------------------------------------------------------------------------------------------------------
#  -------------------- Writes the matching to a text file, the first line verifies that that the matching is stable / not :|
# -------------------------------------------------------------------------------------------------------------------------------
    def runAlgorithm(self):

        if __name__ == '__main__':
            self.algorithm_SPA_S()

            # -------------------------------------------------------------------------------------------------------------------------------
            # ~~~~~~~ OUTPUT NO SUPER STABLE MATCHING EXISTS IF ANY OF THE CONDITIONS ABOVE IS TRUE ::: OTHERWISE OUTPUT THE MATCHING ~~~~~~~
            # -------------------------------------------------------------------------------------------------------------------------------

            if self.multiple_assignment is True or self.lecturer_capacity_checker is True:
                print()
                print('No super-stable matching exists! Final assignment relation is .. ')
                return self.M

            else:
                self.check_stability()
                if self.blockingpair is True:
                    print('Reason is UNKNOWN!!!')
                    print('No super-stable matching exists! Final assignment relation is .. ')
                    return self.M

            if self.multiple_assignment is False and self.lecturer_capacity_checker is False and self.blockingpair is False:
                print('Matching is Super-Stable')
                return self.M

        # If I un assign a student who has been previously assigned, corresponding matching should be unstable
        # print(self.M['s3'])
        # self.M['s3'] = ''

        """
        with open(self.outfile, 'w') as O:
            for _ in range(1):
                if self.blockingpair is True:
                    O.write('Matching is not stable\n')
                    print('Algorithm fails')
                    break
                else:
                    O.write('Matching is stable\n')

                l = len(self.M)
                for i in range(1, l+1):
                    if self.M['s'+str(i)][1:] == '':
                        O.write(str(i)+'\n')
                    else:
                        O.write(str(i) + ' ' + str(self.M['s'+str(i)][1:]) + '\n')

                O.close()
        """

# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
s = SPATSUSM()
print(s.runAlgorithm())


"""
's6': [ ['p2', 'p3', 'p4', 'p5', 'p6']  ---- preference list
        [['p2', 'p3'], ['p4'], ['p5', 'p6']],   ------ ordered preference list with ties
        {'p2': (0, 0), 'p6': (2, 1), 'p5': (2, 0), 'p4': (1, 0), 'p3': (0, 1)}  ---------- project ranks
    ],

's4': [ ['p2']
        [['p2']],
        {'p2': (0, 0)}
    ],

's2': [ ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        [['p1'], ['p2'], ['p3'], ['p4', 'p5'], ['p6']],
        {'p1': (0, 0), 'p5': (3, 1), 'p3': (2, 0), 'p2': (1, 0), 'p6': (4, 0), 'p4': (3, 0)}
    ],

's5': [ ['p1', 'p2', 'p3', 'p4']
        [['p1'], ['p2', 'p3'], ['p4']],
        {'p1': (0, 0), 'p2': (1, 0), 'p4': (2, 0), 'p3': (1, 1)}
    ],

's7': [ ['p3', 'p5', 'p8', 'p4']
        [['p3', 'p5'], ['p8', 'p4']],
        {'p5': (0, 1), 'p4': (1, 1), 'p8': (1, 0), 'p3': (0, 0)}
    ],

's3': [ ['p2', 'p1', 'p4']
        [['p2', 'p1'], ['p4']],
        {'p2': (0, 0), 'p1': (0, 1), 'p4': (1, 0)}
    ],

's1': [ ['p1']
        [['p1']],
        {'p1': (0, 0)}
    ]


        # ----------------------------------------------------------------------------------------------------------------------------------
        #   --------------------- No super stable matching exists if a PROJECT WAS OVERSUBSCRIBED and subsequently UNDER-SUBSCRIBED --------
        # ----------------------------------------------------------------------------------------------------------------------------------
        if self.multiple_assignment is False and self.lecturer_capacity_checker is False:
            for project in self.plc:
                if self.plc[project][1] > 0 and self.plc[project][2] is True:  # project's capacity is under-subscribed but was previously full

                    # Is l_k's worst assignee strictly worse or no better than s_i (a student who applied to p_j)
                    lecturer = self.plc[project][0]
                    position_worst_tie = self.lecturer_wstcounter[lecturer]
                    # next 4 lines are for debugging purpose
                    worst_students = self.lp[lecturer][1][position_worst_tie][:]
                    # the worst students assigned to l_k in M
                    worst_assignee = [w for w in worst_students if project in self.M[w]]
                    if worst_assignee:
                        worst = worst_assignee.pop()
                    else:
                        worst = None
                    rejected_students = self.plc[project][3]  # rejected students
                    student = rejected_students.pop()
                    #print(student)
                    rejected_students.add(student)
                    # print(rejected_students)
                    # print(self.lp[lecturer])
                    while position_worst_tie >= 0:  # check all the ties of/before the worst assigned tie to see if student is contained there
                        if student in self.lp[lecturer][1][position_worst_tie]:
                            self.project_capacity_checker = True
                            print(project + ' was full but subsequently became under-subscribed.')
                            print('The worst assignee of', lecturer,'(lecturer who offers', project,
                                  '), is strictly worse/no better than', student, '- a student who was denied', project,'!')
                            break  # breaks out of the while loop as soon as 1 student is found!
                        #print(position_worst_tie)
                        position_worst_tie -= 1

                    break
"""