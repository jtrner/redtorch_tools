import pytest
import uuid

from rig_factory.controllers.object_controller import ObjectController
import rig_factory.objects as obs
import rig_factory.objects.base_objects.properties as prp


def error_is_different(value_1, value_2):
    raise Exception('Error! Values should be the same; \nGot {0} and {1}'.format(value_1, value_2))


def error_is_same(value_1, value_2):
    raise Exception('Error! Values should be different; \nGot {0} and {1}'.format(value_1, value_2))


def error_not_found(obj, location):
    raise Exception('Error! {0} not found in {1}; \nGot type: {2}, value: {0}'.format(obj, location, type(obj)))


def error_is_found(obj, location):
    raise Exception('Error! {0} should not exist in {1}.'.format(obj, location))


def pass_controller(controller_val):
    controller_val.create_object(
        obs.BaseObject,
        root_name='item_1'
    )
    return controller_val


def test_pass_controller():
    """
    tests if controller passed to pass_controller is the same value when returned via object's controller attribute
    """
    controller_a = ObjectController.get_controller()
    controller_b = ObjectController.get_controller()
    controller_c = ObjectController.get_controller()

    assert pass_controller(controller_a) == controller_a, error_is_different(pass_controller(controller_a),
                                                                             controller_a)
    assert pass_controller(controller_b) == controller_b, error_is_different(pass_controller(controller_b),
                                                                             controller_b)
    assert pass_controller(controller_c) == controller_c, error_is_different(pass_controller(controller_c),
                                                                             controller_c)
    assert pass_controller(controller_a) != controller_b, error_is_same(pass_controller(controller_a), controller_b)
    assert pass_controller(controller_a) != controller_c, error_is_same(pass_controller(controller_a), controller_c)
    assert pass_controller(controller_b) != controller_c, error_is_same(pass_controller(controller_b), controller_c)


def pass_uuid_to_obj(uuid_val):
    controller = ObjectController.get_controller()

    item_1 = controller.create_object(
        obs.BaseObject,
        root_name='item_1',
        uuid=uuid_val
    )
    item_2 = controller.create_object(
        obs.BaseObject,
        root_name='item_2',
        uuid='other_uuid'
    )
    return item_1.uuid, item_2.uuid


def test_pass_uuid_to_obj():
    """
    tests if uuid passed to object is the same uuid
    """
    uuid_str = 'test_uuid'

    assert pass_uuid_to_obj(uuid_str)[0] == uuid_str, error_is_different(pass_uuid_to_obj(uuid_str)[0], uuid_str)
    assert pass_uuid_to_obj(uuid_str)[1] != uuid_str, error_is_same(pass_uuid_to_obj(uuid_str)[1], uuid_str)
    assert pass_uuid_to_obj(uuid_str)[1] == 'other_uuid', error_is_different(pass_uuid_to_obj(uuid_str)[1],
                                                                             'other_uuid')


@pytest.fixture()
def create_base_object():
    controller = ObjectController.get_controller()
    uuid_str = str(uuid.uuid4())

    item_1 = controller.create_object(
        obs.BaseObject,
        root_name='item_1',
        uuid=uuid_str
    )
    item_2 = controller.create_object(
        obs.BaseObject,
        root_name='item_2',
        uuid='other_uuid'
    )
    item_3 = controller.create_object(
        obs.BaseObject,
        root_name='item_3'
    )
    item_4 = str(uuid.uuid4())
    item_5 = str(uuid.uuid4())

    return controller, item_1, item_2, item_3, item_4, item_5


def is_obj_base_object(item):
    # checks if item is an object of the BaseObject class
    return True if isinstance(item, obs.BaseObject) else False


def item_in_data_property(item):
    return True if item in prp.DataProperty.map else False


