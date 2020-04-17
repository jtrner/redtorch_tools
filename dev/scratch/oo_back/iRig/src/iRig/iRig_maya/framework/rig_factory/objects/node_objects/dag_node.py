from depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty


class DagNode(DependNode):

    shader = ObjectProperty(
        name='shader'
    )
    visible = True

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DagNode, cls).create(controller, **kwargs)
        return this

    def __init__(self, **kwargs):
        super(DagNode, self).__init__(**kwargs)
        self.visible = True

    def assign_shading_group(self, shading_group):
        self.controller.assign_shading_group(
            shading_group,
            self
        )

    def get_dag_path(self):
        return self.controller.get_dag_path(self)

    def create_in_scene(self):
        if isinstance(self.parent, DagNode):
            self.m_object = self.controller.scene.create_dag_node(
                self.node_type,
                self.name,
                self.parent.m_object
            )
        else:
            self.m_object = self.controller.scene.create_dag_node(
                self.node_type,
                self.name
            )
