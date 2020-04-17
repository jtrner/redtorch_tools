"""Toolkit functions for modifying, queryig and setting Maya skincluster data."""

# define maya imports
from maya import OpenMaya as api0
from maya import OpenMayaAnim as apiAnim0
import maya.cmds as cmds

# define custom imports
from rig_tools import RIG_LOG

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "IL"
__version__ = "1.1.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def get_m_object(object_node=""):
    """
    Returns the MObject class of the string provided.
    :return: <api0.MObject> for success. <bool> False for failure.
    """
    m_sel = api0.MSelectionList()
    m_sel.add(object_node)
    m_obj = api0.MObject()
    try:
        m_sel.getDependNode(0, m_obj)
    except RuntimeError:
        return False
    return m_obj


def get_mesh_fn(node_name):
    """
    Grabs the MFnMesh of the specified node.
    :param node_name: <str> node name.
    :return: <api0.MFnMesh> if successful, <bool> False if fail.
    """
    sel = api0.MSelectionList()
    sel.add(node_name)
    m_dag = api0.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(api0.MFn.kMesh):
        return False
    return api0.MFnMesh(m_dag)


def get_curve_fn(node_name):
    """
    Grabs the MFnNurbsCurve of the specified node.
    :param node_name: <str> node name.
    :return: <api0.MFnNurbsCurve> if successful, <bool> False if fail.
    """
    sel = api0.MSelectionList()
    sel.add(node_name)
    m_dag = api0.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(api0.MFn.kNurbsCurve):
        return False
    return api0.MFnNurbsCurve(m_dag)


def get_nurb_fn(node_name):
    """
    Grabs the MFnNurbsCurve of the specified node.
    :param node_name: <str> node name.
    :return: <api0.MFnNurbsSurface> if successful, <bool> False if fail.
    """
    sel = api0.MSelectionList()
    sel.add(node_name)
    m_dag = api0.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(api0.MFn.kNurbsSurface):
        return False
    return api0.MFnNurbsSurface(m_dag)


def get_skin_fn(node):
    """
    Gets the MFnSkinCluster from the MObject specified.
    :param node: <MObject> node to look at.
    :return: <MFnSkinCluster> if successful, <bool> False if fail.
    """
    skin_fn = False
    it_dg = api0.MItDependencyGraph(node,
                                        api0.MItDependencyGraph.kDownstream,
                                        api0.MItDependencyGraph.kPlugLevel)
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        if cur_item.hasFn(api0.MFn.kSkinClusterFilter):
            skin_fn = apiAnim0.MFnSkinCluster(cur_item)
            break
        it_dg.next()
    return skin_fn


def get_mesh_from_skincluster(skin_fn=None):
    """
    Finds attached mesh to this skin cluster.
    :param skin_fn: <str> skin cluster function set.
    """
    mesh_fn = False
    skin_obj = skin_fn.object()
    it_dg = api0.MItDependencyGraph(skin_obj,
                                    api0.MItDependencyGraph.kUpstream,
                                    api0.MItDependencyGraph.kPlugLevel)
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        if cur_item.hasFn(api0.MFn.kMesh):
            mesh_fn = api0.MFnMesh(cur_item)
            break
        it_dg.next()
    return mesh_fn


def get_dag_path_fn(m_obj):
    """
    Gets the MDagPath from object provided.
    :param m_obj: MFnObjectType, MFnNurbsCurve, MFnNurbsSurface, MFnMesh.
    :return: <api0.MDagPath> of object. <bool> False for failure.
    """
    object_name = m_obj.name()
    m_dag = api0.MDagPath()
    m_sel = api0.MSelectionList()
    m_sel.add(object_name)
    m_sel.getDagPath(0, m_dag)
    return m_dag


def get_selections():
    """
    Iterate through a selection to get the items selected in the scene.
    :return: <list> Selected objects.
    """
    sel_ls = []
    selection = api0.MSelectionList()
    api0.MGlobal.getActiveSelectionList(selection)
    selection_iter = api0.MItSelectionList(selection)
    obj = api0.MObject()
    while not selection_iter.isDone():
        selection_iter.getDependNode(obj)
        m_dag = api0.MDagPath.getAPathTo(obj)
        sel_ls.append(m_dag.fullPathName())
        selection_iter.next()
    return sel_ls


