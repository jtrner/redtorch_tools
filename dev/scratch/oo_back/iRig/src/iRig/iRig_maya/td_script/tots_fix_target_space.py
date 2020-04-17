"""Fixes the target space targets for various controllers"""

# standard maya imports
from maya import cmds

# define custom imports
import rig_tools.utils.controls as rig_controls
import icon_api.node as i_node
import rig_tools.utils.attributes as rig_attributes
import icon_api.control as i_control


# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Michael Taylor", "Alison Chan"]
__license__ = "ICON License"
__version__ = "2.0.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


# exceptions to apply orientConstraint spaces instead.
BIPED_ORIENTS = ["Hip", "Hip_Fk", "Clavicle", "Arm_Shoulder", "Head", "Neck_End"]
QUADRUPED_ORIENTS = ["Back_Hip", "Front_Hip", "Front_Hip_Fk", "Back_Hip_Fk", "Head", "Neck_End"]
# have a mixture of Parent and Point/ Orient objects for the pole vectors control

# Creates the two Translate and Rotate orientation transforms constraint systems
# TR_EXCEPTIONS = ["Leg_PoleVector", "Arm_PoleVector", "FrontLeg_PoleVector", "BackLeg_PoleVector"]
TR_EXCEPTIONS = []
POINT_ONLY = ["Arm_PoleVector"]

# constrain only the orient Y axis
POLE_VECTOR_ORIENTS = ["Leg_PoleVector", "FrontLeg_PoleVector", "BackLeg_PoleVector"]

# space data, parentConstraint is the default
# targets transforms are listed first, then the driven controller last
BIPED_DATA = {
    'Arm_Wrist': ['C_Spine_Chest_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl', '{}_Arm_Wrist_Ik_Ctrl'],
    'Arm_PoleVector': ['{}_Arm_Wrist_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Arm_PoleVector_Ctrl'],
    'Leg_PoleVector': ['{}_Leg_Ankle_Ik_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Leg_PoleVector_Ctrl'],
    'Foot': ['{}_Hip_Ctrl', '{}_BackHip_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Leg_Ankle_Ik_Ctrl'],
    'Head': ['C_Neck_02_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl'],
    'Hip': ['C_Spine_Hips_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Hip_Ctrl', '{}_BackHip_Ctrl'],
    'Hip_Fk': ['{}_Hip_Ctrl', '{}_BackHip_Ctrl', 'C_Spine_Hips_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Leg_Hip_Fk_Ctrl'],

    'Neck_End': ['Ground_Ctrl', 'Root_Ctrl', 'C_Neck_End_Ctrl'],
    'Clavicle': ['C_Spine_Chest_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_Clavicle_Ctrl'],
    'Arm_Shoulder': ['{}_Clavicle_Ctrl', 'COG_Ctrl',  'Ground_Ctrl', 'Root_Ctrl', '{}_Arm_Shoulder_Fk_Ctrl']
}

QUADRUPED_DATA = {
    'FrontLeg_PoleVector': ['{}_FrontLeg_Ankle_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl',
                            '{}_FrontLeg_PoleVector_Ctrl'],
    'BackLeg_PoleVector': ['{}_BackLeg_Foot_Ik_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl',
                           '{}_BackLeg_PoleVector_Ctrl'],

    'Front_Foot': ['{}_FrontHip_Ctrl', 'C_Spine_Chest_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_FrontLeg_Ankle_Ik_Ctrl'],
    'Back_Foot': ['{}_BackHip_Ctrl', 'C_Spine_Hips_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_BackLeg_Foot_Ik_Ctrl'],

    'Head': ['C_Neck_02_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', 'C_Head_Ctrl'],
    'Neck_End': ['Ground_Ctrl', 'Root_Ctrl', 'C_Neck_End_Ctrl'],

    'BackFoot_Ankle_Fk':  ['{}_BackLeg_Knee_Fk_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_BackFoot_Ankle_Fk_Ctrl'],
    'FrontFoot_Ankle_Fk':  ['{}_FrontLeg_Knee_Fk_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_FrontLeg_Ankle_Ik_Ctrl'],

    'Back_Hip': ['C_Spine_Hips_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_BackHip_Ctrl'],
    'Front_Hip': ['C_Spine_Chest_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_FrontHip_Ctrl'],
    'Front_Hip_Fk': ['{}_FrontHip_Ctrl', 'COG_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_FrontLeg_Hip_Fk_Ctrl'],
    'Back_Hip_Fk': ['{}_BackHip_Ctrl', 'C_Spine_Hips_Ctrl', 'Ground_Ctrl', 'Root_Ctrl', '{}_BackLeg_Hip_Fk_Ctrl'],
}


