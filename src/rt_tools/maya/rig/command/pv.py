"""
name: pv.py

Author: Ehsan Hassani Moghaddam

History:
    15/10/17 (ehassani)    first release!

"""
import maya.api.OpenMaya as om2
import maya.cmds as mc

from ...lib import trsLib


def Pv(jnts=mc.ls(sl=True), distance=1.0, createLoc=False):
    """
    get best position for pole vector based on jnts positions and mode

    import python.rig.command.pv as pv
    pv.Pv(jnts=mc.ls(sl=True), distance=1.0, createLoc=True)

    :param jnts: list of jnts, 3 for biped, 4 for quadruped
    :return: list of pole vector positions with 2 elements
    """
    length = trsLib.getDistance(jnts[0], jnts[-1])
    loc = mc.createNode('transform')

    startVec = om2.MVector(mc.xform(jnts[0], q=1, ws=1, t=1))
    middleVec = om2.MVector(mc.xform(jnts[1], q=1, ws=1, t=1))
    endV = om2.MVector(mc.xform(jnts[-1], q=1, ws=1, t=1))

    startEndV = endV - startVec
    startMiddleVec = middleVec - startVec

    projectedVec = startEndV.normalize() * (startEndV * startMiddleVec)
    mc.xform(loc, ws=True, t=startVec+projectedVec)

    pvPos = trsLib.shootRay(loc, jnts[1], length=length*distance)
    mc.delete(loc)

    if createLoc:
        loc = mc.spaceLocator()[0]
        mc.xform(loc, ws=True, t=pvPos)
        return loc, pvPos

    return pvPos
