import maya.cmds as mc
import numpy as np
import scipy.cluster
from scipy.spatial.distance import cdist
import maya.api.OpenMaya as om


def get_dist_mat(matrix):
    arr = []
    for mat in matrix:
        arr.append(mat)   
    m = np.array(arr)
    distMatrix = cdist(m, m, "euclidean")
    
    return distMatrix

def solve_equations(array_a, array_b):
    a = np.array([array_a])
    b = np.array([array_b])   
    weight_matrix = np.linalg.solve(a, b)[0]

    return weight_matrix 
    
def get_target_dist(target, value):
    first = om.MVector(target )
    second = om.MVector( value)
    newVec = second - first
    return newVec.length() 
    
def gaussian(matrix, radius):
    radius *= 0.707
    result = np.exp(-(matrix * matrix) / (2.0 * radius * radius))
    return result 
    
def get_final_weights(target_distances, matrix_weights):
    final_poses = []
    new_poses = []
    new_wgts = []
    for pos, weight in zip(target_distances,matrix_weights):   
        new_pos = pos * weight
        new_poses.append(new_pos)                  
    new_weight = 0     
    for new_position in new_poses:
        new_weight = new_weight + new_position        
        final_poses = new_weight 
     
    return(final_poses)
       
              
rotations = []
positions = []
for i in ['pSphere2','pSphere3','pSphere4','pSphere5']:
    pos = mc.getAttr(i + '.t')[0]
    pos = [x for x in pos]
    positions.append(pos)
    rot = mc.getAttr(i + '.r')[0]
    rot = [x for x in rot]
    rotations.append(rot)
target_pos = mc.getAttr('pSphere1' + '.t')[0]

distMatrix = get_dist_mat(positions)

target_distances = []
for pos in positions:
    dist = get_target_dist(target_pos, pos)
    target_distances.append(dist)
    
guss = gaussian(np.array(target_distances), radius=10)
##################################################################
blend_list = []
for i in range(len(guss)):
    pose_list = []
    for j in range(len(guss)):
        pose_list.append(0)
    blend_list.append(pose_list)

for i,lis in enumerate(blend_list):
    for j,item in enumerate(lis):
        if i == j:
            blend_list[i][j] = 1
            
new_blend_weight = []
for blend_gu, blend_w in zip(guss, np.array(blend_list)):
    new_blend = blend_gu * blend_w
    new_blend_weight.append(new_blend)  


interp_type = 'linear'
if interp_type == 'linear':  
    blend_matrix_weights = solve_equations(distMatrix, blend_list )
if interp_type == 'Gussian':  
    blend_matrix_weights = solve_equations(distMatrix, new_blend_weight )
  
final_blend = get_final_weights(target_distances, blend_matrix_weights)
print(final_blend)                
##################################################################
new_rotations = []
for gu, rot in zip(guss, np.array(rotations)):
    new_rot = gu * rot
    new_rotations.append(new_rot)


if interp_type == 'linear':  
    matrix_weights = solve_equations(distMatrix, rotations )
if interp_type == 'Gussian':  
    matrix_weights = solve_equations(distMatrix, new_rotations )
    
  
final_poses = get_final_weights(target_distances, matrix_weights)
print(final_poses)
