from readinputSPAT import RISPAT
from copy import deepcopy
from gurobipy import *

class SPATSUPER:
    def __init__(self):
        """
        Command line input is as follows
        1 - name of the text file to read the instance

        NOTE:
            Pre-designed input works as follows
                ::: tie-oddnumber.txt has no super stable matching
                ::: tie-evennumber.txt has a super stable matching
        """
        r = RISPAT()
        r.read_file()
        self.sp = r.sp
        self.sp_copy = r.sp_copy
        self.lp_copy = r.lp_copy
        self.sp_no_tie = r.sp_no_tie
        self.sp_no_tie_deletions = r.sp_no_tie_deletions
        self.plc = r.plc
        self.lp = r.lp
        self.student_length = r.student_length

        self.ck = 0  # assume ck >= number of projects
        self.dk = 0  # assume dk >= number of lecturers
        self.M = {}
        self.project_wstcounter = {}
        self.lecturer_wstcounter = {}

        self.multiple_assignment = False
        self.lecturer_capacity_checker = False  # if a lecturer's capacity was full during some iteration and subsequently became under-subscribed
        self.project_capacity_checker = False
        self.full_projects = set()
        self.run_algorithm = True
        self.blockingpair = False

        #ssc = SUPERSTABILITY()
        #self.blockingpair = ssc.blockingpair

    def algorithm(self):
        # -------------------------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------------
        self.project_wstcounter = {'p' + str(i): '' for i in range(1, len(self.plc)+1)}  # worst student pointer for projects
        for project in self.project_wstcounter:
            self.project_wstcounter[project] = len(self.lp[self.plc[project][0]][2][project]) - 1  # p1: 2 = 0,1,2
            self.plc[project].append(False)  # set all project capacity to False
            self.plc[project].append(set())   # to keep track of students that was rejected from project

        self.lecturer_wstcounter = {'l' + str(i): '' for i in range(1, len(self.lp)+1)}  # worst student pointer for lecturer
        for lecturer in self.lecturer_wstcounter:
            self.lecturer_wstcounter[lecturer] = len(self.lp[lecturer][1]) - 1  # l1: 7

        self.project_length = deepcopy(self.project_wstcounter)  # length of the preferred students for p_j according to l_k
        self.lecturer_length = deepcopy(self.lecturer_wstcounter)  # length of the preferred students for l_k :::::: 0-based

        student_l = len(self.sp)
        student_progress = {'s'+str(i): 0 for i in range(1, len(self.sp)+1)}  # keeps track of whether a student's preference list is empty,
        # using a pointer
        #student_length = {'s' + str(i): '' for i in range(1, student_l+1)}  # stores the length of each students' preference list

        self.M = {'s' + str(i): set() for i in range(1, student_l+1)}  # assign all students to free
        unassigned = ['s'+str(i) for i in range(1, student_l+1)]  # keep track of which student is yet to be assigned
        # ------------------------------------------------------------------------------------------------------------------------
        #  -------------------------------------------------ALGORITHM STARTS HERE -------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------------
        count_running = 1  # debugging purpose, to know the number of times the while loop is repeated..
        while self.run_algorithm is True:
            self.run_algorithm = False
            print('run while loop -', count_running)
            while unassigned:  # while some student is unassigned
                student = unassigned.pop(0)  # the student at the tail of the list ::: super-stable matching is the same irrespective of which student is chosen first
                s_preference = self.sp[student][0]  # the projected preference list for this student.. this changes during the allocation process.

                if student_progress[student] <= self.student_length[student]:  # if the preference list counter has not been exceeded
                    # store the projects at the head of the list in the variable tie, could be length 1 or more
                    tie = s_preference[student_progress[student]]
                    student_progress[student] += 1  # move the pointer to the next tie on the student's ordered preference list

                    for first_project in tie:
                        if first_project == 'dp':
                            continue
                        else:
                            lecturer = self.plc[first_project][0]
                            self.M[student].add(first_project)  # provisionally assign the first_project to student
                            self.plc[first_project][1] -= 1  # reduce the capacity of first_project
                            self.lp[lecturer][0] -= 1  # reduce the capacity of lecturer
                            ##################################################################################################################
                            #  ------------------------------------- IF PROJECT IS OVERSUBSCRIBED --------------------------------------------
                            ##################################################################################################################
                            if self.plc[first_project][1] < 0:  # project is oversubscribed
                                # ----- get the (TAIL) tie of the worst student assigned to this project according to the lecturer offering it----
                                fp_students = self.lp[lecturer][2][first_project]  # students who chose p_j according to Lk -
                                found = False
                                while found is False:  # exit the loop as soon as a worst student assigned to p_j in the tail is found
                                    worst_student_tie = fp_students[self.project_wstcounter[first_project]]  # students who chose p_j according to Lk -
                                    for find_worst_student in worst_student_tie:
                                        if first_project in self.M[find_worst_student]:
                                            found = True
                                            break  # exit the for loop as soon as a worst student assigned to p_j is found
                                    # if no worst assigned student is found, we decrement the project worst counter and repeat the process again..
                                    if found is False:
                                        self.project_wstcounter[first_project] -= 1

                                # -------- next we delete first_project on the preference list of students contained in the tail of L_k_j --------
                                # what we do is replace first_project with a dummy project dp, to avoid the complexity of .remove from the list.
                                index = self.project_wstcounter[first_project]  # stores the position of the tail in L_k_j
                                tail = fp_students[index]
                                for worst_student in tail:
                                    try:
                                        # get the rank of pj on the student's list
                                        # say (2, 0) :::: 2 is position of the tie containing first_project on student's ordered preference list
                                        # while 0 is the position of first_project in the tie
                                        p_rank = self.sp[worst_student][1][first_project]
                                        self.sp[worst_student][0][p_rank[0]][p_rank[1]] = 'dp'  # we replace the project in this position by a dummy project
                                        self.sp_no_tie_deletions[worst_student].remove(first_project)  # removing from a set is O(1)
                                        #self.plc[first_project][3][worst_student] = self.lecturer_wstcounter[lecturer]  # keep track of students who were rejected from first_project
                                        self.plc[first_project][3].add(worst_student)  # keep track of students who were rejected from first_project
                                    except:
                                        pass
                                    # ---- if the student is provisionally assigned to that project, we break the assignment..
                                    if first_project in self.M[worst_student]:
                                        self.M[worst_student].remove(first_project)  # data structure in use is set to make remove fast..
                                        self.plc[first_project][1] += 1  # increment the project capacity
                                        self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                    # ---- note that if worst_student no longer has any provisional projects, and non-empty preference list
                                    # we add them back to the unassigned list..
                                    if self.M[worst_student] == set() and student_progress[worst_student] <= self.student_length[worst_student]:
                                        unassigned.append(worst_student)

                                # ------- we move the worst student pointer from the tail by decrementing the counter
                                self.project_wstcounter[first_project] -= 1
                            ##############################################################################################################

                            ###############################################################################################################
                            #  ------------------------------------- IF LECTURER IS OVERSUBSCRIBED ---------------------------------------------------
                            ###############################################################################################################
                            elif self.lp[lecturer][0] < 0:  # lecturer is oversubscribed
                                lp_students = self.lp[lecturer][1]  # the lecturer's ordered preference list
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
                                # ---------- for each student in the tail, delete all the projects they have in common with l_k-------
                                P_k = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                                index = self.lecturer_wstcounter[lecturer]  # stores the position of worst_student in L_k
                                tail = lp_students[index]
                                for worst_student in tail:
                                    A_s = set(self.sp_no_tie[worst_student])  # the student's unaltered preference list without ties.. !!** why not self.sp_no_tie_deletions??
                                    common_projects = list(P_k.intersection(A_s))
                                    for project in common_projects:
                                        try:
                                            # get the rank of pj on the student's list
                                            # say (2, 0) :::: 2 is position of the tie containing first_project on student's ordered preference list
                                            # while 0 is the position of first_project in the tie
                                            p_rank = self.sp[worst_student][1][project]
                                            self.sp_no_tie_deletions[worst_student].remove(project)
                                            self.sp[worst_student][0][p_rank[0]][p_rank[1]] = 'dp'
                                            self.plc[project][3].add(worst_student)  # keep track of students who were rejected from this project
                                        except:
                                            pass
                                        # ---- if the student is provisionally assigned to that project, we break the assignment..
                                        if project in self.M[worst_student]:
                                            self.M[worst_student].remove(project)  # data structure in use is set to make remove faster..
                                            self.plc[project][1] += 1  # increment the project capacity
                                            self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                    # ---- note that if worst_student no longer has any provisional projects, we add them back to the unassigned list..
                                    if self.M[worst_student] == set() and student_progress[worst_student] <= self.student_length[worst_student]:
                                        unassigned.append(worst_student)
                                # ------- we move the worst student pointer from the tail by decrementing the counter
                                self.lecturer_wstcounter[lecturer] -= 1
                            ##############################################################################################################

                            ###############################################################################################################
                            #  ------------------------------------- IF PROJECT IS FULL ---------------------------------------------------
                            ###############################################################################################################
                            if self.plc[first_project][1] == 0:  # project is full  ---
                                self.plc[first_project][2] = True  # keep track of this
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
                                            # self.plc[first_project][3].add(successor)  # keep track of students who were rejected from first_project
                                        except:
                                            pass
                            ###############################################################################################################
                            ###############################################################################################################
                            #  ------------------------------------- IF LECTURER IS FULL ---------------------------------------------------
                            ###############################################################################################################
                            if self.lp[lecturer][0] == 0:  # lecturer is full
                                self.lp[lecturer][3] = True  # set the lecturer's capacity checker to True
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
                                                p_rank = self.sp[successor][1][project]
                                                self.sp[successor][0][p_rank[0]][p_rank[1]] = 'dp'
                                                self.sp_no_tie_deletions[successor].remove(project)
                                                #  self.plc[project][3].add(successor)  # keep track of students who were rejected from project

                                            except:
                                                pass
                            ##############################################################################################################

                #########################################################################################################################################
                # !* remember to move to the end
                # !* if the current student is unassigned in the matching, with a non-empty preference list, we re-add the student to the unassigned list
                if self.M[student] == set() and student_progress[student] <= self.student_length[student]:
                    unassigned.append(student)
                #########################################################################################################################################

            ###############################################################################################################################################
            # --- At this point, the current execution of the while loop is done and all unassigned students has an empty list..
            # loop, and if the lecturer l_k offering p_j strictly prefers/is indifferent between any of the students rejected from p_j to its worst
            # assigned student at this point of the algorithm, we perform some additional set of deletions...
            ###############################################################################################################################################
            for project in self.plc:
                if self.plc[project][1] > 0 and self.plc[project][2] is True:
                    # Is l_k's worst assignee strictly worse or no better than s_i (any student who was rejected from p_j)
                    lecturer = self.plc[project][0]
                    P_k = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                    position_worst_tie = self.lecturer_wstcounter[lecturer]

                    worst_students = self.lp[lecturer][1][position_worst_tie][:]  # worst students at the tail of L_k
                    # the worst students assigned to l_k in M, since some students at the tail could be assigned to some other lecturer in M
                    worst_assignee = []
                    for w in worst_students:
                        if any(p in self.M[w] for p in P_k):
                            worst_assignee.append(w)
                    if len(worst_assignee) > 0:
                        rejected_students = self.plc[project][3]  # rejected students
                        while (position_worst_tie) >= 0:  # check all the ties of/before the worst assigned tie to see if any student rejected from p_j offered by l_k is contained there
                            if any(student in self.lp[lecturer][1][position_worst_tie] for student in rejected_students):
                                self.run_algorithm = True
                                count_running += 1
                                break
                            position_worst_tie -= 1
                        # delete all the projects worst assignees and strict successors has in common with the lecturer
                        if self.run_algorithm is True:
                            self.plc[project][2] = False
                            index = self.lecturer_wstcounter[lecturer]
                            while index <= self.lecturer_length[lecturer]:
                                for student in self.lp[lecturer][1][index]:
                                    A_s = set(self.sp_no_tie[student])  # the student's unaltered preference list without ties..
                                    common_projects = list(P_k.intersection(A_s))
                                    for project in common_projects:
                                        try:
                                            p_rank = self.sp[student][1][project]
                                            self.sp_no_tie_deletions[student].remove(project)
                                            self.sp[student][0][p_rank[0]][p_rank[1]] = 'dp'
                                            self.plc[project][3].add(student)
                                        except:
                                            pass
                                        # ---- if the student is provisionally assigned to that project, we break the assignment..
                                        if project in self.M[student]:
                                            self.M[student].remove(project)  # data structure in use is set to make remove faster..
                                            self.plc[project][1] += 1  # increment the project capacity
                                            self.lp[lecturer][0] += 1  # increment the lecturer capacity
                                    # ---- if the worst_student no longer has any provisional projects, but has a non-empty preference list
                                    #  we add them back to the unassigned list..
                                    if self.M[student] == set() and student_progress[student] <= self.student_length[student]:
                                        unassigned.append(student)
                                        # print('unassigned students', unassigned)

                                index += 1

        #####################################################################################################################################################
        # If our final assignment relation has any of these three conditions, we can safely report that no super-stable matching exists in the given instance
        #####################################################################################################################################################

        # -------------------------------------------------------------------------------------------------------------------------------
        #   --------------------- 1 ::::  A STUDENT IS MULTIPLY ASSIGNED  -----------------------------
        # -------------------------------------------------------------------------------------------------------------------------------
        for student in self.M:
            if len(self.M[student]) > 1:
                print(student + ' is assigned to ' + str(len(self.M[student])) + ' projects.')
                self.multiple_assignment = True
                break

        # -------------------------------------------------------------------------------------------------------------------------------
        #   --------------------- 2 :::: A LECTURER WAS FULL at some point and subsequently ends up UNDER-SUBSCRIBED --------------
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
        #   ----------- 3 :::: A PROJECT WAS REJECTED FROM A STUDENT at some point and subsequently p_j, l_k ends up UNDER-SUBSCRIBED --
        # -------------------------------------------------------------------------------------------------------------------------------
        if self.multiple_assignment is False and self.lecturer_capacity_checker is False:
            for project in self.plc:
                lecturer = self.plc[project][0]
                # project, lecturer's capacity is under-subscribed.. and project was previously rejected from some student
                if len(self.plc[project][3]) != 0 and self.lp[lecturer][0] > 0 and self.plc[project][1] > 0:
                    self.project_capacity_checker = True
                    #print(lecturer + ', ' + project + ' is under-subscribed.')
                    print(project, 'was deleted from', self.plc[project][3], '\'s preference list')
                    break

