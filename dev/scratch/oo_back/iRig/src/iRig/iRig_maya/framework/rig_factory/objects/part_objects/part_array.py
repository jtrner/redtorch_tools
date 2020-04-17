from rig_factory.objects.part_objects.part_group import PartGroup, PartGroupGuide
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.node_objects.transform import Transform


class PartArrayGuide(PartGroupGuide):

    def __init__(self, **kwargs):
        super(PartArrayGuide, self).__init__(**kwargs)
        self.toggle_class = PartArray.__name__

    def create_members(self):
        pass


class PartArray(PartGroup):

    scale_multiply_transform = ObjectProperty(
        name='scale_multiply_transform'
    )

    def __init__(self, **kwargs):
        super(PartArray, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(PartArray, cls).create(controller, **kwargs)
        scale_multiply_transform = this.create_child(
            Transform,
            root_name='%s_scale_multiply' % this.root_name
        )
        this.controller.create_scale_constraint(this, scale_multiply_transform)
        scale_multiply_transform.plugs['inheritsTransform'].set_value(False)
        this.scale_multiply_transform = scale_multiply_transform
        return this
