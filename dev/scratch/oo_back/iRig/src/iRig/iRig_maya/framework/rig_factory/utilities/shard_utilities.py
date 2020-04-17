from rig_factory.objects.face_objects.face_handle import FaceHandle


def get_shard_skin_cluster_data(rig):
    controller = rig.controller
    data = []
    for shard in [x.shard_mesh for x in rig.get_handles() if isinstance(x, FaceHandle)]:
        if shard:
            skin_cluster = controller.find_skin_cluster(shard)
            if skin_cluster:
                try:
                    data.append(controller.scene.get_skin_data(skin_cluster))
                except Exception, e:
                    print e.message()
    return data


def set_shard_skin_cluster_data(rig, data):
    controller = rig.controller
    shards = dict((x.shard_mesh.get_selection_string(), x.shard_mesh) for x in rig.get_handles() if isinstance(x, FaceHandle))
    for skin_data in data:
        if skin_data['geometry'] in shards:
            controller.scene.create_from_skin_data(skin_data)


def copy_selected_skin_to_shards(rig):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc
    import maya.mel as mel

    controller = rig.controller
    mesh_names = []
    for mesh_name in controller.get_selected_mesh_names():
        if not mc.getAttr('%s.intermediateObject' % mesh_name):
            mesh_names.append(mesh_name)

    skin_mesh = mesh_names[0]
    influences = mc.skinCluster(skin_mesh, q=True, influence=True)
    shards = [x.shard_mesh.get_selection_string() for x in rig.get_handles() if isinstance(x, FaceHandle)]
    if not shards:
        raise Exception('No Shards found')
    mc.select(shards)
    for shard in shards:
        skin_m_object = controller.scene.find_skin_cluster(shard)
        if skin_m_object:
            skin = controller.scene.get_selection_string(skin_m_object)
            controller.scene.skinCluster(skin, e=True, ub=True)
        mc.skinCluster(influences, shard, tsb=True)
        mc.copySkinWeights(skin_mesh, shard, noMirror=True, surfaceAssociation='closestPoint',
                           influenceAssociation='oneToOne')
        floodSkin(shard, operation='smooth', doInternal=False, iters=1)
    mc.select(shards)
    mel.eval('removeUnusedInfluences;')



def floodSkin (targetMesh, operation = 'smooth', doInternal = False, iters = 2):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc

    targetSkin = findSkinCluster (targetMesh)
    normalization = mc.skinCluster (targetSkin, query = True, normalizeWeights = True)
    skinContext = initWeightPaintTool (targetMesh, operation = operation, normalize = 2)

    if not skinContext:
        return

    # run a timer along with the smooth command
    mc.timer (s = True, name = operation)
    floodJointWeights (targetMesh, targetSkin, skinContext, doInternal, iters = iters)
    smoothTime = mc.timer (e = True, name = operation)

    skinContext = initWeightPaintTool (targetMesh, operation = operation, normalize = normalization)

    print '%s skin weights: %s seconds, %s influences\n' %(operation, smoothTime, len(findInfluences(targetMesh)))


def floodJointWeights (targetMesh, targetSkin, skinContext, doInternal = False, iters = 2):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc

    if targetSkin is None:
        targetSkin = findSkinCluster (targetMesh)
        if not targetSkin:
            return

    skinJnts = findInfluences (targetMesh)

    for jnt in skinJnts:
        if mc.getAttr ('%s.liw' %(jnt)) == 0:
            # selectVerts if only smoothing internally
            if doInternal:
                mc.skinCluster (targetSkin, edit = True, influence = jnt, selectInfluenceVerts = jnt)

            toggleSkinInf (targetSkin, jnt)
            for i in range(iters):
                mc.artAttrSkinPaintCtx (skinContext, edit = True, influence = jnt, clear = True)

            # deselectVerts if only smoothing internally
            if doInternal:
                mc.skinCluster (targetSkin, edit = True, removeFromSelection = True, selectInfluenceVerts = jnt)

    mc.skinCluster (targetSkin, edit = True, forceNormalizeWeights = True)

# connect an influence to the skinCluster for painting, disconnect if one already connected
def toggleSkinInf (targetSkin, jnt, doConnect = True):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc

    paintTransJnt = mc.listConnections ('%s.paintTrans' %(targetSkin), s = True, d = True)
    if paintTransJnt is not None:
        mc.disconnectAttr ('%s.message' %(paintTransJnt[0]), '%s.paintTrans' %(targetSkin))
    if doConnect:
        mc.connectAttr ('%s.message' %(jnt), '%s.paintTrans' %(targetSkin), f = True)



# return the all influences attached to a skinCluster
def findInfluences (targetMesh):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc

    targetSkin = findSkinCluster (targetMesh)
    if not targetSkin:
        return False

    # create a list of only joints
    skinJnts = []
    plugs = mc.listAttr ('%s.matrix' %(targetSkin), multi = True)
    for plug in plugs:
        skinJnt = mc.listConnections ('%s.%s' %(targetSkin, plug), s = True, d = True)[0]
        skinJnts.append(skinJnt)

    return skinJnts

def findSkinCluster (targetMesh):
    """

    GET RID OF CMDS

    """
    import maya.cmds as mc
    # find skinCluster for declared mesh
    targetSkin = []
    for connect in mc.listHistory (targetMesh):
        if mc.objectType (connect) == 'skinCluster':
            targetSkin = connect
            break

    if targetSkin == []:
        mc.warning ('%s has no skinCluster' %(targetMesh))
        return False

    return targetSkin



# initialize the weightPaint tool for the given mesh and operation
def initWeightPaintTool (targetMesh, operation = 'smooth', value = 1.0, normalize = 2):
    import maya.cmds as mc

    if not findSkinCluster(targetMesh):
        return False

    if operation == 'replace':
        operation = 'absolute'
    if operation == 'add':
        operation = 'additive'

    validOperations = ['absolute', 'additive', 'scale', 'smooth']
    if operation not in validOperations:
        print 'Valid operations: \'replace\', \'absolute\', \'add\', \'additive\', \'scale\', \'smooth\''
        mc.warning ('Invalid operation type.')
        return False

    # create or edit artisan context. Ensure it's in 'skinWeights' mode
    contexts = mc.lsUI (contexts = True)
    skinContexts = [ctx for ctx in contexts if 'artAttrSkin' in ctx]

    if skinContexts == []:
        skinContext = mc.artAttrSkinPaintCtx('artAttrSkinContext', whichTool = 'skinWeights')
    else:
        skinContext = mc.artAttrSkinPaintCtx(skinContexts[0], edit = True, whichTool = 'skinWeights')

    # select object and set normalization
    mc.select (targetMesh, r = True)
    mc.skinCluster (findSkinCluster (targetMesh), edit = True, normalizeWeights = normalize, forceNormalizeWeights = True)

    # open weightPaint tool
    mc.setToolTo(skinContext)
    mc.artAttrSkinPaintCtx (skinContext, edit = True, value = value, selectedattroper = operation)

    return skinContext