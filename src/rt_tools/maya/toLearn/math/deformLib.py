"""
deformLib.py

Author: Ehsan Hassani Moghaddam

"""

# python modules
import collections
import json
import os
from itertools import groupby
import sys
import logging
import re
from collections import OrderedDict
import math

# third party modules
try:
    from scipy.spatial import ckdtree
except ImportError:
    sys.stdout.write("Could not import scipy.spatial.ckdtree!")

# maya modules
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as mc
import maya.mel as mm

# iRig modules
from iRig.iRig_maya.lib import trsLib
from iRig.iRig_maya.lib import fileLib
from iRig.iRig_maya.lib import keyLib
from iRig.iRig_maya.lib import decoratorLib
# constants
logger = logging.getLogger(__name__)
skin_suffix = 'Skn'


def bind_geo(components):
    """
    Binds the geo with these items in list
    :param components: <list> list of items to bind.
    :return: <bool> for success.
    """
    # grabs geo selection // nurbsSurface selection // nurbsCurve selection
    geos = mc.filterExpand(components, sm=(12, 10, 9), fp=True)
    joints = mc.ls(components, type='joint')

    if not joints or not geos:
        mc.error("[Bind Selection] :: Incorrect components selected for skinning.")
        return False

    # binds the skin with weight blended method.
    for geo in geos:
        mc.skinCluster(joints, geo, normalizeWeights=1, bindMethod=0, skinMethod=2,
                       dropoffRate=0.5, obeyMaxInfluences=1, maximumInfluences=3, tsb=1)
    return True

@decoratorLib.timeIt
def importSkin(dataPath, node=None, ignore=None):
    """
    import skincluster weights from given path
    :param dataPath: path to the directory of skincluster weights (*.wgt files)
    :type ignore: string
    :param node: if given, only imports skin for given node
    :type ignore: string
    :param ignore: doesn't import skin for nodes in ignore list
    :type ignore: list
    """
    # search given path for skin wgt files
    if not os.path.lexists(dataPath):
        return

    json_Files = [os.path.join(dataPath, x) for x in os.listdir(dataPath)
                if x.endswith('.json')]

    wgt_Files = [os.path.join(dataPath, x) for x in os.listdir(dataPath)
                if x.endswith('.wgt')]

    wgtFiles = json_Files + wgt_Files

    # only import on given node
    if node:
        wgtFiles = [x for x in wgtFiles if node == os.path.splitext(os.path.basename(x))[0]]

    # for each wgt file, find geo and check if skinCluster exists
    for wgtFile in wgtFiles:
        skinData = importSkinData(wgtFile)
        node = skinData[0]
        infs = skinData[2]

        if ignore and (node in ignore):
            continue

        if len(mc.ls(node)) > 1:
            logger.error('There are more than one "{}" in the scene, skipped!'.format(node))
            continue

        # does geo exist?
        if not mc.objExists(node):
            logger.warning('Could not find "{0}", trying without namespace!'.format(node))
            # try without namespaces
            node = node.split(':')[-1]
            if not mc.objExists(node):
                logger.error('Could not find "{0}", skipped!'.format(node))
                continue

        # delete existing skinCluster
        sknNode = getSkinCluster(node)
        if sknNode:
            mc.delete(sknNode)

        # find missing joints
        for j in infs:
            if not mc.objExists(j):
                logger.error('joint "{0}" does not exist!'.format(j))

        # error if no joint found
        infs = mc.ls(infs)
        if not infs:
            logger.error('None of influences exist for "{}", skipped!'.format(node))
            continue

        # create a new skinCluster with found joints
        sknName = trsLib.getTransform(node) + '_' + skin_suffix
        skinData[1] = mc.skinCluster(infs, node, tsb=1, rui=0, n=sknName)[0]

        # assign weights
        setSkinData(skinData)


def exportSkin(geos, dataPath, removeUnused=False):
    """
    export skincluster weights for given rig component asset nodes
    :param removeUnused: this flag decides whether to remove unused influences from every skincluster node.
                        set it true if any error occurs in importing skin weights
    """
    geos = mc.ls(geos, type='transform')

    notSkinnedGeos = []
    for node in geos:
        sknNode = getSkinCluster(node)
        if not sknNode:
            notSkinnedGeos.append(node)
            continue

        if removeUnused:
            remove_unused_influences(sknNode)

        skinData = getSkinData(sknNode)

        node = node.rpartition(':')[2]
        wgtFiles = os.path.join(dataPath, node + '.json')

        exportSkinData(skinData, wgtFiles)
        logger.info('Exported skincluster for "{0}"'.format(node))

    if notSkinnedGeos:
        print 'No skincluster node found on nodes bellow, export skipped!'
        print '.................................................................'
        for x in notSkinnedGeos:
            print x
        print '.................................................................'


