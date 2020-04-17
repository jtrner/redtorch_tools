import copy
from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.rig_handles import WorldHandle, LocalHandle
import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_math.matrix import Matrix, compose_matrix
import rig_factory.utilities.limb_utilities as ltl
from rig_math.vector import Vector
import rig_math.utilities as rmu
import rig_factory.positions as pos


class QuadrupedBackLegIkGuide(ChainGuide):

    thigh_name = DataProperty(
        name='thigh_name',
        default_value='thigh'
    )

    calf_name = DataProperty(
        name='calf_name',
        default_value='calf'
    )

    ankle_name = DataProperty(
        name='ankle_name',
        default_value='ankle'
    )

    foot_name = DataProperty(
        name='foot_name',
        default_value='foot'
    )

    toe_name = DataProperty(
        name='toe_name',
        default_value='toe'
    )

    pole_distance = DataProperty(
        name='pole_distance',
        default_value=20.0
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    default_settings = dict(
        root_name='back_leg',
        size=3.0,
        side='left',
        pole_distance=20.0
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLegIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('handle_positions', copy.copy(pos.QUADRUPED_IK_BACK_LEG_POSITIONS))
        this = super(QuadrupedBackLegIkGuide, cls).create(controller, **kwargs)
        this.create_foot_pivots()

        return this

    def create_foot_pivots(self, **kwargs):
        kwargs.setdefault('root_name', 'back_leg')
        body = self.get_root()
        root_name = self.root_name
        size = self.size
        side = self.side
        size_plug = self.plugs['size']
        size_multiply_node = self.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']
        pivot_handles = []
        pivot_joints = []
        for position in ['front', 'back', 'in', 'out']:
            pivot_root_name = '%s_pivot_%s' % (root_name, position)
            translate_values = self.handles[5].plugs['translate'].get_value()
            if position == 'front':
                translate_values = self.handles[6].plugs['translate'].get_value()
            elif position == 'back':
                translate_values = self.handles[4].plugs['translate'].get_value()
            handle = self.create_handle(
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
            self.controller.create_matrix_point_constraint(handle, joint)
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
                radius=1.0
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
        self.controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        self.controller.create_aim_constraint(back_handle, front_joint, aim=[0, 0, -1])
        self.controller.create_aim_constraint(in_handle, out_joint, aim=[-1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        self.controller.create_aim_constraint(out_handle, in_joint, aim=[1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        self.pivot_joints = pivot_joints

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBackLegIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedBackLegIk(Part):

    thigh_name = DataProperty(
        name='thigh_name',
        default_value='thigh'
    )

    calf_name = DataProperty(
        name='calf_name',
        default_value='calf'
    )

    ankle_name = DataProperty(
        name='ankle_name',
        default_value='ankle'
    )

    foot_name = DataProperty(
        name='foot_name',
        default_value='foot'
    )

    toe_name = DataProperty(
        name='toe_name',
        default_value='toe'
    )

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
    hock_handle = ObjectProperty(
        name='hock_handle'
    )

    pole_distance = DataProperty(
        name='pole_distance',
        default_value=20
    )

    stretchable_attr_object = ObjectProperty(
        name='stretchable_attr_object'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        matrix_count = len(kwargs.get('matrices', []))
        if matrix_count != 9:
            raise Exception('you must provide exactly 9 matrices to create a %s (Not %s)' % (cls.__name__, matrix_count))
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedBackLegIk, cls).create(controller, **kwargs)
        return this.build(this, **kwargs)

    @staticmethod
    def build(this, **kwargs):
        controller = this.controller

        # variables

        root_name = this.root_name
        size = this.size
        side = this.side
        aim_vector = env.side_aim_vectors[side]
        up_vector = env.side_up_vectors[side]

        # positions

        matrices = this.matrices
        thigh_matrix = matrices[0]
        knee_matrix = matrices[1]
        ankle_matrix = matrices[2]
        foot_matrix = matrices[3]
        toe_matrix = matrices[4]
        front_pivot_matrix = matrices[5]
        back_pivot_matrix = matrices[6]
        in_pivot_matrix = matrices[7]
        out_pivot_matrix = matrices[8]
        thigh_position = thigh_matrix.get_translation()
        knee_position = knee_matrix.get_translation()
        ankle_position = ankle_matrix.get_translation()
        foot_position = foot_matrix.get_translation()
        thigh_length = (knee_position - thigh_position).mag()
        shin_length = (ankle_position - knee_position).mag()
        ankle_length = (foot_position - ankle_position).mag()
        leg_length = thigh_length + shin_length + ankle_length
        start_length = (foot_position - thigh_position).mag()
        reverse_ankle_vector = (ankle_position - foot_position).normalize()
        ankle_aim_position = foot_position + (reverse_ankle_vector * (leg_length *1.2))
        foot_side_position = foot_position + Vector([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        pole_position = Vector(rmu.calculate_pole_vector_position(
            thigh_position,
            knee_position,
            ankle_position,
            distance=size*this.pole_distance
        ))
        reverse_ankle_matrix = compose_matrix(
            foot_position,
            ankle_position,
            pole_position
        )
        if side == 'right':
            reverse_ankle_matrix.flip_y()
            reverse_ankle_matrix.flip_z()

        hip_matrix = compose_matrix(
            thigh_position,
            foot_position,
            pole_position
        )
        thigh_up_position = list(copy.copy(thigh_position))
        thigh_up_position[1] = thigh_up_position[1] + (size*5)

        #  objects

        root = this.get_root()

        hip_handle = this.create_handle(  # user input for the fot
            handle_type=LocalHandle,
            root_name='{0}_hip'.format(root_name),
            size=size*0.25,
            matrix=thigh_matrix,
            shape='cube'
        )

        foot_handle = this.create_handle(  # user input for the fot
            handle_type=WorldHandle,
            root_name='{0}_foot'.format(root_name),
            size=size*1.5,
            matrix=Matrix(*foot_position),
            shape='cube'
        )

        foot_side_transform = foot_handle.create_child(
            Transform,
            root_name='{0}_foot_up_target'.format(root_name),
            matrix=foot_side_position,
        )

        hip_static_transform = hip_handle.create_child(  # positioned at , remains static
            Transform,
            root_name='{0}_hip_static'.format(root_name),
            matrix=hip_matrix,
        )

        hip_aim_transform = hip_handle.create_child(  # Positioned at thigh, aims at foot
            Transform,
            root_name='{0}_hip_aim'.format(root_name),
            matrix=hip_matrix,
        )

        solver_plane_transform = this.create_child(  # represents the plane of action for the leg
            Transform,
            root_name='{0}_solver_plane'.format(root_name),
            matrix=Matrix(ankle_position),
        )

        ball_pivot = controller.create_object(
            Transform,
            root_name='{0}_ball_pivot'.format(root_name),
            side=side,
            matrix=Matrix(foot_matrix.get_translation()),
            parent=foot_handle.gimbal_handle
        )
        heel_pivot = controller.create_object(
            Transform,
            root_name='{0}_heel_pivot'.format(root_name),
            side=side,
            matrix=Matrix(back_pivot_matrix.get_translation()),
            parent=ball_pivot
        )
        foot_roll_offset_group = controller.create_object(
            Transform,
            root_name='{0}_foot_roll_offset'.format(root_name),
            side=side,
            parent=heel_pivot,
        )
        rock_in_group_zero = foot_roll_offset_group.create_child(
            Transform,
            root_name='{0}_rock_in_zero'.format(root_name),
            side=side,
            matrix=in_pivot_matrix
        )
        rock_in_group = rock_in_group_zero.create_child(
            Transform,
            root_name='{0}_rock_in'.format(root_name),
            side=side,
            matrix=in_pivot_matrix
        )
        rock_out_group_zero = rock_in_group.create_child(
            Transform,
            root_name='{0}_rock_out_zero'.format(root_name),
            side=side,
            matrix=out_pivot_matrix,
        )
        rock_out_group = rock_out_group_zero.create_child(
            Transform,
            root_name='{0}_rock_out'.format(root_name),
            side=side,
            matrix=out_pivot_matrix,
        )
        roll_front_zero = rock_out_group.create_child(
            Transform,
            root_name='{0}_rock_front_zero'.format(root_name),
            side=side,
            matrix=front_pivot_matrix,
        )
        roll_front = roll_front_zero.create_child(
            Transform,
            root_name='{0}_rock_front'.format(root_name),
            side=side,
            matrix=front_pivot_matrix,
        )
        roll_back_zero = roll_front.create_child(
            Transform,
            root_name='{0}_rock_back_zero'.format(root_name),
            side=side,
            matrix=back_pivot_matrix,
            parent=roll_front
        )
        roll_back = roll_back_zero.create_child(
            Transform,
            root_name='{0}_rock_back'.format(root_name),
            side=side,
            matrix=back_pivot_matrix,
        )
        bend_top = controller.create_object(
            Transform,
            root_name='{0}_toe_bend_zero'.format(root_name),
            side=side,
            matrix=foot_matrix,
            parent=roll_back
        )
        ball_roll_group = controller.create_object(
            Transform,
            root_name='{0}_ball_roll_orient'.format(root_name),
            side=side,
            matrix=foot_matrix,
            parent=roll_back
        )
        ball_roll = ball_roll_group.create_child(
            Transform,
            root_name='{0}_ball_roll'.format(root_name),
            matrix=foot_matrix,
        )
        ankle_position_transform = ball_roll.create_child(
            Transform,
            root_name='{0}_ankle_position'.format(root_name),
            matrix=ankle_matrix,
        )

        knee_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name='{0}_knee'.format(root_name),
            size=size,
            side=side,
            matrix=Matrix(*pole_position),
            shape='diamond'
        )

        hock_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name='{0}_hock'.format(root_name),
            size=size*2.0,
            side=side,
            matrix=reverse_ankle_matrix,
            shape='circle',
            axis='z'
        )

        controller.create_point_constraint(
            ball_roll,
            hock_handle.groups[0]
        )

        hock_auto_tilt_transform = hip_aim_transform.create_child(
            Transform,
            root_name='{0}_hock_auto_tilt'.format(root_name),
            matrix=Matrix(ankle_aim_position)
        )

        hock_no_tilt_transform = foot_handle.create_child(
            Transform,
            root_name='{0}_hock_no_tilt'.format(root_name),
            matrix=Matrix(ankle_aim_position)
        )

        hock_aim_target = foot_handle.create_child(
            Transform,
            root_name='{0}_hock_aim_target'.format(root_name),
            matrix=Matrix(ankle_aim_position)
        )

        hock_transform = hock_handle.gimbal_handle.create_child(
            Transform,
            root_name='{0}_hock'.format(root_name),
            matrix=Matrix(ankle_matrix)
        )

        hock_reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_hock' % root_name
        )
        hock_blend_colors = this.create_child(
            DependNode,
            node_type='blendColors',
            root_name='%s_hock_up' % root_name
        )

        hock_remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_hock' % root_name
        )

        toe_ball_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ball_roll' % root_name
        )

        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
            root_name=this.root_name + '_hock'
        )

        toe_tip_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_roll_tip' % root_name
        )
        heel_roll_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_heel_roll' % root_name
        )
        rock_in_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_rock_in' % root_name
        )
        rock_out_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_rock_out' % root_name
        )
        pivot_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_pivots' % root_name
        )

        joints = []
        joint_parent = this.joint_group
        for i, joint_str in enumerate([
            this.thigh_name,
            this.calf_name,
            this.ankle_name,
            this.toe_name,
            '%s_tip' % this.toe_name
        ]):
            joint = this.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, joint_str),
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
            joints.append(joint)
            joint_parent = joint


        controller.create_point_constraint(
            hip_handle,
            joints[0],
            mo=False
        )
        ankle_ik_solver = controller.create_ik_handle(
            joints[0],
            joints[2],
            parent=hock_transform,
            solver='ikRPSolver'
        )
        controller.create_pole_vector_constraint(
            knee_handle,
            ankle_ik_solver
        )

        hock_ik_solver = controller.create_ik_handle(
            joints[2],
            joints[3],
            parent=ball_roll,
            solver='ikSCSolver'
        )

        foot_ik_solver = controller.create_ik_handle(
            joints[3],
            joints[4],
            parent=ball_roll,
            solver='ikSCSolver'
        )

        ankle_ik_solver.plugs['visibility'].set_value(False)
        hock_ik_solver.plugs['visibility'].set_value(False)
        foot_ik_solver.plugs['visibility'].set_value(False)

        controller.create_aim_constraint(
            hock_aim_target,
            hock_handle.groups[0],
            worldUpType='object',
            worldUpObject=foot_side_transform,
            aimVector=aim_vector,
            upVector=up_vector

        )

        this.controller.create_aim_constraint(
            solver_plane_transform,
            hip_aim_transform,
            worldUpType='object',
            worldUpObject=knee_handle,
            aimVector=[0.0, 1.0, 0.0],
            upVector=[0.0, 0.0, -1.0],
            mo=False
        )

        controller.create_orient_constraint(
            foot_handle,
            joints[3],
            mo=True
        )

        controller.create_orient_constraint(
            foot_handle,
            solver_plane_transform,
            skip=('x', 'z'),
        )

        controller.create_point_constraint(
            hip_static_transform,
            foot_handle,
            solver_plane_transform,
            mo=False
        )

        controller.create_parent_constraint(
            solver_plane_transform,
            knee_handle.groups[0],
            mo=True
        )

        hock_target_point_constraint = controller.create_point_constraint(
            hock_auto_tilt_transform,
            hock_no_tilt_transform,
            hock_aim_target
        )


        #  stretchy

        ltl.convert_ik_to_stretchable(
            hip_static_transform,
            foot_handle,
            (joints[1], joints[2], joints[3]),
            foot_handle,
            stretch_plug=False
        )

        foot_roll_plug = foot_handle.create_plug(
            'foot_roll',
            at='double',
            k=True,
            dv=0.0,
        )
        break_plug = foot_handle.create_plug(
            'break',
            at='double',
            k=False,
            dv=0.0,
            min=0.0
        )
        ball_pivot_plug = foot_handle.create_plug(
            'foot_pivot',
            at='double',
            k=True,
            dv=0.0,
        )
        heel_pivot_plug = foot_handle.create_plug(
            'heel_pivot',
            at='double',
            k=True,
            dv=0.0,
        )
        rock_plug = foot_handle.create_plug(
            'rock',
            at='double',
            k=True,
            dv=0.0
        )

        auto_ankle_plug = foot_handle.create_plug(
            'auto_ankle',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )

        auto_ankle_plug.connect_to(hock_target_point_constraint.plugs['%sW0' % hock_auto_tilt_transform])
        auto_ankle_plug.connect_to(hock_reverse.plugs['inputX'])
        hock_reverse.plugs['outputX'].connect_to(hock_target_point_constraint.plugs['%sW1' % hock_no_tilt_transform])
        hock_blend_colors.plugs['color2'].set_value(hock_auto_tilt_transform.plugs['translate'].get_value())
        hock_blend_colors.plugs['output'].connect_to(hock_auto_tilt_transform.plugs['translate'])
        hip_static_transform.plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix1']
        )
        foot_handle.plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix2']
        )
        distance_node.plugs['distance'].connect_to(
            hock_remap_node.plugs['inputValue']
        )
        hock_remap_node.plugs['value'].element(0).child(0).set_value(start_length)
        hock_remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        hock_remap_node.plugs['value'].element(1).child(0).set_value(leg_length)
        hock_remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        hock_remap_node.plugs['outValue'].connect_to(hock_blend_colors.plugs['blender'])

        # Front Roll
        foot_roll_plug.connect_to(toe_tip_remap.plugs['inputValue'])
        break_plug.connect_to(toe_tip_remap.plugs['value'].element(0).child(0))
        toe_tip_remap.plugs['value'].element(0).child(1).set_value(0.0)
        toe_tip_remap.plugs['value'].element(1).child(0).set_value(245.0)
        toe_tip_remap.plugs['value'].element(1).child(1).set_value(200.0)
        toe_tip_remap.plugs['outValue'].connect_to(roll_front.plugs['rotateX'])

        # Heel Roll
        foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
        heel_roll_remap.plugs['value'].element(0).child(0).set_value(0.0)
        heel_roll_remap.plugs['value'].element(0).child(1).set_value(0.0)
        heel_roll_remap.plugs['value'].element(1).child(0).set_value(-100.0)
        heel_roll_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        heel_roll_remap.plugs['outValue'].connect_to(roll_back.plugs['rotateX'])

        # rock in
        rock_plug.connect_to(rock_in_remap.plugs['inputValue'])
        rock_in_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_in_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_in_remap.plugs['value'].element(1).child(0).set_value(-100)
        rock_in_remap.plugs['value'].element(1).child(1).set_value(100)
        rock_in_remap.plugs['outValue'].connect_to(rock_in_group.plugs['rotateZ'])

        # rock out
        rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
        rock_out_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_out_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_out_remap.plugs['value'].element(1).child(0).set_value(100.0)
        rock_out_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateZ'])

        # pivots
        if side == 'right':
            pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        else:
            pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
        ball_pivot_plug.connect_to(pivot_multiply.plugs['input1X'])
        heel_pivot_plug.connect_to(pivot_multiply.plugs['input1Z'])
        pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateY'])
        pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateY'])
        ankle_ik_solver.plugs['visibility'].set_value(0)

        # Ball Roll

        foot_roll_plug.connect_to(toe_ball_remap.plugs['inputValue'])
        toe_ball_remap.plugs['value'].element(0).child(0).set_value(0.0)
        toe_ball_remap.plugs['value'].element(0).child(1).set_value(0.0)
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(0))
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(1))
        toe_ball_remap.plugs['outValue'].connect_to(hock_handle.groups[1].plugs['rotateZ'])

        root.add_plugs(
            [
                foot_handle.plugs['tx'],
                foot_handle.plugs['ty'],
                foot_handle.plugs['tz'],
                foot_handle.plugs['rx'],
                foot_handle.plugs['ry'],
                foot_handle.plugs['rz'],
                foot_handle.plugs['sx'],
                foot_handle.plugs['sy'],
                foot_handle.plugs['sz'],
                hock_handle.plugs['rx'],
                hock_handle.plugs['ry'],
                hock_handle.plugs['rz'],
                knee_handle.plugs['tx'],
                knee_handle.plugs['ty'],
                knee_handle.plugs['tz'],
                rock_plug,
                auto_ankle_plug,
                #break_plug,
                foot_roll_plug,
                heel_pivot_plug,
                ball_pivot_plug,
            ]
        )

        this.joints = joints
        this.hip_handle = hip_handle
        this.hock_handle = hock_handle
        return this
