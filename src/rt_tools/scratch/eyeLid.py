import maya.cmds as mc

eye_number_dialog = mc.promptDialog(
    title='Eye Prefix',
			message='Enter the Prefix Name:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel'
			)

if eye_number_dialog == 'OK':
	print mc.promptDialog(query=True, text=True)
	desired_prefix = mc.promptDialog(query=True, text=True)


eyeball_geo_name_dialog = mc.promptDialog(
			title='Eye Geo',
			message='Enter the name of the eye geo:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel'
			)

if eyeball_geo_name_dialog == 'OK':
	print mc.promptDialog(query=True, text=True)
	eyeball_center = mc.promptDialog(query=True, text=True)
# USER INPUT REQUIRED: provide desired prefix for eye rig


def flip_dict_keys_vals(original_dict):
    """
    Flip a dictionary's keys and values
    :param original_dict: Dictionary to swap the keys and values of
    :return: dictionary of flipped keys and values
    """
    return dict([(value, key) for key, value in original_dict.items()])


def object_vertical_prefix(obj):
    """
    Determine the object's prefix by it's xform position and compare it with start_point and end_point
    :param obj: object to get and compare position from
    :return: string of the position prefix, or Error if no position found
    """
    x_pos, y_pos, _ = mc.xform(obj, query=True, worldSpace=True, translation=True)
    if x_pos == start_point or x_pos == end_point:
        return 'Mid'
    elif y_pos > mid_y:
        return 'Upr'
    elif y_pos < mid_y:
        return 'Lwr'
    else:
        raise Exception(obj + ' not in upper or lower lid.')


def create_eyelid_joints(vert_list, prefix='temp_name'):
    """
    Create joints on each vertex in the given vertex list and prepend with the given prefix
    :param vert_list: list of vertices
    :param prefix: prefix for each joint's name
    :return: list of joints
    """
    lid_jnts = []
    vert_dict = {}

    for vert in vert_list:
        x_val, _, _ = mc.pointPosition(vert)
        vert_dict[vert] = x_val
    x_val_dict = flip_dict_keys_vals(vert_dict)

    grp_vertical_prefix = object_vertical_prefix(x_val_dict.values()[1])
    grp_name = prefix + 'Eyelid_' + grp_vertical_prefix + '_jnt_grp'
    main_grp = mc.group(name=grp_name, empty=True)

    for index, x_val in enumerate(sorted(x_val_dict.keys())):
        ind = '%0.3d' % int(index + 1)
        vert = x_val_dict[x_val]

        eyelid_prefix = prefix + 'Eyelid_' + grp_vertical_prefix
        center_jnt_name = eyelid_prefix + '_C_{}_jnt'.format(ind)
        center_jnt = mc.joint(name=center_jnt_name)
        mc.xform(center_jnt, worldSpace=True, translation=center_pos)

        # get vert position
        x_pos, y_pos, z_pos = mc.xform(vert, query=True, worldSpace=True, translation=True)

        # create eye joint and move to vert position
        jnt_name = eyelid_prefix + '_{}_jnt'.format(ind)
        jnt = mc.joint(name=jnt_name)
        mc.xform(jnt, worldSpace=True, translation=[x_pos, y_pos, z_pos])

        # TODO: Confirm with Sean P joint orient/joint axis/other joint settings
        mc.joint(
            center_jnt,
            edit=True,
            orientJoint='xyz',
            secondaryAxisOrient='yup',
            children=True,
            zeroScaleOrient=True
        )
        if main_grp not in mc.listRelatives(center_jnt, parent=True):
            mc.parent(center_jnt, main_grp)

        lid_jnts.append(jnt)

    return lid_jnts


