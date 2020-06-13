import maya.cmds as mc
import numpy as np
import maya.api.OpenMaya as om2
import pprint

pp = pprint.PrettyPrinter(indent=4)

nodeName = 'ehm_boundingBox.py'


def best_fit():
    # inputs
    sel = om2.MGlobal.getActiveSelectionList()
    dag = sel.getDagPath(0)
    meshFn = om2.MFnMesh(dag)
    pntArray = meshFn.getPoints()

    if mc.objExists('pCube1'):
        mc.delete('pCube1')
    box = mc.polyCube()[0]
    mc.setAttr(box + ".displayLocalAxis", 1)

    # make matrices using positions
    poses_list = [(x.x, x.y, x.z) for x in pntArray]  # [mc.xform(x, q=1, ws=1, t=1) for x in pntArray]
    # poses_matrix = np.matrix( poses_list ).T

    # ROTATE
    # ==================================================
    # get mean, covariances and eigens
    # poses_cov = np.cov( poses_matrix )
    # eig_value, eig_matrix = np.linalg.eig( poses_cov )
    # eig_matrix = eig_matrix.T

    # create transform matrix from eigenVectors
    u, s, v = np.linalg.svd(poses_list)
    print v
    eig_matrix_list = np.insert(v, 3, 0, 1).flatten().tolist()
    eig_matrix_list.extend([0, 0, 0, 1])
    print eig_matrix_list
    eig_matrix_maya = om2.MMatrix(eig_matrix_list)

    # get final rotation from matrix
    transform_matrix_maya = om2.MTransformationMatrix(eig_matrix_maya)
    rot_radian = transform_matrix_maya.rotation()

    # convert rotation from radian to degrees
    rot = [180 * x / 3.14159 for x in rot_radian]

    # TRANSLATE
    # ==================================================

    poses_in_rows = np.array(poses_list).T

    x_max = poses_in_rows[0].max()
    x_min = poses_in_rows[0].min()
    y_max = poses_in_rows[1].max()
    y_min = poses_in_rows[1].min()
    z_max = poses_in_rows[2].max()
    z_min = poses_in_rows[2].min()

    x_world = (x_max + x_min) / 2
    y_world = (y_max + y_min) / 2
    z_world = (z_max + z_min) / 2

    translate = [x_world, y_world, z_world]

    # SCALE
    # ==================================================
    world_poses_list = []
    for pose in poses_list:
        world_pose = om2.MPoint(*pose) * eig_matrix_maya.inverse()
        world_poses_list.append([world_pose.x, world_pose.y, world_pose.z])

    world_poses_list = np.array(world_poses_list).T

    x_max = world_poses_list[0].max()
    x_min = world_poses_list[0].min()
    y_max = world_poses_list[1].max()
    y_min = world_poses_list[1].min()
    z_max = world_poses_list[2].max()
    z_min = world_poses_list[2].min()

    scale = [x_max - x_min, y_max - y_min, z_max - z_min]

    # set transforms
    # ==================================================
    mc.setAttr(box + ".translate", translate[0], translate[1], translate[2])
    mc.setAttr(box + ".rotate", rot[0], rot[1], rot[2])
    mc.setAttr(box + ".scale", scale[0], scale[1], scale[2])



# def main():
#     pluginPath = __file__
#     if mc.pluginInfo(pluginPath, q=True, loaded=True):
#         mc.file(new=True, f=True)
#         mc.unloadPlugin(nodeName)
#
#     mc.loadPlugin(pluginPath)


"""
import sys
path = 'D:/all_works/redtorch_tools/dev/maya/plugin/ehm_plugins/scriptedPlugin/ehm_boundingBox'
if path not in sys.path:
    sys.path.insert(0, path)

import ehm_boundingBox
reload(ehm_boundingBox)

    
mc.select('pSphere1')
ehm_boundingBox.best_fit()
"""
