"""
This module is to add buttons to the "TD Tools" sections of your department tab in Tool Panel.
"""

from functools import partial
import maya.cmds as cmds
import collections

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import imp

# import custom modules
import icon_api.utils as i_utils

# Var that is queried by pipeline
buttons = []
buttons_EAV = []
buttons_SMO = []
buttons_TOTS = []
buttons_RKT = []
buttons_PUP = []
buttons_fixes = []


# this module's path
path = os.path.dirname(os.path.abspath(__file__))

# def sample_function():
#     cmds.confirmDialog(title="Yay", message="Oh my rig!")
# 
# buttons.append({"label" : "Rig Ex", "tool_tip" : "Only an example", "icon_rgb" : "blue",
#                 "command" : partial(sample_function)})

####################################################################################


buttons_fixes.append({"label" : "test", "tool_tip" : "Fix Watson Hand (Hive Mind)",
                      "icon" : "G:/Pipeline/td_scripts/rig/icons/MouthShapes.png", "resize" : [30, 30]})

def divider():
    print(" ... ")

# unlock geo
def unlock_geo():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.unlock_Geo()

# Un-Lock asset
def unlock_asset():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.unlock_asset()

# Un-Lock asset
def show_utils():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.unlock_Utils()

# Un-Lock asset
def show_jnts():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.unlock_Jnts()


tots_unlock_rcl = collections.OrderedDict()
tots_unlock_rcl["Unlock Geo"] = partial(unlock_geo)
tots_unlock_rcl["Show Utils"] = partial(show_utils)
tots_unlock_rcl["Show Joints"] = partial(show_jnts)


# Lock asset
def lock_asset():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.lock_asset()

# zero controllers
def zero_ctrls():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.set_controller_default_zero()

# clean the skin clusters of influeces and unnecessary weights.
def clean_skins():
    import tots_cleanup
    reload(tots_cleanup)
    tots_cleanup.prune_skin_weights()
    tots_cleanup.remove_unused_skin_influences()


tots_lock_rcl = collections.OrderedDict()
tots_lock_rcl["Zero Ctrls"] = partial(zero_ctrls)
tots_lock_rcl["Clean Skins"] = partial(clean_skins)

buttons.append({"label": "Unlk Asset",
                "tool_tip": "Unlocks asset for rigging.",
                "icon": "{}/icons/Unlock.png".format(path),
                "icon_rgb": "blue",
                "right_click_buttons" : tots_unlock_rcl,
                "command": partial(unlock_asset),
                "resize": [30, 30]})

buttons.append({"label": "Lck Asset",
                "tool_tip": "Locks asset for handoff.",
                "icon": "{}/icons/Lock.png".format(path),
                "icon_rgb": "red",
                "right_click_buttons" : tots_lock_rcl,
                "command": partial(lock_asset),
                "resize": [30, 30]})

####################################################################################

def jl():
    import joint_label
    reload(joint_label)
    joint_label.label()


buttons.append({"label" : "Joint Label", "tool_tip" : "Label all joints as their name", "icon" : "rig/rig_insert_reskin.png",
                "icon_rgb" : "green", "command" : partial(jl), "resize" : [30, 30]})


####################################################################################

def ac(orient_axis=None):
    import attach_curve
    reload(attach_curve)
    sel = cmds.ls(sl=True)
    attach_curve.attach_to_curve(objs=sel, connect_orients=True, orient_axis=orient_axis)

ac_rcl = collections.OrderedDict()
ac_rcl["Orient: X"] = partial(ac, "x")
ac_rcl["Orient: Y"] = partial(ac, "y")
ac_rcl["Orient: Z"] = partial(ac, "z")

buttons.append({"label" : "Attach\nto Curve", "tool_tip" : "Attach objects to curve (select objs then curve)", "icon" : "anm/scale_keys.png",
                "icon_rgb" : "purple", "command" : partial(ac), "resize" : [30, 30], "right_click_buttons" : ac_rcl,
                "overlay_image" : "rig/rig_overlay_rightclick.png"})


####################################################################################

def mirror_face_anim_keys():
    import face_mirror_keys
    reload(face_mirror_keys)
    face_mirror_keys.do_it()

buttons.append({
    "label" : "Mirror Keys",
    "tool_tip": "Mirrors the animation keys on controllers.",
    "icon_rgb": "red",
    "icon": "{}/icons/FaceMirror.png".format(path),
    "resize": [30, 30],
    "command": partial(mirror_face_anim_keys)})

####################################################################################


####################################################################################