def remove_unused_influences(skinCls, targetInfluences=[]):
    """

    Snippet to removeUnusedInfluences in Autodesk Maya using Python.
    The MEL version runs slowly, over every influence one at a time.
    "targetInfluences" allows you to directly specify which influences to remove.
    This will only remove targets which are not currently being used.
    """
    allInfluences = mc.skinCluster(skinCls, q=True, inf=True)
    weightedInfluences = mc.skinCluster(skinCls, q=True, wi=True)
    unusedInfluences = [inf for inf in allInfluences if inf not in weightedInfluences]
    if targetInfluences:
        unusedInfluences = [
            inf for inf in allInfluences
            if inf in targetInfluences
            if inf not in weightedInfluences
        ]
    mc.skinCluster(skinCls, e=True, removeInfluence=unusedInfluences)


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


def getTransformFromDag(node):
    dag = getDag(node)
    is_transform = dag.hasFn(om2.MFn.kTransform)
    if is_transform:
        return dag.fullPathName().split('|')[-1]
    else:
        node_fn = om2.MFnDagNode(dag)
        if not node_fn.parentCount():
            raise Exception('Could not find transform for {}'.format(node))
        par_o = node_fn.parent(0)
        node_fn.setObject(par_o)
        return node_fn.fullPathName().split('|')[-1]


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

    # skin's output geo's shape node
    objs = fnSkin.getOutputGeometry()
    if not objs:
        mc.warning('Could not find a geo for skinCluster {}'.format(skin))
        return
    node_fn = om2.MFnDependencyNode(objs[0])
    shapeNode = node_fn.name()

    # shape's dag
    dag = getDag(shapeNode)

    # shape's transform
    geo = getTransformFromDag(shapeNode)

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

    deformer_order = get_deformer_order(geo)

    return geo, skin, infs, numVerts, wgts, blend_wgts, deformer_order


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
    wgts = [x for x in skinData[4]]
    blend_wgts = skinData[5]
    if blend_wgts:
        blend_wgts = [x for x in skinData[5]]
    deformer_order = skinData[6]

    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except:
            raise

    weight_map = dict((i, dict()) for i in range(numVerts))
    h = 0
    for i in range(numVerts):
        for j in sorted([x for x in range(0, len(infs))]):
            if wgts[h] == 0.0:
                h += 1
                continue
            weight_dict_new = {j: wgts[h]}
            weight_map[i].update(weight_dict_new)
            h += 1
        i += 1
        h = i * len(infs)

    skinData = {'geometry': geo,
                'skin_name': skin,
                'joints': infs,
                'numVerts': numVerts,
                'weights': weight_map,
                'blend_wgts': blend_wgts,
                'deformer_order': deformer_order}

    fileLib.saveJson(filePath, data=skinData)


def getSkinCluster(geo):
    return mm.eval("findRelatedSkinCluster " + geo)


def getDagShape(node):
    dagS = getDag(node)
    dagS.extendToShape()
    return dagS


def getDag(node):
    sel = om2.MSelectionList()
    try:
        sel.add(node)
        dag = sel.getDagPath(0)
        return dag
    except Exception as e:
        message = '{} "{}". There might be none or more than one ' \
                  'object with given name.'.format(e, node)
        raise Exception(message)


def dagFromMObject(m_obj):
    if m_obj.hasFn(om2.MFn.kDagNode):
        return om2.MDagPath.getAPathTo(m_obj)


def getDepend(node):
    sel = om2.MSelectionList()
    try:
        sel.add(node)
        dag = sel.getDependNode(0)
        return dag
    except Exception as e:
        message = '{} "{}". There might be none or more than one ' \
                  'object with given name.'.format(e, node)
        raise Exception(message)


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
    geo = skinData[0]
    infs = skinData[2]
    # numVerts = skinData[3]
    wgt_values = skinData[4]
    blend_wgt_values = skinData[5]
    deformer_order = skinData[6]
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
        if (mc.nodeType(infDag) != "joint"):
            raise Exception("please remove unused influence named {} and reexport skin for {}".format(infDag, skin))

        infId = fnSkin.indexForInfluenceObject(infDag)
        infIds.append(infId)

        list(set(infIds))

    # set all weights for all influences at once
    fnSkin.setWeights(dag, component, infIds, wgts)

    # blend_wgts double array
    if blend_wgt_values:
        mc.setAttr(skin + '.skinningMethod', 2)
        setSkinBlendWeights(skin, blend_wgt_values)

    set_deformer_order(geo, deformer_order)

    logger.info('Imported skincluster for "{0}"'.format(skin))


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

    if filePath.endswith('.json'):
        skin_data = fileLib.loadJson(filePath, ordered=True)
        geo = skin_data['geometry']
        joints = skin_data['joints']
        blend_wgts = skin_data['blend_wgts']
        numVerts = skin_data['numVerts']
        skin_name = skin_data['skin_name']
        deformer_order = skin_data['deformer_order']
        weight_num_dict = skin_data['weights']
        weights = [0.0] * (numVerts * len(joints))
        for vtx in range(numVerts):
            for inf in range(len(joints)):
                if str(inf) not in weight_num_dict[str(vtx)]:
                    continue
                weight_dict = weight_num_dict[str(vtx)]
                weights[(vtx * len(joints)) + inf] = weight_dict[str(inf)]

    elif filePath.endswith('.wgt'):
        deformer_order = ''
        with open(filePath, 'r') as f:
            lines = [x for x in f]
            skinData = [list(group) for k,
                                        group in groupby(lines, lambda x: x == "\n")
                        if not k]
            # get geo
            geo = _lineToStr(skinData[0])

            # get skin
            skin_name = _lineToStr(skinData[1])

            # get influences
            joints = [x.rstrip('\n') for x in skinData[2]]

            # get num verts
            numVerts = int(_lineToStr(skinData[3]))

            # get weights as one list with all weights in it
            weights = [float(x) for x in skinData[4][0].split(' ')]

            # get blend weights
            blend_wgts = None
            if len(skinData) > 5:
                blend_wgts = [float(x) for x in skinData[5][0].split(' ')]
                
    return [geo, skin_name, joints, numVerts, weights, blend_wgts, deformer_order]


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
    for i in xrange(numVerts):
        tempList = [i]
        for j in xrange(numInfs):
            tempList.append(float(wgts[(i * numInfs) + j]))
        wgtsList.append(tempList)
    return wgtsList


