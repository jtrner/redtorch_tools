"""
deformLib.py

Author: Ehsan Hassani Moghaddam

"""

# python modules
import os
from itertools import groupby
import sys
import logging
import re
from collections import OrderedDict

# third party modules
try:
    from scipy.spatial import ckdtree
except ImportError:
    sys.stdout.write("Could not import scipy.spatial.ckdtree!")

# maya modules
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as mc

# rt_tools modules
from rt_tools.maya.lib import trsLib
from rt_tools.maya.lib import fileLib
from rt_tools.maya.lib import keyLib

# constants
logger = logging.getLogger(__name__)
skin_suffix = 'Skn'


def bind_geo(*args, **kwargs):
    """
    Binds the geo with these items in list
    :param components: <list> list of items to bind.
    :return: <bool> for success.
    """
    # grabs geo selection // nurbsSurface selection // nurbsCurve selection
    geos = kwargs.pop('geos')
    geos = mc.filterExpand(geos, sm=(12, 10, 9), fp=True)
    joints = kwargs.pop('joints')
    joints = mc.ls(joints)

    if not joints or not geos:
        mc.error("[Bind Selection] :: Incorrect components selected for skinning.")
        return False

    # binds the skin with weight blended method.
    for geo in geos:
        mc.skinCluster(joints, geo, normalizeWeights=1, bindMethod=0, skinMethod=0,
                       dropoffRate=4, obeyMaxInfluences=1, maximumInfluences=5, tsb=1)
    return True


def importSkin(dataPath):
    """
    import deformLib weights from given path
    """

    # search given path for skin wgt files
    if not os.path.lexists(dataPath):
        return

    wgtFiles = [os.path.join(dataPath, x) for x in os.listdir(dataPath)
                if x.endswith('.wgt')]

    # for each wgt file, find geo and check if skinCluster exists
    for wgtFile in wgtFiles:
        # import wgt
        skinData = importSkinData(wgtFile)

        # geo node
        node = skinData[0]
        if len(mc.ls(node)) > 1:
            logger.error('There are more than one "{}" in the scene, skipped!'.format(node))
            continue
        if not mc.objExists(node):
            logger.error('Could not find "{0}", skipped!'.format(node))
            continue

        # delete existing skinCluster
        sknNode = getSkinCluster(node)
        if sknNode:
            mc.delete(sknNode)

        # find missing joints
        for j in skinData[2]:
            if not mc.objExists(j):
                logger.error('joint "{0}" does not exist!'.format(j))

        # error if no joint found
        infs = mc.ls(skinData[2])
        if not infs:
            logger.error('None of influences exist for "{}", skipped!'.format(node))
            continue

        # create a new skinCluster with found joints
        sknName = trsLib.getTransform(node) + '_' + skin_suffix
        skinData[1] = mc.skinCluster(infs, node, tsb=1, rui=0, n=sknName)[0]

        # assign weights
        setSkinData(skinData)


def exportSkin(geos, dataPath):
    """
    export skincluster weights for given rig component asset nodes
    """
    geos = mc.ls(geos, type='transform')

    notSkinnedGeos = []
    for node in geos:
        sknNode = getSkinCluster(node)
        if not sknNode:
            notSkinnedGeos.append(node)
            continue
        skinData = getSkinData(sknNode)

        node = node.rpartition(':')[2]
        wgtFiles = os.path.join(dataPath, node + '.wgt')

        exportSkinData(skinData, wgtFiles)
        logger.info('Exported skinculster for "{0}"'.format(node))

    if notSkinnedGeos:
        print('No skincluster node found on nodes bellow, export skipped!')
        print('.................................................................')
        for x in notSkinnedGeos:
            print(x)
        print('.................................................................')


def getInfs(skin):
    """
    get influences
    :param skin:
    :return: list of influence names
    :return type: list of strings
    """
    fnSkin = getFnSkin(skin)
    aInfDagA = fnSkin.influenceObjects()
    return [str(x) for x in aInfDagA]


def getComponent(dag):
    """
    create vertex component
    :return: om2.MFn.kMeshVertComponent
    """
    # create a list of verts indices
    mesh_fn = om2.MFnMesh(dag)
    verts_array = range(mesh_fn.numVertices)

    # get components
    comp_fn = om2.MFnSingleIndexedComponent()
    component = comp_fn.create(om2.MFn.kMeshVertComponent)
    comp_fn.addElements(verts_array)

    return component


