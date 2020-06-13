import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys
import math

nodeName = 'ehm_flattenDeformer'
nodeId = om.MTypeId(0x0011E182)


class ehm_flattenDeformer(mpx.MPxDeformerNode):
    colliderMatrix = om.MObject()
    falloff = om.MObject()
    offset = om.MObject()
    bulge = om.MObject()

    def __init__(self):
        mpx.MPxDeformerNode.__init__(self)

    def remap(self, value, low1, high1, low2, high2):
        if (high1 - low1) == 0.0:
            return 0.0
        else:
            answer = low2 + (value - low1) * (high2 - low2) / (high1 - low1)
            if answer > high2:
                return high2
            elif answer < low1:
                return low1
            else:
                return answer

    def abs(self, value):
        if value < 0:
            return -value
        else:
            return value

    def clamp(self, value, low, high):
        if value < low:
            return low
        elif value > high:
            return high
        else:
            return value

    def removeScale(self, matrix):
        # removes the scale from the matrix

        normalizedMatrix_values = []

        x1 = matrix(0, 0)
        x2 = matrix(0, 1)
        x3 = matrix(0, 2)
        x = math.sqrt((x1 * x1) + (x2 * x2) + (x3 * x3))

        y1 = matrix(1, 0)
        y2 = matrix(1, 1)
        y3 = matrix(1, 2)
        y = math.sqrt((y1 * y1) + (y2 * y2) + (y3 * y3))

        z1 = matrix(2, 0)
        z2 = matrix(2, 1)
        z3 = matrix(2, 2)
        z = math.sqrt((z1 * z1) + (z2 * z2) + (z3 * z3))

        normalizedMatrix_values.append(matrix(0, 0) / x)
        normalizedMatrix_values.append(matrix(0, 1) / x)
        normalizedMatrix_values.append(matrix(0, 2) / x)
        normalizedMatrix_values.append(matrix(0, 3))

        normalizedMatrix_values.append(matrix(1, 0) / y)
        normalizedMatrix_values.append(matrix(1, 1) / y)
        normalizedMatrix_values.append(matrix(1, 2) / y)
        normalizedMatrix_values.append(matrix(1, 3))

        normalizedMatrix_values.append(matrix(2, 0) / z)
        normalizedMatrix_values.append(matrix(2, 1) / z)
        normalizedMatrix_values.append(matrix(2, 2) / z)
        normalizedMatrix_values.append(matrix(2, 3))

        normalizedMatrix_values.append(matrix(3, 0))
        normalizedMatrix_values.append(matrix(3, 1))
        normalizedMatrix_values.append(matrix(3, 2))
        normalizedMatrix_values.append(matrix(3, 3))

        normalizedMatrix = om.MMatrix()
        om.MScriptUtil.createMatrixFromList(normalizedMatrix_values, normalizedMatrix)

        return normalizedMatrix

    def deform(self, block, geoItr, matrix, geoIndex):

        # envelope
        envelope = mpx.cvar.MPxDeformerNode_envelope
        envelopeHandle = block.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()

        if not envelopeValue:
            return None

        # 0. get deformer input
        input = mpx.cvar.MPxDeformerNode_input

        # 1. Attach a handle to input Array Attribute.
        inputHandle_array = block.outputArrayValue(input)

        # 2. Jump to particular element
        inputHandle_array.jumpToElement(geoIndex)

        # 3. Attach a handle to specific data block
        inputHandle_element = inputHandle_array.outputValue()

        # 4. Reach to the child - inputGeom
        inputGeom = mpx.cvar.MPxDeformerNode_inputGeom
        inMeshHandle = inputHandle_element.child(inputGeom)

        # 5. get Mesh
        inMesh = inMeshHandle.asMesh()

        # get Envelope
        envelope = mpx.cvar.MPxDeformerNode_envelope
        envelopeHandle = block.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()

        # get colliderMatrix
        colliderMatrixHandle = block.inputValue(self.colliderMatrix)
        colliderMatrixValue = colliderMatrixHandle.asMatrix()

        # get rid of colliderMatrix's scale
        colliderMatrixValue = self.removeScale(colliderMatrixValue)

        # get falloff
        falloffHandle = block.inputValue(self.falloff)
        falloffValue = falloffHandle.asFloat()

        # get offset
        offsetHandle = block.inputValue(self.offset)
        offsetValue = offsetHandle.asFloat()

        # get bulge
        bulgeHandle = block.inputValue(self.bulge)
        bulgeValue = bulgeHandle.asFloat()

        inmeshVertexItr = om.MItMeshVertex(
            inMesh)  # using this we have complete control over geometry.  getConnectedVertices()
        # meshFn = om.MFnMesh( inMesh ) # using this we can get and set all point positions in one step

        # deform
        while not geoItr.isDone():

            vertexIndex = geoItr.index()
            # weight
            weight = self.weightValue(block, geoIndex, vertexIndex)

            if weight:
                origPointPosition_wall = geoItr.position() * matrix * colliderMatrixValue.inverse()
                # origPointPosition_wall.y -= offsetValue

                if origPointPosition_wall.y < offsetValue + falloffValue:  # if point passes the collider

                    falloffValue = self.abs(falloffValue)  # ignore negative falloff
                    # multiplyer = self.clamp( origPointPosition_wall.y, 0.0, origPointPosition_wall.y ) # ignore negative origPointPosition_wall.y
                    multiplyer = self.remap(origPointPosition_wall.y, 0.0, falloffValue + offsetValue, 0.0, 1.0)

                    # ---------- calculate bulge --------------
                    # get normal
                    normal_util = om.MScriptUtil()
                    normal_util.createFromList([1.0, 1.0, 1.0], 3)
                    normal = om.MVector(normal_util.asDoublePtr())
                    # vertexIndex = geoItr.index()

                    index_util = om.MScriptUtil()
                    index_util.createFromInt(0)
                    indexPtr = index_util.asIntPtr()
                    # normal in local space
                    inmeshVertexItr.setIndex(vertexIndex, indexPtr)
                    inmeshVertexItr.getNormal(normal, om.MSpace.kObject)

                    # normal in world space
                    normal_inWallSpace = normal * matrix * colliderMatrixValue.inverse()

                    bulge = normal_inWallSpace * bulgeValue * envelopeValue * weight * (1 - multiplyer);
                    origPointPosition_wall += bulge

                    # do the real job
                    if (
                            origPointPosition_wall.y < offsetValue):  # if after bulge, point passes the collider, push it back in
                        origPoint_offset_dist = origPointPosition_wall.y - offsetValue
                        origPointPosition_wall.y -= (origPoint_offset_dist * envelopeValue * weight)
                    xPos = origPointPosition_wall.x
                    yPos = origPointPosition_wall.y
                    zPos = origPointPosition_wall.z

                    pointPosition_wall = om.MPoint(xPos, yPos, zPos);  # new point position in world space
                    pointPosition_local = pointPosition_wall * colliderMatrixValue * matrix.inverse()  # new point position in local space

                    geoItr.setPosition(pointPosition_local)

            geoItr.next()


