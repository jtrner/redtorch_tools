import gc
from rig_factory.objects.face_panel_objects.mouth_slider import MouthSlider
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects import FaceNetwork
import rig_factory.utilities.face_utilities.decorators as dec
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.face_objects.face_handle import FaceHandle
import rig_factory.utilities.node_utilities.name_utilities as nmu
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
import rig_factory.utilities.node_utilities.name_utilities as ntt
from rig_factory.objects.biped_objects.jaw_new import NewJaw
from rig_factory.objects.biped_objects.jaw import Jaw
from rig_math.matrix import Matrix
import time
driven_plug_rounding = 5


def create_from_face_network_data(controller, data, target_namespace=None, selected_handles=False):
    selected = controller.scene.ls(sl=True)
    face_network = controller.face_network
    driven_handles = data['driven_handles']
    if face_network:
        if face_network.face_groups:
            driven_handle_names = [x.name for x in face_network.driven_handles]
            unmatched_handles = [x for x in driven_handles if x not in driven_handle_names]
            if unmatched_handles:
                shortened_unmatched_handles = [unmatched_handles[x] for x in range(len(unmatched_handles)) if x < 10]
                shortened_unmatched_handles.append('...')
                controller.face_warning_signal.emit(
                    'Cannot merge faces with different driven handles \n\n %s' % '\n'.join(
                        shortened_unmatched_handles
                    )
                )
                raise Exception('Mismatched Driven handles in Blueprint. %s' % unmatched_handles)
    geometry_names = data.get('geometry', [])
    geometry = WeakList()
    existing_groups = []
    missing_driver_plugs = []
    missing_driver_nodes = []
    for geometry_name in geometry_names:
        if geometry_name in controller.named_objects:
            geometry.append(controller.named_objects[geometry_name])
        else:
            controller.raise_warning('Could not find geometry "%s"' % geometry_name)
            raise Exception('Could not find geometry "%s"' % geometry_name)
    if not face_network:
        face_network = controller.create_object(
            FaceNetwork,
            root_name=data['root_name'],
            parent=controller.root
        )
        print 'Created face_network : ', face_network
        print 'Added geometry: ', geometry

        if geometry:
            face_network.add_geometry(*geometry)
            assert face_network.blendshape

    driven_attributes = data.get('driven_attributes', None)
    missing_handles = []
    if not face_network.driven_handles:
        for h, handle_name in enumerate(driven_handles):
            handle = controller.named_objects.get(handle_name, None)
            if handle:
                face_network.driven_handles.append(handle)
                if driven_attributes:
                    handle_attributes = driven_attributes[h]
                    if handle_attributes:
                        driven_plugs = controller.initialize_driven_plugs(
                            [handle.groups[face_network.driver_group_index]],
                            handle_attributes
                        )
                        if not face_network.sdk_network:
                            face_network.sdk_network = face_network.create_child(
                                SDKNetwork
                            )
                        face_network.sdk_network.add_driven_plugs(driven_plugs)
                        print 'Added Driven Plugs: %s' % driven_plugs
                print 'Added Handle: "%s"' % handle
            else:
                missing_handles.append(handle_name)
                print 'Warning: Missing handle "%s"' % handle_name

    driven_plugs = WeakList()
    driven_plug_strings = data.get('driven_plugs', None)
    if driven_plug_strings:
        if not face_network.sdk_network:
            face_network.sdk_network = face_network.create_child(
                SDKNetwork
            )
        driven_plug_names = [x.name for x in face_network.sdk_network.driven_plugs]
        for plug_string in driven_plug_strings:
            if plug_string not in driven_plug_names:
                node_name, plug_name = plug_string.split('.')
                if node_name in controller.named_objects:
                    driven_plugs.append(controller.initialize_driven_plug(controller.named_objects[node_name], plug_name))
    if face_network.sdk_network and driven_plugs:
        face_network.sdk_network.add_driven_plugs(driven_plugs)
        print 'Added Driven Plugs: %s' % driven_plugs


    if missing_handles:
        shortened_missing_handles = [missing_handles[x] for x in range(len(missing_handles)) if x < 10]
        shortened_missing_handles.append('...')
        controller.face_warning_signal.emit(
            'Warning:\nSome Driven handles were missing: \n\n%s' % '\n'.join(shortened_missing_handles)
        )
    controller.face_progress_signal.emit(
        message='Creating Groups...',
        value=0,
        maximum=len(data['groups'])
    )
    controller.set_face_network(face_network)
    for group_index, group_data in enumerate(data['groups']):
        group_start = time.time()
        controller.face_progress_signal.emit(
            message=group_data['root_name'],
            value=group_index,
        )
        driver_plug_name = group_data['driver_plug']
        if driver_plug_name is not None and not controller.scene.objExists(driver_plug_name):
            missing_driver_plugs.append(driver_plug_name)
            print 'Driver plug not found "%s".' % driver_plug_name
        else:
            group_name = nmu.create_name_string(
                FaceGroup.__name__,
                root_name=group_data['root_name'],
                side=group_data['side']
            )
            owner_name = group_data.get('owner', None)
            owner = face_network
            if owner_name:
                if owner_name in controller.named_objects:
                    owner = controller.named_objects[owner_name]
            if group_name not in controller.named_objects:
                if driver_plug_name is None:
                    face_group = face_network.create_group(
                        root_name=group_data['root_name'],
                        pretty_name=group_data.get('pretty_name', None),
                        side=group_data['side'],
                        driver_plug=None,
                        create_zero_target=False,
                        owner=owner
                    )
                    print 'Added Face Group: "%s"' % face_group
                else:
                    node_name, plug_name = driver_plug_name.split('.')
                    if not selected_handles or node_name in selected:
                        driver_node = controller.named_objects.get(node_name, None)
                        if not driver_node:
                            print 'Driver node not found "%s".' % node_name
                            missing_driver_nodes.append(node_name)
                        else:
                            driver_plug = driver_node.plugs[plug_name]
                            face_group = face_network.create_group(
                                root_name=group_data['root_name'],
                                side=group_data['side'],
                                driver_plug=driver_plug,
                                owner=owner
                            )
                            print 'Added Face Group: "%s" in %s seconds' % (face_group, (time.time()-group_start))
                            if face_network.blendshape and group_data.get('has_blendshape', False):
                                blendshape_group = face_group.create_blendshape_group()
                                print 'Added Blendshape_group Group: "%s"' % blendshape_group
                            if driver_plug:
                                for target_data in group_data['targets']:
                                    target_start = time.time()

                                    driver_value = round(target_data['driver_value'], 2)
                                    attribute_values = target_data.get('attribute_values', [])
                                    original_values = []
                                    try:
                                        driver_plug.set_value(driver_value)
                                    except Exception, e:
                                        print e.message

                                    for attr, value in attribute_values:
                                        try:
                                            original_values.append(controller.getAttr(attr))
                                            controller.setAttr(attr, value)
                                        except Exception, e:
                                            print e.message

                                    if driver_value != face_group.initial_value:
                                        geometry = []
                                        for x in target_data['mesh_names']:
                                            name_space_mesh_name = '%s:%s' % (target_namespace, x)
                                            list_meshs = controller.scene.ls(name_space_mesh_name, long=True)
                                            if len(list_meshs) > 1:
                                                controller.raise_error('Warning: Duplicate mesh names in alembic file : %s' % name_space_mesh_name)
                                            if list_meshs:
                                                geometry.append(name_space_mesh_name)
                                            else:
                                                print 'Mesh not found %s' % name_space_mesh_name
                                        target_name = nmu.create_name_string(
                                            FaceTarget,
                                            **target_data
                                        )
                                        if target_name in controller.named_objects:
                                            face_target = controller.named_objects[target_name]
                                            update_target_meshs(
                                                face_target,
                                                geometry
                                            )
                                        else:

                                            face_target = face_group.create_face_target(
                                                *geometry,
                                                root_name=target_data['root_name'],
                                                side=face_group.side,
                                                driver_value=driver_value,
                                                set_attr=False,
                                                snap_to_mesh=False
                                            )
                                            print 'Added Face Target: "%s" in %s seconds' % (
                                                face_target,
                                                (time.time() - target_start)
                                            )
                                        tangents = target_data.get('tangents', None)
                                        if tangents and face_target.keyframe_group:
                                            in_tangent, out_tangent = tangents
                                            face_target.keyframe_group.set_keyframe_tangents(in_tangent)

                                    for i in range(len(attribute_values)):
                                        try:
                                            controller.setAttr(attribute_values[i][0], original_values[i])
                                        except Exception, e:
                                            print e.message
                                try:
                                    driver_plug.set_value(face_group.initial_value)
                                except Exception, e:
                                    print e.message
            else:
                print 'Aborted the creation of face group "%s" because of duplicate names' % group_name
                existing_groups.append(group_name)

    if existing_groups:
        shortened_existing_groups = [existing_groups[x] for x in range(len(existing_groups)) if x < 10]
        shortened_existing_groups.append('...')
        controller.face_warning_signal.emit(
            'Some groups were skipped due to duplicate names: \n%s' % '\n'.join(shortened_existing_groups)
        )

    if missing_driver_nodes:
        missing_driver_nodes = [missing_driver_nodes[x] for x in range(len(missing_driver_nodes)) if x < 10]
        missing_driver_nodes.append('...')
        controller.face_warning_signal.emit(
            'Some groups were skipped due to absent driver nodes: \n%s' % '\n'.join(missing_driver_nodes)
        )

    if missing_driver_plugs:
        missing_driver_plugs = [missing_driver_plugs[x] for x in range(len(missing_driver_plugs)) if x < 10]
        missing_driver_plugs.append('...')
        controller.face_warning_signal.emit(
            'Some groups were skipped due to absent driver plugs: \n%s' % '\n'.join(missing_driver_plugs)
        )

    controller.dg_dirty()

    controller.face_progress_signal.emit(
        done=True
    )
    return face_network