def getSkinData(skin, weightsAsList=False):
    """
    given a skinCluster node, get's skin data such as number of
    vertices on the skinCluster, number of influences and weights
    of influences for each vertex
    :param skin: name of skinCluster node to get its data
    :param weightsAsList: if set to True, weights will be written
                          as lists of weights for each vertex
                          with vert id as first element and
                          weights for the vert as next elements
                          else writes number of vertices in one
                          line and all weights in the next line
    :return: list with 6 elements in it:
                                geo, skin, infs, numVerts, wgts, blendWeights
    """
    # skin fn
    fnSkin = getFnSkin(skin)

    # has blendWeights?
    blend_wgts = None
    if mc.getAttr(skin + '.skinningMethod') == 2:
        blend_wgts = getSkinBlendWeights(skin)

    # geo
    dag = fnSkin.getPathAtIndex(0)
    geo = dag.fullPathName().split('|')[-1]

    # create components variable
    oComps = getComponent(dag)

    # num of vertices
    mesh_fn = om2.MFnMesh(dag)
    numVerts = mesh_fn.numVertices

    # get influence names
    infs = getInfs(skin)

    # get all weights for all influences at once
    wgts, numInfs = fnSkin.getWeights(dag, oComps)

    if weightsAsList:
        wgts = _lineToLists(wgts, numVerts, len(infs))

    #
    return geo, skin, infs, numVerts, wgts, blend_wgts


def exportSkinData(skinData, filePath):
    """
    exports given skinData into filePath
    ie:     # export skinData for skinCluster1
            filePath = os.path.join('D:', 'temp.wgts')
            skinData = getSkinData('skinCluster1')
            exportSkinData(skinData, filePath, weightsAsList=False)
    :param skinData: list with 5 elements in it:
                                 geo, skin, infs, numVerts, wgts
    :param filePath: path of skinData file
    :return: None
    """
    geo = skinData[0]
    skin = skinData[1]
    infs = skinData[2]
    numVerts = skinData[3]
    wgts = skinData[4]
    blend_wgts = skinData[5]

    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except:
            raise

    with open(filePath, 'w') as f:
        f.write(geo + '\n\n')
        f.write(skin + '\n\n')
        for inf in infs:
            f.write(inf + '\n')
        f.write('\n')

        # write the whole weights for all verts on the same line
        f.write(str(numVerts))
        f.write('\n\n')
        f.write(' '.join([str(x) for x in wgts]))

        if blend_wgts:
            f.write('\n\n')
            f.write(' '.join([str(x) for x in blend_wgts]))


def getSkinCluster(obj):
    fnSkin = getFnSkinCluster(obj)
    if fnSkin:
        return fnSkin.name()


def getFnSkinCluster(geo):
    # if name of skinCluster is given
    mSel = om2.MSelectionList()
    mSel.add(geo)
    depN = mSel.getDependNode(0)
    if depN.hasFn(om2.MFn.kSkinClusterFilter):
        return oma2.MFnSkinCluster(depN)

    # if name of geo is given
    dagShape = getDagShape(geo)
    try:
        itDG = om2.MItDependencyGraph(dagShape.node(),
                                      om2.MFn.kSkinClusterFilter,
                                      om2.MItDependencyGraph.kUpstream)
        while not itDG.isDone():
            oCurrentItem = itDG.currentNode()
            return oma2.MFnSkinCluster(oCurrentItem)
    except:
        pass
    return None


def getDagShape(geo):
    mSel = om2.MSelectionList()
    mSel.add(geo)
    dagS = mSel.getDagPath(0)
    dagS.extendToShape()
    return dagS


def getDag(node):
    sel = om2.MSelectionList()
    sel.add(node)
    dag = sel.getDagPath(0)
    return dag


def getFnSkin(skin):
    dep = getDependByName(skin)
    if not dep.hasFn(om2.MFn.kSkinClusterFilter):
        raise Exception('{} is not a skinCluster'.format(skin))
    return oma2.MFnSkinCluster(dep)


def getDependByName(node):
    sel = om2.MSelectionList()
    sel.add(node)
    depend = sel.getDependNode(0)
    return depend


