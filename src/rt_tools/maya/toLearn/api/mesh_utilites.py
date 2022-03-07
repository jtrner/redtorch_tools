import maya.cmds as mc
import decorators as dec
import maya.OpenMaya as om
import os
from rig_math.vector import Vector


@dec.m_object_arg
def get_closest_mesh_uv(mesh, position):
    position = om.MPoint(
        position[0],
        position[1],
        position[2]
    )
    face_index = get_closest_face_index(mesh, position)
    dag_path = om.MDagPath.getAPathTo(mesh)
    mesh_functions = om.MFnMesh(dag_path)

    u_util = om.MScriptUtil()
    u_util.createFromDouble(0.0)
    u_pointer = u_util.asFloatPtr()

    v_util = om.MScriptUtil()
    v_util.createFromDouble(0.0)
    v_pointer = v_util.asFloatPtr()

    mesh_functions.getPolygonUV(
        face_index,
        0,
        u_pointer,
        v_pointer
    )

    u = u_util.getFloatArrayItem(u_pointer, 0)
    v = v_util.getFloatArrayItem(v_pointer, 0)

    return u, v


@dec.m_object_arg
def get_closest_face_index(mesh, position):
    dag_path = om.MDagPath.getAPathTo(mesh)
    mesh_functions = om.MFnMesh(dag_path)
    point_a = om.MPoint(
        position[0],
        position[1],
        position[2]
    )
    point_b = om.MPoint()
    space = om.MSpace.kWorld
    script_util = om.MScriptUtil()
    script_util.createFromInt(0)
    id_pointer = script_util.asIntPtr()
    mesh_functions.getClosestPoint(
        point_a,
        point_b,
        space,
        id_pointer
    )
    index = om.MScriptUtil(id_pointer).asInt()
    return index


def get_meshs(node_name):
    if mc.nodeType(node_name) == 'transform':
        meshs = mc.listRelatives(node_name, c=True, type='mesh')
        if meshs:
            return meshs
    return []


def create_shard_mesh(mesh_name, parent_m_object):
    shard_size = 0.0025
    mesh_functions = om.MFnMesh()
    num_polygons = 4
    num_vertices = 4
    vertex_array = om.MFloatPointArray()
    vertex_array.append(om.MFloatPoint(0.0, 0.0, 0.0))
    vertex_array.append(om.MFloatPoint(shard_size, 0.0, 0.0))
    vertex_array.append(om.MFloatPoint(0.0, shard_size, 0.0))
    vertex_array.append(om.MFloatPoint(0.0, 0.0, shard_size))
    polygon_counts = om.MIntArray()
    polygon_counts.append(3)
    polygon_counts.append(3)
    polygon_counts.append(3)
    polygon_counts.append(3)
    poly_connections = om.MIntArray()
    poly_connections.append(0)
    poly_connections.append(2)
    poly_connections.append(1)
    poly_connections.append(0)
    poly_connections.append(3)
    poly_connections.append(2)
    poly_connections.append(3)
    poly_connections.append(1)
    poly_connections.append(2)
    poly_connections.append(3)
    poly_connections.append(0)
    poly_connections.append(2)
    m_object = mesh_functions.create(
        num_vertices,
        num_polygons,
        vertex_array,
        polygon_counts,
        poly_connections,
        parent_m_object
    )
    selection_string = get_selection_string(m_object)
    mc.rename(selection_string, mesh_name)

    return m_object


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


def get_m_object(node_name):
    selection_list = om.MSelectionList()
    selection_list.add(node_name)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


def get_selected_mesh_objects(include_intermediate=False):
    mesh_objects = []
    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    for i in range(selection_list.length()):
        m_object = om.MObject()
        selection_list.getDependNode(i, m_object)
        mesh_objects.extend(get_mesh_objects(
            m_object,
            include_intermediate=include_intermediate
        ))
    return list(set(mesh_objects))


def get_selected_mesh_names(**kwargs):
    return [get_selection_string(x) for x in get_selected_mesh_objects(**kwargs)]


