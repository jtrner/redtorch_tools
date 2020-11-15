"""
name: fk.py

Author: Ehsan Hassani Moghaddam

History:
    06/04/16 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import jntLib
from ...lib import trsLib
from ...lib import attrLib
from ...lib import connect
from ...lib import control
from ...lib import strLib
from . import globalScale

# reload all imported modules from dev
import types

for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('python.'):
            reload(val)


def Fk(joints=[], parent="", shape="circle", scale=None, search='', replace='',
       hideLastCtl=True, connectGlobalScale=True, movable=True,
       lockHideAttrs=['s', 'v'], stretch=True, variableIconSize=True,upVector = [0,0,1], worldUp  = [0,0,1], aimVec = 'x'):
    """
    def for creating fk

    :param movable: if true, each control will point to next one, so controls
                    can be moved, the joint before will aim to it.
    """

    # guess iconSize if not given
    if not scale:
        scale = [1, 1, 1]
        if len(joints) > 1:
            iconSize = trsLib.getDistance(joints[0], joints[-1]) / (len(joints) - 1) * 0.4
            scale = [iconSize, iconSize, iconSize]

    # create controls
    fk_ctl_list = []
    for i in range(len(joints)):
        joint = joints[i]

        # adjust iconSize based on joint length
        if variableIconSize and i < len(joints) - 1:
            iconSize = trsLib.getDistance(joints[i], joints[i+1])
            scale = [iconSize, iconSize, iconSize]

        # add controls
        n = strLib.getDescriptor(joint) or joint
        n = n.replace(search, replace)
        fk_ctl = control.Control(descriptor=n,
                                 side=strLib.getPrefix(joint) or 'c',
                                 parent=None,
                                 shape=shape,
                                 scale=scale,
                                 orient=[1, 0, 0],
                                 matchTranslate=joint,
                                 matchRotate=joint,
                                 matchScale=joint,
                                 lockHideAttrs=lockHideAttrs,
                                 useSecondaryColors=True)

        # parent control
        if i == 0:  # first control
            if parent:
                fk_ctl.setParent(parent)
        else:  # other controls
            fk_ctl.setParent(fk_ctl_list[i - 1].fullName)

        # all controls list
        fk_ctl_list.append(fk_ctl)

    # connect control to rig
    if len(joints) == 1:  # only one joint
        connect.matrix(fk_ctl_list[0].name, joints[0])
        # mc.parentConstraint(fk_ctl_list[0].name, joints[0], name=string.mergeSuffix(joints[0])+"_PAR" )
    else:  # more than one joint chian
        if movable:
            for i in range(len(joints) - 1):
                joint = joints[i]
                ctl = fk_ctl_list[i]
                next_ctl = fk_ctl_list[i + 1]
                # translate connections
                mc.pointConstraint(ctl.fullName, joint, name=strLib.mergeSuffix(joint) + "_PTC")
                # rotation connections
                connect_rotate(ctl, next_ctl, joint, upVector,worldUp, aimVec)
                # scale connections
                if stretch:
                    if connectGlobalScale:
                        # first ctl's top group will have global scale attribute
                        topZro = fk_ctl_list[0].zro
                        attrLib.addFloat(topZro, 'globalScale', min=0.001, dv=1)
                        connect_scale(ctl, next_ctl, joint, topZro + '.globalScale')
                    else:
                        connect_scale(ctl, next_ctl, joint)
        else:
            for i in range(len(joints)):
                joint = joints[i]
                ctl = fk_ctl_list[i]
                mc.parentConstraint(ctl.fullName, joint, name=strLib.mergeSuffix(joint) + "_PAR")
                connect.direct(ctl.fullName, joint, attrs=['s'])

        if hideLastCtl:
            mc.hide(fk_ctl_list[-1].zro)

    return fk_ctl_list


def connect_rotate(ctl, next_ctl, joint,upVector,worldUp,aimVec):
    """
    rotate joint to match next controls direction
    """
    side = strLib.getPrefix(ctl.name)  # joint on right side's X direction is reversed
    if aimVec == 'x':
        if side == "R":
            aimVector = [-1, 0, 0]
        else:
            aimVector = [1, 0, 0]
    elif aimVec == 'y':
        if side == 'R':
            aimVector = [0, -1, 0]
        else:
            aimVector = [0, 1, 0]
    elif aimVec == 'z':
        if side == 'R':
            aimVector = [0, 0, -1]
        else:
            aimVector = [0, 0, 1]

    else:
        return


    mc.aimConstraint(next_ctl.fullName,
                     joint,
                     aimVector=aimVector,
                     worldUpType="objectrotation",
                     upVector=upVector,
                     worldUpVector=worldUp,
                     worldUpObject=ctl.fullName,
                     name=strLib.mergeSuffix(joint) + "_AMC")


def connect_scale(ctl, next_ctl, joint, globalScaleAttr=""):
    """
    scale joint to match distance between to controls    
    """
    distance_node_name = strLib.mergeSuffix(ctl.name) + "Stretch_DSB"
    distance_node = mc.createNode("distanceBetween", name=distance_node_name)

    mdn_node_name = strLib.mergeSuffix(ctl.name) + "Stretch_MDN"
    mdn_node = mc.createNode("multiplyDivide", name=mdn_node_name)

    mc.connectAttr(ctl.fullName + ".worldMatrix[0]", distance_node + ".inMatrix1")
    mc.connectAttr(next_ctl.fullName + ".worldMatrix[0]", distance_node + ".inMatrix2")
    mc.connectAttr(distance_node + ".distance", mdn_node + ".input1X")

    mc.setAttr(mdn_node + ".input2X", mc.getAttr(distance_node + ".distance"))
    mc.setAttr(mdn_node + ".operation", 2)

    mc.connectAttr(mdn_node + ".outputX", joint + ".scaleX", force=True)

    # make globally scalable
    if globalScaleAttr:
        globalScale.run(
            dist=mdn_node,
            globalScaleAttr=globalScaleAttr,
            name=strLib.mergeSuffix(mdn_node)
        )