def edge_flow_mirror_tool():
    """
    Initiate and launch Thomas Bittner's Edge Flow Mirror tool.
    :return: <bool> True for success. <bool> False for failure.
    """
    global edgeFlowMirrorUI
    plug_in_file = 'G:/Rigging/edgeFlowMirror.py'
    ui_file = 'G:/Rigging/edgeFlowMirrorUI.py'
    if os.path.isfile(plug_in_file):
        if not cmds.pluginInfo(plug_in_file, query=True, loaded=True):
            cmds.loadPlugin(plug_in_file, qt=1)
    else:
        cmds.warning('[Edge Flow Error] :: No plugin found in G:/Rigging path.')
        return False
    if 'edgeFlowMirrorUI' not in dir():
        edgeFlowMirrorUI = imp.load_source('edgeFlowMirrorUI', ui_file)
    try:
        edgeFlowMirrorUI.showUI()
    except RuntimeError:
        cmds.warning('[Edge Flow Error] :: Could not open UI.')
        return False
    return True


# buttons.append({
#     "label": "Edge Mirror",
#     "tool_tip": "Mirror tool through geometry edge flow.",
#     "icon_rgb": "red",
#     "icon": "{}/icons/Mirror.png".format(path),
#     "resize": [34, 34],
#     "command": partial(edge_flow_mirror_tool)})

####################################################################################



####################################################################################

def clear_ctrl_anim_keys():
    import clear_keys
    reload(clear_keys)
    clear_keys.do_it()

buttons.append({
    "label" : "Clear Keys",
    "tool_tip": "Deletes all keys from controllers in the scene.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Eraser.png".format(path),
    "resize": [30, 30],
    "command": partial(clear_ctrl_anim_keys)})

####################################################################################


####################################################################################

def ed_migrate():
    import ed_migrate
    reload(ed_migrate)
    ed_migrate.migrate_window()

# ed migrate deformers/shaders button
buttons.append({"label": "Migrate Tool",
                    "tool_tip": "Migrate deformers/shaders to new geo",
                    "icon": "{}/icons/migrate.png".format(path),
                    "command": partial(ed_migrate),
                    "resize": [30, 30]})

####################################################################################


####################################################################################
'''
def tots_fix():
    import tots_fix_bendParents
    reload(tots_fix_bendParents)
    tots_fix_bendParents.do_it()
'''

def tots_fix_postbuild():
    import tots_fix_post_build
    reload(tots_fix_post_build)
    tots_fix_post_build.do_it()


def tots_fix_ears_mirror():
    import ears_fix
    reload(ears_fix)
    ears_fix.do_it()


def tots_fix_elbow_wing_flip():
    import tots_fix_wing_flip
    reload(tots_fix_wing_flip)
    tots_fix_wing_flip.install_flip(wing=True, elbow_ctrl="L_Arm_Elbow_Fk_Ctrl", 
        wrist_ctrl="L_Arm_Wrist_Fk_Ctrl", pole_vector_ctrl="L_Arm_PoleVector_Ctrl", multiplier=-40)


def tots_fix_wing_scale():
    import tots_fix_wing_flip
    reload(tots_fix_wing_flip)
    tots_fix_wing_flip.fix_wing_scale()


def tots_shoulder_follow_fix():
    import shoulder_follow_fix
    reload(shoulder_follow_fix)
    shoulder_follow_fix.do_it()


def tots_quadruped_legs_scale_fix():
    import quadruped_scale_fix
    reload(quadruped_scale_fix)
    quadruped_scale_fix.install_quadruped_scale_factors()


def tots_fix_bendyParents():
    import tots_fix_bendParents
    reload(tots_fix_bendParents)
    tots_fix_bendParents.do_it()


def tots_fix_scale_face_anim():
    import tots_fix_scale_face_curves
    reload(tots_fix_scale_face_curves)
    tots_fix_scale_face_curves.do_it()


def tots_fix_spineTwist():
    import spine_fix
    reload(spine_fix)
    spine_fix.do_it()


def tots_fix_rigInfoConn():
    import tots_fix_rigInfoConnect
    reload(tots_fix_rigInfoConnect)
    tots_fix_rigInfoConnect.do_it()


def tots_fix_shouldersAndHips():
    import leg_fix
    reload(leg_fix)
    leg_fix.fix_error()


def tots_fix_projEyeScale():
    import tots_projEyeScaleFix
    reload(tots_projEyeScaleFix)
    tots_projEyeScaleFix.do_it()


def tots_fix_lidCtrls():
    import tots_lidCtrlFix
    reload(tots_lidCtrlFix)
    tots_lidCtrlFix.do_it()

def tots_fix_ikSoftFix():
    import tots_ikSoftFix
    reload(tots_ikSoftFix)
    tots_ikSoftFix.do_it()


def tots_fix_dynamic_fk():
    import dynamic_fk_install
    reload(dynamic_fk_install)
    dynamic_fk_install.do_it()


