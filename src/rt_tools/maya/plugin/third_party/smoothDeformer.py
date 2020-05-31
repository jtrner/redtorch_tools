import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

nodeName = 'fSmoothDeformer'
nodeId = OpenMaya.MTypeId(0x192fff)

class FSmooth(OpenMayaMPx.MPxDeformerNode):
    # get attrs back
    mIter = OpenMaya.MObject()
    mPreserve = OpenMaya.MObject()
    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geometryIndex):

        input = OpenMayaMPx.cvar.MPxDeformerNode_input
        # 1. Attach a handle to the input
        dataHandleInputArray = dataBlock.inputArrayValue(input)
        # 2. Jump to particular element
        dataHandleInputArray.jumpToElement(geometryIndex)
        # 3. Attach a handle specific data block
        dataHandleInputElement = dataHandleInputArray.inputValue()
        # 4. Reach the child 
        inputGeo = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        dataHandleInputGeo = dataHandleInputElement.child(inputGeo)
        inMesh = dataHandleInputGeo.asMesh()


        inEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        dataHandleEnvelope = dataBlock.inputValue(inEnvelope)
        envelope = dataHandleEnvelope.asFloat()

        
        dataHandleIter = dataBlock.inputValue(FSmooth.mIter)
        _iter = dataHandleIter.asInt()

        dataHandlePreserve = dataBlock.inputValue(FSmooth.mPreserve)
        preserve = dataHandlePreserve.asFloat()


        

        vtxIter = OpenMaya.MItMeshVertex(inMesh)


        fnMesh = OpenMaya.MFnMesh(inMesh)
        outputListPos = OpenMaya.MPointArray()
        previousIterationPositions = OpenMaya.MPointArray()
        basePt = OpenMaya.MPoint()
        
        for i in range(_iter):
        
            vtxIter.reset()
            # if it's the first iteration, we initialize the previousIter list with the real positions
            if i == 0:
                fnMesh.getPoints(previousIterationPositions)
            else:
                previousIterationPositions = outputListPos

            
            while not vtxIter.isDone():
                # 1. get all adjacent vertices
                connectedVertices = OpenMaya.MIntArray()
                vtxIter.getConnectedVertices(connectedVertices)
                # 2. calculate the centroid of all vertices
                xValue, yValue, zValue = 0., 0., 0.
                for vtx in connectedVertices:
                    # vtxPos = OpenMaya.MPoint()
                    # fnMesh.getPoint(vtx, vtxPos)
                    vtxPos = previousIterationPositions[vtx]
                    xValue += vtxPos.x
                    yValue += vtxPos.y
                    zValue += vtxPos.z
                nbVtx = connectedVertices.length()
                
                # 3. get the previous vertex position
                # fnMesh.getPoint(vtxIter.index(), basePt)
                basePt = previousIterationPositions[vtxIter.index()]

                # 4. calculate the mean
                avgX = xValue / nbVtx
                avgY = yValue / nbVtx
                avgZ = zValue / nbVtx

                # 5. calculate the new position
                newPosX = ( ( ( avgX + basePt.x) / 2 ) * envelope ) - (basePt.x * (envelope-1))
                newPosY = ( ( ( avgY + basePt.y) / 2 ) * envelope ) - (basePt.y * (envelope-1))
                newPosZ = ( ( ( avgZ + basePt.z) / 2 ) * envelope ) - (basePt.z * (envelope-1))

                avgPt = OpenMaya.MPoint(newPosX, newPosY, newPosZ)

                # ========================================================
                # preserve volume (ca marche, mais seulement avec un base mesh. Sinon, ca revient a mettre l'enveloppe a 0)
                # vPreserveVolume = basePt - avgPt
                # avgPt += vPreserveVolume * preserve
                # ========================================================

                # stores the new position in a list
                if i == 0:
                    outputListPos.append(avgPt)
                else:
                    outputListPos.set(avgPt, vtxIter.index())
                # newPositions.set(avgPt, vtxIter.index())
                # newPositions[vtxIter.index()] = avgPt
                vtxIter.next()

            # previousIterationPositions = newPositions
        
        geoIterator.setAllPositions(outputListPos)


def deformerCreator():
    nodePtr = OpenMayaMPx.asMPxPtr(FSmooth())
    return nodePtr

def nodeInitializer():
    
    mFnAttr = OpenMaya.MFnNumericAttribute()
    
    FSmooth.mIter= mFnAttr.create('iterations', 'iter', OpenMaya.MFnNumericData.kInt, 1)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(1)
    
    FSmooth.addAttribute(FSmooth.mIter)

    FSmooth.mPreserve= mFnAttr.create('preserveVolume', 'preserve', OpenMaya.MFnNumericData.kFloat, 1.)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(0)
    mFnAttr.setMax(1)
    
    FSmooth.addAttribute(FSmooth.mPreserve)

    outputGeo = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    FSmooth.attributeAffects(FSmooth.mIter, outputGeo)
    FSmooth.attributeAffects(FSmooth.mPreserve, outputGeo)

def initializePlugin(mobject):
    mPlugin = OpenMayaMPx.MFnPlugin(mobject, 'fruity', '1.0')
    try:
        mPlugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write('Failed to register node : %s' %nodeName)
        raise
def uninitializePlugin(mobject):
    mPlugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mPlugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Failed to deregister node : %s' %nodeName )
        raise