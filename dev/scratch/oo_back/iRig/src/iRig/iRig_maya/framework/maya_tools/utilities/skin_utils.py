import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import decorators as dec
import maya.cmds as mc


def get_mesh_fn(node_name):
    """
    Grabs the MFnMesh of the specified node.
    :param node_name: <str> node name.
    :return: <om.MFnMesh> if successful, <bool> False if fail.
    """
    sel = om.MSelectionList()
    sel.add(node_name)
    m_dag = om.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(om.MFn.kMesh):
        return False
    return om.MFnMesh(m_dag), m_dag


def get_curve_fn(node_name):
    """
    Grabs the MFnNurbsCurve of the specified node.
    :param node_name: <str> node name.
    :return: <om.MFnNurbsCurve> if successful, <bool> False if fail.
    """
    sel = om.MSelectionList()
    sel.add(node_name)
    m_dag = om.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(om.MFn.kNurbsCurve):
        return False
    return om.MFnNurbsCurve(m_dag)


def get_nurb_fn(node_name):
    """
    Grabs the MFnNurbsCurve of the specified node.
    :param node_name: <str> node name.
    :return: <om.MFnNurbsSurface> if successful, <bool> False if fail.
    """
    sel = om.MSelectionList()
    sel.add(node_name)
    m_dag = om.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(om.MFn.kNurbsSurface):
        return False
    return om.MFnNurbsSurface(m_dag)


def get_lattice_fn(node_name):
    """
    Grabs the MFnNurbsCurve of the specified node.
    :param node_name: <str> node name.
    :return: <om.MFnNurbsSurface> if successful, <bool> False if fail.
    """
    sel = om.MSelectionList()
    sel.add(node_name)
    m_dag = om.MDagPath()
    sel.getDagPath(0, m_dag)
    if not m_dag.hasFn(om.MFn.kLattice):
        return False
    return om.MFnLattice(m_dag)


def get_node_fn(obj_name=""):
    """
    Returns the node fn.
    :param obj_name: <str> provide object name.
    :return: <om.MFn.kNodeType> o_node.
    """
    if not obj_name:
        return False
    o_node, o_dag = get_mesh_fn(obj_name)
    if not o_node:
        o_node = get_curve_fn(obj_name)
    if not o_node:
        o_node = get_nurb_fn(obj_name)
    if not o_node:
        o_node = get_lattice_fn(obj_name)
    return o_node


def get_skin_cluster_obj(obj_name=""):
    """
    Gets the skin cluster name from the object specified.
    :param obj_name: <str> object name to find the skinCluster from.
    :return: <str> skin cluster name, <om.MFnSkinCluster> skin_fn if successful, <bool> False if fail.
    """
    if not obj_name:
        return False
    o_node = get_node_fn(obj_name)
    o_path = o_node.dagPath()
    m_obj = o_path.node()
    skin_fn = __get_skin_fn(m_obj)
    if skin_fn:
        return skin_fn
    else:
        return False


def object_exists(name):
    """
    Verify the existence of the object provided.
    :param name: <str> object name.
    :return: <bool> True if successful, <bool> False for failure.
    """
    iter_nodes = om.MItDependencyNodes()
    while not iter_nodes.isDone():
        obj = iter_nodes.thisNode()
        depend_fn = om.MFnDependencyNode(obj)
        if depend_fn.name() == name:
            return True
        iter_nodes.next()
    return False


def __get_skin_influences(skin_fn=None):
    """
    Returns a list of all influecnes acting on this skin cluster.
    :param skin_fn: <MFnSkinCluster> skin function class.
    :return: <list> influences, <bool> False for failure.
    """
    m_dag_path_array = om.MDagPathArray()
    skin_fn.influenceObjects(m_dag_path_array)
    joints = list(m_dag_path_array)
    joints = [j for j in joints if mc.objectType(j) == 'joint']
    return joints


def __get_skin_components(skin_fn=None):
    """
    Gets the skin cluster components.
    :param skin_fn: <om.MFnSkinCluster> object.
    :return: <MDagPath> dag_path, <MObject> components.
    """
    mfn_set = om.MFnSet(skin_fn.deformerSet())
    mfn_set_members = om.MSelectionList()
    mfn_set.getMembers(mfn_set_members, False)
    dag_path = om.MDagPath()
    m_comp_obj = om.MObject()
    mfn_set_members.getDagPath(0, dag_path, m_comp_obj)
    return dag_path, m_comp_obj


