#
# Python implementation of Tomas Moller's triangle-triangle intersection algorithm
# for intersections between objects
# Python implementation of the Moller Trumbore ray-triangle intersection for 
# self intersections of polygons sharing an edge.
#
# Andy van Straten - 10 Oct 2014
#
#
# --------- ESSENTIAL NOTES  -------------- #
#
# YOU WILL NEED the numpy library installed on your machine. 
# www.numpy.org
#
#
#
# ---------- USAGE ------------------------ # 
#
# --  For intersections between objects: -- # 
# 
# 1. Make sure TriangleTriangleIntersection.py and RayTriangleIntersection.py are 
#    in your scripts directory. 
#
# 2. Select two meshes. ( Make sure transforms are frozen! )
#
# 3. Execute the following commands from your script editor: 
#
#    import TriangleTriangleIntersection as tti
#    tti.mollerIntersect()
#
#
#
# -- For self intersections: -------------- # 
#
# 1. Make sure TriangleTriangleIntersection.py and RayTriangleIntersection.py are 
#    in your scripts directory. 
# 
# 2. Select a mesh ( Make sure transforms are frozen )
#
# 3. Execute the following commands from your script editor: 
#    
#    import TriangleTriangleIntersection as tti
#    tti.mollerSelfIntersect()
    




import numpy
import math
import maya.cmds as mc
import maya.OpenMaya as om
import RayTriangleIntersection as rti
reload(rti)

EPSILON = 10e-8

def rayTriangleIntersection():
    
    # test with locators
    sl = mc.ls( os=True)
    orig = mc.xform( sl[3], q=True, t=True, ws=True )
    orig = numpy.array( [orig[0], 
                         orig[1], 
                         orig[2]] )
    dir  = mc.xform( sl[4], q=True, t=True, ws=True )
    dir  = numpy.array( [dir[0], 
                         dir[1], 
                         dir[2]] )
    vert0 = mc.xform( sl[0], q=True, t=True, ws=True )
    vert0 = numpy.array( [vert0[0], 
                          vert0[1], 
                          vert0[2]] )
    vert1 = mc.xform( sl[1], q=True, t=True, ws=True )
    vert1 = numpy.array( [vert1[0], 
                          vert1[1], 
                          vert1[2]] )
    vert2 = mc.xform( sl[2], q=True, t=True, ws=True )
    vert2 = numpy.array( [vert2[0], 
                          vert2[1], 
                          vert2[2]] )                          
    
    return rti.rayTriangleIntersection( orig, dir, vert0, vert1, vert2 )
    


def initialise_from_locators():
    sl = mc.ls( sl=True )
    tri1_v0 = mc.xform( sl[0], q=True, t=True, ws=True )
    tri1_v0_np = numpy.array([tri1_v0[0],
                              tri1_v0[1], 
                              tri1_v0[2] ])
    tri1_v1 = mc.xform( sl[1], q=True, t=True, ws=True )
    tri1_v1_np = numpy.array([tri1_v1[0],
                              tri1_v1[1], 
                              tri1_v1[2] ])
    tri1_v2 = mc.xform( sl[2], q=True, t=True, ws=True )
    tri1_v2_np = numpy.array([tri1_v2[0],
                              tri1_v2[1], 
                              tri1_v2[2] ])
    
    tri2_v0 = mc.xform( sl[3], q=True, t=True, ws=True )
    tri2_v0_np = numpy.array([tri2_v0[0],
                              tri2_v0[1], 
                              tri2_v0[2] ])
    tri2_v1 = mc.xform( sl[4], q=True, t=True, ws=True )
    tri2_v1_np = numpy.array([tri2_v1[0],
                              tri2_v1[1], 
                              tri2_v1[2] ])
    tri2_v2 = mc.xform( sl[5], q=True, t=True, ws=True )
    tri2_v2_np = numpy.array([tri2_v2[0],
                              tri2_v2[1], 
                              tri2_v2[2] ])
                             
    tri_1 = [ tri1_v0_np, tri1_v1_np, tri1_v2_np ]                        
    tri_2 = [ tri2_v0_np, tri2_v1_np, tri2_v2_np ]                        
    
    return [tri_1, tri_2]

