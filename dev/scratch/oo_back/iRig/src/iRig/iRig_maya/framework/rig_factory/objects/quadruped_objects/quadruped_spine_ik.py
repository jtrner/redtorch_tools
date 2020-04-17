from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
import rig_factory.environment as env
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty


class QuadrupedSpineIkGuide(ChainGuide):
    default_settings = dict(
        root_name='spine',
        size=1.0,
        side='center',
        joint_count=9,
        count=5
    )

    def __init__(self, **kwargs):
        super(QuadrupedSpineIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedSpineIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'spine')
        this = super(QuadrupedSpineIkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedSpineIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedSpineIk(Part):

    lower_torso_handle = ObjectProperty(
        name='lower_torso_handle'
    )
    upper_torso_handle = ObjectProperty(
        name='upper_torso_handle'
    )
    center_handles = ObjectListProperty(
        name='center_handles'
    )

    def __init__(self, **kwargs):
        super(QuadrupedSpineIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedSpineIk, cls).create(controller, **kwargs)
        matrices = this.matrices
        if len(matrices) < 5:
            raise Exception('you must provide at least 5 matrices to create a %s' % cls.__name__)

        root_name = this.root_name
        size = this.size
        side = this.side
        root = this.get_root()
        joints = []
        center_handles = []
        lower_torso_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name='{0}_lower_torso'.format(root_name),
            shape='cube',
            matrix=Matrix(matrices[1].get_translation()),
            parent=this,
            size=size,
            rotation_order='xzy'
        )
        upper_torso_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name='{0}_upper_torso'.format(root_name),
            shape='cube',
            matrix=Matrix(matrices[-2].get_translation()),
            parent=this,
            size=size,
            rotation_order='xzy'

        )
        joint_parent = this.joint_group
        for x, matrix in enumerate(matrices):
            joint = this.create_child(
                Joint,
                index=x,
                matrix=matrix,
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2,
                visibility=False
            )
            joints.append(joint)
            joint_parent = joint
            if x not in [0, 1, len(matrices)-1, len(matrices)-2]:

                center_handle = this.create_handle(
                    handle_type=LocalHandle,
                    index=x,
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                controller.create_parent_constraint(
                    center_handle,
                    joint,
                    mo=True
                )
                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                if root:
                    root.add_plugs(
                        [
                            center_handle.plugs['tx'],
                            center_handle.plugs['ty'],
                            center_handle.plugs['tz'],
                            center_handle.plugs['rx'],
                            center_handle.plugs['ry'],
                            center_handle.plugs['rz'],
                        ]
                    )

                center_handles.append(center_handle)
        controller.create_parent_constraint(
            lower_torso_handle,
            joints[0],
            mo=True
        )
        controller.create_parent_constraint(
            upper_torso_handle,
            joints[-2],
            mo=True
        )
        lower_aim_transform = this.create_child(
            Transform,
            root_name='{0}_lower_aim'.format(root_name)
        )
        controller.create_point_constraint(
            lower_torso_handle.gimbal_handle,
            lower_aim_transform,
            mo=True
        )
        controller.create_aim_constraint(
            upper_torso_handle.gimbal_handle,
            lower_aim_transform,
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpObject=lower_torso_handle,
            worldUpType='objectrotation',
            worldUpVector=[0.0, 0.0, -1.0]
        )

        sub_handle_count = len(center_handles)
        for i, center_handle in enumerate(center_handles):
            matrix = center_handle.get_matrix()
            lower_aim_transform.plugs['rotate'].connect_to(center_handle.groups[0].plugs['rotate'])
            constraint = controller.create_point_constraint(
                lower_torso_handle.gimbal_handle,
                upper_torso_handle.gimbal_handle,
                center_handle.groups[0],
                mo=True
            )
            value = 1.0/(sub_handle_count+1)*(i+1)
            constraint.plugs['%sW0' % lower_torso_handle.gimbal_handle.name].set_value(1.0-value)
            constraint.plugs['%sW1' % upper_torso_handle.gimbal_handle.name].set_value(value)
            center_handle.groups[1].set_matrix(matrix)
            controller.create_aim_constraint(
                center_handle,
                joints[i+1],
                mo=True,
                aimVector=env.aim_vector,
                upVector=env.up_vector,
                worldUpObject=lower_torso_handle,
                worldUpType='objectrotation',
                worldUpVector=[0.0, 0.0, -1.0]
            )
        if root:
            for handle in [lower_torso_handle, upper_torso_handle]:
                root.add_plugs(
                    [
                        handle.plugs['tx'],
                        handle.plugs['ty'],
                        handle.plugs['tz'],
                        handle.plugs['rx'],
                        handle.plugs['ry'],
                        handle.plugs['rz']
                    ]
                )
        this.lower_torso_handle = lower_torso_handle
        this.upper_torso_handle = upper_torso_handle
        this.center_handles = center_handles

        this.joints = joints
        return this
