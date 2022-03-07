import time
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya_tools.utilities.decorators as dec
import maya_tools.deformer_utilities.general as gen
import maya_tools.utilities.mesh_utilities as mtl
import maya.cmds as mc
from rig_math.vector_2d import Vector


@dec.m_object_arg
def get_mesh(skin_cluster):
    """
    :param skin_cluster: MObject
    :return: MDagPath / None
    """

    iterator = om.MItDependencyGraph(
        skin_cluster,
        om.MItDependencyGraph.kUpstream,
        om.MItDependencyGraph.kPlugLevel
    )
    while not iterator.isDone():
        item = iterator.thisNode()
        if item.hasFn(om.MFn.kMesh):
            return om.MDagPath.getAPathTo(item)
        iterator.next()


@dec.m_object_arg
def get_influences(skin_cluster):
    """
    Returns skin influences.
    :param skin_cluster: MObject
    :return: MDagPathArray.
    """
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    influences = om.MDagPathArray()
    skin_functions.influenceObjects(influences)
    return influences


@dec.m_object_arg
def get_influence_weights(skin_cluster, index, threshold=0.00001):
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    mesh, components = get_components(skin_cluster)
    weights_array = om.MDoubleArray()
    skin_functions.getWeights(mesh, components, index, weights_array)
    weights = dict()
    for x in range(weights_array.length()):
        weight = weights_array[x]
        if weight > threshold:
            weights[x] = weight
    return weights


@dec.m_object_arg
def get_weights(skin_cluster):
    """
    Gets the skin cluster data by vertex component.
    :param skin_cluster: <MObject> Skin Cluster.
    :return: <dict> weight information.
    """
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    influence_data = []
    start = time.time()
    mesh, components = get_components(skin_cluster)
    influences = get_influences(skin_cluster)
    points = gen.get_mesh_points(mesh)
    u_array, v_array = gen.get_mesh_uvs(mesh)
    for i in range(influences.length()):
        influence = influences[i]
        index = skin_functions.indexForInfluenceObject(influence)
        t = om.MFnTransform(influence).getTranslation(om.MSpace.kWorld)
        influence_data.append(dict(
            weights=get_influence_weights(skin_cluster, index),
            index=index,
            position=(t[0], t[1], t[2]),
            name=influence.partialPathName()
        ))
    print 'Got weights for %s verts and %s influences in %s seconds' % (
        points.length(),
        influences.length(),
        time.time()-start
    )
    return dict(
        vertex_positions=[(points[x][0], points[x][1], points[x][2]) for x in range(points.length())],
        vertex_uvs=[(u_array[x], u_array[x]) for x in range(u_array.length())],
        influences=influence_data
    )


@dec.m_object_arg
def remap_name_influences(skin_cluster, influence_data):
    named_data = dict((x['name'], x) for x in influence_data)
    influence_map = dict()
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    influences = om.MDagPathArray()
    skin_functions.influenceObjects(influences)
    for i in range(influences.length()):
        influence = influences[i]
        index = skin_functions.indexForInfluenceObject(influence)
        influence_name = influence.partialPathName()
        if influence_name in named_data:
            influence_map[index] = named_data[influence_name]
    return influence_map


@dec.m_object_arg
def remap_index_influences(skin_cluster, influence_data):
    indexed_data = dict((x['index'], x) for x in influence_data)
    influence_map = dict()
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    influences = om.MDagPathArray()
    skin_functions.influenceObjects(influences)
    for i in range(influences.length()):
        influence = influences[i]
        index = skin_functions.indexForInfluenceObject(influence)
        if index in indexed_data:
            influence_map[index] = indexed_data[index]
    return influence_map


