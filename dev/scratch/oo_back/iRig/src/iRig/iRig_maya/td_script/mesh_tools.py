# import standard modules
import sys
import math
import time

# import maya modules
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds


def util_int_array_to_list(array):
    newList = [0] * len(array)
    for i in range(len(array)):
        newList[i] = array[i]
    return newList


def get_component_object(edge=""):
    """
    Grabs the component selected object.
    :param edge: <str> edge selection.
    :return: <MDagPath> selected dag object, <MObject> m object.
    """
    selection = OpenMaya.MSelectionList()
    selection.add(edge)
    dag_sel = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    iter = OpenMaya.MItSelectionList(selection)
    iter.getDagPath(dag_sel, component)
    return dag_sel, component


def analyze_geometry(middle_edge=""):
    """
    Analyzes the geometry by the middle edge selection.
    :param middle_edge: <str> middle edge selection geo.
    :return: data.
    """
    start_time = time.time()
    
    dag_sel, component = get_component_object(middle_edge)
    m_mesh_edge = OpenMaya.MItMeshEdge(dag_sel, component)

    mesh_fn = OpenMaya.MFnMesh(dag_sel)
    point_count = mesh_fn.numVertices()
    edge_count = mesh_fn.numEdges()
    poly_count = mesh_fn.numPolygons()

    base_obj_name = mesh_fn.name()
    m_mesh_edge.reset()
    first_edge = m_mesh_edge.index()

    print(base_obj_name, first_edge, point_count)

    prev_index = 0
    map_array = OpenMaya.MIntArray()
    side_array = OpenMaya.MIntArray()

    checked_vert = OpenMaya.MIntArray()
    side_vert = OpenMaya.MIntArray()
    checked_point = OpenMaya.MIntArray()
    checked_edge = OpenMaya.MIntArray()
    for x in range(point_count):
        checked_vert.append(-1)
        side_vert.append(-1)

    for x in range(edge_count):
        checked_edge.append(-1)

    for x in range(poly_count):
        checked_point.append(-1)

    l_faceList = OpenMaya.MIntArray()
    r_faceList = OpenMaya.MIntArray()

    l_currentP = 0
    l_currentE = 0
    r_currentP = 0
    r_currentE = 0
    vertex_iter = OpenMaya.MItMeshVertex(dag_sel)
    poly_iter = OpenMaya.MItMeshPolygon(dag_sel)
    edge_iter = OpenMaya.MItMeshEdge(dag_sel)

    l_edgeQueue = OpenMaya.MIntArray()
    r_edgeQueue = OpenMaya.MIntArray()

    l_edgeQueue.append(first_edge)
    r_edgeQueue.append(first_edge)

    script_util = OpenMaya.MScriptUtil()
    ptr = script_util.asIntPtr()
    l_edgeVertices = script_util.asInt2Ptr()
    r_edgeVertices = script_util.asInt2Ptr()
    l_ifCheckedVertices = script_util.asInt2Ptr()
    r_faceEdgeVertices = script_util.asInt2Ptr()

    l_faceEdges = []
    r_faceEdges = []
    l_faceEdgesCount = 0
    r_faceEdgesCount = 0

    faceEdgeComponent = OpenMaya.MObject()
    faceEdgeVtxComp = OpenMaya.MFnSingleIndexedComponent()

    num_polygons = mesh_fn.numPolygons()
    connectedEdgesPerFaces = [None] * num_polygons
    edges = OpenMaya.MIntArray()
    
    for i in range(num_polygons):
        poly_iter.setIndex(i, ptr)
        poly_iter.getEdges(edges)
        connectedEdgesPerFaces[i] = list(edges)

    run = True
    while run:
        if not l_currentE or not r_currentE:
            run = False
        l_currentE = l_edgeQueue[0]
        r_currentE = r_edgeQueue[0]

        l_edgeQueue.remove(0)
        r_edgeQueue.remove(0)

        checked_edge[l_currentE] = r_currentE
        checked_edge[r_currentE] = l_currentE

        if l_currentE == r_currentE and l_currentE != first_edge:
            continue

        # get the left face
        edge_iter.setIndex(l_currentE, ptr)
        edge_iter.getConnectedFaces(l_faceList)
        if len(l_faceList) == 1:
            l_currentP = l_faceList[0]
        elif checked_point[l_faceList[0]] == -1 and checked_point[l_faceList[1]] != -1:
            l_currentP = l_faceList[0]
        elif checked_point[l_faceList[1]] == -1 and checked_point[l_faceList[0]] != -1:
            l_currentP = l_faceList[1]
        elif checked_point[l_faceList[0]] == -1 and checked_point[l_faceList[1]] == -1:
            l_currentP = l_faceList[0]
            checked_point[l_currentP] = -2

        # get the right face
        edge_iter.setIndex(r_currentE, ptr)
        edge_iter.getConnectedFaces(r_faceList)
        if len(r_faceList) == 1:
            r_currentP = r_faceList[0]
        elif checked_point[r_faceList[0]] == -1 and checked_point[r_faceList[1]] != -1:
            r_currentP = r_faceList[0]
        elif checked_point[r_faceList[1]] == -1 and checked_point[r_faceList[0]] != -1:
            r_currentP = r_faceList[1]
        elif checked_point[r_faceList[1]] == -1 and checked_point[r_faceList[0]] == -1:
            return OpenMaya.MStatus.kFailure
        elif checked_point[r_faceList[1]] != -1 and checked_point[r_faceList[0]] != -1:
            continue

        checked_point[r_currentP] = l_currentP
        checked_point[l_currentP] = r_currentP

        mesh_fn.getEdgeVertices(l_currentE, l_edgeVertices)
        l_edgeVertices0 = script_util.getInt2ArrayItem(l_edgeVertices, 0, 0)
        l_edgeVertices1 = script_util.getInt2ArrayItem(l_edgeVertices, 0, 1)

        mesh_fn.getEdgeVertices(r_currentE, r_edgeVertices)
        r_edgeVertices0 = script_util.getInt2ArrayItem(r_edgeVertices, 0, 0)
        r_edgeVertices1 = script_util.getInt2ArrayItem(r_edgeVertices, 0, 1)

        if l_currentE == first_edge:
            r_edgeVertices0 = script_util.getInt2ArrayItem(r_edgeVertices, 0, 0)
            r_edgeVertices1 = script_util.getInt2ArrayItem(r_edgeVertices, 0, 1)
            l_edgeVertices0 = script_util.getInt2ArrayItem(l_edgeVertices, 0, 0)
            l_edgeVertices1 = script_util.getInt2ArrayItem(l_edgeVertices, 0, 1)

            checked_vert[l_edgeVertices0] = r_edgeVertices0
            checked_vert[l_edgeVertices1] = r_edgeVertices1
            checked_vert[r_edgeVertices0] = l_edgeVertices0
            checked_vert[r_edgeVertices1] = l_edgeVertices1
        else:
            if checked_vert[l_edgeVertices0] == -1 and checked_vert[r_edgeVertices0] == -1:
                checked_vert[l_edgeVertices0] = r_edgeVertices0
                checked_vert[r_edgeVertices0] = l_edgeVertices0
            if checked_vert[l_edgeVertices1] == -1 and checked_vert[r_edgeVertices1] == -1:
                checked_vert[l_edgeVertices1] = r_edgeVertices1
                checked_vert[r_edgeVertices1] = l_edgeVertices1
            if checked_vert[l_edgeVertices0] == -1 and checked_vert[r_edgeVertices1] == -1:
                checked_vert[l_edgeVertices0] = r_edgeVertices1
                checked_vert[r_edgeVertices1] = l_edgeVertices0
            if checked_vert[l_edgeVertices1] == -1 and checked_vert[r_edgeVertices0] == -1:
                checked_vert[l_edgeVertices1] = r_edgeVertices0
                checked_vert[r_edgeVertices0] = l_edgeVertices1

        side_vert[l_edgeVertices0] = 2
        side_vert[l_edgeVertices1] = 2
        side_vert[r_edgeVertices0] = 1
        side_vert[r_edgeVertices1] = 1

        r_faceEdgesCount = 0
        for edge in connectedEdgesPerFaces[r_currentP]:
            if len(r_faceEdges) > r_faceEdgesCount:
                r_faceEdges[r_faceEdgesCount] = edge
            else:
                r_faceEdges.append(edge)
            r_faceEdgesCount += 1

        l_faceEdgesCount = 0
        for edge in connectedEdgesPerFaces[l_currentP]:
            if len(l_faceEdges) > l_faceEdgesCount:
                l_faceEdges[l_faceEdgesCount] = edge
            else:
                l_faceEdges.append(edge)
            l_faceEdgesCount += 1

        l_checked_vertertex = 0
        l_nonCheckedVertex = 0

        for i in range(l_faceEdgesCount):
            if checked_edge[l_faceEdges[i]] == -1:
                edge_iter.setIndex(l_currentE, ptr)

                if edge_iter.connectedToEdge(l_faceEdges[i]) and l_currentE != l_faceEdges[i]:
                    mesh_fn.getEdgeVertices(l_faceEdges[i], l_ifCheckedVertices)
                    l_ifCheckedVertice0 = script_util.getInt2ArrayItem(l_ifCheckedVertices, 0, 0)
                    l_ifCheckedVertice1 = script_util.getInt2ArrayItem(l_ifCheckedVertices, 0, 1)
                    if l_ifCheckedVertice0 == l_edgeVertices0 or l_ifCheckedVertice0 == l_edgeVertices1:
                        l_checked_vertertex = l_ifCheckedVertice0
                        l_nonCheckedVertex = l_ifCheckedVertice1
                    elif l_ifCheckedVertice1 == l_edgeVertices0 or l_ifCheckedVertice1 == l_edgeVertices1:
                        l_checked_vertertex = l_ifCheckedVertice1
                        l_nonCheckedVertex = l_ifCheckedVertice0
                    else:
                        continue

                    for k in range(r_faceEdgesCount):
                        edge_iter.setIndex(r_currentE, ptr)
                        if edge_iter.connectedToEdge(r_faceEdges[k]) and r_currentE != r_faceEdges[k]:
                            mesh_fn.getEdgeVertices(r_faceEdges[k], r_faceEdgeVertices)
                            r_faceEdgeVertice0 = script_util.getInt2ArrayItem(r_faceEdgeVertices, 0, 0)
                            r_faceEdgeVertice1 = script_util.getInt2ArrayItem(r_faceEdgeVertices, 0, 1)

                            if r_faceEdgeVertice0 == checked_vert[l_checked_vertertex]:
                                checked_vert[l_nonCheckedVertex] = r_faceEdgeVertice1
                                checked_vert[r_faceEdgeVertice1] = l_nonCheckedVertex
                                side_vert[l_nonCheckedVertex] = 2
                                side_vert[r_faceEdgeVertice1] = 1
                                l_edgeQueue.append(l_faceEdges[i])
                                r_edgeQueue.append(r_faceEdges[k])

                            if r_faceEdgeVertice1 == checked_vert[l_checked_vertertex]:
                                checked_vert[l_nonCheckedVertex] = r_faceEdgeVertice0
                                checked_vert[r_faceEdgeVertice0] = l_nonCheckedVertex
                                side_vert[l_nonCheckedVertex] = 2
                                side_vert[r_faceEdgeVertice0] = 1
                                l_edgeQueue.append(l_faceEdges[i])
                                r_edgeQueue.append(r_faceEdges[k])

    xAverage2 = 0
    xAverage1 = 0
    check_pos_point = OpenMaya.MPoint()
    for i in range(point_count):
        if checked_vert[i] != i and checked_vert[i] != -1:
            mesh_fn.getPoint(checked_vert[i], check_pos_point)
            if side_vert[i] == 2:
                xAverage2 += check_pos_point.x
            if side_vert[i] == 1:
                xAverage1 += check_pos_point.x

    switchSide = xAverage2 < xAverage1

    for i in range(point_count):
        map_array.append(checked_vert[i])
        if checked_vert[i] != i:
            if not switchSide:
                side_array.append(side_vert[i])
            else:
                if side_vert[i] == 2:
                    side_array.append(1)
                else:
                    side_array.append(2)
        else:
            side_array.append(0)

    for i in range(len(map_array)):
        if map_array[i] == -1:
            map_array[i] = i

    print("[Analyze Geometry] :: {} vertices in {}.".format(point_count, time.time() - start_time))

    return map_array, side_array, base_obj_name