def setSkinData(skinData=None, ignoreMissingJnts=True, **kwargs):
    """
    extracts weights from given skinData and sets
    the wights on given skinCluster
    :param skin: name of skinCluster node to set its data
    :param skinData:
    :return: None
    """
    # gather data
    skin = kwargs.setdefault('skin', skinData[1])
    infs = skinData[2]
    # numVerts = skinData[3]
    wgt_values = skinData[4]
    blend_wgt_values = skinData[5]
    # numInfs = len(infs)

    # skin fn
    fnSkin = getFnSkin(skin)

    # geo iter
    dag = fnSkin.getPathAtIndex(0)

    # wgts double array
    wgts = om2.MDoubleArray()
    wgts.copy(wgt_values)

    # create components variable
    comp_fn = om2.MFnSingleIndexedComponent()
    component = comp_fn.create(om2.MFn.kMeshVertComponent)
    comp_fn.addElements(range(len(wgt_values)))

    # get influence indices
    infIds = om2.MIntArray()
    for inf in infs:

        # add a joint names 'missing_JNT' if influence doesn't exist
        if not mc.objExists(inf):
            if ignoreMissingJnts:
                inf = 'missing_JNT'
                if not mc.objExists(inf):
                    mc.select(clear=True)
                    mc.joint(n=inf)
                try:
                    mc.skinCluster(skin, e=True, ai=inf)
                except:
                    pass

        infDag = getDag(inf)
        infId = fnSkin.indexForInfluenceObject(infDag)
        infIds.append(infId)

    # set all weights for all influences at once
    fnSkin.setWeights(dag, component, infIds, wgts)

    # blend_wgts double array
    if blend_wgt_values:
        mc.setAttr(skin + '.skinningMethod', 2)
        setSkinBlendWeights(skin, blend_wgt_values)


def getInfIndex(skin, jnt):
    skin_fn = getFnSkin(skin)
    jnt_dag = getDag(jnt)
    if jnt_dag in skin_fn.influenceObjects():
        return skin_fn.indexForInfluenceObject(jnt_dag)


def createSkinCluster(geos):
    """
    :return: sets self.skins to a list of newly created skincluster nodes
    """
    skins = []
    for geometry in geos:
        skin = mc.skinCluster('C_root_JNT', geometry, name=geometry + '_' + skin_suffix)
        skins.append(skin)
    return skins


def importSkinData(filePath):
    """
    import skin data from file
    ie:     # import skinData for skinCluster1
            filePath = os.path.join('D:', 'temp.wgts')
            skinData = importSkinData(filePath, False)
            setSkinData(skinData, skin='skinCluster1')
    :param filePath: path to skin data file
    :return: skinData list which contains
             geo, skin, infs, numVerts, wgts, blend_wgts
    :return type: list
    """
    with open(filePath, 'r') as f:
        lines = [x for x in f]
        skinData = [list(group) for k,
                                    group in groupby(lines, lambda x: x == "\n")
                    if not k]

        # get geo
        geo = _lineToStr(skinData[0])

        # reference mesh with skinCluster have Deformed in the end, get rid of them
        geo = geo.split('Deformed')[0]

        # get skin
        skin = _lineToStr(skinData[1])

        # get influences
        infs = [x.rstrip('\n') for x in skinData[2]]

        # get num verts
        numVerts = int(_lineToStr(skinData[3]))

        # get weights as one list with all weights in it
        wgts = [float(x) for x in skinData[4][0].split(' ')]

        # get blend weights
        blend_wgts = None
        if len(skinData) > 5:
            blend_wgts = [float(x) for x in skinData[5][0].split(' ')]

        return [geo, skin, infs, numVerts, wgts, blend_wgts]


def _firstToIntRestToFloat(aList):
    """
    convert first element of a list to int and the rest to floats
    :param aList:
    :return:
    """
    aList[0] = int(aList[0])
    aList[1:] = [float(x) for x in aList[1:]]
    return aList


def _lineToStr(line):
    return line[0].rstrip('\n')


def _lineToLists(wgts, numVerts, numInfs):
    """
    converts one list of weights which are for all vertices
    to lists which have vertex id as their first element
    and weights for that vertex as next elements.
    :return: list of weight lists
    """
    wgtsList = []
    for i in range(numVerts):
        tempList = [i]
        for j in range(numInfs):
            tempList.append(float(wgts[(i * numInfs) + j]))
        wgtsList.append(tempList)
    return wgtsList


def copySkin(src=None, targets=None, useSelection=False):
    """
    from rt_tools.maya.lib import deformLib
    deformLib.copySkin(useSelection=True)
    """
    if useSelection:
        sels = mc.ls(sl=True)
        if len(sels) < 2:
            logger.error('Need to provide a source geo + target geo(s) to copy skinCluster!')
        src = sels[0]
        targets = sels[1:]

    if not isinstance(targets, (list, tuple)):
        targets = [targets]

    # get joints from src
    infs = mc.skinCluster(src, q=True, inf=True)

    skn_nodes = []
    for tgt in targets:
        # delete current skinCluster if exists
        skn = getSkinCluster(tgt)
        if skn:
            mc.delete(skn)

        # create skin for target
        skn_node = tgt + '_' + skin_suffix
        mc.skinCluster(infs, tgt, toSelectedBones=True, n=skn_node)
        skn_nodes.append(skn_node)

        # copy weights from src to target
        mc.copySkinWeights(src,
                           tgt,
                           noMirror=True,
                           surfaceAssociation='closestPoint',
                           influenceAssociation=['label', 'name', 'closestJoint'])

    logger.info("[Finished Skin] :: {}".format(skn_nodes))

    return skn_nodes


