# Tests for intersections between a line and a triangle
#
# Initially written as a helper method for detecting self intersections
# by Andy van Straten - 10 Oct 2014
#
# Implements Moller Trumbore ray-triangle intersection. 

import numpy
import math
import maya.cmds as mc
import maya.OpenMaya as om
import TriangleTriangleIntersection as tti

def rayTriangleIntersection( orig, p2, vert0, vert1, vert2 ):

    
    EPSILON = 10e-8
    
    # find vectors for two edges sharing vert0    
    edge1 = numpy.subtract( vert0, vert1 )
    edge2 = numpy.subtract( vert0, vert2 )

    # begin calculating determinant - also used to calculate U parameter
    dir = numpy.subtract( orig, p2 )
    dir_length = numpy.linalg.norm( dir )
    dir = numpy.divide( dir, dir_length )
    pvec = tti.pyCross( dir, edge2 )
    
    det = numpy.dot( edge1, pvec )
    
    # ignore the author's one sided triangle cull, we don' care about that. 
    # check if the point lies on the triangle
    if det > (EPSILON*-1) and det < EPSILON:
        # we're parallel with the plane, no intersection
        return 0
        
    inv_det = 1.0/det
    # calculate distance from vert0 to ray origin
    tvec = numpy.subtract( vert0, orig )    

    # calc u parameter and test bounds
    u = numpy.dot(tvec, pvec) * inv_det
    # print 'inv_det', inv_det
    if (u < 0.0) or (u > 1.0):
        #print 'outside u param'
        return 0

    qvec = tti.pyCross( tvec, edge1 )
    v = numpy.dot( dir, qvec ) * inv_det
    if (v < 0.0) or (v +u) > 1.0:
        #print 'outside v param'
        return 0

    # calculate t, the distance. I'm assuming.
    t = numpy.dot( edge2, qvec ) * inv_det
    #if the distance is negative, the ray is heading away from 
    # the plane, no intersection.
    if t < 0:  
        return 0; 
    
    # this is my code
    # need to check if the distance between points is less
    # than the distance between the origin and intersection. 
    # This allows for the line segment, rather than just the ray. 
    p1p2_vec = numpy.subtract( orig, p2 )
    p1p2_vec_length = numpy.linalg.norm( p1p2_vec )
    
    if t > p1p2_vec_length:
        return 0
    
    return 1
    
