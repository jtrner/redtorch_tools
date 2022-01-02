from rig_math.matrix import Matrix
from rig_math.vector import Vector

import maya.cmds as mc

count = 500


matrix_1 = Matrix(mc.xform('locator1', q=True, m=True, ws=True))
matrix_2 = Matrix(mc.xform('locator2', q=True, m=True, ws=True))


for i in range(count):
    matrix = interpolate_matrices(matrix_1, matrix_2, i=1.0/count*(i+1))
    mc.xform('locator3', m=list(matrix), ws=True)
    mc.refresh()



def interpolate_matrices(matrix_1, matrix_2, i=0.5):
    print i
    result = Matrix()
    
    X1 = matrix_1.x_vector()
    Y1 = matrix_1.y_vector()
    Z1 = matrix_1.z_vector()
    T1 = matrix_1.get_translation()
    
    X2 = matrix_2.x_vector()
    Y2 = matrix_2.y_vector()
    Z2 = matrix_2.z_vector()
    T2 = matrix_2.get_translation()
    
    result.data = [[],[],[],[]]
    
    result.data[0].extend(list((X1*i) + (X2*(1.0-i))))
    result.data[0].append(0)
    result.data[1].extend(list((Y1*i) + (Y2*(1.0-i))))
    result.data[1].append(0)
    
    result.data[2].extend(list((Z1*i) + (Z2*(1.0-i))))
    result.data[2].append(0)
    
    result.data[3].extend(list((T1*i) + (T2*(1.0-i))))
    result.data[3].append(1)
    return result