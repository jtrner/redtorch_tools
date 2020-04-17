import maya.cmds as mc
import maya.OpenMaya as om
from rig_math.vector import Vector

NURBS_CURVE_FORMS = [
    om.MFnNurbsCurve.kOpen,
    om.MFnNurbsCurve.kClosed,
    om.MFnNurbsCurve.kPeriodic
]


def create_loft_ribbon(positions, vector, parent, degree=2):
    vector = Vector(vector)
    curve_list = []
    for position in positions:
        curve_name = mc.curve(
            degree=1,
            point=[vector, vector * -1],
            worldSpace=True
        )

        mc.setAttr('{0}.tx'.format(curve_name), position[0])
        mc.setAttr('{0}.ty'.format(curve_name), position[1])
        mc.setAttr('{0}.tz'.format(curve_name), position[2])

        curve_list.append(curve_name)
    loft_transform = mc.loft(curve_list, ch=False, uniform=True, rn=False, po=0, rsn=True, degree=degree)[0]
    nurbs_surface = mc.listRelatives(loft_transform, c=True, type='nurbsSurface')[0]
    parent_name = get_selection_string(parent)
    nurbs_surface = mc.rename(nurbs_surface, '%sShape' % parent_name)
    mc.parent(nurbs_surface, parent_name, s=True, r=True)
    mc.delete(curve_list, loft_transform)
    return get_m_object(nurbs_surface)


def create_extrude_ribbon(positions, vector, parent, degree=2):
    vector = Vector(vector)
    positions = [Vector(x) - (vector*0.5) for x in positions]
    nurbs_curve = draw_nurbs_curve(positions, degree, 0, parent)
    nurbs_name = get_selection_string(nurbs_curve)
    loft_transform = mc.extrude(
        nurbs_name,
        ch=False,
        rn=False,
        po=0,
        et=0,
        upn=0,
        d=vector.normalize(),
        rotation=0,
        scale=1,
        dl=3,
        length=vector.mag()
    )[0]
    nurbs_surface = mc.listRelatives(loft_transform, c=True, type='nurbsSurface')[0]
    parent_name = get_selection_string(parent)
    nurbs_curve_name = get_selection_string(nurbs_curve)
    nurbs_surface = mc.rename(nurbs_surface, '%sShape' % parent_name)
    mc.reverseSurface(nurbs_surface, d=3, ch=0, rpo=1)
    mc.parent(nurbs_surface, parent_name, s=True, r=True)
    mc.delete(nurbs_curve_name, loft_transform)
    return get_m_object(nurbs_surface)


def draw_nurbs_curve(positions, degree, form, parent):
    create_2d = False
    rational = False
    spans = len(positions) - degree
    point_array = om.MPointArray()
    knots_array = om.MDoubleArray()
    for p in positions:
        point_array.append(om.MPoint(*p))
    for k in calculate_knots(spans, degree, form):
        knots_array.append(k)
    args = [
        point_array,
        knots_array,
        degree,
        NURBS_CURVE_FORMS[form],
        create_2d,
        rational,
        parent
    ]
    m_object = om.MFnNurbsCurve().create(*args)
    return m_object

def calculate_knots(spans, degree, form):

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


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


def get_m_object(node_name):
    if isinstance(node_name, om.MObject):
        return node_name
    selection_list = om.MSelectionList()
    selection_list.add(node_name)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object