# combine information
TARGETS_DATA = BIPED_DATA.copy()
TARGETS_DATA.update(QUADRUPED_DATA)
ORIENTS_DATA = BIPED_ORIENTS + QUADRUPED_ORIENTS


def util_delete_attribute(ctl_attr_name=""):
    """
    Delete the attribute if it exists.
    :param ctl_attr_name: <str> control attribute name.
    :return: <bool> True for success. <bool> False for failure.
    """
    if cmds.objExists(ctl_attr_name):
        cmds.deleteAttr(ctl_attr_name)
    else:
        return False
    return True


def util_get_transform(geo=''):
    """
    Grabs transform object
    :param geo: <str> the mesh object to find transform.
    :returns: <list> Mesh Transform object. <list> Empty list for failure.
    """
    if not geo:
        return []
    return [cmds.listRelatives(m, p=1, type='transform')[0] for m in geo]


def util_snap_space(source, target):
    """
    using the same position snap the source to the target.
    """
    return cmds.xform(source, m=cmds.xform(target, ws=1, m=1, q=1))


def util_insert_transform(object_name="", parent_to="parent", rename_object="", constraints=None):
    """
    Inserts a transform for the selected object.
    :param replace_suffix: <str> replace the string with this name.
    :param object_name: <str> insert the parent transform on top of this object.
    :param parent_to: <str> parents to the "object" or "parent".
    :param rename_object: <str> use this name for the new transform object.
    :param constraints:  <tuple>, <str> 'point', 'orient', 'scale', 'parent', ('point', 'orient') for multi constraints.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not object_name:
        return False
    if not rename_object:
        return False
    par_obj_name = cmds.listRelatives(object_name, p=1)
    if not par_obj_name:
        return False
    if cmds.objExists(rename_object):
        cmds.error("[Insert Transform] :: Object already exists! {}".format(rename_object))
        return False
    cmds.createNode('transform', name=rename_object)
    util_snap_space(rename_object, object_name)
    if parent_to == 'parent':
        cmds.parent(rename_object, par_obj_name)
        cmds.parent(object_name, rename_object)
    elif parent_to == 'object':
        cmds.parent(rename_object, object_name)
    elif parent_to == 'world':
        cmds.parent(rename_object, 'Follow_Drivers_Grp')
    else:
        cmds.parent(rename_object, object_name)
    if constraints:
        if 'point' in constraints:
            cmds.pointConstraint(object_name, rename_object, mo=1)
        if 'orient' in constraints:
            cmds.orientConstraint(object_name, rename_object, mo=1)
        if 'parent' in constraints:
            cmds.parentConstraint(object_name, rename_object, mo=1)
        if 'scale' in constraints:
            cmds.scaleConstraint(object_name, rename_object, mo=1)
    return True


def util_identify_character():
    """
    Identifies whether the current character rig is bipedal or quadrupedal.
    :return: <str> 'biped'/ 'quadruped' name for success. <False> for failure.
    """
    # check biped controller existence
    biped_checks = []
    for b_key, b_data in BIPED_DATA.items():
        for side in 'LR':
            biped_checks.append(cmds.objExists(b_data[-1].format(side)))

    # check quadruped controller existence
    quadruped_checks = []
    for b_key, b_data in QUADRUPED_DATA.items():
        for side in 'LR':
            quadruped_checks.append(cmds.objExists(b_data[-1].format(side)))

    # return results
    if all(biped_checks):
        return 'biped'
    if all(quadruped_checks):
        return 'quadruped'
    return False


def install_targets(selected=[], cnst_type="parent", skip=[]):
    """
    Given a list of selected objects where the TARGETS and then the SOURCE is selected last.
    :param selected: <list> of transform objects.
    :param cnst_type: <str> constraint type: "parent", "orient", "point"
    :return: <dict> iNode data for success.
    """
    # please put the controls you want to add follows for, in the order they should appear:
    follow_sources = selected[:-1]
    target_ctrl_name = selected[-1]

    # make the mimic array:
    follow_mimics = []
    for ctrl in follow_sources:
        # look for gimbals
        gimbal_name = ctrl.replace("_Ctrl", "_Gimbal_Ctrl")
        if cmds.objExists(gimbal_name):
            follow_mimic = i_control.mimic_control_class(i_node.Node(gimbal_name))
            follow_mimics.append(follow_mimic.control)

        # add the controls if gimbal doesn't exist
        if not cmds.objExists(gimbal_name):
            follow_mimic = i_control.mimic_control_class(i_node.Node(ctrl))
            follow_mimics.append(follow_mimic.control)

    # indicates the control to add a follow switch to:
    target_ctrl = i_control.mimic_control_class(i_node.Node(target_ctrl_name))

    rig_attributes.create_follow_attr(control=target_ctrl.control, cns_type=cnst_type,
                                      options=follow_mimics, skip=skip)
    util_check_condition_nodes(target_ctrl_name)
    return True


def util_remove_constraints(object_name="", cnst_type='parentConstraint'):
    """
    Removes incorrect constraints.
    :param object_name: <str>
    :param cnst_type: <str>
    :return: <bool> True for success. <bool> False for failure.
    """
    constraint_types = ['parentConstraint', 'pointConstraint', 'orientConstraint']
    if cnst_type not in constraint_types:
        return False
    follow_grp = object_name + '_Follow_Grp'
    if not cmds.objExists(follow_grp):
        return False
    pair_blend_node = cmds.listConnections(follow_grp, s=1, d=0, type='pairBlend')
    if pair_blend_node:
        pair_blend_node = pair_blend_node[0]
        cnst_object = cmds.listConnections(pair_blend_node, s=1, d=0, type=cnst_type)
        if cnst_object:
            cmds.delete(cnst_object)
    else:
        cnst_object = cmds.listConnections(follow_grp, s=1, d=0, type=cnst_type)
        if cnst_object:
            cmds.delete(cnst_object)
    return True


def util_check_condition_nodes(object_name=""):
    """
    Checks if the condition nodes are all connected correctly
    :return: <bool> True for success.
    """
    constraints = ['parentConstraint', 'orientConstraint', 'pointConstraint']
    follow_grp = object_name + '_Follow_Grp'
    cnst_objects = cmds.listConnections(follow_grp, s=1, d=0)
    cnst_objects = list(set(cnst_objects))
    if cnst_objects:
        for cnst_obj in cnst_objects:
            if cmds.objectType(cnst_obj) not in constraints:
                continue
            condition_nodes = cmds.listConnections(cnst_obj, s=1, d=0, type='condition')
            for cnd_node in condition_nodes:
                # check the first term connnection
                in_attr = cnd_node + '.ft'
                out_attr = object_name + '.Follow'
                if not cmds.listConnections(in_attr):
                    cmds.connectAttr(out_attr, in_attr)
    return True


def install_target_biped_data(data_name=''):
    """
    Installs proper target data for the character rig.
    :return: <bool> True for success.
    """
    for d, selected in BIPED_DATA.items():
        if data_name:
            if data_name not in d:
                continue
        print("[Installing Biped Target Data] :: {}".format(d))

        # create exceptions
        cnst_type = 'parent'
        if d in BIPED_ORIENTS:
            cnst_type = 'orient'

        for side in 'LR':
            new_list = []
            for tr_object in selected:
                target_name = tr_object.format(side)
                if not cmds.objExists(target_name):
                    continue
                new_list.append(target_name)

            # remove useless constraints
            util_remove_constraints(target_name, cnst_type="pointConstraint")
            util_remove_constraints(target_name, cnst_type="orientConstraint")
            util_remove_constraints(target_name, cnst_type="parentConstraint")

            # install the follow constraint targets
            if d in TR_EXCEPTIONS:
                object_name = new_list[0]

                # special circumstance: create separate control for the pole vectors
                t_object = object_name.replace('_Ctrl', '_T')
                util_insert_transform(object_name, rename_object=t_object, parent_to='world', constraints=('point'))
                new_list[0] = t_object

                # create the r transform
                r_object = object_name.replace('_Ctrl', '_R')
                util_insert_transform(object_name, rename_object=r_object, parent_to='world', constraints=('parent'))
                new_list.insert(1, r_object)


                # constrain the pole vectors
                install_targets(new_list, cnst_type='parent')

                cmds.rename(t_object, t_object + '_Source_Follow_Driver_Point_Tfm')
                cmds.rename(r_object, r_object + '_Source_Follow_Driver_Parent_Tfm')

            else:
                install_targets(new_list, cnst_type=cnst_type)
    return True


def install_target_quadruped_data(data_name=''):
    """
    Installs proper target data for the character rig.
    :return: <bool> True for success.
    """
    for d, selected in QUADRUPED_DATA.items():
        if data_name:
            if data_name not in d:
                continue
        print("[Installing Quadruped Target Data] :: {}".format(d))

        # create exceptions
        cnst_type = 'parent'
        if d in QUADRUPED_ORIENTS:
            cnst_type = 'orient'

        for side in 'LR':
            new_list = []
            for tr_object in selected:
                target_name = tr_object.format(side)
                if not cmds.objExists(target_name):
                    continue
                new_list.append(target_name)

            # remove useless constraints
            util_remove_constraints(target_name, cnst_type="pointConstraint")
            util_remove_constraints(target_name, cnst_type="orientConstraint")

            # remove incorrect constraints
            if cnst_type == 'orient':
                util_remove_constraints(target_name, cnst_type="parentConstraint")
                util_remove_constraints(target_name, cnst_type="orientConstraint")

            # install the follow constraint targets
            install_targets(new_list, cnst_type=cnst_type)
    return True


def install_data(data_name=''):
    """
    Installs proper target data for the character rig.
    :return: <bool> True for success.
    """
    for d, selected in TARGETS_DATA.items():
        if data_name:
            if data_name not in d:
                continue
        print("[Installing Target Data] :: {}".format(d))

        for side in 'LR':
            new_list = []
            for tr_object in selected:
                target_name = tr_object.format(side)
                new_list.append(target_name)

            # cancel the procedure if control does not exist.
            if not all(map(cmds.objExists, new_list)):
                continue

            follow_ctrl_name = new_list[-1]
            # first remove the existing follow attribute
            util_delete_attribute(follow_ctrl_name + '.Follow')

            print("[Target Data Installation] :: {} -> {}".format(target_name, new_list))

            # remove useless constraints
            util_remove_constraints(target_name, cnst_type="pointConstraint")
            util_remove_constraints(target_name, cnst_type="orientConstraint")
            util_remove_constraints(target_name, cnst_type="parentConstraint")

            # create exceptions
            cnst_type = 'parent'
            if d in ORIENTS_DATA:
                cnst_type = 'orient'

            # install the follow constraint targets
            if d in TR_EXCEPTIONS:
                object_name = new_list[0]

                # special circumstance: create separate control for the pole vectors
                t_object = object_name.replace('_Ctrl', '_T')
                util_insert_transform(object_name, rename_object=t_object, parent_to='world', constraints=('point'))
                new_list[0] = t_object

                # create the r transform
                r_object = object_name.replace('_Ctrl', '_R')
                util_insert_transform(object_name, rename_object=r_object, parent_to='world', constraints=('parent'))
                new_list.insert(1, r_object)

                # install the follow constraint targets
                try:
                    install_targets(new_list, cnst_type='parent')
                except RuntimeError:
                    print("[Target Data Failure] :: {}".format(d))

                cmds.rename(t_object, t_object + '_Source_Follow_Driver_Point_Tfm')
                cmds.rename(r_object, r_object + '_Source_Follow_Driver_Parent_Tfm')

            elif d in POINT_ONLY:
                # install only the poinnt follow constraint targets
                try:
                    install_targets(new_list, cnst_type='point')
                except RuntimeError:
                    print("[Point Target Data Failure] :: {}".format(d))

            elif d in POLE_VECTOR_ORIENTS:
                # install the point and orient follow constraint targets
                try:
                    install_targets(new_list, cnst_type='point')
                    install_targets(new_list, cnst_type='orient', skip=["x", "z"])
                except RuntimeError:
                    print("[Pole Vector Target Data Failure] :: {}".format(d))

            else:
                # install only the follow parent constraint targets
                try:
                    install_targets(new_list, cnst_type=cnst_type)
                except RuntimeError:
                    print("[Parent Target Data Failure] :: {}".format(d))

    return True


def do_it():
    """
    Install Character target systems.
    :return: <bool> True for success. <bool> False for failure.
    """
    character_id = util_identify_character()
    if character_id:
        print('[Target Space] :: Character is a {}'.format(character_id))
    else:
        cmds.error('[Target Space Error] :: Could not identify character type.')
    if character_id == 'biped':
        install_target_biped_data()
    elif character_id == 'quadruped':
        install_target_quadruped_data()
    return False
