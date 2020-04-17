import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma


def create_ik_handle(start_joint, end_effector, solver='ikSCsolver', name=None, parent=None):
    start_joint_dag_path = om.MDagPath.getAPathTo(start_joint)
    end_effector_dag_path = om.MDagPath.getAPathTo(end_effector)
    m_object = oma.MFnIkHandle().create(
        start_joint_dag_path,
        end_effector_dag_path
    )
    oma.MFnIkHandle(m_object).setSolver(solver)
    selection_string = get_selection_string(m_object)
    if name:
        selection_string = mc.rename(selection_string, name)
    if parent:
        parent_selection_string = get_selection_string(parent)
        mc.parent(selection_string, parent_selection_string)
        parents = mc.listRelatives(selection_string, p=True)
        if parents:
            if parents[0] != str(parent_selection_string):
                raise Exception('Parents broke')
    return m_object


def create_ik_spline_handle(start_joint, end_effector, solver, curve, parent=None):
    spline_handle_name = mc.ikHandle(
        sj=get_selection_string(start_joint),
        ee=get_selection_string(end_effector),
        sol=solver,
        curve=get_selection_string(curve),
        roc=False,
        pcv=False,
        ccv=False,
    )
    if parent:
        mc.parent(spline_handle_name, parent)

    """
    find out which index dont use name
    """
    for item in spline_handle_name:
        if 'ikHandle' in item:
            spline_handle_name = item
    return get_m_object(spline_handle_name)


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