@dec.flatten_args
def create_network_from_handles(*handles, **kwargs):

    """
    Create a face network from a Face object using handle sto define driven handles and handle vertices to find base
    geometry.
    """
    geometry = kwargs.pop('geometry', None)

    for handle in handles:
        if not isinstance(handle, CurveHandle):
            raise Exception('%s is not an instances of class: %s' % (handle, CurveHandle.__name__))

    controller = handles[0].controller
    if not controller.root:
        raise Exception('No controller root found.')

    if not geometry:
        geometry = []
        for handle in handles:
            for vertex in handle.vertices:
                geometry.append(vertex.mesh)

    if not geometry:
        print 'Warning ! No handle vertices or face geometry found.'

    kwargs['root_name'] = 'face'
    kwargs['parent'] = controller.root

    geometry = list(set(geometry))
    this = controller.create_object(
        FaceNetwork,
        *geometry,
        **kwargs
    )

    kwargs.pop('index', None)
    this.add_driven_handles(*[x.name for x in handles])
    controller.root.face_shape_network = this
    controller.set_face_network(this)
    return this


def update_target_handles(face_target):
    """
    Updates the face target based on current handle positions
    recalculates the Blendshape target
    """
    if isinstance(face_target, FaceTarget):
        controller = face_target.controller
        face_group = face_target.face_group
        weight_plug = None
        weight_value = 0.0
        if face_group.blendshape_group:
            weight_plug = face_group.blendshape_group.get_weight_plug()
            weight_value = weight_plug.get_value()
        face_network = face_group.face_network
        controller.update_keyframe_group(face_target)
        face_group.driver_plug.set_value(face_target.driver_value)
        controller.isolate_sdk_group(face_group.sdk_group)
        if face_group.blendshape_group:
            for blendshape_group in face_group.blendshape_group.blendshape.blendshape_groups:   # Maybe have an isolate finction on blendshapeGroup object
                if blendshape_group != face_group.blendshape_group:
                    blendshape_group.get_weight_plug().set_value(0.0)
        for g in range(len(face_network.geometry)):
            if face_target.blendshape_inbetween:
                controller.scene.copy_mesh_in_place(
                    face_network.geometry[g].m_object,
                    face_target.target_meshs[g].m_object
                )
                if face_group.blendshape_group:
                    if weight_plug:  # Neciserry ?
                        weight_plug.set_value(0.0)
                face_target.deformed_meshs[g].parent.plugs['v'].set_value(True)  # Neciserry ?
                controller.scene.copy_mesh_in_place(
                    face_network.geometry[g].m_object,
                    face_target.deformed_meshs[g].m_object
                )
                if weight_plug:

                    weight_plug.set_value(weight_value)
                face_target.deformed_meshs[g].parent.plugs['v'].set_value(False)  # Neciserry ?
        controller.dg_dirty()  # Neciserry ?

    else:
        raise Exception('Invalid type "%s"' % type(face_target))


