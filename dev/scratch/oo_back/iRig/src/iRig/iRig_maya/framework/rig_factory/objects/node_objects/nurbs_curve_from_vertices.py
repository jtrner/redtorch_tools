from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectListProperty
)


class NurbsCurveFromVertices(DagNode):

    # Required kwargs
    mesh_name = DataProperty(
        name='mesh_name',
    )
    vertices = DataProperty(
        name='vertices',
    )

    # Optional kwargs
    degree = DataProperty(
        name='degree',
    )
    form = DataProperty(
        name='form',
    )

    construction_history = ObjectListProperty(
        name='construction_history',
    )

    def __init__(self, **kwargs):
        super(NurbsCurveFromVertices, self).__init__(**kwargs)
        self.node_type = 'nurbsCurve'

    @classmethod
    def create(cls, controller, **kwargs):

        kwargs.setdefault('degree', 3)
        kwargs.setdefault('form', 0)
        kwargs.setdefault('vertices', [])

        if kwargs.get('parent', None) is None:
            raise TypeError(
                'Cannot create a NurbsCurveFromEdge without a parent'
            )
        if kwargs.get('mesh_name', None) is None:
            raise TypeError(
                'Cannot create a NurbsCurveFromEdge without a mesh name'
            )

        return super(NurbsCurveFromVertices, cls).create(controller, **kwargs)

    def create_in_scene(self):

        # create_curve_from_vertices Is not needed.. just use objects and plugs in the create function

        self.controller.scene.create_curve_from_vertices(self)

    def get_curve_data(self):
        return self.controller.get_curve_data(self)
