import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys


nodeName = 'pushOut'
maxAngle = 0.6 * 3.14159265
nodeId = om.MTypeId(0x0011E1FE)

class PushOutNode(mpx.MPxDeformerNode):

    def __init__(self):
        super(PushOutNode, self).__init__()

    def deform(self, data_block, geo_iter, world_matrix, multi_index):

        envelope = data_block.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return

        max_distance = data_block.inputValue(PushOutNode.max_distance).asFloat()
        if max_distance == 0:
            return

        target_position = data_block.inputValue(PushOutNode.target_position).asFloatVector()
        target_position = om.MPoint(target_position) * world_matrix.inverse()
        target_position = om.MFloatVector(target_position)

        input_handle = data_block.outputArrayValue(self.input)
        input_handle.jumpToElement(multi_index)
        input_element_handle = input_handle.outputValue()

        input_geom = input_element_handle.child(self.inputGeom).asMesh()
        mesh_fn = om.MFnMesh(input_geom)

        normals = om.MFloatVectorArray()
        mesh_fn.getVertexNormals(False, normals)

        geo_iter.reset()
        while not geo_iter.isDone():
            idx = geo_iter.index()

            # weight
            weight = self.weightValue(data_block, multi_index, idx)

            pt_local = geo_iter.position()

            target_vector = -(target_position - om.MFloatVector(pt_local))

            distance = target_vector.length()
            if distance <= max_distance:

                normal = normals[geo_iter.index()]

                angle = normal.angle(target_vector)
                if angle <= maxAngle:
                    offset = target_vector * ((max_distance - distance) / max_distance) * (weight)

                    geo_iter.setPosition(pt_local + om.MVector(offset))

            geo_iter.next()

    def accessoryAttribute(self):
        return PushOutNode.target_position

    def accessoryNodeSetup(self, dag_modifier):

        locator = dag_modifier.createNode("locator")

        locator_fn = om.MFnDependencyNode(locator)
        locator_translate_plug = locator_fn.findPlug("translate", False)

        target_position_plug = om.MPlug(self.thisMObject(), PushOutNode.target_position)
        dag_modifier.connect(locator_translate_plug, target_position_plug)

def nodeCreator():
    return mpx.asMPxPtr(PushOutNode())

def nodeInitializer():
    numeric_attr = om.MFnNumericAttribute()

    PushOutNode.max_distance = numeric_attr.create("maximumDistance", "maxDist", om.MFnNumericData.kFloat, 1.0)
    numeric_attr.setKeyable(True)
    numeric_attr.setMin(0.0)
    numeric_attr.setMax(2.0)

    PushOutNode.target_position = numeric_attr.createPoint("targetPosition", "targetPos");
    numeric_attr.setKeyable(True)

    PushOutNode.addAttribute(PushOutNode.max_distance)
    PushOutNode.addAttribute(PushOutNode.target_position)

    output_geom = mpx.cvar.MPxGeometryFilter_outputGeom
    PushOutNode.attributeAffects(PushOutNode.max_distance, output_geom)
    PushOutNode.attributeAffects(PushOutNode.target_position, output_geom)


def initializePlugin(plugin):
    plugin = mpx.MFnPlugin(plugin, 'Behnam HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer, mpx.MPxNode.kDeformerNode)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))
    mc.makePaintable(nodeName, "weights", attrType="multiFloat", shapeMode="deformer")


def uninitializePlugin(plugin):
    mc.makePaintable(nodeName, "weights", remove=True)

    plugin = mpx.MFnPlugin(plugin)
    try:
        plugin.deregisterNode(nodeId)
    except Exception as e:
        sys.stderr.write('Faild to unload plugin: {}, error: {}'.format(nodeName, e))


def main():
    pluginPath = __file__
    if mc.pluginInfo(nodeName, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)

    sphere = mc.polySphere()[0]
    mc.select(sphere)
    dfmN = mc.deformer(type= nodeName)


