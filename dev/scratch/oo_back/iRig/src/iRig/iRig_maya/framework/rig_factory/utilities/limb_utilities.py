from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle

import rig_math.utilities as rmu
import rig_factory.environment as env
# import rig_factory.utilities.rig_utilities as rtl


SIDE_SCALE = 's{0}'.format(env.side_vector_axis['left'][-1])  # scale attribute to scale for squash and stretch
AXES = ['x', 'y', 'z']
AXES.remove(env.side_vector_axis['left'][-1])
AXES.remove(env.aim_vector_axis[-1])
FRONT_SCALE = 's{0}'.format(AXES[0])  # scale attribute to scale for squash and stretch


def generate_squash_and_stretch_based_on_curve_length(curve_info_node,
                                                      joints,
                                                      attr_object,
                                                      attr_label='stretch_multiplier',
                                                      scale_axis_side=SIDE_SCALE,
                                                      scale_axis_front=FRONT_SCALE,
                                                      ):
    root = attr_object.owner.get_root()
    stretch_multiplier_plug = attr_object.create_plug(attr_label, at='double', k=True, dv=1, min=0, max=10)
    root.add_plugs([stretch_multiplier_plug])

    default_length = curve_info_node.plugs['arcLength'].get_value()

    squash_ratio = joints[0].create_child(
        DependNode,
        node_type='multiplyDivide',
        root_name='{0}_squashRatio'.format(joints[0].root_name),
    )
    squash_ratio.plugs['input1X'].set_value(default_length)  # default length
    squash_ratio.plugs['operation'].set_value(2)  # divide by
    curve_info_node.plugs['arcLength'].connect_to(squash_ratio.plugs['input2X'])  # live length

    stretch_ratio = joints[0].create_child(
        DependNode,
        node_type='multiplyDivide',
        root_name='{0}_stretchRatio'.format(joints[0].root_name),
    )
    stretch_ratio.plugs['input1X'].set_value(default_length)  # default length
    stretch_ratio.plugs['operation'].set_value(2)  # divide by
    curve_info_node.plugs['arcLength'].connect_to(stretch_ratio.plugs['input2X'])  # live length

    first_half_len = len(joints)/2
    squash_first_half_multiplier = rmu.calculate_in_between_weights(first_half_len)
    squash_last_half_multiplier = rmu.calculate_in_between_weights(len(joints) - first_half_len)[::-1]
    squash_multiplier_values = rmu.smooth_average_list_values(squash_first_half_multiplier + squash_last_half_multiplier)
    for i, (joint, blend_weight) in enumerate(zip(joints, squash_multiplier_values)):
        squash_blend = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            root_name='{0}_squashBlender'.format(joints[0].root_name),
            index=i,
        )
        squash_blend.plugs['color2R'].set_value(1)
        squash_blend.plugs['blender'].set_value(blend_weight)
        squash_ratio.plugs['outputX'].connect_to(squash_blend.plugs['color1R'])

        stretch_blend = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            root_name='{0}_stretchBlender'.format(joints[0].root_name),
            index=i,
        )
        stretch_blend.plugs['color2R'].set_value(1)
        stretch_blend.plugs['blender'].set_value(blend_weight)
        stretch_ratio.plugs['outputX'].connect_to(stretch_blend.plugs['color1R'])

        squash_stretch_flip_cond = joint.create_child(
            DependNode,
            node_type='condition',
            root_name='{0}_squashStretchFlipCond'.format(joints[0].root_name),
            inded=i,
        )
        stretch_ratio.plugs['outputX'].connect_to(squash_stretch_flip_cond.plugs['firstTerm'])  # if user attr
        squash_stretch_flip_cond.plugs['operation'].set_value(4)  # less than
        squash_stretch_flip_cond.plugs['secondTerm'].set_value(1)  # 1
        stretch_blend.plugs['outputR'].connect_to(squash_stretch_flip_cond.plugs['colorIfTrueR'])
        squash_blend.plugs['outputR'].connect_to(squash_stretch_flip_cond.plugs['colorIfFalseR'])

        multiplier = joints[0].create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_multiplier'.format(joints[0].root_name),
            index=i
        )
        squash_stretch_flip_cond.plugs['outColorR'].connect_to(multiplier.plugs['input1X'])
        multiplier.plugs['operation'].set_value(3)
        stretch_multiplier_plug.connect_to(multiplier.plugs['input2X'])  # live length

        for axis in (scale_axis_side, scale_axis_front):
            multiplier.plugs['outputX'].connect_to(joint.plugs[axis])

    return [stretch_multiplier_plug]


