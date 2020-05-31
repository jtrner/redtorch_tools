import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys

nodeName = 'Wheeler'
nodeId = om.MTypeId(0x0011E180)


class Wheeler(mpx.MPxNode):
    inRadius = om.MObject()
    inTranslate = om.MObject()
    outRotate = om.MObject()

    def __init__(self):
        mpx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):

        if plug == Wheeler.outRotate:

            # get a handle to inputs
            inRadiusPlug = dataBlock.inputValue(Wheeler.inRadius)
            inTranslatePlug = dataBlock.inputValue(Wheeler.inTranslate)

            # get inputs
            radiusVal = inRadiusPlug.asFloat()
            translateVal = inTranslatePlug.asFloat()

            # calculate ouput
            resultRotate = float(translateVal) / float(2 * 3.14159 * radiusVal) * (-360)

            # get handle to output
            outRotatePlug = dataBlock.outputValue(Wheeler.outRotate)

            # set output
            outRotatePlug.setFloat(resultRotate)

            # clean the block
            dataBlock.setClean(plug)

        else:
            return om.kUnknownParameter


def nodeCreator():
    return mpx.asMPxPtr(Wheeler())


def nodeInitializer():
    # create attribute fn
    attrFn = om.MFnNumericAttribute()

    # create attributes
    Wheeler.inRadius = attrFn.create('radius', 'r', om.MFnNumericData.kFloat, 1.0)
    attrFn.setReadable(1)
    attrFn.setWritable(1)
    attrFn.setKeyable(1)
    attrFn.setStorable(1)

    Wheeler.inTranslate = attrFn.create('translate', 't', om.MFnNumericData.kFloat, 0.0)
    attrFn.setReadable(1)
    attrFn.setWritable(1)
    attrFn.setKeyable(1)
    attrFn.setStorable(1)

    Wheeler.outRotate = attrFn.create('rotate', 'ro', om.MFnNumericData.kFloat)
    attrFn.setReadable(1)
    attrFn.setWritable(0)
    attrFn.setKeyable(0)
    attrFn.setStorable(0)

    # attach attributes
    Wheeler.addAttribute(Wheeler.inRadius)
    Wheeler.addAttribute(Wheeler.inTranslate)
    Wheeler.addAttribute(Wheeler.outRotate)

    # design circuitry
    Wheeler.attributeAffects(Wheeler.inRadius, Wheeler.outRotate)
    Wheeler.attributeAffects(Wheeler.inTranslate, Wheeler.outRotate)


def initializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Faild to load plugin: %s' % nodeName)


def uninitializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Faild to unload plugin: %s' % nodeName)
