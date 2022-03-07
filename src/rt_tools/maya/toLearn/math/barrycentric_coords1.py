import maya.api.OpenMaya as om2
import maya.cmds as mc
import math
def project_point_on_line(point, line_points):
    p_1, p_2 = line_points

    p1_to_p2_normal = (p_2 - p_1).normal()

    p1_to_point = point - p_1

    dist_from_p1 = p1_to_point * p1_to_p2_normal

    projected_p = p_1 + (p1_to_p2_normal * dist_from_p1)

    return projected_p
    
def anotherway(point, line_points):
    p_1, p_2 = line_points

    p1_to_p2 = p_2 - p_1
    p1_to_point = point - p_1
   
    dot = p1_to_point * p1_to_p2
  
    
    proj = float(dot) /float(p1_to_p2.length())
    proj = p1_to_p2.normal() * proj   
    proj = p_1 + proj

def get_point_ratio_on_line(point, line_points):
    p_1, p_2, p_3 = line_points

    projected_point = project_point_on_line(point, [p_1, p_2])
    proj_point = anotherway(point, [p_1, p_2])

    d_1 = (p_1 - projected_point).length()
    d_2 = (p_2 - projected_point).length()
    d_3 = (p_3 - projected_point).length()
    dists = [d_1, d_2, d_3]

    biggest_dist_value_index = dists.index(max(dists))

    if biggest_dist_value_index == 0:
        w_1 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_3 - p_2).length()
        if d_2 > line_len:  # point is too far from p_2
            w_2 = 0.0
            w_3 = 1.0
        elif d_3 > line_len:  # point is too far from p_3
            w_3 = 0.0
            w_2 = 1.0
        else:  # point is somewhere between p_2 and p_3
            w_2 = 1.0 - (d_2 / line_len)
            w_3 = 1.0 - w_2
            print(w_3)

    elif biggest_dist_value_index == 1:
        w_2 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_3 - p_1).length()
        if d_1 > line_len:  # point is too far from p_1
            w_1 = 0.0
            w_3 = 1.0
        elif d_3 > line_len:  # point is too far from p_3
            w_3 = 0.0
            w_1 = 1.0
        else:  # point is somewhere between p_1 and p_3
            w_1 = 1.0 - (d_1 / line_len)
            w_3 = 1.0 - w_1

    elif biggest_dist_value_index == 2:
        w_3 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_2 - p_1).length()
        if d_2 > line_len:  # point is too far from p_2
            w_2 = 0.0
            w_1 = 1.0
        elif d_1 > line_len:  # point is too far from p_1
            w_1 = 0.0
            w_2 = 1.0
        else:  # point is somewhere between p_1 and p_2
            w_1 = 1.0 - (d_1 / line_len)
            w_2 = 1.0 - w_1

    return w_1, w_2, w_3

def project_point_on_plane(point, triangle_points):
    p_1, p_2, p_3 = triangle_points

    tri_normal = ((p_2 - p_1) ^ (p_3 - p_1)).normal()

    p1_to_point = point - p_1

    perpendular_distance = p1_to_point * tri_normal

    projected_point = point - (tri_normal * perpendular_distance)

    return projected_point
    
def closest_point_on_line(point, line_points):
    p_1, p_2 = line_points
    line = p_2 - p_1
    line_len = line.length()

    project_point = project_point_on_line(point, line_points)
    p1_to_proj_pnt = project_point - p_1

    dot = p1_to_proj_pnt * line
    sign = 1 if dot > 0.0 else -1

    p1_to_proj_pnt_dist = p1_to_proj_pnt.length() * sign

    if 0 < p1_to_proj_pnt_dist < line_len:
        return p_1 + p1_to_proj_pnt
    if p1_to_proj_pnt_dist < line_len:
        return p_1
    elif p1_to_proj_pnt_dist > line_len:
        return p_2    

A = mc.xform('A' ,q= 1 ,ws = 1,t =1 )
B = mc.xform('B' ,q= 1 ,ws = 1,t =1 )
C = mc.xform('C' ,q= 1 ,ws = 1,t =1 )
point = mc.xform('point' ,q= 1 ,ws = 1,t =1 )
A = om2.MVector(A)
B = om2.MVector(B)
C = om2.MVector(C)
point = om2.MVector(point)

get_point_ratio_on_line(point = point, line_points = [A , B, C])