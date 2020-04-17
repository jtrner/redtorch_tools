from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.sdk_objects.driven_plug import DrivenPlug
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.weak_list import WeakList


class SDKNetwork(BaseNode):

    sdk_groups = ObjectListProperty(
        name='sdk_groups'
    )
    driven_plugs = ObjectListProperty(
        name='driven_plugs'
    )
    post_infinity_type = DataProperty(
        name='post_infinity_type'
    )
    pre_infinity_type = DataProperty(
        name='pre_infinity_type'
    )
    is_weighted = DataProperty(
        name='is_weighted'
    )
    in_tangent = DataProperty(
        name='in_tangent'
    )
    out_tangent = DataProperty(
        name='out_tangent'
    )
    out_angle = DataProperty(
        name='out_angle'
    )
    in_angle = DataProperty(
        name='in_angle'
    )
    in_tangent_weight = DataProperty(
        name='in_tangent_weight'
    )
    out_tangent_weight = DataProperty(
        name='out_tangent_weight'
    )
    in_tangent_type = DataProperty(
        name='in_tangent_type'
    )
    out_tangent_type = DataProperty(
        name='out_tangent_type'
    )
    tangents_locked = DataProperty(
        name='tangents_locked'
    )
    is_breakdown = DataProperty(
        name='is_breakdown'
    )
    pickwalk_groups = DataProperty(
        name='pickwalk'
    )
    container = ObjectProperty(
        name='container'
    )
    lock_curves = DataProperty(
        name='lock_curves',
        default_value=True
    )

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('post_infinity_type', 'linear')
        kwargs.setdefault('pre_infinity_type', 'linear')
        kwargs.setdefault('in_tangent', 'linear')
        kwargs.setdefault('out_tangent', 'linear')
        container = kwargs.get('container', None)
        if container:
            controller.start_ownership_signal.emit(None, container)
        this = super(SDKNetwork, cls).create(controller, **kwargs)
        if container:
            container.sdk_networks.append(this)
            controller.end_ownership_signal.emit(this, container)
        return this

    def __init__(self, **kwargs):
        super(SDKNetwork, self).__init__(**kwargs)

    def prune_curves(self, threshold=0.0001):
        self.controller.prune_curves(self, threshold=threshold)

    def add_driven_plugs(self, plugs):

        plugs = WeakList(set(plugs))
        controller = self.controller
        existing_plugs = self.driven_plugs
        existing_count = len(existing_plugs)
        for i, plug in enumerate(plugs):
            if plug not in self.driven_plugs:
                if not isinstance(plug, DrivenPlug):
                    raise StandardError('driven plugs must be of type "%s"' % DrivenPlug.__name__)
                if not self.controller.scene.mock and self.controller.scene.listConnections(plug, s=True, d=False):
                    raise StandardError('The driven plug "%s" already seems to have an incoming connection' % plug)

                blend_node = controller.create_object(
                    DependNode,
                    root_name=plug.name.replace('.', '_'),
                    index=existing_count + i,
                    node_type='blendWeighted',
                    parent=plug.get_node()
                )
                plug.get_node().plugs['nodeState'].connect_to(blend_node.plugs['nodeState'])  # stops maya from cleaning up this node
                blend_out_plug = blend_node.initialize_plug('output')

                default_value = plug.get_value()
                if plug.root_name in ['sx', 'sy', 'sz', 'scaleX', 'scaleY', 'scaleZ']:
                    add_node = blend_node.create_child(
                        DependNode,
                        node_type='addDoubleLinear',
                        root_name='%s_post_default' % blend_node.root_name
                    )
                    blend_out_plug.connect_to(add_node.plugs['input1'])
                    add_node.plugs['input2'].set_value(default_value)
                    add_node.plugs['output'].connect_to(plug)
                else:
                    blend_out_plug.connect_to(plug)

                plug.get_node().plugs['nodeState'].connect_to(blend_node.plugs['nodeState'])
                blend_node.initialize_plug('input')
                self.driven_plugs.append(plug)
                plug.blend_node = blend_node

    def reset_driven_plugs(self):
        for plug in self.driven_plugs:
            if plug.root_name in ['sx', 'sy', 'sz', 'scaleX', 'scaleY', 'scaleZ']:
                plug.set_value(1.0)
            else:
                plug.set_value(0.0)

    def set_driven_plugs(self, plugs):
        self.driven_plugs = []
        self.add_driven_plugs(plugs)

    def add_selected_driven_plugs(self):
        driven_plugs = []
        for plug_string in self.controller.get_selected_plug_strings():
            node_name, plug_string = plug_string.split('.')
            node = self.controller.initialize_node(node_name)
            driven_plug = self.controller.initialize_driven_plug(
                node,
                plug_string
            )
            if driven_plug not in self.driven_plugs:
                driven_plugs.append(driven_plug)
        self.add_driven_plugs(driven_plugs)

    def initialize_driven_plugs(self, nodes, attributes):
        self.add_driven_plugs(
            self.controller.initialize_driven_plugs(
                nodes,
                attributes
            )
        )

    def create_group(self, **kwargs):
        self.reset_driven_plugs()
        kwargs.setdefault('side', self.side)
        return self.controller.create_object(
            SDKGroup,
            sdk_network=self,
            **kwargs
        )

    def get_curves(self):
        curves = []
        for g in self.sdk_groups:
            for c in g.animation_curves:
                curves.append(c)
        return curves

    def get_positions(self):
        positions = []
        for driven_plug in self.driven_plugs:
            result_plug = driven_plug.node.plugs['output'].connections[0].in_plug
            positions.append(result_plug.get_value())
        return positions

    def get_user_positions(self):
        positions = []
        for driven_plug in self.driven_plugs:
            result_plug = driven_plug.node.plugs['output'].connections[0].in_plug
            result_value = result_plug.get_value()
            difference = 0.0
            for index in driven_plug.plugs:
                    difference += driven_plug.plugs[index].get_value()
            positions.append(result_value-difference)
        return positions

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index
        )
        blueprint['driven_plugs'] = ['%s.%s' % (x.get_node().get_selection_string(), x.root_name) for x in self.driven_plugs]
        return blueprint

    def teardown(self):

        if self.container:

            container = self.container
            self.controller.start_disown_signal.emit(self, container)
            self.container.sdk_networks.remove(self)
            self.controller.end_disown_signal.emit(self, container)
            del container

        objects_to_delete = WeakList()
        if self.sdk_groups:
            objects_to_delete.extend(self.sdk_groups)

        if self.driven_plugs:
            objects_to_delete.extend([x.blend_node for x in self.driven_plugs])

        self.controller.delete_objects(
            objects_to_delete,
            collect=self.controller.garbage_collection
        )

        super(SDKNetwork, self).teardown()

    def get_next_avaliable_index(self):
        existing_indices = [x.index for x in self.sdk_groups]
        i = 0
        while i in existing_indices:
            i += 1
        return i
