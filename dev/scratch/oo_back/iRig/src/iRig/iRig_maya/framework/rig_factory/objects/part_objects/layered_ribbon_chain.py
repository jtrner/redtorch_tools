
"""
TODO:
    * Blueprint support.
    * Restore the parts ability to result in joints that are in a chain
    without affecting child classes (layered_ribbon_spline_chain).
"""

import re

import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.rig_objects.joint_ribbon import JointRibbon
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle

from rig_math.matrix import Matrix


class LayeredRibbonChainGuide(SplineChainGuide):

    default_settings = {
        'root_name': 'chain',
        'size': 1.0,
        'side': 'center',
        'count': 5,
        'add_root': False,
        'fk_mode': False,
        'sub_levels': '9',
        'joint_count': 60,
        'extruded_ribbon': False
    }

    add_root = DataProperty(
        name='add_root'
    )
    fk_mode = DataProperty(
        name='fk_mode'
    )
    sub_levels = DataProperty(
        name='sub_levels'
    )
    extruded_ribbon = DataProperty(
        name='extruded_ribbon',
        default_value=False
    )

    def __init__(self, **kwargs):
        super(LayeredRibbonChainGuide, self).__init__(**kwargs)
        self.toggle_class = LayeredRibbonChain.__name__
        self.joint_chain = False


class LayeredRibbonChain(Part):

    add_root = DataProperty(
        name='add_root'
    )
    fk_mode = DataProperty(
        name='fk_mode'
    )
    sub_levels = DataProperty(
        name='sub_levels'
    )
    extruded_ribbon = DataProperty(
        name='extruded_ribbon',
        default_value=False
    )
    up_vector = DataProperty(
        name='up_vector'
    )

    root_handle = ObjectProperty(
        name='root_handle'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    joint_matrices = DataProperty(
        name='joint_matrices'
    )

    top_handles = ObjectListProperty(
        name='top_handles'
    )
    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LayeredRibbonChain, cls).create(controller, **kwargs)
        level_shapes = kwargs.get(
            'level_shapes',
            ['ball', 'circle', 'square']
        )
        root = this.get_root()
        add_root = this.add_root
        fk_mode = this.fk_mode
        matrices = this.matrices
        root_name = this.root_name
        side = this.side
        size = this.size
        sub_levels = map(int, re.findall(r'\d+', this.sub_levels))
        up_vector = this.up_vector
        handles = []

        if add_root:
            root_handle = this.create_handle(
                matrix=matrices[0],
                root_name=root_name + '_root_handle',
                shape='square',
                size=2 * size,
            )
            root.add_plugs([
                root_handle.plugs[m + a]
                for m in 'trs'
                for a in 'xyz'
            ])
            handle_kwargs = {'parent': root_handle}
            this.root_handle = root_handle
            this.handles.append(root_handle)
        else:
            handle_kwargs = {}

        top_handles = []
        top_joints = []
        fk_tweak_handles = []

        for i, matrix in enumerate(matrices):

            handle = this.create_handle(
                handle_type=GimbalHandle,
                index=i,
                matrix=matrix,
                root_name=root_name,
                shape='frame_x' if fk_mode else 'cube',
                size=1.25 * size,
                **handle_kwargs
            )
            root.add_plugs([
                handle.plugs[m + a]
                for m in 'trs'
                for a in 'xyz'
            ])

            if i < len(matrices) - 1 and fk_mode:
                handle.stretch_shape(matrices[i + 1])
                x_scale = 1.3 if i == 0 else 1.0
                shape_scale = [
                    x_scale if side == 'right' else x_scale * -1.0,
                    0.8,
                    0.8,
                ]
                handle.multiply_shape_matrix(Matrix(scale=shape_scale))
            joint = this.joint_group.create_child(
                Joint,
                root_name=root_name + '_top',
                index=i,
            )
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2
            )
            joint.zero_rotation()
            handles.append(handle)

            if fk_mode:
                handle_kwargs['parent'] = handle.gimbal_handle

            controller.create_parent_constraint(
                handle.gimbal_handle,
                joint,
                mo=False
            )

            top_handles.append(handle)
            top_joints.append(joint)

        settings_matrix = top_joints[0].get_matrix()
        settings_handle = this.create_handle(
            shape='gear',
            root_name=this.root_name + '_settings',
            matrix=settings_matrix,
            parent=top_joints[0]

        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )
        length_multiply_plug = settings_handle.create_plug(
            'ribbon_length_multiply',
            at='double',
            min=0.0,
            max=1.0,
            dv=1.0,
            k=True
        )
        handles.insert(0, settings_handle)

        settings_handle.groups[0].plugs['tz'].set_value(size*5 if side == 'right' else size*-5)
        fk_tweaks_plug = settings_handle.create_plug(
            'tweak_handle_vis',
            attributeType='bool',
            defaultValue=False,
            keyable=True
        )
        root.add_plugs([fk_tweaks_plug])
        this.settings_handle = settings_handle

        for tweak_handle in fk_tweak_handles:
            fk_tweaks_plug.connect_to(
                tweak_handle.plugs['visibility']
            )

        difference = len(sub_levels) - len(level_shapes)
        if difference > 0:
            level_shapes.extend([level_shapes[-1]] * difference)

        length_shapes = zip(sub_levels, level_shapes)

        sub_joints = list(top_joints)
        joint_ribbons = []
        for i, (level_length, level_shape) in enumerate(length_shapes):

            joint_ribbon = this.create_child(
                JointRibbon,
                index=i,
                up_vector=up_vector,
                positions=[x.get_translation() for x in sub_joints],
                joint_chain=False,
                joint_count=level_length,
                handle_size=size - i * 0.2,
                handle_shape=level_shape,
                handle_color=env.secondary_colors[side],
                extruded_ribbon=this.extruded_ribbon,
                owner=this
            )
            #top_handles.extend(joint_ribbon.handles)
            joint_ribbon.ribbon.plugs['inheritsTransform'].set_value(False)

            controller.scene.skinCluster(
                sub_joints,
                joint_ribbon.ribbon.nurbs_surface,
                toSelectedBones=True,
                maximumInfluences=1,
                bindMethod=0,
            )

            sub_joints = joint_ribbon.joints
            handles.extend(joint_ribbon.handles)
            joint_ribbons.append(joint_ribbon)
        if joint_ribbons:
            length_multiply_plug.connect_to(joint_ribbons[-1].plugs['length_multiply'])
        root.add_plugs(length_multiply_plug)
        this.joints = sub_joints
        this.set_handles(handles)
        this.top_handles = top_handles
        return this
