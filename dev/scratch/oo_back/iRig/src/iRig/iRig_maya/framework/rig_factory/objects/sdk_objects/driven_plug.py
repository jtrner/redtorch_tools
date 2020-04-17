from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class DrivenPlug(Plug):

    blend_node = ObjectProperty(
        name='blend_node'
    )

    default_value = DataProperty(
        name='default_value'
    )

    def create_in_scene(self):
        super(DrivenPlug, self).create_in_scene()
        self.default_value = self.get_value()

