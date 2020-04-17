import pytest
import random

import rig_factory.objects as obs
from rig_factory.controllers.object_controller import ObjectController
import rig_factory.objects.base_objects.properties as prp


def error_with_message(message):
    raise Exception(message)


def error_different_values(value_type, value_1, value_2):
    raise Exception('Error! Nodes have different {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_same_values(value_type, value_1, value_2):
    raise Exception('Error! Nodes have same {0}! Got {1} and {2}'.format(value_type, value_1, value_2))


def error_not_found(obj, location):
    raise Exception('Error! {0} not found in {1}.'.format(obj, location))


def error_is_found(obj, location):
    raise Exception('Error! {0} should not exist in {1}.'.format(obj, location))


def is_obj_base_node(item):
    # checks if item is an object of the BaseNode class
    return True if isinstance(item, obs.BaseNode) else False


def create_base_node(controller_val, root_name=None):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=root_name
    )
    return item


def test_create_base_node():
    """
    tests if BaseNode name, side, and index is None
    then tests if assigning a value to the BaseNode's name/side/index is the same as the value assigned to it
    """
    controller = ObjectController.get_controller()
    item_1 = create_base_node(controller, root_name='item_1')
    item_2 = create_base_node(controller, root_name='item_2')
    item_3 = create_base_node(controller, root_name='item_3')
    item_4 = create_base_node(controller, root_name='item_4')

    new_name = 'Issac'
    new_side = 'L'
    new_index = 2
    item_2.name = new_name
    item_3.side = new_side
    item_4.index = new_index
    assert item_1.name is 'item_1', error_different_values('name', item_1.name, 'item_1')
    assert item_1.name is not new_name, error_same_values('name', item_1.name, new_name)
    assert item_1.side is None, error_different_values('side', item_1.side, None)
    assert item_1.side is not new_side, error_same_values('side', item_1.side, new_side)
    assert item_1.index is None, error_different_values('index', item_1.index, None)
    assert item_1.index is not new_index, error_same_values('index', item_1.index, new_index)

    assert item_2.name is new_name, error_different_values('name', item_2.name, new_side)
    assert item_2.side is None, error_different_values('side', item_2.side, None)
    assert item_2.side is not new_side, error_same_values('side', item_2.side, new_side)
    assert item_2.index is None, error_different_values('index', item_2.index, None)
    assert item_2.index is not new_index, error_same_values('index', item_2.index, new_index)

    assert item_3.name is 'item_3', error_different_values('name', item_2.name, 'item_3')
    assert item_3.name is not new_name, error_different_values('name', item_2.name, new_name)
    assert item_3.side is new_side, error_different_values('side', item_2.side, new_side)
    assert item_3.index is None, error_different_values('index', item_2.index, None)
    assert item_3.index is not new_index, error_different_values('index', item_2.index, new_index)

    assert item_4.name is 'item_4', error_different_values('name', item_2.name, 'item_4')
    assert item_4.name is not new_name, error_different_values('name', item_2.name, new_name)
    assert item_4.side is None, error_different_values('side', item_2.side, None)
    assert item_4.side is not new_side, error_different_values('side', item_2.side, new_side)
    assert item_4.index is new_index, error_different_values('index', item_2.index, new_index)


def root_name_in_data_property(item):
    if is_obj_base_node(item):
        return True if item.root_name else False
    else:
        return False


def create_base_node_root_name(controller_val, root_name):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=root_name
    )
    return item


