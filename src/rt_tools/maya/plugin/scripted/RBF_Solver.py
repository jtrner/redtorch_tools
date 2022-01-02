import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.api.OpenMaya as om
import numpy as np
import scipy.cluster
from scipy.spatial.distance import cdist
import maya.cmds as mc
import sys
import math

nodeName = 'RBF_Solver'
nodeID = om.MTypeId(0x0011E191)


# node definition
class RBF_Solver(om.MPxNode):
    input = om.MObject()
    output = om.MObject()

    @staticmethod
    def nodeCreator():
        return RBF_Solver()

    @staticmethod
    def nodeInitializer():

        # in driven attr
        driven_mat_type = om.MFnMatrixAttribute()
        RBF_Solver.driven_mat = driven_mat_type.create('driven_mat', 'dm' )
        driven_mat_type.storable = True
        driven_mat_type.writable = True
        driven_mat_type.keyable = True

        # in first_input attr
        first_input_mat_type = om.MFnMatrixAttribute()
        RBF_Solver.first_input_mat = first_input_mat_type.create('first_input_mat', 'fm' )
        first_input_mat_type.storable = True
        first_input_mat_type.writable = True
        first_input_mat_type.keyable = True

        # in second_input attr
        second_input_mat_type = om.MFnMatrixAttribute()
        RBF_Solver.second_input_mat = second_input_mat_type.create('second_input_mat', 'sc' )
        second_input_mat_type.storable = True
        second_input_mat_type.writable = True
        second_input_mat_type.keyable = True

        # in third_input attr
        third_input_mat_type = om.MFnMatrixAttribute()
        RBF_Solver.third_input_mat = third_input_mat_type.create('third_input_mat', 'th' )
        third_input_mat_type.storable = True
        third_input_mat_type.writable = True
        third_input_mat_type.keyable = True

        # in forth_input attr
        forth_input_mat_type = om.MFnMatrixAttribute()
        RBF_Solver.forth_input_mat = forth_input_mat_type.create('forth_input_mat', 'fom' )
        forth_input_mat_type.storable = True
        forth_input_mat_type.writable = True
        forth_input_mat_type.keyable = True

        # add interp_type enum attr
        interpolate_type = om.MFnEnumAttribute()
        RBF_Solver.interp_type = interpolate_type.create("interp_type", "in", 1)
        interpolate_type.addField('Linear', 0)
        interpolate_type.addField('Gaussian', 1)
        interpolate_type.writable = True
        interpolate_type.hidden = False
        interpolate_type.keyable = True
        interpolate_type.internal = True

        # rotation attr
        rotation_type = om.MFnNumericAttribute()
        RBF_Solver.rotateX = rotation_type.create(
            "rotateX",
            "rx",
            om.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateY
        RBF_Solver.rotateY = rotation_type.create(
            "rotateY",
            "ry",
            om.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateZ
        RBF_Solver.rotateZ = rotation_type.create(
            "rotateZ",
            "rz",
            om.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        RBF_Solver.rotation = rotation_type.create('rotation', 'rt', RBF_Solver.rotateX,
                                                                     RBF_Solver.rotateY,
                                                                     RBF_Solver.rotateZ)
        rotation_type.storable = False
        rotation_type.writable = False

        # rotation attr
        scale_type = om.MFnNumericAttribute()
        RBF_Solver.scaleX = scale_type.create(
            "scaleX",
            "sx",
            om.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateY
        RBF_Solver.scaleY = scale_type.create(
            "scaleY",
            "sy",
            om.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateZ
        RBF_Solver.scaleZ = scale_type.create(
            "scaleZ",
            "sz",
            om.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False
        RBF_Solver.scale = scale_type.create('scale', 'se',RBF_Solver.scaleX,
                                                           RBF_Solver.scaleY,
                                                           RBF_Solver.scaleZ)
        scale_type.storable = False
        scale_type.writable = False

        # blend weight first attr
        blend_first_weight_type = om.MFnNumericAttribute()
        RBF_Solver.firstWeight = blend_first_weight_type.create(
            "firstWeight",
            "fw",
            om.MFnNumericData.kFloat,
            0.0
        )
        blend_first_weight_type.storable = False
        blend_first_weight_type.writable = False

        # blend weight first attr
        blend_second_weight_type = om.MFnNumericAttribute()
        RBF_Solver.secondWeight = blend_second_weight_type.create(
            "secondWeight",
            "sw",
            om.MFnNumericData.kFloat,
            0.0
        )
        blend_second_weight_type.storable = False
        blend_second_weight_type.writable = False

        # blend weight third attr
        blend_third_weight_type = om.MFnNumericAttribute()
        RBF_Solver.thirdWeight = blend_third_weight_type.create(
            "thirdWeight",
            "tw",
            om.MFnNumericData.kFloat,
            0.0
        )
        blend_third_weight_type.storable = False
        blend_third_weight_type.writable = False

        # blend weight forth attr
        blend_forth_weight_type = om.MFnNumericAttribute()
        RBF_Solver.forthWeight = blend_forth_weight_type.create(
            "forthWeight",
            "fo",
            om.MFnNumericData.kFloat,
            0.0
        )
        blend_forth_weight_type.storable = False
        blend_forth_weight_type.writable = False


        # add attributes
        RBF_Solver.addAttribute(RBF_Solver.driven_mat)
        RBF_Solver.addAttribute(RBF_Solver.first_input_mat)
        RBF_Solver.addAttribute(RBF_Solver.second_input_mat)
        RBF_Solver.addAttribute(RBF_Solver.third_input_mat)
        RBF_Solver.addAttribute(RBF_Solver.forth_input_mat)
        RBF_Solver.addAttribute(RBF_Solver.interp_type)
        RBF_Solver.addAttribute(RBF_Solver.rotation)
        RBF_Solver.addAttribute(RBF_Solver.scale)
        RBF_Solver.addAttribute(RBF_Solver.firstWeight)
        RBF_Solver.addAttribute(RBF_Solver.secondWeight)
        RBF_Solver.addAttribute(RBF_Solver.thirdWeight)
        RBF_Solver.addAttribute(RBF_Solver.forthWeight)
        for attr in [RBF_Solver.rotation, RBF_Solver.scale, RBF_Solver.firstWeight,
                     RBF_Solver.secondWeight, RBF_Solver.thirdWeight, RBF_Solver.forthWeight]:
            RBF_Solver.attributeAffects(RBF_Solver.driven_mat, attr)
            RBF_Solver.attributeAffects(RBF_Solver.first_input_mat, attr)
            RBF_Solver.attributeAffects(RBF_Solver.second_input_mat, attr)
            RBF_Solver.attributeAffects(RBF_Solver.third_input_mat, attr)
            RBF_Solver.attributeAffects(RBF_Solver.forth_input_mat, attr)
            RBF_Solver.attributeAffects(RBF_Solver.interp_type, attr)

    def __init__(self):
        om.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if RBF_Solver.rotation and RBF_Solver.scale:
            driven_matrix = dataBlock.inputValue(RBF_Solver.driven_mat).asMatrix()
            driven_matrix = om.MMatrix(driven_matrix)

            first_matrix = dataBlock.inputValue(RBF_Solver.first_input_mat).asMatrix()
            first_matrix = om.MMatrix(first_matrix)

            second_matrix = dataBlock.inputValue(RBF_Solver.second_input_mat).asMatrix()
            second_matrix = om.MMatrix(second_matrix)

            third_matrix = dataBlock.inputValue(RBF_Solver.third_input_mat).asMatrix()
            third_matrix = om.MMatrix(third_matrix)

            forth_matrix = dataBlock.inputValue(RBF_Solver.forth_input_mat).asMatrix()
            forth_matrix = om.MMatrix(forth_matrix)

            rotations = []
            positions = []
            target_pos = []
            poses = []
            rots = []

            for mat in [first_matrix, second_matrix, third_matrix, forth_matrix]:
                transformation_mat = om.MTransformationMatrix(mat)
                translate = transformation_mat.translation(om.MSpace.kTransform)
                rot = transformation_mat.rotation()
                rot.x = rot.x / math.pi * 180.0
                rot.y = rot.y / math.pi * 180.0
                rot.z = rot.z / math.pi * 180.0
                poses.append(translate)
                rots.append(rot)

            for t in poses:
                each_pose = []
                each_pose.append(t[0])
                each_pose.append(t[1])
                each_pose.append(t[2])
                positions.append(each_pose)
            for r in rots:
                each_ro = []
                each_ro.append(r.x)
                each_ro.append(r.y)
                each_ro.append(r.z)
                rotations.append(each_ro)

            target_mat = om.MTransformationMatrix(driven_matrix)
            translate_target = target_mat.translation(om.MSpace.kTransform)
            for target in [translate_target[0], translate_target[1], translate_target[2]]:
                target_pos.append(target)


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

            for i, lis in enumerate(blend_list):
                for j, item in enumerate(lis):
                    if i == j:
                        blend_list[i][j] = 1

            new_blend_weight = []
            for blend_gu, blend_w in zip(guss, np.array(blend_list)):
                new_blend = blend_gu * blend_w
                new_blend_weight.append(new_blend)

            linearType = dataBlock.inputValue(RBF_Solver.interp_type)

            blend_matrix_weights = []
            if linearType.asShort() == 0:
                blend_matrix_weights = solve_equations(distMatrix, blend_list)
            if linearType.asShort()  == 1:
                blend_matrix_weights = solve_equations(distMatrix, new_blend_weight)

            final_blend = get_final_weights(target_distances, blend_matrix_weights)
            ##################################################################
            new_rotations = []
            for gu, rot in zip(guss, np.array(rotations)):
                new_rot = gu * rot
                new_rotations.append(new_rot)

            matrix_weights = []
            if linearType.asShort() == 0:
                matrix_weights = solve_equations(distMatrix, rotations)
            if linearType.asShort() == 1:
                matrix_weights = solve_equations(distMatrix, new_rotations)

            final_poses = get_final_weights(target_distances, matrix_weights)


            firstWeight_out = dataBlock.outputValue(RBF_Solver.firstWeight)
            firstWeight_out.setFloat(final_blend[0])

            secondWeight_out = dataBlock.outputValue(RBF_Solver.secondWeight)
            secondWeight_out.setFloat(final_blend[1])

            thirdWeight_out = dataBlock.outputValue(RBF_Solver.thirdWeight)
            thirdWeight_out.setFloat(final_blend[2])

            forthWeight_out = dataBlock.outputValue(RBF_Solver.forthWeight)
            forthWeight_out.setFloat(final_blend[3])


            rot_out = dataBlock.outputValue(RBF_Solver.rotation)
            rot_out.set3Float(final_poses[0], final_poses[1] , final_poses[2] )

            # scal = transformation_mat.scale(om.MSpace.kTransform)
            # scale_out = dataBlock.outputValue(RBF_Solver.scale)
            # scale_out.set3Float(, , )


            dataBlock.setClean(plug)


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
    first = om.MVector(target)
    second = om.MVector(value)
    newVec = second - first

    return newVec.length()


def gaussian(matrix, radius):
    radius *= 0.707
    result = np.exp(-(matrix * matrix) / (2.0 * radius * radius))

    return result


def get_final_weights(target_distances, matrix_weights):
    final_poses = []
    new_poses = []
    for pos, weight in zip(target_distances, matrix_weights):
        new_pos = pos * weight
        new_poses.append(new_pos)
    new_weight = 0
    for new_position in new_poses:
        new_weight = new_weight + new_position
        final_poses = new_weight

    return (final_poses)


def initializePlugin(mObj):
    plugin = om.MFnPlugin(mObj, 'Behnam HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeID, RBF_Solver.nodeCreator, RBF_Solver.nodeInitializer)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))


def uninitializePlugin(mObj):
    plugin = om.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeID)
    except Exception as e:
        sys.stderr.write('Faild to unload plugin: {}, error: {}'.format(nodeName, e))



def maya_useNewAPI():
    pass


# import maya.cmds as mc
#
#
# def main():
#     nodeName = 'RBF_Solver'
#
#     pluginPath = r'D:\all_works\redtorch_tools\src\rt_tools\maya\plugin\scripted\RBF_Solver.py'
#     if mc.pluginInfo('RBF_Solver', q=True, loaded=True):
#         mc.file(new=True, f=True)
#         mc.unloadPlugin(nodeName)
#
#     mc.loadPlugin(pluginPath)
#
#
# main()
# mc.file('D:\demoreel2022\data\interpolate2.ma', o=True)
#
# mc.createNode('RBF_Solver')
#
# mc.connectAttr('pSphere1' + '.worldMatrix[0]', 'RBF_Solver1' + '.driven_mat')
# mc.connectAttr('pSphere2' + '.worldMatrix[0]', 'RBF_Solver1' + '.first_input_mat')
# mc.connectAttr('pSphere3' + '.worldMatrix[0]', 'RBF_Solver1' + '.second_input_mat')
# mc.connectAttr('pSphere4' + '.worldMatrix[0]', 'RBF_Solver1' + '.third_input_mat')
# mc.connectAttr('pSphere5' + '.worldMatrix[0]', 'RBF_Solver1' + '.forth_input_mat')
#
#
# mc.connectAttr('RBF_Solver1' + '.firstWeight', 'shoulderCorrective.armpit')
# mc.connectAttr('RBF_Solver1' + '.secondWeight', 'shoulderCorrective.backShoulder')
# mc.connectAttr('RBF_Solver1' + '.thirdWeight', 'shoulderCorrective.frontShoulder')
# mc.connectAttr('RBF_Solver1' + '.forthWeight', 'shoulderCorrective.upperShoulder')
#



