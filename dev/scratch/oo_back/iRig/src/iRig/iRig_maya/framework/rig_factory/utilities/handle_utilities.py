
import rig_factory
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.rig_objects.grouped_handle import StandardHandle
from rig_factory.objects.part_objects.container import ContainerGuide, Container
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle

import rig_factory.environment as env
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.base_objects.weak_list import WeakList
#
#
# def create_handles(owner, count, handle_type=None):
#     handles = WeakList()
#     for x in range(count):
#         handles.append(create_handle(
#             owner,
#             handle_type=handle_type
#         ))
#     return handles


def create_part_handle(part, handle_type, **kwargs):
    controller = part.controller
    owner = part
    if isinstance(part.owner, BasePart):  # Special case for nested parts
        kwargs.setdefault('root_name', part.root_name)
        kwargs.setdefault('size', part.size)
        kwargs.setdefault('side', part.side)
        kwargs.setdefault('parent', part)
        owner = part.owner

    this = owner.create_child(
        handle_type,
        **kwargs
    )
    controller.start_ownership_signal.emit(this, owner)
    this.owner = owner
    this.owner.handles.append(this)
    controller.end_ownership_signal.emit(this, owner)
    if part != owner:
        part.handles.append(this)
    return this


def create_standard_handle(part, **kwargs):
    handle_type = kwargs.pop(
        'handle_type',
        StandardHandle
    )
    return create_part_handle(part, handle_type, **kwargs)


def create_guide_handle(part, **kwargs):
    handle_type = kwargs.pop(
        'handle_type',
        GuideHandle
    )
    return create_part_handle(part, handle_type, **kwargs)


def expand_handle_shapes(controller, rig):
    top_group = controller.create_object(
        Transform,
        parent=rig,
        root_name='%s_expanded_handles' % rig.root_name
    )
    #try:
    #    rig.settings_handle.plugs['geometry_display'].set_value(1)
    #except:
    #    pass
    rig.expanded_handles_group = top_group
    expanded_handles = []
    for handle in rig.get_handles():
        handle.plugs['overrideEnabled'].set_value(1)
        handle.plugs['overrideVisibility'].set_value(False)
        shape_matrix_plug = handle.plugs['shape_matrix']
        expanded_group = top_group.create_child(
            Transform,
            root_name='%s_expanded_group' % handle.root_name,
            index=handle.index,
            side=handle.side,
            parent=top_group,
            matrix=list(handle.get_matrix())
        )
        expanded_handle = expanded_group.create_child(
            CurveHandle,
            root_name='%s_expanded' % handle.root_name,
            shape=handle.shape,
            matrix=list(handle.get_matrix()),
            axis=handle.axis
        )
        expanded_handles.append(expanded_handle)
        expanded_handle.plugs['overrideEnabled'].set_value(True)
        expanded_handle.plugs['overrideRGBColors'].set_value(1)
        expanded_handle.plugs['overrideColorRGB'].set_value([0.6, 0.2, 0.9])
        expanded_handle.set_matrix(
            shape_matrix_plug.get_value(Matrix().data),
            world_space=False
        )
        expanded_handle.plugs['matrix'].connect_to(shape_matrix_plug)
    controller.root.expanded_handles = expanded_handles


def collapse_handle_shapes(controller, rig):
    #try:
    #    rig.settings_handle.plugs['geometry_display'].set_value(0)
    #except:
    #    pass
    for handle in rig.get_handles():
        handle.plugs['overrideEnabled'].set_value(1)
        handle.plugs['overrideVisibility'].set_value(True)
    if rig.expanded_handles_group:
        controller.delete_objects(WeakList([rig.expanded_handles_group]))


def snap_handles_to_mesh_positons(rig):
    if isinstance(rig, (ContainerGuide, PartGroupGuide)):
        for handle in rig.get_handles():
            snap_handle_to_mesh_positons(handle)
    else:
        raise Exception('Invalid handle type "%s" for snap_handles_to_mesh_positons' % type(rig))


def snap_handle_to_mesh_positons(handle):
    if isinstance(handle, GuideHandle):
        controller = handle.controller
        vertices = handle.vertices
        if vertices:
            position = controller.scene.get_bounding_box_center(vertices)
            controller.xform(handle, ws=True, t=position)
            #handle.plugs['translate'].set_value(position)
    else:
        raise Exception('Invalid handle type "%s" for snap_handle_to_selected_verts' % type(handle))


def assign_vertices(controller, handle, vertices):
    if isinstance(handle, GuideHandle):
        if vertices:
            handle.vertices = vertices
            position = controller.scene.get_bounding_box_center(*vertices)
            handle.plugs['translate'].set_value(position)
    else:
        raise Exception('Invalid handle type "%s" for snap_handle_to_selected_verts' % type(handle))


