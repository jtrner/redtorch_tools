from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import Matrix


class BaseSliderGuide(PartGuide):

    def __init__(self, **kwargs):
        super(BaseSliderGuide, self).__init__(**kwargs)
        self.toggle_class = BaseSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BaseSliderGuide, cls).create(controller, **kwargs)
        handle = this.create_handle()
        handle.mesh.assign_shading_group(this.get_root().shaders[this.side].shading_group)
        joint = handle.create_child(
            Joint
        )
        controller.create_parent_constraint(handle, joint)
        this.joints = [joint]
        joint.plugs['drawStyle'].set_value(2)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BaseSliderGuide, self).get_toggle_blueprint()
        blueprint['matrices'] = [list(self.joints[0].get_matrix())]
        return blueprint


class BaseSlider(Part):

    def __init__(self, **kwargs):
        super(BaseSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        matrices = kwargs.get('matrices', None)
        if not matrices:
            raise Exception('you must pass "matrices" keyword argument to create a %s' % cls.__name__)
        this = super(BaseSlider, cls).create(controller, **kwargs)
        joint = this.create_child(
            Joint,
            parent=this.joint_group,
            #matrix=matrices[0]
        )
        this.joints = [joint]
        joint.plugs['drawStyle'].set_value(2)
        return this

    def post_create(self, **kwargs):
        super(BaseSlider, self).post_create()
        # Positions should be handled internally by slider parts
