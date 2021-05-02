"""
import sys
path = 'D:/plugin/scripted'
if path not in sys.path:
    sys.path.insert(0, path)

import squish
reload(squish)


squish.main()
"""

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import math

nodeName = 'squish'
nodeId = om.MTypeId(0x0011E18F)

# Some global variables were moved from MPxDeformerNode to MPxGeometryFilter.
# Set some constants to the proper C++ cvars based on the API version.
kApiVersion = mc.about(apiVersion=True)
if kApiVersion < 201600:
    kInput = mpx.cvar.MPxDeformerNode_input
    kInputGeom = mpx.cvar.MPxDeformerNode_inputGeom
    kOutputGeom = mpx.cvar.MPxDeformerNode_outputGeom
    kEnvelope = mpx.cvar.MPxDeformerNode_envelope
else:
    kInput = mpx.cvar.MPxGeometryFilter_input
    kInputGeom = mpx.cvar.MPxGeometryFilter_inputGeom
    kOutputGeom = mpx.cvar.MPxGeometryFilter_outputGeom
    kEnvelope = mpx.cvar.MPxGeometryFilter_envelope


class squish(mpx.MPxDeformerNode):

    def __init__(self):
        mpx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoItr, world_matrix, geo_idx):

        # get envelope
        envelopeHandle = dataBlock.inputValue(kEnvelope)
        envelopeValue = envelopeHandle.asFloat()
        if not envelopeValue:
            return

        # get Mesh
        inMesh = self.getDeformerInputGeometry(dataBlock, geo_idx)

        # get matrix
        matrixHandle = dataBlock.inputValue(self.matrix)
        matrixValue = matrixHandle.asMatrix()

        # stretchValue
        stretchHandle = dataBlock.inputValue(self.stretch)
        stretchValue = stretchHandle.asFloat()

        # volumeValue
        volumeHandle = dataBlock.inputValue(self.volume)
        volumeValue = volumeHandle.asFloat()

        # bendXValue
        bendXHandle = dataBlock.inputValue(self.bendX)
        bendXValue = bendXHandle.asFloat()

        # using this we have complete control over geometry # use MFnMesh for faster results
        inmeshVertexItr = om.MItMeshVertex(inMesh)

        # get original point positions
        origPoses = om.MPointArray()
        geoItr.allPositions(origPoses, om.MSpace.kObject)

        # deformed points
        finalPoses = om.MPointArray()

        # geo_idx pointer
        index_util = om.MScriptUtil()
        index_util.createFromInt(geo_idx)
        geo_idx_ptr = index_util.asIntPtr()

        # deform
        while not geoItr.isDone():
            idx = geoItr.index()

            # weight
            weight = self.weightValue(dataBlock, geo_idx, idx)

            # set index for vertex iterator
            inmeshVertexItr.setIndex(idx, geo_idx_ptr)

            # get orig position
            pointPosition = origPoses[idx]

            # take the point to space of given deformer_handle_transform_node
            point_world = pointPosition * world_matrix * matrixValue.inverse()

            # find how much the deformer_handle_transform_node is scaled in Y
            deformer_scale_y = om.MVector(matrixValue[1]).length()

            # only deform points that are above the given deformer_handle_transform_node
            if point_world.y > 0.0:

                # strech and volume
                stretch_deltas = self.calculate_strech(
                    point_world,
                    stretchValue,
                    volumeValue,
                    envelopeValue,
                    weight,
                )
                point_world += stretch_deltas

                # bend
                bend_deltas = self.calculate_bend(
                    point_world,
                    bendXValue,
                    deformer_scale_y,
                    envelopeValue,
                    weight,
                )
                point_world += bend_deltas

            # put the point back to world position
            point_world = point_world * matrixValue * world_matrix.inverse()

            finalPos = point_world  # pointPosition + stretchAmount

            finalPoses.append(finalPos)

            geoItr.next()

        geoItr.setAllPositions(finalPoses)

    def getDeformerInputGeometry(self, pDataBlock, pGeometryIndex):
        """
        get a reference to the input mesh using deformer's 'input' and 'inputGeom' attributes.
        """
        inputHandle = pDataBlock.outputArrayValue(kInput)
        inputHandle.jumpToElement(pGeometryIndex)
        inputGeometryObject = inputHandle.outputValue().child(kInputGeom).asMesh()
        return inputGeometryObject

    @staticmethod
    def calculate_strech(point_world, stretchValue, volumeValue, envelopeValue, weight):
        # add 1.0 to stretch value so 0.0 is neutral pose instead of 1.0 being neutral
        stretchValue += 1.0

        # stretch value can't be zero or negative
        if stretchValue <= 0.0:
            stretchValue = 0.0001

        # stretch the point along y
        stretch_vector = om.MVector(0, point_world.y, 0) * stretchValue

        # find how much the point is going to move and multiply it by weight and envelope
        stretch_y_delta = (stretch_vector.y - point_world.y)

        # maintain volume by scaling the x and z in the opposite direction
        squish_mult = (stretchValue ** 0.5) / stretchValue
        stretch_x_delta = volumeValue * ((point_world.x * squish_mult) - point_world.x)
        stretch_z_delta = volumeValue * ((point_world.z * squish_mult) - point_world.z)

        # return stretch amounts in x, y and z
        stretch_deltas = om.MVector(
            stretch_x_delta,
            stretch_y_delta,
            stretch_z_delta,
        )

        return stretch_deltas * envelopeValue * weight

    @staticmethod
    def calculate_bend(point_world, bendXValue, deformer_scale_y, envelopeValue, weight):
        """
        To calculate bend x:
         - project point to Y vector (get rid of x)
         - get ratio of this Y compared to deformer_handle_transform_node.scaleY
         - based on given angle and deformer_handle_transform_node.scaleY find the bend circle (center and radius)
         - use the Y ratio to find location of projected-point-to-Y if it was bent to match this circle
         - get a vector from center of bend_circle to found point
         - extend this vector by the distance we had removed from original point to project to Y (x axis distance)
        """
        bend_delta_x = 0.0
        bend_delta_y = 0.0
        bend_delta_z = 0.0

        if bendXValue != 0.0:
            # find bend circle (center and radius)
            circumference = deformer_scale_y * 360.0 / bendXValue
            radius_for_middle_points = circumference / (2 * math.pi)
            center_of_circle_x = radius_for_middle_points
            radius = radius_for_middle_points - point_world.x

            # find out much current point should rotate around the circle
            angle_of_pnt_on_circle = point_world.y * bendXValue

            # find x and y of the point on circle
            x_in_radian = math.radians(angle_of_pnt_on_circle)
            cos_x = math.cos(x_in_radian)
            sin_x = math.sin(x_in_radian)

            # scale the found x and y to match the radius of given circle for each point
            bend_delta_x = center_of_circle_x - (radius * cos_x)
            bend_delta_y = radius * sin_x

        #
        bend_deltas = om.MVector(
            bend_delta_x - point_world.x,
            bend_delta_y - point_world.y,
            bend_delta_z,
        )
        return bend_deltas * envelopeValue * weight


