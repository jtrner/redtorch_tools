import maya.cmds as mc
import maya.api.OpenMaya as om
from math import sqrt
pos = mc.xform('pSphere12', q=True, t=True)
obj1 = om.MPoint(pos)
obj2 = om.MMatrix(mc.xform('pSphere13', q=True, m=True))
mat = obj2.transpose().inverse() * obj1

print(mat)


mc.xform('pSphere14', t = (mat[0], mat[1], mat[2]))


