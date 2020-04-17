"""
deformLib.py

author: Ehsan Hassani Moghaddam

"""

# python modules
import os
from itertools import groupby
import sys
import logging

# third party modules
try:
    from scipy.spatial import ckdtree
except ImportError:
    sys.stdout.write("Could not import scipy.spatial.ckdtree!")

# maya modules
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as mc

# iRig modules
from iRig_maya.lib import trsLib

# constants
logger = logging.getLogger(__name__)


def importSkin(dataPath):
    """
    import skincluster weights from given path
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

        # make sure skinCluster node exists and has the right name
        sknNode = getSkinCluster(node)
        sknName = trsLib.getTransform(node) + '_SKN'
        if sknNode:
            mc.rename(sknNode, sknName)
        else:
            for j in skinData[2]:
                if not mc.objExists(j):
                    logger.error('joint "{0}" does not exist!'.format(j))

            infs = mc.ls(skinData[2])
            if not infs:
                logger.error('None of influences below exist for "{}", skipped!'.format(node))
                continue

            mc.skinCluster(infs, node, tsb=1, rui=0, n=sknName)

        # assign weights
        setSkinData(skinData)


def exportSkin(geos, dataPath):
    """
    export skincluster weights for given rig component asset nodes
    """
    notSkinnedGeos = []
    for node in geos:
        print 'Exporting skinculster for "{0}"'.format(node)
        sknNode = getSkinCluster(node)
        if not sknNode:
            notSkinnedGeos.append(node)
            continue
        sknNode = mc.rename(sknNode, node.split('Shape')[0] + '_SKN')
        skinData = getSkinData(sknNode)

        wgtFiles = os.path.join(dataPath, node + '.wgt')

        exportSkinData(skinData, wgtFiles)

    if notSkinnedGeos:
        print 'No skincluster node found on nodes bellow, export skipped!'
        print '.................................................................'
        for x in notSkinnedGeos:
            print x
        print '.................................................................'


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


def createSkinCluster(geos):
    """
    :return: sets self.skins to a list of newly created skincluster nodes
    """
    skins = []
    for geometry in geos:
        skin = mc.skinCluster('C_root_JNT', geometry, name=geometry + '_SKN')
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

        return geo, skin, infs, numVerts, wgts, blend_wgts


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


def createFFD(geos, name, divisions=(2, 3, 2),
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
