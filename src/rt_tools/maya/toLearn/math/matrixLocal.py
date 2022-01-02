import maya.api.OpenMaya as om2
import maya.cmds as mc

A = om2.MMatrix(mc.getAttr('A.matrix'))
B = om2.MMatrix(mc.getAttr('B.matrix'))
C = om2.MMatrix(mc.getAttr('C.matrix'))
D = om2.MMatrix(mc.getAttr('D.matrix'))
E = om2.MMatrix(mc.getAttr('E.matrix'))

#xA = B
# row major
result = E * D * C *B * A 
print(result)
# col major
result = A.transpose() * B.transpose() * C.transpose() * D.transpose() * E.transpose() 
result = result.transpose()
print(result)


mc.xform('resultMatrix', m = result)