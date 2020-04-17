"""
Organizes utility joints for both quadrupedal and bipedal characters.
"""
import icon_api.node as i_node
import icon_api.utils as i_utils
# define standard imports
import re
# define custom imports
import rig_tools.frankenstein.utils as rig_frankenstein_utils
# define maya imports
from maya import cmds

import ears_fix
import joint_label
import leg_fix
import pup_FrontLegClavUpgrade
import shoulder_follow_fix
import tots_facePanelV2
# import tots_fix_sub_brow_ctrls_Alex
import tots_fix_bendParents
# import local modules
import tots_fix_sub_brow_ctrls
import tots_fix_target_space
import tots_followConstraint
import tots_lidCtrlFix

# define private variables
__author__ = "Alexei Gaidachev and Michael Taylor"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Michael Taylor", "Alison Chan"]
__license__ = "ICON License"
__version__ = "1.2.1"
__maintainer__ = "Michael Taylor"
__email__ = "michaelt@iconcreativestudio.com"
__status__ = "Production"


def util_connect_attr(output_attr, input_attr):
    """
    Connect the attributes
    :param output_attr: <str> the output attriubte to connect to the input attribute.
    :param input_attr: <str> the input attribute to be connected into.
    """
    if not any([output_attr, input_attr]):
        return False
    if not cmds.isConnected(output_attr, input_attr, ignoreUnitConversion=1):
        cmds.connectAttr(output_attr, input_attr, f=1)
    return True


def connect_character_scale_offset():
    """
    Fixes the character scale offset.
    """
    root_name = 'Root_Ctrl'
    scale_name = 'ScaleXYZ'
    scale_offset_node_name = 'RigScaleOffset_MD'

    scale_plugs = cmds.listConnections('{}.{}'.format(root_name, scale_name), d=1, s=0, plugs=1)
    for plug in scale_plugs:
        print(plug)
        if scale_offset_node_name in plug:
            continue
        locked_attr = cmds.getAttr(plug, l=1)
        if locked_attr:
            if '.scale' in plug:
                new_plug = plug.rpartition('.')[0] + '.scale'
                print new_plug
                cmds.setAttr(new_plug, l=False)
            cmds.setAttr(plug, l=0)
        util_connect_attr(scale_offset_node_name + '.outputX', plug)
        if locked_attr:
            if '.scale' in plug:
                new_plug = plug.rpartition('.')[0] + '.scale'
                cmds.setAttr(new_plug, l=1)
            cmds.setAttr(plug, l=1)
    return True


def remove_unconnected_face_nodes():
    """
    Removes unconnected face panel nodes.
    :return: <bool> True for success.
    """
    selected = cmds.ls(sl=False, type='blendWeighted')
    for s in selected:
        destinations = cmds.listConnections(s, source=False, d=1, skipConversionNodes=True)
        if not destinations:
            print('[Face Nodes Removal] :: {}'.format(s))
            cmds.delete(s)
    return True





def label_joints():
    """
    Labels the joints accordingly.
    """
    joints = cmds.ls(type='joint')
    for j in joints:
        side = j.partition("_")[0].lower()
        if "c" in side:
            cmds.setAttr(j + '.side', 0)
        if "l" in side:
            cmds.setAttr(j + '.side', 1)
        if "r" in side:
            cmds.setAttr(j + '.side', 2)
        cmds.setAttr(j + '.type', 18)
        cmds.evalDeferred("cmds.setAttr('{0}.otherType', '{0}', type='string')".format(j))


def avg_joint_radius():
    """
    Averages out the bind joint radiuses.
    """
    joints = cmds.ls("*_Bnd_*", type='joint')
    radius = 0
    for j in joints:
        radius += cmds.getAttr(j+'.radius')
    avg_radius = radius / len(joints)
    for j in joints:
        cmds.setAttr(j+'.radius', avg_radius)


def tag_face_controls():
    """
    Tags the face curves for export.
    """
    manual_nodes = cmds.ls('*Tweak*Anm')
    manual_nodes_cnv = i_utils.convert_data(manual_nodes, to_generic=False)
    face_pack_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type" : "Face"})
    i_node.connect_to_info_node(node=face_pack_info_node[0], info_attribute="build_objects", objects=manual_nodes_cnv)


def organize_joints():
    """
    Organizes the joints for easier skinning.
    """
    legs_ls = ['{}_FrontLeg_Ik_Setup_Grp', '{}_FrontLeg_Fk_Setup_Grp', '{}_BackLeg_Ik_Setup_Grp',
               '{}_BackLeg_Fk_Setup_Grp', '{}_Leg_Ik_Setup_Grp', '{}_Leg_Fk_Setup_Grp']
    arms_ls = ['{}_Arm_Rig_Jnt_Grp']
    utility_jnt_ls = ["{}_BackLeg_Hip_Jnt", "{}_BackLeg_Knee_Jnt", "{}_BackLeg_Ankle_Jnt",
                      "{}_FrontLeg_Hip_Jnt", "{}_FrontLeg_Knee_Jnt", "{}_FrontLeg_Ankle_Jnt",
                      '{}_Hip_Base_Rig_Jnt']
    utility_attr = "Character.UtilityVis"
    leg_jnt_ls = ["{}_FrontLeg_BendTop_Grp", "{}_BackLeg_BendTop_Grp", "{}_BackLeg_BendMid_Grp",
                  "{}_FrontLeg_BendBtm_Grp"]
    side_vars = 'LR'
    leg_jnt_radius = []

    # connect the utility joints
    for side in side_vars:
        for leg in legs_ls:
            leg_attr = leg.format(side) + '.visibility'
            if not cmds.objExists(leg_attr):
                continue
            if not cmds.isConnected(utility_attr, leg_attr):
                cmds.connectAttr(utility_attr, leg_attr)

    # reparent the bound joints
    for side in side_vars:
        for leg_jnt in leg_jnt_ls:
            leg_name = leg_jnt.format(side)
            if not cmds.objExists(leg_name):
                continue
            if not cmds.listRelatives(leg_name, p=1)[0] == 'Jnt_Grp':
                cmds.parent(leg_name, 'Jnt_Grp')
        for arm_jnt in arms_ls:
            arm_name = arm_jnt.format(side)
            if not cmds.objExists(arm_name):
                continue
            cmds.connectAttr(utility_attr, arm_name + '.v')

    # get and set the average radius
    all_leg_jnts = cmds.ls('*Leg*', type='joint')
    if all_leg_jnts:
        for a_jnt in all_leg_jnts:
            leg_jnt_radius.append(cmds.getAttr(a_jnt + '.radius'))
        avg_radius = sum(leg_jnt_radius) / len(leg_jnt_radius)
        for a_jnt in all_leg_jnts:
            cmds.setAttr(a_jnt + '.radius', avg_radius)

    # resize the utility joints
    for side in side_vars:
        for jnt in utility_jnt_ls:
            jnt_attr = jnt.format(side) + '.radius'
            if not cmds.objExists(jnt_attr):
                continue
            cmds.setAttr(jnt_attr, 0.01)
    cmds.setAttr(utility_attr, 0)

    # hide leg joints
    for leg in cmds.ls('?_Leg_Hip_Jnt'):
        cmds.setAttr(leg + '.drawStyle', 2)
    for leg in cmds.ls('?_Leg_Knee_Jnt'):
        cmds.setAttr(leg + '.drawStyle', 2)


def face_gui_cleanup():
    """
    Cleans up the facial gui.
    """
    cmds.parent('Face_Lip_Slider_Controls_Grp', 'Face_C_Teeth_Lwr_Ctrl_Offset_Grp')
    cmds.parent('Face_Gui_Controls_Grp', 'Ctrl_Grp')
    cmds.hide(['Face_C_Teeth_Lwr_Ctrl_Offset_Grp', 'Face_C_Tongue_CrvObj_Slider_Grp', 'Face_C_Jaw_CrvObj_Slider_Grp', 'Face_C_Teeth_Upr_Ctrl_Offset_Grp', 'Face_C_LipSync_CrvObj_Slider_Grp', 'Face_L_LipCurl_CrvObj_Slider_Grp', 'Face_R_LipCurl_CrvObj_Slider_Grp'])
    if cmds.objExists('Face_Gui_Ctrl_Follow_Grp'):
        parent_cnst = cmds.listConnections('Face_Gui_Ctrl_Follow_Grp', type='parentConstraint', s=1, d=0)
        if parent_cnst:
            cmds.delete(parent_cnst)
        cmds.setAttr('Face_Gui_Ctrl_Follow_Grp.translateX', 0)
        cmds.setAttr('Face_Gui_Ctrl_Follow_Grp.translateY', 0)
        cmds.setAttr('Face_Gui_Ctrl_Follow_Grp.translateZ', 0)