def find_mirror_points(middle_edge="", task=''):
    """
    Finds the mirror points.
    :param middle_edge: <str> the middle edge of the mesh.
    :param task: <str> geometrySymmetry, geometryMirror
    :return:
    """
    do_vertex_space = False
    old_target_points = OpenMaya.MFloatVectorArray()
    new_target_points = OpenMaya.MFloatVectorArray()
    target_obj = OpenMaya.MDagPath()

    weight_array = OpenMaya.MDoubleArray()
    oldweight_array = OpenMaya.MDoubleArray()
    influences_count = 0
    vtx_components = OpenMaya.MObject()
    skin_cls = OpenMaya.MObject()
    both_indexes = OpenMaya.MIntArray()
    mapArray, sideArray, base_objectName = analyze_geometry(middle_edge)

    mirror_int = 0
    if task == "geometryMirror":
        mirror_int = 1
    if task == "geometrySymmetry":
        mirror_int = 2

    component = OpenMaya.MObject()
    base_sel = OpenMaya.MSelectionList()
    base_sel.add(base_objectName);
    base_obj = OpenMaya.MDagPath()

    base_sel.getDagPath(0, base_obj, component)
    vertexCount = OpenMaya.MFnMesh(base_obj).numVertices()
    if vertexCount == 0:
        cmds.warning('[Edge Flow Mirror Error] :: No vertices found with this mesh: {}'.format(base_objectName))
        return OpenMaya.MStatus.kFailure

    objectName = OpenMaya.MFnMesh(base_obj).partialPathName()

    fnBaseMesh = OpenMaya.MFnMesh(base_obj)
    basePoints = OpenMaya.MPointArray()
    fnBaseMesh.getPoints(basePoints)

    offset = [0, 0, 0]

    old_target_points.clear()
    new_target_points.clear()

    fnTargetMesh = OpenMaya.MFnMesh(target_obj)
    target_objectDagPath = OpenMaya.MDagPath()

    target_objectDagPath = OpenMaya.MDagPath()
    OpenMaya.MFnDagNode(target_obj).getPath(target_objectDagPath);

    target_pnts = OpenMaya.MPointArray()
    fnTargetMesh.getPoints(target_pnts, OpenMaya.MSpace.kObject)

    for i in range(target_pnts.length()):
        old_target_points.append(OpenMaya.MFloatVector(target_pnts[i].x, target_pnts[i].y, target_pnts[i].z))
        new_target_points.append(OpenMaya.MFloatVector(target_pnts[i].x, target_pnts[i].y, target_pnts[i].z))

    if mirror_int != 2:
        # create the symmetry shape
        if not do_vertex_space:
            pointOffset = OpenMaya.MPoint()
            for i in range(len(both_indexes)):
                if mirror_int == 0 or direction == sideArray[both_indexes[i]]:
                    pointOffset = (target_pnts[both_indexes[i]] - basePoints[both_indexes[i]])
                    new_target_points.set(OpenMaya.MFloatVector(basePoints[mapArray[both_indexes[i]]].x - pointOffset.x,
                                                                   basePoints[mapArray[both_indexes[i]]].y + pointOffset.y,
                                                                   basePoints[mapArray[both_indexes[i]]].z + pointOffset.z),
                                             mapArray[both_indexes[i]])

                    """
                    offset[0] = target_pnts[both_indexes[i]].x - basePoints[both_indexes[i]].x
                    offset[1] = target_pnts[both_indexes[i]].y - basePoints[both_indexes[i]].y
                    offset[2] = target_pnts[both_indexes[i]].z - basePoints[both_indexes[i]].z
    
                    x = basePoints[mapArray[both_indexes[i]]].x + offset[0] * -1 # basePoints' index is -1
                    y = basePoints[mapArray[both_indexes[i]]].y + offset[1]
                    z = basePoints[mapArray[both_indexes[i]]].z + offset[2]
    
                    new_target_points.set(OpenMaya.MFloatVector(x, y, z), mapArray[both_indexes[i]])
                    """
    elif do_vertex_space:

        vert_count = fnBaseMesh.numVertices()
        face_count = fnBaseMesh.numPolygons()
        connected_vertices = OpenMaya.MIntArray()
        connected_faces = OpenMaya.MIntArray()
        script_util = OpenMaya.MScriptUtil()
        ptr = script_util.asIntPtr()

        con_verts = [None] * vert_count
        con_faces = [None] * vert_count
        base_normals = [None] * vert_count
        target_normals = [None] * vert_count

        vert_iter = OpenMaya.MItMeshVertex(base_obj)
        for i in range(vert_count):
            vert_iter.setIndex(i, ptr)
            vert_iter.getConnectedVertices(connected_vertices)
            vert_iter.getConnectedFaces(connected_faces)
            con_verts[i] = util_int_array_to_list(connected_vertices)
            con_faces[i] = util_int_array_to_list(connected_faces)
            vec = OpenMaya.MVector()

            vert_iter.getNormal(vec)
            vec.normalize()
            base_normals[i] = OpenMaya.MVector(vec)

        target_vert_iter = OpenMaya.MItMeshVertex(target_obj)
        for i in range(vert_count):
            vec = OpenMaya.MVector()
            target_vert_iter.getNormal(vec)
            vec.normalize()
            target_normals[i] = OpenMaya.MVector(vec)

        face_iter = OpenMaya.MItMeshPolygon(base_obj)
        vertsOnFaces = [None] * face_count
        for i in range(face_count):
            face_iter.setIndex(i, ptr)
            face_iter.getVertices(connected_vertices)
            vertsOnFaces[i] = util_int_array_to_list(connected_vertices)

        # changeLocals = [None] * vert_count
        skips = [False] * vert_count
        xIds = [None] * vert_count
        zIds = [None] * vert_count
        xNegs = [None] * vert_count
        zNegs = [None] * vert_count

        skipsCounter = 0
        # create matrices for one side
        # print 'created large arrays: ', (time.time()-t)
        for i in range(len(both_indexes)):
            b_index = both_indexes[i]

            if sideArray[b_index] == 1:  # dont do the right ones yet, they'll get mirrored
                continue

            do_skip = False

            # if i not in both_indexes:
            #    do_skip = True

            if (basePoints[b_index] - target_pnts[b_index]).length() < 0.00001 and (
                    basePoints[mapArray[b_index]] - target_pnts[mapArray[b_index]]).length() < 0.00001:
                do_skip = True

            timeE += (time.time() - t)

            if do_skip:
                skips[b_index] = True
                skipsCounter += 1
                continue

            xId = []
            zId = []
            xNeg = []
            zNeg = []

            # get the avarage
            #
            averagePos = OpenMaya.MPoint(0, 0, 0)
            for vertId in con_verts[b_index]:
                averagePos.x += basePoints[vertId].x
                averagePos.y += basePoints[vertId].y
                averagePos.z += basePoints[vertId].z

            averagePos /= len(con_verts[b_index])

            # averagePos = basePoints[b_index]
            timeDinc = time.time()
            for f, face in enumerate(con_faces[b_index]):
                t = time.time()
                twoDots = [-1, -1]
                twoVecs = [None, None]

                for vert in vertsOnFaces[face]:
                    if vert != b_index and vert in con_verts[b_index]:
                        for d in range(2):
                            if twoDots[d] == -1:
                                twoDots[d] = vert
                                twoVecs[d] = OpenMaya.MVector(basePoints[vert] - averagePos)
                                break

                timeA += time.time() - t
                t = time.time()
                # skip face if it's from middle vertex and not along middle edges
                #
                if sideArray[b_index] == 0 and sideArray[twoDots[0]] != 0 and sideArray[twoDots[1]] != 0:
                    continue

                if f == 0:
                    firstVecs = list(twoVecs)

                    xId.append(twoDots[0])
                    zId.append(twoDots[1])
                    xNeg.append(False)
                    zNeg.append(False)

                timeB += time.time() - t
                t = time.time()

                # reshuffle them to match the first one as close as possible
                #
                """
                def distanceSqr(a):
                    return a.x*a.x + a.y*a.y + a.z*a.z

                if f > 0:

                    negs = [False, False]

                    # compare current 2 dots with first dot from first face
                    dist0 = distanceSqr(twoVecs[0] - firstVecs[0])
                    dist1 = distanceSqr(twoVecs[1] - firstVecs[0])

                    dist0n = distanceSqr(-twoVecs[0] - firstVecs[0])
                    dist1n = distanceSqr(-twoVecs[1] - firstVecs[0])


                    dist0negated = False
                    dist1negated = False

                    if dist0 > dist0n:
                        dist0 = dist0n
                        dist0negated = True
                    if dist1 > dist1n:
                        dist1 = dist1n
                        dist1negated = True


                    if dist0 > dist1:    
                        swap(0,1,twoDots)
                        swap(0,1,twoVecs)

                    xId.append(twoDots[0])
                    zId.append(twoDots[1])

                    xNeg.append(dist0negated)
                    zNeg.append(distanceSqr(twoVecs[1]-firstVecs[1]) > distanceSqr(-twoVecs[1]-firstVecs[1]))

                """
                if f > 0:

                    negs = [False, False]

                    # compare current 2 dots with first dot from first face
                    angle0 = twoVecs[0].angle(firstVecs[0])
                    angle1 = twoVecs[1].angle(firstVecs[0])
                    angle0neg = False
                    angle1neg = False

                    if angle0 > math.pi * 0.5:
                        angle0 = math.pi - angle0
                        angle0neg = True
                    if angle1 > math.pi * 0.5:
                        angle1 = math.pi - angle1
                        angle1neg = True

                    if angle0 < angle1:
                        xId.append(twoDots[0])
                        zId.append(twoDots[1])
                        xNeg.append(angle0neg)
                        zNeg.append(twoVecs[1].angle(firstVecs[1]) > math.pi * 0.5)

                    else:
                        xId.append(twoDots[1])
                        zId.append(twoDots[0])
                        xNeg.append(angle1neg)
                        zNeg.append(twoVecs[0].angle(firstVecs[1]) > math.pi * 0.5)

                timeC += time.time() - t
            timeD += (time.time() - timeDinc)

            xIds[b_index] = xId
            zIds[b_index] = zId

            xNegs[b_index] = xNeg
            zNegs[b_index] = zNeg

        # print 'got all the matrices: timeA:', timeA, 'timeB:', timeB, 'timeC:', timeC
        # print 'timeD:', timeD, 'timeE:', timeE
        # print 'complete time: ', (time.time() - matrixCreateStartTime)

        dv = 74
        # print xIds[dv], xNegs[dv]
        # print zIds[dv], zNegs[dv]

        # now create the other ones by mirroring
        #
        # print 'now create the other ones by mirroring'
        for i in range(len(both_indexes)):
            b_index = both_indexes[i]

            if sideArray[b_index] != 1:
                continue

            if skips[mapArray[b_index]]:
                skipsCounter += 1
                skips[b_index] = True
                continue

            xId = list(xIds[mapArray[b_index]])  # [None] * vert_count
            zId = list(zIds[mapArray[b_index]])  # [None] * vert_count

            for k in range(len(xId)):
                xId[k] = mapArray[xId[k]]
                zId[k] = mapArray[zId[k]]

            xIds[b_index] = xId
            zIds[b_index] = zId

            xNegs[b_index] = xNegs[mapArray[b_index]]
            zNegs[b_index] = zNegs[mapArray[b_index]]

        # print 'skipping ', skipsCounter, 'vertices'

        # print 'now mirror them'
        t = time.time()
        for i in range(both_indexes.length()):

            if mapArray[both_indexes[i]] != -2:

                b_index = both_indexes[i]

                if (skips[b_index]):
                    continue

                if mirror_int == 0 or direction == sideArray[b_index] or sideArray[b_index] == 0:

                    idsCount = len(xIds[b_index])
                    baseX = OpenMaya.MVector(0, 0, 0)
                    baseZ = OpenMaya.MVector(0, 0, 0)

                    for k in range(idsCount):
                        if xNegs[b_index][k]:
                            xMult = -1
                        else:
                            xMult = 1
                        if zNegs[b_index][k]:
                            zMult = -1
                        else:
                            zMult = 1

                        baseX += (OpenMaya.MVector(basePoints[xIds[b_index][k]] - basePoints[b_index])) * xMult
                        baseZ += (OpenMaya.MVector(basePoints[zIds[b_index][k]] - basePoints[b_index])) * zMult

                    baseX /= idsCount
                    baseZ /= idsCount
                    baseX.normalize()
                    baseZ.normalize()

                    baseMat = createMatrixFromList(
                        [baseX.x, baseX.y, baseX.z, 0, base_normals[b_index].x, base_normals[b_index].y,
                         base_normals[b_index].z, 0, baseZ.x, baseZ.y, baseZ.z, 0, basePoints[b_index].x,
                         basePoints[b_index].y, basePoints[b_index].z, 1])
                    changeWorld = createMatrixFromPos(target_pnts[b_index])
                    changeLocal = changeWorld * baseMat.inverse()

                    if sideArray[b_index] == 0:  # middle vertex

                        middleId = -1
                        for nId in xIds[b_index] + zIds[b_index]:
                            if sideArray[nId] == 0:
                                middleId = nId
                                continue

                        # check which angle is closer
                        #
                        middleIdVect = OpenMaya.MVector(basePoints[middleId] - basePoints[b_index])
                        angleX = middleIdVect.angle(baseX)
                        angleZ = middleIdVect.angle(baseZ)
                        if angleX > math.pi * 0.5: angleX = math.pi - angleX
                        if angleZ > math.pi * 0.5: angleZ = math.pi - angleZ

                        if angleX < angleZ:
                            centeredLocal = createMatrixFromPos(
                                OpenMaya.MPoint(changeLocal(3, 0), changeLocal(3, 1), -changeLocal(3, 2)))
                        else:
                            centeredLocal = createMatrixFromPos(
                                OpenMaya.MPoint(-changeLocal(3, 0), changeLocal(3, 1), changeLocal(3, 2)))

                        changetarget = centeredLocal * baseMat
                        mappedBIndex = b_index

                    elif sideArray[b_index] != 0:  # not middle vertex
                        mappedBIndex = mapArray[b_index]

                        targetX = OpenMaya.MVector(0, 0, 0)
                        targetZ = OpenMaya.MVector(0, 0, 0)

                        idsCount = len(xIds[mappedBIndex])

                        for k in range(idsCount):
                            if xNegs[mappedBIndex][k]:
                                xMult = -1
                            else:
                                xMult = 1
                            if zNegs[mappedBIndex][k]:
                                zMult = -1
                            else:
                                zMult = 1

                            targetX += (OpenMaya.MVector(
                                basePoints[xIds[mappedBIndex][k]] - basePoints[mappedBIndex])) * xMult
                            targetZ += (OpenMaya.MVector(
                                basePoints[zIds[mappedBIndex][k]] - basePoints[mappedBIndex])) * zMult

                        targetX /= idsCount
                        targetZ /= idsCount

                        targetX.normalize()
                        targetZ.normalize()

                        targetMat = createMatrixFromList(
                            [targetX.x, targetX.y, targetX.z, 0, base_normals[mappedBIndex].x,
                             base_normals[mappedBIndex].y, base_normals[mappedBIndex].z, 0, targetZ.x, targetZ.y,
                             targetZ.z, 0, basePoints[mappedBIndex].x, basePoints[mappedBIndex].y,
                             basePoints[mappedBIndex].z, 1])

                        changetarget = changeLocal * targetMat

                    new_target_points.set(
                        OpenMaya.MFloatVector(changetarget(3, 0), changetarget(3, 1), changetarget(3, 2)), mappedBIndex)
        # print 'mirrored them .. ', (time.time()-t)



