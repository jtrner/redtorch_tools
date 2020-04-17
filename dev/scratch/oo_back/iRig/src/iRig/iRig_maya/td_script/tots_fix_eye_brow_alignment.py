# import maya modules
import maya.cmds as cmds


def do_it():
    """
    Align the eyes and the eyebrows.
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