def test_root_name_data_property():
    """
    tests if root_name is in Data Property
    Note: by default, root_name is None
    """
    controller = ObjectController.get_controller()
    node_prp = 'root_name'
    default_root_name = 'test_{0}'.format(node_prp)
    name_a = 'main|body|arm|hand|finger'
    name_b = name_a.rsplit('|')[-1]
    name_c = 'other name'
    item_1 = create_base_node(controller, default_root_name)
    item_2 = create_base_node_root_name(controller, name_a)
    item_3 = create_base_node_root_name(controller, name_b)
    item_4 = create_base_node_root_name(controller, name_c)
    search_location = prp.DataProperty.__name__

    assert root_name_in_data_property(item_1) is True, error_not_found(node_prp.capitalize(), search_location)
    assert root_name_in_data_property(item_2) is True, error_not_found(node_prp.capitalize(), search_location)
    assert root_name_in_data_property(item_3) is True, error_not_found(node_prp.capitalize(), search_location)
    assert root_name_in_data_property(item_4) is True, error_not_found(node_prp.capitalize(), search_location)

    assert root_name_in_data_property(name_a) is False, error_is_found(name_a, search_location)
    assert root_name_in_data_property(name_b) is False, error_is_found(name_b, search_location)
    assert root_name_in_data_property(name_c) is False, error_is_found(name_c, search_location)
    assert root_name_in_data_property('blank') is False, error_is_found('blank', search_location)

    assert item_1.root_name is default_root_name, error_different_values(node_prp, item_1.root_name, default_root_name)
    assert item_2.root_name == name_a, error_different_values(node_prp, item_2.root_name, name_a)
    assert item_3.root_name == name_b, error_different_values(node_prp, item_3.root_name, name_b)
    assert item_4.root_name == name_c, error_different_values(node_prp, item_4.root_name, name_c)

    assert item_1.root_name != name_a, error_same_values(node_prp, item_1.root_name, name_a)
    assert item_1.root_name != name_b, error_same_values(node_prp, item_1.root_name, name_b)
    assert item_1.root_name != name_c, error_same_values(node_prp, item_1.root_name, name_c)
    assert item_2.root_name is not default_root_name, error_same_values(node_prp, item_2.root_name, default_root_name)

    assert item_2.root_name != name_b, error_same_values(node_prp, item_2.root_name, name_b)
    assert item_2.root_name != name_c, error_same_values(node_prp, item_2.root_name, name_c)
    assert item_3.root_name is not default_root_name, error_same_values(node_prp, item_3.root_name, default_root_name)

    assert item_3.root_name != name_a, error_same_values(node_prp, item_3.root_name, name_a)
    assert item_3.root_name != name_c, error_same_values(node_prp, item_3.root_name, name_c)
    assert item_4.root_name is not default_root_name, error_same_values(node_prp, item_4.root_name, default_root_name)
    assert item_4.root_name != name_a, error_same_values(node_prp, item_4.root_name, name_a)
    assert item_4.root_name != name_b, error_same_values(node_prp, item_4.root_name, name_b)


def name_in_data_property(item):
    if is_obj_base_node(item):
        return True if item.name else False
    else:
        return False


def create_base_node_name(controller_val, name):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=name
    )
    return item


def test_name_data_property():
    """
    tests if name is in Data Property
    Note: by default, name is None
    """
    controller = ObjectController.get_controller()
    node_prp = 'name'
    default_name = 'test_{0}'.format(node_prp)
    name_a = 'main|body|arm|hand|finger'
    name_b = name_a.rsplit('|')[-1]
    name_c = 'other name'
    item_1 = create_base_node(controller, default_name)
    item_2 = create_base_node_name(controller, name=name_a)
    item_3 = create_base_node_name(controller, name=name_b)
    item_4 = create_base_node_name(controller, name=name_c)
    search_location = prp.DataProperty.__name__

    assert name_in_data_property(item_1) is True, error_not_found(node_prp.capitalize(), search_location)
    assert name_in_data_property(item_2) is True, error_not_found(node_prp.capitalize(), search_location)
    assert name_in_data_property(item_3) is True, error_not_found(node_prp.capitalize(), search_location)
    assert name_in_data_property(item_4) is True, error_not_found(node_prp.capitalize(), search_location)

    assert name_in_data_property(name_a) is False, error_is_found(name_a, search_location)
    assert name_in_data_property(name_b) is False, error_is_found(name_b, search_location)
    assert name_in_data_property(name_c) is False, error_is_found(name_c, search_location)
    assert name_in_data_property('blank') is False, error_is_found('blank', search_location)

    assert item_1.name is default_name, error_different_values(node_prp, item_1.name, default_name)
    assert item_2.name == name_a, error_different_values(node_prp, item_2.name, name_a)
    assert item_3.name == name_b, error_different_values(node_prp, item_3.name, name_b)
    assert item_4.name == name_c, error_different_values(node_prp, item_4.name, name_c)

    assert item_1.name != name_a, error_same_values(node_prp, item_1.name, name_a)
    assert item_1.name != name_b, error_same_values(node_prp, item_1.name, name_b)
    assert item_1.name != name_c, error_same_values(node_prp, item_1.name, name_c)
    assert item_2.name is not default_name, error_same_values(node_prp, item_2.name, default_name)
    assert item_2.name != name_b, error_same_values(node_prp, item_2.name, name_b)
    assert item_2.name != name_c, error_same_values(node_prp, item_2.name, name_c)
    assert item_3.name is not default_name, error_same_values(node_prp, item_3.name, default_name)
    assert item_3.name != name_a, error_same_values(node_prp, item_3.name, name_a)
    assert item_3.name != name_c, error_same_values(node_prp, item_3.name, name_c)
    assert item_4.name is not default_name, error_same_values(node_prp, item_4.name, default_name)
    assert item_4.name != name_a, error_same_values(node_prp, item_4.name, name_a)
    assert item_4.name != name_b, error_same_values(node_prp, item_4.name, name_b)


