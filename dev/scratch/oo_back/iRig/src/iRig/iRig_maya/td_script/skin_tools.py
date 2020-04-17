"""Provides an easy way to save and load skincluster data files based on selection in Maya."""

# define standard imports
import os
import time
import pprint

# define maya imports
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# define custom imports
import skincluster_utils
import io_utils
import fileTools.default as ft
from rig_tools import RIG_LOG

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "ICON License"
__version__ = "1.1.1"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"

reload(skincluster_utils)

# define global variables
SKIN_PATH = str(os.path.join(ft.ez.path('elems'), 'rig_data', 'skin', 'clipboard'))


def copy_skin_influences(source_obj="", target_obj=""):
    """
    Inserts influence joints into the target mesh.
    :param source_obj: <str>
    :param target_obj: <str>
    :return: <bool> True for success. <bool> False for failure.
    """
    if not source_obj or not target_obj:
        return False
    start_time = time.time()
    if isinstance(target_obj, (str, unicode)):
        target_obj = [target_obj]
    source_skin_name, source_skin_fn = skincluster_utils.get_skin_cluster_obj(source_obj)
    if not source_skin_fn:
        cmds.warning('[Copy Skin Influences] :: {}, No skin found.'.format(source_obj))
        return False
    for t_obj in target_obj:
        target_skin_name, target_skin_fn = skincluster_utils.get_skin_cluster_obj(t_obj)
        if not target_skin_fn:
            cmds.warning('[Copy Skin Influences] :: {}, No skin found.'.format(t_obj))
            continue
        source_influences = skincluster_utils.util_get_skin_influences(source_skin_fn)
        target_influences = skincluster_utils.util_get_skin_influences(target_skin_fn)
        difference = list(set(source_influences) - set(target_influences))
        if difference:
            print('[Copy Skin Influences] :: {}, found objects: {}'.format(target_obj, difference))
            cmds.skinCluster(target_skin_name, e=1, dr=0.0, lw=1, wt=0, ai=difference)
            # unlock influences after adding
            for d_jnt in difference:
                cmds.setAttr('%s.liw' % d_jnt, 0)
        else:
            print('[Copy Skin Influences] :: No objects to add to {}'.format(t_obj))
    end_time = time.time()
    print('[Copy Skin Influences] Completed in {} seconds.'.format(end_time - start_time))
    return True


def bind_geo(components=[]):
    """
    Binds the geo with these items in list
    :param components: <list> list of items to bind.
    :return: <bool> for success.
    """
    # grabs geo selection // nurbsSurface selection // nurbsCurve selection
    geos = cmds.filterExpand(components, sm=(12, 10, 9), fp=True)
    joints = cmds.ls(components, type='joint')

    if not joints or not geos:
        cmds.error("[Bind Selection] :: Incorrect components selected for skinning.")
        return False

    # binds the skin with weight blended method.
    for geo in geos:
        cmds.skinCluster(joints, geo, normalizeWeights=1, bindMethod=0, skinMethod=2,
                         dropoffRate=0.5, obeyMaxInfluences=1, maximumInfluences=3, tsb=1)
    return True


def bind_selection():
    """
    Binds the selected geo items to the selected joint items using the correct binding parameters.
    :returns: <bool> True for success. <bool> False for failure.
    """
    selection = cmds.ls(sl=1)
    if not selection:
        cmds.error("[Bind Selection] :: No components selected for skinning.")
        return False

    bind_geo(selection)
    return True


