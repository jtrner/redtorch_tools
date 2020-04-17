"""Provides a toolkit for Maya deformers for saving, manipulating and setting of weights, data retreival"""

# import standard modules
import os
import time
import pprint
import itertools

# import maya modules
from maya import cmds
from maya import OpenMaya as api0
from maya import OpenMayaAnim as apiAnim0

# import custom modules
#try:
#    from maya_scene.utilities import deformer_utilities
#except ImportError:
#    from maya_scene import deformer_utilities
import io_utils
import fileTools.default as ft
import renamer
from rig_tools import RIG_LOG

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "ICON LICENSE"
__version__ = "1.0.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


# define global variables
DEFORM_PATH = str(os.path.join(ft.ez.path('elems'), 'rig_data', 'deformer', 'clipboard'))
HANDLE_ID = renamer.HANDLE_ID


def util_rename_deform_set(deformer=""):
    """
    Either by specified name or selection, rename its deformer set.
    :param deformer: <str> deformer name. You may leave this blank.
    :return: <str> name of the deformer set. <bool> False for failure.
    """
    if not deformer:
        deformer = cmds.ls(sl=1)
    if not deformer:
        return False
    deformer = deformer[0]
    try:
        set_name = util_find_deformer_set(deformer=deformer)
    except RuntimeError:
        cmds.error("[Rename Deform Set] :: Unable to retreivve deformer set object.")
    new_set_name = deformer + 'Set'
    print("[Rename Deform Set] :: Set renamed: {}".format(new_set_name))
    return cmds.rename(set_name, new_set_name)


def util_get_deformer_weights(deformer=""):
    """
    Return deformer weights.
    :param deformer: <str> deformer name.
    :return: <list> deformer weight data.
    """
    return deformer_utilities.get_deformer_weights(deformer)


def util_get_active_deform_components(mesh_obj="", verbose=0, all_active=1):
    """
    Get non 100% active deformers.
    :param mesh_obj: <str> mesh object to check.
    :param verbose: <bool> print stuff.
    :param all_active: <bool> return all active components.
    :return: <dict> deformer, non 100% vertices.
    """
    return_dict = {}
    deformers = util_find_deformers(mesh_obj)
    if verbose:
        print(deformers)
    for deform in deformers:
        deform_set = util_find_deformer_set(deform)
        active_components = cmds.sets(deform_set, q=1)
        if verbose:
            print(deform_set, active_components)
        if all_active:
            return_dict[deform] = active_components
        else:
            if len(active_components) != 1:
                return_dict[deform] = active_components
    return return_dict


def util_get_set_components(set_name=""):
    """
    Query the set components acting on the set.
    :param set_name: <str> set name to query from.
    :return: <list> components.
    """
    return cmds.sets(set_name, q=1)


def util_mesh_get_closest_vertex(mesh_name="", vertex_name=""):
    """
    Gets the closest vertex point on the mesh supplied.
    :param mesh_name: <str> find a vertex on this mesh from the vertex name provided.
    :param vertex_name: <str> use this vertex position to find the closest vertex on the mesh provided.
    :return: <str> closest vertex.
    """
    pos = cmds.xform(vertex_name, t=1, ws=1, q=1)
    pos_m_vector = api0.MVector(*pos)
    m_sel_list = api0.MSelectionList()
    m_sel_list.add(mesh_name)
    m_dag = api0.MDagPath()
    dag_path = m_sel_list.getDagPath(0, m_dag)
    m_mesh = api0.MFnMesh(dag_path)

    # getting closest face ID
    ID = m_mesh.getClosestPoint(api0.MPoint(pos_m_vector),space=api0.MSpace.kWorld)[1]

    # face's vertices list_vertex
    list_vertex = cmds.ls(cmds.polyListComponentConversion (mesh_name+'.f['+str(ID)+']', ff=True, tv=True), flatten=True)

    # setting vertex [0] as the closest one
    d = pos_m_vector - api0.MVector(cmds.xform(list_vertex[0], t=True, ws=True, q=True))

    # using distance squared to compare distance
    smallest_distance = d.x*d.x+d.y*d.y+d.z*d.z
    closest = list_vertex[0]

    # iterating from vertex [1]
    for i in range(1,len(list_vertex)) :
        d = pos_m_vector - api0.MVector(cmds.xform(list_vertex[i],t=True,ws=True,q=True))
        d2 = d.x*d.x+d.y*d.y+d.z*d.z
        if d2 < smallest_distance:
            smallest_distance = d2
            closest = list_vertex[i]      
    return closest


def util_check_vertex_in_set(deformer_name, vertex_name):
    """
    Check if vertex supplied is within the deformer set.
    :param deformer_name: <str> deformer name to check the vertex at.
    :param vertex_name: <str> vertex name to check within the set.
    :returns: <bool> True/ False if a vertex belongs within the set.
    """
    deform_set = cmds.listSets(object=deformer_name)[0]
    return cmds.sets(vertex_name, im=deform_set)


