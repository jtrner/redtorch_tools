import maya.api.OpenMaya as om2
import maya.cmds as mc

def project_point_on_line(point, line_points):
    p_1, p_2 = line_points

    p1_to_p2_normal = (p_2 - p_1).normal()

    p1_to_point = point - p_1

    dist_from_p1 = p1_to_point * p1_to_p2_normal

    projected_p = p_1 + (p1_to_p2_normal * dist_from_p1)

    return projected_p

def closest_point_on_line(point, line_points):
    p_1, p_2 = line_points
    line = p_2 - p_1
    line_len = line.length()

    project_point = project_point_on_line(point, line_points)

    p1_to_proj_pnt = project_point - p_1

    dot = p1_to_proj_pnt * line
    print(dot)
    sign = 1 if dot > 0.0 else -1

    p1_to_proj_pnt_dist = p1_to_proj_pnt.length() * sign
    print(p1_to_proj_pnt_dist)

    if 0 < p1_to_proj_pnt_dist < line_len:
        print('B', 'C')
        mc.xform('locator1' ,ws = 1,t = p_1 + p1_to_proj_pnt )

        return p_1 + p1_to_proj_pnt
    if p1_to_proj_pnt_dist < line_len:
        print('B')
        mc.xform('locator1' ,ws = 1,t = p_1  )
        return p_1

    elif p1_to_proj_pnt_dist > line_len:
        print('C')
        mc.xform('locator1' ,ws = 1,t = p_1  )
        return p_2 
          
        
A = mc.xform('A' ,q= 1 ,ws = 1,t =1 )
B = mc.xform('B' ,q= 1 ,ws = 1,t =1 )
C = mc.xform('C' ,q= 1 ,ws = 1,t =1 ) 
A = om2.MVector(A)
B = om2.MVector(B)
C = om2.MVector(C)       
a = closest_point_on_line(A, [B, C])
print(a)