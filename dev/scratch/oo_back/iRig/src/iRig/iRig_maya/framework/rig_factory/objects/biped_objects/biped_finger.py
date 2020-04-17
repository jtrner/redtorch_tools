
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import Matrix


class BipedFingerGuide(ChainGuide):

    default_settings = dict(
        root_name='finger',
        count=5,
        size=1.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedFingerGuide, self).__init__(**kwargs)
        self.toggle_class = BipedFinger.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        this = super(BipedFingerGuide, cls).create(controller, **kwargs)
        return this


class BipedFinger(Part):

    def __init__(self, **kwargs):
        super(BipedFinger, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedFinger, cls).create(controller, **kwargs)
        matrices = this.matrices
        size = this.size
        side = this.side
        joints = []
        root = this.get_root()
        joint_parent = this.joint_group
        handle_parent = this
        for x, matrix in enumerate(matrices):
            joint = this.create_child(
                Joint,
                index=x,
                matrix=matrix,
                parent=joint_parent
            )
            joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            if x != len(matrices)-1:
                handle = this.create_handle(
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='frame_z',
                    index=x,
                    parent=handle_parent,
                    rotation_order='xyz'
                )

                handle.stretch_shape(matrices[x+1])
                z_scale = {0: 2.5, 1: 2.0}.get(x, 1.5)
                handle.multiply_shape_matrix(
                    Matrix(
                        scale=[
                            0.8,
                            0.8,
                            z_scale if side == 'right' else z_scale * -1.0
                        ]
                    )
                )

                controller.create_parent_constraint(
                    handle,
                    joint
                )
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                root.add_plugs(
                    [
                        handle.plugs['tx'],
                        handle.plugs['ty'],
                        handle.plugs['tz'],
                        handle.plugs['rx'],
                        handle.plugs['ry'],
                        handle.plugs['rz'],
                        handle.plugs['sx'],
                        handle.plugs['sy'],
                        handle.plugs['sz']
                    ]
                )
                handle_parent = handle
        joints[0].plugs['type'].set_value(1)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)
        this.joints = joints
        return this