def initialise_variables():
    # get verts
    tri_1 = 'ABC'
    tri_2 = 'DEF'
    sel = om.MSelectionList()
    sel.add( tri_1 )
    sel.add( tri_2 )
    
    tri_1_dagPath = om.MDagPath()
    tri_2_dagPath = om.MDagPath()
    
    sel.getDagPath( 0, tri_1_dagPath )
    sel.getDagPath( 1, tri_2_dagPath )
    
    tri_1_it = om.MItMeshVertex( tri_1_dagPath )
    tri_2_it = om.MItMeshVertex( tri_2_dagPath )
    
    tri_1 = list()
    tri_2 = list()    
    
    while not tri_1_it.isDone():
        
        vert_mpoint = tri_1_it.position()
        vert_xyz = numpy.array([vert_mpoint.x, 
                             vert_mpoint.y,
                             vert_mpoint.z ])
                             
        tri_1.append(vert_xyz)
        tri_1_it.next()
    
    while not tri_2_it.isDone():
        
        vert_mpoint = tri_2_it.position()
        vert_xyz = numpy.array([vert_mpoint.x, 
                             vert_mpoint.y,
                             vert_mpoint.z ])
                             
        tri_2.append(vert_xyz)
        tri_2_it.next()
    
    return [tri_1, tri_2]

def drawLoc( p ):

    loc = mc.spaceLocator()[0]
    mc.setAttr( loc + '.tx', p[0] )
    mc.setAttr( loc + '.ty', p[1] )
    mc.setAttr( loc + '.tz', p[2] )
    return loc

def drawTriangle( tri ):
    for p in tri:
       drawLoc( p ) 
    
def pyCross( a, b ):
    #.. because for some reason numpy..cross is mega slow
    x = (a[1] * b[2]) - (a[2] * b[1])
    y = (a[2] * b[0]) - (a[0] * b[2])
    z = (a[0] * b[1]) - (a[1] * b[0])
    return numpy.array([x, y, z ])

def distSquared( a, b ):
    x = (a[0] - b[0]) ** 2
    y = (a[1] - b[1]) ** 2
    z = (a[2] - b[2]) ** 2
    return x + y + z

def centerPoint( triangle ):
    sum = numpy.add( triangle[0], triangle[1] )    
    sum = numpy.add( sum, triangle[2] )
    return numpy.array([sum[0]/3, sum[1]/3, sum[2]/3 ])  
    
def signed_dist_check( triangles ):

    p2_0 = triangles[1][0]
    p2_1 = triangles[1][1]
    p2_2 = triangles[1][2]
    
    p2_01_vec = numpy.subtract( p2_1, p2_0 )
    p2_02_vec = numpy.subtract( p2_2, p2_0 )
    
    p2_n = pyCross( p2_01_vec, p2_02_vec )
    
    #p2_length = numpy.linalg.norm( p2_n )
    #p2_n_unit = numpy.divide( p2_n, p2_length )
    #p2_n = p2_n_unit
    
    #p1_length = numpy.linalg.norm( p1_n )
    #p1_n_unit = numpy.divide( p1_n, p1_length )
    #p1_n = p1_n_unit
    
    d2 = numpy.dot( p2_n, p2_0 ) * -1    
    
    distances_tri1 = list()
    
    for v1 in triangles[0]:
        signed_dist = numpy.dot( p2_n, v1 ) + d2
        distances_tri1.append( signed_dist )
    
    d0d1 = distances_tri1[0] * distances_tri1[1]
    d0d2 = distances_tri1[0] * distances_tri1[2]
    
    if d0d1 > 0 and d0d2 > 0:
        return [0]
        
    
    if abs(distances_tri1[0]) < EPSILON and abs(distances_tri1[1]) < EPSILON and abs(distances_tri1[2]) < EPSILON : 
        # print' HELLO coplanar 1'
        # print 'testing for coplanar intersection'
        if coplanar_tri_tri( p2_n, triangles[0], triangles[1] ):
            # print 'coplanar intersection detected'
            return [2]
        else:
            # print 'triangles are coplanar, and intersection has been ruled out'
            return [0]
        
    ## run same test on other triangle    
    
    p1_0 = triangles[0][0]
    p1_1 = triangles[0][1]
    p1_2 = triangles[0][2]
    
    p1_01_vec = numpy.subtract(p1_1, p1_0)
    p1_02_vec = numpy.subtract(p1_2, p1_0)
    
    p1_n = pyCross( p1_01_vec, p1_02_vec )
    
    d1 = numpy.dot( p1_n, p1_0 ) * -1
    distances_tri2 = list()
    
    for v2 in triangles[1]:
        signed_dist = numpy.dot( p1_n, v2 ) + d1
        distances_tri2.append( signed_dist )
    
    '''
    print distances_tri1[0]
    print distances_tri1[1]
    print distances_tri1[2]
    print ''
    
    print distances_tri2[0]
    print distances_tri2[1]
    print distances_tri2[2]
    print ''
    '''
    
    d0d1 = distances_tri2[0] * distances_tri2[1]
    d0d2 = distances_tri2[0] * distances_tri2[2]
    if d0d1 > 0 and d0d2 > 0:
        return [0]
        
    if abs(distances_tri2[0]) < EPSILON and abs(distances_tri2[1]) < EPSILON and abs(distances_tri2[2]) < EPSILON : 
        # print ' HELLO coplanar 2'
        
        if coplanar_tri_tri( p1_n, triangles[1], triangles[0] ):
            # print 'coplanar intersection detected'
            return [2]
        else:
            # print 'triangles are coplanar, and intersection has been ruled out'
            return [0]
    
    # print 'there can be still an intersection'
    return [ 1, [ distances_tri1, distances_tri2 ] ]

    
