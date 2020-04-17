import os
os.environ['TT_PROJCODE'] = 'GRM'
os.environ['TT_ENTNAME'] = 'gizmo'
from rig_factory.objects.standard_biped_objects.standard_spine import StandardSpineGuide
from rig_factory.controllers.rig_controller import RigController
from rig_factory.objects.part_objects.container import ContainerGuide

controller = RigController.get_controller(standalone=True)

controller.root = controller.create_object(
    ContainerGuide,
    root_name='root'
)

spine = controller.root.create_part(
    StandardSpineGuide,
    root_name='spine',
    side='center'
)

rig = controller.toggle_state()