def util_get_set_items(set_name=""):
    """
    Grabs the correct order of set items from the set name provided.
    :param set_name: <str> set name to use for query.
    :returns: <list> ordered list of affected items.
    """
    set_size = cmds.sets(set_name, size=1, query=1)
    set_items = cmds.listConnections(set_name+'.dagSetMembers')
    if len(set_items) != set_size:
        cmds.warning('[Set Size Warning] :: Incorrect set size avaliable for set: {}'.format(set_name))
    return set_items


def util_get_set_members(set_name=""):
    """
    Get the set members affecting the defromer object.
    :param set_name: <str> set name to use for query.
    """
    element_dict = {}
    set_elements = util_get_set_components(set_name)

    set_items = util_get_set_items(set_name)
    for set_item in set_items:
        element_dict[set_item] = []
        for element in set_elements:
            if set_item in element:
                element_dict[set_item].append(element)
    cmds.select(cl=1)
    
    element_order = []
    for item in set_items:
        element_order.append((item, element_dict[item]))
    return element_order


def util_get_attributes(obj):
    """
    Gets attribute dictionary, with values of an object
    :param obj: <str> object name.
    """
    return_dictionary = {}
    attrs = cmds.listAttr(obj, s=1)
    for attr in attrs:
        try:
            return_dictionary[attr] = cmds.getAttr('{}.{}'.format(obj, attr))
        except ValueError:
            continue
    return return_dictionary


def util_get_lattice_objects():
    """
    Grab all lattice objects in the scene.
    :return: <list> lattice objects.
    """
    it = api0.MItDependencyNodes(api0.MFn.kFFD);
    lattice_objects = []
    while not it.isDone():
        fn = apiAnim0.MFnLatticeDeformer(it.item());
        affected = api0.MObjectArray();
        fn.getAffectedGeometry(affected);
        for i in range(affected.length()):
            fnDep = api0.MFnDependencyNode(affected[i]);
            # print(fnDep.name());
        # base lattice
        base_lattice_obj = fn.baseLattice()
        fn_dag_node = api0.MFnDagNode(base_lattice_obj);
        fn_par_dag_node = api0.MFnDagNode(fn_dag_node.parent(0));

        find = fn_dag_node.name(), fn_par_dag_node.name(), fn.name()
        lattice_objects.append(find)
        it.next();
    return lattice_objects;


def util_set_deformer_weights(m_deformer, all_weights, index=False):
    """
    Direct copy from deformer_utilities.py from pipeline. Needed to set the weight by specific index.
    :param m_deformer: <MOBject> deformer's MObject class.
    :param all_weights: <dict> all weights related to this deformer.
    :param index: <int>, <bool> integer for the valid deformer index weights. False to stop operation.
    """
    if index is False:
        return False
    deformer_functons = apiAnim0.MFnGeometryFilter(m_deformer)
    depend_functions = api0.MFnDependencyNode(m_deformer)
    set_functions = api0.MFnSet(deformer_functons.deformerSet())
    members = api0.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    for dag_index in range(set_members_plug.numElements()):
        element_plug = set_members_plug.elementByLogicalIndex(dag_index)
        connected_plugs = api0.MPlugArray()
        element_plug.connectedTo(connected_plugs, True, False)
        weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
        object_weights = all_weights[dag_index]
        for i in range(connected_plugs.length()):
            if not index in i:
                continue
            for w in range(len(object_weights)):
                weight_plug.child(0).elementByLogicalIndex(w).setDouble(object_weights[w])
    return True


def util_get_deformer_shape(node):
    """
    From the node provided, aquire the attached deformer node.
    :param node: <MObject> Maya's Shape node.
    :return: <MObject> deformer node.
    """
    if isinstance(node, str):
        node = util_get_m_object(node)
    m_node = api0.MFnDependencyNode(node)
    check_node_name = m_node.name()
    it_dg = api0.MItDependencyGraph(node,
                                    api0.MItDependencyGraph.kDownstream,
                                    api0.MItDependencyGraph.kDepthFirst,
                                    api0.MItDependencyGraph.kNodeLevel)
    defomer_nodes = []
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        for deformer_node_id in HANDLE_ID:
            if cur_item.hasFn(deformer_node_id):
                m_node = api0.MFnDependencyNode(cur_item)
                defomer_nodes.append({check_node_name: {'name': m_node.name(),
                                                        'type_name': m_node.typeName(),
                                                        'm_depend_node': m_node,
                                                        'm_obj': cur_item,
                                                        'type_id': cur_item.apiType()}})
                break
        it_dg.next()
    return defomer_nodes


def util_get_m_object(obj_name=""):
    """
    Gets the MObject from the string specified.
    :param obj_name: <str> name of node.
    :return: <MObject> if successful, <bool> False if fail.
    """
    if not obj_name:
        return False
    m_obj = api0.MObject()
    m_list = api0.MSelectionList()
    api0.MGlobal.getSelectionListByName(obj_name, m_list)
    m_list.getDependNode(0, m_obj);
    return m_obj


