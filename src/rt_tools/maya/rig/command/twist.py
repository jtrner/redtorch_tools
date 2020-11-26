"""
name: twist.py

Author: Ehsan Hassani Moghaddam

History:
    05/26/17 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import trsLib
from ...lib import connect
from ...lib import control
from ...lib import strLib

# reload all imported modules from dev
import types

for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('python.'):
            reload(val)


def run(start, end, name, side, nb=5, reverse=False, useRibbon=False):
    """
    def for creating bendy limb

    :param reverse: set to True for uparm and hip as the twist driver 
                    will be the parent (clavicle), but set to False
                    for lowerArm and knee as the twist driver will be
                    the child (hand or foot)
    :return: moduleGrp and (ctlGrp if useRibbon if True, else twist joints)
    """
    # module grp
    moduleGrp = mc.createNode('transform', n=name + '_twist_module_GRP')
    mc.parentConstraint(start, moduleGrp)

    negate = False
    if side == 'R':
        negate = True

    if useRibbon:
        ctlGrp,startJnt,midJnt,endJnt,startCtlzro,midCtlzro,endCtlzro,startCtlname,midCtlname,endCtlname = createRibbonJnts(start=start,
                                                                  end=end, moduleGrp=moduleGrp,nb=nb, name=name, side=side, reverse=reverse)
        return ctlGrp,moduleGrp,startJnt,midJnt,endJnt,startCtlzro,midCtlzro,endCtlzro,startCtlname,midCtlname,endCtlname
    else:
        jnts = createSimpleTwistJnts(start=start, end=end, moduleGrp=moduleGrp, name =name,
                                     side=side,nb=nb, reverse=reverse, negate=negate)
        return jnts, moduleGrp


def createSimpleTwistJnts(start, end, moduleGrp, name, side, nb=5, reverse=False, negate=False):
    """
    Create simple twist joints
    """
    twst, aimCns = createTwistReader(start=start, end=end, side=side, name=name,
                                     moduleGrp=moduleGrp, reverse=reverse)
    # twist is reversed on the right side
    negateVal = 1 #-1 if negate else 1

    jnts = []
    for i in xrange(nb):
        jnt = mc.joint(moduleGrp, n='{}_{}_JNT'.format(name, i + 1))
        mc.delete(mc.orientConstraint(start, jnt))
        jnts.append(jnt)

        # position
        ratio = 1.0 / nb
        connect.weightConstraint(start, end, jnt, type='pointConstraint',
                                 weights=(1 - ratio * i, ratio * i))

        # rotation
        mdn = mc.createNode('multiplyDivide', n='{}{}_twist_amount_MDN'.format(name, i+1))
        mc.connectAttr(twst + '.rx', mdn + '.input1X')

        if reverse:
            mc.setAttr(mdn + '.input2X', negateVal * (float(nb - i) / nb) * -2.0)
        else:
            mc.setAttr(mdn + '.input2X', negateVal * (float(i) / nb) * 2.0)

        mc.connectAttr(mdn + '.outputX', jnt + '.rx')

        # scale
        mc.connectAttr(start + '.sx', jnt + '.sx')

    return jnts


def createRibbonJnts(start, end, moduleGrp, name, side, nb=5, reverse=False):
    """
    Create twist joints using ribbon
    """
    twst, aimCns = createTwistReader(start=start, end=end, side=side, name=name,
                                     moduleGrp=moduleGrp, reverse=reverse)

    # ctls grp
    ctlGrp = mc.createNode('transform', n=name + '_twist_ctl_GRP')
    mc.parentConstraint(start, ctlGrp)
    mc.connectAttr(start + '.sx', ctlGrp + '.sx')

    # create ribbon
    dist = trsLib.getDistance(start, end)
    plane = mc.nurbsPlane(axis=[0, 1, 0], w=dist, lr=0.01, u=4, n=name + '_NRB')[0]
    mc.delete(plane, ch=True)
    planeShape = trsLib.getShapes(plane)[0]
    ribbonGrp = mc.createNode('transform', n=name + '_ribbon_GRP', p=moduleGrp)
    mc.setAttr(ribbonGrp + '.inheritsTransform', 0)
    mc.parent(plane, ribbonGrp)

    # create follicles
    flcs = []
    for i in xrange(nb):

        # create flc and connect to plane
        flcShape = mc.createNode('follicle')
        mc.connectAttr(planeShape + '.worldMatrix', flcShape + '.inputWorldMatrix')
        mc.connectAttr(planeShape + '.local', flcShape + '.inputSurface')

        # driver flc transform using flc shape
        flc = mc.listRelatives(flcShape, p=True)[0]
        for j in ['t', 'r']:
            for k in ['x', 'y', 'z']:
                mc.connectAttr(flcShape + '.o' + j + k, flc + '.' + j + k)

        # position flcs
        ratio = 1.0 / (nb - 1)
        mc.setAttr(flcShape + '.parameterU', i * ratio + ratio / 2)
        mc.setAttr(flcShape + '.parameterV', 0.5)

        # rename flc
        flc = mc.rename(flc, '{0}{1}_FLC'.format(name, i))
        flcs.append(flc)

    # group follicles
    flcGrp = mc.createNode('transform', n=name + '_flc_GRP', p=moduleGrp)
    mc.setAttr(flcGrp + '.inheritsTransform', 0)
    mc.parent(flcs, flcGrp)

    # start controls
    n = name.split('_', 1)[1]
    startCtl = control.Control(descriptor=n + '_start',
                               side=strLib.getPrefix(name) or 'c',
                               parent=ctlGrp,
                               translate=[-dist / 2, 0, 0],
                               orient=[1, 0, 0],
                               color='greenPale',
                               scale=[dist / 4] * 3)

    # mid controls
    midCtl = control.Control(descriptor=n + '_mid',
                             side=strLib.getPrefix(name) or 'c',
                             parent=ctlGrp,
                             translate=[0, 0, 0],
                             orient=[1, 0, 0],
                             color='greenPale',
                             scale=[dist / 4] * 3)

    # end controls
    endCtl = control.Control(descriptor=n + '_end',
                             side=strLib.getPrefix(name) or 'c',
                             parent=ctlGrp,
                             translate=[dist / 2, 0, 0],
                             orient=[1, 0, 0],
                             color='greenPale',
                             scale=[dist / 4] * 3)

    # create surface driver jnts
    startJnt = mc.joint(ribbonGrp, n=startCtl.name.replace('CTL', 'JNT'))
    midJnt = mc.joint(ribbonGrp, n=midCtl.name.replace('CTL', 'JNT'))
    endJnt = mc.joint(ribbonGrp, n=endCtl.name.replace('CTL', 'JNT'))

    connect.matrix(startCtl.name, startJnt, mo=False)
    connect.matrix(midCtl.name, midJnt, mo=False)
    connect.matrix(endCtl.name, endJnt, mo=False)

    mc.skinCluster(startJnt, midJnt, endJnt, plane)

    # position ctls
    trsLib.match(startCtl.zro, start)
    mc.delete(mc.pointConstraint(start, end, midCtl.zro))
    trsLib.match(midCtl.zro, r=startCtl.name)
    trsLib.match(endCtl.zro, t=end, r=startCtl.name)

    # inverse scale for ctls when limb is stretches to prevent shear
    scmdn = mc.createNode('multiplyDivide', n=name + '_scale_compensate_MDN')
    mc.setAttr(scmdn + '.operation', 2)
    mc.setAttr(scmdn + '.input1X', 1)
    mc.connectAttr(start + '.sx', scmdn + '.input2X')
    mc.connectAttr(scmdn + '.outputX', startCtl.zro + '.sx')
    mc.connectAttr(scmdn + '.outputX', midCtl.zro + '.sx')
    mc.connectAttr(scmdn + '.outputX', endCtl.zro + '.sx')

    # create jnts
    jntGrp = mc.createNode('transform', n=name + '_jnt_GRP', p=moduleGrp)
    jnts = []
    for i in xrange(nb):
        mc.select(jntGrp)
        j = mc.joint(n='{0}{1}_JNT'.format(name, i))
        trsLib.match(j, t=flcs[i], r=start)
        mc.parent(j, flcs[i])
        jnts.append(j)

    # set twist offset of aimConstraint
    rot1 = mc.xform(start, q=True, ws=True, ro=True)
    rot2 = mc.xform(startJnt, q=True, ws=True, ro=True)
    offset = rot1[0] - rot2[0]
    mc.setAttr(aimCns + '.offsetX', offset)

    # connect twist to ctls
    mdn = mc.createNode('multiplyDivide', n=name + '_twist_amount_MDN')
    mc.connectAttr(twst + '.rx', mdn + '.input1X')
    mc.connectAttr(twst + '.rx', mdn + '.input1Y')

    if reverse:
        mc.setAttr(mdn + '.input2', -2, -1, 0)
        mc.connectAttr(mdn + '.outputX', startCtl.zro + '.rx')
    else:
        mc.setAttr(mdn + '.input2', 2, 1, 0)
        mc.connectAttr(mdn + '.outputX', endCtl.zro + '.rx')

    mc.connectAttr(mdn + '.outputY', midCtl.zro + '.rx')

    # return
    return ctlGrp,startJnt,midJnt,endJnt,startCtl.zro,midCtl.zro,endCtl.zro,startCtl.name,midCtl.name,endCtl.name



def createTwistReader(start, end, side, moduleGrp, reverse, name, offset=0):
    aimVec = [1, 0, 0] if side == 'L' else [-1, 0, 0]
    twstGrp = mc.createNode('transform', n=name + '_twist_reader_GRP')
    trsLib.match(twstGrp, moduleGrp)
    mc.parent(twstGrp, moduleGrp)
    if reverse:  # for uparm or hip
        startPar = trsLib.getParent(start)
        mc.parentConstraint(startPar, twstGrp, mo=True)
    else:  # for elbow or knee
        mc.parentConstraint(start, twstGrp)

    twstZro = mc.createNode('transform', n=name + '_twist_reader_ZRO')
    mc.parent(twstZro, twstGrp)
    if reverse:
        trsLib.match(twstZro, t=start)
        aimCns = mc.aimConstraint(end, twstZro, worldUpType="none", aim=aimVec, mo=False)[0]
    else:
        trsLib.match(twstZro, t=end)
        endChild = trsLib.getChild(end)
        mc.pointConstraint(end, twstZro)
        aimCns = mc.aimConstraint(endChild, twstZro, worldUpType="none", aim=aimVec, mo=False)[0]

    mc.setAttr(aimCns + '.offsetX', offset)

    twst = mc.createNode('transform', n=name + '_twist_reader_SRT')
    mc.parent(twst, twstZro)
    trsLib.match(twst, t=twstZro)
    if reverse:
        cns = mc.orientConstraint(start, twstZro, twst)[0]
    else:
        cns = mc.orientConstraint(end, twstZro, twst)[0]
    mc.setAttr(cns + '.interpType', 2)

    return twst, aimCns
