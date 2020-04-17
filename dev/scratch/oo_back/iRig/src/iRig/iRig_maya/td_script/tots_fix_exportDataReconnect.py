# define maya imports
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import math
import os
import random
import re

import maya_utils
import tex_utils
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO
import maya.cmds as cmds
import pymel.core as pm
import maya.cmds as cmds


def do_it(col=''):
#reconnect export data
    """
    Connects the eyes.
    """
    eyes = cmds.ls('*file1_ExportData.frameOffset')
    if not eyes:
        return 0
    if not col:
        node = re.search("(?<=_Eyes)(.*)(?=_DIFF)", eyes[0])
        if node:
            col = node.group(0)
    print("[Connect Export Data Color] :: {}".format(col))


    curve = '_Eye_Ramp_Input_AnimCurve'
    place = '_Eye_Projection_3DPlace'
    exportFile = ""
    if cmds.objExists('L_Chr_Eyes'+col+'_DIFF_CLR_file1_ExportData'):
        exportFile = '_Chr_Eyes'+col+'_DIFF_CLR_file1_ExportData'
    elif cmds.objExists('L_Chr_Eyes'+col+'_DIFF_CLR_file_ExportData'):
        exportFile = '_Chr_Eyes'+col+'_DIFF_CLR_file_ExportData'
    exportPlace = '_Chr_Eyes'+col+'_DIFF_CLR_place3dTexture_ExportData'

    if col:
        print "Export Fix"
        for side in ['L', 'R']:
            if cmds.objExists(side+curve):
                if cmds.objExists(side+exportFile):
                    if not cmds.isConnected(side+curve+'.output', side+exportFile+'.frameOffset'):
                        cmds.keyframe(side+curve, index = (1,1), valueChange = cmds.getAttr(side+exportFile+'.frameOffset'))
                        cmds.connectAttr(side+curve+'.output', side+exportFile+'.frameOffset', force=True)
                else:
                    print("[Connect Export Data Failed] Anim curve does not exist")
            else:
                print("[Connect Export Data Failed] Anim curve does not exist")

            if cmds.objExists(side+place):
                if cmds.objExists(side+exportPlace):
                    cmds.parentConstraint(side+place, side+exportPlace, maintainOffset=True)
                    cmds.scaleConstraint(side+place, side+exportPlace, maintainOffset=True)
    else:
        print "no colour"