def getSkinBlendWeights(skin):
    # get skin fn
    skin_fn = getFnSkin(skin)

    # get shape
    shape_dag = skin_fn.getPathAtIndex(0)

    # create a list of verts indices
    components = getComponent(shape_dag)

    # get blend weights
    blend_wgts = skin_fn.getBlendWeights(shape_dag, components)

    return blend_wgts


def setSkinBlendWeights(skin, weights):
    # get skin fn
    skin_fn = getFnSkin(skin)

    # get shape
    shape_dag = skin_fn.getPathAtIndex(0)

    # create a list of verts indices
    components = getComponent(shape_dag)

    # set blend weights
    blend_wgts = om2.MDoubleArray()
    blend_wgts.copy(weights)
    skin_fn.setBlendWeights(shape_dag, components, blend_wgts)


def createLattice(geos, name, divisions=(2, 3, 2),
                  trs=((0, 0, 0), (0, 0, 0), (1, 1, 1)),
                  base_trs=((0, 0, 0), (0, 0, 0), (1, 1, 1)),
                  local=False,
                  outsideLattice=0,
                  outsideFalloffDist=1.0,
                  objectCentered=True):
    # create ffd
    mc.select(geos)
    ffd_node, lattice, ffdBase = mc.lattice(divisions=divisions, objectCentered=objectCentered)
    ffd_node = mc.rename(ffd_node, name + '_LatticeNode')
    lattice = mc.rename(lattice, name + '_Lattice')
    ffdBase = mc.rename(ffdBase, name + '_LatticeBase')

    # set transform values
    if not objectCentered:
        trsLib.setTRS(lattice, trs, space='world')
        trsLib.setTRS(ffdBase, base_trs, space='world')

    # set ffd settings
    mc.setAttr(ffd_node + '.local', local)
    mc.setAttr(ffd_node + '.outsideLattice', outsideLattice)
    mc.setAttr(ffd_node + '.outsideFalloffDist', outsideFalloffDist)

    return ffd_node, lattice, ffdBase


def exportLattice(ffd, path):
    """
    :Maya Bug: if lattice is skinned, getAttr returns different values!

        mc.getAttr('body_FFD_Lattice.pt[0][0][0].xValue')
        # lattice before skinning returns: -0.5
        # lattice skinned returns: [(0.0, 0.0, 0.0)]

    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    for ffd in 'ffd1Lattice', 'ffd3Lattice':
        ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
        deformLib.exportLattice(ffd=ffd, path=ffd_json)
    """
    # get transform values
    data = {'trs': trsLib.getTRS(ffd, space='world')}

    # get cv positions
    cvs = mc.ls(ffd + '.controlPoints[*]', fl=True)
    data['cv_positions'] = [mc.xform(cv, q=True, t=True) for cv in cvs]

    # get geometries
    ffd_s = trsLib.getShapes(ffd)[0]
    ffd_node = (mc.listConnections(ffd_s + '.latticeOutput') or [None])[0]
    ffd_outs = mc.listConnections(ffd_node + '.message', s=False, d=True, plugs=True)
    ffd_sets = [x for x in ffd_outs if '.usedBy' in x]
    ffd_set = ffd_sets[0].split('.')[0]
    data['geos'] = mc.listConnections(ffd_set + '.dagSetMembers') or []

    # get base transform values
    ffdBase = (mc.listConnections(ffd_node + '.baseLattice.baseLatticeMatrix') or [None])[0]
    data['base_trs'] = trsLib.getTRS(ffdBase, space='world')

    # get divisions
    sDiv = mc.getAttr(ffd_s + '.sDivisions')
    tDiv = mc.getAttr(ffd_s + '.tDivisions')
    uDiv = mc.getAttr(ffd_s + '.uDivisions')
    data['divisions'] = (sDiv, tDiv, uDiv)

    # get ffd settings
    data['local'] = mc.getAttr(ffd_node + '.local')
    data['outsideLattice'] = mc.getAttr(ffd_node + '.outsideLattice')

    for axis in 'STU':
        val = mc.getAttr(ffd_node + '.localInfluence' + axis)
        data['localInfluence' + axis] = val

    # write it to disk as json
    fileLib.saveJson(path=path, data=data)


