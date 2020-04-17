import copy
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.mesh import Mesh, MeshVertex
from line import Line
from cone import Cone
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
import rig_factory.environment as env


class GuideHandle(Joint):

    owner = ObjectProperty(
        name='owner'
    )

    mesh = ObjectProperty(
        name='mesh'
    )

    vertices = ObjectListProperty(
        name='vertices'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        vertices = kwargs.get('vertices', None)
        if isinstance(vertices, MeshVertex):
            kwargs['vertices'] = [vertices]
        this = super(GuideHandle, cls).create(controller, **kwargs)

        size = this.size
        size_plug = this.create_plug(
            'size',
            at='double',
            k=True,
            dv=size
        )
        #radius_plug = this.plugs['radius']
        #radius_plug.set_value(size)
        #size_plug.connect_to(radius_plug)
        #size_plug.set_value(size)
        #radius_plug.set_value(size)

        sphere_node = this.create_child(
            DependNode,
            node_type='polyPrimitiveMisc',
        )
        multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        mesh = this.create_child(Mesh)


        sphere_node.plugs['output'].connect_to(mesh.plugs['inMesh'])
        size_plug.connect_to(multiply_node.plugs['input1X'])
        multiply_node.plugs['input2X'].set_value(0.5)
        multiply_node.plugs['outputX'].connect_to(sphere_node.plugs['radius'])
        size_plug.set_value(size)
        this.mesh = mesh
        return this

    def assign_selected_vertices(self):
        self.controller.assign_selected_vertices_to_handle(self)

    def snap_to_vertices(self, vertices):
        self.controller.snap_handle_to_vertices(self, vertices)

    def get_root(self):
        if self.owner:
            return self.owner.get_root()


class BoxHandleGuide(Transform):

    default_settings = dict(
        root_name='handle',
        size=1.0,
        side='center',
    )
    cones = ObjectListProperty(
        name='cones'
    )
    cube_mesh = ObjectProperty(
        name='cube_mesh'
    )
    aim_constraint = ObjectProperty(
        name='aim_constraint'
    )
    handles = ObjectListProperty(
        name='handles'
    )
    joints = ObjectListProperty(
        name='joints'
    )

    def __init__(self, **kwargs):
        super(BoxHandleGuide, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        handle_positions = kwargs.pop('handle_positions', dict())
        owner = kwargs.pop('owner', None)
        if not owner:
            raise Exception('Must provide owner')

        matrix = kwargs.pop('matrix', Matrix())
        this = super(BoxHandleGuide, cls).create(controller, **kwargs)

        size = this.size
        size_plug = this.create_plug(
            'size',
            at='double',
            k=True,
            dv=size
        )

        side = this.side
        size = this.size

        root_name = this.root_name

        # Create nodes

        joint = this.create_child(
            Joint,
            index=0
        )
        up_translation = list(matrix.get_translation())
        aim_translation = copy.copy(up_translation)
        up_translation[2] += (size * 2)
        aim_translation[1] += (size * 2)

        up_matrix = Matrix(*up_translation)
        aim_matrix = Matrix(*aim_translation)

        handle_1 = owner.create_handle(
            index=0,
            matrix=matrix,
            parent=this,
            root_name=root_name,
            side=side
        )
        handle_2 = owner.create_handle(
            index=1,
            matrix=aim_matrix,
            parent=this,
            root_name=root_name,
            side=side

        )
        up_handle = owner.create_handle(
            index=0,
            root_name='%s_up' % root_name,
            matrix=up_matrix,
            parent=this,
            side=side
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


        #Objects
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

        joint.zero_rotation()
        this.aim_constraint = controller.create_aim_constraint(
            handle_2,
            joint,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
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
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )

        # Attributes

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

        this.handles = [handle_1, handle_2, up_handle]
        this.cones = [cone_x, cone_y, cone_z]
        this.cube_mesh = cube_mesh
        this.joints = [joint]
        return this

