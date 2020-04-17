
# Follow Constraint

import pymel.core as pm
import maya.cmds as cmds
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.attributes as rig_attributes
import maya.mel as mel
from math import pow,sqrt




def do_it(selected, type):
    # please put the controls you want to add follows for, in the order they should appear:
    follow_sources = selected[:-1]
    target_ctrl_name = selected[-1]

    # make the mimic array:
    follow_mimics = []
    for ctrl in follow_sources:
        # look for gimbals
        gimbal_name = ctrl.replace("_Ctrl", "_Gimbal_Ctrl")
        if cmds.objExists(gimbal_name):
            follow_mimic = i_control.mimic_control_class(i_node.Node(gimbal_name))
            follow_mimics.append(follow_mimic.control)

        # add the controls if gimbal doesn't exist
        if cmds.objExists(gimbal_name)==False:
            follow_mimic = i_control.mimic_control_class(i_node.Node(ctrl))
            follow_mimics.append(follow_mimic.control)

    # indicates the control to add a follow switch to:
    target_ctrl = i_control.mimic_control_class(i_node.Node(target_ctrl_name))

    #clean old follow constraints
    if cmds.objExists(target_ctrl_name+'_Follow_Grp_'+type+'Constraint1'):
        cmds.delete(target_ctrl_name+'_Follow_Grp_'+type+'Constraint1')
    if cmds.objExists(target_ctrl_name+'.Follow'):
        cmds.deleteAttr(target_ctrl_name+'.Follow')

    follow_info = rig_attributes.create_follow_attr(control=target_ctrl.control, cns_type=type, options=follow_mimics)
    for i in cmds.ls(target_ctrl_name+'_Follow*Cnd', shortNames=True):
        try:
            (cmds.connectAttr(target_ctrl_name+'.Follow', i+'.firstTerm', force=True))
        except:
            pass

def prntSelected():
    sel = cmds.ls(sl=1)
    do_it(sel, 'parent')

def orntSelected():
    sel = cmds.ls(sl=1)
    do_it(sel, 'orient')

def pointSelected():
    sel = cmds.ls(sl=1)
    do_it(sel, 'point')