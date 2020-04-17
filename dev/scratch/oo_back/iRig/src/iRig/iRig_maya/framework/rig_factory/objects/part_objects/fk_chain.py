from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import Matrix


class FkChainGuide(ChainGuide):

    default_settings = dict(
        root_name='fkchain',
        count=5,
        size=1.0,
        side='center',
        up_vector_indices=[0]
    )

    def __init__(self, **kwargs):
        super(FkChainGuide, self).__init__(**kwargs)
        self.toggle_class = FkChain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FkChainGuide, cls).create(controller, **kwargs)
        return this


class FkChain(Part):

    def __init__(self, **kwargs):
        super(FkChain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FkChain, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name
        size = this.size
        side = this.side
        handles = []
        joints = this.joints

        # Fk Handle
        fk_joint_parent = this.joint_group
        fk_handle_parent = this
        for x, matrix in enumerate(matrices):
            joint = this.create_child(
                Joint,
                root_name='fk_%s' % root_name,
                index=x,
                matrix=matrix,
                parent=fk_joint_parent
            )
            fk_joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            if x != len(matrices)-1:
                handle = this.create_handle(
                    root_name='fk_%s' % root_name,
                    index=x,
                    size=size*2.5,
                    matrix=matrix,
                    side=side,
                    shape='frame_z',
                    parent=fk_handle_parent
                )

                handle.stretch_shape(matrices[x + 1].get_translation())
                shape_scale = [
                    0.8,
                    0.8,
                    -1.0 if side == 'right' else 1.0,
                ]
                handle.multiply_shape_matrix(Matrix(scale=shape_scale))
                controller.create_parent_constraint(
                    handle,
                    joint
                )
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                handle.plugs['rotateOrder'].connect_to(joint.plugs['rotateOrder'])
                fk_handle_parent = handle
                handles.append(handle)
        root = this.get_root()
        if root:
            for handle in handles:
                root.add_plugs(
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz']
                )

        joints[0].plugs['type'].set_value(1)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)

        return this
