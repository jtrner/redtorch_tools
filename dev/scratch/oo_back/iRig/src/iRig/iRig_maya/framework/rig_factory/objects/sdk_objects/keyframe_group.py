from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.sdk_objects.sdk_keyframe import SDKKeyFrame


class KeyframeGroup(BaseNode):

    sdk_group = ObjectProperty(
        name='sdk_group'
    )
    keyframes = ObjectListProperty(
        name='keyframes'
    )
    in_value = DataProperty(
        name='in_value'
    )
    in_tangent_type = DataProperty(
        name='in_tangent_type'
    )
    out_tangent_type = DataProperty(
        name='out_tangent_type'
    )

    def __init__(self, **kwargs):
        super(KeyframeGroup, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        controller.scene.autoKeyframe(state=False)
        sdk_group = kwargs.get('sdk_group', None)
        in_value = kwargs.get('in_value', None)
        isolate = kwargs.get('isolate', True)
        kwargs.setdefault('parent', sdk_group)
        kwargs.setdefault('root_name', sdk_group.root_name)
        if not isinstance(in_value, float):
            raise Exception(
                'You must provide an "in_value" keyword argument of type "float" to create a %s, %s' % (
                    KeyframeGroup,
                    in_value
                )
            )
        if in_value in [x.in_value for x in sdk_group.keyframe_groups]:
            raise Exception(
                'A keyframe group with the in_value "%s" already exists' % in_value
            )
        kwargs['name'] = '%s_%s' % (
            sdk_group.name,
            len(sdk_group.keyframe_groups) + 1
        )
        if isolate:
            sdk_group.isolate()
        controller.start_ownership_signal.emit(None, sdk_group)
        this = super(KeyframeGroup, cls).create(controller, **kwargs)
        this.sdk_group = sdk_group
        sdk_group.keyframe_groups.append(this)
        controller.end_ownership_signal.emit(this, sdk_group)

        for driven_plug in sdk_group.sdk_network.driven_plugs:
            animation_curve = this.sdk_group.get_animation_curve(driven_plug)
            new_keyframe = controller.create_object(
                SDKKeyFrame,
                animation_curve=animation_curve,
                in_value=in_value,
                parent=animation_curve
            )
            this.keyframes.append(new_keyframe)

        return this

    def update(self):
        self.sdk_group.isolate()
        for keyframe in self.keyframes:
            end_plug = keyframe.animation_curve.driven_plug
            self.controller.change_keyframe(
                keyframe,
                out_value=end_plug.get_value()
            )
        self.sdk_group.driver_plug.set_value(self.in_value)

    def set_keyframe_tangents(self, tangent_type):

        self.in_tangent_type = tangent_type
        self.out_tangent_type = tangent_type

        self.controller.change_keyframe(
            self,
            in_tangent=tangent_type,
            out_tangent=tangent_type
        )

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            in_value=self.in_value
        )
        return blueprint

    def teardown(self):

        curve_names = [key.animation_curve.name for key in self.keyframes]

        self.controller.scene.select(cl=True)

        self.controller.scene.selectKey(
            curve_names,
            float=(self.in_value,),
            keyframe=True
        )

        self.controller.scene.cutKey(
            animation='keys',
            clear=True,
        )

        super(KeyframeGroup, self).teardown()