def assign_selected_vertices(controller, handle):
    if isinstance(handle, GuideHandle):
        controller.scene.convert_selection(toVertex=True)
        selected_vertices = controller.scene.list_selected_vertices()
        if not selected_vertices:
            raise Exception('No mesh components selected.')
        mesh_names = controller.scene.get_selected_mesh_names()
        if len(mesh_names) != 1:
            raise Exception('Select one mesh')
        vertex_indices = controller.scene.get_selected_vertex_indices()
        body = handle.owner.get_root()
        vertices = []
        for i in range(len(mesh_names)):
            mesh_name = mesh_names[i]
            if mesh_name not in body.geometry:
                print 'Warning: The mesh name "%s" is not part of the rig' % mesh_name
            else:
                mesh = body.geometry[mesh_name]
                vertices.extend([mesh.get_vertex(x) for x in vertex_indices[i]])
        if vertices:
            handle.vertices = vertices
        if selected_vertices:
            controller.xform(
                handle,
                ws=True,
                t=controller.scene.get_bounding_box_center(*selected_vertices)
            )
    else:
        raise Exception('Invalid handle type "%s" for snap_handle_to_selected_verts' % type(handle))


def snap_part_to_mesh(part, mesh_name):
    controller = part.controller
    similar_mesh = controller.find_similar_mesh(mesh_name)
    if not similar_mesh:
        raise Exception('Invalid mesh: %s' % mesh_name)
    for handle in get_handles(part):
        if handle.vertices:
            vertex_strings = []
            for x in handle.vertices:
                if x.mesh == similar_mesh:
                    vertex_strings.append('%s.vtx[%s]' % (mesh_name, x.index))
            if vertex_strings:
                position = controller.scene.get_bounding_box_center(*vertex_strings)
                controller.xform(handle, t=position, ws=True)
        else:
            print 'Handle "%s" had no vertices ' % handle

def assign_closest_vertices(part, mesh_name):
    controller = part.controller
    root = controller.root
    if not root:
        raise Exception('Root node not found')
    if mesh_name in root.geometry:
        mesh = root.geometry[mesh_name]
        for handle in part.get_handles():
            index = controller.get_closest_vertex_index(
                mesh,
                handle.get_matrix().get_translation()
            )
            handle.snap_to_vertices([mesh.get_vertex(index)])
    else:
        raise Exception('Invalid mesh: %s ' % mesh_name)


def snap_part_to_selected_mesh(part):
    controller = part.controller
    mesh_names = controller.get_selected_mesh_names()
    for mesh_name in mesh_names:
        snap_part_to_mesh(part, mesh_name)


def set_handle_mesh_positions(controller, part, positions):
    handle_map = dict((handle.name, handle) for handle in part.get_handles())
    for handle_name in positions:
        if handle_name in handle_map:
            vertices = []
            for mesh_name, vertex_index in positions[handle_name]:
                if mesh_name in part.get_root().geometry:
                    mesh = part.get_root().geometry[mesh_name]
                    vertices.append(mesh.get_vertex(vertex_index))
            controller.snap_handle_to_vertices(
                handle_map[handle_name],
                vertices
            )


def get_handles(item):
    if isinstance(item, BaseContainer):
        handles = WeakList()
        for h in item.handles:
            handles.append(h)
            if isinstance(h, GimbalHandle):
                handles.append(h.gimbal_handle)
        for sub_part in item.parts:
            handles.extend(get_handles(sub_part))
        return handles
    elif isinstance(item, BasePart):
        handles = WeakList()
        for h in item.handles:
            handles.append(h)
            if isinstance(h, GimbalHandle):
                handles.append(h.gimbal_handle)
        return handles
    else:
        raise Exception('Invalid type "%s" for get_handles' % type(item))


def get_joints(item):
    if isinstance(item, BaseContainer):
        joints = WeakList(item.joints)
        for sub_part in item.parts:
            joints.extend(get_joints(sub_part))
        return joints
    elif isinstance(item, BasePart):
        return item.joints
    else:
        raise Exception('Invalid type "%s" for get_joints' % type(item))


def get_deform_joints(item):
    if isinstance(item, BaseContainer):
        joints = WeakList(item.deform_joints)
        for sub_part in item.parts:
            joints.extend(get_deform_joints(sub_part))
        return joints
    elif isinstance(item, BasePart):
        return item.deform_joints
    else:
        raise Exception('Invalid type "%s" for get_joints' % type(item))


def get_handle_mesh_positions(controller, rig):
    mesh_positions = dict()
    for handle in rig.get_handles():
        if hasattr(handle, 'vertices') and handle.vertices:
            mesh_positions[handle.name] = [(x.mesh.get_selection_string(), x.index) for x in handle.vertices]
    return mesh_positions


