# define private variables
__version__ = '1.0.0'
__author__ = 'Alexei Gaidachev'
__vendor__ = 'ICON'
__notes__ = 'As per directions of Andrew Poon, this is the ball rig template we should use for all the ball rigs.'

# define standard modules
import time

# define maya modules
from maya import cmds

# define custom modules
from rig_tools.utils import deformers
import icon_api.control as i_control
import icon_api.utils as i_utils

# define global variables
attributes = ['.t', '.r', '.s', '.tx', '.ty', '.tz','.rx', '.ry', '.rz', '.sx', '.sy', '.sz']


def util_attributes(transform_name="", lock=True):
    """
    Lock and unlock attributes.
    :param transform_name: <str> transform object name.
    :param lock: <bool> Lock and Unlock the attributes.
    :return: <bool> True for success.
    """
    for a in attributes:
        cmds.setAttr(transform_name + a, l=lock, k=not lock)
    return True


def find_deformers(x):
    """
    Fi1nds all possible deformer types.
    :param x: deformer shape node.
    :return: <str> x, deformer shape node.
    """
    if x:
        if cmds.objectType(x) in ['cluster', 'skinCluster', 'lattice',
                                  'softMod', 'deltaMush', 'ffd', 'tweak', 'wire', 'nonLinear']:
            return x
    return None


def util_find_deformers(geo_name=""):
    """
    Finds body geo attached deformers.
    :param geo_name: <str> geometry name to find deformers in.
    :return: <list> list of deformers.
    """
    # finds all the deformers on the selected body mesh object
    deformers = lambda x: filter(None, map(find_deformers, cmds.listHistory(x[-1], pruneDagObjects=1)))
    deformer_names_ls = deformers([geo_name]) or []
    deformer_names_ls.insert(len(deformer_names_ls), geo_name)
    return deformer_names_ls


def util_reorder_ball_deformers(geo_name=""):
    """
    Reorders the ball deformer rig by placing the cluster deformer before the lattice.
    :return: <bool> True for success.
    """
    deform_list = util_find_deformers(geo_name=geo_name)
    deform_list = [x for x in deform_list if not 'Squash' in x]
    # make sure the cluster is first before the lattice
    new_list = []
    for d_item in deform_list:
        if cmds.objectType(d_item) == 'cluster':
            cls_index = deform_list.index(d_item)
            cls_deformer = d_item
        if cmds.objectType(d_item) == 'ffd':
            ffd_index = deform_list.index(d_item)
            ffd_deformer = d_item
    if ffd_index > cls_index:
        deform_list.pop(ffd_index)
        deform_list.insert(0, ffd_deformer)
    cmds.reorderDeformers(*deform_list)
    return True


def delete_rig(rig_name='Snowball'):
    """
    Deletes the currently created rig.
    :param rig_name: <str> rig name to use when deleting the system.
    :return: <bool> True for success.
    """

    return True


def get_bounding_box_center(object_name=''):
    """
    Grabs the center of bounding box
    :param object_name:
    :return:
    """
    bbox_min = cmds.getAttr(object_name + '.boundingBoxMin')[0]
    bbox_max = cmds.getAttr(object_name + '.boundingBoxMax')[0]
    center_x = (bbox_min[0] + bbox_max[0])/2.0
    center_y = (bbox_min[1] + bbox_max[1])/2.0
    center_z = (bbox_min[2] + bbox_max[2])/2.0
    return [center_x, center_y, center_z]


def get_bounding_box_min_max_y(object_name=''):
    """
    Grabs the center of bounding box
    :param object_name:
    :return:
    """
    bbox_min = cmds.getAttr(object_name + '.boundingBoxMin')[0]
    bbox_max = cmds.getAttr(object_name + '.boundingBoxMax')[0]
    return [bbox_min[1], bbox_max[1]]


def install_ball_rig():
    """
    Installs the ball rig with the box input.
    :return: <bool> True for success.
    """
    result = cmds.promptDialog(
        title='Build Ball Rig Template',
        message='Enter Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')
    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)
        do_it(text)
    return 1


def check_name(rig_name=''):
    """
    Check if the name is already in use in the scene.
    :param rig_name: <str> name to check.
    :return: <bool> True the name exists. <False> False, the name is not in use.
    """
    # rig names
    rig_names = ['{}_Box_TopRingSquishy_Ctrl', '{}_Box_BotRingSquishy_Ctrl', '{}_Box_COG_Ctrl_Offset_Grp',
                 '{}_Box_Lat', '{}_Box_Grp', '{}_Top_Squash', '{}_Btm_Squash',
                 '{}_Geo_Ctrl_Offset_Grp', '{}_Box_COG_Ctrl', '{}_BoxMover_ClsHandle']
    name_checks = []
    for name in rig_names:
        name_checks.append(cmds.objExists(name.format(rig_name)))
    return any(name_checks)