def tots_add_brow_subctrls():
    import tots_fix_sub_brow_ctrls
    reload(tots_fix_sub_brow_ctrls)
    tots_fix_sub_brow_ctrls.do_it()

def tots_panelV2():
    import tots_facePanelV2
    reload(tots_facePanelV2)
    tots_facePanelV2.do_it()


def do_nothing():
    print("[TOTS Fixes] :: Right click please?")
    cmds.warning("[TOTS Fixes] :: Please right click this button.")


tots_fix_rcl = collections.OrderedDict()
tots_fix_rcl["Bendy Parents"] = partial(tots_fix_bendyParents)
tots_fix_rcl["Spine Twist Fix"] = partial(tots_fix_spineTwist)
tots_fix_rcl["Scale Face Curves"] = partial(tots_fix_scale_face_anim)
tots_fix_rcl["Connect Ctrls to Rig Info"] = partial(tots_fix_rigInfoConn)
tots_fix_rcl["Fix Shoulder and Hip orients"] = partial(tots_fix_shouldersAndHips)
tots_fix_rcl["Quadruped Legs Scale Fix"] = partial(tots_quadruped_legs_scale_fix)
tots_fix_rcl["Shoulder Follow Fix"] = partial(tots_shoulder_follow_fix)
tots_fix_rcl["Elbow Flip Wing Fix"] = partial(tots_fix_elbow_wing_flip)
tots_fix_rcl["Elbow Flip Wing Scale Fix"] = partial(tots_fix_wing_scale)
tots_fix_rcl["Eye Proj Scale Fix"] = partial(tots_fix_projEyeScale)
tots_fix_rcl["Lid Ctrls Fix"] = partial(tots_fix_lidCtrls)
tots_fix_rcl["Add Brow Sub Ctrls"] = partial(tots_add_brow_subctrls)
tots_fix_rcl["Fix Ear Ctrl Mirror"] = partial(tots_fix_ears_mirror)
tots_fix_rcl["Dynamic Fk Install"] = partial(tots_fix_dynamic_fk)
tots_fix_rcl["Face Panel V2"] = partial(tots_panelV2)
tots_fix_rcl["Post Build"] = partial(tots_fix_postbuild)


buttons_TOTS.append({
    "label" : "Fixs",
    "tool_tip": "Random fixes, right click for options.",
    "icon_rgb": "yellow",
    "icon": "{}/icons/Bandaid.png".format(path),
    "resize": [30, 30],
    "command": partial(do_nothing),
    "right_click_buttons" : tots_fix_rcl,
    "overlay_image": "rig/rig_overlay_rightclick.png"})


####################################################################################


####################################################################################


def tots_eyes():
    import tots_projection_eyes
    reload(tots_projection_eyes)
    tots_projection_eyes.do_it()

buttons_TOTS.append({
    "label" : "Eyes",
    "tool_tip": "Build projection eyes.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Eyes.png".format(path),
    "resize": [30, 30],
    "command": partial(tots_eyes)})




####################################################################################


####################################################################################

def do_nothingHS():
    print("[TOTS Headsquash] :: Right click please?")
    cmds.warning("[TOTS Headsquash] :: Please right click this button.")

def tots_hs():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_headSquash()

def tots_js():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_jawSquash()

def tots_cs():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_centerSquash()

def tots_squash_copy():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.copy_deformerWeights()


tots_squash_rcl = collections.OrderedDict()
tots_squash_rcl["Head Squash"] = partial(tots_hs)
tots_squash_rcl["Jaw Squash"] = partial(tots_js)
tots_squash_rcl["Center Squash"] = partial(tots_cs)
tots_squash_rcl["Copy Weights"] = partial(tots_squash_copy)


buttons_TOTS.append({
    "label" : "HeadSqsh",
    "tool_tip": "Build head and jaw squashes for season 2.",
    "icon_rgb": "red",
    "icon": "{}/icons/HeadSquash.png".format(path),
    "resize": [30, 30],
    "command": partial(do_nothing),
    "right_click_buttons" : tots_squash_rcl})


####################################################################################


####################################################################################


def tots_ball_rig():
    import ball_rig_template
    reload(ball_rig_template)
    ball_rig_template.install_ball_rig()

buttons_TOTS.append({
    "label" : "Ball Rig",
    "tool_tip": "Build a Ball Rig.",
    "icon_rgb": "red",
    "icon": "{}/icons/Ball.png".format(path),
    "resize": [30, 30],
    "command": partial(tots_ball_rig)})



####################################################################################


####################################################################################


def tots_wire_rig():
    import wire_setup
    reload(wire_setup)
    wire_setup.do_it()

buttons_TOTS.append({
    "label" : "Wire Rig",
    "tool_tip": "Build a wire setup rig.",
    "icon_rgb": "red",
    "icon": "{}/icons/Curve.png".format(path),
    "resize": [30, 30],
    "command": partial(tots_wire_rig)})