def check_eyeball_setup():
    """
    Checks if the eyeball setup has been done.
    :return: <bool> True for yes, <bool> False for no.
    """
    eye_check = []
    obj_check = ['EyeProxys_Grp', 'EyeProjections_Grp']
    EYE_GEOS = ["{}_*_Eye_Geo", "{}_*Eyeball_Geo"]
    for eye_geo in EYE_GEOS:
        for side in 'LR':
            eye_check.extend(cmds.ls(eye_geo.format(side)))
    if eye_check:
        return True
    if any(map(cmds.objExists, obj_check)):
        return True


def fix_leg_aim():
    """
    Fixes the hip pivoting rotation problem.
    :return: <bool> True for success.
    """
    ground_ctrl = 'Ground_Gimbal_Ctrl'
    autoaim_origin_grps = cmds.ls('?_Leg_Hip_AutoAim_Origin_Grp')
    for side in 'LR':
        for origin_grp in autoaim_origin_grps:
            origin_grp = origin_grp.format(side)
            if not cmds.listConnections(origin_grp + '.tx', s=1, d=0, type='parentConstraint'):
                cmds.parentConstraint(ground_ctrl, origin_grp, mo=1)
            if not cmds.listConnections(origin_grp + '.sx', s=1, d=0, type='scaleConstraint'):
                cmds.scaleConstraint(ground_ctrl, origin_grp, mo=1)
    return True


def fix_eye_brow_alignment():
    """
    Align the eyes and the elyelids.
    :return: <bool> True for success.
    """
    jnts = [u'Face_L_Brow_01_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Brow_02_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Brow_03_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Upr_01_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Upr_02_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Upr_03_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Lwr_01_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Lwr_02_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Lwr_03_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Outer_Tweak_Ctrl_Offset_Grp',
            u'Face_L_Eye_Lid_Inner_Tweak_Ctrl_Offset_Grp']

    for j in jnts:
        targ = j.replace("L_", "R_")
        cmds.setAttr(targ + ".translateX", cmds.getAttr(j + ".translateX") * -1)
        cmds.setAttr(targ + ".translateY", cmds.getAttr(j + ".translateY"))
        cmds.setAttr(targ + ".translateZ", cmds.getAttr(j + ".translateZ"))
        cmds.setAttr(targ + ".rotateX", cmds.getAttr(j + ".rotateX"))
        cmds.setAttr(targ + ".rotateY", cmds.getAttr(j + ".rotateY") * -1)
        cmds.setAttr(targ + ".rotateZ", cmds.getAttr(j + ".rotateZ") * -1)
    return True


def fix_eye_ctrls():
    """
    Fix the eye controller X rotations.
    :return: <bool> True for success. <bool> False for failure.
    """
    aim_ctrls = cmds.ls('?_Eye_Aim*_Ctrl_Offset_Grp')
    if not aim_ctrls:
        return False
    for a_ctrl in aim_ctrls:
        values = cmds.getAttr(a_ctrl + '.rx')
        if values:
            cmds.setAttr(a_ctrl + '.rx', 0.0)
    return True


def fix_constraints():
    """
    Add constraints on the character to finalize it.
    :return: <bool> True for success. <bool> False for failure.
    """
    arm_autoaim = cmds.ls('?_Arm_Shoulder_AutoAim_Origin_Grp')
    ears = cmds.ls('?_Ear_01_Ctrl_Offset_Grp')
    tails = cmds.ls('?_Tail_01_Ctrl_Offset_Grp')
    tongue = cmds.ls('C_Tongue_01_Ctrl_Offset_Grp')
    head_ctrl = 'C_Head_Gimbal_Ctrl'
    hips_ctrl = 'C_Spine_Hips_Ctrl'
    jaw_ctrl = 'Face_C_Jaw_Tweak_Ctrl'
    gimbal_ctrl = 'Ground_Gimbal_Ctrl'
    if ears:
        for ear_ctrl in ears:
            if 'L_' in ear_ctrl:
                if cmds.objExists('Face_L_Ear_Tweak_Ctrl'):
                    cmds.parentConstraint('Face_L_Ear_Tweak_Ctrl', ear_ctrl, mo=1)
                    cmds.scaleConstraint('Face_L_Ear_Tweak_Ctrl', ear_ctrl, mo=1)
            else:
                if cmds.objExists('Face_R_Ear_Tweak_Ctrl'):
                    cmds.parentConstraint('Face_R_Ear_Tweak_Ctrl', ear_ctrl, mo=1)
                    cmds.scaleConstraint('Face_R_Ear_Tweak_Ctrl', ear_ctrl, mo=1)
    if tails:
        for tail_ctrl in tails:
            cmds.parentConstraint(hips_ctrl, tail_ctrl, mo=1)
            cmds.scaleConstraint(hips_ctrl, tail_ctrl, mo=1)
    if tongue:
        cmds.parentConstraint(jaw_ctrl, tongue[0], mo=1)
        cmds.scaleConstraint(jaw_ctrl, tongue[0], mo=1)
    if arm_autoaim:
        for auto in arm_autoaim:
            cmds.parentConstraint(gimbal_ctrl, auto, mo=1)
            cmds.scaleConstraint(gimbal_ctrl, auto, mo=1)
    return True


def remove_broken_face_nodes():
    """
    Face nodes to delete to make sure the face transfers successfully.
    :return: <bool> True for success.
    """
    for blnd in cmds.ls('Face_*_Blend'):
        blnd_cnn = cmds.listConnections(blnd, s=0, d=1, skipConversionNodes=1)
        if not blnd_cnn:
            print('[Deleting Useless Blnd Node] :: {}'.format(blnd))
            cmds.delete(blnd)
    return True


# Bendy flip fix
def bendyFlipFix():
    chain = ['Top', 'Btm']
    end = ['Start', 'End']
    side = ['L', 'R']

    for s in side:
        for c in chain:
            for e in end:

                twistGrp = s+'_Arm_'+c+'_Bend_'+e+'_Ctrl_Ik_Xtra_Grp'

                prnt = s+'_Arm_'+c+'_Bend_'+e+'_Ctrl_Cns_Grp'

                if cmds.objExists(prnt):
                    prv = ''
                    targ = ''
                    ctrlPrnt = ''
                    ignore = False
                    print prnt
                    if c=='Top':
                        if e=='Start':
                            targ = s+'_Arm_Elbow_Jnt'
                            ctrlPrnt = s+'_Arm_Top_Bend_Start_Ctrl_Shoulder_AutoAim_Wrist_Grp'
                            conversion = cmds.listConnections(s+'_Arm_Top_Bend_Start_Ctrl_Shoulder_AutoAim_Wrist_Grp.rotateY')[0]
                            cmds.disconnectAttr(conversion+'.output', ctrlPrnt+'.rotateY')
                            # prv = s+'_Arm_Shoulder_Jnt'
                            prv = s+'_Clavicle_Base_Bnd_Jnt'
                        elif e=='End':
                            ignore = True  # targ = s+'_Arm_Shoulder_Jnt'  # ctrlPrnt = s+'_Arm_Top_Bend_End_Ctrl_Aim_Grp'  # prv = s+'_Arm_Elbow_Jnt'
                    if c=='Btm':

                        prv = s+'_Arm_Elbow_Jnt'
                        if e=='Start':
                            ignore = True  # targ = s+'_Arm_Elbow_Jnt'  # ctrlPrnt = s+'_Arm_Btm_Bend_Start_Ctrl_Aim_Grp'  # prv = s+'_Arm_Shoulder_Jnt'
                        elif e=='End':
                            targ = s+'_Arm_Elbow_Jnt'
                            ctrlPrnt = s+'_Arm_Btm_Bend_End_Ctrl_Wrist_AutoAim_Shoulder_Xtra_Grp'
                            prv = s+'_Arm_Wrist_Jnt'

                    if not ignore:

                        grp = cmds.createNode('transform', name=s+'_Arm_'+c+'_Bend_'+e+'_Twist_Driver_Loc_Grp')

                        drvr = cmds.spaceLocator(name=s+'_Arm_'+c+'_Bend_'+e+'_Twist_Driver_Loc')[0]

                        cmds.parent(drvr, grp)
                        cmds.parent(grp, prnt)

                        cmds.setAttr(grp+'.translateX', 0)
                        cmds.setAttr(grp+'.translateY', 0)
                        cmds.setAttr(grp+'.translateZ', 0)
                        cmds.setAttr(grp+'.rotateX', 0)
                        cmds.setAttr(grp+'.rotateY', 0)
                        cmds.setAttr(grp+'.rotateZ', 0)
                        cmds.setAttr(grp+'.scaleX', 1)
                        cmds.setAttr(grp+'.scaleY', 1)
                        cmds.setAttr(grp+'.scaleZ', 1)

                        cmds.parentConstraint(prv, grp, maintainOffset=True)
                        if s=='R':
                            cmds.aimConstraint(targ, drvr, aimVector=(0, -1, 0), upVector=(0, 0, 0), worldUpType='none', maintainOffset=True)
                        else:
                            cmds.aimConstraint(targ, drvr, aimVector=(0, 1, 0), upVector=(0, 0, 0), worldUpType='none', maintainOffset=True)

                        # cmds.pointConstraint(targ, drvr, maintainOffset=True)

                        if cmds.objExists(twistGrp):
                            cmds.parent(twistGrp, drvr)
                            cmds.parent(ctrlPrnt, twistGrp)
                        else:
                            cmds.parent(ctrlPrnt, drvr)


                else:
                    print 'Unable to build '+s+', '+c+', '+e+'. '+prnt+' missing.'
    return True