def importLattice(path):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    for ffd in 'ffd1Lattice', 'ffd3Lattice':
        ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
        deformLib.importLattice(path=ffd_json)
    """

    # read data from json
    data = fileLib.loadJson(path=path)
    if not data:
        mc.error('Not a valid lattice config! "{}"'.format(path))

    # create ffd
    name = os.path.splitext(os.path.basename(path))[0]
    mc.select(mc.ls(data['geos']))
    ffd_node, ffd, ffdBase = mc.lattice(divisions=data['divisions'])
    ffd_node = mc.rename(ffd_node, name + 'Node')
    ffd = mc.rename(ffd, name)
    ffdBase = mc.rename(ffdBase, name + 'Base')

    # set transform values
    trsLib.setTRS(ffd, data['trs'], space='world')
    trsLib.setTRS(ffdBase, data['base_trs'], space='world')

    # set cv positions
    for i, pos in enumerate(data['cv_positions']):
        mc.xform('{}.controlPoints[{}]'.format(ffd, i), t=pos)

    # set ffd settings
    mc.setAttr(ffd_node + '.local', data['local'])
    mc.setAttr(ffd_node + '.outsideLattice', data['outsideLattice'])

    for axis in 'STU':
        val = data.get('localInfluence' + axis, 2)
        mc.setAttr(ffd_node + '.localInfluence' + axis, val)

    return ffd_node, ffd, ffdBase


def mirrorFFD(ffd, copy=True, findAndDeformGeos=True, search='L_', replace='R_'):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    deformLib.mirrorFFD(ffd='ffd1Lattice')
    """
    old_ffd_name = ffd
    ffd_dup = trsLib.mirror(ffd, copy=copy)
    ffd_cvs = mc.ls(ffd_dup + '.controlPoints[*]')
    mc.scale(-1, 1, 1, ffd_cvs, r=True, ocp=True)

    # get divisions
    ffd_s = trsLib.getShapes(ffd)[0]
    sDiv = mc.getAttr(ffd_s + '.sDivisions')
    tDiv = mc.getAttr(ffd_s + '.tDivisions')
    uDiv = mc.getAttr(ffd_s + '.uDivisions')
    divisions = (sDiv, tDiv, uDiv)

    # get old ffdBase
    ffd_node = (mc.listConnections(ffd_s + '.latticeOutput') or [None])[0]
    ffdBase = (mc.listConnections(ffd_node + '.baseLattice.baseLatticeMatrix') or [None])[0]

    # get ffd settings
    local = mc.getAttr(ffd_node + '.local')
    outsideLattice = mc.getAttr(ffd_node + '.outsideLattice')

    # mirror ffdBase
    ffdBase_dup = trsLib.mirror(ffdBase, copy=copy)

    # get geometries
    geos = []
    if findAndDeformGeos:
        geos = mc.listConnections(ffd_node + '.outputGeometry')
        geos = [x for x in geos if getShapes(x)]

    # initialize cv_positions list
    cv_positions = [[[x, y, z] for z in range(uDiv) for y in range(tDiv)] for x in range(sDiv)]

    # get cv positions
    cvs = sorted(mc.ls(ffd_dup + '.controlPoints[*]', fl=True))
    for cv in cvs:
        x = mc.getAttr(cv + '.xValue')
        y = mc.getAttr(cv + '.yValue')
        z = mc.getAttr(cv + '.zValue')
        ijk_str = cv.split('.pt')[-1]  # ffd1Lattice3.pt[2][1][1] -> '[2][1][1]'
        i, j, k = [int(ii) for ii in re.findall(r'(\d+)', ijk_str)]
        cv_positions[i][j][k] = (x, y, z)

    #
    if copy:
        ffd_node, ffd, ffdBase = mc.lattice(divisions=divisions)
        name = old_ffd_name.replace(search, replace, 1)
        ffd_node = mc.rename(ffd_node, name + 'Base')
        ffd = mc.rename(ffd, name)
        ffdBase = mc.rename(ffdBase, name + 'Base')

        mc.setAttr(ffd_node + '.local', local)
        mc.setAttr(ffd_node + '.outsideLattice', outsideLattice)

    # set point positions
    for i in range(sDiv):
        for j in range(tDiv):
            for k in range(uDiv):
                reversed_i = sDiv - i - 1  # reverse index of x axes column to mirror
                pos = cv_positions[i][j][k]
                mc.setAttr('{}.pt[{}][{}][{}]'.format(ffd, reversed_i, j, k), *pos)

    # match with mirrored temp ffd
    trsLib.match(ffd, ffd_dup)
    trsLib.match(ffdBase, ffdBase_dup)

    # delete temp duplicated and mirrored ffd and ffdBase
    mc.delete(ffd_dup, ffdBase_dup)

    # find deformer set
    out = (mc.listConnections(ffd_node + '.message', plugs=True) or [None])[0]
    ffdSet = None
    if '.usedBy[' in out:
        ffdSet = out.split('.')[0]

    # deform other side geos
    otherSideGeos = [geo.replace(search, replace, 1) for geo in geos]
    if otherSideGeos:
        mc.sets(mc.ls(otherSideGeos), fe=ffdSet)

    # return
    return ffd_node, ffd, ffdBase, ffdSet