def do_it(rig_name='Snowball'):
    """
    Creates a ball rig template from a selection by using the current box deformer rig.
    :param rig_name: <str> the name of the ball rig to build.
    :return: <bool> True for success.
    """
    # define global variables
    sel_object = i_utils.check_sel()
    check_confirm = check_name(rig_name)
    if check_confirm:
        cmds.warning('[Ball Rig] :: Name is already in use: {}'.format(rig_name))
        return False

    st = time.time()

    if not sel_object:
        cmds.confirmDialog(title="Nothing Selected", message='Please select a spherical geometry.')
        raise RuntimeError("[Ball Rig] :: No Geometry is selected.")

    # Find bounding box information of lattice created. This will be outer boundary of the objects as a group
    sel_name = sel_object[0].name
    bbox_min = cmds.getAttr(sel_name + '.boundingBoxMin')[0]
    bbox_max = cmds.getAttr(sel_name + '.boundingBoxMax')[0]
    control_size = bbox_max[1] - bbox_min[1]
    joint_name = rig_name + '_00_Bnd_Jnt'

    # create the existing box rig
    deformers.create_box_lattice(name=rig_name, objects=sel_object)

    # reoder the deformers for every geometry object selected
    for geo_name in sel_object:
        util_reorder_ball_deformers(geo_name.name)

    # create more controls
    top_box_ctrl = rig_name + '_Box_TopRingSquishy_Ctrl'
    btm_box_ctrl = rig_name + '_Box_BotRingSquishy_Ctrl'
    cog_box_offset_grp = rig_name + '_Box_COG_Ctrl_Offset_Grp'
    lattice_box = rig_name + '_Box_Lat'
    lattice_box_base = lattice_box + 'Base'
    lattice_name = rig_name + '_Lattice'
    ball_cog_grp = rig_name + '_Box_Grp'
    top_squash_name = rig_name + '_Top_Squash'
    btm_squash_name = rig_name + '_Btm_Squash'
    geo_offset_grp = rig_name + '_Geo_Ctrl_Offset_Grp'
    box_cog_ctrl = rig_name + '_Box_COG_Ctrl'
    box_mover_cls = rig_name + '_BoxMover_ClsHandle'

    # define controller parameters
    squash_top_ctrl = i_control.Control(
        control=rig_name + '_Squash_Top_Ctrl')

    squash_bot_ctrl = i_control.Control(
        control=rig_name + '_Squash_Bot_Ctrl')

    cog_ctrl = i_control.Control(
        control=rig_name + '_COG_Ctrl')

    ball_ctrl = i_control.Control(
        control=rig_name + '_Geo_Ctrl')

    # create the controllers
    top_node = squash_top_ctrl.create(
        name=rig_name + '_Squash_Top_Ctrl',
        control_type='2D Panel Circle',
        color="darkGreen",
        lock_hide_attrs=['tx', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
        size=control_size * 0.25)

    bot_node = squash_bot_ctrl.create(
        name=rig_name + '_Squash_Bot_Ctrl',
        control_type='2D Panel Circle',
        color="darkGreen",
        lock_hide_attrs=['tx', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
        size=control_size * 0.25)

    cog_node = cog_ctrl.create(
        name=rig_name + '_COG_Ctrl',
        control_type='2D Arrow 4Way',
        color="yellow",
        size=control_size * 0.95)

    ball_node = ball_ctrl.create(
        name=rig_name + '_Geo_Ctrl',
        control_type='3D Sphere',
        color="pink",
        lock_hide_attrs = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'],
        size=control_size * 1.10)

    # create and position the squash deformers
    selected_objects = [x.name for x in sel_object]
    bot_squash, bot_squash_handle = cmds.nonLinear(selected_objects,
                                                   type='squash', name=btm_squash_name, lowBound=-2, highBound=0)
    top_squash, top_squash_handle = cmds.nonLinear(selected_objects,
                                                   type='squash', name=top_squash_name, lowBound=0, highBound=2)

    # query positions
    bot_translate = cmds.xform(btm_box_ctrl, ws=1, t=1, q=1)
    top_translate = cmds.xform(top_box_ctrl, ws=1, t=1, q=1)
    center_of_geometry = cmds.xform(lattice_box, ws=1, t=1, q=1)

    # position the controllers
    cmds.xform(top_squash_handle, ws=1, t=bot_translate)
    cmds.xform(bot_squash_handle, ws=1, t=top_translate)
    cmds.xform(squash_top_ctrl.top_tfm.name, ws=1, t=top_translate)
    cmds.xform(squash_bot_ctrl.top_tfm.name, ws=1, t=bot_translate)
    cmds.xform(cog_ctrl.top_tfm.name, ws=1, t=center_of_geometry)
    cmds.xform(ball_ctrl.top_tfm.name, ws=1, t=center_of_geometry)

    # rotate the bottom controller for squash
    cmds.xform(squash_bot_ctrl.top_tfm.name, ro=(0.0, 0.0, -180.0), relative=1, euler=1)

    # calculate the translation factor to feed into the squash factor
    min_max_y = get_bounding_box_min_max_y(sel_name)
    translation_factor = abs(min_max_y[0]) + min_max_y[1]

    # top squash translation factor
    top_mult = cmds.createNode('multiplyDivide', name='Top_Squash_Translation_Factor')
    cmds.setAttr(top_mult + '.operation', 2)
    cmds.setAttr(top_mult + '.input2X', translation_factor)
    cmds.connectAttr(squash_top_ctrl.control.name + '.translateY', top_mult + '.input1X')
    cmds.connectAttr(top_mult + '.outputX', top_squash + '.factor')

    # bottom squash translation factor
    btm_mult = cmds.createNode('multiplyDivide', name='Btm_Squash_Translation_Factor')
    cmds.setAttr(btm_mult + '.operation', 2)
    cmds.setAttr(btm_mult + '.input2X', translation_factor)
    cmds.connectAttr(squash_bot_ctrl.control.name + '.translateY', btm_mult + '.input1X')
    cmds.connectAttr(btm_mult + '.outputX', bot_squash + '.factor')

    # create a joint and bind the geometry to this joint
    # cmds.joint(name=joint_name, position=center_of_geometry, absolute=True)
    # cmds.skinCluster(joint_name, sel_name)

    # constraint the joint to the sphere controller
    # cmds.orientConstraint(ball_ctrl.control.name, joint_name, mo=0)

    # parent the ball_geo_ctrl to the COG ctrl
    cmds.parent(ball_ctrl.offset_grp.name, box_cog_ctrl)
    cmds.parent(squash_top_ctrl.offset_grp.name, cog_ctrl.gimbal.name)
    cmds.parent(squash_bot_ctrl.offset_grp.name, cog_ctrl.gimbal.name)
    cmds.parent(cog_box_offset_grp, cog_ctrl.gimbal.name)

    # # constrain the joint
    # cmds.pointConstraint(cog_ctrl.gimbal.name, joint_name, mo=0)
    # cmds.scaleConstraint(cog_ctrl.gimbal.name, joint_name, mo=0)

    # add a switch to toggle the box cog
    attr_name = 'Box_COG_Ctrl_Vis'
    attr_full_name = cog_ctrl.control.name + '.' + attr_name
    cmds.addAttr(cog_ctrl.control.name, ln=attr_name, at='enum', en="Off:On")
    cmds.setAttr(attr_full_name, cb=1)
    cmds.setAttr(attr_full_name, k=1)
    cmds.connectAttr(attr_full_name, cog_box_offset_grp.replace('_Offset_Grp', 'Shape') + '.v')

    # reconnect the box_mover_cls
    cmds.delete(list(set(cmds.listConnections(box_mover_cls, s=1, d=0, type='parentConstraint'))))
    cmds.delete(list(set(cmds.listConnections(box_mover_cls, s=1, d=0, type='scaleConstraint'))))
    cmds.parentConstraint(ball_ctrl.gimbal.name, box_mover_cls, mo=1)
    cmds.scaleConstraint(ball_ctrl.gimbal.name, box_mover_cls, mo=1)

    # group the squash and the joint to this group
    util_grp_name = rig_name + '_Util_Grp'
    cmds.group(name=util_grp_name, em=1)
    try:
        cmds.parent([ball_cog_grp, util_grp_name])
    except ValueError:
        pass
    cmds.parent(util_grp_name, 'Utility_Grp')

    squash_grp_name = rig_name + 'Squash_Handles_Util_Grp'
    cmds.group(name=squash_grp_name, em=1)
    cmds.parentConstraint(cog_ctrl.gimbal.name, squash_grp_name, mo=0)
    cmds.scaleConstraint(cog_ctrl.gimbal.name, squash_grp_name, mo=0)
    cmds.parent([top_squash_handle, bot_squash_handle, squash_grp_name])
    cmds.parent(squash_grp_name, util_grp_name)

    # rename the squash transforms
    cmds.rename(top_squash, top_squash_name)
    cmds.rename(bot_squash, btm_squash_name)
    cmds.rename(top_squash_handle, top_squash_name + '_Handle')
    cmds.rename(bot_squash_handle, btm_squash_name + '_Handle')

    # finalzie the design
    cmds.setAttr(squash_top_ctrl.control.name + '.GimbalVis', 0)
    cmds.setAttr(squash_bot_ctrl.control.name + '.GimbalVis', 0)
    cmds.setAttr(cog_ctrl.control.name + '.GimbalVis', 0)

    # constrain the ffd lattice shapes
    # ffd Transform
    util_attributes(lattice_box, lock=False)
    cmds.parentConstraint(box_cog_ctrl, lattice_box, mo=1)
    cmds.scaleConstraint(box_cog_ctrl, lattice_box, mo=1)
    util_attributes(lattice_box, lock=True)

    # ffd Base
    util_attributes(lattice_box_base, lock=False)
    cmds.parentConstraint(box_cog_ctrl, lattice_box_base, mo=1)
    cmds.scaleConstraint(box_cog_ctrl, lattice_box_base, mo=1)
    util_attributes(lattice_box_base, lock=True)

    # set lattice deformer attributes to falloff
    cmds.setAttr("{}.outsideLattice".format(lattice_name), 2)

    en = time.time()
    print("[Ball Rig] :: took {} seconds.".format(round(en - st, 3)))
    return True