def __get_skin_fn(node):
    """
    Gets the MFnSkinCluster from the MObject specified.
    :param node: <MObject> node to look at.
    :return: <MFnSkinCluster> if successful, <bool> False if fail.
    """
    skin_fn = False
    it_dg = om.MItDependencyGraph(node,
                                  om.MItDependencyGraph.kDownstream,
                                  om.MItDependencyGraph.kPlugLevel)
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        if cur_item.hasFn(om.MFn.kSkinClusterFilter):
            skin_fn = oma.MFnSkinCluster(cur_item)
            break
        it_dg.next()
    return skin_fn


def get_affecting_geometry(o_skin=None):
    """
    Gets the Mesh object from the MFnSkinCluster specified.
    :param node: <MObject> node to look at.
    :return: <MObject>, <MFn> <MDagPath>.
    """
    skin_name = o_skin.name()
    sel = om.MSelectionList()
    sel.add(skin_name)
    node = om.MObject()
    sel.getDependNode(0, node)

    it_dg = om.MItDependencyGraph(node,
                                  om.MItDependencyGraph.kDownstream,
                                  om.MItDependencyGraph.kDepthFirst,
                                  om.MItDependencyGraph.kPlugLevel)
    m_dag = om.MDagPath()
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()

        # kDagNode
        if cur_item.hasFn(om.MFn.kDagNode):
            om.MDagPath.getAPathTo(cur_item, m_dag)

        # MFnMesh
        if cur_item.hasFn(om.MFn.kMesh):
            o_node = om.MFnMesh(cur_item)
            break

        # MFnNurbsCurve
        if cur_item.hasFn(om.MFn.kNurbsCurve):
            o_node = om.MFnNurbsCurve(cur_item)
            break

        # MFnNurbsSurface
        if cur_item.hasFn(om.MFn.kNurbsCurve):
            o_node = om.MFnNurbsSurface(cur_item)
            break

        # MFnLattice
        if cur_item.hasFn(om.MFn.kLattice):
            o_node = om.MFnLattice(cur_item)
            break

        # next item in the graph
        it_dg.next()

    return cur_item, o_node, m_dag


def get_skin_blend_weights(o_skin=None):
    """
    Get MFnSkinCluster Dual Quaternion blend weights weights array.
    :param skin_fn: <MFnSkinCLuster> skin cluster function class object.
    :return: <list> blendWeights double list array. <bool> False if list is empty.
    """
    # get the variable data
    weights_array = om.MDoubleArray()
    weight_length = weights_array.length()
    obj_dag_path, obj_component = __get_skin_components(skin_fn=skin_fn)

    # procure the blend weight component data
    o_skin.getBlendWeights(obj_dag_path, obj_component, weights_array)
    blend_weights_array = [weights_array[i] for i in range(weight_length)]
    values_list = list(filter(lambda x: x < 0.0, blend_weights_array))
    if values_list:
        return blend_weights_array
    else:
        return False


def get_skin_influences(skin_cls=None):
    """
    Grabs all influence node_objects acting on this skin node.
    :param skin_cls: <class> Object.
    :return: <list> influences.
    """
    o_skin = skin_cls.m_object
    skin_fn = oma.MFnSkinCluster(o_skin)
    return __get_skin_influences(skin_fn)


def set_skin_blend_weights(o_skin=None, blend_weight_data=None):
    """
    Sets the blend weights skin data.
    :param skin_fn: <MFnSkinCLuster> skin cluster function class object.
    :param weight_data: <list> weight values.
    :return: True for success. False for failure.
    """
    # get current skin components
    obj_dag_path, obj_component = __get_skin_components(skin_fn=skin_fn)

    m_blendweights = om.MDoubleArray(len(blend_weight_data))
    for i, w in enumerate(blend_weight_data):
        m_blendweights.set(w, i)
    skin_fn.setBlendWeights(obj_dag_path, obj_component, m_blendweights)
    return True