####################################################################################


####################################################################################
def tots_fix_tweakVis():
    import tots_fix_tweakVisToggle
    reload(tots_fix_tweakVisToggle)
    tots_fix_tweakVisToggle.do_it()


tots_dyn_rcl = collections.OrderedDict()
tots_dyn_rcl["Tweak Vis Toggle"] = partial(tots_fix_tweakVis)


def tots_dynamics():
    import tots_convertToDynamicChain
    reload(tots_convertToDynamicChain)
    tots_convertToDynamicChain.do_it()

buttons_TOTS.append({
    "label" : "Dynamics",
    "tool_tip": "Convert Simple FK chain to Dynamics.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Tail.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : tots_dyn_rcl,
    "command": partial(tots_dynamics)})

####################################################################################


####################################################################################

def tots_followsPrnt():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.prntSelected()

def tots_followsOrnt():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.orntSelected()

def tots_followsPoint():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.pointSelected()

tots_follow_rcl = collections.OrderedDict()
tots_follow_rcl["Parent Follow"] = partial(tots_followsPrnt)
tots_follow_rcl["Orientation Follow"] = partial(tots_followsOrnt)
tots_follow_rcl["Point Follow"] = partial(tots_followsPoint)

buttons_TOTS.append({
    "label" : "Follow",
    "tool_tip": "Select drivers then select Driven.",
    "icon_rgb": "black",
    "icon": "{}/icons/migrate.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : tots_follow_rcl,
    "command": partial(do_nothing)})

####################################################################################


####################################################################################

def tots_tweaksShirtBuild():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.buildTweaks('Shirt')

def tots_tweaksDiaperBuild():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.buildTweaks('Diaper')

def tots_tweaksShirtJnt():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.createShirtJoints()

def tots_tweaksDiaperJnts():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.createDiaperJoints()

tots_tweaks_rcl = collections.OrderedDict()
tots_tweaks_rcl["Create Shirt Joints"] = partial(tots_tweaksShirtJnt)
tots_tweaks_rcl["Build Shirt Tweaks"] = partial(tots_tweaksShirtBuild)
tots_tweaks_rcl["------"] = partial(divider)
tots_tweaks_rcl["Create Diaper Joints"] = partial(tots_tweaksDiaperJnts)
tots_tweaks_rcl["Build Diaper Tweaks"] = partial(tots_tweaksDiaperBuild)

buttons_TOTS.append({
    "label" : "Tweaks",
    "tool_tip": "Builds shirt or diaper tweaks",
    "icon_rgb": "black",
    "icon": "{}/icons/Tweak.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : tots_tweaks_rcl,
    "command": partial(do_nothing)})




####################################################################################


####################################################################################

def g_hand_fix():
    # Load G files
    try:  # Reg pipe
        import rig_tools.utils.misc as rig_misc
        rig_misc.legacy_load_g_rigging_will()
    except:  # Legacy pipe
        import rig_tools.legacy as rig_legacy
        rig_legacy.g_load_g_rigging_will()
    import WillsRigScrips as wrs
    reload(wrs)

    # Run fix
    wrs.hand_fix_rig()

buttons_EAV.append({
    "label" : "Hand Fix", "tool_tip" : "Fix Watson Hand (Hive Mind)", "icon" : "rig/hand.png",
    "command" : partial(g_hand_fix), "resize" : [30, 30]})


####################################################################################


def bind_like():
    import skin_tools
    reload(skin_tools)
    skin_tools.bind_like()


def bind_selected():
    import skin_tools
    reload(skin_tools)
    skin_tools.bind_selection()


def save_skin():
    import skin_tools
    reload(skin_tools)
    skin_tools.save_skin()


def load_skin():
    import skin_tools
    reload(skin_tools)
    skin_tools.load_skin()


def save_deformer():
    import deform_utils
    reload(deform_utils)
    deform_utils.save_defomer()


def load_deformer():
    import deform_utils
    reload(deform_utils)
    deform_utils.load_deformer()


def do_nothing():
    print("[Skin Util] :: Right click please?")
    cmds.warning("[Skin Util] :: Please right click this button.")


skin_rcl = collections.OrderedDict()
skin_rcl["Bind Like"] = partial(bind_like)
skin_rcl["Bind Selection"] = partial(bind_selected)
skin_rcl["Save Skin"] = partial(save_skin)
skin_rcl["Load Skin"] = partial(load_skin)
skin_rcl["------"] = partial(divider)
# skin_rcl["Save Deformers"] = partial(save_deformer)
# skin_rcl["Load Deformers"] = partial(load_deformer)
buttons.append({"label": "Skin Util",
                "tool_tip": "Generic Skinning Tools for Ease of Use.",
                "icon": "{}/icons/Salad.png".format(path),
                "command": partial(do_nothing),
                "resize": [30, 30],
                "right_click_buttons" : skin_rcl,
                "overlay_image": "rig/rig_overlay_rightclick.png"})


