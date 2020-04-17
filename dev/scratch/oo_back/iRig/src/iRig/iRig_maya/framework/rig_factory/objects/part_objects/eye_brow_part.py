import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_math.matrix import Matrix


class EyebrowPartGuide(PartGuide):
    """
    Uses count for the number of top handles and joint count for the
    number of bottom joints.
    """

    count = DataProperty(
        name='count'
    )
    joint_count = DataProperty(
        name='joint_count'
    )

    default_settings = dict(
        root_name='eyebrow',
        size=1.0,
        side='center',
        joint_count=7,
        count=3,
    )

    def __init__(self, **kwargs):
        super(EyebrowPartGuide, self).__init__(**kwargs)
        self.toggle_class = EyebrowPart.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyebrowPartGuide, cls).create(controller, **kwargs)

        root = this.get_root()
        root_name = this.root_name
        size = this.size
        count = this.count
        joint_count = this.joint_count
        length_scale = 3

        side = kwargs.get('side', 'center')
        vector = kwargs.get('vector', (0, 0, -1.0))

        ribbon = this.create_child(
            Ribbon,
            [[i * size * length_scale, 0, 0] for i in range(count)],
            vector=vector,
            root_name='%s_ribbon' % root_name,
            degree=2,
        )
        ribbon.plugs.set_values(
            inheritsTransform=False,
        )

        guide_handles = []
        guide_handle_joints = []
        for i in range(count):

            x_parameter = ((count - 1) * size * length_scale) / (count - 1)
            guide_handle = this.create_handle(
                index=i,
                matrix=Matrix(x_parameter * i, 0, 0),
                size=size,
            )
            guide_handle.mesh.assign_shading_group(
                root.shaders[side].shading_group
            )
            this.plugs['size'].connect_to(
                guide_handle.plugs['size']
            )
            guide_handles.append(guide_handle)

            x_guide_cone = guide_handle.create_child(
                Cone,
                index=i,
                root_name='%s_x_cone' % root_name,
                axis=(1.0, 0, 0),
                size=size,
            )
            x_guide_cone.mesh.assign_shading_group(
                root.shaders['x'].shading_group
            )

            y_guide_cone = guide_handle.create_child(
                Cone,
                index=i,
                root_name='%s_y_cone' % root_name,
                axis=(0, 1.0, 0),
                size=size,
            )
            y_guide_cone.mesh.assign_shading_group(
                root.shaders['y'].shading_group
            )

            z_guide_cone = guide_handle.create_child(
                Cone,
                index=i,
                root_name='%s_z_cone' % root_name,
                axis=(0, 0, 1.0),
                size=size,
            )
            z_guide_cone.mesh.assign_shading_group(
                root.shaders['z'].shading_group
            )

            joint = this.create_child(
                Joint,
                index=i,
            )
            joint.plugs.set_values(
                visibility=False,
            )
            guide_handle_joints.append(joint)

            guide_handle.plugs['translate'].connect_to(
                joint.plugs['translate']
            )

        this.controller.scene.skinCluster(
            ribbon,
            guide_handle_joints,
            bindMethod=0,
            maximumInfluences=1,
        )

        # Ribbon is hidden after skinning to avoid a maya issue when
        # skinning to hidden objects.
        ribbon.nurbs_surface.plugs.set_values(visibility=False)

        surface_point_parameter = 1.0 / (joint_count - 1)
        surface_points = []
        surface_point_joints = []
        for i in range(joint_count):

            surface_point = ribbon.create_child(
                SurfacePoint,
                index=i,
                parent=ribbon,
                surface=ribbon.nurbs_surface,
            )
            surface_point.follicle.plugs.set_values(
                parameterU=0.5,
                parameterV=surface_point_parameter * i,
                visibility=False,
            )
            surface_points.append(surface_point)

            joint = surface_point.create_child(
                Joint,
                index=i,
            )
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=1,
                radius=0.25,
            )
            surface_point_joints.append(joint)

        this.joints = guide_handle_joints

        return this


