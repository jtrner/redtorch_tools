import sys
path = "F:\\softwares\\numpy.1.9.2"
if path not in sys.path:
    sys.path.append( path )

import sys
import numpy as np
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
from math import exp



nodeName= "cageDeformer"
nodeId = OpenMaya.MTypeId(0x102fff)

class Cage(OpenMayaMPx.MPxDeformerNode):
    """
    http://www.djx.com.au/blog/2015/03/09/barycentric-coordinates-part-2/
    """
    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)
    
    def deform(self, dataBlock, geoIt, matrix, geometryIndex):    



        input = OpenMayaMPx.cvar.MPxDeformerNode_input
        # 1. Attach a handle to input Array Attribute.
        dataHandleInputArray = dataBlock.outputArrayValue(input)
        # 2. Jump to particular element
        dataHandleInputArray.jumpToElement(geometryIndex)
        # 3. Attach a handle to specific data block
        dataHandleInputElement = dataHandleInputArray.outputValue()
        # 4. Reach to the child - inputGeom     
        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        mDstMesh = dataHandleInputGeom.asMesh()

        inEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        dataHandleEnvelope = dataBlock.inputValue(inEnvelope)
        envelope = dataHandleEnvelope.asFloat()

        # ------------ get the cage ------------
        # oSrcMesh = dataBlock.inputValue(Cage.aSrcMesh).asMesh()
        hSrcMesh = dataBlock.inputValue(Cage.aSrcMesh)
        mSrcMesh = hSrcMesh.asMesh()
        if mSrcMesh.isNull():return
        # create a function set to get all the positions
        fnSrcMesh = OpenMaya.MFnMesh(mSrcMesh)
        srcMeshPointArray = OpenMaya.MPointArray()
        fnSrcMesh.getPoints(srcMeshPointArray, OpenMaya.MSpace.kWorld)
        # get the dag path of the cage
        matrix = hSrcMesh.geometryTransformMatrix()
        
        # comp = OpenMaya.MObject()
        currentFace = OpenMaya.MItMeshPolygon(mSrcMesh)#, comp)
 
        # ------------ get the base cage ------------ 
        mBaseSrcMesh = dataBlock.inputValue(Cage.aBaseSrcMesh).asMesh()
        if mBaseSrcMesh.isNull():return
        fnBaseSrcMesh = OpenMaya.MFnMesh(mBaseSrcMesh)
        baseSrcMeshPointArray = OpenMaya.MPointArray()
        fnBaseSrcMesh.getPoints(baseSrcMeshPointArray, OpenMaya.MSpace.kWorld)

        # ------------ get the matrix ------------ 
        # mMatrix = dataBlock.inputValue(Cage.aInputMatrix).asMatrix()
        # if not mMatrix:return

        # ------------ create the mesh intersector ------------
        # matrix = srcDagPath.inclusiveMatrix()
        intersector = OpenMaya.MMeshIntersector()
        intersector.create(mSrcMesh, matrix)

        # create variables to store the returned data
        pointInfo = OpenMaya.MPointOnMesh()
        uUtil = OpenMaya.MScriptUtil(0.0)
        uPtr = uUtil.asFloatPtr()
        vUtil = OpenMaya.MScriptUtil(0.0)
        vPtr = vUtil.asFloatPtr()
        pointArray = OpenMaya.MPointArray()
        vertIdList = OpenMaya.MIntArray()

        dummy = OpenMaya.MScriptUtil()
        dummyIntPtr = dummy.asIntPtr()

        outputListPos = OpenMaya.MPointArray()


        # RBF preparation
        self.poses = []
        # baseSrcMeshPos = OpenMaya.MPointArray()
        # fnBaseSrcMesh.getPoints(baseSrcMeshPos)
        for i in xrange(baseSrcMeshPointArray.length()):
            self.poses.append([baseSrcMeshPointArray[i].x, baseSrcMeshPointArray[i].y, baseSrcMeshPointArray[i].z])
        self.poses = np.array(self.poses)
        sigma = 1
        numberOfPoses = len(self.poses)
        numberOfDimensions = 3

        mat = [[None]*numberOfPoses]*numberOfPoses
        transformVectors = [srcMeshPointArray[i] - baseSrcMeshPointArray[i] for i in xrange(numberOfPoses)]

        while( not geoIt.isDone()):

            currentPos = geoIt.position()              
            # RBF interpolation
            point = geoIt.position()
            f = [] # array of the gaussian dist between the point and the n-th pose
            
            for i in xrange(numberOfPoses):
                pose = self.poses[i]
                distance = self.getDist(pose, point)
                gaussian = exp(-pow(distance*sigma, 2))
                f.append(gaussian)

            ii = []
            for i in xrange(numberOfPoses):
                jj = []
                posei = self.poses[i]
                for j in xrange(numberOfPoses):
                    posej = self.poses[j]
                    dist = self.getDist(posei, posej)
                    gaussian = exp(-pow(dist, 2))
                    jj.append(gaussian)
                ii.append(jj)
            MM = np.array(ii)
            poseWeights = np.linalg.solve(MM, f)
            
            """
            if geoIt.index() == 4:
                print 'poseWeights :'
                for p in poseWeights:print p
            """

            # normalization
            total = sum(poseWeights)
            for i in range(len(poseWeights)):
                poseWeights[i] = poseWeights[i] / total
            
            """
            if geoIt.index() == 4:
                print 'normalized pw :'
                for p in poseWeights:print p
            """

            for i in xrange(numberOfPoses):
                currentPos += transformVectors[i] * poseWeights[i]

            
            # linear interpolation
            """
            # get the closest point between current vertex and baseSrcMesh
            closestPointOnBaseMesh = OpenMaya.MPoint()
            polygonUtil = OpenMaya.MScriptUtil(0.0)
            polygonPtr = polygonUtil.asIntPtr()
            fnBaseSrcMesh.getClosestPoint(currentPos, closestPointOnBaseMesh, OpenMaya.MSpace.kWorld, polygonPtr)
            # get the UVs coord of this point
            util = OpenMaya.MScriptUtil(0.0)
            utilPtr = util.asFloat2Ptr()
            fnBaseSrcMesh.getUVAtPoint(closestPointOnBaseMesh, utilPtr)
            # get the corresponding point on the srcMesh
            closestPointOnMesh = OpenMaya.MPoint()
            polygonId = polygonUtil.getInt(polygonPtr)
            fnSrcMesh.getPointAtUV(polygonId, closestPointOnMesh, utilPtr, OpenMaya.MSpace.kWorld)
            # calculate vector between baseSrcMesh and srcMesh
            vDelta = closestPointOnMesh - closestPointOnBaseMesh
            # apply it to the target
            currentPos += vDelta
            """

            outputListPos.append(currentPos)

            geoIt.next()

        geoIt.setAllPositions(outputListPos)
    def getDist(self, a, b):
        s = 0
        for i in xrange(3):
            s += pow(a[i] - b[i], 2)
        return pow(s, .5)

