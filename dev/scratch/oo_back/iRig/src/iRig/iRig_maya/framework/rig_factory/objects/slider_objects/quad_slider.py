from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part, PartGuide
import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class QuadSliderGuide(PartGuide):

    default_settings = dict(
        root_name='handle',
        size=1.0,
        side='center',
        shape='arrow_quad'
    )

    shape = DataProperty(
        name='shape'
    )
    def __init__(self, **kwargs):
        super(QuadSliderGuide, self).__init__(**kwargs)
        self.toggle_class = QuadSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        handle_positions = kwargs.pop('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        this = super(QuadSliderGuide, cls).create(controller, **kwargs)
        side = this.side
        size = this.size

        root_name = this.root_name

        # Create nodes

        joint = this.create_child(
            Joint,
            index=0
        )

        handle_1 = this.create_handle(
            handle_type=GuideHandle,
            index=0
        )
        handle_2 = this.create_handle(
            handle_type=GuideHandle,
            index=1,
        )
        up_handle = this.create_handle(
            handle_type=GuideHandle,
            index=0,
            root_name='%s_up' % root_name
        )
        locator_1 = handle_1.create_child(
            Locator
        )
        locator_2 = handle_2.create_child(
            Locator
        )
        up_locator = up_handle.create_child(
            Locator
        )
        up_line = this.create_child(
            Line,
            index=0
        )
        aim_line = this.create_child(
            Line,
            index=1
        )
        position_1 = handle_positions.get(handle_1.name, [0.0, 0.0, 0.0])
        position_2 = handle_positions.get(handle_2.name, [x * (size*3) for x in env.side_world_vectors[side]])
        up_position = handle_positions.get(up_handle.name, [0.0, 0.0, size*-3])
        handle_1.plugs['translate'].set_value(position_1)
        handle_2.plugs['translate'].set_value(position_2)
        up_handle.plugs['translate'].set_value(up_position)
        cube_transform = this.create_child(
            Transform,
            root_name='%s_cube' % root_name
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type='polyCube',
        )
        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
        )
        cube_mesh = cube_transform.create_child(
            Mesh
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
        )

        cone_x = joint.create_child(
            Cone,
            root_name='%s_cone_x' % root_name,
            size=size,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = joint.create_child(
            Cone,
            root_name='%s_cone_y' % root_name,
            size=size,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = joint.create_child(
            Cone,
            root_name='%s_cone_z' % root_name,
            size=size,
            axis=[0.0, 0.0, 1.0]
        )

        # Constraints

        aim_vector = env.aim_vector
        up_vector = env.up_vector
        if side == 'right':
            aim_vector = [x *-1.0 for x in aim_vector]

        joint.zero_rotation()
        controller.create_aim_constraint(
            handle_2,
            joint,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=aim_vector,
            upVector=up_vector
        )
        controller.create_point_constraint(
            handle_1,
            joint
        )
        controller.create_point_constraint(
            handle_1,
            cube_transform
        )
        controller.create_aim_constraint(
            handle_2,
            cube_transform,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=aim_vector,
            upVector=up_vector
        )
        # Attributes

        size_plug = this.plugs['size']
        size_plug.connect_to(multiply.plugs['input1X'])
        multiply.plugs['input2X'].set_value(0.25)
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        locator_1.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point2'])
        locator_1.plugs['worldPosition'].element(0).connect_to(up_line.curve.plugs['controlPoints'].element(0))
        up_locator.plugs['worldPosition'].element(0).connect_to(up_line.curve.plugs['controlPoints'].element(1))
        locator_1.plugs['worldPosition'].element(0).connect_to(aim_line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(aim_line.curve.plugs['controlPoints'].element(1))

        size_plug.connect_to(cube_node.plugs['height'])
        size_plug.connect_to(cube_node.plugs['depth'])
        size_plug.connect_to(cube_node.plugs['width'])

        multiply.plugs['outputX'].connect_to(handle_1.plugs['size'])
        multiply.plugs['outputX'].connect_to(handle_2.plugs['size'])
        multiply.plugs['outputX'].connect_to(up_handle.plugs['size'])

        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        up_locator.plugs['visibility'].set_value(False)
        cube_mesh.plugs['overrideEnabled'].set_value(True)
        cube_mesh.plugs['overrideDisplayType'].set_value(2)
        cube_transform.plugs['overrideEnabled'].set_value(True)
        cube_transform.plugs['overrideDisplayType'].set_value(2)
        joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=size*0.25
        )
        up_handle.plugs['radius'].set_value(size*0.25)
        handle_1.plugs['radius'].set_value(size*0.25)
        handle_2.plugs['radius'].set_value(size*0.25)

        size_plug.connect_to(cone_x.plugs['size'])
        size_plug.connect_to(cone_y.plugs['size'])
        size_plug.connect_to(cone_z.plugs['size'])
        cone_x.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
        )
        cone_y.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
        )
        cone_z.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
        )
        # Shaders
        root = this.get_root()
        handle_1.mesh.assign_shading_group(root.shaders[side].shading_group)
        handle_2.mesh.assign_shading_group(root.shaders[side].shading_group)
        up_handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        cone_x.mesh.assign_shading_group(root.shaders['x'].shading_group)
        cone_y.mesh.assign_shading_group(root.shaders['y'].shading_group)
        cone_z.mesh.assign_shading_group(root.shaders['z'].shading_group)

        this.joints = [joint]
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadSliderGuide, self).get_toggle_blueprint()
        blueprint['shape'] = self.shape
        return blueprint


