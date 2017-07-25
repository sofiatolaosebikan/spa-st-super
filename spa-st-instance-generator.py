import sys
import random
from copy import deepcopy


class SPASTIG:
    def __init__(self):

        self.students = int(sys.argv[1])
        self.projects = int(sys.argv[2])
        self.lecturers = int(sys.argv[3])  # assume number of lecturers <= number of projects
        self.ck = int(sys.argv[4])  # assume ck >= number of projects
        self.dk = int(sys.argv[5])  # assume dk >= number of lecturers
        self.li = int(sys.argv[6])  # lower bound of the student's preference list
        self.lj = int(sys.argv[7])  # upper bound of the student's preference list
        self.infile = sys.argv[8]

        self.sp = {}
        self.sp_copy = {}
        self.plc = {}
        self.lp = {}

    def instance_generator(self):
        """
        A program that generates a random instance for the student project allocation problem with ties.
        :return: a random instance of SPA-ST

        This program writes a random instance of the Student-Project Allocation problem with Ties to a text file.
        It takes input separated STRICTLY by SPACE as follows:
            number of students
            number of projects
            number of lecturers
            total project positions
            total lecturer capacity
            lower bound of the student's preference list
            upper bound of the student's preference list
            the file name to write the instance with a .txt extension.
            the file name to write the corresponding matching
        """
        #  how can I randomly decide what the length of the students preference list should be?

        project_capacity = {'p'+str(i): 1 for i in range(1, self.projects+1)}  # we assign capacity 1 to all projects
        project_lecturer = {'p'+str(i): 'l'+str(i) for i in range(1, self.lecturers+1)}  # # we assign p1:l1, p2:l2,..., p30:l30
        project_lecturer_capacity = {'p'+str(i): [] for i in range(1, self.projects+1)}  # to merge project capacities and corresponding lecturer
        project_list = list(project_capacity.keys())  # [p1, p2, ... , p150]

        lecturer_capacity = {'l' + str(i): 1 for i in range(1, self.lecturers + 1)}  # we assign capacity 1 to all lecturers
        lecturer_student = {'l' + str(i): [] for i in range(1, self.lecturers + 1)}  # 'li':['s6', 's1'], in preference order
        lecturer_preference = {'l' + str(i): [] for i in range(1, self.lecturers + 1)}  # finally we combine lecturer's capacity and student pref
        lecturer_project = {'l' + str(i): ['p' + str(i)] for i in range(1, self.lecturers + 1)}  # we assign l1:[p1], l2:[p2], ..., l30:[p30]
        lecturer_list = list(lecturer_capacity.keys())  # [l1, l2, ... , l30]

        student_preference_capacity = {'s' + str(i): 0 for i in range(1, self.students + 1)}  # stores the length of each student's preference list
        student_preference = {'s' + str(i): [] for i in range(1, self.students + 1)}  # stores randomly selected projects
        students_list = list(student_preference_capacity.keys())

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # randomly assign the remaining project capacities
        for i in range(self.ck - self.projects):  # range(9 - 8) = range(1) = 1 iteration. Okay!
            project_capacity[random.choice(project_list)] += 1
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # randomly assign the remaining lecturer capacities
        for j in range(self.dk - self.lecturers):
            lecturer_capacity[random.choice(lecturer_list)] += 1
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # assign remaining projects to lecturers
        for l in range(self.lecturers+1, self.projects+1):
            le = random.choice(lecturer_list)
            lecturer_project[le].append('p'+str(l))  # does it matter that the project is picked accordingly and only lecturers are random
            # I suspect if it is not done this way, some projects will end up with no lecturer
            project_lecturer['p'+str(l)] = le  # point all projects to the lecturer offering it
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  at this point, we can merge project_capacity and project_lecturer
        for project in project_lecturer_capacity:
            project_lecturer_capacity[project].append(project_capacity[project])
            project_lecturer_capacity[project].append(project_lecturer[project])

        # -----------------------------------------------------------------------------------------------------------------------------------------

        # Next is the students ...... :) At this point we already know which lecturer is offering which project
        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  randomly decide the length of each student's preference list
        for s in students_list:
            length = random.randint(self.li, self.lj)  # the length of each student's preference list is between [2,8].
            student_preference_capacity[s] += length
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  based on the length of their preference list, we provide projects at random
        for student in students_list:
            projects_copy = project_list[:]
            length = student_preference_capacity[student]
            for i in range(length):
                p = random.choice(projects_copy)
                projects_copy.remove(p)  # I did this to avoid picking the same project 2x. This could also be achieved by shuffling and popping?
                student_preference[student].append(p)
                lecturer_student[project_lecturer[p]].append(student)
            # random.shuffle(student_preference[student])  this line shuffles the final preference list for each student. Strictly ranked.
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  Now we decide the student preference for each lecturer. We convert to set and back to list because set removes duplicate.
        #  There will be duplicates in the lecture_student list since we add a student to a lecturer's list for every project the student
        #  has in common with the lecturer, which could be more than 1.
        for lecturer in lecturer_student:
            lecturer_student[lecturer] = list(set(lecturer_student[lecturer]))
            random.shuffle(lecturer_student[lecturer])  # this line shuffles the final preference list for each lecturer. Hence ordered.
        # -----------------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------------
        #  Now we combine the lecturer's capacity and lecturer_student_preference
        for lecturer in lecturer_list:
            lecturer_preference[lecturer].append(lecturer_capacity[lecturer])
            lecturer_preference[lecturer].append(lecturer_student[lecturer])
        # -----------------------------------------------------------------------------------------------------------------------------------------

        return student_preference, project_lecturer_capacity, lecturer_preference

    def writeInstance(self):  # writes the SPA instance to a txt file

        if __name__ == '__main__':
            S, P, L = self.instance_generator()
            students = len(S)
            projects = len(P)
            lecturers = len(L)
            with open(self.infile, 'w') as I:

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ...write number of student (n) number of projects (m) number of lecturers (k) ---- for convenience, they are all separated by space
                I.write(str(students) + ' ' + str(projects) + ' ' + str(lecturers) + '\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the students index and their corresponding preferences ---- 1 2 3 1 7
                for n in range(1, students + 1):
                    preference = S['s'+str(n)]
                    sliced = [p[1:] for p in preference]
                    I.write(str(n) + ' ')
                    I.writelines('%s ' % p for p in sliced)
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                #  ..write the projects index, its capacity and the lecturer who proposed it ------- 1 5 1
                for m in range(1, projects + 1):
                    lecturer_capacity = P['p'+str(m)]
                    lecturer_capacity[1] = lecturer_capacity[1][1:]

                    I.write(str(m) + ' ')
                    I.writelines('%s ' % l for l in lecturer_capacity)
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------

                # ---------------------------------------------------------------------------------------------------------------------------------------
                # .. write the lecturers index, their capacity and their corresponding preferences ---- 1 2 3 1 7
                for k in range(1, lecturers + 1):
                    preference = L['l' + str(k)]
                    preferred_students = preference[1]
                    sliced = [p[1:] for p in preferred_students]
                    I.write(str(k) + ' ' + str(preference[0]) + ' ')
                    I.writelines('%s ' % p for p in sliced)
                    I.write('\n')
                # ---------------------------------------------------------------------------------------------------------------------------------------
                I.close()

S = SPASTIG()
S.writeInstance()