def fixIkFollows():
    sides = ['L', 'R']
    for side in sides:
        #Biped
        if cmds.objExists(side+'_Arm_Wrist_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_Arm_AnimConstraint_Ctrl', 'C_Spine_Chest_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl', side+'_Arm_Wrist_Ik_Ctrl'], 'parent')
        if cmds.objExists(side+'_Arm_Wrist_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_Leg_AnimConstraint_Ctrl', side+'_Hip_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_Leg_Ankle_Ik_Ctrl'], 'parent')
        if cmds.objExists(side+'_Leg_Ankle_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_Leg_AnimConstraint_Ctrl', side+'_Hip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_Leg_Ankle_Ik_Ctrl'], 'parent')

            # Pole Vectors
            origPos = cmds.xform(side+'_Leg_PoleVector_Ctrl_Offset_Grp', query=True, translation=True)
            cmds.delete(side+'_Leg_PoleVector_Ctrl_Follow_Grp_pointConstraint1')
            cmds.setAttr(side+'_Leg_PoleVector_Ctrl_Follow_Grp.translateX', 0)
            cmds.setAttr(side+'_Leg_PoleVector_Ctrl_Follow_Grp.translateY', 0)
            cmds.setAttr(side+'_Leg_PoleVector_Ctrl_Follow_Grp.translateZ', 0)
            temp = cmds.pointConstraint(side+'_Leg_Ankle_Ik_Ctrl', side+'_Leg_PoleVector_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)
            cmds.xform(side+'_Leg_PoleVector_Ctrl_Offset_Follow_Grp', translation=origPos, worldSpace=True)
            tots_followConstraint.do_it([side+'_Leg_Ankle_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_Leg_PoleVector_Ctrl'], 'point')
        #Weird butterfly extra arms
        if cmds.objExists(side+'_Arm_02_Wrist_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_Arm_02_AnimConstraint_Ctrl', 'C_Spine_Chest_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl', side+'_Arm_02_Wrist_Ik_Ctrl'], 'parent')
        #Quadrepred
        if cmds.objExists(side+'_FrontLeg_Foot_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_FrontLeg_AnimConstraint_Ctrl', side+'_FrontHip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_FrontLeg_Foot_Ik_Ctrl'], 'parent')

            # Pole Vectors
            origPos = cmds.xform(side+'_FrontLeg_PoleVector_Ctrl_Offset_Grp', query=True, translation=True)
            cmds.delete(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp_pointConstraint1')
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateX', 0)
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateY', 0)
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateZ', 0)
            temp = cmds.pointConstraint(side+'_FrontLeg_Foot_Ik_Ctrl', side+'_FrontLeg_PoleVector_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)
            cmds.xform(side+'_FrontLeg_PoleVector_Ctrl_Offset_Follow_Grp', translation=origPos, worldSpace=True)
            tots_followConstraint.do_it([side+'_FrontLeg_Foot_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_FrontLeg_PoleVector_Ctrl'], 'point')

        if cmds.objExists(side+'_BackLeg_Foot_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_BackLeg_AnimConstraint_Ctrl', side+'_BackHip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_BackLeg_Foot_Ik_Ctrl'], 'parent')

            #Pole Vectors
            origPos = cmds.xform(side+'_BackLeg_PoleVector_Ctrl_Offset_Grp', query=True, translation=True)
            cmds.delete(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp_pointConstraint1')
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateX', 0)
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateY', 0)
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateZ', 0)
            temp = cmds.pointConstraint(side+'_BackLeg_Foot_Ik_Ctrl', side+'_BackLeg_PoleVector_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)
            cmds.xform(side+'_BackLeg_PoleVector_Ctrl_Offset_Follow_Grp', translation=origPos, worldSpace=True)
            tots_followConstraint.do_it([side+'_BackLeg_Foot_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_BackLeg_PoleVector_Ctrl'], 'point')

        #Digigrade
        if cmds.objExists(side+'_FrontLeg_Ankle_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_FrontLeg_AnimConstraint_Ctrl', side+'_FrontHip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_FrontLeg_Ankle_Ik_Ctrl'], 'parent')

            # Pole Vectors
            origPos = cmds.xform(side+'_FrontLeg_PoleVector_Ctrl_Offset_Grp', query=True, translation=True)
            cmds.delete(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp_pointConstraint1')
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateX', 0)
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateY', 0)
            cmds.setAttr(side+'_FrontLeg_PoleVector_Ctrl_Follow_Grp.translateZ', 0)
            temp = cmds.pointConstraint(side+'_FrontLeg_Ankle_Ik_Ctrl', side+'_FrontLeg_PoleVector_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)
            cmds.xform(side+'_FrontLeg_PoleVector_Ctrl_Offset_Follow_Grp', translation=origPos, worldSpace=True)
            tots_followConstraint.do_it([side+'_FrontLeg_Ankle_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_FrontLeg_PoleVector_Ctrl'], 'point')

        if cmds.objExists(side+'_BackLeg_Ankle_Ik_Ctrl'):
            tots_followConstraint.do_it([side+'_BackLeg_AnimConstraint_Ctrl', side+'_BackHip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_BackLeg_Ankle_Ik_Ctrl'], 'parent')

            # Pole Vectors
            origPos = cmds.xform(side+'_BackLeg_PoleVector_Ctrl_Offset_Grp', query=True, translation=True)
            cmds.delete(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp_pointConstraint1')
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateX', 0)
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateY', 0)
            cmds.setAttr(side+'_BackLeg_PoleVector_Ctrl_Follow_Grp.translateZ', 0)
            temp = cmds.pointConstraint(side+'_BackLeg_Ankle_Ik_Ctrl', side+'_BackLeg_PoleVector_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)
            cmds.xform(side+'_BackLeg_PoleVector_Ctrl_Offset_Follow_Grp', translation=origPos, worldSpace=True)
            tots_followConstraint.do_it([side+'_BackLeg_Ankle_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_BackLeg_PoleVector_Ctrl'], 'point')




def wingPostBuild():
    sides = ['L', 'R']
    for side in sides:

        # create wing tip ik controls
        if cmds.objExists(side+'_Wing_Info'):
            def makeCtrl(pos, nm):
                ctrl = nm+'_Ctrl'
                cns = nm+'_Ctrl_Cns_Grp'
                off = nm+'_Ctrl_Offset_Grp'
                # print pos

                cmds.group(empty=1, name=off)
                par = cmds.parentConstraint(pos, off, maintainOffset=False)
                cmds.delete(par)
                cmds.group(empty=1, name=cns, parent=off)

                cmds.circle(ch=0, n=ctrl)
                cmds.setAttr(ctrl+'Shape'+'.overrideEnabled', 1)
                cmds.setAttr(ctrl+'Shape'+'.overrideColor', 18)

                circ1 = cmds.duplicate(ctrl)
                circ2 = cmds.duplicate(ctrl)

                circ1Cvs = circ1[0]+'.cv[*]'
                cmds.select(circ1Cvs, r=1)
                cmds.rotate(90, 0, 0, r=1, os=1)

                circ1Shape = circ1[0]+'Shape'
                cmds.parent(circ1Shape, ctrl, r=1, s=1)
                cmds.setAttr(circ1Shape+'.overrideEnabled', 1)
                cmds.setAttr(circ1Shape+'.overrideColor', 18)
                cmds.rename(circ1Shape, circ1Shape.replace('1Shape', 'Shape1'))
                cmds.delete(circ1)

                circ2Cvs = circ2[0]+'.cv[*]'
                cmds.select(circ2Cvs, r=1)
                cmds.rotate(0, 90, 0, r=1, os=1)
                cmds.select(d=1)

                circ2Shape = circ2[0]+'Shape'
                cmds.parent(circ2Shape, ctrl, r=1, s=1)
                cmds.setAttr(circ2Shape+'.overrideEnabled', 1)
                cmds.setAttr(circ2Shape+'.overrideColor', 18)
                cmds.rename(circ2Shape, circ2Shape.replace('2Shape', 'Shape2'))
                cmds.delete(circ2)
                cmds.parent(ctrl, cns)
                cmds.setAttr(ctrl+'.tx', 0)
                cmds.setAttr(ctrl+'.ty', 0)
                cmds.setAttr(ctrl+'.tz', 0)
                cmds.setAttr(ctrl+'.rx', 0)
                cmds.setAttr(ctrl+'.ry', 0)
                cmds.setAttr(ctrl+'.rz', 0)

                return (off, cns, ctrl)

            jnts = []
            # ctrl 1
            ctrl = makeCtrl(side+'_Wing_FeatherTip_Foll_1_ClsHandle', side+'_Wing_FeatherTip_Ik_01')
            cmds.parent(ctrl[0], side+'_Wing_Ctrl_Grp')
            cons = cmds.parentConstraint(side+'_Wing_BaseOffset_2_Ctrl', ctrl[0], maintainOffset=True)
            cmds.scaleConstraint(side+'_Wing_BaseOffset_2_Ctrl', ctrl[0], maintainOffset=True)
            cmds.setAttr(cons[0]+'.interpType', 0)

            jnt = cmds.joint(name=side+'_Wing_Tip_1_Ctrl_Jnt')
            cmds.parentConstraint(ctrl[2], jnt, maintainOffset=False)
            cmds.scaleConstraint(ctrl[2], jnt, maintainOffset=False)
            jnts.append(jnt)

            # ctrl 2
            ctrl = makeCtrl(side+'_Wing_FeatherTip_Foll_6_ClsHandle', side+'_Wing_FeatherTip_Ik_02')
            cmds.parent(ctrl[0], side+'_Wing_Ctrl_Grp')
            cmds.parentConstraint(side+'_Wing_BaseOffset_3_Ctrl', ctrl[0], maintainOffset=True)
            cmds.scaleConstraint(side+'_Wing_BaseOffset_3_Ctrl', ctrl[0], maintainOffset=True)

            jnt = cmds.joint(name=side+'_Wing_Tip_2_Ctrl_Jnt')
            cmds.parentConstraint(ctrl[2], jnt, maintainOffset=False)
            cmds.scaleConstraint(ctrl[2], jnt, maintainOffset=False)
            jnts.append(jnt)

            # ctrl 3
            ctrl = makeCtrl(side+'_Wing_FeatherTip_Foll_9_ClsHandle', side+'_Wing_FeatherTip_Ik_03')
            cmds.parent(ctrl[0], side+'_Wing_Ctrl_Grp')
            cons = cmds.parentConstraint(side+'_Wing_BaseOffset_3_Ctrl', ctrl[0], maintainOffset=True)
            cmds.scaleConstraint(side+'_Wing_BaseOffset_3_Ctrl', ctrl[0], maintainOffset=True)
            cmds.parentConstraint(side+'_Wing_BaseOffset_4_Ctrl', ctrl[0], maintainOffset=True)
            cmds.scaleConstraint(side+'_Wing_BaseOffset_4_Ctrl', ctrl[0], maintainOffset=True)
            cmds.setAttr(cons[0]+'.interpType', 0)

            jnt = cmds.joint(name=side+'_Wing_Tip_3_Ctrl_Jnt')

            #fixes flipping
            loc1 = cmds.createNode('transform', name=side+'_Wing_BaseOffset_4_Loc')
            cmds.parent(loc1, side+'_Wing_BaseOffset_4_Ctrl')
            temp = cmds.parentConstraint(side+'_Wing_FeatherTip_Ik_03_Ctrl', loc1, maintainOffset=False)
            cmds.delete(temp[0])
            loc2 = cmds.createNode('transform', name=side+'_Wing_BaseOffset_3_Loc')
            cmds.parent(loc2, side+'_Wing_BaseOffset_3_Ctrl')
            temp = cmds.parentConstraint(side+'_Wing_FeatherTip_Ik_03_Ctrl', loc2, maintainOffset=False)
            cmds.delete(temp[0])
            cmds.setAttr(side+'_Wing_FeatherTip_Ik_03_Ctrl_Offset_Grp.rotateOrder', 4)
            pc = cmds.parentConstraint(loc1, side+'_Wing_FeatherTip_Ik_03_Ctrl_Offset_Grp', maintainOffset=True)
            pc = cmds.parentConstraint(loc2, side+'_Wing_FeatherTip_Ik_03_Ctrl_Offset_Grp', maintainOffset=True)
            cmds.setAttr(pc[0]+'.interpType', 2)
            cmds.scaleConstraint(loc1, side+'_Wing_FeatherTip_Ik_03_Ctrl_Offset_Grp')
            cmds.scaleConstraint(loc2, side+'_Wing_FeatherTip_Ik_03_Ctrl_Offset_Grp')

            cmds.parentConstraint(ctrl[2], jnt, maintainOffset=False)
            cmds.scaleConstraint(ctrl[2], jnt, maintainOffset=False)
            jnts.append(jnt)


            # ctrl 4
            ctrl = makeCtrl(side+'_Wing_FeatherTip_Foll_13_ClsHandle', side+'_Wing_FeatherTip_Ik_04')
            cmds.parent(ctrl[0], side+'_Wing_Ctrl_Grp')
            cmds.parentConstraint(side+'_Wing_BaseOffset_4_Ctrl', ctrl[0], maintainOffset=True)
            cmds.scaleConstraint(side+'_Wing_BaseOffset_4_Ctrl', ctrl[0], maintainOffset=True)

            jnt = cmds.joint(name=side+'_Wing_Tip_4_Ctrl_Jnt')
            cmds.parentConstraint(ctrl[2], jnt, maintainOffset=False)
            cmds.scaleConstraint(ctrl[2], jnt, maintainOffset=False)
            jnts.append(jnt)

            cmds.parent(jnts, side+'_Wing_Ik_Grp')

            # kill old follicles
            cmds.delete(side+'_Wing_FeatherTip_Cls_Grp')

            # create visual wing tip
            surf = side+'_Wing_FeatherTip_Surf'
            visualSurf = cmds.duplicate(surf)
            cmds.rename(visualSurf, side+'_Wing_FeatherTip_Ref_Surf')
            visualSurf = side+'_Wing_FeatherTip_Ref_Surf'
            cmds.parent(visualSurf, side+'_Wing_Ctrl_Grp')
            cmds.setAttr(visualSurf+'.overrideEnabled', 0)
            cmds.setAttr(visualSurf+'.overrideDisplayType', 0)
            cmds.setAttr(visualSurf+'Shape.castsShadows', 0)
            cmds.setAttr(visualSurf+'Shape.receiveShadows', 0)
            cmds.setAttr(visualSurf+'Shape.motionBlur', 0)
            cmds.setAttr(visualSurf+'Shape.primaryVisibility', 0)
            cmds.setAttr(visualSurf+'Shape.smoothShading', 0)
            cmds.setAttr(visualSurf+'Shape.visibleInReflections', 0)
            cmds.setAttr(visualSurf+'Shape.visibleInRefractions', 0)
            cmds.setAttr(visualSurf+'Shape.hideOnPlayback', 0)

            # skin surface
            cmds.skinCluster(jnts, surf, toSelectedBones=True)
            cmds.skinCluster(jnts, visualSurf, toSelectedBones=True)

            cmds.setAttr(visualSurf+'Shape.template', 1)

            # reconstrain armpit
            if cmds.objExists(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_parentConstraint1'):
                cmds.delete(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_parentConstraint1')
            if cmds.objExists(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_scaleConstraint1'):
                cmds.delete(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_scaleConstraint1')
            cons = cmds.parentConstraint('C_Spine_Chest_Gimbal_Ctrl', side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp', maintainOffset=True)
            cmds.scaleConstraint('C_Spine_Chest_Gimbal_Ctrl', side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp', maintainOffset=True)
            cmds.parentConstraint(side+'_Arm_Top_Bend_Start_Ctrl_Ik_Xtra_Grp', side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp', maintainOffset=True)
            cmds.scaleConstraint(side+'_Arm_Top_Bend_Start_Ctrl_Ik_Xtra_Grp', side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp', maintainOffset=True)
            cmds.setAttr(cons[0]+'.interpType', 3)

            # Fix thumb FK orientation on left side
            cmds.setAttr('L_Wing_Feather01_Start_Fk_Ctrl_Offset_Grp.rotateY', -90)

            # Add "Hand" mode
            cmds.addAttr(side+'_Arm_IKFKSwitch_Ctrl', ln='Hand_Override', at='enum', k=1, en='Wing:Hand')
            rev = cmds.createNode('reverse', n=side+'_hand_Override_Rev')
            cmds.connectAttr(side+'_Arm_IKFKSwitch_Ctrl.Hand_Override', rev+'.inputX')
            for feath in ['01_', '02_', '03_', '04_', '05_']:
                offsets = cmds.ls(side+'_Wing_Feather'+feath+'*Ctrl_Offset_Grp')
                cns = cmds.ls(side+'_Wing_Feather'+feath+'*Ctrl_Cns_Grp')
                for i in range(len(offsets)):
                    bcT = cmds.createNode('blendColors', n=(offsets[i].replace('_Fk_Tweak_Ctrl_Offset_Grp', '_Trans_Blend')))
                    bcR = cmds.createNode('blendColors', n=(offsets[i].replace('_Fk_Tweak_Ctrl_Offset_Grp', '_Rot_Blend')))
                    cmds.connectAttr(rev+'.outputX', bcT+'.blender')
                    cmds.connectAttr(rev+'.outputX', bcR+'.blender')
                    my_jnt = offsets[i].replace('_Fk_Ctrl_Offset_Grp', '_Jnt')
                    cmds.connectAttr(my_jnt+'.t', bcT+'.color1')
                    cmds.connectAttr(my_jnt+'.r', bcR+'.color1')
                    pbt = cmds.getAttr(bcT+'.color1')
                    pbr = cmds.getAttr(bcR+'.color1')
                    cmds.setAttr(bcT+'.color2', round(pbt[0][0], 3), round(pbt[0][1], 3), round(pbt[0][2], 3))
                    cmds.setAttr(bcR+'.color2', round(pbr[0][0], 3), round(pbr[0][1], 3), round(pbr[0][2], 3))
                    cmds.connectAttr(bcT+'.output', offsets[i]+'.t', f=1)
                    cmds.connectAttr(bcR+'.output', cns[i]+'.r', f=1)
            hand_off = cmds.group(em=1, n=side+'_Hand_Offset_Grp', p=side+'_Wing_BaseOffset_4_Ctrl')
            cmds.parent(hand_off, side+'_Wing_FkCtrl_Grp')
            hand_cns = cmds.group(em=1, n=side+'_Hand_Cons_Grp', p=hand_off)
            hand_xtra = cmds.group(em=1, n=side+'_Hand_Xtra_Grp')
            cmds.parent(hand_xtra, hand_cns)

            cmds.parentConstraint(side+'_Wing_BaseOffset_4_Ctrl', hand_cns, mo=0)
            cmds.connectAttr(side+'_Arm_IKFKSwitch_Ctrl.Hand_Override', side+'_Hand_Cons_Grp_parentConstraint1.'+side+'_Wing_BaseOffset_4_CtrlW0')

            bcTip = cmds.createNode('blendColors', n=side+'_WingFeathers_Tip_Blend')
            bcBase = cmds.createNode('blendColors', n=side+'_WingFeathers_Base_Blend')
            cmds.connectAttr(rev+'.outputX', bcTip+'.blender')
            cmds.connectAttr(rev+'.outputX', bcBase+'.blender')
            cmds.setAttr(bcTip+'.color1R', 0.8)
            cmds.setAttr(bcTip+'.color1G', 0.8)
            cmds.setAttr(bcTip+'.color1B', 0.8)
            cmds.setAttr(bcTip+'.color2R', 0)
            cmds.setAttr(bcTip+'.color2G', 0)
            cmds.setAttr(bcTip+'.color2B', 0)
            cmds.setAttr(bcBase+'.color1R', 0.167)
            cmds.setAttr(bcBase+'.color1G', 0.333)
            cmds.setAttr(bcBase+'.color1B', 0.5)
            cmds.setAttr(bcBase+'.color2R', 0)
            cmds.setAttr(bcBase+'.color2G', 0)
            cmds.setAttr(bcBase+'.color2B', 0)
            for each_grp in ['01', '02', '03', '04', '05']:
                cmds.parent(side+'_Wing_Feather'+each_grp+'_Start_Fk_Ctrl_Offset_Grp', hand_xtra)

            # Reduce Wing FK controls
            attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
            for num in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:

                if cmds.objExists(side+'_Wing_Feather'+num+'_00_Fk_Ctrl_Xtra_Grp'):
                    if cmds.objExists(side+'_Wing_Feather'+num+'_Start_Fk_Ctrl'):
                        for attr in ['.rx', '.ry', '.rz']:
                            cmds.connectAttr(side+'_Wing_Feather'+num+'_Start_Fk_Ctrl'+attr, side+'_Wing_Feather'+num+'_00_Fk_Ctrl_Xtra_Grp'+attr)
                        cmds.disconnectAttr('Control_Ctrl.'+side+'_Wing', side+'_Wing_Feather'+num+'_00_Fk_CtrlShape.visibility')
                        cmds.setAttr(side+'_Wing_Feather'+num+'_00_Fk_CtrlShape.visibility', 0, lock=True)
                        for a in attrs:
                            cmds.setAttr(side+'_Wing_Feather'+num+'_00_Fk_Ctrl.'+a, lock=True)
                if cmds.objExists(side+'_Wing_Feather'+num+'_02_Fk_Ctrl_Xtra_Grp'):
                    if cmds.objExists(side+'_Wing_Feather'+num+'_01_Fk_Ctrl'):
                        for attr in ['.rx', '.ry', '.rz']:
                            cmds.connectAttr(side+'_Wing_Feather'+num+'_01_Fk_Ctrl'+attr, side+'_Wing_Feather'+num+'_02_Fk_Ctrl_Xtra_Grp'+attr)
                        cmds.disconnectAttr('Control_Ctrl.'+side+'_Wing', side+'_Wing_Feather'+num+'_02_Fk_CtrlShape.visibility')
                        cmds.setAttr(side+'_Wing_Feather'+num+'_02_Fk_CtrlShape.visibility', 0, lock=True)
                        for a in attrs:
                            cmds.setAttr(side+'_Wing_Feather'+num+'_02_Fk_Ctrl.'+a, lock=True)
                if cmds.objExists(side+'_Wing_Feather'+num+'_02_Fk_Ctrl_Xtra_Grp'):
                    if cmds.objExists(side+'_Wing_Feather'+num+'_03_Fk_Ctrl'):
                        for attr in ['.rx', '.ry', '.rz']:
                            cmds.connectAttr(side+'_Wing_Feather'+num+'_03_Fk_Ctrl'+attr, side+'_Wing_Feather'+num+'_End_Fk_Ctrl_Xtra_Grp'+attr)
                        cmds.disconnectAttr('Control_Ctrl.'+side+'_Wing', side+'_Wing_Feather'+num+'_End_Fk_CtrlShape.visibility')
                        cmds.setAttr(side+'_Wing_Feather'+num+'_End_Fk_CtrlShape.visibility', 0, lock=True)
                        for a in attrs:
                            cmds.setAttr(side+'_Wing_Feather'+num+'_End_Fk_Ctrl.'+a, lock=True)

            cmds.setAttr(side+'_Wing_Feather07_End_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)
            cmds.setAttr(side+'_Wing_Feather08_End_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)
            cmds.setAttr(side+'_Wing_Feather09_End_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)
            cmds.setAttr(side+'_Wing_Feather10_End_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)
            cmds.setAttr(side+'_Wing_Feather11_End_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)
            cmds.setAttr(side+'_Wing_Feather12_Start_Fk_Ctrl_Xtra_Grp.visibility', 0, lock=True)

            for a in attrs:
                cmds.setAttr(side+'_Wing_Feather07_End_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather08_End_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather09_End_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather10_End_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather11_End_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather12_Start_Fk_Ctrl.'+a, lock=True)
                cmds.setAttr(side+'_Wing_Feather12_End_Fk_Ctrl.'+a, lock=True)

            # This will add the Knee flipping functionality for birds (could be edited for arm)
            cmds.addAttr(side+'_Leg_PoleVector_Ctrl', at='float', ln='KneeFlip', dv=0, k=1, min=0, max=1, h=0)
            my_Blend = cmds.createNode('blendColors', n=side+'_kneeFlip_Blnd')
            cmds.connectAttr(side+'_Leg_PoleVector_Ctrl.KneeFlip', my_Blend+'.blender')
            my_val = cmds.getAttr(side+'_Leg_PoleVector_Ctrl_Offset_Follow_Grp.tz')
            cmds.setAttr(my_Blend+'.color1R', -my_val)
            cmds.setAttr(my_Blend+'.color1G', -1)
            cmds.setAttr(my_Blend+'.color2R', my_val)
            cmds.setAttr(my_Blend+'.color2G', 1)
            cmds.connectAttr(my_Blend+'.outputR', side+'_Leg_PoleVector_Ctrl_Offset_Follow_Grp.tz')
            cmds.connectAttr(my_Blend+'.outputG', side+'_Leg_Hip_Bend0_Hdl.dWorldUpVectorEndZ')
            cmds.connectAttr(my_Blend+'.outputG', side+'_Leg_Hip_Bend0_Hdl.dWorldUpVectorZ')
            cmds.connectAttr(my_Blend+'.outputG', side+'_Leg_Knee_Bend0_Hdl.dWorldUpVectorZ')

            # Add finger master control
            finger_grps = ["Wing_Feather01_Start_Fk_Ctrl_Cns_Grp", "Wing_Feather01_00_Fk_Ctrl_Cns_Grp", "Wing_Feather01_01_Fk_Ctrl_Cns_Grp", "Wing_Feather01_02_Fk_Ctrl_Cns_Grp", "Wing_Feather01_03_Fk_Ctrl_Cns_Grp",
                           "Wing_Feather02_Start_Fk_Ctrl_Cns_Grp", "Wing_Feather02_00_Fk_Ctrl_Cns_Grp", "Wing_Feather02_01_Fk_Ctrl_Cns_Grp", "Wing_Feather02_02_Fk_Ctrl_Cns_Grp", "Wing_Feather02_03_Fk_Ctrl_Cns_Grp",
                           "Wing_Feather03_Start_Fk_Ctrl_Cns_Grp", "Wing_Feather03_00_Fk_Ctrl_Cns_Grp", "Wing_Feather03_01_Fk_Ctrl_Cns_Grp", "Wing_Feather03_02_Fk_Ctrl_Cns_Grp", "Wing_Feather03_03_Fk_Ctrl_Cns_Grp",
                           "Wing_Feather04_Start_Fk_Ctrl_Cns_Grp", "Wing_Feather04_00_Fk_Ctrl_Cns_Grp", "Wing_Feather04_01_Fk_Ctrl_Cns_Grp", "Wing_Feather04_02_Fk_Ctrl_Cns_Grp", "Wing_Feather04_03_Fk_Ctrl_Cns_Grp",
                           "Wing_Feather05_Start_Fk_Ctrl_Cns_Grp", "Wing_Feather05_00_Fk_Ctrl_Cns_Grp", "Wing_Feather05_01_Fk_Ctrl_Cns_Grp", "Wing_Feather05_02_Fk_Ctrl_Cns_Grp", "Wing_Feather05_03_Fk_Ctrl_Cns_Grp"]

            base_list = ["Wing_Feather01_Start_Fk_Ctrl", "Wing_Feather02_Start_Fk_Ctrl", "Wing_Feather03_Start_Fk_Ctrl", "Wing_Feather04_Start_Fk_Ctrl", "Wing_Feather05_Start_Fk_Ctrl"]

            master = "Master_Feather_Ctrl"

            if "L" in side:
                i_node.create("control", name=side+'_'+master, control_type="3D Pin Pyramid", with_gimbal=False, color="aqua", size=5)
            else:
                i_node.create("control", name=side+'_'+master, control_type="3D Pin Pyramid", with_gimbal=False, color="pink", size=5)
            master_snap = cmds.xform(side+"_Wing_Feather03_Start_Fk_Ctrl", q=True, ws=True, m=True)
            master_finger_grp = "Master_Feather_Ctrl_Offset_Grp"
            cmds.xform(side+'_'+master_finger_grp, ws=True, m=master_snap)
            cmds.parent(side+'_'+master_finger_grp, side+"_Arm_IKFKSwitch_Ctrl")

            for attr_lock in ["tx", "ty", "tz", "sy", "sz"]:
                cmds.setAttr(side+'_'+master+'.'+attr_lock, k=False, l=True)
            for fingers in finger_grps:
                target = side+'_'+fingers
                master_grp = cmds.group(em=True, n=(side+'_'+(fingers.replace("Cns", "Master"))))

                # move the little guy
                matrix = cmds.xform(target, q=True, ws=True, m=True)
                cmds.xform(master_grp, ws=True, m=matrix)
                cmds.setAttr(master_grp+".ry", cmds.getAttr(side+'_'+fingers+".ry"))

                # parent the little guy
                the_parent = cmds.listRelatives(target, p=True)
                cmds.parent(master_grp, the_parent, a=True)
                cmds.parent(target, master_grp, a=True)

                # make rot x nodes and attach to control
                if "Meta" in fingers:
                    pass
                else:
                    rot_finger_adl = cmds.shadingNode("addDoubleLinear", au=True, n=(side+'_'+(fingers.replace("Cns_Grp", "Rot_ADL"))))
                    rot_x_finger_md = cmds.shadingNode("multiplyDivide", au=True, n=(side+'_'+(fingers.replace("Cns_Grp", "X_MD"))))
                    cmds.connectAttr(rot_x_finger_md+".outputX", rot_finger_adl+".input1", f=True)
                    cmds.connectAttr(side+'_'+master+".rx", rot_x_finger_md+".input1X", f=True)

                    # make grandmaster control for 01 controls, connect the rx output to it instead of the master group
                    if "Start" in target:
                        grand_master_grp = cmds.group(em=True, n=(side+'_'+(fingers.replace("Cns", "Grand_Master"))))
                        cmds.xform(grand_master_grp, ws=True, m=matrix)
                        cmds.parent(grand_master_grp, the_parent, a=True)
                        cmds.parent(master_grp, grand_master_grp, a=True)

                        cmds.connectAttr(rot_finger_adl+".output", grand_master_grp+".rx", f=True)

                    else:
                        cmds.connectAttr(rot_finger_adl+".output", master_grp+".rx", f=True)

                # make rot z nodes and attach to control while excluding
                exclude = ["Thumb", "Meta"]
                if any(term in target for term in exclude):
                    pass
                else:
                    rot_z_finger_md = cmds.shadingNode("multiplyDivide", au=True, n=(side+'_'+(fingers.replace("Cns_Grp", "Z_MD"))))
                    cmds.connectAttr(side+'_'+master+".rz", rot_z_finger_md+".input1X", f=True)
                    cmds.connectAttr(rot_z_finger_md+".outputX", master_grp+".rz", f=True)

                    if "Start" in target:
                        rot_y_finger_md = cmds.shadingNode("multiplyDivide", au=True, n=(side+'_'+(fingers.replace("Cns_Grp", "Y_MD"))))
                        cmds.connectAttr(rot_y_finger_md+".outputX", rot_finger_adl+".input2", f=True)
                        cmds.connectAttr(side+'_'+master+".ry", rot_y_finger_md+".input1X", f=True)

                    cmds.setAttr(rot_z_finger_md+".input2X", 0.25)

            # add spread attribute and hook up nodes
            for all_fingers in base_list:
                spread_finger_md = cmds.shadingNode("multiplyDivide", au=True, n=(side+'_'+(all_fingers+"_Spread_MD")))
                spread_finger_adl = cmds.shadingNode("addDoubleLinear", au=True, n=(side+'_'+(all_fingers+"_Spread_ADL")))
                average_spread_adl = cmds.shadingNode("addDoubleLinear", au=True, n=(side+'_'+(all_fingers+"_Average_ADL")))
                meta_finger_md = cmds.shadingNode("multiplyDivide", au=True, n=(side+'_'+(all_fingers+"_Meta_Y_MD")))
                cmds.connectAttr(side+'_'+master+".ry", meta_finger_md+".input1X", f=True)
                cmds.setAttr(average_spread_adl+".input2", -1)
                cmds.connectAttr(side+'_'+master+".sx", average_spread_adl+".input1", f=True)
                cmds.connectAttr(average_spread_adl+".output", spread_finger_md+".input1X", f=True)
                cmds.connectAttr(side+'_'+all_fingers+"_Z_MD.outputX", spread_finger_adl+".input1", f=True)
                cmds.connectAttr(spread_finger_md+".outputX", spread_finger_adl+".input2", f=True)
                cmds.connectAttr(spread_finger_adl+".output", side+'_'+all_fingers+"_Master_Grp"+".rz", f=True)



            # Back toe compensate
            if cmds.objExists(side+'_Toe04_01_Ctrl'):

                cmds.parentConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe01_01_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe01_01_Ctrl_Offset_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe02_01_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe02_01_Ctrl_Offset_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe03_01_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe03_01_Ctrl_Offset_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe04_01_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ankle_Bnd_Jnt', side+'_Toe04_01_Ctrl_Offset_Grp', mo=1)

                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe01_02_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe01_02_Ctrl_Offset_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe02_02_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe02_02_Ctrl_Offset_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe03_02_Ctrl_Offset_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe03_02_Ctrl_Offset_Grp', mo=1)

                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe01_02_Offset_Jnt_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe01_02_Offset_Jnt_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe02_02_Offset_Jnt_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe02_02_Offset_Jnt_Grp', mo=1)
                cmds.parentConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe03_02_Offset_Jnt_Grp', mo=1)
                cmds.scaleConstraint(side+'_Foot_Ball_Bnd_Jnt', side+'_Toe03_02_Offset_Jnt_Grp', mo=1)

                rotGrp = cmds.group(em=1, n=side+'_Toe04_Offset_Rotate_Grp', p=side+'_Foot_Heel_Pivot_Grp')
                cmds.parent(rotGrp, 'Ctrl_Grp')
                cmds.parentConstraint(side+'_Foot_Heel_Pivot_Grp', rotGrp)
                cmds.scaleConstraint(side+'_Foot_Heel_Pivot_Grp', rotGrp)

                MD = cmds.createNode('multiplyDivide', n=side+'_BackToe_Reverse_MD')
                cmds.setAttr(MD+'.input2X', -1)
                cmds.connectAttr(rotGrp+'.rx', MD+'.input1X')
                cmds.connectAttr(MD+'.outputX', side+'_Toe04_01_Ctrl_Cns_Grp.rx')

                x = cmds.group(em=1, n=side+'_Toe04_01_Xtra_Jnt_Grp', p=side+'_Toe04_01_Cns_Jnt_Grp')
                cmds.parent(side+'_Toe04_01_Jnt_Grp', x)

                cmds.connectAttr(rotGrp+'.rx', x+'.rx')

                cmds.addAttr(side+'_Leg_Ankle_Ik_Ctrl', at='float', ln='Heel_Toe_Compensate', dv=0, k=1, min=0, max=1, h=0)
                cmds.connectAttr(side+'_Leg_Ankle_Ik_Ctrl.Heel_Toe_Compensate', side+'_Toe04_Offset_Rotate_Grp_parentConstraint1.'+side+'_Foot_Heel_Pivot_GrpW0')


            #things that act once, but only on birds
            if side == 'L':
                # Add throat controls
                name = ['Mouth_Upr', 'Mouth_Lwr', 'Mouth_Throat']

                for n in name:
                    # create new joints
                    cmds.select(clear=True)
                    jnt = cmds.joint(name='Face_C_'+n+'_Bnd_Jnt')
                    cmds.parent(jnt, 'Face_Mouth_Joints_Grp')
                    cmds.setAttr(jnt+'.segmentScaleCompensate', 0)
                    cmds.setAttr(jnt+'.type', 18)
                    # cmds.setAttr(jnt+'.otherType', cmds.getAttr(prntJnt+'.otherType'), type='string')

                    # create new controls
                    ctrl = cmds.duplicate('Face_C_Nose_Tip_Tweak_Ctrl', name='Face_C_'+n+'_Tweak_Ctrl')[0]
                    offset = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Offset_Grp'))
                    drv = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Drv_Grp'), parent=offset)
                    cns = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Cns_Grp'), parent=drv)
                    cmds.parent(ctrl, cns)
                    cmds.parent(offset, 'Face_Tweaks_Grp')
                    if n=='Mouth_Lwr':
                        cmds.parent(offset, 'Face_C_Jaw_Tweak_Ctrl')
                    cmds.parentConstraint(ctrl, jnt)
                    cmds.scaleConstraint(ctrl, jnt)

                # Neck edits
                neckSwitch = 'C_Neck_IKFKSwitch_Ctrl'
                if cmds.objExists(neckSwitch):
                    defaults = cmds.getAttr(neckSwitch+'.default_attrs')
                    cmds.setAttr(neckSwitch+'.default_attrs', defaults.replace("EndPivotVis': 0.0", "EndPivotVis': 1.0"), type='string')

                    cmds.setAttr(neckSwitch+'.HeadVis', 0, lock=True, channelBox=False)
                    cmds.setAttr(neckSwitch+'.EndCtrlVis', 1, lock=True, channelBox=False)
                    cmds.setAttr(neckSwitch+'.StartCtrlVis', 0)
                    cmds.setAttr(neckSwitch+'.VolumeOnOff', 0)

                    # lock out head control
                    attrs = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz']
                    ctrls = ['C_Head_Ctrl', 'C_Head_Gimbal_Ctrl']
                    for c in ctrls:
                        for a in attrs:
                            cmds.setAttr(c+a, lock=True, keyable=False, channelBox=False)
                    cmds.setAttr('C_Head_Ctrl.Follow', 2, lock=True, keyable=False, channelBox=False)

                    # fix neck twist
                    if cmds.objExists('C_Neck_Pin_Grp_parentConstraint1'):
                        cmds.delete('C_Neck_Pin_Grp_parentConstraint1')
                    cmds.parentConstraint('C_Spine_Chest_Gimbal_Ctrl', 'C_Neck_Pin_Grp', maintainOffset=True)

                    cmds.createNode('transform', name='C_Neck_Ik_Twist_Grp', parent='C_Neck_Base_Ctrl')
                    cmds.createNode('transform', name='C_Neck_Ik_Twist_Loc', parent='C_Neck_Ik_Twist_Grp')
                    cmds.orientConstraint('C_Neck_End_Gimbal_Ctrl', 'C_Neck_Ik_Twist_Loc', maintainOffset=True)
                    cmds.connectAttr('C_Neck_Ik_Twist_Loc.rotateY', 'C_Neck_BaseEnd_Twist_Adl.input2', force=True)

                    # fix neck follow constraint
                    cmds.deleteAttr("C_Neck_End_Ctrl.Follow")
                    pin = i_node.create("control", name='C_Head_Pin', control_type="3D Locator", with_gimbal=False, color="yellow", size=20)
                    cmds.parent('C_Head_Pin_Ctrl_Offset_Grp', 'Root_Gimbal_Ctrl')
                    temp = cmds.parentConstraint('C_Neck_End_Ctrl', 'C_Head_Pin_Ctrl_Offset_Grp', maintainOffset=False)
                    cmds.delete(temp)
                    tots_followConstraint.do_it(['Ground_Ctrl', 'Root_Ctrl', 'C_Head_Pin_Ctrl'], 'parent')
                    tots_followConstraint.do_it(['C_Head_Pin_Ctrl', 'C_Neck_Fk_02_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Neck_End_Ctrl'], 'orient')
                    cmds.parentConstraint('C_Head_Pin_Ctrl_Follow_Driver_Orient_Tfm', 'C_Neck_End_Ctrl_Cns_Grp', maintainOffset=True)
                    cmds.connectAttr('C_Neck_End_Ctrl_Follow_C_Head_Pin_Ctrl_Cnd.outColorR', 'C_Neck_End_Ctrl_Cns_Grp_parentConstraint1.C_Head_Pin_Ctrl_Follow_Driver_Orient_TfmW0')
                    cmds.connectAttr('C_Neck_End_Ctrl_Follow_C_Head_Pin_Ctrl_Cnd.outColorR', 'C_Head_Pin_Ctrl_Offset_Grp.visibility')
                    cmds.setAttr('C_Neck_End_Ctrl.Follow', 1)
                    tots_followConstraint.do_it(['C_Spine_Chest_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Neck_Base_Pivot_Ctrl'], 'orient')

    if cmds.objExists('L__Wing_Info'):
        # set wing attrs that can't be looped left side first
        cmds.setAttr("L_"+base_list[0]+"_Y_MD.input2X", -0.75)
        cmds.setAttr("L_"+base_list[1]+"_Y_MD.input2X", -0.25)
        cmds.setAttr("L_"+base_list[2]+"_Y_MD.input2X", 0.25)
        cmds.setAttr("L_"+base_list[3]+"_Y_MD.input2X", 0.75)
        cmds.setAttr("L_"+base_list[4]+"_X_MD.input2X", 0.6)

        cmds.setAttr("L_"+base_list[0]+"_Spread_MD.input2X", -14)
        cmds.setAttr("L_"+base_list[1]+"_Spread_MD.input2X", -2)
        cmds.setAttr("L_"+base_list[2]+"_Spread_MD.input2X", 10)
        cmds.setAttr("L_"+base_list[3]+"_Spread_MD.input2X", 22)

        # now the right
        cmds.setAttr("R_"+base_list[0]+"_Y_MD.input2X", -0.75)
        cmds.setAttr("R_"+base_list[1]+"_Y_MD.input2X", -0.25)
        cmds.setAttr("R_"+base_list[2]+"_Y_MD.input2X", 0.25)
        cmds.setAttr("R_"+base_list[3]+"_Y_MD.input2X", 0.75)
        cmds.setAttr("R_"+base_list[4]+"_X_MD.input2X", 0.6)
        cmds.setAttr("R_"+base_list[0]+"_Spread_MD.input2X", 14)
        cmds.setAttr("R_"+base_list[1]+"_Spread_MD.input2X", 2)
        cmds.setAttr("R_"+base_list[2]+"_Spread_MD.input2X", -10)
        cmds.setAttr("R_"+base_list[3]+"_Spread_MD.input2X", -22)

        cmds.setAttr("R_"+master+"Shape.overrideColor", 13)

def bipedPostBuild():
    # fix head follow constraint
    if not cmds.objExists('C_Neck_IKFKSwitch_Ctrl'):
        pin = 'C_Head_Pin_Ctrl'
        if not cmds.objExists(pin):
            pin = i_node.create("control", name='C_Head_Pin', control_type="3D Locator", with_gimbal=False, color="yellow", size=20)
            cmds.parent('C_Head_Pin_Ctrl_Offset_Grp', 'Root_Gimbal_Ctrl')
            temp = cmds.parentConstraint('C_Head_Ctrl', 'C_Head_Pin_Ctrl_Offset_Grp', maintainOffset=False)
            cmds.delete(temp)

        tots_followConstraint.do_it(['C_Head_Pin_Ctrl', 'C_Neck_02_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl'], 'orient')
        if not cmds.objExists('C_Head_Ctrl_Cns_Grp_orientConstraint1'):
            cmds.parentConstraint('C_Head_Pin_Ctrl_Follow_Driver_Orient_Tfm', 'C_Head_Ctrl_Cns_Grp', maintainOffset=True)
            cmds.connectAttr('C_Head_Ctrl_Follow_C_Head_Pin_Ctrl_Cnd.outColorR', 'C_Head_Pin_Ctrl_Cns_Grp.visibility')
            cmds.connectAttr('C_Head_Ctrl_Follow_C_Head_Pin_Ctrl_Cnd.outColorR', 'C_Head_Ctrl_Cns_Grp_parentConstraint1.C_Head_Pin_Ctrl_Follow_Driver_Orient_TfmW0')
        cmds.setAttr('C_Head_Ctrl.Follow', 1)
        tots_followConstraint.do_it(['Ground_Ctrl', 'Root_Ctrl', 'C_Head_Pin_Ctrl'], 'parent')

def shoulderFollowFix():
    # Fix Shoulder follow constraint
    for side in 'LR':
        tots_followConstraint.do_it([side+'_Clavicle_Ctrl', 'C_Spine_Chest_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', side+'_Arm_Shoulder_Fk_Ctrl'], 'orient')


def packsParentFix():
    # Fix IKFK switch constraints
    if not cmds.objExists('C_Spine_IKFKSwitch_Ctrl_parentConstraint1'):
        cmds.parentConstraint('COG_Gimbal_Ctrl', 'C_Spine_IKFKSwitch_Ctrl')

def fixToePivot():
    # Fix Toe pivot being in the wrong position

    for side in ['L_', 'R_', 'L_Front', 'R_Front', 'L_Back', 'R_Back']:
        if cmds.objExists(side+'Foot_Ball_Ik_Ctrl_Offset_Grp'):
            cmds.parent(side+'Foot_Ball_Ik_Ctrl_Offset_Grp', w=1)
            my_point = cmds.pointConstraint(side+'Foot_ToeTip_Ik_Ctrl', side+'Foot_Ball_Toe_Pivot_Offset_Grp', mo=0)
            cmds.delete(my_point)
            cmds.parent(side+'Foot_Ball_Ik_Ctrl_Offset_Grp', side+'Foot_Ball_Toe_Pivot_Cns_Grp')


def facePostBuild():
    # cleanup the face gui
    print("[Post Build] :: Running facial gui cleanup.")
    try:
        face_gui_cleanup()
    except RuntimeError:
        cmds.warning("[Post Build] :: Face gui cleanup failed.")

    # sub brow joints install
    print("[Post Build] :: Running sub brow controllers fix.")
    try:
        # tots_fix_sub_brow_ctrls_Alex.do_it()
        reload(tots_fix_sub_brow_ctrls)
        tots_fix_sub_brow_ctrls.do_it()
    except RuntimeError:
        cmds.warning("[Post Build] :: Sub Brow ctrls installation failed.")

    # fix the lid controllers
    print("[Post Build] :: Running lid ctrl fix.")
    try:
        reload(tots_lidCtrlFix)
        tots_lidCtrlFix.do_it()
    except RuntimeError:
        cmds.warning("[Post Build] :: Lid Ctrl fix failed.")

    print("[Post Build] :: Running eyes and brow alignment.")
    try:
        fix_eye_brow_alignment()
    except RuntimeError:
        cmds.warning("[Post Build] :: alignment failure.")

    try:
        fix_eye_ctrls()
    except RuntimeError:
        cmds.warning("[Post Build] :: Eye target control orientations fix failure.")

    try:
        reload(tots_facePanelV2)
        tots_facePanelV2.do_it()
    except RuntimeError:
        cmds.warning("[Post Build] :: Face Panel v2 upgrade failed.")



def do_it():
    """
    Run post-build operations to clean up the character rigs.
    :return: <bool> True for success. <bool> False for failure.
    """

    # need to make the the face curves import successfully.
    print("[Post Build] :: Checking broken face nodes.")
    remove_broken_face_nodes()

    print("[Post Build] :: Running joint utilties.")
    # average out the joints sizes
    avg_joint_radius()

    #Face edits
    if cmds.objExists('Face_Gui_Ctrl'):
        facePostBuild()

    # organize joints for better rigging
    print("[Post Build] :: Running rig organizations.")
    try:
        organize_joints()
    except RuntimeError:
        cmds.warning("[Post Build] :: Joint organization failed.")


    # fix the arms
    print("[Post Build] :: Running bend parents fix.")
    try:
        reload(tots_fix_bendParents)
        tots_fix_bendParents.do_it()
    except RuntimeError:
        cmds.warning("[Post Build] :: Bend parents failed.")

    # reconnect the scale to the Character nodes' scale offset multiply divide node
    print("[Post Build] :: Connecting Scale offset fix.")
    try:
        connect_character_scale_offset()
    except RuntimeError:
        cmds.warning("[Post Build] :: Character scale offset connections failed.")

    # fix shoulder follow
    print("[Post Build] :: Running shoulder follow fix.")
    try:
        shoulderFollowFix()
    except RuntimeError:
        cmds.warning("[Post Build] :: Character shoulder follow fix failed.")

    # fix the ears mirror issue
    print("[Post Build] :: Running ear mirror fix.")
    try:
        reload(ears_fix)
        ears_fix.do_it()
    except RuntimeError:
        cmds.warning("[Post Build] :: Character ears fix failed.")
    except TypeError:
        cmds.warning("[Post Build] :: Character ears fix deformation order failed.")
    except SyntaxError:
        cmds.warning("[Post Build] :: Character ears fix unknown error.")

    # fix the hip problem
    try:
        fix_leg_aim()
    except RuntimeError:
        cmds.warning("[Post Build] :: Leg build failure.")



    # tag the face controls for export
    # print("[Post Build] :: Running face curve connections.")
    # try:
    #     tag_face_controls()
    # except RuntimeError:
    #     cmds.warning("[Post Build] :: Face curve connections failed.")

    print("[Post Build] :: Running targets' space fix.")
    try:
        reload(tots_fix_target_space)
        tots_fix_target_space.install_data()
    except RuntimeError:
        cmds.warning("[Post Build] :: Target space installation failed.")



    print("[Post Build] :: Running the leg hip orients fix.")
    try:
        reload(leg_fix)
        leg_fix.fix_error()
    except RuntimeError:
        cmds.warning("[Post Build] :: legs and hip orient failure.")



    try:
        fix_constraints()
    except RuntimeError:
        cmds.warning("[Post Build] :: Constraint systems build failed.")

    # label the bind joints for optimal weight mirroring
    joint_label.label()

    try:
        bendyFlipFix()
    except RuntimeError:
        cmds.warning("[Post Build] :: Bendy flip fix failed.")



    try:
        wingPostBuild()
    except RuntimeError:
        cmds.warning("[Post Build] :: Season 2 wing upgrade failed.")

    try:
        fixIkFollows()
    except RuntimeError:
        cmds.warning("[Post Build] :: IK wrist follow fix failed.")

    try:
        bipedPostBuild()
    except RuntimeError:
        cmds.warning("[Post Build] :: Biped post build failed.")

    try:
        packsParentFix()
    except RuntimeError:
        cmds.warning("[Post Build] :: Packs parent fix post build failed.")

    try:
        reload(pup_FrontLegClavUpgrade)
        if cmds.objExists('forearm_guides_Grp'):
            pup_FrontLegClavUpgrade.build_extra_forarm_rig()
    except RuntimeError:
        cmds.warning("[Post Build] :: Quad Clav upgrade post build failed.")

    try:
        fixToePivot()
    except RuntimeError:
        cmds.warning("[Post Build] :: Toe pivot fix post build failed.")



    return True