def update_target_selected_mesh(face_target, relative=True):

    mesh_objects = face_target.controller.get_selected_mesh_names()
    if not mesh_objects:
        raise Exception('No valid mesh sdk_objects selected')
    # check for dirty mesh node_objects !!
    update_target_meshs(
        face_target,
        mesh_objects,
        relative=relative
    )


def go_to_target(face_target):
    """
    Set the driver plug of a face group to the driver value of a face target
    """
    if isinstance(face_target, FaceTarget):
        controller = face_target.controller
        if controller.locked_face_drivers:
            attribute_values = face_target.attribute_values
            if attribute_values:
                for attribute_name, value in attribute_values:
                    node_name, plug_name = attribute_name.split('.')
                    node = controller.initialize_node(node_name, parent=None)
                    plug = node.plugs[plug_name]
                    if not controller.scene.listConnections(plug.name, s=True, d=False):
                        plug.set_value(value)
        try:
            face_target.face_group.driver_plug.set_value(face_target.driver_value)
        except Exception, e:
            print e.message
    else:
        raise Exception('Invalid type "%s"' % type(face_target))


def update_target_meshs(face_target, meshs, relative=True):
    """
    Pass mesh node_objects to a face target and update its sdks and blendshapes
    """
    if isinstance(face_target, FaceTarget):
        if face_target.driver_value == 0.0:
            raise Exception('Cannot update target mesh and driver value of 0.0')
        controller = face_target.controller
        face_group = face_target.face_group
        blendshape_group = face_group.blendshape_group
        face_network = face_group.face_network
        blendshape = face_network.blendshape
        face_group.set_weight(0.0)
        mesh_transforms = []
        if relative and meshs:
            mesh_transforms = controller.scene.create_corrective_geometry(
                [x.name for x in face_network.base_geometry],
                [x.name for x in face_network.geometry],
                meshs
            )
            meshs = [controller.scene.listRelatives(x, c=True, type='mesh')[0] for x in mesh_transforms]
        face_group.set_weight(1.0)
        face_network.reset_driver_plugs()

        similar_geometry = dict()
        for input_geo in meshs:
            similar_mesh = controller.find_similar_mesh(
                input_geo,
                geometry=face_network.blendshape.base_geometry
            )
            if similar_mesh:
                similar_geometry[similar_mesh.name] = input_geo
            else:
                raise Exception('Unable to find similar mesh to "%s"' % input_geo)
        go_to_target(face_target)
        for i, base_mesh in enumerate(face_network.geometry):
            if base_mesh.name in similar_geometry:
                input_mesh = similar_geometry[base_mesh.name]
                input_mesh_m_object = controller.scene.get_m_object(input_mesh)
                controller.scene.copy_mesh_in_place(
                    input_mesh_m_object,
                    face_target.target_meshs[i].m_object
                )
                weight_plug = blendshape_group.get_weight_plug()
                weight_value = weight_plug.get_value()
                deform_mesh = face_target.deformed_meshs[i]
                face_network.snap_to_mesh(input_mesh)
                controller.update_keyframe_group(face_target)
                deform_mesh.parent.plugs['visibility'].set_value(True)
                go_to_target(face_target)
                weight_plug.set_value(0.0)
                #controller.refresh()
                controller.scene.copy_mesh_in_place(
                    face_network.geometry[i].m_object,
                    deform_mesh.m_object
                )
                weight_plug.set_value(weight_value)
                deform_mesh.parent.plugs['visibility'].set_value(False)
        if mesh_transforms:
            controller.scene.delete(mesh_transforms)
        face_network.reset_driver_plugs()
        controller.dg_dirty()
    else:
        raise Exception('Invalid type "%s"' % type(face_target))


