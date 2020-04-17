from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint


# TODO: add ik joint code that works in rig state
class QuadrupedNeckIkGuide(ChainGuide):
    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        joint_count=5,
        count=5
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeckIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('root_name', 'neck')
        this = super(QuadrupedNeckIkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedNeckIk(Part):

    def __init__(self, **kwargs):
        super(QuadrupedNeckIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('You must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedNeckIk, cls).create(controller, **kwargs)
        matrices = this.matrices
        if len(matrices) < 4:
            raise Exception('you must provide at least 4 matrices to create a %s' % cls.__name__)

        joints = []
        joint_parent = this.joint_group
        for x, matrix in enumerate(matrices):

            joint = this.create_child(
                Joint,
                index=x,
                matrix=matrix,
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2,
                visibility=False
            )
            joints.append(joint)
            joint_parent = joint

        controller.create_parent_constraint(
            this,
            joints[0],
            mo=True
        )

        this.joints = joints
        return this
