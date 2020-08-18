#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last edited on Sat Feb  1 20:20:49 2020

@author: sofiat
"""

from IPModelSuper import IPModelSuper
         
class IPSuper():
    def __init__(self, filename):
        self.filename = filename
        self.M = {}
        self.obj = 0
        self.found_susm = None
        self.G = IPModelSuper(self.filename)
        try:
            self.G.assignmentConstraints()
            self.G.objfunctionConstraints() 
            self.G.avoidblockingpair()
            
            self.G.J.optimize()  
            self.obj = self.G.J.objVal
            # print('******:::::****>', self.obj)
            M = {}
            i = 1
            while i <= len(self.G.sp):
                student = 's'+str(i)
                self.M[student] = []
                for project in self.G.sp[student][2]:
                    lecturer = self.G.plc[project][0]
                    a = self.G.J.getVarByName(student + " is assigned to " + project)
                    if a.x == 1.0:
                        self.M[student].append(project)
                        M[student] = project
                        if project not in self.M: 
                            self.M[project] = [student]
                        else:                
                            self.M[project].append(student)  
                        if lecturer not in self.M: 
                            self.M[lecturer] = [student]
                        else:                
                            self.M[lecturer].append(student) 
                i += 1
#             print(M)
#             for k,v in self.M.items():
#                 print('\t', k, '::>', v)
# #            
#        
        except:
            self.found_susm = 'N'
            
        self.sp = self.G.sp
        self.sp_no_tie = self.G.sp_no_tie
        self.lp = self.G.lp
        self.plc = self.G.plc
        self.lp_rank = self.G.lp_rank
        self.proj_rank = self.G.proj_rank
        self.blocking_pair = False
        
    # =======================================================================    
    # blocking pair types
    # =======================================================================    
    def blockingpair_1bi(self, student, project, lecturer):
        #  project and lecturer capacity
        cj, dk = self.plc[project][1], self.lp[lecturer][0]
        # no of students assigned to project in M
        project_occupancy, lecturer_occupancy = 0, 0
        if project in self.M: 
            project_occupancy = len(self.M[project])
        # no of students assigned to lecturer in M
        if lecturer in self.M: 
            lecturer_occupancy = len(self.M[lecturer])
        #  project and lecturer are both under-subscribed
        if project_occupancy < cj and lecturer_occupancy < dk:
            return True
        return False
    
    def blockingpair_1bii(self, student, project, lecturer):
        # p_j is undersubscribed, l_k is full and either s_i \in M(l_k)
        # or l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
        cj, dk = self.plc[project][1], self.lp[lecturer][0]
        project_occupancy, lecturer_occupancy = 0, 0
        if project in self.M: 
            project_occupancy = len(self.M[project])
            
        if lecturer in self.M: 
            lecturer_occupancy = len(self.M[lecturer])
            
        #  project is undersubscribed and lecturer is full
        if project_occupancy < cj and lecturer_occupancy == dk:
            Mlk_students = self.M[lecturer]
            if student in Mlk_students:
                return True
            # l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
            student_indexLk = self.lp_rank[lecturer][student]
            for si in Mlk_students:
                 si_indexLk = self.lp_rank[lecturer][si]
                 if si_indexLk >= student_indexLk:
                    return True                
        return False
    
    def blockingpair_1biii(self, student, project, lecturer):
        # p_j is full and l_k prefers s_i to the worst student in M(p_j) or is indifferent between them
        cj, project_occupancy = self.plc[project][1], 0
        
        if project in self.M: 
            project_occupancy = len(self.M[project])
            
        if project_occupancy == cj:
            Mpj_students = self.M[project]
            # l_k prefers s_i to the worst student in M(p_j) or is indifferent between them
            student_indexLkj = self.proj_rank[project][student]
            for si in Mpj_students:
                 si_indexLkj = self.proj_rank[project][si]
                 if si_indexLkj >= student_indexLkj:
                    return True  
        return False
    
   
    # =======================================================================    
    # Is M strongly stable? Check for blocking pair
    # self.blocking_pair is set to True if blocking pair exists
    # =======================================================================
    def check_stability(self):
        for student in self.sp:
            preferred_projects = []
            if self.M[student] == []:
                preferred_projects = self.sp_no_tie[student]
            else:
                matched_project = self.M[student][0]
                rank_matched_project = self.sp[student][2][matched_project][0]
                A_si = self.sp[student][1]
                preferred_projects = [s for tie in A_si[:rank_matched_project+1] for s in tie]
                preferred_projects.remove(matched_project)
        
            for project in preferred_projects:
                lecturer = self.plc[project][0]
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1bi(student, project, lecturer)
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1bii(student, project, lecturer)
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1biii(student, project, lecturer)
                
                if self.blocking_pair:
#                    print(student, project, lecturer)
                    break

            if self.blocking_pair:
                print(student, project, lecturer)
                
                break                                
                          
    def run(self):
        if len(self.M) > 0:
            self.check_stability()
            if not self.blocking_pair:
                self.found_susm = 'Y'
            else:
                self.found_susm = 'BP'
        return self.found_susm

#I = IPSuper("CT/4/instance10000.txt")
#I = IPStrongBP("../correctnessTesting/3/instance7359.txt")
#print(I.run())