def get_face_network_data(*args):
    if not args:
        raise Exception('Invalid args: %s' % str(args))
    face_groups = WeakList()
    face_network = None
    for arg in args:
        if isinstance(arg, FaceGroup):
            face_groups.append(arg)
            face_network = arg.face_network

        elif isinstance(arg, FaceNetwork):
            face_network = arg
            face_groups.extend(arg.get_members())
        else:
            raise Exception('invalid object: %s' % arg)
    if face_network:
        controller = face_network.controller

        network_blueprint = dict(
            root_name=face_network.root_name,
            geometry=[x.get_selection_string() for x in face_network.geometry],
            driven_plugs=[x.name for x in face_network.sdk_network.driven_plugs] if face_network.sdk_network else [],
            driven_handles=[x.name for x in face_network.driven_handles] if face_network.sdk_network else []
        )

        controller.face_progress_signal.emit(
            message='Getting Data...',
            value=0,
            maximum=len(face_network.members)
        )

        group_blueprints = []
        for i, face_group in enumerate(face_groups):

            controller.face_progress_signal.emit(
                message='Getting data from "%s"' % face_group.root_name,
                value=i,
            )

            group_blueprint = dict(
                pretty_name=face_group.pretty_name,
                root_name=face_group.root_name,
                index=face_group.index,
                side=face_group.side,
                driver_plug=face_group.driver_plug.name if face_group.driver_plug else None,
                owner=face_group.owner.name,
                has_blendshape=bool(face_group.blendshape_group)
            )
            target_blueprints = []
            for face_target in face_group.face_targets:
                if face_target.driver_value != 0.0:
                    keyframe_group = face_target.keyframe_group
                    target_blueprint = dict(
                        root_name=face_target.root_name,
                        index=face_target.index,
                        side=face_target.side,
                        mesh_names=[x.get_selection_string().split('|')[-1] for x in face_target.target_meshs],
                        driver_value=face_target.driver_value,
                        attribute_values=face_target.attribute_values if controller.locked_face_drivers else get_driven_plug_values(face_target), #  face_target.attribute_values is an elena thing and needs to go
                        tangents=(
                            keyframe_group.in_tangent_type,
                            keyframe_group.out_tangent_type
                        )

                    )
                    target_blueprints.append(target_blueprint)
            group_blueprint['targets'] = target_blueprints
            group_blueprints.append(group_blueprint)
        network_blueprint['groups'] = group_blueprints
        controller.face_progress_signal.emit(
            message='Finished getting Data...',
            done=True
        )

        return network_blueprint
    else:
        return None


def get_driven_plug_values(face_target):

    face_group = face_target.face_group
    sorted_targets = sorted(face_group.face_targets, key=lambda x: x.driver_value)
    target_index = sorted_targets.index(face_target)

    plug_values = []

    for driven_plug_name in face_group.sdk_group.animation_curves:
        animation_curve = face_group.sdk_group.animation_curves[driven_plug_name]
        plug_value = animation_curve.get_value_at_index(target_index)
        rounded_value = round(plug_value, driven_plug_rounding)
        plug_values.append(
            (
                driven_plug_name,
                rounded_value
            )
        )

    return plug_values


def get_deletable_curves(face_group, range_threshold=0.001):
    deletable_curves = set(face_group.sdk_group.animation_curves.values())
    for driven_plug_name in face_group.sdk_group.animation_curves:
        animation_curve = face_group.sdk_group.animation_curves[driven_plug_name]
        first_keyframe = animation_curve.keyframes[0]
        for key in animation_curve.keyframes:
            # Need to add default
            if abs(key.get_out_value() - first_keyframe.get_out_value()) > range_threshold:
                if animation_curve in deletable_curves:
                    deletable_curves.remove(animation_curve)
    return WeakList(deletable_curves)