def get_skin_components(skin_fn=None):
    """
    Gets the skin cluster components.
    :param skin_fn: <api0.MFnSkinCluster> object.
    :return: <MDagPath> dag_path, <MObject> components.
    """
    mfn_set = api0.MFnSet(skin_fn.deformerSet())
    mfn_set_members = api0.MSelectionList()
    dag_path = api0.MDagPath()
    m_component_obj = api0.MObject()
    
    # add the mesh to the skin cluster sets if the set members are empty
    mfn_set.getMembers(mfn_set_members, False)
    if mfn_set_members.isEmpty():
        mesh_fn = get_mesh_from_skincluster(skin_fn=skin_fn)
        
    if mfn_set_members.isEmpty():
        mesh_name = mesh_fn.name()
        print("[Skin Components] :: Adding {} to {}".format(mesh_name, mfn_set.name()))
        cmds.sets(mesh_fn.name(), fe=mfn_set.name())
        mfn_set.getMembers(mfn_set_members, False)
    
    # try adding reference geo ShapeDeformed to set.
    if mfn_set_members.isEmpty():
        mesh_name = mesh_fn.name().split(':')[-1] + "Deformed"
        print("[Skin Components] :: Adding {} to {}".format(mesh_name, mfn_set.name()))
        cmds.sets(mesh_name, fe=mfn_set.name())
        mfn_set.getMembers(mfn_set_members, False)

    mfn_set_members.getDagPath(0, dag_path, m_component_obj)
    return dag_path, m_component_obj


def get_node_fn(obj_name=""):
    """
    Returns the node fn.
    :param obj_name: <str> provide object name.
    :return: <api0.MFn.kNodeType> o_node.
    """
    if not obj_name:
        return False
    o_node = get_mesh_fn(obj_name)
    if not o_node:
        o_node = get_curve_fn(obj_name)
    if not o_node:
        o_node = get_nurb_fn(obj_name)
    return o_node


def get_skin_cluster_obj(obj_name="", return_str=False):
    """
    Gets the skin cluster name from the object specified.
    :param obj_name: <str> object name to find the skinCluster from.
    :return: <str> skincluster name, <api0.MFnSkinCluster> skin_fn if successful, <bool> False if fail.
    """
    if not obj_name:
        return False
    o_node = get_node_fn(obj_name)
    o_path = o_node.dagPath()
    m_obj = o_path.node()
    skin_fn = get_skin_fn(m_obj)
    if skin_fn:
        return skin_fn.name(), skin_fn
    else:
        return False, False


def get_skin_set_obj(skin_name=""):
    """
    Gets the skinCluster Set object name.
    :return: <str>, <str> Skin Cluster set name, Skin Cluster set.
    """
    try:
        cur_item = get_m_object(skin_name)
        skin_fn = apiAnim0.MFnSkinCluster(cur_item)
        skin_set = api0.MFnSet(skin_fn.deformerSet())
        skin_set.name, skin_set
        return skin_set.name(), skin_set
    except RuntimeError:
        return False, False


def get_skin_vars(mesh_name="", debug=False):
    """
    Returns skin cluster influences and weights.
    :param mesh_name: <str> mesh object name.
    :param debug: <bool> debug this function.
    :return: <list> weights, <int> number of influences, <int> number of components
                if successful,
            <bool> False, <bool> False, <bool> False
                if fail.
    :note:
        the returning .getWeights() returns an array of values.
        the length of this array equates to: number_of_weights = influences * verts.
        meaning that for every vertex, there are this number of influeces acting on it.
    """
    skin_name, skin_fn = get_skin_cluster_obj(mesh_name)
    node_fn = get_node_fn(mesh_name)
    double_array = api0.MDoubleArray()
    util = api0.MScriptUtil()
    util.createFromInt(0)
    uint_ptr = util.asUintPtr()
    m_dag = get_dag_path_fn(node_fn)
    fn_comp = api0.MFnSingleIndexedComponent()

    if not skin_fn:
        RIG_LOG.error("[No Skin] :: No skincluster found on {}.".format(mesh_name))
        return False, False, False

    m_inf = api0.MDagPathArray()
    skin_fn.influenceObjects(m_inf)

    if node_fn.typeName() == 'nurbsSurface':
        components_fn = fn_comp.create(api0.MFn.kSurfaceCVComponent)
        num_components = node_fn.numCVs()
        fn_comp.setCompleteData(node_fn.numCVs())
    if node_fn.typeName() == 'nurbsCurve':
        components_fn = fn_comp.create(api0.MFn.kCurveCVComponent)
        fn_comp.setCompleteData(node_fn.numCVs())
        num_components = node_fn.numCVs()
    if node_fn.typeName() == 'mesh':
        components_fn = fn_comp.create(api0.MFn.kMeshVertComponent)
        fn_comp.setCompleteData(node_fn.numVertices())
        num_components = node_fn.numVertices()

    if debug:
        RIG_LOG.info("[MDagPath] :: {}".format(m_dag))
        RIG_LOG.info("[MFnSkinCluster] :: {}".format(skin_fn))
        RIG_LOG.info("[MFnComponent] :: {}".format(components_fn))
        RIG_LOG.info("[MDoubleArray] :: {}".format(double_array))
        RIG_LOG.info("[uIntPtr] :: {}".format(uint_ptr))

    skin_fn.getWeights(m_dag, components_fn, double_array, uint_ptr)
    return double_array, m_inf.length(), num_components


