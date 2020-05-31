import maya.cmds as mc
import sys
from math import exp

import numpy as np
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

nodeName = "cageDeformer"
nodeId = OpenMaya.MTypeId(0x102fff)


# Some global variables were moved from MPxDeformerNode to MPxGeometryFilter.
# Set some constants to the proper C++ cvars based on the API version.
kApiVersion = mc.about(apiVersion=True)
if kApiVersion < 201600:
    kInput = OpenMayaMPx.cvar.MPxDeformerNode_input
    kInputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
    kOutputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    kEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
else:
    kInput = OpenMayaMPx.cvar.MPxGeometryFilter_input
    kInputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
    kOutputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom
    kEnvelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope


class Cage(OpenMayaMPx.MPxDeformerNode):
    """
    http://www.djx.com.au/blog/2015/03/09/barycentric-coordinates-part-2/
    """

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIt, matrix, geometryIndex):
        input = OpenMayaMPx.cvar.MPxDeformerNode_input
        dataHandleInputArray = dataBlock.outputArrayValue(input)
        dataHandleInputArray.jumpToElement(geometryIndex)
        dataHandleInputElement = dataHandleInputArray.outputValue()
        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        mDstMesh = dataHandleInputGeom.asMesh()

        inEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        dataHandleEnvelope = dataBlock.inputValue(inEnvelope)
        envelope = dataHandleEnvelope.asFloat()

        # ------------ get the cage ------------
        hSrcMesh = dataBlock.inputValue(Cage.aSrcMesh)
        mSrcMesh = hSrcMesh.asMesh()
        if mSrcMesh.isNull(): return

        fnSrcMesh = OpenMaya.MFnMesh(mSrcMesh)
        srcMeshPointArray = OpenMaya.MPointArray()
        fnSrcMesh.getPoints(srcMeshPointArray, OpenMaya.MSpace.kWorld)

        matrix = hSrcMesh.geometryTransformMatrix()

        currentFace = OpenMaya.MItMeshPolygon(mSrcMesh)  # , comp)

        # ------------ get the base cage ------------ 
        mBaseSrcMesh = dataBlock.inputValue(Cage.aBaseSrcMesh).asMesh()
        if mBaseSrcMesh.isNull(): return
        fnBaseSrcMesh = OpenMaya.MFnMesh(mBaseSrcMesh)
        baseSrcMeshPointArray = OpenMaya.MPointArray()
        fnBaseSrcMesh.getPoints(baseSrcMeshPointArray, OpenMaya.MSpace.kWorld)

        outputListPos = OpenMaya.MPointArray()

        # RBF preparation
        self.poses = []
        for i in xrange(baseSrcMeshPointArray.length()):
            self.poses.append([baseSrcMeshPointArray[i].x, baseSrcMeshPointArray[i].y, baseSrcMeshPointArray[i].z])
        self.poses = np.array(self.poses)
        sigma = 1
        numberOfPoses = len(self.poses)

        transformVectors = [srcMeshPointArray[i] - baseSrcMeshPointArray[i] for i in xrange(numberOfPoses)]

        while not geoIt.isDone():

            currentPos = geoIt.position()
            point = geoIt.position()
            f = []  # array of the gaussian dist between the point and the n-th pose

            for i in xrange(numberOfPoses):
                pose = self.poses[i]
                distance = self.getDist(pose, point)
                gaussian = exp(-pow(distance * sigma, 2))
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

            # normalization
            total = sum(poseWeights)
            for i in range(len(poseWeights)):
                poseWeights[i] = poseWeights[i] / total

            for i in xrange(numberOfPoses):
                currentPos += transformVectors[i] * poseWeights[i]

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

    Cage.aSrcMesh = tAttr.create("sourceMesh", "srcMsh", OpenMaya.MFnData.kMesh)
    Cage.addAttribute(Cage.aSrcMesh)

    Cage.aBaseSrcMesh = tAttr.create("baseSourceMesh", "baseSrcMsh", OpenMaya.MFnData.kMesh)
    Cage.addAttribute(Cage.aBaseSrcMesh)

    Cage.aInputMatrix = mAttr.create("inputMatrix", "inMtx")
    Cage.addAttribute(Cage.aInputMatrix)

    """
    SWIG - Simplified Wrapper Interface Generator 
    """
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    Cage.attributeAffects(Cage.aSrcMesh, outputGeom)
    Cage.attributeAffects(Cage.aBaseSrcMesh, outputGeom)
    Cage.attributeAffects(Cage.aInputMatrix, outputGeom)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "fruity", "1.0")
    try:
        mplugin.registerNode(nodeName,
                             nodeId,
                             deformerCreator,
                             nodeInitializer,
                             OpenMayaMPx.MPxNode.kDeformerNode)
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
if mc.pluginInfo("ehm_volumeDeformer", q=True, loaded=True):
    mc.unloadPlugin("ehm_volumeDeformer", f=True)


mc.loadPlugin( "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin\\ehm_plugins\\scriptedPlugin\\ehm_volumeDeformer\ehm_volumeDeformer.py" )

base = mc.polyCube(ch=False, w=2, h=2, d=2)[0]
mc.hide( base )
driver = mc.polyCube(ch=False, w=2, h=2, d=2)[0]
driven = mc.polySphere(ch=False)[0]

volumeDeformer = mc.deformer(driven, type="cageDeformer")[0]
mc.connectAttr(base+".outMesh", volumeDeformer+".baseSourceMesh")
mc.connectAttr(driver+".outMesh", volumeDeformer+".sourceMesh")

"""
