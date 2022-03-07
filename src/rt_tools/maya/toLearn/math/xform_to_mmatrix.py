import maya.cmds as mc
import maya.OpenMaya as om
from math import sqrt


def floatMMatrixToMMatrix_(fm):
    mat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList ([
        fm[0],fm[1],fm[2],fm[3],
        fm[4],fm[5],fm[6],fm[7],
        fm[8],fm[9],fm[10],fm[11],
        fm[12],fm[13],fm[14],fm[15]], mat)
    return mat

obj_mat = mc.xform('locator1',q=True, m=True)
print(obj_mat)
colliderMatrixValue = floatMMatrixToMMatrix_(obj_mat) 
print(colliderMatrixValue[0]) 

pos = mc.xform('pSphere1',q=True, t=True)
pos = om.MPoint(pos[0], pos[1], pos[2],1) 
Matrix_multiply = pos * colliderMatrixValue.inverse()
mat_vec = om.MVector(Matrix_multiply[0], Matrix_multiply[1], Matrix_multiply[2])
normal_vec = mat_vec.normal()
normal_point = om.MPoint(normal_vec[0], normal_vec[1], normal_vec[2], 1)
target = mc.xform('pSphere1',q=True, m=True)
target = floatMMatrixToMMatrix_(target) 
new_pos = normal_vec + om.MVector(pos[0], pos[1], pos[2])
#new_pos = pos - new_pos                
mc.xform('pSphere3', t=(new_pos[0], new_pos[1], new_pos[2]))

