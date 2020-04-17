import maya.cmds as mc
from maya_tools.deformer_utilities.general import get_m_object
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectProperty, ObjectListProperty
)


class NurbsCurveFromEdge(DagNode):

    construction_history = ObjectListProperty(
        name='construction_history',
    )
    components = DataProperty(
        name='components',
    )
    degree = DataProperty(
        name='degree',
    )
    form = DataProperty(
        name='form',
    )

    def __init__(self, **kwargs):
        super(NurbsCurveFromEdge, self).__init__(**kwargs)
        self.node_type = 'nurbsCurve'

    @classmethod
    def create(cls, controller, **kwargs):

        kwargs.setdefault('degree', 3)
        kwargs.setdefault('form', 0)

        if kwargs.get('parent', None) is None:
            raise TypeError(
                'Cannot create a NurbsCurveFromEdge without a parent'
            )
        if kwargs.get('components', None) is None:
            raise TypeError(
                'Cannot create a NurbsCurveFromEdge without components'
            )

        return super(NurbsCurveFromEdge, cls).create(controller, **kwargs)

    def create_in_scene(self):

        parent = self.parent
        components = self.components

        if len(components) < 1:
            TypeError('Not enough items in components: minimum 1')

        mesh = components[0].split('.')[0]
        points = [x.split('.')[-1] for x in components]

        poly_edge_to_curve_name = mc.createNode('polyEdgeToCurve')
        nurbs_curve_name = mc.createNode('nurbsCurve', parent=parent)

        connections = [
            (
                mesh + '.displaySmoothMesh',
                poly_edge_to_curve_name + '.displaySmoothMesh',
            ), (
                mesh + '.outMesh',
                poly_edge_to_curve_name + '.inputPolymesh',
            ), (
                mesh + '.outSmoothMesh',
                poly_edge_to_curve_name + '.inputSmoothPolymesh',
            ), (
                mesh + '.smoothLevel',
                poly_edge_to_curve_name + '.smoothLevel',
            ), (
                mesh + '.worldMatrix[0]',
                poly_edge_to_curve_name + '.inputMat',
            ), (
                poly_edge_to_curve_name + '.outputcurve',
                nurbs_curve_name + '.create',
            ),
        ]
        for connection in connections:
            mc.connectAttr(*connection)

        mc.setAttr(
            poly_edge_to_curve_name + '.inputComponents',
            len(points),
            *points,
            type='componentList'
        )

        self.m_object = get_m_object(nurbs_curve_name)
        self.construction_history = [get_m_object(poly_edge_to_curve_name)]

    def get_curve_data(self):
        return self.controller.get_curve_data(self)
