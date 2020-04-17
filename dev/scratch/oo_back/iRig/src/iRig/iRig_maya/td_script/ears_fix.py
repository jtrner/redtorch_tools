# define private variables
__author__ = "Alexei Gaidachev"
__vendor__ = "ICON"
__version__ = "1.0.0"

# define custom imports
import skin_tools
import skincluster_utils as skin_utl
import matrix_utils
from icon_api import control
from icon_api import node
from rig_tools import RIG_LOG

# import standard modules
#import time

# define maya modules
from maya import cmds


def util_get_body_geo():
    """
    Finds body geo name.
    :return: <str> Body geo name on success. <bool> False for failure.
    """
    body_geo_name = cmds.ls('*:Body_Geo')
    if not body_geo_name:
        RIG_LOG.error('[Ears Fix] :: Body_Geo does not exist in scene.')
        return False
    return body_geo_name[0]


def add_parent_transform(object_name=""):
    """
    Adds a new parent transform object above the object_name transform object.
    :param object_name: <str> objec tnmae.
    :return: <str> parent group transform name for success.
    """
    par_grp = object_name + 'Par_Grp'
    cmds.createNode('transform', name=par_grp)
    m_xform = cmds.xform(par_grp, m=1, ws=1, q=1)
    cmds.xform(par_grp, m=m_xform, ws=1)

    parent_object_name = cmds.listRelatives(object_name, p=1)[0]
    cmds.parent(par_grp, parent_object_name)
    cmds.parent(object_name, par_grp)
    return par_grp


def remove_constraint(right_ear_ctrl_offset=""):
    """
    Removes constraints acting on this transform node.
    :return: <dict> {<str> constraint_name: <str> node_name}
    """
    # remove the constraint
    cnst_dict = {}  
    cnst_list = cmds.listConnections(right_ear_ctrl_offset, s=1, d=0)
    if cnst_list:
        constraints = list(set(cnst_list))
        if constraints:
            for cnst in constraints:
                parent_obj = list(set(cmds.listConnections('{}.target[0].targetParentMatrix'.format(cnst), d=0, s=1)))[0]
                cnst_dict.update({cnst: {'master': parent_obj, 'slave': right_ear_ctrl_offset}})
                cmds.delete(cnst)
    return cnst_dict


def apply_constraint(cnst_dict={}):
    """
    From a dictionary given, reconstruct the constraint process.
    :param cnst_dict: <dict> {<str> constraint_name: <str> node_name}
    :return: <bool> True for success.
    """
    for cnst_name, cnst_data in cnst_dict.items():
        master_obj = cnst_data['master']
        slave_obj = cnst_data['slave']
        if 'parentConstraint' in cnst_name:
            cmds.parentConstraint(master_obj, slave_obj, mo=1)
        if 'scaleConstraint' in cnst_name:
            cmds.scaleConstraint(master_obj, slave_obj, mo=1)
    return True


def find_deformers(x):
    """
    Fi1nds all possible deformer types.
    :param x: deformer shape node.
    :return: <str> x, deformer shape node.
    """
    if x:
        if cmds.objectType(x) in ['cluster', 'skinCluster', 'lattice',
                                  'softMod', 'deltaMush', 'tweak', 'wire', 'nonLinear']:
            return x
    return None


def find_ctrl_transform(x):
    """
    Finds the eligible controller transforms.
    :param x: _CtrlShape node.
    :return: <str> x, controller shape node.
    """
    if '_Tweak_' in x:
        return None
    return cmds.listRelatives(x, p=1)[0]


def mirror_tots_ear_transforms():
    """
    Mirror TOTS Ear transforms.
    :return: <bool> True for success. <bool> False for failure.
    """
    ear_joints = ['{}_Ear_01_Ctrl_Cns_Grp', '{}_Ear_01_Tweak_Offset_Jnt_Grp', '{}_Ear_02_Tweak_Offset_Jnt_Grp', '{}_Ear_03_Offset_Jnt_Grp']

    # mirror the TOTS ears
    for index, ear in enumerate(ear_joints):
        left_ear = ear.format('L')
        right_ear = ear.format('R')

        if not cmds.objExists(left_ear) or not cmds.objExists(right_ear):
            cmds.error("[Ear Mirror Error] :: Invalid Groups.")
            return False

        print(left_ear, '>>>', right_ear)

        if index == 1:
            # add a transform on top of the right ear controller.
            parent_group_name = add_parent_transform(right_ear)
            matrix_utils.mirror_x_axis(object_name=left_ear, mirror_object=parent_group_name)
            continue

        # compute the mirror matrix and apply to the target transfrom
        matrix_utils.mirror_x_axis(object_name=left_ear, mirror_object=right_ear)
    return True