def bind_like(rename_skin=1):
    """
    Binds the target geo with the same skinning as the source geo.
    :param rename_skin: <bool> if set to True, renames the skinCluster based on the target mesh.
    :return: <bool> True for success. <bool> False for fail.
    """
    selections = cmds.ls(sl=1)
    source = selections[0]
    targets = selections[1:]
    RIG_LOG.info("[Source] :: {}".format(source))
    RIG_LOG.info("[Targets] :: {}".format(targets))
    # get skinCluster node
    skin_cls_node, skin_fn = skincluster_utils.get_skin_cluster_obj(source, return_str=True)
    if not skin_cls_node:
        RIG_LOG.error("[No Skin Found] :: {}".format(source))
        return False
    RIG_LOG.info("[Using skin] :: {}".format(skin_cls_node))
    joints = cmds.listConnections(skin_cls_node + '.matrix', s=1, d=0)

    # make sure that what you are ginding are actually joints
    joints = [j for j in joints if cmds.objectType(j) == 'joint']

    for target in targets:
        skin_name, skin_name_fn = skincluster_utils.get_skin_cluster_obj(target, return_str=True)
        if not skin_name:
            skin_name = cmds.skinCluster(target, joints, tsb=1)[0]
        cmds.copySkinWeights(ss=skin_cls_node, ds=skin_name, noMirror=1,
                             influenceAssociation=("label", "oneToOne", "name"),
                             surfaceAssociation="closestComponent")
        if rename_skin:
            # mesh_node = cmds.listConnections(skin_name, type='mesh')[0]
            skin_new_name = target + '_Skin'
            skin_new_name = skin_new_name.rpartition(':')[-1]
            cmds.rename(skin_name, skin_new_name)
    RIG_LOG.info("[Finished Skin] :: {}".format(skin_new_name))
    return True


def save_skin(filesDirectory=None, object_list=None):
    """
    Saves the skin cluster from objects.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not filesDirectory:
        filesDirectory = SKIN_PATH
    if not object_list:
        object_list = cmds.ls(sl=1)
    if not object_list:
        RIG_LOG.error("[No Selection] :: Please select bound objects.")
        return False
    for sel_obj in object_list:
        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        skin_file = sel_name + '.json'
        skin_file_path = os.path.join(filesDirectory, skin_file)

        # get skin cluster data
        try:
            skin_data = skincluster_utils.get_skin_data(sel_obj)
        except RuntimeError:
            # no skin data found
            print('[Skin Tools Error] :: Unable to get skin from {}.'.format(sel_obj))
            continue
        except AttributeError:
            # unable to find skin deformer set
            print('[Skin Tools Error] :: Unable to get deformer set from {}.'.format(sel_obj))
            continue

        # write the skin cluster data
        start_time = time.time()
        io_utils.write_file(skin_file_path, data=skin_data)
        RIG_LOG.info("[File Saved] :: {} Took {} seconds.".format(skin_file, time.time() - start_time))
    return True


def load_skin(mfn_load=False, filesDirectory=None, object_list=None):
    """
    Loads the skin clusters from directory and applies to the current scene.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not filesDirectory:
        filesDirectory = SKIN_PATH
    if not object_list:
        object_list = cmds.ls(sl=1)
    if not object_list:
        RIG_LOG.error("[No Selection] :: Please select bound items.")
        return False

    for sel_obj in object_list:
        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        skin_file = sel_name + '.json'
        skin_file_path = os.path.join(filesDirectory, skin_file)

        print(os.path.exists(skin_file_path))

        # attempt to read the skin cluster .json file
        try:
            weight_data = io_utils.read_file(skin_file_path)
        except IOError:
            RIG_LOG.error("[No File] :: Please save skin cluster file first.")
            continue

        # apply the skin cluster data for this object
        start_time = time.time()
        if mfn_load:
            # no undo
            skincluster_utils.mfn_set_skin_data(weight_data=weight_data, mesh_name=sel_obj)
        else:
            # is undoable
            skincluster_utils.set_skin_data(weight_data=weight_data, mesh_name=sel_obj)
        RIG_LOG.info("[File Loaded] :: {} Took {} seconds.".format(skin_file, time.time() - start_time))
    return True


def get_skin_file_data():
    """
    Prints the current skin cluster JSON file.
    :return: <bool> True for success. <bool> False for failure.
    :note:
        The skin file data is structured in this manner:
         u'76' : This is the vertex index unicode integer.
            [u'0', u'1', u'2', u'3', u'4'] : This is the joint index unicode integer.
                [0.7754, 0.1462, 0.0785, 0.0, 0.0] :  These are the weight float values associated with the joint index.
    """
    selection = cmds.ls(sl=1)
    weight_data = {}

    if not selection:
        RIG_LOG.error("[No Selection] :: Please select bound objects.")
        return False
    for sel_obj in selection:
        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        skin_file = sel_name + '.json'
        skin_file_path = os.path.join(SKIN_PATH, skin_file)

    # attempt to read the skin cluster .json file
    try:
        weight_data = io_utils.read_file(skin_file_path)
    except IOError:
        RIG_LOG.error("[No File] :: Please save skin cluster file first.")
        return False
    return weight_data
