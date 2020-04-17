from rig_factory.objects.node_objects.animation_curve import AnimationCurve
from rig_factory.objects.sdk_objects.sdk_keyframe import SDKKeyFrame
from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.node_objects.depend_node import DependNode


class SDKCurve(AnimationCurve):

    default_value = DataProperty(
        name='post_infinity_type',
        default_value='default_value'
    )

    def __init__(self, **kwargs):
        super(SDKCurve, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        sdk_group = kwargs.get('sdk_group', None)
        driven_plug = kwargs.get('driven_plug', None)
        if not sdk_group:
            raise Exception(
                'You must provide a sdk_group to create a %s' % SDKCurve.__name__
            )
        if not driven_plug:
            raise Exception(
                'You must provide a driven_plug to create a %s' % SDKCurve.__name__
            )
        kwargs['default_value'] = driven_plug.get_value()
        kwargs['driver_plug'] = sdk_group.driver_plug
        kwargs['post_infinity_type'] = sdk_group.sdk_network.post_infinity_type
        kwargs['pre_infinity_type'] = sdk_group.sdk_network.post_infinity_type
        kwargs['is_weighted'] = sdk_group.sdk_network.is_weighted
        kwargs.setdefault('parent', sdk_group)
        this = super(SDKCurve, cls).create(controller, **kwargs)
        input_plug = this.initialize_plug('input')
        sdk_group.driver_plug.connect_to(input_plug)
        return this

    def create_in_scene(self):
        blend_weighted_plug = self.driven_plug.blend_node.plugs['input'].element(self.sdk_group.index)
        if self.driven_plug.root_name in ['sx', 'sy', 'sz', 'scaleX', 'scaleY', 'scaleZ']:
            add_node = self.create_child(
                DependNode,
                node_type='addDoubleLinear',
                root_name='%s_post_default' % self.root_name
            )
            add_node.plugs['output'].connect_to(blend_weighted_plug)
            add_node.plugs['input2'].set_value(self.default_value*-1.0)
            m_plug = add_node.plugs['input1'].m_plug
        else:
            m_plug = blend_weighted_plug.m_plug

        self.m_object = self.controller.scene.create_animation_curve(
            m_plug,
            name=self.name
        )

    def create_keyframe(self, **kwargs):
        return self.controller.create_object(
            SDKKeyFrame,
            animation_curve=self,
            **kwargs
        )
