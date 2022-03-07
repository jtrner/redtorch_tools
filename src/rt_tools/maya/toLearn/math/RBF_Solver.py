import maya.cmds as mc
import numpy as np
import scipy.cluster
from scipy.spatial.distance import cdist
import maya.api.OpenMaya as om


def get_dist_mat(matrix):
    
    m = np.array([matrix[0],
                 matrix[1],
                 matrix[2],
                 matrix[3]])
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

matrix_weights = solve_equations(distMatrix, rotations )
target_distances = []
for pos in positions:
    dist = get_target_dist(target_pos, pos)
    target_distances.append(dist)
    
e = 2.71828
target_doubled = [x*2 for x in target_distances]
target_powered = [x**2 for x in target_doubled]

target_neg = [-1 * x for x in target_powered]
target_epsiloned = [e**x for x in target_neg]

final_poses = []

print(matrix_weights)
print(target_distances)
new_weight = 0
for weight in matrix_weights:
    new_weight = new_weight + weight
    new_matrix_weights = new_weight         
         
for pos in target_epsiloned:
    for weights in new_matrix_weights:
        new_pos = pos * weights
        final_poses.append(new_pos)
        
x_vec = final_poses[0] + final_poses[3] + final_poses[6] + final_poses[9]
y_vec = final_poses[1] + final_poses[4] + final_poses[7] + final_poses[10]
z_vec = final_poses[2] + final_poses[5] + final_poses[8] + final_poses[11]
    
print(x_vec, y_vec, z_vec)


