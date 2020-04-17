import copy
from rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.rig_objects.rig_handles import LocalHandle, WorldHandle
from rig_factory.objects.part_objects.part import Part
import rig_factory.positions as pos


class QuadrupedBackLegFkGuide(ChainGuide):

    hip_name = DataProperty(
        name='hip_name',
        default_value='hip'
    )

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

    default_settings = dict(
        root_name='back_leg',
        size=1.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLegFk.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('root_name', 'back_leg')
        #kwargs.setdefault('handle_positions', copy.copy(pos.QUADRUPED_POSITIONS))
        this = super(QuadrupedBackLegFkGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBackLegFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedBackLegFk(Part):

    hip_name = DataProperty(
        name='hip_name',
        default_value='hip'
    )

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

    fk_handles = ObjectListProperty(
        name='fk_handles'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )
    fk_handle_gimbals = ObjectListProperty(
        name='fk_handle_gimbals'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        if len(kwargs.get('matrices', [])) != 5:
            raise Exception('you must provide exactly 6 matrices to create a %s' % cls.__name__)
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedBackLegFk, cls).create(controller, **kwargs)
        parent = kwargs.pop('parent', this)
        size = this.size
        side = this.side
        root_name = this.root_name
        matrices = this.matrices
        joints = []
        joint_parent = this.joint_group
        handle_parent = this
        root = this.get_root()
        for i, joint_str in enumerate([
            this.thigh_name,
            this.calf_name,
            this.ankle_name,
            this.toe_name,
            '%s_tip' % this.toe_name
        ]):
            is_last = i == 4
            joint = joint_parent.create_child(
                'Joint',
                root_name='{0}_{1}'.format(root_name, joint_str),
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            joint_parent = joint
            if not is_last:  # No need to create a handle for tip of limb
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    root_name=root_name,
                    index=i,
                    size=size,
                    matrix=matrices[i],
                    side=side,
                    shape='cube',
                    parent=handle_parent
                )
                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint
                )
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
                handle.stretch_shape(matrices[i+1])
                handle_parent = handle.gimbal_handle
        this.joints = joints
        return this
