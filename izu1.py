#!/usr/bin/env python3

def NEG(number):
    if(number == 0):
        return 1
    else:
        return 0

def AND(a,b):
    if(a == 1 and b == 1):
        return 1
    else:
        return 0

def OR(a,b):
    if (a == 0 and b == 0):
        return 0
    else:
        return 1

def IMP(a,b):
    if (a == 1 and b == 0):
        return 0
    else:
        return 1

def EKV(a,b):
    if(a == b):
        return 1
    else:
        return 0

for p in range(0, 2 ):
    for q in range(0, 2):
        for r in range(0, 2):
            print("p={0} q={1} r={2}".format(p,q,r))
            print("or={0}".format(NEG(p)))
            result = IMP(EKV(NEG(p),AND(q,r)), OR(p, NEG(AND(p,q)) ) )

            print( result)