def get_handle_data(rig):
    data = []
    for handle in rig.get_handles():
        handle_data = dict(
            vertices=[str(x) for x in handle.vertices],
            root_name=handle.root_name,
            side=handle.side,
            index=handle.index,
            size=handle.size,
            selection_string=handle.get_selection_string()
        )
        data.append(handle_data)
    return data


def mirror_handle_positions(rigs, side='left'):
    all_handles = dict((x.name, x) for x in rigs[0].controller.root.get_handles())
    for rig in rigs:
        if not isinstance(rig, (BaseContainer, BasePart)):
            raise Exception('Invalid type "%s"' % type(rig))
        if side not in env.side_mirror_dictionary:
            raise Exception('Invalid side "%s"' % side)
        for handle in rig.get_handles():
            if handle.side == side:
                mirror_handle_name = handle.name.replace(
                    '%s_' % rig_factory.settings_data['side_prefixes'][side],
                    '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[side]]
                )
                if mirror_handle_name in all_handles:
                    mirror_handle = all_handles[mirror_handle_name]
                    matrix = handle.get_matrix()
                    translate = list(matrix.get_translation())
                    translate[0] = translate[0] * -1
                    matrix.set_translation(translate)
                    mirror_handle.set_matrix(matrix)


def mirror_handle_vertices(rigs, side='left'):
    controller = rigs[0].controller

    all_handles = dict((x.name, x) for x in controller.root.get_handles())
    for rig in rigs:
        if not isinstance(rig, (BaseContainer, BasePart)):
            raise Exception('Invalid type "%s"' % type(rig))
        if side not in env.side_mirror_dictionary:
            raise Exception('Invalid side "%s"' % side)
    if side not in env.side_mirror_dictionary:
        raise Exception('Invalid side "%s"' % side)
    for handle in rig.get_handles():
        if handle.side == side:
            mirror_handle_name = handle.name.replace(
                '%s_' % rig_factory.settings_data['side_prefixes'][side],
                '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[side]]
            )
            if mirror_handle_name in all_handles:
                mirror_handle = all_handles[mirror_handle_name]
                mirror_vertices = []
                for vertex in handle.vertices:
                    position = controller.xform(vertex, ws=True, t=True, q=True)
                    position[0] = position[0] * -1
                    mirror_index = controller.get_closest_vertex_index(
                        vertex.mesh,
                        position,
                    )
                    mirror_vertex = vertex.mesh.get_vertex(mirror_index)
                    mirror_vertices.append(mirror_vertex)
                assign_vertices(controller, mirror_handle, mirror_vertices)

def transfer_handle_vertices(rig, mesh, side='left'):
    controller = rig.controller
    for handle in rig.get_handles():
        new_vertices = []
        for vertex in handle.vertices:
            position = controller.xform(vertex, ws=True, t=True, q=True)
            mirror_index = controller.get_closest_vertex_index(
                mesh,
                position,
            )
            mirror_vertex = mesh.get_vertex(mirror_index)
            new_vertices.append(mirror_vertex)
        assign_vertices(controller, handle, new_vertices)


def get_handle_shapes(rig):
    handle_shapes = dict()
    for handle in rig.get_handles():
        handle_shapes[handle.name] = [
            handle.shape,
            handle.plugs['shape_matrix'].get_value(Matrix().data)
        ]
    return handle_shapes


def set_handle_shapes(rig, shapes):
    """
    Reads handle shape data of both the old and new format
    Old: SHAPE_MATRIX
    New: (SHAPE_NAME, SHAPE_MATRIX)
    """
    if shapes:
        handle_map = {handle.name: handle for handle in rig.get_handles()}
        for handle_name, handle_data in shapes.items():
            if handle_name in handle_map:
                item = handle_map[handle_name]
                if len(handle_data) == 2:
                    shape, matrix = handle_data
                    item.set_shape(shape)
                    item.plugs['shape_matrix'].set_value(matrix)
                else:
                    item.plugs['shape_matrix'].set_value(handle_data)
    rig.custom_handles = True


def strs_to_handles_list(controller, str_sel_list):
    '''
    Convert maya strings list to framework node_objects
    :param controller: Rigging framework controller obj
    :param str_sel_list: list(str) List of string names to convert.
    :return: list() List of framework node_objects.
    '''
    handles = []
    for obj_str in str_sel_list:
        if obj_str in controller.named_objects.keys():
            handles.append(controller.named_objects[obj_str])
    return handles


def get_mirror_handles(handles):
    '''
    Get the mirrored side's object. Objects which were not able to find its symmetrical object will be filtered and
    not be returned.
    :param handles: list(), list of framework node_objects
    :return: 2 list(), Lists of the handles and their existing symmetrical handles. These two lists are
    parallel to each other.
    '''
    rev_handles = []
    org_handles = []
    all_handles = dict((x.name, x) for x in handles[0].controller.root.expanded_handles)
    for handle in handles:
        if handle.side != 'center':
            mirror_handle_name = handle.name.replace(
                '%s_' % rig_factory.settings_data['side_prefixes'][handle.side],
                '%s_' % rig_factory.settings_data['side_prefixes'][env.side_mirror_dictionary[handle.side]]
            )
            if mirror_handle_name in all_handles.keys():
                rev_handles.append(all_handles[mirror_handle_name])
                org_handles.append(handle)
    return org_handles, rev_handles


