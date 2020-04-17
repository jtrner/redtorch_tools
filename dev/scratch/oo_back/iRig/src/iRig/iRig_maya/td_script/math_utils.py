"""Math utility function modules for rigging setups in Maya."""

# define standard modules
import math
import time
import re

# define maya imports
from maya import OpenMaya as api0
from maya import cmds

# import custom modules
from rig_math.vector import Vector

# import local modules
import skincluster_utils

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "IL"
__version__ = "1.0.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"

get_position = lambda x: cmds.xform(x, q=1, ws=1, t=1)


def get_selected_bbox_center():
    """
    Returns the center of selection.
    :return: <float>, <float>, <float>
    """
    min_vec = api0.MVector()
    max_vec = api0.MVector()
    min_vec.x, min_vec.y, min_vec.z, max_vec.x, max_vec.y, max_vec.z = cmds.exactWorldBoundingBox()

    local_center = (max_vec - min_vec) / 2
    center_bbox = local_center + min_vec
    return center_bbox.x, center_bbox.y, center_bbox.z


def get_bbox_center(object_name=""):
    """
    Returns the bounding box center using <MVector> class objects.
    :param object_name: <str> objecvt name to grab bounding box attribute from.
    :return: <MVector> list.
    """
    bbox_min = cmds.getAttr(object_name + '.boundingBoxMin')[0]
    bbox_max = cmds.getAttr(object_name + '.boundingBoxMax')[0]
    min_vec = api0.MVector(bbox_min)
    max_vec = api0.MVector(bbox_max)
    return ((max_vec - min_vec) / 2) + min_vec


def object_bbox(object_name=""):
    """
    Get the object bounding box.
    :param object_name: <str> objects' name.
    :return: <tuple> Min, <tuple> Max
    """
    # Get the shape directly below the selected transform.
    mesh_fn = skincluster_utils.get_node_fn(object_name)
    m_box = mesh_fn.boundingBox()
    min_point = m_box.min()
    max_point = m_box.max()
    return (min_point.x, min_point.y, min_point.z), (max_point.x, max_point.y, max_point.z)


def bounding_box(object_name="", get_center=False, get_top_y=False, get_btm_y=False,
                 get_pos_z=False, get_neg_z=False, get_pos_x=False, get_neg_x=False, xyz=False):
    """
    Returns the bounding box center using <MVector> class objects.
    :param object_name: <str> objecvt name to grab bounding box attribute from.
    :param get_top_y: <bool> returns the center of the top bounding box of an object.
    :param get_btm_y: <bool> returns the bottom of the y axis against the center object.
    :param get_pos_z: <bool> returns the forward z axis against the center object.
    :param get_neg_z: <bool> returns the bakward z axis against the center object.
    :param get_pos_x: <bool> returns the left x axis against the center object.
    :param get_neg_x: <bool> returns the right x axis against the center object.
    :param get_center: <bool> returns the bounding box center of the object.
    :param xyz: <bool> return a list of float values instead of MVector class.
    :return: <bool> False for failure, <MVector> list if successful.
    """
    if not object_name:
        return False

    # define variables
    min_vec = api0.MVector()
    max_vec = api0.MVector()

    if isinstance(object_name, (str, unicode)):
        bbox_min = cmds.getAttr(object_name + '.boundingBoxMin')[0]
        bbox_max = cmds.getAttr(object_name + '.boundingBoxMax')[0]
    if isinstance(object_name, (list, tuple)):
        bbox = cmds.exactWorldBoundingBox(object_name)
        bbox_min = bbox[0], bbox[1], bbox[2]
        bbox_max = bbox[3], bbox[4], bbox[5]
    else:
        return False

    # assign <MVector> class attributes
    min_vec.x = bbox_min[0]
    min_vec.y = bbox_min[1]
    min_vec.z = bbox_min[2]

    max_vec.x = bbox_max[0]
    max_vec.y = bbox_max[1]
    max_vec.z = bbox_max[2]

    # calculate the bounding box origin in world space
    local_center = (max_vec - min_vec) / 2
    center_bbox = local_center + min_vec
    if get_center:
        if xyz:
            center_bbox.x, center_bbox.y, center_bbox.z
        return center_bbox

    # return data through specified instructions
    if get_top_y:
        center_bbox.y = local_center.y + center_bbox.y
    if get_btm_y:
        center_bbox.y = center_bbox.y - local_center.y
    if get_pos_z:
        center_bbox.z = local_center.z + center_bbox.z
    if get_neg_z:
        center_bbox.z = center_bbox.z - local_center.z
    if get_pos_x:
        center_bbox.x = local_center.x + center_bbox.x
    if get_neg_x:
        center_bbox.z = center_bbox.x - local_center.x
    if xyz:
        return center_bbox.x, center_bbox.y, center_bbox.z
    return center_bbox


