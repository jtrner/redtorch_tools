import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys

nodeName = 'ehm_pushDeformer'
nodeId = om.MTypeId(0x0011E187)


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


class ehm_pushDeformer(mpx.MPxDeformerNode):

    def __init__(self):
        mpx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoItr, matrix, index):

        # get envelope
        envelopeHandle = dataBlock.inputValue(kEnvelope)
        envelopeValue = envelopeHandle.asFloat()
        if not envelopeValue:
            return

        # get Mesh
        inMesh = self.getDeformerInputGeometry(dataBlock, index)

        # pushValue
        pushHandle = dataBlock.inputValue(self.push)
        pushValue = pushHandle.asFloat()

        # using this we have complete control over geometry # use MFnMesh for faster results
        inmeshVertexItr = om.MItMeshVertex(inMesh)

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

            # set index for vertex iterator
            inmeshVertexItr.setIndex(idx, indexPtr)

            # get orig position
            pointPosition = origPoses[idx]

            # get normal
            normal_util = om.MScriptUtil()
            normal_util.createFromList([0, 0, 0], 3)
            normal = om.MVector(normal_util.asDoublePtr())
            inmeshVertexItr.getNormal(normal, om.MSpace.kObject)

            # consider ENVELOPE and WEIGHTS
            pushAmount = normal * pushValue * envelopeValue * weight

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
    return mpx.asMPxPtr(ehm_pushDeformer())


def nodeInitializer():
    # add attribute function set
    nAttr = om.MFnNumericAttribute()

    # input
    ehm_pushDeformer.push = nAttr.create('push', 'pu', om.MFnNumericData.kFloat, 0.0)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    # add attributes
    ehm_pushDeformer.addAttribute(ehm_pushDeformer.push)

    # design circuitary
    ehm_pushDeformer.attributeAffects(ehm_pushDeformer.push, kOutputGeom)

    # make deformer paintable
    om.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ehm_pushDeformer weights;")


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

    sphere = mc.polySphere()[0]
    sphere2 = mc.polySphere()[0]
    dfmN = mc.deformer(sphere, sphere2, type=nodeName)[0]
    mc.setAttr(dfmN+'.push', 2)

    """
    import sys
    path = 'D:/all_works/redtorch_tools/src/rt_tools/maya/plugin/scripted'
    if path not in sys.path:
        sys.path.insert(0, path)
    
    import ehm_pushDeformer
    reload(ehm_pushDeformer)
    
    
    ehm_pushDeformer.main()
    """
