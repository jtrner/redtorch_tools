import maya.OpenMaya as om
import maya.mel as mel
import maya_tools.utilities.decorators as dec


def get_nurbs_surface_objects(object, include_intermediate=False):

    mesh_objects = []
    dependency_node = om.MFnDependencyNode(object)
    node_type = str(dependency_node.typeName())
    if node_type == 'nurbsSurface':
        node_functions = om.MFnDependencyNode(object)
        m_attribute = node_functions.attribute('intermediateObject')
        m_plug = node_functions.findPlug(m_attribute, False)
        if include_intermediate or not m_plug.asBool():
            mesh_objects.append(object)
    elif node_type in ('transform', 'joint'):
        dag_path = om.MDagPath.getAPathTo(object)
        dag_functions = om.MFnDagNode(dag_path)
        for c in range(dag_functions.childCount()):
            mesh_objects.extend(get_nurbs_surface_objects(dag_functions.child(c)))
    return mesh_objects


def get_selected_nurbs_surface_objects(include_intermediate=False):
    mesh_objects = []
    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    for i in range(selection_list.length()):
        m_object = om.MObject()
        selection_list.getDependNode(i, m_object)
        mesh_objects.extend(get_nurbs_surface_objects(
            m_object,
            include_intermediate=include_intermediate
        ))
    return list(set(mesh_objects))


@dec.m_dag_path_arg
def get_closest_uv(surface, position):

    surface_functions = om.MFnNurbsSurface(surface)

    u_util = om.MScriptUtil()
    u_util.createFromDouble(0)
    u_param = u_util.asDoublePtr()

    v_util = om.MScriptUtil()
    v_util.createFromDouble(0)
    v_param = v_util.asDoublePtr()

    p = surface_functions.closestPoint(
        om.MPoint(*position),
        u_param,
        v_param,
        False,
        1.0,
        om.MSpace.kWorld
    )

    return om.MScriptUtil.getDouble(u_param), om.MScriptUtil.getDouble(v_param)


@dec.m_dag_path_arg
def get_closest_point(surface, position):

    surface_functions = om.MFnNurbsSurface(surface)

    u_util = om.MScriptUtil()
    u_util.createFromDouble(0)
    u_param = u_util.asDoublePtr()

    v_util = om.MScriptUtil()
    v_util.createFromDouble(0)
    v_param = v_util.asDoublePtr()

    p = surface_functions.closestPoint(
        om.MPoint(*position),
        u_param,
        v_param,
        False,
        1.0,
        om.MSpace.kWorld
    )

    return p[0], p[1], p[2]


@dec.m_dag_path_arg
def mirror_surface_shape(surface, negative=False):
    surface_functions = om.MFnNurbsSurface(surface)
    u_count = surface_functions.numCVsInU()
    v_count = surface_functions.numCVsInV()
    odd_u_count = u_count % 2 != 0

    center_index = None
    if odd_u_count:
        target_index_count = (u_count-1) / 2
        center_index = target_index_count + 1

    else:
        target_index_count = u_count / 2

    print 'center_index = ', center_index

    for v in range(v_count):
        for u in range(target_index_count + 1):
            source_index = get_opposing_index(u, u_count)
            print u, source_index
            if negative:
                m_point = om.MPoint()
                surface_functions.getCV(
                    source_index,
                    v,
                    m_point,
                    om.MSpace.kObject
                )
                point = list(m_point)
                point[0] = point[0] * -1
                surface_functions.setCV(
                    u,
                    v,
                    om.MPoint(*point),
                    om.MSpace.kObject
                )
            else:
                m_point = om.MPoint()
                surface_functions.getCV(
                    u,
                    v,
                    m_point,
                    om.MSpace.kObject
                )
                point = list(m_point)
                point[0] = point[0] * -1
                surface_functions.setCV(
                    source_index,
                    v,
                    om.MPoint(*point),
                    om.MSpace.kObject
                )
    mel.eval('dgdirty -a')


def get_opposing_index(value, count):
    opposing_index = count - value - 1
    return opposing_index
