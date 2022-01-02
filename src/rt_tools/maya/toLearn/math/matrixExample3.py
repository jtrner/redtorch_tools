import maya.api.OpenMaya as om2
import maya.cmds as mc

# A
__startIndex__ = {0:0,
                  1:4,
                  2:8,
                  3:12}
                  
def setMatrixRow(row=0,vec=None,matrix=None):
    matrix[__startIndex__[row]] = vec[0]
    matrix[__startIndex__[row]+1] = vec[1]
    matrix[__startIndex__[row]+2] = vec[2]
    
    return matrix

def getMatrixRow(row=0,inMat=None):
    outVec = om2.MVector(inMat[__startIndex__[row]],
                        inMat[__startIndex__[row]+1],
                        inMat[__startIndex__[row]+2])
    return outVec
    
A = om2.MMatrix([2, 0, 0, 0,
                 0, 1, 0, 0,
                 0, 0, 1, 0,
                 1, 2, 3, 1])
                 
x_point = om2.MPoint(1, 2, 3)

b = x_point * A
print(b)


x_vector = om2.MVector(1, 2, 3)

b = x_vector * A
print(b)

#b = A.transpose() * x
                