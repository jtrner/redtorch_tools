from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.part_objects.handle import HandleGuide
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle

from rig_math.matrix import Matrix, Vector


class JawGuide(HandleGuide):

    default_settings = dict(
        root_name='jaw',
        size=0.25,
        side='center'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(JawGuide, cls).create(controller, **kwargs)
        size = this.size
        joint_2 = this.create_child(
            Joint,
            index=1,
            parent=this.joints[0]
        )
        joint_2.zero_rotation()
        joint_2.plugs['ty'].set_value(size)
        joint_2.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        this.joints.append(joint_2)
        return this

    def __init__(self, **kwargs):
        super(JawGuide, self).__init__(**kwargs)
        self.toggle_class = Jaw.__name__

    def get_toggle_blueprint(self):
        """
        Passing guide vertices to rig so I can figure out where the jaw should be relative to blendshape/sculpts etc
        """
        blueprint = super(JawGuide, self).get_toggle_blueprint()
        guide_vertices = []
        for handle in self.handles:
            guide_vertices.append([(x.mesh.name, x.index) for x in handle.vertices])
        blueprint['guide_vertices'] = guide_vertices
        return blueprint


class Jaw(Part):
    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    guide_vertices = DataProperty(
        name='guide_vertices'
    )


    driver_transform = ObjectProperty(
        name='driver_transform'
    )


    def __init__(self, **kwargs):
        super(Jaw, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Jaw, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name
        matrices = this.matrices
        if not matrices:
            matrices = [Matrix(), Matrix()
                        ]
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
        joint_1.zero_rotation()
        joint_2.zero_rotation()
        joint_2.plugs['ty'].set_value(1.0)

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

        jaw_control = this.create_handle(
            handle_type=GroupedHandle,
            group_count=5,
            shape='cube',
            size=size,
            matrix=matrices[0],
            root_name='%s_rotate' % this.root_name
        )
        vector_1 = Vector(joint_1.get_matrix().get_translation())
        vector_2 = Vector(joint_2.get_matrix().get_translation())
        vector_3 = (vector_2 - vector_1).normalize()
        result = vector_2 + (vector_3 * size)
        arrow_matrix = Matrix(*result)
        jaw_aim_handle = this.create_handle(
            shape='arrow',
            size=size,
            matrix=arrow_matrix,
            root_name='%s_aim_handle' % this.root_name
        )
        jaw_control.multiply_shape_matrix(Matrix(scale=[3.0, 1.2, 1.0]))
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
        jaw_multiply_node.plugs['input2X'].set_value(-15)
        jaw_multiply_node.plugs['input2Z'].set_value(-15)
        jaw_multiply_node.plugs['outputX'].connect_to(jaw_control.groups[1].plugs['rx'])
        jaw_multiply_node.plugs['outputZ'].connect_to(jaw_control.groups[1].plugs['rz'])
        controller.create_parent_constraint(
            jaw_control,
            joint_1
        )


        controller.create_parent_constraint(
            jaw_control,
            driver_transform,
            mo=False
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
            jaw_aim_handle.plugs['tx'],
            jaw_aim_handle.plugs['ty'],
            -1.0, 1.0,
            -1.0, 1.0,
            '%s_up_right' % root_name
        )

        this.joints = [joint_1, joint_2]
        this.driver_transform = driver_transform

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
