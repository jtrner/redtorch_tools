from rig_factory.objects.node_objects.animation_curve import AnimationCurve


class DrivenCurve(AnimationCurve):

    def __init__(self, **kwargs):
        super(DrivenCurve, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if not kwargs.get('driven_plug', None):
            raise Exception(
                'You must provide a driven_plug to create a %s' % DrivenCurve.__name__
            )
        if not kwargs.get('driven_plug', None):
            raise Exception(
                'You must provide a driver_plug to create a %s' % DrivenCurve.__name__
            )
        kwargs.setdefault('post_infinity_type', 'linear')
        kwargs.setdefault('pre_infinity_type', 'linear')
        this = super(DrivenCurve, cls).create(controller, **kwargs)
        input_plug = this.initialize_plug('input')
        input_plug.set_value(0.0)
        this.driver_plug.connect_to(input_plug)
        return this

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_animation_curve(
            self.driven_plug.m_plug,
            name=self.name
        )
