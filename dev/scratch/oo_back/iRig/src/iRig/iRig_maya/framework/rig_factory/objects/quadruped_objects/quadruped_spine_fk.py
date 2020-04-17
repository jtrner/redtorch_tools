from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_math.matrix import Matrix
import rig_factory.environment as env


class QuadrupedSpineFkGuide(ChainGuide):
    default_settings = dict(
        root_name='spine',
        size=1.0,
        side='center',
        count=5
    )

    def __init__(self, **kwargs):
        super(QuadrupedSpineFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedSpineFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'spine')
        this = super(QuadrupedSpineFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedSpineFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedSpineFk(Part):

    hip_handle = ObjectProperty(
        name='hip_handle'
    )

    def __init__(self, **kwargs):
        super(QuadrupedSpineFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedSpineFk, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name
        matrices = this.matrices
        joints = []
        handle_parent = this
        joint_parent = this.joint_group
        root = this.get_root()

        hip_matrix = Matrix(matrices[0])
        hip_matrix.set_translation(matrices[1].get_translation())
        hip_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='{0}_hip'.format(root_name),
            shape='double_triangle_z',
            matrix=hip_matrix,
            rotation_order='xzy'
        )

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

            if not x == 0 and not x == len(matrices)-1:
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    size=size*1.25,
                    matrix=matrices[x],
                    shape='partial_cube',
                    parent=handle_parent,
                    index=x,
                    rotation_order='xzy'
                )
                handle.stretch_shape(matrices[x + 1])

                handle.multiply_shape_matrix(
                    Matrix(
                        scale=[0.85, 0.85, 0.85]
                    )
                )
                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=True
                )

                if root:
                    root.add_plugs(
                        [
                            handle.plugs['tx'],
                            handle.plugs['ty'],
                            handle.plugs['tz'],
                            handle.plugs['rx'],
                            handle.plugs['ry'],
                            handle.plugs['rz']
                        ]
                    )

                handle_parent = handle.gimbal_handle

        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0],
            mo=True
        )
        aim_vector = env.side_aim_vectors[side]
        hip_length = (matrices[1].get_translation() - matrices[0].get_translation()).mag()
        hip_shape_matrix = Matrix(
            hip_length * 0.75 * aim_vector[0] * -1.0,
            hip_length * 0.75 * aim_vector[1] * -1.0,
            hip_length * 0.75 * aim_vector[2] * -1.0
        )
        hip_shape_matrix.set_scale([size, hip_length, size])
        hip_handle.set_shape_matrix(hip_shape_matrix)

        root.add_plugs(
            [
                hip_handle.plugs['tx'],
                hip_handle.plugs['ty'],
                hip_handle.plugs['tz'],
                hip_handle.plugs['rx'],
                hip_handle.plugs['ry'],
                hip_handle.plugs['rz']
            ]
        )
        this.hip_handle = hip_handle
        this.joints = joints
        return this
