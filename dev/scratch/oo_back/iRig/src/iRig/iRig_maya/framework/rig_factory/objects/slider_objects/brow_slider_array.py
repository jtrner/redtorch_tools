from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.guide_handle import BoxHandleGuide
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class BrowSliderArrayGuide(PartGuide):

    default_settings = dict(
        size=1.0,
        side='left',
        shape='arrow_vertical',
        count=3,
        lid_root_name='up_lid',
        root_name='brow'

    )

    shape = DataProperty(
        name='shape'
    )

    lid_root_name = DataProperty(
        name='lid_root_name'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        count = kwargs.setdefault('count', 3)
        this = super(BrowSliderArrayGuide, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name

        joints = []
        handles = []
        locators = []

        lid_handle = this.create_child(
            BoxHandleGuide,
            root_name=this.lid_root_name,
            size=float(size)*0.5,
            owner=this
        )
        this.plugs['size'].connect_to(lid_handle.plugs['size'])

        joint = lid_handle.joints[0]
        root = this.get_root()
        lid_handle.cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        lid_handle.handles[0].mesh.assign_shading_group(root.shaders[side].shading_group)
        lid_handle.handles[1].mesh.assign_shading_group(root.shaders['y'].shading_group)
        lid_handle.handles[2].mesh.assign_shading_group(root.shaders['z'].shading_group)

        lid_handle.cones[0].mesh.assign_shading_group(root.shaders['x'].shading_group)
        lid_handle.cones[1].mesh.assign_shading_group(root.shaders['y'].shading_group)
        lid_handle.cones[2].mesh.assign_shading_group(root.shaders['z'].shading_group)
        joints.append(joint)
        handles.extend(lid_handle.handles)

        lid_locator = joint.create_child(
            Locator,
            root_name='line_%s' % this.lid_root_name
        )
        lid_locator.plugs.set_values(
            visibility=False
        )
        brow_positions = ['in', 'mid', 'out']

        for i in range(count):
            position_root_name = '%s_%s' % (this.root_name, brow_positions[i])
            box_handle = this.create_child(
                BoxHandleGuide,
                root_name=position_root_name,
                matrix=Matrix((i+1)*(size*4), 0.0, 0.0),
                owner=this
            )
            joint = box_handle.joints[0]
            box_handle.cube_mesh.assign_shading_group(root.shaders[side].shading_group)
            box_handle.handles[0].mesh.assign_shading_group(root.shaders[side].shading_group)
            box_handle.handles[1].mesh.assign_shading_group(root.shaders['y'].shading_group)
            box_handle.handles[2].mesh.assign_shading_group(root.shaders['z'].shading_group)
            box_handle.cones[0].mesh.assign_shading_group(root.shaders['x'].shading_group)
            box_handle.cones[1].mesh.assign_shading_group(root.shaders['y'].shading_group)
            box_handle.cones[2].mesh.assign_shading_group(root.shaders['z'].shading_group)
            joints.append(joint)
            handles.extend(box_handle.handles)
            locator = joint.create_child(
                Locator,
                root_name='line_%s' % position_root_name

            )
            locator.plugs.set_values(
                visibility=False
            )
            locators.append(locator)

            if i > 0:
                line = this.create_child(
                    Line,
                    index=i
                )
                locator_1 = locators[i-1]
                locator_2 = locators[i]

                locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
                locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))

            line = this.create_child(
                Line,
                root_name='%s_lid' % root_name,
                index=i
            )
            locator_1 = lid_locator
            locator_2 = locators[i]
            locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
            locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
            this.plugs['size'].connect_to(box_handle.plugs['size'])

        this.joints = joints
        this.handles = handles
        this.base_handles = list(handles)

        return this

    def __init__(self, **kwargs):
        super(BrowSliderArrayGuide, self).__init__(**kwargs)
        self.toggle_class = BrowSliderArray.__name__

    def get_toggle_blueprint(self):
        blueprint = super(BrowSliderArrayGuide, self).get_toggle_blueprint()
        blueprint['shape'] = self.shape
        return blueprint


class BrowSliderArray(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )
    shape = DataProperty(
        name='shape'
    )
    disconnected_joints = True

    def __init__(self, **kwargs):
        super(BrowSliderArray, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BrowSliderArray, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name
        matrices = this.matrices
        handles = []
        joints = []

        lid_joint = this.create_child(
            Joint,
            root_name='%s_lid' % root_name,
            matrix=matrices[0],
            parent=this.joint_group
        )
        lid_handle = this.create_handle(
            shape=this.shape,
            size=float(size) * 0.5,
            matrix=matrices[0],
            root_name='up_lid'
        )
        lid_joint.zero_rotation()
        lid_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2
        )
        controller.create_parent_constraint(
            lid_handle,
            lid_joint
        )
        handles.append(lid_handle)
        joints.append(lid_joint)
        brow_positions = ['in', 'mid', 'out']
        for i, matrix in enumerate(matrices[1:]):
            position_root_name = '%s_%s' % (this.root_name, brow_positions[i])
            joint = this.joint_group.create_child(
                Joint,
                matrix=matrix,
                root_name=position_root_name

            )
            handle = this.create_handle(
                root_name=position_root_name,
                shape=this.shape,
                size=size,
                matrix=matrix
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
                handle.plugs['ty'],
                lid_handle.plugs['ty'],
                0.25, 1.0,
                -0.3, 1.0,
                'brow_up_blink'
            )

            create_corrective_driver(
                handle.plugs['ty'],
                lid_handle.plugs['ty'],
                -0.25, 1.0,
                -0.3, 1.0,
                'brow_down_blink'
            )
            handles.append(handle)
            joints.append(joint)

        this.handles = handles
        this.joints = joints

        return this


def create_corrective_driver(plug_1, plug_2, in_value_1, out_value_1, in_value_2, out_value_2, name):

    root_name = '%s_%s_%s' % (
        plug_1.name.replace('.', '_'),
        plug_2.name.replace('.', '_'),
        name
    )
    node = plug_1.get_node()
    multiply_node = node.create_child(
        DependNode,
        node_type='multiplyDivide',
        root_name=root_name
    )
    remap_node_1 = node.create_child(
        DependNode,
        node_type='remapValue',
        root_name=root_name,
        index=1
    )
    remap_node_2 = node.create_child(
        DependNode,
        node_type='remapValue',
        root_name=root_name,
        index=2
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