def mirror_tots_ears(skin_reset=False):
    """
    Mirrors the TOTS ears. Because the ears are not parented under joints, but are inter-connected via groups.
    :return: <bool> True for success. <bool> False for failure.
    """

    # mirror
    status = mirror_tots_ear_transforms()
    if not status:
        cmds.error("[TOTS Ear Mirror Failure] :: Could not mirror transform.")
        return False

    if skin_reset:
        # grab the body geo name
        body_geo_name = util_get_body_geo()
        if body_geo_name:
            # procure the skin cluster node
            skin_name, skin_fn = skin_utl.get_skin_cluster_obj(body_geo_name)

            # save the skin cluster
            skin_tools.save_skin()

            # finds all the deformers on the selected body mesh object
            deformer_names_ls = util_find_deformers()

            time.sleep(0.5)

            # un-bind the skin-cluster
            cmds.skinCluster(skin_name, unbind=True, edit=True)

            # load the skinCluster
            skin_tools.load_skin(mfn_load=False, object_list=[body_geo_name])

            # rename the skin cluster to what it was before
            new_skin, new_skin_fn = skin_utl.get_skin_cluster_obj(body_geo_name)
            cmds.rename(new_skin, skin_name)

            # reorder the deformers
            cmds.reorderDeformers(*deformer_names_ls)
    return True


def mirror_selected_controller():
    """
    Mirrors the ear based on the selection of the left year.
    :return: <bool> True if successful, <bool> False if failure.
    """
    # select a controller to mirror with.
    selection = cmds.ls(sl=1)
    if not selection:
        RIG_LOG.error('[Ears Fix] :: There is nothing selected.')
        return False

    # isolate the selection by the first list index
    selection = selection[0]

    # determine if the current selection is a controller transform
    if not selection.endswith('_Ctrl'):
        RIG_LOG.error('[Ears Fix] :: The selected transform is not a controller.')
        return False

    if 'L' not in selection and 'R' not in selection:
        RIG_LOG.error('[Ears Fix] :: The selected transform does not have a side.')
        return False

    # find the left and right side of the controller transform objects.
    if 'R_' in selection:
        right_ear_ctrl = selection
        left_ear_ctrl = selection.replace('R_', 'L_')
        if not cmds.objExists(left_ear_ctrl):
            RIG_LOG.error('[Ears Fix] :: Left ear controller does not exist: {}.'.format(left_ear_ctrl))
            return False

    if 'L_' in selection:
        left_ear_ctrl = selection
        right_ear_ctrl = selection.replace('L_', 'R_')
        if not cmds.objExists(right_ear_ctrl):
            RIG_LOG.error('[Ears Fix] :: Right ear controller does not exist: {}.'.format(right_ear_ctrl))
            return False

    # find the opposing group node:  {}_Ear_01_Ctrl_Offset_Grp
    right_ear_ctrl_offset = right_ear_ctrl + '_Offset_Grp'

    # remove the constraint
    cnst_dict = remove_constraint(right_ear_ctrl_offset)

    # compute the mirror matrix and apply to the target transfrom
    matrix_utils.mirror_x_axis(object_name=left_ear_ctrl, mirror_object=right_ear_ctrl_offset)
    
    # reapply the constraint
    apply_constraint(cnst_dict=cnst_dict)

    # mirror the left to right ear controllers.
    ear_ctrls = filter(None, map(find_ctrl_transform, cmds.listRelatives(left_ear_ctrl, ad=1, type='shape')))
    for ctrl in ear_ctrls:
        control.mirror(driver_control=node.Node(ctrl))

    # return True for success
    return True


def grab_offset_ctrls(offset_grp=""):
    """
    Gets all the controls from the offset grp provided.
    :param offset_grp: <str> Offset group to gather information from.
    """
    offset_grp_ls = [o for o in cmds.listRelatives(offset_grp, ad=1, c=1, type='transform') if 'Tweak' not in o if
                     o.endswith('Offset_Grp')]
    offset_grp_ls.insert(0, offset_grp)
    return offset_grp_ls