def prune_driven_curves(controller, range_threshold=0.001):
    face_groups = controller.face_network.face_groups
    controller.face_progress_signal.emit(
        message='Pruning Curves',
        value=0,
        maximum=len(face_groups)
    )
    deletable_curve_names = []
    for f, face_group in enumerate(face_groups):
        print 'Pruning curves for : %s' % face_group
        face_group.controller.face_progress_signal.emit(
            value=f,
            message='Pruning Curves (%s)' % face_group.root_name
        )
        deletable_curves = get_deletable_curves(
            face_group,
            range_threshold=range_threshold
        )
        deletable_curve_names.extend([x.name for x in deletable_curves])
        for x in deletable_curves:
            x.unparent()
    gc.collect()
    if deletable_curve_names:
        controller.scene.lock_node(
            deletable_curve_names,
            l=False
        )
        controller.scene.delete(
            deletable_curve_names
        )
    controller.face_progress_signal.emit(done=True)


def prune_driven_keys(controller, range_threshold=0.0001):
    return  # disabled untill i figure out threshold issue
    face_groups = controller.face_network.face_groups
    controller.face_progress_signal.emit(
        message='Pruning Keys',
        value=0,
        maximum=len(face_groups)
    )

    def get_deletable_keys(face_groups):
        del_keys = set()
        all_keys = []
        for ind, face_group in enumerate(face_groups):
            controller.face_progress_signal.emit(
                value=ind,
                message='Pruning Keys (%s)' % face_group.root_name
            )
            for driven_plug_name in face_group.sdk_group.animation_curves:
                animation_curve = face_group.sdk_group.animation_curves[driven_plug_name]
                all_keys.append(animation_curve.keyframes)
                for key in animation_curve.keyframes:
                    index = animation_curve.keyframes.index(key)
                    if 0 < index < len(animation_curve.keyframes) - 1:
                        prev_key_total = abs(animation_curve.keyframes[index-1].out_value - key.out_value)
                        next_key_total = abs(animation_curve.keyframes[index+1].out_value - key.out_value)
                        if prev_key_total <= range_threshold and next_key_total <= range_threshold:
                            del_keys.add(key)
        return WeakList(del_keys)

    controller.delete_objects(get_deletable_keys(face_groups))
    controller.face_progress_signal.emit(done=True)


def create_sculpt_geometry(face_target, *targets):

    controller = face_target.controller
    delete_sculpt_geometry(controller)

    scene = controller.scene
    if scene.mock:
        raise Exception('Not Implemented...')

    if isinstance(face_target, FaceTarget):
        face_group = face_target.face_group
        face_network = face_group.face_network
        if face_network.geometry:

            if scene.objExists('face_sculpt_gp'):
                scene.delete('face_sculpt_gp')
            sculpt_group = scene.createNode('transform', name='face_sculpt_gp')
            sculpt_meshs = []

            for g in range(len(face_network.geometry)):
                group_name = 'face_sculpt_%s' % g
                mesh_name = 'face_sculpt_%sShape' % g
                if scene.objExists(group_name):
                    scene.delete(group_name)
                if scene.objExists(mesh_name):
                    scene.delete(mesh_name)
                mesh_group = scene.createNode(
                    'transform',
                    name=group_name,
                    parent=sculpt_group
                )

                import maya.cmds as mc
                import maya.mel as mel
                import maya.OpenMaya as om
                import maya.OpenMayaAnim as oma

                def get_m_object(node_name):
                    if isinstance(node_name, om.MObject):
                        return node_name
                    selection_list = om.MSelectionList()
                    selection_list.add(node_name)
                    m_object = om.MObject()
                    selection_list.getDependNode(0, m_object)
                    return m_object

                mesh_source = face_network.geometry[g].m_object
                parent = get_m_object(mesh_group)

                mesh_functions = om.MFnMesh(mesh_source)
                new_mesh = mesh_functions.copy(mesh_source, parent)
                new_mesh = scene.get_selection_string(new_mesh)
                new_mesh = scene.rename(new_mesh, mesh_name)
                sculpt_meshs.append(new_mesh)

            scene.assign_shading_group(
                face_network.sculpt_shader.shading_group.name,
                sculpt_meshs
            )
            return sculpt_meshs
        else:
            raise Exception('Face target has no target geometry')
    else:
        raise Exception('Invalid type (%s)' % type(face_target))


def delete_sculpt_geometry(controller):
    if controller:
        if controller.scene.objExists('face_sculpt_gp'):
            controller.scene.delete('face_sculpt_gp')


