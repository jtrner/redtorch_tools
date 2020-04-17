"""
TODO:
    Add missing features from Richards example.
"""

from rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.line import Line
from rig_math.matrix import Matrix
from rig_math.vector import Vector
import rig_factory.utilities.limb_utilities as limb_utils
import rig_factory.environment as env
import rig_math.utilities as rmu


class QuadrupedFrontLegIkGuide(ChainGuide):
    default_settings = dict(
        root_name='leg',
        size=1.0,
        side='left'
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLegIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedFrontLegIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 6
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('root_name', 'leg')
        this = super(QuadrupedFrontLegIkGuide, cls).create(controller, **kwargs)
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
            pivot_root_name = '%s_pivot_%s' % (root_name, position)
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
        controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        controller.create_aim_constraint(back_handle, front_joint, aim=[0, 0, -1])
        controller.create_aim_constraint(in_handle, out_joint, aim=[-1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        controller.create_aim_constraint(out_handle, in_joint, aim=[1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        this.pivot_joints = pivot_joints

        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedFrontLegIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def align_knee(self):
        root_position = Vector(self.handles[1].get_translation())
        knee_position = Vector(self.handles[2].get_translation())
        up_vector_position = Vector(self.handles[0].get_translation())
        ankle_position = Vector(self.handles[4].get_translation())
        mag_1 = (knee_position - root_position).mag()
        mag_2 = (ankle_position - knee_position).mag()
        total_mag = mag_1 + mag_2
        if total_mag == 0.0:
            print 'Warning: the second joint had no angle. unable to calculate pole position'
            return up_vector_position
        fraction_1 = mag_1 / total_mag
        center_position = root_position + (ankle_position - root_position) * fraction_1
        angle_vector = (up_vector_position - center_position)
        angle_mag = angle_vector.mag()
        if angle_mag == 0.0:
            print 'Warning: the second joint had no angle. unable to calculate pole position'
            return up_vector_position

        distance = (knee_position - center_position).mag()
        knee_offset = angle_vector.normalize() * distance
        knee_position = center_position + knee_offset
        return self.handles[2].plugs['translate'].set_value(knee_position.data)


class QuadrupedFrontLegIk(Part):

    ankle_handle = ObjectProperty(
        name='ankle_handle'
    )
    knee_handle = ObjectProperty(
        name='knee_handle'
    )
    toe_handle = ObjectProperty(
        name='toe_handle'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLegIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedFrontLegIk, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        hip_matrix = matrices[0]
        knee_matrix = matrices[1]
        ankle_matrix = matrices[3]
        foot_matrix = matrices[4]
        toe_matrix = matrices[5]
        front_pivot_matrix = matrices[6]
        back_pivot_matrix = matrices[7]
        in_pivot_matrix = matrices[8]
        out_pivot_matrix = matrices[9]
        root = this.get_root()
        ik_joints = []
        joints = []
        joint_parent = this.joint_group
        ik_joint_parent = this.joint_group
        for i, joint_str in enumerate(['upper', 'middle', 'lower', 'ankle', 'toe', 'toe_tip']):
            if i != 0:
                joint_parent = joints[-1]
                ik_joint_parent = ik_joints[-1]
            ik_joint = this.create_child(
                Joint,
                root_name='{0}_{1}_kinematic'.format(root_name, joint_str),
                parent=ik_joint_parent,
                matrix=matrices[i],
            )
            ik_joint.zero_rotation()
            ik_joints.append(ik_joint)
            joint = this.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, joint_str),
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            joints.append(joint)
            ik_joint.plugs['v'].set_value(False)
            root.add_plugs(
                ik_joint.plugs['rx'],
                ik_joint.plugs['ry'],
                ik_joint.plugs['rz'],
                keyable=False
            )
            ik_joint.plugs['scale'].connect_to(joint.plugs['scale'])
        hip_transform = this.create_child(
            Transform,
            root_name='{0}_hip'.format(root_name),
            matrix=Matrix(*hip_matrix.get_translation()),
        )
        controller.create_matrix_point_constraint(
            hip_transform,
            ik_joints[0]
        )

        ankle_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name='{0}_ankle'.format(root_name),
            matrix=Matrix(*ankle_matrix.get_translation()),
            shape='cube',
        )
        pole_position = rmu.calculate_pole_vector_position(
            hip_matrix.get_translation(),
            knee_matrix.get_translation(),
            ankle_matrix.get_translation(),
            distance=((size * 0.1) + 1.0) * 50
        )
        ankle_pole_transform = this.create_child(
            Transform,
            root_name='{0}_ankle_pole'.format(root_name),
            matrix=ankle_matrix,
        )
        controller.create_orient_constraint(
            ankle_handle,
            ankle_pole_transform,
            skip=('x', 'z'),
        )
        controller.create_point_constraint(
            hip_transform,
            ankle_handle,
            ankle_pole_transform
        )
        knee_handle = this.create_handle(
            root_name='{0}_knee'.format(root_name),
            size=size*0.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='ball',
        )
        locator_1 = joints[1].create_child(Locator)
        locator_2 = knee_handle.create_child(Locator)
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        line = this.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        ball_pivot = controller.create_object(
            Transform,
            root_name='{0}_ball_pivot'.format(root_name),
            side=side,
            matrix=Matrix(foot_matrix.get_translation()),
            parent=ankle_handle.gimbal_handle
        )
        heel_pivot = controller.create_object(
            Transform,
            root_name='{0}_heel_pivot'.format(root_name),
            side=side,
            matrix=Matrix(back_pivot_matrix.get_translation()),
            parent=ball_pivot
        )
        toe_povot = controller.create_object(
            Transform,
            root_name='{0}_toe_pivot'.format(root_name),
            side=side,
            matrix=Matrix(toe_matrix.get_translation()),
            parent=heel_pivot
        )
        foot_roll_offset_group = controller.create_object(
            Transform,
            root_name='{0}_foot_roll_offset'.format(root_name),
            side=side,
            parent=toe_povot,
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
        foot_roll_plug = ankle_handle.create_plug(
            'foot_roll',
            at='double',
            k=True,
            dv=0.0,
        )
        break_plug = ankle_handle.create_plug(
            'break',
            at='double',
            k=True,
            dv=45.0,
            min=0.0
        )
        toe_pivot_plug = ankle_handle.create_plug(
            'toe_pivot',
            at='double',
            k=True,
            dv=0.0,
        )
        ball_pivot_plug = ankle_handle.create_plug(
            'ball_pivot',
            at='double',
            k=True,
            dv=0.0,
        )
        heel_pivot_plug = ankle_handle.create_plug(
            'heel_pivot',
            at='double',
            k=True,
            dv=0.0,
        )
        rock_plug = ankle_handle.create_plug(
            'rock',
            at='double',
            k=True,
            dv=0.0
        )

        # Front Roll
        toe_tip_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_roll_tip' % root_name
        )
        foot_roll_plug.connect_to(toe_tip_remap.plugs['inputValue'])
        break_plug.connect_to(toe_tip_remap.plugs['value'].element(0).child(0))
        toe_tip_remap.plugs['value'].element(0).child(1).set_value(0.0)
        toe_tip_remap.plugs['value'].element(1).child(0).set_value(245.0)
        toe_tip_remap.plugs['value'].element(1).child(1).set_value(200.0)
        toe_tip_remap.plugs['outValue'].connect_to(roll_front.plugs['rotateX'])

        # Ball Roll
        toe_ball_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_ball_roll' % root_name
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
            root_name='%s_heel_roll' % root_name
        )
        foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
        heel_roll_remap.plugs['value'].element(0).child(0).set_value(0.0)
        heel_roll_remap.plugs['value'].element(0).child(1).set_value(0.0)
        heel_roll_remap.plugs['value'].element(1).child(0).set_value(-100.0)
        heel_roll_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        heel_roll_remap.plugs['outValue'].connect_to(roll_back.plugs['rotateX'])

        # rock in
        rock_in_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_rock_in' % root_name
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
            root_name='%s_rock_out' % root_name
        )
        rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
        rock_out_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_out_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_out_remap.plugs['value'].element(1).child(0).set_value(100.0)
        rock_out_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateZ'])

        # pivots

        pivot_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_pivots' % root_name
        )
        if side == 'right':
            pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        else:
            pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
        ball_pivot_plug.connect_to(pivot_multiply.plugs['input1X'])
        toe_pivot_plug.connect_to(pivot_multiply.plugs['input1Y'])
        heel_pivot_plug.connect_to(pivot_multiply.plugs['input1Z'])
        pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateY'])
        pivot_multiply.plugs['outputY'].connect_to(toe_povot.plugs['rotateY'])
        pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateY'])

        # Stretchable

        limb_utils.convert_ik_to_stretchable(
            hip_transform,
            ankle_position_transform,
            (ik_joints[1], ik_joints[2], ik_joints[3]),
            ankle_handle
        )

        ankle_ik_solver = controller.create_ik_handle(
            ik_joints[0],
            ik_joints[3],
            parent=ankle_position_transform,
            solver='ikRPSolver'
        )
        foot_ball_ik_solver = controller.create_ik_handle(
            ik_joints[3],
            ik_joints[4],
            parent=ball_roll,
            solver='ikRPSolver'
        )
        toe_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='{0}_toe'.format(root_name),
            size=size,
            side=side,
            matrix=foot_matrix,
            shape='frame_z',
            parent=bend_top
        )

        toe_handle.stretch_shape(toe_matrix.get_translation())
        if side == 'left':
            toe_handle.multiply_shape_matrix(Matrix(scale=[1.0, 1.0, -1.0]))
        toe_bend = toe_handle.gimbal_handle.create_child(
            Transform,
            root_name='{0}_toe_bend'.format(root_name),
            side=side,
            matrix=foot_matrix
        )

        toe_tip_ik_solver = controller.create_ik_handle(
            ik_joints[4],
            ik_joints[5],
            parent=toe_bend,
            solver='ikRPSolver'
        )
        toe_tip_ik_solver.plugs['visibility'].set_value(False)
        ankle_ik_solver.plugs['visibility'].set_value(False)
        foot_ball_ik_solver.plugs['visibility'].set_value(False)

        controller.create_pole_vector_constraint(
            knee_handle,
            ankle_ik_solver
        )

        # isolate knee
        isolate_hip_joint = this.create_child(
            Joint,
            root_name='{}_isolate_hip'.format(root_name),
            parent=this.joint_group,
            matrix=matrices[0],
        )
        isolate_hip_joint.zero_rotation()
        isolate_knee_joint = this.create_child(
            Joint,
            root_name='{}_isolate_knee'.format(root_name),
            parent=isolate_hip_joint,
            matrix=matrices[1],
        )
        isolate_knee_joint.zero_rotation()
        isolate_hip_joint.plugs['v'].set_value(False)
        isolate_knee_joint.plugs['v'].set_value(False)
        controller.create_point_constraint(
            ik_joints[0],
            isolate_hip_joint
        )
        controller.create_point_constraint(
            knee_handle,
            isolate_knee_joint
        )
        isolate_up_transform = this.create_child(
            Transform,
            root_name='{}_isolate_up'.format(root_name),
            parent=this.joint_group
        )
        this.create_child(
            ReversePoleVector,
            hip_transform, knee_handle, ankle_handle.gimbal_handle,
            isolate_up_transform,
            root_name='%s_reverse_pole' % root_name
        )
        controller.create_aim_constraint(
            knee_handle,
            isolate_hip_joint,
            worldUpObject=isolate_up_transform,
            worldUpType='object',
            aimVector=env.side_aim_vectors[side],
            upVector=env.side_up_vectors[side]
        )
        controller.create_aim_constraint(
            ankle_handle.gimbal_handle,
            isolate_knee_joint,
            worldUpObject=isolate_up_transform,
            worldUpType='object',
            aimVector=env.side_aim_vectors[side],
            upVector=env.side_up_vectors[side]
        )
        lock_knee_plug = ankle_handle.create_plug(
            'lock_knee',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        isolate_hip_pair_blend = isolate_hip_joint.create_child(
            DependNode,
            node_type='pairBlend',
        )
        isolate_hip_joint.plugs['translate'].connect_to(isolate_hip_pair_blend.plugs['inTranslate2'])
        ik_joints[0].plugs['translate'].connect_to(isolate_hip_pair_blend.plugs['inTranslate1'])
        isolate_hip_joint.plugs['rotate'].connect_to(isolate_hip_pair_blend.plugs['inRotate2'])
        ik_joints[0].plugs['rotate'].connect_to(isolate_hip_pair_blend.plugs['inRotate1'])
        isolate_hip_pair_blend.plugs['outTranslate'].connect_to(joints[0].plugs['translate'])
        isolate_hip_pair_blend.plugs['outRotate'].connect_to(joints[0].plugs['rotate'])
        isolate_hip_pair_blend.plugs['rotInterpolation'].set_value(1)
        lock_knee_plug.connect_to(isolate_hip_pair_blend.plugs['weight'])
        isolate_knee_pair_blend = isolate_knee_joint.create_child(
            DependNode,
            node_type='pairBlend',
        )
        isolate_knee_joint.plugs['translate'].connect_to(isolate_knee_pair_blend.plugs['inTranslate2'])
        ik_joints[1].plugs['translate'].connect_to(isolate_knee_pair_blend.plugs['inTranslate1'])
        isolate_knee_joint.plugs['rotate'].connect_to(isolate_knee_pair_blend.plugs['inRotate2'])
        ik_joints[1].plugs['rotate'].connect_to(isolate_knee_pair_blend.plugs['inRotate1'])
        isolate_knee_pair_blend.plugs['outTranslate'].connect_to(joints[1].plugs['translate'])
        isolate_knee_pair_blend.plugs['outRotate'].connect_to(joints[1].plugs['rotate'])
        isolate_knee_pair_blend.plugs['rotInterpolation'].set_value(1)
        lock_knee_plug.connect_to(isolate_knee_pair_blend.plugs['weight'])

        utility_group.plugs['visibility'].set_value(True)
        controller.create_parent_constraint(
            ik_joints[3],
            joints[3],
            mo=False
        )
        controller.create_scale_constraint(
            ankle_handle,
            ik_joints[3],
            mo=False
        )

        controller.create_parent_constraint(
            toe_handle.gimbal_handle,
            joints[4],
            mo=False
        )
        controller.create_scale_constraint(
            toe_handle.gimbal_handle,
            ik_joints[5],
            mo=False
        )

        controller.create_parent_constraint(
            ik_joints[2],
            joints[2],
            mo=False
        )

        ik_joints[3].plugs['scale'].connect_to(joints[3].plugs['scale'])
        ik_joints[3].plugs['scale'].connect_to(joints[3].plugs['scale'])

        root.add_plugs([
            knee_handle.plugs['tx'],
            knee_handle.plugs['ty'],
            knee_handle.plugs['tz'],
            toe_handle.plugs['tx'],
            toe_handle.plugs['ty'],
            toe_handle.plugs['tz'],
            toe_handle.plugs['rx'],
            toe_handle.plugs['ry'],
            toe_handle.plugs['rz'],
            toe_handle.plugs['sx'],
            toe_handle.plugs['sy'],
            toe_handle.plugs['sz'],
            ankle_handle.plugs['tx'],
            ankle_handle.plugs['ty'],
            ankle_handle.plugs['tz'],
            ankle_handle.plugs['rx'],
            ankle_handle.plugs['ry'],
            ankle_handle.plugs['rz'],
            ankle_handle.plugs['sx'],
            ankle_handle.plugs['sy'],
            ankle_handle.plugs['sz'],
            foot_roll_plug,
            rock_plug,
            toe_pivot_plug,
            ball_pivot_plug,
            heel_pivot_plug,
            lock_knee_plug
        ])

        root.add_plugs(
            break_plug,
            keyable=False
        )

        this.ankle_handle = ankle_handle
        this.knee_handle = knee_handle
        this.toe_handle = toe_handle
        this.joints = joints
        return this
