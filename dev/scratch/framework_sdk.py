from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
from rig_math.matrix import Matrix

controller = RigController.get_controller()

root = controller.create_object(
    obs.Transform,
    root_name='root'
)

controller.set_root(root)


face_network = controller.create_object(
    obs.FaceNetwork,
    root_name='face'
)
sdk_network = controller.create_object(
    obs.SDKNetwork,
    root_name='face'
)
face_network.sdk_network = sdk_network

driven = controller.create_object(
    obs.GroupedHandle,
    root_name='driven',
    matrix=Matrix(),
    shape='cube',
    parent=root

)

driver = controller.create_object(
    obs.GroupedHandle,
    root_name='driver',
    matrix=Matrix(),
    shape='cube',
    parent=root
)

#face_network.add_driven_handles([driven])
face_network.sdk_network.initialize_driven_plugs(
    [driven.groups[-1]],
    ['tx', 'ty', 'tz']
)

group = face_network.create_group(
    root_name='brow_vertical',
    driver_plug=driver.plugs['tx']
)
face_target = group.create_face_target(driver_value=10.0)


group = face_network.create_group(
    root_name='brow_horizontal',
    driver_plug=driver.plugs['ty']
)

face_target.keyframe_group.update()


for g in face_network.face_groups:
    print 'Slider --->', g
    for t in g.face_targets:
            print 'Slider --->', t.keyframe_group, t.blendshape_inbetween