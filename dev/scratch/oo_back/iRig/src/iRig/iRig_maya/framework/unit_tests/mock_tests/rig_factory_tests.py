import json
from object_factory.objects.properties import ObjectProperty
from rig_factory.rig_controller import RigController


controller = RigController.get_controller(standalone=True)

with open('D:/pipeline/paxtong/dev/git_repo/rigging_framework/rig_builder/blueprints/standard_biped.json', mode='r') as f:
    blueprint = json.loads(f.read())
controller.build_blueprint(blueprint)

data = controller.serialize()
controller.reset()
controller.deserialize(data)

'''
len(objects), len(object_data)

for x in object_data:
    data_uuid = x['values']['uuid']
    assert data_uuid in objects
    item_dict = ObjectProperty.map.get(objects[data_uuid], dict())
    for prp in item_dict:
        property_dict = item_dict[prp]
        for y in property_dict:
        assert prp.name in x['objects']
        property_data_uuid = x['objects'][prp.name]
        assert prp.uuid == property_data_uuid
'''