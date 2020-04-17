import copy
import json
import os
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.base_objects.weak_list import WeakList


def get_blueprint(item):
    blueprint = item.get_blueprint()
    if isinstance(item, SDKNetwork):
        group_blueprints = []
        for sdk_group in item.sdk_groups:
            group_blueprints.append(get_blueprint(sdk_group))
        blueprint['groups'] = group_blueprints

    if isinstance(item, SDKGroup):
        keyframe_group_blueprint = []
        for keyframe_group in item.keyframe_groups:
            keyframe_group_blueprint.append(get_blueprint(keyframe_group))
        blueprint['keyframe_groups'] = keyframe_group_blueprint

    if isinstance(item, KeyframeGroup):
        keyframe_blueprint = []
        for keyframe in item.keyframes:
            keyframe_blueprint.append(get_blueprint(keyframe))
        blueprint['in_value'] = item.in_value
        blueprint['keyframes'] = keyframe_blueprint

    return blueprint


def build_blueprint(controller, blueprint):
    object_type = blueprint['klass']
    if object_type == SDKNetwork.__name__:
        sdk_groups_data = blueprint.pop('groups', [])
        existing_nodes = dict()
        driven_plugs = blueprint.pop('driven_plugs', [])
        converted_plugs = WeakList()
        for plug in driven_plugs:
            node_string, attr_string = plug.split('.')
            if node_string not in controller.named_objects:
                raise Exception('invalid plug node "%s"' % node_string)
            node = controller.named_objects[node_string]
            converted_plugs.append(controller.initialize_driven_plug(node, attr_string))
        network = controller.create_sdk_network(
            **blueprint
        )
        network.set_driven_plugs(converted_plugs)
        for x in sdk_groups_data:
            x = copy.deepcopy(x)
            keyframe_groups_data = x.pop('keyframe_groups')
            node_name, plug_name = x.pop('driver_plug').split('.')
            if node_name in existing_nodes:
                driver_node = existing_nodes[node_name]
            else:
                driver_node = controller.initialize_node(node_name)
                existing_nodes[node_name] = driver_node

            driver_plug = driver_node.plugs[plug_name]
            sdk_group = network.create_group(
                driver_plug=driver_plug,
                **x
            )
            for y in keyframe_groups_data:
                keyframes_data = y.pop('keyframes')
                for i in range(len(keyframes_data)):
                    key_data = keyframes_data[i]
                    converted_plugs[i].set_value(key_data['out_value'])
                sdk_group.create_keyframe_group(
                    **y
                )
        controller.dg_dirty()
        return network
    else:
        raise Exception('Invalid type "%s"' % object_type)

