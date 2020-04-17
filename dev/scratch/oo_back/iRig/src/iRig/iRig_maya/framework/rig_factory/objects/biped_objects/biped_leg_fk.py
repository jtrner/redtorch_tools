from rig_factory.objects.base_objects.properties import ObjectListProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
import rig_factory
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle

from rig_math.matrix import Matrix


class BipedLegFkGuide(ChainGuide):
    default_settings = dict(
        root_name='leg',
        size=1.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedLegFkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLegFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'leg')
        this = super(BipedLegFkGuide, cls).create(controller, **kwargs)
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedLegFk(Part):

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
        super(BipedLegFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedLegFk, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        root = this.get_root()
        joints = []
        joint_parent = this.joint_group
        handle_parent = this
        handles = []
        for i in range(5):
            is_last = i > 3
            matrix = matrices[i]
            joint = joint_parent.create_child(
                Joint,
                matrix=matrix,
                index=i
            )
            joint_parent = joint
            joint.zero_rotation()
            if not is_last:  # No need to create a handle for tip of limb
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    root_name=root_name,
                    index=i,
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='frame_x' if i < 2 else 'frame_z',
                    parent=handle_parent
                )

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
                handle.stretch_shape(matrices[i+1])
                if i < 2:
                    handle.multiply_shape_matrix(
                        Matrix(
                            scale=[
                                -1.25 if side == 'right' else 1.25,
                                0.8,
                                0.8
                            ]
                        )
                    )
                else:
                    handle.multiply_shape_matrix(
                        Matrix(
                            scale=[
                                0.75,
                                0.5,
                                0.8 if side == 'right' else -0.8
                            ]
                        )
                    )

                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=True,
                )
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                handle_parent = handle.gimbal_handle
                handles.append(handle)

            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)

        thigh_handle, calf_handle, ankle_handle, toe_handle = handles
        thigh_handle.set_rotation_order('xyz')
        calf_handle.set_rotation_order('xyz')
        ankle_handle.set_rotation_order('xyz')
        toe_handle.set_rotation_order('xyz')
        this.joints = joints

        return this
