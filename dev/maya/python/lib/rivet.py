"""
name: rivet.py

Author: Ehsan Hassani Moghaddam

History:
    10/03/18 (ehassani)     first release!

"""
import maya.cmds as mc

from . import trsLib


def getClosestUV(mesh=None, point=[0, 0, 0], useObj=None):
    """
    get UV of surface in given world space point

    """
    surfShape = trsLib.getShapes(mesh)[0]
    if useObj:
        point = mc.xform(useObj, q=True, t=True, ws=True)
    pOnSurf = mc.createNode('closestPointOnMesh')

    mc.connectAttr(surfShape + '.worldMatrix[0]', pOnSurf + '.inputMatrix')
    mc.connectAttr(surfShape + '.worldMesh[0]', pOnSurf + '.inMesh')

    mc.setAttr(pOnSurf + '.inPosition', *point)

    u = mc.getAttr(pOnSurf + '.result.parameterU')
    v = mc.getAttr(pOnSurf + '.result.parameterV')

    mc.delete(pOnSurf)

    return u, v


def follicleByClosestPoint(mesh=None, point=[0, 0, 0], useObj=None, name='new_FLC'):
    """
    create follicle on given point on given mesh
    """
    u, v = getClosestUV(mesh=mesh, point=point, useObj=useObj)

    flc = mc.createNode('follicle')
    flc = mc.listRelatives(flc, p=True)[0]
    flc = mc.rename(flc, name)
    flcShape = mc.listRelatives(flc, s=True)[0]
    geoShape = mc.listRelatives(mesh, s=True)[0]

    mc.connectAttr(geoShape + '.outMesh', flcShape + '.inputMesh')
    mc.connectAttr(geoShape + '.worldMatrix[0]', flcShape + '.inputWorldMatrix')

    mc.setAttr(flcShape + '.parameterU', u)
    mc.setAttr(flcShape + '.parameterV', v)

    mc.connectAttr(flcShape + '.outTranslate', flc + '.t')
    mc.connectAttr(flcShape + '.outRotate', flc + '.r')

    return flc, flcShape


def follicleOnFace(mesh=None, face=0):
    """
    create follicle on given face
    """
    mc.select('{}.f[{}]'.format(mesh, face))
    bb = mc.polyEvaluate(bc=True)
    point = [(bb[0][0] + bb[0][1]) / 2,
             (bb[1][0] + bb[1][1]) / 2,
             (bb[2][0] + bb[2][1]) / 2]

    flc, flcShape = follicleByClosestPoint(mesh=mesh,
                           point=point,
                           name='new_FLC')

    return flc, flcShape
