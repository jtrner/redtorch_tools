__version__ = '0.0.0'
import PySignal
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.node_objects.animation_curve import AnimationCurve, KeyFrame
from rig_factory.controllers.node_controller import NodeController
from rig_factory.objects.sdk_objects.driven_plug import DrivenPlug
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.utilities.sdk_utilities.blueprint_utilities as btl


class SDKController(NodeController):

    sdk_network_changed_signal = PySignal.ClassSignal()

    def __init__(self):
        super(SDKController, self).__init__()
        self.sdk_network = None

    def reset(self, *args):
        super(SDKController, self).reset()
        self.set_sdk_network(None)

    def view_blueprint(self):
        btl.view_blueprint(self)

    def get_blueprint(self, rig):
        return btl.get_blueprint(rig)

    def build_blueprint(self, blueprint, **kwargs):
        return btl.build_blueprint(self, blueprint, **kwargs)

    def set_sdk_network(self, sdk_network):
        if not isinstance(sdk_network, SDKNetwork) and not sdk_network is None:
            raise Exception('Cannot set_sdk_network with a : %s' % type(sdk_network))
        self.sdk_network = sdk_network
        self.sdk_network_changed_signal.emit(sdk_network)

    def prune_curves(self, item, threshold=0.0001):
        if isinstance(item, SDKNetwork):
            for sdk_group in item.sdk_groups:
                self.prune_curves(sdk_group)
        if isinstance(item, SDKGroup):
            for driver_plug_name in item.animation_curves:
                self.prune_curves(item.animation_curves[driver_plug_name])
        elif isinstance(item, AnimationCurve):
            for animation_curve in item.keyframes:
                for i, key in enumerate(animation_curve.keys):
                    if i > 0:
                        movement_value = key.out_value - animation_curve.keys[i-1].out_value
                        if movement_value < threshold or movement_value < threshold*-1:
                            animation_curve.keys[i-1].delete()
                    else:
                        pass
        else:
            raise Exception('Cannot prune_curves on a : %s' % type(item))

    def create_sdk_network(self, **kwargs):
        this = self.create_object(
            SDKNetwork,
            **kwargs
        )
        self.set_sdk_network(this)
        return this

    def get_selected_driven_plugs(self):
        plugs = []
        for node in self.get_selected_nodes():
            for attr in self.scene.get_selected_attribute_names():
                plugs.append(self.get_driven_plug(node, attr))
        return plugs

    def get_driven_plug(self, node, plug_name):
        driven_plug = DrivenPlug(
            controller=self,
            parent=node,
            name=plug_name
        )
        #self.register_item(driven_plug)
        self.scene.initialize_plug(driven_plug)
        return driven_plug

    def isolate_sdk_group(self, item):
        """
        Subtract the effect of all but this group from the driven plugs
        :param SDKGroup:
        :return: None
        """

        if isinstance(item, SDKGroup):
            sdk_network = item.sdk_network
            sdk_groups = sdk_network.sdk_groups
            driven_plugs = sdk_network.driven_plugs
            for driven_plug in driven_plugs:
                difference = 0.0
                for gi in range(len(sdk_groups)):
                    if item.index != gi:
                        blend_input_plug = driven_plug.blend_node.plugs['input'].element(gi)
                        difference += blend_input_plug.get_value(0.0)
                driven_plug.set_value(driven_plug.get_value(0.0) - difference)
        else:
            raise Exception('Cannot "isolate" a : %s' % type(item))

    @staticmethod
    def set_active(item, value):
        raise Exception('Cannot "set_active" on a : %s' % type(item))

    @staticmethod
    def set_weight(sdk_group, value):
        if isinstance(sdk_group, SDKGroup):
            for driven_plug in sdk_group.sdk_network.driven_plugs:
                driven_plug.blend_node.plugs['weight'].element(sdk_group.index).set_value(value)
        else:
            raise Exception('Cannot "set_weight" on a : %s' % type(sdk_group))

    def deserialize(self, *args, **kwargs):
        items = super(SDKController, self).deserialize(*args, **kwargs)
        for item in items:
            if isinstance(item, SDKNetwork):
                self.set_sdk_network(item)
        return items

    def update_keyframe_group(self, keyframe_group, isolate=True):
        """
        Set the driver value of all keyframes tp driven plugs current value
        """
        if isinstance(keyframe_group, KeyframeGroup):
            controller = keyframe_group.controller
            if isolate:
                self.isolate_sdk_group(keyframe_group.sdk_group)
            for keyframe in keyframe_group.keyframes:
                controller.scene.change_keyframe(
                    keyframe.animation_curve.m_object,
                    keyframe.in_value,
                    out_value=keyframe.animation_curve.driven_plug.get_value()
                )
            controller.dg_dirty()
        else:
            raise TypeError('Invalid type "%s"' % type(keyframe_group))


    #def update_keyframe_groups(self, *keyframe_groups):
    #    """
    #    Split the difference between multiple keyframe groups
    #    """
    ##    sdk_group = keyframe_groups[0].sdk_group
     #   sdk_network = sdk_group.sdk_network
     #   user_positions = sdk_network.get_user_positions()
     #   in_values = [x.in_value for x in keyframe_groups]
     #   combined_values = sum(in_values)
     #   group_positions = []
     ##   for keyframe_group in keyframe_groups:
      #      group_positions.append(keyframe_group.get_positions())
      #  for g, keyframe_group in enumerate(keyframe_groups):
      #      in_value = keyframe_group.in_value
      #      weight = in_value / combined_values
      ###      for k, keyframe in enumerate(keyframe_group.keyframes):
        #        keyframe.out_value = group_positions[g][k] + (weight*user_positions[k])
        #        self.change_keyframe(keyframe)
        #    keyframe_group.sdk_group.driver_plug.set_value(keyframe_group.in_value)

    def change_keyframe(self, item, **kwargs):
        if isinstance(item, KeyFrame):
            self.scene.change_keyframe(
                item.animation_curve.m_object,
                item.in_value,
                **kwargs
            )
            for key in kwargs:
                setattr(item, key, kwargs[key])

        elif isinstance(item, KeyframeGroup):
            for keyframe in item.keyframes:
                self.change_keyframe(
                    keyframe,
                    **kwargs
                )
        else:
            raise Exception('Unsupported type "%s"' % type(item))

    def initialize_driven_plugs(self, nodes, attributes):
        driven_plugs = WeakList()
        for node in nodes:
            for attribute in attributes:
                driven_plugs.append(self.initialize_driven_plug(node, attribute))
        return driven_plugs

    def initialize_driven_plug(self, node, key):
        # Turning off accepts_duplicate_names is faster than deleting existing plugs
        if key in node.existing_plugs:
            node.existing_plugs[key].unparent()

        #accepts_duplicate_names = self.accepts_duplicate_names
        #self.accepts_duplicate_names = True
        plug = self.create_object(
            DrivenPlug,
            parent=node,
            root_name=key
        )
        node.existing_plugs[key] = plug
        #self.accepts_duplicate_names = accepts_duplicate_names

        return plug

def flatten_items(*args):
    items = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            items.extend(flatten_items(*arg))
        else:
            items.append(arg)
    return items