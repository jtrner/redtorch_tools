import maya.api.OpenMaya as om
import maya.cmds as mc


A = om2.MMatrix([2, 0, 0, 0,
                 0, 2, 0, 0,
                 0, 0, 2, 0,
                 1, 2, 3, 1])
                 

X = om2.MMatrix([1, 0, 0, 0,
                 0, 1, 0, 0,
                 0, 0, 1, 0,
                 1, 2, 3, 1])
#row                 
b = x *  A
print(b)
#col
b = A * x
print(b)  
#(((2, 2, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (1, 8, 3, 1))) 
#(((2, 2, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (1, 6, 3, 1)))(wrong)
b = A.transpose() * x.transpose()
print(b)
#(((2, 0, 0, 1), (2, 2, 0, 8), (0, 0, 2, 3), (0, 0, 0, 1)))(more weird)
#becaues it's in column again
b = b.transpose()
print(b)
#(((2, 2, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (1, 8, 3, 1)))(correct)
#this is same as first one

                               