def size_in_data_property(item):
    if is_obj_base_node(item):
        return True if item.size is not None else False
    else:
        return False


def create_base_node_size(controller_val, root_name, size):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=root_name,
        size=size
    )
    return item


def test_size_data_property():
    """
    tests if size is in Data Property
    Note: by default, size is 1.0
    """
    controller = ObjectController.get_controller()
    node_prp = 'size'
    default_size = 1.0
    size_a = 28.349
    size_b = 0.05467
    size_c = -6.057
    item_1 = create_base_node(controller)
    item_2 = create_base_node_size(controller, 'test_size2', size_a)
    item_3 = create_base_node_size(controller, 'test_size3', size_b)
    item_4 = create_base_node_size(controller, 'test_size4', size_c)
    search_location = prp.DataProperty.__name__

    assert size_in_data_property(item_1) is True, error_not_found(node_prp.capitalize(), search_location)
    assert size_in_data_property(item_2) is True, error_not_found(node_prp.capitalize(), search_location)
    assert size_in_data_property(item_3) is True, error_not_found(node_prp.capitalize(), search_location)
    assert size_in_data_property(item_4) is True, error_not_found(node_prp.capitalize(), search_location)

    assert size_in_data_property(size_a) is False, error_is_found(size_a, search_location)
    assert size_in_data_property(size_b) is False, error_is_found(size_b, search_location)
    assert size_in_data_property(size_c) is False, error_is_found(size_c, search_location)
    assert size_in_data_property(16794.523) is False, error_is_found(16794.523, search_location)

    assert item_1.size == default_size, error_different_values(node_prp, item_1.size, default_size)
    assert item_2.size == size_a, error_different_values(node_prp, item_2.size, size_a)
    assert item_3.size == size_b, error_different_values(node_prp, item_3.size, size_b)
    assert item_4.size == size_c, error_different_values(node_prp, item_4.size, size_c)

    assert item_1.size != size_a, error_same_values(node_prp, item_1.size, size_a)
    assert item_1.size != size_b, error_same_values(node_prp, item_1.size, size_b)
    assert item_1.size != size_c, error_same_values(node_prp, item_1.size, size_c)
    assert item_2.size is not default_size, error_same_values(node_prp, item_2.size, default_size)
    assert item_2.size != size_b, error_same_values(node_prp, item_2.size, size_b)
    assert item_2.size != size_c, error_same_values(node_prp, item_2.size, size_c)
    assert item_3.size is not default_size, error_same_values(node_prp, item_3.size, default_size)
    assert item_3.size != size_a, error_same_values(node_prp, item_3.size, size_a)
    assert item_3.size != size_c, error_same_values(node_prp, item_3.size, size_c)
    assert item_4.size is not default_size, error_same_values(node_prp, item_4.size, default_size)
    assert item_4.size != size_a, error_same_values(node_prp, item_4.size, size_a)
    assert item_4.size != size_b, error_same_values(node_prp, item_4.size, size_b)


def side_in_data_property(item):
    if is_obj_base_node(item):
        return True if item.side else False
    else:
        return False


def create_base_node_side(controller_val, root_name, side):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=root_name,
        side=side
    )
    return item


