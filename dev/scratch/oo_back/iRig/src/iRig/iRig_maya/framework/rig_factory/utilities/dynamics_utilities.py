from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.node_objects.depend_node import DependNode


def create_dynamic_handle(owner, **kwargs):
    follicle = kwargs.pop('follicle', None)
    kwargs.setdefault('handle_type', CurveHandle)
    this = owner.create_handle(
        **kwargs
    )

    if follicle:

        override_dynamics_plug = this.create_plug('OverrideDynamics', at='enum', en="Off:On", k=True)
        dynamics_on_off_plug = this.create_plug('DynamicOnOff', defaultValue=1.0, minValue=0, maxValue=1, k=True)
        stiffness_plug = this.create_plug('Stiffness', defaultValue=0.5, minValue=0, maxValue=100, k=True)
        damp_plug = this.create_plug('Damp', defaultValue=1, minValue=0, maxValue=100, k=True)
        length_flex_plug = this.create_plug('LengthFlex', defaultValue=.2, minValue=0, maxValue=1, k=True)
        collision_plug = this.create_plug('Collision', at='enum', en="Off:On", k=True)
        start_curve_attract_plug = this.create_plug('StartCurveAttract', at='double', defaultValue=0.5, minValue=0.0,
                                                    maxValue=1.0, k=True)
        attraction_damp_plug = this.create_plug('AttractionDamp', at='long', defaultValue=4, minValue=1, maxValue=10,
                                                k=True)
        point_lock_plug = this.create_plug('PointLock', defaultValue=1, at='enum', en="NoAttach:Base:Tip:BothEnds",
                                           k=True)
        root = owner.get_root()
        root.add_plugs(
            dynamics_on_off_plug,
            stiffness_plug,
            damp_plug,
            length_flex_plug,
            length_flex_plug,
            collision_plug,
            start_curve_attract_plug,
        )
        condition_node = this.create_child(
            DependNode,
            node_type='condition'
        )
        condition_node.plugs['colorIfFalseR'].set_value(0)
        condition_node.plugs['colorIfTrueR'].set_value(2)
        dynamics_on_off_plug.connect_to(condition_node.plugs['firstTerm'])
        condition_node.plugs['secondTerm'].set_value(1)
        condition_node.plugs['outColorR'].connect_to(follicle.plugs['simulationMethod'])
        point_lock_plug.connect_to(follicle.plugs['pointLock'])
        collision_plug.connect_to(follicle.plugs['collide'])
        damp_plug.connect_to(follicle.plugs['damp'])
        stiffness_plug.connect_to(follicle.plugs['stiffness'])
        length_flex_plug.connect_to(follicle.plugs['lengthFlex'])
        start_curve_attract_plug.connect_to(follicle.plugs['startCurveAttract'])
        attraction_damp_plug.connect_to(follicle.plugs['attractionDamp'])
        override_dynamics_plug.connect_to(follicle.plugs['overrideDynamics'])
        root.add_plugs(
            point_lock_plug,
            collision_plug,
            damp_plug,
            stiffness_plug,
            length_flex_plug,
            start_curve_attract_plug,
            attraction_damp_plug

        )

        root.add_plugs(
            dynamics_on_off_plug,
            override_dynamics_plug,
            keyable=False
        )

    return this
