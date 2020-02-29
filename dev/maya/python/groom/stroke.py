"""
name: stroke.py

Author: Ehsan Hassani Moghaddam

History:
    05/04/18 (ehassani)    first release!

"""

import maya.cmds as mc
import maya.mel as mm

from ..lib import trsLib


def attachStroke(crvs):
    # strokes
    oldStrokes = mc.ls(type='stroke')
    mc.select(crvs)
    mm.eval('AttachBrushToCurves')
    allStrokes = mc.ls(type='stroke')

    # set strokes properties
    strokes = [x for x in allStrokes if x not in oldStrokes]
    [setWidth(strokes, start=0.5, end=0.05, sampleDensity=1) for x in strokes]
    strokes = [mc.listRelatives(x, p=True)[0] for x in strokes]

    # set brush properties
    brushes = [mc.listConnections(x+'.brush', d=False, s=True)[0] for x in strokes]
    [mc.setAttr(x+'.color1', 1, 1, 1) for x in brushes]
    
    # # rename curves and strokes
    # newStrokes = []
    # for i, crv in enumerate(crvs):
    #     stk = mc.rename(strokes[i], crv.replace('_CRV', '_STK'))
    #     newStrokes.append(stk)

    return strokes, brushes


def setWidth(nodes=None, start=1.0, end=0.1, **kwargs):
    if not nodes:
        nodes = mc.ls(type='stroke')
    else:
        nodes = [trsLib.getShapeOfType(x, type="stroke", fullPath=True)[0] for x in nodes]
    
    for node in nodes:
        mc.setAttr(node + '.pressureScale[0].pressureScale_Position', 0.5)
        mc.setAttr(node + '.pressureScale[0].pressureScale_Interp', 2)
        mc.setAttr(node + '.pressureScale[0].pressureScale_FloatValue', 1)

        mc.setAttr(node + '.pressureMap1', 1)
        mc.setAttr(node + '.pressureMap2', 0)

        mc.setAttr(node + '.pressureScale[1].pressureScale_Position', 1)
        mc.setAttr(node + '.pressureScale[1].pressureScale_FloatValue', 0.05)

        mc.setAttr(node + '.pressureMin1', end)
        mc.setAttr(node + '.pressureMax1', start)

        for k, v in kwargs.items():
            mc.setAttr(node + '.' + k, v)