def util_find_deformers(selection=""):
    """
    finds all possible deformers.
    :param selection: <str> find the deformers from the selection provided.
    """
    deformer_types = ['skinCluster', 'cluster', 'deformCluster', 'lattice', 'softMod', 'deltaMush', 'wire', 'nonLinear', 'ffd']
    findDeformers = lambda sel: [x for x in deformer_types if cmds.objectType(sel) in x]
    inputs = cmds.listHistory(selection, pruneDagObjects=1)

    deformer_ls = []
    for inp in inputs:
        deformer = findDeformers(inp)
        if not deformer:
            continue
        deformer_ls.append(inp)
    return deformer_ls


def util_find_deformer_set(deformer=""):
    """
    Finds the deformer set associated with this deformer.
    :param deformer: <str> find the MFnSet from this deformer provided.
    :returns: <bool> False for failure. <str> deform set.
    """
    try:
        deformer_obj = util_get_m_object(deformer)
    except RuntimeError:
        cmds.error("[Find Deform Set] :: Unable to find deform object: {}".format(deformer))
        return False
    deform_fn = apiAnim0.MFnGeometryFilter(deformer_obj)
    deform_set_obj = deform_fn.deformerSet()
    if deform_set_obj.isNull():
        raise Exception('[Find Deform Set] :: Unable to determine deformer set for "{}"!'.format(deformer))
    return api0.MFnDependencyNode(deform_set_obj).name()


def util_read_file(filesDirectory=None, object_list=None):
    """
    Reads the deformer file in rig_data directory.
    :param filesDirectory: <str> file directory path name.
    :param object_list: <list> find the data from the objects provided.
    :return: <dict> deformer data on selected objects.
    """
    if not filesDirectory:
        filesDirectory = DEFORM_PATH
    if not object_list:
        object_list = cmds.ls(sl=1)
    if not object_list:
        RIG_LOG.error("[No Selection] :: Please select bound objects.")
        return False

    for sel_obj in object_list:
        deform_data = {}

        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        deform_file = sel_name + '.json'
        deform_file_path = os.path.join(filesDirectory, deform_file)
        try:
            deform_data = io_utils.read_file(deform_file_path)
        except IOError:
            RIG_LOG.error("[No File] :: Please save deform cluster file first.")
            continue
        print(deform_data.keys())
    return deform_data


def save_defomer(filesDirectory=None, object_list=None):
    """
    Saves the deformer from objects.
    :param filesDirectory: <str> file directory path name.
    :param object_list: <list> save the data from the objects provided.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not filesDirectory:
        filesDirectory = DEFORM_PATH
    if not object_list:
        object_list = cmds.ls(sl=1)
    if not object_list:
        RIG_LOG.error("[No Selection] :: Please select bound objects.")
        return False

    for sel_obj in object_list:
        deform_data = {}

        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        deform_file = sel_name + '.json'
        deform_file_path = os.path.join(filesDirectory, deform_file)
        
        deformers = util_find_deformers(sel_obj)
        if not deformers:
            continue
        mesh_name = sel_name.split('-')[-1]
        # get deformer data
        for deformer in deformers:
            if 'skinCluster' in cmds.objectType(deformer):
                continue
            deform_data[deformer] = {}
            deformer_set = util_find_deformer_set(deformer)

            # gets the m_object of the deformer and grabs the data in it
            deform_data[deformer] = {
            'Weights': deformer_utilities.get_deformer_weights(deformer),
            'Set': deformer_set,
            'Elements': cmds.sets(deformer_set, q=1),
            'Attributes': {deformer: util_get_attributes(deformer),

                        }
            }

        # write the deformer data
        start_time = time.time()
        io_utils.write_file(deform_file_path, data=deform_data)
        RIG_LOG.info("[File Saved] :: {} Took {} seconds.".format(deform_file, time.time() - start_time))
    return True


def load_deformer(filesDirectory=None, object_list=None):
    """
    Loads the deformers from directory and applies to the current scene.
    :param filesDirectory: <str> file directory path name.
    :param object_list: <list> find the data from the objects provided.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not filesDirectory:
        filesDirectory = DEFORM_PATH
    if not object_list:
        object_list = cmds.ls(sl=1)
    if not object_list:
        RIG_LOG.error("[No Selection] :: Please select bound items.")
        return False

    for sel_obj in object_list:
        sel_name = sel_obj
        if ':' in sel_obj:
            sel_name = sel_obj.replace(':', '-')
        deform_file = sel_name + '.json'
        deform_file_path = os.path.join(filesDirectory, deform_file)

        if not os.path.exists(deform_file_path):
            continue

        # attempt to read the deformer .json file
        try:
            deform_data = io_utils.read_file(deform_file_path)
        except IOError:
            RIG_LOG.error("[No File] :: Please save deform cluster file first.")
            continue
        print deform_data.keys()
        for deformer in deform_data:
            if not cmds.objExists(deformer):
                continue
            set_name = deform_data[deformer]['Set']
            weights_data = deform_data[deformer]['Weights']
            cmds.sets(sel_obj, fe=set_name)
            util_set_deformer_weights(deformer, weights_data)
    return True
