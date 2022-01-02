import maya.api.OpenMaya as om2
import maya.cmds as mc

A = om2.MMatrix(mc.getAttr('A.worldMatrix[0]'))
X = om2.MMatrix(mc.getAttr('X.worldMatrix[0]'))
print(A)


B = X * A

mc.xform('B', m = B)

X_x = om2.MPoint(1, 0, 0 , 1)# last item defined as origin
print(X_x * A)
X_x = om2.MPoint(1, 0, 0 , 0)
X_y = om2.MPoint(0, 1, 0 , 0)
X_z = om2.MPoint(0, 0, 1 , 0)
X_point = om2.MPoint(5, 2, 0 , 1)


B_x =  A.transpose() * X_x 
print(B_x)
B_y = X_y * A
B_z = X_z * A
B_point = X_point * A

mc.xform('axis_x_endpoint', ws = 1, t = om2.MVector(B_x))
mc.xform('axis_y_endpoint', ws = 1, t = om2.MVector(B_y))
mc.xform('axis_z_endpoint', ws = 1, t = om2.MVector(B_z))
mc.xform('axispoint', ws = 1, t = om2.MVector(B_point))