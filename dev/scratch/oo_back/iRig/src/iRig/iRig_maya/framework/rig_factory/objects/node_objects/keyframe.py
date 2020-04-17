from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class KeyFrame(BaseNode):

    animation_curve = ObjectProperty(
        name='animation_curve'
    )
    in_value = DataProperty(
        name='in_value'
    )
    out_value = DataProperty(
        name='out_value'
    )

    in_tangent = DataProperty(
        name='in_tangent',
        default_value='linear'
    )
    out_tangent = DataProperty(
        name='out_tangent',
        default_value='linear'
    )
    """
    out_angle = DataProperty(
        name='out_angle'
    )
    in_angle = DataProperty(
        name='in_angle'
    )
    in_tangent_weight = DataProperty(
        name='in_tangent_weight'
    )
    out_tangent_weight = DataProperty(
        name='out_tangent_weight'
    )
    in_tangent_type = DataProperty(
        name='in_tangent_type'
    )
    out_tangent_type = DataProperty(
        name='out_tangent_type'
    )
    tangents_locked = DataProperty(
        name='tangents_locked'
    )
    is_breakdown = DataProperty(
        name='is_breakdown'
    )
    """

    def __init__(self, **kwargs):
        super(KeyFrame, self).__init__(**kwargs)

    def get_blueprint(self):
        return dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            in_value=self.in_value,
            out_value=self.out_value,
            #in_tangent=self.in_tangent,
            #out_tangent=self.out_tangent,
            #in_angle=self.in_angle,
            #out_angle=self.out_angle,
            #in_tangent_weight=self.in_tangent_weight,
            #out_tangent_weight=self.out_tangent_weight,
            #in_tangent_type=self.in_tangent_type,
            #out_tangent_type=self.out_tangent_type,
            #tangents_locked=self.tangents_locked,
            #is_breakdown=self.is_breakdown
        )

    def delete(self):
        self.controller.delete_keyframe(self)

    def set_values(self, **kwargs):
        self.controller.change_keyframe(
            self,
            **kwargs
        )

    @classmethod
    def create(cls, controller, **kwargs):
        animation_curve = kwargs.get('animation_curve', None)
        in_value = kwargs.get('in_value', None)
        out_value = kwargs.get('out_value', None)

        if animation_curve is None:
            raise Exception(
                'You must provide a animation_curve to create a %s' % KeyFrame.__name__
            )
        if in_value is None:
            raise Exception(
                'You must provide a in_value to create a %s' % KeyFrame.__name__
            )
        if in_value in [x.in_value for x in animation_curve.keyframes]:
            raise Exception(
                'A keyframe at the in value of "%s" already exists' % in_value
            )

        index = len(animation_curve.keyframes)
        kwargs['name'] = '%s_%s' % (
            animation_curve.name,
            index
        )

        kwargs.setdefault('out_value', out_value if out_value is not None else animation_curve.driven_plug.get_value())
        kwargs.setdefault('root_name', animation_curve.root_name)
        kwargs.setdefault('index', index)
        kwargs.setdefault('parent', animation_curve)
        this = super(KeyFrame, cls).create(controller, **kwargs)
        animation_curve.keyframes.append(this)
        this.create_in_scene()
        return this

    def create_in_scene(self):
        self.controller.scene.create_keyframe(
            self.animation_curve.m_object,
            self.in_value,
            self.out_value,
            self.controller.scene.tangents[self.in_tangent],
            self.controller.scene.tangents[self.out_tangent]
        )

    def teardown(self):
        self.controller.scene.delete_keyframe(self.animation_curve.m_object, self.in_value)
        super(KeyFrame, self).teardown()

    def get_out_value(self):
        self.out_value = self.controller.scene.get_key_value(
            self.animation_curve.m_object,
            self.in_value
        )
        return self.out_value