####################################################################################


####################################################################################


def facebake_bake():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.bake()


def facebake_eyeFix():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.eyeFix()


def facebake_reset():
    import facebake_manual
    reload(facebake_manual)
    sel = i_utils.check_sel()
    if not sel:
        return
    facebake_manual.reset()


def facebake_popFix():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.popFix()


def facebake_defaultClean():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.defaultClean()


def facebake_forceMirror():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.forceMirror()


def facebake_mirrorOn():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.mirrorMovementOn()


def facebake_mirrorOff():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.mirrorMovementOff()

def facebake_exportTag():
    import facebake_manual
    reload(facebake_manual)
    facebake_manual.exportTag()

fb_rcl = collections.OrderedDict()
fb_rcl["Fix Eye Mirror"] = partial(facebake_eyeFix)
fb_rcl["Reset Tweak"] = partial(facebake_reset)
fb_rcl["Force Mirror"] = partial(facebake_forceMirror)
fb_rcl["Fix Popping"] = partial(facebake_popFix)
fb_rcl["Fix Default"] = partial(facebake_defaultClean)
fb_rcl["Mirror Move On"] = partial(facebake_mirrorOn)
fb_rcl["Mirror Move Off"] = partial(facebake_mirrorOff)
fb_rcl["Tag for Export"] = partial(facebake_exportTag)
buttons.append({"label" : "Face Bake", "tool_tip" : "Face Bake Legacy Backups (L-Cl: Bake / R-Cl: Reset, etc)",
                "icon" : "rig/rig_cake.png",  # :note: This icon is pre-colored so cannot add an icon_rgb
                "command" : partial(facebake_bake), "resize" : [30, 30], "right_click_buttons" : fb_rcl,
                "overlay_image" : "rig/rig_overlay_rightclick.png"})


####################################################################################

# Gen Fix button - for misc right-click things by rig tds.

def rcl_only():
    import icon_api.utils as i_utils
    i_utils.error("Right-click functions only.", dialog=True)


def create_fake_template_curves():
    import gen_fixes
    reload(gen_fixes)
    gen_fixes.create_fake_template_curves()

def watson():
    import watson
    reload(watson)
    watson.watson_tool()

def smo_feet_loc_mirror():
    import smo_feet_loc_mirror
    reload(smo_feet_loc_mirror)
    smo_feet_loc_mirror.feet_loc_mirror()

def smo_kid_template_fix():
    import smo_kid_template_fix
    reload(smo_kid_template_fix)
    smo_kid_template_fix.template_fix()

def smo_postBuild():
    import smo_postBuild
    reload(smo_postBuild)
    smo_postBuild.do_it()

def smo_headsquash():
    import smo_headSquash
    reload(smo_headSquash)
    smo_headSquash.headSquash_window()

def smo_dynamics():
    import smo_dynamics
    reload(smo_dynamics)
    smo_dynamics.dynamics_window()

def smo_projection_eyes():
    import smo_projectionEyes
    reload(smo_projectionEyes)
    smo_projectionEyes.do_it()

def smo_face_rig():
    import smo_faceRig
    reload(smo_faceRig)
    smo_faceRig.smo_faceRig_window()

def smo_wing_fix():
    import wings_fix
    reload(wings_fix)
    wings_fix.do_it()

def smo_eyes_fix():
    import eyes_fix
    reload(eyes_fix)
    eyes_fix.do_it()

def rj_skin_io():
    import rj_skinIO
    reload(rj_skinIO)
    rj_skinIO.rj_skin_window()

def smo_lock():
    import smo_lock
    reload(smo_lock)
    smo_lock.do_it()

# smo fixes button
buttons_SMO.append({"label": "Watson",
                    "tool_tip": "Elementary...",
                    "icon": "{}/icons/watson.png".format(path),
                    "command": partial(watson),
                    "resize": [30, 30]})

# smo fixes button
fix_smo = collections.OrderedDict()
fix_smo["-----SMO Char Template-----"] = partial(divider)
fix_smo["Feet Locator Mirror"] = partial(smo_feet_loc_mirror)
fix_smo["Kid Template Fix"] = partial(smo_kid_template_fix)
fix_smo["-------SMO Char Build-------"] = partial(divider)
fix_smo["Post Build Script"] = partial(smo_postBuild)
fix_smo["Head Squash"] = partial(smo_headsquash)
fix_smo["Add Dynamics"] = partial(smo_dynamics)
fix_smo["Projection Eyes"] = partial(smo_projection_eyes)
fix_smo["Face Rig Tool"] = partial(smo_face_rig)
fix_smo["--------SMO OLD--------"] = partial(divider)
fix_smo["Wing Fix (SMO)"] = partial(smo_wing_fix)
fix_smo["Eyes Fix (SMO)"] = partial(smo_eyes_fix)
buttons_SMO.append({"label": "SMO Things",
                    "tool_tip": "Misc Rig-Fix things for the SMO project.",
                    "icon": "rig/rig_smo_speed.png",
                    "command": partial(rcl_only),
                    "resize": [30, 30],
                    "right_click_buttons": fix_smo,
                    "overlay_image": "rig/rig_overlay_rightclick.png"})