def create_jnt_locators(joint_list, prefix='temp_name'):
    """
    Create locators on each joint in the given joints list and prepend with the given prefix
    :param joint_list: list of joints
    :param prefix: prefix for each locator's name
    :return: list of locators
    """
    loc_list = []
    obj_prefix = prefix + 'Eyelid_' + object_vertical_prefix(joint_list[1])
    grp_name = obj_prefix + '_loc_grp'
    main_grp = mc.group(name=grp_name, empty=True)

    for index, jnt in enumerate(joint_list):
        ind = '%0.3d' % int(index + 1)
        loc_name = obj_prefix + '_loc_' + ind
        loc = mc.spaceLocator(name=loc_name)[0]
        position = mc.xform(jnt, query=True, worldSpace=True, translation=True)
        mc.xform(loc, worldSpace=True, translation=position)

        jnt_parent = mc.listRelatives(jnt, parent=True)[0]

        # TODO: confirm w/Sean P desired aim constraint settings
        mc.aimConstraint(
            loc,
            jnt_parent,
            maintainOffset=True,
            weight=1.0,
            aimVector=(1.0, 0.0, 0.0),
            upVector=(0.0, 1.0, 0.0),
            worldUpType='object',
            worldUpObject=aim_loc
        )
        mc.parent(loc, main_grp)
        loc_list.append(loc)

    return loc_list


def create_curve(vert_list, curv_deg=1, curv_name='temporary_name_lid'):
    """
    Create a nurbsCurve from the given vertex list, degree and name
    :param vert_list: vertex list to get positions from using pointPosition
    :param curv_deg: curve degree, default is 1
    :param curv_name: name to give curve
    :return: string of the curve's transform name suffixed with '_crv'
    """
    curv_pnts = [mc.pointPosition(pnt) for pnt in vert_list]
    curv = mc.curve(name=curv_name + '_crv', degree=curv_deg, point=sorted(curv_pnts))
    return curv


def get_shape(obj):
    """
    Get the object's shape(s)
    :param obj: object to get the shape from
    :return: object's shape, raise Exception if more than one shape / no shapes found
    """
    shapes_list = mc.listRelatives(obj, shapes=True)
    if len(shapes_list) > 1:
        raise Exception (obj + ' has more than one shape! ' + shapes_list)
    elif len(shapes_list) == 1:
        return shapes_list[0]
    else:
        raise Exception('No shapes found for ' + obj)


def loc_point_on_curv(curv, loc_list):
    """
    Connect the given curve to each locator so the curve drives the locator's translation
    :param curv: curve to drive the locators' translation
    :param loc_list: list of locators
    :return: None
    """
    curv_shp = curv if mc.objectType(curv, isType='nurbsCurve') else get_shape(curv)
    for index, loc in enumerate(loc_list):
        pci_node = mc.createNode('pointOnCurveInfo', name=loc + '_pci')
        mc.setAttr(pci_node + '.parameter', index)
        mc.connectAttr(curv_shp + '.worldSpace', pci_node + '.inputCurve')
        mc.connectAttr(pci_node + '.result.position', loc + '.translate')


def rebuild_curve_spans(curv, spans_num):
    """
    Rebuilds and replaces curve with the given spans
    :param curv: Curve to rebuild and replace
    :param spans_num: number of spans
    :return: rebuilt curve with adjusted spans
    """
    mc.rebuildCurve(
        curv,
        constructionHistory=False,
        replaceOriginal=True,
        endKnots=1,
        keepRange=2,  # 2 - re-paramaterize to number of given spans
        spans=spans_num,
        degree=3
    )
    return curv

# converts user's selection to vertices
mc.ConvertSelectionToVertices()

# get selected vertices and flatten the list
vert_selection = mc.ls(selection=True, flatten=True)

upr_lid = []
lwr_lid = []
start_point = mc.pointPosition(vert_selection[0])[0]
end_point = mc.pointPosition(vert_selection[0])[0]

