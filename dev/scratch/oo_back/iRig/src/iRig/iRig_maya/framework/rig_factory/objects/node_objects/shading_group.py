from depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectListProperty


class ShadingGroup(DependNode):

    shaders = ObjectListProperty(
        name='shaders'
    )

    def __init__(self, **kwargs):
        super(ShadingGroup, self).__init__(**kwargs)
        self.node_type = 'shadingEngine'

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_shading_group(
            self.name
        )