def test_item_in_data_property(create_base_object):
    """
    test if object is in Data Property
    """
    search_location = prp.DataProperty.__name__
    item_1 = create_base_object[1]
    item_2 = create_base_object[2]
    item_3 = create_base_object[3]
    item_4 = create_base_object[4]
    item_5 = create_base_object[5]

    assert item_in_data_property(item_1) is True, error_not_found(item_1, search_location)
    assert item_in_data_property(item_2) is True, error_not_found(item_2, search_location)
    assert item_in_data_property(item_3) is True, error_not_found(item_3, search_location)
    assert item_in_data_property(item_4) is False, error_is_found(item_4, search_location)
    assert item_in_data_property(item_5) is False, error_is_found(item_5, search_location)


def uuid_in_data_property(item):
    if is_obj_base_object(item):
        return True if item.uuid else False
    else:
        return False


def test_uuid_in_data_property(create_base_object):
    """
    tests if uuid is in Data Property
    """
    search_location = prp.DataProperty.__name__
    item_1 = create_base_object[1]
    item_2 = create_base_object[2]
    item_3 = create_base_object[3]
    item_4 = create_base_object[4]
    item_5 = create_base_object[5]

    assert uuid_in_data_property(item_1) is True, error_not_found(item_1, search_location)
    assert uuid_in_data_property(item_2) is True, error_not_found(item_2, search_location)
    assert uuid_in_data_property(item_3) is True, error_not_found(item_3, search_location)
    assert uuid_in_data_property(item_4) is False, error_is_found(item_4, search_location)
    assert uuid_in_data_property(item_5) is False, error_is_found(item_5, search_location)


def test_return_uuid(create_base_object):
    """
    tests if uuid is the same as the object's uuid
    """
    item_1 = create_base_object[1]
    item_2 = create_base_object[2]
    item_3 = create_base_object[3]
    item_4 = create_base_object[4]
    item_5 = create_base_object[5]

    assert item_1.uuid == item_1.uuid, error_is_different(item_1.uuid, item_1.uuid)
    assert item_2.uuid == item_2.uuid, error_is_different(item_2.uuid, item_2.uuid)
    assert item_3.uuid == item_3.uuid, error_is_different(item_3.uuid, item_3.uuid)

    assert item_4 != item_5, error_is_same(item_4, item_5)
    assert item_1.uuid != item_4, error_is_same(item_1, item_4)
    assert item_2.uuid != item_4, error_is_same(item_2, item_4)
    assert item_3.uuid != item_4, error_is_same(item_3, item_4)
    assert item_1.uuid != item_5, error_is_same(item_1, item_5)
    assert item_2.uuid != item_5, error_is_same(item_2, item_5)
    assert item_3.uuid != item_5, error_is_same(item_3, item_5)


def create_multiple_obj(controller):
    obj_list = []
    for ind in range(5):
        obj = controller.create_object(
            obs.BaseObject,
            root_name='root_name_'+str(ind)
        )
        obj_list.append(obj)
    return controller, obj_list


def test_serialize_obj():
    controller_1 = ObjectController.get_controller()
    controller_2 = ObjectController.get_controller()
    multiple_obj_list = create_multiple_obj(controller_1)
    controller_1 = multiple_obj_list[0]
    obj_list_1 = multiple_obj_list[1]
    data = controller_1.serialize()
    obj_list_1 = sorted(obj_list_1, key=lambda x: x.uuid)
    obj_list_2 = sorted(controller_2.deserialize(data), key=lambda x: x.uuid)

    for num in range(len(obj_list_1)):
        obj_1 = obj_list_1[num]
        obj_2 = obj_list_2[num]
        assert uuid_in_data_property(obj_1), error_not_found(obj_1, obj_list_1)
        assert uuid_in_data_property(obj_2), error_not_found(obj_2, obj_list_2)
        assert obj_1.uuid == obj_2.uuid, error_is_different(obj_1.uuid, obj_2.uuid)
        for key in prp.DataProperty.map[obj_1].keys():
            assert prp.DataProperty.map[obj_1][key] == prp.DataProperty.map[obj_1][key], \
                error_is_different(prp.DataProperty.map[obj_1][key], prp.DataProperty.map[obj_2][key])