def nodeCreator():
    return mpx.asMPxPtr(ehm_flattenDeformer())


def nodeInitializer():
    # ----------------add attribute function set
    # collider matrix Fn
    matrixFn = om.MFnMatrixAttribute()
    # falloff Fn
    numericFn = om.MFnNumericAttribute()

    # ----------------create attributes
    # collider matrix
    ehm_flattenDeformer.colliderMatrix = matrixFn.create('colliderMatrix', 'cm', om.MFnMatrixAttribute.kDouble)
    matrixFn.setReadable(1)
    matrixFn.setWritable(1)
    matrixFn.setStorable(1)
    matrixFn.setKeyable(1)
    # falloff
    ehm_flattenDeformer.falloff = numericFn.create('falloff', 'fo', om.MFnNumericData.kFloat, 0.0)
    numericFn.setReadable(1)
    numericFn.setWritable(1)
    numericFn.setStorable(1)
    numericFn.setKeyable(1)
    # offset
    ehm_flattenDeformer.offset = numericFn.create('offset', 'of', om.MFnNumericData.kFloat, 0.0)
    numericFn.setReadable(1)
    numericFn.setWritable(1)
    numericFn.setStorable(1)
    numericFn.setKeyable(1)
    # bulge
    ehm_flattenDeformer.bulge = numericFn.create('bulge', 'b', om.MFnNumericData.kFloat, 0.0)
    numericFn.setReadable(1)
    numericFn.setWritable(1)
    numericFn.setStorable(1)
    numericFn.setKeyable(1)

    # ---------------- add attributes
    # collider matrix
    ehm_flattenDeformer.addAttribute(ehm_flattenDeformer.colliderMatrix)
    # falloff
    ehm_flattenDeformer.addAttribute(ehm_flattenDeformer.falloff)
    # offset
    ehm_flattenDeformer.addAttribute(ehm_flattenDeformer.offset)
    # bulge
    ehm_flattenDeformer.addAttribute(ehm_flattenDeformer.bulge)

    # ---------------- design circuitary
    outputGeom = mpx.cvar.MPxDeformerNode_outputGeom
    # collider matrix
    ehm_flattenDeformer.attributeAffects(ehm_flattenDeformer.colliderMatrix, outputGeom)
    # falloff
    ehm_flattenDeformer.attributeAffects(ehm_flattenDeformer.falloff, outputGeom)
    # offset
    ehm_flattenDeformer.attributeAffects(ehm_flattenDeformer.offset, outputGeom)
    # bulge
    ehm_flattenDeformer.attributeAffects(ehm_flattenDeformer.bulge, outputGeom)

    # ---------------- make deformer paintable
    om.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ehm_flattenDeformer weights;")


def initializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer, mpx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write('Faild to load plugin: %s' % nodeName)


def uninitializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Faild to unload plugin: %s' % nodeName)
