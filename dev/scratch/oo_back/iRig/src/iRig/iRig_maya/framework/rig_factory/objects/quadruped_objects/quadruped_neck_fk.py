from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint


# TODO: add fk joint code that works in rig state
class QuadrupedNeckFkGuide(ChainGuide):
    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        count=5
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeckFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('root_name', 'neck')
        this = super(QuadrupedNeckFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedNeckFk(Part):

    def __init__(self, **kwargs):
        super(QuadrupedNeckFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('You must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedNeckFk, cls).create(controller, **kwargs)

        matrices = this.matrices
        joints = []
        joint_parent = this.joint_group
        for x, matrix in enumerate(matrices):
            joint = joint_parent.create_child(
                Joint,
                matrix=matrices[x],
                parent=joint_parent,
                index=x
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
