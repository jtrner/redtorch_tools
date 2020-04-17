from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from rig_factory.objects.part_objects.handle import HandleGuide


class DoubleSliderGuide(HandleGuide):

    default_settings = dict(
        root_name='handle',
        size=1.0,
        side='center',
        shape='arrow_vertical'
    )

    shape = DataProperty(
        name='shape'
    )

    def __init__(self, **kwargs):
        super(DoubleSliderGuide, self).__init__(**kwargs)
        self.toggle_class = DoubleSlider.__name__

    def get_toggle_blueprint(self):
        blueprint = super(DoubleSliderGuide, self).get_toggle_blueprint()
        blueprint['shape'] = self.shape
        return blueprint


class DoubleSlider(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    shape = DataProperty(
        name='shape'
    )

    def __init__(self, **kwargs):
        super(DoubleSlider, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DoubleSlider, cls).create(controller, **kwargs)
        size = this.size
        matrices = this.matrices
        joint = this.create_child(
            Joint,
            index=0,
            matrix=matrices[0],
            parent=this.joint_group
        )
        handle = this.create_handle(
            shape=this.shape if this.shape else 'arrow',
            size=size,
            matrix=matrices[0]
        )
        joint.zero_rotation()
        joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )
        controller.create_parent_constraint(
            handle,
            joint
        )
        this.joints = [joint]
        return this