def test_side_data_property():
    """
    tests if side is in Data Property
    Note:
        -by default, side does not exist in Data Property
        -side is created AFTER giving it a value
    """
    controller = ObjectController.get_controller()
    node_prp = 'side'
    default_side = None
    side_a = 'L'
    side_b = 'R'
    side_c = 'C'
    item_1 = create_base_node(controller)
    item_2 = create_base_node_side(controller, 'side_a', side_a)
    item_3 = create_base_node_side(controller, 'side_b', side_b)
    item_4 = create_base_node_side(controller, 'side_c', side_c)
    search_location = prp.DataProperty.__name__

    assert side_in_data_property(item_1) is False, error_is_found(node_prp.capitalize(), search_location)
    assert side_in_data_property(item_2) is True, error_not_found(node_prp.capitalize(), search_location)
    assert side_in_data_property(item_3) is True, error_not_found(node_prp.capitalize(), search_location)
    assert side_in_data_property(item_4) is True, error_not_found(node_prp.capitalize(), search_location)

    assert side_in_data_property(side_a) is False, error_is_found(side_a, search_location)
    assert side_in_data_property(side_b) is False, error_is_found(side_b, search_location)
    assert side_in_data_property(side_c) is False, error_is_found(side_c, search_location)
    assert side_in_data_property('blank') is False, error_is_found('blank', search_location)

    assert item_1.side == default_side, error_different_values(node_prp, item_1.side, default_side)
    assert item_2.side == side_a, error_different_values(node_prp, item_2.side, side_a)
    assert item_3.side == side_b, error_different_values(node_prp, item_3.side, side_b)
    assert item_4.side == side_c, error_different_values(node_prp, item_4.side, side_c)

    assert item_1.side != side_a, error_same_values(node_prp, item_1.side, side_a)
    assert item_1.side != side_b, error_same_values(node_prp, item_1.side, side_b)
    assert item_1.side != side_c, error_same_values(node_prp, item_1.side, side_c)
    assert item_2.side is not default_side, error_same_values(node_prp, item_2.side, default_side)
    assert item_2.side != side_b, error_same_values(node_prp, item_2.side, side_b)
    assert item_2.side != side_c, error_same_values(node_prp, item_2.side, side_c)
    assert item_3.side is not default_side, error_same_values(node_prp, item_3.side, default_side)
    assert item_3.side != side_a, error_same_values(node_prp, item_3.side, side_a)
    assert item_3.side != side_c, error_same_values(node_prp, item_3.side, side_c)
    assert item_4.side is not default_side, error_same_values(node_prp, item_4.side, default_side)
    assert item_4.side != side_a, error_same_values(node_prp, item_4.side, side_a)
    assert item_4.side != side_b, error_same_values(node_prp, item_4.side, side_b)


def index_in_data_property(item):
    if is_obj_base_node(item):
        return True if item.index else False
    else:
        return False


def create_base_node_index(controller_val, root_name, index):
    controller = controller_val
    item = controller.create_object(
        obs.BaseNode,
        root_name=root_name,
        index=index
    )
    return item


def test_index_data_property():
    """
    tests if index is in Data Property
    Note:
        -by default, index does not exist in Data Property
        -index is created AFTER giving it a value
    """
    controller = ObjectController.get_controller()
    node_prp = 'index'
    default_index = None
    index_a = 1
    index_b = 2
    index_c = 3
    item_1 = create_base_node(controller)
    item_2 = create_base_node_index(controller, 'index_a', index_a)
    item_3 = create_base_node_index(controller, 'index_b', index_b)
    item_4 = create_base_node_index(controller, 'index_c', index_c)
    search_location = prp.DataProperty.__name__

    assert index_in_data_property(item_1) is False, error_is_found(node_prp.capitalize(), search_location)
    assert index_in_data_property(item_2) is True, error_not_found(node_prp.capitalize(), search_location)
    assert index_in_data_property(item_3) is True, error_not_found(node_prp.capitalize(), search_location)
    assert index_in_data_property(item_4) is True, error_not_found(node_prp.capitalize(), search_location)

    assert index_in_data_property(index_a) is False, error_is_found(index_a, search_location)
    assert index_in_data_property(index_b) is False, error_is_found(index_b, search_location)
    assert index_in_data_property(index_c) is False, error_is_found(index_c, search_location)
    assert index_in_data_property(154) is False, error_is_found(154, search_location)

    assert item_1.index == default_index, error_different_values(node_prp, item_1.index, default_index)
    assert item_2.index == index_a, error_different_values(node_prp, item_2.index, index_a)
    assert item_3.index == index_b, error_different_values(node_prp, item_3.index, index_b)
    assert item_4.index == index_c, error_different_values(node_prp, item_4.index, index_c)

    assert item_1.index != index_a, error_same_values(node_prp, item_1.index, index_a)
    assert item_1.index != index_b, error_same_values(node_prp, item_1.index, index_b)
    assert item_1.index != index_c, error_same_values(node_prp, item_1.index, index_c)
    assert item_2.index is not default_index, error_same_values(node_prp, item_2.index, default_index)
    assert item_2.index != index_b, error_same_values(node_prp, item_2.index, index_b)
    assert item_2.index != index_c, error_same_values(node_prp, item_2.index, index_c)
    assert item_3.index is not default_index, error_same_values(node_prp, item_3.index, default_index)
    assert item_3.index != index_a, error_same_values(node_prp, item_3.index, index_a)
    assert item_3.index != index_c, error_same_values(node_prp, item_3.index, index_c)
    assert item_4.index is not default_index, error_same_values(node_prp, item_4.index, default_index)
    assert item_4.index != index_a, error_same_values(node_prp, item_4.index, index_a)
    assert item_4.index != index_b, error_same_values(node_prp, item_4.index, index_b)