def generate_squash_and_stretch_adjacent_distances(joints,
                                                   attr_object,
                                                   attr_label='volume_stretch',
                                                   scale_axis_side=SIDE_SCALE,
                                                   scale_axis_front=FRONT_SCALE,
                                                   default_value=1):
    '''
    Converts mesh skinning joints to be able to squash and stretch. This system looks at the distance between its
    surrounding joint positions and scales itself based on those distances.
    NOTE: if applying to IK spline DO NOT include the last joint of the VERY last joing in the spline IK, go from first
    joint to second last. jointsList[:-1]

    :param joints: list() all the joints which will have the squash and stretch applied.
    :param attr_object: Object in your rig which the custom attributes will be applied.
    :param attr_label: str() Text label for the stretch custom attribute.
    :param scale_axis_side: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param scale_axis_front: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param default_value: float() Default value of the custom attribute, default is 1 for on.
    '''
    root_name = joints[0].root_name

    stretchable_weight_plug = attr_object.create_plug(
        '{0}_weight'.format(attr_label),
        at='double',
        k=True,
        dv=1,
        min=0,
        max=1)  # 1 for stretchable, 0 for not stretchable

    stretchable_plug = attr_object.create_plug(
        attr_label,
        at='double',
        k=True,
        dv=default_value,
        min=0,
        max=10)  # 1 for stretchable, 0 for not stretchable

    position_locators = []
    for i, jnt in enumerate(joints):
        pos = jnt.create_child(Locator, root_name='{0}_distancePosition'.format(root_name), index=i)
        position_locators.append(pos)

    distance_nodes = []
    for i in range(len(position_locators)-1):
        distance_between_node = position_locators[i].create_child(
            DependNode,
            node_type='distanceBetween',
            root_name='%s_distanceBetween' % root_name,
            index=i)
        position_locators[i].plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs['point1'])
        position_locators[i + 1].plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs['point2'])
        distance_nodes.append(distance_between_node)

    for i, jnt in enumerate(joints[1:]):
        default_distance = distance_nodes[i].plugs['distance'].get_value()

        # stretchable weight blend node
        stretchable_weight = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            root_name='{0}_stretchableWeight{1:03d}'.format(root_name, i),
            index=i)
        stretchable_weight.plugs['color2R'].set_value(1.0)
        stretchable_weight_plug.connect_to(stretchable_weight.plugs['blender'])

        if not (default_distance <= 0.0001 and default_distance >= -0.0001):
            distance_ratio = jnt.create_child(
                DependNode,
                node_type='multiplyDivide',
                root_name='%s_distanceRatio' % root_name,
                index=i
            )
            distance_ratio.plugs['input1X'].set_value(default_distance)  # default distance
            distance_ratio.plugs['operation'].set_value(2)  # divide by
            distance_nodes[i].plugs['distance'].connect_to(distance_ratio.plugs['input2X'])  # live distance

            stretch_add = jnt.create_child(
                DependNode,
                node_type='plusMinusAverage',
                root_name='%s_stretchAdd' % root_name,
                index=i
            )
            distance_ratio.plugs['outputX'].connect_to(stretch_add.plugs['input1D'].element(0))  # live distance
            stretch_add.plugs['operation'].set_value(1)  # add by
            stretchable_plug.connect_to(stretch_add.plugs['input1D'].element(1))

            stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
        else:
            stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])

    root = attr_object.owner.get_root()
    root.add_plugs([stretchable_weight_plug, stretchable_plug])


