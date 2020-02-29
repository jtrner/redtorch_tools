"""
name: ikLeg.py

Author: Ehsan Hassani Moghaddam

History:
    06/09/16 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import control
from ...lib import mathLib

reload(trsLib)
reload(attrLib)
reload(control)
reload(mathLib)


def IkLeg(joints,
          parent='',
          side='',
          prefix='',
          poleVec='',
          heelPos='',
          verbose=False):
    """
    def for creating ikLeg
    """

    # rig joints
    hipIkJnt = joints[0]
    footIkJnt = joints[2]
    ballIkJnt = joints[3]
    ballIkEnd = joints[4]

    iconSize = trsLib.getDistance(joints[0], joints[-1])

    name = side + '_' + prefix

    # leg ik handle
    leg_ikh_and_eff = mc.ikHandle(solver="ikRPsolver",
                                  startJoint=hipIkJnt,
                                  endEffector=footIkJnt,
                                  name=name + "_foot_IKH")
    legIkh = leg_ikh_and_eff[0]
    legIkZro = trsLib.insert(legIkh, name=legIkh.replace('IKH', 'ikh_ZRO'))

    # add controls
    footIkCtl = control.Control(descriptor="footIk",
                                side=side,
                                parent=parent,
                                shape="cube",
                                scale=[iconSize * 0.25, iconSize * 0.25, iconSize * 0.25],
                                matchTranslate=footIkJnt,
                                rotate=mathLib.getFootRotation(footIkJnt, ballIkJnt),
                                lockHideAttrs=['s', 'v'],
                                verbose=verbose)

    kneeIkCtl = control.Control(descriptor="kneeIk",
                                side=side,
                                parent=parent,
                                shape="sphere",
                                scale=[iconSize * 0.05, iconSize * 0.05, iconSize * 0.05],
                                matchTranslate=poleVec,
                                matchRotate=poleVec,
                                lockHideAttrs=['r', 's', 'v'],
                                verbose=verbose)

    # heel pivot
    heelPivCtl = control.Control(descriptor="heelPivot",
                                 side=side,
                                 parent=parent,
                                 shape="sphere",
                                 scale=[iconSize * 0.05, iconSize * 0.05, iconSize * 0.05],
                                 orient=[0, 0, 1],
                                 matchTranslate=heelPos,
                                 matchRotate=footIkCtl.name,
                                 useSecondaryColors=True,
                                 lockHideAttrs=['s', 'v'],
                                 verbose=verbose)
    mc.parent(heelPivCtl.zro, footIkCtl.name)

    # toe pivot
    toePivCtl = control.Control(descriptor="toePivot",
                                side=side,
                                parent=parent,
                                shape="sphere",
                                scale=[iconSize * 0.05, iconSize * 0.05, iconSize * 0.05],
                                orient=[0, 0, 1],
                                matchTranslate=ballIkEnd,
                                matchRotate=footIkCtl.name,
                                useSecondaryColors=True,
                                verbose=verbose)
    mc.parent(toePivCtl.zro, heelPivCtl.name)

    # toe ctl
    toeCtl = control.Control(descriptor="toe",
                             side=side,
                             parent=toePivCtl.name,
                             shape="square",
                             scale=[iconSize * 0.25, iconSize * 0.25, iconSize * 0.25],
                             orient=[0, 0, 1],
                             moveShape=[0, 0, 0.2],
                             matchTranslate=ballIkJnt,
                             matchRotate=footIkCtl.name,
                             verbose=verbose)
    mc.orientConstraint(toeCtl.name, ballIkJnt, mo=True, name=name + 'BallJnt_ORI')

    # heel pivot
    heelCtl = control.Control(descriptor="heel",
                              side=side,
                              parent=toePivCtl.name,
                              shape="square",
                              scale=[iconSize * 0.25, iconSize * 0.25, iconSize * 0.25],
                              orient=[0, 0, 1],
                              moveShape=[0, 0, -0.2],
                              matchTranslate=ballIkJnt,
                              matchRotate=footIkCtl.name,
                              verbose=verbose)

    # this group be driven by all pivots and will drive the ik
    revFootGrp = mc.createNode('transform', n=name + 'revFootEnd_srt', p=heelCtl.name)

    mc.orientConstraint(revFootGrp, footIkJnt, mo=True, name=name + 'FootJnt_ORI')
    mc.parentConstraint(revFootGrp,
                        legIkZro,
                        name=name + 'LegIkh_PNT',
                        mo=True,
                        skipRotate=['x', 'y', 'z'])

    # visibility
    attrLib.addSeparator(footIkCtl.name, 'vis')

    # extra foot ctls vis
    a = attrLib.addEnum(footIkCtl.name, 'extraCtls', en=['off', 'on'], k=0)  # , cb=1)
    extraCtls = [heelCtl.name, toePivCtl.name, heelPivCtl.name]
    extraCtlsShapes = [trsLib.getShapes(x)[0] for x in extraCtls]
    [attrLib.connectAttr(a, x + '.v') for x in extraCtlsShapes]

    # behavior
    attrLib.addSeparator(footIkCtl.name, 'behavior')

    # roll
    a = attrLib.addFloat(footIkCtl.name, 'roll')
    upLimit = mc.createNode('clamp', n=name + 'UpperRollLimit_CLM')
    mc.connectAttr(a, upLimit + '.inputR')
    mc.setAttr(upLimit + '.maxR', 200)
    mc.connectAttr(upLimit + '.outputR', heelCtl.zro + '.rx')

    lowLimit = mc.createNode('clamp', n=name + 'LowerRollLimit_CLM')
    mc.connectAttr(a, lowLimit + '.inputR')
    mc.setAttr(lowLimit + '.minR', -200)
    mc.connectAttr(lowLimit + '.outputR', heelPivCtl.zro + '.rx')

    # tip
    a = attrLib.addFloat(footIkCtl.name, 'tip')
    mc.connectAttr(a, toePivCtl.zro + '.rx')

    # tip side to side
    a = attrLib.addFloat(footIkCtl.name, 'tipSideToSide')
    mc.connectAttr(a, toePivCtl.zro + '.ry')

    # connect control to rig
    mc.poleVectorConstraint(kneeIkCtl.name, legIkh, name=name + "_PVC")

    return (footIkCtl, kneeIkCtl), [legIkh]