@pytest.fixture
def create_base_node_set_parent():
    controller = ObjectController.get_controller()
    root_name = 'default_root_name'
    obj_list = []
    list_range = 5
    for ind in range(list_range):
        name = '{0}_{1}'.format(root_name, str(ind))
        obj = controller.create_object(
            obs.BaseNode,
            root_name=name
        )
        obj_list.append(obj)
        if ind > 0:
            obj.set_parent(obj_list[ind-1])
    parent = obj_list[2]
    child = obj_list[3]
    return parent, child


def test_create_base_node_set_parent(create_base_node_set_parent):
    """
    checks if parent is a None or Transform Type
    checks if parent is not the same as child
    checks if parent is not any of it's descendants
    checks if parent is not any of it's ancestors
    """
    parent = create_base_node_set_parent[0]
    child = create_base_node_set_parent[1]
    descendant_list = parent.get_descendants()
    ancestor_list = parent.get_ancestors()
    test_item = 'just a string'

    assert parent is None or isinstance(parent, obs.BaseNode), error_with_message("Error! Invalid node type, '"
                                                                                  "{0}'".format(parent))

    assert parent != child, error_with_message("Error! Parent cannot be it's own child!")

    for descendant in descendant_list:
        assert parent != descendant, error_with_message("Error! Already parented to object, {0}".format(descendant))

    # NOTE: Ancestor list SHOULD NOT contain self #############################
    for num in range(len(ancestor_list) - 1):
        assert parent != ancestor_list[num], error_with_message("Error! Parent cannot be it's ancestor, "
                                                                "'{0}'".format(ancestor_list[num]))


def test_create_base_node_child(create_base_node_set_parent):
    """
    checks if child is not the same as parent
    checks if child is not any of it's descendants
    checks if child is not any of it's ancestors
    """
    parent = create_base_node_set_parent[0]
    child = create_base_node_set_parent[1]
    descendant_list = child.get_descendants()
    ancestor_list = child.get_ancestors()

    assert child != parent, error_with_message("Error! Child cannot be it's own parent!")

    for descendant in descendant_list:
        assert child != descendant, error_with_message("Error! Cannot be parented to it's child, "
                                                       "{0}".format(descendant))

    for num in range(len(ancestor_list) - 1):
        assert child != ancestor_list[num], error_with_message("Error! Child cannot be it's ancestor, "
                                                               "'{0}'".format(ancestor_list[num]))


def create_multiple_obj(controller):
    obj_list = []
    for ind in range(5):
        obj = controller.create_object(
            obs.BaseNode,
            root_name='root_name_' + str(ind),
            side='C',
            index=ind
        )
        obj_list.append(obj)

    for num in range(len(obj_list)):
        parent_num = random.randint(0, len(obj_list) - 1)
        if num != parent_num:
            obj_list[num].set_parent(obj_list[parent_num])
    return controller, obj_list


def test_serialize_obj():
    controller_1 = ObjectController.get_controller()
    controller_2 = ObjectController.get_controller()
    multiple_obj_list = create_multiple_obj(controller_1)
    controller_1 = multiple_obj_list[0]
    obj_list_1 = multiple_obj_list[1]
    data = controller_1.serialize()
    obj_list_1 = sorted(obj_list_1, key=lambda x: x.name)
    obj_list_2 = sorted(controller_2.deserialize(data), key=lambda x: x.name)

    for num in range(len(obj_list_1)):
        obj_1 = obj_list_1[num]
        obj_2 = obj_list_2[num]

        assert root_name_in_data_property(obj_1) is True, error_not_found(obj_1.root_name, list(obj.root_name for obj in obj_list_1))
        assert name_in_data_property(obj_1) is True, error_not_found(obj_1.name, obj_list_1)
        assert size_in_data_property(obj_1) is True, error_not_found(obj_1.size, obj_list_1)
        assert side_in_data_property(obj_1) is True, error_not_found(obj_1.side, obj_list_1)

        assert root_name_in_data_property(obj_2), error_not_found(obj_2, obj_list_2)
        assert name_in_data_property(obj_2), error_not_found(obj_2, obj_list_2)
        assert size_in_data_property(obj_2), error_not_found(obj_2, obj_list_2)
        assert side_in_data_property(obj_2), error_not_found(obj_2, obj_list_2)

        for key in prp.DataProperty.map[obj_1].keys():
            assert prp.DataProperty.map[obj_1][key] == prp.DataProperty.map[obj_2][key], \
                error_different_values(key.name, prp.DataProperty.map[obj_1][key], prp.DataProperty.map[obj_2][key])

