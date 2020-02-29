"""
path = '/sw/dev/hassanie/ehm_stuff/ehm_lib'
if path not in sys.path:
    sys.path.insert(0, path)

import mathLib
reload(mathLib)

u, v, w = mathLib.barycentricFromObjs(a='a', b='b', c='c', p='p')

aa = mc.xform('aa', q=True, ws=True, t=True)
bb = mc.xform('bb', q=True, ws=True, t=True)
cc = mc.xform('cc', q=True, ws=True, t=True)
pos = mathLib.getPositionFromBarycentric(aa, bb, cc, u, v, w)
mc.xform('pp', ws=True, t=pos)
"""
import maya.cmds as mc
import maya.api.OpenMaya as om2


def barycentricFromPositions(a, b, c, p):
    v0 = om2.MVector(b) - om2.MVector(a)
    v1 = om2.MVector(c) - om2.MVector(a)
    v2 = om2.MVector(p) - om2.MVector(a)
    d00 = v0 * v0
    d01 = v0 * v1
    d11 = v1 * v1
    d20 = v2 * v0
    d21 = v2 * v1
    denom = (d00 * d11) - (d01 * d01)
    v = ((d11 * d20) - (d01 * d21)) / denom
    w = ((d00 * d21) - (d01 * d20)) / denom
    u = 1.0 - v - w
    return u, v, w

def barycentricFromObjs(a=None, b=None, c=None, p=None, useSelection=False):
    if useSelection:
        sels = mc.ls(sl=True)
        a = sels[0]
        b = sels[1]
        c = sels[2]
        p = sels[3]
    a = mc.xform(a, q=True, ws=True, t=True)
    b = mc.xform(b, q=True, ws=True, t=True)
    c = mc.xform(c, q=True, ws=True, t=True)
    p = mc.xform(p, q=True, ws=True, t=True)
    u, v, w = barycentricFromPositions(a, b, c, p)
    return u, v, w


def getPositionFromBarycentric(a, b, c, u, v, w):
    """ p = ua + vb + wc """
    px = om2.MVector(a) * u
    py = om2.MVector(b) * v
    pz = om2.MVector(c) * w
    return px + py + pz


def getClosestAxisToTarget(obj, target):
    # localize target position
    mObj = mc.xform(obj, q=True, m=True, ws=True)

    pos = target
    if isinstance(target, basestring):
        pos = mc.xform(target, q=True, t=True, ws=True)

    pTgt = om2.MPoint(*pos)
    matInv = om2.MMatrix(mObj).inverse()
    vTgt = om2.MVector(pTgt * matInv).normalize()

    # get closes axis based on biggest dot product
    xyzAxis = (om2.MVector.kXaxisVector,
               om2.MVector.kYaxisVector,
               om2.MVector.kZaxisVector)
    vClosest = None
    closestDot = None
    for i, v in enumerate(xyzAxis):
        dot = v * vTgt
        if vClosest is None or abs(dot) > closestDot:
            vClosest = i
            closestDot = abs(dot)

    # check for negative axis
    result = xyzAxis[vClosest]
    inv = 1 if result * vTgt > 0.0 else -1

    return result * inv


def matrixFrom3Vec(vecX, vecY, vecZ):
    mat = om2.MMatrix(
        [[vecX.x, vecX.y, vecX.z, 0],
         [vecY.x, vecY.y, vecY.z, 0],
         [vecZ.x, vecZ.y, vecZ.z, 0],
         [0, 0, 0, 1]])
    return mat


def matrixToEuler(mat):
    mat = om2.MTransformationMatrix(mat)
    rad = mat.rotation()
    toDegree = 180.0 / 3.14159265359
    rot = rad[0] * toDegree, rad[1] * toDegree, rad[2] * toDegree
    return rot


def getFootRotation(footJnt, ballJnt):
    footP = mc.xform(footJnt, q=True, ws=True, t=True)
    ballP = mc.xform(ballJnt, q=True, ws=True, t=True)
    z = om2.MVector(ballP) - om2.MVector(footP)
    z.normalize()

    y = om2.MVector(0, 1, 0)
    x = y ^ z
    z = x ^ y

    mat = matrixFrom3Vec(x, y, z)
    rot = matrixToEuler(mat)
    return rot
