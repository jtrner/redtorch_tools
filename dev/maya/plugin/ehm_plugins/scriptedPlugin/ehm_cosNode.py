import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'ehm_cosNode'
nodeID = OpenMaya.MTypeId(0x0011E184)


# node definition
class ehm_cosNode(OpenMayaMPx.MPxNode):
    input = OpenMaya.MObject()
    output = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == ehm_cosNode.output:
            dataHandle = dataBlock.inputValue(ehm_cosNode.input)

            inputFloat = dataHandle.asFloat()
            result = math.cos(inputFloat)

            outputHandle = dataBlock.outputValue(ehm_cosNode.output)
            outputHandle.setFloat(result)

            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_cosNode())


def nodeInitializer():
    # input
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_cosNode.input = nAttr.create('input', 'in', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    # output
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_cosNode.output = nAttr.create('output', 'out', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    # add attributes
    ehm_cosNode.addAttribute(ehm_cosNode.input)
    ehm_cosNode.addAttribute(ehm_cosNode.output)
    ehm_cosNode.attributeAffects(ehm_cosNode.input, ehm_cosNode.output)


# init plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('failed to load node: ehm_cosNode')
        raise


# uninit plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write('failed to unload plugin ehm_cosNode')
        raise
