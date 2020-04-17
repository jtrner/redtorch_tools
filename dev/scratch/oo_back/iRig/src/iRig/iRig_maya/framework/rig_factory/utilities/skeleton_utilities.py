from rig_factory.objects.node_objects.joint import Joint
import rig_factory.environment as env


def build_bind_skeleton(container, root_name='bind'):
    for part in container.get_parts():
        controller = part.controller
        root = part.get_root()
        deform_joints = []
        part_joints = part.joints
        joint_parent = root.deform_group
        for j, part_joint in enumerate(part_joints):
            deform_joint = controller.create_object(
                Joint,
                parent=joint_parent,
                root_name='%s_%s' % (part_joint.root_name, root_name),
                index=part_joint.index,
                side=part_joint.side,
                size=part_joint.size,
                matrix=part_joint.get_matrix()
            )
            deform_joint.plugs['radius'].set_value(part_joint.size)
            deform_joint.zero_rotation()
            deform_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                radius=part_joint.plugs['radius'].get_value(),
                type=part_joint.plugs['type'].get_value(),
                side=part_joint.plugs['side'].get_value(),
                drawStyle=part_joint.plugs['drawStyle'].get_value(2)
            )
            part_joint.plugs['rotateOrder'].connect_to(deform_joint.plugs['rotateOrder'])
            part_joint.plugs['inverseScale'].connect_to(deform_joint.plugs['inverseScale'])
            part_joint.plugs['jointOrient'].connect_to(deform_joint.plugs['jointOrient'])
            part_joint.plugs['translate'].connect_to(deform_joint.plugs['translate'])
            part_joint.plugs['rotate'].connect_to(deform_joint.plugs['rotate'])
            part_joint.plugs['scale'].connect_to(deform_joint.plugs['scale'])
            part_joint.plugs['drawStyle'].set_value(2)
            if part.joint_chain:
                joint_parent = deform_joint
            deform_joints.append(deform_joint)
        part.deform_joints = deform_joints
        part.base_deform_joints = deform_joints
