from rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty


class FaceMixin(object):

    target_geometry = ObjectProperty(
        name='target_geometry'
    )
    deform_geometry = ObjectProperty(
        name='deform_geometry'
    )

    def __init__(self, **kwargs):
        super(FaceMixin, self).__init__(**kwargs)

    def get_control_points(self):
        return self.controller.get_control_points(self)

    def snap_to_mesh(self, mesh):
        self.controller.snap_to_mesh(self, mesh)

    def set_target_geometry(self, mesh):
        self.controller.set_target_geometry(self, mesh)

    def set_deform_geometry(self, mesh):
        self.controller.set_deform_geometry(self, mesh)

    def mirror(self):
        self.controller.mirror(self)


class FaceGuide(PartGroupGuide, FaceMixin):

    default_settings = dict(
        root_name='face',
        size=1.0,
        side=None
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FaceGuide, cls).create(controller, **kwargs)
        joint = this.create_child(Joint)
        joint.plugs['inheritsTransform'].set_value(False)
        this.joints = [joint]
        return this

    def __init__(self, **kwargs):
        super(FaceGuide, self).__init__(**kwargs)
        self.toggle_class = Face.__name__
        self.disconnected_joints = True


class Face(PartGroup, FaceMixin):

    default_settings = dict(
        root_name='face',
        size=1.0,
        side='center'
    )

    joint_root = ObjectProperty(
        name='joint_root'
    )
    control_root = ObjectProperty(
        name='control_root'
    )
    geometry_root = ObjectProperty(
        name='geometry_root'
    )
    blendshape_root = ObjectProperty(
        name='blendshape_root'
    )
    deform_surface = ObjectProperty(
        name='deform_surface'
    )
    face_shape_network = ObjectProperty(
        name='face_shape_network'
    )
    template_data = DataProperty(
        name='template_data'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Face, cls).create(controller, **kwargs)
        joint = this.create_child(Joint)
        joint.plugs['inheritsTransform'].set_value(False)
        this.joints = [joint]
        return this

    def __init__(self, **kwargs):
        super(Face, self).__init__(**kwargs)
