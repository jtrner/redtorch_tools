import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'ehm_dynamicChain2'
nodeID = OpenMaya.MTypeId(0x0011E187)


# node definition
class ehm_dynamicChain2(OpenMayaMPx.MPxNode):
    input = OpenMaya.MObject()
    timeOffset = OpenMaya.MObject()
    speed = OpenMaya.MObject()
    frequency = OpenMaya.MObject()
    output = OpenMaya.MObject()
    test = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == ehm_dynamicChain2.output:
            # get input
            dataHandle = dataBlock.inputValue(ehm_dynamicChain2.input)
            inputFloat = dataHandle.asFloat()

            # get timeOffset
            dataHandle = dataBlock.inputValue(ehm_dynamicChain2.timeOffset)
            timeOffsetFloat = dataHandle.asFloat()

            # get speed
            dataHandle = dataBlock.inputValue(ehm_dynamicChain2.speed)
            speedFloat = dataHandle.asFloat()

            # get frequency
            dataHandle = dataBlock.inputValue(ehm_dynamicChain2.frequency)
            frequencyFloat = dataHandle.asFloat()

            result = math.sin((inputFloat - timeOffsetFloat) * speedFloat) * frequencyFloat

            outputHandle = dataBlock.outputValue(ehm_dynamicChain2.output)
            outputHandle.setFloat(result)

            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_dynamicChain2())


def nodeInitializer():
    # input
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_dynamicChain2.input = nAttr.create('input', 'in', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)

    # timeOffset
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_dynamicChain2.timeOffset = nAttr.create('timeOffset', 'to', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)

    # speed
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_dynamicChain2.speed = nAttr.create('speed', 's', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)

    # frequency
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_dynamicChain2.frequency = nAttr.create('frequency', 'f', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)

    # output
    nAttr = OpenMaya.MFnNumericAttribute()
    ehm_dynamicChain2.output = nAttr.create('output', 'out', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    # test
    cmpAttr = OpenMaya.MFnCompoundAttribute()
    ehm_dynamicChain2.test = cmpAttr.create('test', 'te')
    cmpAttr.setArray(True)
    cmpAttr.addChild(ehm_dynamicChain2.input)
    cmpAttr.setKeyable(1)

    # add attributes
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.input)
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.timeOffset)
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.speed)
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.frequency)
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.output)
    ehm_dynamicChain2.addAttribute(ehm_dynamicChain2.test)

    # affect attributes
    ehm_dynamicChain2.attributeAffects(ehm_dynamicChain2.input, ehm_dynamicChain2.output)
    ehm_dynamicChain2.attributeAffects(ehm_dynamicChain2.timeOffset, ehm_dynamicChain2.output)
    ehm_dynamicChain2.attributeAffects(ehm_dynamicChain2.speed, ehm_dynamicChain2.output)
    ehm_dynamicChain2.attributeAffects(ehm_dynamicChain2.frequency, ehm_dynamicChain2.output)


# init plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('failed to load node: ehm_dynamicChain2')
        raise


# uninit plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write('failed to unload plugin ehm_dynamicChain2')
        raise
