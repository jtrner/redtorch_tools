import copy
from rig_factory.objects.base_objects.properties import (
    ObjectProperty, ObjectListProperty, DataProperty
)
from rig_factory.objects.biped_objects.biped_leg_fk import BipedLegFk
from rig_factory.objects.biped_objects.biped_leg_ik import BipedLegIk
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_math.matrix import Matrix, compose_matrix
from rig_math.vector import Vector
import rig_factory.environment as env
import rig_math.utilities as rmu
import rig_factory.positions as pos


class BipedLegGuide(ChainGuide):
    default_settings = dict(
        root_name='leg',
        size=4.0,
        side='left',
        foot_placement_depth=1.0,
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )
    foot_placement_depth = DataProperty(
        name='foot_placement_depth',
    )

    def __init__(self, **kwargs):
        super(BipedLegGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 6
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'leg')
        kwargs.setdefault('handle_positions', copy.copy(pos.BIPED_POSITIONS))
        this = super(BipedLegGuide, cls).create(controller, **kwargs)
        body = this.get_root()
        root_name = this.root_name
        size = this.size
        side = this.side
        pivot_handles = []
        pivot_joints = []
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']
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

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def align_knee(self):
        root_position = Vector(self.handles[3].get_translation())
        knee_position = Vector(self.handles[4].get_translation())
        up_vector_position = Vector(self.handles[2].get_translation())
        ankle_position = Vector(self.handles[6].get_translation())
        mag_1 = (knee_position - root_position).mag()
        mag_2 = (ankle_position - knee_position).mag()
        total_mag = mag_1 + mag_2
        if total_mag == 0.0:
            self.controller.raise_warning('Warning: the second joint had no angle. unable to calculate pole position')
            return up_vector_position
        fraction_1 = mag_1 / total_mag
        center_position = root_position + (ankle_position - root_position) * fraction_1
        angle_vector = (up_vector_position - center_position)
        angle_mag = angle_vector.mag()
        if angle_mag == 0.0:
            self.controller.raise_warning('Warning: the second joint had no angle. unable to calculate pole position')
            return up_vector_position

        distance = (knee_position - center_position).mag()
        knee_offset = angle_vector.normalize() * distance
        knee_position = center_position + knee_offset
        return self.handles[4].plugs['translate'].set_value(knee_position.data)


