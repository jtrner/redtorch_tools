from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle
import rig_factory.environment as env


def create_spline_ik(
        start_joint,
        end_joint,
        nurbs_curve,
        world_up_type=4,
        up_vector=None,
        up_vector_2=None,
        world_up_object=None,
        world_up_object_2=None,
        twist_value_type=0,
        advanced_twist=True,
        forward_axis=None,
        up_axis=None,
        side='center'
):

    if not isinstance(start_joint, Joint) or not isinstance(end_joint, Joint):
        raise Exception('You must use two "Joint" node_objects as arguments when you call "create_ik_spline_handle"')
    if not isinstance(nurbs_curve, NurbsCurve):
        raise Exception('You must use a "NurbsCurve" object as an argument when you call "create_ik_spline_handle"')

    this = start_joint.parent.create_child(
        IkSplineHandle,
        start_joint,
        end_joint,
        nurbs_curve,
        side=side
        )

    this.plugs['dTwistControlEnable'].set_value(advanced_twist)  # Enable Twist Controls
    this.plugs['dWorldUpType'].set_value(world_up_type)  # Object UP (Start/End)
    this.plugs['dForwardAxis'].set_value(forward_axis if forward_axis is not None else dict(left=2, right=3, center=2)[side])  # Forward Axis
    this.plugs['dWorldUpAxis'].set_value(up_axis if up_axis is not None else dict(left=4, right=3, center=4)[side])  # Up Axis
    this.plugs['dTwistValueType'].set_value(twist_value_type)  # Up Axis
    if world_up_object:
        this.plugs['dWorldUpVector'].set_value(up_vector if up_vector is not None else env.side_up_vectors[side])
        world_up_object.plugs['worldMatrix'].element(0).connect_to(this.plugs['dWorldUpMatrix'])
    if world_up_object_2:
        this.plugs['dWorldUpVectorEnd'].set_value(up_vector_2 if up_vector_2 is not None else env.side_up_vectors[side])
        world_up_object_2.plugs['worldMatrix'].element(0).connect_to(this.plugs['dWorldUpMatrixEnd'])

    return this