def get_mirrored_handle_positions(face_network, node_prefixes=('L_', 'R_')):
    """
    This doesnt really wok on any kind of asymmetry
    Should use local space somehow instead
    """
    controller = face_network.controller
    handle_data = dict()
    if not controller.scene.mock:
        for handle in face_network.driven_handles:
            handle_group = handle.groups[face_network.driver_group_index]
            mirror_handle_group_name = None
            if handle.side == 'left':
                mirror_handle_group_name = handle_group.name.replace(node_prefixes[0], node_prefixes[1])
            elif handle.side == 'right':
                mirror_handle_group_name = handle_group.name.replace(node_prefixes[1], node_prefixes[0])
            elif handle.side == 'center':
                mirror_handle_group_name = handle_group.name
            if mirror_handle_group_name in controller.named_objects:
                mirror_handle_group = controller.named_objects[mirror_handle_group_name]
                translation = mirror_handle_group.plugs['translate'].get_value()
                rotation = mirror_handle_group.plugs['rotate'].get_value()
                scale = mirror_handle_group.plugs['scale'].get_value()
                translation[0] = translation[0] * -1.0
                rotation[1] = rotation[1] * -1.0
                rotation[2] = rotation[2] * -1.0
                handle_data[handle.name] = (translation, rotation, scale)
    return handle_data


def set_handle_positions(face_network, handle_data):
    controller = face_network.controller
    for handle_name in handle_data:
        handle = controller.named_objects[handle_name]
        translation, rotation, scale = handle_data[handle_name]
        group = handle.groups[face_network.driver_group_index]
        group.plugs['translate'].set_value(translation)
        group.plugs['rotate'].set_value(rotation)
        group.plugs['scale'].set_value(scale)


def mirror_face_groups(face_network, node_prefixes=('L_', 'R_'), plug_prefixes=('left_', 'right_')):
    controller = face_network.controller
    right_groups = dict((x.root_name, x) for x in face_network.face_groups if x.side == 'right')
    left_groups = [x for x in face_network.face_groups if x.side == 'left']
    controller.face_progress_signal.emit(
        message='Mirroring Face Groups',
        maximum=len(left_groups),
        value=0
    )
    print 'Mirroring Face Groups...'
    reverse_index_lists = controller.scene.get_reverse_index_lists(face_network.base_geometry)

    controller.face_network_about_to_change_signal.emit(controller.face_network)

    for i, left_group in enumerate(left_groups):
        #right_group = None
        #if left_group.root_name in right_groups:
        #    print 'Found existing right side face group...'
        #    right_group = right_groups[left_group.root_name]
        #else:
        left_driver_plug = left_group.driver_plug
        left_driver_node_name = left_driver_plug.get_node().get_selection_string()
        plug_name = left_driver_plug.root_name
        right_driver_node_name = left_driver_node_name.replace(*node_prefixes)
        right_group = None
        if not right_driver_node_name == left_driver_node_name:
            right_plug_name = plug_name.replace(*plug_prefixes)
            if right_driver_node_name in controller.named_objects:
                right_driver_plug = controller.named_objects[right_driver_node_name].plugs[right_plug_name]
                group_node_name = ntt.create_name_string(
                    FaceGroup,
                    driver_plug=right_driver_plug,
                    root_name=left_group.root_name,
                    side='right'
                )
                if group_node_name not in controller.named_objects:
                    right_group = face_network.create_group(
                        driver_plug=right_driver_plug,
                        root_name=left_group.root_name,
                        side='right'
                    )
                else:
                    print ' FaceGroup "%s" already exists. skipping..' % group_node_name

            else:
                print 'Unable to find right side driver node in controller for %s' % left_driver_plug
        else:
            print 'Unable to search/replace right side driver node for %s' % left_driver_plug
        if right_group:
            right_targets = dict((x.driver_value, x) for x in right_group.face_targets)
            for left_target in left_group.face_targets:
                #print 'Mirroring target %s ' % left_target
                if left_target.driver_value != 0.0:
                    temp_target_geometry = controller.scene.create_mirrored_geometry(
                        [x.name for x in left_target.target_meshs],
                        [x.name for x in face_network.base_geometry],
                        reverse_index_lists=reverse_index_lists
                    )
                    mesh_targets = [controller.scene.listRelatives(x, c=True, type='mesh')[0] for x in temp_target_geometry]
                    left_group.driver_plug.set_value(left_target.driver_value)
                    handle_positions = get_mirrored_handle_positions(
                        face_network,
                        node_prefixes=node_prefixes
                    )
                    face_network.reset_driver_plugs()
                    right_group.driver_plug.set_value(left_target.driver_value)

                    set_handle_positions(
                        face_network,
                        handle_positions
                    )
                    # needs to happen twice because of handles parented to handles
                    set_handle_positions(
                        face_network,
                        handle_positions
                    )

                    face_network.consolidate_handle_positions()
                    right_target = right_group.create_face_target(
                        *mesh_targets,
                        driver_value=left_target.driver_value
                    )

                    right_target.keyframe_group.set_keyframe_tangents(left_target.keyframe_group.in_tangent_type)
                    if temp_target_geometry:
                        controller.scene.delete(temp_target_geometry)
                    face_network.reset_driver_plugs()
                    controller.dg_dirty()


        else:
            print 'Unable to create right group...'

        controller.face_progress_signal.emit(
            message='Mirroring Face Group (%s)' % left_group.root_name,
            value=i
        )

    controller.face_network_finished_change_signal.emit(face_network)
    controller.face_progress_signal.emit(done=True)


