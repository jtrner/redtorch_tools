import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'ehm_surfaceOrient'
nodeID = OpenMaya.MTypeId(0x0011E188)


# node definition
class ehm_surfaceOrient(OpenMayaMPx.MPxNode):
    inputSurface = OpenMaya.MObject()

    rotateX = OpenMaya.MObject()
    rotateY = OpenMaya.MObject()
    rotateZ = OpenMaya.MObject()
    rotation = OpenMaya.MObject()

    translateX = OpenMaya.MObject()
    translateX = OpenMaya.MObject()
    translateX = OpenMaya.MObject()
    translate = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        pass

        if (plug == ehm_surfaceOrient.rotation):
            # get input translate
            translateHandle = dataBlock.inputValue(ehm_surfaceOrient.translate)
            translateValue = translateHandle.asDouble3()
            pTranslate = OpenMaya.MPoint(translateValue[0], translateValue[1], translateValue[2], 1.0)

            # get surface
            surfaceHandle = dataBlock.inputValue(ehm_surfaceOrient.inputSurface)
            oSurf = surfaceHandle.asNurbsSurface()

            # get params at closest point to input translate
            util = OpenMaya.MScriptUtil()
            util.createFromDouble(0)
            paramU = util.asDoublePtr()

            utilV = OpenMaya.MScriptUtil()
            utilV.createFromDouble(0)
            paramV = utilV.asDoublePtr()

            fnSurface = OpenMaya.MFnNurbsSurface(oSurf)
            pointOnSurf = fnSurface.closestPoint(pTranslate, paramU, paramV, False, 0.001, OpenMaya.MSpace.kObject)

            paramU = OpenMaya.MScriptUtil().getDouble(paramU)
            paramV = OpenMaya.MScriptUtil().getDouble(paramV)

            # get tangent at point
            tangentU = OpenMaya.MVector()
            tangentV = OpenMaya.MVector()
            fnSurface.getTangents(paramU, paramV, tangentU, tangentU, OpenMaya.MSpace.kObject)

            # get normal at point
            normal = fnSurface.normal(paramU, paramV, OpenMaya.MSpace.kObject)
            normal.normalize()

            # make x,y and z perpendicular
            tangentV = tangentU ^ normal

            # get rotation from 3 vectors, tangentU, tangentV and normal
            resultMatrix = OpenMaya.MMatrix()
            utilM = OpenMaya.MScriptUtil()
            utilM.createMatrixFromList([tangentU.x, tangentU.y, tangentU.z, 0.0
                                           , tangentV.x, tangentV.y, tangentV.z, 0.0
                                           , normal.x, normal.y, normal.z, 0.0
                                           , pTranslate.x, pTranslate.y, pTranslate.z, 1.0], resultMatrix)

            transMatrix = OpenMaya.MTransformationMatrix(resultMatrix)

            resultEuler = transMatrix.eulerRotation()

            # set rotation value
            xAngle = OpenMaya.MAngle(resultEuler.x)
            rotateHandle = dataBlock.outputValue(ehm_surfaceOrient.rotateX)
            rotateHandle.setMAngle(xAngle)

            yAngle = OpenMaya.MAngle(resultEuler.y)
            rotateHandle = dataBlock.outputValue(ehm_surfaceOrient.rotateY)
            rotateHandle.setMAngle(yAngle)

            zAngle = OpenMaya.MAngle(resultEuler.z)
            rotateHandle = dataBlock.outputValue(ehm_surfaceOrient.rotateZ)
            rotateHandle.setMAngle(zAngle)

            # outputHandle = dataBlock.outputValue( ehm_surfaceOrient.rotation )
            # outputHandle.setFloat( result )

            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_surfaceOrient())


def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()

    # input surface
    ehm_surfaceOrient.inputSurface = tAttr.create('inputSurface', 'is', OpenMaya.MFnNurbsSurfaceData.kNurbsSurface)
    tAttr.setStorable(1)
    tAttr.setWritable(1)
    ehm_surfaceOrient.addAttribute(ehm_surfaceOrient.inputSurface)

    # input Translate
    ehm_surfaceOrient.translateX = nAttr.create("translateX", "tx", OpenMaya.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(0)

    ehm_surfaceOrient.translateY = nAttr.create("translateY", "ty", OpenMaya.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(0)

    ehm_surfaceOrient.translateZ = nAttr.create("translateZ", "tz", OpenMaya.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(0)

    ehm_surfaceOrient.translate = nAttr.create('translate', 't', ehm_surfaceOrient.translateX,
                                               ehm_surfaceOrient.translateY, ehm_surfaceOrient.translateZ)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    ehm_surfaceOrient.addAttribute(ehm_surfaceOrient.translate)

    # out rotation
    ehm_surfaceOrient.rotateX = uAttr.create("rotateX", "rx", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setStorable(0)

    ehm_surfaceOrient.rotateY = uAttr.create("rotateY", "ry", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setStorable(0)

    ehm_surfaceOrient.rotateZ = uAttr.create("rotateZ", "rz", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setStorable(0)

    ehm_surfaceOrient.rotation = nAttr.create("rotate", "r", ehm_surfaceOrient.rotateX, ehm_surfaceOrient.rotateY,
                                              ehm_surfaceOrient.rotateZ)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    ehm_surfaceOrient.addAttribute(ehm_surfaceOrient.rotation)
    ehm_surfaceOrient.attributeAffects(ehm_surfaceOrient.inputSurface, ehm_surfaceOrient.rotation)
    ehm_surfaceOrient.attributeAffects(ehm_surfaceOrient.translate, ehm_surfaceOrient.rotation)


# init plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('failed to load node: ehm_surfaceOrient')
        raise


# uninit plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write('failed to unload plugin ehm_surfaceOrient')
        raise
