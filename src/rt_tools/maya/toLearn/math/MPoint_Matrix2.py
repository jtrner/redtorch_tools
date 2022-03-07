import maya.cmds as mc
import maya.OpenMaya as om
from math import sqrt

def matrixFromPoint(pnts):
    mat = om.MMatrix()

    om.MScriptUtil.createMatrixFromList([
        1,0,0,0,
        0,1,0,0,
        0,0,1,0,
        pnts[0],pnts[1],pnts[2],pnts[3]], mat)
    return mat
pos = mc.xform('point', q=True, t=True)
a = om.MPoint(pos[0], pos[1], pos[2], 1)
pos2 = mc.xform('object', q=True, t=True)
b = om.MPoint(pos2[0], pos2[1], pos2[2], 1)
print(a[0])    
mat = matrixFromPoint(pnts = [a[0],a[1], a[2], 1])    
a = a * mat
c = a - b
c = a - c
mc.xform('temp', t=(a[0], a[1], a[2]))

mc.xform('final', t=(c[0], c[1], c[2]))

