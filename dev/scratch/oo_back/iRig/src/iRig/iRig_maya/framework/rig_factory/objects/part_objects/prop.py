from rig_factory.objects.part_objects.container import Container, ContainerGuide
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.part_objects.main import Main


class PropGuide(ContainerGuide):

    default_settings = dict(
        root_name='prop'
    )

    def __init__(self, **kwargs):
        kwargs.setdefault('root_name', self.default_settings['root_name'])
        super(PropGuide, self).__init__(**kwargs)
        self.toggle_class = Prop.__name__


class Prop(Container):

    main = ObjectProperty(
        name='main'
    )

    def __init__(self, **kwargs):
        super(Prop, self).__init__(**kwargs)

    def post_create(self, **kwargs):
        super(Prop, self).post_create(**kwargs)
        if self.main:
            self.controller.create_parent_constraint(
                self.main.joints[-1],
                self.placement_group,
                mo=True
            )

    def create_part(self, object_type, **kwargs):
        part = super(Prop, self).create_part(object_type, **kwargs)
        if isinstance(part, Main):
            self.main = part
        return part