@dec.m_object_arg
def get_mesh_objects(object, include_intermediate=False):

    mesh_objects = []
    dependency_node = om.MFnDependencyNode(object)
    node_type = str(dependency_node.typeName())
    if node_type == 'mesh':
        node_functions = om.MFnDependencyNode(object)
        m_attribute = node_functions.attribute('intermediateObject')
        m_plug = node_functions.findPlug(m_attribute, False)
        if include_intermediate or not m_plug.asBool():
            mesh_objects.append(object)
    elif node_type in ('transform', 'joint'):
        dag_path = om.MDagPath.getAPathTo(object)
        dag_functions = om.MFnDagNode(dag_path)
        for c in range(dag_functions.childCount()):
            mesh_objects.extend(get_mesh_objects(dag_functions.child(c)))
    return mesh_objects



@dec.m_object_arg
def get_closest_vertex_index(mesh, point):
    """
    :param mesh: MObject
    :param point: MPoint
    :return: int  Vertex index
    """
    dag_path = om.MDagPath.getAPathTo(mesh)
    component = om.MObject()
    vertex_iterator = om.MItMeshVertex(dag_path, component)
    closest_distance = float('inf')
    closest_index = None
    while not vertex_iterator.isDone():
        d = vertex_iterator.position().distanceTo(point)
        if d < closest_distance:
            closest_distance = d
            closest_index = vertex_iterator.index()
        vertex_iterator.next()
    return closest_index


@dec.m_object_arg
def get_closest_vertex_uv(mesh, point):
    """
    :param mesh: MObject
    :param point: MPoint
    :return: int  Vertex index
    """
    dag_path = om.MDagPath.getAPathTo(mesh)
    component = om.MObject()
    vertex_iterator = om.MItMeshVertex(dag_path, component)
    closest_distance = float('inf')
    closest_uv = [None, None]
    while not vertex_iterator.isDone():
        d = vertex_iterator.position().distanceTo(point)
        if d < closest_distance:
            closest_distance = d
            uv_util = om.MScriptUtil()
            uv_util.createFromList(closest_uv, 2)
            uvPoint = uv_util.asFloat2Ptr()
            vertex_iterator.getUV(uvPoint)
            closest_uv[1] = uv_util.getFloat2ArrayItem(uvPoint, 0, 1)
            closest_uv[0] = uv_util.getFloat2ArrayItem(uvPoint, 0, 0)
        vertex_iterator.next()
    return closest_uv


@dec.m_dag_path_arg
def get_vertex_count(mesh):
    return om.MItMeshVertex(mesh, om.MObject()).count()


def get_bounding_box_center(*nodes):
    bbox = mc.exactWorldBoundingBox(*nodes)
    center_x = (bbox[0] + bbox[3]) / 2.0
    center_y = (bbox[1] + bbox[4]) / 2.0
    center_z = (bbox[2] + bbox[5]) / 2.0
    return round(center_x, 5), round(center_y, 5), round(center_z, 5)


def find_opposite_mesh(meshs, target_mesh, threshold=0.01):
    assert mc.nodeType(target_mesh) == 'mesh'
    assert all([mc.nodeType(x) == 'mesh' for x in meshs])
    vertex_count = get_vertex_count(target_mesh)
    matching_meshs = []
    for mesh in meshs:
        if get_vertex_count(mesh) == vertex_count:
            matching_meshs.append(mesh)
    if len(matching_meshs) == 0:
        return None

    bounding_box_center = Vector(get_bounding_box_center(target_mesh))
    transform = mc.listRelatives(target_mesh, p=True)[0]
    transform_position = Vector(mc.xform(transform, q=True, ws=True, t=True))
    local_position = bounding_box_center - transform_position
    for matching_mesh in matching_meshs:
        if matching_mesh != target_mesh:
            matching_bounding_box_center = Vector(get_bounding_box_center(matching_mesh))
            if abs(matching_bounding_box_center.data[0]) > threshold:
                matching_transform = mc.listRelatives(matching_mesh, p=True)[0]
                matching_transform_position = Vector(mc.xform(matching_transform, q=True, ws=True, t=True))
                matching_local_position = matching_bounding_box_center - matching_transform_position
                if not matching_local_position[0] * local_position[0] > 0.0:
                    return matching_mesh


