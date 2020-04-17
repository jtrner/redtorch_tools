
def get_blendshape_data(blendshape):
    blendshape_functions = oma.MFnBlendShapeDeformer(blendshape)
    base_meshs = om.MObjectArray()
    blendshape_functions.getBaseObjects(base_meshs)
    group_index_list = om.MIntArray()
    blendshape_functions.weightIndexList(group_index_list)
    base_mesh_names = []
    group_data = []
    base_meshs = []
    for s in range(base_meshs.length()):
        base_mesh = base_meshs[s]
        base_mesh_names.append(get_selection_string(base_mesh))
        base_meshs.append(base_mesh)

    inbetween_weights = dict()
    for s in range(base_meshs.length()):
        index_array = om.MIntArray()
        for g in range(group_index_list.length()):
            blendshape_functions.targetItemIndexList(g, base_meshs[s], index_array)
            for i in range(index_array.length()):
                inbetween_weights.setdefault(s, []).append(float(index_array[i] - 5000) / 1000)
    print inbetween_weights

    for g in range(group_index_list.length()):
        group_index = group_index_list[g]
        inbetween_data = dict()

        for inbetween_weight in inbetween_weights[g]:
            inbetween_targets = []
            for s, base_mesh in enumerate(base_meshs):
                targets = om.MObjectArray()
                blendshape_functions.getTargets(base_mesh, g, targets)
                inbetween_targets.append(get_selection_string(mesh))
            inbetween_data[inbetween_weight] = inbetween_targets

        group_data.append(dict(
            index=group_index,
            inbetweens=inbetween_data,
            weight=blendshape_functions.weight(g)
        ))
    return dict(
        base_mesh_names=base_mesh_names,
        groups=group_data
    )