def nodeCreator():
    return mpx.asMPxPtr(squish())


def nodeInitializer():
    # attribute function sets
    nAttr = om.MFnNumericAttribute()
    matAttr = om.MFnMatrixAttribute()

    # handle matrix
    squish.matrix = matAttr.create('matrix', 'matrix', 1)
    matAttr.default = om.MMatrix()
    matAttr.setStorable(True)
    matAttr.setWritable(True)

    # stretch
    squish.stretch = nAttr.create('stretch', 'stretch', om.MFnNumericData.kFloat, 0.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setMin(-0.99)

    # volume multiplier
    squish.volume = nAttr.create('volume', 'volume', om.MFnNumericData.kFloat, 1.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setMin(0.0)

    # bendX
    squish.bendX = nAttr.create('bendX', 'bendX', om.MFnNumericData.kFloat, 0.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    # add attrs
    squish.addAttribute(squish.matrix)
    squish.addAttribute(squish.stretch)
    squish.addAttribute(squish.volume)
    squish.addAttribute(squish.bendX)

    # design circuitary
    squish.attributeAffects(squish.matrix, kOutputGeom)
    squish.attributeAffects(squish.stretch, kOutputGeom)
    squish.attributeAffects(squish.volume, kOutputGeom)
    squish.attributeAffects(squish.bendX, kOutputGeom)

    # make deformer paintable
    om.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer squish weights;")


def initializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer, mpx.MPxNode.kDeformerNode)


def uninitializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj)
    plugin.deregisterNode(nodeId)


def main():
    pluginPath = __file__
    if mc.pluginInfo(nodeName, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)

    geo = mc.polyCube(height=2, subdivisionsHeight=10)[0]

    dfmN = mc.deformer(geo, type=nodeName)[0]


    # mc.setAttr(dfmN + '.stretch', 2)
    mc.setAttr(dfmN + '.bendX', 90)

    loc = mc.spaceLocator()[0]
    mc.connectAttr(loc + '.matrix', dfmN + '.matrix')
    mc.move(0, -0.01, 0, loc)
    # mc.rotate(0, 45, 20, loc)
    mc.scale(1, 1, 1, loc)
