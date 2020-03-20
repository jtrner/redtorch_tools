import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys

nodeName = 'ballDeformer'
nodeId = om.MTypeId(0x0011E18E)


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


class ballDeformer(mpx.MPxDeformerNode):
    ballMatrix = om.MObject()
    push = om.MObject()
    radius = om.MObject()

    def __init__(self):
        mpx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoItr, matrix, index):

        # get envelope
        envelopeA = kEnvelope
        envelopeValue = dataBlock.inputValue(envelopeA).asFloat()
        if not envelopeValue:
            return

        # get Mesh
        inMesh = self.getDeformerInputGeometry(dataBlock, index)

        # pushValue
        pushHandle = dataBlock.inputValue(self.push)
        pushValue = pushHandle.asFloat()

        # radiusValue
        radiusHandle = dataBlock.inputValue(self.radius)
        radiusValue = radiusHandle.asFloat()

        # ballMatrixValue
        ballMatrixHandle = dataBlock.inputValue(self.ballMatrix)
        ballMatrixValue = pushHandle.asMatrix()

        ballPosV = om.MVector(ballMatrixValue(3, 1),
                              ballMatrixValue(3, 2),
                              ballMatrixValue(3, 3))

        # get original point positions
        origPoses = om.MPointArray()
        geoItr.allPositions(origPoses, om.MSpace.kObject)

        # deformed points
        finalPoses = om.MPointArray()

        # index 0 pointer
        index_util = om.MScriptUtil()
        index_util.createFromInt(index)
        indexPtr = index_util.asIntPtr()

        # deform
        while not geoItr.isDone():
            idx = geoItr.index()

            # weight
            weight = self.weightValue(dataBlock, index, idx)

            # get orig position
            pointPosition = origPoses[idx]

            # direction
            direction = om.MVector(pointPosition) - ballPosV


            # is inside sphere
            dist = direction.length()
            if dist > radiusValue:
                finalPoses.append(pointPosition)

            else:
                # consider ENVELOPE and WEIGHTS
                pushAmount = direction.normal() * pushValue * (radiusValue - dist) * envelopeValue * weight

                finalPos = pointPosition + pushAmount

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


def nodeCreator():
    return mpx.asMPxPtr(ballDeformer())


def nodeInitializer():
    # add push attr
    nAttr = om.MFnNumericAttribute()
    ballDeformer.push = nAttr.create('push', 'push', om.MFnNumericData.kFloat, 0.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    # add radius attr
    ballDeformer.radius = nAttr.create('radius', 'radius', om.MFnNumericData.kFloat, 1.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    # add matrix attr
    matAttr = om.MFnMatrixAttribute()
    ballDeformer.ballMatrix = matAttr.create('ballMatrix', 'ballMatrix', om.MFnMatrixAttribute.kDouble)
    matAttr.setReadable(1)
    matAttr.setWritable(1)
    matAttr.setStorable(1)
    matAttr.setKeyable(1)

    # add attributes
    ballDeformer.addAttribute(ballDeformer.push)
    ballDeformer.addAttribute(ballDeformer.radius)
    ballDeformer.addAttribute(ballDeformer.ballMatrix)

    # design circuitary
    ballDeformer.attributeAffects(ballDeformer.push, kOutputGeom)
    ballDeformer.attributeAffects(ballDeformer.radius, kOutputGeom)
    ballDeformer.attributeAffects(ballDeformer.ballMatrix, kOutputGeom)

    # make deformer paintable
    om.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ballDeformer weights;")


def initializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer, mpx.MPxNode.kDeformerNode)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))


def uninitializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj)
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

    plane = mc.polyPlane()[0]
    dfmN = mc.deformer(plane, type=nodeName)[0]
    mc.setAttr(dfmN+'.push', 0)

    loc = mc.spaceLocator()[0]
    mc.connectAttr(loc + '.worldMatrix[0]', dfmN + '.ballMatrix')

    sphere = mc.polySphere()[0]
    mc.parent(sphere, loc)
    mc.setAttr(sphere + '.template', 1)
    mc.connectAttr(loc + '.sx', dfmN + '.radius')


    """
    import sys
    path = os.path.join("D:/all_works/scratch")
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
    
    import ballDeformer
    reload(ballDeformer)    
    
    ballDeformer.main()
    """
