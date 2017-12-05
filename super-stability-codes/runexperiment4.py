from spastsuper import SPASTSUPER
from IPSPASTsuper import GurobiSPAST
import numpy as np
import sys
import os
import csv
from gurobipy import *

def run():

    if __name__ == '__main__':
        #directory = 'experiments/4/100/'
        filename = sys.argv[1]
        input_file = filename
        s = SPASTSUPER(input_file)
        s.algorithm()
        s.check_stability()
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        # WRITE THE FILENAME<SPACE>TIME TAKEN<SPACE>Y/N SIGNIFYING IF A SUPER-STABLE MATCHING EXISTS<SPACE>CARDINALITY OF SUCH MATCHING AND 0 OTHERWISE
        # ---------------------------------------------------------------------------------------------------------------------------------------------

        if s.multiple_assignment is True or s.lecturer_capacity_checker is True or s.project_capacity_checker is True:
            G = GurobiSPAST(input_file)
            try:
                G.assignmentConstraints()
                G.objfunctionConstraints()
                G.avoidblockingpair()
                G.J.optimize()
                v = G.J.objVal  # check optimization value, if this cannot be obtained then model is infeasible -- thus exception error is thrown.
                print(filename + ' ' + str(s.time_taken) + ' N/Y ' + str(int(v)))
            except:
                print(filename + ' ' + str(s.time_taken) + ' N/N ' + str(0))

        else:
            if s.blockingpair is True:
                print(filename + ' ' + str(s.time_taken) + ' U ' + str(0))

        if s.multiple_assignment is False and s.lecturer_capacity_checker is False and s.project_capacity_checker is False and s.blockingpair is False:
            print(filename + ' ' + str(s.time_taken) + ' Y ' + str(s.assigned))

run()