def copySkin(src=None, targets=None, useSelection=False):
    """
    from iRig_maya.lib import deformLib
    deformLib.copySkin(useSelection=True)
    """
    if useSelection:
        sels = mc.ls(sl=True)
        if len(sels) < 2:
            logger.error('Need to provide a source geo + target geo(s) to copy skinCluster!')
        src = sels[0]
        targets = sels[1:]

    if isinstance(targets, basestring):
        targets = [targets]

    # get joints from src
    src_skin = getSkinCluster(src)
    infs = mc.skinCluster(src_skin, q=True, inf=True)

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

    # keep user selection
    if useSelection:
        mc.select(sels)

    logger.info("[Finished Skin] :: {}".format(skn_nodes))

    return skn_nodes


def skinOtherSide(sources=None, useSelection=False):
    """
    mirrors the skinning of geometries of selected objects to objects on the other side.
    from iRig_maya.lib import deformLib
    deformLib.skinOtherSide(useSelection=True)
    """
    if useSelection:
        sources = mc.ls(sl=True)
        if not sources:
            logger.error('Need to provide source geos to mirror the skin to the other side!')
            return

    if isinstance(sources, basestring):
        sources = [sources]

    skn_nodes = []
    for src in sources:
        # find side and other side
        geo_no_namespace = src.split(':')[-1]
        side = geo_no_namespace[0]
        other_side = get_other_side(side)

        # find other side (target) geos
        tgt = '{0}{1}'.format(other_side, src[1:])
        if not mc.objExists(tgt):
            logging.warning('Geo does not exist, skipped: {}'.format(tgt))
            continue

        # delete current skinCluster if exists
        skn = getSkinCluster(tgt)
        if skn:
            mc.delete(skn)

        # get skincluster from src
        src_skin = getSkinCluster(src)
        if not src_skin:
            logger.warning('Could not find skincluster on source geo "{}"'.format(src))
            continue

        # get joints from src
        infs = mc.skinCluster(src_skin, q=True, inf=True)

        # find joints for other side geos
        infs_other_side = []
        for inf in infs:
            if ':' in inf:
                ns = inf.rsplit(':', 1)[0]
                inf = inf.split(':')[-1]
            else:
                ns = ''
            inf_side = inf[0]
            other_inf_side = get_other_side(inf_side)
            infs_other_side.append('{0}:{1}{2}'.format(ns, other_inf_side, inf[1:]))

        # create skin for target
        skn_node = tgt + '_' + skin_suffix
        mc.skinCluster(infs_other_side, tgt, toSelectedBones=True, n=skn_node)
        skn_nodes.append(skn_node)

        # copy weights from src to target
        mc.copySkinWeights(
            ss=src_skin,
            ds=skn_node,
            mirrorMode='YZ',
            surfaceAssociation='closestPoint',
            influenceAssociation=['label', 'closestJoint']
        )

    # keep user selection
    if useSelection:
        mc.select(sources)

    logger.info("[Finished Mirror Skin] :: {}".format(skn_nodes))

    return skn_nodes


def get_other_side(side):
    sides_dict = {
        'C': 'C',
        'L': 'R',
        'R': 'L',
    }
    return sides_dict.get(side, side)


def copySkinFromReference():
    """
    copy skin from referenced to last selected
    """
    sels = mc.ls(sl=True)
    source = sels[0]
    target = sels[1]
    infs = mc.skinCluster(source, q=True, inf=True)

    infs = mc.ls([x.split(':')[-1] for x in infs])
    mc.skinCluster(infs, target, tsb=True)

    mc.copySkinWeights(source,
                       target,
                       noMirror=True,
                       surfaceAssociation='closestPoint',
                       influenceAssociation=['label', 'name', 'closestJoint'])


def getSkinBlendWeights(skin):
    # get skin fn
    skin_fn = getFnSkin(skin)

    # get shape
    # probably maya bug skin_fn.getPathAtIndex(0) sometimes doesn't return anything.
    shape_mobj = skin_fn.getOutputGeometry()[0]
    shape_dag = dagFromMObject(shape_mobj)

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

    import iRig.iRig_maya.lib.deformLib as deformLib
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
    import iRig.iRig_maya.lib.deformLib as deformLib
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
    import iRig.iRig_maya.lib.deformLib as deformLib
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


