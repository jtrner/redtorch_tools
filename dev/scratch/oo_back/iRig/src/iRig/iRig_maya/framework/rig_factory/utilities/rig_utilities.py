from rig_factory.objects.rig_objects.capsule import Capsule
from rig_factory.objects.rig_objects.space_switcher import SpaceSwitcher
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.shader import Shader
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster
import rig_factory.environment as env
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.rig_objects.constraint import ParentConstraint, PointConstraint, \
    OrientConstraint, ScaleConstraint

import rig_factory


def create_part(controller, owner, object_type, **kwargs):
    assert owner
    kwargs.setdefault('size', owner.size)
    kwargs['owner'] = owner
    kwargs['parent'] = owner
    if owner.control_group:
        kwargs['parent'] = owner.control_group
    controller.start_ownership_signal.emit(None, owner)
    this = controller.create_object(object_type, **kwargs)
    assert this.owner

    controller.end_ownership_signal.emit(this, owner)
    return this


def initialize_node(controller, node_name, **kwargs):
    """
    takes the name of an existing node and wraps it in the right Object instance
    :param node:
    :param parent:
    :return:
    """
    parent = kwargs.get('parent', None)
    if isinstance(node_name, basestring):
        m_object = controller.scene.get_m_object(node_name)
    else:
        m_object = node_name
    node_name = controller.scene.get_selection_string(m_object)
    object_type = controller.scene.get_m_object_type(m_object)

    if object_type == 'skinCluster':
        influences = [controller.initialize_node(x) for x in controller.scene.skinCluster(node_name, q=True, influence=True)]
        geometry = controller.initialize_node(controller.scene.skinCluster(node_name, q=True, geometry=True)[0])
        node = SkinCluster(
            controller=controller,
            root_name=node_name
        )
        node.name = node_name
        node.m_object = controller.scene.get_m_object(node_name)
        node.geometry = geometry
        node.influences = influences

        if parent:
            controller.start_parent_signal.emit(node, parent)
            node.parent = parent
            parent.children.append(node)
            controller.end_parent_signal.emit(node, parent)

        return node


def create_rig_shaders(rig):
    for key in env.colors:
        side_color = env.colors[key]
        if key:
            shader = rig.create_child(
                Shader,
                node_type='lambert',
                root_name=key,
                side=None
            )
            shader.plugs['ambientColor'].set_value([0.75, 0.75, 0.75])
            shader.plugs['color'].set_value(side_color)
            shader.plugs['diffuse'].set_value(0.0)
            shader.plugs['transparency'].set_value([0.8, 0.8, 0.8])
            rig.shaders[key] = shader
    flat_colors = dict(
        x=[1.0, 0.1, 0.1],
        y=[0.1, 1.0, 0.1],
        z=[0.1, 0.1, 1.0],
        black=[0.1, 0.1, 0.1]
    )
    for key in flat_colors:
        color = flat_colors[key]
        shader = rig.create_child(
            Shader,
            node_type='lambert',
            root_name=key,
            side=None
        )
        shader.plugs['ambientColor'].set_value(color)
        shader.plugs['color'].set_value(color)
        shader.plugs['diffuse'].set_value(0.0)
        shader.plugs['transparency'].set_value([0.5, 0.5, 0.5])
        rig.shaders[key] = shader
    glass_shader = rig.create_child(
        Shader,
        node_type='blinn',
        root_name='glass',
        side=None
    )

    glass_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    glass_shader.plugs['transparency'].set_value([0.9, 0.9, 0.9])
    rig.shaders['glass'] = glass_shader

    blank_shader = rig.create_child(
        Shader,
        node_type='lambert',
        root_name='blank',
        side=None
    )
    glass_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    rig.shaders[None] = blank_shader

    origin_shader = rig.create_child(
        Shader,
        node_type='blinn',
        root_name='origin',
        side=None
    )
    glass_shader.plugs['specularColor'].set_value([0.08, 0.08, 0.08])
    origin_shader.plugs['color'].set_value([0.8, 0.6, 0.6])
    rig.shaders['origin'] = origin_shader

    for shader in rig.shaders.values():
        rig.plugs['nodeState'].connect_to(shader.plugs['nodeState'])  # stops maya from cleaning up this node