def get_mirror_index_list(base_mesh, target_mesh=None):
    '''
    Generates a list of the vtx index numbers of the corresponding side (x axis). Parallel to the list's index number of
    the base_mesh.
    It can do this either on itself or another mesh (target_mesh) with a completely different vertex count.
    :param base_mesh: str(), Base mesh name.
    :param target_mesh: str(), Target mesh name.
    :return: list()
    '''
    if not target_mesh:
        target_mesh = base_mesh

    src_vtx_count = mc.polyEvaluate(base_mesh, v=True)
    tar_vtx_count = mc.polyEvaluate(target_mesh, v=True)

    src_vtx_positions = [mc.pointPosition('{0}.vtx[{1}]'.format(base_mesh, i), local=True) for i in range(src_vtx_count)]
    tar_vtx_positions = [mc.pointPosition('{0}.vtx[{1}]'.format(target_mesh, i), local=True) for i in range(tar_vtx_count)]

    mirrored_index_list = []
    for i in range(tar_vtx_count):
        mirrored_position = [tar_vtx_positions[i][0] * -1, tar_vtx_positions[i][1], tar_vtx_positions[i][2]]  # What the flipped x axis would be
        closest_distance = 100000.0  # start off with a ridiculously high number as the closest distance
        closest_vtx = None
        for j in range(src_vtx_count):
            # distance from the vtx to the mirrored position
            distance = sum([abs(mirror - looking) for mirror, looking in zip(mirrored_position, src_vtx_positions[j])])
            if distance < closest_distance:
                closest_vtx = j
                closest_distance = distance
        mirrored_index_list.append(closest_vtx)

    return mirrored_index_list


def get_closest_index_list(base_mesh, target_mesh, world_space=True):
    src_vtx_count = mc.polyEvaluate(base_mesh, v=True)
    tar_vtx_count = mc.polyEvaluate(target_mesh, v=True)

    src_vtx_positions = [mc.pointPosition('{0}.vtx[{1}]'.format(base_mesh, i), l=not world_space, w=world_space) for i in range(src_vtx_count)]
    tar_vtx_positions = [mc.pointPosition('{0}.vtx[{1}]'.format(target_mesh, i), l=not world_space, w=world_space) for i in range(tar_vtx_count)]

    index_list = []
    for i in range(tar_vtx_count):
        closest_distance = 100000.0  # start off with a ridiculously high number as the closest distance
        closest_vtx = None
        for j in range(src_vtx_count):
            # distance from the vtx to the mirrored position
            distance = sum([abs(mirror - looking) for mirror, looking in zip(tar_vtx_positions[i], src_vtx_positions[j])])
            if distance < closest_distance:
                closest_vtx = j
                closest_distance = distance
        index_list.append(closest_vtx)

    return index_list


def get_reverse_index_lists(base_meshs):
    reverse_index_lists = []
    mirror_mesh_dict = dict((x, find_opposite_mesh(base_meshs, x)) for x in base_meshs)
    for base_mesh in base_meshs:
        reverse_indices = dict()
        vertex_count = get_vertex_count(base_mesh)
        source_positions = []
        destination_positions = []
        for i in range(vertex_count):
            point = mc.pointPosition(
                '{0}.vtx[{1}]'.format(base_mesh, i),
                l=True
            )
            source_positions.append(point)
        mirror_mesh = mirror_mesh_dict.get(base_mesh, None)
        if mirror_mesh:
            for i in range(vertex_count):
                point = mc.pointPosition(
                    '{0}.vtx[{1}]'.format(mirror_mesh, i),
                    l=True
                )
                destination_positions.append(point)
        else:
            destination_positions = source_positions
        for i in range(vertex_count):
            closest_distance = 100000.0
            closest_index = None
            mirror_position = (source_positions[i][0] * -1, source_positions[i][1], source_positions[i][2])
            for j in range(vertex_count):
                xpos = mirror_position[0] - (destination_positions[j][0])
                ypos = mirror_position[1] - (destination_positions[j][1])
                zpos = mirror_position[2] - (destination_positions[j][2])
                total = abs(xpos) + abs(ypos) + abs(zpos)
                if total < closest_distance:
                    closest_index = j
                    closest_distance = total
            reverse_indices[i] = closest_index
        reverse_index_lists.append(reverse_indices)
    return reverse_index_lists


