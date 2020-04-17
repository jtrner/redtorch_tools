from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, ObjectDictProperty
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.sdk_objects.sdk_curve import SDKCurve
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.weak_list import WeakList


class SDKGroup(BaseNode):

    sdk_network = ObjectProperty(
        name='sdk_network'
    )
    driver_plug = ObjectProperty(
        name='driver_plug'
    )
    animation_curves = ObjectDictProperty(
        name='animation_curves'
    )
    keyframe_groups = ObjectListProperty(
        name='keyframe_groups'
    )
    active = DataProperty(
        name='active'
    )

    def __init__(self, **kwargs):
        super(SDKGroup, self).__init__(**kwargs)

    def isolate(self):
        self.controller.isolate_sdk_group(self)

    def set_active(self, value):
        self.controller.set_active(self, value)

    def set_weight(self, value):
        self.controller.set_weight(self, value)

    def create_keyframe_group(self, **kwargs):
        return self.controller.create_object(
            KeyframeGroup,
            sdk_group=self,
            **kwargs
        )

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            driver_plug='%s.%s' % (
                self.driver_plug.get_node().get_selection_string(),
                self.driver_plug.root_name
            )
        )
        return blueprint

    @classmethod
    def create(cls, controller, **kwargs):
        sdk_network = kwargs.get('sdk_network', None)
        if not isinstance(kwargs.get('driver_plug', None), Plug):
            raise Exception(
                'Cannot create an %s without a "driver_plug" keyword argument' % SDKGroup.__name__
            )
        if not sdk_network or not sdk_network.__class__.__name__ == 'SDKNetwork':
            raise Exception(
                'You must provide an SDKNetwork as the keyword argument'
            )
        kwargs.setdefault('parent', sdk_network)
        controller.start_ownership_signal.emit(None, sdk_network)
        kwargs.setdefault(
            'index',
            sdk_network.get_next_avaliable_index()
        )
        this = super(SDKGroup, cls).create(
            controller,
            **kwargs
        )
        sdk_network.sdk_groups.append(this)
        controller.end_ownership_signal.emit(this, sdk_network)
        return this

    def get_animation_curve(self, driven_plug):
        if driven_plug.name in self.animation_curves:
            return self.animation_curves[driven_plug.name]
        default_value = driven_plug.get_value()
        driver_plug = self.driver_plug
        root_name = '%s_%s_%s' % (
            self.root_name,
            driver_plug.name.replace('.', '_'),
            driven_plug.name.replace('.', '_')
        )

        animation_curve = self.controller.create_object(
            SDKCurve,
            sdk_group=self,
            driven_plug=driven_plug,
            root_name=root_name,
            index=len(self.animation_curves)
        )
        self.animation_curves[driven_plug.name] = animation_curve
        if self.sdk_network.lock_curves:
            self.controller.scene.lock_node(animation_curve, lock=True)
        animation_curve.plugs['output'].set_value(default_value)
        return animation_curve

    def teardown(self):
        self.controller.scene.lock_node([x.name for x in self.animation_curves.values()], lock=False)
        if self.animation_curves:
            curves = WeakList(self.animation_curves.values())
            self.controller.delete_objects(  # Not working on custom sdks
                curves,
                collect=self.controller.garbage_collection
            )
        sdk_network = self.sdk_network
        self.controller.start_disown_signal.emit(self, sdk_network)
        sdk_network.sdk_groups.remove(self)
        self.sdk_network = None
        self.controller.end_disown_signal.emit(self, sdk_network)
        super(SDKGroup, self).teardown()