def _get_blend_weights_array(mfn_skin=None, obj_dag_path=None, obj_component=None):
    """
    Get MFnSkinCluster Dual Quaternion blend weights weights array.
    :param mfn_skin: <MFnSkinCLuster> skin cluster function class object.
    :param obj_dag_path: <MFnDagPath> dag path function class object.
    :param obj_component: <MFnSet> MObject set function class object
    :return: <list> blendWeights double list array. <bool> False if list is empty.
    """
    weights_array = api0.MDoubleArray()
    mfn_skin.getBlendWeights(obj_dag_path, obj_component, weights_array)
    weight_length = weights_array.length()
    blend_weights_array = [weights_array[i] for i in range(weight_length)]
    values_list = list(filter(lambda x: x < 0.0, blend_weights_array))
    # print("BlendWeights :: {}".format(blend_weights_array))
    return blend_weights_array


def util_get_skin_influences(skin_fn=""):
    """
    Returns skin influence objects by list of names.
    :param skin_fn: <MFNSkinCluster> skin cluster MFn Object.
    :return: <list> skin influences.
    """
    # get the MDagPath for all influence
    inf_dags = api0.MDagPathArray()
    skin_fn.influenceObjects(inf_dags)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    inf_ids = {}
    infs_ls = []
    for x in xrange(inf_dags.length()):
        inf_path = inf_dags[x].partialPathName()
        inf_id = int(skin_fn.indexForInfluenceObject(inf_dags[x]))
        inf_ids[inf_id] = x
        infs_ls.append(inf_path)
    return infs_ls


def get_skin_data(mesh_name=""):
    """
    Exports skinCluster as a dictionary.
    :param mesh_name: <str> the mesh string to export skinCluster from.
    :return: <dict> skin weights. <bool> False for failure.
    """
    weights_data = {}
    weights_data["mesh"] = mesh_name

    # gets the component data from the object provided
    weights, num_influences, num_components = get_skin_vars(mesh_name=mesh_name)
    weights_data["num_influences"] = num_influences
    weights_data["num_components"] = num_components
    # weights_data["mfn_weights"] = weights

    # get the MFnSkinCluster for skin_obj
    skin_name, skin_fn = get_skin_cluster_obj(obj_name=mesh_name)
    obj_dag, obj_component = get_skin_components(skin_fn=skin_fn)

    # get skin cluster attributes
    envelope_plug = skin_fn.findPlug('envelope')
    weights_data["envelope"] = envelope_plug.asDouble()

    skinning_method_plug = skin_fn.findPlug('skinningMethod')
    weights_data["skinningMethod"] = skinning_method_plug.asInt()

    use_component_plug = skin_fn.findPlug('useComponents')
    weights_data["useComponents"] = use_component_plug.asBool()

    normalize_weights_plug = skin_fn.findPlug('normalizeWeights')
    weights_data["normalizeWeights"] = normalize_weights_plug.asBool()

    user_normals_plug = skin_fn.findPlug('deformUserNormals')
    weights_data["deformUserNormals"] = user_normals_plug.asInt()

    weights_data["blendWeights"] = _get_blend_weights_array(
        mfn_skin=skin_fn, obj_dag_path=obj_dag, obj_component=obj_component)

    # get the MDagPath for all influence
    inf_dags = api0.MDagPathArray()
    skin_fn.influenceObjects(inf_dags)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    inf_ids = {}
    infs_ls = []
    for x in xrange(inf_dags.length()):
        inf_path = inf_dags[x].fullPathName()
        inf_id = int(skin_fn.indexForInfluenceObject(inf_dags[x]))
        inf_ids[inf_id] = x
        infs_ls.append(inf_path)

    # trim_inf_names = map(lambda i_str: i_str.rpartition('|')[-1], infs_ls)
    weights_data['influences'] = infs_ls
    RIG_LOG.info("[Influences of {}] :: {}".format(skin_name, num_influences))

    # get the MPlug for the weightList and weights attributes
    weight_ls_plug = skin_fn.findPlug('weightList')
    weights_plug = skin_fn.findPlug('weights')
    weights_ls_attr = weight_ls_plug.attribute()
    weights_attr = weights_plug.attribute()
    weight_ids = api0.MIntArray()

    # build the dictionary where vertex_id is the key
    weights_data["data"] = {}
    for v_id in xrange(weight_ls_plug.numElements()):
        val_weights = {}
        weights_plug.selectAncestorLogicalIndex(v_id, weights_ls_attr)
        weight_ls_plug.getExistingArrayAttributeIndices(weight_ids)

        # create a copy of the current weights_plug
        inf_plug = api0.MPlug(weights_plug)
        for inf_id in weight_ids:
            # tell the inf_plug it represents the current influence id
            inf_plug.selectAncestorLogicalIndex(inf_id, weights_attr)

            # add this influence and its weight to this verts weights
            if inf_ids.has_key(inf_id):
                val_weights[inf_ids[inf_id]] = inf_plug.asDouble()
        weights_data["data"][v_id] = val_weights
    return weights_data


