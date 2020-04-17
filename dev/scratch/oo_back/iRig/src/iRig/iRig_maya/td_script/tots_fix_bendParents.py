# define maya imports
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import math
import os
import random

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

def do_it():
#Fix bend leg parenting
    for side in ["L_", "R_"]:
        for end in ["Front", "Back"]:
            for pos in ["Top", "Mid", "Btm"]:
                if cmds.objExists(side+end+"Leg_Bend"+pos+"_Grp"):
                    if cmds.listRelatives(side+end+"Leg_Bend"+pos+"_Grp", parent=True)[0] != side+end+"Leg_Bend_Setup_Grp":
                        cmds.parent(side+end+"Leg_Bend"+pos+"_Grp", side+end+"Leg_Bend_Setup_Grp")