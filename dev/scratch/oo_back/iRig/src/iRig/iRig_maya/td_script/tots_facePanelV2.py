
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



# Repostion face panel pieces
def do_it():

    cmds.setAttr('Face_L_Eye_Blink_CrvObj_Slider_Grp.translateX', 101.203)
    cmds.setAttr('Face_R_Eye_Blink_CrvObj_Slider_Grp.translateX', 99.687)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.translateX', 0)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.translateY', 0)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.rotatePivotX', 0)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.rotatePivotY', 0)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.rotatePivotZ', 0)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.translateX', -5.212)
    cmds.setAttr('Face_Eye_Slider_Controls_Grp.translateY', 7.539)
    cmds.setAttr('Face_R_Eye_Blink_CrvObj_Slider_Grp.translateX', -1.025)
    cmds.setAttr('Face_R_Eye_Blink_CrvObj_Slider_Grp.translateY', -0.315)
    cmds.setAttr('Face_L_Eye_Blink_CrvObj_Slider_Grp.translateX', 0.418)
    cmds.setAttr('Face_L_Eye_Blink_CrvObj_Slider_Grp.translateY', -0.315)

    cmds.setAttr('Face_L_Eye_Blink_CrvObj_Slider_Title.visibility', lock=False)
    cmds.setAttr('Face_L_Eye_Blink_CrvObj_Slider_Title.visibility', 0, lock=True)
    cmds.setAttr('Face_R_Eye_Blink_CrvObj_Slider_Title.visibility', lock=False)
    cmds.setAttr('Face_R_Eye_Blink_CrvObj_Slider_Title.visibility', 0, lock=True)

    cmds.setAttr('Face_L_Eye_Lid_Upr_Ctrl_Offset_Grp.translateX', -2.169)
    cmds.setAttr('Face_L_Eye_Lid_Upr_Ctrl_Offset_Grp.translateY', 2.97)
    cmds.setAttr('Face_L_Eye_Lid_Lwr_Ctrl_Offset_Grp.translateX', -2.169)
    cmds.setAttr('Face_L_Eye_Lid_Lwr_Ctrl_Offset_Grp.translateY', 1.584)
    cmds.setAttr('Face_R_Eye_Lid_Upr_Ctrl_Offset_Grp.translateX', -7.912)
    cmds.setAttr('Face_R_Eye_Lid_Upr_Ctrl_Offset_Grp.translateY', 2.97)
    cmds.setAttr('Face_R_Eye_Lid_Lwr_Ctrl_Offset_Grp.translateX', -7.912)
    cmds.setAttr('Face_R_Eye_Lid_Lwr_Ctrl_Offset_Grp.translateY', 1.584)

    cmds.setAttr('Face_L_Brow_Ctrl_Offset_Grp.translateY', 5.478)
    cmds.setAttr('Face_R_Brow_Ctrl_Offset_Grp.translateY', 5.478)
    cmds.setAttr('Face_L_Brow_In_Ctrl_AutoFollow_Tfm.translateY', 0)
    cmds.setAttr('Face_L_Brow_Mid_Ctrl_AutoFollow_Tfm.translateY', 0)
    cmds.setAttr('Face_L_Brow_Out_Ctrl_AutoFollow_Tfm.translateY', 0)
    cmds.setAttr('Face_R_Brow_In_Ctrl_AutoFollow_Tfm.translateY', 0)
    cmds.setAttr('Face_R_Brow_Mid_Ctrl_AutoFollow_Tfm.translateY', 0)
    cmds.setAttr('Face_R_Brow_Out_Ctrl_AutoFollow_Tfm.translateY', 0)

    cmds.setAttr('Face_C_Brow_Ctrl_Offset_Grp.translateY', 4.6)

    cmds.delete('Face_C_Mouth_LipUpr_Move_Ctrl_Bsh')
    cmds.setAttr('Face_C_Mouth_LipUpr_Ctrl_AutoFollow_Tfm.translateY', -0.197)
    cmds.setAttr('Face_L_Mouth_LipUpr_Ctrl_AutoFollow_Tfm.translateX', 1.064)
    cmds.setAttr('Face_R_Mouth_LipUpr_Ctrl_AutoFollow_Tfm.translateX', -1.064)
    cmds.delete('Face_C_Mouth_LipLwr_Move_Ctrl_Bsh')
    cmds.setAttr('Face_C_Mouth_LipLwr_Ctrl_AutoFollow_Tfm.translateY', 0.13)
    cmds.setAttr('Face_L_Mouth_LipLwr_Ctrl_AutoFollow_Tfm.translateX', 1.064)
    cmds.setAttr('Face_R_Mouth_LipLwr_Ctrl_AutoFollow_Tfm.translateX', -1.064)

    cmds.setAttr('Face_L_Cheek_Ctrl_Offset_Grp.translateX', -0.289)
    cmds.setAttr('Face_L_Cheek_Ctrl_Offset_Grp.translateY', -1.004)
    cmds.setAttr('Face_R_Cheek_Ctrl_Offset_Grp.translateX', -9.829)
    cmds.setAttr('Face_R_Cheek_Ctrl_Offset_Grp.translateY', -1.004)

    if cmds.objExists('Face_L_Squint_Crv'):
        cmds.setAttr('Face_L_Squint_Crv.translateY', -1)
    cmds.setAttr('Face_L_Squint_Ctrl_Offset_Grp.translateY', -0.589)
    if cmds.objExists('Face_R_Squint_Crv'):
        cmds.setAttr('Face_R_Squint_Crv.translateY', -1)
    cmds.setAttr('Face_R_Squint_Ctrl_Offset_Grp.translateY', -0.589)

    if cmds.objExists('Face_Gui_Ctrl_Follow_Grp_parentConstraint1'):
        cmds.delete('Face_Gui_Ctrl_Follow_Grp_parentConstraint1')
    for a in cmds.listAttr('Face_Gui_Ctrl'):
        if a=='Follow':
            cmds.deleteAttr('Face_Gui_Ctrl.Follow')