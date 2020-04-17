from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_math.matrix import Matrix
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
import rig_math.utilities as rmu
import rig_factory.utilities.handle_utilities as handle_utils
import rig_factory.utilities.limb_utilities as limb_utils
import rig_factory


class StandardIKArmGuide(ChainGuide):
    default_settings = dict(
        root_name='arm',
        size=4.0,
        side='left'
    )

    twist_joint_counts = ObjectListProperty(
        name='twist_joint_counts',
        default_value=[0, 5, 5, 0]
    )

    def __init__(self, **kwargs):
        super(StandardIKArmGuide, self).__init__(**kwargs)
        self.toggle_class = StandardIKArm.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'arm')
        this = super(StandardIKArmGuide, cls).create(controller, **kwargs)
        size = this.size
        this.handles[2].plugs['tz'].set_value(-5.0 * size)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(StandardIKArmGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        blueprint['twist_joint_counts'] = self.twist_joint_counts
        return blueprint


class StandardIKArm(Part):
    wrist_handle = ObjectProperty(
        name='wrist_handle'
    )
    wrist_handle_gimbal = ObjectProperty(
        name='wrist_handle_gimbal'
    )
    elbow_handle = ObjectProperty(
        name='elbow_handle'
    )
    clavicle_handle = ObjectProperty(
        name='clavicle_handle'
    )
    ik_group = ObjectProperty(
        name='ik_group'
    )
    ik_joints = ObjectListProperty(
        name='ik_joints'
    )
    stretchable_plugs = ObjectListProperty(
        name='stretchable_plugs'
    )

    clavicle_handle_gimbal = ObjectProperty(
        name='clavicle_handle_gimbal'
    )

    def __init__(self, **kwargs):
        super(StandardIKArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        twist_joint_counts = kwargs.get('twist_joint_counts', [0, 5, 5, 0])
        #if not isinstance(twist_joint_counts, (tuple, list)) or len(twist_joint_counts) != 4:
        #    raise Exception('the keyword argument "twist_joint_counts" must be a list of exactly 4 integers')

        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(StandardIKArm, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        clavicle_root_matrix = matrices[0]
        clavicle_matrix = matrices[1]
        elbow_matrix = matrices[2]
        wrist_matrix = matrices[3]
        hand_matrix = matrices[4]
        biped_rotation_order = rig_factory.BipedRotationOrder()

        ik_joints = []
        ik_group = this.create_child(
            Transform,
            root_name='%s_ik' % root_name
        )
        ik_joint_parent = utility_group
        for i, joint_str in enumerate(['clavicle', 'armUpper', 'armLower', 'hand', 'handTip']):
            if i != 0:
                ik_joint_parent = ik_joints[-1]
            ik_joint = this.create_child(
                Joint,
                parent=ik_joint_parent,
                root_name='{0}_{1}IK'.format(root_name, joint_str),
                matrix=matrices[i],
            )
            ik_joint.zero_rotation()
            ik_joints.append(ik_joint)

        ik_wrist_handle = this.create_handle(
            parent=ik_group,
            root_name='{0}_wristIK'.format(root_name),
            size=size * 2.5,
            side=side,
            matrix=wrist_matrix,
            shape='cube',
            rotation_order=biped_rotation_order.arm_ik
        )

        ik_wrist_handle_gimbal = this.create_handle(
            parent=ik_wrist_handle,
            root_name='{0}_wristIKGimbal'.format(root_name),
            size=size*2.0,
            side=side,
            matrix=wrist_matrix,
            shape='cube',
            rotation_order=biped_rotation_order.arm_ik
        )

        pole_position = rmu.calculate_pole_vector_position(
            clavicle_matrix.get_translation(),
            elbow_matrix.get_translation(),
            wrist_matrix.get_translation(),
            distance=((size/10) + 1) * 20
        )

        ik_elbow_handle = this.create_handle(
            parent=ik_wrist_handle,
            root_name='{0}_elbowIK'.format(root_name),
            size=size * 0.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='ball',
        )

        ik_handle = controller.create_ik_handle(
            ik_joints[1],
            ik_joints[3],
            parent=ik_group,
            solver='ikRPSolver'
        )

        clavicle_handle = this.create_handle(
            parent=ik_group,
            root_name='{0}_clavicleIK'.format(root_name),
            size=size * 2.5,
            side=side,
            matrix=clavicle_root_matrix,
            shape='c_curve',
            rotation_order=biped_rotation_order.arm_clavicle,
        )

        clavicle_handle_gimbal = this.create_handle(
            parent=clavicle_handle,
            root_name='{0}_clavicleIKGimbal'.format(root_name),
            size=size * 2.0,
            side=side,
            matrix=clavicle_root_matrix,
            shape='c_curve',
            rotation_order=biped_rotation_order.arm_clavicle,
        )

        clavicle_root = clavicle_handle.create_child(
            Transform,
            root_name='{0}_clavicleRootIK'.format(root_name),
            matrix=ik_joints[1].get_matrix(),
        )

        controller.create_parent_constraint(
            clavicle_handle_gimbal,
            ik_joints[0],
            mo=True,
        )

        clavicle_handle.stretch_shape(matrices[1].get_translation())
        clavicle_handle_gimbal.stretch_shape(matrices[1].get_translation())

        controller.create_orient_constraint(
            ik_wrist_handle_gimbal,
            ik_joints[3],
            mo=True,
        )
        controller.create_point_constraint(
            ik_wrist_handle_gimbal,
            ik_handle,
            mo=True,
        )
        twist_plug = ik_wrist_handle_gimbal.create_plug(
            'twist',
            at='double',
            k=True,
            dv=0.0
        )

        handle_utils.create_and_connect_gimbal_visibility_attr(ik_wrist_handle, ik_wrist_handle_gimbal)
        handle_utils.create_and_connect_gimbal_visibility_attr(clavicle_handle, clavicle_handle_gimbal)
        for handle in [ik_wrist_handle, ik_wrist_handle_gimbal, clavicle_handle, clavicle_handle_gimbal]:
            handle_utils.create_and_connect_rotation_order_attr(handle)

        twist_plug.connect_to(ik_handle.plugs['twist'])
        locator_1 = ik_joints[2].create_child(Locator, root_name='{0}_rootLine'.format(root_name))
        locator_2 = ik_elbow_handle.create_child(Locator, root_name='{0}_tipLine'.format(root_name))
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        line = ik_group.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        controller.create_pole_vector_constraint(ik_elbow_handle, ik_handle)

        # make stretchable
        limb_utils.convert_ik_to_stretchable(clavicle_root,
                                             ik_wrist_handle_gimbal,
                                             (ik_joints[2], ik_joints[3]),
                                             ik_wrist_handle_gimbal,
                                             attr_labels=['bicep', 'forearm'],
                                             invert_translation=True if side == 'right' else False)

        ik_handle.plugs['visibility'].set_value(False)
        utility_group.plugs['visibility'].set_value(True)

        root = this.get_root()
        for handle in (ik_wrist_handle, ik_wrist_handle_gimbal, clavicle_handle, clavicle_handle_gimbal):
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])
        for axis in ('x', 'y', 'z'):
            root.add_plugs([ik_elbow_handle.plugs['t{0}'.format(axis)]])
        root.add_plugs([twist_plug])

        this.wrist_handle = ik_wrist_handle
        this.wrist_handle_gimbal = ik_wrist_handle_gimbal
        this.elbow_handle = ik_elbow_handle
        this.clavicle_handle = clavicle_handle
        this.clavicle_handle_gimbal = clavicle_handle_gimbal
        this.ik_joints = ik_joints
        this.ik_group = ik_group
        return this