def create_mirrored_geometry(target_meshs, base_meshs, reverse_index_lists=None):
    mirror_mesh_dict = dict((x, find_opposite_mesh(target_meshs, x)) for x in target_meshs)
    if reverse_index_lists is None:
        reverse_index_lists = get_reverse_index_lists(*base_meshs)
    temp_meshs = []
    for m, mesh in enumerate(target_meshs):
        mirror_mesh = mirror_mesh_dict[mesh]
        target_mesh = mesh
        if mirror_mesh:
            target_mesh = mirror_mesh
        reverse_index_list = reverse_index_lists[m]
        transform_name = mc.listRelatives(mesh, p=True)[0]
        new_transform = mc.createNode(
            'transform',
            name='%s_duplicate' % transform_name
        )
        transform_m_object = get_m_object(new_transform)
        new_mesh_m_object = om.MFnMesh().copy(get_m_object(target_mesh), transform_m_object)
        new_mesh = get_selection_string(new_mesh_m_object)
        for index in reverse_index_list:
            mirror_index = reverse_index_list[index]
            position = mc.xform(
                '{0}.vtx[{1}]'.format(
                    mesh,
                    index
                ),
                q=True,
                ws=False,
                t=True
            )

            mc.xform(
                '{0}.vtx[{1}]'.format(
                    new_mesh,
                    mirror_index
                ),
                os=True,
                t=(position[0] * -1, position[1], position[2])
            )
        temp_meshs.append(new_transform)
    return temp_meshs


def find_similar_mesh(mesh, *other_meshs):
    """
    :param mesh: MObject
    :param other_meshs: MObject (tuple))
    :return: MObject or None
    """
    vertex_count = get_vertex_count(mesh)
    matching_meshs = []
    for other_mesh in other_meshs:
        if get_vertex_count(other_mesh) == vertex_count:
            matching_meshs.append(other_mesh)
    if len(matching_meshs) == 0:
        return None
    if len(matching_meshs) == 1:
        return matching_meshs[0]
    mesh_name = get_selection_string(mesh)
    bounding_box_center = Vector(get_bounding_box_center(mesh_name))
    transform = mc.listRelatives(mesh_name, p=True)[0]
    transform_position = Vector(mc.xform(
        transform,
        q=True,
        ws=True,
        t=True
    ))
    local_position = bounding_box_center - transform_position
    closest_mesh = None
    closest_distance = float('inf')
    for matching_mesh in matching_meshs:
        matching_mesh_name = get_selection_string(matching_mesh)
        matching_bounding_box_center = Vector(get_bounding_box_center(matching_mesh_name))
        matching_transform = mc.listRelatives(matching_mesh_name, p=True)[0]
        matching_transform_position = Vector(mc.xform(
            matching_transform,
            q=True,
            ws=True,
            t=True
        ))
        matching_local_position = matching_bounding_box_center - matching_transform_position
        if not matching_local_position[0] * local_position[0] < 0.0:
            distance_vector = Vector(matching_local_position) - local_position
            if distance_vector.magnitude() == 0:
                return matching_mesh
            x_distance = abs(distance_vector.data[0])
            if x_distance < closest_distance:
                closest_distance = x_distance
                closest_mesh = matching_mesh
    return closest_mesh


