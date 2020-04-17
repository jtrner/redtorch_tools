# import maya modules
from maya import cmds

# import custom modules
from rig_math.vector import Vector


def util_get_children(par_node):
	"""
	Get the transform children.
	:param par_node: <str> get the children from this parent provided.
	:returns: <list> children on parent node.
	"""
	return cmds.listRelatives(par_node, c=1, type='transform')


def util_connect_attr(output_attr, input_attr):
    """
    Connect the attributes
    :param output_attr: <str> the output attriubte to connect to the input attribute.
    :param input_attr: <str> the input attribute to be connected into.
	:returns: <bool> True for success. <bool> False for failure.    
    """
    if not any([output_attr, input_attr]):
        return False
    if not cmds.isConnected(output_attr, input_attr, ignoreUnitConversion=1):
        cmds.connectAttr(output_attr, input_attr, f=1)
    return True


def util_create_node(node_name, node_type):
    """
    Create the node.
    :param node_type: <str> the type of node to create.
    :param node_name: <str> name this new node.
	:returns: <bool> True for success. <bool> False for failure.
    """
    if not cmds.objExists(node_name):
        cmds.createNode(node_type, name=node_name)
    return True


def util_add_attr(obj_attr, attr_type, min_value=0, max_value=1, default_value=0):
    """
    Create this new attribute.
    :param obj_attr: <str> the name of the attribute to add.
    :param attr_type: <str> the name of the attribute to add.
	:returns: <bool> True for success. <bool> False for failure.
    """
    if '.' in obj_attr:
    	obj_name, attr_name = obj_attr.split('.')
    if not cmds.objExists(obj_attr):
    	cmds.addAttr(obj_name, ln=attr_name, at='float', min=min_value, max=max_value, dv=default_value)
    cmds.setAttr(obj_attr, k=1)
    return True

def util_set_attr(attr, value):
    """
    set value to this attribute string.
    :param attr: <str> attribute string eg. transform1.translateY
    :param value: <int> value to set the attribute to.
   	:returns: <bool> True for success. <bool> False for failure.
    """
    current_val = cmds.getAttr(attr)
    if current_val != value:
        confirm_connection = cmds.listConnections(attr, s=1, d=0, plugs=1)
        if confirm_connection:
            return False
        cmds.setAttr(attr, value)
    return True


def fix_wing_scale():
	"""
	Fixes the wing scaling issue.
	:returns: <bool> True for success. <False> for failure.
	"""
	for side in 'LR':
		# connect the children
		wing_tip_cls_grp = '{}_Wing_FeatherTip_Cls_Grp'.format(side)
		wing_base_cls_grp = '{}_Wing_FeatherBase_Cls_Grp'.format(side)
		feather_tip_foll_grp = '{}_Wing_FeatherTip_Foll_Grp'.format(side)
		feather_base_foll_grp = '{}_Wing_FeatherBase_Foll_Grp'.format(side)
		arm_base_foll_grp = '{}_ArmBase_Foll_Grp'.format(side)
		root_ctrl = 'Root_Ctrl'

		# constrain these items
		wing_fk_grp = '{}_Wing_FkCtrl_Grp'.format(side)
		wing_base_offset_grps = cmds.ls('{}_Wing_BaseOffset_?_Ctrl_Offset_Grp'.format(side))
		if not wing_base_offset_grps:
			cmds.warning('[Wing Scale Fix] :: Wing Components not found: {LR}_Wing_BaseOffset_?_Ctrl_Offset_Grp.')
			return 0

		check_items = [wing_tip_cls_grp, wing_base_cls_grp, feather_tip_foll_grp, feather_base_foll_grp, arm_base_foll_grp, wing_fk_grp, root_ctrl]
		if not any(map(cmds.objExists, check_items)):
			cmds.warning('[Wing Scale Fix] :: No Components found: {}'.format(check_items))
			return 0

		# perform connections
		for s in 'xyz':
			try:
				map(lambda x: cmds.connectAttr(root_ctrl + '.ScaleXYZ', x+'.s{}'.format(s), f=1), util_get_children(wing_tip_cls_grp))
			except RuntimeError:
				pass

			try:
				map(lambda x: cmds.connectAttr(root_ctrl + '.ScaleXYZ', x+'.s{}'.format(s), f=1), util_get_children(wing_base_cls_grp))
			except RuntimeError:
				pass

			try:
				map(lambda x: cmds.connectAttr(root_ctrl + '.ScaleXYZ', x+'.s{}'.format(s), f=1), util_get_children(feather_tip_foll_grp))
			except RuntimeError:
				pass

			try:
				map(lambda x: cmds.connectAttr(root_ctrl + '.ScaleXYZ', x+'.s{}'.format(s), f=1), util_get_children(feather_base_foll_grp))
			except RuntimeError:
				pass

			try:
				map(lambda x: cmds.connectAttr(root_ctrl + '.ScaleXYZ', x+'.s{}'.format(s), f=1), util_get_children(arm_base_foll_grp))
			except RuntimeError:
				pass

		# perform constraints
		try:
			cmds.scaleConstraint(root_ctrl, wing_fk_grp,  mo=1)
		except RuntimeError:
			pass

		try:
			map(lambda x: cmds.scaleConstraint(root_ctrl, x,  mo=1), wing_base_offset_grps)
		except RuntimeError:
			pass
	return True