def deformerCreator():
    nodePtr = OpenMayaMPx.asMPxPtr(Cage())
    return nodePtr

def nodeInitializer():  
    """
    """
    tAttr = OpenMaya.MFnTypedAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()

    Cage.aSrcMesh= tAttr.create("sourceMesh", "srcMsh", OpenMaya.MFnData.kMesh)
    Cage.addAttribute(Cage.aSrcMesh)

    Cage.aBaseSrcMesh = tAttr.create("baseSourceMesh", "baseSrcMsh", OpenMaya.MFnData.kMesh)
    Cage.addAttribute(Cage.aBaseSrcMesh)

    Cage.aInputMatrix = mAttr.create("inputMatrix", "inMtx")
    Cage.addAttribute(Cage.aInputMatrix)

    """
    SWIG - Simplified Wrapper Interface Generator 
    """
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom 
    Cage.attributeAffects(Cage.aSrcMesh,outputGeom )
    Cage.attributeAffects(Cage.aBaseSrcMesh, outputGeom)
    Cage.attributeAffects(Cage.aInputMatrix, outputGeom)

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject,"fruity","1.0")
    try:
        mplugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer,OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: %s" % nodeName)
        raise

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % nodeName)
        raise


"""
mc.file(new=True, f=True)
if mc.pluginInfo("cageDeformer", q=True, loaded=True):
    mc.unloadPlugin("cageDeformer", f=True)


mc.loadPlugin( "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin\\third_party\\cageDeformer.py" )

base = mc.polyCube(ch=False)[0]
mc.hide( base )
driver = mc.polyCube(ch=False)[0]
driven = mc.polySphere(ch=False)[0]

volumeDeformer = mc.deformer(driven, type="cageDeformer")[0]
mc.connectAttr(base+".outMesh", volumeDeformer+".baseSourceMesh")
mc.connectAttr(driver+".outMesh", volumeDeformer+".sourceMesh")

"""
