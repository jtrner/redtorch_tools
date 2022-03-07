import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

def get_m_object(node):

    selection_list = om.MSelectionList()
    selection_list.add(str(node))
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object
    
def get_deformer_members(m_deformer):
    members_dict = dict()
    deformer_functons = oma.MFnGeometryFilter(get_m_object( 'C_JawSquash_Ffd_Def'))
    set_functions = om.MFnSet(deformer_functons.deformerSet())
    members = om.MSelectionList()
    set_functions.getMembers(members, False)
    members.length()
    all_members = {}
    for i in range(members.length()):
        m_object = om.MObject()
        members.getDependNode(i, m_object)
        if m_object.hasFn(om.MFn.kDagNode):
            component_m_object = om.MObject()
            dag_path = om.MDagPath()
            members.getDagPath(i, dag_path, component_m_object)
            if dag_path and not component_m_object.isNull():
                dag_functions = om.MFnDagNode(dag_path)
                if str(dag_functions.typeName()) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
                    object_vertices = []
                    iterator = om.MItGeometry(dag_path, component_m_object)
                    while not iterator.isDone():
                        object_vertices.append(int(iterator.index()))
                        iterator.next()
                    all_members.update({str(dag_functions.name()):object_vertices})


    return(all_members)
def get_m_dag_path(node):
    if isinstance(node, om.MDagPath):
        return node
    if isinstance(node, om.MObject):
        return om.MDagPath.getAPathTo(node)
    selection_list = om.MSelectionList()
    selection_list.add(node)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return om.MDagPath.getAPathTo(m_object)
    
def remove_deformer_geometry(m_deformer, geometry):
    print('bbbbbbbbbbbbbbbbb', geometry)
    members = get_deformer_members(m_deformer)
    
    set_functions = om.MFnSet(oma.MFnGeometryFilter(m_deformer).deformerSet())
    print(members)
    for mesh_name in geometry:
        if 'Body_GeoShape' or members:
            vertices = om.MIntArray()
            [vertices.append(x) for x in members[mesh_name]]
            component = om.MFnSingleIndexedComponent()
            component_object = component.create(om.MFn.kMeshVertComponent)
            component.addElements(vertices)
            set_functions.removeMember(get_m_dag_path(mesh_name), component_object)
            
remove_deformer_geometry(get_m_object( 'C_JawSquash_Ffd_Def'), ['Body_GeoShape'])            