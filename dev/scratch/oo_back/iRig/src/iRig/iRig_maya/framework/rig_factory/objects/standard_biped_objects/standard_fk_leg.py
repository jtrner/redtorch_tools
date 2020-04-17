from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
import rig_factory.utilities.handle_utilities as handle_utilities
import rig_factory


class StandardFKLegGuide(ChainGuide):
    default_settings = dict(
        root_name='leg',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(StandardFKLegGuide, self).__init__(**kwargs)
        self.toggle_class = StandardFKLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'leg')
        this = super(StandardFKLegGuide, cls).create(controller, **kwargs)
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(StandardFKLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class StandardFKLeg(Part):
    fk_group = ObjectProperty(
        name='fk_group'
    )
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
        super(StandardFKLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(StandardFKLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        biped_rotation_order = rig_factory.BipedRotationOrder()
        rotate_order = biped_rotation_order.leg_fk

        fk_joints = []
        fk_handles = []
        fk_handle_gimbals = []
        fk_group = this.create_child(
            Transform,
            root_name='%s_FK' % root_name
        )
        fk_joint_parent = utility_group
        fk_handle_parent = fk_group
        for x, joint_str in enumerate(['legUpperFK', 'legLowerFK', 'ankleFK', 'toeFK', 'toeTipFK']):
            matrix = matrices[x]
            fk_joint = this.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, joint_str),
                matrix=matrix,
                parent=fk_joint_parent
            )
            fk_joint_parent = fk_joint
            fk_joint.zero_rotation()
            if joint_str != 'toeTipFK':  # No need to create a handle for tip of limb
                fk_handle = this.create_handle(
                    root_name='{0}_{1}'.format(root_name, joint_str),
                    size=size * 2.5,
                    matrix=matrix,
                    side=side,
                    shape='square',
                    parent=fk_group,
                    rotate_order=rotate_order
                )
                if joint_str != 'legUpperFK':  # don't constrain first fk handle
                    controller.create_parent_constraint(
                        fk_handle_parent,
                        fk_handle.groups[0],
                        mo=True
                    )
                fk_handle.stretch_shape(matrices[x + 1].get_translation())
                fk_handles.append(fk_handle)

                fk_handle_gimbal = this.create_handle(
                    root_name='{0}_{1}Gimbal'.format(root_name, joint_str),
                    size=size * 2.0,
                    matrix=matrix,
                    side=side,
                    shape='square',
                    parent=fk_handle,
                    rotate_order=rotate_order,
                )
                controller.create_parent_constraint(
                    fk_handle_gimbal,
                    fk_joint,
                    mo=True,
                )
                fk_handle_gimbal.stretch_shape(matrices[x + 1].get_translation())
                fk_handle_gimbals.append(fk_handle_gimbal)
                fk_handle_parent = fk_handle_gimbal
            else:
                controller.create_matrix_parent_constraint(
                    fk_handles[-1],
                    fk_joint
                )

            fk_joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            fk_joints.append(fk_joint)

        for fk, fk_gimbal in zip(fk_handles, fk_handle_gimbals):
            handle_utilities.create_and_connect_gimbal_visibility_attr(fk, fk_gimbal)
            handle_utilities.create_and_connect_rotation_order_attr(fk)
            handle_utilities.create_and_connect_rotation_order_attr(fk_gimbal)

        root = this.get_root()
        for handle in fk_handles+fk_handle_gimbals:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])

        this.fk_handles = fk_handles
        this.fk_joints = fk_joints
        this.fk_group = fk_group
        this.fk_handle_gimbals = fk_handle_gimbals

        return this
