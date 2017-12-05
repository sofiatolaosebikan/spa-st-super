# coding: utf-8

# In[3]:

from readinputSPAST import READSPAST
from copy import deepcopy
from gurobipy import *
import csv
         
class GurobiSPAST():
    def __init__(self, filename):
        self.filename = filename
        r = READSPAST()
        r.read_file(self.filename)
        self.students = r.students
        self.projects = r.projects
        self.lecturers = r.lecturers
        
        self.sp = r.sp
        self.sp_copy = r.sp_copy
        self.sp_no_tie = r.sp_no_tie
        self.sp_no_tie_deletions = r.sp_no_tie_deletions
        self.plc = r.plc
        self.lp = r.lp
        self.J = Model("SPAP")
        

                
    def assignmentConstraints(self):
        #=============================================================================================================#
        # Create variables
        #=============================================================================================================#
        
        # =============================================== CONSTRAINT 4 ===============================================#
        # ...for each acceptable (student, project) pair, we create the binary variable xij and impose constraint 4   #
        #=============================================================================================================#
        
        for student in self.sp:                                    
            self.sp[student].append(dict()) # to store the binary variables for each project student finds acceptable
            sumstudentvariables = LinExpr()            
            for project in self.sp[student][2]:                
                # addVar(lb, ub, obj, vtype, name, column)
                xij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=student + " is assigned " + project)            
                self.sp[student][4][project] = xij            
                sumstudentvariables += xij 
            # .. add constraint that a student can be assigned to at most one project
            # addConstr(lhs, sense, rhs, name)
            self.J.addConstr(sumstudentvariables <= 1, "Constraint for "+ student)
        #=============================================================================================================#


            
        #=============================================================================================================#
        # =============================================== CONSTRAINT 5 ===============================================#
        # we loop through each project and each student that finds this project acceptable
        # then increment the corresponding student-project variable (xij)
        #=============================================================================================================#
        for project in self.plc:
            totalprojectcapacity = LinExpr()
            for student in self.sp:
                if project in self.sp[student][2]:
                    totalprojectcapacity += self.sp[student][4][project]        
            self.J.addConstr(totalprojectcapacity <= self.plc[project][1], "Total capacity constraint for "+ project)
        #=============================================================================================================#
        
                
        
        #=============================================================================================================#
        # =============================================== CONSTRAINT 6 ===============================================#
        # loop through each lecturer and each acceptable (student,project) pairs
        # if for an acceptable pair, the project is offered by lecturer, then increment
        # the totallecturercapacity with the corresponding (student,project) variable (xij)
        #=============================================================================================================#
        for lecturer in self.lp:
            totallecturercapacity = LinExpr()
            for student in self.sp:
                for project in self.sp[student][2]:
                    if lecturer == self.plc[project][0]:
                        totallecturercapacity += self.sp[student][4][project]
            self.J.addConstr(totallecturercapacity <= self.lp[lecturer][0], "Total capacity constraint for "+ lecturer) 
        #=============================================================================================================#
        
    
    
    
    
    #|--------------------------------------------------------------------------------------------------------------------------|#
    #|                                                                                                                          |#
    #| For an arbitrary acceptable pair (s_i, p_j), we define all the relevant terms to ensure (s_i, p_j) does not block M..    |#
    #|                                                                                                                          |#
    #|--------------------------------------------------------------------------------------------------------------------------|#
    
    
    #=============================================================================================================#
    # =============================================== CONSTRAINT 7 ===============================================#
    # we define thetaij :::::: 
    # If thetaij = 1, s_i is either unmatched in M or strictly prefers p_j to M(s_i) or is indifferent between them
    #=============================================================================================================#
    def theta(self, student, project):
        thetaij = LinExpr()
        sumSij = LinExpr() 
        xij = self.sp[student][4][project]
        indexproject = self.sp[student][2][project][0] # get the rank of project on student's preference list
        # for each project (p_j') that student strictly prefers to project (p_j):: p_j not inclusive
        for tie in self.sp[student][1][:indexproject]:
            for pjprime in tie:       
                sumSij += self.sp[student][4][pjprime]
        thetaij.addConstant(1.0)
        thetaij.add(sumSij, -1)
        thetaij.add(xij, -1)
        return thetaij      
    #=============================================================================================================#
    
    
    #=============================================================================================================#
    # =============================================== CONSTRAINT 8 ===============================================#
    # we define alpha_j to be a binary variable that corresponds to the occupancy of p_j in M
    # if p_j is undersubscribed in M then we enforce alpha_j to be 1
    #=============================================================================================================#    
    def alpha(self, project):        
        alphaj = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=project+" is undersubscribed")                
        capacity = self.plc[project][1]           # c_j
        projectoccupancy = LinExpr()
        for student in self.sp:
            if project in self.sp[student][2]:
                projectoccupancy += self.sp[student][4][project]
        self.J.addConstr(capacity*alphaj >= (capacity - projectoccupancy), "constraint 7")
        return alphaj
    #=============================================================================================================# 
    
    # =============================================== CONSTRAINT 9 ==============================================#
    # we create a binary variable betak that corresponds to the occupancy of l_k in M. 
    # If l_k is undersubscribed in M, we enforce betak = 1
    #=============================================================================================================#
    def beta(self,student,project):                
        lecturer = self.plc[project][0]              # l_k
        lecturercapacity = self.lp[lecturer][0]    # d_k                
        betak = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name= lecturer + " is undersubscribed")
        lectureroccupancy = LinExpr()
        for pro in self.lp[lecturer][2]:
            for tie in self.lp[lecturer][2][pro]:
                for stud in tie:         
                    lectureroccupancy += self.sp[stud][4][pro]
        self.J.addConstr((lecturercapacity*betak) >= (lecturercapacity - lectureroccupancy), "constraint 8")             
        return betak
    #=============================================================================================================#
    
    
    # =============================================== CONSTRAINT 11 ==============================================#
    # we create a binary variable etak,  if l_k is full in M, we enforce etak = 1
    #=============================================================================================================#
    def eta(self,student,project):        
        lecturer = self.plc[project][0]              # l_k
        dk = self.lp[lecturer][0]                   # d_k
        lecturerpreference = self.lp[lecturer][1]  # L_k
        etak = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name= lecturer+ " is full")
        lecturercapacity = LinExpr()

        # obtain project's occupancy for all students
        for proj in self.lp[lecturer][2]:
            for tie in self.lp[lecturer][2][proj]:
                for stud in tie:         
                    lecturercapacity += self.sp[stud][4][proj]    
        
        lecturercapacity.addConstant(1.0)                
        self.J.addConstr((dk*etak) >= (lecturercapacity - dk), "constraint 10")             
        return etak
    #=============================================================================================================#
    
    
    
    # =============================================== CONSTRAINT 12 ==============================================#
    # we create a binary variable deltaik 
    # if s_i \in M(l_k) or l_k prefers s_i to a worst student in M(l_k) or is
    # indifferent between them, we enforce deltaik = 1
    #=============================================================================================================#
    def delta(self,student,project):        
        lecturer = self.plc[project][0]              # l_k
        dk = self.lp[lecturer][0]    # d_k
        lecturerpreference = self.lp[lecturer][1]  # L_k
        deltaik = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name= lecturer+ " prefers " + student + " to his worst assignee")
        lecturercapacity = LinExpr()     

        # obtain lecturer's occupancy for all students
        for proj in self.lp[lecturer][2]:
            for tie in self.lp[lecturer][2][proj]:
                for stud in tie:         
                    lecturercapacity += self.sp[stud][4][proj]
      
        index = 0
        while True:
            if student in lecturerpreference[index]:
                break 
            index += 1
        Dik = lecturerpreference[:index]
        lectureroccupancy = LinExpr()        


        # obtain lecturer's occupancy for students in Dik
        for ti in Dik:
            for st in ti:
                for pr in self.sp[st][2]:
                    if self.plc[pr][0] == lecturer:
                        lectureroccupancy += self.sp[st][4][pr]
        
        lecturercapacity.add(lectureroccupancy, -1)        
        self.J.addConstr((dk*deltaik) >= (lecturercapacity), "constraint 11")             
        return deltaik
    #=============================================================================================================#
    
    
    
    #=============================================================================================================#
    # =============================================== CONSTRAINT 14 ===============================================#
    # we define gamma_j to be a binary variable that corresponds to the occupancy of p_j in M
    # if p_j is full in M then we enforce gamma_j to be 1
    #=============================================================================================================#    
    def gamma(self, project):        
        gammaj = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=project+" is full")                
        cj = self.plc[project][1]           # c_j
        projectoccupancy = LinExpr()
        for student in self.sp:
            if project in self.sp[student][2]:
                projectoccupancy += self.sp[student][4][project]
        self.J.addConstr(cj*gammaj >= ((1+projectoccupancy)-cj), "constraint 13")
        return gammaj
    
    #=============================================================================================================# 
                                         
    # =============================================== CONSTRAINT 15 ==============================================#
    # we create a binary variable lambdaijk 
    # if l_k strictly prefers s_i to a worst student in M(p_j) or is
    # indifferent between them, we enforce lambdaijk = 1
    #=============================================================================================================#
    def Lambda(self,student,project):        
        lecturer = self.plc[project][0]              # l_k
        cj = self.plc[project][1]
        lambdaijk = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name= lecturer+ " prefers " + student + " to his worst student in M("+project+")")
        projectcapacity = LinExpr() 
        projectpreference = self.lp[lecturer][2][project]    # L_k^j

        # obtain project's occupancy for all students
        for tie in projectpreference:
            for stud in tie:
                projectcapacity += self.sp[stud][4][project]
                
        index = 0
        while True:  # find the position of the tie containing student
            if student in projectpreference[index]:
                break
            index += 1
        Tijk = projectpreference[:index]

        # obtain projects's occupancy for students in Tijk
        projectoccupancy = LinExpr()
        for ti in Tijk:
            for st in ti:
                projectoccupancy += self.sp[st][4][project]
        projectcapacity.add(projectoccupancy, -1)
        self.J.addConstr((cj*lambdaijk) >= projectcapacity, "constraint 14")
        return lambdaijk
    # =============================================================================================================#

    # =============================================================================================================#
    # =============================================== CONSTRAINT 10, 13 AND 16 ===================================#
    # we enforce constraints to avoid blocking pair of type 2a, 2b and 2c for each acceptable (student, project) pairs
    def avoidblockingpair(self):
        # for all acceptable (student, project) pairs
        # for efficieny ::: is there a way to only check those pairs that could block the final matching?
        for student in self.sp:             
            for project in self.sp[student][2]:             
                thetaij = self.theta(student, project)
                alphaj = self.alpha(project)
                betak = self.beta(student, project)
                etak = self.eta(student, project)
                deltaik = self.delta(student, project)
                gammaj = self.gamma(project)
                lambdaijk = self.Lambda(student, project)                
                # ---- blocking pair 2a -----
                self.J.addConstr(thetaij + alphaj + betak <= 2, "constraint 9 - avoid blocking pair 2a")
                # ----- blocking pair 2b -----
                self.J.addConstr(thetaij + alphaj + etak + deltaik <= 3, "constraint 12 - avoid blocking pair 2b")              
                # ----- blocking pair 2c -----
                self.J.addConstr(thetaij + gammaj + lambdaijk <= 2, "constraint 14 - avoid blocking pair 2c")  
                
    # =============================================================================================================#

    # =============================================================================================================#
    # =============================================== CONSTRAINT 14 ==============================================#
    # maximize the objective function
    #=============================================================================================================#
    def objfunctionConstraints(self):        
        # finally we add the objective function to maximise the number of matched student-project pairs
        Totalxijbinaryvariables = LinExpr()
        for student in self.sp:            
            for project in self.sp[student][2]:
                Totalxijbinaryvariables += self.sp[student][4][project]
        
        #setObjective(expression, sense=None)
        # It is superfulous to maximise the final matching as all super-stable matchings are of the same size
        self.J.setObjective(Totalxijbinaryvariables) 

