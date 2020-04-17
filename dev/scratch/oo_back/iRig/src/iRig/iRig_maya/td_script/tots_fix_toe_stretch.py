from maya import cmds


def do_it(toe_main_node=""):
	if not toe_main_node:
		for side in "LR":
			toe_offset_grps = cmds.ls('{}_Toe0?_01_Ctrl_Offset_Grp'.format(side))
			toe_tweak_offset_grps = cmds.ls('{}_Toe0?_01_Tweak_Offset_Jnt_Grp') + cmds.ls('{}_Toe0?_02_Tweak_Offset_Jnt_Grp')
			for 