# rj skin io button
buttons_SMO.append({"label": "RJ skin IO",
                    "tool_tip": "Export and Import skin weights",
                    "icon": "{}/icons/saveSkin.png".format(path),
                    "command": partial(rj_skin_io),
                    "resize": [30, 30]})

# ed migrate deformers/shaders button
buttons_SMO.append({"label": "Migrate Tool",
                    "tool_tip": "Migrate deformers/shaders to new geo",
                    "icon": "{}/icons/migrate.png".format(path),
                    "command": partial(ed_migrate),
                    "resize": [30, 30]})

# SMO lock asset button
buttons_SMO.append({"label": "SMO Lock",
                    "tool_tip": "Lock assets for publish",
                    "icon": "{}/icons/Lock.png".format(path),
                    "command": partial(smo_lock),
                    "resize": [30, 30]})

# rcl fixes button
fix_rcl = collections.OrderedDict()
fix_rcl["Create Face GUI Template Curves (1x only)"] = partial(create_fake_template_curves)
buttons.append({"label": "General Fixes",
                "tool_tip": "Misc Rig-Fix things from the TDs (right-click only)",
                "icon": "rig/rig_fixes.png",
                "command": partial(rcl_only),
                "resize": [30, 30],
                "right_click_buttons": fix_rcl,
                "overlay_image": "rig/rig_overlay_rightclick.png"})


####################################################################################
def open_ngskintools_ui():
    try:
        cmds.loadPlugin('ngSkinTools')
    except RuntimeError:
        cmds.error('Unable to load plugin - Cannot open UI')
        return
        
    from ngSkinTools.ui.mainwindow import MainWindow
    MainWindow.open()

buttons.append({"label": "NG Skin",
                "tool_tip": "Loader for the ngSkinTools plugin",
                "icon": "{}/icons/ngSkinToolsShelfIcon.png".format(path),
                "command": partial(open_ngskintools_ui),
                "resize": [30, 30]})

####################################################################################


####################################################################################

# Mouth shapes for RKT characters guide
def mouthShapes():
	import mhMouthShapes
	reload(mhMouthShapes)
	mhMouthShapes.toggle()

buttons_RKT.append({
    "label" : "MouthGuide", "tool_tip" : "Fix Watson Hand (Hive Mind)", "icon" : "G:/Pipeline/td_scripts/rig/icons/MouthShapes.png",
    "command" : partial(mouthShapes), "resize" : [30, 30]})



####################################################################################


#PUP Struction buttons


####################################################################################

def pup_fix_postbuild():
    import pup_fix_post_build
    reload(pup_fix_post_build)
    pup_fix_post_build.do_it()


def pup_fix_ears_mirror():
    import ears_fix
    reload(ears_fix)
    ears_fix.do_it()


def pup_fix_elbow_wing_flip():
    import tots_fix_wing_flip
    reload(tots_fix_wing_flip)
    tots_fix_wing_flip.install_flip(wing=True, elbow_ctrl="L_Arm_Elbow_Fk_Ctrl",
        wrist_ctrl="L_Arm_Wrist_Fk_Ctrl", pole_vector_ctrl="L_Arm_PoleVector_Ctrl", multiplier=-40)


def pup_fix_wing_scale():
    import tots_fix_wing_flip
    reload(tots_fix_wing_flip)
    tots_fix_wing_flip.fix_wing_scale()


def pup_shoulder_follow_fix():
    import shoulder_follow_fix
    reload(shoulder_follow_fix)
    shoulder_follow_fix.do_it()


def pup_quadruped_legs_scale_fix():
    import quadruped_scale_fix
    reload(quadruped_scale_fix)
    quadruped_scale_fix.install_quadruped_scale_factors()


def pup_fix_bendyParents():
    import tots_fix_bendParents
    reload(tots_fix_bendParents)
    tots_fix_bendParents.do_it()


def pup_fix_scale_face_anim():
    import tots_fix_scale_face_curves
    reload(tots_fix_scale_face_curves)
    tots_fix_scale_face_curves.do_it()


def pup_fix_spineTwist():
    import spine_fix
    reload(spine_fix)
    spine_fix.do_it()