class BipedLeg(Part):

    ik_leg = ObjectProperty(
        name='ik_leg'
    )

    foot_placement_depth = DataProperty(
        name='foot_placement_depth',
        default_value=1.0
    )
    fk_leg = ObjectProperty(
        name='fk_leg'
    )
    ik_match_joint = ObjectProperty(
        name='ik_match_joint'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    heel_placement_node = ObjectProperty(
        name='heel_placement_node'
    )
    ball_placement_node = ObjectProperty(
        name='ball_placement_node'
    )

    def __init__(self, **kwargs):
        super(BipedLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        foot_placement_depth = this.foot_placement_depth
        aim_vector = env.side_aim_vectors[side]
        joint_parent = this.joint_group
        joints = []
        for i in range(6):
            if i != 0:
                joint_parent = joints[-1]
            joint = this.create_child(
                Joint,
                root_name=root_name,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            joints.append(joint)
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
        hip_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='%s_hip_base' % root_name,
            matrix=matrices[0],
            shape='frame_y',
            rotation_order='xzy'
        )
        hip_handle.stretch_shape(matrices[1])
        hip_vector = matrices[1].get_translation() - matrices[0].get_translation()
        hip_length = hip_vector.mag()
        if side == 'right':
            hip_length = hip_length * -1.0
        hip_shape_matrix = Matrix(
            0.0,
            hip_length*2,
            0.0,
            scale=[size*0.5, hip_length, size*0.5]
        )
        hip_handle.set_shape_matrix(hip_shape_matrix)
        controller.create_parent_constraint(
            hip_handle,
            joints[0]
        )
        fk_leg = this.create_child(
            BipedLegFk,
            matrices=matrices[1:],
            root_name='{0}_fk'.format(root_name),
            owner=this,
            parent=hip_handle.gimbal_handle
        )
        ik_leg = this.create_child(
            BipedLegIk,
            matrices=matrices[1:],
            root_name='{0}_ik'.format(root_name),
            owner=this,
            parent=hip_handle.gimbal_handle
        )
        fk_joints = fk_leg.joints
        ik_joints = ik_leg.joints
        fk_leg.joints[0].set_parent(joints[0])
        ik_leg.joints[0].set_parent(joints[0])
        ik_leg.ik_joints[0].set_parent(joints[0])
        ik_leg.isolated_joints[0].set_parent(joints[0])

        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        for i in range(5):
            pair_blend = joints[i+1].create_child(
                DependNode,
                node_type='pairBlend',
                parent=this
            )
            blend_colors = joints[i+1].create_child(
                DependNode,
                node_type='blendColors',
                parent=this
            )
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            ik_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color1'])
            fk_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color2'])
            pair_blend.plugs['outTranslate'].connect_to(joints[i+1].plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joints[i+1].plugs['rotate'])
            blend_colors.plugs['output'].connect_to(joints[i+1].plugs['scale'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            part_ik_plug.connect_to(pair_blend.plugs['weight'])
            part_ik_plug.connect_to(blend_colors.plugs['blender'])

        settings_handle = this.create_handle(
            handle_type=CurveHandle,
            parent=joints[3],
            root_name='{0}_settings'.format(root_name),
            shape='gear_simple',
            axis='x',
            matrix=matrices[3],
            size=size*0.5
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
            translate=[x*(size*-2.0) for x in aim_vector]
        )
        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )
        ik_plug.connect_to(part_ik_plug)
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
        )
        part_ik_plug.connect_to(ik_leg.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        reverse_node.plugs['outputX'].connect_to(fk_leg.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        this.ik_match_joint = fk_leg.joints[2].create_child(
            Joint,
            root_name='%s_ik_match' % root_name,
            matrix=ik_leg.ankle_handle.get_matrix()
        )
        joints[1].plugs['type'].set_value(2)
        joints[2].plugs['type'].set_value(3)
        joints[3].plugs['type'].set_value(4)
        joints[4].plugs['type'].set_value(5)
        for joint in joints:
            joint.plugs['side'].set_value({'center': 0, 'left': 1, 'right': 2, None: 3}[side])
        this.joints = joints
        root = this.get_root()
        root.add_plugs(
            ik_plug,
            hip_handle.plugs['tx'],
            hip_handle.plugs['ty'],
            hip_handle.plugs['tz'],
            hip_handle.plugs['rx'],
            hip_handle.plugs['ry'],
            hip_handle.plugs['rz']
        )
        this.ik_leg = ik_leg
        this.fk_leg = fk_leg
        this.settings_handle = settings_handle

        (
            front_pivot_matrix,
            back_pivot_matrix,
            in_pivot_matrix,
            out_pivot_matrix,
        ) = ik_leg.matrices[5:9]

        front_pivot_position = front_pivot_matrix.get_translation()
        back_pivot_position = back_pivot_matrix.get_translation()
        out_pivot_position = out_pivot_matrix.get_translation()
        in_pivot_position = in_pivot_matrix.get_translation()

        center_pivot_position = (
            front_pivot_position
            + back_pivot_position
        ) / 2

        ball_pivot_matrix = compose_matrix(
            (center_pivot_position + front_pivot_position) / 2,
            front_pivot_position,
            out_pivot_position
        )
        heel_pivot_matrix = compose_matrix(
            (center_pivot_position + back_pivot_position) / 2,
            front_pivot_position,
            out_pivot_position
        )

        heel_placement = this.joints[3].create_child(
            Transform,
            root_name='%s_foot_placement' % root_name,
            index=0,
            matrix=heel_pivot_matrix,
        )
        translate_z = heel_placement.plugs['translateZ'].get_value()
        placement_offset = foot_placement_depth * 0.5 if side == 'left' else foot_placement_depth * -0.5
        heel_placement.plugs.set_values(
            translateZ=translate_z + placement_offset
        )
        heel_placement_mesh = heel_placement.create_child(
            DagNode,
            node_type='mesh',
            index=0
        )
        heel_placement_mesh.plugs['hideOnPlayback'].set_value(True)
        heel_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            index=0
        )
        heel_placement_poly_cube.plugs['output'].connect_to(
            heel_placement_mesh.plugs['inMesh'],
        )
        heel_placement_poly_cube.plugs.set_values(
            width=foot_placement_depth,
            height=(center_pivot_position - back_pivot_position).magnitude(),
            depth=(in_pivot_position - out_pivot_position).magnitude(),
        )
        this.heel_placement_node = heel_placement

        ball_placement = this.joints[4].create_child(
            Transform,
            root_name='%s_foot_placement' % root_name,
            index=1,
            matrix=ball_pivot_matrix,
        )
        translate_z = ball_placement.plugs['translateZ'].get_value()
        placement_offset = foot_placement_depth * 0.5 if side == 'left' else foot_placement_depth * -0.5
        ball_placement.plugs.set_values(
            translateZ=translate_z + placement_offset
        )
        ball_placement_mesh = ball_placement.create_child(
            DagNode,
            node_type='mesh',
            index=1
        )
        ball_placement_mesh.plugs['hideOnPlayback'].set_value(True)
        ball_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            index=1
        )
        ball_placement_poly_cube.plugs['output'].connect_to(
            ball_placement_mesh.plugs['inMesh'],
        )
        ball_placement_poly_cube.plugs.set_values(
            width=foot_placement_depth,
            height=(front_pivot_position - center_pivot_position).magnitude(),
            depth=(in_pivot_position - out_pivot_position).magnitude(),
        )
        this.ball_placement_node = ball_placement

        return this

    def toggle_ik(self):
        value = self.settings_handle.plugs['ik_switch'].get_value()
        if value > 0.5:
            self.match_to_fk()
        else:
            self.match_to_ik()

    def match_to_fk(self):
        self.settings_handle.plugs['ik_switch'].set_value(0.0)
        positions = [x.get_matrix() for x in self.ik_leg.joints]
        for i in range(len(positions[0:4])):
            self.fk_leg.handles[i].set_matrix(Matrix(positions[i]))

    def match_to_ik(self):
        self.settings_handle.plugs['ik_switch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_leg.joints]
        pole_position = rmu.calculate_pole_vector_position(
                positions[0].get_translation(),
                positions[1].get_translation(),
                positions[2].get_translation(),
                distance=self.size*10
            )
        self.ik_leg.knee_handle.set_matrix(Matrix(pole_position))
        self.ik_leg.ankle_handle.set_matrix(self.ik_match_joint.get_matrix())
        self.ik_leg.toe_handle.set_matrix(positions[3])
