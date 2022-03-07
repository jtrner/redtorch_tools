import math
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import sys

__version__ = 1.0

kPluginNodeTypeName = "shardMatrix"
dynNodeId = om.MTypeId(0x00001)


# Node definition
class ShardMatrix(ommpx.MPxNode):
    in_mesh_attribute = om.MObject()
    translate_out = om.MObject()
    rotate_out = om.MObject()
    scale_out = om.MObject()
    #size_attribute = om.MObject()
    rotation_order = om.MEulerRotation.kXYZ

    def __init__(self):
        ommpx.MPxNode.__init__(self)

    def compute(self, plug, data):

        if plug == ShardMatrix.translate_out:
            input_data = data.inputValue(ShardMatrix.in_mesh_attribute)
            mesh_m_object = input_data.asMesh()
            mesh_functions = om.MFnMesh(mesh_m_object)
            point_0 = om.MPoint()
            mesh_functions.getPoint(0, point_0, om.MSpace.kWorld)
            translate_out_handle = data.outputValue(ShardMatrix.translate_out)
            translate_out_value = om.MFloatVector(
                point_0[0],
                point_0[1],
                point_0[2]
            )
            translate_out_handle.setMFloatVector(translate_out_value)
            data.setClean(plug)

        elif plug == ShardMatrix.rotate_out:
            space = om.MSpace.kWorld
            input_data = data.inputValue(ShardMatrix.in_mesh_attribute)
            mesh_m_object = input_data.asMesh()
            mesh_functions = om.MFnMesh(mesh_m_object)
            point_0 = om.MPoint()
            mesh_functions.getPoint(0, point_0, space)
            point_1 = om.MPoint()
            mesh_functions.getPoint(1, point_1, space)
            point_2 = om.MPoint()
            mesh_functions.getPoint(2, point_2, space)
            point_3 = om.MPoint()
            mesh_functions.getPoint(1, point_3, space)
            translate = point_0[0], point_0[1], point_0[2]
            vx = om.MVector(point_1 - point_0).normal()
            vy = om.MVector(point_2 - point_0).normal()
            vz = cross(vx, vy) * -1
            matrix = om.MMatrix()
            om.MScriptUtil.setDoubleArray(matrix[0], 0, vx[0])
            om.MScriptUtil.setDoubleArray(matrix[0], 1, vx[1])
            om.MScriptUtil.setDoubleArray(matrix[0], 2, vx[2])
            om.MScriptUtil.setDoubleArray(matrix[1], 0, vy[0])
            om.MScriptUtil.setDoubleArray(matrix[1], 1, vy[1])
            om.MScriptUtil.setDoubleArray(matrix[1], 2, vy[2])
            om.MScriptUtil.setDoubleArray(matrix[2], 0, vz[0])
            om.MScriptUtil.setDoubleArray(matrix[2], 1, vz[1])
            om.MScriptUtil.setDoubleArray(matrix[2], 2, vz[2])
            om.MScriptUtil.setDoubleArray(matrix[3], 0, translate[0])
            om.MScriptUtil.setDoubleArray(matrix[3], 1, translate[1])
            om.MScriptUtil.setDoubleArray(matrix[3], 2, translate[2])
            transformation_matrix = om.MTransformationMatrix(matrix)
            rotate_out_hande = data.outputValue(ShardMatrix.rotate_out)
            euler_rotation = transformation_matrix.eulerRotation()
            euler_rotation.reorderIt(self.rotation_order)
            angles = [math.degrees(angle) for angle in (euler_rotation.x, euler_rotation.y, euler_rotation.z)]
            rotate_out_value = om.MFloatVector(
                angles[0],
                angles[1],
                angles[2]
            )
            rotate_out_hande.setMFloatVector(rotate_out_value)
            data.setClean(plug)

        elif plug == ShardMatrix.scale_out:
            #size_handle = data.outputValue(ShardMatrix.size_attribute)
            #scale_value = size_handle.asFloat()
            scale_value = 0.0025

            space = om.MSpace.kWorld
            input_data = data.inputValue(ShardMatrix.in_mesh_attribute)
            mesh_m_object = input_data.asMesh()
            mesh_functions = om.MFnMesh(mesh_m_object)
            point_0 = om.MPoint()
            mesh_functions.getPoint(0, point_0, space)
            point_1 = om.MPoint()
            mesh_functions.getPoint(1, point_1, space)
            point_2 = om.MPoint()
            mesh_functions.getPoint(2, point_2, space)
            point_3 = om.MPoint()
            mesh_functions.getPoint(3, point_3, space)
            scale_vector_x = om.MVector(point_1 - point_0)
            scale_vector_y = om.MVector(point_2 - point_0)
            scale_vector_z = om.MVector(point_3 - point_0)
            scale_out_handle = data.outputValue(ShardMatrix.scale_out)
            scale_out_handle.setMFloatVector(om.MFloatVector(
                scale_vector_x.length()/scale_value,
                scale_vector_y.length()/scale_value,
                scale_vector_z.length()/scale_value
            ))
            data.setClean(plug)

        else:
            return om.kUnknownParameter


