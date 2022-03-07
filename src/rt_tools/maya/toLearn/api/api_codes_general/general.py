import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya_tools.utilities.decorators as dec
import maya.cmds as mc
import logging

@dec.m_object_arg
def set_deformer_mesh_weights(m_deformer, mesh_name, target_weights):
    """
    set deformer weights for specific mesh
    """
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)

    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
        weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
        source_plug = set_members_plug.elementByLogicalIndex(dag_index).source()
        if not source_plug.isNull():
            mesh_m_object = source_plug.node()
            current_mesh_name = om.MFnDependencyNode(mesh_m_object).name()
            if current_mesh_name == mesh_name:
                for w in range(len(target_weights)):
                    weight_plug.child(0).elementByLogicalIndex(w).setDouble(target_weights[w])
            return


@dec.m_object_arg
def get_deformer_mesh_weights(m_deformer, mesh_name):
    """
    get deformer weights for specific mesh
    """

    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)

    object_weights = None
    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
        source_plug = set_members_plug.elementByLogicalIndex(dag_index).source()
        if not source_plug.isNull():
            mesh_m_object = source_plug.node()
            current_mesh_name = om.MFnDependencyNode(mesh_m_object).name()
            if current_mesh_name == mesh_name:
                mesh_iterator = om.MItGeometry(mesh_m_object)
                weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
                object_weights = []
                while not mesh_iterator.isDone():
                    i = mesh_iterator.index()
                    weight = weight_plug.child(0).elementByLogicalIndex(i).asDouble()
                    object_weights.append(weight)
                    mesh_iterator.next()
                break
    if not object_weights:
        raise Exception('Unable to find mesh weights for %s' % mesh_name)
    return object_weights

@dec.m_object_arg
def set_deformer_weights(m_deformer, all_weights):
    if isinstance(all_weights, list):
        print('Legacy Weights format found... ')
        set_deformer_weights_list(m_deformer, all_weights)
    elif isinstance(all_weights, dict):
        set_deformer_weights_dict(m_deformer, all_weights)
    else:
        raise Exception('Invalid weights type "%s"' % type(all_weights))


@dec.m_object_arg
def set_deformer_weights_dict(m_deformer, all_weights):

    members = get_deformer_members(m_deformer)
    for x in all_weights:
        if x not in members:
            print('WARNING: "%s" was not a member of %s. unable to set weights' % (x, get_selection_string(m_deformer)))
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
        element_plug = set_members_plug.elementByLogicalIndex(dag_index)
        connected_plugs = om.MPlugArray()
        element_plug.connectedTo(connected_plugs, True, False)
        mesh_m_object = connected_plugs[0].node()
        mesh_name = om.MFnDependencyNode(mesh_m_object).name()
        if mesh_name in all_weights:
            weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
            object_weights = all_weights[mesh_name]
            for i in range(connected_plugs.length()):
                for w in range(len(object_weights)):
                    weight_plug.child(0).elementByLogicalIndex(w).setDouble(object_weights[w])
        else:
            print('The mesh "%s" was not found in membership of %s. Unable to set deformer weights.' % (
                mesh_name,
                depend_functions.name()
            ))

@dec.m_object_arg
def set_deformer_weights_list(m_deformer, all_weights):
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
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
    return get_deformer_weights_dict(m_deformer)


@dec.m_object_arg
def get_deformer_weights_dict(m_deformer):
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    all_weights = dict()
    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
        object_weights = []
        element_plug = set_members_plug.elementByLogicalIndex(dag_index)
        connected_plugs = om.MPlugArray()
        element_plug.connectedTo(connected_plugs, True, False)
        if connected_plugs[0]:
            mesh_m_object = connected_plugs[0].node()
            mesh_iterator = om.MItGeometry(mesh_m_object)
            weight_plug = weights_list_plug.elementByLogicalIndex(dag_index)
            while not mesh_iterator.isDone():
                i = mesh_iterator.index()
                weight = weight_plug.child(0).elementByLogicalIndex(i).asDouble()
                object_weights.append(weight)
                mesh_iterator.next()
            all_weights[om.MFnDependencyNode(mesh_m_object).name()] = object_weights
    return all_weights


@dec.m_object_arg
def get_geometry(m_deformer):
    """
    Gets member geometry names witghout the components
    """
    geometry_names = []
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    members.length()
    for i in range(members.length()):
        m_object = om.MObject()
        members.getDependNode(i, m_object)
        geometry_names.append(om.MFnDependencyNode(m_object).name())
    return geometry_names


@dec.m_object_arg
def get_deformer_members(m_deformer):
    members_dict = dict()
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    members.length()
    for i in range(members.length()):
        m_object = om.MObject()
        members.getDependNode(i, m_object)
        if m_object.hasFn(om.MFn.kDagNode):
            component_m_object = om.MObject()
            dag_path = om.MDagPath()
            members.getDagPath(i, dag_path, component_m_object)
            if dag_path and not component_m_object.isNull():
                dag_functions = om.MFnDagNode(dag_path)
                if str(dag_functions.typeName()) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
                    object_vertices = []
                    iterator = om.MItGeometry(dag_path, component_m_object)
                    while not iterator.isDone():
                        object_vertices.append(int(iterator.index()))
                        iterator.next()
                    members_dict[str(dag_functions.name())] = object_vertices
    return members_dict


