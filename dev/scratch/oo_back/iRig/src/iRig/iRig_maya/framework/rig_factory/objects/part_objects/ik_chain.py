from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import Matrix
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle


class IkChainGuide(ChainGuide):

    default_settings = dict(
        root_name='chain',
        count=4,
        size=1.0,
        side='center',
        up_vector_indices=[0]
    )

    def __init__(self, **kwargs):
        super(IkChainGuide, self).__init__(**kwargs)
        self.toggle_class = IkChain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(IkChainGuide, cls).create(controller, **kwargs)
        return this


class IkChain(Part):

    def __init__(self, **kwargs):
        super(IkChain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(IkChain, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name
        size = this.size
        side = this.side
        joints = this.joints
        root = this.get_root()

        joint_parent = this.joint_group

        tip_handle = this.create_handle(
            handle_type=GimbalHandle,
            root_name=root_name,
            size=size * 2.5,
            matrix=matrices[-1],
            side=side,
            shape='cube',
        )
        base_handle = this.create_handle(
            handle_type=GimbalHandle,
            root_name='%s_base' % root_name,
            size=size * 2.5,
            matrix=matrices[0],
            side=side,
            shape='square',
        )
        for x, matrix in enumerate(matrices):
            joint = this.create_child(
                Joint,
                index=x,
                matrix=matrix,
                parent=joint_parent
            )
            joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
        ik_handle = controller.create_ik_handle(
            joints[0],
            joints[-1],
            parent=tip_handle,
            solver='ikRPSolver'
        )

        controller.create_orient_constraint(
            tip_handle.gimbal_handle,
            joints[-1],
            mo=False,
        )

        controller.create_point_constraint(
            base_handle.gimbal_handle,
            joints[0],
            mo=False,
        )

        ik_handle.plugs['v'].set_value(False)


        root.add_plugs(
            tip_handle.plugs['rx'],
            tip_handle.plugs['ry'],
            tip_handle.plugs['rz'],
            tip_handle.plugs['tx'],
            tip_handle.plugs['ty'],
            tip_handle.plugs['tz'],
            base_handle.plugs['rx'],
            base_handle.plugs['ry'],
            base_handle.plugs['rz'],
            base_handle.plugs['tx'],
            base_handle.plugs['ty'],
            base_handle.plugs['tz'],
        )

        return this
