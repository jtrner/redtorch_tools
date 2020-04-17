from depend_node import DependNode
from shading_group import ShadingGroup
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.base_objects.weak_list import WeakList

class Shader(DependNode):

    shading_group = ObjectProperty(
        name='shading_group'
    )

    def __init__(self, **kwargs):

        super(Shader, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Shader, cls).create(controller, **kwargs)
        shading_group = controller.create_object(
            ShadingGroup,
            root_name=this.root_name,
            index=this.index,
            side=this.side,
            parent=this
        )
        this.plugs['outColor'].connect_to(shading_group.plugs['surfaceShader'])
        this.shading_group = shading_group
        shading_group.shaders.append(this)
        return this

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_shader(
            self.node_type,
            self.name
        )

    def teardown(self):
        if len(self.shading_group.shaders) < 2:
            self.controller.delete_objects(
                WeakList([self.shading_group]),
                collect=self.controller.garbage_collection
            )
        super(Shader, self).teardown()
