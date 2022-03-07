import maya.OpenMaya as om
import maya_tools.utilities.decorators as dec

NURBS_CURVE_FORMS = [
    om.MFnNurbsCurve.kOpen,
    om.MFnNurbsCurve.kClosed,
    om.MFnNurbsCurve.kPeriodic
]


@dec.m_dag_path_arg
def get_closest_point(curve, position):
    curve_functions = om.MFnNurbsCurve(curve)
    u_util = om.MScriptUtil()
    u_util.createFromDouble(0)
    u_param = u_util.asDoublePtr()
    point = om.MPoint(*position)
    curve_functions.closestPoint(
        point,
        u_param,
        om.MSpace.kWorld
    )
    return om.MScriptUtil(u_param).asDouble()


def draw_nurbs_curve_data(positions, degree, form, create_2d=False, rational=False):
    """
    This will build curve data in api without ever creating the actual node
    A use-full way to work with curve math without ever creating nodes
    """
    spans = len(positions) - degree
    point_array = om.MPointArray()
    knots_array = om.MDoubleArray()
    for p in positions:
        point_array.append(om.MPoint(*p))
    for k in calculate_knots(spans, degree, form):
        knots_array.append(k)
    result_curve_data = om.MFnNurbsCurveData().create()
    om.MFnNurbsCurve().create(
        point_array,
        knots_array,
        degree,
        NURBS_CURVE_FORMS[form],
        create_2d,
        rational,
        result_curve_data
    )
    return result_curve_data


def calculate_knots(spans, degree, form):

    """
    **TO DO
    update to use correct math for building knot vector (see rigSpline.cpp)
    """
    knots = []
    knot_count = spans + 2*degree -1

    if form == 2:
        pit = (degree-1)*-1
        for itr in range(knot_count):
            knots.append(pit)
            pit += 1
        return knots

    for itr in range(degree):
        knots.append(0)
    for itr in range(knot_count - (degree*2)):
        knots.append(itr+1)
    for kit in range(degree):
        knots.append(itr+2)
    return knots


def get_predicted_curve_length(positions, degree, form):
    """
    This will build curve data and measure it without ever creating the actual node
    A use-full way to solve curve lengths for nodes that have internal nurbs curves
    """
    curve_data = draw_nurbs_curve_data(positions, degree, form)
    curve_functions = om.MFnNurbsCurve(curve_data)
    for i in range(len(positions)):
        point = om.MPoint()
        curve_functions.getCV(i, point, om.MSpace.kWorld)
    return curve_functions.length()


def get_closest_predicted_point_on_curve(point, positions, degree, form):
    """
    This will build curve data and find the closest point on it without ever creating the actual node
    A use-full way to solve curve parameters for nodes that have internal nurbs curves
    """
    curve_data = draw_nurbs_curve_data(positions, degree, form)
    curve_functions = om.MFnNurbsCurve(curve_data)
    u_util = om.MScriptUtil()
    u_util.createFromDouble(0)
    u_param = u_util.asDoublePtr()
    point = om.MPoint(*point)
    curve_functions.closestPoint(
        point,
        u_param,
        om.MSpace.kWorld
    )
    return om.MScriptUtil(u_param).asDouble()

@dec.m_object_arg
def get_nurbs_curve_objects(object, include_intermediate=False):
    mesh_objects = []
    dependency_node = om.MFnDependencyNode(object)
    node_type = str(dependency_node.typeName())
    if node_type == 'nurbsCurve':
        node_functions = om.MFnDependencyNode(object)
        m_attribute = node_functions.attribute('intermediateObject')
        m_plug = node_functions.findPlug(m_attribute, False)
        if include_intermediate or not m_plug.asBool():
            mesh_objects.append(object)
    elif node_type in ('transform', 'joint'):
        dag_path = om.MDagPath.getAPathTo(object)
        dag_functions = om.MFnDagNode(dag_path)
        for c in range(dag_functions.childCount()):
            mesh_objects.extend(get_nurbs_curve_objects(dag_functions.child(c)))
    return mesh_objects


def get_selected_nurbs_curve_objects(include_intermediate=False):
    mesh_objects = []
    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    for i in range(selection_list.length()):
        m_object = om.MObject()
        selection_list.getDependNode(i, m_object)
        mesh_objects.extend(get_nurbs_curve_objects(
            m_object,
            include_intermediate=include_intermediate
        ))
    return list(set(mesh_objects))