def install_flip(knee=False, wing=False, pole_vector_flip_position=[], elbow_ctrl="", wrist_ctrl="", pole_vector_ctrl="", multiplier=-40):
	"""
	Taken from Elias and made it workable.
	:param knee: <bool> perform knee flipping operation.
	:param wing: <bool> perform wing flip operation.
	:param elbow_ctrl: <str> the elbow control name to get transform position from.
	:param wrist_ctrl: <str> the wrist control name to get transform position from.
	:param pole_vector_ctrl: <str> pole vector control name to get transform position from.
	:returns: <bool> True for success. <bool> False for failure.
	"""
	if not pole_vector_flip_position:
		v1 = Vector(cmds.xform(elbow_ctrl, ws=1, q=1, t=1))
		v2 = Vector(cmds.xform(pole_vector_ctrl, ws=1, q=1, t=1))
		v3 = Vector(cmds.xform(wrist_ctrl, ws=1, q=1, t=1))
		x_vec = v3 - v1
		y_vec = v2 - v1
		v_loc = x_vec.cross_product(y_vec).normalize() * multiplier
		# world-space coordinates
		pole_vector_flip_position = (v1 + v_loc) - v2

	for side in ['L','R']:
		# knee
		if knee:
			attr_name='KneeFlip'
			pole_vector_ctrl = '{}_Leg_PoleVector_Ctrl'.format(side)
			tr_blend_node = '{}_Tr_KneeFlip_Blnd'.format(side)
			leg_knee_ik = '{}Leg_Knee_Bend0_Hdl'.format(side)
			leg_hip_ik = '{}Leg_Hip_Bend0_Hdl'.format(side)

			leg_hip_worldup_bend_vec_end_attr = '{}.dWorldUpVectorEndZ'.format(arm_shoulder_ik)
			leg_hip_worldup_bend_vec_z_attr = '{}.dWorldUpVectorZ'.format(arm_shoulder_ik)
			leg_knee_worldup_bend_vec_z_attr = '{}.dWorldUpVectorZ'.format(arm_elbow_ik)
			leg_knee_worldup_bend_vec_y_attr = '{}.dWorldUpVectorY'.format(arm_shoulder_ik)
			leg_knee_worldup_bend_vec_y_attr = '{}.dWorldUpVectorY'.format(arm_elbow_ik)

			util_set_attr(tr_blend_node + '.color1R', -my_val)
			util_set_attr(tr_blend_node + '.color1G', -1)
			util_set_attr(tr_blend_node + '.color2R', my_val)
			util_set_attr(tr_blend_node + '.color2G', 1)

			util_connect_attr(tr_blend_node + '.outputR', pole_vector_offset_tz_attr)
			util_connect_attr(blend_out_g_attr, shoulder_worldup_bend_vec_end_attr)
			util_connect_attr(blend_out_g_attr, shoulder_worldup_bend_vec_z_attr)
			util_connect_attr(blend_out_g_attr, elbow_worldup_bend_vec_z_attr)

		# wing
		if wing:
			attr_name='ElbowFlip'
			fk_ik_switch = '{}_Arm_IKFKSwitch_Ctrl'.format(side)
			pole_vector_ctrl = '{}_Arm_PoleVector_Ctrl'.format(side)
			tr_blend_node = '{}_Tr_ElbowFlip_Blnd'.format(side)
			switch_mult_node = '{}_Tr_ElbowFlip_Mult'.format(side)
			arm_shoulder_ik = '{}_Arm_Shoulder_Bend0_Hdl'.format(side)
			arm_elbow_ik = '{}_Arm_Elbow_Bend0_Hdl'.format(side)

			fk_ik_switch_attr = '{}.FKIKSwitch'.format(fk_ik_switch)

			if side == 'R':
				util_set_attr(arm_shoulder_ik + '.dForwardAxis', 2)
				util_set_attr(arm_shoulder_ik + '.dWorldUpAxis', 7)

			tr_blend_attr = '{}.blender'.format(tr_blend_node)
			elbow_attr = '{}.{}'.format(pole_vector_ctrl, attr_name)
			pole_vector_offset_tx_attr = '{}_Offset_Follow_Grp.tx'.format(pole_vector_ctrl)
			pole_vector_offset_tz_attr = '{}_Offset_Follow_Grp.tz'.format(pole_vector_ctrl)
			pole_vector_offset_ty_attr = '{}_Offset_Follow_Grp.ty'.format(pole_vector_ctrl)

			util_add_attr(elbow_attr, 'float')
			util_create_node(tr_blend_node, 'blendColors')

			util_create_node(switch_mult_node, 'multiplyDivide')
			util_connect_attr(fk_ik_switch_attr, switch_mult_node + '.input1X')
			util_connect_attr(elbow_attr, switch_mult_node + '.input2X')

			mult_output_attr = switch_mult_node + '.outputX'
			util_connect_attr(mult_output_attr, tr_blend_attr)

			util_set_attr(tr_blend_node + '.color1R', pole_vector_flip_position[0])
			util_set_attr(tr_blend_node + '.color1G', pole_vector_flip_position[1])
			util_set_attr(tr_blend_node + '.color1B', pole_vector_flip_position[2])

			my_val = cmds.getAttr(pole_vector_offset_tz_attr)

			blend_out_r_attr = tr_blend_node + '.outputR'
			blend_out_g_attr = tr_blend_node + '.outputG'
			blend_out_b_attr = tr_blend_node + '.outputB'

			shoulder_worldup_bend_vec_end_attr = '{}.dWorldUpVectorEndZ'.format(arm_shoulder_ik)
			shoulder_worldup_bend_vec_z_attr = '{}.dWorldUpVectorZ'.format(arm_shoulder_ik)
			elbow_worldup_bend_vec_z_attr = '{}.dWorldUpVectorZ'.format(arm_elbow_ik)
			shoulder_worldup_bend_vec_y_attr = '{}.dWorldUpVectorY'.format(arm_shoulder_ik)
			elbow_worldup_bend_vec_y_attr = '{}.dWorldUpVectorY'.format(arm_elbow_ik)

			up_shoulder_blend_node = '{}_Shoulder_{}_Blnd'.format(side, attr_name)
			up_end_shoulder_blend_node = '{}_Shoulder_End_{}_Blnd'.format(side, attr_name)
			up_elbow_blend_node = '{}_Elbow_{}_Blnd'.format(side, attr_name)
			up_end_elbow_blend_node = '{}_Elbow_End_{}_Blnd'.format(side, attr_name)

			util_create_node(up_shoulder_blend_node, 'blendColors')
			util_create_node(up_end_shoulder_blend_node, 'blendColors')
			util_create_node(up_elbow_blend_node, 'blendColors')
			util_create_node(up_end_elbow_blend_node, 'blendColors')

			util_connect_attr(mult_output_attr, up_shoulder_blend_node + '.blender')
			util_connect_attr(mult_output_attr, up_end_shoulder_blend_node + '.blender')
			util_connect_attr(mult_output_attr, up_elbow_blend_node + '.blender')
			util_connect_attr(mult_output_attr, up_end_elbow_blend_node + '.blender')
			util_connect_attr(mult_output_attr, tr_blend_attr)

			util_set_attr(tr_blend_node + '.color2R', 0)
			util_set_attr(tr_blend_node + '.color2G', 0)
			util_set_attr(tr_blend_node + '.color2B', 0)

			# up shoulder vector
			if side == 'L':
				# World Up Object
				# elbow flip 0
				util_set_attr(up_shoulder_blend_node + '.color2R', 0)
				util_set_attr(up_shoulder_blend_node + '.color2G', 0)
				util_set_attr(up_shoulder_blend_node + '.color2B', 1)

				# elbow flip 1
				util_set_attr(up_shoulder_blend_node + '.color1R', 1)
				util_set_attr(up_shoulder_blend_node + '.color1G', 0)
				util_set_attr(up_shoulder_blend_node + '.color1B', 0)

			if side == 'R':
				# World Up Object
				# elbow flip 0
				util_set_attr(up_shoulder_blend_node + '.color2R', -1)
				util_set_attr(up_shoulder_blend_node + '.color2G', 0)
				util_set_attr(up_shoulder_blend_node + '.color2B', 0)

				# elbow flip 1
				util_set_attr(up_shoulder_blend_node + '.color1R', 0)
				util_set_attr(up_shoulder_blend_node + '.color1G', 1)
				util_set_attr(up_shoulder_blend_node + '.color1B', -1)

			util_connect_attr(up_shoulder_blend_node + '.outputR', arm_shoulder_ik + '.dWorldUpVectorX')
			util_connect_attr(up_shoulder_blend_node + '.outputG', arm_shoulder_ik + '.dWorldUpVectorY')
			util_connect_attr(up_shoulder_blend_node + '.outputB', arm_shoulder_ik + '.dWorldUpVectorZ')

			# up end shoulder vector
			if side == 'L':
				# World Up Object 2
				util_set_attr(up_end_shoulder_blend_node + '.color2R', 0)
				util_set_attr(up_end_shoulder_blend_node + '.color2G', 0)
				util_set_attr(up_end_shoulder_blend_node + '.color2B', 1)

				util_set_attr(up_end_shoulder_blend_node + '.color1R', 1)
				util_set_attr(up_end_shoulder_blend_node + '.color1G', 0)
				util_set_attr(up_end_shoulder_blend_node + '.color1B', 0)

			if side == 'R':
				# World Up Object 2
				# elbow flip 0
				util_set_attr(up_end_shoulder_blend_node + '.color2R', -1)
				util_set_attr(up_end_shoulder_blend_node + '.color2G', 0)
				util_set_attr(up_end_shoulder_blend_node + '.color2B', 0)

				# elbow flip 1
				util_set_attr(up_end_shoulder_blend_node + '.color1R', 0)
				util_set_attr(up_end_shoulder_blend_node + '.color1G', 1)
				util_set_attr(up_end_shoulder_blend_node + '.color1B', -1)

			util_connect_attr(up_end_shoulder_blend_node + '.outputR', arm_shoulder_ik + '.dWorldUpVectorEndX')
			util_connect_attr(up_end_shoulder_blend_node + '.outputG', arm_shoulder_ik + '.dWorldUpVectorEndY')
			util_connect_attr(up_end_shoulder_blend_node + '.outputB', arm_shoulder_ik + '.dWorldUpVectorEndZ')

			# elbow up vector
			if side == 'L':
				# World Up Object
				util_set_attr(up_elbow_blend_node + '.color1R', 1)
				util_set_attr(up_elbow_blend_node + '.color1G', 0)
				util_set_attr(up_elbow_blend_node + '.color1B', 0)

				util_set_attr(up_elbow_blend_node + '.color2R', 0)
				util_set_attr(up_elbow_blend_node + '.color2G', 0)
				util_set_attr(up_elbow_blend_node + '.color2B', 1)

			if side == 'R':
				# World Up Object
				# elbow flip 0
				util_set_attr(up_elbow_blend_node + '.color2R', 0)
				util_set_attr(up_elbow_blend_node + '.color2G', 0)
				util_set_attr(up_elbow_blend_node + '.color2B', 1)

				# elbow flip 1
				util_set_attr(up_elbow_blend_node + '.color1R', -1)
				util_set_attr(up_elbow_blend_node + '.color1G', 1)
				util_set_attr(up_elbow_blend_node + '.color1B', 0)

			util_connect_attr(up_elbow_blend_node + '.outputR', arm_elbow_ik + '.dWorldUpVectorX')
			util_connect_attr(up_elbow_blend_node + '.outputG', arm_elbow_ik + '.dWorldUpVectorY')
			util_connect_attr(up_elbow_blend_node + '.outputB', arm_elbow_ik + '.dWorldUpVectorZ')

			# elbow up end vector
			if side == 'L':
				# World Up Object 2
				util_set_attr(up_end_elbow_blend_node + '.color1R', 0)
				util_set_attr(up_end_elbow_blend_node + '.color1G', 0)
				util_set_attr(up_end_elbow_blend_node + '.color1B', 1)

				util_set_attr(up_end_elbow_blend_node + '.color2R', 0)
				util_set_attr(up_end_elbow_blend_node + '.color2G', 0)
				util_set_attr(up_end_elbow_blend_node + '.color2B', 0)

			if side == 'R':
				# World Up Object 2
				# elbow flip 0
				util_set_attr(up_end_elbow_blend_node + '.color2R', 0)
				util_set_attr(up_end_elbow_blend_node + '.color2G', 0)
				util_set_attr(up_end_elbow_blend_node + '.color2B', 1)

				# elbow flip 1
				util_set_attr(up_end_elbow_blend_node + '.color1R', 0)
				util_set_attr(up_end_elbow_blend_node + '.color1G', 0)
				util_set_attr(up_end_elbow_blend_node + '.color1B', 1)

			util_connect_attr(up_end_elbow_blend_node + '.outputR', arm_elbow_ik + '.dWorldUpVectorEndX')
			util_connect_attr(up_end_elbow_blend_node + '.outputG', arm_elbow_ik + '.dWorldUpVectorEndY')
			util_connect_attr(up_end_elbow_blend_node + '.outputB', arm_elbow_ik + '.dWorldUpVectorEndZ')

			# finally connect the translation into the offset grp
			util_connect_attr(tr_blend_node + '.outputR', pole_vector_offset_tx_attr)
			util_connect_attr(tr_blend_node + '.outputG', pole_vector_offset_ty_attr)
			util_connect_attr(tr_blend_node + '.outputB', pole_vector_offset_tz_attr)
	return True