def symmetry_constrain_handle_shapes(org_handles, obj_handles):
    '''
    Apply symmetryConstraint on handles to its symmetrical side. The two arguments should work in parallel of each
    other, use the get_mirror_handles function. Joints will be created, as the symmetryConstraint has a 'joint orient'
    attr that is required for it to work properly with rotations, and then node_objects will be then constrained to the
    joint.
    :param org_handles: The parents of the list of handles.
    :param obj_handles: The children of the list of handles.
    :return: 2 lists(), The parent joints which were generated, and the symmetrical joints that were generated.
    '''
    org_jnts = []
    rev_jnts = []
    for org, rev in zip(org_handles, obj_handles):
        org_jnt, rev_jnt = symmetry_constrain_handle_shape(org, rev)
        org_jnts.append(org_jnt)
        rev_jnts.append(rev_jnt)
    return org_jnts, rev_jnts


def symmetry_constrain_handle_shape(org, rev):
    '''
    symmetryConstraint on handles to its symmetrical side. The two arguments should work in parallel of each
    other, use the get_mirror_handles function. Joints will be created, as the symmetryConstraint has a 'joint orient'
    attr that is required for it to work properly with rotations, and then node_objects will be then constrained to the
    joint.
    :param org: The parent handle.
    :param rev: The child handle.
    :return: 2 type(Joint), The parent joint which were generated, and the symmetrical joint that was generated.
    '''
    root = org.controller.root
    org_jnt = root.utilities_group.create_child(Joint, root_name='{0}_org'.format(org.root_name),
                                                matrix=org.get_matrix(), side=org.side, index=org.index)
    rev_jnt = root.utilities_group.create_child(Joint, root_name='{0}_rev'.format(org.root_name),
                                                matrix=rev.get_matrix(), side=rev.side, index=rev.index)

    org.controller.create_parent_constraint(org, org_jnt)
    rev.controller.create_parent_constraint(rev_jnt, rev)

    sym_cnst = rev.create_child(DagNode, node_type='symmetryConstraint',
                                root_name='{0}_symmetryConstraint'.format(rev.root_name))

    org_jnt.plugs['translate'].connect_to(sym_cnst.plugs['targetTranslate'])
    org_jnt.plugs['rotate'].connect_to(sym_cnst.plugs['targetRotate'])
    org_jnt.plugs['scale'].connect_to(sym_cnst.plugs['targetScale'])
    org_jnt.plugs['parentMatrix'].element(0).connect_to(sym_cnst.plugs['targetParentMatrix'])
    org_jnt.plugs['worldMatrix'].element(0).connect_to(sym_cnst.plugs['targetWorldMatrix'])
    org_jnt.plugs['rotateOrder'].connect_to(sym_cnst.plugs['targetRotateOrder'])
    org_jnt.plugs['jointOrient'].connect_to(sym_cnst.plugs['targetJointOrient'])

    sym_cnst.plugs['constraintTranslate'].connect_to(rev_jnt.plugs['translate'])
    sym_cnst.plugs['constraintRotate'].connect_to(rev_jnt.plugs['rotate'])
    sym_cnst.plugs['constraintScale'].connect_to(rev_jnt.plugs['scale'])
    sym_cnst.plugs['constraintRotateOrder'].connect_to(rev_jnt.plugs['rotateOrder'])
    sym_cnst.plugs['constraintJointOrient'].connect_to(rev_jnt.plugs['jointOrient'])

    rev_jnt.plugs['parentInverseMatrix'].element(0).connect_to(sym_cnst.plugs['constraintInverseParentWorldMatrix'])

    for jnt in [org_jnt, rev_jnt]:
        jnt.plugs['v'].set_value(0)

    for axis in ('scaleX', 'scaleY', 'scaleZ'):
        org.plugs[axis].connect_to(rev.plugs[axis])

    return org_jnt, rev_jnt


def apply_symmetry_constraint_on_selected_shape_handles(controller):
    '''
    Apply symmetry constraint on selected shape handles. It's in the name of the function... silly.
    :param controller: rig controller
    :return: 2 lists(), of the generated lists
    '''
    handles = strs_to_handles_list(controller, controller.scene.ls(sl=True))
    org_handles, rev_handles = get_mirror_handles(handles)
    org_jnts, rev_jnts = symmetry_constrain_handle_shapes(org_handles, rev_handles)
    return org_jnts, rev_jnts
