This repository contains the codes that was used to produce the experimental evaluation in the following paper:

> Olaosebikan, S. and Manlove, D. (2020). Super-stability in the student-project allocation problem with ties. Journal of Combinatorial Optimization, (doi: 10.1007/s10878-020-00632-x) (Early Online Publication)

=========

> instanceGenerator.py

This writes to a .txt file, a randomly-generated instance of the Student-Project Allocation problem with students preferences over projects, lecturer preferences over Students, and with Ties (SPA-ST).

=========

> readinput.py

This reads the instance from the .txt file into a suitable data structure representing the students, projects and lecturers preference information.

=========

> bruteforce.py

This finds all the super-stable matching, given an instance of SPA-ST, should one exist. The purpose of implementing this approach was mainly for correctness testing of our implementation of the polynomial-time algorithm (spastsuper.py). The bruteforce implementation terminates in less than 5 seconds, on SPA-ST instances consisting of no more than 10 students with a preference list length of 3. 

=========

> spastsuper.py

This is an implementation of the polynomial-time algorithm (Algorithm SPA-ST-Super), which was presented in the paper above. It finds a super-stable matching, given an instance of SPA-ST, should one exist. 

=========

> ipmodel.py

This implements the integer programming model described in Appendix A of the paper above. It finds a super-stable matching, given an instance of SPA-ST, should one exist. The purpose of implementing this approach was to scale up the correctness testing of our polynomial-time algorithm implementation.

> runipmodel.py

This runs the ipmodel from above on a given SPA-ST instance. You need to have the Gurobi optimization solver installed on your computer. See https://www.gurobi.com/documentation/quickstart.html

=========

> examples.ipynb

We illustrate how to read the .txt file generated from a run of instanceGenerator.py. We also illustrate how to run the python fles in this repo.