"""
FINDING OPTIMAL ROTATION AND TRANSLATION BETWEEN CORRESPONDING 3D POINTS
Nghia Ho
http://nghiaho.com/?page_id=671


"""

import sys
path = "F:\\softwares\\numpy.1.9.2"
if path not in sys.path:
    sys.path.append( path )

import numpy as np
#from math import sqrt
import maya.cmds as mc

mc
def rigid_transform_3D( A, B ):
    assert len(A) == len(B)

    N = A.shape[0] # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # centre the points
    AA = A - np.tile(centroid_A, (N, 1))
    BB = B - np.tile(centroid_B, (N, 1))

    # covariance matrix
    H = np.transpose(AA).dot( BB )

    # SVD
    U, S, Vt = np.linalg.svd(H)

    # rotation
    R = Vt.T * U.T

    # special reflection case
    if np.linalg.det(R) < 0:
       print "Reflection detected"
       Vt[2,:] *= -1
       R = Vt.T * U.T
    """
    if determinant(R) &lt; 0
        multiply 3rd column of V by -1
        recompute R
    end if

    or better?
    
    if determinant(R) &lt; 0
        multiply 3rd column of R by -1
    end if
    """

    # translation
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

import sys
path = "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin"
if path not in sys.path:
    sys.path.append( path )
    
    
import ehm_plugins.ehm_rigidTransform.rigidTransform as rigid
reload( rigid )

A = rigid.matrixArrayFromTransform( mc.ls("A?") )
B = rigid.matrixArrayFromTransform( mc.ls("B?") )

r, t = rigid.rigid_transform_3D(A, B)
rigid.setFromRT( "fourByFourMatrix1", r, t )

"""


"""
# original code
#============================================
from numpy import *
from math import sqrt

# Input: expects Nx3 matrix of points
# Returns R,t
# R = 3x3 rotation matrix
# t = 3x1 column vector

def rigid_transform_3D(A, B):
    assert len(A) == len(B)

    N = A.shape[0]; # total points

    centroid_A = mean(A, axis=0)
    centroid_B = mean(B, axis=0)
    
    # centre the points
    AA = A - tile(centroid_A, (N, 1))
    BB = B - tile(centroid_B, (N, 1))

    # dot is matrix multiplication for array
    H = transpose(AA) * BB

    U, S, Vt = linalg.svd(H)

    R = Vt.T * U.T

    # special reflection case
    if linalg.det(R) < 0:
       print "Reflection detected"
       Vt[2,:] *= -1
       R = Vt.T * U.T

    t = -R*centroid_A.T + centroid_B.T

    print t

    return R, t

# Test with random data

# Random rotation and translation
R = mat(random.rand(3,3))
t = mat(random.rand(3,1))

# make R a proper rotation matrix, force orthonormal
U, S, Vt = linalg.svd(R)
R = U*Vt

# remove reflection
if linalg.det(R) < 0:
   Vt[2,:] *= -1
   R = U*Vt

# number of points
n = 10

A = mat(random.rand(n,3));
B = R*A.T + tile(t, (1, n))
B = B.T;

# recover the transformation
ret_R, ret_t = rigid_transform_3D(A, B)

A2 = (ret_R*A.T) + tile(ret_t, (1, n))
A2 = A2.T

# Find the error
err = A2 - B

err = multiply(err, err)
err = sum(err)
rmse = sqrt(err/n);

print "Points A"
print A
print ""

print "Points B"
print B
print ""

print "Rotation"
print R
print ""

print "Translation"
print t
print ""

print "RMSE:", rmse
print "If RMSE is near zero, the function is correct!"

"""