def pup_fix_rigInfoConn():
    import tots_fix_rigInfoConnect
    reload(tots_fix_rigInfoConnect)
    tots_fix_rigInfoConnect.do_it()


def pup_fix_shouldersAndHips():
    import leg_fix
    reload(leg_fix)
    leg_fix.fix_error()


def pup_fix_projEyeScale():
    import tots_projEyeScaleFix
    reload(tots_projEyeScaleFix)
    tots_projEyeScaleFix.do_it()


def pup_fix_lidCtrls():
    import tots_lidCtrlFix
    reload(tots_lidCtrlFix)
    tots_lidCtrlFix.do_it()

def pup_fix_ikSoftFix():
    import tots_ikSoftFix
    reload(tots_ikSoftFix)
    tots_ikSoftFix.do_it()


def pup_fix_dynamic_fk():
    import dynamic_fk_install
    reload(dynamic_fk_install)
    dynamic_fk_install.do_it()


def pup_add_brow_subctrls():
    import tots_fix_sub_brow_ctrls
    reload(tots_fix_sub_brow_ctrls)
    tots_fix_sub_brow_ctrls.do_it()

def pup_panelV2():
    import tots_facePanelV2
    reload(tots_facePanelV2)
    tots_facePanelV2.do_it()


def do_nothing():
    print("[PUP Fixes] :: Right click please?")
    cmds.warning("[PUP Fixes] :: Please right click this button.")


pup_fix_rcl = collections.OrderedDict()
pup_fix_rcl["Bendy Parents"] = partial(pup_fix_bendyParents)
pup_fix_rcl["Spine Twist Fix"] = partial(pup_fix_spineTwist)
pup_fix_rcl["Scale Face Curves"] = partial(pup_fix_scale_face_anim)
pup_fix_rcl["Connect Ctrls to Rig Info"] = partial(pup_fix_rigInfoConn)
pup_fix_rcl["Fix Shoulder and Hip orients"] = partial(pup_fix_shouldersAndHips)
pup_fix_rcl["Quadruped Legs Scale Fix"] = partial(pup_quadruped_legs_scale_fix)
pup_fix_rcl["Shoulder Follow Fix"] = partial(pup_shoulder_follow_fix)
pup_fix_rcl["Elbow Flip Wing Fix"] = partial(pup_fix_elbow_wing_flip)
pup_fix_rcl["Elbow Flip Wing Scale Fix"] = partial(pup_fix_wing_scale)
pup_fix_rcl["Eye Proj Scale Fix"] = partial(pup_fix_projEyeScale)
pup_fix_rcl["Lid Ctrls Fix"] = partial(pup_fix_lidCtrls)
pup_fix_rcl["Add Brow Sub Ctrls"] = partial(pup_add_brow_subctrls)
pup_fix_rcl["Fix Ear Ctrl Mirror"] = partial(pup_fix_ears_mirror)
pup_fix_rcl["Dynamic Fk Install"] = partial(pup_fix_dynamic_fk)
pup_fix_rcl["Face Panel V2"] = partial(pup_panelV2)
pup_fix_rcl["Post Build"] = partial(pup_fix_postbuild)


buttons_PUP.append({
    "label" : "Fixs",
    "tool_tip": "Random fixes, right click for options.",
    "icon_rgb": "yellow",
    "icon": "{}/icons/Bandaid.png".format(path),
    "resize": [30, 30],
    "command": partial(do_nothing),
    "right_click_buttons" : pup_fix_rcl,
    "overlay_image": "rig/rig_overlay_rightclick.png"})

####################################################################################



####################################################################################


def pup_clavsSetup():
    import pup_FrontLegClavUpgrade
    reload(pup_FrontLegClavUpgrade)
    pup_FrontLegClavUpgrade.build_extra_forarm_guides()

def pup_clavsBuild():
    import pup_FrontLegClavUpgrade
    reload(pup_FrontLegClavUpgrade)
    pup_FrontLegClavUpgrade.build_extra_forarm_rig()

pup_clavs_rcl = collections.OrderedDict()
pup_clavs_rcl["Setup Guides"] = partial(pup_clavsSetup)
pup_clavs_rcl["Build Clav Upgrade"] = partial(pup_clavsBuild)


buttons_PUP.append({
    "label" : "Clavs",
    "tool_tip": "Upgrade Quad Clavicles.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Tweak.png".format(path),
    "resize": [30, 30],
    "command": partial(do_nothing),
    "right_click_buttons" : pup_clavs_rcl,
    "overlay_image": "rig/rig_overlay_rightclick.png"})


####################################################################################



####################################################################################


def pup_eyes():
    import pup_projection_eyes
    reload(pup_projection_eyes)
    pup_projection_eyes.do_it()