def go_to_face_target(face_target):
    if isinstance(face_target, FaceTarget):
        controller = face_target.controller
        if controller.locked_face_drivers:
            attribute_values = face_target.attribute_values
            if attribute_values:
                for attribute_name, value in attribute_values:
                    node_name, plug_name = attribute_name.split('.')
                    node = controller.initialize_node(node_name, parent=None)
                    plug = node.plugs[plug_name]
                    if not controller.scene.listConnections(plug.name, s=True, d=False):
                        plug.set_value(value)
        else:
            try:
                face_target.face_group.driver_plug.set_value(face_target.driver_value)
            except Exception, e:
                print e.message
    else:
        raise Exception('Invalid Type (not FaceTarget)')


def bake_shards(controller):
    """
    :param controller:
    :return:
    """

    root = controller.root
    jaws = list(root.find_parts(NewJaw))
    if not jaws:
        jaws = list(root.find_parts(Jaw))

    mouth_sliders = list(root.find_parts(MouthSlider))
    shard_handles = WeakList([x for x in root.get_handles() if isinstance(x, FaceHandle) and x.shard_matrix])
    handle_groups_shard = [x.groups[-1] for x in shard_handles]
    if not mouth_sliders:
        print 'Unable to bake shards.  Couldnt find mouth_sliders.'
        return
    if not jaws:
        print 'Unable to bake shards.  Couldnt find jaw.'
        return
    shard_matrix_nodes = WeakList(x.shard_matrix for x in shard_handles)
    shard_transforms = WeakList(x.shard_transform for x in shard_handles)

    shard_driven_plugs = WeakList()
    for x in handle_groups_shard:
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            shard_driven_plugs.append(x.plugs[attr])

    # Jaw corrective values

    groups_data = dict()
    jaw = jaws[0]
    mouth_slider = mouth_sliders[0]
    driver_transform = jaw.driver_transform
    plugs = [
        jaw.handles[0].plugs['translateX'],
        jaw.handles[0].plugs['translateY'],
        jaw.handles[0].plugs['translateZ']
    ]

    for f, driver_plug in enumerate(plugs):
        initial_value = driver_plug.get_value()
        targets_data = dict()
        for driver_value in [-10.0, 10.0]:
            target_data = dict()
            driver_plug.set_value(driver_value)
            for h in [x.groups[-2] for x in shard_handles]:
                for p in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                    plug_string = '%s.%s' % (h, p)
                    value = controller.scene.getAttr(plug_string)
                    target_data[plug_string] = value
            targets_data[driver_value] = target_data
            targets_data[driver_value] = target_data
        driver_plug.set_value(initial_value)
        groups_data[jaw.handles[0].plugs[driver_plug.root_name]] = targets_data
    plugs = [
        jaw.handles[0].plugs['rotateX'],
        jaw.handles[0].plugs['rotateY'],
        jaw.handles[0].plugs['rotateZ']
    ]

    for f, driver_plug in enumerate(plugs):
        initial_value = driver_plug.get_value()
        targets_data = dict()
        for driver_value in [-180.0, -90.0, -75.0, -50.0, -25.0, 25.0, 50.0, 75.0, 90.0, 180.0]:
            target_data = dict()
            driver_plug.set_value(driver_value)
            for h in [x.groups[-2] for x in shard_handles]:
                for p in ['rx', 'ry', 'rz', 'tx', 'ty', 'tz']:
                    plug_string = '%s.%s' % (h, p)
                    value = controller.scene.getAttr(plug_string)
                    target_data[plug_string] = value
            targets_data[driver_value] = target_data
        driver_plug.set_value(initial_value)
        groups_data[jaw.handles[0].plugs[driver_plug.root_name]] = targets_data

    # Down left corrective values

    down_left_driven = dict()

    down_left_drivers = {
        mouth_slider.jaw_handle.plugs['tx']: 1.0,
        mouth_slider.jaw_handle.plugs['ty']: -1.0,
        mouth_slider.jaw_handle.plugs['jaw_down_left']: 1.0
    }
    for plug in down_left_drivers:
        plug.set_value(down_left_drivers[plug])
    for h in [x.groups[-2] for x in shard_handles]:
        down_left_driven[h] = controller.scene.xform(h, ws=True, m=True, q=True)

    for plug in down_left_drivers:
        plug.set_value(0.0)

    # Down right corrective values

    down_right_driven = dict()

    down_right_drivers = {
        mouth_slider.jaw_handle.plugs['tx']: -1.0,
        mouth_slider.jaw_handle.plugs['ty']: -1.0,
        mouth_slider.jaw_handle.plugs['jaw_down_right']: 1.0
    }
    for plug in down_right_drivers:
        plug.set_value(down_right_drivers[plug])
    for h in [x.groups[-2] for x in shard_handles]:
        down_right_driven[h] = controller.scene.xform(h, ws=True, m=True, q=True)
    for plug in down_right_drivers:
        plug.set_value(0.0)

    # delete shards

    controller.delete_objects(shard_matrix_nodes)
    controller.delete_objects(shard_transforms)
    zero_handles(controller, shard_handles)

    # create Sdks

    sdk_network = controller.create_object(
        SDKNetwork,
        root_name='jaw_shards',
        side='center'
    )
    sdk_network.initialize_driven_plugs(
        [x.groups[-2] for x in shard_handles],
        ['rx', 'ry', 'rz', 'tx', 'ty', 'tz']
    )

    for p, driver_plug in enumerate(groups_data):
        sdk_group = sdk_network.create_group(
            driver_plug=driver_transform.plugs[driver_plug.root_name],
            root_name='%s_shards' % driver_plug.name.replace('.', '_'),
            side='center'
        )
        sdk_group.create_keyframe_group(
            in_value=0.0
        ).set_keyframe_tangents('smooth')
        for driver_value in groups_data[driver_plug]:
            driver_plug.set_value(driver_value)
            target_data = groups_data[driver_plug][driver_value]
            for plug_name in target_data:
                controller.scene.setAttr(plug_name, target_data[plug_name])
            sdk_group.create_keyframe_group(
                in_value=driver_value
            ).set_keyframe_tangents('smooth')
            for plug_name in target_data:
                controller.scene.setAttr(plug_name, 0.0)
            driver_plug.set_value(0.0)

        zero_handles(controller, shard_handles)

    # Down Left Sdks

    sdk_group = sdk_network.create_group(
        driver_plug=mouth_slider.jaw_handle.plugs['jaw_down_left'],
        root_name='down_left_jaw_shards',
        side='center'
    )
    sdk_group.create_keyframe_group(
        in_value=0.0
    )
    for plug in down_left_drivers:
        plug.set_value(down_left_drivers[plug])
    for handle in down_left_driven:
        controller.scene.xform(handle, ws=True, m=down_left_driven[handle])

    sdk_group.create_keyframe_group(
        in_value=1.0
    )
    for plug in down_left_drivers:
        plug.set_value(0.0)

    # Down Right Sdks

    sdk_group = sdk_network.create_group(
        driver_plug=mouth_slider.jaw_handle.plugs['jaw_down_right'],
        root_name='down_right_jaw_shards',
        side='center'
    )
    sdk_group.create_keyframe_group(
        in_value=0.0
    )
    for plug in down_right_drivers:
        plug.set_value(down_right_drivers[plug])
    for handle in down_right_driven:
        controller.scene.xform(handle, ws=True, m=down_right_driven[handle])

    sdk_group.create_keyframe_group(
        in_value=1.0
    )
    for plug in down_right_drivers:
        plug.set_value(0.0)

    controller.dg_dirty()