def getFFDNodes(ffd):
    """
    ffd_s, ffd_node, ffdBase = deformLib.getFFDNodes(ffd)
    """
    ffd_s = trsLib.getShapes(ffd)[0]
    ffd_node = (mc.listConnections(ffd_s + '.latticeOutput') or [None])[0]
    ffdBase = (mc.listConnections(ffd_node + '.baseLattice.baseLatticeMatrix') or [None])[0]
    return ffd_s, ffd_node, ffdBase


def getShapes(mesh="", fullPath=False):
    """
    @return string[]     shape list
    """
    shapes = trsLib.getShapeOfType(node=mesh, type="mesh", fullPath=fullPath)
    return shapes


def findClosestPolygons(geoToFindPolygons, proxyGeo):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    deformLib.findClosestPolygons(geoToFindPolygons, proxyGeo)
    """
    tgtPoints = getPolygonCenters(geoToFindPolygons)
    proxyPoints = getPolygonCenters(proxyGeo)
    return getClosestPointsIDs(tgtPoints=tgtPoints, proxyPoints=proxyPoints)


def getClosestPointsIDs(tgtPoints, proxyPoints):
    """
    finds indices of points on tgtPoints that are close to proxyPoints
    """
    tree = ckdtree.cKDTree(tgtPoints)
    _, ids = tree.query(proxyPoints)
    return [x for x in ids]


def findClosestUfromGeoToCrv(geo, crv):
    """
    finds closest U value to crv for each vertex on geo
    """
    tgtPoints = getPoints(geo, asMPoint=True)
    sel = om2.MSelectionList()
    sel.add(crv)
    dag = sel.getDagPath(0)
    crvFn = om2.MFnNurbsCurve(dag)
    u_vals = []
    for tgtPnt in tgtPoints:
        pnt, u = crvFn.closestPoint(tgtPnt, space=om2.MSpace.kWorld)
        u_vals.append(u)
    return u_vals


def getCurveCVs(crv, asMPoint=False):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    deformLib.getCurveCVs('curve1')
    """
    sel = om2.MSelectionList()
    sel.add(crv)
    dag = sel.getDagPath(0)
    crvFn = om2.MFnNurbsCurve(dag)
    poses = crvFn.cvPositions(om2.MSpace.kWorld)
    if asMPoint:
        return poses
    else:
        return [[x.x, x.y, x.z] for x in poses]


