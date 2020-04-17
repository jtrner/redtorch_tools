import json
from rig_factory.controllers.rig_controller import RigController
from rig_factory.objects import *


def create_all_handle_shapes():

    controller = RigController.get_controller()
    controller.root = controller.create_object(
        Container,
        root_name='root'
    )
    part = controller.root.create_part(
        Part,
        root_name='part'
    )
    with open('D:/pipeline/paxtong/dev/git_repo/rigging_framework/rig_factory/handle_shapes.json', mode='r') as f:
        for i, shape_type in enumerate(json.loads(f.read())):
            handle = part.create_handle(
                shape=shape_type,
                root_name=shape_type
            )
            handle.plugs['tx'].set_value(i)
