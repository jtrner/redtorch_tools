from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import Matrix


class AnimalArmGuide(PartGuide):

    def __init__(self, **kwargs):
        super(AnimalArmGuide, self).__init__(**kwargs)
        self.toggle_class = AnimalArm.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        root_name = kwargs.setdefault('root_name', 'arm')
        side = kwargs.setdefault('side', 'left')
        this = super(AnimalArmGuide, cls).create(controller, **kwargs)
        utility_group = this.utility_group

        # Shoulder
        shoulderJoint = this.create_child(Joint, root_name='{0}_shoulder'.format(root_name), matrix=Matrix(0.0, 5.0, 0.0))
        # Elbow
        elbowJoint = shoulderJoint.create_child(Joint, root_name='{0}_elbow'.format(root_name), matrix=Matrix(1.0, 2.0, 0.0))
        # Wrist
        wristJoint = elbowJoint.create_child(Joint, root_name='{0}_wrist'.format(root_name), matrix=Matrix(0.0, 0.0, 0.0))
        # Up Vector
        upVectorJoint = shoulderJoint.create_child(Joint, root_name='{0}_upVector'.format(root_name), matrix=Matrix(3.0, 3.0, 0.0))
        # Aim Chain
        test = this.create_child(Transform, root_name='{0}_test'.format(root_name))
        controller.create_animation_handle(root_name='{0}_testB'.format(root_name), shape='cube', matrix=Matrix(0.0, 0.0, 0.0), parent=this, side=side)
        # IK
        controller.create_ik_handle(shoulderJoint, wristJoint, parent=utility_group, solver='ikRPSolver', side=side)

        return this


class AnimalArm(Part):

    def __init__(self, **kwargs):
        super(AnimalArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('root_name', 'arm')
        kwargs.setdefault('side', 'left')
        this = super(AnimalArm, cls).create(controller, **kwargs)
        root_name = this.root_name
        side = this.side
        matrices = this.matrices
        handles = this.handles
        joints = this.joints
        utility_group = this.utility_group

        return this
