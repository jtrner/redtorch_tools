import maya.cmds as mc
import maya.api.OpenMaya as om2
import math

x_vector = om2.MVector(1, 0 , 0)
y_vector = om2.MVector(0, 1 , 0)
z_vector = om2.MVector(0, 0 , 1)

mc.xform('x', ws = 1, t = x_vector)
mc.xform('y', ws = 1, t = y_vector)
mc.xform('z', ws = 1, t = z_vector)

y_vector[1] = math.cos(math.radians(90))
y_vector[2] = math.sin(math.radians(90)) * -1

z_vector[1] = math.sin(math.radians(90)) * -1
z_vector[2] = math.cos(math.radians(90)) 

x_vector[0] = math.sin(math.radians(90)) * -1 
x_vector[1] = math.cos(math.radians(90)) 

y_vector[2] = math.sin(math.radians(90)) 

z_vector[1] = math.sin(math.radians(90)) * -1

x_vector[0] = math.sin(math.radians(90)) * -1 

y_vector[2] = math.sin(math.radians(90)) * -1

x_vector[0] = math.sin(math.radians(90)) 

z_vector[1] = math.sin(math.radians(90)) 

y_vector[2] = math.sin(math.radians(90)) 

x_vector[0] = math.sin(math.radians(90)) * -1 

z_vector[1] = math.sin(math.radians(90)) * -1

y_vector[2] = math.sin(math.radians(90)) * -1

x_vector[0] = math.sin(math.radians(90)) * -1 

z_vector[1] = math.sin(math.radians(90)) * -1

y_vector[2] = math.sin(math.radians(90)) * -1

x_vector[0] = math.sin(math.radians(90)) * -1 

z_vector[1] = math.sin(math.radians(90)) * -1







 
mc.xform('x', ws = 1, t = x_vector)
mc.xform('y', ws = 1, t = y_vector)
mc.xform('z', ws = 1, t = z_vector)