def coplanar_tri_tri( normal, tri1_pts, tri2_pts ):  
    # method to handle triangle intersection test if the triangles are coplanar.

    abs_n = list()
    index0 = int()
    index1 = int()
    
    # first project onto an axis-aligned plane, that maximizes the area
    # of the triangles, compute indices: i0,i1.
    abs_n.append( math.fabs(normal[0]) )
    abs_n.append( math.fabs(normal[1]) )
    abs_n.append( math.fabs(normal[2]) )
    
    if abs_n[0]> abs_n[1] : 
        if abs_n[0]> abs_n[2]: 
            index0=1      # abs_n[0] is greatest #
            index1=2
        else:
            index0=0
            index1=1

    else:  # abs_n[0]<=abs_n[1] #
        if abs_n[2] > abs_n[1]:
            index0=0
            index1=1
        else: 
            index0=0
            index1=2
    
    # first check if any of the edges intersect
    if edge_against_tri_edges( tri1_pts[0], tri1_pts[1], tri2_pts, index0, index1 ):
        #print 'intersection detected, 1'
        return 1
    if edge_against_tri_edges( tri1_pts[1], tri1_pts[2], tri2_pts, index0, index1 ):
        #print 'intersection detected, 2'
        return 1
    if edge_against_tri_edges( tri1_pts[2], tri1_pts[0], tri2_pts, index0, index1 ):
        #print 'intersection detected, 2'
        return 1

    return 0

def edge_edge_test( v_0, p_0, p_1, a_x, a_y, i0, i1 ):
    b_x = p_0[i0] - p_1[i0]
    b_y = p_0[i1] - p_1[i1]
    
    c_x = v_0[i0] - p_0[i0]
    c_y = v_0[i1] - p_0[i1]
    
    f = a_y*b_x - a_x*b_y
    d = b_y*c_x - b_x*c_y
    
    if ( ( f>0 and d>=0 and d<=f ) or (f<0 and d<=0 and d>=f) ) :
        e = a_x*c_y - a_y*c_x
        if f>0:
            if e>=0 and e<=f:
                return 1
            elif e<=0 and e>=f: 
                return 1
    
    return 0
    
    
def edge_against_tri_edges( p_0, p_1, tri_pts, i0, i1 ):
    
    a_x = p_1[i0] - p_0[i0]
    a_y = p_1[i1] - p_0[i1]
    
    if edge_edge_test( p_0, tri_pts[0], tri_pts[1], a_x, a_y, i0, i1 ):
        return 1
    if edge_edge_test( p_0, tri_pts[1], tri_pts[2], a_x, a_y, i0, i1 ):
        return 1
    if edge_edge_test( p_0, tri_pts[2], tri_pts[0], a_x, a_y, i0, i1 ):
        return 1
    
    return 0

