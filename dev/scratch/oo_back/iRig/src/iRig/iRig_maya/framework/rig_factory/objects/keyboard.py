import rigging_widgets.widget_launchers.launch_widgets as lw
from rig_factory.objects.part_objects.handle import HandleGuide
x_count = 10
z_count = 4


for x in range(x_count):
    for z in range(z_count):
        lw.controller.root.create_part(
            HandleGuide,
            root_name='key_%s_%s' % (x, z)
        )