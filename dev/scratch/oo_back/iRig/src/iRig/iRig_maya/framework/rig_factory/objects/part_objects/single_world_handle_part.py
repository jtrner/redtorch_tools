from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import PartGuide, Part


class SingleWorldHandleGuide(PartGuide):

    default_settings = dict(
        root_name='handle',
        size=0.5,
        side='center'
    )

    def __init__(self, **kwargs):
        super(SingleWorldHandleGuide, self).__init__(**kwargs)
        self.toggle_class = SingleWorldHandle.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SingleWorldHandleGuide, cls).create(controller, **kwargs)
        handle = this.create_handle()
        joint = this.create_child(
            Joint
        )
        controller.create_parent_constraint(
            handle,
            joint
        )
        this.joints = [joint]
        this.base_handles = [handle]
        return this


class SingleWorldHandle(Part):

    default_settings = dict(
        root_name='handle',
        size=0.5,
        side='center'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SingleWorldHandle, cls).create(controller, **kwargs)
        handle = this.create_handle()
        joint = this.create_child(
            Joint
        )
        controller.create_parent_constraint(
            handle,
            joint
        )
        this.joints = [joint]
        return this