def normalize_skin(influences=[], skin_name="", mesh_name=""):
    """
    Normalizes the skin cluster weights by pruning.
    :param influences: <list> list of influence joints.
    :param skin_name: <str> skin cluster node name.
    :param mesh_name: <str> mesh name with skin cluster.
    :return: <bool> True for success.
    """


    # unlock influences used by skin cluster
    if influences:
        for inf in influences:
            cmds.setAttr('%s.liw' % inf)


    # normalize needs turned off for the prune to work
    skin_normalize = cmds.getAttr('%s.normalizeWeights' % skin_name)
    if skin_normalize != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, 0)
        cmds.skinPercent(skin_name, mesh_name, nrm=False, prw=100)


    # restore normalize setting
    if skin_normalize != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, skin_normalize)
        cmds.skinCluster(skin_name, e=1, forceNormalizeWeights=1)

    return True


def add_skincluster(mesh_name="", influence_objects=[]):
    """
    Adds a skin cluster to an object if it does not exist.
    :param mesh_name: <str> mesh object to attach skin cluster to.
    :param influence_objects: <list> adds influences to skin cluster node.
    :return: <str> skin_name for success, <bool> False for failure.
    """
    if not mesh_name:
        return False

    if not influence_objects:
        return False

    # get the skin cluster attached to object, if not found, create it
    skin_name, skin_fn = get_skin_cluster_obj(mesh_name)
    if not skin_name:
        skin_name = mesh_name + "_Skin"
        if ":" in skin_name:
            skin_name = skin_name.rpartition(':')[-1]
        cmds.skinCluster(mesh_name, influence_objects, name=skin_name, tsb=1)
        RIG_LOG.info("[Skin Cluster] :: Created {}".format(skin_name))
    return skin_name


def set_blend_weights(mesh_name=None, weights=None):
    """
    Sets the blend weights skin data.
    :param mesh_name: the mesh name to get components from.
    :param weights: weight values.
    :return: True for success. False for failure.
    """
    if not weights:
        return False

    # get current skin components
    skin_name, skin_fn = get_skin_cluster_obj(mesh_name)

    if not skin_fn:
        RIG_LOG.error("[No Skin] :: No skincluster found on {}.".format(mesh_name))
        return False

    obj_dag, obj_component = get_skin_components(skin_fn)

    # set the blend weights on the skin cluster node
    m_blendweights = api0.MDoubleArray(len(weights))
    for i, w in enumerate(weights):
        m_blendweights.set(w, i)
    skin_fn.setBlendWeights(obj_dag, obj_component, m_blendweights)
    return True


