import maya.api.OpenMaya as om2
import maya.cmds as mc
import math

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
    matData = mc.getAttr(transform+'.'+matAttr)
    mat = om2.MMatrix(matData)
    return mat


def getRotationQuaternion(transform):
    matA = getMatrix(transform)
    tm_inMat = om2.MTransformationMatrix(matA)
    py_quat = tm_inMat.rotationComponents(asQuaternion=True)
    quat = om2.MQuaternion(py_quat)
    return quat   

quatA = getRotationQuaternion('quatA')
print(quatA)
quatA.w *= -1
print(quatA)
quat_mat = quatA.asMatrix()
print(quat_mat)

mc.xform('quatA', m =quat_mat )

quatAInv = quatA.inverse()
print(quatAInv)
quatACong = quatA.conjugate()
print(quatACong)

#result is same when using inverse, conjugate and quatA.w *= -1