def interval_test( triangles, distances ):
    
    # print 'triangles', triangles
    p1_0 = triangles[0][0]
    p1_1 = triangles[0][1]
    p1_2 = triangles[0][2]
    
    p2_0 = triangles[1][0]
    p2_1 = triangles[1][1]
    p2_2 = triangles[1][2]
    
    
    p1_01_vec = numpy.subtract(p1_1, p1_0)
    p1_02_vec = numpy.subtract(p1_2, p1_0)
    p1_n = pyCross( p1_01_vec, p1_02_vec )
    
    p2_01_vec = numpy.subtract(p2_1, p2_0)
    p2_02_vec = numpy.subtract(p2_2, p2_0)
    p2_n = pyCross( p2_01_vec, p2_02_vec )
    
    #    L = O + tD where D = N1 x N2 is the direction of the 
    #    line and O is some point on it
    # print p2_n
    D = pyCross( p1_n, p2_n )
        
    D_length = numpy.linalg.norm( D )
    D_unit = numpy.divide( D, D_length )
    D = D_unit
        
    # project points from triangle 1 on the of intersection
    
    tri1_projs = list()
    tri2_projs = list()
    
    proj_tri1_0 = numpy.dot( D, p1_0 )
    proj_tri1_1 = numpy.dot( D, p1_1 )
    proj_tri1_2 = numpy.dot( D, p1_2 )
    '''
    drawLoc( numpy.multiply( proj_tri1_0, D ) )  
    drawLoc( numpy.multiply( proj_tri1_1, D ) )  
    drawLoc( numpy.multiply( proj_tri1_2, D ) )  
    '''
    tri1_projs.append( proj_tri1_0 )
    tri1_projs.append( proj_tri1_1 )
    tri1_projs.append( proj_tri1_2 )
    
    proj_tri2_0 = numpy.dot( D, p2_0 )
    proj_tri2_1 = numpy.dot( D, p2_1 )
    proj_tri2_2 = numpy.dot( D, p2_2 )
    '''
    drawLoc( numpy.multiply( proj_tri2_0, D ) )  
    drawLoc( numpy.multiply( proj_tri2_1, D ) )  
    drawLoc( numpy.multiply( proj_tri2_2, D ) )
    '''
    tri2_projs.append( proj_tri2_0 )
    tri2_projs.append( proj_tri2_1 )
    tri2_projs.append( proj_tri2_2 )
    
    # now we need to decide which vectors to find intersections. 
    # because we haven't rejected so far, 2 vertices will lie on one 
    # side of the plane, and 1 will be on the other, for both triangles.
    
    d_tri1 = distances[0]
    d_tri2 = distances[1]
    
    i0 = None
    i1 = None
    i2 = None
    
    if d_tri1[0] * d_tri1[1] > 0.0:
        i0 = 0
        i1 = 1
        i2 = 2
    elif  d_tri1[0] * d_tri1[2] > 0.0:   
        i0 = 0
        i1 = 2
        i2 = 1
    else:
        i0 = 1
        i1 = 2
        i2 = 0
    
        
    x = ( tri1_projs[i1] - tri1_projs[i2] ) 
    denom = ( distances[0][i2] - distances[0][i1] )
    if denom == 0.0:  # hack to ignore zero dividers
        return 0
    y = distances[0][i2] / ( distances[0][i2] - distances[0][i1] )
    t1_1 = tri1_projs[i2] +  x * y
    
    x = ( tri1_projs[i0] - tri1_projs[i2] )
    denom =   distances[0][i2] - distances[0][i0]
    if denom == 0.0:
        return 0
    y = distances[0][i2] / denom
    t1_2 = tri1_projs[i2] +  x * y
    
    i0 = None
    i1 = None
    i2 = None
    
    if d_tri2[0] * d_tri2[1] > 0:
        i0 = 0
        i1 = 1
        i2 = 2
    elif  d_tri2[0] * d_tri2[2] > 0:   
        i0 = 0
        i1 = 2
        i2 = 1
    else:
        i0 = 1
        i1 = 2
        i2 = 0
    
    x = ( tri2_projs[i1] - tri2_projs[i2] )  
    denom = ( distances[1][i2] - distances[1][i1] )
    if denom == 0.0:  # hack to ignore zero dividers
        return 0    
    y = distances[1][i2] / ( denom )
    t2_1 = tri2_projs[i2] + x * y
    
    x = ( tri2_projs[i0] - tri2_projs[i2] ) 
    denom = ( distances[1][i2] - distances[1][i0] )
    if denom == 0.0:  # hack to ignore zero dividers
        return 0 
    y = distances[1][i2] / ( denom )
    t2_2 = tri2_projs[i2] + x * y    
    
           
    tri1_smallest = t1_2
    tri1_largest = t1_1
    
    if t1_1 < t1_2:
        tri1_smallest = t1_1
        tri1_largest = t1_2
        
    tri2_smallest = t2_2
    tri2_largest = t2_1
    
    if t2_1 < t2_2:
        tri2_smallest = t2_1
        tri2_largest = t2_2
    
              
    if tri1_largest < tri2_smallest:
        return 0
    if tri2_largest < tri1_smallest:
        return 0
    '''
    print 'interval values'
    print 'tri1_largest', tri1_largest
    print 'tri1_smallest', tri1_smallest
    print 'tri2_largest', tri2_largest
    print 'tri2_smallest', tri2_smallest
    '''
    
    return 1