def nodeCreator():
    return ommpx.asMPxPtr(ShardMatrix())


def nodeInitializer():
    typed_attribute_functions = om.MFnTypedAttribute()
    numeric_attribute_functions = om.MFnNumericAttribute()
    ShardMatrix.translate_out = numeric_attribute_functions.createPoint("translate", "t")
    numeric_attribute_functions.setStorable(False)
    ShardMatrix.rotate_out = numeric_attribute_functions.createPoint("rotate", "r")
    numeric_attribute_functions.setStorable(False)
    ShardMatrix.scale_out = numeric_attribute_functions.createPoint("scale", "s")
    numeric_attribute_functions.setStorable(False)
    ShardMatrix.in_mesh_attribute = typed_attribute_functions.create(
        "inMesh", "im",
        om.MFnData.kMesh
    )
    typed_attribute_functions.setReadable(False)
    #ShardMatrix.size_attribute = numeric_attribute_functions.create(
    #    "sizeMultiply", "sm",
    #    om.MFnNumericData.kDouble, 1.0
    #)
    #typed_attribute_functions.setKeyable(True)
    #typed_attribute_functions.setReadable(True)
    #typed_attribute_functions.setStorable(True)

    ShardMatrix.addAttribute(ShardMatrix.in_mesh_attribute)
    #ShardMatrix.addAttribute(ShardMatrix.size_attribute)
    ShardMatrix.addAttribute(ShardMatrix.translate_out)
    ShardMatrix.addAttribute(ShardMatrix.rotate_out)
    ShardMatrix.addAttribute(ShardMatrix.scale_out)

    ShardMatrix.attributeAffects(ShardMatrix.in_mesh_attribute, ShardMatrix.translate_out)
    ShardMatrix.attributeAffects(ShardMatrix.in_mesh_attribute, ShardMatrix.rotate_out)
    ShardMatrix.attributeAffects(ShardMatrix.in_mesh_attribute, ShardMatrix.scale_out)
    #ShardMatrix.attributeAffects(ShardMatrix.size_attribute, ShardMatrix.translate_out)
    #ShardMatrix.attributeAffects(ShardMatrix.size_attribute, ShardMatrix.scale_out)


def initializePlugin(mobject):
    mplugin = ommpx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(kPluginNodeTypeName, dynNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write("Failed to register node: %s" % kPluginNodeTypeName)
        raise


def uninitializePlugin(mobject):
    mplugin = ommpx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(dynNodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % kPluginNodeTypeName)
        raise

def cross(vec_a, vec_b):
    return om.MVector(
        vec_a[1] * vec_b[2] - vec_a[2] * vec_b[1],
        vec_a[2] * vec_b[0] - vec_a[0] * vec_b[2],
        vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0]
    )