############################################################################################################################################
############################################################################################################################################

    ############################################################################################################################################
    #  ---- If the three conditions above does not halt the algorithm, verify the matching is super-stable by making sure no (student, project)
    #  pair blocks the assignment relation...
    ############################################################################################################################################
    #  -------------------------------------------------------------------------------------------------------------------------------
    #   --------------------- BLOCKING PAIR CRITERIA ----------------------
    # -------------------------------------------------------------------------------------------------------------------------------
    def blockingpair1(self, project, lecturer):
        #  project and lecturer are both under-subscribed
        if self.plc[project][1] > 0 and self.lp[lecturer][0] > 0:
            self.blockingpair = True

    def blockingpair2a(self, student, project, lecturer, matched_project):
        #  project is under-subscribed, lecturer is full and s_i is in M(l_k)
        #  that is, student is matched to a project offered by l_k
        if self.plc[project][1] > 0 and self.lp[lecturer][0] == 0 and self.plc[matched_project][0] == lecturer:
            self.blockingpair = True

    def blockingpair2b(self, student, project, lecturer):
        #  project is under-subscribed, lecturer is full and l_k strictly prefers s_i to its worst student in M(l_k) or is indifferent between them
        if self.plc[project][1] > 0 and self.lp[lecturer][0] == 0:
            # check if s_i's tie is in a position with/before l_k's worst assigned student's tie
            position_worst_tie = self.lecturer_wstcounter[lecturer]
            while position_worst_tie >= 0:  # check all the ties of/before the worst assigned tie to see if student is contained there
                if student in self.lp[lecturer][1][position_worst_tie]:
                    self.blockingpair = True
                    break  # breaks out of the while loop as soon as that student is found!
                position_worst_tie -= 1

    def blockingpair3(self, student, project, lecturer):
        #  project is full and lecturer prefers s_i to the worst student assigned to M(p_j) or is indifferent between them
        if self.plc[project][1] == 0:
            position_worst_tie = self.project_wstcounter[project]
            while position_worst_tie >= 0:  # check all the ties of/before the worst assigned tie to see if student is contained there
                if student in self.lp[lecturer][2][project][position_worst_tie]:
                    self.blockingpair = True
                    break  # breaks out of the while loop as soon as that student is found!
                position_worst_tie -= 1
    # -------------------------------------------------------------------------------------------------------------------------------
    #   ----------------- FIND BLOCKING PAIR ---------- If one exist, self.blockingpair is set to True and this bit halts .. ---
    # -------------------------------------------------------------------------------------------------------------------------------

    def check_stability(self):
        for student in self.M:
            if self.M[student] == set():  # if student s_i is not assigned in M, we check if it forms a blocking pair with all the projects in A(s_i).
                preferred_projects = self.sp_no_tie[student]  # list of pj's wrt to s_i s6 = ['p2', 'p3', 'p4', 'p5', 'p6']

            else:  # if student s_i is matched to a project in M
                matched_project = self.M[student].pop()  # get the matched project
                self.M[student].add(matched_project)
                rank_matched_project = self.sp_copy[student][1][matched_project]  # find its rank on s_i's preference list A(s_i)
                p_list = self.sp_copy[student][0]  # list of pj's wrt to s_i      # a copy of A(s_i)
                temp = rank_matched_project[0]  # position of the tie of the matched project in the list
                preferred_projects = set()  # projects that student strictly prefers to her matched project or indifferent between..
                while temp >= 0:
                    keep = set([p for p in p_list[temp] if p is not matched_project])
                    preferred_projects.update(keep)
                    temp -= 1

            for project in preferred_projects:
                lecturer = self.plc[project][0]  # l_k

                self.blockingpair1(project, lecturer)  # project and lecturer is under-subscribed
                if self.blockingpair is True:
                    break

                if self.M[student] != set():  # this is the only blocking pair difference between a matched and unmatched student..
                    matched_project = self.M[student].pop()  # get the matched project
                    self.M[student].add(matched_project)
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
            self.algorithm()
            # -------------------------------------------------------------------------------------------------------------------------------
            # ~~~~~~~ OUTPUT NO SUPER STABLE MATCHING EXISTS IF ANY OF THE CONDITIONS ABOVE IS TRUE ::: OTHERWISE OUTPUT THE MATCHING ~~~~~~~
            # -------------------------------------------------------------------------------------------------------------------------------

            if self.multiple_assignment is True or self.lecturer_capacity_checker is True or self.project_capacity_checker is True:
                print()
                print('No super-stable matching exists! Final assignment relation is .. ')
                return self.M

            else:
                if self.blockingpair is True:
                    print('Reason is UNKNOWN!!!')
                    print('No super-stable matching exists! Final assignment relation is .. ')
                    return self.M

            if self.multiple_assignment is False and self.lecturer_capacity_checker is False and self.project_capacity_checker is False and self.blockingpair is False:
                print('Matching is Super-Stable')
                return self.M
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
s = SPATSUPER()
print(s.runAlgorithm())
