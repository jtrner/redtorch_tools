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
    print("matrix is '{}'".format(matA))
    tm_inMat = om2.MTransformationMatrix(matA)
    print("transfromation matrix is '{}'".format(tm_inMat))
    py_quat = tm_inMat.rotationComponents(asQuaternion=True)
    print("rotation component is '{}'".format(py_quat))
    quat = om2.MQuaternion(py_quat)
    print("Quaternion is '{}'".format(quat))
    return quat   
transA_a =  getRotationQuaternion('transformA')  
print(transA_a)
transA_mat = getMatrix('transformA')
transA_pos = getMatrixRow(3, transA_mat)
print(transA_pos)
rotate_q = om2.MQuaternion()
print(rotate_q)
rotate_q.setToYAxis(math.radians(90))
print(rotate_q)
result_q = rotate_q * transA_a
print(result_q)
resultMatrix = result_q.asMatrix()
print(resultMatrix)

setMatrixRow(3, transA_pos, resultMatrix)
print(resultMatrix)


mc.xform('transformOut', m = resultMatrix)