def set_skin_data(weight_data={}, mesh_name="", use_hierarchy=False):
    """
    Sets the skin weights.
    :param weight_data: <dict> the skin weight to import.
    :param mesh_name: <str> the mesh to set the skin cluster weights on.
    :return: <bool> True for success. <False> for failure.
    """
    RIG_LOG.info("[Set Skin Data] :: Running on {}.".format(mesh_name))

    if not weight_data:
        RIG_LOG.error("[Weight Data Failure] :: No weight data found.")
        return False

    data = weight_data['data']
    weight_influences = weight_data['influences']

    # check the influences in the scene to see if they are valid
    check_influences = []
    shortname_influences = []
    for weighted_jnt in weight_influences:
        weighted_jnt_name = weighted_jnt.rpartition('|')[-1]
        if not cmds.objExists(weighted_jnt_name):
            check_influences.append(weighted_jnt_name)
        shortname_influences.append(weighted_jnt_name)

    print len(weight_influences), len(shortname_influences)

    if check_influences:
        RIG_LOG.error("[Invalid Infuences] :: Influences not found: {}".format(check_influences))
        return False

    if use_hierarchy:
        jnt_list = weight_influences
    else:
        jnt_list = shortname_influences

    # apply skin if there is one does not exist
    skin_name = add_skincluster(mesh_name=mesh_name, influence_objects=jnt_list)
    print("[Set Skin] :: {}".format(skin_name))
    if not skin_name:
        return False

    # normalize the skin cluster node prior setting of the skin cluster weights
    try:
        normalize_skin(influences=jnt_list, skin_name=skin_name, mesh_name=mesh_name)
    except RuntimeError:
        # The skinCluster does not deform the selected component(s)
        pass

    # unpack the dictionary and set the skin weights.
    for vert_id, weight_values in data.items():
        weights_ls_attr = '%s.weightList[%s]' % (skin_name, vert_id)
        for inf_id, infValue in weight_values.items():
            weights_plug = '.weights[%s]' % inf_id
            cmds.setAttr(weights_ls_attr + weights_plug, infValue)

    # set the blendWeights
    if 'blendWeights' in weight_data:
        blend_weights = weight_data['blendWeights']
        set_blend_weights(mesh_name=mesh_name, weights=blend_weights)

    # set the attributes
    if 'envelope' in weight_data:
        cmds.setAttr(skin_name + '.envelope', weight_data['envelope'])

    if 'skinningMethod' in weight_data:
        cmds.setAttr(skin_name + '.skinningMethod', weight_data['skinningMethod'])

    if 'useComponents' in weight_data:
        cmds.setAttr(skin_name + '.useComponents', weight_data['useComponents'])

    if 'normalizeWeights' in weight_data:
        cmds.setAttr(skin_name + '.normalizeWeights', weight_data['normalizeWeights'])

    if 'deformUserNormals' in weight_data:
        cmds.setAttr(skin_name + '.deformUserNormals', weight_data['deformUserNormals'])

    RIG_LOG.info("[Set Skin Finished] :: Skin cluster weights are set.".format(skin_name))
    return True


