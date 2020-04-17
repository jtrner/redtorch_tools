
import rig_factory
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_math.vector import Vector
import rig_factory.environment as env


class SplineArray(Transform):

    transforms = ObjectListProperty(
        name='transforms'
    )
    ribbon = ObjectProperty(
        name='ribbon'
    )
    up_vector = DataProperty(
        name='up_vector'
    )
    positions = DataProperty(
        name='positions'
    )
    count = DataProperty(
        name='count',
        default_value=12
    )


    @classmethod
    def create(cls, controller, **kwargs):
        positions = kwargs.get('positions', None)
        if not isinstance(positions, list):
            raise Exception('"positions" keyword argument must be type: list, not type: "%s"' % (type(positions)))
        this = super(SplineArray, cls).create(controller, **kwargs)
        root_name = this.root_name
        member_root_name = this.root_name
        transforms = []

        if this.index is not None:
            member_root_name = '%s_%s' % (root_name, rig_factory.index_dictionary[this.index])
        size = this.size
        degree = 2 if len(positions) < 3 else 3
        length_multiply_plug = this.create_plug(
            'length_multiply',
            at='double',
            min=0.0,
            max=1.0,
            dv=1.0,
            k=False
        )
        ribbon = this.create_child(
            Ribbon,
            positions,
            root_name='{}_ribbon'.format(root_name),
            vector=(Vector(this.up_vector) * (size * 0.25)).data,
            degree=degree,
            extrude=True
        )
        tangent_curve_transform = this.create_child(
            Transform,
            root_name='%s_targent_curve' % root_name
        )
        tangent_curve = tangent_curve_transform.create_child(
            NurbsCurve
        )
        tangent_curve_from_surface = tangent_curve_transform.create_child(
            DependNode,
            node_type='curveFromSurfaceIso'
        )
        tangent_curve_transform.plugs['inheritsTransform'].set_value(False)
        ribbon.nurbs_surface.plugs['worldSpace'].element(0).connect_to(tangent_curve_from_surface.plugs['inputSurface'])
        tangent_curve_from_surface.plugs['outputCurve'].connect_to(tangent_curve.plugs['create'])
        tangent_curve_from_surface.plugs['isoparmDirection'].set_value(1)
        tangent_curve_from_surface.plugs['isoparmValue'].set_value(0.5)
        ribbon.plugs['visibility'].set_value(False)
        tangent_curve.plugs['visibility'].set_value(False)

        segment_parameter = 1.0 / (this.count - 1)

        for i in range(this.count):
            transform = this.create_child(
                Transform,
                index=i,
                root_name=member_root_name,
                parent=this,
            )
            up_transform = this.create_child(
                Transform,
                index=i,
                root_name='%s_up' % member_root_name,
                parent=this,
            )
            parameter_multiply_node = transform.create_child(
                DependNode,
                node_type='multiplyDivide',
            )
            point_on_curve_info = transform.create_child(
                DependNode,
                node_type='pointOnCurveInfo',
                root_name='%s_point_on_curve' % root_name
            )
            point_on_surface_info = transform.create_child(
                DependNode,
                node_type='pointOnSurfaceInfo',
                root_name='%s_point_on_surface' % root_name
            )

            up_transform.plugs['inheritsTransform'].set_value(False)
            transform.plugs['inheritsTransform'].set_value(False)

            point_on_surface_info.plugs['turnOnPercentage'].set_value(True)
            ribbon.nurbs_surface.plugs['worldSpace'].element(0).connect_to(point_on_surface_info.plugs['inputSurface'])
            parameter_multiply_node.plugs['outputX'].connect_to(point_on_surface_info.plugs['parameterV'])
            point_on_surface_info.plugs['parameterU'].set_value(1.0)
            point_on_surface_info.plugs['position'].connect_to(up_transform.plugs['translate'])

            point_on_curve_info.plugs['turnOnPercentage'].set_value(True)
            tangent_curve.plugs['worldSpace'].element(0).connect_to(point_on_curve_info.plugs['inputCurve'])
            length_multiply_plug.connect_to(parameter_multiply_node.plugs['input1X'])
            parameter_multiply_node.plugs['input2X'].set_value(segment_parameter * i)
            parameter_multiply_node.plugs['outputX'].connect_to(point_on_curve_info.plugs['parameter'])
            point_on_curve_info.plugs['position'].connect_to(transform.plugs['translate'])

            controller.create_tangent_constraint(
                tangent_curve,
                transform,
                aimVector=env.side_aim_vectors[this.side],
                upVector=env.side_up_vectors[this.side],
                worldUpType='object',
                worldUpObject=up_transform.name
            )
            transforms.append(transform)
        this.transforms = transforms
        this.ribbon = ribbon
        return this
