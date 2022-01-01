import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.api.OpenMaya as om2
import maya.cmds as mc
import sys
import math

nodeName = 'parentCons'
nodeID = om2.MTypeId(0x0011E18F)


# node definition
class parentCons(om2.MPxNode):
    input = om2.MObject()
    output = om2.MObject()

    @staticmethod
    def nodeCreator():
        return parentCons()

    @staticmethod
    def nodeInitializer():
        # in childBase attr
        childBase_type = om2.MFnMatrixAttribute()
        parentCons.childBase = childBase_type.create('childBase', 'cb' )
        childBase_type.storable = True
        childBase_type.writable = True
        childBase_type.keyable = True

        # in parentBase attr
        parentBase_type = om2.MFnMatrixAttribute()
        parentCons.parentBase = parentBase_type.create('parentBase', 'pb')
        parentBase_type.storable = True
        parentBase_type.writable = True
        parentBase_type.keyable = True

        # in parent attr
        parent_type = om2.MFnMatrixAttribute()
        parentCons.parent = parent_type.create('parent', 'pt' )
        parent_type.storable = True
        parent_type.writable = True
        parent_type.keyable = True

        # translation attr
        translation_type = om2.MFnNumericAttribute()
        parentCons.translateX = translation_type.create(
            "translateX",
            "tx",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        # output rotateY
        parentCons.translateY = translation_type.create(
            "translateY",
            "ty",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        # output rotateZ
        parentCons.translateZ = translation_type.create(
            "translateZ",
            "tz",
            om2.MFnNumericData.kFloat,
            0.0
        )
        translation_type.storable = False

        parentCons.translation = translation_type.create('translation', 'ts', parentCons.translateX,
                                                                              parentCons.translateY,
                                                                              parentCons.translateZ)
        translation_type.storable = False
        translation_type.writable = False

        # rotation attr
        rotation_type = om2.MFnNumericAttribute()
        parentCons.rotateX = rotation_type.create(
            "rotateX",
            "rx",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateY
        parentCons.rotateY = rotation_type.create(
            "rotateY",
            "ry",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        # output rotateZ
        parentCons.rotateZ = rotation_type.create(
            "rotateZ",
            "rz",
            om2.MFnNumericData.kFloat,
            0.0
        )
        rotation_type.storable = False

        parentCons.rotation = rotation_type.create('rotation', 'rt', parentCons.rotateX,
                                                                     parentCons.rotateY,
                                                                     parentCons.rotateZ)
        rotation_type.storable = False
        rotation_type.writable = False

        # rotation attr
        scale_type = om2.MFnNumericAttribute()
        parentCons.scaleX = scale_type.create(
            "scaleX",
            "sx",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateY
        parentCons.scaleY = scale_type.create(
            "scaleY",
            "sy",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False

        # output rotateZ
        parentCons.scaleZ = scale_type.create(
            "scaleZ",
            "sz",
            om2.MFnNumericData.kFloat,
            1.0
        )
        scale_type.storable = False
        parentCons.scale = scale_type.create('scale', 'se',parentCons.scaleX,
                                                           parentCons.scaleY,
                                                           parentCons.scaleZ)
        scale_type.storable = False
        scale_type.writable = False


        # add attributes
        parentCons.addAttribute(parentCons.childBase)
        parentCons.addAttribute(parentCons.parentBase)
        parentCons.addAttribute(parentCons.parent)
        parentCons.addAttribute(parentCons.translation)
        parentCons.addAttribute(parentCons.rotation)
        parentCons.addAttribute(parentCons.scale)
        parentCons.attributeAffects(parentCons.childBase, parentCons.translation)
        parentCons.attributeAffects(parentCons.parentBase, parentCons.translation)
        parentCons.attributeAffects(parentCons.parent, parentCons.translation)
        parentCons.attributeAffects(parentCons.childBase, parentCons.rotation)
        parentCons.attributeAffects(parentCons.parentBase, parentCons.rotation)
        parentCons.attributeAffects(parentCons.parent, parentCons.rotation)
        parentCons.attributeAffects(parentCons.childBase, parentCons.scale)
        parentCons.attributeAffects(parentCons.parentBase, parentCons.scale)
        parentCons.attributeAffects(parentCons.parent, parentCons.scale)

    def __init__(self):
        om2.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == parentCons.translation and parentCons.rotation and parentCons.scale:
            parent_base_matrix = dataBlock.inputValue(parentCons.parentBase).asMatrix()
            #parentBaseM = matFromList(parentBaseM)
            parent_base_matrix = om2.MMatrix(parent_base_matrix)

            child_base_matrix = dataBlock.inputValue(parentCons.childBase).asMatrix()
            #childBaseM = child_base_matrix.asDouble()
            #childBaseM = matFromList(childBaseM)
            child_base_matrix = om2.MMatrix(child_base_matrix)

            parent_matrix = dataBlock.inputValue(parentCons.parent).asMatrix()
            #parentM = parent_matrix.asDouble()
            #parentM = matFromList(parentM)
            parent_matrix = om2.MMatrix(parent_matrix)

            child_parent_mult =  child_base_matrix.transpose() * parent_base_matrix.transpose()
            child_parent_mult  = child_parent_mult.transpose()

            offset_parentM_mult =   child_parent_mult * parent_matrix

            transformation_mat = om2.MTransformationMatrix(offset_parentM_mult)

            translate = transformation_mat.translation(om2.MSpace.kTransform)
            trans_out = dataBlock.outputValue(parentCons.translation)
            trans_out.set3Float(translate[0], translate[1], translate[2])

            rot = transformation_mat.rotation()
            rot.x = rot.x / math.pi*180.0
            rot.y = rot.y / math.pi*180.0
            rot.z = rot.z / math.pi*180.0
            rot_out = dataBlock.outputValue(parentCons.rotation)
            rot_out.set3Float(rot.x, rot.y, rot.z)

            scal = transformation_mat.scale(om2.MSpace.kTransform)
            scale_out = dataBlock.outputValue(parentCons.scale)
            scale_out.set3Float(scal[0], scal[1], scal[2])


            dataBlock.setClean(plug)



def initializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj, 'Behnam HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeID, parentCons.nodeCreator, parentCons.nodeInitializer)
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