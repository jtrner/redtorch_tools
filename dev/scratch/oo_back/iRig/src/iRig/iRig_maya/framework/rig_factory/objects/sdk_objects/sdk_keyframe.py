from rig_factory.objects.node_objects.keyframe import KeyFrame


class SDKKeyFrame(KeyFrame):

    @classmethod
    def create(cls, controller, **kwargs):
        animation_curve = kwargs.get('animation_curve', )
        if not animation_curve.__class__.__name__ == 'SDKCurve':
            raise Exception('Invalid animation curve type')

        sdk_network = animation_curve.sdk_group.sdk_network
        kwargs.setdefault('in_tangent', sdk_network.in_tangent)
        kwargs.setdefault('out_tangent', sdk_network.out_tangent)
        kwargs.setdefault('out_angle', sdk_network.out_angle)
        kwargs.setdefault('in_angle', sdk_network.in_angle)
        kwargs.setdefault('in_tangent_weight', sdk_network.in_tangent_weight)
        kwargs.setdefault('out_tangent_weight', sdk_network.out_tangent_weight)
        kwargs.setdefault('in_tangent_type', sdk_network.in_tangent_type)
        kwargs.setdefault('out_tangent_type', sdk_network.out_tangent_type)
        kwargs.setdefault('tangents_locked', sdk_network.tangents_locked)
        kwargs.setdefault('is_breakdown', sdk_network.is_breakdown)
        return super(SDKKeyFrame, cls).create(controller, **kwargs)
