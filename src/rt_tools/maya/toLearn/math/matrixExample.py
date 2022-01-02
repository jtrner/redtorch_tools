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

x = getMatrixRow(0,A) 
print(x)  
y = getMatrixRow(1,A)
print(y)   
z = getMatrixRow(2,A)  

x_new = x * 2
print(x_new)
y_new = y * 5
z_new = z * 2 

x = setMatrixRow(0, x_new, A)
y = setMatrixRow(1, y_new, A)
z = setMatrixRow(2, z_new, A)

mc.xform('pSphere1', m = A)
