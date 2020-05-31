"""
name: ikLegQuad.py

Author: Ehsan Hassani Moghaddam

History:
    06/09/16 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import connect
from ...lib import control
from ...lib import jntLib
from ...lib import crvLib
from . import pv

reload(trsLib)
reload(attrLib)
reload(connect)
reload(control)
reload(jntLib)
reload(crvLib)
reload(pv)


def IkLegQuad(joints=None,
              ctlGrp='',
              moduleGrp='',
              side='',
              prefix='',
              globalScaleAttr='',
              isFront=True,
              scapJnt=None,
              scapEndJnt=None,
              verbose=False):
    """
    def for creating ikLegQuad
    """

    # load ikSpringSolver
    mc.loadPlugin('ikSpringSolver', qt=True)
    if not mc.objExists('ikSpringSolver'):
        mc.createNode('ikSpringSolver', name='ikSpringSolver')

    # rig joints
    hipJnt = joints[0]
    kneeJnt = joints[1]
    footJnt = joints[2]
    ballJnt = joints[3]
    toesJnt = joints[4]
    toesEnd = joints[5]

    # set preferred angle based on current orientation
    for jnt in joints[1:]:
        for axis in ['X', 'Y', 'Z']:
            v = mc.getAttr(jnt + '.jointOrient' + axis)
            mc.setAttr(jnt + '.preferredAngle' + axis, v)

    iconSize = trsLib.getDistance(joints[0], joints[-1])

    name = side + '_' + prefix

    mult = [1, -1][side == 'R']

    # knee pv
    kneePvPos = pv.Pv([hipJnt, kneeJnt, footJnt])
    if not kneePvPos:
        kneePvPos = mc.xform(kneeJnt, q=True, ws=True, t=True)
        if isFront:
            kneePvPos[2] += iconSize / 2  # iconSize == leg length
        else:
            kneePvPos[2] -= iconSize / 2

    # knee ctl
    kneeCtl = control.Control(
        descriptor=prefix + "_knee_ik",
        side=side,
        parent=ctlGrp,
        shape="sphere",
        translate=kneePvPos,
        scale=[iconSize * 0.05] * 3,
        lockHideAttrs=['r', 's', 'v'],
        verbose=verbose)

    # whole leg ik spring
    spring_jnts = jntLib.extract_from_to(
        hipJnt,
        ballJnt,
        search="_ik_TRS",
        replace="_ik_spring_TRS")

    spring_ikh_and_eff = mc.ikHandle(
        solver="ikSpringSolver",
        startJoint=spring_jnts[0],
        endEffector=spring_jnts[-1],
        name=name + "_spring_IKH")
    sIkh = spring_ikh_and_eff[0]
    mc.setAttr(sIkh + '.poleVector', 0, 1, 0)
    sIkZro = trsLib.insert(sIkh, name=name + '_spring_ikh_ZRO')
    mc.parent(sIkZro, moduleGrp)

    # leg ik handle
    leg_ikh_and_eff = mc.ikHandle(
        solver="ikRPsolver",
        startJoint=hipJnt,
        endEffector=footJnt,
        name=name + "_IKH")
    ikh = leg_ikh_and_eff[0]
    mc.poleVectorConstraint(kneeCtl.name, ikh, name=name + "_PVC")
    ikZero = trsLib.insert(ikh, name=name + '_ikh_ZRO')[0]
    mc.parent(ikZero, moduleGrp)

    # foot ik handle
    foot_ikh_and_eff = mc.ikHandle(
        solver="ikSCsolver",
        startJoint=footJnt,
        endEffector=ballJnt,
        name=name + "_foot_IKH")
    footIkh = foot_ikh_and_eff[0]
    footZro = trsLib.insert(footIkh, name=name + '_foot_ikh_ZRO')
    mc.parent(footZro, moduleGrp)

    # ball ik handle
    ball_ikh_and_eff = mc.ikHandle(
        solver="ikSCsolver",
        startJoint=ballJnt,
        endEffector=toesJnt,
        name=name + "_ball_IKH")
    mc.parent(ball_ikh_and_eff[0], moduleGrp)

    # toes ik handle
    toes_ikh_and_eff = mc.ikHandle(
        solver="ikSCsolver",
        startJoint=toesJnt,
        endEffector=toesEnd,
        name=name + "_toes_IKH")
    mc.parent(toes_ikh_and_eff[0], moduleGrp)

    # add controls
    footCtl = control.Control(
        descriptor=prefix + "_foot_ik",
        side=side,
        parent=ctlGrp,
        shape="cube",
        scale=[iconSize * 0.25] * 4,
        matchTranslate=ballJnt,
        lockHideAttrs=['s', 'v'],
        verbose=verbose)
    mc.parentConstraint(footCtl.name, sIkZro, mo=True, sr=['x', 'y', 'z'])

    # # check if limb is flipped (temp solution)
    # tmp = mc.getAttr(spring_jnts[0] + '.rotate')[0]
    # mult = 1
    # for v in tmp:
    #     if v > 10 or v < -10:  # if joint has rotation more than 10 degrees assume it's flipped
    #         mult = -1
    #         break

    # twist
    kneeTwist = attrLib.addFloat(footCtl.name, 'kneeTwist')
    mc.connectAttr(kneeTwist, ikh + '.twist')
    # mc.connectAttr(ankleTwist, sIkh + '.twist')
    # connect.withAddedValue(ankleTwist, sIkh + '.twist', addedValue=mult * 90)

    # spring end grp
    spring_end_trs = mc.createNode('transform', n=name + '_spring_end_TRS')
    trsLib.match(spring_end_trs, footJnt)
    mc.parent(spring_end_trs, footCtl.name)
    mc.pointConstraint(spring_jnts[-1], spring_end_trs, name=name + '_springEnd_PNT')
    mc.parentConstraint(spring_end_trs, footIkh, mo=True, sr=['x', 'y', 'z'],
                        name=name + '_ball_jnt_PNT')

    # toe ctl
    toeCtl = control.Control(
        descriptor=prefix + "_toe",
        side=side,
        parent=spring_end_trs,
        shape="square",
        color=control.SECCOLORS[side],
        scale=[iconSize * 0.25] * 4,
        orient=[0, 0, 1],
        moveShape=[0, 0, 0.2],
        matchTranslate=toesJnt,
        matchRotate=footCtl.name,
        lockHideAttrs=['t', 's', 'v'],
        verbose=verbose)
    mc.parentConstraint(toeCtl.name, ball_ikh_and_eff[0], mo=True)
    mc.parentConstraint(toeCtl.name, toes_ikh_and_eff[0], mo=True)

    # heel pivot
    heelCtl = control.Control(
        descriptor=prefix + "_heel",
        side=side,
        parent=spring_end_trs,
        shape="cylinder",
        color=control.SECCOLORS[side],
        scale=[iconSize * 0.1] * 3,
        orient=[1, 0, 0],
        moveShape=[iconSize * -0.2 * mult, 0, 0],
        matchTranslate=ballJnt,
        matchRotate=footJnt,
        lockHideAttrs=['t', 's', 'v'],
        verbose=verbose)
    mc.orientConstraint(heelCtl.name, footJnt, mo=True,
                        name=name + '_foot_jnt_ORI')
    mc.parentConstraint(heelCtl.name, ikZero, mo=True, sr=('x', 'y', 'z'),
                        name=name + '_leg_ikh_PNT')
    mc.parentConstraint(heelCtl.name, footIkh, mo=True, st=('x', 'y', 'z'),
                        name=name + '_ball_jnt_ORI')

    legLength = trsLib.getDistance(joints[0], joints[-1])
    legLength += trsLib.getDistance(joints[1], joints[2])
    legLength += trsLib.getDistance(joints[2], joints[3])
    setupAutoAnkle(ikCtl=footCtl.name,
                   aimTo=scapEndJnt,
                   heelCtl=heelCtl.name,
                   static=spring_end_trs,
                   spring=spring_jnts[-1],
                   legLength=legLength,
                   globalScaleAttr=globalScaleAttr,
                   name=name + '_heel',
                   moduleGrp=moduleGrp)

    # # workaround for spring IK flipping when first joint's
    # # parent rotates more than 180 away from last joint
    # if scapJnt:
    #     mc.parent(spring_jnts[0], scapJnt)

    # add pv guide lines
    crvLib.connectVisual(nodes=(kneeCtl.name, kneeJnt),
                         name=name + '_pv_guide',
                         parent=ctlGrp)

    ret = [
           [footCtl, kneeCtl, heelCtl, toeCtl],
           [ikh, footIkh],
           [spring_jnts, sIkh],
           [ball_ikh_and_eff[0], toes_ikh_and_eff[0]]
           ]
    return ret


def setupAutoAnkle(ikCtl, aimTo, heelCtl, static, spring, legLength, globalScaleAttr, name, moduleGrp):
    """
    when leg is stright, it's better for heel to match ikSpring
    and when len is not straight, it's better for heel to aim to scapicle
    """
    # top auto ankle system group
    heelZro = mc.listRelatives(heelCtl, p=True)[0]
    heelGrp = trsLib.insert(heelZro, mode='parent', name=name + '_auto_GRP')[0]

    # ankle manual twist group that matches foot position but points to knee
    heelTwistZro = mc.createNode('transform', name=name + '_manual_twist_ZRO', p=heelGrp)
    trsLib.match(heelTwistZro, ikCtl)
    ankleJnt = trsLib.getParent(spring)
    kneeJnt = trsLib.getParent(ankleJnt)
    mc.delete(mc.aimConstraint(kneeJnt, heelTwistZro))

    heelTwistGrp = trsLib.insert(heelTwistZro, mode='child', name=name + '_manual_twist_GRP')[0]
    ankleTwist = attrLib.addFloat(ikCtl, 'ankleTwist')
    connect.negative(ankleTwist, heelTwistGrp + '.rx')
    mc.parent(heelZro, heelTwistGrp)

    # create automation method swtich
    a = mc.spaceLocator(n=name + '_spring_start_LOC')[0]
    mc.parent(a, aimTo)
    trsLib.match(a, aimTo)
    b = mc.spaceLocator(n=name + '_spring_end_LOC')[0]
    mc.parent(b, ikCtl)
    trsLib.match(b, ikCtl)
    mc.hide(a, b)
    dist = mc.createNode('distanceBetween', n=name + '_spring_len_DSB')
    mc.connectAttr(a + '.worldMatrix', dist + '.inMatrix1')
    mc.connectAttr(b + '.worldMatrix', dist + '.inMatrix2')

    # gs
    gs = mc.createNode('multiplyDivide', n=name + '_spring_global_scale_MDN')
    mc.setAttr(gs + '.operation', 2)
    mc.connectAttr(dist + '.distance', gs + '.input1X')
    mc.connectAttr(globalScaleAttr, gs + '.input2X')

    mdn = mc.createNode('multiplyDivide', n=name + '_spring_len_MDN')
    mc.connectAttr(gs + '.outputX', mdn + '.input1X')
    mc.setAttr(mdn + '.input2X', legLength)
    mc.setAttr(mdn + '.operation', 2)
    clm = mc.createNode('clamp', n='lenClamp')
    mc.setAttr(clm + '.maxR', 1)
    mc.connectAttr(mdn + '.outputX', clm + '.inputR')
    rev = mc.createNode('reverse', n='lenRev')
    mc.connectAttr(clm + '.outputR', rev + '.inputX')

    # aim to scap
    aimToScap = trsLib.insert(heelGrp, mode='child', name=name + '_aim_to_scap_TRS')[0]
    mc.aimConstraint(aimTo,
                     aimToScap,
                     aimVector=[-1, 1, 0],
                     worldUpType="objectrotation",
                     upVector=[1, 0, 0],
                     worldUpVector=[1, 0, 0],
                     worldUpObject=moduleGrp,
                     name=name + "_AMC",
                     mo=True)

    # spring grp
    springGrp = trsLib.insert(heelGrp, mode='child', name=name + '_match_to_spring_TRS')[0]
    mc.parentConstraint(spring, springGrp, mo=True)

    # auto ankle
    autoAnkle = trsLib.insert(heelGrp, mode='child', name=name + '_auto_ankle_TRS')[0]

    # spring vs aimToScap  
    cns = mc.orientConstraint(aimToScap, springGrp, autoAnkle)[0]
    mc.setAttr(cns + '.interpType', 2)
    attrs = mc.orientConstraint(cns, q=True, weightAliasList=True)
    mc.connectAttr(rev + '.outputX', cns + '.' + attrs[0])
    mc.connectAttr(clm + '.outputR', cns + '.' + attrs[1])

    # result
    attrLib.addSeparator(heelCtl, 'behavior')
    connect.blendConstraint(static, autoAnkle, heelGrp, blendNode=heelCtl,
                            blendAttr='autoAnkle', type='orientConstraint')
