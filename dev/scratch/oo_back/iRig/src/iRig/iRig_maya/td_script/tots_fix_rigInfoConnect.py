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
import pymel.core as pm
import maya.cmds as cmds
def do_it():


# connect controls to rig info



    ctrls = cmds.ls(long=False, type='transform')

    newCtrls = []

    for c in ctrls:

        splitted = c.split("_")
        if "Ctrl" in splitted[len(splitted)-1]:
            newCtrls.append(c)

    conCount = 0
    for m in cmds.listAttr("Rig_Info", multi=True):
        if "Controls[" in m:
            conCount += 1

    for n in newCtrls:
        if not cmds.listConnections(n+".message"):
            cmds.connectAttr(n+".message", "Rig_Info.Controls["+str(conCount)+"]", force=True)
            print "Connected "+n
        conCount += 1

