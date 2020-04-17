"""Alternative head squash that is automatic to all conditions"""

# define standard imports
import time

# define maya imports
import maya.cmds as cmds

# define local imports
import icon_api.node as i_node


# define private variables
__author__ = "Alison Chan"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Michael Taylor", "Alison Chan"]
__license__ = "ICON LISENCE"
__version__ = "1.0.0"
__maintainer__ = "Alison Chan"
__email__ = "alison@iconcreativestudio.com"
__status__ = "Production"


def make_icon_controls(control_list, control_pos, ctrl_colour, ctrl_shape):
    """
    Create icon controllers based on the arguments given
    :param control_list: <list> list of controllers to make.
    :param control_pos: <str> position of the control
    :param ctrl_colour: <str>
    :param ctrl_shape: <str>
    :return: <bool> True for success. <bool> False for failure.
    """
    for ctrl in control_list:
        i_node.create("control", name=ctrl, control_type=ctrl_shape, with_gimbal=False, color=ctrl_colour, size=5)
        ctrl_offset_group = ctrl + '_Ctrl_Offset_Grp'
        cmds.xform(ctrl_offset_group, ws=True, t=control_pos)

        # parent this correctly
        if cmds.objExists('Ctrl_Grp'):
            cmds.parent(ctrl_offset_group, 'Ctrl_Grp')
    return True


def create_squash(selected=[], ignore_selection_warning=0):
    """
    Creates squash deformation on selected.
    :param selected: <list> objects to affect.
    :return: <bool> True for success. <bool> False for failure.
    """
    # verify polygon vertice selection only
    if not ignore_selection_warning:
        if selected:
            selected = cmds.filterExpand(selected, sm=(31), ex=1)
        if not selected:
            selected = cmds.filterExpand(sm=(31), ex=1)
        if not selected:
            cmds.warning('[Head Squash] :: Please select character head polygon vertices.')
            return False

    non_linear_def = (('Head_Squash', 'squash'),
                      ('Head_Flare', 'flare'),
                      ('Head_Twist', 'twist'),
                      ('Head_BendX', 'bend'),
                      ('Head_BendZ', 'bend'))

    # check if names exist
    if any([cmds.objExists(x[0]) for x in non_linear_def]):
        cmds.warning('[Head Squash] :: Components already exist in scene.')
        return False

    # get bottom and top bounding box positions
    pivot = cmds.exactWorldBoundingBox(selected)
    top_pos = ((pivot[0] + pivot[3]) / 2, pivot[4], (pivot[2] + pivot[5]) / 2)
    bot_pos = ((pivot[0] + pivot[3]) / 2, pivot[1], (pivot[2] + pivot[5]) / 2)

    print('[Head Squash] :: Starting head squash.')
    start_time = time.time()

    deformer_list = []
    deformer_handle_list = []

    for lin in non_linear_def:
        # make and rename the non linears
        deformer_name, deformer_type = lin

        linear_parts = cmds.nonLinear(selected, name=deformer_name, type=deformer_type)
        lin_def = cmds.rename(linear_parts[0], deformer_name)
        lin_handle = cmds.rename(linear_parts[1], deformer_name + "_Handle")

        deformer_list.append(lin_def)
        deformer_handle_list.append(lin_handle)

        # move and set attributes for the non-linears
        cmds.xform(lin_handle, ws=True, t=bot_pos)
        cmds.setAttr(lin_def + ".lowBound", 0)
        cmds.setAttr(lin_def + ".highBound", 2)

    # create the main head controller
    squash_lin_ctrl_names = ["C_Main_Head_Squash"]
    ctrl_colour = "watermelon"
    ctrl_shape = "3d Sphere"
    make_icon_controls(squash_lin_ctrl_names, top_pos, ctrl_colour, ctrl_shape)

    # connect deformer bits
    head_squash = deformer_list[0]
    head_flare = deformer_list[1]
    head_twist = deformer_list[2]
    head_bend_x = deformer_list[3]
    head_bend_z = deformer_list[4]

    # rotate bend Z handle
    cmds.setAttr(deformer_handle_list[4] + ".rotateY", -90)

    squash_md = cmds.createNode('multiplyDivide', n="Head_Squash_MD")
    twist_md = cmds.createNode('multiplyDivide', n="Head_Twist_MD")
    bend_md = cmds.createNode('multiplyDivide', n="Head_Bend_MD")

    # head controller name:
    head_squash_control = 'C_Main_Head_Squash_Ctrl'
    head_utility_grp = 'Alt_Head_Squash_Deformers_Grp'

    # connect MD nodes
    cmds.connectAttr(head_squash_control + ".translateY", squash_md + ".input1Y")
    cmds.connectAttr(squash_md + ".outputY", head_squash + ".factor")
    cmds.setAttr(squash_md + ".input2Y", 0.025)

    cmds.connectAttr(head_squash_control + ".rotateY", twist_md + ".input1Y")
    cmds.connectAttr(twist_md + ".outputY", head_twist + ".endAngle")
    cmds.setAttr(twist_md + ".input2Y", -1)

    cmds.connectAttr(head_squash_control + ".translateX", bend_md + ".input1X")
    cmds.connectAttr(bend_md + ".outputX", head_bend_x + ".curvature")
    cmds.connectAttr(head_squash_control + ".translateZ", bend_md + ".input1Z")
    cmds.connectAttr(bend_md + ".outputZ", head_bend_z + ".curvature")

    cmds.connectAttr(head_squash_control + ".scaleX", head_flare + ".endFlareX")
    cmds.connectAttr(head_squash_control + ".scaleZ", head_flare + ".endFlareZ")

    # group everything
    cmds.group(deformer_handle_list, n=head_utility_grp)
    if cmds.objExists('Utility_Grp'):
        cmds.parent(head_utility_grp, 'Utility_Grp')

    print('[Head Squash] :: Completed in {} seconds.'.format(time.time() - start_time))
    return True