elif mirror_int == 2:  # create symmetryshape

    for i in range(both_indexes.length()):
        if sideArray[both_indexes[i]] == 1 and mapArray[both_indexes[i]] != -1:
            target_pnts[both_indexes[i]].x = target_pnts[both_indexes[i]].x * -1

    for i in range(both_indexes.length()):
        if mapArray[both_indexes[i]] != -1:

            x = (target_pnts[both_indexes[i]].x + target_pnts[mapArray[both_indexes[i]]].x) * 0.5;
            y = (target_pnts[both_indexes[i]].y + target_pnts[mapArray[both_indexes[i]]].y) * 0.5;
            z = (target_pnts[both_indexes[i]].z + target_pnts[mapArray[both_indexes[i]]].z) * 0.5;
            target_pnts[both_indexes[i]].x = x;
            target_pnts[both_indexes[i]].y = y;
            target_pnts[both_indexes[i]].z = z;
            target_pnts[mapArray[both_indexes[i]]].x = x;
            target_pnts[mapArray[both_indexes[i]]].y = y;
            target_pnts[mapArray[both_indexes[i]]].z = z;

            if mapArray[both_indexes[i]] == both_indexes[i]:  # middlePoint
                target_pnts[both_indexes[i]].x = 0;

    for i in range(both_indexes.length()):
        if mapArray[both_indexes[i]] != -1:
            if sideArray[both_indexes[i]] == 1:  # middle
                target_pnts[both_indexes[i]].x = target_pnts[both_indexes[i]].x * -1;

            new_target_points.set(
                OpenMaya.MFloatVector(target_pnts[both_indexes[i]].x, target_pnts[both_indexes[i]].y,
                                      target_pnts[both_indexes[i]].z), both_indexes[i])

    # selecting wrong points:
    fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
    vtxComponent = OpenMaya.MObject();
    vtx_components = fnVtxComp.create(OpenMaya.MFn.kMeshVertComponent);
    selectPoints = OpenMaya.MSelectionList()

    missingPoints = False;
    selectedPoints.reset();
    while not selectedPoints.isDone():  # for (; !selectedPoints.isDone(); selectedPoints.next())
        index = selectedPoints.index()
        if mapArray[index] == -1:  # if no mirrorPoint found
            fnVtxComp.addElement(index)
            missingPoints = True;

        selectedPoints.next()

    if missingPoints:
        selectPoints.clear()
        selectPoints.add(dagPathSelShape, vtx_components)
        print "some points couldn't be mirrored (see selection)"
        OpenMaya.MGlobal.setActiveSelectionList(selectPoints)

    else:
        print "found mirrorPoint for each selected point"
