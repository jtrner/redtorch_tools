import datetime
import os
from itertools import groupby
from collections import OrderedDict
import sys
import re
stdout = sys.stdout

try:
    from scipy.spatial import ckdtree
except:
    stdout.write("Could not import scipy.spatial.ckdtree!")

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as mc
import maya.mel as mm

from . import control
from . import attrLib
from . import trsLib
from . import strLib
from . import fileLib
from . import meshLib
from . import key


def getDag(objName):
    sel = om.MSelectionList()
    sel.add(objName)
    dag = om.MDagPath()
    sel.getDagPath(0, dag)
    return dag


def resetSkinCluster(skinCluster):
    """
    splats the current pose of the skeleton into the skinCluster - ie whatever
    the current pose is becomes the bindpose
    """
    nInf = len(mc.listConnections('%s.matrix' % skinCluster, destination=False))
    for n in range(nInf):
        try:
            slotNJoint = mc.listConnections('%s.matrix[ %d ]' % (skinCluster, n), destination=False)[0]
        except IndexError:
            continue

        matrixAsStr = ' '.join(map(str, mc.getAttr('%s.worldInverseMatrix' % slotNJoint)))
        melStr = 'setAttr -type "matrix" %s.bindPreMatrix[ %d ] %s' % (skinCluster, n, matrixAsStr)
        mm.eval(melStr)

        # reset the stored pose in any dagposes that are conn
        for dPose in mc.listConnections(skinCluster, d=False, type='dagPose') or []:
            mc.dagPose(slotNJoint, reset=True, n=dPose)


def getDeformers(obj, _type):
    nodes = []
    history = mc.listHistory(obj)
    for node in history:
        nodeTypes = mc.nodeType(node, inherited=True)
        if ('geometryFilter' in nodeTypes) and (mc.nodeType(node) == _type):
            nodes.append(node)
    return nodes


def getAllDeformers(obj, ignoredDeformersList=None):
    nodes = []
    history = mc.listHistory(obj)
    for node in history:
        nodeTypes = mc.nodeType(node, inherited=True)
        if ('geometryFilter' in nodeTypes):
            addIt = True
            if ignoredDeformersList:
                for exc in ignoredDeformersList:
                    if mc.nodeType(node) == exc:
                        addIt = False
                        break
            if addIt:
                nodes.append(node)
    return nodes


def getDeformer(obj, _type):
    nodes = getDeformers(obj, _type)
    if nodes:
        return nodes[0]


def getSkinCluster(obj):
    fnSkin = getFnSkinCluster(obj)
    if fnSkin:
        return fnSkin.name()


def getFnSkin(skin):
    skinDepend = getDependByName(skin)
    return oma.MFnSkinCluster(skinDepend)


def getDependByName(objName):
    sel = om.MSelectionList()
    try:
        sel.add(objName)
    except :
        mc.error('Object does not exist: {0}'.format(objName))
    depend = om.MObject()
    sel.getDependNode(0, depend)
    return depend


def getComponent(dag):
    """
    create vertex component
    :return: om.MFn.kMeshVertComponent
    """
    # geo iter
    itGeo = om.MItGeometry(dag)

    # create components variable
    numVerts = itGeo.count()
    fnComp = om.MFnSingleIndexedComponent()
    oComps = fnComp.create(om.MFn.kMeshVertComponent)
    for i in xrange(numVerts):
        fnComp.addElement(i)

    return oComps