def create_corrective_geometry(base_shapes, shapes, corrective_shapes):
    base_shape_m_objects = [get_m_object(x) for x in base_shapes]
    shape_m_objects = [get_m_object(x) for x in shapes]

    parent_transforms = []
    for corrective_shape in corrective_shapes:
        corrective_shape_m_object = get_m_object(corrective_shape)
        base_shape_m_object = find_similar_mesh(corrective_shape_m_object, *base_shape_m_objects)
        shape_m_object = find_similar_mesh(corrective_shape_m_object, *shape_m_objects)
        shape_name = get_selection_string(shape_m_object)
        if base_shape_m_object and shape_m_object:
            parent_transform = om.MFnDagNode().create(
                'transform',
                '%s_difference' % shape_name
            )
            difference_mesh_m_object = om.MFnMesh().copy(
                base_shape_m_object,
                parent_transform
            )
            difference_mesh_mesh_name = get_selection_string(difference_mesh_m_object)
            blendshape = mc.blendShape(
                shape_name,
                corrective_shape,
                difference_mesh_mesh_name
            )[0]
            mc.setAttr('%s.w[0]' % blendshape, -1.0)
            mc.setAttr('%s.w[1]' % blendshape, 1.0)
            mc.delete(difference_mesh_mesh_name, ch=True)
            parent_transforms.append(get_selection_string(parent_transform))

    return parent_transforms


def get_selected_vertex_indices(*meshs):

    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    vertices = []
    if selection_list.length():
        for i in range(selection_list.length()):
            m_object = om.MObject()
            selection_list.getDependNode(i, m_object)
            if m_object.hasFn(om.MFn.kDagNode):
                component_m_object = om.MObject()
                dag_path = om.MDagPath()
                selection_list.getDagPath(i, dag_path, component_m_object)
                if dag_path and not component_m_object.isNull():
                    dag_functions = om.MFnDagNode(dag_path)
                    if str(dag_functions.typeName()) == 'mesh':
                        object_vertices = []
                        mesh_iterator = om.MItMeshVertex(dag_path, component_m_object)
                        while not mesh_iterator.isDone():
                            object_vertices.append(int(mesh_iterator.index()))
                            mesh_iterator.next()
                        vertices.append(object_vertices)
    return vertices


def import_alembic(path, name_space):
    if not mc.namespace(exists=':%s' % name_space):
        mc.namespace(add=name_space)
    mc.namespace(set=name_space)
    if not os.path.exists(path):
        raise IOError('Geometry file does not exist: %s' % path)
    mc.loadPlugin('AbcImport')
    mc.AbcImport(
        path,
        mode='import'
    )
    mc.namespace(set=':')


def update_mesh_deltas(mesh_names, original_alembic_path, delta_alembic_path):

    """
    inserts closed eye shape before build

    @param mesh_names:
    @param origional_alembic_path:
    @param delta_alembic_path:
    @return:
    """

    import_alembic(original_alembic_path, 'original_geometry')
    import_alembic(delta_alembic_path, 'delta_geometry')

    for mesh_name in mesh_names:
        original_mesh = 'original_geometry:%s' % mesh_name
        delta_mesh = 'delta_geometry:%s' % mesh_name

        if mc.objExists(original_mesh) and mc.objExists(delta_mesh):
            blendshape = mc.blendShape(
                original_mesh,
                delta_mesh,
                mesh_name
            )[0]

            mc.setAttr('%s.w[0]' % blendshape, -1.0)
            mc.setAttr('%s.w[1]' % blendshape, 1.0)
            mc.delete(mesh_name, ch=True)
            mc.polyNormalPerVertex(
                mesh_name,
                ufn=True
            )
            mc.polySoftEdge(
                mesh_name,
                angle=180,
                ch=False
            )
    mc.delete(mc.ls('original_geometry:*'))
    mc.delete(mc.ls('delta_geometry:*'))
    if mc.namespace(exists=':%s' % 'original_geometry'):
        mc.namespace(rm='original_geometry', mergeNamespaceWithRoot=True)
    if mc.namespace(exists=':%s' % 'delta_geometry'):
        mc.namespace(rm='delta_geometry', mergeNamespaceWithRoot=True)


def create_poly_extrude_edge(*args, **kwargs):
    poly_extrude_node = mc.polyExtrudeEdge(*args, **kwargs)
    return get_m_object(poly_extrude_node[0])

