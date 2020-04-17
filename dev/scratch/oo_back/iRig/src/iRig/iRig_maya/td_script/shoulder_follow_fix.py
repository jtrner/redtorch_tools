# import maya modules
from maya import cmds

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Michael Taylor"]
__license__ = "IL"
__version__ = "1.0.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def check_parent_constraint(node_name=''):
    """
    :@param node_name: <str> check this node for parent constraint.
    """
    parent_cns = cmds.listConnections(node_name + '.tx', s=1, d=0, type='parentConstraint')
    return bool(parent_cns)


def check_orient_constraint(node_name=''):
    """
    :@param node_name: <str> check this node for parent constraint.
    """
    orient_cns = cmds.listConnections(node_name + '.rx', s=1, d=0, type='orientConstraint')
    return bool(orient_cns)


def check_scale_constraint(node_name=''):
    """
    :@param node_name: <str> check this node for parent constraint.
    """
    orient_cns = cmds.listConnections(node_name + '.sx', s=1, d=0, type='orientConstraint')
    return bool(orient_cns)


def check_attribute(node_name="", attr=""):
    """
    :@param node_name: <str> check this node for an attriubute.
    """
    return cmds.objExists(node_name + '.' + attr)


def insert_transform(node_name="", tfm_xform=""):
    """
    :@param node_name: <str> create a new node with this name.
    :@param tfm_xform: <str> use this space for the new node creation.
    :returns: <str> name of the new node.
    """
    m_xform = cmds.xform(tfm_xform, ws=1, m=1, q=1)
    cmds.createNode('transform', name=node_name)
    cmds.xform(node_name, m=m_xform, ws=1)
    par_node = cmds.listRelatives(tfm_xform, p=1, type='transform')[0]
    cmds.parent(node_name, par_node)
    cmds.parent(tfm_xform, node_name)
    return node_name