def getInfs(skin):
    """
    get influences
    :param skin:
    :return: list of influence names
    :return type: list of strings
    """
    fnSkin = getFnSkin(skin)
    aInfDagA = om.MDagPathArray()
    fnSkin.influenceObjects(aInfDagA)
    numInfs = aInfDagA.length()
    infs = []
    for i in xrange(numInfs):
        inf = aInfDagA[i].fullPathName().split('|')[-1]
        infs.append(inf)

    return infs


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
    :return: list with 5 elements in it:
                                geo, skin, infs, numVerts, wgts
    """
    # skin fn
    fnSkin = getFnSkin(skin)

    # geo
    dag = om.MDagPath()
    fnSkin.getPathAtIndex(0, dag)
    geo = dag.fullPathName().split('|')[-1]

    # create weight variable
    wgts = om.MDoubleArray()

    # create components variable
    oComps = getComponent(dag)

    # num of vertices
    itGeo = om.MItGeometry(dag)
    numVerts = itGeo.count()

    # get influence names
    infs = getInfs(skin)

    # create a pointer to number of influences
    su = om.MScriptUtil()
    su.createFromInt(len(infs))
    numInfsPtr = su.asUintPtr()

    # get all weights for all influences at once
    fnSkin.getWeights(dag, oComps, wgts, numInfsPtr)

    if weightsAsList:
        wgts = _lineToLists(wgts, numVerts, len(infs))

    return geo, skin, infs, numVerts, wgts


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
    numVerts = skinData[3]
    wgtsValues = skinData[-1]
    numInfs = len(infs)

    # skin fn
    fnSkin = getFnSkin(skin)

    # geo iter
    dag = om.MDagPath()
    fnSkin.getPathAtIndex(0, dag)

    # create weight variable
    wgts = om.MDoubleArray(len(wgtsValues))
    for i in xrange(numVerts):
        for j in xrange(numInfs):
            # print ' i:', i, '  j:', j, '  id:', (i*numInfs)+j
            wgts.set(wgtsValues[(i * numInfs) + j], (i * numInfs) + j)

    # create components variable
    fnComp = om.MFnSingleIndexedComponent()
    oComps = fnComp.create(om.MFn.kMeshVertComponent)
    for i in xrange(len(wgtsValues)):
        fnComp.addElement(i)

    # get influence indices
    infIds = om.MIntArray()
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
    fnSkin.setWeights(dag, oComps, infIds, wgts)

    # reset bind
    # resetSkinCluster(skin)


def exportSkin(skinData, filePath, weightsAsList=False):
    """
    exports given skinData into filePath
    ie:     # export skinData for skinCluster1
            filePath = os.path.join('D:', 'temp.wgts')
            skinData = getSkinData('skinCluster1')
            exportSkin(skinData, filePath, weightsAsList=False)
    :param skinData: list with 5 elements in it:
                                 geo, skin, infs, numVerts, wgts
    :param filePath: path of skinData file
    :param weightsAsList: if set to True, weights will be written
                          as lists of weights for each vertex
                          with vert id as first element and
                          weights for the vert as next elements
                          else writes number of vertices in one
                          line and all weights in the next line
    :return: None
    """
    geo = skinData[0]
    skin = skinData[1]
    infs = skinData[2]
    numVerts = skinData[3]
    wgts = skinData[4]
    numInfs = len(infs)    

    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except :
            raise
            
    with open(filePath, 'w') as f:
        f.write(geo + '\n\n')
        f.write(skin + '\n\n')
        for inf in infs:
            f.write(inf + '\n')
        f.write('\n')

        # write weights as a list with vertex id as first element
        # and weights for that vertex as next elements
        if weightsAsList:
            for i in xrange(numVerts):
                wgtsLine = str(i) + ' '
                for j in xrange(numInfs):
                    wgtsLine += str(wgts[(i * numInfs) + j])
                    wgtsLine += ' '
                wgtsLine += '\n'
                f.write(wgtsLine)

        # or write the whole weights for all verts on the same line
        else:
            f.write(str(numVerts))
            f.write('\n\n')
            f.write(' '.join([str(x) for x in wgts]))


def importSkin(filePath, weightsAsList=False):
    """
    import skin data from file
    ie:     # import skinData for skinCluster1
            filePath = os.path.join('D:', 'temp.wgts')
            skinData = importSkin(filePath, False)
            setSkinData(skinData, skin='skinCluster1')
    :param filePath: path to skin data file
    :param weightsAsList: set to True if weights were written
                        as lists of weights for each vertex
                        with vert id as first element and
                        weights for the vert as next elements
    :return: skinData list which contains
             geo, skin, infs, numVerts, wgts
    :return type: list
    """
    with open(filePath, 'r') as f:
        lines = [x for x in f]
        groupby(lines, lambda x: x == "\n")
        lines = [list(group) for k,
                                 group in groupby(lines, lambda x: x == "\n")
                 if not k]
        # get geo
        geo = _lineToStr(lines[0])
        # get skin
        skin = _lineToStr(lines[1])
        # get influences
        infs = [x.rstrip('\n') for x in lines[2]]

        # get weights and number of vertices
        if weightsAsList:  # get weights as separate lists
            wgts = _lineToStr(lines[-1])
            numVerts = _lineToStr(lines[-2])
            try:  # if the line before last one is one number, wgts were saved as one line
                numVerts = int(numVerts)
                wgts = wgts.split(' ')
                wgts = _lineToLists(wgts, numVerts, len(infs))
                print 'Weights were saved as one line, converted to multiple lists!'
            except:
                wgts = [x[:-1] for x in lines[-1]]  # remove end \n from lines
                numVerts = len(wgts)
                # wgts = ''.join(wgts)[:-1]  # merge all lines into one string
                wgts = [x.split(' ')[:-1] for x in wgts]  # convert to list of strings
                wgts = [_firstToIntRestToFloat(x) for x in wgts]
                print 'Weights were saved as multiple lines, returning them as multiple lists!'

        # get weights as one list with all weights in it
        else:
            try:  # if the line before last one is integer, wgts were saved in one line
                numVerts = _lineToStr(lines[-2])
                numVerts = int(numVerts)
                wgts = [float(x) for x in lines[-1][0].split(' ')]
            except:  # weights were saved in multiple lines (as lists)
                try:
                    wgts = [x[2:-1] for x in lines[-1]]  # remove vertex id and end \n from lines
                    numVerts = len(wgts)
                    wgts = ''.join(wgts)[:-1]  # merge all lines into one string
                    wgts = [float(x) for x in wgts.split(' ')]  # convert to list of floats
                except:
                    mc.error('skinClsuter file seems to be corrupt: {}'.format(filePath))

        return geo, skin, infs, numVerts, wgts


def replaceInfluences_old(skinData=None, skin=None, srcJnts=None, tgtJnts=None):
    """
    moves weights of one joint (src) to another (tgt)
    ie:     # move weights from srcJnts to tgtJnts for skinCluster1
            skinData = getSkinData('skinCluster1')
            srcJnts = ['joint1', 'joint3', 'joint5', 'joint7']
            tgtJnts = ['joint2', 'joint4', 'joint6', 'joint8']
            replaceInfluences(skinData, None, srcJnts, tgtJnts)
    :param skin: skinCluster to work on
    :param srcJnts: source joints to move their weights to others
    :param tgtJnts: target joints to move weights to
    :return:
    """
    assert len(srcJnts) == len(tgtJnts)
    if not skinData:
        skinData = getSkinData(skin)

    infs = skinData[2]
    # numVerts = skinData[3]
    wgts = skinData[4]

    for i, (src, tgt) in enumerate(zip(srcJnts, tgtJnts)):
        # get index of influences
        srcIndex = infs.index(src)
        tgtIndex = infs.index(tgt)

        # get weights of influences
        srcWgts = _getWgtByInfId(wgts, srcIndex, len(infs))
        tgtWgts = _getWgtByInfId(wgts, tgtIndex, len(infs))

        # calculate result weights
        tgtWgts = [sum(x) for x in zip(tgtWgts, srcWgts)]
        srcWgts = [0] * len(srcWgts)

        # set weights
        wgts = _setWgtsByInfId(wgts, tgtIndex, tgtWgts)
        wgts = _setWgtsByInfId(wgts, srcIndex, srcWgts)

    skinData = (skinData[0], skinData[1], skinData[2], skinData[3], wgts)
    setSkinData(skinData)
    stdout.write('Weights successfully transferred')


def replaceInfluence(geo, srcJnts, tgtJnt, error=False):
    """
    # this will give 'a' and 'b' weights to 'c', even if 'c' is not skinned to 'pCube1'
    mc.replaceInfluence('pCube1', srcJnts=['a', 'b'], tgtJnt='c')

    # this will give 'a' and 'b' weights to 'c', but errors if 'c' is not skinned to 'pCube1'
    deformer.replaceInfluence('pCube1', srcJnts=['a', 'b'], tgtJnt='c', error=True)

    :param geo: name of geo to replace influence weights
    :type geo: string
    :param srcJnts: source joint(s)
    :type srcJnts: list
    :param tgtJnt: target joint
    :type tgtJnt: string
    :param error: error if target joint is not affecting the skinCluster
    :return: N/A
    """
    path = os.path.dirname(__file__)
    path = os.path.join(path, '../../plugin/ehm_plugins/scriptedPlugin/replaceInfluence.py')
    mc.loadPlugin(os.path.abspath(path), qt=True)
    mc.replaceInfluence(geo, s=srcJnts, t=tgtJnt, e=error)


def rigidifySkinCluster():
    sel = mc.ls(sl=True, fl=True)[0]
    mc.select(sel)
    mm.eval('artAttrSkinWeightCopy;')
    mc.select(sel.split('.')[0] + '.vtx[*]')
    mm.eval('artAttrSkinWeightPaste;')


def _getWgtByInfId(wgts, index, numInfs):
    """
    return weights of all vertices for one influence
    :param wgts: list of weights for all the verts for all the joints
    :param index: influence index
    :param numInfs: number of all the influence in skinCluster
    :return: list of weights of all verts for one joint
    """
    numVerts = len(wgts) / numInfs
    wgtLine = []
    for i in xrange(numVerts):
        tmpId = numInfs * i + index
        wgtLine.append(wgts[tmpId])
    return wgtLine


def _setWgtsByInfId(wgts, index, weights):
    """
    return weights of all vertices for one influence
    :param wgts: list of weights for all the verts for all the joints
    :param index: influence index
    :return: list of weights of all verts for one joint
    """
    numVerts = len(weights)
    numInfs = len(wgts) / numVerts
    for i in xrange(numVerts):
        tmpId = numInfs * i + index
        wgts.set(weights[i], tmpId)
    return wgts


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


def disableDeformers(geo):
    """ Deactivate deformers """
    inputs = []
    history = mc.listHistory(geo)
    for historyNode in history:
        historyTypes = mc.nodeType(historyNode, inherited=True)
        if 'geometryFilter' in historyTypes:
            inputs.append(historyNode)

    for i in inputs:
        mc.setAttr(i+'.envelope', 0)


def enableDeformers(geo):
    """ Deactivate deformers """
    inputs = []
    history = mc.listHistory(geo)
    for historyNode in history:
        historyTypes = mc.nodeType(historyNode, inherited=True)
        if 'geometryFilter' in historyTypes:
            inputs.append(historyNode)

    for i in inputs:
        mc.setAttr(i+'.envelope', 1)


def copySkinFromReference():
    sels = mc.ls(sl=True)
    source = sels[-1]
    targets = sels[:-1]
    infs = mc.skinCluster(source, q=True, inf=True)
    
    infs = [x.split(':')[-1] for x in infs]

    mc.select(mc.ls(infs), targets)
    mm.eval('newSkinCluster "-tsb -bm 0 -nw 1 -wd 0 -mi 5 -omi true -dr 4 -rui false";')

    for tgt in targets:
        mc.copySkinWeights(source,
                           tgt,
                           noMirror=True,
                           surfaceAssociation='closestPoint',
                           influenceAssociation=['label', 'name', 'closestJoint'])


def copySkin(src=None, targets=None, useSelection=False):
    """
    from rt_python.lib import deformer
    deformer.copySkin(useSelection=True)
    """
    if useSelection:
        sels = mc.ls(sl=True)
        src = sels[-1]
        targets = sels[:-1]

    if isinstance(targets, basestring):
        targets = [targets]
    
    infs = mc.skinCluster(src, q=True, inf=True)
    # delete current skinCluster if exists
    for tgt in targets:
        skn = getSkinCluster(tgt)
        if skn:
            mc.delete(skn)

    # print '..........', infs, src, targets
    for tgt in targets:
        sknNode = tgt + '_SKN'
        if strLib.hasSuffix(tgt):
            sknNode = strLib.mergeSuffix(tgt) + '_SKN'
        mc.skinCluster(infs, tgt, toSelectedBones=True, n=sknNode)

    # mc.select(infs, targets)
    # mm.eval('newSkinCluster "-tsb -bm 0 -nw 1 -wd 0 -mi 5 -omi true -dr 4 -rui false";')

    for tgt in targets:
        mc.copySkinWeights(src,
                           tgt,
                           noMirror=True,
                           surfaceAssociation='closestPoint',
                           influenceAssociation=['label', 'name', 'closestJoint'])


def mirrorSkin(sources=None, useSelection=False):
    """
    from rt_python.lib import deformer
    deformer.mirrorSkin(useSelection=True)
    """
    if useSelection:
        sources = mc.ls(sl=True)

    for src in sources:

        # find side
        side = src[0]
        otherSide = 'L'
        if side == 'L':
            otherSide = 'R'

        # find target
        tgt = src.replace(side, otherSide, 1)
        if not mc.objExists(tgt):
            continue

        # get src skinCluster
        srcSkin = getSkinCluster(src)
        if not srcSkin:
            continue

        # get influences
        infs = mc.skinCluster(src, q=True, inf=True)
        infs = [x.replace(side, otherSide, 1) for x in infs]

        # delete current skinCluster if exists
        tgtSkin = getSkinCluster(tgt)
        if tgtSkin:
            mc.delete(tgtSkin)

        # find name for skinCluster
        tgtSkin = tgt + '_SKN'
        if strLib.hasSuffix(tgt):
            tgtSkin = strLib.mergeSuffix(tgt) + '_SKN'

        # skin
        tgtSkin = mc.skinCluster(infs, tgt, toSelectedBones=True, n=tgtSkin)[0]

        # mirror weights
        mc.copySkinWeights(ss=srcSkin,
                           ds=tgtSkin,
                           mirrorMode='YZ',
                           surfaceAssociation='closestPoint',
                           influenceAssociation='closestJoint')

    mc.select(sources)


def importDeformer():
    """
        if (!objExists("pCubeShape1")) {
        print ("[WARNING] Cannot find node [pCubeShape1] for [pCube1_scls]. skipping!!!");
    } else {
        // delete existing skinCluster
        select -cl;
        string $listExisting[] = `listConnections -type "skinCluster" pCubeShape1 `;
        if (size($listExisting) > 0){
            delete $listExisting;
        }
        string $history[] = `listHistory "pCubeShape1"`;
        string $histExisting[] = `ls -type "skinCluster" $history`;
        int $histSize = `size $histExisting`;
        for ($i=0; $i < $histSize; $i++){
            string $geoms[] = `skinCluster -q -g $histExisting[$i]`;
            int $numGeos = `size $geoms`;
            for ($i=0; $i < $numGeos; $i++){
                if ($geoms[$i] == "pCubeShape1"){
                    print $geoms[$i];}
                }
        }
        // test num export joints vs num existing joints
        string $exportJnts[] = {"joint1"};
        string $missingJnts[];
        for($i = 0; $i < `size($exportJnts)`; $i ++){
            if(!`objExists $exportJnts[$i]`){
                $missingJnts[size($missingJnts)] = $exportJnts[$i];
            }
        }
        // warn if missing joints
        if(size($missingJnts) > 0){
            print "Cannot create skinCluster [pCube1_scls]\n";
            print "The following joints no longer exist\n";
            for($i = 0; $i < `size($missingJnts)`; $i ++){print ("\t"+$missingJnts[$i]+"\n");}
        }
        // if all joints exist - build skin cluster
        else{
            select -cl;     
            string $created[] = `skinCluster -tsb -sm 0 -nw 1 -mi 5 -n "pCube1_scls" joint1 pCubeShape1`;
            setAttr ($created[0]+".useComponents") 0;
            setAttr ($created[0]+".maintainMaxInfluences") 1;
            connectAttr -f importedDeformer:pCube1_scls_weights.weightList ($created[0]+".weightList");
            disconnectAttr importedDeformer:pCube1_scls_weights.weightList ($created[0]+".weightList");
            connectAttr -f importedDeformer:pCube1_scls_weights.blendWeights ($created[0]+".blendWeights");
            disconnectAttr importedDeformer:pCube1_scls_weights.blendWeights ($created[0]+".blendWeights");
            select -cl;
        }
    }
    delete importedDeformer:pCube1_scls_weights;
    delete importedDeformer:skinCluster_srcNode;
    namespace -rm :importedDeformer -dnc;

    """
    pass


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


def createSoftMod(geos, name='newSoftMod', position=[0, 0, 0]):
    """
    geo = 'C_head_GEO'

    """
    if '_' in name:
        side, name = name.split('_')
    else:
        side = 'C'
    
    # controls
    baseCtl = control.Control(side=side,
                              descriptor=name+'Center',
                              shape='cube',
                              scale=[1.2, 1.2, 1.2],
                              color='maroon',
                              translate=position)
    baseZro = baseCtl.zro
    baseCtl = baseCtl.name

    ctl = control.Control(side=side,
                          descriptor=name,
                          parent=baseCtl,
                          shape='sphere',
                          scale=[0.3, 0.3, 0.3],
                          matchTranslate=baseCtl).name

    # world position of control
    loc = mc.spaceLocator(n=baseCtl.replace('CTL', 'LOC'))[0]
    locShape = mc.listRelatives(loc, s=True)[0]
    mc.delete(mc.parentConstraint(baseCtl, loc))
    mc.parent(loc, baseCtl)
    mc.hide(loc)

    # soft mod
    mc.select(geos)
    sMod, sHnd = mc.softMod(rel=True)
    sMod = mc.rename(sMod, ctl.replace('CTL', 'SFM'))
    sHnd = mc.rename(sHnd, ctl.replace('CTL', 'SFH'))
    sHndShape = mc.listRelatives(s=True)[0]
    mc.parent(sHnd, baseZro)
    mc.hide(sHnd)
    sZro = trsLib.insert(sHnd, name=strLib.mergeSuffix(sHnd) + 'Zro')[0]
    mc.setAttr(sZro+'.inheritsTransform', 0)
    mc.pointConstraint(baseCtl, sZro)

    # connect
    for axis in ['X', 'Y', 'Z']:
        mc.setAttr(sHnd+'.rotatePivot'+axis, 0)
        mc.connectAttr(locShape+'.worldPosition[0].worldPosition'+axis,
                       sMod+'.falloffCenter'+axis)
        mc.connectAttr(locShape+'.worldPosition[0].worldPosition'+axis,
                       sHndShape+'.origin'+axis)

    mc.pointConstraint(ctl, sHnd)

    a = attrLib.addFloat(ctl, ln='falloff', min=0, dv=1)
    mc.connectAttr(a, sMod+'.falloffRadius')

    a = attrLib.addEnum(ctl, ln='falloffMode', en=['volume', 'surface'])
    mc.connectAttr(a, sMod+'.falloffMode')

    return baseCtl, ctl, sMod, sHnd


def localCluster(ctl, geo):
    """
    localCluster(clt='pCube1', geo='C_scale4_GEO_BS_flare')
    """
    cls = mc.deformer(geo, type='cluster', after=True)[0]
    mc.connectAttr(ctl+'.worldMatrix', cls+'.matrix')
    mc.connectAttr(ctl+'.parentInverseMatrix', cls+'.bindPreMatrix')
    return cls


def steal(srcGeo, tgtGeo):
    srcGeoShapes = trsLib.getShapes(srcGeo)

    # steal inMesh connections
    tgtGeoS = trsLib.getShapes(tgtGeo)[0]
    inputs = mc.listConnections(srcGeoShapes[0]+'.inMesh', plugs=True)
    if inputs:
        attrLib.connectAttr(inputs[0], tgtGeoS+'.inMesh')
        attrLib.disconnectAttr(srcGeoShapes[0]+'.inMesh')

    # # steal orig shape inMesh connections
    # if srcGeoShapes[1:]:
    #     tgtOrig = mc.duplicate(srcGeoShapes[1], name=tgtGeo+'ShapeOrig')[0]
    #
    #     mc.select(tgtOrig, tgtGeo)
    #     trsLib.parentShapes()
    #
    #     tgtGeoS = trsLib.getShapes(tgtGeo)[0]
    #     inputs = mc.listConnections(srcGeoShapes[1]+'.inMesh', plugs=True)
    #     if inputs:
    #         attrLib.connectAttr(inputs[0], tgtGeoS+'.inMesh')
    #         attrLib.disconnectAttr(srcGeoShapes[1]+'.inMesh')
    #         # trsLib.removeOrigShapes(srcGeo)


def convertConstraintToCluster(node):
    cnss = mc.listRelatives(node, type='constraint') or []
    if not cnss:
        return
    for cns in cnss:
        typ = mc.nodeType(cnss)
        cns_cmd = getattr(mc, typ)
        targetList = cns_cmd(cns, q=True, targetList=True)
        if not targetList:
            return
        cls = mc.cluster(node)
        mc.parent(cls, targetList[0])
    mc.delete(cnss)


def wrap(driver, driven):
    mc.select(driven, driver)
    mm.eval('doWrapArgList "7" { "1","0","1", "2", "0", "1", "0", "0" }')


def localSkin(skins, world):
    jointsDict = {}

    if not skins:
        skins = mc.ls(type='skinCluster')

    for scls in skins:
        conns = mc.listConnections('{}.matrix'.format(scls), s=1, c=1, d=0)
        for i in range(len(conns) / 2):
            destPlug = conns[i * 2]
            src = conns[i * 2 + 1]
            if not mc.nodeType(src) == 'joint':
                mc.warning('This is not a joint :{}'.format(src))
                continue

            if src not in jointsDict:
                jointsDict[src] = '{}_mmt'.format(src)
                if not mc.objExists(jointsDict[src]):
                    jointsDict[src] = mc.createNode('multMatrix', n='{}_mmt'.format(src))
                    mc.connectAttr('{}.worldMatrix[0]'.format(src), '{}.matrixIn[0]'.format(jointsDict[src]))
                    mc.connectAttr('{}.worldInverseMatrix[0]'.format(world), '{}.matrixIn[1]'.format(jointsDict[src]))
            mc.connectAttr('{}.matrixSum'.format(jointsDict[src]), destPlug, f=1)


def exportFFD(ffd, path):
    """
    import python.lib.deformer as deformer
    reload(deformer)
    for ffd in 'ffd1Lattice', 'ffd3Lattice':
        ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
        deformer.exportFFD(ffd=ffd, path=ffd_json)
    """
    # get transform values
    data = {'trs': trsLib.getTRS(ffd, space='world')}

    # get cv positions
    cv_positions = []
    cvs = mc.ls(ffd+'.controlPoints[*]', fl=True)
    for cv in cvs:
        x = mc.getAttr(cv + '.xValue')
        y = mc.getAttr(cv + '.yValue')
        z = mc.getAttr(cv + '.zValue')
        cv_positions.append((x, y, z))
    data['cv_positions'] = cv_positions

    # get geometries
    ffd_s = trsLib.getShapes(ffd)[0]
    ffd_node = (mc.listConnections(ffd_s + '.latticeOutput') or [None])[0]
    if ffd_node:
        data['geos'] = mc.listConnections(ffd_node + '.outputGeometry') or []

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

    # write it to disk as json
    fileLib.saveJson(path=path, data=data)


def importFFD(path):
    """
    import python.lib.deformer as deformer
    reload(deformer)
    for ffd in 'ffd1Lattice', 'ffd3Lattice':
        ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
        deformer.importFFD(path=ffd_json)
    """

    # read data from json
    data = fileLib.loadJson(path=path)
    if not data:
        mc.error('Not a valid lattice config! "{}"'.format(path))

    # create ffd
    name = os.path.splitext(os.path.basename(path))[0]
    mc.select(data['geos'])
    ffd_node, ffd, ffdBase = mc.lattice(divisions=data['divisions'])
    ffd_node = mc.rename(ffd_node, name + '_FFN')
    ffd = mc.rename(ffd, name)
    ffdBase = mc.rename(ffdBase, name + '_FFB')

    # set transform values
    trsLib.setTRS(ffd, data['trs'], space='world')
    trsLib.setTRS(ffdBase, data['base_trs'], space='world')

    # set cv positions
    for i, pos in enumerate(data['cv_positions']):
        mc.setAttr('{}.controlPoints[{}].xValue'.format(ffd, i), pos[0])
        mc.setAttr('{}.controlPoints[{}].yValue'.format(ffd, i), pos[1])
        mc.setAttr('{}.controlPoints[{}].zValue'.format(ffd, i), pos[2])

    # set ffd settings
    mc.setAttr(ffd_node + '.local', data['local'])
    mc.setAttr(ffd_node + '.outsideLattice', data['outsideLattice'])

    return ffd_node, ffd, ffdBase


def mirrorFFD(ffd, copy=True, findAndDeformGeos=True, search='L_', replace='R_'):
    """
    import python.lib.deformer as deformer
    reload(deformer)
    deformer.mirrorFFD(ffd='ffd1Lattice')
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
        geos = [x for x in geos if meshLib.isMesh(x)]

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
        ffd_node = mc.rename(ffd_node, name + '_FFN')
        ffd = mc.rename(ffd, name)
        ffdBase = mc.rename(ffdBase, name + '_FFB')

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
    ffd_s, ffd_node, ffdBase = deformer.getFFDNodes(ffd)
    """
    ffd_s = trsLib.getShapes(ffd)[0]
    ffd_node = (mc.listConnections(ffd_s + '.latticeOutput') or [None])[0]
    ffdBase = (mc.listConnections(ffd_node + '.baseLattice.baseLatticeMatrix') or [None])[0]
    return ffd_s, ffd_node, ffdBase


def findClosestPolygons(geoToFindPolygons, proxyGeo):
    """
    import python.lib.deformer as deformer
    reload(deformer)
    deformer.findClosestPolygons(geoToFindPolygons, proxyGeo)
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
    import python.lib.deformer as deformer
    reload(deformer)
    deformer.getCurveCVs('curve1')
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
    import python.lib.deformer as deformer
    reload(deformer)
    deformer.getPoints('pCube1')
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
        index = int(attrName.split('[')[1].split(']')[0]) # eg: 18
        return index
    except:
        mc.warning('target "{0}" does not exists on "{1}"'.format(target, bls))
        return


