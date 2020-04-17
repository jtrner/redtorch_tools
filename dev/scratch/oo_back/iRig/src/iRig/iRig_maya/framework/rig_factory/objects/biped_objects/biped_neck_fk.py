
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from rig_math.matrix import Matrix


class BipedNeckFkGuide(ChainGuide):

    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        count=5
    )

    def __init__(self, **kwargs):
        super(BipedNeckFkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeckFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'spine')
        this = super(BipedNeckFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedNeckFk(Part):
    
    head_handle = ObjectProperty(
        name='head_handle'
    )

    # This is needed so ik/fk neck can work
    tangent_group = ObjectProperty(
        name='tangent_group'
    )

    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )

    def __init__(self, **kwargs):
        super(BipedNeckFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        head_matrix = Matrix(kwargs.pop('head_matrix', list(Matrix())))
        this = super(BipedNeckFk, cls).create(controller, **kwargs)
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

            # Creates joints for every matrix in `matrices`
            joint = joint_parent.create_child(
                Joint,
                root_name=root_name,
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

            # Creates handles for all joints except the first, and the
            # final two.
            if 0 < x < matrix_count - 2:

                handle = this.create_handle(
                    handle_type=LocalHandle,
                    size=size*1.25,
                    matrix=matrix,
                    shape='cube',
                    parent=handle_parent,
                    index=x,
                    rotation_order='xzy'
                )
                handle.stretch_shape(matrices[x + 1])
                handle.multiply_shape_matrix(
                    Matrix(scale=[0.85, 0.85, 0.85])
                )
                handle_parent = handle.gimbal_handle
                handles.append(handle)

                root.add_plugs([
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ])
                controller.create_parent_constraint(handle, joint)

        # Creates the "Head" handle.
        head_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='%s_head' % root_name,
            size=size,
            matrix=Matrix(matrices[-1].get_translation()),
            shape='partial_cube_x',
            parent=handles[-1].gimbal_handle,
            rotation_order='zxy'
        )
        head_handle.set_shape_matrix(head_matrix)

        root.add_plugs(
            [
                head_handle.plugs['tx'],
                head_handle.plugs['ty'],
                head_handle.plugs['tz'],
                head_handle.plugs['rx'],
                head_handle.plugs['ry'],
                head_handle.plugs['rz']
            ]
        )

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            joints[-1],
            mo=True
        )

        controller.create_parent_constraint(
            this,
            joints[0],
            mo=True
        )

        this.head_handle = head_handle
        this.joints = joints
        return this