def old_way():
	"""
	Mimics the setup of Freddy for other rigs.
	DEPRECIATED DO NOT USE
	:returns: <bool> True for success. <bool> False for failure.
	"""
	pole_vector_ctrl = "{}_Arm_PoleVector_Ctrl"
	ikfk_switch_ctrl = "{}_Arm_IKFKSwitch_Ctrl"
	elbow_hdl =  "{}_Arm_Elbow_Bend0_Hdl"
	arm_shoulder_hdl = "{}_Arm_Shoulder_Bend0_Hdl"
	flip_attr = 'ElbowFlip'

	for side in 'LR':
		flip_blend_node = '{}_{}_Blnd'.format(side, flip_attr)
		flip_blend_spline_node = '{}_{}_Spline_Blnd'.format(side, flip_attr)
		flip_mult_node = '{}_MD'.format(flip_attr)

		side_elbow_hdl = elbow_hdl.format(side)
		side_arm_shoulder_hdl = arm_shoulder_hdl.format(side)
		side_pole_vector_ctrl = pole_vector_ctrl.format(side)
		side_ikfk_switch_ctrl = ikfk_switch_ctrl.format(side)
		flip_ctrl_attr = '{}.{}'.format(side_pole_vector_ctrl, flip_attr)

		if not any(map(cmds.objExists, [side_elbow_hdl, side_arm_shoulder_hdl, side_pole_vector_ctrl, side_ikfk_switch_ctrl])):
			cmds.warning("[TOTS Wing Fix] :: Insufficient nodes found to continue with this operation.")
			return False

		# check node existence
		if not cmds.objExists(flip_ctrl_attr):
			cmds.addAttr(side_pole_vector_ctrl, at='float', ln=flip_attr, dv=0, k=1, min=0, max=1, h=0)

		print("Creating: ", flip_blend_node)
		if not cmds.objExists(flip_blend_node):
			cmds.createNode('blendColors', n=flip_blend_node)
		cmds.setAttr('{}.color1R'.format(flip_blend_node), -34.151)
		cmds.setAttr('{}.color1G'.format(flip_blend_node), 56.747)
		cmds.setAttr('{}.color1B'.format(flip_blend_node), 1.0)
		cmds.setAttr('{}.color2R'.format(flip_blend_node), 0.0)
		cmds.setAttr('{}.color2G'.format(flip_blend_node), 0.0)
		cmds.setAttr('{}.color2B'.format(flip_blend_node), 0.0)

		print("Creating: ", flip_blend_spline_node)
		if not cmds.objExists(flip_blend_spline_node):
			cmds.createNode('blendColors', n=flip_blend_spline_node)
		cmds.setAttr('{}.color1R'.format(flip_blend_spline_node), 1.0)
		cmds.setAttr('{}.color1G'.format(flip_blend_spline_node), 0.0)
		cmds.setAttr('{}.color1B'.format(flip_blend_spline_node), 0.0)
		cmds.setAttr('{}.color2R'.format(flip_blend_spline_node), 0.0)
		cmds.setAttr('{}.color2G'.format(flip_blend_spline_node), 1.0)
		cmds.setAttr('{}.color2B'.format(flip_blend_spline_node), 0.0)

		if not cmds.objExists(flip_mult_node):
			cmds.createNode('multiplyDivide', n=flip_mult_node)

		# perform multiplyDivide connections
		pv_attr = "{}.elbowFlip".format(side_pole_vector_ctrl)
		ikfk_attr = "{}.FKIKSwitch".format(side_ikfk_switch_ctrl)
		if "L" in side:
			mult_plug = 'X'
		else:
			mult_plug = 'Y'
		if not cmds.isConnected(pv_attr, '{}.input1{}'.format(flip_mult_node, mult_plug)):
			cmds.connectAttr(pv_attr, '{}.input1{}'.format(flip_mult_node, mult_plug), f=1)
		if not cmds.isConnected(ikfk_attr, '{}.input2{}'.format(flip_mult_node, mult_plug)):
			cmds.connectAttr(ikfk_attr, '{}.input2{}'.format(flip_mult_node, mult_plug), f=1)
		if not cmds.isConnected('{}.output{}'.format(flip_mult_node, mult_plug), '{}.blender'.format(flip_blend_node)):
			cmds.connectAttr('{}.output{}'.format(flip_mult_node, mult_plug), '{}.blender'.format(flip_blend_node))

		# perform blend node connections
		spline_blend_r_attr = "{}.outputR".format(flip_blend_spline_node)
		spline_blend_g_attr = "{}.outputG".format(flip_blend_spline_node)

		# Arm_Shoulder_Bend0_Hdl
		if not cmds.isConnected(spline_blend_r_attr, '{}.dWorldUpVectorX'.format(side_arm_shoulder_hdl)):
			cmds.connectAttr(spline_blend_r_attr, '{}.dWorldUpVectorX'.format(side_arm_shoulder_hdl), f=1)
		if not cmds.isConnected(spline_blend_r_attr, '{}.dWorldUpVectorEndX'.format(side_arm_shoulder_hdl)):
			cmds.connectAttr(spline_blend_r_attr, '{}.dWorldUpVectorEndX'.format(side_arm_shoulder_hdl), f=1)

		if not cmds.isConnected(spline_blend_g_attr, '{}.dWorldUpVectorZ'.format(side_arm_shoulder_hdl)):
			cmds.connectAttr(spline_blend_g_attr, '{}.dWorldUpVectorZ'.format(side_arm_shoulder_hdl), f=1)
		if not cmds.isConnected(spline_blend_g_attr, '{}.dWorldUpVectorEndZ'.format(side_arm_shoulder_hdl)):
			cmds.connectAttr(spline_blend_g_attr, '{}.dWorldUpVectorEndZ'.format(side_arm_shoulder_hdl), f=1)

		# Arm_Elbow_Bend0_Hdl
		if not cmds.isConnected(spline_blend_r_attr, '{}.dWorldUpVectorX'.format(side_elbow_hdl)):
			cmds.connectAttr(spline_blend_r_attr, '{}.dWorldUpVectorX'.format(side_elbow_hdl), f=1)

		if not cmds.isConnected(spline_blend_g_attr, '{}.dWorldUpVectorZ'.format(side_elbow_hdl)):
			cmds.connectAttr(spline_blend_g_attr, '{}.dWorldUpVectorZ'.format(side_elbow_hdl), f=1)
	return True


