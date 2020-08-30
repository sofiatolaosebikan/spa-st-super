#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 2020

@author: sofiat
"""

import sys
from spastsuper import SuperPoly
from bruteforce import SuperBruteForce



            

filename = sys.argv[1]
s = SuperPoly(filename)    
sa = s.run()
b = SuperBruteForce(filename)
ba = b.choose(1)
print(filename + " " + sa + ba)

    