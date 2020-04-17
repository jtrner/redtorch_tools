import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya_tools.utilities.mesh_utilities as mhu

spaces = dict(
    local=oma.MFnBlendShapeDeformer.kLocalOrigin,
    world=oma.MFnBlendShapeDeformer.kWorldOrigin
)


def create_blendshape(*geometry, **kwargs):

    # NOTE it would be better to set this up in API, but that will mean doing paralell setup manually in faceNetwork
    """
    setup kwargs to pass on
    """
    mc.select(cl=True)


    blendshape = mc.createNode(
        'blendShape',
        name=kwargs.get('name', 'blendShape')
    )
    parallel = kwargs.get('parallel', True)

    mc.blendShape(
        blendshape,
        e=True,
        parallel=parallel,
        geometry=geometry
    )
    #if parallel:
    #    mc.blendShape(
    #        blendshape,
    #        e=True,
    #        parallel=True
    #    )
    return get_m_object(blendshape)


def add_base_geometry(blendshape, *geometry):
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    for m_object in geometry:
        blendshape_functions.addBaseObject(m_object)


def add_target(blendshape, base_geometry, group_index, target_geometry, weight_value):
    if weight_value is None or weight_value == 0.0:
        raise Exception('Weight is %s' % weight_value)
    weight_value = round(float(weight_value), 3)
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    existing_weights = []
    for index in range(blendshape_functions.numWeights()):
        existing_weights.append(blendshape_functions.weight(index))

    blendshape_functions.addTarget(
        base_geometry,
        group_index,
        target_geometry,
        weight_value
    )


def list_targets(blendshape, index):
    result = []
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    base_objects = om.MObjectArray()
    blendshape_functions.getBaseObjects(base_objects)
    for t in range(base_objects.length()):
        base_mesh = base_objects[t]
        indices = om.MIntArray()
        blendshape_functions.weightIndexList(indices)
        item_array = om.MIntArray()
        blendshape_functions.targetItemIndexList(index, base_mesh, item_array)
        targets = om.MObjectArray()
        blendshape_functions.getTargets(base_mesh, index, targets)
        result.extend([targets[i] for i in range(targets.length())])
    return result


def clear_group_targets(blendshape, index):

    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    base_objects = om.MObjectArray()
    blendshape_functions.getBaseObjects(base_objects)
    indices = om.MIntArray()
    blendshape_functions.weightIndexList(indices)

    if index in list(indices):
        for t in range(base_objects.length()):
            base_mesh = base_objects[t]
            indices = om.MIntArray()
            blendshape_functions.weightIndexList(indices)
            targets = om.MObjectArray()
            blendshape_functions.getTargets(
                base_mesh,
                index,
                targets
            )
            inbetween_array = om.MIntArray()
            blendshape_functions.targetItemIndexList(
                index,
                base_mesh,
                inbetween_array
            )
            for i in range(inbetween_array.length()):
                mesh_name = get_selection_string(targets[i])
                mc.showHidden(mesh_name)
                weight = (float(inbetween_array[i]) - 5000) / 1000.0
                blendshape_functions.removeTarget(
                    base_objects[t],
                    index,
                    targets[i],
                    weight
                )
                mesh_name = get_selection_string(targets[i])


def clear_targets(blendshape):
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    base_objects = om.MObjectArray()
    blendshape_functions.getBaseObjects(base_objects)
    indices = om.MIntArray()
    blendshape_functions.weightIndexList(indices)
    for index in indices:
        clear_group_targets(blendshape, index)


def remove_target(blendshape, base_geometry, group_index, target_geometry, weight_value):
    if weight_value is None or weight_value == 0.0:
        raise Exception('Weight is %s' % weight_value)
    weight_value = round(float(weight_value), 3)
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    existing_weights = []
    for index in range(blendshape_functions.numWeights()):
        existing_weights.append(blendshape_functions.weight(index))
    oma.MFnBlendShapeDeformer(blendshape).removeTarget(
        base_geometry,
        group_index,
        target_geometry,
        weight_value
    )


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    selection_list = om.MSelectionList()
    selection_list.add(str(node))
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


def get_geom_index(geometry, deformer):
    '''
    Returns the geometry index of a shape to a specified deformer.
    @param geometry: Name of shape or parent transform to query
    @type geometry: str
    @param deformer: Name of deformer to query
    @type deformer: str
    '''
    # Check geometry
    geo = geometry
    if mc.objectType(geometry) == 'transform':
        try:
            geometry = mc.listRelatives(geometry, s=True, ni=True, pa=True)[0]
        except:
            raise Exception('Object "' + geo + '" is not a valid geometry!')
    geom_obj = get_m_object(geometry)

    # Get geometry index
    deformer_obj = get_m_object(deformer)
    deformer_fn = oma.MFnGeometryFilter(deformer_obj)
    try:
        geom_index = deformer_fn.indexForOutputShape(geom_obj)
    except:
        raise Exception('Object "' + geometry + '" is not affected by deformer "' + deformer + '"!')

    return geom_index


