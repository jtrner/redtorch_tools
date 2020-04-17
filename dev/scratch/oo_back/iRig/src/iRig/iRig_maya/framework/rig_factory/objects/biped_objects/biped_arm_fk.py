from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_math.matrix import Matrix


class BipedArmFkGuide(ChainGuide):
    default_settings = dict(
        root_name='arm',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedArmFkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArmFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 4
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'arm')
        this = super(BipedArmFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedArmFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedArmFk(Part):

    def __init__(self, **kwargs):
        super(BipedArmFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedArmFk, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        joints = []
        handle_parent = this
        joint_parent = this.joint_group
        root = this.get_root()

        segments = (
            ('upper', 3),
            ('lower', 3),
            ('wrist', 2),
            ('wrist_tip', 0),
        )

        handles = []
        for i, (segment, rotate_order) in enumerate(segments):
            joint = joint_parent.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, segment),
                matrix=matrices[i],
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            joint_parent = joint
            if i < len(matrices) - 1:
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    root_name='{0}_{1}'.format(root_name, segment),
                    size=size*0.9,
                    matrix=matrices[i],
                    shape='frame_x',
                    parent=handle_parent,
                )
                handle.plugs['rotation_order'].set_value(rotate_order)
                handle.stretch_shape(matrices[i + 1])
                x_scale = 1.3 if i == 0 else 1.0
                shape_scale = [
                    x_scale if side == 'right' else x_scale * -1.0,
                    0.8,
                    0.8
                ]
                handle.multiply_shape_matrix(Matrix(scale=shape_scale))

                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=False
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
                handle_parent = handle.gimbal_handle
                handles.append(handle)
        up_arm_handle, forearm_handle, wrist_handle = handles
        up_arm_handle.set_rotation_order('zyx')
        forearm_handle.set_rotation_order('xyz')
        wrist_handle.set_rotation_order('xzy')
        this.joints = joints
        return this
