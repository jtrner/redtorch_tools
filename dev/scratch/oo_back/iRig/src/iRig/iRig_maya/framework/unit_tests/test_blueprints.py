"""
Checks if serialized then deserialized object data matches with in scene object data
Create ContainerGuide then create parts (obs.PartGuide.__subclasses__())
Tests:
- Number of objects
- uuid of Data Properties, Object Properties, Object List Properties, Object Dict Properties

NOTE: when testing in "mock", comment mc.loadPlugin for shard_matrix (mock is not a Maya environment)
"""

import os

#import maya.cmds as mc

import maya_tools
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, ObjectDictProperty
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs

obs.register_classes()
controller = RigController.get_controller(mock=True)
#mc.loadPlugin('%s/shard_matrix.py' % os.path.dirname(maya_tools.__file__.replace('\\', '/')))

controller.root = controller.create_object(
    obs.ContainerGuide,
    root_name='root'
)

for index, class_guide in enumerate(obs.PartGuide.__subclasses__()):
    class_name = class_guide.__name__
    # TODO: TEMP!! After BipedMain (and other biped objects) refactor, run tests to ensure objects are valid 8.28.2019
    if 'BipedMain' not in class_name and 'Chain' not in class_name:
        class_obj = controller.root.create_part(
            class_guide,
            root_name='{0}_{1}'.format(index, class_name),
            count=3
        )


def uuid_test():
    data = controller.serialize()
    controller.reset()
    controller.deserialize(data)

    objects = controller.objects

    object_data = data['objects']
    assert len(objects) == len(object_data)

    for od in object_data:
        # Get uuid from serialized data
        the_uuid = od['values']['uuid']
        # Lookup object by uuid
        assert the_uuid in objects
        the_object = objects[the_uuid]

        # data property ----
        # get dict of all properties of the object
        item_dict = DataProperty.map.get(the_object, dict())
        for prp in item_dict:
            assert prp.name in od['values']
            od_prp = od['values'][prp.name]
            relationship_uuid = item_dict[prp]
            assert od_prp == relationship_uuid

        # object property ----
        # get dict of all object properties for object
        item_dict = ObjectProperty.map.get(the_object, dict())

        # iterate keys (ObjectProperty instances)
        for prp in item_dict:
            # Get Relationship object
            relationship_object = item_dict[prp]()
            # Make sure property name "parent" is in objectData
            assert prp.name in od['objects']
            # Get Relationship uuid
            relationship_uuid = od['objects'][prp.name]
            # make sure uuids match between data and actual object
            assert relationship_uuid == relationship_object.uuid

        # object list property ----
        # get dict of all object properties for object
        item_dict = ObjectListProperty.map.get(the_object, dict())

        # iterate keys (ObjectListProperty instances)
        for prp in item_dict:
            # Get Relationship object
            relationship_object_list = item_dict[prp]
            assert prp.name in od['objects']
            relationship_uuid_list = od['objects'][prp.name]
            for relationship_object in relationship_object_list:
                assert relationship_object.uuid in relationship_uuid_list

        # object dict prp ----
        item_dict = ObjectDictProperty.map.get(the_object, dict())

        for prp in item_dict:
            object_dict = item_dict[prp]
            for key in object_dict:
                relationship_object = object_dict[key]
                if relationship_object:
                    data_dict = od['objects'][prp.name]
                    assert key in data_dict
                    assert relationship_object.uuid == data_dict[key]
                # print relationship_object


# py test
def test_blueprint():
    uuid_test()
    controller.toggle_state()
    uuid_test()
    controller.toggle_state()
    uuid_test()


# unittest
if __name__ == '__main__':
    uuid_test()
    controller.toggle_state()
    uuid_test()
    controller.toggle_state()
    uuid_test()