@dec.m_object_arg
def remap_world_space_influences(skin_cluster, influence_data):
    named_data = dict((x['name'], x) for x in influence_data)
    influence_map = dict()
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    influences = om.MDagPathArray()
    skin_functions.influenceObjects(influences)
    for x in xrange(influences.length()):
        influence = influences[x]
        index = skin_functions.indexForInfluenceObject(influence)
        closest_distance = float('inf')
        closest_influence_name = None
        influence_point = om.MPoint(om.MFnTransform(influence).getTranslation(om.MSpace.kWorld))
        for y in influence_data:
            data_point = om.MPoint(*y['position'])
            distance = data_point.distanceTo(influence_point)
            if distance < closest_distance:
                closest_distance = distance
                if closest_influence_name not in influence_map.values():
                    closest_influence_name = y['name']
        if closest_influence_name:
            influence_map[index] = named_data[closest_influence_name]
    return influence_map


@dec.m_object_arg
def set_weights(skin_cluster, data, influence_association='name', vertex_association='index', use_selected_vertices=False):
    skin_cluster_name = gen.get_selection_string(skin_cluster)
    mesh = get_mesh(skin_cluster)
    mesh_name = mc.skinCluster(skin_cluster_name, q=True, geometry=True)[0]
    vertex_selection = None

    if use_selected_vertices:
        get_vertex_selection = mtl.get_selected_vertex_indices()
        selected_mesh_names = [gen.get_selection_string(x) for x in mtl.get_selected_mesh_objects()]
        if len(selected_mesh_names) != 1:
            raise Exception('You must select vertices on %s to set_weights on selected_vertices' % mesh_name)
        if mesh_name != selected_mesh_names[0] or not get_vertex_selection:
            raise Exception('You must select vertices on %s to set_weights on selected_vertices' % mesh_name)
        vertex_selection = mc.ls(sl=True)

    influences = get_influences(skin_cluster)

    if influence_association == 'index':
        influence_map = remap_index_influences(skin_cluster, data['influences'])
    elif influence_association == 'name':
        influence_map = remap_name_influences(skin_cluster, data['influences'])
    elif influence_association == 'world_space':
        influence_map = remap_world_space_influences(skin_cluster, data['influences'])
    else:
        raise KeyError('Invalid influence_association "%s"' % influence_association)

    for inf in mc.skinCluster(skin_cluster_name, q=True, influence=True):
        mc.setAttr('%s.liw' % inf, False)

    mc.setAttr(
        '%s.normalizeWeights' % skin_cluster_name,
        False
    )
    start = time.time()

    vertex_map = None
    if vertex_association == 'world_space':
        points = om.MPointArray()
        for p in data['vertex_positions']:
            points.append(p[0], p[1], p[2])
        vertex_map = remap_position_indices(
            mesh_name,
            points
        )
    if vertex_association == 'uvs':
        vertex_map = remap_uv_indices(
            mesh_name,
            data['uvs']
        )

    mesh_points = gen.get_mesh_points(mesh)
    print 'Built vertex association map for %s vertices  in %s seconds' % (
        mesh_points.length(),
        time.time()-start
    )

    start = time.time()
    if vertex_selection:
        mc.skinPercent(skin_cluster_name, vertex_selection, nrm=False, prw=100)
    else:
        mc.skinPercent(skin_cluster_name, mesh_name, nrm=False, prw=100)

    for x in influence_map:
        set_influence_weights(
            skin_cluster,
            x,
            influence_map[x]['weights'],
            vertex_map=vertex_map,
            use_selected_vertices=use_selected_vertices
        )

    mc.setAttr(
        '%s.normalizeWeights' % skin_cluster_name,
        True
    )
    print 'Set weights for %s verts and %s influences in %s seconds' % (
        mesh_points.length(),
        influences.length(),
        time.time()-start
    )


@dec.m_dag_path_arg
def remap_position_indices(mesh, points, use_selected_vertices=None):
    if not isinstance(points, om.MPointArray):
        raise Exception('Positions must be type: MPointArray, not %s' % type(points))
    if not isinstance(mesh, om.MDagPath):
        raise Exception('mesh must be type: MDagPath, not %s' % type(mesh))
    index_map = dict()
    if use_selected_vertices:
        selection_list = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection_list)
        mesh = om.MDagPath()
        components = om.MObject()
        selection_list.getDagPath(0, mesh, components)

    else:
        components = om.MObject()
    vertex_iterator = om.MItMeshVertex(mesh, components)
    while not vertex_iterator.isDone():
        position = vertex_iterator.position()
        vertex_index = vertex_iterator.index()
        closest_distance = float('inf')
        closest_index = None
        for p in range(points.length()):
            point = points[p]
            distance = position.distanceTo(point)
            if distance < closest_distance:
                closest_distance = distance
                closest_index = p
        index_map[vertex_index] = closest_index
        vertex_iterator.next()
    return index_map


