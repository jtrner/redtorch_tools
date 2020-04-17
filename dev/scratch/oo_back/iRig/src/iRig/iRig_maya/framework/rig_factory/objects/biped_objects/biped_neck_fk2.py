"""
Based on `biped_neck_fk`.
Changes:
    * Does not contain `break_tangent` functionality.
"""

from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_math.matrix import Matrix


class BipedNeckFkGuide2(ChainGuide):

    default_settings = dict(
        root_name='spine',
        size=1.0,
        side='center',
        count=5,
    )

    def __init__(self, **kwargs):
        super(BipedNeckFkGuide2, self).__init__(**kwargs)
        self.toggle_class = BipedNeckFk2.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'spine')
        this = super(BipedNeckFkGuide2, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckFkGuide2, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedNeckFk2(Part):

    head_handle = ObjectProperty(
        name='head_handle'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        head_matrix = Matrix(kwargs.pop('head_matrix', list(Matrix())))
        this = super(BipedNeckFk2, cls).create(controller, **kwargs)
        size = this.size
        root = this.get_root()
        matrices = this.matrices
        root_name = this.root_name

        handle_parent = this
        joint_parent = this.joint_group
        matrix_count = len(matrices)
        handles = []
        joints = []
        for x, matrix in enumerate(matrices):

            joint = joint_parent.create_child(
                Joint,
                matrix=matrix,
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

            if 0 < x < matrix_count - 2:
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    size=size * 1.25,
                    matrix=matrix,
                    shape='cube',
                    parent=handle_parent,
                    index=x,
                    rotation_order='xzy'
                )
                handle.stretch_shape(matrices[x + 1])
                handle.multiply_shape_matrix(Matrix(scale=[0.85] * 3))
                controller.create_parent_constraint(handle, joint)
                root.add_plugs([
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ])
                handles.append(handle)
                handle_parent = handle.gimbal_handle

        head_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name=root_name + '_head',
            size=size,
            matrix=Matrix(matrices[-1].get_translation()),
            shape='partial_cube_x',
            parent=handles[-1].gimbal_handle,
            rotation_order='zxy'
        )
        head_handle.set_shape_matrix(head_matrix)
        controller.create_parent_constraint(head_handle, joints[-1])
        root.add_plugs([
            head_handle.plugs['tx'],
            head_handle.plugs['ty'],
            head_handle.plugs['tz'],
            head_handle.plugs['rx'],
            head_handle.plugs['ry'],
            head_handle.plugs['rz']
        ])

        this.head_handle = head_handle
        this.joints = joints
        return this