def get_vector_distance(start_obj="", end_obj=""):
    """
    Grabs the vector distance between the start object and the end object.
    :param start_obj: <str> start object to get position from.
    :param end_obj: <str> end object to get position from.
    :returns: <float> distance between the two objects.
    """
    start_vector = get_position(start_obj)
    end_vector = get_position(end_obj)
    x = (end_vector[0] - start_vector[0]) ** 2
    y = (end_vector[1] - start_vector[1]) ** 2
    z = (end_vector[2] - start_vector[2]) ** 2
    return (x + y + z) ** 0.5


def get_perfect_position_distance(start_obj="", end_obj="", query_obj=""):
    """
    From the transforms specified, get the unit division between start and end.
    :param start_obj: <str> The start object transform.
    :param end_obj:  <str> The end object transform.
    :returns: <float> distance division.
    """
    get_top_distance = get_vector_distance(query_obj, end_obj)
    get_btm_distance = get_vector_distance(query_obj, start_obj)
    total_distance = get_top_distance + get_btm_distance
    return (get_top_distance / total_distance, get_btm_distance / total_distance)


def do_point_constraint_variable_division(start_obj="", end_obj="", middle_objects=[]):
    """
    From the transforms specified, get the unit division to position the point constraints perfectly..
    :param start_obj: <str> The start object transform.
    :param end_obj:  <str> The end object transform.
    :param middle_objects: <list> iterate through this list of objects to get the perfect point constraint position.
    :returns: <float> distance division.
    """
    if not cmds.objExists(start_obj) or not cmds.objExists(end_obj) or not all(map(cmds.objExists, middle_objects)):
        return False

    for mid_obj in middle_objects:
        numerator, denominator = get_perfect_position_distance(start_obj, end_obj, mid_obj)
        print("[Unit Position] :: {}, {}/{}".format(mid_obj, numerator, denominator))
        loc_cnst = cmds.pointConstraint([start_obj, end_obj, mid_obj])[0]
        loc_weights = cmds.listAttr(loc_cnst, ud=1)[1:]

        # set the numerator and the denominator as constraint weights
        cmds.setAttr(loc_cnst + '.{}'.format(loc_weights[0]), numerator)
        cmds.setAttr(loc_cnst + '.{}'.format(loc_weights[1]), denominator)
    return True


