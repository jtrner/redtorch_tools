import maya.cmds as mc
from maya_tools.deformer_utilities.general import get_m_object
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve

from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectProperty, ObjectListProperty
)


class CurveFromEdge(Transform):

    mesh_name = DataProperty(
        name='mesh_name',
    )
    vertex_indices = DataProperty(
        name='vertex_indices',
    )
    degree = DataProperty(
        name='degree',
    )
    form = DataProperty(
        name='form',
    )
    construction_history = ObjectListProperty(
        name='construction_history',
    )
    nurbs_curve = ObjectProperty(
        name='nurbs_curve',
    )
    default_settings = dict(
        degree=3,
        form=0
    )

    def __init__(self, **kwargs):
        super(CurveFromEdge, self).__init__(**kwargs)
        self.node_type = 'nurbsCurve'

    @classmethod
    def create(cls, controller, **kwargs):

        if kwargs.get('components', None) is None:
            raise TypeError(
                'Cannot create a NurbsCurveFromEdge without components'
            )

        this = super(CurveFromEdge, cls).create(controller, **kwargs)

        if this.mesh_name and this.vertex_indices:
            mesh = controller.named_objects.get(this.mesh_name, None)
            if not mesh:
                controller.raise_warning('EyeLashPart: The mesh "%s" was not found in the controller' % mesh)
            vertex_strings = ['vtx[%s]' % x for x in this.vertex_indices]
            curve_from_edge_node = this.create_child(
                DependNode,
                node_type='curveFromEdge'
            )
            nurbs_curve = this.create_child(
                NurbsCurve,
                node_type='curveFromEdge'
            )
            mesh.plugs['displaySmoothMesh'].connect_to(curve_from_edge_node.plugs['displaySmoothMesh'])
            mesh.plugs['outMesh'].connect_to(curve_from_edge_node.plugs['inputPolymesh'])
            mesh.plugs['outSmoothMesh'].connect_to(curve_from_edge_node.plugs['inputSmoothPolymesh'])
            mesh.plugs['smoothLevel'].connect_to(curve_from_edge_node.plugs['smoothLevel'])
            mesh.plugs['worldMatrix[0]'].connect_to(curve_from_edge_node.plugs['inputMat'])
            mesh.plugs['outputcurve'].connect_to(nurbs_curve.plugs['create'])
            controller.scene.setAttr(
                curve_from_edge_node.plugs['inputComponents'],
                len(vertex_strings),
                *vertex_strings,
                type='componentList'
            )
            this.nurbs_curve = nurbs_curve
        return this



    def create_in_scene(self):
        super(CurveFromEdge, self).create_in_scene()
        mesh_name = self.mesh_name
        vertex_indices = self.vertex_indices

        if len(vertex_indices) < 1:
            TypeError('Not enough items in components: minimum 1')


        vertex_strings = ['vtx[%s]' % x for x in vertex_indices]

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
