def template_fix():

    import maya.cmds as cmds

    # change constraint
    cmds.setAttr("COGPlacement_Python_BuildPack.notes", "cmds.pointConstraint('Spine_01','COG_Ctrl_Offset_Grp',mo=False)", type="string")
    # delete ring attr
    cmds.setAttr("Hand_BuildPack.RootList", "Palm,Thumb_01,Index_01,Middle_01,Pinky_01", type="string")
    # delete extra finger
    if cmds.objExists("L_Ring_01"):
        cmds.delete("L_Ring_01")