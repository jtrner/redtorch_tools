from rig_factory.objects.base_objects.properties import ObjectListProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part


# TODO: add fk joint code that works in rig state
class QuadrupedFrontLegFkGuide(ChainGuide):
    default_settings = dict(
        root_name='front_leg',
        size=1.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLegFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedFrontLegFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('root_name', 'front_leg')
        this = super(QuadrupedFrontLegFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedFrontLegFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedFrontLegFk(Part):

    fk_handles = ObjectListProperty(
        name='fk_handles'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )
    fk_handle_gimbals = ObjectListProperty(
        name='fk_handle_gimbals'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLegFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedFrontLegFk, cls).create(controller, **kwargs)
        matrices = this.matrices

        joints = []
        handles = []
        handle_parent = this
        joint_parent = this.joint_group
        for i in range(len(matrices)):

            joint = joint_parent.create_child(
                Joint,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            joint_parent = joint

            handle = this.create_handle(
                parent=handle_parent,
                index=i,
                matrix=matrices[i],
                shape='frame_x'
            )
            if i < len(matrices) - 1:
                handle.stretch_shape(matrices[i + 1])
            this.controller.create_parent_constraint(
                handle,
                joint
            )
            this.controller.create_scale_constraint(
                handle,
                joint
            )
            handles.append(handle)
            handle_parent = handle

        this.joints = joints
        this.handles = handles
        return this