def get_target_shape_index(blendshape, target_shape_name):
    '''
    Provide a string of the target name you wish to get the index number from the blendshape node.
    :param blendshape: str(), Name of the blendshape node
    :param target_shape_name: str(), Name of the target shape in the blendshape node.
    :return: int(), Index of the target shape in the blendshape node.
    '''
    aliasList = mc.aliasAttr(blendshape, q=True)
    aliasTarget = aliasList[(aliasList.index(target_shape_name) + 1)]
    targetIndex = aliasTarget.split('[')[-1]
    targetIndex = int(targetIndex.split(']')[0])
    return targetIndex


def get_base_weights(blend_shape_node, geo_index=0):
    geometry = mc.blendShape(blend_shape_node, q=True, geometry=True)
    base_mesh = geometry[geo_index]
    number_of_vtx = mc.polyEvaluate(base_mesh, v=True)
    weight_dict = {}
    for vtx in range(number_of_vtx):
        m_plug = om.MPlug()
        sl = om.MSelectionList()
        sl.add("%s.inputTarget[%s].baseWeights" % (blend_shape_node, geo_index))
        sl.getPlug(0, m_plug)
        weight = m_plug.elementByLogicalIndex(vtx).asFloat()
        index = m_plug.elementByPhysicalIndex(vtx).logicalIndex()
        weight_dict[index] = weight
    return weight_dict


def set_base_weights(blend_shape_node, geo_index=0, weights_data=None):
    for index, weight in weights_data.iteritems():
        m_plug = om.MPlug()
        sl = om.MSelectionList()
        sl.add("%s.inputTarget[%s].baseWeights" % (blend_shape_node, geo_index))
        sl.getPlug(0, m_plug)
        m_plug.elementByLogicalIndex(index).setFloat(weight)


def get_target_weights(base_mesh, blend_shape_node, geo_index=0, target_shape_index=0):
    '''
    Get the blendshape weight value for each index
    :param base_mesh: str(), Name of base mesh.
    :param blend_shape_node: type(Blendshape), Blendshape node , instance of BlendshapeController
    :param geo_index: int(), Input target geo index
    :param target_shape_index: int(), Input target geo shape index
    :return:
    '''
    # Get weights
    weight_dict = {}
    number_of_vtx = mc.polyEvaluate(base_mesh, v=True)
    for vtx in range(number_of_vtx):
        m_plug = om.MPlug()
        sl = om.MSelectionList()
        sl.add('%s.inputTarget[%s].inputTargetGroup[%s].targetWeights' % (
            blend_shape_node,
            geo_index,
            target_shape_index
        ))
        sl.getPlug(0, m_plug)
        weight = m_plug.elementByLogicalIndex(vtx).asFloat()
        index = m_plug.elementByPhysicalIndex(vtx).logicalIndex()
        weight_dict[index] = weight
    return weight_dict


def set_target_weights(blend_shape_node, geo_index=0, target_shape_index=0, weights_data=None):
    '''
    Set per vertex target weights for the specified blendShape target
    @param blend_shape_node: Blendshape node object to set target weights for
    @type blend_shape_node: type(Blendshape)
    @param geo_index: int(), Input target geo index
    @param target_shape_index: Index of the target shape in the blendShape node to set weights for
    @type target_shape_index: int
    @param wt: Weight value list to apply to the specified blendShape target
    @type wt: list
    @param weights_data: Dictionary of the vtx number as key, and a float value between 0.0 and 1.0 of the blendshape
    weight.
    @type geometry: dict
    '''
    # Set target weights
    for index, weight in weights_data.iteritems():
        m_plug = om.MPlug()
        sl = om.MSelectionList()
        sl.add('%s.inputTarget[%s].inputTargetGroup[%s].targetWeights' % (
            blend_shape_node,
            geo_index,
            target_shape_index
        ))
        sl.getPlug(0, m_plug)
        m_plug.elementByLogicalIndex(index).setFloat(weight)