def getPoints(geo, asMPoint=False):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    deformLib.getPoints('pCube1')
    """
    sel = om2.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)
    geoIt = om2.MFnMesh(dag)
    poses = geoIt.getPoints(om2.MSpace.kWorld)
    if asMPoint:
        return poses
    else:
        return [[x.x, x.y, x.z] for x in poses]


def getPolygonCenters(geo):
    sel = om2.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)
    mpIt = om2.MItMeshPolygon(dag)
    poses = []
    while not mpIt.isDone():
        pos = mpIt.center()
        poses.append([pos.x, pos.y, pos.z])
        mpIt.next(0)
    return poses


def getGeoPntColorFromCrvAndRamp(geo, crv, ramp):
    u_vals = findClosestUfromGeoToCrv(geo=geo, crv=crv)
    vals = []
    for u in u_vals:
        val = mc.colorAtPoint(ramp, u=u, v=u)[0]
        vals.append(val)
    return vals


def setBlendShapeWeights(bls, geoIdx, tgtIdx, wgts):
    """
    sets given weights (wgts) for given target (tgtIdx) on blendShape

    :param bls: blendShape node
    :param geoIdx: index of geometry (when using groups of geometires as targets)
    :param tgtIdx: index of target name on blendShape node
    :param wgts: list of weights - length of this must match the blendShape
    :return:
    """
    for i, val in enumerate(wgts):
        mc.setAttr('{}.inputTarget[{}].inputTargetGroup[{}].targetWeights[{}]'.format(bls, geoIdx, tgtIdx, i), val)


def getTargetIdx(bls, target):
    """
    get index of target on the blendShape
    """
    aliases = mc.aliasAttr(bls, q=True)  # eg: ['a', 'weight[0]', 'b', 'weight[18]']
    try:
        actuallName = target
        attrName = aliases[aliases.index(actuallName) + 1]  # eg: 'weight[18]'
        index = int(attrName.split('[')[1].split(']')[0])  # eg: 18
        return index
    except:
        mc.warning('target "{0}" does not exists on "{1}"'.format(target, bls))
        return


def setBlsWgtsFromCrv(bls, geo, crv, target=None, geoIdx=0, curveType='mid'):
    """
    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    bls = 'blendShape1'
    geos = mc.listRelatives('C_mouth_GRP', f=True)
    crv = 'curve1'
    curveType = 'mid'
    target = 'C_mouth_GRP1'
    for i, geo in enumerate(geos):
        deformLib.setBlsWgtsFromCrv(bls=bls, geo=geo, crv=crv, target=target, geoIdx=i, curveType=curveType)

    """
    mc.setAttr(bls + '.envelope', 0)
    wgts = getWgtsFromCrvAndAnimCrv(geo=geo, crv=crv, curveType=curveType)
    mc.setAttr(bls + '.envelope', 1)
    tgtIdx = getTargetIdx(bls, target) or 0
    setBlendShapeWeights(bls=bls, geoIdx=geoIdx, tgtIdx=tgtIdx, wgts=wgts)


def getWeightsAlongAnimCurve(u_vals, curveType='mid'):
    """
    gets a list of wights based on given U values and curve type
    :param u_vals: u parameter of animcurve to query its value
    :param curveType: positions on the curve eg: 'start', 'mid' or 'end'
                      '5start', '5startMid', '5mid', '5endMid', '5end'
    """
    if curveType.startswith('5'):
        curveType = curveType[1:]
        animCrv = keyLib.create5CurvePrincipleAnimCurve(curveType=curveType)
    else:
        animCrv = keyLib.create3CurvePrincipleAnimCurve(curveType=curveType)

    frameCache = mc.createNode('frameCache')
    mc.connectAttr(animCrv + '.output', frameCache + '.stream')
    vals = []
    for u in u_vals:
        mc.setAttr(frameCache + '.varyTime', u)
        val = mc.getAttr(frameCache + '.varying')
        vals.append(val)

    mc.delete(animCrv, frameCache)
    return vals


def getWgtsFromCrvAndAnimCrv(geo, crv, curveType='mid'):
    u_vals = findClosestUfromGeoToCrv(geo=geo, crv=crv)
    vals = getWeightsAlongAnimCurve(u_vals, curveType=curveType)
    return vals


def invertBlsWgts(bls):
    inputTargets = mc.ls('{}.inputTarget[*]'.format(bls))
    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromBls(bls, geoIdx)
        for i in range(numVerts):
            baseWgtAt = '{}.baseWeights[{}]'.format(inputTarget, i)
            wgts = mc.getAttr(baseWgtAt)
            val = 1.0 - wgts
            mc.setAttr(baseWgtAt, val)


def getNumVertsFromBls(bls, geoIdx):
    mesh = mc.createNode('mesh')
    mc.connectAttr('{}.outputGeometry[{}]'.format(bls, geoIdx), mesh + '.inMesh')
    numVerts = mc.polyEvaluate(mesh, v=True)
    mc.delete(mc.listRelatives(mesh, p=1))
    return numVerts


def resetBlsWgts(bls):
    inputTargets = mc.ls('{}.inputTarget[*]'.format(bls))
    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromBls(bls, geoIdx)
        for i in range(numVerts):
            baseWgtAt = '{}.baseWeights[{}]'.format(inputTarget, i)
            mc.setAttr(baseWgtAt, 1)


def exportBlsWgts(bls, path):
    """
    exports baseWeights for all geos in the blendShape node

    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)
    bls = 'blendShape1'
    bls_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', bls+'.json')
    deformLib.exportBlsWgts(bls=bls, path=bls_json)
    """
    inputTargets = mc.ls('{}.inputTarget[*]'.format(bls))

    data = OrderedDict()

    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromBls(bls, geoIdx)
        wgts = []
        for i in range(numVerts):
            wgt = mc.getAttr('{}.baseWeights[{}]'.format(inputTarget, i))
            wgts.append(wgt)
        data[inputTarget + '.baseWeights'] = wgts

    fileLib.saveJson(path=path, data=data)


def importBlsWgts(path, newBls=None):
    """
    imports baseWeights for all geos in the blendShape node

    deformLib.importBlsWgts(path=bls_json, newBls=None)
    """
    data = fileLib.loadJson(path=path)
    if not data:
        mc.error('given blendShape weight json file is no valid: {}'.format(path))

    for inputTarget, wgts in data.items():
        if newBls:
            inputTarget = newBls + '.' + inputTarget.split('.', 1)[-1]
        for i in range(len(wgts)):
            mc.setAttr('{}[{}]'.format(inputTarget, i), wgts[i])


def createShrinkWrap(driver, driven, **kwargs):
    """
    deformLib.createShrinkWrap(driver='L_Sclera_00__MSH',
                              driven='L_Pupils_00__MSH',
                              projection=4,
                              offset=0)
    """
    n = kwargs.pop('name', 'shrinkWrap1')
    driverShape = trsLib.getShapes(driver)[0]
    shrink = mc.deformLib(driven, type='shrinkWrap', name=n)[0]

    mc.connectAttr(driverShape + '.worldMesh[0]', shrink + '.targetGeom')
    mc.connectAttr(driverShape + '.continuity', shrink + '.continuity')
    mc.connectAttr(driverShape + '.smoothUVs', shrink + '.smoothUVs')
    mc.connectAttr(driverShape + '.keepBorder', shrink + '.keepBorder')
    mc.connectAttr(driverShape + '.boundaryRule', shrink + '.boundaryRule')
    mc.connectAttr(driverShape + '.keepHardEdge', shrink + '.keepHardEdge')
    mc.connectAttr(driverShape + '.propagateEdgeHardness', shrink + '.propagateEdgeHardness')
    mc.connectAttr(driverShape + '.keepMapBorders', shrink + '.keepMapBorders')

    for k, v in kwargs.items():
        mc.setAttr(shrink + '.' + k, v)

    return shrink


def exportDeformerWgts(node, path):
    """
    exports baseWeights for all geos in the blendShape node

    import rt_tools.maya.lib.deformLib as deformLib
    reload(deformLib)

    # export shrink wrap weights
    node = 'shrinkWrap1'
    wgts_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', node+'.json')
    deformLib.exportDeformerWgts(node=node, path=wgts_json)

    # export lattice weights
    lattice_cage = 'C_Body_Lattice_Cage'
    ffd_node = deformLib.getFFDNodes(lattice_cage)[1]
    data_dir = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop')
    ffd_json = os.path.join(data_dir, 'lattice', ffd_node+'_weights.json')
    deformLib.exportDeformerWgts(node=ffd_node, path=ffd_json)

    """
    # shrinkWrap1.weightList[0].weights[5]
    inputTargets = mc.ls('{}.weightList[*]'.format(node))

    data = OrderedDict()

    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromBls(node, geoIdx)
        wgts = []
        for i in range(numVerts):
            wgt = mc.getAttr('{}.weights[{}]'.format(inputTarget, i))
            wgts.append(wgt)
        data[inputTarget + '.weights'] = wgts

    fileLib.saveJson(path=path, data=data)


def importDeformerWgts(path, newNode=None):
    """
    imports baseWeights for all geos in the blendShape node

    deformLib.importDeformerWgts(path=wgts_json, newNode=None)

    """
    data = fileLib.loadJson(path=path)
    if not data:
        mc.error('given deformer weight json file is no valid: {}'.format(path))

    for wgt_attr, wgts in data.items():
        if newNode:
            wgt_attr = newNode + '.' + wgt_attr.split('.', 1)[-1]
        for i in range(len(wgts)):
            mc.setAttr('{}[{}]'.format(wgt_attr, i), wgts[i])

def blendShapeTarget(objName = '', targetName = '',blendName = ''):
    # add target
    last_used_index = mc.blendShape(objName, q=True, weightCount=True)
    new_target_index = 0 if last_used_index == 0 else last_used_index + 1
    # the only way to add an internal target is to add a physical mesh and then delete it
    temp_duplicate = mc.duplicate(objName, n=targetName)[0]
    mc.blendShape(blendName, e=True, target=(objName, new_target_index, targetName, 1.0))
    mc.delete(temp_duplicate)
    # in case duplicated base shape had deformations on it,
    # we reset the new target (0=base shape index)
    mc.blendShape(blendName, e=True, resetTargetDelta=(0, new_target_index))
    # enter sculpt target mode
    mc.blendShape(blendName, e=True, weight=(new_target_index, 1.0))
    # or use the target name: cmds.setAttr('%s.%s' % (bls, target_name), 1.0)
    mc.sculptTarget(blendName, e=True, target=new_target_index)
    # sculpt, sculpt, sculpt
    # exit sculpt target mode
    mc.sculptTarget(blendName, e=True, target=-1)
    mc.blendShape(blendName, e=True, weight=(new_target_index, 0.0))
