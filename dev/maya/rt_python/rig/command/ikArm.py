"""
name: ikArm.py

Author: Ehsan Hassani Moghaddam

History:
    06/09/16 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import trsLib
from ...lib import control

reload(trsLib)
reload(control)


def IkArm(joints,
          parent='',
          side='',
          prefix='',
          poleVec='',
          verbose=False):
    """
    def for creating ikArm
    """

    name = side + '_' + prefix

    # rig joints
    uparm_ik_jnt = joints[0]
    elbow_ik_jnt = joints[1]
    hand_ik_jnt = joints[2]

    iconSize = trsLib.getDistance(joints[0], joints[-1])

    # arm ik handle
    arm_ikh_and_eff = mc.ikHandle(solver='ikRPsolver',
                                  startJoint=uparm_ik_jnt,
                                  endEffector=hand_ik_jnt,
                                  name=name + '_IKH')
    arm_ikh = arm_ikh_and_eff[0]
    armIkZro = trsLib.insert(arm_ikh, name=arm_ikh.replace('IKH', 'ikh_ZRO'))

    # add controls
    hand_ik_ctl = control.Control(descriptor=prefix + '_hand_ik',
                                  side=side,
                                  parent=parent,
                                  shape='cube',
                                  scale=[iconSize * 0.2, iconSize * 0.2, iconSize * 0.2],
                                  matchTranslate=hand_ik_jnt,
                                  matchRotate=elbow_ik_jnt,
                                  matchScale=hand_ik_jnt,
                                  lockHideAttrs=['s', 'v'],
                                  verbose=verbose)
    elbow_ik_ctl = control.Control(descriptor=prefix + '_elbow_ik',
                                   side=side,
                                   parent=parent,
                                   shape='sphere',
                                   scale=[iconSize * 0.05, iconSize * 0.05, iconSize * 0.05],
                                   matchTranslate=poleVec,
                                   matchRotate=poleVec,
                                   lockHideAttrs=['r', 's', 'v'],
                                   verbose=verbose)

    # rotate ik hand ctl
    if side == 'R':
        mc.rotate(180, 0, 0, hand_ik_ctl.zro, r=True, os=True)

    # connect control to rig
    mc.poleVectorConstraint(elbow_ik_ctl.fullName, arm_ikh, name=name + '_ikh_PVC')
    mc.orientConstraint(hand_ik_ctl.fullName, hand_ik_jnt, mo=True, name=name + '_ik_jnt_ORI')
    mc.pointConstraint(hand_ik_ctl.fullName, armIkZro, name=name + '_ik_zro_PNT')

    # return
    return [hand_ik_ctl, elbow_ik_ctl], [arm_ikh]
