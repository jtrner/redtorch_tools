from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
import rig_factory.utilities.handle_utilities as handle_utilities
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
import rig_factory


class StandardFKArmGuide(ChainGuide):
    default_settings = dict(
        root_name='arm',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(StandardFKArmGuide, self).__init__(**kwargs)
        self.toggle_class = StandardFKArm.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'arm')
        this = super(StandardFKArmGuide, cls).create(controller, **kwargs)
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(StandardFKArmGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class StandardFKArm(Part):
    fk_group = ObjectProperty(
        name='fk_group'
    )
    fk_handles = ObjectListProperty(
        name='fk_handles'
    )
    fk_handle_gimbals = ObjectListProperty(
        name='fk_handle_gimbals'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )

    def __init__(self, **kwargs):
        super(StandardFKArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(StandardFKArm, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        biped_rotation_order = rig_factory.BipedRotationOrder()

        fk_joints = []
        fk_handles = []
        fk_handle_gimbals = []
        fk_group = this.create_child(
            Transform,
            root_name='%s_fk' % root_name
        )
        fk_joint_parent = utility_group
        fk_handle_parent = fk_group
        fk_rotation_orders=(biped_rotation_order.arm_clavicle,
                            biped_rotation_order.arm_upper_fk,
                            biped_rotation_order.arm_lower_fk,
                            biped_rotation_order.arm_wrist_fk,
                            biped_rotation_order.arm_wrist_fk)
        for x, (joint_str, rotation_order) in enumerate(zip(('clavicleFK',
                                                             'armUpperFK',
                                                             'armLowerFK',
                                                             'handFK',
                                                             'handTipFK'),
                                                            fk_rotation_orders)):
            matrix = matrices[x]
            fk_joint = this.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, joint_str),
                matrix=matrix,
                parent=fk_joint_parent
            )
            fk_joint_parent = fk_joint
            fk_joint.zero_rotation()
            if x < 4:
                fk_handle = this.create_handle(
                    root_name='{0}_{1}'.format(root_name, joint_str),
                    size=size * 2.5,
                    matrix=matrix,
                    side=side,
                    shape='c_curve' if joint_str == 'clavicleFK' else 'square',
                    parent=fk_group,
                    rotation_order=rotation_order
                )
                controller.create_parent_constraint(  # constrain instead of parenting to prevent inheriting visibility
                    fk_handle_parent,
                    fk_handle.groups[0],
                    mo=True)
                fk_handles.append(fk_handle)
                fk_handle.stretch_shape(matrices[x + 1].get_translation())

                fk_handle_gimbal = this.create_handle(
                    root_name='{0}_{1}Gimbal'.format(root_name, joint_str),
                    size=size * 2.0,
                    matrix=matrix,
                    side=side,
                    shape='c_curve' if joint_str == 'clavicleFK' else 'square',
                    rotation_order=rotation_order,
                    parent=fk_handle,
                )
                fk_handle_gimbals.append(fk_handle_gimbal)
                fk_handle_gimbal.stretch_shape(matrices[x + 1].get_translation())

                controller.create_parent_constraint(
                    fk_handle_gimbal,
                    fk_joint
                )
                handle_utilities.create_and_connect_gimbal_visibility_attr(fk_handle, fk_handle_gimbal)
                handle_utilities.create_and_connect_rotation_order_attr(fk_handle)
                handle_utilities.create_and_connect_rotation_order_attr(fk_handle_gimbal)

                fk_handle_parent = fk_handle_gimbal

            fk_joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            fk_joints.append(fk_joint)

        root = this.get_root()
        for fk_handle in fk_handles:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([fk_handle.plugs['{0}{1}'.format(transform, axis)]])

        this.fk_handles = fk_handles
        this.fk_handle_gimbals = fk_handle_gimbals
        this.fk_joints = fk_joints
        this.fk_group = fk_group
        return this
