"""
Making the tongue drivable by the face rig.
"""
# import maya modules
from maya import cmds

get_parent = lambda x: cmds.listRelatives(x, p=1, type='transform') or []
get_child = lambda x: cmds.listRelatives(x, c=1, type='transform') or []
set_xform = lambda x, y: cmds.xform(x, m=cmds.xform(y, ws=1, q=1, m=1))


def do_it():
	"""
	Gets the tongue controllers and put a driver transform
	"""
	tongue_ctrls = cmds.ls('C_Tongue_Tweak_??_Ctrl')

	if not tongue_ctrls:
		cmds.warning('[Tongue_Fix] :: There are no tongue tweak controllers.')
		return 0

	for tongue_ctrl in tongue_ctrls:
		cns_grp = get_parent(tongue_ctrl)
		drv_grp_name = tongue_ctrl + '_Drv_Grp'

		offset_grp_name = tongue_ctrl + '_Offset_Grp'
		cns_grp_name = tongue_ctrl + '_Cns_Grp'

		driver_grp_check = get_parent(cns_grp)
		if not cmds.objExists(drv_grp_name):
			cmds.createNode('transform', name=drv_grp_name)
		set_xform(drv_grp_name, offset_grp_name)
		if drv_grp_name not in driver_grp_check:
			cmds.parent(drv_grp_name, offset_grp_name)

		cns_grp_check = get_child(drv_grp_name)

		if not cns_grp_check:
			cmds.parent(cns_grp_name, drv_grp_name)
	return True
