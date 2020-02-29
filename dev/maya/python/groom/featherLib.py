"""
featherLib.py

"""

import maya.cmds as mc
import maya.api.OpenMaya as om

from ..lib import trsLib
from ..lib import meshLib
from ..lib import crvLib
from ..groom import stroke


# reload all imported modules from dev
import types
for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('dev'):
            reload(val)


def groomCrvsToFeather(geo, feather, curves):
    """
    copies "feather" each given curve based on geo's surface

    geo = 'body'
    feather = 'bodyFeatherA'
    curves = mc.listRelatives('featherDir_crvs_grp', type='nurbsCurve', ad=True)
    featherLib.groomCrvsToFeather(geo, feather, curves)
    """
    for crv in curves:
        dup = trsLib.duplicateClean(feather)[0]

        cvs = crvLib.getCVs(crv)

        start = mc.xform(cvs[0], q=1, ws=1, t=1)
        end = mc.xform(cvs[-1], q=1, ws=1, t=1)
        normal = meshLib.getClosestNormal(geo, start)
        pos = meshLib.getClosestPoint(geo, start)

        s = om.MVector(*start)
        e = om.MVector(*end)
        n = om.MVector(*normal)

        y = (e - s).normal()
        x = (y ^ n).normal()
        z = (x ^ y).normal()

        mat = [x[0], x[1], x[2], 0,
               y[0], y[1], y[2], 0,
               z[0], z[1], z[2], 0,
               pos[0], pos[1], pos[2], 1]

        curveLen = (e - s).length()

        mc.xform(dup, matrix=mat)
        mc.setAttr(dup+'.s', curveLen, curveLen, curveLen)


def strokeOnSurf(surf, num=110, name='L_feather'):
    
    # main group
    mainGrp = name + '_GRP'
    if not mc.objExists(mainGrp):
        mc.createNode('transform', n=mainGrp)

    # parent surf
    par = mc.listRelatives(surf, p=True)
    if (not par) or (par[0] != mainGrp):
        mc.parent(surf, mainGrp)

    # curves
    crvs = crvLib.fromSurf(surf=surf, num=num, name=name)
    mc.group(crvs, n=name+'Crv_GRP', p=mainGrp)
    mc.delete(crvs, ch=True)

    # strokes
    strokes, brushes = stroke.attachStroke(crvs)
    mc.group(strokes, n=name+'Stroke_GRP', p=mainGrp)

    # rename curves and strokes
    newCrvs = []
    newStrokes = []
    for i in range(num-1):
        crv = mc.rename(crvs[i], '{}{:04d}_CRV'.format(name, i))
        newCrvs.append(crv)
        stk = mc.rename(strokes[i], '{}{:04d}_STK'.format(name, i))
        newStrokes.append(stk)

    # add noise deformer for curves
    crvLib.selectNonFirst(newCrvs)
    deformer = mc.deformer(type='textureDeformer')[0]
    mc.setAttr(deformer+'.pointSpace', 0)
    mc.setAttr(deformer+'.strength', 0.3)
    noise = mc.createNode('noise')
    mc.connectAttr(noise+'.outColor', deformer+'.texture')

    handle = mc.createNode('textureDeformerHandle', n=name+'_TDH', p=mainGrp)
    mc.connectAttr(handle+'.matrix', deformer+'.handleMatrix')
    mc.setAttr(handle+'.rx', -55)

    return newCrvs, newStrokes



