import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'ehm_sinNode'
nodeID = OpenMaya.MTypeId(0x0011E185)


# node definition
class ehm_sinNode(OpenMayaMPx.MPxNode):
    input = OpenMaya.MObject()
    output = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if (plug == ehm_sinNode.output):
            dataHandle = dataBlock.inputValue(ehm_sinNode.input)

            inputFloat = dataHandle.asFloat()
            result = math.sin(inputFloat)

            outputHandle = dataBlock.outputValue(ehm_sinNode.output)
            outputHandle.setFloat(result)

            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_sinNode())


def nodeInitializer():
    # input
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_sinNode.input = nAttr.create('input', 'in', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    # output
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_sinNode.output = nAttr.create('output', 'out', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    # add attributes
    ehm_sinNode.addAttribute(ehm_sinNode.input)
    ehm_sinNode.addAttribute(ehm_sinNode.output)
    ehm_sinNode.attributeAffects(ehm_sinNode.input, ehm_sinNode.output)


# init plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('failed to load node: ehm_sinNode')
        raise


# uninit plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write('failed to unload plugin ehm_sinNode')
        raise