def set_skin_blend_weights(skin_cls=None):
    """
    returns the skin blend weight data.
    :param skin_cls: <class> object.
    :param weight_data: <list> weight values.
    :return: <list> blend weights, <bool> False for nothing.
    """
    o_skin = skin_cls.m_object
    m_weight_data = skin_cls.blend_weight_data
    skin_fn = oma.MFnSkinCluster(o_skin)
    return set_blend_weights(skin_fn=skin_fn, weight_data=m_weight_data)


def get_skin_blend_weights(skin_cls=None):
    """
    returns the skin blend weight data.
    :param skin_cls: <class> object.
    :return: <list> blend weights, <bool> False for nothing.
    """
    o_skin = skin_cls.m_object
    skin_fn = oma.MFnSkinCluster(o_skin)
    return __get_blend_weights_array(skin_fn=skin_fn)


def set_skin_weights(skin_cls=None):
    """
    Accepts the skin class module.
    :param skin_cls: <class> skin.
    :return: <bool> True for success. <bool> False for failure.
    """
    o_skin = skin_cls.m_object
    weight_data = skin_cls.weight_data

    if not weight_data or not isinstance(weight_data, dict):
        om.MGlobal.displayError("[Set Weights Error] :: Please supply vertex weight data dictionary.")
        return False

    # set the skin cluster with the weight information
    return set_weights(o_skin=o_skin, weight_data=weight_data)


def set_weights(m_object, weights):
    """
    Set the skin weights with the weight vertex index information given.
    :param o_skin: <MObject> skinCluster object.
    :param weight_data: <dict> weight data.
    :return: <bool> True for success. <bool> False for failure.
    """
    skin_fn = oma.MFnSkinCluster(m_object)
    m_obj, o_node, o_dag = get_affecting_geometry(skin_fn)
    mesh_iterator = om.MItMeshVertex(o_dag)
    old_weights_array = om.MDoubleArray()
    geometry_iterator = om.MItGeometry(o_dag)
    o_type = m_obj.apiTypeStr()
    while not geometry_iterator.isDone():
        new_weights_array = om.MDoubleArray()
        vertex_int = mesh_iterator.index()
        influence_indices = om.MIntArray()
        if 'kMesh' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
        elif 'kNurbsSurface' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kSurfaceCVComponent)
        elif 'kNurbsCurve' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kCurveCVComponent)
        elif 'kLattice' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kLatticeComponent)
        else:
            raise Exception('Invalid type')
        om.MFnSingleIndexedComponent(component).addElement(vertex_int)
        weight_array = weights[vertex_int]
        for idx, i_num in enumerate(weight_array):
            influence_indices.append(idx)
            new_weights_array.append(0.0)
            old_weights_array.append(0.0)
            new_weights_array[idx] += i_num
        skin_fn.setWeights(o_dag, component, influence_indices, new_weights_array, 0, old_weights_array)
        geometry_iterator.next()
    return True

def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]

@dec.m_object_arg
def get_skin_weights(m_object):
    """
    Get mesh vertex component weights.
    :param mesh_name: <str> mesh object name.
    :return: <dict> weighting data.
    """
    return get_skin_weights_by_component(m_object)

@dec.m_object_arg
def get_skin_weights_by_component(m_object):
    """
    Gets the skin cluster data by vertex component.
    :param o_skin: <MObject> Skin Cluster.
    :return: <dict> weight information.
    """
    # get the MFnSkinCluster for skin_obj
    if 'apiTypeStr' in dir(m_object):
        skin_fn = oma.MFnSkinCluster(m_object)
    else:
        skin_fn = m_object
    weight_data = {}
    m_obj, o_node, o_dag = get_affecting_geometry(skin_fn)

    influences_path_array = om.MDagPathArray()
    len_of_influences = influences_path_array.length()
    skin_fn.influenceObjects(influences_path_array)
    influence_objects = []
    for inf_i in xrange(len_of_influences):
        m_dag = influences_path_array[inf_i]
        if m_dag.hasFn(om.MFn.kJoint):
            influence_objects.extend(m_dag.fullPathName())
        else:
            raise RuntimeError("[Get Skin Error] :: Non-Joint Influences: {}".format(m_dag.partialPathName()))

    # get the vertex data
    weights_array = om.MDoubleArray()
    m_util = om.MScriptUtil()
    influences_int = m_util.asUintPtr()

    # create an iterator to query every point weights by index
    m_it = om.MItGeometry(o_dag)
    o_type = m_obj.apiTypeStr()
    while not m_it.isDone():
        vertex_int = m_it.index()
        if 'Mesh' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
        if 'NurbsSurface' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kSurfaceCVComponent)
        if 'NurbsCurve' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kCurveCVComponent)
        if 'Lattice' in o_type:
            component = om.MFnSingleIndexedComponent().create(om.MFn.kLatticeComponent)
        om.MFnSingleIndexedComponent(component).addElement(vertex_int)
        skin_fn.getWeights(o_dag, component, weights_array, influences_int)
        weight_data[vertex_int] = list(weights_array)
        m_it.next()
    return weight_data

