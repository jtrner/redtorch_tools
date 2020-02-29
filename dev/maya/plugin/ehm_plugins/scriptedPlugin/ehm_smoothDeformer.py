# bug // Error: UnboundLocalError: local variable 'averagedPoses' referenced before assignment // 


import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

pluginName = 'ehm_smoothDeformer'
pluginId = OpenMaya.MTypeId(0x0011E183)


class ehm_smoothDeformer(OpenMayaMPx.MPxDeformerNode):
    smoothIteration = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, block, geoItr, matrix, GeoIndex):

        # envelope
        envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        envelopeHandle = block.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()

        if not envelopeValue:
            return None

        # smoothIteration
        smoothIterationHandle = block.inputValue(self.smoothIteration)
        smoothIterationValue = smoothIterationHandle.asShort()

        # 0. get deformer input
        input = OpenMayaMPx.cvar.MPxDeformerNode_input

        # 1. Attach a handle to input Array Attribute.
        inputHandle_array = block.outputArrayValue(input)

        # 2. Jump to particular element
        inputHandle_array.jumpToElement(GeoIndex)

        # 3. get value of current element
        inputValue_element = inputHandle_array.outputValue()

        # 4. Reach to the child - inputGeom
        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        inMeshHandle = inputValue_element.child(inputGeom)

        # 5. get Mesh
        inMesh = inMeshHandle.asMesh()

        inmeshVertexItr = OpenMaya.MItMeshVertex(
            inMesh)  # using this we can find connected vertices to our current vertex.  getConnectedVertices()

        origPoses = OpenMaya.MPointArray()  # original points' positions list
        geoItr.allPositions(origPoses, OpenMaya.MSpace.kObject)  # get original point positions

        averagedPoses = OpenMaya.MPointArray()  # list of average positions of all neighbour vertices'  positions

        for level in range(smoothIterationValue):  # for each smooth iteration

            averagedPoses.clear()

            while not inmeshVertexItr.isDone():  # calculate new position for each vertex

                currentVertIndex = inmeshVertexItr.index()
                # weight
                weight = self.weightValue(block, GeoIndex, currentVertIndex)

                if weight:
                    currentPos = OpenMaya.MVector(origPoses[currentVertIndex])

                    connectedVertsIndices = OpenMaya.MIntArray()  # hold indices of neighbour vertices
                    inmeshVertexItr.getConnectedVertices(
                        connectedVertsIndices)  # find indices of neighbour vertices

                    neighboursPoses = OpenMaya.MVector()
                    for i in xrange(
                            connectedVertsIndices.length()):  # get the average position from neighbour positions
                        neighboursPoses += OpenMaya.MVector(origPoses[connectedVertsIndices[i]])

                    # get the neighbour average position divide positions by [number of neighbours + 1(vertex itself) ] to 
                    neighboursaveragedPos = neighboursPoses / connectedVertsIndices.length()
                    averagedPos = (currentPos + neighboursaveragedPos) / 2

                    # consider ENVELOPE and WEIGHTS value in calculations in 4 steps
                    moveAmount = averagedPos - currentPos
                    moveAmount *= envelopeValue
                    moveAmount *= weight

                    # add move amount to default position to find the final position of the vertex
                    averagedPos = OpenMaya.MPoint(currentPos + moveAmount)

                else:  # if weight is 0.0
                    averagedPos = origPoses[currentVertIndex]

                averagedPoses.append(averagedPos)  # add the averaged value to averageList

                inmeshVertexItr.next()  # go to next vertex

            inmeshVertexItr.reset()
            origPoses = OpenMaya.MPointArray(averagedPoses)  # use current positions as the original

        geoItr.setAllPositions(averagedPoses)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_smoothDeformer())


def nodeInitializer():
    # add attribute function set
    numericFn = OpenMaya.MFnNumericAttribute()

    # create attributes
    ehm_smoothDeformer.smoothIteration = numericFn.create('smoothIteration', 'si', OpenMaya.MFnNumericData.kShort, 1)
    numericFn.setReadable(1)
    numericFn.setWritable(1)
    numericFn.setStorable(1)
    numericFn.setKeyable(1)
    numericFn.setMin(1)

    # add attributes
    ehm_smoothDeformer.addAttribute(ehm_smoothDeformer.smoothIteration)

    # design circuitary
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    ehm_smoothDeformer.attributeAffects(ehm_smoothDeformer.smoothIteration, outputGeom)

    # make deformer paintable
    OpenMaya.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ehm_smoothDeformer weights;")


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
