import maya.cmds as mc
import maya.api.OpenMaya as om

a = om.MVector(mc.xform('pSphere1', q = True, t = True))
b = om.MVector(mc.xform('pSphere2', q = True, t = True))

def get_projection(a, b):
    projected_vector = ((a * b)/(b*b))* b
    print(projected_vector)
    return projected_vector
    

c = get_projection(a, b)
mc.xform('pSphere3',  t = c)