def old_way():
    """
    :description: Installs shoulder follow attribute.
    :returns: <bool> True for success.
    """
    front_hip_ctrl = '{}_*Hip_Ctrl'
    front_hip_ctrl_follow_Grp = '{}_*Hip_Ctrl_Follow_Grp'
    root_gimbal_follow_tfm = 'Root_Gimbal_Ctrl_Follow_Driver_Orient_Tfm'
    ground_gimbal_follow_tfm = 'Ground_Gimbal_Ctrl_Follow_Driver_Orient_Tfm'
    spine_chest_follow_tfm = 'C_Spine_Chest_Gimbal_Ctrl_Follow_Driver_Orient_Tfm'

    # constrain the origin groups
    auto_aim_grps = cmds.ls('*_AutoAim_Origin_Grp')
    for grp in auto_aim_grps:
        if not check_parent_constraint(grp):
            cmds.parentConstraint('Ground_Gimbal_Ctrl', grp, mo=1)
        if not check_scale_constraint(grp):
            cmds.parentConstraint('Ground_Gimbal_Ctrl', grp, mo=1)

    for side in 'LR':
        hip_ctrls = cmds.ls(front_hip_ctrl.format(side))
        for hip_ctrl in hip_ctrls:
            hip_follow_attr = hip_ctrl + '.Follow'

            follow_grp = hip_ctrl + '_Follow_Grp'
            follow_chest_cnd = hip_ctrl + '_Follow_Chest_Cnd'
            follow_ground_cnd = hip_ctrl + '_Follow_Ground_Cnd'
            follow_root_cnd = hip_ctrl + '_Follow_Root_Cnd'

            if not check_attribute(hip_ctrl, 'Follow'):
                cmds.addAttr(hip_ctrl, ln='Follow', at='enum', enumName="Chest:Ground:Root", k=1)

            if not cmds.objExists(root_gimbal_follow_tfm):
                cmds.createNode('transform', name=root_gimbal_follow_tfm)

            if not cmds.objExists(ground_gimbal_follow_tfm):
                cmds.createNode('transform', name=ground_gimbal_follow_tfm)

            if not cmds.objExists(spine_chest_follow_tfm):
                cmds.createNode('transform', name=spine_chest_follow_tfm)

            if not check_parent_constraint(root_gimbal_follow_tfm):
                cmds.parentConstraint('Root_Gimbal_Ctrl', root_gimbal_follow_tfm)

            if not check_parent_constraint(ground_gimbal_follow_tfm):
                cmds.parentConstraint('Ground_Gimbal_Ctrl', ground_gimbal_follow_tfm)

            if not check_parent_constraint(spine_chest_follow_tfm):
                cmds.parentConstraint('Ground_Gimbal_Ctrl', spine_chest_follow_tfm)

            # create the follow grp
            if not cmds.objExists(follow_grp):
                insert_transform(node_name=follow_grp, tfm_xform=hip_ctrl)

            if not check_orient_constraint(follow_grp):
                cnst_node = cmds.orientConstraint(spine_chest_follow_tfm, ground_gimbal_follow_tfm, root_gimbal_follow_tfm, follow_grp, mo=1)[0]

            if not cmds.objExists(follow_chest_cnd):
                cmds.createNode('condition', name=follow_chest_cnd)
                cmds.setAttr(follow_chest_cnd + '.secondTerm', 0)
                cmds.setAttr(follow_chest_cnd + '.colorIfTrueR', 1)
                cmds.setAttr(follow_chest_cnd + '.colorIfFalseR', 0)

            if not cmds.isConnected(hip_follow_attr, follow_chest_cnd + '.firstTerm'):
                cmds.connectAttr(hip_follow_attr, follow_chest_cnd + '.firstTerm', f=1)

            if not cmds.isConnected(follow_chest_cnd + '.outColorR', '{}.C_Spine_Chest_Gimbal_Ctrl_Follow_Driver_Orient_TfmW0'.format(cnst_node)):
                cmds.connectAttr(follow_chest_cnd + '.outColorR', '{}.C_Spine_Chest_Gimbal_Ctrl_Follow_Driver_Orient_TfmW0'.format(cnst_node), f=1)

            if not cmds.objExists(follow_ground_cnd):
                cmds.createNode('condition', name=follow_ground_cnd)
                cmds.setAttr(follow_ground_cnd + '.secondTerm', 1)
                cmds.setAttr(follow_ground_cnd + '.colorIfTrueR', 1)
                cmds.setAttr(follow_ground_cnd + '.colorIfFalseR', 0)

            if not cmds.isConnected(hip_follow_attr, follow_ground_cnd + '.firstTerm'):
                cmds.connectAttr(hip_follow_attr, follow_ground_cnd + '.firstTerm', f=1)

            if not cmds.isConnected(follow_ground_cnd + '.outColorR', '{}.Ground_Gimbal_Ctrl_Follow_Driver_Orient_TfmW1'.format(cnst_node)):
                cmds.connectAttr(follow_ground_cnd + '.outColorR', '{}.Ground_Gimbal_Ctrl_Follow_Driver_Orient_TfmW1'.format(cnst_node), f=1)

            if not cmds.objExists(follow_root_cnd):
                cmds.createNode('condition', name=follow_root_cnd)
                cmds.setAttr(follow_root_cnd + '.secondTerm', 2)
                cmds.setAttr(follow_root_cnd + '.colorIfTrueR', 1)
                cmds.setAttr(follow_root_cnd + '.colorIfFalseR', 0)

            if not cmds.isConnected(hip_follow_attr, follow_root_cnd + '.firstTerm'):
                cmds.connectAttr(hip_follow_attr, follow_root_cnd + '.firstTerm', f=1)

            if not cmds.isConnected(follow_root_cnd + '.outColorR', '{}.Root_Gimbal_Ctrl_Follow_Driver_Orient_TfmW2'.format(cnst_node)):
                cmds.connectAttr(follow_root_cnd + '.outColorR', '{}.Root_Gimbal_Ctrl_Follow_Driver_Orient_TfmW2'.format(cnst_node), f=1)
    return True


def do_it():
    """
    Fixes the issue with the pole vectors
    :return: <bool> True for success.
    """
    ground_grp = 'Follow_Driver_Ground_Grp'
    if not cmds.objExists(ground_grp):
        return False
    if not cmds.objExists('RigScaleOffset_MD'):
        scale_ctrl = 'Ground_Gimbal_Ctrl'
        if not check_scale_constraint(ground_grp):
            cmds.scaleConstraint(scale_ctrl, ground_grp, mo=1)
    else:
        scale_ctrl = 'RigScaleOffset_MD'
        for scale_attr in ['.sx', '.sy', '.sz']:
            output_attr = scale_ctrl + '.outputX'
            input_attr = ground_grp + scale_attr
            if not cmds.isConnected(output_attr, input_attr):
                cmds.connectAttr(output_attr, input_attr, f=1)
        if not check_parent_constraint(ground_grp):
            cmds.parentConstraint(scale_ctrl, ground_grp, mo=1)
    return True
