import maya.OpenMaya as om
import maya.api.OpenMaya as om

import maya.cmds as mc

def matFromList(matList):
    mat = om.MMatrix()
    util = om.MScriptUtil()
    util.createMatrixFromList(matList, mat)
    return mat
    
a = mc.getAttr('pSphere2.worldMatrix[0]')
first = om.MMatrix(a)
print(first)
first = first.inverse()

b = mc.getAttr('pSphere4.worldMatrix[0]')
second = om.MMatrix(b)
print(second)

f = mc.getAttr('pSphere5.worldMatrix[0]')
third = om.MMatrix(f)
print(third)

c =   second.transpose()* first.transpose()
d = c.transpose()

e = d * second

mc.xform('pSphere5', m = e)