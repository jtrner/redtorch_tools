import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.base_ribbon_guide import BaseRibbonGuide
from rig_factory.objects.rig_objects.spline_array import SplineArray
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle, GroupedHandle
from rig_math.matrix import Matrix


class SimpleRibbonGuide(BaseRibbonGuide):

    default_settings = {
        'root_name': 'simple_ribbon',
        'size': 1.0,
        'side': 'right',
        'count': 5,
        'joint_count': 33,
        'fk_mode': False
    }

    fk_mode = DataProperty(
        name='fk_mode'
    )

    def __init__(self, **kwargs):
        super(SimpleRibbonGuide, self).__init__(**kwargs)
        self.toggle_class = SimpleRibbon.__name__

    def get_toggle_blueprint(self):
        blueprint = super(SimpleRibbonGuide, self).get_toggle_blueprint()
        position_1 = self.handles[0].get_matrix().get_translation()
        position_2 = self.handles[1].get_matrix().get_translation()
        blueprint.update(
            joint_matrices=[list(x.get_matrix()) for x in self.joints],
            matrices=[list(x.get_matrix()) for x in self.base_joints],
            up_vector=(position_2 - position_1).normalize().data
        )
        return blueprint


class SimpleRibbon(Part):

    add_root = DataProperty(
        name='add_root'
    )
    fk_mode = DataProperty(
        name='fk_mode'
    )
    sub_levels = DataProperty(
        name='sub_levels'
    )

    up_vector = DataProperty(
        name='up_vector'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    joint_matrices = DataProperty(
        name='joint_matrices'
    )

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )
    @classmethod
    def create(cls, controller, **kwargs):
        matrices = kwargs.get('matrices', [])
        if len(matrices) < 4:
            raise Exception('You must provide atleast 4 matrices to create a %s' % cls.__name__)
        this = super(SimpleRibbon, cls).create(controller, **kwargs)
        root = this.get_root()
        matrices = this.matrices
        joint_count = len(this.joint_matrices)
        root_name = this.root_name
        side = this.side
        size = this.size
        up_vector = this.up_vector
        joints = []
        spline_joints = []
        segment_handles = []
        sub_segment_handles = []

        for i, matrix in enumerate(matrices):
            joint = this.joint_group.create_child(
                Joint,
                index=i,
                matrix=matrix,
                root_name='%s_base' % root_name
            )
            joint.zero_rotation()
            joints.append(joint)
            joint.plugs['drawStyle'].set_value(2)

        settings_matrix = joints[0].get_matrix()
        settings_handle = this.create_handle(
            shape='gear',
            root_name=this.root_name + '_settings',
            matrix=settings_matrix,
            parent=joints[0]

        )
        settings_handle.groups[0].plugs['tz'].set_value(size*5 if side == 'right' else size*-5)

        length_multiply_plug = settings_handle.create_plug(
            'length',
            at='double',
            min=0.0,
            max=1.0,
            dv=1.0,
            k=True
        )

        sub_controls_plug = settings_handle.create_plug(
            'sub_controls',
            at='double',
            min=0.0,
            max=1.0,
            dv=0.0,
            k=True
        )


        base_handle = this.create_handle(
            handle_type=GimbalHandle,
            matrix=matrices[1],
            shape='cube',
            root_name='%s_base' % root_name
        )

        base_tip_handle = this.create_handle(
            handle_type=GroupedHandle,
            matrix=matrices[0],
            shape='diamond',
            root_name='%s_base_sub_tip' % root_name,
            size=size*0.33333,
            parent=base_handle.gimbal_handle
        )


        base_sub_handle = this.create_handle(
            handle_type=GroupedHandle,
            matrix=matrices[1],
            shape='diamond',
            root_name='%s_base_sub' % root_name,
            size=size*0.33333,
            parent=base_handle.gimbal_handle
        )

        sub_segment_handles.extend([base_tip_handle, base_sub_handle])


        #sub_controls_plug.connect_to(base_tip_handle.plugs['visibility'])
        #sub_controls_plug.connect_to(base_sub_handle.plugs['visibility'])


        distance = (base_handle.get_translation() - base_tip_handle.get_translation()).mag()
        base_shape_matrix = Matrix(0.0, distance*0.5 if side=='right' else distance*-0.5, 0.0)
        base_shape_matrix.set_scale([size, distance, size])
        base_handle.set_shape_matrix(base_shape_matrix)

        controller.create_parent_constraint(
            base_sub_handle,
            joints[1],
            mo=True
        )
        controller.create_parent_constraint(
            base_tip_handle,
            joints[0],
            mo=True
        )

        segment_handle_parent = this
        if this.fk_mode:
            segment_handle_parent = base_handle

        for h, matrix in enumerate(matrices[2:-2]):
            segment_handle = this.create_handle(
                handle_type=GimbalHandle,
                matrix=matrix,
                shape='cube',
                root_name='%s_segment' % root_name,
                index=h,
                parent=segment_handle_parent
            )

            sub_segment_handle = this.create_handle(
                handle_type=GroupedHandle,
                matrix=matrix,
                shape='diamond',
                root_name='%s_sub_segment' % root_name,
                size=size * 0.33333,
                parent=segment_handle.gimbal_handle,
                index=h

            )
            controller.create_parent_constraint(
                sub_segment_handle,
                joints[h+2],
                mo=False
            )

            #sub_controls_plug.connect_to(sub_segment_handle.plugs['visibility'])
            segment_handles.append(segment_handle)
            sub_segment_handles.append(sub_segment_handle)
            if this.fk_mode:
                segment_handle_parent = segment_handle


        end_handle = this.create_handle(
            handle_type=GimbalHandle,
            matrix=matrices[-2],
            shape='cube',
            root_name='%s_end' % root_name,
            parent=segment_handle_parent
        )

        end_tip_handle = this.create_handle(
            handle_type=GroupedHandle,
            matrix=matrices[-1],
            shape='diamond',
            root_name='%s_end_sub_tip' % root_name,
            size=size * 0.3333,
            parent=end_handle.gimbal_handle
        )
        end_sub_handle = this.create_handle(
            handle_type=GroupedHandle,
            matrix=matrices[-2],
            shape='diamond',
            root_name='%s_end_sub' % root_name,
            size=size * 0.33333,
            parent=end_handle.gimbal_handle
        )

        controller.create_parent_constraint(
            end_sub_handle,
            joints[-2],
            mo=True
        )
        controller.create_parent_constraint(
            end_tip_handle,
            joints[-1],
            mo=True
        )
        end_handle.stretch_shape(end_tip_handle.get_matrix())
        #sub_controls_plug.connect_to(end_tip_handle.plugs['visibility'])
        #sub_controls_plug.connect_to(end_sub_handle.plugs['visibility'])
        sub_segment_handles.extend([end_tip_handle, end_sub_handle])

        spline_array = this.create_child(
            SplineArray,
            up_vector=up_vector,
            positions=[list(x.get_translation()) for x in matrices],
            joint_chain=False,
            count=joint_count,
            handle_shape='square',
            handle_color=env.secondary_colors[side],
            extruded_ribbon=True,
            root_name='%s_spline' % root_name,
            side=side
        )

        length_multiply_plug.connect_to(spline_array.plugs['length_multiply'])
        spline_array.ribbon.plugs['inheritsTransform'].set_value(False)
        controller.scene.skinCluster(
            joints,
            spline_array.ribbon.nurbs_surface,
            toSelectedBones=True,
            maximumInfluences=1,
            bindMethod=0,
        )

        joint_parent = this.joint_group
        for transform in spline_array.transforms:
            joint = joint_parent.create_child(
                Joint,
                index=transform.index,
                matrix=transform.get_matrix()
            )
            joint.zero_rotation()
            spline_joints.append(joint)
            joint_parent = joint
            controller.create_parent_constraint(
                transform,
                joint
            )

        root.add_plugs(
            [
                base_handle.plugs['tx'],
                base_handle.plugs['ty'],
                base_handle.plugs['tz'],
                base_handle.plugs['rx'],
                base_handle.plugs['ry'],
                base_handle.plugs['rz'],
                base_handle.plugs['sx'],
                base_handle.plugs['sy'],
                base_handle.plugs['sz'],
                end_handle.plugs['tx'],
                end_handle.plugs['ty'],
                end_handle.plugs['tz'],
                end_handle.plugs['rx'],
                end_handle.plugs['ry'],
                end_handle.plugs['rz'],
                end_handle.plugs['sx'],
                end_handle.plugs['sy'],
                end_handle.plugs['sz'],
                length_multiply_plug,

            ]
        )
        for sub_handle in segment_handles:
            root.add_plugs(
                [
                    sub_handle.plugs['tx'],
                    sub_handle.plugs['ty'],
                    sub_handle.plugs['tz'],
                    sub_handle.plugs['rx'],
                    sub_handle.plugs['ry'],
                    sub_handle.plugs['rz'],
                    sub_handle.plugs['sx'],
                    sub_handle.plugs['sy'],
                    sub_handle.plugs['sz']
                ]
            )

        for h in sub_segment_handles:
            root.add_plugs(
                [
                    h.plugs['tx'],
                    h.plugs['ty'],
                    h.plugs['tz']
                ]
            )

        root.add_plugs(
            [sub_controls_plug],
            keyable=False
        )
        this.settings_handle = settings_handle
        #this.secondary_handles = sub_handles
        this.joints = spline_joints
        return this