def setBlsWgtsFromCrv(bls, geo, crv, target=None, geoIdx=0, curveType='mid'):
    """
    import python.lib.deformer as deformer
    reload(deformer)
    bls = 'blendShape1'
    geos = mc.listRelatives('C_mouth_GRP', f=True)
    crv = 'curve1'
    curveType = 'mid'
    target = 'C_mouth_GRP1'
    for i, geo in enumerate(geos):
        deformer.setBlsWgtsFromCrv(bls=bls, geo=geo, crv=crv, target=target, geoIdx=i, curveType=curveType)

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
        animCrv = key.create5CurvePrincipleAnimCurve(curveType=curveType)
    else:
        animCrv = key.create3CurvePrincipleAnimCurve(curveType=curveType)

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
    mc.connectAttr('{}.outputGeometry[{}]'.format(bls, geoIdx), mesh+'.inMesh')
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

    import python.lib.deformer as deformer
    reload(deformer)
    bls = 'blendShape1'
    bls_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', bls+'.json')
    deformer.exportBlsWgts(bls=bls, path=bls_json)
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

    deformer.importBlsWgts(path=bls_json, newBls=None)
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
    deformer.createShrinkWrap(driver='L_Sclera_00__MSH',
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


def exportDeformerWgts(node, path):
    """
    exports baseWeights for all geos in the blendShape node

    import python.lib.deformer as deformer
    reload(deformer)
    node = 'shrinkWrap1'
    wgts_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', node+'.json')
    deformer.exportDeformerWgts(node=node, path=wgts_json)
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

    deformer.importDeformerWgts(path=wgts_json, newNode=None)

    """
    data = fileLib.loadJson(path=path)
    if not data:
        mc.error('given deformer weight json file is no valid: {}'.format(path))

    for inputTarget, wgts in data.items():
        if newNode:
            inputTarget = newNode + '.' + inputTarget.split('.', 1)[-1]
        for i in range(len(wgts)):
            mc.setAttr('{}[{}]'.format(inputTarget, i), wgts[i])


def softSelection():
    """
    elements,weights = softSelection() 
    """
    #Grab the soft selection
    selection = om.MSelectionList()
    softSelection = om.MRichSelection()
    om.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
   
    dagPath = om.MDagPath()
    component = om.MObject()
   
    # Filter Defeats the purpose of the else statement
    iter = om.MItSelectionList( selection, om.MFn.kMeshVertComponent )
    elements, weights = [], []
    while not iter.isDone():
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = om.MFnSingleIndexedComponent(component)   
        getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0
       
        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i)) 
        iter.next()
       
    return elements, weights
