import os
import maya_tools
import rig_factory.objects as obs
from rig_factory.controllers.node_controller import NodeController
import rig_factory.objects.base_objects.properties as prp


def error_with_message(message):
    raise Exception(message)


def error_different_values(value_type, value_1, value_2):
    raise Exception('Error! Nodes have different {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_same_values(value_type, value_1, value_2):
    raise Exception('Error! Nodes have same {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_not_found(obj, obj_property, location):
    raise Exception("Error! {0}'s {1} not found in {2}.".format(obj, obj_property, location))


def error_is_found(obj, obj_property, location):
    raise Exception("Error! {0}'s {1} should not exist in {2}.".format(obj, obj_property, location))


def is_obj_depend_node(obj):
    # checks if item is an object of the DependNode class
    return True if isinstance(obj, obs.DependNode) else False


def create_depend_node():
    controller = NodeController.get_controller(mock=True)
    item = controller.create_object(
        obs.DependNode,
        node_type='condition',
        root_name='test_name'
    )
    return item


def test_create_depend_node():
    """
    tests if object is a DependNode
    """
    obj_a = create_depend_node()
    obj_b = create_depend_node()
    obj_c = create_depend_node()
    assert is_obj_depend_node(obj_a) is True, error_with_message('{0} is not a DependNode'.format(obj_a))
    assert is_obj_depend_node(obj_b) is True, error_with_message('{0} is not a DependNode'.format(obj_b))
    assert is_obj_depend_node(obj_c) is True, error_with_message('{0}is not a DependNode'.format(obj_c))


def is_node_type_in_data_property(item):
    if is_obj_depend_node(item):
        return True if 'node_type' in (key.name for key in prp.DataProperty.map[item].keys()) else False
    else:
        return False


def create_depend_node_node_type(node_type):
    controller = NodeController.get_controller(standalone=True)
    mc.loadPlugin('%s/shard_matrix.py' % os.path.dirname(maya_tools.__file__.replace('\\', '/')))
    item = controller.create_object(
        obs.DependNode,
        root_name='test_name',
        node_type=node_type
    )
    return item


def test_create_depend_node_node_type():
    """
    tests if node_type exists in DependNode's DataProperty
    """
    search_location = prp.DataProperty.__name__
    node_prp = 'node_type'
    obj_a = create_depend_node_node_type('condition')
    obj_b = create_depend_node_node_type('multMatrix')
    obj_c = create_depend_node_node_type('choice')
    assert is_node_type_in_data_property(obj_a) is True, error_not_found(obj_a, node_prp, search_location)
    assert is_node_type_in_data_property(obj_b) is True, error_not_found(obj_b, node_prp, search_location)
    assert is_node_type_in_data_property(obj_c) is True, error_not_found(obj_c, node_prp, search_location)


def is_existing_plugs_in_obj_dict_prp(item):
    if is_obj_depend_node(item):
        return True if 'existing_plugs' in (key.name for key in prp.ObjectDictProperty.map[item].keys()) else False
    else:
        return False


def create_depend_node_plug(node_type):
    controller = NodeController.get_controller(standalone=True)
    item = controller.create_object(
        obs.DependNode,
        root_name='test_name',
        node_type=node_type
    )
    item_plug = item.create_plug(
        'blend',
        at='double',
        k=True
    )
    return item


def test_is_existing_plugs_in_obj_dict_property():
    """
    tests if existing_plugs exists in DependNode's ObjectDictProperty
    """
    search_location = prp.ObjectDictProperty.__name__
    node_prp = 'existing_plugs'
    obj_a = create_depend_node_plug('choice')
    obj_b = create_depend_node_plug('polyCube')
    obj_c = create_depend_node_plug('condition')
    assert is_existing_plugs_in_obj_dict_prp(obj_a) is True, error_not_found(obj_a, node_prp, search_location)
    assert is_existing_plugs_in_obj_dict_prp(obj_b) is True, error_not_found(obj_b, node_prp, search_location)
    assert is_existing_plugs_in_obj_dict_prp(obj_c) is True, error_not_found(obj_c, node_prp, search_location)


def create_multiple_obj(controller):
    obj_list = []
    for ind in range(5):
        obj = controller.create_object(
            obs.DependNode,
            root_name='root_name_{0}'.format(ind),
            node_type='condition'
        )
        obj_list.append(obj)
    return controller, obj_list


def test_serialize_obj():
    controller_1 = NodeController.get_controller()
    controller_2 = NodeController.get_controller()
    multiple_obj_list = create_multiple_obj(controller_1)
    controller_1 = multiple_obj_list[0]
    obj_list_1 = multiple_obj_list[1]
    data = controller_1.serialize()
    obj_list_1 = sorted(obj_list_1, key=lambda x: x.root_name)
    obj_list_2 = sorted(controller_2.deserialize(data), key=lambda x: x.root_name)
    node_prp = 'node_type'

    for num in range(len(obj_list_1)):
        obj_1 = obj_list_1[num]
        obj_2 = obj_list_2[num]
        assert is_node_type_in_data_property(obj_1), error_not_found(obj_1, node_prp, obj_list_1)
        assert is_node_type_in_data_property(obj_2), error_not_found(obj_2, node_prp, obj_list_2)
        for key in prp.DataProperty.map[obj_1].keys():
            assert prp.DataProperty.map[obj_1][key] == prp.DataProperty.map[obj_2][key], \
                error_different_values(key.name, prp.DataProperty.map[obj_1][key], prp.DataProperty.map[obj_2][key])

#if __name__ == '__main__':
#    test_create_depend_node()
