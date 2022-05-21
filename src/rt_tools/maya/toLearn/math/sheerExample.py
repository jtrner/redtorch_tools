import maya.api.OpenMaya as om
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
    
def getMatrix(transform,matAttr = "worldMatrix[0]"):
    matData = cmds.getAttr(transform+'.'+matAttr)
    mat = om2.MMatrix(matData)
    return mat
    
A = om2.MMatrix(mc.getAttr('pSphere1.worldMatrix[0]')) 
print(A)

x_new =om2.MVector(1, 1, 0)
print(x_new)
y_new = om2.MVector(0, 1, 0)
z_new = om2.MVector(0, 0, 1) 

x = setMatrixRow(0, x_new, A)
print(x)
y = setMatrixRow(1, y_new, A)
z = setMatrixRow(2, z_new, A)

mc.xform('pSphere1', m = A)