def insert_null(ctrl_node=""):
	"""
	Inserts a null node underneath a specific controller.
	:param ctrl_node: <str> ctrl node to parent under.
	:returns: <str> null xform object.
	"""
	cmds.select(cl=1)
	x_form = cmds.xform(ctrl_node, ws=1, m=1, q=1)
	end_name = ctrl_node.rpartition('_')[-1]
	null_name = ctrl_node.replace('_{}'.format(end_name), '_Null')
	if cmds.objExists(null_name):
		cmds.delete(null_name)
	cmds.group(name=null_name, world=1, em=1)
	print("[Elbow Flip Wing Fix] :: {} Created.".format(null_name))
	cmds.xform(null_name, ws=1, m=x_form)
	if ctrl_node not in check_parent(null_name):
		cmds.parent(null_name, ctrl_node)
	rot_y = cmds.getAttr('{}.rotateY'.format(null_name))
	cmds.setAttr('{}.rotateY'.format(null_name), rot_y + (-90))
	return null_name


def insert_target_null(ctrl_node="", target_pos="", parent_node="", world=0):
	"""
	inserts a null with this target position.
	:param ctrl_node: <str> ctrl node to parent under.
	:param target_pos: <str> target position transform.
	:param parent_node: <str> parent the node to this node.
	:param world: <bool>, <int>, insert the transform as world space.
	"""
	cmds.select(cl=1)
	x_form = cmds.xform(target_pos, ws=world, m=1, q=1)
	end_name = ctrl_node.rpartition('_')[-1]
	null_name = ctrl_node.replace('_{}'.format(end_name), '_Tgt')
	if cmds.objExists(null_name):
		cmds.delete(null_name)
	cmds.group(name=null_name, world=1, em=1)
	cmds.xform(null_name, ws=1, m=x_form)
	print("[Elbow Flip Wing Fix] :: {} Created.".format(null_name))
	# if target_pos not in check_parent(ctrl_node):
	try:
		if parent_node:
			cmds.parent(null_name, parent_node)
		else:
			parent_node = check_parent(ctrl_node)
			cmds.parent(null_name, parent_node)
	except RuntimeError:
		pass
	return null_name


