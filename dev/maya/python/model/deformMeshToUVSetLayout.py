def deformMeshToUVSetLayout():
    # get the active selection
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selection )
    #iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
    iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kGeometric)

    # go through selection
    while not iterSel.isDone():
        # get dagPath
        dagPath = OpenMaya.MDagPath()
        iterSel.getDagPath( dagPath )

        # create empty point array & float arrays
        inMeshMPointArray = OpenMaya.MPointArray()
        U_MFloatArray = OpenMaya.MFloatArray()
        V_MFloatArray = OpenMaya.MFloatArray()
        vertexCountMIntArray = OpenMaya.MIntArray()
        vertexListMIntArray = OpenMaya.MIntArray()
        uvCountsMIntArray = OpenMaya.MIntArray()
        uvIdsMIntArray = OpenMaya.MIntArray()

        # create function set, get points in world space & UVs
        meshFn = OpenMaya.MFnMesh(dagPath)
        meshFn.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)
        meshFn.getUVs(U_MFloatArray, V_MFloatArray)
        meshFn.getVertices(vertexCountMIntArray, vertexListMIntArray)
        meshFn.getAssignedUVs (uvCountsMIntArray, uvIdsMIntArray)

        # write UV postions to inMeshMPointArray
        for i in range( vertexListMIntArray.length() ):
            inMeshMPointArray[vertexListMIntArray[i]].x = U_MFloatArray[uvIdsMIntArray[i]]
            inMeshMPointArray[vertexListMIntArray[i]].y = V_MFloatArray[uvIdsMIntArray[i]]
            inMeshMPointArray[vertexListMIntArray[i]].z = 0

        # apply new point positions to mesh
        meshFn.setPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)

        iterSel.next()