buttons_PUP.append({
    "label" : "Eyes",
    "tool_tip": "Build projection eyes.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Eyes.png".format(path),
    "resize": [30, 30],
    "command": partial(pup_eyes)})




####################################################################################


####################################################################################


def pup_do_nothingHS():
    print("[PUP Headsquash] :: Right click please?")
    cmds.warning("[PUP Headsquash] :: Please right click this button.")

def pup_hs():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_headSquash()

def pup_js():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_jawSquash()

def pup_cs():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.make_centerSquash()

def pup_squash_copy():
    import tots_headSquashV2
    reload(tots_headSquashV2)
    tots_headSquashV2.copy_deformerWeights()


pup_squash_rcl = collections.OrderedDict()
pup_squash_rcl["Head Squash"] = partial(pup_hs)
pup_squash_rcl["Jaw Squash"] = partial(pup_js)
pup_squash_rcl["Center Squash"] = partial(pup_cs)
pup_squash_rcl["Copy Weights"] = partial(pup_squash_copy)


buttons_PUP.append({
    "label" : "HeadSqsh",
    "tool_tip": "Build head and jaw squashes for season 2.",
    "icon_rgb": "red",
    "icon": "{}/icons/HeadSquash.png".format(path),
    "resize": [30, 30],
    "command": partial(pup_do_nothingHS),
    "right_click_buttons" : pup_squash_rcl})


####################################################################################


####################################################################################


def pup_ball_rig():
    import ball_rig_template
    reload(ball_rig_template)
    ball_rig_template.install_ball_rig()

buttons_PUP.append({
    "label" : "Ball Rig",
    "tool_tip": "Build a Ball Rig.",
    "icon_rgb": "red",
    "icon": "{}/icons/Ball.png".format(path),
    "resize": [30, 30],
    "command": partial(pup_ball_rig)})



####################################################################################


####################################################################################

def pup_fix_tweakVis():
    import tots_fix_tweakVisToggle
    reload(tots_fix_tweakVisToggle)
    tots_fix_tweakVisToggle.do_it()


pup_dyn_rcl = collections.OrderedDict()
pup_dyn_rcl["Tweak Vis Toggle"] = partial(pup_fix_tweakVis)


def pup_dynamics():
    import tots_convertToDynamicChain
    reload(tots_convertToDynamicChain)
    tots_convertToDynamicChain.do_it()

buttons_PUP.append({
    "label" : "Dynamics",
    "tool_tip": "Convert Simple FK chain to Dynamics.",
    "icon_rgb": "blue",
    "icon": "{}/icons/Tail.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : pup_dyn_rcl,
    "command": partial(pup_dynamics)})

####################################################################################


####################################################################################

def pup_followsPrnt():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.prntSelected()

def pup_followsOrnt():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.orntSelected()

def pup_followsPoint():
    import tots_followConstraint
    reload(tots_followConstraint)
    tots_followConstraint.pointSelected()

pup_follow_rcl = collections.OrderedDict()
pup_follow_rcl["Parent Follow"] = partial(pup_followsPrnt)
pup_follow_rcl["Orientation Follow"] = partial(pup_followsOrnt)
pup_follow_rcl["Point Follow"] = partial(pup_followsPoint)

buttons_PUP.append({
    "label" : "Follow",
    "tool_tip": "Select drivers then select Driven.",
    "icon_rgb": "black",
    "icon": "{}/icons/migrate.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : pup_follow_rcl,
    "command": partial(do_nothing)})

####################################################################################


####################################################################################

def pup_tweaksShirtBuild():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.buildTweaks('Shirt')

def pup_tweaksDiaperBuild():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.buildTweaks('Diaper')

def pup_tweaksShirtJnt():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.createShirtJoints()

def pup_tweaksDiaperJnts():
    import tots_tweaks
    reload(tots_tweaks)
    tots_tweaks.createDiaperJoints()

pup_tweaks_rcl = collections.OrderedDict()
pup_tweaks_rcl["Create Shirt Joints"] = partial(pup_tweaksShirtJnt)
pup_tweaks_rcl["Build Shirt Tweaks"] = partial(pup_tweaksShirtBuild)
pup_tweaks_rcl["------"] = partial(divider)
pup_tweaks_rcl["Create Diaper Joints"] = partial(pup_tweaksDiaperJnts)
pup_tweaks_rcl["Build Diaper Tweaks"] = partial(pup_tweaksDiaperBuild)

buttons_PUP.append({
    "label" : "Tweaks",
    "tool_tip": "Builds shirt or diaper tweaks",
    "icon_rgb": "black",
    "icon": "{}/icons/Tweak.png".format(path),
    "resize": [30, 30],
    "right_click_buttons" : pup_tweaks_rcl,
    "command": partial(do_nothing)})




####################################################################################


####################################################################################