def clear_parent_constraints(ctrl_node=""):
	"""
	Removes the constraints from this node.
	:returns: <bool> True for success. <False> for empty.
	"""
	attributes = ['.rx', '.ry', '.rz', '.tx', '.ty', '.tz']
	connections = []
	for attr in attributes:
		map(connections.append, cmds.listConnections(ctrl_node + attr, s=1, d=0) or [])
	if not connections:
		return False
	connections = list(set(connections))
	print('deleting: ', connections)
	cmds.delete(connections)
	return True


def clear_orient_constraints(ctrl_node=""):
	"""
	Removes the constraints from this node.
	:returns: <bool> True for success. <False> for empty.
	"""
	attributes = ['.rx', '.ry', '.rz']
	connections = []
	for attr in attributes:
		src_connection = cmds.listConnections(ctrl_node + attr, s=1, d=0)
		if not src_connection:
			continue
		connections.extend(src_connection)
	connections = list(set(connections))
	if connections:
		if not 'orientConstraint' in cmds.objectType(connections):
			raise RuntimeError('[TOTS Elbow Flip Error] :: Please delete this node: {}'.format(connections))
		cmds.delete(connections)
	return True


def clear_point_constraints(ctrl_node=""):
	"""
	Removes the constraints from this node.
	:returns: <bool> True for success. <False> for empty.
	"""
	attributes = ['.tx', '.ty', '.tz']
	connections = []
	for attr in attributes:
		src_connection = cmds.listConnections(ctrl_node + attr, s=1, d=0)
		if not src_connection:
			continue
		connections.extend(src_connection)
	connections = list(set(connections))
	if connections:
		if not 'pointConstraint' in cmds.objectType(connections):
			raise RuntimeError('[TOTS Elbow Flip Error] :: Please delete this node: {}'.format(connections))
		cmds.delete(connections)
	return True


