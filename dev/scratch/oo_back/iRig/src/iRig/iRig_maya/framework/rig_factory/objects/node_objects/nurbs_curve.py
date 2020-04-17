from dag_node import DagNode
from rig_factory.objects.base_objects.properties import DataProperty


class NurbsCurve(DagNode):

    positions = DataProperty(
        name='positions'
    )
    degree = DataProperty(
        name='degree'
    )
    form = DataProperty(
        name='form'
    )

    def __init__(self, **kwargs):
        kwargs['positions'] = [list(x) for x in kwargs.get('positions', [])]
        super(NurbsCurve, self).__init__(**kwargs)
        self.node_type = 'nurbsCurve'

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('degree', 3)
        kwargs.setdefault('form', 0)
        if not kwargs['parent']:
            raise Exception('Cannot create a NurbsCurve without a parent')
        return super(NurbsCurve, cls).create(controller, **kwargs)

    def get_curve_data(self):
        return self.controller.get_curve_data(self)

    def create_in_scene(self):
        if self.positions:
            self.m_object = self.controller.scene.draw_nurbs_curve(
                self.positions,
                self.degree,
                self.form,
                self.name,
                self.parent.m_object
            )
        else:
            self.m_object = self.controller.scene.create_dag_node(
                self.node_type,
                self.name,
                self.parent.m_object
            )
