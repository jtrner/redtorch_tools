import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.part_objects.part import PartGuide
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.rig_objects.spline_array import SplineArray
from rig_factory.objects.rig_objects.capsule import Capsule


class BaseRibbonGuide(PartGuide):

    capsules = ObjectListProperty(
        name='capsules'
    )
    locators = ObjectListProperty(
        name='locators'
    )
    count = DataProperty(
        name='count'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    joint_count = DataProperty(
        name='joint_count',
        default_value=9
    )
    default_settings = dict(
        root_name='chain',
        size=1.0,
        side='center',
        joint_count=9,
        count=5
    )

    def __init__(self, **kwargs):
        super(BaseRibbonGuide, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        up_vector_indices = kwargs.pop('up_vector_indices', [0])
        this = super(BaseRibbonGuide, cls).create(controller, **kwargs)
        root = this.get_root()
        side = kwargs.setdefault('side', 'center')
        size = this.size
        joint_count = this.joint_count
        root_name = this.root_name
        side_vectors = env.side_world_vectors[side]
        spacing = size * 2.0
        size_plug = this.plugs['size']
        aim_vector = env.aim_vector
        up_vector = env.up_vector
        handle_positions = kwargs.get('handle_positions', dict())
        if side == 'right':
            aim_vector = [x * -1.0 for x in env.aim_vector]
            up_vector = [x * -1.0 for x in env.up_vector]
        spline_joints = []
        joints = []
        handles = []
        locators = []
        up_handles = []
        base_handles = []
        aim_up_handles = []
        capsules = []
        up_handle_lines = dict()

        size_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_size' % root_name
        )
        size_plug.connect_to(size_multiply.plugs['input1X'])
        size_plug.connect_to(size_multiply.plugs['input1Y'])
        size_multiply.plugs['input2X'].set_value(0.5)
        size_multiply.plugs['input2Y'].set_value(0.25)

        for i in range(this.count):
            if i in up_vector_indices:
                up_handle = this.create_handle(
                    index=len(up_handles),
                    root_name='%s_up' % root_name
                )
                position = handle_positions.get(up_handle.name, [
                    side_vectors[0] * (spacing * i),
                    side_vectors[1] * (spacing * i),
                    spacing * -5
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

            joint = this.create_child(
                Joint,
                index=i,
                root_name='%s_base' % root_name
            )
            handle = this.create_handle(
                index=i
            )
            position = handle_positions.get(handle.name, [0.0, spacing*i, 0.0])
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
                drawStyle=2
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
                controller.create_aim_constraint(
                    handles[i + 1],
                    joints[i],
                    worldUpType='object',
                    worldUpObject=up_handle.get_selection_string(),
                    aimVector=aim_vector,
                    upVector=up_vector
                )
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
                locator_1.plugs.set_values(
                    visibility=False
                )
                locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
                locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
                up_handle_lines[up_handle] = line


        spine_handles = handles[1:]
        curve_degree = 1 if this.count < 3 else 2
        positions = [x.get_translation() for x in this.handles[1:]]

        nurbs_curve_transform = this.create_child(
            Transform,
            root_name=root_name
        )
        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            root_name=root_name,
            positions=positions
        )
        nurbs_curve.plugs['v'].set_value(False)
        curve_info = controller.create_object(
            DependNode,
            root_name='%s_curveInfo' % root_name,
            node_type='curveInfo'
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
        for i, spine_handle in enumerate(spine_handles):
            position_locator = locators[i]
            position_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )
            position_locator.plugs['visibility'].set_value(False)
        length_divide = controller.create_object(
            DependNode,
            root_name='%s_length_divide' % root_name,
            node_type='multiplyDivide'
        )
        curve_info.plugs['arcLength'].connect_to(length_divide.plugs['input1X'])
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2X'].set_value(joint_count - 1)

        spline_array = this.create_child(
            SplineArray,
            up_vector=up_vector,
            positions=map(list, positions),
            joint_chain=False,
            count=joint_count,
            handle_shape='square',
            handle_color=env.secondary_colors[side],
            extruded_ribbon=True,
            root_name='%s_spline' % root_name,
            side=side
        )

        controller.scene.skinCluster(
            [x.get_selection_string() for x in joints],
            spline_array.ribbon.nurbs_surface,
            toSelectedBones=True,
            maximumInfluences=1,
            bindMethod=0,
        )

        joint_parent = this
        spline_locators = []
        for i in range(joint_count):
            source_transform = spline_array.transforms[i]
            joint = joint_parent.create_child(
                Joint,
                index=source_transform.index,
                matrix=source_transform.get_matrix()
            )
            joint.zero_rotation()
            spline_joints.append(joint)
            joint_parent = joint
            controller.create_parent_constraint(
                source_transform,
                joint
            )
            joint.plugs['drawStyle'].set_value(2)
            spline_locator = joint.create_child(
                Locator
            )
            spline_locator.plugs['visibility'].set_value(False)
            spline_locators.append(spline_locator)
            if i != 0:
                capsule = this.create_child(
                    Capsule,
                    index=i,
                    root_name='%s_spline_segment' % root_name,
                    parent=this,
                    size=size * 0.5
                )
                capsule.poly_cylinder.plugs['roundCap'].set_value(0)
                capsule.mesh.assign_shading_group(root.shaders[side].shading_group)
                size_plug.connect_to(capsule.plugs['size'])

                locator_1 = spline_locators[i - 1]
                locator_2 = spline_locators[i]
                joint_1 = spline_joints[i - 1]
                joint_2 = spline_joints[i]
                locator_1.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position1'])
                locator_2.plugs['worldPosition'].element(0).connect_to(capsule.plugs['position2'])
                controller.create_point_constraint(joint_1, joint_2, capsule)
                controller.create_aim_constraint(
                    joint_2,
                    capsule,
                    aimVector=env.aim_vector
                )
        this.locators = locators
        this.capsules = capsules
        handles.extend(up_handles)
        this.base_joints = joints
        this.base_handles = base_handles
        this.joints = spline_joints
        return this

    def get_blueprint(self):
        if self.toggle_class is None:
            raise Exception('You must subclass this and set the toggle_class')
        blueprint = super(BaseRibbonGuide, self).get_blueprint()
        blueprint.update(dict(
            count=self.count,
            joint_count=self.joint_count
        ))
        return blueprint

    def get_toggle_blueprint(self):
        if self.toggle_class is None:
            raise Exception('You must subclass this and set the toggle_class')
        blueprint = super(BaseRibbonGuide, self).get_toggle_blueprint()
        position_1 = self.handles[0].get_matrix().get_translation()
        position_2 = self.handles[1].get_matrix().get_translation()
        blueprint.update(
            joint_matrices=[list(x.get_matrix()) for x in self.joints],
            matrices=[list(x.get_matrix()) for x in self.base_joints],
            up_vector=(position_2 - position_1).normalize().data
        )
        return blueprint
