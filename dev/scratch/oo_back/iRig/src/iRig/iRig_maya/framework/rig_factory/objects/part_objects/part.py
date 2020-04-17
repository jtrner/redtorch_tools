import os
import copy
import rig_factory
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh

from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.rig_objects.grouped_handle import StandardHandle
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.environment as env
from rig_factory.objects.base_objects.json_dict import JsonDict
from rig_math.matrix import Matrix


blueprint_dict_type = JsonDict if os.getenv('PIPE_DEV_MODE') else dict


class PartGuide(BasePart):

    rig_data = DataProperty(
        name='rig_data'
    )
    default_settings = dict(
        root_name='part'
    )
    base_handles = ObjectListProperty(
        name='base_handles'
    )

    def __init__(self, **kwargs):
        super(PartGuide, self).__init__(**kwargs)
        self.toggle_class = Part.__name__

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(PartGuide, cls).create(*args, **kwargs)

        size = this.size
        size_plug = this.create_plug(
            'size',
            at='double',
            k=True,
            dv=size
        )
        size_plug.set_value(size)
        utility_group = this.create_child(
            'Transform',
            root_name='%s_utility' % this.root_name
        )
        utility_group.plugs['visibility'].set_value(False)
        this.utility_group = utility_group
        #this.plugs['translate'].set_locked(True)
        #this.plugs['rotate'].set_locked(True)
        #this.plugs['scale'].set_locked(True)
        return this

    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)

    def reset_parent_joint(self):
        parent_joint = self.parent_joint
        if parent_joint:
            self.controller.start_unparent_joint_signal.emit(self)
            parent_joint.child_parts.remove(self)
            self.parent_joint = None
            self.controller.finish_unparent_joint_signal.emit(self)
        if self.parent_capsule:
            self.parent_capsule.delete()

    def set_parent_joint(self, joint):

        if not isinstance(joint, Joint):
            raise Exception(
                'To set_parent_joint, you must provide type Joint or type(None), not %s' % joint.__class__.__name__
            )

        self.controller.start_parent_joint_signal.emit(self, joint)
        if self.parent_joint:
            self.parent_joint.child_parts.remove(self)
        self.parent_joint = joint
        joint.child_parts.append(self)
        self.controller.finish_parent_joint_signal.emit(self, joint)
        return self.controller.create_parent_capsule(self, joint)

    def get_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            name=self.name,
            base_type=PartGuide.__name__,  # needed by blueprint view
            handle_positions=self.get_handle_positions(),
            handle_vertices=self.get_vertex_data(),
            index_handle_positions=self.get_index_handle_positions()
        )

        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        blueprint['size'] = self.plugs['size'].get_value(1.0)
        if not blueprint.get('matrices', None):
            blueprint['matrices'] = [list(x.get_matrix()) for x in self.joints]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.toggle_class,
            module=self.__module__,
        )
        if self.rig_data:
            blueprint.update(self.rig_data)
        blueprint['guide_blueprint'] = self.get_blueprint()
        blueprint['matrices'] = [list(x.get_matrix()) for x in self.joints]
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        blueprint['size'] = self.plugs['size'].get_value(1.0)
        return blueprint

    def get_mirror_blueprint(self):
        sides = dict(right='left', left='right')
        if self.side not in sides:
            raise Exception('Cannot mirror "%s" invalid side "%s"' % (self, self.side))

        blueprint = self.get_blueprint()
        blueprint['side'] = sides[blueprint['side']]
        blueprint.pop('name', None)
        blueprint.pop('pretty_name', None)

        blueprint['disconnected_joints'] = self.disconnected_joints

        mirrored_vertices = dict()
        vertex_data = self.get_vertex_data()
        search_prefix = rig_factory.settings_data['side_prefixes'][self.side]
        replace_prefix = rig_factory.settings_data['side_prefixes'][sides[self.side]]
        for handle_name in vertex_data:
            mirror_handle_name = handle_name.replace(search_prefix, replace_prefix)
            vertex_pairs = vertex_data[handle_name]
            mirrored_vertex_pairs = []
            for pair in vertex_pairs:
                mesh_name, index = pair
                if mesh_name in self.controller.named_objects:
                    mesh = self.controller.named_objects[mesh_name]
                    if isinstance(mesh, Mesh):
                        position = self.controller.scene.xform(
                            '%s.vtx[%s]' % (mesh_name, index),
                            q=True,
                            ws=True,
                            t=True
                        )
                        position[0] *= -1.0
                        mirror_index = mesh.get_closest_vertex_index(position)
                        mirrored_vertex_pairs.append((mesh_name, mirror_index))
            mirrored_vertices[mirror_handle_name] = mirrored_vertex_pairs

        blueprint['index_handle_positions'] = [[x[0]*-1.0, x[1], x[2]] for x in self.get_index_handle_positions()]
        blueprint['handle_vertices'] = mirrored_vertices

        return blueprint

    def post_create(self, **kwargs):
        super(PartGuide, self).post_create(**kwargs)
        self.set_index_handle_positions(kwargs.get(
            'index_handle_positions',
            []
        ))
        self.set_handle_positions(kwargs.get(
            'handle_positions',
            dict()
        ))
        self.set_vertex_data(kwargs.get(
            'handle_vertices',
            dict()
        ))


