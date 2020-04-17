from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_math.matrix import Matrix, Vector


class NewJawGuide(ChainGuide):

    default_settings = dict(
        root_name='jaw',
        size=0.25,
        side='center'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs['count'] = 2
        kwargs.setdefault('root_name', 'jaw')
        return super(NewJawGuide, cls).create(controller, **kwargs)

    def __init__(self, **kwargs):
        super(NewJawGuide, self).__init__(**kwargs)
        self.toggle_class = NewJaw.__name__

    def get_toggle_blueprint(self):
        """
        Passing guide vertices to rig so I can figure out where the jaw should be relative to blendshape/sculpts etc
        """
        blueprint = super(NewJawGuide, self).get_toggle_blueprint()
        guide_vertices = []
        for handle in self.handles:
            guide_vertices.append([(x.mesh.name, x.index) for x in handle.vertices])
        blueprint['guide_vertices'] = guide_vertices
        return blueprint


class NewJaw(Part):
    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    driver_transform = ObjectProperty(
        name='driver_transform'
    )

    guide_vertices = DataProperty(
        name='guide_vertices'
    )

    def __init__(self, **kwargs):
        super(NewJaw, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(NewJaw, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name
        matrices = this.matrices
        position_1 = matrices[0].get_translation()
        position_2 = matrices[1].get_translation()
        jaw_vector = position_2 - position_1

        joint_parent = this.joint_group.create_child(
            Transform,
            root_name='%s_jaw' % this.root_name
        )
        joint_1 = joint_parent.create_child(
            Joint,
            index=0,
            matrix=matrices[0]
        )
        joint_2 = this.create_child(
            Joint,
            index=0,
            parent=joint_1
        )

        driver_pos = this.create_child(
            Transform,
            root_name='%s_driver_pos' % root_name,
            matrix=matrices[0]
        )
        driver_transform = driver_pos.create_child(
            Transform,
            root_name='%s_driver' % root_name,
            matrix=matrices[0]
        )

        joint_1.zero_rotation()
        joint_2.zero_rotation()
        joint_2.plugs['ty'].set_value(1.0)
        jaw_control = this.create_handle(
            handle_type=GimbalHandle,
            group_count=5,
            shape='cube',
            size=size,
            matrix=matrices[0],
            root_name='%s_rotate' % this.root_name
        )

        controller.create_parent_constraint(
            jaw_control,
            driver_transform,
            mo=False
        )

        jaw_control.stretch_shape(
            matrices[1].get_translation()
        )
        jaw_control.multiply_shape_matrix(Matrix(scale=[3.0, 1.2, 1.0]))
        jaw_aim_handle = this.create_handle(
            shape='arrow',
            size=size,
            matrix=Matrix(position_1 + (jaw_vector * 1.5)),
            root_name='%s_aim_handle' % this.root_name
        )
        jaw_aim_handle.multiply_shape_matrix(Matrix(scale=[1.0, -1.0, 1.0]))

        up_transform = jaw_control.groups[0].create_child(
            Transform,
            root_name='%s_up_transform' % root_name
        )
        up_transform.plugs['tz'].set_value(size * -15)
        joint_1.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=size
        )
        joint_2.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=size
        )

        jaw_multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide',
        )
        jaw_aim_handle.plugs['ty'].connect_to(jaw_multiply_node.plugs['input1X'])
        jaw_aim_handle.plugs['tx'].connect_to(jaw_multiply_node.plugs['input1Z'])
        jaw_multiply_node.plugs['input2X'].set_value(-5)
        jaw_multiply_node.plugs['input2Z'].set_value(-5)
        jaw_multiply_node.plugs['outputX'].connect_to(jaw_control.groups[1].plugs['rx'])
        jaw_multiply_node.plugs['outputZ'].connect_to(jaw_control.groups[1].plugs['rz'])
        controller.create_parent_constraint(
            jaw_control.gimbal_handle,
            joint_1
        )
        create_corrective_driver(
            jaw_aim_handle.plugs['tx'],
            jaw_aim_handle.plugs['ty'],
            1.0, 1.0,
            1.0, 1.0,
            '%s_down_left' % root_name
        )
        create_corrective_driver(
            jaw_aim_handle.plugs['tx'],
            jaw_aim_handle.plugs['ty'],
            -1.0, 1.0,
            1.0, 1.0,
            '%s_down_right' % root_name
        )
        create_corrective_driver(
            jaw_aim_handle.plugs['tx'],
            jaw_aim_handle.plugs['ty'],
            1.0, 1.0,
            -1.0, 1.0,
            '%s_up_left' % root_name
        )

        create_corrective_driver(
            driver_transform.plugs['rx'],
            driver_transform.plugs['rz'],
            45.0, 1.0,
            -45.0, 1.0,
            '%s_driver_down_left' % root_name
        )

        create_corrective_driver(
            driver_transform.plugs['rx'],
            driver_transform.plugs['rz'],
            45.0, 1.0,
            45.0, 1.0,
            '%s_driver_down_right' % root_name
        )

        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    jaw_control.plugs['tx'],
                    jaw_control.plugs['ty'],
                    jaw_control.plugs['tz'],
                    jaw_control.plugs['rx'],
                    jaw_control.plugs['ry'],
                    jaw_control.plugs['rz'],
                    jaw_aim_handle.plugs['tx'],
                    jaw_aim_handle.plugs['ty'],
                    jaw_aim_handle.plugs['tz'],
                    jaw_control.plugs['rotation_order']
                ]
            )
        this.driver_transform = driver_transform
        this.joints = [joint_1, joint_2]
        return this


def create_corrective_driver(plug_1, plug_2, in_value_1, out_value_1, in_value_2, out_value_2, name):
    node = plug_1.get_node()
    multiply_node = node.create_child(
        DependNode,
        node_type='multiplyDivide',
        name='%s_mlt' % name
    )
    remap_node_1 = node.create_child(
        DependNode,
        node_type='remapValue',
        name='%s_1_rmp' % name
    )
    remap_node_2 = node.create_child(
        DependNode,
        node_type='remapValue',
        name='%s_2_rmp' % name
    )
    remap_node_1.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_1.plugs['value'].element(0).child(1).set_value(0.0)
    remap_node_1.plugs['value'].element(1).child(0).set_value(in_value_1)
    remap_node_1.plugs['value'].element(1).child(1).set_value(out_value_1)

    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(1).child(0).set_value(in_value_2)
    remap_node_2.plugs['value'].element(1).child(1).set_value(out_value_2)
    plug_1.connect_to(remap_node_1.plugs['inputValue'])
    plug_2.connect_to(remap_node_2.plugs['inputValue'])
    remap_node_1.plugs['outValue'].connect_to(multiply_node.plugs['input1X'])
    remap_node_2.plugs['outValue'].connect_to(multiply_node.plugs['input2X'])
    combo_plug = node.create_plug(
        name,
        k=True,
        at='double'
    )
    multiply_node.plugs['outputX'].connect_to(combo_plug)