@dec.m_object_arg
def set_weights_by_logical_index(m_object, weight_data={}):
    """
    Sets the weights generated by logical index.
    :param o_skin: <MFnSkinCluster>
    :return: <bool> True for success. <bool> False for failure.
    """
    skin_name = m_object.name()
    for vert_id, inf_weights in weight_data.items():
        wl_attr = '%s.weightList[%s]' % (skin_name, vert_id)
        for inf_id, inf_value in inf_weights.items():
            wAttr = '.weights[%s]' % inf_id
            mc.setAttr(wl_attr + wAttr, inf_value)
    return True

@dec.m_object_arg
def get_skin_weights_by_logical_index(m_object):
    """
    Exports skinCluster as a dictionary.
    :param mesh_name: <str> the mesh string to export skinCluster from.
    :return: <dict> skin weights. <bool> False for failure.
    """
    weights_data = {}

    # get the MFnSkinCluster for skin_obj
    if 'apiTypeStr' in dir(m_object):
        skin_fn = oma.MFnSkinCluster(m_object)
    else:
        skin_fn = m_object
    # get the MDagPath for all influence
    inf_dags = om.MDagPathArray()
    skin_fn.influenceObjects(inf_dags)

    # get the MPlug for the weightList and weights attributes
    weight_ls_plug = skin_fn.findPlug('weightList')
    weights_plug = skin_fn.findPlug('weights')
    weights_ls_attr = weight_ls_plug.attribute()
    weights_attr = weights_plug.attribute()
    weight_ids = om.MIntArray()

    # get the index id for influence object
    inf_ids = {}
    for x in xrange(inf_dags.length()):
        inf_path = inf_dags[x].fullPathName()
        inf_id = int(skin_fn.indexForInfluenceObject(inf_dags[x]))
        inf_ids[inf_id] = x

    # build the dictionary where vertex_id is the key
    for v_id in xrange(weight_ls_plug.numElements()):
        val_weights = {}
        weights_plug.selectAncestorLogicalIndex(v_id, weights_ls_attr)
        weight_ls_plug.getExistingArrayAttributeIndices(weight_ids)

        # create a copy of the current weights_plug
        inf_plug = om.MPlug(weights_plug)

        for inf_id in weight_ids:
            # tell the inf_plug it represents the current influence id
            inf_plug.selectAncestorLogicalIndex(inf_id, weights_attr)

            # add this influence and its weight to this verts weights
            if inf_ids.has_key(inf_id):
                val_weights[inf_ids[inf_id]] = inf_plug.asDouble()
        weights_data[v_id] = val_weights
    return weights_data


def skin_as(skin_cls=None, target_objects=[]):
    """
    Binds the target geo with the same skinning as the source geo.
    :param rename_skin: <bool> if set to True, renames the skinCluster based on the target mesh.
    :return: <bool> True for success. <bool> False for fail.
    """
    o_skin = skin_cls.m_object
    o_geom = skin_cls.geometry

    # get skinCluster node
    skin_cls_node = om.MFnSkinCluster(o_skin)
    if not skin_cls_node:
        om.MGlobal.displayError("[Skin As Error] :: No skin found {}".format(o_geom))
        return False

    # get the joints affecting the skin node
    joints = __get_skin_influences(skin_fn=skin_cls_node)

    # bind the target sdk_objects to the source skin and copy the weights to the target object.
    for target in target_objects:
        skin_name = mc.skinCluster(target, joints, tsb=1)[0]
        mc.copySkinWeights(ss=skin_cls_node, ds=skin_name, noMirror=1,
                             influenceAssociation=("closestJoint", "oneToOne", "name"),
                             surfaceAssociation="closestComponent")
        if ":" in target:
            target = target.split(':')[-1]
        skin_name = target + '_Skin'
        mc.rename(skin_name, skin_name)
    om.MGlobal.displayInfo("[Skin As] :: Completed {}".format(skin_name))
    return True

