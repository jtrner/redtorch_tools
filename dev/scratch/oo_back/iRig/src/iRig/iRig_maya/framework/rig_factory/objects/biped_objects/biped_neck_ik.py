"""
TODO:
    Fix ik not matching fx when the guide is built with an arc to it's
    Handles.
    Fix `tangent_plug` range to something like: -1 > 0 > 1 where 0
    is the normal joint location and -1 and 1 are the min and max joint
    position as they are currently.
"""

from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_math.matrix import Matrix
import rig_factory.environment as env


class BipedNeckIkGuide(ChainGuide):
    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        joint_count=5,
        count=5
    )

    def __init__(self, **kwargs):
        super(BipedNeckIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeckIk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'spine')
        this = super(BipedNeckIkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedNeckIk(Part):

    head_handle = ObjectProperty(
        name='head_handle'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a ' + cls.__name__)
        this = super(BipedNeckIk, cls).create(controller, **kwargs)
        head_matrix = kwargs.pop('head_matrix', list(Matrix()))
        matrices = this.matrices
        matrices_len = len(matrices)
        if matrices_len < 4:
            raise Exception('you must provide at least 4 matrices to create a ' + cls.__name__)
        root_name = this.root_name
        size = this.size
        side = this.side
        root = this.get_root()

        lower_neck_transform = this.create_child(
            Transform,
            root_name=root_name + '_lower_neck',
            matrix=Matrix(matrices[1].get_translation())
        )

        center_handles = []
        joint_parent = this.joint_group
        joints = []
        for i, matrix in enumerate(matrices):
            
            joint = this.create_child(
                Joint,
                index=i,
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
            
            if 1 < i < matrices_len - 2:

                center_handle = this.create_handle(
                    handle_type=LocalHandle,
                    index=i,
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                controller.create_parent_constraint(
                    center_handle,
                    joint
                )
                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                center_handles.append(center_handle)

                root.add_plugs([
                    center_handle.plugs['tx'],
                    center_handle.plugs['ty'],
                    center_handle.plugs['tz'],
                    center_handle.plugs['rx'],
                    center_handle.plugs['ry'],
                    center_handle.plugs['rz']
                ])

        head_handle = this.create_handle(
            handle_type=WorldHandle,
            root_name=root_name + '_head',
            shape='partial_cube_x',
            matrix=Matrix(matrices[-1].get_translation()),
            parent=this,
            size=size,
            rotation_order='zxy'
        )
        head_handle.plugs['shape_matrix'].set_value(list(head_matrix))

        tangent_plug = head_handle.create_plug(
            'break_tangent',
            at='double',
            k=True,
            dv=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            max=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            min=(matrices[-2].get_translation() - matrices[-3].get_translation()).mag() * -0.9
        )
        tangent_base = head_handle.create_child(
            Transform,
            root_name='%s_head_tangent_base' % root_name,
            matrix=matrices[-2]
        )
        tangent_gp = tangent_base.create_child(
            Transform,
            root_name='%s_head_tangent' % root_name,
            matrix=matrices[-2]
        )
        joint_base_group = this.create_child(
            Transform,
            root_name='%s_joint_base' % root_name,
            matrix=matrices[0]
        )
        tangent_plug.connect_to(tangent_gp.plugs['ty'])

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            joints[-1],
            mo=True
        )
        controller.create_parent_constraint(
            tangent_gp,
            joints[-2],
        )

        controller.create_parent_constraint(
            joint_base_group,
            joints[0],
        )
        lower_aim_transform = this.create_child(
            Transform,
            root_name='{0}_lower_aim'.format(root_name)
        )

        controller.create_point_constraint(
            lower_neck_transform,
            lower_aim_transform,
            mo=False
        )

        controller.create_aim_constraint(
            head_handle.gimbal_handle,
            lower_aim_transform,
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpObject=lower_neck_transform,
            worldUpType='objectrotation',
            worldUpVector=[0.0, 0.0, -1.0]
        )

        center_handles_len = len(center_handles)
        for i, center_handle in enumerate(center_handles):
            lower_aim_transform.plugs['rotate'].connect_to(center_handle.groups[0].plugs['rotate'])
            constraint = controller.create_point_constraint(
                lower_neck_transform,
                tangent_gp,
                center_handle.groups[0],
                mo=False
            )
            value = 1.0 / (center_handles_len + 1) * (i + 1)
            constraint.plugs[tangent_gp.name + 'W1'].set_value(value)
            constraint.plugs[lower_neck_transform.name + 'W0'].set_value(1.0 - value)

            matrix = center_handle.get_matrix()
            center_handle.groups[1].set_matrix(matrix)
            controller.create_aim_constraint(
                center_handle,
                joints[i + 1],
                mo=True,
                aimVector=env.aim_vector,
                upVector=env.up_vector,
                worldUpObject=lower_neck_transform,
                worldUpType='objectrotation',
                worldUpVector=[0.0, 0.0, -1.0]
            )

        root.add_plugs([
            head_handle.plugs['tx'],
            head_handle.plugs['ty'],
            head_handle.plugs['tz'],
            head_handle.plugs['rx'],
            head_handle.plugs['ry'],
            head_handle.plugs['rz']
        ])

        this.head_handle = head_handle
        this.joints = joints
        return this
