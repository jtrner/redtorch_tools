import maya.cmds as mc
import maya.api.OpenMaya as om

a = om.MPoint(mc.xform('a', q = True, t = True))
b = om.MPoint(mc.xform('b', q = True, t = True))
c = om.MPoint(mc.xform('c', q = True, t = True))
p = om.MPoint(mc.xform('p', q = True, t = True))

    
def get_projection(a, b):
    projected_vector = ((a * b)/(b*b))* b
    return projected_vector
    
ab = b - a
ac = c - a
normal = ab ^ ac
mc.xform('normal',  t = normal.normal())
projectVector = get_projection((p - a), normal)
mc.xform('p_1',  t = om.MVector(p) - om.MVector(a))

mc.xform('projectVector',  t = projectVector)
final_pos = om.MVector(p) - om.MVector(projectVector)
mc.xform('final_pos',  t = final_pos)
indexes = ['a', 'b', 'c']
disList = [p.distanceTo(vp) for vp in [a, b, c]]
print('disList', disList)
print(indexes.index('b'))
print(disList[indexes.index('a')])
indexes = sorted(indexes, key=lambda x: disList[indexes.index(x)])
print(indexes)