def bind_rig_geometry(self, rig, geometry):
    if isinstance(rig, ContainerGuide):
        geometry_name = str(geometry)
        bind_joints = rig.get_deform_joints()
        if geometry_name not in rig.geometry:
            raise Exception('the geometry "%s" is not a part of the rig "%s"' % (geometry, rig))
        if not bind_joints:
            bind_joints = rig.get_joints()
            print 'Warning. "%s" does not have any bind joints...' % rig
        skin_cluster = self.create_skin_cluster(
            geometry,
            bind_joints,
            root_name=geometry_name
        )
        rig.deformers.append(skin_cluster)
        geometry.deformers.append(skin_cluster)
        return skin_cluster
    else:
        raise Exception('Invalid type "%s" cannot bind_rig_geometry' % rig)


def create_space_switcher(controller, body, *handles, **kwargs):

    """

    This should all go in the create function of SpaceSwitcher

    """
    translate = kwargs.get('translate', True)
    rotate = kwargs.get('rotate', True)
    scale = kwargs.get('scale', False)

    handle = handles[-1]
    root_name = handle.root_name
    side = handle.side
    handle_matrix = handle.get_matrix()
    index = handle.index
    index_name = root_name
    if index:
        index_name = '{0}_{1}'.format(root_name, rig_factory.index_dictionary[index])
    if handle.space_switcher:
        controller.delete_objects(WeakList([handle.space_switcher]))
    if len(handles) > 1:
        targets = handles[:-1]
        this = controller.create_object(
            SpaceSwitcher,
            parent=body.utilities_group,
            root_name='%s_blend_parent' % index_name,
            side=side,
            translate=translate,
            rotate=rotate,
            scale=scale
        )
        if 'parentSpace' in handle.existing_plugs:
            controller.delete_objects(WeakList([handle.existing_plugs['parentSpace']]))
        space_plug = handle.create_plug(
            'parentSpace',
            at='enum',
            k=True,
            en=':'.join([x.pretty_name for x in handles[:-1]])
        )
        owner = handle.owner
        if not owner:
            raise StandardError('Unable to find owner from "%s"' % handle)
        root = owner.get_root()
        if not root:
            raise StandardError('Unable to find root from handle "%s"' % handle)
        root.add_plugs(space_plug)
        target_groups = []
        rotate_order = handle.groups[1].plugs['rotateOrder'].get_value()

        for i, target in enumerate(targets):
            target_group = this.create_child(
                Transform,
                root_name='%s_%sSpaceSwitch' % (index_name, target.name),
                matrix=handle_matrix,
                side=side,
            )
            target_groups.append(target_group)
            target_group.plugs['rotateOrder'].set_value(rotate_order)

            if translate and rotate:
                constraint = controller.create_object(
                    ParentConstraint,
                    target,
                    target_group,
                    mo=True
                )
                constraint.set_parent(this)

            elif rotate:
                controller.create_object(
                    OrientConstraint,
                    target,
                    target_group,
                    mo=True
                )
            elif translate:
                controller.create_object(
                    PointConstraint,
                    target,
                    target_group,
                    mo=True
                )
            if scale:
                controller.create_object(
                    ScaleConstraint,
                    target,
                    target_group,
                    mo=True
                )
        for i, target_group in enumerate(target_groups):
            constraint_nodes = []
            if translate and rotate:
                constraint_nodes.append(
                    controller.create_parent_constraint(
                        target_group,
                        handle.groups[1],
                        mo=True,
                        parent=this
                    )
                )
            elif rotate:
                constraint_nodes.append(
                    controller.create_orient_constraint(
                        target_group,
                        handle.groups[1],
                        mo=True,
                        parent=this
                    )
                )
            elif translate:
                constraint_nodes.append(
                    controller.create_point_constraint(
                        target_group,
                        handle.groups[1],
                        mo=True
                    )
                )
            if scale:
                constraint_nodes.append(
                    controller.create_scale_constraint(
                        target_group,
                        handle.groups[1],
                        mo=True,
                        parent=this
                    )
                )
            for j, constraint_node in enumerate(list(set(constraint_nodes))):
                weight_plug_str = controller.scene.listAttr(str(constraint_node), k=True)[-1]
                condition = this.create_child(
                    DependNode,
                    index=i+j,
                    root_name='%s_%sCondSwitch' % (index_name, targets[j].root_name),
                    node_type='condition',
                )
                space_plug.connect_to(condition.plugs['firstTerm'])  # if custom attr value
                condition.plugs['operation'].set_value(0)  # equal to
                condition.plugs['secondTerm'].set_value(i)  # i
                condition.plugs['colorIfTrueR'].set_value(1)  # turn on, if true
                condition.plugs['colorIfFalseR'].set_value(0)  # turn off, if false
                condition.plugs['outColorR'].connect_to(constraint_node.plugs[weight_plug_str])
        this.targets = targets
        handle.space_switcher = this


