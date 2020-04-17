import os
import rig_factory.utilities.decorators as dec
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, \
    ObjectDictProperty
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle, GroupedHandle
import rig_factory.utilities.geometry_utilities as gtl
import rig_factory.environment as env
from weakref import WeakSet
import copy


class BaseContainer(Transform):

    parts = ObjectListProperty(
        name='parts'
    )
    shaders = ObjectDictProperty(
        name='shaders'
    )
    owner = ObjectProperty(
        name='owner'
    )
    joints = ObjectListProperty(
        name='joints'
    )
    deform_joints = ObjectListProperty(
        name='deform_joints'
    )
    base_deform_joints = ObjectListProperty(
        name='base_deform_joints'
    )
    handles = ObjectListProperty(
        name='handles'
    )
    color = DataProperty(
        name='color'
    )
    toggle_class = DataProperty(
        name='toggle_class'
    )
    geometry_group = ObjectProperty(
        name='geometry_group'
    )
    root_geometry_group = ObjectProperty(
        name='root_geometry_group'
    )
    low_geometry_group = ObjectProperty(
        name='low_geometry_group'
    )
    utility_geometry_group = ObjectProperty(
        name='utility_geometry_group'
    )
    export_data_group = ObjectProperty(
        name='export_data_group'
    )
    placement_group = ObjectProperty(
        name='placement_group'
    )
    parent_joint = ObjectProperty(
        name='parent_joint'
    )
    geometry_paths = DataProperty(
        name='geometry_paths',
        default_value=[]
    )
    utility_geometry_paths = DataProperty(
        name='utility_geometry_paths',
        default_value=[]
    )
    geometry = ObjectDictProperty(
        name='geometry'
    )
    deformers = ObjectListProperty(
        name='deformers'
    )
    default_settings = dict(
        root_name='body'
    )
    disconnected_joints = DataProperty(
        name='disconnected_joints',
        default_value=False
    )
    deformation_rig_enabled = DataProperty(
        name='deformation_rig_enabled',
        default_value=True
    )
    expanded_handles = ObjectListProperty(
        name='expanded_handles'
    )
    visible_plugs = ObjectListProperty(
        name='visible_plugs'
    )
    unlocked_plugs = ObjectListProperty(
        name='unlocked_plugs'
    )
    keyable_plugs = ObjectListProperty(
        name='keyable_plugs'
    )
    control_group = ObjectProperty(
        name='control_group'
    )
    joint_group = ObjectProperty(
        name='joint_group'
    )
    origin_geometry_group = ObjectProperty(
        name='origin_geometry_group'
    )
    origin_geometry_names = DataProperty(
        name='origin_geometry_names',
        default_value=dict()
    )
    delete_geometry_names = DataProperty(
        name='delete_geometry_names',
        default_value=[]
    )
    metadata = DataProperty(
        name='metadata',
        default_value=dict()
    )
    custom_plugs = ObjectListProperty(
        name='custom_plugs'
    )
    joint_chain = DataProperty(
        name='joint_chain',
        default_value=False
    )
    version = DataProperty(
        name='version',
        default_value='0.0.0'
    )

    unlockable_node_types = ['nucleus', 'hairSystem']

    def __init__(self, **kwargs):
        for x in self.default_settings:
            kwargs.setdefault(x, self.default_settings[x])
        super(BaseContainer, self).__init__(**kwargs)

    @dec.flatten_args
    def add_plugs(self, *plugs, **kwargs):
        keyable = kwargs.get('keyable', True)
        unlocked = kwargs.get('unlocked', True)
        visible = kwargs.get('visible', True)
        for plug in plugs:
            if isinstance(plug, basestring):
                if '.' not in plug:
                    raise StandardError('Invalid plug : %s' % plug)
                node_name, plug_name = plug.split('.')
                if not self.controller.scene.objExists(node_name):
                    raise StandardError('The node "%s" does not exist' % node_name)
                node = None
                if node_name in self.controller.named_objects:
                    node = self.controller.named_objects[node]
                else:
                    uuid = self.controller.scene.ls(node_name, uuid=True)[0]
                    if uuid in self.controller.objects:
                        node = self.controller.objects[uuid]
                if not node:
                    raise StandardError('The node is not registered with the rig controller : %s' % node_name)
                plug = node.plugs[plug_name]

            if keyable:
                self.keyable_plugs.append(plug)
            if unlocked:
                self.unlocked_plugs.append(plug)
            if visible:
                self.visible_plugs.append(plug)
            node = plug.get_node()
            if isinstance(node, GroupedHandle) and node.groups:
                if self.controller.scene.objExists('%s.%s' % (node.groups[-1].name, plug.root_name)):
                    gimbal_plug = node.groups[-1].plugs[plug.root_name]
                    if keyable:
                        self.keyable_plugs.append(gimbal_plug)
                    if unlocked:
                        self.unlocked_plugs.append(gimbal_plug)
                    if visible:
                        self.visible_plugs.append(gimbal_plug)
            if isinstance(node, GimbalHandle) and node.gimbal_handle:
                if self.controller.scene.objExists('%s.%s' % (node.gimbal_handle.name, plug.root_name)):
                    gimbal_plug = node.gimbal_handle.plugs[plug.root_name]
                    if keyable:
                        self.keyable_plugs.append(gimbal_plug)
                    if unlocked:
                        self.unlocked_plugs.append(gimbal_plug)
                    if visible:
                        self.visible_plugs.append(gimbal_plug)

    def teardown(self):
        if self.controller.root == self:
            self.controller.set_root(None)
        self.controller.disown(self)
        super(BaseContainer, self).teardown()

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BaseContainer, cls).create(controller, **kwargs)
        this.plugs['overrideEnabled'].set_value(False)
        uuid_plug = this.create_plug(
            'serialization_uuid',
            dt='string',
            keyable=False
        )
        uuid_plug.set_channel_box(True)
        uuid_plug.set_locked(True)
        if this.owner:
            this.owner.parts.append(this)
        else:
            this.create_shaders()
            this.create_groups()
        return this

    def import_geometry_paths(self):
        if not self.geometry_paths:
            print 'The container had no geometry paths.'
        else:
            self.controller.progress_signal.emit(
                message='Importing Geometry...',
                maximum=len(self.geometry_paths) + 1,
                value=0
            )
            for i, path in enumerate(self.geometry_paths):
                self.controller.progress_signal.emit(
                    message='Importing Geometry: %s' % path.split('/')[-1],
                    value=i+1
                )
                if os.path.exists(path):
                    new_geometry = gtl.import_geometry(
                        self.controller,
                        path,
                        parent=self.geometry_group
                    )
                    self.geometry.update(new_geometry)
                else:
                    print 'The geometry path does not exist: %s' % path
            self.controller.progress_signal.emit(done=True)

    def import_utility_geometry_paths(self):
        if not self.utility_geometry_paths:
            print 'The container had no utility geometry paths.'
        else:
            self.controller.progress_signal.emit(
                message='Importing Geometry...',
                maximum=len(self.geometry_paths)+1,
                value=0
            )
            for i, path in enumerate(self.utility_geometry_paths):
                self.controller.progress_signal.emit(
                    message='Importing Geometry: %s' % path.split('/')[1],
                    value=i+1
                )
                if os.path.exists(path):
                    new_geometry = gtl.import_geometry(
                        self.controller,
                        path,
                        parent=self.geometry_group
                    )
                    self.geometry.update(new_geometry)
                else:
                    print 'The geometry path does not exist: %s' % path
            self.controller.progress_signal.emit(done=True)

    def create_origin_geometry(self):
        controller = self.controller
        error_messages = []
        for origin_geometry_name in self.origin_geometry_names:
            if origin_geometry_name in controller.named_objects:
                origin_geometry_faces = self.origin_geometry_names[origin_geometry_name]
                geometry_transform = controller.named_objects[origin_geometry_name]
                mesh_objects = [x for x in geometry_transform.children if isinstance(x, Mesh)]
                if len(mesh_objects) < 1:
                    error_messages.append('No mesh children found under "%s"' % geometry_transform)
                elif len(mesh_objects) > 1:
                    error_messages.append('more than one mesh children found under "%s"' % geometry_transform)
                else:
                    origin_geometry_transform = controller.create_object(
                        Transform,
                        name='%s_Origin' % origin_geometry_name,
                        parent=self.origin_geometry_group
                    )
                    origin_mesh = controller.copy_mesh(
                        mesh_objects[0].name,
                        origin_geometry_transform,
                        name='%s_OriginShape' % origin_geometry_name,
                    )
                    origin_mesh.assign_shading_group(
                        self.shaders['origin'].shading_group
                    )
                    self.geometry[origin_mesh.name] = origin_mesh
                    if origin_geometry_faces:
                        index_strings = origin_geometry_faces.split('[')[-1].split(']')[0].split(':')
                        start_index, end_index = map(int, index_strings)
                        self.controller.scene.select('%s.f[%s:%s]' % (origin_mesh, start_index, end_index))
                        self.controller.scene.select('%s.f[*]' % origin_mesh, tgl=True)
                        self.controller.scene.delete()
                        self.controller.scene.delete(origin_mesh, ch=True)

                    difference_blendshape = controller.create_blendshape(
                        mesh_objects[0],
                        parent=mesh_objects[0],
                        root_name=mesh_objects[0].name
                    )
                    blendshsape_group = difference_blendshape.create_group(
                        origin_mesh,
                        root_name=origin_mesh.name
                    )
                    blendshsape_group.get_weight_plug().set_value(1.0)

            else:
                #self.origin_geometry_names.pop(origin_geometry_name)
                pass

        if error_messages:
            controller.raise_error('\n'.join(error_messages))

    def post_create(self, **kwargs):
        pass

    def create_groups(self):
        pass

    def get_deformer_data(self):
        return self.controller.get_deformer_data(self)

    def create_nonlinear_deformer(self, object_type, geometry, **kwargs):
        kwargs['parent'] = self
        deformer = self.controller.create_nonlinear_deformer(
            object_type,
            *[self.geometry[str(x)] for x in geometry],
            **kwargs
        )
        self.deformers.append(deformer)
        return deformer

    def create_part(self, object_type, **kwargs):
        return self.controller.create_part(
            self,
            object_type,
            **kwargs
        )

    def create_shaders(self):
        self.controller.create_rig_shaders(self)

    def get_joints(self):
        joints = WeakList(self.joints)
        for part in self.get_parts():
            joints.extend(part.joints)
        return joints

    def get_deform_joints(self):
        deform_joints = WeakList(self.deform_joints)
        for part in self.get_parts():
            deform_joints.extend(part.deform_joints)
        return deform_joints

    def get_base_deform_joints(self):
        deform_joints = WeakList(self.base_deform_joints)
        for part in self.get_parts():
            deform_joints.extend(part.base_deform_joints)
        return deform_joints

    def snap_to_selected_mesh(self):
        self.controller.snap_part_to_selected_mesh(self)

    def get_handles(self):
        return self.controller.get_handles(self)

    def get_joint_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_joints())

    def get_handle_positions(self):
        return dict((x.name, list(x.get_matrix().get_translation())) for x in self.get_handles())

    def set_handle_positions(self, positions):
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in positions:
            if handle_name in handle_map:
                position = positions[handle_name]
                # Lose this in the future so set positions is faster\
                if len(position) > 3:
                    position = list(Matrix(*position).get_translation())
                handle_map[handle_name].plugs['translate'].set_value(position)

    def get_handle_mesh_positions(self):
        return self.controller.get_handle_mesh_positions(self)

    def set_handle_mesh_positions(self, positions):
        self.controller.set_handle_mesh_positions(self, positions)

    def snap_handles_to_mesh_positons(self):
        self.controller.snap_handles_to_mesh_positons(self)

    def get_parts(self):
        parts = WeakList()
        for part in self.parts:
            parts.append(part)
            if isinstance(part, BaseContainer):
                parts.extend(part.get_parts())
        return parts

    def find_first_part(self, *types, **kwargs):
        side = kwargs.get('side', 'any')
        root_name = kwargs.get('root_name', 'any')
        for part in self.get_parts():
            if not types or isinstance(part, types):
                if side == 'any' or part.side == side:
                    if root_name is 'any' or part.root_name == root_name:
                        return part

    def find_parts(self, *types, **kwargs):
        side = kwargs.get('side', 'any')
        parts = WeakSet()
        for part in self.get_parts():
            if not types or isinstance(part, types):
                if side == 'any' or part.side == side:
                    parts.add(part)
        return parts

    def get_parent_joint_indices(self):
        joints = self.get_joints()
        parent_joint_indices = []
        parts = self.get_parts()
        for part in parts:
            index = None
            if part.parent_joint:
                if part.parent_joint in joints:
                    index = joints.index(part.parent_joint)
                else:
                    raise Exception('%s has an invalid parent joint "%s"' % (part, part.parent_joint))
            parent_joint_indices.append(index)
        return parent_joint_indices

    def get_parent_joint_names(self):
        joint_names = [x.name for x in self.get_joints()]
        parent_joint_names = []
        parts = self.get_parts()
        for part in parts:
            joint_name = None
            if part.parent_joint:
                if part.parent_joint.name in joint_names:
                    joint_name = part.parent_joint.name
                else:
                    raise Exception('%s has an invalid parent joint "%s"' % (part, part.parent_joint))
            parent_joint_names.append(joint_name)
        return parent_joint_names

    def get_parent_joint_data(self):
        joint_data = []
        parts = self.get_parts()
        joint_names = [x.name for x in self.get_joints()]
        for i, part in enumerate(parts):
            joint_name = None
            joint_index = None
            if part.parent_joint:
                if part.parent_joint.name in joint_names:
                    joint_name = part.parent_joint.name
                    joint_index = joint_names.index(joint_name)
                else:
                    raise Exception('%s has an invalid parent joint "%s"' % (part, part.parent_joint))
            joint_data.append([part.name, joint_name, joint_index])
        return dict(
            joint_data=joint_data,
            joint_count=len(joint_names)
        )

    def set_parent_joint_data(self, data):
        parts = self.get_parts()
        joints = self.get_joints()
        part_dict = dict((x.name, x) for x in parts)
        joint_dict = dict((x.name, x) for x in joints)
        warnings = []
        joint_data = data['joint_data']
        joint_count = data['joint_count']
        if joint_count == len(joints) and len(parts) == len(joint_data):
            for i in range(len(joint_data)):
                part_name, joint_name, joint_index = joint_data[i]
                if joint_index is not None:
                    parts[i].set_parent_joint(joints[joint_index])

        else:
            for i in range(len(joint_data)):
                part_name, joint_name, joint_index = joint_data[i]
                if part_name in part_dict and joint_name in joint_dict:
                    part_dict[part_name].set_parent_joint(joint_dict[joint_name])
                else:
                    warnings.append(part_name)
        if warnings:
            self.controller.raise_warning('Unable to set parent joint for :\n %s' % '\n'.join(warnings))

    def set_parent_joints_by_index(self, joint_indices):
        joints = self.get_joints()
        parts = self.get_parts()
        if len(joint_indices) != len(parts):
            self.controller.raise_warning('parent joint mismatch  joints = %s parts = %s   Skipping parent joints' % (len(joint_indices), len(parts)))
            return
        self.clear_parent_joints()
        for p in range(len(parts)):
            joint_index = joint_indices[p]
            if joint_index is not None:
                if len(joints) > joint_index:
                    parts[p].set_parent_joint(joints[joint_index])
                else:
                    print 'Warning! Unable to assign parent joint for %s' % parts[p]

    def set_parent_joints_by_name(self, joint_names):
        joint_dict = dict((x.name, x) for x in  self.get_joints())
        parts = self.get_parts()
        if len(joint_names) != len(parts):
            self.controller.raise_warning('parent joint mismatch  joints = %s parts = %s   Skipping parent joints' % (len(joint_names), len(parts)))
            return
        self.clear_parent_joints()
        for p in range(len(parts)):
            joint_name = joint_names[p]
            if joint_name is not None:
                if joint_name in joint_dict:
                    parts[p].set_parent_joint(joint_dict[joint_name])
                else:
                    print 'Warning! Unable to find parent joint "%s"  for %s' % (joint_name, parts[p])


    def clear_parent_joints(self):
        capsules = WeakList()
        for part in self.get_parts():
            part.parent_joint = None
            if not isinstance(part, BaseContainer):
                if part.parent_capsule:
                    capsules.append(part.parent_capsule)
        self.controller.delete_objects(capsules)

    def import_utility_geometry(self, path):
        return self.controller.import_utility_geometry(
                self,
                path,
            )

    def import_geometry(self, path):

        if not self.geometry_group:
            raise Exception('%s does not have a geometry group.. try importing from the root')
        else:
            objects = self.controller.import_geometry(
                self,
                path
            )
            return objects

    def get_geometry(self, mesh_name):
        if mesh_name in self.geometry:
            return self.geometry[mesh_name]
        elif self.controller.scene.mock:
            mesh = self.create_child(
                Mesh,
                name=mesh_name
            )
            self.geometry[mesh_name] = mesh
            return mesh

    def get_root(self):
        if self.owner:
            return self.owner.get_root()
        return self

    def lock_nodes(self):
        self.controller.lock_node(*self.get_descendants(), lock=True, ic=True)

    def unlock_nodes(self):
        self.controller.lock_node(*self.get_descendants(), lock=False)

    def bind_geometry(self, geometry):
        return self.controller.bind_rig_geometry(self, geometry)

    def disown(self):
        self.controller.disown(self)

    def get_skin_cluster_data(self):
        return self.controller.get_skin_cluster_data(self)

    def set_skin_cluster_data(self, data):
        return self.controller.set_skin_cluster_data(self, data)

    def set_delta_mush_data(self, data):
        if data:
            self.controller.set_delta_mush_data(self, data)

    def get_delta_mush_data(self):
        return self.controller.get_delta_mush_data(self)

    def build_delta_mush(self, data):
        if data:
            try:
                self.set_delta_mush_data(data)
            except Exception, e:
                print e.message

    def get_wrap_data(self):
        return self.controller.get_wrap_data(self)

    def set_wrap_data(self, data):
        if data:
            self.controller.set_wrap_data(self, data)

    def finalize(self):
        pass

    def set_transform_axis_visibility(self, value):
        for item in self.get_descendants():
            if isinstance(item, Transform):
                item.plugs['displayLocalAxis'].set_value(value)

    def get_parent_part(self):
        if self.parent_joint:
            root = self.get_root()
            for part in root.get_parts():
                if self.parent_joint in part.joints:
                    return part

    def get_child_parts(self):
        root = self.get_root()
        joints = self.joints
        child_parts = WeakList()
        for part in root.get_parts():
            if part.parent_joint in joints:
                child_parts.append(part)
        return child_parts

    def create_deformation_rig(self, **kwargs):
        controller = self.controller
        root = self.get_root()
        deform_joints = []
        part_joints = self.joints
        joint_parent = root.deform_group
        for j, part_joint in enumerate(part_joints):

            """
            Name should be '%s_deform' % part_joint.root_name,
            (not bind)
            """

            deform_joint = controller.create_object(
                Joint,
                parent=joint_parent,
                root_name='%s_bind' % part_joint.root_name,
                index=part_joint.index,
                side=part_joint.side,
                size=part_joint.size,
                matrix=part_joint.get_matrix()
            )
            deform_joint.plugs['radius'].set_value(part_joint.size)
            deform_joint.zero_rotation()
            deform_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                radius=part_joint.plugs['radius'].get_value(),
                type=part_joint.plugs['type'].get_value(),
                side=part_joint.plugs['side'].get_value(),
                drawStyle=part_joint.plugs['drawStyle'].get_value(2)
            )
            part_joint.plugs['rotateOrder'].connect_to(deform_joint.plugs['rotateOrder'])
            part_joint.plugs['inverseScale'].connect_to(deform_joint.plugs['inverseScale'])
            part_joint.plugs['jointOrient'].connect_to(deform_joint.plugs['jointOrient'])
            part_joint.plugs['translate'].connect_to(deform_joint.plugs['translate'])
            part_joint.plugs['rotate'].connect_to(deform_joint.plugs['rotate'])
            part_joint.plugs['scale'].connect_to(deform_joint.plugs['scale'])
            part_joint.plugs['drawStyle'].set_value(2)

            deform_joints.append(deform_joint)
        self.deform_joints = deform_joints
        self.base_deform_joints = deform_joints

        for part in self.parts:
            part.create_deformation_rig()

    def finish_create(self, **kwargs):
        if self.parent_joint:
            if self.base_deform_joints and not self.disconnected_joints:
                parent_index = self.get_root().get_joints().index(self.parent_joint)
                parent_bind_joint = self.get_root().get_base_deform_joints()[parent_index]
                self.joint_group.set_matrix(parent_bind_joint.get_matrix())
                self.base_deform_joints[0].set_parent(parent_bind_joint)
