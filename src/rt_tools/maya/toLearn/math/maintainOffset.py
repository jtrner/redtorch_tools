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
obj_pos = mc.xform('locator1',q=True, t=True)
obj_pos = om.MPoint(obj_pos[0], obj_pos[1], obj_pos[2], 1)
print(obj_mat)
colliderMatrixValue = floatMMatrixToMMatrix_(obj_mat) 
print(colliderMatrixValue[0]) 

pos = mc.xform('pSphere1',q=True, t=True)
pos = om.MPoint(pos[0], pos[1], pos[2],1) 
worldPoint = pos * colliderMatrixValue
mc.xform('worldPoint', t=(worldPoint[0], worldPoint[1], worldPoint[2]))

dif_x_vec = worldPoint.x - obj_pos.x

dif_y_vec = worldPoint.y - obj_pos.y

dif_z_vec = worldPoint.z - obj_pos.z

mc.xform('pSphere2', t=(dif_x_vec,dif_y_vec, dif_z_vec))

