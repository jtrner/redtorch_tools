import sys;sys.path.insert(0, 'D:/rigging_library')
from rig_factory.objects.standard_biped_objects.standard_leg import StandardIKFKLegGuide
from rig_factory.controllers.rig_controller import RigController
from rig_factory.objects.part_objects.container import ContainerGuide

controller = RigController.get_controller(standalone=True)

controller.root = controller.create_object(
    ContainerGuide,
    root_name='root'
)

leg = controller.root.create_part(
    StandardIKFKLegGuide,
    root_name='leg',
    side='left'
)

rig = controller.toggle_state()
