import sys
import random
from copy import deepcopy


class RISPAT:
    def __init__(self):
        self.students = 0
        self.projects = 0
        self.lecturers = 0  # assume number of lecturers <= number of projects
        self.ck = 0  # assume ck >= number of projects
        self.dk = 0  # assume dk >= number of lecturers        ]
        self.sp = {}
        self.sp_copy = {}
        self.lp_copy = {}
        self.sp_no_tie = {}
        self.sp_no_tie_deletions = {}
        self.plc = {}
        self.lp = {}
        self.student_length = {}

    def read_file(self):  # reads the SPAT instance
        """
        # !* changed type of tie from tuple to list -- tuple does not support item assignment -- at the point we will replace some projects as dp
        The entries in the file is read and it returns the format below which is consequently used to find a super-stable matching

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

        with open(sys.argv[1]) as t:
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
            for k in entry[1:]:
                if k[0] == '(':
                    split_tie = k.rstrip(')').lstrip('(').split(':')
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
        student_l = len(self.sp)
        self.student_length = {'s' + str(i): '' for i in range(1, student_l + 1)}  # stores the length of each students' preference list
        for student in self.sp:
            rank = {}  # store the index of each project on each student's preference list, for ease of deletion later on in the allocation
            preferences = self.sp[student]  # s7 : [['p5', 'p3'], ['p8']]
            self.sp[student] = []
            length = len(preferences)
            self.student_length[student] = length - 1  # s7: 2 - 1 = 1 because we are using 0-based index
            for i in range(length):
                pref = preferences[i]
                count_tie = 0
                for p in pref:
                    rank[p] = (i, count_tie)
                    count_tie += 1
            self.sp[student].append(preferences)
            self.sp[student].append(rank)

        self.sp_copy = deepcopy(self.sp)

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
        for lecturer in self.lp:
            # L_k_j in created in this loop
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

# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------
# s = RISPAT()
# s.read_file()
# print(s.sp)
# print(s.sp_no_tie)
# print(s.plc)
# print(s.lp)
# print(s.student_length)
#
