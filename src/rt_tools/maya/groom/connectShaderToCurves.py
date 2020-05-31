# get time range
import maya.cmds as mc
import maya.mel as mel

def connectShaderToCurves():
    controler = mc.PyNode( "featherPrimary:featherBlack_GRP" )
    shader = mc.PyNode( "featherPrimary:featherBlackCurves_MTL" )
    curves = mc.ls(sl=True)

    for curve in curves:
        shader.outColor >> curve.aiCurveShader
        controler.aiCurveWidth >> curve.aiCurveWidth
        controler.aiMinPixelWidth >> curve.aiMinPixelWidth