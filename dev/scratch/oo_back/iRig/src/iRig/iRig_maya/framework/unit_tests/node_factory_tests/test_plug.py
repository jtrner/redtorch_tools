import os

import maya.cmds as mc
import pytest

import maya_tools
from rig_factory.controllers.node_controller import NodeController
from rig_factory.controllers.object_controller import ObjectController
import rig_factory.objects as obs
import rig_factory.objects.base_objects.properties as prp


def error_with_message(message):
    raise Exception(message)


def error_different_values(value_type, value_1, value_2):
    raise Exception('Error! Plugs have different {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_same_values(value_type, value_1, value_2):
    raise Exception('Error! Plugs have same {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_not_found(obj, obj_property, location):
    raise Exception("Error! {0}'s {1} not found in {2}.".format(obj, obj_property, location))


def error_is_found(obj, obj_property, location):
    raise Exception("Error! {0}'s {1} should not exist in {2}.".format(obj, obj_property, location))


def is_obj_plug(obj):
    # checks if item is an object of the DependNode class
    return True if isinstance(obj, obs.Plug) else False


def create_plugs_simple():
    controller = NodeController.get_controller(standalone=True)
    mc.loadPlugin('%s/shard_matrix.py' % os.path.dirname(maya_tools.__file__.replace('\\', '/')))
    obj = controller.create_object(
        obs.DependNode,
        node_type='condition',
        root_name='blend_weighted'
    )
    obj_plug = obj.create_plug(
        'blend',
        at='double',
        k=True
    )
    return obj_plug


def create_obj_simple():
    controller = ObjectController.get_controller()
    obj_a = controller.create_object(
        obs.BaseNode
    )
    obj_b = controller.create_object(
        obs.BaseObject,
        root_name='base_obj'
    )
    return obj_a, obj_b


def test_create_obj_plugs():
    """
    tests if the obj is a Plug
    """
    plug_a = create_plugs_simple()
    plug_b = create_plugs_simple()
    obj_a, obj_b = create_obj_simple()
    assert is_obj_plug(plug_a) is True, error_with_message('{0} is not a Plug.'.format(plug_a))
    assert is_obj_plug(plug_b) is True, error_with_message('{0} is not a Plug.'.format(plug_b))
    assert is_obj_plug(obj_a) is False, error_with_message('{0} is a Plug.'.format(obj_a))
    assert is_obj_plug(obj_b) is False, error_with_message('{0} is a Plug.'.format(obj_b))


def is_prp_in_data_prp(item, item_prp):
    if is_obj_plug(item):
        return True if item_prp in (key.name for key in prp.DataProperty.map[item].keys()) else False
    else:
        return False


@pytest.mark.parametrize("plug_prp", ['user_defined'])
def test_prp_in_data_prp(plug_prp):
    """
    test if 'create_data', 'value', 'user_defined' is in plug's DataProperty
    """
    search_location = prp.DataProperty.__name__
    plug_a = create_plugs_simple()
    plug_b = create_plugs_simple()
    obj_a, obj_b = create_obj_simple()
    assert is_prp_in_data_prp(plug_a, plug_prp) is True, error_not_found(plug_a, plug_prp, search_location)
    assert is_prp_in_data_prp(plug_b, plug_prp) is True, error_not_found(plug_b, plug_prp, search_location)
    assert is_prp_in_data_prp(obj_a, plug_prp) is False, error_is_found(obj_a, plug_prp, search_location)
    assert is_prp_in_data_prp(obj_b, plug_prp) is False, error_is_found(obj_b, plug_prp, search_location)


def is_prp_in_obj_prp(item, item_prp):
    if is_obj_plug(item):
        return True if item_prp in (key.name for key in prp.ObjectProperty.map[item].keys()) else False
    else:
        return False


@pytest.mark.parametrize("plug_prp", ['array_plug'])
def test_prp_in_obj_prp(plug_prp):
    """
    tests:
    -if 'array_plug' is in plug's DataProperty
    -if plug is an array
    -if 'element' is an element
    -if element's parent == weights_plug
    -if element's get_node == blend_weighted_node
    """
    search_location = prp.ObjectProperty.__name__
    controller = NodeController.get_controller(standalone=True)
    blend_weighted_node = controller.create_object(
        obs.DependNode,
        root_name='test_node',
        node_type='blendWeighted'
    )
    weights_plug = blend_weighted_node.initialize_plug('weight')
    element_plug = weights_plug.element(0)
    obj_a = create_obj_simple()[0]
    obj_b = create_obj_simple()[1]

    assert is_prp_in_obj_prp(element_plug, plug_prp) is True, error_not_found(element_plug, plug_prp, search_location)
    assert is_prp_in_obj_prp(weights_plug, plug_prp) is False, error_is_found(weights_plug, plug_prp, search_location)
    assert is_prp_in_obj_prp(obj_a, plug_prp) is False, error_is_found(obj_a, plug_prp, search_location)
    assert is_prp_in_obj_prp(obj_b, plug_prp) is False, error_is_found(obj_b, plug_prp, search_location)

    assert weights_plug.is_array() is True, error_with_message('{0} is not an array.'.format(weights_plug))
    assert weights_plug.is_element() is False, error_with_message('{0} is an element.'.format(weights_plug))

    assert element_plug.is_array() is False, error_with_message('{0} is an array.'.format(element_plug))
    assert element_plug.is_element() is True, error_with_message('{0} is not an element.'.format(element_plug))

    assert element_plug.parent == weights_plug, error_different_values('parent', element_plug.parent, weights_plug)
    assert element_plug.get_node() == blend_weighted_node, \
        error_different_values('parent node', element_plug.get_node(), blend_weighted_node)


def is_prp_in_obj_dict_prp(item, item_prp):
    if is_obj_plug(item):
        return True if item_prp in (key.name for key in prp.ObjectDictProperty.map[item].keys()) else False
    else:
        return False


def test_prp_in_obj_dict_prp():
    """
    tests:
     -if 'elements' and 'child_plugs' is in plug's ObjectDictProperty
     -if 'elements' is an element
     -if 'child_plugs' is an array

    """
    search_location = prp.ObjectDictProperty.__name__
    prp_element = 'elements'
    prp_child_plugs = 'child_plugs'
    controller = NodeController.get_controller()
    transform_obj = controller.create_object(
        obs.Transform,
        root_name='test_transform'
    )
    translate_plug = transform_obj.initialize_plug('translate')
    rotate_plug = transform_obj.initialize_plug('rotate')
    sel_handle_plug = transform_obj.initialize_plug('selectHandle')
    world_matrix_plug = transform_obj.initialize_plug('worldMatrix')
    parent_matrix_plug = transform_obj.initialize_plug('parentMatrix')

    translate_child = translate_plug.child(0)
    rotate_child = rotate_plug.child(1)
    sel_handle_child = sel_handle_plug.child(2)
    world_matrix_element = world_matrix_plug.element(0)
    world_matrix_element_extra = world_matrix_plug.element(1)
    parent_matrix_element = parent_matrix_plug.element(0)

    blend_weighted_node = controller.create_object(
        obs.DependNode,
        root_name='test_node',
        node_type='blendWeighted'
    )
    weights_plug = blend_weighted_node.initialize_plug('weight')
    element_plug = weights_plug.element(0)

    plug_c = create_obj_simple()[0]
    plug_d = create_obj_simple()[1]

    assert is_prp_in_obj_dict_prp(translate_plug, prp_child_plugs) is True, \
        error_not_found(translate_plug, prp_child_plugs, search_location)
    assert is_prp_in_obj_dict_prp(translate_plug, prp_element) is False, \
        error_is_found(translate_plug, prp_element, search_location)
    assert translate_plug.is_element() is False, error_with_message('{0} is an element.'.format(translate_plug))
    assert translate_plug.is_array() is False, error_with_message('{0} is an array.'.format(translate_plug))

    assert is_prp_in_obj_dict_prp(rotate_plug, prp_child_plugs) is True, \
        error_not_found(rotate_plug, prp_child_plugs, search_location)
    assert is_prp_in_obj_dict_prp(rotate_plug, prp_element) is False, \
        error_is_found(rotate_plug, prp_element, search_location)
    assert rotate_plug.is_element() is False, error_with_message('{0} is an element.'.format(rotate_plug))
    assert rotate_plug.is_array() is False, error_with_message('{0} is an array.'.format(rotate_plug))

    assert is_prp_in_obj_dict_prp(sel_handle_plug, prp_child_plugs) is True, \
        error_not_found(sel_handle_plug, prp_child_plugs, search_location)
    assert is_prp_in_obj_dict_prp(sel_handle_plug, prp_element) is False, \
        error_is_found(sel_handle_plug, prp_element, search_location)
    assert sel_handle_plug.is_element() is False, error_with_message('{0} is an element.'.format(sel_handle_plug))
    assert sel_handle_plug.is_array() is False, error_with_message('{0} is an array.'.format(sel_handle_plug))

    assert is_prp_in_obj_dict_prp(world_matrix_plug, prp_element) is True, \
        error_not_found(world_matrix_plug, prp_element, search_location)
    assert is_prp_in_obj_dict_prp(world_matrix_plug, prp_child_plugs) is False, \
        error_is_found(world_matrix_plug, prp_child_plugs, search_location)
    assert world_matrix_plug.is_element() is False, error_with_message('{0} is an element.'.format(world_matrix_plug))
    assert world_matrix_plug.is_array() is True, error_with_message('{0} is not an array.'.format(world_matrix_plug))

    assert is_prp_in_obj_dict_prp(parent_matrix_plug, prp_element) is True, \
        error_not_found(parent_matrix_plug, prp_element, search_location)
    assert is_prp_in_obj_dict_prp(parent_matrix_plug, prp_child_plugs) is False, \
        error_is_found(parent_matrix_plug, prp_child_plugs, search_location)
    assert parent_matrix_plug.is_element() is False, error_with_message('{0} is an element.'.format(parent_matrix_plug))
    assert parent_matrix_plug.is_array() is True, error_with_message('{0} is not an array.'.format(parent_matrix_plug))

    assert is_prp_in_obj_dict_prp(weights_plug, prp_element) is True, \
        error_not_found(weights_plug, prp_element, search_location)
    assert is_prp_in_obj_dict_prp(weights_plug, prp_child_plugs) is False, \
        error_is_found(weights_plug, prp_child_plugs, search_location)
    assert weights_plug.is_element() is False, error_with_message('{0} is an element.'.format(weights_plug))
    assert weights_plug.is_array() is True, error_with_message('{0} is not an array.'.format(weights_plug))

    assert element_plug.is_element() is True, error_with_message('{0} is not an element.'.format(element_plug))
    assert element_plug.is_array() is False, error_with_message('{0} is an array.'.format(element_plug))

    assert is_prp_in_obj_dict_prp(plug_c, prp_element) is False, error_is_found(plug_c, prp_element, search_location)
    assert is_prp_in_obj_dict_prp(plug_c, prp_child_plugs) is False, error_is_found(plug_c, prp_child_plugs,
                                                                                    search_location)
    assert is_prp_in_obj_dict_prp(plug_d, prp_element) is False, error_is_found(plug_d, prp_element, search_location)
    assert is_prp_in_obj_dict_prp(plug_d, prp_child_plugs) is False, error_is_found(plug_d, prp_child_plugs,
                                                                                    search_location)

    assert translate_child in translate_plug.children, \
        error_not_found(translate_child, 'child', translate_plug.children)
    assert rotate_child in rotate_plug.children, \
        error_not_found(rotate_child, 'child', rotate_plug.children)
    assert sel_handle_child in sel_handle_plug.children, \
        error_not_found(sel_handle_child, 'child', sel_handle_plug.children)
    assert world_matrix_element in world_matrix_plug.children, \
        error_not_found(world_matrix_element, 'element', world_matrix_plug.children)
    assert world_matrix_element_extra in world_matrix_plug.children, \
        error_not_found(world_matrix_element_extra, 'element', world_matrix_plug.children)
    assert parent_matrix_element in parent_matrix_plug.children, \
        error_not_found(parent_matrix_element, 'element', parent_matrix_plug.children)

    assert translate_plug.get_node() == transform_obj, \
        error_different_values(type(transform_obj), translate_plug.get_node(), transform_obj)
    assert rotate_plug.get_node() == transform_obj, \
        error_different_values(type(transform_obj), rotate_plug.get_node(), transform_obj)
    assert sel_handle_plug.get_node() == transform_obj, \
        error_different_values(type(transform_obj), sel_handle_plug.get_node(), transform_obj)
    assert world_matrix_plug.get_node() == transform_obj, \
        error_different_values(type(transform_obj), world_matrix_plug.get_node(), transform_obj)
    assert parent_matrix_plug.get_node() == transform_obj, \
        error_different_values(type(transform_obj), parent_matrix_plug.get_node(), transform_obj)

    assert translate_child.get_node() == transform_obj, \
        error_different_values(type(transform_obj), translate_child.get_node(), transform_obj)
    assert rotate_child.get_node() == transform_obj, \
        error_different_values(type(transform_obj), rotate_child.get_node(), transform_obj)
    assert sel_handle_child.get_node() == transform_obj, \
        error_different_values(type(transform_obj), sel_handle_child.get_node(), transform_obj)
    assert world_matrix_element.get_node() == transform_obj, \
        error_different_values(type(transform_obj), world_matrix_element.get_node(), transform_obj)
    assert world_matrix_element_extra.get_node() == transform_obj, \
        error_different_values(type(transform_obj), world_matrix_element_extra.get_node(), transform_obj)
    assert parent_matrix_element.get_node() == transform_obj, \
        error_different_values(type(transform_obj), parent_matrix_element.get_node(), transform_obj)


if __name__ == '__main__':
    pass