def mfn_set_skin_data(mesh_name="", weight_data={}, debug=True, iterate_each_vertex=False):
    """
    This method is much faster but does not use undo. This uses MFnSkinCluster.setWeights() function.
    :return: <bool> True for success. <bool> False for failure.
    :param mesh_name: <str> the mesh object name to apply weights on.
    :param weight_data: <dict> the weight data to extract information from.
    :param iterate_each_vertex: <bool> uses a MItMeshVertex to parse through point data.
    :param debug: <bool> prints the class variables.
    :note:

        setWeights(MFnSkinCluster *,MDagPath const &,MObject const &,unsigned int,double,bool,MDoubleArray *)
        setWeights(MFnSkinCluster *,MDagPath const &,MObject const &,MIntArray &,MDoubleArray &,bool,MDoubleArray *)
        setWeights(MFnSkinCluster *,MDagPath const &,MObject const &,unsigned int,float,bool,MFloatArray *)
        setWeights(MFnSkinCluster *,MDagPath const &,MObject const &,MIntArray &,MFloatArray &,bool,MFloatArray *)

        Sets the skinCluster weight for the influence object on the specified components of the object whose dagPath is
        specified. The influence is specified using the physical (non-sparse) index of the influence object.
        This corresponds to the order the influences are returned by the influenceObjects method.

        In order to undo the setWeight operation,
         it is necessary to save the oldValues array and call setWeight with the oldValues array at the time of undo.

        The number of oldValues returned will be of size number of specified components x the total number
         of influence objects.

        The values in the oldValues array will be ordered with first the all the values for the first component,
         then all the values for the next, and so on.

        Note that unlike most deformers, a skinCluster node can deform only a single geometry.
        Therefore, if additional geometries are added to the skinCluster set,
        they will be ignored, and weights cannot be set for the additional geometry.
    """
    RIG_LOG.info("[Set MFnSkin Data] :: Running on {}.".format(mesh_name))

    if not mesh_name:
        RIG_LOG.error("[Parameter Error] :: No mesh has been given.".format(mesh_name))
        return False

    if not weight_data:
        RIG_LOG.error("[Parameter Error] :: No weight data dictionery has been given.".format(weight_data))
        return False

    # define variables
    zero_weights = api0.MDoubleArray()
    data = weight_data["data"]
    influences = weight_data["influences"]
    num_influences = weight_data["num_influences"]
    num_components = weight_data["num_components"]
    num_weights = num_components * num_influences
    node_fn = get_node_fn(mesh_name)
    mesh_dag = get_dag_path_fn(node_fn)
    mesh_fn = get_mesh_fn(mesh_name)
    vertex_array = api0.MIntArray(num_components, 0)
    component_fn = api0.MFnSingleIndexedComponent().create(api0.MFn.kMeshVertComponent)
    api0.MFnSingleIndexedComponent(component_fn).addElements(vertex_array)
    joint_int_array = api0.MIntArray(num_influences, 0)
    weights_dbl_array = api0.MDoubleArray(num_weights, 0)

    # set joint MIntArray object
    for ii in xrange(num_influences):
        joint_int_array.set(ii, ii)

    # construct the weights array for setting MFnSkinCluster weights array class object
    data_count = 0
    for component_idx in xrange(num_components):
        influence_array = data[str(component_idx)]
        for inf_idx, weight_float in influence_array.items():
            weights_dbl_array.set(weight_float, data_count)
            data_count += 1

    # apply skin if there is one does not exist
    add_skincluster(mesh_name=mesh_name, influence_objects=influences)

    # grabs the MFnSkinCluster class object attached
    skin_name, skin_fn = get_skin_cluster_obj(mesh_name)

    # prevent the program from proceeding if no skinclusters are found
    if not skin_name:
        RIG_LOG.info("[No Skincluster] :: No skin cluster could be instantiated.")
        return False

    # normalize the skin cluster node prior setting of the skin cluster weights
    normalize_skin(influences=influences, skin_name=skin_name, mesh_name=mesh_name)

    # turn off undo and perform MFnSkinCluster setWeights
    cmds.undoInfo(state=False)

    if debug:
        RIG_LOG.info('[MFnMesh MDagPath] :: {}'.format(mesh_dag))
        RIG_LOG.info('[MFnComponent MObject] :: {}'.format(component_fn))
        RIG_LOG.info('[MFloatArray] :: {}'.format(joint_int_array))
        RIG_LOG.info('[MDoubleArray] :: {}, {}'.format(data_count, weights_dbl_array))

    if not iterate_each_vertex:
        skin_fn.setWeights(mesh_dag,
                           component_fn,
                           joint_int_array,
                           weights_dbl_array,
                           False)

    else:
        inPointArray = api0.MPointArray()
        mesh_fn.getPoints(inPointArray)
        wgts = api0.MDoubleArray(num_influences)
        infPaths = api0.MDagPathArray()
        inIntArray = api0.MIntArray(skin_fn.influenceObjects(infPaths))
        mItVtx = api0.MItMeshVertex(mesh_dag)

        for vert_id, weight_values in data.items():
            for inf_num in range(num_influences):
                print(weight_values[unicode(inf_num)], inf_num)
                wgts.set(weight_values[unicode(inf_num)], inf_num)

            for i in range(inPointArray.length()):
                if mItVtx.index() == int(vert_id):
                    comp = mItVtx.currentItem()
                    skin_fn.setWeights(mesh_dag, comp, inIntArray, wgts, False)
                    break
                mItVtx.next()

    cmds.undoInfo(state=True)
    RIG_LOG.info("[Set MFnSkin] :: Finished.")
    return True
