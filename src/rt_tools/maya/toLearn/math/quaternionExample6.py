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
count = 1
for jnt in ['joint1', 'joint2','joint3']:
    diff_q = quatB * quatA.inverse()
    twist_q = om2.MQuaternion()
    twist_q.x = diff_q.x 
    twist_q.x = twist_q.x * count        
    twist_result = quatA * twist_q
    resultMatrix = twist_result.asMatrix()
    A = om2.MMatrix(mc.getAttr(jnt + '.worldMatrix[0]'))
    vec = getMatrixRow(3, inMat = A)
    mat = setMatrixRow(3, vec = vec, matrix = resultMatrix)   
    mc.xform(jnt, m = mat)
    count = count/2.0
    print(count)


