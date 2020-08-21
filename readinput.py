from copy import deepcopy


class READSPAST:
    def __init__(self, filename):
        self.filename = filename
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
        self.lp_rank = {}
        self.proj_rank = {}

    def read_file(self):  # reads the SPAT instance from a file
        """
        # !* changed type of tie from tuple to list -- tuple does not support item assignment at the point we will replace some projects as dp
        The entries in the file is read and it returns the format below which is consequently used to find a super-stable matching

        self.sp = student_preferences = {s_i: [pref_list_length, list(A_i), {p_j: (tie_rank, project_rank_in_tie) for each p_j in A_i}], 0}
                                
        self.lp = lecturer_preference = {l_k : [d_k, list(L_k), {p_j: list(L_k_j))}, replete, len(L_k), tail(L_k)))]}
                                    
        self.plc = projects_info = {p_j: [l_k, c_j, replete, [rejected_students], len(L_k^j), tail(L_k^j)))}
        * tail(L_k^j) will keep track of the worst student pointer
        
        """

        with open(self.filename) as t:
            t = t.readlines()
        entry1 = t[0].rstrip(' \n').split(' ')
        self.students, self.projects, self.lecturers = int(entry1[0]), int(entry1[1]), int(entry1[2])

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the student's dictionary

        for i in range(1, self.students+1):
            entry = t[i].rstrip(' \n').split(' ')
            student = 's' + str(entry[0])
            preferencelist = []
            self.sp_no_tie[student] = []
            self.sp_no_tie_deletions[student] = set()  # because removing from a set is constant time
            for k in entry[1:]:
                if k[0] == '(':
                    split_tie = k.rstrip(')').lstrip('(').split(':')
                    tie = ['p'+str(j) for j in split_tie]
                    preferencelist.append(tie)
                    for j in tie:
                        self.sp_no_tie[student].append(j)
                        self.sp_no_tie_deletions[student].add(j)
                else:
                    preferencelist.append(['p'+str(k)])
                    self.sp_no_tie[student].append('p' + str(k))
                    self.sp_no_tie_deletions[student].add('p' + str(k))
            length = len(preferencelist)
        # ---------------------------------------------------------------------------------------------------------------------
            rank = {}  # store the index of each project on each student's preference list, for ease of deletion later on in the allocation
            for i in range(length):
                orderedpreference = preferencelist[i]
                count_tie = 0
                for p in orderedpreference:
                    rank[p] = (i, count_tie)
                    count_tie += 1
            self.sp[student] = [length, preferencelist, rank, 0]  # s7 : [2, [['p5', 'p3'], ['p8']], {'p3': (0, 1), 'p5': (0, 0), 'p8': (1, 0)}, 2]
            # the last entry is to keep track of when a student has an empty preference list - to be incremented and compared with length


        self.sp_copy = deepcopy(self.sp)

        # -------------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the projects's dictionary

        for i in range(self.students+1, self.students+1+self.projects):
            entry = t[i].rstrip(' \n').split(' ')
            # project = [lecturer, project_capacity_yet_to_be_filled, full(project) = False, keep track of students that was rejected from project]
            # length of the preferred students for p_j according to l_k to be appended when we have more information..
            self.plc['p'+str(entry[0])] = ['l'+str(entry[2]), int(entry[1]), False, []]
        # -------------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------------
        #  we build the lecturer's dictionary

        for i in range(self.students+1+self.projects, self.students+1+self.projects+self.lecturers):
            entry = t[i].rstrip(' \n').split(' ')
            lecturer = 'l' + str(entry[0])
            self.lp_rank[lecturer] = {} # stores rank of each student in L_k
            lecturerpreferencelist = []
            rank = 1
            for k in entry[2:]:
                if k[0] == '(':
                    split_tie = k.rstrip(')').lstrip('(').split(':')
                    tie = ['s'+str(j) for j in split_tie]
                    lecturerpreferencelist.append(tie)
                    for s in tie:
                        self.lp_rank[lecturer][s] = rank
                else:
                    s = 's' + str(k)
                    lecturerpreferencelist.append([s])
                    self.lp_rank[lecturer][s] = rank
                    
                rank += 1
            # -------------------------------------------------------------------------------------------------------------------
            #  another useful dictionary is created here and attached to the lecturer's dictionary - L_k_j
            #  the lecturer's ranked preference list according to each project they offer
            d = {}
            # the students preferred by this lecturer   ------ [['s7'], ['s4', 's1'], ['s2'], ['s3', 's5', 's6']] for lecturer 1
            for project in self.plc:
                if self.plc[project][0] == lecturer:
                    d[project] = []
                    self.proj_rank[project] = {} # stores rank of each student in L_k_j
                    rank = 1
                    for tie in lecturerpreferencelist:  # Is it the case that a student will not be on the ranked preference of a lecturer - same project in common
                        student_tie = []
                        for student in tie:
                            if project in self.sp_no_tie[student]:
                                student_tie.append(student)
                                self.proj_rank[project][student] = rank
                        if len(student_tie) == 0:
                            continue
                        else:
                            d[project].append(student_tie)
                        rank += 1
                    self.plc[project].append(len(d[project])-1)  # append len(L_k_j)
                    self.plc[project].append(len(d[project])-1)  # worst_student_pointer


            length = len(lecturerpreferencelist)
            # lecturer = [lecturer_capacity, lecturerpreferencelist, d, full(lecturer) = False, len(lecturerpreferencelist), worst_student_pointer]
            self.lp[lecturer] = [int(entry[1]), lecturerpreferencelist, d, False, length-1, length - 1]
            self.lp_copy = deepcopy(self.lp)
            
            
            
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------

