import maya.OpenMaya as om


def m_object_arg(func):
    def convert_to_m_object(*args, **kwargs):
        args = list(args)
        args[0] = get_m_object(args[0])
        return func(*args, **kwargs)
    return convert_to_m_object


def m_dag_path_arg(func):
    def convert_to_m_dag_path(*args, **kwargs):
        args = list(args)
        args[0] = get_m_dag_path(args[0])
        return func(*args, **kwargs)
    return convert_to_m_dag_path


def flatten_args(func):
    def flatten(*args, **kwargs):
        return func(*flatten_items(*args), **kwargs)
    return flatten


def flatten_items(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            nodes.extend(flatten_items(*arg))
        else:
            nodes.append(arg)
    return nodes


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    if isinstance(node, om.MDagPath):
        return node.node()
    selection_list = om.MSelectionList()
    selection_list.add(str(node))
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


def get_m_dag_path(node):
    if isinstance(node, om.MDagPath):
        return node
    if isinstance(node, om.MObject):
        return om.MDagPath.getAPathTo(node)
    selection_list = om.MSelectionList()
    selection_list.add(str(node))
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return om.MDagPath.getAPathTo(m_object)