@dec.m_dag_path_arg
def remap_uv_indices(mesh, uvs, use_selected_vertices=None):
    if not isinstance(uvs, list):
        raise Exception('Uvs must be type: list, not %s' % type(uvs))
    if not isinstance(mesh, om.MDagPath):
        raise Exception('mesh must be type: MDagPath, not %s' % type(mesh))
    selected_vertex_indices = None
    if use_selected_vertices:
        selected_vertex_indices = mtl.get_selected_vertex_indices()
    u_array, v_array = gen.get_mesh_uvs(mesh)
    index_map = dict()
    point_vectors = [(uvs[x][0], uvs[x][1]) for x in range(len(uvs))]
    for vertex_index in range(u_array.length()):
        if not use_selected_vertices or vertex_index in selected_vertex_indices:
            mesh_vector = Vector(
                u_array[vertex_index],
                v_array[vertex_index]
            )
            closest_distance = float('inf')
            closest_index = None
            for p in range(len(uvs)):
                difference_vector = mesh_vector - point_vectors[vertex_index]
                distance = difference_vector.norm()
                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = p
            index_map[vertex_index] = closest_index
    return index_map


@dec.m_object_arg
def set_locked_influence_weights(skin_cluster, value):
    for influence in mc.skinCluster(
            gen.get_selection_string(skin_cluster),
            q=True,
            influence=True
    ):
        mc.setAttr(
            '%s.liw' % influence,
            value
        )


@dec.m_object_arg
def reset(skin_cluster):
    skin_cluster_name = gen.get_selection_string(skin_cluster)
    for inf in mc.skinCluster(skin_cluster_name, q=True, influence=True):
        mc.setAttr('%s.liw' % inf)
    mc.setAttr('%s.normalizeWeights' % skin_cluster_name, 0)


@dec.m_object_arg
def set_influence_weights(skin_cluster, index, weights, vertex_map=None, use_selected_vertices=False):
    points = om.MPointArray()
    om.MFnMesh(get_mesh(skin_cluster)).getPoints(points)
    node_functions = om.MFnDependencyNode(skin_cluster)
    influence_weight_plug = node_functions.findPlug(
        node_functions.attribute('weightList'),
        False
    )
    selected_vertex_indices = None
    if use_selected_vertices:
        get_vertex_indices = mtl.get_selected_vertex_indices()
        if get_vertex_indices:
            selected_vertex_indices = get_vertex_indices[0]
    if vertex_map:
        for vertex_index in range(points.length()):
            weights_plug = influence_weight_plug.elementByLogicalIndex(int(vertex_index)).child(0)
            if not selected_vertex_indices or vertex_index in selected_vertex_indices:
                source_index = vertex_map[vertex_index]
                if source_index in weights:
                    weights_plug.elementByLogicalIndex(index).setDouble(weights[source_index])
    else:
        for vertex_index in weights:
            weights_plug = influence_weight_plug.elementByLogicalIndex(int(vertex_index)).child(0)
            if not selected_vertex_indices or vertex_index in selected_vertex_indices:
                weights_plug.elementByLogicalIndex(index).setDouble(weights[vertex_index])


@dec.m_object_arg
def get_components(skin_cluster):
    skin_functions = oma.MFnSkinCluster(skin_cluster)
    deformer_set_functions = om.MFnSet(skin_functions.deformerSet())
    set_members = om.MSelectionList()
    dag_path = om.MDagPath()
    components = om.MObject()
    deformer_set_functions.getMembers(set_members, False)
    if set_members.isEmpty():
        raise Exception('Deformer set was empty. Can not get components')
    set_members.getDagPath(0, dag_path, components)
    return dag_path, components
