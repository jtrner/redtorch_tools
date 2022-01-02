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
quatA = getRotationQuaternion('QuatA')
quatB = getRotationQuaternion('QuatB')


quatResult = om2.MQuaternion()
quatResult = quatResult.slerp(quatA, quatB, 0.1)
resultMatrix = quatResult.asMatrix()
mc.xform('QuatOut', m = resultMatrix)

import time

for x in range(11):
    step = x/10.0
    print(step)
    quatResult = quatResult.slerp(quatA,quatB,step)
    resultMatrix = quatResult.asMatrix()
    mc.xform('QuatOut', m = resultMatrix)
    maya.cmds.refresh()
    time.sleep(0.25)







