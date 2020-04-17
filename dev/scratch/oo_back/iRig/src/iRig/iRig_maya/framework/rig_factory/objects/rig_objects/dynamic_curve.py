from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.rig_objects.hair_network import HairNetwork
from rig_factory.objects.base_objects.base_node import BaseNode


class DynamicCurve(BaseNode):

    base_curve = ObjectProperty(
        name='base_curve'
    )

    surface_point = ObjectProperty(
        name='surface_point'
    )

    out_curve = ObjectProperty(
        name='out_curve'
    )

    out_curve_transform = ObjectProperty(
        name='out_curve'
    )

    hair_network = ObjectProperty(
        name='hair_network'
    )

    @classmethod
    def create(cls, controller, **kwargs):

        base_curve = kwargs.get('base_curve', None)

        if not isinstance(base_curve, NurbsCurve):
            raise TypeError(
                'You must provide a NurbsCurve as the "base_curve" keyword argument to create a %s' % cls.__name__
            )

        this = super(DynamicCurve, cls).create(controller, **kwargs)
        root_name = this.root_name
        hair_network = this.hair_network

        rebuilt_curve_transform = this.create_child(
            Transform,
            root_name='%s_rebuild' % root_name,
            parent=hair_network.curve_group
        )

        rebuilt_nurbs_curve = rebuilt_curve_transform.create_child(
            NurbsCurve
        )
        out_curve_transform = this.create_child(
            Transform,
            root_name='%s_out' % root_name,
            parent=hair_network.curve_group
        )
        out_curve = out_curve_transform.create_child(
            NurbsCurve
        )
        surface_point = this.create_child(
            SurfacePoint,
            parent=hair_network.follicle_group
        )
        rebuild_curve = this.create_child(
            DependNode,
            node_type='rebuildCurve',
            root_name='%s_rebuild' % root_name,
        )
        rebuilt_nurbs_curve.plugs['intermediateObject'].set_value(True)

        follicle = surface_point.follicle

        rebuild_curve.plugs.set_values(
            degree=1,
            keepControlPoints=1,
            keepTangents=0,
            endKnots=1,
            keepRange=0
        )

        follicle.plugs.set_values(
            restPose=1,
            startDirection=1,
            degree=3
        )
        follicle.plugs['stiffnessScale'].element(1).child(1).set_value(0.5)
        follicle.plugs['attractionScale'].element(1).child(1).set_value(0.5)
        surface_point.plugs['inheritsTransform'].set_value(False)
        base_curve.plugs['worldSpace'].element(0).connect_to(rebuild_curve.plugs['inputCurve'])
        rebuild_curve.plugs['outputCurve'].connect_to(rebuilt_nurbs_curve.plugs['create'])
        rebuilt_nurbs_curve.plugs['worldSpace'].element(0).connect_to(follicle.plugs['startPosition'])
        follicle.plugs['outCurve'].connect_to(out_curve.plugs['create'])

        if hair_network:
            if not isinstance(hair_network, HairNetwork):
                raise TypeError(
                    'You must provide a HairNetwork as the "hair_network" keyword argument'
                )
            hair_index = hair_network.hair_system.plugs['inputHair'].get_next_avaliable_index()
            follicle.plugs['outHair'].connect_to(hair_network.hair_system.plugs['inputHair'].element(hair_index))
            hair_network.hair_system.plugs['outputHair'].element(hair_index).connect_to(follicle.plugs['currentPosition'])

        this.surface_point = surface_point
        this.out_curve = out_curve
        this.out_curve_transform = out_curve_transform
        return this