def compute_tri_boundingbox( pts ):
    # Compute and return the bounding box for a triangle
    # 
    # Accepts: 
    #   pts - a list of 3 points. ( also lists )
    # 
    # Returns: 
    #   bb - MBoundingBox object
    xmin = pts[0][0]
    xmax = pts[0][0]
    ymin = pts[0][1]
    ymax = pts[0][1]
    zmin = pts[0][2]
    zmax = pts[0][2]
    
    for i in xrange( 1, 3 ):
        if pts[i][0] < xmin:
           xmin =  pts[i][0]
        if pts[i][0] > xmax:
           xmax = pts[i][0]
           
        if pts[i][1] < ymin:
           ymin =  pts[i][1]
        if pts[i][1] > ymax:
           ymax = pts[i][1]     
           
        if pts[i][2] < zmin:
           zmin =  pts[i][2]
        if pts[i][2] > zmax:
           zmax = pts[i][2] 
    
    p1 = om.MPoint( xmin, ymin, zmin )
    p2 = om.MPoint( xmax, ymax, zmax )
    
    bb = om.MBoundingBox( p1, p2 )
    
    return bb
    
def compute_mesh_boundingbox( triangles ):

    xmin = triangles[0][1][0][0]
    xmax = triangles[0][1][0][0]
    ymin = triangles[0][1][0][1]
    ymax = triangles[0][1][0][1]
    zmin = triangles[0][1][0][2]
    zmax = triangles[0][1][0][2]

    for tri2 in triangles:
        for pts in tri2[1]:
        
            if pts[0] < xmin:
                xmin = pts[0]
            if pts[0] > xmax:
                xmax = pts[0]
            
            if pts[1] < ymin:
                ymin = pts[1]
            if pts[1] > ymax:
                ymax = pts[1]            
                
            if pts[2] < zmin:
                zmin = pts[2]
            if pts[2] > zmax:
                zmax = pts[2]    
    
    p1 = om.MPoint( xmin, ymin, zmin )
    p2 = om.MPoint( xmax, ymax, zmax )
    
    bb = om.MBoundingBox( p1, p2 )
    
    return bb
    
  
def test_intersection( triangles ):
    # print 'hello welcome to the test intersection method'
    # go through a process of ruling out potential intersections.
    
    res = signed_dist_check( triangles )
    
    if res[0]==2:
        # print 'intersection found via coplanar'
        return 1
    
    if not res[0]:
        # print 'intersection ruled out at signed dist check'
        return 0
    
    # passed signed basic dist check, we must investigate further    
    
    if not interval_test( triangles, res[1] ):
        #print 'intersection ruled out at interval test'
        return 0
    
    
    return 1 

    

