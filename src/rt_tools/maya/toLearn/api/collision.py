import maya.cmds as mc
import maya.OpenMaya as om
from math import sqrt

def getDagPath(node):
    sel = om.MSelectionList()
    sel.add(node)
    dag = om.MDagPath()
    sel.getDagPath(0, dag)
    return dag

def dot_product(x, y):
    return sum([x[i] * y[i] for i in range(len(x))])

def norm(x):
    return sqrt(dot_product(x, x))

def normalize(x):
    return [x[i] / norm(x) for i in range(len(x))]

def project_onto_plane(x, n):
    d = dot_product(x, n) / norm(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    return [x[i] - p[i] for i in range(len(x))]

ring_dag = getDagPath('ring')
bell_dag = getDagPath('bell')

ringMatrix = ring_dag.inclusiveMatrix()
bellMatrix = bell_dag.inclusiveMatrix()

ring_pos = om.MVector(ringMatrix(3,0), 
                       ringMatrix(3,1), 
                       ringMatrix(3,2))

ring_y_axis = om.MVector(ringMatrix(1,0), 
                          ringMatrix(1,1), 
                          ringMatrix(1,2))
                          
bell_pos = om.MVector(bellMatrix(3,0), 
                       bellMatrix(3,1), 
                       bellMatrix(3,2))

bell_z_axis = om.MVector(bellMatrix(1,0), 
                          bellMatrix(1,1), 
                          bellMatrix(1,2))   
                                  


ring_y_axis_pro = (ring_y_axis[0],ring_y_axis[1],ring_y_axis[2]) 
bell_z_axis_pro = (bell_z_axis[0],bell_z_axis[1],bell_z_axis[2]) 

proj_swing = project_onto_plane(ring_y_axis_pro, bell_z_axis_pro)
proj_swing = om.MVector(proj_swing[0],proj_swing[1],proj_swing[2]).normal()* 3


dist_vec = ring_pos - bell_pos
ring_plane_normalized = ring_y_axis.normal()
dist = dist_vec * ring_plane_normalized
scaled_vec = om.MVector(dist * ring_plane_normalized[0], dist * ring_plane_normalized[1], dist * ring_plane_normalized[2])
proj_ring_translate = bell_pos - scaled_vec
mc.xform('proj_ring_translate', t = (proj_ring_translate[0],proj_ring_translate[1],
                            proj_ring_translate[2]))
ray_source = proj_ring_translate + om.MVector(ring_y_axis).normal() * 3
mc.xform('ray_source', t = (ray_source[0],ray_source[1],ray_source[2]))
mc.xform('proj_swing', t = (proj_swing[0],proj_swing[1],proj_swing[2]))

meshFn = om.MFnMesh(bell_dag)
accel = meshFn.autoUniformGridParams()
hitPoints = om.MFloatPointArray()
hit_ray_params = om.MFloatArray()
hit_faces = om.MIntArray()
a = meshFn.allIntersections(om.MFloatPoint(ray_source[0],ray_source[1],ray_source[2], 1), 
                        om.MFloatVector(proj_swing[0],proj_swing[1],proj_swing[2]), 
                        None, None, False, om.MSpace.kWorld,ring_y_axis.length(), 
                        False, accel, False, hitPoints, hit_ray_params, hit_faces, 
                        None, None, None, 0.0001)
print(a)
p1 = hitPoints[0]  
if p1:
    mc.xform('p1', t = (p1[0],p1[1],p1[2]))
    
    print(hitPoints.length()) 
    ring_proj_swing = project_onto_plane((proj_swing[0],proj_swing[1],proj_swing[2]),
                                         ring_y_axis_pro)
    ring_proj_swing = om.MVector(ring_proj_swing[0], ring_proj_swing[1],
                                 ring_proj_swing[2]).normal() * 0.73
    mc.xform('ring_proj_swing', t = (ring_proj_swing[0],ring_proj_swing[1],ring_proj_swing[2]))
    
    #consider ring scale
    ring_proj_swing_inv = om.MVector(ring_proj_swing * ringMatrix.inverse())
    delta = ring_proj_swing.length() / ring_proj_swing_inv.length()
    p = ring_pos + ring_proj_swing * delta
    mc.xform('p', t = (p[0],p[1],p[2]))
    
    #Linear equation
    r = (om.MVector(p1) - bell_pos).length()
    c = om.MPoint(bell_pos)
    v = om.MVector(ring_y_axis).normal()
    
    a = v.x * v.x + v.y * v.y + v.z * v.z
    b = 2 * (v.x * (p.x - p.x) + v.y * (p.y - c.y) + v.z * (p.z - c.z)) 
    c = (p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * ( p.z - c.z) - r * r
    
    delta = b * b - 4 * a * c
    
    root1 = ((-1 * b) + sqrt(delta)) / 2 * a
    root2 = ((-1 * b) - sqrt(delta)) / 2 * a
    
    p2 = om.MVector(p + v * root1)
    mc.xform('p2', t = (p2[0],p2[1],p2[2]))
    
matrixFn = om.MTransformationMatrix(bellMatrix)   
p1_pos = mc.xform('p1', q=True, t=True)
p2_pos = mc.xform('p2', q=True, t=True)
if (proj_swing * (om.MVector(p1_pos[0],p1_pos[1],p1_pos[2]) -  om.MVector(p2_pos[0],p2_pos[1],p2_pos[2])) < 0 or bell_z_axis * ring_y_axis < 0):
    quat = om.MQuaternion(om.MVector(p1_pos[0],p1_pos[1],p1_pos[2]) - bell_pos, om.MVector(p2_pos[0],p2_pos[1],p2_pos[2]) - bell_pos, 1)
    print(quat)
    matrixFn.rotateBy(quat, om.MSpace.kTransform)

euler = matrixFn.rotation().asEulerRotation()
rotation = om.MVector(om.MAngle(euler.x).asDegrees(), om.MAngle(euler.y).asDegrees(), om.MAngle(euler.z).asDegrees())
print(rotation)
#mc.xform('bell', ro = (rotation[0],rotation[1],rotation[2]))

points = om.MPointArray()
polyIdis = om.MIntArray()
a = meshFn.intersect(om.MPoint(ray_source[0],ray_source[1],ray_source[2], 1), 
                        om.MVector(proj_swing[0],proj_swing[1],proj_swing[2]), 
                        points, 0.001, om.MSpace.kObject,polyIdis)
print(polyIdis)
print(points[0])
print(points[0][0],points[0][1],points[0][2])
