import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya_tools.utilities.decorators as dec
import maya.cmds as mc

@dec.m_object_arg
def set_deformer_weights(m_deformer, all_weights):
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    for dag_index in range(set_members_plug.numElements()):
        element_plug = set_members_plug.elementByLogicalIndex(dag_index)
        connected_plugs = om.MPlugArray()
        element_plug.connectedTo(connected_plugs, True, False)
        weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
        object_weights = all_weights[dag_index]
        for i in range(connected_plugs.length()):
            for w in range(len(object_weights)):
                weight_plug.child(0).elementByLogicalIndex(w).setDouble(object_weights[w])


@dec.m_object_arg
def get_deformer_weights(m_deformer):
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    all_weights = []
    for dag_index in range(set_members_plug.numElements()):
        object_weights = []
        element_plug = set_members_plug.elementByLogicalIndex(dag_index)
        connected_plugs = om.MPlugArray()
        element_plug.connectedTo(connected_plugs, True, False)
        mesh_m_object = connected_plugs[0].node()
        mesh_iterator = om.MItGeometry(mesh_m_object)
        weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
        while not mesh_iterator.isDone():
            i = mesh_iterator.index()
            weight = weight_plug.child(0).elementByLogicalIndex(i).asDouble()
            object_weights.append(weight)
            mesh_iterator.next()
        all_weights.append(object_weights)
    return all_weights


def find_deformer_node(node, deformer_type):
    """
    Get the deformer node from the node's construction history; return None deformer found.
    :param node: (transform) - node to check for deformer node
    :param deformer_type: (str) - name of the deformer type (eg. wrap, lattice)
    :return: deformer node, otherwise None
    """
    for history_node in mc.listHistory(get_selection_string(node)):
        if mc.nodeType(history_node) == deformer_type:
            return history_node
    return None


def node_exists(node_name):
    try:
        selection = om.MSelectionList()
        selection.add( node_name )
        return True
    except Exception, e:
        return False


@dec.m_dag_path_arg
def get_mesh_points(mesh, space=om.MSpace.kWorld):
    points = om.MPointArray()
    om.MFnMesh(mesh).getPoints(points, space)
    return points


@dec.m_dag_path_arg
def get_mesh_uvs(mesh):
    mesh_functions = om.MFnMesh(mesh)
    u_array = om.MFloatArray()
    v_array = om.MFloatArray()
    mesh_functions.getUVs(u_array, v_array)
    return u_array, v_array


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    if isinstance(node, om.MDagPath):
        return node.node()
    selection_list = om.MSelectionList()
    selection_list.add(node)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object

def get_m_dag_path(node):
    if isinstance(node, om.MDagPath):
        return node
    if isinstance(node, om.MObject):
        return om.MDagPath.getAPathTo(node)
    selection_list = om.MSelectionList()
    selection_list.add(node)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return om.MDagPath.getAPathTo(m_object)