def findClosestPolygons(searchGeo, targetGeo):
    """
    for each face of targetGeo, finds closest face on searchGeo.
    usage:
        import iRig.iRig_maya.lib.deformLib as deformLib
        reload(deformLib)
        deformLib.findClosestPolygons(searchGeo, targetGeo)
    :param searchGeo: geo to find face indices on
                      eg: source geo with good deformer weights
    :param targetGeo: for each face of this geo, search the other geo
                      eg: geometry to copy weights to.
    :return: (list)
        indices of closets faces of searchGeo, eg: [3, 4, 2, 4]
    """
    searchPoints = getPolygonCenters(searchGeo)
    targetPoints = getPolygonCenters(targetGeo)
    return getClosestPointsIDs(
        searchPoints=searchPoints,
        targetPoints=targetPoints
    )


def getClosestPointsIDs(searchPoints, targetPoints, count=1):
    """
    finds indices of points on searchPoints that are close to targetPoints
    """
    tree = ckdtree.cKDTree(searchPoints)
    _, ids = tree.query(targetPoints, k=count)
    return [x.tolist() for x in ids]


def get3ClosestVerts(searchGeo, targetGeo):
    searchPoints = getPoints(searchGeo)
    targetPoints = getPoints(targetGeo)
    return getClosestPointsIDs(
        searchPoints=searchPoints,
        targetPoints=targetPoints,
        count=3,
    )


def getClosestPoint(from_point, mesh_name):
    target_point = om2.MPoint(*from_point)
    sel = om2.MSelectionList()
    sel.add(mesh_name)
    geo_mobj = sel.getDependNode(0)
    mesh_intersector = om2.MMeshIntersector()
    mesh_intersector.create(geo_mobj)
    point_on_mesh = mesh_intersector.getClosestPoint(target_point)
    return point_on_mesh.point


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
    import iRig.iRig_maya.lib.deformLib as deformLib
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


def getPoints(geo, asMPoint=False, space=om2.MSpace.kWorld):
    """
    import iRig.iRig_maya.lib.deformLib as deformLib
    reload(deformLib)
    deformLib.getPoints('pCube1')
    """
    sel = om2.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)
    geoIt = om2.MFnMesh(dag)
    poses = geoIt.getPoints(space=space)
    if asMPoint:
        return poses
    else:
        return [[x.x, x.y, x.z] for x in poses]


def getPolygonCenters(geo, space=om2.MSpace.kWorld):
    sel = om2.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)
    mpIt = om2.MItMeshPolygon(dag)
    poses = []
    while not mpIt.isDone():
        pos = mpIt.center(space=space)
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
    import iRig.iRig_maya.lib.deformLib as deformLib
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
        numVerts = getNumVertsFromDeformer(bls, geoIdx)
        for i in range(numVerts):
            baseWgtAt = '{}.baseWeights[{}]'.format(inputTarget, i)
            wgts = mc.getAttr(baseWgtAt)
            val = 1.0 - wgts
            mc.setAttr(baseWgtAt, val)


def getNumVertsFromDeformer(bls, geoIdx):
    mesh = mc.createNode('mesh')
    mc.connectAttr('{}.outputGeometry[{}]'.format(bls, geoIdx), mesh + '.inMesh')
    numVerts = mc.polyEvaluate(mesh, v=True)
    mc.delete(mc.listRelatives(mesh, p=1))
    return numVerts


def resetBlsWgts(bls):
    inputTargets = mc.ls('{}.inputTarget[*]'.format(bls))
    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromDeformer(bls, geoIdx)
        for i in range(numVerts):
            baseWgtAt = '{}.baseWeights[{}]'.format(inputTarget, i)
            mc.setAttr(baseWgtAt, 1)


def exportBlsWgts(bls, path):
    """
    exports baseWeights for all geos in the blendShape node

    import iRig.iRig_maya.lib.deformLib as deformLib
    reload(deformLib)
    bls = 'blendShape1'
    bls_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', bls+'.json')
    deformLib.exportBlsWgts(bls=bls, path=bls_json)
    """
    inputTargets = mc.ls('{}.inputTarget[*]'.format(bls))

    data = OrderedDict()

    for inputTarget in inputTargets:
        geoIdx = int(re.findall(r'(\d+)', inputTarget)[-1])
        numVerts = getNumVertsFromDeformer(bls, geoIdx)
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
    shrink = mc.deformer(driven, type='shrinkWrap', name=n)[0]

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


def createWrap(driver, driven):
    mc.select(driven, driver)
    wrap_node = mm.eval(
        'doWrapArgList "7" {"1", "0", "1", "2", "1", "1", "0", "0"};'
    )[0]
    return wrap_node


