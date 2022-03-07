import math

import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

kInput = ompx.cvar.MPxGeometryFilter_input
kInputGeom = ompx.cvar.MPxGeometryFilter_inputGeom
kOutputGeom = ompx.cvar.MPxGeometryFilter_outputGeom
kEnvelope = ompx.cvar.MPxGeometryFilter_envelope
kGroupId = ompx.cvar.MPxGeometryFilter_groupId


class ProjectDeformer(ompx.MPxDeformerNode):
    type_id = om.MTypeId(0x0011E196)
    type_name = "ProjectDeformer"
    meshes_attr = om.MObject()
    colliderList = om.MObject()
    reset_pos = om.MObject()
    bulge_multiplier_attr = om.MObject()
    levels_attr = om.MObject()
    bulgeshape_attr = om.MObject()
    prev_points = None

    @classmethod
    def initialize(cls):

        typedAttr = om.MFnTypedAttribute()
        reset_attr = om.MFnEnumAttribute()

        cls.colliderList = typedAttr.create("colliderList", "collist", om.MFnData.kMesh)
        typedAttr.setArray(True)
        typedAttr.setReadable(False)
        typedAttr.setKeyable(True)
        typedAttr.setDisconnectBehavior(0)

        # add interp_type enum attr
        cls.reset_pos = reset_attr.create("mode", "md", 1)
        reset_attr.addField('reset_pos', 0)
        reset_attr.addField('keep_pushing', 1)
        reset_attr.setKeyable(True)

        cls.addAttribute(cls.colliderList)
        cls.addAttribute(cls.reset_pos)

        cls.attributeAffects(cls.colliderList, kOutputGeom)
        cls.attributeAffects(cls.reset_pos, kOutputGeom)

    @classmethod
    def creator(cls):

        return cls()

    def __init__(self):
        ompx.MPxDeformerNode.__init__(self)

    def deform(self, data_block, geometry_iterator, local_to_world_matrix, geometry_index):

        envelope_attribute = kEnvelope
        envelope_value = data_block.inputValue(envelope_attribute).asFloat()
        if envelope_value == 0:
            return

        thisNode = om.MFnDependencyNode(self.thisMObject())
        colliderIndexList = om.MIntArray()

        input_geometry_object = self.getDeformerInputGeometry(
            data_block,
            geometry_index
        )

        normals = om.MFloatVectorArray()
        mesh_fn = om.MFnMesh(input_geometry_object)
        mesh_fn.getVertexNormals(True, normals, om.MSpace.kTransform)
        orig_points = om.MFloatPointArray()
        mesh_fn.getPoints(orig_points)

        colliderListHandle = data_block.inputArrayValue(ProjectDeformer.colliderList)

        if colliderListHandle.elementCount() < 1:
            return

        colliderListPlug = thisNode.findPlug("colliderList", False)
        for i in range(colliderListHandle.elementCount()):
            item = colliderListPlug.elementByPhysicalIndex(i)
            index = int(item.name()[-2])
            colliderIndexList.append(index)

        for col in range(colliderIndexList.length()):
            colliderListHandle.jumpToElement(colliderIndexList[col])
            colliderInput = colliderListHandle.inputValue().asMesh()
            colMeshFN = om.MFnMesh(colliderInput)

            push_mode = data_block.inputValue(self.reset_pos)

            if push_mode.asShort() == 1:
                orig_points = orig_points if not self.prev_points else self.prev_points

            mesh_vertex_iterator = om.MItMeshVertex(input_geometry_object)

            while not mesh_vertex_iterator.isDone():

                vertex_index = mesh_vertex_iterator.index()

                normal = om.MVector(normals[vertex_index])
                point = mesh_vertex_iterator.position()
                ws_point = point * local_to_world_matrix
                ws_fl_point = om.MFloatPoint(ws_point)

                ws_normal = normal * local_to_world_matrix

                ws_fl_normal = om.MFloatVector(ws_normal) * -1

                intersecting_point, cl_pnt = self.getIntersection(
                    ws_fl_point,
                    ws_fl_normal,
                    colMeshFN
                )

                if intersecting_point:
                    diff = om.MFloatPoint(cl_pnt[0], cl_pnt[1], cl_pnt[2]) - ws_fl_point

                    new_point = point + om.MVector(
                        diff * envelope_value
                    ) * local_to_world_matrix.inverse()

                    orig_points[vertex_index].x = new_point.x
                    orig_points[vertex_index].y = new_point.y
                    orig_points[vertex_index].z = new_point.z

                mesh_vertex_iterator.next()

            self.prev_points = om.MFloatPointArray()
            mesh_fn.setPoints(orig_points)
            mesh_fn.getPoints(self.prev_points)

    def getIntersection(self, point, normal, mesh):

        intersection_normal = om.MVector()
        closest_point = om.MPoint()

        mesh.getClosestPointAndNormal(
            om.MPoint(point),
            closest_point,
            intersection_normal,
            om.MSpace.kWorld,
        )

        angle = normal.angle(om.MFloatVector(intersection_normal))
        if angle >= math.pi or angle <= -math.pi:
            average_normal = normal
        else:
            average_normal = om.MVector(normal) + intersection_normal

        intersections = om.MFloatPointArray()
        mesh.allIntersections(
            point, om.MFloatVector(average_normal), None, None, False, om.MSpace.kWorld,
            1000, False, None, True, intersections, None,
            None, None, None, None
        )

        intersecting_point = None
        if intersections.length() % 2 == 1:
            intersecting_point = intersections[0]

        return intersecting_point, closest_point

    def getDeformerInputGeometry(self, data_block, geometry_index):

        inputAttribute = ompx.cvar.MPxGeometryFilter_input
        inputGeometryAttribute = ompx.cvar.MPxGeometryFilter_inputGeom

        inputHandle = data_block.outputArrayValue(inputAttribute)
        inputHandle.jumpToElement(geometry_index)
        inputGeometryObject = inputHandle.outputValue().child(
            inputGeometryAttribute
        ).asMesh()

        return inputGeometryObject