class QuadSlider(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    shape = DataProperty(
        name='shape'
    )

    def __init__(self, **kwargs):
        super(QuadSlider, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(QuadSlider, cls).create(controller, **kwargs)
        size = this.size
        matrices = this.matrices
        joint = this.create_child(
            Joint,
            index=0,
            matrix=matrices[0],
            parent=this.joint_group
        )
        handle = this.create_handle(
            shape=this.shape,
            size=size,
            matrix=matrices[0]
        )
        joint.zero_rotation()
        joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )
        controller.create_parent_constraint(
            handle,
            joint
        )

        create_corrective_driver(
            handle.plugs['tx'],
            handle.plugs['tz'],
            0.4, 1.0,
            0.4, 1.0,
            root_name='tx_tz_pos_pos',
            side=this.side
        )

        create_corrective_driver(
            handle.plugs['tx'],
            handle.plugs['tz'],
            -0.4, 1.0,
            -0.4, 1.0,
            root_name='tx_tz_neg_neg',
            side=this.side
        )

        create_corrective_driver(
            handle.plugs['tx'],
            handle.plugs['tz'],
            0.4, 1.0,
            -0.4, 1.0,
            root_name='tx_tz_pos_neg',
            side=this.side
        )

        create_corrective_driver(
            handle.plugs['tx'],
            handle.plugs['tz'],
            -0.4, 1.0,
            0.4, 1.0,
            root_name='tx_tz_neg_pos',
            side=this.side
        )

        this.joints = [joint]
        return this


def create_corrective_driver(plug_1, plug_2, in_value_1, out_value_1, in_value_2, out_value_2, **kwargs):
    node = plug_1.get_node()
    multiply_node = node.create_child(
        DependNode,
        node_type='multiplyDivide',
        **kwargs
    )
    root_name = kwargs.pop('root_name')
    kwargs['root_name'] = '%s_first' % root_name
    remap_node_1 = node.create_child(
        DependNode,
        node_type='remapValue',
        **kwargs
    )
    kwargs['root_name'] = '%s_second' % root_name
    remap_node_2 = node.create_child(
        DependNode,
        node_type='remapValue',
        **kwargs
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
        root_name,
        k=True,
        at='double'
    )

    blend_node = node.create_child(
        DependNode,
        node_type='blendWeighted',
        **kwargs
    )
    multiply_node.plugs['outputX'].connect_to(blend_node.plugs['input'].element(0))
    blend_node.plugs['output'].connect_to(combo_plug)