def generate_squash_and_stretch_lite(joints,
                                     attr_object,
                                     attr_labels=None,
                                     attr_labels_suffix='volume_stretch',
                                     default_value=0.0,
                                     scale_axis_side=SIDE_SCALE,
                                     scale_axis_front=FRONT_SCALE,
                                     anchor_handles=None,
                                     inherit_scale_on_last_chain=False):
    '''
    Converts mesh skinning joints to be able to squash and stretch. It works best if there are same amount of skin
    joints between every control control provided(anchor_handles). This system works by looking at the distances
    between the provided controls in the anchor_handles, and evenly distributes that distance between the in between
    joints, provided in the joints arg.
    Note: This also works best with the convert_ik_to_stretchable function in the limb utils.

    :param joints: list() all the joints which will have the squash and stretch applied.
    :param attr_object: Object in your rig which the custom attributes will be applied.
    :param attr_labels: list(str) List of strings of the limb "bone" which will be on the custom attributes.
    Example: ['biceot', 'forearm'] or ['thigh', 'shin'] etc.
    Note: Make sure this list has the length one less longer than the attr_labels list
    together.
    :param attr_labels_suffix: str() the suffix string that comes after every attr_labels arg.
    :param default_value: float() Default value of the custom attribute, default is 1 for on.
    :param scale_axis_side: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param scale_axis_front: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param anchor_handles: list() List of rig handles(controls) that the code will use to measure the distances between
    for the squash and stretch.
    Note: Make sure this list has the length one more longer than the attr_labels list
    :param inherit_scale_on_last_chain: bool() For something like the leg, where the squash and stretch goes to the toe,
    setting this arg to True, the last chain(Toe) will inherit whatever scale is coming out of the second last joint
    (foot).
    '''
    if len(anchor_handles) - 1 != len(attr_labels):
        raise Exception('Make sure the attr_labels list has the length 1 less than the anchor_handles list. For example, attr_labels=["thigh", "shin"], anchor_handles[jointA, jointB, jointC]')

    root_name = joints[0].root_name

    # linear falloff
    length_of_one_segment = len(joints) / (len(anchor_handles) - 1)
    linear_values = [0.0 for i in range(length_of_one_segment*(len(anchor_handles)-1))]
    list_start_linear = [i * (1.0 / (length_of_one_segment - 1)) for i in range(length_of_one_segment)]
    list_end_linear = list_start_linear[::-1]
    linear_values[:length_of_one_segment] = list_end_linear
    if inherit_scale_on_last_chain:
        linear_values[-length_of_one_segment:] = list_end_linear  # Tapers small to large at last chain
    else:
        linear_values[-length_of_one_segment:] = list_start_linear  # Tapers large to small at last chain

    # smoothed list
    smoothed_values = linear_values

    # break from anchor indicies
    anchor_indicies = [i * length_of_one_segment for i in range(len(anchor_handles))]
    chains = []
    last_index = anchor_indicies[0]
    for index in anchor_indicies[1:]:
        chains.append(joints[last_index:index])
        last_index = index
    output_nodes = []
    for i, chain in enumerate(chains):
        distance_node = create_distance_between(anchor_handles[i], anchor_handles[i+1])
        default_distance = distance_node.plugs['distance'].get_value()

        distance_ratio = joints[0].create_child(DependNode,
                                                node_type='multiplyDivide',
                                                root_name='%s_defaultDistanceRatio' % root_name,
                                                index=i)
        distance_node.plugs['distance'].connect_to(distance_ratio.plugs['input1X'])  # live length
        distance_ratio.plugs['operation'].set_value(2)  # divide by
        distance_ratio.plugs['input2X'].set_value(default_distance)  # default distance

        squash_and_stretch_offset = joints[0].create_child(DependNode,
                                                           node_type='multiplyDivide',
                                                           root_name='%s_chainSquashAndStretchOffset' % root_name,
                                                           index=i)
        squash_and_stretch_offset.plugs['input1X'].set_value(1)
        squash_and_stretch_offset.plugs['operation'].set_value(2)  # divide by
        distance_ratio.plugs['outputX'].connect_to(squash_and_stretch_offset.plugs['input2X'])  # live length ratio

        output_nodes.append({'node': squash_and_stretch_offset, 'chain': chain})

    joint_index = 0
    last_stretch_add = None
    for i, data in enumerate(output_nodes):
        stretchable_weight_plug = attr_object.create_plug(
            '{0}_{1}_weight'.format(attr_labels[i], attr_labels_suffix),
            at='double',
            k=True,
            dv=1,
            min=0,
            max=1)  # 1 for stretchable, 0 for not stretchable
        stretchable_plug = attr_object.create_plug(
            '{0}_{1}'.format(attr_labels[i], attr_labels_suffix),
            at='double',
            k=True,
            dv=default_value,
            min=-10,
            max=10)  # 1 for stretchable, 0 for not stretchable
        for j, jnt in enumerate(data['chain']):
            # blend
            per_joint_blend = joints[0].create_child(DependNode,
                                                     node_type='blendColors',
                                                     root_name='{0}_perJointBlend{1:03d}'.format(root_name, j),
                                                     index=i)
            per_joint_blend.plugs['color1R'].set_value(1.0)
            data['node'].plugs['outputX'].connect_to(per_joint_blend.plugs['color2R'])
            per_joint_blend.plugs['blender'].set_value(smoothed_values[joint_index])
            joint_index += 1

            stretch_add = joints[0].create_child(DependNode,
                                                 node_type='plusMinusAverage',
                                                 root_name='{0}_stretchAdd{1:03d}'.format(root_name, j),
                                                 index=i)
            per_joint_blend.plugs['outputR'].connect_to(stretch_add.plugs['input1D'].element(0))  # blend result output
            stretch_add.plugs['operation'].set_value(1)  # add by
            stretchable_plug.connect_to(stretch_add.plugs['input1D'].element(1))  # stretchable attribute

            # stretchable weight blend node
            stretchable_weight = joints[0].create_child(DependNode,
                                                        node_type='blendColors',
                                                        root_name='{0}_stretchableWeight{1:03d}'.format(root_name,
                                                                                                        j),
                                                        index=i)
            stretchable_weight.plugs['color2R'].set_value(1.0)
            stretchable_weight_plug.connect_to(stretchable_weight.plugs['blender'])

            if inherit_scale_on_last_chain and i == len(output_nodes) - 1:  # inherit scale to True and last chain
                inherit_scale = joints[0].create_child(DependNode,
                                                       node_type='multiplyDivide',
                                                       root_name='{0}_inheritScale{1:03d}'.format(root_name, j),
                                                       index=i)
                last_stretch_add.plugs['output1D'].connect_to(inherit_scale.plugs['input1X'])
                inherit_scale.plugs['operation'].set_value(1)  # multiply by
                stretch_add.plugs['output1D'].connect_to(inherit_scale.plugs['input2X'])

                inherit_scale.plugs['outputX'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
            elif i == len(output_nodes) - 1:  # inherit scale to False last chain
                last_stretch_add = stretch_add

                stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
            else:  # every other joint other than last joint
                last_stretch_add = stretch_add

                stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])

        root = attr_object.owner.get_root()
        root.add_plugs([stretchable_weight_plug, stretchable_plug])


