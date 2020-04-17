import math_utils; reload(math_utils)
import icon_api.node as i_node
import deform_utils

# build deformer
name= "Tree_Bend_32"
if cmds.objExists(name + '_BendHandle'):
	raise RuntimeError('[Bendy Rig] :: Cancelling Operation!')
selected = cmds.ls(sl=1)
bend_deformer, bend_handle = cmds.nonLinear(selected, type='bend')
x, y, z = math_utils.bounding_box(object_name=selected, get_btm_y=1, xyz=1)
cmds.setAttr(bend_deformer + '.lowBound', 0.0)
cmds.setAttr(bend_deformer + '.highBound', 3.0)
cmds.setAttr(bend_handle + '.template', 1)
cmds.xform(bend_handle, t=(x, y, z), ws=1)
cmds.rename(bend_handle, name + '_BendHandle')
cmds.rename(bend_deformer, name + '_Bend')



# create control
locator = cmds.ls(sl=1)
i_control = i_node.create("control", 
    name=name, control_type="2D Circle", with_gimbal=True, color="aqua")
offset = str(i_control.top_tfm)
cmds.select(offset)
cmds.xform(offset, m=cmds.xform(locator, ws=1, m=1, q=1))



# control finalization
selection = cmds.ls(sl=1)
if selection[0].endswith('_Offset_Grp'):
	selection = [selection[0].replace('_Offset_Grp', '')]
name = selection[0].rpartition('_Ctrl')[0]
if not cmds.objExists(selection[0] + '.Arc'):
	cmds.addAttr(selection[0], ln='Arc', at='float', k=1)
	cmds.setAttr(selection[0] + '.Arc', k=1)
cmds.connectAttr(selection[0] + '.Arc', name+'_Bend.curvature', f=1)
for attr in ('.rx', '.rz', '.sx', '.sy', '.sz'):
	cmds.setAttr(selection[0] + attr, k=0, l=1)
for sel  in selected:
	cmds.parentConstraint(name+'_Gimbal_Ctrl', sel, mo=1)
	cmds.scaleConstraint(name+'_Gimbal_Ctrl', sel, mo=1)

cmds.parent(name + '_BendHandle', name+'_Gimbal_Ctrl')




# invert the arc attributes
tree_ctrls = cmds.ls(sl=1)
for ea in tree_ctrls:
	bend_attr = cmds.listConnections(ea + '.Arc', s=0, d=1, plugs=1, skipConversionNodes=1)
	inverter_name = ea.replace('_Ctrl', '_Arc_Inverter')
	cmds.createNode('multDoubleLinear', name=inverter_name)
	cmds.connectAttr(ea + '.Arc', inverter_name + '.input1')
	cmds.setAttr(inverter_name + '.input2', -1)
	cmds.connectAttr(inverter_name + '.output', bend_attr[0], f=1)
	

	
master_ctrl = 'R_Tree_Row_Ctrl.Arc'
for ea in cmds.ls('Tree_Bend_*_Arc_Inverter'):
	m_linear = ea.replace('_Arc_Inverter', 'Arc_Master_Linear')
	cmds.createNode('addDoubleLinear', name=m_linear)
	bend_name = ea.replace('_Arc_Inverter', '_Bend')
	cmds.connectAttr(ea + '.output', m_linear + '.input1')
	cmds.connectAttr(master_ctrl, m_linear + '.input2')
	cmds.connectAttr(m_linear + '.output', bend_name + '.curvature', f=1)
	
	
	
master_ctrl = 'R_Tree_Row_Ctrl.Arc_Rotate'
for ea in cmds.ls('Tree_Bend_??_Inverter'):
	m_linear = ea.replace('_Inverter', '_Arc_Rotate_Master_Linear')
	cmds.createNode('addDoubleLinear', name=m_linear)
	bend_name = ea.replace('_Inverter', '_BendHandle')
	cmds.connectAttr(ea + '.output', m_linear + '.input1')
	cmds.connectAttr(master_ctrl, m_linear + '.input2')
	cmds.connectAttr(m_linear + '.output', bend_name + '.rotateY', f=1)


def reposition_gimbal_ctrl(selection=""):
	"""
	Reppositions the gimbal controller.
	:return: <bool> True for success. <bool> False for failure.
	"""
	main_ctrl, gimbal_ctrl = cmds.listRelatives(cmds.filterExpand(selection, sm=9)[-2:], p=1, type='transform')

	base_name = main_ctrl.rpartition('_Ctrl')[0]
	gimbal_offset_name = gimbal_ctrl + '_Offset_Grp'
	bend_handle_name = base_name + '_BendHandle_Offset_Grp'
	bend_deformer = base_name + '_Bend'

	deform_set = deform_utils.util_find_deformer_set(bend_deformer)
	return_list = deform_utils.util_get_set_members(deform_set)
	geos = [f[0] for f in return_list]

	cmds.setAttr(main_ctrl + '.GimbalVis', 1)
	# delete the tree geo constraints
	for ea in geos:
		p_cnst = cmds.listConnections(ea, s=1, d=0, type='parentConstraint')
		if p_cnst:
			cmds.delete(p_cnst[0])

		s_cnst = cmds.listConnections(ea, s=1, d=0, type='scaleConstraint')
		if s_cnst:
			cmds.delete(s_cnst[0])

	# reposition the gimbal controller
	get_pos = cmds.xform(bend_handle_name, t=1, ws=0, q=1)
	cmds.parent(bend_handle_name, main_ctrl)
	cmds.xform(gimbal_offset_name, t=get_pos)
	cmds.parent(bend_handle_name, gimbal_ctrl)
	for ea in geos:
		try:
			cmds.parentConstraint(gimbal_ctrl, ea, mo=1)
		except RuntimeError:
			pass
		try:
			cmds.scaleConstraint(gimbal_ctrl, ea, mo=1)
		except RuntimeError:
			pass
	return True
