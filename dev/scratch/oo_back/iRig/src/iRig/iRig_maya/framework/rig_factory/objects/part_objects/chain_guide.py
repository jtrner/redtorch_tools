import rig_factory.environment as env
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.rig_objects.capsule import Capsule
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.line import Line
from part import Part, PartGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class ChainGuide(PartGuide):

    capsules = ObjectListProperty(
        name='capsules'
    )
    locators = ObjectListProperty(
        name='locators'
    )
    up_handles = ObjectListProperty(
        name='up_handles'
    )

    count = DataProperty(
        name='count'
    )

    default_settings = dict(
        count=4
    )

    def __init__(self, **kwargs):
        super(ChainGuide, self).__init__(**kwargs)
        self.toggle_class = Chain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        up_vector_indices = kwargs.pop('up_vector_indices', [0])
        side = kwargs.setdefault('side', 'center')
        side_vectors = env.side_world_vectors[side]
        this = super(ChainGuide, cls).create(controller, **kwargs)
        root = this.get_root()
        size = this.size
        spacing = size * 5.0
        size_plug = this.plugs['size']
        root_name = this.root_name
        joint_parent = this
        aim_vector = env.aim_vector
        up_vector = env.up_vector
        handle_positions = kwargs.get('handle_positions', dict())
        if side == 'right':
            aim_vector = [x*-1.0 for x in env.aim_vector]
            up_vector = [x*-1.0 for x in env.up_vector]
        size_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_size' % root_name
        )
        size_plug.connect_to(size_multiply.plugs['input1X'])
        size_plug.connect_to(size_multiply.plugs['input1Y'])
        size_multiply.plugs['input2X'].set_value(0.5)
        size_multiply.plugs['input2Y'].set_value(0.25)

        joints = []
        handles = []
        locators = []
        up_handles = []
        base_handles = []
        aim_up_handles = []
        capsules = []
        up_handle_lines = dict()
        for i in range(this.count):
            if i in up_vector_indices:
                up_handle = this.create_handle(
                    index=len(up_handles),
                    root_name='%s_up' % root_name
                )
                position = handle_positions.get(up_handle.name, [
                    side_vectors[0]*(spacing*i),
                    side_vectors[1]*(spacing*i),
                    spacing*-5
                ])
                up_handle.plugs['translate'].set_value(position)
                up_handle.mesh.assign_shading_group(this.get_root().shaders[side].shading_group)
                size_multiply.plugs['outputY'].connect_to(up_handle.plugs['size'])
                up_handles.append(up_handle)
                root.add_plugs(
                    [
                        up_handle.plugs['tx'],
                        up_handle.plugs['ty'],
                        up_handle.plugs['tz']
                    ]
                )
            aim_up_handles.append(up_handle)
            if i > 0:
                joint_parent = joints[i - 1]
            joint = joint_parent.create_child(
                Joint,
                index=i,
            )
            handle = this.create_handle(
                index=i,
            )
            position = handle_positions.get(handle.name, [x * (spacing*i) for x in side_vectors])
            handle.plugs['translate'].set_value(position)
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz']
                ]
            )
            cone_x = joint.create_child(
                Cone,
                root_name='%s_cone_x' % root_name,
                index=i,
                size=size,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                root_name='%s_cone_y' % root_name,
                index=i,
                size=size,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                root_name='%s_cone_z' % root_name,
                index=i,
                size=size,
                axis=[0.0, 0.0, 1.0]
            )
            locator = joint.create_child(
                Locator
            )
            controller.create_point_constraint(
                handle,
                joint,
                mo=False
            )
            size_multiply.plugs['outputY'].connect_to(handle.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_x.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_y.plugs['size'])
            size_multiply.plugs['outputX'].connect_to(cone_z.plugs['size'])
            joint.plugs.set_values(
                radius=0.0,
                overrideEnabled=True,
                overrideDisplayType=2,
                overrideRGBColors=True,
                overrideColorR=0.0,
                overrideColorG=0.0,
                overrideColorB=0.0
            )

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
            locator.plugs.set_values(
                visibility=False
            )
            locator.plugs['visibility'].set_value(False)
            root = this.get_root()
            handle.mesh.assign_shading_group(root.shaders[side].shading_group)
            cone_x.mesh.assign_shading_group(root.shaders['x'].shading_group)
            cone_y.mesh.assign_shading_group(root.shaders['y'].shading_group)
            cone_z.mesh.assign_shading_group(root.shaders['z'].shading_group)
            joints.append(joint)
            locators.append(locator)
            handles.append(handle)
            base_handles.append(handle)
        for i in range(this.count):
            up_handle = aim_up_handles[i]
            if i < this.count - 1:
                capsule = this.create_child(
                    Capsule,
                    index=i,
                    root_name='%s_segment' % root_name,
                    parent=this
                )
                capsule.mesh.assign_shading_group(this.get_root().shaders[side].shading_group)
                size_plug.connect_to(capsule.plugs['size'])
                locator_1 = locators[i]
                locator_2 = locators[i + 1]
                joint_1 = joints[i]
                joint_2 = joints[i + 1]
                locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
                locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
                controller.create_point_constraint(joint_1, joint_2, capsule)
                controller.create_aim_constraint(
                    joint_2,
                    capsule,
                    aimVector=env.aim_vector
                )
                controller.create_aim_constraint(
                    handles[i + 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle.get_selection_string(),
                    aimVector=aim_vector,
                    upVector=up_vector
                )
                capsules.append(capsule)
            else:
                controller.create_aim_constraint(
                    handles[i - 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle,
                    aimVector=[x * -1 for x in aim_vector],
                    upVector=up_vector
                )
            if up_handle not in up_handle_lines:
                line = this.create_child(
                    Line,
                    index=i
                )
                locator_1 = locators[i]
                locator_2 = up_handle.create_child(Locator)
                locator_2.plugs.set_values(
                    visibility=False
                )
                locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
                locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
                up_handle_lines[up_handle] = line

        this.locators = locators
        this.capsules = capsules
        handles.extend(up_handles)
        this.up_handles = up_handles
        this.joints = joints
        this.base_handles = base_handles
        return this


class Chain(Part):
    """
    Added Part for consistency with other rig_factory objects
    Not intended for actual use
    """
    
    capsules = ObjectListProperty(
        name='capsules'
    )
    locators = ObjectListProperty(
        name='locators'
    )
    up_handles = ObjectListProperty(
        name='up_handles'
    )
    count = DataProperty(
        name='count'
    )

    default_settings = dict(
        count=4
    )
    
    def __init__(self, **kwargs):
        super(Chain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Chain, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name
        size = this.size
        side = this.side
        handles = []
        joints = this.joints

        # Chain Handle
        joint_parent = this.joint_group
        handle_parent = this
        for x, matrix in enumerate(matrices):
            joint = this.create_child(
                Joint,
                root_name='fk_%s' % root_name,
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
            if x != len(matrices)-1:
                fk_handle = this.create_handle(
                    root_name='fk_%s' % root_name,
                    index=x,
                    size=size*2.5,
                    matrix=matrix,
                    side=side,
                    shape='cube',
                    parent=handle_parent
                )
                controller.create_parent_constraint(
                    fk_handle,
                    joint
                )
                fk_handle.plugs['scale'].connect_to(joint.plugs['scale'])
                fk_handle.plugs['rotateOrder'].connect_to(joint.plugs['rotateOrder'])
                fk_handle.stretch_shape(matrices[x + 1].get_translation())
                handle_parent = fk_handle
                handles.append(fk_handle)
        for fk_handle in handles:
            this.get_root().add_plugs([
                    fk_handle.plugs['rx'], fk_handle.plugs['ry'], fk_handle.plugs['rz']
                    ]
            )
        joints[0].plugs['type'].set_value(1)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)

        return this
