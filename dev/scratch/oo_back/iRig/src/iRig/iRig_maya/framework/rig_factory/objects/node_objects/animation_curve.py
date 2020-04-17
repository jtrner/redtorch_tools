from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.keyframe import KeyFrame


class AnimationCurve(DependNode):

    sdk_group = ObjectProperty(
        name='sdk_group'
    )
    driver_plug = ObjectProperty(
        name='driver_plug'
    )
    driven_plug = ObjectProperty(
        name='driven_plug'
    )
    keyframes = ObjectListProperty(
        name='keyframes'
    )
    pre_infinity_type = DataProperty(
        name='pre_infinity_type',
        default_value='linear'
    )
    post_infinity_type = DataProperty(
        name='post_infinity_type',
        default_value='linear'
    )

    def create_keyframe(self, **kwargs):
        kwargs['animation_curve'] = self
        return self.controller.create_object(
            KeyFrame,
            **kwargs
        )

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_animation_curve(
            self.driven_plug.m_plug,
            name=self.name
        )
        self.controller.scene.lock_node(self, lock=True)

    def teardown(self):
        self.controller.scene.lock_node(self, lock=False)
        super(AnimationCurve, self).teardown()

    def get_value_at_index(self, index):
        return self.controller.scene.get_animation_curve_value_at_index(self.m_object, index)