def select_intersecting_vertices( mesh_01, mesh_02 ):
#
# Will select the faces of on the mesh selected first, that are
# deemed to be intersecting any face of the mesh selected second. 
#
# Accepts:
# - mesh_01, mesh_02  MDagPath objects to run algorithm on
#
# Returns:
# - None
    
    # print 'welcome to select intersecting verts method'
    
    mesh_01_iter = om.MItMeshPolygon( mesh_01 )
    mesh_02_iter = om.MItMeshPolygon( mesh_02 )
    
    # [ [ 0, [ [ x, y, z ], [ x, y, z ], [ x, y, z ] ] ], 
    #   [ 1, [ x, y, z ], [ x, y, z ], [ x, y, z ]  ], 
    #   ...
    #   [ n, [ x, y, z ], [ x, y, z ], [ x, y, z ]  ] ]
    
    mesh_01_triangles = list()
    mesh_02_triangles = list()
    
    while not mesh_01_iter.isDone():
        
        # a runaround to get an actual int containing the number of tris
        if mesh_01_iter.hasValidTriangulation():
            numTrianglesUtil = om.MScriptUtil()
            numTriangles = numTrianglesUtil.asIntPtr()       
            mesh_01_iter.numTriangles( numTriangles )
            numTriangles = numTrianglesUtil.getInt( numTriangles )
            
            ####
            # test optimisation where we only check 1 triangle per polygon
            # numTriangles = 1
            
            for i in xrange( numTriangles ):
                triPts = om.MPointArray()
                vertexIndices = om.MIntArray()    
                
                mesh_01_iter.getTriangle( i, triPts, vertexIndices )
                trianglePts_numpy = list()
                for j in xrange( 3 ):
                
                    vert_xyz = numpy.array([ triPts[j].x, 
                                             triPts[j].y,
                                             triPts[j].z ])
                    #print vert_xyz                         
                    trianglePts_numpy.append( vert_xyz )
                #print ''
                mesh_01_triangles.append( [ mesh_01_iter.index(), trianglePts_numpy ] )
                          
            
        mesh_01_iter.next()
    
    #print ' ############ '
    
    while not mesh_02_iter.isDone():
        if mesh_02_iter.hasValidTriangulation():
            # a runaround to get an actual int containing the number of tris
            numTrianglesUtil = om.MScriptUtil()
            numTriangles = numTrianglesUtil.asIntPtr()       
            mesh_02_iter.numTriangles( numTriangles )
            numTriangles = numTrianglesUtil.getInt( numTriangles )
            
            for i in xrange( numTriangles ):
                triPts = om.MPointArray()
                vertexIndices = om.MIntArray()    
                
                mesh_02_iter.getTriangle( i, triPts, vertexIndices )
                trianglePts_numpy = list()
                for j in xrange( 3 ):
                
                    vert_xyz = numpy.array([ triPts[j].x, 
                                             triPts[j].y,
                                             triPts[j].z ])
                    trianglePts_numpy.append( vert_xyz )
                    
                mesh_02_triangles.append( [ mesh_02_iter.index(), trianglePts_numpy ] )
                
            
        mesh_02_iter.next()
    
    # compute all triangle bounding boxes
    mesh_01_triangle_bboxes = list()
    mesh_02_triangle_bboxes = list()
        
    for triangle_1 in mesh_01_triangles:
        bb = compute_tri_boundingbox( triangle_1[1] )
        mesh_01_triangle_bboxes.append( bb )
    
    for triangle_2 in mesh_02_triangles:
        bb = compute_tri_boundingbox( triangle_2[1] )
        mesh_02_triangle_bboxes.append( bb )
    
    t1_intersections = om.MIntArray()
    t2_boundingbox = compute_mesh_boundingbox( mesh_02_triangles )
       
    
    for i, triangle_1 in enumerate( mesh_01_triangles ):
        # print 'stepping through all triangles in triangle_1. this is ', i
        # test if the triangle's bounding box even intersects the other mesh bounding box
        
        mesh_bb_res = mesh_01_triangle_bboxes[i].intersects( t2_boundingbox )
        if mesh_bb_res: 
                
            if triangle_1[0] not in t1_intersections:
                #drawTriangle( triangle_1[1] )
            
                for j, triangle_2 in enumerate( mesh_02_triangles ):
                    if mesh_01_triangle_bboxes[i].intersects( mesh_02_triangle_bboxes[j] ):
                        # print 'bounding boxes DO intersect'                              
                                                          
                        res = test_intersection( [ triangle_1[1], triangle_2[1] ] ) 
                        # print res
                        if res:
                            t1_intersections.append( triangle_1[0] )
                    '''        
                    else:
                        print 'bounding boxes dont intersect mate.'
                    '''     
    
    # print t1_intersections
    #mc.select( cl=True )
    
    intArray = t1_intersections
    vertices = om.MFnSingleIndexedComponent()
    components = vertices.create( om.MFn.kMeshPolygonComponent )
    vertices.addElements( intArray )
    
    activeSelect = om.MSelectionList()
    activeSelect.add( mesh_01, components )
    om.MGlobal.setActiveSelectionList( activeSelect )
    
def mollerIntersect():
    #
    #   
    # print 'hello, welcome to check selected meshes method.'
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( sel )

    mesh_01 = om.MDagPath()
    mesh_02 = om.MDagPath()

    sel.getDagPath( 0, mesh_01 )
    sel.getDagPath( 1, mesh_02 )
    select_intersecting_vertices( mesh_01, mesh_02 )
    
 
def mollerSelfIntersect():
 
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( sel )

    mesh_01 = om.MDagPath()
    sel.getDagPath( 0, mesh_01 )
    select_self_intersecting_vertices( mesh_01 )

    