def do_point_constraint_equal_division(start_loc="", end_loc="", num_locs=4):
    """
    Divides the space between the two locators using pointConstraints.
    :param start_loc: <str> The start locator transform object.
    :param end_loc:  <str> The end locator transform object.
    :param num_locs: <int> The number of locators to build in between the two locator transforms.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not cmds.objExists(start_loc) and not cmds.objExists(end_loc):
        return False
    locator_str = start_loc + "_Mid_{}_Loc"

    step_numerator = 1.0 / (float(num_locs) + 1.0)
    numerator = 0.0
    denominator = 0.0
    for idx in range(num_locs):
        numerator += step_numerator
        denominator = 1.0 - numerator
        print('[Step, {}] :: {}/{}'.format(step_numerator, numerator, denominator))
        locator_name = locator_str.format(idx)

        # delete if this locator exists
        if cmds.objExists(locator_name):
            cmds.delete(locator_name)

        cmds.spaceLocator(name=locator_name)
        loc_cnst = cmds.pointConstraint([start_loc, end_loc, locator_name])[0]
        loc_weights = cmds.listAttr(loc_cnst, ud=1)[1:]

        cmds.setAttr(loc_cnst + '.{}'.format(loc_weights[0]), numerator)
        cmds.setAttr(loc_cnst + '.{}'.format(loc_weights[1]), denominator)
    return True


def util_get_node(node, ikEffector=0, ikHandle=0, curve=0, upstream=0, downstream=0):
    """
    Gets the MFnIkEffector from the MObject specified.
    :param node: <MObject> node to start itrative lookup from.
    :param ikEffector: <bool> Finds the ikEffector.
    :param ikHandle: <bool> Finds the ikHandle.
    :return: <MFnIkEffector> if successful, <bool> False if fail.
    """
    if downstream:
        it_params = [node, api0.MItDependencyGraph.kDownstream, api0.MItDependencyGraph.kDepthFirst, api0.MItDependencyGraph.kPlugLevel]
    if upstream:
        it_params = [node, api0.MItDependencyGraph.kUpstream, api0.MItDependencyGraph.kBreadthFirst, api0.MItDependencyGraph.kPlugLevel]
    node_fn = False
    it_dg = api0.MItDependencyGraph(*it_params)
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        if cur_item.hasFn(api0.MFn.kIkEffector) and ikEffector:
            return cur_item
        if cur_item.hasFn(api0.MFn.kIkHandle) and ikHandle:
            return cur_item
        if cur_item.hasFn(api0.MFn.kNurbsCurve) and curve:
            return cur_item
        it_dg.next()
    return node_fn


def util_get_m_object(obj_name=""):
    """
    Gets the MObject from the string specified.
    :param node: <str> name of node.
    :return: <MObject> if successful, <bool> False if fail.
    """
    if not obj_name:
        return False
    m_obj = api0.MObject()
    m_list = api0.MSelectionList()
    api0.MGlobal.getSelectionListByName(obj_name, m_list)
    m_list.getDependNode(0, m_obj);
    return m_obj


def util_connect_attr(output_attr, input_attr):
    """
    Connect the attributes
    :param output_attr: <str> the output attriubte to connect to the input attribute.
    :param input_attr: <str> the input attribute to be connected into.
    """
    if not any([output_attr, input_attr]):
        return False
    if not cmds.isConnected(output_attr, input_attr, ignoreUnitConversion=1):
        cmds.connectAttr(output_attr, input_attr, f=1)
    return True


def util_create_node(node_name, node_type):
    """
    Create the node.
    :param node_type: <str> the type of node to create.
    :param node_name: <str> name this new node.
    """
    if not cmds.objExists(node_name):
        cmds.createNode(node_type, name=node_name)
    return True


def util_set_attr(attr, value):
    """
    set value to this attribute string.
    :param attr: <str> attribute string eg. transform1.translateY
    :param value: <int> value to set the attribute to.
    """
    current_val = cmds.getAttr(attr)
    if current_val != value:
        confirm_connection = cmds.listConnections(attr, s=1, d=0, plugs=1)
        if confirm_connection:
            return False
        cmds.setAttr(attr, value)
    return True


def util_get_position(obj_str=""):
    """
    Gets the world-space position.
    :param obj_str: transform object.
    """
    return cmds.xform(obj_str, ws=1, t=1, q=1)


def util_load_plugin(plug_name=""):
    """
    Loads the plugin.
    :param plug_name: <str> loads this plugin.
    :returns: <bool> plugin is loaded.
    """
    if not cmds.pluginInfo('matrixNodes', l=1, q=1):
        cmds.loadPlugin('matrixNodes', qt=1)
    return cmds.pluginInfo('matrixNodes', l=1, q=1)


def create_rivet_plane(name='', connect_scale=False, plane_history=0):
    """
    Creates a rivet plane with rivet matrix setup.
    :param name: <str> give a base name for this rivet setup.
    :param connect_scale: <bool> connects the scale vector to the locator.
    :returns: (<str> locator name, <str> plane surface name)
    """
    util_load_plugin('matrixNodes')

    surface_name = name + '_Rivet_Srf'
    posinfo_name = name + '_Rivet_POSI'
    vector_name = name + '_Vector'
    fourbyfour_name = name + '_4By4_Matrix'
    decompose_name = name + '_DecompMatrix'
    locator_name = name + '_LocShape'

    if not cmds.objExists(surface_name):
        cmds.nurbsPlane(name=surface_name, p=(0, 0, 0), ax=(0, 1, 0), w=1, lr=1, d=3, u=0.5, v=0.5, ch=plane_history)

    util_create_node(posinfo_name, 'pointOnSurfaceInfo')
    util_create_node(vector_name, 'vectorProduct')
    util_create_node(fourbyfour_name, 'fourByFourMatrix')
    util_create_node(decompose_name, 'decomposeMatrix')
    util_create_node(locator_name, 'locator')

    # set attributes
    util_set_attr(posinfo_name + '.parameterU', 0.5)
    util_set_attr(posinfo_name + '.parameterV', 0.5)
    util_set_attr(vector_name + '.operation', 2)

    # connnect attributes
    util_connect_attr(surface_name + '.worldSpace[0]', posinfo_name + '.inputSurface')
    for out_attr, in_attr in zip(['.positionX', '.positionY', '.positionZ'], ['.in30', '.in31', '.in32']):
        util_connect_attr(posinfo_name + out_attr, fourbyfour_name + in_attr)
    for out_attr, in_attr in zip(['.normalX', '.normalY', '.normalZ'], ['.in00', '.in01', '.in02']):
        util_connect_attr(posinfo_name + out_attr, fourbyfour_name + in_attr)
    for out_attr, in_attr in zip(['.tangentVx', '.tangentVy', '.tangentVz'], ['.in10', '.in11', '.in12']):
        util_connect_attr(posinfo_name + out_attr, fourbyfour_name + in_attr)
    util_connect_attr(posinfo_name + '.normal', vector_name + '.input1')
    util_connect_attr(posinfo_name + '.tangentV', vector_name + '.input2')
    for out_attr, in_attr in zip(['.outputX', '.outputY', '.outputZ'], ['.in20', '.in21', '.in22']):
        util_connect_attr(vector_name + out_attr, fourbyfour_name + in_attr)
    util_connect_attr(fourbyfour_name + '.output', decompose_name + '.inputMatrix')

    locator_transform_name = locator_name.replace('Shape', '')
    util_connect_attr(decompose_name + '.outputTranslate', locator_transform_name + '.translate')
    util_connect_attr(decompose_name + '.outputRotate', locator_transform_name + '.rotate')
    if connect_scale:
        util_connect_attr(decompose_name + '.outputScale', locator_transform_name + '.scale')
    return (locator_transform_name, surface_name)


def do_rotation_variable_division(start_obj="", end_obj="", middle_objects=[], construct_nodes=False):
    """
    From the transforms specified, get the unit division of orientation percentage based on distance between start and end.
    :param start_obj: <str> The start object transform.
    :param end_obj:  <str> The end object transform.
    :param construct_nodes: <bool> Construct the nodes to supplement the math calculated for rotational data.
    :param middle_objects: <list> iterate through this list of objects to get the perfect point constraint position.
    :returns: <float> distance division.
    """
    if not all(map(cmds.objExists, middle_objects + [start_obj, end_obj])):
        return False

    # initialize functions
    get_connection_input = lambda pma_name: 'input3D[{}]'.format(len(cmds.ls("{}.input3D[*]".format(pma_name))) + 1)

    # initialize the multiplier
    falloff_attr = 'rotationFalloff'
    driver_attr = start_obj + '.' + falloff_attr
    rotate_attr = start_obj + '.rotate'
    multiplier_node = start_obj + '_MultRotate'

    if not cmds.objExists(driver_attr):
        cmds.addAttr(start_obj, ln=falloff_attr, min=0.0, max=1.0, dv=1.0, at='float', k=1)
        cmds.setAttr(driver_attr, k=1)

    # create multiplyDivide node
    util_create_node('multiplyDivide', multiplier_node)
    util_connect_attr(rotate_attr, multiplier_node + '.input1')
    util_connect_attr(driver_attr, multiplier_node + '.input2X')
    util_connect_attr(driver_attr, multiplier_node + '.input2Y')
    util_connect_attr(driver_attr, multiplier_node + '.input2Z')

    # initialize the plusMinusAverage nodes
    avg_data = {}
    for idx, ea_obj in enumerate(middle_objects):
        pma_name = ea_obj + '_AddRotations'
        avg_data[ea_obj] = {'plusMinusAverage': pma_name}
        pma_output = '{}.output3D'.format(pma_name)
        obj_input = '{}.rotate'.format(ea_obj)
        ea_multiplier_node = '{}_Multiplier{}'.format(start_obj, idx)

        util_create_node('plusMinusAverage', pma_name)
        # add the multiplier
        util_create_node('multiplyDivide', ea_multiplier_node)
        util_connect_attr(multiplier_node + '.output', ea_multiplier_node + '.input1')
        util_connect_attr(pma_output, obj_input)

        # find out which connections have been made so far
        avg_data[ea_obj] = {'plusMinusAverage': pma_name,
                            'input3D': get_connection_input(pma_name),
                            'multiplyDivide': ea_multiplier_node,
                            }

    # begin the node math
    start_position = get_position(start_obj)
    end_position = get_position(end_obj)
    total_objects = len(middle_objects)
    for index, mid_obj in enumerate(middle_objects):
        data = avg_data[mid_obj]
        if index > 0:
            data['input3D'] = pma_input_idx
        get_top_distance = get_vector_distance(start_obj, mid_obj)
        get_btm_distance = get_vector_distance(end_obj, mid_obj)
        total_distance = get_top_distance + get_btm_distance
        if index < total_objects:
            # skip the last calculation
            bottom_multiplier = (get_btm_distance / total_distance)

            # set and connect the information
            mult_input_2x = data['multiplyDivide'] + '.input2X'
            mult_input_2y = data['multiplyDivide'] + '.input2Y'
            mult_input_2z = data['multiplyDivide'] + '.input2Z'
            util_set_attr(mult_input_2x, bottom_multiplier)
            util_set_attr(mult_input_2y, bottom_multiplier)
            util_set_attr(mult_input_2z, bottom_multiplier)

            mult_output_attr = '{}.output'.format(data['multiplyDivide'])
            pma_input_attr = '{}.{}'.format(data['plusMinusAverage'], data['input3D'])
            util_connect_attr(mult_output_attr, pma_input_attr)
            pma_input_idx = get_connection_input(pma_name)
            print(mid_obj, bottom_multiplier)
    return True


def calculate_pole_vector_position(position_1, position_2, position_3, distance=10.0):
    """
    Calculates the poleVector position from the three positions specified.
    :param position_1: <list> translation values of the first transform.
    :param position_2: <list> translation values of the second transform.
    :param position_3: <list> translation values of the third transform.
    :param distance: <float> the distance from the second transfrom to create the translation values to.
    :returns: <list> world space position.
    """

    position_1 = Vector(position_1)
    position_2 = Vector(position_2)
    position_3 = Vector(position_3)
    mag_1 = (position_2 - position_1).mag()
    mag_2 = (position_3 - position_2).mag()
    total_mag = mag_1 + mag_2

    if total_mag == 0.0:
        cmds.warning('Warning: the second joint had no angle. unable to calculate pole position')
        return position_2

    fraction_1 = mag_1 / total_mag
    center_position = position_1 + (position_3 - position_1) * fraction_1
    angle_vector = (position_2 - center_position)
    angle_mag = angle_vector.mag()
    if angle_mag == 0.0:
        cmds.warning('Warning: the second joint had no angle. unable to calculate pole position')
        return position_2

    pole_offset = angle_vector.normalize() * distance
    pole_position = position_2 + pole_offset
    return pole_position.data


def pole_vector_locator(start, mid, end):
    """
    Creates a Pole Vector Locator.
    :returns: <str> locator.
    """
    position = calculate_pole_vector_position(*map(util_get_position, [start, mid, end]))
    locator = cmds.spaceLocator(name='PoleVector')[0]
    cmds.setAttr(locator + '.t', *position)
    return locator



def setup_spline_twist(end_obj="", start_obj="", ik_spline_solver="", down_axis="X"):
    """
    Makes the spline solver twistable.
    :param world_up_object: <str> the end controller of the spline solver.
    :param world_base_object: <str> the start controller of the spline solver.
    :param ik_spline_solver: <str> the ik spline solver node.
    :returns: <bool> True for success. <bool> False for failure.
    """
    if not end_obj or not start_obj or not ik_spline_solver:
        return False

    start_obj_matrix_attr = start_obj + '.worldMatrix[0]'
    end_obj_matrix_attr = end_obj + '.worldMatrix[0]'
    ik_spline_solver_base_matrix_attr = ik_spline_solver + '.dWorldUpMatrix'
    ik_spline_solver_end_matrix_attr = ik_spline_solver + '.dWorldUpMatrixEnd'

    # enable twist
    cmds.setAttr(ik_spline_solver + '.dTwistControlEnable', 1)

    # set the splite spine attribute settings
    cmds.setAttr(ik_spline_solver + '.dWorldUpType', 4)
    cmds.setAttr(ik_spline_solver + '.dWorldUpAxis', 4)
    cmds.setAttr(ik_spline_solver + '.dForwardAxis', 2)

    # set up vectors
    if down_axis == "X":
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorX', 1)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndX', 1)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorY', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndY', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorZ', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndZ', 0)

    if down_axis == "Y":
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorX', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndX', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorY', 1)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndY', 1)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorZ', 0)
        cmds.setAttr(ik_spline_solver + '.dWorldUpVectorEndZ', 0)

    # set up the twist value type
    cmds.setAttr(ik_spline_solver + '.dTwistValueType', 1)

    # set up the connections
    if not cmds.isConnected(start_obj_matrix_attr, ik_spline_solver_base_matrix_attr):
        cmds.connectAttr(start_obj_matrix_attr, ik_spline_solver_base_matrix_attr, f=1)
    if not cmds.isConnected(end_obj_matrix_attr, ik_spline_solver_end_matrix_attr):
        cmds.connectAttr(end_obj_matrix_attr, ik_spline_solver_end_matrix_attr, f=1)
    return True


def setup_spline_stretch(joints=[], name="", down_axis="X", world_up_object="", world_base_object=""):
    """
    Makes a stretchy spline from joints provided.
    :param joints: <list> list of joints to create the stretchy math.
    :param name: <str> the name to use in all utility node creation.
    :param down_axis: <str> the axis pointing towards the joints, for the spline node stretch and twist setup.
    :param world_up_object: <str> Usually a controller at the end of the spline chain.
    :param world_base_object: <str> Usually a controller at the base of the spline chain.
    :returns: <bool> True for success. <bool> False for failure.
    """
    if not joints:
        cmds.error("[Spline Stretch] :: No joints parameter have been specified.")
        return False

    if not name:
        cmds.error("[Spline Stretch] :: No name parameter has been specified.")
        return False


    # find all necessary variables
    joint_node = util_get_m_object(joints[0])
    ik_handle_node = util_get_node(joint_node, ikHandle=1, downstream=1)
    ik_curve_node = util_get_node(ik_handle_node, curve=1, upstream=1)
    ik_effector_node = util_get_node(ik_handle_node, ikEffector=1, upstream=1)

    if not ik_handle_node and not ik_curve_node and not ik_effector_node:
        cmds.error("[Spline Stretch] :: Invalid components for Ik spline stretch system installation.")
        return False

    ik_handle_str = api0.MFnDagNode(ik_handle_node).name()
    ik_curve_str = api0.MFnDagNode(ik_curve_node).name()
    ik_effector_str = api0.MFnDagNode(ik_effector_node).name()

    # setup twist to the spline if parameters are given
    if world_up_object and world_base_object:
        setup_spline_twist(world_up_object, world_base_object, ik_handle_str, down_axis=down_axis)

    # setup stretchy
    arc_len_name = "{}_Arclen".format(name)
    if not cmds.objExists(arc_len_name):
         cmds.rename(cmds.arclen(ik_curve_str, ch=1), arc_len_name)

    print("[Arc Length] :: Arc Len Node {}".format(arc_len_name))
    print("[Spline Stretch] :: Ik Handle {}".format(ik_handle_str))
    print("[Spline Stretch] :: Ik Curve {}".format(ik_curve_str))
    print("[Spline Stretch] :: Ik Effector {}".format(ik_effector_str))

    unit_mult_node = "{}_UnitDiv".format(name)
    unit_mult_node_op_attr = "{}.operation".format(unit_mult_node)
    unit_mult_node_1x_attr = "{}.input1X".format(unit_mult_node)
    unit_mult_node_2x_attr = "{}.input2X".format(unit_mult_node)
    unit_mult_node_outx_attr = "{}.outputX".format(unit_mult_node)
    arc_len_attr = "{}.arcLength".format(arc_len_name)
    orig_arc_length = cmds.getAttr(arc_len_attr)

    # prepare the main division node
    if not cmds.objExists(unit_mult_node):
        cmds.createNode("multiplyDivide", name=unit_mult_node)
    if not cmds.isConnected(arc_len_attr, unit_mult_node_1x_attr):
        cmds.connectAttr(arc_len_attr, unit_mult_node_1x_attr, f=1)
    if not cmds.getAttr(unit_mult_node_2x_attr) == unit_mult_node_2x_attr:
        cmds.setAttr(unit_mult_node_2x_attr, orig_arc_length)
    if not cmds.getAttr(unit_mult_node_op_attr) == 2:
        cmds.setAttr(unit_mult_node_op_attr, 2)

    # iterate through all joints to get the constant down axis.
    for j in joints:
        joint_axis = '{}.translate{}'.format(j, down_axis)
        get_axis_value = cmds.getAttr(joint_axis)

        # prepare the joint division node
        joint_mult_node = j + '_Mult'
        joint_mult_node_2x_attr = "{}.input2X".format(joint_mult_node)
        joint_mult_node_1x_attr = "{}.input1X".format(joint_mult_node)
        joint_mult_node_outx_attr = "{}.outputX".format(joint_mult_node)

        if not cmds.objExists(joint_mult_node):
            cmds.createNode("multiplyDivide", name=joint_mult_node)
        if not cmds.getAttr(joint_mult_node_1x_attr) == get_axis_value:
            cmds.setAttr(joint_mult_node_1x_attr, get_axis_value)
        if not cmds.isConnected(unit_mult_node_outx_attr, joint_mult_node_2x_attr):
            cmds.connectAttr(unit_mult_node_outx_attr, joint_mult_node_2x_attr, f=1)
        if not cmds.isConnected(joint_mult_node_outx_attr, joint_axis):
            cmds.connectAttr(joint_mult_node_outx_attr, joint_axis, f=1)
    return True


def build_bbox_locator():
    """
    Builds a locator at the center of selection
    :return: <str> locator name.
    """
    selected = cmds.ls(sl=1)
    t_xform = get_selected_bbox_center()
    locator = cmds.spaceLocator(name=selected[0].replace(':', '_').replace('.', '_') + 'Loc')[0]
    cmds.xform(locator, t=t_xform, ws=1)
    return locator


def build_between_locator():
    """
    Builds a locator between two selected objects.
    :return: <str> locator name.
    """
    selected = cmds.ls(sl=1, fl=1)
    if not selected:
                return 0
    translates = []
    for sel in selected:
        print sel
        translates.append(cmds.xform(sel, t=1, ws=1, q=1))
    trans_x = 0.0
    trans_y = 0.0
    trans_z = 0.0
    for translations in translates:
        trans_x += translations[0]
        trans_y += translations[1]
        trans_z += translations[2]
    avg_factor = float(len(translates))
    print avg_factor
    print trans_x, trans_y, trans_z
    trans_x = trans_x / avg_factor
    trans_y = trans_y / avg_factor
    trans_z = trans_z / avg_factor

    locator = cmds.spaceLocator(name=selected[0].replace(':', '_').replace('.', '_') + 'Loc')[0]
    cmds.xform(locator, t=[trans_x, trans_y, trans_z], ws=1)
    return locator