def initializePlugin(plugin):
    """Called when plugin is loaded.
    Args:
        plugin (MObject): The plugin.
    """
    plugin_fn = ompx.MFnPlugin(plugin, "BehnamHM", "1.0.0")

    try:
        plugin_fn.registerNode(
            ProjectDeformer.type_name,
            ProjectDeformer.type_id,
            ProjectDeformer.creator,
            ProjectDeformer.initialize,
            ompx.MPxNode.kDeformerNode
        )
    except:
        print
        "failed to register node {0}".format(ProjectDeformer.type_name)
        raise


def uninitializePlugin(plugin):
    """Called when plugin is unloaded.
    Args:
        plugin (MObject): The plugin.
    """
    plugin_fn = ompx.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(ProjectDeformer.type_id)
    except:
        print
        "failed to deregister node {0}".format(
            ProjectDeformer.type_name
        )
        raise


'''
from maya import cmds as mc
def main():
    pluginPath = r'D:\all_works\redtorch_tools\src\rt_tools\maya\plugin\scripted\ProjectDeformer.py'
    nodeName = 'ProjectDeformer'
    if mc.pluginInfo(nodeName, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    cmds.loadPlugin(pluginPath)

    mesh = mc.polyPlane()[0]
    mesh2 = mc.polySphere()[0]
    mc.setAttr("pPlane1.s",17.148547, 17.148547, 17.148547)

    mc.setAttr("polyPlane1.subdivisionsWidth", 18.5)
    mc.setAttr("polyPlane1.subdivisionsHeight", 18.5)

    collider_shapes = cmds.listRelatives(mesh2, shapes=True)
    mc.select(mesh)
    deformer_nodes = cmds.deformer( type='ProjectDeformer' )
    mc.connectAttr(
    '{0}.worldMesh'.format(collider_shapes[0]),
    '{0}.colliderList[0]'.format(deformer_nodes[0]),
    )
main()    


'''


