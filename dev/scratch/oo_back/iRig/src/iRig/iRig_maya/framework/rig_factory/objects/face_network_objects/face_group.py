from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory


class FaceGroup(Transform):
    initial_value = DataProperty(
        name='initial_value'
    )
    is_corrective = DataProperty(
        name='is_corrective',
        default_value=False
    )
    owner = ObjectProperty(
        name='owner'
    )
    driver_plug = ObjectProperty(
        name='driver_plug'
    )
    sdk_group = ObjectProperty(
        name='sdk_group'
    )
    blendshape_group = ObjectProperty(
        name='blendshape_group'
    )
    mirror_group = ObjectProperty(
        name='mirror_group'
    )
    face_targets = ObjectListProperty(
        name='face_targets'
    )
    remap_node = ObjectProperty(
        name='remap_node'
    )
    blend_node = ObjectProperty(
        name='blend_node'
    )
    members = ObjectListProperty(
        name='members'
    )

    create_zero_target = DataProperty(
        name='create_zero_target',
        default_value=True
    )

    @property
    def face_network(self):
        owner = self
        while isinstance(owner, FaceGroup):
            owner = owner.owner
        return owner

    @classmethod
    def create(cls, controller, **kwargs):
        owner = kwargs.get('owner', None)
        if not owner:
            raise Exception('You must provide a "owner" keyword argument')
        driver_plug = kwargs.get('driver_plug', None)
        if not isinstance(driver_plug, Plug) and driver_plug is not None:
            raise Exception(
                'you must "driver_plug" keyword argument of type(%s) to create a %s' % (Plug, FaceGroup)
            )

        initial_value = 0.0

        if driver_plug:
            kwargs.setdefault('root_name', driver_plug.name.replace('.', '_'))
            initial_value = round(driver_plug.get_value(0.0), 2)

        if initial_value != 0.0:
            controller.raise_warning('Non zero default driver plug values not supported: %s' % driver_plug)

        kwargs.setdefault('parent', owner)
        kwargs.setdefault(
            'initial_value',
            initial_value
        )
        controller.start_ownership_signal.emit(
            None,
            owner
        )

        this = super(FaceGroup, cls).create(controller, **kwargs)

        if this.owner:
            this.owner.members.append(this)

        face_network = this.face_network
        sdk_network = face_network.sdk_network
        if driver_plug and sdk_network:

            this.sdk_group = sdk_network.create_group(
                **kwargs
            )

        controller.end_ownership_signal.emit(
            this,
            owner
        )
        #  using current value is problematic.. This makes non zero default driver values (like scale) impossible...

        if this.create_zero_target:
            this.create_face_target(
                driver_value=0.0
            )
        controller.register_item(this)
        return this

    def __init__(self, **kwargs):
        super(FaceGroup, self).__init__(**kwargs)
        self.controller.face_group_created_signal.emit(self)

    def create_blendshape_group(self):
        face_network = self.face_network
        blendshape = face_network.blendshape
        if self.blendshape_group:
            raise StandardError('The face group "%s" already has a blendshape group' % self)
        if blendshape:
            self.blendshape_group = blendshape.create_group(
                root_name=self.root_name,
                side=self.side
            )
            return self.blendshape_group
        else:
            raise Exception('The FaceNetwork does not have a Blendshape')

    def create_face_target(self, *geometry, **kwargs):

        for x in geometry:
            list_nodes = self.controller.scene.ls(x)
            if list_nodes and len(list_nodes) > 1:
                raise Exception('Duplicate geometry names : %s' % ', '.join(list_nodes))
        kwargs['geometry'] = geometry
        kwargs['face_group'] = self
        kwargs['parent'] = self

        return self.controller.create_object(FaceTarget, **kwargs)

    def mirror(self, **kwargs):
        return self.controller.mirror(self, **kwargs)

    def isolate(self):
        self.controller.consolidate_handle_positions(self.owner)
        self.controller.isolate_sdk_group(self.sdk_group)

    def create_driver_curve(self):

        if self.blendshape_group and self.driver_plug:
            remap_node = self.remap_node
            blend_node = self.blend_node

            if not blend_node:
                root_name = '%s_%s_blend_driver' % (
                    self.root_name,
                    self.driver_plug.name.replace('.', '_').split('|')[-1]
                )
                remap_node = self.create_child(
                    DependNode,
                    node_type='remapValue',
                    root_name=root_name
                )
                blend_node = self.create_child(
                    DependNode,
                    node_type='blendWeighted',
                    root_name=root_name
                )
                self.driver_plug.connect_to(remap_node.plugs['inputValue'])
                remap_node.plugs['outValue'].connect_to(blend_node.plugs['input'].element(0))
                self.remap_node = remap_node
                self.blend_node = blend_node

            blend_node.plugs['output'].connect_to(self.blendshape_group.get_weight_plug())
            min_driver_value, min_weight, max_driver_value, max_weight = self.calculate_driver_values()
            remap_node.plugs['value'].element(0).child(0).set_value(min_driver_value)
            remap_node.plugs['value'].element(0).child(1).set_value(min_weight)
            remap_node.plugs['value'].element(1).child(0).set_value(0.0)
            remap_node.plugs['value'].element(1).child(1).set_value(0.0)
            remap_node.plugs['value'].element(2).child(0).set_value(max_driver_value)
            remap_node.plugs['value'].element(2).child(1).set_value(max_weight)

    def calculate_driver_values(self):
        driver_values = set(x.driver_value for x in [x for x in self.face_targets if x.blendshape_inbetween])
        driver_values.add(0.0)
        if len(driver_values) < 2:
            driver_values.add(1.0)
        driver_values = sorted(driver_values)
        min_driver_value = driver_values[0]
        max_driver_value = driver_values[-1]
        min_weight = -1.0
        max_weight = 1.0
        if min_driver_value == 0.0:
            min_weight = 0.0
        if max_driver_value == 0.0:
            max_weight = 0.0
        return min_driver_value, min_weight, max_driver_value, max_weight

    def set_weight(self, value):
        self.sdk_group.set_weight(value)
        if self.blendshape_group:
            self.blendshape_group.get_weight_plug().set_value(value)

    def teardown(self):
        self.driver_plug.set_value(self.initial_value)
        nodes_to_delete = WeakList()
        if self.members:
            nodes_to_delete.extend(self.members)
        if self.face_targets:
            nodes_to_delete.extend(self.face_targets)
        if self.remap_node:
            nodes_to_delete.append(self.remap_node)
        if self.blendshape_group:
            nodes_to_delete.append(self.blendshape_group)
        if self.sdk_group:
            nodes_to_delete.append(self.sdk_group)
        self.controller.delete_objects(
            nodes_to_delete,
            collect=self.controller.garbage_collection
        )
        owner = self.owner
        self.controller.start_disown_signal.emit(self, owner)
        owner.members.remove(self)
        self.owner = None
        self.controller.end_disown_signal.emit(self, owner)
        super(FaceGroup, self).teardown()

    def get_next_avaliable_index(self):
        existing_indices = [x.index for x in self.face_targets]
        i = 0
        while True:
            if i not in existing_indices:
                return i
            i += 1

    def get_members(self, include_self=False):
        members = WeakList()
        if include_self:
            members.append(self)
        members.extend(self.members)
        for member in self.members:
            members.extend(member.get_members())
        return members