def create_parent_capsule(controller, part, parent_joint):

    if part.parent_capsule:
        controller.delete_objects(WeakList([part.parent_capsule]))

    if parent_joint is not None and part.joints:
        root_name = part.root_name
        kwargs = dict(
            side=part.side,
            size=1.0
        )
        this = controller.create_object(
            Transform,
            parent=part,
            root_name='%s_parent' % root_name,
            **kwargs
        )
        capsule = controller.create_object(
            Capsule,
            root_name='%s_parent' % root_name,
            parent=this,
            **kwargs
        )
        kwargs['index'] = 0
        kwargs['patemny'] = 0

        locator_transform_1 = controller.create_object(
            Transform,
            root_name='%s_parent_start' % root_name,
            parent=this,
            **kwargs
        )
        locator_1 = part.create_child(
            Locator,
            root_name='%s_parent_start' % root_name,
            parent=locator_transform_1,
            **kwargs
        )
        locator_transform_2 = controller.create_object(
            Transform,
            root_name='%s_parent_end' % root_name,
            parent=this,
            **kwargs
        )
        locator_2 = part.create_child(
            Locator,
            root_name='%s_parent_end' % root_name,
            parent=locator_transform_2,
            **kwargs
        )
        controller.create_point_constraint(
            part.joints[0], locator_transform_1
        )
        controller.create_point_constraint(
            parent_joint, locator_transform_2
        )
        controller.create_point_constraint(
            part.joints[0],
            parent_joint,
            capsule
        )
        controller.create_aim_constraint(
            parent_joint,
            capsule,
            aimVector=env.aim_vector
        )
        locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
        locator_transform_1.plugs['visibility'].set_value(False)
        locator_transform_2.plugs['visibility'].set_value(False)
        part.parent_capsule = this
        capsule.mesh.assign_shading_group(part.get_root().shaders['highlight'].shading_group)

        return this


def create_ik_handle(controller, start_joint, end_joint, parent=None, solver='ikSCsolver'):
    if not isinstance(start_joint, Joint) or not isinstance(end_joint, Joint):
        raise Exception('You must use two "Joint" node_objects as arguments when you call "create_ik_handle"')

    matrix = end_joint.get_matrix()

    root_name = '%s_%s' % (start_joint.name, end_joint.name)
    name = controller.name_function(
        IkHandle.__name__,
        root_name=root_name

    )

    this = IkHandle(
        controller=controller,
        root_name=root_name,
        index=start_joint.index,
        matrix=matrix,
        solver=solver,
        parent=parent
    )

    this.name = name

    end_effector = controller.create_object(
        'IkEffector',
        root_name='%s_%s' % (start_joint.name, end_joint.name),
        parent=end_joint.parent,
        matrix=matrix
    )
    end_joint.plugs['tx'].connect_to(end_effector.plugs['tx'])
    end_joint.plugs['ty'].connect_to(end_effector.plugs['ty'])
    end_joint.plugs['tz'].connect_to(end_effector.plugs['tz'])

    this.start_joint = start_joint
    this.end_joint = end_joint
    this.end_effector = end_effector

    this.m_object = controller.scene.create_ik_handle(
        start_joint.m_object,
        end_effector.m_object,
        solver=solver,
        parent=parent.m_object,
        name=name
    )
    controller.register_item(this)

    return this


def create_distance_between(handle_a, handle_b, root_name=None, index=None, parent=None):
    if not parent:
        parent = handle_a
    if not root_name:
        root_name = handle_a.root_name
    if root_name and index:
        root_name = '{0}_{1:03d}'.format(root_name, index)

    distance_between_node = parent.create_child(DependNode,
                                             node_type='distanceBetween',
                                             root_name='%s_distanceBetween' % root_name)
    for handle, plug in zip((handle_a, handle_b), ('point1', 'point2')):
        pos = handle.create_child(Locator,
                                  root_name='%s_distancePosition%s' % (root_name, plug))
        pos.plugs['visibility'].set_value(False)
        pos.plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs[plug])
    return distance_between_node

