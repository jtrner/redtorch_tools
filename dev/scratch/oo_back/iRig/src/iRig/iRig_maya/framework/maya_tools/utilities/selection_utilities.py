import maya.OpenMaya as om


def get_selected_transform_names():
    return [get_selection_string(x) for x in get_selected_transforms()]


def get_selected_transforms():
    transforms = []
    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    for i in range(selection_list.length()):
        m_object = om.MObject()
        selection_list.getDependNode(i, m_object)
        if get_m_object_type(m_object) == 'transform':
            transforms.append(m_object)
    return transforms


def get_m_object_type(m_object):
    return str(om.MFnDependencyNode(m_object).typeName())

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
