"""
extractDeltas.py

usage:
    import extractDeltas
    reload(extractDeltas)
    src = 'base'
    tgt = 'tgt'
    extractDeltas.ExtractDeltas(src, tgt)


test:

def toMMatrix(mat):
    ret = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(mat, ret)
    return ret

def getJntMatrix(jnt):
    bindM = mc.getAttr(jnt+'.bindPose')
    bindMat = toMMatrix(bindM)

    currM = mc.getAttr(jnt+'.worldMatrix')
    currMat = toMMatrix(currM)

    mat = currMat * bindMat.inverse()

    return mat

jnt = 'joint2'

jMat = getJntMatrix(jnt)

parMat = toMMatrix(mc.getAttr(jnt+'.parentMatrix'))

poseMat = jMat * parMat

trsMat = om.MTransformationMatrix(poseMat)

rad = trsMat.eulerRotation()
rot = [rad.x * 57.2958,
       rad.y * 57.2958,
       rad.z * 57.2958]

print rot



"""

import maya.cmds as mc
import maya.OpenMaya as om

from ...lib import deformLibLib
from ...lib import trsLib


def ExtractDeltas(src, tgt):
    
    deformLib.disableDeformers(src)
    crr, crrShape = trsLib.duplicateClean(src)
    crr = mc.rename(crr, tgt+'_corrective')
    deformLib.enableDeformers(src)
    
    skin = deformLib.getSkinCluster(src)
    
    numVerts = mc.polyEvaluate(crr, v=True)

    for i in range(numVerts):
        v = '.vtx[{0}]'.format(i)

        jnts = mc.skinPercent(skin, src+v, q=True, t=None)
        wgts = mc.skinPercent(skin, src+v, q=True, v=True)

        tgtP = mc.xform(tgt+v, q=True, os=True, t=True)
        tgtV = om.MVector(*tgtP)

        srcP = mc.xform(src+v, q=True, os=True, t=True)
        srcV = om.MVector(*srcP)

        fullDeltaVec = tgtV - srcV
        
        # if vertices are not moved, don't 
        if fullDeltaVec.length() < 0.001:
            continue

        deltaVec = om.MVector()
        for j, w in zip(jnts, wgts):
            deltaVec += fullDeltaVec * getJntMatrix(j) * w

        # set final pose of verts using deltaVec
        # deltaVec *= 2
        mc.xform(crr+v, ws=True, r=True, t=[deltaVec.x, deltaVec.y, deltaVec.z])

    mc.blendShape(crr, src, frontOfChain=True, w=[0, 1])


def printMatrix(mMatrix):
    print  mMatrix(0,0), '\t', mMatrix(0,1), '\t', mMatrix(0,2), '\t', mMatrix(0,3)
    print ''
    print  mMatrix(1,0), '\t', mMatrix(1,1), '\t', mMatrix(1,2), '\t', mMatrix(1,3)
    print ''
    print  mMatrix(2,0), '\t', mMatrix(2,1), '\t', mMatrix(2,2), '\t', mMatrix(2,3)
    print ''
    print  mMatrix(3,0), '\t', mMatrix(3,1), '\t', mMatrix(3,2), '\t', mMatrix(3,3)


def printVec(mVec):
    print  mVec.x, '\t', mVec.y, '\t', mVec.z


def vecToMatrix(mVec):
    """
    convert translate MVector to MMatrix
    """
    ret = [1,         0,         0,         0,
           0,         1,         0,         0,
           0,         0,         1,         0,
           mVec.x,    mVec.y,    mVec.z,    1]
    return toMMatrix(ret)   


def getJntMatrix(jnt):
    """
    get current transformation of given joint
    :return: MMatrix
    """
    bindM = mc.getAttr(jnt+'.bindPose')
    bindMat = toMMatrix(bindM)

    jM = mc.getAttr(jnt+'.worldMatrix')
    jMat = toMMatrix(jM)

    mat = jMat.inverse() * bindMat

    return mat


def inverseMatrixList(matList):
    mat = toMMatrix(matList)
    mat.inverse()
    return toMatrix(mat)


def toMMatrix(mat):
    """
    converts list to maya matrix
    :return: MMatrix
    """
    ret = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(mat, ret)
    return ret


def toMatrix(mMatrix):
    """
    converts maya matrix to list
    :return: list with 16 elements
    """
    ret = [mMatrix(0,0), mMatrix(0,1), mMatrix(0,2), mMatrix(0,3),
           mMatrix(1,0), mMatrix(1,1), mMatrix(1,2), mMatrix(1,3),
           mMatrix(2,0), mMatrix(2,1), mMatrix(2,2), mMatrix(2,3),
           mMatrix(3,0), mMatrix(3,1), mMatrix(3,2), mMatrix(3,3)]
    return ret


def setPose(base, tgt):
    numVerts = mc.polyEvaluate(base, v=True)

    for i in range(numVerts):
        v = '.vtx[{0}]'.format(i)
        pos = mc.xform(tgt+v, q=True, ws=True, t=True)
        for i in range(10):
            mc.xform(base+v, ws=True, t=pos)


def toMMatrix(mat):
    ret = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(mat, ret)
    return ret


def linearBlendSkinDeform():
    jnt = 'joint2'

    bindM = mc.getAttr(jnt+'.bindPose')
    bindMat = toMMatrix(bindM)

    currM = mc.getAttr(jnt+'.worldMatrix')
    currMat = toMMatrix(currM)

    # create locator
    loc = 'loc'

    # init pose vector
    locP = mc.xform(loc, q=True, ws=True, t=True)
    locV = om.MVector(*locP)
    
    jntP = mc.xform(jnt, q=True, ws=True, t=True)
    jntV = om.MVector(*jntP)
    
    initV = locV - jntV

    # put loc on pose
    currV = initV * bindMat.inverse() * currMat
    currV += jntV
    mc.xform(loc, ws=True, t=[currV.x, currV.y, currV.z])


def decompose(mMatrix):
    trsMat = om.MTransformationMatrix(mMatrix)

    # rotate
    rad = trsMat.eulerRotation()
    rot = [rad.x * 57.2958,
           rad.y * 57.2958,
           rad.z * 57.2958]

    # translate
    trnV = trsMat.translation(om.MSpace.kWorld)
    trn = [trnV.x, trnV.y, trnV.z]

    return trn, rot