def select_self_intersecting_vertices( mesh_01 ):
#
# Will select the faces of a mesh that are deemed to be intersecting
# with any other face on that selected mesh. 
#
# Accepts:
#  mesh_01 -  MDagPath object to run algorithm on
#
# Returns:
# - None

    mesh_01_iter = om.MItMeshPolygon( mesh_01 )
    
    # [ [ 0, [ [ x, y, z ], [ x, y, z ], [ x, y, z ] ] ], 
    #   [ 1, [ x, y, z ], [ x, y, z ], [ x, y, z ]  ], 
    #   ...
    #   [ n, [ x, y, z ], [ x, y, z ], [ x, y, z ]  ] ]
    
    mesh_01_triangles = list()
    # in C I made a whole class for this, but in python we can just store lists of different types
    # easily. So the content of a mesh_01_triangles element might look like this.
    # [ faceIndex, numpyArray of triangle points, list of indices for those points, int with 0 or 1, (has intersection) ]
    
    mesh_01_triangle_bboxes = list()
    numTriangles_mesh_01 = 0
            
    while not mesh_01_iter.isDone():   
        
        if mesh_01_iter.hasValidTriangulation(): 
        
            numTrianglesUtil = om.MScriptUtil()
            numTriangles = numTrianglesUtil.asIntPtr()   
            mesh_01_iter.numTriangles( numTriangles )
            numTriangles = numTrianglesUtil.getInt( numTriangles )
            
            for i in xrange(numTriangles): 
                
                triPts = om.MPointArray()
                currVertexIndices = om.MIntArray()
                
                mesh_01_iter.getTriangle( i, triPts, currVertexIndices )
                
                trianglePts_numpy = list()
                verts = list()
                
                for j in xrange(3): 
                    
                    vert_xyz = numpy.array([ triPts[j].x, 
                                                   triPts[j].y,
                                                   triPts[j].z ])                    
                    verts.append( currVertexIndices[j] )
                    trianglePts_numpy.append( vert_xyz )
                
                numTriangles_mesh_01 += 1
                mesh_01_triangles.append( [ mesh_01_iter.index(), trianglePts_numpy, verts, 0 ] )
                bb = compute_tri_boundingbox( trianglePts_numpy )
                mesh_01_triangle_bboxes.append( bb )                
                
                
        mesh_01_iter.next()
 
    pointsList_1 = list()
    res = 0
    
    for i in xrange( numTriangles_mesh_01 ): 
    
        pointsList_1 = mesh_01_triangles[i][1]
        tri1_vtxIndices_array = mesh_01_triangles[i][2]
        
        # in c++: for( int j=i; j < numTriangles_mesh_01; j++ )
        for j in range(i, numTriangles_mesh_01, 1 ): 
            if (i!=j): 
                # by definition, two triangles cannot be intersecting if they share the same edge. 
                # unfortunately, sometimes Moller's algorithm returns this occurance as an intersection. 
                # lets remove border faces from the testing. 

                # now our triangles are often 'implicit' meaning, assuming much of the mesh is actually quadded, no real 
                # edge would exist between the tris of that quad. We can test for this, because I store
                # the quad index. Just test if they are the same. 
                # but what about the triangles of adjacent faces?  
                # well, one way is to get the current triangle vertices. 
                # then get the triangles' vertices we are planning to test against. If they share two vertex indices (of the three), don't compute the test.  
                
                tri2_vtxIndices_array = mesh_01_triangles[j][2]
                numShared = 0
                sharedVertices = [None, None, None]
                
                
                if ( (tri1_vtxIndices_array[0] == tri2_vtxIndices_array[0]) or (tri1_vtxIndices_array[0] == tri2_vtxIndices_array[1]) or (tri1_vtxIndices_array[0] == tri2_vtxIndices_array[2]) ): 
                    sharedVertices[numShared] = tri1_vtxIndices_array[0]
                    numShared+=1 
                    
                if ( (tri1_vtxIndices_array[1] == tri2_vtxIndices_array[0]) or (tri1_vtxIndices_array[1] == tri2_vtxIndices_array[1]) or (tri1_vtxIndices_array[1] == tri2_vtxIndices_array[2]) ): 
                    sharedVertices[numShared] = tri1_vtxIndices_array[1]
                    numShared+=1 
                
                if ( (tri1_vtxIndices_array[2] == tri2_vtxIndices_array[0]) or (tri1_vtxIndices_array[2] == tri2_vtxIndices_array[1]) or (tri1_vtxIndices_array[2] == tri2_vtxIndices_array[2]) ): 
                    sharedVertices[numShared] = tri1_vtxIndices_array[2]
                    numShared+=1
                
                if ( numShared==1 ): 
                    # send the shared vertex position first, then the other two points of one triangle. 
                    # followed by the other two points of the second triangle. 
                    
                    vertIter0 = om.MItMeshVertex( mesh_01 )
                    dummyUtil = om.MScriptUtil()
                    dummy = numTrianglesUtil.asIntPtr()  
                    vertIter0.setIndex( sharedVertices[0], dummy )
                    
                    pos = om.MPoint()
                    pos = vertIter0.position()
                    
                    vert0 = numpy.array( [ pos.x, pos.y, pos.z ] )
                    
                    tri1_notSharedIndices = [None, None]  
                    tri2_notSharedIndices = [None, None]  
                    tri1_notSharedCount = 0
                    tri2_notSharedCount = 0
                    
                    for k in xrange(3): 
                        if ( tri1_vtxIndices_array[k] != sharedVertices[0] ):
                            tri1_notSharedIndices[tri1_notSharedCount] = tri1_vtxIndices_array[k] 
                            tri1_notSharedCount+=1
                    
                        if ( tri2_vtxIndices_array[k] != sharedVertices[0] ):
                            tri2_notSharedIndices[tri2_notSharedCount] = tri2_vtxIndices_array[k]
                            tri2_notSharedCount+=1
                        
                    # why don't I just use the same iterator here? well, i don't think its stable to be frank.
                    # maybe test. 
                    vertIter1 = om.MItMeshVertex( mesh_01 )
                    vertIter1.setIndex( tri1_notSharedIndices[0], dummy )
                    pos1 = vertIter1.position()  # om.MPoint
                    vert1 = numpy.array( [ pos1.x, pos1.y, pos1.z ]  )
                    
                    vertIter2 = om.MItMeshVertex( mesh_01 )
                    vertIter2.setIndex( tri1_notSharedIndices[1], dummy )
                    pos2 = vertIter2.position()  # om.MPoint
                    vert2 = numpy.array( [ pos2.x, pos2.y, pos2.z ]  )
                    
                    vertIter3 = om.MItMeshVertex( mesh_01 )
                    vertIter3.setIndex( tri2_notSharedIndices[0], dummy )
                    pos3 = vertIter3.position()  # om.MPoint
                    orig = numpy.array( [ pos3.x, pos3.y, pos3.z ]  )
                    
                    vertIter4 = om.MItMeshVertex( mesh_01 )
                    vertIter4.setIndex( tri2_notSharedIndices[1], dummy )
                    pos4 = vertIter4.position()  # om.MPoint
                    p2 = numpy.array( [ pos4.x, pos4.y, pos4.z ]  )
                    
                    # print 'testing via rayTriangle'
                    
                    result = rti.rayTriangleIntersection( orig, p2, vert0, vert1, vert2 )
                    
                    if result: 
                        # print 'intersection detected via ray triangle'
                        # set a flag saying an intersection has been found.                     
                        mesh_01_triangles[i][3] = 1
                        mesh_01_triangles[j][3] = 1
                    
                elif ( numShared != 2) and ( numShared != 1 ): # faces sharing an edge cannot be intersecting, by definition
                    pointsList_2 = mesh_01_triangles[j][1]
                    
                    # test for intersection, do the bounding box intersection first
                    # if mesh_01_triangle_bboxes[i].intersects( mesh_01_triangle_bboxes[j] ): 
                
                    # then step into our old friend Moller triangle-triangle intersections
                    # print 'running regular tri-tri intersect'                        
                    res = test_intersection( [ pointsList_1, pointsList_2] )
                    # print 'results from test_intersection method', res
                    if res:
                        '''
                        print 'pointsList_1', pointsList_1
                        print 'pointsList_1', pointsList_1[0]
                        print type( pointsList_1[0] )
                        pts1 = list()
                        pts1.append( list( pointsList_1[0] ) )
                        pts1.append( list( pointsList_1[1] ) )
                        pts1.append( list( pointsList_1[2] ) )
                        
                        pts2 = list()
                        pts2.append( list( pointsList_2[0] ) )
                        pts2.append( list( pointsList_2[1] ) )
                        pts2.append( list( pointsList_2[2] ) )
                                                                        
                        drawTriangle( pts1 )
                        drawTriangle( pts2 )
                        
                        print 'intersection detected via regular moller intersect'
                        '''
                        # print 'face', mesh_01_triangles[i][0], 'and', mesh_01_triangles[j][0]
                        mesh_01_triangles[i][3] = 1
                        mesh_01_triangles[j][3] = 1

    intArray = om.MIntArray()
    numIntersections = 0
    for i in xrange(numTriangles_mesh_01): 
        if mesh_01_triangles[i][3]:
            numIntersections += 1
            intArray.append( mesh_01_triangles[i][0] )
    
    print 'num intersections', numIntersections
    
    vertices = om.MFnSingleIndexedComponent()
    components = vertices.create( om.MFn.kMeshPolygonComponent )
    vertices.addElements( intArray )
    
    activeSelect = om.MSelectionList()
    activeSelect.add( mesh_01, components )
    
    om.MGlobal.setActiveSelectionList( activeSelect )
                        
                    
                    