
import maya.cmds as mc    
import numpy as np
import maya.OpenMaya as om
import pprint

pp = pprint.PrettyPrinter( indent=4 )

def best_fit():
    # inputs
    locs = mc.ls( "locator?" )
    
    box = "pCube1"
    if not mc.objExists( box ):
        box = mc.polyCube()[0]
        mc.setAttr( box+".displayLocalAxis", 1 )


    # make matrices using positions
    poses_list = [mc.xform(x,q=1,ws=1,t=1) for x in locs]
    poses_matrix = np.matrix( poses_list ).T
    pp.pprint( poses_list )

    # TRANSLATE AND ROTATE
    #==================================================
    # get mean, covariances and eigens
    #translate = np.insert( poses_matrix.mean(1).flatten(), 3, 0, 1 ).tolist()[0]
    poses_cov = np.cov( poses_matrix )
    eig_value, eig_matrix = np.linalg.eig( poses_cov )
    pp.pprint( eig_matrix )

    # create transform matrix from eigenVectors
    eig_matrix = eig_matrix.T
    eig_matrix_list = np.insert(eig_matrix,3,0,1).flatten().tolist()
    eig_matrix_list.extend( [0,0,0,1] )
    eig_matrix_maya = om.MMatrix()
    om.MScriptUtil.createMatrixFromList( eig_matrix_list, eig_matrix_maya )

    # get final rotation from matrix
    transform_matrix_maya = om.MTransformationMatrix( eig_matrix_maya )
    rot_radian = transform_matrix_maya.eulerRotation()

    # convert rotation from radian to degrees
    rot = [180 * x / 3.14159 for x in rot_radian]

    # TRANSLATE
    #==================================================
    
    poses_in_rows =  np.array( poses_list ).T
    
    x_max = poses_in_rows[0].max()
    x_min = poses_in_rows[0].min()
    y_max = poses_in_rows[1].max()
    y_min = poses_in_rows[1].min()
    z_max = poses_in_rows[2].max()
    z_min = poses_in_rows[2].min()

    x_world = ( x_max + x_min ) / 2
    y_world = ( y_max + y_min ) / 2
    z_world = ( z_max + z_min ) / 2

    translate = [ x_world, y_world, z_world ]

    # SCALE
    #==================================================
    #world_to_local = np.linalg.inv( eig_matrix )
    #poses_list = [ world_to_local.dot(x) for x in poses_list ]
    world_poses_list = []
    for pose in poses_list:
        world_pose = om.MPoint( *pose ) * eig_matrix_maya.inverse()
        world_poses_list.append( [world_pose.x, world_pose.y, world_pose.z] )

    world_poses_list =  np.array( world_poses_list ).T

    x_max = world_poses_list[0].max()
    x_min = world_poses_list[0].min()
    y_max = world_poses_list[1].max()
    y_min = world_poses_list[1].min()
    z_max = world_poses_list[2].max()
    z_min = world_poses_list[2].min()

    scale = [ x_max-x_min, y_max-y_min, z_max-z_min ]



    # set transforms
    #==================================================
    mc.setAttr( box+".translate", translate[0], translate[1], translate[2] )
    mc.setAttr( box+".rotate", rot[0], rot[1], rot[2] )
    #mc.setAttr( box+".scale", scale[0], scale[1], scale[2] )


def visualizePoints( points ):
    for point in points:
        #if isinstance( point, om.MPoint ):
        #    point = point.x, point.y, point.z
        loc = mc.spaceLocator()
        mc.xform( loc, ws=True, t=point )
"""
import sys
path = "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin"
if path not in sys.path:
    sys.path.append( path )
    
import sys
path = "F:\\softwares\\numpy.1.9.2"
if path not in sys.path:
    sys.path.append( path )
    
import ehm_plugins.ehm_boundingBox.ehm_boundingBox as bb
reload( bb )
bb.best_fit()

"""










    