def exportDeformerWgts(node, path):
    """
    exports deformer weights

    import iRig.iRig_maya.lib.deformLib as deformLib
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

    deformer_order_data = OrderedDict()

    geos = mc.deformer(
        node,
        query=True,
        geometry=True
    )
    for geo in geos:
        deformer_order = get_deformer_order(geo)
        deformer_order_data[geo] = deformer_order

    deformer_weights = getDeformerWeights(node)

    deformer_data = {'weights': deformer_weights,
                     'deformer_order': deformer_order_data}

    fileLib.saveJson(path=path, data=deformer_data)

    logger.info('Weights were exported for "{}" here: {}'.format(node, path))


def importDeformerWgts(path, deformer_name=None):
    """
    imports deformer weight from given path
    deformLib.importDeformerWgts(path=wgts_json)
    """
    deformer_data = fileLib.loadJson(path=path)
    if not deformer_data:
        mc.error('given deformer weight json file is no valid: {}'.format(path))

    deformer_weights = deformer_data['weights']
    deformer_order = deformer_data['deformer_order']

    if deformer_name:
        deformer_node = deformer_name
    else:
        deformer_node = os.path.splitext(os.path.basename(path))[0]

    for key in deformer_weights:
        if mc.objExists(deformer_node):
            if not key in mc.deformer(deformer_node, q=True, g=True):
                addGeosToDeformer(geos=key, deformer=deformer_node)
    setDeformerWgts(deformer=deformer_node, weights_data=deformer_weights)

    for geo, order in deformer_order.items():
        set_deformer_order(geo, order)


def getDeformerSet(node):
    """
    Finds deformer set on given deformer node
    """
    outs = mc.listConnections(node + '.message', plugs=True) or [None]
    for out in outs:
        if '.usedBy[' in out:
            return out.split('.')[0]


def copyLattice(source, targets):
    """
    deforms target geos using the same lattice on source geo
    copies lattice weights from source to targets too
    :param source: source geo that has lattice on it
    :param targets: geometries to add the same lattice found on source
    :return: N/A
    """
    # find lattice on source
    ffds = findDeformersByType(source, deformer_type='ffd')
    if not ffds:
        return

    # apply lattice to targets
    for ffd in ffds:
        addGeosToDeformer(geos=targets, deformer=ffd)

        # copy weights to targets
        copyDeformerWeights(source, targets, ffd)


def copyDeformer(source, targets, deformer, Weights_only=False, target_deformer=None):
    """
    deforms target geos using the same deformer on source geo
    copies deformer weights from source to targets too

    :usage:
        import maya.cmds as mc
        import iRig.iRig_maya.lib.deformLib as deformLib
        reload(deformLib)

        source = 'Body_Geo'
        targets = mc.ls(sl=True)
        deformers = [
            'C_HeadSquash_SquashY_Def',
            'C_HeadSquash_BendX_Def',
            'C_HeadSquash_BendZ_Def'
        ]
        for deformer in deformers:
            deformLib.copyDeformer(source, targets, deformer)

    :param source: source geo that has deformer on it
    :param targets: geometries to add the same deformer found on source
    :param deformer: the deform we want to copy from source to targets
    :return: N/A
    """
    # apply deformer to targets
    if not Weights_only:
        addGeosToDeformer(geos=targets, deformer=deformer)

    # copy weights to targets
    copyDeformerWeights(source, targets, deformer, target_deformer=target_deformer)


def findDeformersByType(geo, deformer_type='ffd'):
    """
    finds deformers of given type on given geo
    :param geo: geometry to find deformers for
    :param deformer_type: type of deformers to look for on given geo
    :return: list of found deformers on geo
    """
    deformers = mc.findDeformers(geo)

    nodes = []
    for node in deformers:
        if mc.nodeType(node) == deformer_type:
            nodes.append(node)

    return nodes


def addGeosToDeformer(geos, deformer):
    """
    deforms given geos by given deformer
    :param geos: name of geometries to deform
    :param deformer: name of deformer node which will deform geos
    :return: N/A
    """
    mc.deformer(deformer, geometry=geos, edit=True)


def getDeformerWeights(deformer):
    """
    gets weights of all geos for given deformer as a dictionary
    with geo name as key and weights as value
    :param deformer: name of deformer to get weigths from
    :return: OrderedDict of geos and weights
    """
    geo_indices_dict = getGeoIndicesFromDeformer(deformer)

    deformer_weights = OrderedDict()
    for geo in geo_indices_dict.keys():
        deformer_weights[geo] = getDeformerWgtsForGeo(geo, deformer)

    return deformer_weights


def setDeformerWgts(deformer, weights_data):
    """
    sets deformer weights for given deformer
    :param deformer: deformer to set weights for
    :param weights_data: dictionary of weights with geo_name as keys
           and weights as values. eg: {'pCube1': [0.0, 1.0, ...]}
    :return: N/A
    """
    for geo, weights in weights_data.items():
        setDeformerWgtsForGeo(geo, deformer, weights)


def setDeformerWgtsForGeo(geo, deformer, weights):
    """
    sets deformer weights for given geometry
    :param geo: geo to set deformer weights for
    :param deformer: deformer node to set weights for
    :param weights: list of weights for given geo. eg: [1.0, 0.0, ...]
    :return: N/A
    """
    # attribute name was saved as key, eg: 'deltaMush1.weightList[0].weights' (old system)
    if geo.endswith('weights'):
        attr = geo

    # geo name is saved as key (new system)
    else:
        index = getGeoIndexFromDeformer(geo, deformer)
        if index is None:
            mc.warning('Weights were not set for "{}" as it is not deformed by "{}"'.format(geo, deformer))
            return
        attr = '{}.weightList[{}].weights'.format(deformer, index)

    # set weights
    for i in range(len(weights)):
        mc.setAttr('{}[{}]'.format(attr, i), weights[i])


def getDeformerWgtsForGeo(geo, deformer):
    """
    Get deformer weights for given geo on given deformer
    :param geo: name of geo to get its weights
    :param deformer: name of deformer on geo we want to get weights for
    :return: list of vertex weights. eg: [1.0, 0.0, ...]
    """
    geo_idx = getGeoIndexFromDeformer(geo, deformer)

    numVerts = mc.polyEvaluate(geo, v=True)
    # find out vertices of the geo that are deforming
    deformer_set = getDeformerSet(deformer)
    all_deformed_verts = mc.sets(deformer_set, query=True)
    this_geos_deformed_verts = [x for x in all_deformed_verts if geo in x or mc.listRelatives(geo, p=True)[0] in x]
    deformed_verts = mc.ls(this_geos_deformed_verts, fl=True)
    deformed_vert_ids = [int(x.split('[')[1][:-1]) for x in deformed_verts]

    # get a list of weights for all verts (the ones out of deformer set have 0.0 weight)
    wgts = []
    for i in range(numVerts):
        if i in deformed_vert_ids:
            attr = '{}.weightList[{}].weights[{}]'.format(deformer, geo_idx, i)
            wgt = mc.getAttr(attr)
            wgts.append(wgt)
        else:
            wgts.append(0.0)

    return wgts

def mirror_deformer_wgts(geo, tolerance = 0.02):

    mSel = om2.MSelectionList()
    mSel.add(geo)
    mObj = mSel.getDagPath(0)
    mfnMesh = om2.MFnMesh(mObj)
    baseShape = mfnMesh.getPoints()
    mfnMesh.setPoints(baseShape)

    lVerts = []
    rVerts = []
    mVerts = []
    corresponding_Verts = {}

    for i in range(mfnMesh.numVertices):
        thisPoint = mfnMesh.getPoint(i)

        if thisPoint.x > 0 + tolerance:
            lVerts.append((i, thisPoint))

        elif thisPoint.x < 0 - tolerance:
            rVerts.append((i, thisPoint))

        else:
            mVerts.append((i, thisPoint))

    rVertspoints = [i for v, i in rVerts]
    for vert, mp in lVerts:
        nmp = om2.MPoint(-mp.x, mp.y, mp.z)
        rp = mfnMesh.getClosestPoint(nmp)
        if rp[0] in rVertspoints:
            corresponding_Verts[vert] = rVerts[rVertspoints.index(rp[0])][0]
        else:
            dList = [nmp.distanceTo(rVert) for rVert in rVertspoints]
            mindist = min(dList)
            corresponding_Verts[vert] = rVerts[dList.index(mindist)][0]

    return(corresponding_Verts)


def get_side_deformer_wgts(geo, deformer):
    geo_idx = getGeoIndexFromDeformer(geo, deformer)

    numVerts = mc.polyEvaluate(geo, v=True)
    # find out vertices of the geo that are deforming
    deformer_set = getDeformerSet(deformer)
    all_deformed_verts = mc.sets(deformer_set, query=True)
    this_geos_deformed_verts = [x for x in all_deformed_verts if geo in x or mc.listRelatives(geo, p=True)[0] in x]
    deformed_verts = mc.ls(this_geos_deformed_verts, fl=True)
    deformed_vert_ids = [int(x.split('[')[1][:-1]) for x in deformed_verts]

    # get a list of weights for all verts (the ones out of deformer set have 0.0 weight)
    dict_vert_ids = mirror_deformer_wgts(geo)
    left_vert_ids = [x for x in dict_vert_ids]
    deformed_left_vert_ids = [x for x in deformed_vert_ids if x in left_vert_ids]

    wgts = []
    rightAttrs = []
    for i in range(numVerts):
        if i in deformed_left_vert_ids:
            attr = '{}.weightList[{}].weights[{}]'.format(deformer, geo_idx, i)
            wgt = mc.getAttr(attr)
            wgts.append(wgt)
            rightId = dict_vert_ids[i]
            right_attr = '{}.weightList[{}].weights[{}]'.format(deformer, geo_idx, rightId)
            rightAttrs.append(right_attr)

    return wgts, rightAttrs

def set_side_deformer_wgts(weights, rightAttr):
    # set weights
    for i, j in zip(weights, rightAttr):
        mc.setAttr('{}'.format(j), i)


def getGeoIndexFromDeformer(geo, deformer):
    """
    finds index of geo on given deformer
    :param geo: geo name to find deformer index for
    :param deformer: node deforming geo
    :return: (int) index of given geometry on given deformer
    """
    shapes = getShapes(geo)
    if not shapes:
        return
    shape = shapes[0]

    geo_indices_dict = getGeoIndicesFromDeformer(deformer)

    return geo_indices_dict.get(shape, None)


def getGeoIndicesFromDeformer(deformer):
    """
    get a dictionary of all geos and indices on a deformer
    :param deformer: deformer to find geos and indices from
    :return: (OrderedDict) geos and their indices on given deformer
             eg: {'pCube1Shape': 0, 'pSphere1Shape': 1}
    """
    geos = mc.deformer(
        deformer,
        query=True,
        geometry=True
    )
    indices = mc.deformer(
        deformer,
        query=True,
        geometryIndices=True
    )

    geo_indices_dict = OrderedDict()

    for geo, index in zip(geos, indices):
        geo_indices_dict[geo] = index

    return geo_indices_dict


def copyDeformerWeights(source, targets, deformer, target_deformer=None):
    """
    copies deformer weights from source to targets

    :param source: source geo to copy weights from
    :type source: string
    :param targets: geometries to paste weights on
    :type targets: list
    :param deformer: deformer node driving source and targets
                     to set weights for
    :return: N/A
    """
    src_weights = getDeformerWgtsForGeo(source, deformer)
    searchPoints = getPoints(source, asMPoint=True)
    for target in targets:
        targetPoints = getPoints(target, asMPoint=True)
        approximate_weights = approximateWeights(
            searchPoints,
            targetPoints,
            src_weights
        )
        if target_deformer:
            setDeformerWgtsForGeo(target, target_deformer, approximate_weights)
            logger.info('Copied weights from "{0}_{1}" on  "{2}_{3}"'.format(source, deformer, target, target_deformer))

        else:
            setDeformerWgtsForGeo(target, deformer, approximate_weights)
            logger.info('Copied deformer from "{0}_{1}" on  "{2}"'.format(source, deformer, target))


def approximateWeights(searchPoints, targetPoints, weights):
    """
    find the best possible weight value for given target geometry.
    for each target vertex, finds the 3 closest verts on source, then
    finds all vertex weights of that face, and calculates the best
    weight using barrycentric coordinates.

    :param searchPoints: source points that has given weights
    :type searchPoints: list of vertex positions, eg: MPoint
    :param targetPoints: target points to find weights for
    :type targetPoints: list of vertex positions, eg: MPoint
    :param weights: list of deformer weights of source geo
    :return: list of weights. eg: [1.0, 0.0, ...]
    """
    triangle_indices = getClosestPointsIDs(
        searchPoints=[[x.x, x.y, x.z] for x in searchPoints],
        targetPoints=[[x.x, x.y, x.z] for x in targetPoints],
        count=3,
    )
    triangle_points = []
    for indices in triangle_indices:
        triangle_points.append(
            [
                searchPoints[indices[0]],
                searchPoints[indices[1]],
                searchPoints[indices[2]],
            ]
        )
    approximate_weights = []
    for i in range(len(triangle_indices)):
        indices = triangle_indices[i]
        w_1, w_2, w_3 = get_barrycentric_coords(
            point=targetPoints[i],
            triangle_points=triangle_points[i],
        )
        wgt_1 = weights[indices[0]] * w_1
        wgt_2 = weights[indices[1]] * w_2
        wgt_3 = weights[indices[2]] * w_3
        approximate_weights.append(wgt_1 + wgt_2 + wgt_3)

    return approximate_weights


def get_barrycentric_coords(point, triangle_points):
    """
    find barrycentric coordinates from given point on given triangle

    :param point: the point we want to find its barrycentric coordinates for
    :type point: MPoint or list of 3 floats
    :param triangle_points: triangle corners we want to get coordinates on
    :type triangle_points: list of 3 MPoint or list of 3 lists of 3 floats
    :return: 3 barrycentric coordinate values
    :return type: list of 3 floats
    """
    point = om2.MVector(point)
    p_1, p_2, p_3 = [om2.MVector(x) for x in triangle_points]

    tri_area = get_triangle_area(p_1, p_2, p_3)

    # for faster results if source and target points are exactly on top of each other
    # we can use the source weights directly without any interpolation
    point_len = point.length()
    p_1_len = p_1.length()
    p_2_len = p_2.length()
    p_3_len = p_3.length()
    if point_len - p_1_len < 0.0001:
        return 1.0, 0.0, 0.0
    elif point_len - p_2_len < 0.0001:
        return 0.0, 1.0, 0.0
    elif point_len - p_3_len < 0.0001:
        return 0.0, 0.0, 1.0

    # points don't make a triangle, they make a line
    # project point on the line and linearly interpolate weights based on distances
    if tri_area < 0.0000001:
        w_1, w_2, w_3 = get_point_ratio_on_line(point, [p_1, p_2, p_3])

    else:
        # project point on triangle plane
        projected_point = project_point_on_plane(point, [p_1, p_2, p_3])

        # calculate sub triangles areas
        area_1 = get_triangle_area(p_2, p_3, projected_point)
        area_2 = get_triangle_area(p_3, p_1, projected_point)
        area_3 = get_triangle_area(p_1, p_2, projected_point)

        # get area ratio (barrycentric coordinates)
        w_1 = area_1 / tri_area
        w_2 = area_2 / tri_area
        w_3 = area_3 / tri_area

        point_outside_triangle = w_1 < 0.0 or \
                                 w_2 < 0.0 or \
                                 w_3 < 0.0 or \
                                 w_1 + w_2 + w_3 > 1.0

        if point_outside_triangle:
            closest_1 = closest_point_on_line(point, [p_1, p_2])
            closest_2 = closest_point_on_line(point, [p_1, p_3])
            closest_3 = closest_point_on_line(point, [p_2, p_3])

            len_1 = (closest_1 - point).length()
            len_2 = (closest_2 - point).length()
            len_3 = (closest_3 - point).length()

            if len_1 <= len_2 and len_1 <= len_3:
                w_1, w_2, w_3 = get_point_ratio_on_line(point, [p_1, p_2, p_2])
            elif len_2 <= len_1 and len_2 <= len_3:
                w_1, w_2, w_3 = get_point_ratio_on_line(point, [p_1, p_3, p_3])
            elif len_3 <= len_1 and len_3 <= len_2:
                w_1, w_2, w_3 = get_point_ratio_on_line(point, [p_2, p_3, p_3])

    return w_1, w_2, w_3


def get_triangle_area(A, B, C):
    AC = C - A
    AB = B - A
    dot = AB.normal() * AC.normal()
    if dot > 0.9999999 or dot < -0.9999999:
        return 0.0
    area = (AC.length() * AB.length()) * math.sin(math.acos(dot)) / 2.0
    return area


def project_point_on_plane(point, triangle_points):
    p_1, p_2, p_3 = triangle_points

    tri_normal = ((p_2 - p_1) ^ (p_3 - p_1)).normal()

    p1_to_point = point - p_1

    perpendular_distance = p1_to_point * tri_normal

    projected_point = point - (tri_normal * perpendular_distance)

    return projected_point


def project_point_on_line(point, line_points):
    p_1, p_2 = line_points

    p1_to_p2_normal = (p_2 - p_1).normal()

    p1_to_point = point - p_1

    dist_from_p1 = p1_to_point * p1_to_p2_normal

    projected_p = p_1 + (p1_to_p2_normal * dist_from_p1)

    return projected_p


def closest_point_on_line(point, line_points):
    p_1, p_2 = line_points
    line = p_2 - p_1
    line_len = line.length()

    project_point = project_point_on_line(point, line_points)
    p1_to_proj_pnt = project_point - p_1

    dot = p1_to_proj_pnt * line
    sign = 1 if dot > 0.0 else -1

    p1_to_proj_pnt_dist = p1_to_proj_pnt.length() * sign

    if 0 < p1_to_proj_pnt_dist < line_len:
        return p_1 + p1_to_proj_pnt
    if p1_to_proj_pnt_dist < line_len:
        return p_1
    elif p1_to_proj_pnt_dist > line_len:
        return p_2


def get_point_ratio_on_line(point, line_points):
    p_1, p_2, p_3 = line_points

    projected_point = project_point_on_line(point, [p_1, p_2])

    d_1 = (p_1 - projected_point).length()
    d_2 = (p_2 - projected_point).length()
    d_3 = (p_3 - projected_point).length()
    dists = [d_1, d_2, d_3]

    biggest_dist_value_index = dists.index(max(dists))

    if biggest_dist_value_index == 0:
        w_1 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_3 - p_2).length()
        if d_2 > line_len:  # point is too far from p_2
            w_2 = 0.0
            w_3 = 1.0
        elif d_3 > line_len:  # point is too far from p_3
            w_3 = 0.0
            w_2 = 1.0
        else:  # point is somewhere between p_2 and p_3
            w_2 = 1.0 - (d_2 / line_len)
            w_3 = 1.0 - w_2

    elif biggest_dist_value_index == 1:
        w_2 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_3 - p_1).length()
        if d_1 > line_len:  # point is too far from p_1
            w_1 = 0.0
            w_3 = 1.0
        elif d_3 > line_len:  # point is too far from p_3
            w_3 = 0.0
            w_1 = 1.0
        else:  # point is somewhere between p_1 and p_3
            w_1 = 1.0 - (d_1 / line_len)
            w_3 = 1.0 - w_1

    elif biggest_dist_value_index == 2:
        w_3 = 0.0
        # point is outside the full line,  farthest weight is 0.0
        line_len = (p_2 - p_1).length()
        if d_2 > line_len:  # point is too far from p_2
            w_2 = 0.0
            w_1 = 1.0
        elif d_1 > line_len:  # point is too far from p_1
            w_1 = 0.0
            w_2 = 1.0
        else:  # point is somewhere between p_1 and p_2
            w_1 = 1.0 - (d_1 / line_len)
            w_2 = 1.0 - w_1

    return w_1, w_2, w_3

def set_deformer_order(item_name, deformers):
    for deformer_1, deformer_2 in zip(deformers[:-1], deformers[1:]):
        try:
            mc.reorderDeformers(
                deformer_1,
                deformer_2,
                item_name
            )

        except RuntimeError:
            logger.info(
                'could not reorder: `%s` with `%s` on `%s`'
                % (deformer_1, deformer_2, item_name)
            )


def get_deformer_order(item_name):

    return [
        x for x in (
            mc.listHistory(
                item_name,
                pruneDagObjects=True,
                interestLevel=1
            )
            or []
        )
        if 'geometryFilter' in mc.nodeType(x, inherited=True)
    ]