def mirror_blend_shape_weights(base_mesh,
                               base_blend_shape,
                               base_geo_index=0,
                               base_blend_shape_index=0,
                               target_mesh=None,
                               target_blend_shape=None,
                               target_geo_index=None,
                               target_blend_shape_index=None,
                               positive_to_negative_x=True,
                               weights_data=None,
                               mirrored_indices=None):
    '''
    Copy the same vertex value of the blendshape weights to the flip side of x axis.
    :param base_mesh: str(), Name of the geometry to source from.
    :param base_blend_shape: type(Blendshape), Source blendshape node.
    :param base_geo_index: int(), Source input target geo index
    :param base_blend_shape_index: int(), Index of the source shape name in the blendshape node.
    :param target_blend_shape: type(Blendshape), Blendshape node. If not specified, it will be the same as the source.
    :param target_mesh: str(), Name of the geometry to target to.
    :param target_geo_index: int(), Target input target geo index
    :param target_blend_shape_index: int(), Index of the target shape name in the target blendshape node. If not
    specified, it will be the same as the source.
    :param positive_to_negative_x: bool(), If copying from negative x to positive x, set to False.
    :param weights_data: dict(), with the index number as the key and float from 0.0 to 1.0 as the definition. If not
    specified, it will get the data from the source mesh and blendshape node.
    :param mirrored_indices: list(), The corresponding vertex on the mirrored x axis vtx indicies.
    :return:
    '''
    # if target mesh args not provided, set them to base mesh. Therefore the mirror will happen to itself(mesh).
    if not target_mesh:
        target_mesh = base_mesh
    if not target_blend_shape:
        target_blend_shape = base_blend_shape
    if not target_geo_index:
        target_geo_index = base_geo_index
    if not target_blend_shape_index:
        target_blend_shape_index = base_blend_shape_index

    if not mirrored_indices:
        mirrored_indices = mhu.get_mirror_index_list(base_mesh, target_mesh)

    if not weights_data:
        weights_data = get_target_weights(base_mesh, base_blend_shape, base_geo_index, base_blend_shape_index)
        vtx_count = mc.polyEvaluate(target_mesh, v=True)
        set_weights_data = {}
        for i in range(vtx_count):
            vtx_position = mc.pointPosition('{0}.vtx[{1}]'.format(target_mesh, i), local=True)
            if (positive_to_negative_x and vtx_position[0] > 0.0) or (not positive_to_negative_x and vtx_position[0] < 0.0):
                set_weights_data[i] = weights_data[mirrored_indices[i]]
    else:
        set_weights_data = weights_data

    set_target_weights(target_blend_shape, target_geo_index, target_blend_shape_index, set_weights_data)


def flip_blend_shape_weights(base_mesh,
                             base_blend_shape,
                             base_geo_index=0,
                             base_blend_shape_index=0,
                             target_mesh=None,
                             target_blend_shape=None,
                             target_geo_index=None,
                             target_blend_shape_index=None,
                             weights_data=None,
                             mirrored_indices=None):
    '''
    Flips the vertex values of the blendshape weights on the x axis.
    :param base_mesh: str(), Name of the geometry to source from.
    :param base_blend_shape: str(), Name of the source blendshape node name.
    :param base_geo_index: int(), Source input target geo index
    :param base_blend_shape_index: int(), Name of the source shape name in the blendshape node.
    :param target_mesh: str(), Name of the geometry to target to.
    :param target_blend_shape: str(), Name of the target blendshape node. If not specified, it will be the same as the
    source.
    :param target_geo_index: int(), Target input target geo index
    :param target_blend_shape_index: str(), Name of the target shape name in the target blendshape node. If not
    specified, it will be the same as the source.
    :param weights_data: dict(), with the index number as the key and float from 0.0 to 1.0 as the definition. If not
    specified, it will get the data from the source mesh and blendshape node.
    :param mirrored_indices: list(), The corresponding vertex on the mirrored x axis vtx indicies.
    :return:
    '''
    # if target mesh args not provided, set them to base mesh. Therefore the flip will happen to itself(base_mesh).
    if not target_mesh:
        target_mesh = base_mesh
    if not target_blend_shape:
        target_blend_shape = base_blend_shape
    if not target_geo_index:
        target_geo_index = base_geo_index
    if not target_blend_shape_index:
        target_blend_shape_index = base_blend_shape_index
    if not mirrored_indices:
        mirrored_indices = mhu.get_mirror_index_list(base_mesh, target_mesh)

    if not weights_data:
        weights_data = get_target_weights(base_mesh, base_blend_shape, base_geo_index, base_blend_shape_index)
        vtx_count = mc.polyEvaluate(target_mesh, v=True)
        set_weights_data = {}
        for i in range(vtx_count):
            set_weights_data[i] = weights_data[mirrored_indices[i]]
    else:
        set_weights_data = weights_data

    set_target_weights(target_blend_shape, target_geo_index, target_blend_shape_index, set_weights_data)


def transfer_blend_shape_weights(base_mesh,
                                 base_blend_shape,
                                 base_geo_index=0,
                                 base_blend_shape_index=0,
                                 target_mesh=None,
                                 target_blend_shape=None,
                                 target_geo_index=None,
                                 target_blend_shape_index=None,
                                 weights_data=None,
                                 indices=None,
                                 world_space=True):
    # if target mesh args not provided, set them to base mesh. Therefore the flip will happen to itself(base_mesh).
    if not target_mesh:
        target_mesh = base_mesh
    if not target_blend_shape:
        target_blend_shape = base_blend_shape
    if not target_geo_index:
        target_geo_index = base_geo_index
    if not target_blend_shape_index:
        target_blend_shape_index = base_blend_shape_index
    if not indices:
        indices = mhu.get_closest_index_list(base_mesh, target_mesh, world_space)

    if not weights_data:
        weights_data = get_target_weights(base_mesh, base_blend_shape, base_geo_index, base_blend_shape_index)
        vtx_count = mc.polyEvaluate(target_mesh, v=True)
        set_weights_data = {}
        for i in range(vtx_count):
            set_weights_data[i] = weights_data[indices[i]]
    else:
        set_weights_data = weights_data

    set_target_weights(target_blend_shape, target_geo_index, target_blend_shape_index, set_weights_data)
