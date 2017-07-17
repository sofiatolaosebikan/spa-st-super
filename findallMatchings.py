from readinputSPAT import RISPAT
from copy import deepcopy
class find_all_matching:
    def __init__(self):

        r = RISPAT()
        r.read_file()
        self.sp = deepcopy(r.sp)
        self.sp_copy = deepcopy(r.sp_copy)
        self.sp_no_tie = deepcopy(r.sp_no_tie)
        self.sp_no_tie_deletions = deepcopy(r.sp_no_tie_deletions)
        self.plc = deepcopy(r.plc)
        self.lp = deepcopy(r.lp)
        self.lp_copy = deepcopy(r.lp_copy)

        self.M = {'s' + str(i): '' for i in range(1, len(self.sp) + 1)}  # assign all students to free
        #self.superStableM = {}

        self.project_wstcounter = {'p' + str(i): '' for i in range(1, len(self.plc) + 1)}  # worst student pointer for projects
        self.lecturer_wstcounter = {'l' + str(i): '' for i in range(1, len(self.lp) + 1)}  # worst student pointer for lecturer

        self.blockingpair = False
        self.superStableMblockingpair = True

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
            while position_worst_tie >= 0: # check all the ties of/before the worst assigned tie to see if student is contained there
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
            if self.M[student] == '':  # if student s_i is not assigned in M, we check if it forms a blocking pair with all the projects in A(s_i).
                preferred_projects = self.sp_no_tie[student]  # list of pj's wrt to s_i s6 = ['p2', 'p3', 'p4', 'p5', 'p6']

            else:  # if student s_i is matched to a project in M
                matched_project = self.M[student] # get the matched project
                rank_matched_project = self.sp_copy[student][1][matched_project]  # find its rank on s_i's preference list A(s_i)
                p_list = self.sp_copy[student][0]  # list of pj's wrt to s_i      # a copy of A(s_i)
                temp = rank_matched_project[0]  # position of the tie of the matched project in the list
                preferred_projects = set()  # projects that student strictly prefers to her matched project or indifferent between..
                while temp >= 0:
                    keep = set([p for p in p_list[temp] if p != matched_project])
                    #print(keep)
                    preferred_projects.update(keep)
                    temp -= 1
                #print(student, rank_matched_project, p_list, temp, preferred_projects)

            for project in preferred_projects:
                lecturer = self.plc[project][0]  # l_k

                self.blockingpair1(project, lecturer)   # project and lecturer is under-subscribed
                if self.blockingpair is True:
                    #print(student, project, lecturer)
                    break

                if self.M[student] != '':  # this is the only blocking pair difference between a matched and unmatched student..
                    self.blockingpair2a(student, project, lecturer, self.M[student])  # project is under-subscribed lecturer is full
                    if self.blockingpair is True:
                        #print(student, project, lecturer)
                        break

                self.blockingpair2b(student, project, lecturer)  # project is under-subscribed lecturer is full
                if self.blockingpair is True:
                    #print(student, project, lecturer)
                    break

                self.blockingpair3(student, project, lecturer)
                if self.blockingpair is True:
                    #print(student, project, lecturer)
                    break
    def lecturer_worst_counter(self):
        for lecturer in self.lp:
            lp = self.lp[lecturer][1]
            count = len(lp) - 1
            while count >= 0:
                for student in lp[count]:
                    if self.M[student] and lecturer == self.plc[self.M[student]][0]:
                        self.lecturer_wstcounter[lecturer] = count
                        break
                if self.lecturer_wstcounter[lecturer] == '':
                    count -= 1
                else:
                    break
            if self.lecturer_wstcounter[lecturer] == '':
                self.lecturer_wstcounter[lecturer] = len(lp) - 1

    def project_worst_counter(self):
        for project in self.plc:
            lecturer = self.plc[project][0]
            projected_plist = self.lp[lecturer][2][project]
            count = len(projected_plist) - 1
            while count >= 0:
                for student in projected_plist[count]:
                    if self.M[student] and project == self.M[student]:
                        self.project_wstcounter[project] = count
                        break
                if self.project_wstcounter[project] == '':
                    count -= 1
                else:
                    break
            if self.project_wstcounter[project] == '':
                self.project_wstcounter[project] = len(projected_plist) - 1

    #################################################################################################################################################
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FIND ALL POSSIBLE MATCHINGS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #################################################################################################################################################
    def choose(self, i):
        student = 's' + str(i)
        if i > len(self.sp_no_tie):
            #print(self.M)
            self.project_wstcounter = {'p' + str(i): '' for i in range(1, len(self.plc) + 1)}  # worst student pointer for projects
            self.lecturer_wstcounter = {'l' + str(i): '' for i in range(1, len(self.lp) + 1)}  # worst student pointer for lecturer
            self.lecturer_worst_counter()
            self.project_worst_counter()
            self.blockingpair = False
            #print('starts as ', self.blockingpair)
            self.check_stability()
            #print('ends as ', self.blockingpair)

            #print(self.lecturer_wstcounter)
            #print(self.project_wstcounter)
            #print(self.blockingpair)

            if self.blockingpair is False:  # this means no blocking pair is found, thus M is super-stable
                print('~~~~~~~~~~ found a super-stable matching ~~~~~~~~~~')
                print(self.M)
                print()
                self.superStableMblockingpair = False
                #self.superStableM = deepcopy(self.M)

        else:
            for project in self.sp_no_tie[student]:
                lecturer = self.plc[project][0]
                if self.plc[project][1] > 0 and self.lp[lecturer][0] > 0:
                    self.M[student] = project
                    self.plc[project][1] -= 1
                    self.lp[lecturer][0] -= 1
                    self.choose(i+1)
                    self.M[student] = ''
                    self.plc[project][1] += 1
                    self.lp[lecturer][0] += 1
            self.choose(i+1)


    def run(self):
        if __name__ == '__main__':
            self.choose(1)

            if self.superStableMblockingpair is True:
                print('no super-stable matching exists')
                print('to find an assignment relation, run algorithm-SPAT-SUPER')



find_all_matching().run()


#
# {'s4': 'p3', 's5': 'p2', 's2': '', 's6': 'p2', 's1': '', 's3': 'p3'}
# {'s1': set(), 's5': {'p3'}, 's6': {'p2'}, 's3': {'p3'}, 's4': {'p2'}, 's2': set()}

