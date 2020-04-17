from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.quadruped_objects.quadruped_neck_fk import QuadrupedNeckFk
from rig_factory.objects.quadruped_objects.quadruped_neck_ik import QuadrupedNeckIk
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.depend_node import DependNode


# TODO: add ik/fk blend code that works in rig state
class QuadrupedNeckGuide(SplineChainGuide):

    default_head_scale = 4

    head_cube = ObjectProperty(
        name='ik_neck'
    )

    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        joint_count=9,
        count=5
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeck.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(QuadrupedNeckGuide, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name
        head_matrix = kwargs.get('head_matrix', None)
        if head_matrix is None:
            head_scale = size*cls.default_head_scale
            head_matrix = Matrix([0.0, head_scale*.5, 0.0])
            head_matrix.set_scale([head_scale] * 3)

        cube_transform = this.create_child(
            Transform,
            root_name='%s_head' % root_name
        )
        this.head_cube = cube_transform
        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedNeckGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint


class QuadrupedNeck(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    ik_neck = ObjectProperty(
        name='ik_neck'
    )

    fk_neck = ObjectProperty(
        name='fk_neck'
    )
    joint_matrices = []

    def __init__(self, **kwargs):
        super(QuadrupedNeck, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        head_matrix = kwargs.pop('head_matrix', list(Matrix()))
        this = super(QuadrupedNeck, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name

        fk_neck = this.create_child(
            QuadrupedNeckFk,
            matrices=matrices,
            root_name='{0}_fk'.format(root_name),
            head_matrix=head_matrix,
            owner=this
        )
        ik_neck = this.create_child(
            QuadrupedNeckIk,
            matrices=matrices,
            root_name='{0}_ik'.format(root_name),
            head_matrix=head_matrix,
            owner=this
        )

        ik_joints = ik_neck.joints
        fk_joints = fk_neck.joints

        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        joints = []
        joint_parent = this.joint_group

        for i in range(len(matrices)):
            joint = this.create_child(
                Joint,
                root_name='%s_blend' % root_name,
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

        this.fk_neck = fk_neck
        this.ik_neck = ik_neck
        this.joints = joints
        return this