class EyebrowPart(Part):
    """
    Creates what is essentially a ribbon, but with two minor changes.
    The two top joints at either end of the ribbon take rotations from
    both their next sibling joint's handle as well as their own parent's
    handle.
    """

    count = DataProperty(
        name='count'
    )
    joint_count = DataProperty(
        name='joint_count'
    )

    def __init__(self, **kwargs):
        super(EyebrowPart, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyebrowPart, cls).create(controller, **kwargs)
        root = this.get_root()
        root_name = this.root_name
        count = this.count
        size = this.size
        joint_count = this.joint_count
        matrices = this.matrices

        ribbon = this.create_child(
            Ribbon,
            root_name='%s_ribbon' % root_name,
            positions=[list(x.get_translation()) for x in matrices],
            degree=3,
        )
        ribbon.plugs.set_values(
            inheritsTransform=False,
        )
        this.controller.scene.rebuildSurface(
            ribbon,
            degreeV=0,
            direction=1,
            spansV=(count - 1) * 2,
        )

        surface_point_transform = this.create_child(
            Transform,
            root_name='%s_spt' % root_name,
        )

        handles_transform = this.create_child(
            Transform,
            root_name='%s_handles' % root_name,
        )

        tweak_handles_transform = this.create_child(
            Transform,
            root_name='%s_tweak_handles' % root_name,
        )
        tweak_handles_transform.plugs.set_values(
            inheritsTransform=False,
        )

        top_handles = []
        top_joints = []
        aim_transform = None
        constraint_transform = None
        for i, matrix in enumerate(matrices):

            is_end = i == 0 or i == len(matrices) - 1

            handle = this.create_handle(
                handle_type=LocalHandle,
                index=i,
                shape='ball',
                matrix=matrix.get_translation(),
                size=size,
            )
            root.add_plugs([
                handle.plugs[mode + axis]
                for mode in 'trs'
                for axis in 'xyz'
            ])
            top_handles.append(handle)

            if is_end:
                aim_transform = handle.create_child(
                    Transform,
                    root_name='%s_aim' % root_name,
                )
                constraint_transform = aim_transform.create_child(
                    Transform,
                    root_name='%s_constraint' % root_name
                )
                handle.plugs['rotate'].connect_to(
                    constraint_transform.plugs['rotate']
                )

            joint = this.joint_group.create_child(
                Joint,
                root_name=root_name,
                index=i,
            )
            joint.plugs.set_values(
                visibility=False,
            )
            top_joints.append(joint)

            parent = constraint_transform if is_end else handle
            controller.create_parent_constraint(parent, joint)
            controller.create_scale_constraint(parent, joint)

            if i == 1:
                controller.create_aim_constraint(
                    top_handles[1],
                    aim_transform,
                    upVector=(0, 0, -1),
                    worldUpVector=(0, 0, -1),
                    worldUpObject=top_handles[1],
                    worldUpType='objectrotation',
                )
            elif i == len(matrices) - 1:
                controller.create_aim_constraint(
                    top_handles[-2],
                    aim_transform,
                    upVector=(0, 0, -1),
                    worldUpVector=(0, 0, -1),
                    worldUpObject=top_handles[1],
                    worldUpType='objectrotation',
                    aimVector=(-1, 0, 0),
                )

        surface_point_parameter = 1.0 / (joint_count - 1)
        surface_points = []
        bottom_handles = []
        bottom_joints = []
        for i in range(joint_count):

            surface_point = surface_point_transform.create_child(
                SurfacePoint,
                index=i,
                surface=ribbon.nurbs_surface,
            )
            surface_point.follicle.plugs.set_values(
                parameterU=0.5,
                parameterV=surface_point_parameter * i,
            )
            surface_point.plugs.set_values(
                visibility=False,
            )
            surface_points.append(surface_point)

            handle = tweak_handles_transform.create_child(
                LocalHandle,
                owner=tweak_handles_transform,
                index=i,
                root_name='%s_tweak' % root_name,
                size=size,
                shape='circle',
            )
            root.add_plugs([
                handle.plugs[mode + axis]
                for mode in 'trs'
                for axis in 'xyz'
            ])
            bottom_handles.append(handle)

            surface_point.plugs['translate'].connect_to(
                handle.groups[0].plugs['translate'],
            )
            surface_point.plugs['rotate'].connect_to(
                handle.groups[0].plugs['rotate'],
            )

            this.plugs['scale'].connect_to(
                handle.groups[0].plugs['scale'],
            )

            joint = this.joint_group.create_child(
                Joint,
                root_name='%s_tweak' % root_name,
                index=i,
            )
            joint.plugs.set_values(
                visibility=False,
            )
            bottom_joints.append(joint)

            controller.create_parent_constraint(
                handle,
                joint,
            )
            controller.create_scale_constraint(
                handle,
                joint,
            )

        this.controller.scene.skinCluster(
            ribbon,
            top_joints,
            bindMethod=0,
            maximumInfluences=2,
        )

        # Ribbon is hidden after skinning to avoid a maya issue when
        # skinning to hidden objects.
        ribbon.plugs.set_values(visibility=False)

        this.secondary_handles = bottom_handles
        this.joints = top_joints

        return this
