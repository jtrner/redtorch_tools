from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
import rig_math.utilities as rmu
from rig_math.vector import Vector
from rig_math.matrix import Matrix
import rig_factory.environment as env
import rig_factory.utilities.limb_utilities as ltl


class BipedArmIkGuide(ChainGuide):
    default_settings = dict(
        root_name='arm',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedArmIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArmIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 4
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'arm')
        this = super(BipedArmIkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedArmIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def align_elbow(self):
        raise self.controller.raise_exception(StandardError('Not Implemented'))
        """
        root_position = Vector(self.handles[3].get_translation())
        elbow_position = Vector(self.handles[4].get_translation())
        up_vector_position = Vector(self.handles[2].get_translation())
        wrist_position = Vector(self.handles[6].get_translation())
        mag_1 = (elbow_position - root_position).mag()
        mag_2 = (wrist_position - elbow_position).mag()
        total_mag = mag_1 + mag_2
        if total_mag == 0.0:
            print 'Warning: the second joint had no angle. unable to calculate pole position'
            return up_vector_position
        fraction_1 = mag_1 / total_mag
        center_position = root_position + (wrist_position - root_position) * fraction_1
        angle_vector = (up_vector_position - center_position)
        angle_mag = angle_vector.mag()
        if angle_mag == 0.0:
            print 'Warning: the second joint had no angle. unable to calculate pole position'
            return up_vector_position
        distance = (elbow_position - center_position).mag()
        elbow_offset = angle_vector.normalize() * distance
        elbow_position = center_position + elbow_offset
        return self.handles[4].plugs['translate'].set_value(elbow_position.data)
        """


class BipedArmIk(Part):
    wrist_handle = ObjectProperty(
        name='wrist_handle'
    )
    wrist_handle_gimbal = ObjectProperty(
        name='wrist_handle_gimbal'
    )
    elbow_handle = ObjectProperty(
        name='elbow_handle'
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


    def __init__(self, **kwargs):
        super(BipedArmIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedArmIk, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        shoulder_matrix = matrices[0]
        elbow_matrix = matrices[1]
        wrist_matrix = matrices[2]
        root = this.get_root()
        ik_joints = []
        joints = []
        joint_parent = this.joint_group
        ik_joint_parent = this.joint_group
        for i, joint_str in enumerate(['upper', 'lower', 'hand', 'hand_tip']):
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
            ik_joint.plugs['scale'].connect_to(joint.plugs['scale'])
            root.add_plugs(
                ik_joint.plugs['rx'],
                ik_joint.plugs['ry'],
                ik_joint.plugs['rz'],
                keyable=False
            )
        wrist_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='{0}_wrist'.format(root_name),
            size=size * 0.9,
            side=side,
            matrix=wrist_matrix,
            shape='cube',
            rotation_order='xyz'
        )

        controller.create_scale_constraint(
            wrist_handle,
            ik_joints[2],
            mo=False
        )

        pole_position = rmu.calculate_pole_vector_position(
            shoulder_matrix.get_translation(),
            elbow_matrix.get_translation(),
            wrist_matrix.get_translation(),
            distance=((size/10) + 1) * 50
        )
        elbow_handle = this.create_handle(
            handle_type=WorldHandle,
            parent=this,
            root_name='{0}_elbow'.format(root_name),
            size=size*0.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='ball',
            rotation_order='xyz'
        )
        ik_handle = controller.create_ik_handle(
            ik_joints[0],
            ik_joints[2],
            parent=this,
            solver='ikRPSolver'
        )

        shape_scale = [
            1.3 if side == 'right' else 1.3 * -1.0,
            0.8,
            0.8
        ]

        clavicle_root = this.create_child(
            Transform,
            root_name='{0}_clavicle_root'.format(root_name),
            matrix=ik_joints[0].get_matrix(),
        )

        controller.create_orient_constraint(
            wrist_handle.gimbal_handle,
            ik_joints[2],
            mo=True,
        )
        controller.create_point_constraint(
            wrist_handle.gimbal_handle,
            ik_handle,
            mo=True,
        )
        twist_plug = wrist_handle.create_plug(
            'twist',
            at='double',
            k=True,
            dv=0.0
        )

        twist_plug.connect_to(ik_handle.plugs['twist'])
        locator_1 = joints[1].create_child(Locator, root_name='{0}_root_line'.format(root_name))
        locator_2 = elbow_handle.create_child(Locator, root_name='{0}_tip_line'.format(root_name))
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        line = this.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        controller.create_pole_vector_constraint(
            elbow_handle,
            ik_handle
        )
        ltl.convert_ik_to_stretchable(
            clavicle_root,
            wrist_handle.gimbal_handle,
            [ik_joints[1], ik_joints[2]],
            wrist_handle
        )


        # isolate elbow
        isolate_shoulder_joint = this.create_child(
            Joint,
            root_name='{}_isolate_shoulder'.format(root_name),
            matrix=matrices[0],
        )
        isolate_shoulder_joint.zero_rotation()
        isolate_elbow_joint = this.create_child(
            Joint,
            root_name='{}_isolate_elbow'.format(root_name),
            parent=isolate_shoulder_joint,
            matrix=matrices[1],
        )
        isolate_elbow_joint.zero_rotation()
        isolate_shoulder_joint.plugs['v'].set_value(False)
        isolate_elbow_joint.plugs['v'].set_value(False)

        controller.create_point_constraint(
            ik_joints[0],
            isolate_shoulder_joint
        )
        controller.create_point_constraint(
            elbow_handle,
            isolate_elbow_joint
        )

        wrist_pole_transform = this.create_child(
            Transform,
            root_name='{0}_wrist_pole'.format(root_name),
        )

        controller.create_point_constraint(
            clavicle_root,
            wrist_handle.gimbal_handle,
            wrist_pole_transform
        )

        isolate_up_transform = this.create_child(
            Transform,
            root_name='{}_isolate_up'.format(root_name),
            parent=this.joint_group
        )
        this.create_child(
            ReversePoleVector,
            clavicle_root, elbow_handle, wrist_handle.gimbal_handle,
            isolate_up_transform,
            root_name='%s_reverse_pole' % root_name
        )
        controller.create_aim_constraint(
            elbow_handle,
            isolate_shoulder_joint,
            worldUpObject=isolate_up_transform,
            worldUpType='object',
            aimVector=env.side_aim_vectors[side],
            upVector=env.side_up_vectors[side]
        )
        controller.create_aim_constraint(
            wrist_handle.gimbal_handle,
            isolate_elbow_joint,
            worldUpObject=isolate_up_transform,
            worldUpType='object',
            aimVector=env.side_aim_vectors[side],
            upVector=env.side_up_vectors[side]
        )
        lock_elbow_plug = wrist_handle.create_plug(
            'lock_elbow',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        isolate_shoulder_pair_blend = isolate_shoulder_joint.create_child(
            DependNode,
            node_type='pairBlend',
        )
        isolate_shoulder_joint.plugs['translate'].connect_to(isolate_shoulder_pair_blend.plugs['inTranslate2'])
        ik_joints[0].plugs['translate'].connect_to(isolate_shoulder_pair_blend.plugs['inTranslate1'])
        isolate_shoulder_joint.plugs['rotate'].connect_to(isolate_shoulder_pair_blend.plugs['inRotate2'])
        ik_joints[0].plugs['rotate'].connect_to(isolate_shoulder_pair_blend.plugs['inRotate1'])
        isolate_shoulder_pair_blend.plugs['outTranslate'].connect_to(joints[0].plugs['translate'])
        isolate_shoulder_pair_blend.plugs['outRotate'].connect_to(joints[0].plugs['rotate'])
        isolate_shoulder_pair_blend.plugs['rotInterpolation'].set_value(1)
        lock_elbow_plug.connect_to(isolate_shoulder_pair_blend.plugs['weight'])
        isolate_elbow_pair_blend = isolate_elbow_joint.create_child(
            DependNode,
            node_type='pairBlend',
        )
        isolate_elbow_joint.plugs['translate'].connect_to(isolate_elbow_pair_blend.plugs['inTranslate2'])
        ik_joints[1].plugs['translate'].connect_to(isolate_elbow_pair_blend.plugs['inTranslate1'])
        isolate_elbow_joint.plugs['rotate'].connect_to(isolate_elbow_pair_blend.plugs['inRotate2'])
        ik_joints[1].plugs['rotate'].connect_to(isolate_elbow_pair_blend.plugs['inRotate1'])
        isolate_elbow_pair_blend.plugs['outTranslate'].connect_to(joints[1].plugs['translate'])
        isolate_elbow_pair_blend.plugs['outRotate'].connect_to(joints[1].plugs['rotate'])
        isolate_elbow_pair_blend.plugs['rotInterpolation'].set_value(1)
        lock_elbow_plug.connect_to(isolate_elbow_pair_blend.plugs['weight'])

        utility_group.plugs['visibility'].set_value(True)
        controller.create_parent_constraint(
            ik_joints[2],
            joints[2],
            mo=False
        )

        #controller.create_parent_constraint(
        #    this,
        #    joints[0]
        #)
        #ik_joints[4].plugs['translate'].connect_to(joints[4].plugs['translate'])
        #ik_joints[4].plugs['rotate'].connect_to(joints[4].plugs['rotate'])

        ik_handle.plugs['visibility'].set_value(False)
        utility_group.plugs['visibility'].set_value(True)
        for handle in (wrist_handle, ):
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
        root.add_plugs(
            [
                elbow_handle.plugs['tx'],
                elbow_handle.plugs['ty'],
                elbow_handle.plugs['tz'],
                twist_plug,
                lock_elbow_plug
            ]
        )

        this.wrist_handle = wrist_handle
        this.elbow_handle = elbow_handle
        this.joints = joints
        this.ik_joints = ik_joints
        return this