# Determine the middle of each axis from vert_selection
vert_x_positions = [mc.pointPosition(pnt)[0] for pnt in vert_selection]
vert_y_positions = [mc.pointPosition(pnt)[1] for pnt in vert_selection]
vert_z_positions = [mc.pointPosition(pnt)[2] for pnt in vert_selection]
mid_x = (max(vert_x_positions) + min(vert_x_positions)) / 2.0
mid_y = (max(vert_y_positions) + min(vert_y_positions)) / 2.0
mid_z = (max(vert_z_positions) + min(vert_z_positions)) / 2.0

# Determine start and end point on the x axis from vert_selection (L/R eye corners)
for vert in vert_selection:
    x_pos = mc.pointPosition(vert)[0]
    if x_pos > end_point:
        end_point = x_pos
    if x_pos < start_point:
        start_point = x_pos

# Determine which vertex belongs in the upper and lowr lid list
for vert in vert_selection:
    x_val, y_val, _ = mc.pointPosition(vert)
    if y_val > mid_y or x_val == start_point or x_val == end_point:
        upr_lid.append(vert)
    if y_val < mid_y or x_val == start_point or x_val == end_point:
        lwr_lid.append(vert)
    if vert not in upr_lid and vert not in lwr_lid:
        raise Exception(vert + ' not in upr or lwr lid!')

# Get center position and create a locator on it
center_pos = mc.xform(eyeball_center, q=True, translation=True, ws=True)

# create center locator and put it at approx eyeball center
center_loc = mc.spaceLocator(name=desired_prefix + 'center_loc')[0]
mc.xform(center_loc, translation=(center_pos[0], center_pos[1], center_pos[2]))

# create eye joints
left_upr_lid_jnts = create_eyelid_joints(upr_lid, prefix=desired_prefix)
left_lwr_lid_jnts = create_eyelid_joints(lwr_lid, prefix=desired_prefix)

# create aim locator
aim_loc_pos = [mid_x, max(vert_y_positions) * 1.2, (mid_z * 0.75)]
aim_loc = mc.spaceLocator(name=desired_prefix + 'aim_loc')[0]
mc.xform(aim_loc, worldSpace=True, translation=aim_loc_pos)

# create locators for lid joints
upr_lid_locs = create_jnt_locators(left_upr_lid_jnts, prefix=desired_prefix)
lwr_lid_locs = create_jnt_locators(left_lwr_lid_jnts, prefix=desired_prefix)

# create driver curve ("high res" cubic curve)
upr_lid_driver = create_curve(upr_lid, curv_deg=3, curv_name=desired_prefix + 'upr_lid_driver')
lwr_lid_driver = create_curve(lwr_lid, curv_deg=3, curv_name=desired_prefix + 'lwr_lid_driver')

# create wire curve ("low res" linear curve)
upr_lid_wire = create_curve(upr_lid, curv_deg=1, curv_name=desired_prefix + 'upr_lid_wire')
lwr_lid_wire = create_curve(lwr_lid, curv_deg=1, curv_name=desired_prefix + 'lwr_lid_wire')

# group driver and wire curves
mc.group([upr_lid_driver, upr_lid_wire, lwr_lid_driver, lwr_lid_wire], name=desired_prefix + 'eyelid_crv_util_grp')

# checks and rebuilds the driver curve if it doesn't have the same spans as the wire curve
if mc.getAttr(lwr_lid_wire + '.spans') != mc.getAttr(lwr_lid_driver + '.spans'):
    lwr_lid_driver = rebuild_curve_spans(lwr_lid_driver, mc.getAttr(lwr_lid_wire + '.spans'))
if mc.getAttr(upr_lid_wire + '.spans') != mc.getAttr(upr_lid_driver + '.spans'):
    upr_lid_driver = rebuild_curve_spans(upr_lid_driver, mc.getAttr(upr_lid_wire + '.spans'))

# connect driver curves to upr/lwr lid locators (so curve moves locators)
loc_point_on_curv(upr_lid_driver, upr_lid_locs)
loc_point_on_curv(lwr_lid_driver, lwr_lid_locs)
