from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_math.matrix import Matrix
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
import rig_math.utilities as rmu
import rig_factory.utilities.handle_utilities as handle_utils
import rig_factory.utilities.limb_utilities as limb_utils
import rig_factory


class StandardIKLegGuide(ChainGuide):
    default_settings = dict(
        root_name='leg',
        size=4.0,
        side='left'
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    def __init__(self, **kwargs):
        super(StandardIKLegGuide, self).__init__(**kwargs)
        self.toggle_class = StandardIKLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'leg')
        this = super(StandardIKLegGuide, cls).create(controller, **kwargs)
        body = this.get_root()
        root_name = this.root_name
        size = this.size
        side = this.side
        size_plug = this.plugs['size']

        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']

        pivot_handles = []
        pivot_joints = []
        for position in ['front', 'back', 'in', 'out']:
            pivot_root_name = '%s_%s' % (root_name, position)
            translate_values = this.handles[5].plugs['translate'].get_value()
            if position == 'front':
                translate_values = this.handles[6].plugs['translate'].get_value()
            elif position == 'back':
                translate_values = this.handles[4].plugs['translate'].get_value()
            handle = this.create_handle(
                root_name='%s_%s' % (root_name, position),
                index=None,
            )
            handle.plugs['translate'].set_value(translate_values)
            joint = handle.create_child(
                Joint,
                root_name=pivot_root_name
            )
            cone_x = joint.create_child(
                Cone,
                root_name='%s_%s_cone_x' % (root_name, position),
                size=size * 0.1,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                root_name='%s_%s_cone_y' % (root_name, position),
                size=size * 0.099,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                root_name='%s_%s_cone_z' % (root_name, position),
                size=size * 0.098,
                axis=[0.0, 0.0, 1.0]
            )
            pivot_handles.append(handle)
            pivot_joints.append(joint)
            controller.create_matrix_point_constraint(handle, joint)
            handle.mesh.assign_shading_group(body.shaders[side].shading_group)
            cone_x.mesh.assign_shading_group(body.shaders['x'].shading_group)
            cone_y.mesh.assign_shading_group(body.shaders['y'].shading_group)
            cone_z.mesh.assign_shading_group(body.shaders['z'].shading_group)
            size_multiply_plug.connect_to(handle.plugs['size'])
            size_multiply_plug.connect_to(cone_x.plugs['size'])
            size_multiply_plug.connect_to(cone_y.plugs['size'])
            size_multiply_plug.connect_to(cone_z.plugs['size'])
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=0.0
            )
            cone_x.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_y.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_z.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
        front_handle, back_handle, in_handle, out_handle = pivot_handles
        front_joint, back_joint, in_joint, out_joint = pivot_joints
        controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        controller.create_aim_constraint(back_handle, front_joint, aim=[0, 0, -1])
        controller.create_aim_constraint(in_handle, out_joint, aim=[-1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        controller.create_aim_constraint(out_handle, in_joint, aim=[1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        this.pivot_joints = pivot_joints
        all_joints = this.joints + this.pivot_joints

        return this

    def get_toggle_blueprint(self):
        blueprint = super(StandardIKLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint


class StandardIKLeg(Part):
    hip_handle = ObjectProperty(
        name='hip_handle'
    )
    ankle_handle = ObjectProperty(
        name='ankle_handle'
    )
    knee_handle = ObjectProperty(
        name='knee_handle'
    )
    toe_handle = ObjectProperty(
        name='toe_handle'
    )
    toe_handle_gimbal = ObjectProperty(
        name='toe_handle_gimbal'
    )
    ik_group = ObjectProperty(
        name='ik_group'
    )
    ik_joints = ObjectListProperty(
        name='ik_joints'
    )
    ik_handles = ObjectListProperty(
        name='ik_handles'
    )
    stretchable_attr_object = ObjectProperty(
        name='stretchable_attr_object'
    )
    ik_hip_handle_gimbal = ObjectProperty(
        name='ik_hip_handle_gimbal'
    )
    ik_ankle_handle_gimbal = ObjectProperty(
        name='ik_ankle_handle_gimbal'
    )

    def __init__(self, **kwargs):
        super(StandardIKLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(StandardIKLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        hip_matrix = matrices[0]
        knee_matrix = matrices[1]
        ankle_matrix = matrices[2]
        foot_matrix = matrices[3]
        toe_matrix = matrices[4]
        front_pivot_matrix = matrices[5]
        back_pivot_matrix = matrices[6]
        in_pivot_matrix = matrices[7]
        out_pivot_matrix = matrices[8]
        biped_rotation_order = rig_factory.BipedRotationOrder()

        # Ik Leg
        ik_joints = []
        ik_group = this.create_child(
            Transform,
            root_name='%s_IK' % root_name
        )
        ik_joint_parent = utility_group
        for i, joint_str in enumerate(['legUpper', 'legLower', 'ankle', 'toe', 'toeTip']):
            if i != 0:
                ik_joint_parent = ik_joints[-1]
            ik_joint = this.create_child(
                Joint,
                root_name='{0}_{1}IK'.format(root_name, joint_str),
                parent=ik_joint_parent,
                matrix=matrices[i],
            )
            ik_joint.zero_rotation()
            ik_joints.append(ik_joint)

        # ### Hip Handle ###
        hip_handle = this.create_handle(
            root_name='{0}_hipIK'.format(root_name),
            size=size * 5,
            side=side,
            matrix=Matrix(*hip_matrix.get_translation()),
            shape='c_curve',
            parent=ik_group,
            rotate_order=biped_rotation_order.leg_hip,
        )
        if side == 'left':
            matrix = Matrix()
            matrix.set_scale((-1.0*size*5, size * 5, size * 5))
            hip_handle.plugs['shape_matrix'].set_value(matrix)

        # ### Hip Handle Gimbal ###
        hip_handle_gimbal = this.create_handle(
            root_name='{0}_hipIKGimbal'.format(root_name),
            size=size * 4,
            side=side,
            matrix=Matrix(*hip_matrix.get_translation()),
            shape='c_curve',
            parent=hip_handle,
            rotate_order=biped_rotation_order.leg_hip,
        )
        if side == 'left':
            matrix = Matrix()
            matrix.set_scale((-1.0*size*4, size * 4, size * 4))
            hip_handle_gimbal.plugs['shape_matrix'].set_value(matrix)

        controller.create_matrix_point_constraint(
            hip_handle_gimbal,
            ik_joints[0]
        )

        # ### Ankle IK ###
        ik_ankle_handle = this.create_handle(
            root_name='{0}_ankleIK'.format(root_name),
            size=size * 2.5,
            side=side,
            matrix=Matrix(*ankle_matrix.get_translation()),
            shape='cube',
            parent=ik_group,
            rotate_order=biped_rotation_order.leg_ik,
        )
        ik_ankle_handle_gimbal = this.create_handle(
            root_name='{0}_ankleIKGimbal'.format(root_name),
            size=size * 2.0,
            side=side,
            matrix=Matrix(*ankle_matrix.get_translation()),
            shape='cube',
            parent=ik_ankle_handle,
            rotate_order=biped_rotation_order.leg_ik,
        )
        pole_position = rmu.calculate_pole_vector_position(
            hip_matrix.get_translation(),
            knee_matrix.get_translation(),
            ankle_matrix.get_translation(),
            distance=((size * 0.1) + 1) * 20
        )
        ik_knee_handle = this.create_handle(
            root_name='{0}_kneeIK'.format(root_name),
            size=size * -1.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='arrow',
        )
        controller.create_matrix_point_constraint(
            ik_ankle_handle_gimbal,
            ik_knee_handle.groups[0]
        )

        locator_1 = ik_joints[1].create_child(Locator)
        locator_2 = ik_knee_handle.create_child(Locator)
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)

        line = ik_group.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))

        # Build Foot Roll ##############################################################################################
        foot_roll_offset_group = controller.create_object(
            Transform,
            root_name='{0}_footRollOffsetIK'.format(root_name),
            side=side,
            parent=ik_ankle_handle_gimbal,
        )
        rock_in_group_zero = foot_roll_offset_group.create_child(
            Transform,
            root_name='{0}_rockInIKZero'.format(root_name),
            side=side,
            matrix=in_pivot_matrix
        )
        rock_in_group = rock_in_group_zero.create_child(
            Transform,
            root_name='{0}_rockInIK'.format(root_name),
            side=side,
            matrix=in_pivot_matrix
        )
        rock_out_group_zero = rock_in_group.create_child(
            Transform,
            root_name='{0}_rockOutIKZero'.format(root_name),
            side=side,
            matrix=out_pivot_matrix,
        )
        rock_out_group = rock_out_group_zero.create_child(
            Transform,
            root_name='{0}_rockOutIK'.format(root_name),
            side=side,
            matrix=out_pivot_matrix,
        )
        ik_roll_front_zero = rock_out_group.create_child(
            Transform,
            root_name='{0}_rockFrontIKZero'.format(root_name),
            side=side,
            matrix=front_pivot_matrix,
        )
        ik_roll_front = ik_roll_front_zero.create_child(
            Transform,
            root_name='{0}_rockFrontIK'.format(root_name),
            side=side,
            matrix=front_pivot_matrix,
        )
        ik_roll_back_zero = ik_roll_front.create_child(
            Transform,
            root_name='{0}_rockBackIKZero'.format(root_name),
            side=side,
            matrix=back_pivot_matrix,
            parent=ik_roll_front
        )
        ik_roll_back = ik_roll_back_zero.create_child(
            Transform,
            root_name='{0}_rockBackIK'.format(root_name),
            side=side,
            matrix=back_pivot_matrix,
        )

        bend_top = controller.create_object(
            Transform,
            root_name='{0}_toeBendIKZero'.format(root_name),
            side=side,
            matrix=foot_matrix,
            parent=ik_roll_back
        )
        bend_driver = controller.create_object(
            Transform,
            root_name='{0}_toeBendTopIK'.format(root_name),
            side=side,
            matrix=foot_matrix,
            parent=bend_top
        )

        ball_roll = controller.create_object(
            Transform,
            root_name='{0}_ballRollIK'.format(root_name),
            side=side,
            matrix=foot_matrix,
            parent=ik_roll_back
        )

        foot_roll_plug = ik_ankle_handle.create_plug(
            'foot_roll',
            at='double',
            k=True,
            dv=0.0,
        )

        rock_plug = ik_ankle_handle.create_plug(
            'rock',
            at='double',
            k=True,
            dv=0.0
        )

        break_plug = ik_ankle_handle.create_plug(
            'break',
            at='double',
            k=True,
            dv=45.0
        )

        ik_toe_handle = this.create_handle(
            root_name='{0}_toeIK'.format(root_name),
            size=size*2.5,
            side=side,
            matrix=foot_matrix,
            shape='square',
            parent=ik_group
        )
        controller.create_parent_constraint(
            bend_top,
            ik_toe_handle.groups[0],
            mo=True
        )

        ik_toe_handle.stretch_shape(toe_matrix.get_translation())

        ik_toe_handle_gimbal = this.create_handle(
            root_name='{0}_toeIKGimbal'.format(root_name),
            size=size*2.0,
            side=side,
            matrix=foot_matrix,
            shape='square',
            parent=ik_toe_handle,
            rotate_order=biped_rotation_order.leg_ik,
        )
        ik_toe_handle_gimbal.stretch_shape(toe_matrix.get_translation())

        ik_toe_bend = ik_toe_handle_gimbal.create_child(
            Transform,
            root_name='{0}_toeBendIK'.format(root_name),
            side=side,
            matrix=foot_matrix
        )

        # Front Roll
        toe_tip_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ik_roll_tip' % root_name
        )
        foot_roll_plug.connect_to(toe_tip_remap.plugs['inputValue'])
        break_plug.connect_to(toe_tip_remap.plugs['value'].element(0).child(0))
        toe_tip_remap.plugs['value'].element(0).child(1).set_value(0.0)
        toe_tip_remap.plugs['value'].element(1).child(0).set_value(245.0)
        toe_tip_remap.plugs['value'].element(1).child(1).set_value(200.0)
        toe_tip_remap.plugs['outValue'].connect_to(ik_roll_front.plugs['rotateX'])

        # Ball Roll
        toe_ball_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ik_ball_roll' % root_name
        )
        foot_roll_plug.connect_to(toe_ball_remap.plugs['inputValue'])
        toe_ball_remap.plugs['value'].element(0).child(0).set_value(0.0)
        toe_ball_remap.plugs['value'].element(0).child(1).set_value(0.0)
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(0))
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(1))
        toe_ball_remap.plugs['outValue'].connect_to(ball_roll.plugs['rotateX'])

        # Heel Roll
        heel_roll_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ik_heel_roll' % root_name
        )
        foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
        heel_roll_remap.plugs['value'].element(0).child(0).set_value(0.0)
        heel_roll_remap.plugs['value'].element(0).child(1).set_value(0.0)
        heel_roll_remap.plugs['value'].element(1).child(0).set_value(-100.0)
        heel_roll_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        heel_roll_remap.plugs['outValue'].connect_to(ik_roll_back.plugs['rotateX'])

        # rock in
        rock_in_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ik_rock_in' % root_name
        )
        rock_plug.connect_to(rock_in_remap.plugs['inputValue'])
        rock_in_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_in_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_in_remap.plugs['value'].element(1).child(0).set_value(-100)
        rock_in_remap.plugs['value'].element(1).child(1).set_value(100)
        rock_in_remap.plugs['outValue'].connect_to(rock_in_group.plugs['rotateZ'])

        # rock out
        rock_out_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ik_rock_out' % root_name
        )
        rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
        rock_out_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_out_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_out_remap.plugs['value'].element(1).child(0).set_value(100.0)
        rock_out_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateZ'])

        # Stretchable
        limb_utils.convert_ik_to_stretchable(hip_handle,
                                             ik_ankle_handle_gimbal,
                                             (ik_joints[1], ik_joints[2]),
                                             ik_ankle_handle_gimbal,
                                             attr_labels=['thigh', 'shin'],
                                             invert_translation=True if side == 'right' else False)

        ankle_ik_solver = controller.create_ik_handle(
            ik_joints[0],
            ik_joints[2],
            parent=ball_roll,
            solver='ikRPSolver'
        )
        foot_ball_ik_solver = controller.create_ik_handle(
            ik_joints[2],
            ik_joints[3],
            parent=ball_roll,
            solver='ikRPSolver'
        )
        toe_tip_ik_solver = controller.create_ik_handle(
            ik_joints[3],
            ik_joints[4],
            parent=ik_toe_bend,
            solver='ikRPSolver'
        )

        controller.create_pole_vector_constraint(
            ik_knee_handle,
            ankle_ik_solver
        )

        handle_utils.create_and_connect_gimbal_visibility_attr(hip_handle, hip_handle_gimbal)
        handle_utils.create_and_connect_gimbal_visibility_attr(ik_ankle_handle, ik_ankle_handle_gimbal)
        handle_utils.create_and_connect_gimbal_visibility_attr(ik_toe_handle, ik_toe_handle_gimbal)

        for handle in [hip_handle,
                       hip_handle_gimbal,
                       ik_ankle_handle,
                       ik_ankle_handle_gimbal,
                       ik_toe_handle,
                       ik_toe_handle_gimbal]:
            handle_utils.create_and_connect_rotation_order_attr(handle)

        ankle_ik_solver.plugs['visibility'].set_value(False)
        foot_ball_ik_solver.plugs['visibility'].set_value(False)
        toe_tip_ik_solver.plugs['visibility'].set_value(False)
        utility_group.plugs['visibility'].set_value(True)

        root = this.get_root()
        for handle in [hip_handle, hip_handle_gimbal, ik_ankle_handle, ik_ankle_handle_gimbal, ik_toe_handle,
                       ik_toe_handle_gimbal]:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])
        for handle in [ik_knee_handle]:
            for axis in ('x', 'y', 'z'):
                root.add_plugs([handle.plugs['t{0}'.format(axis)]])

        this.ik_hip_handle = hip_handle
        this.ik_hip_handle_gimbal = hip_handle_gimbal
        this.ik_ankle_handle = ik_ankle_handle
        this.ik_ankle_handle_gimbal = ik_ankle_handle_gimbal
        this.ik_knee_handle = ik_knee_handle
        this.ik_toe_handle = ik_toe_handle
        this.ik_toe_handle_gimbal = ik_toe_handle_gimbal

        this.ik_joints = ik_joints
        this.ik_group = ik_group
        this.stretchable_attr_object = ik_ankle_handle
        return this
