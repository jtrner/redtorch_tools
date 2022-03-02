import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
from math import sqrt
import sys


nodeName = 'skirt'
maxAngle = 0.3 * 3.14159265
nodeId = om.MTypeId(0x0011E194)

class SkirtNode(mpx.MPxDeformerNode):

    def __init__(self):
        super(SkirtNode, self).__init__()

    def deform(self, data_block, geo_iter, world_matrix, multi_index):

        envelope = data_block.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return


        legMatrix = data_block.inputValue(SkirtNode.legMatrix).asMatrix()
        skirtMatrix = data_block.inputValue(SkirtNode.skirtMatrix).asMatrix()

        leg_pos = om.MVector(legMatrix(3, 0),
                              legMatrix(3, 1),
                              legMatrix(3, 2))

        leg_y_axis = om.MVector(legMatrix(1, 0),
                                 legMatrix(1, 1),
                                 legMatrix(1, 2))

        skirt_pos = om.MVector(skirtMatrix(3, 0),
                              skirtMatrix(3, 1),
                              skirtMatrix(3, 2))

        skirt_y_axis = om.MVector(skirtMatrix(1, 0),
                                 skirtMatrix(1, 1),
                                 skirtMatrix(1, 2))

        leg_y_axis_pro = (leg_y_axis[0], leg_y_axis[1], leg_y_axis[2])
        skirt_y_axis_pro = (skirt_y_axis[0], skirt_y_axis[1], skirt_y_axis[2])

        proj_swing = project_onto_plane(leg_y_axis_pro, skirt_y_axis_pro)

        proj_swing = om.MVector(proj_swing[0], proj_swing[1], proj_swing[2]).normal() * 3

        dist_vec = leg_pos - skirt_pos
        ring_plane_normalized = leg_y_axis.normal()
        dist = dist_vec * ring_plane_normalized
        scaled_vec = om.MVector(dist * ring_plane_normalized[0], dist * ring_plane_normalized[1],
                                dist * ring_plane_normalized[2])
        proj_ring_translate = skirt_pos - scaled_vec
        ray_source = proj_ring_translate + om.MVector(leg_y_axis).normal() * 3

        input_handle = data_block.outputArrayValue(self.input)
        input_handle.jumpToElement(multi_index)
        input_element_handle = input_handle.outputValue()
        input_geom = input_element_handle.child(self.inputGeom).asMesh()
        meshFn = om.MFnMesh(input_geom)
        normals = om.MFloatVectorArray()
        meshFn.getVertexNormals(False, normals)

        geo_iter.reset()
        while not geo_iter.isDone():
            idx = geo_iter.index()
            accel = meshFn.autoUniformGridParams()
            hitPoints = om.MFloatPointArray()
            hit_ray_params = om.MFloatArray()
            hit_faces = om.MIntArray()
            meshFn.allIntersections(om.MFloatPoint(ray_source[0], ray_source[1], ray_source[2], 1),
                                    om.MFloatVector(proj_swing[0], proj_swing[1], proj_swing[2]),
                                    None, None, False, om.MSpace.kWorld, leg_y_axis.length(),
                                    False, accel, False, hitPoints, hit_ray_params, hit_faces,
                                    None, None, None, 0.0001)
            p1 = hitPoints[0]
            max_dist = 12
            if p1:
                ring_proj_swing = project_onto_plane((proj_swing[0], proj_swing[1], proj_swing[2]),
                                                     leg_y_axis_pro)
                ring_proj_swing = om.MVector(ring_proj_swing[0], ring_proj_swing[1],
                                             ring_proj_swing[2]).normal() * 0.73

                # consider ring scale
                ring_proj_swing_inv = om.MVector(ring_proj_swing * legMatrix.inverse())
                delta = ring_proj_swing.length() / ring_proj_swing_inv.length()
                p = leg_pos + ring_proj_swing * delta

                # Linear equation
                r = (om.MVector(p1) - skirt_pos).length()
                c = om.MPoint(skirt_pos)
                v = om.MVector(leg_y_axis).normal()

                a = v.x * v.x + v.y * v.y + v.z * v.z
                b = 2 * (v.x * (p.x - p.x) + v.y * (p.y - c.y) + v.z * (p.z - c.z))
                c = (p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * (p.z - c.z) - r * r

                delta = b * b - 4 * a * c

                root1 = ((-1 * b) + sqrt(delta)) / 2 * a
                root2 = ((-1 * b) - sqrt(delta)) / 2 * a

                p2 = om.MVector(p + v * root1)

                # weight
                weight = self.weightValue(data_block, multi_index, idx)

                pt_local = geo_iter.position()
                target_vector = (om.MVector(p2[0] , p2[1], p2[2]) - om.MVector(pt_local))
                distance = target_vector.length()
                if distance < max_dist:

                    normal = normals[geo_iter.index()]
                    angle = normal.angle(om.MFloatVector(om.MVector(p2[0] , p2[1], p2[2])))
                    if angle <= maxAngle:
                        dist = ((max_dist - distance) / max_dist)
                        offset = (pt_local + om.MVector(normal.normal())) * dist * (weight)
                        if om.MVector(offset).length() > om.MVector(pt_local).length():
                            geo_iter.setPosition(om.MPoint(offset))

            geo_iter.next()



def nodeCreator():
    return mpx.asMPxPtr(SkirtNode())

def nodeInitializer():
    matrix_attr = om.MFnMatrixAttribute()

    SkirtNode.legMatrix = matrix_attr.create("legMatrix", "leg")
    matrix_attr.setKeyable(True)

    SkirtNode.skirtMatrix = matrix_attr.create("skirtMatrix", "skt")
    matrix_attr.setKeyable(True)

    SkirtNode.addAttribute(SkirtNode.legMatrix)
    SkirtNode.addAttribute(SkirtNode.skirtMatrix)

    output_geom = mpx.cvar.MPxGeometryFilter_outputGeom
    SkirtNode.attributeAffects(SkirtNode.legMatrix, output_geom)
    SkirtNode.attributeAffects(SkirtNode.skirtMatrix, output_geom)


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


def getDagPath(node):
    sel = om.MSelectionList()
    sel.add(node)
    dag = om.MDagPath()
    sel.getDagPath(0, dag)
    return dag

def dot_product(x, y):
    return sum([x[i] * y[i] for i in range(len(x))])

def norm(x):
    return sqrt(dot_product(x, x))

def normalize(x):
    return [x[i] / norm(x) for i in range(len(x))]

def project_onto_plane(x, n):
    d = dot_product(x, n) / norm(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    return [x[i] - p[i] for i in range(len(x))]

def main():
    pluginPath = __file__
    if mc.pluginInfo(nodeName, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)

    sphere = mc.polySphere()[0]
    mc.select(sphere)
    dfmN = mc.deformer(type= nodeName)

# def main():
#     nodeName = 'skirt'
#
#     pluginPath = r'D:\all_works\redtorch_tools\src\rt_tools\maya\plugin\scripted\skirt.py'
#     if mc.pluginInfo('skirt', q=True, loaded=True):
#         mc.file(new=True, f=True)
#         mc.unloadPlugin(nodeName)
#
#     mc.loadPlugin(pluginPath)
#
#
# main()
# mc.file('G:\tutorials\api\collision.ma', o=True)
# mc.select('bell')
# mc.deformer(type='skirt')
# mc.connectAttr('ring.worldMatrix[0]', 'skirt1.legMatrix')
# mc.connectAttr('bell.worldMatrix[0]', 'skirt1.skirtMatrix')



