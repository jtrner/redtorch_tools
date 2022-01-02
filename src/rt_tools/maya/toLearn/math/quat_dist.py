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
quat_a =  getRotationQuaternion('pCube1')  
quat_b =  getRotationQuaternion('pCube2')

def quat_dot(quatA, quatB):
    dot_value = (quatA.x * quatB.x) + (quatA.y * quatB.y) + (quatA.z * quatB.z) + (quatA.w * quatB.w)
    if (dot_value < -1.0):
        dot_value = -1.0
    elif (dot_value > 1.0):
        dot_value = 1.0

    return dot_value
    
def get_quat_dist(quatA, quatB):
    
    dot = quat_dot(quatA, quatB)
    return (math.acos(2.0 * dot * dot - 1.0))
    

quat_dist = get_quat_dist(quat_a, quat_b)  
print(quat_dist)
  

