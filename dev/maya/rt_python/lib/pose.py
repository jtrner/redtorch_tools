"""
name: pose.py

Author: Ehsan Hassani Moghaddam

History:

03/16/18 (ehassani)     first release!

"""
import maya.cmds as mc
import maya.OpenMaya as om

from . import trsLib
from . import jntLib
from . import strLib
from . import attrLib


# constants
BIPED_LEG_FK_CTLS = {'L': ['L_hipFk_CTL', 'L_kneeFk_CTL', 'L_footFk_CTL', 'L_ballFk_CTL'],
                     'R': ['R_hipFk_CTL', 'R_kneeFk_CTL', 'R_footFk_CTL', 'R_ballFk_CTL']}

BIPED_LEG_IK_CTLS = {'L': ['L_footIk_CTL', 'L_kneeIk_CTL'],
                     'R': ['R_footIk_CTL', 'R_kneeIk_CTL']}

BIPED_ARM_FK_CTLS = {'L': ['L_shoulderFk_CTL', 'L_elbowFk_CTL', 'L_handFk_CTL'],
                     'R': ['R_shoulderFk_CTL', 'R_elbowFk_CTL', 'R_handFk_CTL']}

BIPED_ARM_IK_CTLS = {'L': ['L_handIk_CTL', 'L_elbowIk_CTL'],
                     'R': ['R_handIk_CTL', 'R_elbowIk_CTL']}

BIPED_IK_HAND = {'L': 'L_handIk_CTL',
                 'R': 'R_handIk_CTL'}

BIPED_IK_ELBOW = {'L': 'L_elbowIk_CTL',
                  'R': 'R_elbowIk_CTL'}

BIPED_ARM_JNTS = {'L': ['L_shoulderFk_JNT', 'L_elbowFk_JNT', 'L_handFk_JNT'],
                  'R': ['R_shoulderFk_JNT', 'R_elbowFk_JNT', 'R_handFk_JNT']}


def getAllCtlOnRig(node=None):
    rigGrp = trsLib.getNS(node) + ':rig_GRP'
    if mc.objExists(rigGrp):
        childs = mc.listRelatives(rigGrp, ad=True)
        ctls = [x for x in childs if x.endswith('_CTL')]
        return ctls


def resetAsset(node=None):
    if not node:
        node = mc.ls(sl=True)
        if node:
            node = node[0]
    ctls = getAllCtlOnRig(node)
    if ctls:
        [trsLib.resetTRS(x) for x in ctls]


def bipedRecordTPose():
    bipedArmRecordTPose()
    bipedLegRecordTPose()


def bipedArmRecordTPose():
    for side in ['L', 'R']:
        for ctl in (BIPED_ARM_FK_CTLS[side] + \
                    BIPED_ARM_IK_CTLS[side]):
            recordPose(ctl, 'tPose')


def bipedLegRecordTPose():
    for side in ['L', 'R']:
        for ctl in (BIPED_LEG_FK_CTLS[side] + \
                    BIPED_LEG_IK_CTLS[side]):
            recordPose(ctl, 'tPose')


def bipedArmSetToTPose():
    """
    sets biped arm to T_pose
    """
    resetAsset('rig_GRP')

    for side in ['L', 'R']:
        # inputs
        jnts = BIPED_ARM_JNTS[side]
        fkCtls = BIPED_ARM_FK_CTLS[side]
        ikCtl = BIPED_IK_HAND[side]
        pvCtl = BIPED_IK_ELBOW[side]
        
        # create a temp IK joint chain form arm
        tmpJnts = jntLib.extract_from_to(jnts[0], jnts[2], search="_JNT", replace="_TMP")
        tmpIkhEff = mc.ikHandle(solver="ikRPsolver",
                                startJoint=tmpJnts[0],
                                endEffector=tmpJnts[2],
                                name="TMP_IKH")

        # create tPose group on top of ik control and parent it to last tmp hand jnt
        zro = trsLib.getZro(ikCtl)
        ikTPoseGrp = getTPoseGrp(ikCtl)
        mc.parent(ikTPoseGrp, tmpJnts[-1])
        
        # calculate position of hand when arm is fully straight
        start = om.MVector(*mc.xform(jnts[0], q=1, ws=1, t=1))
        mid = om.MVector(*mc.xform(jnts[1], q=1, ws=1, t=1))
        end = om.MVector(*mc.xform(jnts[2], q=1, ws=1, t=1))
        xDir = [-1, 1][(end - start).x > 0]
        length = (end - mid).length() + (mid - start).length()
        ikVec = start + om.MVector(length*xDir, 0, 0)
        mc.setAttr(tmpIkhEff[0]+'.t', ikVec.x, ikVec.y, ikVec.z)
        
        # create a temp poleVector and position it behind the elbow
        pvTPoseGrp = getTPoseGrp(pvCtl)
        pvPos = om.MVector(*mc.xform(tmpJnts[1], q=1, ws=1, t=1))
        pvDist = trsLib.getDistance(pvCtl, jnts[1])
        mc.xform(pvTPoseGrp, ws=True, t=[pvPos.x, pvPos.y, pvPos.z - pvDist])
        mc.xform(pvTPoseGrp, ws=True, ro=[0, 0, 0])
        mc.poleVectorConstraint(pvCtl, tmpIkhEff[0], name="TMP_PVC")

        # last joint shouldn't have orientation
        mc.setAttr(tmpJnts[2]+'.r', 0, 0, 0)
        mc.setAttr(tmpJnts[2]+'.jo', 0, 0, 0)

        # create tPose group on top of fk controls and match them to temp IK
        for jnt, ctl in zip(tmpJnts, fkCtls):
            tPoseGrp = getTPoseGrp(ctl)
            trsLib.match(tPoseGrp, jnt)

        # parent ik back to zro
        mc.parent(ikTPoseGrp, zro)

        # clean up
        mc.delete(tmpJnts)