@dec.m_object_arg
def add_deformer_members(m_deformer, members):
    set_functions = om.MFnSet(oma.MFnGeometryFilter(m_deformer).deformerSet())
    if not isinstance(members, dict):
        members = dict((x, None) for x in members)
    for member_name in members:
        vertex_indices = members[member_name]
        if mc.nodeType(member_name) == 'mesh' and vertex_indices:
            vertices = om.MIntArray()
            [vertices.append(x) for x in vertex_indices]
            component = om.MFnSingleIndexedComponent()
            component_object = component.create(om.MFn.kMeshVertComponent)
            component.addElements(vertices)
            dag = om.MDagPath()
            sel = om.MSelectionList()
            sel.add(member_name)
            sel.getDagPath(0, dag)
            set_functions.addMember(dag, component_object)
        else:
            dag = om.MDagPath()
            sel = om.MSelectionList()
            sel.add(member_name)
            sel.getDagPath(0, dag)
            set_functions.addMember(dag)


@dec.m_object_arg
def remove_deformer_geometry(m_deformer, geometry):
    members = get_deformer_members(m_deformer)
    for g in geometry:
        if g not in members:
            logging.getLogger('rig_build').warning('%s was not a member of the deformer set' % g)
        else:
            members.pop(g)
    # Need to clear the set to clean up components added with cmds.sets
    set_deformer_members(m_deformer, members)


def set_deformer_members(m_deformer, members):
    set_functions = om.MFnSet(oma.MFnGeometryFilter(m_deformer).deformerSet())
    set_functions.clear()
    add_deformer_members(m_deformer, members)


@dec.m_object_arg
def get_deformer_weights_list(m_deformer):
    deformer_functons = oma.MFnGeometryFilter(m_deformer)
    depend_functions = om.MFnDependencyNode(m_deformer)
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    weights_list_plug = depend_functions.findPlug(depend_functions.attribute('weightList'), False)
    set_members_plug = set_functions.findPlug(set_functions.attribute('dagSetMembers'), False)
    all_weights = []
    dag_indices = om.MIntArray()
    set_members_plug.getExistingArrayAttributeIndices(dag_indices)
    for dag_index in dag_indices:
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


@dec.m_object_arg
def find_deformer_nodes(node, deformer_type):
    deformers = []
    for history_node in mc.listHistory(get_selection_string(node)):
        if mc.nodeType(history_node) == deformer_type:
            deformers.append(history_node)
    return deformers


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
    except Exception as e:
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


def get_m_object_set(m_object):
    # returns m_set from an m_object
    fnSet = om.MFnSet()
    itGraph = om.MItDependencyGraph(m_object, om.MFn.kSet)
    while not itGraph.isDone():
        fnSet.setObject(itGraph.currentItem())
        itGraph.next()
    m_object_set = fnSet
    return m_object_set


def get_m_members_data(m_object, m_object_set):
    # get member data of a mSet
    m_members_data = dict()
    members = om.MSelectionList()
    m_object_set.getMembers(members, False)
    dagPath = om.MDagPath()
    components = om.MObject()
    members.getDagPath(0, dagPath, components)
    weightFn = oma.MFnWeightGeometryFilter(m_object)
    weights = om.MFloatArray()
    weightFn.getWeights(0, components, weights)
    itGeo = om.MItGeometry(dagPath, components)
    i = 0
    while not itGeo.isDone():
        m_members_data.update({'vertex id:', itGeo.index(), 'weight:', weights[i]})
        i += 1
        itGeo.next()
    return m_members_data


def name_to_plug(attrName, nodeObject):
    # finds a plug
    depNodeFn = om.MFnDependencyNode(nodeObject)
    attrObject = depNodeFn.attribute(attrName)
    plug = om.MPlug(nodeObject, attrObject)
    return plug

def get_m_shape(m_object):
    # returns m_shape
    if m_object.apiType() == om.MFn.kTransform:
        path = om.MDagPath.getAPathTo(m_object)
        numShapes = om.MScriptUtil()
        numShapes.createFromInt(0)
        numShapesPtr = numShapes.asUintPtr()
        path.numberOfShapesDirectlyBelow(numShapesPtr)
        if om.MScriptUtil(numShapesPtr).asUint():
            path.extendToShapeDirectlyBelow(0)
            m_shape = path.node()
            return m_shape
    return m_object


def get_m_point(matrixList):
    util = om.MScriptUtil()
    m_matrix = om.MMatrix()
    util.createMatrixFromList(matrixList, m_matrix)
    m_transformation_matrix = om.MTransformationMatrix(m_matrix)
    vector = m_transformation_matrix.translation(om.MSpace.kWorld)
    m_point = om.MPoint(vector)

    return m_point