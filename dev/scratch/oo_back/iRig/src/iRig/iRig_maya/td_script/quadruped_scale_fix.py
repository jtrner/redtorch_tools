# import maya modules
from maya import cmds


def check_scale_constraint(node_name=''):
    """
    :@param node_name: <str> check this node for scale constraint.
    """
    scale_cns = cmds.listConnections(node_name + '.sx', s=1, d=0, type='scaleConstraint')
    return bool(scale_cns)


def check_parent_constraint(node_name=''):
    """
    :@param node_name: <str> check this node for parent constraint.
    """
    scale_cns = cmds.listConnections(node_name + '.tx', s=1, d=0, type='parentConstraint')
    return bool(scale_cns)


def install_quadruped_scale_factors():
    """
    :description: Creates multiplyDivide scaleFactor nodes and attaches the scaleXYZ to the bendJoints directly.
    :returns: <bool> True for success.
    """
    stretch_ls = []
    for i in range(0, 4):
        stretch_ls += cmds.ls('*{}Stretch_Md'.format(i))
    stretch_ls += cmds.ls('*_StretchStart_Md')

    for stretch_mult in stretch_ls:
        node_plug = cmds.listConnections(stretch_mult + '.input1X', plugs=1)[0]
        # connect via RigScaleOffset_MD if it exists
        if cmds.objExists('RigScaleOffset_MD'):
            if not cmds.isConnected('RigScaleOffset_MD.outputX', stretch_mult + '.input2X'):
                cmds.connectAttr('RigScaleOffset_MD.outputX', stretch_mult + '.input2X', f=1)
        # else connect using the Root ScaleXYZ
        else:
            if not cmds.isConnected('Root_Ctrl.ScaleXYZ', stretch_mult + '.input2X'):
                cmds.connectAttr('Root_Ctrl.ScaleXYZ', stretch_mult + '.input2X', f=1)
        if not cmds.isConnected(node_plug, stretch_mult + '.input1X'):
            cmds.connectAttr(node_plug, stretch_mult + '.input1X', f=1)
        if not cmds.getAttr(stretch_mult + '.operation') == 2:
            cmds.setAttr(stretch_mult + '.operation', 2)

    # create the scale factor
    joints_ls = cmds.ls('*_Bend?_Bnd_Jnt')
    for jnt in joints_ls:
        for scale_attr in ['sx', 'sz']:
            scale_factor_node = '{}_{}_ScaleFactor'.format(jnt, scale_attr)
            node = cmds.listConnections(jnt + '.' + scale_attr, s=1, d=0, plugs=1)
            if not node:
                continue
            node = node[0]
            if not cmds.objExists(scale_factor_node):
                cmds.createNode('multiplyDivide', name=scale_factor_node)
            if scale_factor_node not in node:
                if not cmds.isConnected(node, scale_factor_node + '.input2X'):
                    cmds.connectAttr(node, scale_factor_node + '.input2X', f=1)
                if not cmds.isConnected('Root_Ctrl.ScaleXYZ', scale_factor_node + '.input1X'):
                    cmds.connectAttr('Root_Ctrl.ScaleXYZ', scale_factor_node + '.input1X', f=1)
                if not cmds.getAttr(scale_factor_node + '.operation') == 2:
                    cmds.setAttr(scale_factor_node + '.operation', 2)
                if not cmds.isConnected(scale_factor_node + '.outputX', jnt + '.' + scale_attr):
                    cmds.connectAttr(scale_factor_node + '.outputX', jnt + '.' + scale_attr, f=1)

    return True


def old_way():
    """
    :description: Fix the quadruped leg scaling issues.
    :returns: <bool> True for success.
    """
    face_grp = 'Face_Ctrl_Grp'
    follow_drivers_grp = 'Follow_Drivers_Grp'
    eye_proxy_grp = 'EyeProxyPivot_Grp'
    l_backleg_grp = 'L_BackLeg_Ctrl_Grp'
    r_backleg_grp = 'R_BackLeg_Ctrl_Grp'
    l_frontleg_grp = 'L_FrontLeg_Ctrl_Grp'
    r_frontleg_grp = 'R_FrontLeg_Ctrl_Grp'
    ground_gimbal_name = 'Ground_Gimbal_Ctrl'
    rig_scale_offset_node = 'RigScaleOffset_MD'

    # re parent the leg ik utility nodes
    leg_utils = cmds.ls('?_*Leg_*Bend')
    for leg_u in leg_utils:
        if not cmds.listRelatives(leg_u, p=1)[0] == 'Utility_Grp':
            cmds.parent(leg_utils, 'Utility_Grp')

    # installs scale factors on the bendy joints.
    install_quadruped_scale_factors()

    if cmds.objExists(face_grp):
        if not check_scale_constraint(face_grp):
            cmds.scaleConstraint('C_Head_Gimbal_Ctrl', face_grp)

    if cmds.objExists(follow_drivers_grp):
        if not check_scale_constraint(follow_drivers_grp):
            cmds.scaleConstraint('Root_Ctrl', follow_drivers_grp)

    if cmds.objExists(eye_proxy_grp):
        if not check_scale_constraint(eye_proxy_grp):
            cmds.scaleConstraint('C_Head_Gimbal_Ctrl', eye_proxy_grp)

    for leg in [l_backleg_grp, r_backleg_grp, l_frontleg_grp, r_frontleg_grp]:
        if cmds.objExists(leg):
            if not check_scale_constraint(leg):
                cmds.scaleConstraint('Ground_Gimbal_Ctrl', leg)
            if not check_parent_constraint(leg):
                cmds.parentConstraint('Ground_Gimbal_Ctrl', leg)

    # constrain the leg setup groups
    bendy_setup_grps = cmds.ls('?_Leg_Bend_Setup_Grp')
    for bend_grp in bendy_setup_grps:
        if not check_parent_constraint(bend_grp):
            cmds.parentConstraint(ground_gimbal_name, bend_grp, mo=1)
        if not check_scale_constraint(bend_grp):
            for scl in ['x', 'y', 'z']:
                out_attr = '{}.output{}'.format(rig_scale_offset_node, scl.capitalize())
                in_attr = '{}.s{}'.format(bend_grp, scl)
                if not cmds.isConnected(out_attr, in_attr):
                    cmds.connectAttr(out_attr, in_attr)

    # constrain the arm setup groups
    arm_joints = cmds.ls('?_Arm_Shoulder_Bend_Parent_Jnt') + cmds.ls('?_Arm_Elbow_Bend_Parent_Jnt')
    for arm_jnt in arm_joints:
        grp_name = arm_jnt + '_Offset_Grp'
        grp_scale_offset_name = arm_jnt + '_Scale_Offset_Grp'
        if not cmds.objExists(grp_scale_offset_name):
            cmds.createNode('transform', name=grp_scale_offset_name)
        for scl in ['x', 'y', 'z']:
            out_attr = '{}.output{}'.format(rig_scale_offset_node, scl.capitalize())
            in_attr = '{}.s{}'.format(grp_scale_offset_name, scl)
            if not cmds.isConnected(out_attr, in_attr):
                cmds.connectAttr(out_attr, in_attr)
        if not cmds.objExists(grp_name):
            parent_node = cmds.listRelatives(arm_jnt, p=1)[0]
            cmds.createNode('transform', name=grp_name)
            cmds.parent(grp_name, parent_node)
            cmds.parent(grp_scale_offset_name, grp_name)
            cmds.parent(arm_jnt, grp_scale_offset_name)
        if not check_parent_constraint(grp_name):
            cmds.parentConstraint(ground_gimbal_name, grp_name, mo=1)
    return True