def create_stretchy_ik_joints(nurbs_curve, joints, side):
    '''
    Converts your IK spline to be stretchable(joints, evenly spaced). This function does not generate a custom attribute
    for blending on and off the stretching. Possible future development could add the custom attribute, but as of the
    moment, we do not have a use for it.
    :param nurbs_curve: Nurbs curve object to measure the length from.
    :param joints: list(), Joints to set translation on for the stretching.
    :param side: str(), 'left', 'right', or 'center'
    :return:
    '''
    root_name = nurbs_curve.root_name

    # create arclen node
    curve_info = nurbs_curve.create_child(DependNode,
                                          root_name='%s_curveInfo' % root_name,
                                          node_type='curveInfo')
    nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])

    # divide arc length evenly between the joint translate
    arm_length_divide = nurbs_curve.create_child(DependNode,
                                                 root_name='%s_curveLengthDivide' % root_name,
                                                 node_type='multiplyDivide')
    curve_info.plugs['arcLength'].connect_to(arm_length_divide.plugs['input1'].child(0))  # live arc length
    arm_length_divide.plugs['operation'].set_value(2)  # divide by
    arm_length_divide.plugs['input2X'].set_value(
        (len(joints) - 1) * -1 if side == 'right' else len(joints) - 1)  # divide by number of joints

    for i, joint in enumerate(joints):  # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086
        if i != 0 and i != len(joints) - 1:
            arm_length_divide.plugs['outputX'].connect_to(joint.plugs['t{0}'.format(env.aim_vector_axis)])

    arm_length_divide.plugs['outputX'].connect_to(joints[-1].plugs['t{0}'.format(env.aim_vector_axis)])

    return [curve_info, arm_length_divide]


