# bug // Error: UnboundLocalError: local variable 'averagedPoses' referenced before assignment // 


import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

pluginName = 'ehm_smoothDeformer'
pluginId = OpenMaya.MTypeId(0x0011E183)


class ehm_smoothDeformer(OpenMayaMPx.MPxDeformerNode):
    aIteration = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, data, itGeo, localToWorldMatrix, geomIndex):

        # envelope
        envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        envelopeHandle = data.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()

        if not envelopeValue:
            return None

        # aIteration
        aIterationHandle = data.inputValue(self.aIteration)
        iteration = aIterationHandle.asShort()

        # 0. get deformer input
        input = OpenMayaMPx.cvar.MPxDeformerNode_input

        # 1. Attach a handle to input Array Attribute.
        inputHandle_array = data.outputArrayValue(input)

        # 2. Jump to particular element
        inputHandle_array.jumpToElement(geomIndex)

        # 3. get value of current element
        inputValue_element = inputHandle_array.outputValue()

        # 4. Reach to the child - inputGeom
        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        OInputGeomHandle = inputValue_element.child(inputGeom)

        # 5. get Mesh
        OInputGeom = OInputGeomHandle.asMesh()

        itVtx = OpenMaya.MItMeshVertex(
            OInputGeom)  # using this we can find connected vertices to our current vertex.  getConnectedVertices()

        origPoses = OpenMaya.MPointArray()  # original points' positions list
        itGeo.allPositions(origPoses, OpenMaya.MSpace.kObject)  # get original point positions

        averagedPoses = OpenMaya.MPointArray()  # list of average positions of all neighbour vertices'  positions

        for level in range(iteration):  # for each smooth iteration

            averagedPoses.clear()

            while not itVtx.isDone():  # calculate new position for each vertex

                currentVertIndex = itVtx.index()
                # weight
                w = self.wValue(data, geomIndex, currentVertIndex)

                if w:
                    currentPos = OpenMaya.MVector(origPoses[currentVertIndex])

                    connectedVertsIndices = OpenMaya.MIntArray()  # hold indices of neighbour vertices
                    itVtx.getConnectedVertices(
                        connectedVertsIndices)  # find indices of neighbour vertices

                    neighboursPoses = OpenMaya.MVector()
                    for i in xrange(
                            connectedVertsIndices.length()):  # get the average position from neighbour positions
                        neighboursPoses += OpenMaya.MVector(origPoses[connectedVertsIndices[i]])

                    # get the neighbour average position divide positions by [number of neighbours + 1(vertex itself) ] to 
                    averagedPos = (currentPos + neighboursPoses) / (connectedVertsIndices.length() + 1)

                    # consider ENVELOPE and wS value in calculations in 4 steps
                    moveAmount = averagedPos - currentPos
                    moveAmount *= envelopeValue
                    moveAmount *= w

                    # add move amount to default position to find the final position of the vertex
                    averagedPos = OpenMaya.MPoint(currentPos + moveAmount)

                else:  # if w is 0.0
                    averagedPos = origPoses[currentVertIndex]

                averagedPoses.append(averagedPos)  # add the averaged value to averageList

                itVtx.next()  # go to next vertex

            itVtx.reset()
            origPoses = OpenMaya.MPointArray(averagedPoses)  # use current positions as the original

        itGeo.setAllPositions(averagedPoses)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_smoothDeformer())


def nodeInitializer():
    # add attribute function set
    numericFn = OpenMaya.MFnNumericAttribute()

    # create attributes
    ehm_smoothDeformer.aIteration = numericFn.create('aIteration', 'si', OpenMaya.MFnNumericData.kShort, 1)
    numericFn.setReadable(1)
    numericFn.setWritable(1)
    numericFn.setStorable(1)
    numericFn.setKeyable(1)
    numericFn.setMin(1)

    # add attributes
    ehm_smoothDeformer.addAttribute(ehm_smoothDeformer.aIteration)

    # design circuitary
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    ehm_smoothDeformer.attributeAffects(ehm_smoothDeformer.aIteration, outputGeom)

    # make deformer paintable
    OpenMaya.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ehm_smoothDeformer ws;")


def initializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj, 'Ehsan HM', '1.1', 'any')
    try:
        plugin.registerNode(pluginName, pluginId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write('Load plugin failed: %s' % pluginName)


def uninitializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(pluginId)
    except:
        sys.stderr.write('Unload plugin failed: %s' % pluginName)
