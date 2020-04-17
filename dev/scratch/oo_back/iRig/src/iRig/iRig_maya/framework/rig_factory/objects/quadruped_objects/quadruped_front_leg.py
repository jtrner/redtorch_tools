from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.quadruped_objects.quadruped_front_leg_fk import QuadrupedFrontLegFk
from rig_factory.objects.quadruped_objects.quadruped_front_leg_ik import QuadrupedFrontLegIk
from rig_math.vector import Vector
from rig_factory.objects.node_objects.depend_node import DependNode


# TODO: add ik/fk blend code that works in rig state
class QuadrupedFrontLegGuide(ChainGuide):
    default_settings = dict(
        root_name='front_leg',
        size=1.0,
        side='left'
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLegGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedFrontLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('root_name', 'front_leg')
        this = super(QuadrupedFrontLegGuide, cls).create(controller, **kwargs)

        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedFrontLegGuide, self).get_toggle_blueprint()
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


class QuadrupedFrontLeg(Part):

    ik_leg = ObjectProperty(
        name='ik_leg'
    )

    fk_leg = ObjectProperty(
        name='fk_leg'
    )

    def __init__(self, **kwargs):
        super(QuadrupedFrontLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(QuadrupedFrontLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        matrices = this.matrices

        fk_leg = this.create_child(
            QuadrupedFrontLegFk,
            matrices=matrices,
            root_name='{0}_fk'.format(root_name),
            owner=None,
            joint_group=this.joint_group
        )
        ik_leg = this.create_child(
            QuadrupedFrontLegIk,
            matrices=matrices,
            root_name='{0}_ik'.format(root_name),
            joint_group=this.joint_group
        )
        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        ik_joints = ik_leg.joints
        fk_joints = fk_leg.joints
        joint_parent = this.joint_group

        joints = []
        for i in range(len(matrices)):
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
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name='%s_blend' % root_name,
                index=i
            )
            joint.plugs.set_values(
                drawStyle=2
            )
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            part_ik_plug.connect_to(pair_blend.plugs['weight'])
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joint.plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])
            joints.append(joint)
            joint_parent = joint

        fk_joints = fk_leg.joints
        ik_joints = ik_leg.joints
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)

        this.joints = joints
        this.ik_leg = ik_leg
        this.fk_leg = fk_leg
        return this
