# convert to dynamic chain
# select top control of chain
# make sure that the Offset Group is parent constrained before converting EG: L_Ear_01_Ctrl_Offset_Grp
# if you're having trouble adding multiple chains to a rig that already has dynamics, do one chain at a time.

import maya.cmds as cmds
import sys

pths = sys.path
for pth in ['G:/Pipeline/Rigging']:
    if pth not in pths:
        sys.path.append(pth)

import DynamicToolBox as dtb; reload(dtb)

def do_it():
    my_selection = cmds.ls(sl=1)
    if my_selection == []:
        cmds.error('please select something')
    for e in my_selection:
        if '_01_Ctrl' not in e:
            cmds.error('please select the base of your chain')
    packGrp = 'Dynamics_BuildPack'
    if cmds.objExists(packGrp) == False:
        cmds.group(em=1, n=packGrp)
    cmds.select(d=1)

    for each in my_selection:
        my_chain = each.replace('_01_Ctrl', '')
        my_joints = cmds.ls(my_chain + '_Fk*_Bnd_Jnt')
        my_DC_joints = []

        cmds.select(d=1)
        t_root = cmds.xform(my_joints[0], ws=1, q=1, t=1)
        offset_root = (my_joints[0].replace('Fk', '')).replace('_Bnd_Jnt', '_Offset_Jnt_Grp')
        r_root = cmds.xform(offset_root, ws=1, q=1, ro=1)
        DC_root_jnt = cmds.joint(p=t_root,
                                 o=r_root,
                                 n=(my_joints[0].replace('Fk01', 'DC_Root')).replace('_Bnd_Jnt', ''),
                                 a=1)
        cmds.select(d=1)
        my_DC_joints.append(DC_root_jnt)

        for j in my_joints:
            t = cmds.xform(j, ws=1, q=1, t=1)
            offset = (j.replace('Fk', '')).replace('_Bnd_Jnt', '_Offset_Jnt_Grp')
            if cmds.objExists(offset):
                r = cmds.xform(offset, os=1, q=1, ro=1)
            DC_jnt = cmds.joint(p=t, o=r, n=(j.replace('Fk', 'DC_')).replace('_Bnd_Jnt', ''), a=1)
            if cmds.objExists(offset) == False:
                for orient in ['.jointOrientX', '.jointOrientY', '.jointOrientZ']:
                    cmds.setAttr(DC_jnt + orient, 0)
            my_DC_joints.append(DC_jnt)

        cmds.parent(my_DC_joints[1], my_DC_joints[0])
        cmds.parent(my_DC_joints[0], packGrp)

    # if the dynamics were pr
    if cmds.objExists("Dynamic_Ctrl"):
        dtb.ChainAdd()
    else:
        dtb.AutoChainBuild()

    cmds.setAttr('Control_Ctrl.DynamicCtrls', 1)

    for each in my_selection:
        my_constraint = each + '_Offset_Grp_parentConstraint1'
        cnc = cmds.listConnections(my_constraint + '.target[0].targetParentMatrix')[0]
        cmds.parentConstraint(cnc, each.replace('_01_Ctrl', '_DC_Root_Ctrl_Offset_Grp'), mo=1)
        cmds.scaleConstraint(cnc, each.replace('_01_Ctrl', '_DC_Root_Ctrl_Offset_Grp'), mo=1)
        my_controls = cmds.ls(each.replace('_01_Ctrl', '_??_Ctrl')) + cmds.ls(
            each.replace('_01_Ctrl', '_Tweak_??_Ctrl')) + cmds.ls(each.replace('_01', '_??_Tweak_Ctrl'))
        my_dyn_controls = cmds.ls(each.replace('_01_Ctrl', '_DC_??_Ctrl')) + cmds.ls(
            each.replace('_01_Ctrl', '_DC_??_Tweak_Ctrl'))

        for ctrl in my_controls:
            if 'Tweak_Ctrl' in ctrl:
                spl = ctrl.split('_')
                tweak = cmds.rename(ctrl, ctrl.replace('_' + spl[-3], '_Tweak_' + spl[-3]))
                tweak = cmds.rename(tweak, tweak.replace('_Tweak_Ctrl', '_Temp'))
            else:
                cmds.rename(ctrl, ctrl.replace('_Ctrl', '_Temp'))
        for dyn_ctrl in my_dyn_controls:
            if 'Tweak' in dyn_ctrl:
                spl = dyn_ctrl.split('_')
                tweak = cmds.rename(dyn_ctrl, dyn_ctrl.replace('_' + spl[-3], '_Tweak_' + spl[-3]))
                tweak = cmds.rename(tweak, tweak.replace('_Tweak_Ctrl', '_Ctrl'))
                cmds.rename(tweak, tweak.replace('_DC', ''))
            else:
                cmds.rename(dyn_ctrl, dyn_ctrl.replace('_DC', ''))
        my_temp_controls = cmds.ls('*_Temp')
        for my_c in my_temp_controls:
            my_parent = my_c.replace('_Temp', '_Ctrl')
            my_temp_children = cmds.listRelatives(my_c, c=1)
            my_children = cmds.listRelatives(my_parent, c=1)
            for child in my_children:
                if 'Shape' in child:
                    cmds.delete(child)
            for temp_child in my_temp_children:
                if 'Shape' in temp_child:
                    cmds.parent(temp_child, my_parent, r=1, s=1)
                    cmds.connectAttr('Control_Ctrl.DynamicCtrls', temp_child + '.visibility', f=1)
                    cmds.connectAttr('Dynamic_DisplayType_CND.outColorR', temp_child + '.overrideDisplayType', f=1)
                    cmds.rename(temp_child, temp_child.replace('Temp', 'Ctrl'))

        my_chain = each.replace('_01_Ctrl', '')
        my_joints = cmds.ls(my_chain + '_Fk*_Bnd_Jnt')
        for my_joint in my_joints:
            my_DC = (my_joint.replace('Fk', 'DC_')).replace('_Jnt', '')
            if cmds.objExists(my_DC):
                cmds.parent(my_joint, my_DC)
        cmds.delete(my_chain + '_01_Ctrl_Offset_Grp')
        cmds.delete(my_chain + '_01_Offset_Jnt_Grp')

    cmds.delete(packGrp)






def doIt(self, args):
	'''
	Find all namespaces in scene and remove them.
	Except for default namespaces
	'''

	# Get a list of namespaces in the scene
	# recursive Flag seraches also children
	# internal Flag excludes default namespaces of Maya
	namespaces = []
	for ns in pm.listNamespaces( recursive  =True, internal =False):
		namespaces.append(ns)
		print 'Namespace ' + ns + ' added to list.'

	# Reverse Iterate through the contents of the list to remove the deepest layers first
	for ns in reversed(namespaces):
		currentSpace = ns

		pm.namespace(removeNamespace = ns, mergeNamespaceWithRoot = True)
		print currentSpace + ' has been merged with Root!'

	# Empty the List
	namespaces[:] = []