import maya.OpenMaya as om
import maya.cmds as mc
import maya_tools.utilities.decorators as dec

def get_shapes(curve_node=None):
    """
    Returns data from the transform node selected.
    :param curve_node: <str> node to look at.
    :return: <MObject>, <MFn> <MDagPath>.
    """
    if isinstance(curve_node (str, unicode)):
        sel = om.MSelectionList()
        sel.add(curve_node)
        node = om.MObject()
        sel.getDependNode(0, node)

    it_dg = om.MItDependencyGraph(node,
                                  om.MItDependencyGraph.kDownstream,
                                  om.MItDependencyGraph.kDepthFirst,
                                  om.MItDependencyGraph.kPlugLevel)

    m_dag = om.MDagPath()
    o_nodes = []
    m_objects = []
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()

        # kNurbsCurve
        if cur_item.hasFn(om.MFn.kNurbsCurve):
            m_objects.append(cur_item)
            o_nodes.append(om.MFnNurbsCurve(cur_item))

        # next item in the graph
        it_dg.next()
    return m_objects, o_nodes


@dec.m_object_arg
def get_shape_data(nurbs_curve):
    """
    Gets the shape data information from the MFNNurbsCurve data provided.
    :param nurb_fn: <MFnNurbsCurve>
    :return: <dict> nurb data.
    """
    curve_fn = om.MFnNurbsCurve(nurbs_curve)
    space = om.MSpace.kObject
    data = {
        'spans': 0,
        'cvs': None,
        'degree': 0,
        'form': "",
        'edit_points': []
    }

    # grab degrees and form
    data['degree'] = curve_fn.degree()
    data['form'] = int(curve_fn.form())

    # get curve knots
    knotArray = om.MDoubleArray()
    curve_fn.getKnots(knotArray)
    data['knots'] = list(knotArray)

    # get control vertices
    cv_array = om.MPointArray()
    curve_fn.getCVs(cv_array, space)
    data['cvs'] = [[cv_array[i].x, cv_array[i].y, cv_array[i].z] for i in range(cv_array.length())]

    # get edit points
    #edit_point = om.MPoint()
    #for u in data['knots']:
    #    curve_fn.getPointAtParam(u, edit_point, space)
    #    data['edit_points'].append((edit_point.x, edit_point.y, edit_point.z))
    return data

@dec.m_object_arg
def get_surface_shape_data(nurbs_curve):
    """
    Gets the shape data information from the MFNNurbsCurve data provided.
    :param nurb_fn: <MFnNurbsCurve>
    :return: <dict> nurb data.
    """
    surface_function = om.MFnNurbsSurface(nurbs_curve)
    space = om.MSpace.kObject
    cv_array = om.MPointArray()
    surface_function.getCVs(cv_array, space)
    knots_u_array = om.MDoubleArray()
    surface_function.getKnotsInU(knots_u_array)
    knots_v_array = om.MDoubleArray()
    surface_function.getKnotsInV(knots_v_array)

    data = [
        [[cv_array[i].x, cv_array[i].y, cv_array[i].z] for i in range(cv_array.length())],
        list(knots_u_array),
        list(knots_v_array),
        int(surface_function.degreeU()),
        int(surface_function.degreeV()),
        int(surface_function.formInU()),
        int(surface_function.formInV()),
    ]

    return data

def get_m_object(node_name):
    if isinstance(node_name, om.MObject):
        return node_name
    selection_list = om.MSelectionList()
    selection_list.add(node_name)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


def create_text_curve(name, text, font, parent):
    """
    Create curves from the given text
    :param name: (str) - user input for the curves' name
    :param text: (str) - text to convert into curves
    :param font: (str) - type of font to use
    :param parent: (object) - object to parent the curves to
    :return: (list) - a list of the created text curves' m_object
    """
    root = mc.textCurves(name=name, text=text, font=font)[0]
    mc.makeIdentity(root, apply=True, s=True, r=True, t=True)
    [mc.makeIdentity(x, apply=True, s=True, r=True, t=True) for x in mc.listRelatives(root, ad=True, type='nurbsCurve')]
    curve_m_objects = []
    nurbs_curves = mc.listRelatives(root, ad=True, type='nurbsCurve')
    for i, curve_name in enumerate(nurbs_curves):
        new_name = mc.rename(curve_name, '{0}_{1}_{2}_ncv'.format(name, text.replace(' ', '_'), i))
        mc.parent(new_name, parent, r=True, s=True)
        curve_m_objects.append(get_m_object(new_name))

    mc.delete(root)
    return curve_m_objects