def convert_ik_to_stretchable(start_handle, end_effector, joints, attribute_handle, stretch_plug=True):
    '''
    Converts your IK limb to be stretchable(joints, evenly spaced). This function also generates the custom attribute
    for blending on and off the stretching.
    :param start_handle: Root control which it will get the transforms data from.
    :param end_handle: Tip(AKA effector) control which it will get the transforms data from.
    :param joints: list(), Joints from your IK rig
    '''
    assert attribute_handle.owner

    part = attribute_handle.owner
    controller = part.controller

    assert part.get_root()
    auto_stretch_plug = attribute_handle.create_plug(
        'auto_stretch',
        at='double',
        dv=1.0,
        k=True,
        min=0,
        max=1
    )

    root = part.get_root()
    root.add_plugs(
        auto_stretch_plug,
        keyable=False,
    )


    stretch_multiply = start_handle.create_child(
        DependNode,
        node_type='multiplyDivide',
        root_name='{0}_stretch'.format(start_handle.root_name)
    )

    if stretch_plug:
        stretch_plug = attribute_handle.create_plug(
            'stretch',
            at='double',
            k=True,
            dv=0.0
        )
        root.add_plugs(
            stretch_plug
        )
        stretch_plug.connect_to(stretch_multiply.plugs['input1X'])

    if attribute_handle.side == 'right':
        stretch_multiply.plugs['input2X'].set_value(-1.0)

    joint_lengths = [j.plugs['t{0}'.format(env.aim_vector_axis)].get_value() for j in joints]
    default_total_length = abs(sum(joint_lengths))
    distance_between = create_distance_between(start_handle, end_effector)

    scale_divide = controller.create_object(
        DependNode,
        root_name='%s_stretchy_scale_divide' % part.root_name,
        node_type='multiplyDivide',
    )
    scale_divide.plugs['operation'].set_value(2)
    distance_between.plugs['distance'].connect_to(scale_divide.plugs['input1X'])
    part.scale_multiply_transform.plugs['scaleY'].connect_to(scale_divide.plugs['input2X'])
    scale_divide.plugs['input1Y'].set_value(default_total_length)
    #scale_divide.plugs['outputX'].connect_to(scale_divide.plugs['input2Y'])

    distance_between_halfs = []
    for joint in joints:
        distance_between_cond = start_handle.create_child(
            DependNode,
            node_type='condition',
            root_name='{0}_{1}_distance_between'.format(start_handle.root_name, joint.root_name),
            index=joint.index
        )
        scale_divide.plugs['outputX'].connect_to(distance_between_cond.plugs['colorIfTrueR'])
        scale_divide.plugs['outputX'].connect_to(distance_between_cond.plugs['firstTerm'])
        distance_between_cond.plugs['operation'].set_value(2)

        scale_divide.plugs['outputY'].connect_to(distance_between_cond.plugs['secondTerm'])
        scale_divide.plugs['outputY'].connect_to(distance_between_cond.plugs['colorIfFalseR'])

        stretchable_blend = start_handle.create_child(
            DependNode,
            node_type='blendColors',
            root_name='{0}_{1}_stretchable'.format(start_handle.root_name, joint.root_name),
            index=joint.index
        )
        auto_stretch_plug.connect_to(stretchable_blend.plugs['blender'])
        stretchable_blend.plugs['color2R'].set_value(default_total_length)
        distance_between_cond.plugs['outColorR'].connect_to(stretchable_blend.plugs['color1R'])
        extra_distance = start_handle.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_{1}_extra_distance'.format(start_handle.root_name, joint.root_name),
            index=joint.index
        )
        stretchable_blend.plugs['outputR'].connect_to(extra_distance.plugs['input1D'].element(0))  # live len
        extra_distance.plugs['operation'].set_value(2)  # subtract
        extra_distance.plugs['input1D'].element(1).set_value(default_total_length)  # default total len
        distance_between_half = start_handle.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_{1}_half_distance'.format(start_handle.root_name, joint.root_name),
            index=joint.index
        )
        extra_distance.plugs['output1D'].connect_to(distance_between_half.plugs['input1X'])  # live len - default total len
        distance_between_half.plugs['operation'].set_value(2)  # divide by
        distance_between_half.plugs['input2X'].set_value(len(joints) * (-1 if start_handle.side == 'right' else 1))
        distance_between_halfs.append(distance_between_half)
    for i, ik_joint in enumerate(joints):
        default_length = ik_joint.plugs['t{0}'.format(env.aim_vector_axis)].get_value()
        add_distance = start_handle.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_add_distance'.format(start_handle.root_name),
            index=i
        )

        add_distance.plugs['operation'].set_value(1)  # add
        distance_between_halfs[i].plugs['outputX'].connect_to(add_distance.plugs['input1D'].element(0))
        add_distance.plugs['input1D'].element(1).set_value(default_length)
        stretch_multiply.plugs['outputX'].connect_to(add_distance.plugs['input1D'].element(2)) # add manual stretch
        add_distance.plugs['output1D'].connect_to((ik_joint.plugs['t{0}'.format(env.aim_vector_axis)]))


def create_distance_between(handle_a, handle_b, root_name=None, index=None, parent=None):
    if not parent:
        parent = handle_a
    if not root_name:
        root_name = handle_a.root_name
    if root_name and index:
        root_name = '{0}_{1:03d}'.format(root_name, index)

    distance_between_node = parent.create_child(DependNode,
                                             node_type='distanceBetween',
                                             root_name='%s_distanceBetween' % root_name)
    for handle, plug in zip((handle_a, handle_b), ('point1', 'point2')):
        pos = handle.create_child(Locator,
                                  root_name='%s_distancePosition%s' % (root_name, plug))
        pos.plugs['visibility'].set_value(False)
        pos.plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs[plug])
    return distance_between_node

