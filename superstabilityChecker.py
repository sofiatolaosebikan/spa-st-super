from findallMatchings import find_all_matching
from copy import deepcopy


class SUPERSTABILITY:
    def __init__(self):

        S = find_all_matching()
        self.sp = S.sp
        self.sp_copy = S.sp_copy
        self.sp_no_tie = S.sp_no_tie
        self.sp_no_tie_deletions = S.sp_no_tie_deletions
        self.plc = S.plc
        self.lp = S.lp
        self.lp_copy = S.lp_copy
        self.M = S.M



        self.project_wstcounter = S.project_wstcounter
        self.lecturer_wstcounter = S.lecturer_wstcounter
        self.blockingpair = False




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

                self.blockingpair1(project, lecturer)   # project and lecturer is under-subscribed
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
