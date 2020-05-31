"""
Gaussian Formula: 
                  f(x) = 1/d.sqrt(2pi) . (e ^ ( -(x-mean(x))^2 / 2.d^2 ))

Objective: Create 100 locators distributed using gaussian function on the origin

Solution: 
    - generate a unit vector randomly pointing to some direction
    - generate an array of floats using gaussian to use as length of vector
    - create and place locators on these vectors
"""

import random
import math
import maya.cmds as mc
import maya.OpenMaya as om


def gaussianRandom():
    s = 0.0
    while (s >= 1.0 or s == 0):
        v1 = random.uniform(-1, 1)  # 2.0 * random.uniform(0,1) - 1.0
        v2 = random.uniform(-1, 1)  # 2.0 * random.uniform(0,1) - 1.0
        s = v1 * v1 + v2 * v2
    s = math.sqrt((-2.0 * math.log(s)) / s)
    return v1 * s


def gaussianMeanDeviation(mean, standard_deviation):
    return mean + (gaussianRandom() * standard_deviation)


def gaussian(mean=0, standard_deviation=1, min=-1.0, max=1.0):
    u1 = random.uniform(0, 1)
    u2 = random.uniform(0, 1)
    randStdNormal = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)  # random normal(0,1)
    randNormal = mean + standard_deviation * randStdNormal  # random normal(mean,standard_deviation^2)
    return randNormal


def gaussian2(mean=0, standard_deviation=1, min=-1.0, max=1.0):
    x = gaussianMeanDeviation(mean, standard_deviation)
    while (x < min) or (x > max):
        x = gaussianMeanDeviation(mean, standard_deviation)
    return x


def gaussian3():
    x = random.uniform(-1, 1)
    a = 1.0 / math.sqrt(math.pi * 2.0)
    b = math.exp(-x * x / 2)
    g = a * b
    return g


def upAimToRotMat(aim, up):
    aimVec = om.MVector(aim[0], aim[1], aim[2])
    upVec = om.MVector(up[0], up[1], up[2])
    aimVec.normalize()
    upVec.normalize()
    zVec = aimVec ^ upVec
    zVec.normalize()
    upVec = zVec ^ aimVec
    upVec.normalize()

    return matFromList([aimVec[0], aimVec[1], aimVec[2], 0,
                        upVec[0], upVec[1], upVec[2], 0,
                        zVec[0], zVec[1], zVec[2], 0,
                        0, 0, 0, 1])


def matToRot(mat):
    tMat = om.MTransformationMatrix(mat)
    rot = tMat.eulerRotation()
    deg = [x * 180 / math.pi for x in rot]  # radian to degree
    return deg


def matFromList(matList):
    mat = om.MMatrix()
    util = om.MScriptUtil()
    util.createMatrixFromList(matList, mat)
    return mat


def test(numberOfLocators=100, method=0):
    locs = []
    for i in xrange(numberOfLocators):
        if method == 0:
            g = gaussian()
        elif method == 1:
            g = gaussian2()
        elif method == 2:
            g = gaussian3()

        u1 = random.uniform(-1, 1)
        u2 = random.uniform(-1, 1)
        rotMat = upAimToRotMat([u1, u2, 0], [0, 1, 0])

        rot = matToRot(rotMat)
        loc = mc.spaceLocator()[0]

        mc.setAttr(loc + ".tx", g)
        mc.rotate(rot[0], rot[1], rot[2], loc, pivot=[0, 0, 0])
        pos = mc.getAttr(loc + ".rotatePivotTranslate")[0]
        mc.setAttr(loc + ".rotatePivotTranslate", 0, 0, 0)
        mc.setAttr(loc + ".t", pos[0] + g, pos[1], pos[2])
        mc.setAttr(loc + ".r", 0, 0, 0)
        mc.setAttr(loc + ".s", 0.05, 0.05, 0.05)

        locs.append(loc)

    grp = mc.group(empty=True)
    mc.parent(locs, grp)
    mc.select(grp)


"""
import sys
path = "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin\\ehm_plugins\\scriptedPlugin"
if path not in sys.path:
    sys.path.append( path )
import ehm_gaussian as gaus
reload( gaus )

import random
import math

numOfLocs = 100
mc.select(all=True)
mc.delete()
gaus.test(numOfLocs)
gaus.test(numOfLocs, 1)
mc.move(5,0,0)
gaus.test(numOfLocs, 2)
mc.move(10,0,0)
mc.select(clear=True)

"""
