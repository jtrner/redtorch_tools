import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.api.OpenMaya as om2
import maya.cmds as mc
import sys
import math

nodeName = 'aimCons'
nodeID = om2.MTypeId(0x0011E193)


# node definition
class aimCons(om2.MPxNode):
    input = om2.MObject()
    output = om2.MObject()

    @staticmethod
    def nodeCreator():
        return aimCons()

    @staticmethod
    def nodeInitializer():
        # in start attr
        start_type = om2.MFnMatrixAttribute()
        aimCons.start = start_type.create('start', 's' )
        start_type.storable = True
        start_type.writable = True
        start_type.keyable = True

        # in end attr
        end_type = om2.MFnMatrixAttribute()
        aimCons.end = end_type.create('end', 'e')
        end_type.storable = True
        end_type.writable = True
        end_type.keyable = True

        # in up attr
        up_type = om2.MFnMatrixAttribute()
        aimCons.up = up_type.create('up', 'u')
        up_type.storable = True
        up_type.writable = True
        up_type.keyable = True

        # translation attr
        translation_type = om2.MFnNumericAttribute()
        aimCons.translateX = translation_type.create(
            "translateX",
            "tx",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        # output rotateY
        aimCons.translateY = translation_type.create(
            "translateY",
            "ty",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        # output rotateZ
        aimCons.translateZ = translation_type.create(
            "translateZ",
            "tz",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        aimCons.translation = translation_type.create('translation', 'ts', aimCons.translateX,
                                                                           aimCons.translateY,
                                                                           aimCons.translateZ)
        translation_type.storable = False
        translation_type.writable = False

        # rotation attr
        rotation_type = om2.MFnNumericAttribute()
        aimCons.rotateX = rotation_type.create(
            "rotateX",
            "rx",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateY
        aimCons.rotateY = rotation_type.create(
            "rotateY",
            "ry",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateZ
        aimCons.rotateZ = rotation_type.create(
            "rotateZ",
            "rz",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        aimCons.rotation = rotation_type.create('rotation', 'rt', aimCons.rotateX,
                                                                  aimCons.rotateY,
                                                                  aimCons.rotateZ)
        rotation_type.storable = False
        rotation_type.writable = False

        # rotation attr
        scale_type = om2.MFnNumericAttribute()
        aimCons.scaleX = scale_type.create(
            "scaleX",
            "sx",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateY
        aimCons.scaleY = scale_type.create(
            "scaleY",
            "sy",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateZ
        aimCons.scaleZ = scale_type.create(
            "scaleZ",
            "sz",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False
        aimCons.scale = scale_type.create('scale', 'se',aimCons.scaleX,
                                                        aimCons.scaleY,
                                                        aimCons.scaleZ)
        scale_type.storable = False
        scale_type.writable = False

        # add attributes
        aimCons.addAttribute(aimCons.start)
        aimCons.addAttribute(aimCons.end)
        aimCons.addAttribute(aimCons.up)
        aimCons.addAttribute(aimCons.translation)
        aimCons.addAttribute(aimCons.rotation)
        aimCons.addAttribute(aimCons.scale)
        aimCons.attributeAffects(aimCons.start, aimCons.translation)
        aimCons.attributeAffects(aimCons.end, aimCons.translation)
        aimCons.attributeAffects(aimCons.up, aimCons.translation)
        aimCons.attributeAffects(aimCons.start, aimCons.rotation)
        aimCons.attributeAffects(aimCons.end, aimCons.rotation)
        aimCons.attributeAffects(aimCons.up, aimCons.rotation)
        aimCons.attributeAffects(aimCons.start, aimCons.scale)
        aimCons.attributeAffects(aimCons.end, aimCons.scale)
        aimCons.attributeAffects(aimCons.up, aimCons.scale)

    def __init__(self):
        om2.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == aimCons.translation and aimCons.rotation and aimCons.scale:
            start_matrix = dataBlock.inputValue(aimCons.start).asMatrix()
            start_matrix = om2.MMatrix(start_matrix)

            end_matrix = dataBlock.inputValue(aimCons.end).asMatrix()
            end_matrix = om2.MMatrix(end_matrix)

            up_matrix = dataBlock.inputValue(aimCons.up).asMatrix()
            up_matrix = om2.MMatrix(up_matrix)

            start_transform_fn = om2.MTransformationMatrix(start_matrix)
            end_transform_fn = om2.MTransformationMatrix(end_matrix)
            up_transform_fn = om2.MTransformationMatrix(up_matrix)

            start_translate = start_transform_fn.translation(om2.MSpace.kTransform)
            end_translate = end_transform_fn.translation(om2.MSpace.kTransform)
            up_translate = up_transform_fn.translation(om2.MSpace.kTransform)

            start_vec = om2.MVector(start_translate)
            end_vec = om2.MVector(end_translate)
            up_vec = om2.MVector(up_translate)

            start_end_vec = (end_vec - start_vec ).normalize()
            start_up_vec = (up_vec - start_vec).normalize()

            side_vec = (start_end_vec ^ start_up_vec).normalize()

            new_up_vec = (side_vec ^ start_end_vec).normalize()

            matrix = (
                start_end_vec[0], start_end_vec[1], start_end_vec[2], 0,
                new_up_vec[0], new_up_vec[1], new_up_vec[2], 0,
                side_vec[0], side_vec[1], side_vec[2], 0,
                start_translate[0], start_translate[1], start_translate[2], 1
            )

            aim_matrix = om2.MMatrix(matrix)

            aim_transform_fn = om2.MTransformationMatrix(aim_matrix)

            aim_translate = aim_transform_fn.translation(om2.MSpace.kTransform)

            aim_rot = aim_transform_fn.rotation()
            aim_rot.x = aim_rot.x / math.pi*180.0
            aim_rot.y = aim_rot.y / math.pi*180.0
            aim_rot.z = aim_rot.z / math.pi*180.0

            aim_scale = aim_transform_fn.scale(om2.MSpace.kTransform)

            trans_out = dataBlock.outputValue(aimCons.translation)
            trans_out.set3Float(aim_translate[0], aim_translate[1], aim_translate[2])

            rot_out = dataBlock.outputValue(aimCons.rotation)
            rot_out.set3Float(aim_rot.x, aim_rot.y, aim_rot.z)

            scale_out = dataBlock.outputValue(aimCons.scale)
            scale_out.set3Float(aim_scale[0], aim_scale[1], aim_scale[2])


            dataBlock.setClean(plug)


def initializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj, 'Behnam HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeID, aimCons.nodeCreator, aimCons.nodeInitializer)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))


def uninitializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeID)
    except Exception as e:
        sys.stderr.write('Faild to unload plugin: {}, error: {}'.format(nodeName, e))

def matFromList(matList):
    mat = OpenMaya.MMatrix()
    util = OpenMaya.MScriptUtil()
    util.createMatrixFromList(matList, mat)
    return mat

def maya_useNewAPI():
    pass


# import maya.cmds as mc
#
#
# def main():
#     nodeName = 'parentCons'
#
#     pluginPath = r'D:\all_works\redtorch_tools\src\rt_tools\maya\plugin\scripted\parentCons.py'
#     if mc.pluginInfo('parentCons', q=True, loaded=True):
#         mc.file(new=True, f=True)
#         mc.unloadPlugin(nodeName)
#
#     mc.loadPlugin(pluginPath)
#
#
# main()
# mc.createNode('parentCons')
# a = mc.getAttr('parentCons1.translation')
# print(a)