class Part(BasePart):

    guide_blueprint = DataProperty(
        name='guide_blueprint'
    )
    joint_chain = DataProperty(
        name='joint_chain',
        default_value=True
    )
    secondary_handles = ObjectListProperty(
        name='secondary_handles'
    )
    joint_group = ObjectProperty(
        name='joint_group'
    )
    scale_multiply_transform = ObjectProperty(
        name='scale_multiply_transform'
    )

    matrices = []  # This gets lost in serialization..

    def __init__(self, **kwargs):
        super(Part, self).__init__(**kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        matrices = copy.deepcopy(kwargs.pop('matrices', []))
        this = super(Part, cls).create(*args, **kwargs)
        assert this.owner
        assert this.get_root()
        this.matrices = [Matrix(*x) for x in matrices]
        utility_group = this.create_child(
            Transform,
            root_name='%s_utility' % this.root_name
        )
        if isinstance(this.owner, Part):
            joint_group = this.owner.joint_group

        else:
            joint_group = this.create_child(
                Transform,
                root_name='%s_joints' % this.root_name
            )
        scale_multiply_transform = this.create_child(
            Transform,
            root_name='%s_scale_multiply' % this.root_name
        )
        this.controller.create_scale_constraint(this, scale_multiply_transform)
        scale_multiply_transform.plugs['inheritsTransform'].set_value(False)
        utility_group.plugs['visibility'].set_value(False)
        this.utility_group = utility_group
        this.joint_group = joint_group
        this.scale_multiply_transform = scale_multiply_transform
        return this

    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)

    def create_deformation_rig(self, **kwargs):

        controller = self.controller
        root = self.get_root()
        deform_joints = []
        part_joints = self.joints
        joint_parent = root.deform_group
        for j, part_joint in enumerate(part_joints):
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

            if self.joint_chain:
                joint_parent = deform_joint
            deform_joints.append(deform_joint)
        self.deform_joints = deform_joints
        self.base_deform_joints = deform_joints

    def set_parent_joint(self, joint):
        if not isinstance(joint, Joint):
            raise Exception(
                'To set_parent_joint, you must provide type Joint, not %s' % joint.__class__.__name__
            )
        #if not isinstance(self.parent, BaseContainer):
        #    self.set_parent(joint)
        self.controller.create_parent_constraint(
            joint,
            self,
            mo=True
        )
        self.controller.create_scale_constraint(
            joint,
            self
        )
        self.parent_joint = joint

    def get_handle_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_handles())

    def set_handle_positions(self, positions):
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in positions:
            if handle_name in handle_map:
                handle_map[handle_name].set_matrix(Matrix(*positions[handle_name]))
            else:
                raise Exception('Handle "%s" did not exist. Unable to set position' % handle_name)

    def add_parent_space(self, joint):
        if not isinstance(joint, Joint):
            raise Exception('To set_parent_joint, you must provide type Joint, not %s' % joint.__class__.__name__)
        self.controller.create_parent_constraint(
            joint,
            self,
            mo=True
        )
        return self.controller.create_parent_capsule(
            self,
            joint
        )

    def get_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            matrices=[list(x) for x in self.matrices],
            guide_blueprint=self.guide_blueprint
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        if not blueprint.get('matrices', None):
            blueprint['matrices'] = [list(x.get_matrix()) for x in self.joints]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        if not blueprint:
            raise Exception('No Guide Blueprint found!')
        blueprint['rig_data'] = dict()
        return blueprint

    def post_create(self, **kwargs):
        super(Part, self).post_create(**kwargs)
        self.set_vertex_data(kwargs.get(
            'handle_vertices',
            dict()
        ))

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

    def finish_create(self, **kwargs):
        if self.parent_joint:
            if self.base_deform_joints and not self.disconnected_joints:
                parent_index = self.get_root().get_joints().index(self.parent_joint)
                parent_bind_joint = self.get_root().get_base_deform_joints()[parent_index]
                self.joint_group.set_matrix(parent_bind_joint.get_matrix())
                if self.joint_chain:
                    self.base_deform_joints[0].set_parent(parent_bind_joint)
                else:
                    parent_bind_joint.plugs['radius'].set_value(0)
                    for deform_joint in self.base_deform_joints:
                        deform_joint.set_parent(parent_bind_joint)