def get_cnst_weight_attrs(cnst_name=""):
	"""
	Gets the weighted attribute names.
	:returns: <list> weighted attributes.
	"""
	return cmds.listAttr(cnst_name, ud=1, k=1)


def check_parent(ctrl_name=""):
	"""
	Returns the parent object of the transform.
	:returns: <str> parent object.
	"""
	par_node = cmds.listRelatives(ctrl_name, p=1, type='transform') or []
	if par_node:
		return par_node[0]
	return par_node


def fix_flip_old():
	"""
	Solve Elbow flip wing problem.
	:returns: <bool> True for success. <bool> False for failure.
	"""
	print("[Tots Wing Flip Fix] :: Called.")
	wrist_auto_aim_grp = '{}_Arm_Btm_Bend_End_Ctrl_Wrist_AutoAim_Shoulder_Grp'
	arm_wrist_fk_ctrl = '{}_Arm_Wrist_Fk_Ctrl'
	arm_shoulder_fk_jnt = '{}_Arm_Shoulder_Fk_Jnt'
	arm_shoulder_fk_ctrl = "{}_Arm_Shoulder_Fk_Gimbal_Ctrl"
	arm_elbow_ik_jnt = "{}_Arm_Elbow_Ik_Jnt"
	arm_elbow_fk_jnt = '{}_Arm_Elbow_Fk_Jnt'
	arm_elbow_fk_ctrl = '{}_Arm_Elbow_Fk_Ctrl'
	ikfk_switch_ctrl = "{}_Arm_IKFKSwitch_Ctrl"
	pv_ctrl = '{}_Arm_PoleVector_Ctrl'
	flip_attr = 'ElbowFlip'

	for side in 'LR':
		side_arm_shoulder_fk_ctrl = arm_shoulder_fk_ctrl.format(side)
		side_arm_wrist_fk_ctrl = arm_wrist_fk_ctrl.format(side)
		side_wrist_auto_aim_grp = wrist_auto_aim_grp.format(side)
		side_arm_elbow_ik_jnt  = arm_elbow_ik_jnt.format(side)
		side_arm_elbow_fk_jnt = arm_elbow_fk_jnt.format(side)
		side_arm_elbow_fk_ctrl = arm_elbow_fk_ctrl.format(side)
		side_arm_shoulder_fk_jnt = arm_shoulder_fk_jnt.format(side)
		flip_blend_node = '{}_Shoulder_{}_Blnd'.format(side, flip_attr)
		flip_condition_node = '{}_Shoulder_{}_Cnd'.format(side, flip_attr)
		side_pv_ctrl = pv_ctrl.format(side)
		side_ikfk_switch_ctrl = ikfk_switch_ctrl.format(side)
		elbow_flip_attr = '{}.{}'.format(side_pv_ctrl, flip_attr)
		wrist_ik_rev_node = '{}_Ik_Wrist_Rev'.format(side)
		fkik_switch_attr = '{}.FKIKSwitch'.format(side_ikfk_switch_ctrl)

		# install checks
		if not cmds.objExists(side_pv_ctrl):
			raise RuntimeError('[TOTS Elbow Flip Error] :: {} does not exist.'.format(side_pv_ctrl))

		if not cmds.objExists(side_ikfk_switch_ctrl):
			raise RuntimeError('[TOTS Elbow Flip Error] :: {} does not exist.'.format(side_ikfk_switch_ctrl))

		if not cmds.objExists(elbow_flip_attr):
			raise RuntimeError('[TOTS Elbow Flip Error] :: {} does not exist.'.format(elbow_flip_attr))

		if not cmds.objExists(side_arm_shoulder_fk_ctrl):
			raise RuntimeError('[TOTS Elbow Flip Error] :: {} does not exist.'.format(side_arm_shoulder_fk_ctrl))

		if not cmds.objExists(side_wrist_auto_aim_grp):
			raise RuntimeError('[TOTS Elbow Flip Error] :: {} does not exist.'.format(side_wrist_auto_aim_grp))

		# construct blend colors node
		if not cmds.objExists(flip_blend_node):
			cmds.createNode('blendColors', name=flip_blend_node)

		# construct condition node
		if not cmds.objExists(flip_condition_node):
			cmds.createNode('condition', name=flip_condition_node)

		# insert a null object under the shoulder fk controller
		shoulder_null_obj = insert_null(side_arm_shoulder_fk_ctrl)
		elbow_null_obj = insert_null(side_arm_elbow_fk_ctrl)

		# removes constraint
		clear_orient_constraints(side_arm_shoulder_fk_jnt)
		clear_orient_constraints(side_arm_elbow_fk_jnt)
		clear_parent_constraints(side_wrist_auto_aim_grp)

		orient_relationship = {
			shoulder_null_obj: {'jnt': side_arm_shoulder_fk_jnt, 'ctrl': side_arm_shoulder_fk_ctrl},
			elbow_null_obj: {'jnt': side_arm_elbow_fk_jnt, 'ctrl': side_arm_elbow_fk_ctrl}
			}

		for null_obj in orient_relationship:
			fk_joint = orient_relationship[null_obj]['jnt']
			ctrl_name = orient_relationship[null_obj]['ctrl']
			# creates new constraint
			orient_node = cmds.orientConstraint(ctrl_name, null_obj, fk_joint, mo=0)[0]
			gimbal_weight, null_weight = get_cnst_weight_attrs(orient_node)
			orient_gimbal_wgt_attr = '{}.{}'.format(orient_node, gimbal_weight)
			orient_null_wgt_attr = '{}.{}'.format(orient_node, null_weight)

			# attributes

			# connect blend colors node
			blend_b_attr = '{}.blender'.format(flip_blend_node)
			blend_1r_attr = '{}.color1R'.format(flip_blend_node)
			blend_1g_attr = '{}.color1G'.format(flip_blend_node)
			blend_2r_attr = '{}.color2R'.format(flip_blend_node)
			blend_2g_attr = '{}.color2G'.format(flip_blend_node)
			blend_or_attr = '{}.outputR'.format(flip_blend_node)
			blend_og_attr = '{}.outputG'.format(flip_blend_node)

			if not cmds.isConnected(blend_or_attr, orient_gimbal_wgt_attr):
				cmds.connectAttr(blend_or_attr, orient_gimbal_wgt_attr, f=1)

			if not cmds.isConnected(blend_og_attr, orient_null_wgt_attr):
				cmds.connectAttr(blend_og_attr, orient_null_wgt_attr, f=1)

			if not cmds.isConnected(fkik_switch_attr, blend_b_attr):
				cmds.connectAttr(fkik_switch_attr, blend_b_attr, f=1)

			# connect condition node
			cnd_ft_attr = '{}.firstTerm'.format(flip_condition_node)
			cnd_or_attr = '{}.outColorR'.format(flip_condition_node)
			cnd_og_attr = '{}.outColorG'.format(flip_condition_node)
			pv_eflip_attr = '{}.ElbowFlip'.format(side_pv_ctrl)
			
			if not cmds.isConnected(pv_eflip_attr, cnd_ft_attr):
				cmds.connectAttr(pv_eflip_attr, cnd_ft_attr, f=1)
			
			if not cmds.isConnected(cnd_or_attr, blend_2r_attr):
				cmds.connectAttr(cnd_or_attr, blend_2r_attr, f=1)

			if not cmds.isConnected(cnd_og_attr, blend_2g_attr):
				cmds.connectAttr(cnd_og_attr, blend_2g_attr, f=1)

			# set conditon settings	
			cmds.setAttr('{}.secondTerm'.format(flip_condition_node), 1)
			cmds.setAttr('{}.colorIfTrueR'.format(flip_condition_node), 0)
			cmds.setAttr('{}.colorIfTrueG'.format(flip_condition_node), 1)
			cmds.setAttr('{}.colorIfFalseR'.format(flip_condition_node), 1)
			cmds.setAttr('{}.colorIfFalseG'.format(flip_condition_node), 0)

		# now perform a position relationship
		cmds.setAttr(elbow_flip_attr, 1)
		elbow_target_obj = insert_target_null(side_arm_elbow_fk_ctrl, side_arm_elbow_ik_jnt, world=1)
		clear_point_constraints(fk_joint)
		point_node = cmds.pointConstraint(side_arm_elbow_fk_ctrl, elbow_target_obj, fk_joint, mo=0)[0]
		ctrl_weight, null_weight = get_cnst_weight_attrs(point_node)
		ctrl_weight_attr = '{}.{}'.format(point_node, ctrl_weight)
		null_weight_attr = '{}.{}'.format(point_node, null_weight)

		if not cmds.isConnected(blend_or_attr, ctrl_weight_attr):
			cmds.connectAttr(blend_or_attr, ctrl_weight_attr, f=1)

		if not cmds.isConnected(blend_og_attr, null_weight_attr):
			cmds.connectAttr(blend_og_attr, null_weight_attr, f=1)

		# add a constraint to the auto-aim grp
		point_cnst = cmds.pointConstraint(side_arm_wrist_fk_ctrl, side_wrist_auto_aim_grp, mo=0)[0]
		fk_wrist_ctrl_weight = get_cnst_weight_attrs(point_cnst)[0]
		if not cmds.objExists(wrist_ik_rev_node):
			cmds.createNode('reverse', name=wrist_ik_rev_node)
		rev_node_input_x = wrist_ik_rev_node + '.inputX'
		rev_node_output_x = wrist_ik_rev_node + '.outputX'
		if not cmds.isConnected(fkik_switch_attr, rev_node_input_x):
			cmds.connectAttr(fkik_switch_attr, rev_node_input_x)
		if not cmds.isConnected(rev_node_output_x, '{}.{}'.format(point_cnst, fk_wrist_ctrl_weight)):
			cmds.connectAttr(rev_node_output_x, '{}.{}'.format(point_cnst, fk_wrist_ctrl_weight))
		orient_offset_null = insert_target_null(side_wrist_auto_aim_grp, side_arm_elbow_fk_ctrl, parent_node=side_arm_elbow_fk_ctrl, world=1)
		cmds.orientConstraint(orient_offset_null, side_wrist_auto_aim_grp, skip=["x", "z"], mo=0)
		cmds.orientConstraint(side_arm_wrist_fk_ctrl, orient_offset_null, skip=["x", "z"], mo=0)

		# finalize fix
		cmds.setAttr(elbow_flip_attr, 0)

	# return MS::kSuccess
	return True

