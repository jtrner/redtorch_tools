from rig_factory.rig_controller import RigController
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.part_objects.teeth import TeethGuide

controller = RigController.get_controller(standalone=True)


controller.root = controller.create_object(
    ContainerGuide,
    root_name='body'
)

controller.root.import_geometry('C:/Users/paxtong/Desktop/nostril.abc')
bend_part = controller.root.create_part(
    TeethGuide,
    root_name='bendy'
)
controller.root = controller.toggle_state()
controller.root.parts[0].add_geometry([controller.root.geometry['body_GeoShape']])
