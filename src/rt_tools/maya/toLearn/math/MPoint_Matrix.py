import maya.cmds as mc
import maya.api.OpenMaya as om
from math import sqrt
pos = mc.xform('a', q=True, t=True)
a = om.MPoint(pos)
pos2 = mc.xform('b', q=True, t=True)
b = om.MPoint(pos2)
mat = om.MMatrix(mc.xform('mat', q=True, m=True))
print(mat)
d = a * mat
c = d - b
print(c)
print(d)
mc.xform('c', t = om.MVector(c))