def zero_handles(controller, handles):
    for handle in handles:
        controller.scene.xform(
            handle.groups[-1],
            ws=False,
            m=list(Matrix())
        )
        controller.scene.xform(
            handle.groups[-2],
            ws=False,
            m=list(Matrix())
        )
        controller.scene.xform(
            handle,
            ws=False,
            m=list(Matrix())
        )


def bake_shards_old(controller):
    """
    :param controller:
    :return:
    """
    face_network = controller.face_network
    shard_handles = [x for x in face_network.driven_handles if isinstance(x, FaceHandle)]
    shard_matrix_nodes = WeakList(x.shard_matrix for x in shard_handles)
    shard_mesh_nodes = WeakList(x.shard_mesh for x in shard_handles)
    shard_transforms = WeakList(x.shard_transform for x in shard_handles)
    skin_clusters = []
    for mesh in shard_mesh_nodes:
        skin = controller.scene.find_related_skin_cluster(mesh.name)
        if skin:
            skin_clusters.append(skin)
    shard_groups = [x.groups[1] for x in shard_handles]
    face_groups = face_network.face_groups
    controller.face_progress_signal.emit(
        message='Baking Shard Behavior',
        value=0,
        maximum=len(face_groups)
    )
    for f, face_group in enumerate(face_groups):
        controller.face_progress_signal.emit(
            message='Baking Shard Behavior (%s)' % face_group.root_name,
            value=f
        )
        for face_target in face_group.face_targets:
            print 'Baking shards for face target : %s' % face_target
            if face_target.driver_value != 0.0:
                go_to_face_target(face_target)
                handle_matrices = [x.get_matrix() for x in shard_handles]
                [controller.scene.setAttr('%s.envelope' % x, 0.0) for x in skin_clusters]
                for i in range(len(shard_groups)):
                    shard_handles[i].set_matrix(handle_matrices[i])
                controller.update_target_handles(face_target)
                [controller.scene.setAttr('%s.envelope' % x, 1.0) for x in skin_clusters]
                face_group.driver_plug.set_value(0.0)

    controller.delete_objects(shard_matrix_nodes)
    controller.delete_objects(shard_transforms)
    controller.face_progress_signal.emit(done=True)