def getWeights(skin_cluster):
    skin_name = get_selection_string(skin_cluster)
    geometry = mc.skinCluster(skin_name, q=True, geometry=True)
    influences = mc.skinCluster(skin_name, q=True, influence=True)

    clusterName = skin_name
    weightsList = []
    for shapeName in geometry:
        # poly mesh and skinCluster name

        # get the MFnSkinCluster for clusterName
        selList = om.MSelectionList()
        selList.add(clusterName)
        clusterNode = om.MObject()
        selList.getDependNode(0, clusterNode)
        skinFn = oma.MFnSkinCluster(clusterNode)

        # get the MDagPath for all influence
        infDags = om.MDagPathArray()
        skinFn.influenceObjects(infDags)

        # create a dictionary whose key is the MPlug indice id and
        # whose value is the influence list id
        infIndexs = {}
        infs = []
        for x in xrange(infDags.length()):
            infPath = infDags[x].fullPathName()
            infIndex = int(skinFn.indexForInfluenceObject(infDags[x]))
            infIndexs[infIndex] = x
            infs.append(infPath)

        # get the MPlug for the weightList and weights attributes
        wlPlug = skinFn.findPlug('weightList')
        wPlug = skinFn.findPlug('weights')
        wlAttr = wlPlug.attribute()
        wAttr = wPlug.attribute()
        wInfIds = om.MIntArray()

        # the weights are stored in dictionary, the key is the vertId,
        # the value is another dictionary whose key is the influence id and
        # value is the weight for that influence
        weights = {}
        for vId in xrange(wlPlug.numElements()):
            vWeights = {}
            # tell the weights attribute which vertex id it represents
            wPlug.selectAncestorLogicalIndex(vId, wlAttr)

            # get the indice of all non-zero weights for this vert
            wPlug.getExistingArrayAttributeIndices(wInfIds)

            # create a copy of the current wPlug
            infPlug = om.MPlug(wPlug)
            for infIndex in wInfIds:
                # tell the infPlug it represents the current influence id
                infPlug.selectAncestorLogicalIndex(infIndex, wAttr)

                # add this influence and its weight to this verts weights
                try:
                    vWeights[infIndexs[infIndex]] = infPlug.asDouble()
                except KeyError:
                    print 'Warning! An influence seems to have been removed skin cluster at index--->>', infIndex
                    # assumes a removed influence
                    pass
            weights[vId] = vWeights
        weightsList.append(weights)
    return weightsList


def setWeights(skin_cluster, weights):

    skin_name = get_selection_string(skin_cluster)
    geometry = mc.skinCluster(skin_name, q=True, geometry=True)
    influences = mc.skinCluster(skin_name, q=True, influence=True)

    if geometry:
        for itr in range(len(geometry)):
            # poly mesh and skinCluster name
            shapeName = geometry[itr]
            # unlock influences used by skincluster
            for influence in influences:
                mc.setAttr('%s.liw' % influence, False)
            # normalize needs turned off for the prune to work
            skinNorm = mc.getAttr('%s.normalizeWeights' % skin_name)
            if skinNorm != 0:
                mc.setAttr('%s.normalizeWeights' % skin_name, 0)
            mc.skinPercent(skin_name, shapeName, nrm=False, prw=100)
            # restore normalize setting
            if skinNorm != 0:
                mc.setAttr('%s.normalizeWeights' % skin_name, skinNorm)
            for vertId, weightData in weights[itr].items():
                wlAttr = '%s.weightList[%s]' % (skin_name, vertId)
                for infIndex, infValue in weightData.items():
                    wAttr = '.weights[%s]' % infIndex
                    mc.setAttr(wlAttr + wAttr, infValue)