def bipedArmGoToTPose(node=None):
    """
    sets biped arm to T_pose
    """
    ns = trsLib.getNS(node)
    for side in ['L', 'R']:
        nodes = BIPED_ARM_FK_CTLS[side] + BIPED_ARM_IK_CTLS[side]
        _genericGoToTPose(ns, nodes)


def bipedLegGoToTPose(node=None):
    """
    sets biped leg to T_pose
    """
    ns = trsLib.getNS(node)
    for side in ['L', 'R']:
        nodes = BIPED_LEG_FK_CTLS[side] + BIPED_LEG_IK_CTLS[side]
        _genericGoToTPose(ns, nodes)


def bipedGoToTPose(node=None):
    """
    sets biped to T_pose
    """
    bipedArmGoToTPose(node)
    bipedLegGoToTPose(node)


def _genericGoToTPose(ns=':', nodes=None):
    """
    sets given nodes to T_pose
    """
    if isinstance(nodes, basestring):
        nodes = [nodes]
    rigGrp = ns + ':rig_GRP'
    if not getAllCtlOnRig(rigGrp):
        return
    resetAsset(rigGrp)
    nodes = [ns + ':' + x for x in nodes]
    for ctl in nodes:
        tPoseGrp = getTPoseGrp(ctl)
        trs = [[0,0,0], [0,0,0], [1,1,1]]
        if mc.attributeQuery('tPose', node=ctl, exists=True):
            trs = eval(mc.getAttr(ctl+'.tPose'))
        trsLib.setTRS(tPoseGrp, trs)


def _genericGoToAPose(ns=':', nodes=None):
    """
    sets given nodes to A_pose
    """
    if isinstance(nodes, basestring):
        nodes = [nodes]
    rigGrp = ns + ':rig_GRP'
    if not getAllCtlOnRig(rigGrp):
        return
    resetAsset(rigGrp)
    nodes = [ns + ':' + x for x in nodes]
    for ctl in nodes:
        tPoseGrp = getTPoseGrp(ctl)
        trsLib.resetTRS(tPoseGrp)


def bipedArmGoToAPose(node=None):
    """
    sets biped arm to A_pose
    """
    ns = trsLib.getNS(node)
    for side in ['L', 'R']:
        nodes = BIPED_ARM_FK_CTLS[side] + BIPED_ARM_IK_CTLS[side]
        _genericGoToAPose(ns, nodes)


def bipedLegGoToAPose(node=None):
    """
    sets biped leg to A_pose
    """
    ns = trsLib.getNS(node)
    for side in ['L', 'R']:
        nodes = BIPED_LEG_FK_CTLS[side] + BIPED_LEG_IK_CTLS[side]
        _genericGoToAPose(ns, nodes)


def bipedGoToAPose(node=None):
    """
    sets biped leg to A_pose
    """
    bipedArmGoToAPose(node)
    bipedLegGoToAPose(node)


def recordPose(ctl, poseName):
    tPoseGrp = getTPoseGrp(ctl)
    aPose = trsLib.getTRS(tPoseGrp)
    attrLib.addString(ctl, poseName, v=str(aPose))


def getTPoseGrp(node):
    """
    adds an extra group on given node with '_TPO' suffix if it doesn't exist
    and return it
    """
    tPoseGrp = strLib.mergeSuffix(node) + '_TPO'
    if not mc.objExists(tPoseGrp):
        tPoseGrp = trsLib.insert(node, name=strLib.mergeSuffix(node) + '_TPO')[0]
    return tPoseGrp