# filename = "instances/tie-3.txt"
# s = READSPAST(filename)
# s.read_file()
# print(s.sp)
# print()
# print(s.sp_no_tie)
# print()
# print(s.plc)
# print()
# print(s.lp)
# print()
# print(s.lp_rank)
# print()
# print(s.proj_rank)


"""
output for instances/tie-3.txt

self.sp = {'s1': [1, [['p1']], {'p1': (0, 0)}, 0], 
           's2': [2, [['p2', 'p3'], ['p1']], {'p2': (0, 0), 'p3': (0, 1), 'p1': (1, 0)}, 0], 
           's3': [2, [['p3'], ['p1', 'p4']], {'p3': (0, 0), 'p1': (1, 0), 'p4': (1, 1)}, 0], 
           's4': [1, [['p1']], {'p1': (0, 0)}, 0], 
           's5': [2, [['p1', 'p2'], ['p4']], {'p1': (0, 0), 'p2': (0, 1), 'p4': (1, 0)}, 0]}

self.sp_no_tie = {'s1': ['p1'], 
                  's2': ['p2', 'p3', 'p1'], 
                  's3': ['p3', 'p1', 'p4'], 
                  's4': ['p1'], 
                  's5': ['p1', 'p2', 'p4']}

self.plc = {'p1': ['l1', 2, False, [], 2, 2], 
            'p2': ['l1', 1, False, [], 0, 0], 
            'p3': ['l1', 1, False, [], 1, 1], 
            'p4': ['l2', 1, False, [], 0, 0]}

self.lp = {'l1': [4, [['s1'], ['s4', 's3'], ['s5', 's2']], 
                  {'p1': [['s1'], ['s4', 's3'], ['s5', 's2']], 'p2': [['s5', 's2']], 'p3': [['s3'], ['s2']]}, False, 2, 2], 
           'l2': [1, [['s3', 's5']], {'p4': [['s3', 's5']]}, False, 0, 0]}

self.lp_rank = {'l1': {'s1': 1, 's4': 2, 's3': 2, 's5': 3, 's2': 3}, 
                'l2': {'s3': 1, 's5': 1}}

self.proj_rank = {'p1': {'s1': 1, 's4': 2, 's3': 2, 's5': 3, 's2': 3}, 
                  'p2': {'s5': 1, 's2': 1}, 
                  'p3': {'s3': 1, 's2': 2}, 
                  'p4': {'s3': 1, 's5': 1}}
"""
