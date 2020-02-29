import numpy as np
from math import sqrt
import maya.cmds as mc

# inputs
locs_a = mc.ls( "A?" )
locs_b = mc.ls( "B?" )

# make matrices using positions
A = np.array( [mc.xform(x,q=1,ws=1,t=1) for x in locs_a] )
B = np.array( [mc.xform(x,q=1,ws=1,t=1) for x in locs_b] )

    assert len(A) == len(B)

    N = A.shape[0] # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # centre the points
    AA = A - np.tile(centroid_A, (N, 1))
    BB = B - np.tile(centroid_B, (N, 1))

    # dot is matrix multiplication for array
    H = np.transpose(AA).dot( BB )

    U, S, Vt = np.linalg.svd(H)

    R = Vt.T * U.T

    # special reflection case
    if np.linalg.det(R) < 0:
       print "Reflection detected"
       Vt[2,:] *= -1
       R = Vt.T * U.T

    t = -R*centroid_A.T + centroid_B.T

    return R, t



def matrixArrayFromTransform( objs ):
mat = []
for obj in objs:
    t = mc.xform( obj, q=1, ws=1, t=1 )
    mat.append( t )
return np.matrix( mat )



def setFromRT( fourByFour, r, t ):
for i in xrange(3):
    for j in xrange(3):
        mc.setAttr( "{0}.in{1}{2}".format(fourByFour, i, j), r[j,i] )

for i in xrange(3):
    mc.setAttr( "{0}.in3{1}".format(fourByFour, i), t[i,0] )
   
   
"""   

A = matrixArrayFromTransform( mc.ls(sl=1) )
B = matrixArrayFromTransform( mc.ls(sl=1) )

r, t = rigid_transform_3D(A, B)
setFromRT( "fourByFourMatrix1", r, t )

"""