def util_find_deformers():
    """
    Finds body geo attached deformers.
    :return: <list> list of deformers.
    """
    body_geo_name = util_get_body_geo()
    if body_geo_name:
        # finds all the deformers on the selected body mesh object
        deformers = lambda x: filter(None, map(find_deformers, cmds.listHistory(x[-1], pruneDagObjects=1)))
        deformer_names_ls = deformers([body_geo_name]) or []
        deformer_names_ls.insert(len(deformer_names_ls), body_geo_name)
        return deformer_names_ls
    return false


def do_it():
    """
    Steps:
        Select the geometry mesh.
        Find the mirror matrix of the right side and apply it.
        Save weights.
        Save deformation order.
        Unbind the skeleton from the skinCluster node if there is a skin attached.
        Mirror controller shapes.
        Load the skinCluster from file.w
    :return: <bool> False for failure. <bool> True for Success.
    """
    # check if ear offset grp exists
    dynamic_chain = False
    ear_offset_grp = 'L_Ear_01_Ctrl_Offset_Grp'
    if not cmds.objExists(ear_offset_grp):
        RIG_LOG.warning('[Ears Fix] :: {} does not exist in scene.'.format(ear_offset_grp))
        ear_offset_grp = 'L_Ear_DC_01_Ctrl_Offset_Grp'
        dynamic_chain = True
        if not cmds.objExists(ear_offset_grp):
            RIG_LOG.error('[Ears Fix] :: {} does not exist in scene.'.format(ear_offset_grp))
            return False
    skin_name = None
    skin_fn = None

    # grab the body geo name
    body_geo_name = util_get_body_geo()
    deformer_names_ls = []
    if body_geo_name:
        # procure the skin cluster node
        skin_name, skin_fn = skin_utl.get_skin_cluster_obj(body_geo_name)

        # if deformers are found
        if skin_name:
            deformer_names_ls = util_find_deformers()

            # save the skin cluster
            skin_tools.save_skin(object_list=[body_geo_name])

    # mirror the parent controller transform
    offset_grp_ls = grab_offset_ctrls(ear_offset_grp)
    for offset_grp in offset_grp_ls:
        right_side_offset_grp = offset_grp.replace('L_', 'R_')
        if dynamic_chain:
            right_side_jnt_grp = right_side_offset_grp.replace("_Ctrl_Offset_Grp", "_Bnd")
        else:
            right_side_jnt_grp = right_side_offset_grp.replace("_Ctrl_Offset_Grp", "_Offset_Jnt_Grp")

        print("[Ears Fix] :: Mirroring {} >> {}".format(offset_grp, right_side_offset_grp))
        # remove the constraint
        cnst_dict = remove_constraint(right_side_offset_grp)
        jnt_cns_dict = remove_constraint(right_side_jnt_grp)

        # compute the mirror matrix and apply to the target transfrom
        matrix_utils.mirror_x_axis(object_name=offset_grp, mirror_object=right_side_offset_grp)
        matrix_utils.mirror_x_axis(object_name=offset_grp, mirror_object=right_side_jnt_grp)

        # reapply the constraint
        if cnst_dict:
            apply_constraint(cnst_dict=cnst_dict)
        if jnt_cns_dict:
            apply_constraint(cnst_dict=jnt_cns_dict)

    # unbind the skinCluster.
    if skin_name:
        cmds.skinCluster(skin_name, unbind=True, edit=True)

    # mirror controllers.
    ear_ctrls = ['L_Ear_01_Ctrl', 'L_Ear_02_Ctrl', 'L_Ear_03_Ctrl']
    for ctrl in ear_ctrls:
        control.mirror(driver_control=node.Node(ctrl))

    # load the skinCluster
    if skin_name:
        skin_tools.load_skin(mfn_load=False, object_list=[body_geo_name])

        # rename the skin cluster to what it was before
        new_skin, new_skin_fn = skin_utl.get_skin_cluster_obj(body_geo_name)
        cmds.rename(new_skin, skin_name)

    # reorder the deformers

    if deformer_names_ls:
        cmds.reorderDeformers(*deformer_names_ls)

    # clear the selection
    cmds.select(cl=1)

    # return True for success
    return True
