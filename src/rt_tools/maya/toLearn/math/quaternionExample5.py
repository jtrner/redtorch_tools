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

#diff_q = quatB * quatA.inverse()
#print(diff_q)
#result_q = diff_q * quatA
#resultMatrix = result_q. asMatrix()
#mc.xform('QuatA', m = resultMatrix)
#calculating the differ ,then multiplying quatA to differ to finding quatB
diff_q = quatB * quatA.inverse()
print(diff_q)

twist_q = om2.MQuaternion()
twist_q.x = diff_q.x
print(twist_q.x)

twist_result = quatA * twist_q
print(twist_result)
resultMatrix = twist_result.asMatrix()
mc.xform('QuatTwist', m = resultMatrix)




