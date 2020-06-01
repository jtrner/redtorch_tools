"""
name: optimize.py

Author: Ehsan Hassani Moghaddam

History:

04/26/18 (ehassani)     first release!

"""
import maya.cmds as mc
import maya.mel as mm

from . import attrLib
from . import strLib
from . import connect


def removeSpaceSwitches(ignoreList=None):
    """
    deletes all space switches in the scene except the ones starting with values in ignoreList
    :usage:
        optimize.removeSpaceSwitches(ignoreList=['C_eyes'])

    :param ignoreList:
    :return:
    """
    if not ignoreList:
        ignoreList = []

    # delete space swithces
    spaceCnsList = mc.ls('*Space_PAR')
    spaceCnsList = [x for x in spaceCnsList if not any([x.startswith(y) for y in ignoreList])]
    for spaceCns in spaceCnsList:
        # find drivers and driven
        drvn = mc.listConnections(spaceCns+'.constraintParentInverseMatrix')[0]
        drvrs = mc.parentConstraint(spaceCns, q=1, tl=1)
        # find dominant driver
        weights = [mc.parentConstraint(d, spaceCns, q=1, w=1) for d in drvrs]
        bestDrvr = drvrs[weights.index(max(weights))]
        # get parent of dominant driver as drivers are usually just empty groups (hooks)
        par = mc.listRelatives(bestDrvr, p=1)
        if par:
            bestDrvr = par[0]
        # delete constraint
        mc.delete(spaceCns, drvrs)
        # parent drvn to bestdrvr or the parent of bestDrvr
        attrLib.lockHideAttrs(drvn, attrs=['t', 'r', 's'], lock=False, hide=False)
        mc.parent(drvn, bestDrvr)

    # delete space attrLibs
    spaceAttrs = mc.ls('*CTL.spaceParent')
    spaceAttrs = [x for x in spaceAttrs if not any([x.startswith(y) for y in ignoreList])]
    for spaceAttr in spaceAttrs:
        mc.deleteAttr(spaceAttr)


def removeUnknownPlugins():
    plugins = mc.unknownPlugin(q=True, list=True)
    if not plugins:
        return
    for p in plugins:
        try:
            mc.unknownPlugin(p, r=True)
        except:
            pass
    print 'Plugins removed:', plugins


def cleanUpScene():
    mm.eval('performCleanUpSceneForEverything')


def removeExtraConstraints():
    """
    parent module groups to other module groups instead of using constraints
    :return:
    """
    # use parent instead of matrix constraints for module groups
    for moduleGrp in mc.ls('*Module_GRP'):
        hooks = mc.ls('*'+strLib.mergeSuffix(moduleGrp)+'_HOK')
        if hooks:
            par = mc.listRelatives(hooks[0], p=True)[0]
            mc.parent(moduleGrp, par)
            matrixNodes = mc.ls(hooks[0].replace('HOK', '?MX'))
            mc.delete(hooks, matrixNodes)

        attrLib.addSeparator('C_main_CTL', 'extra')

        # re-create module groups connections
        mc.connectAttr('C_main_CTL.rigVis', moduleGrp+'.v')
        connect.reverse('C_main_CTL.rigSelectable', moduleGrp+'.overrideEnabled')
        mc.setAttr(moduleGrp+'.overrideDisplayType', 2)


def deleteExtraGroups():
    mc.delete('starter_GRP', 'module_GRP', 'setting_GRP')


def deleteUnusedTransforms():
    trsNodes = mc.ls(type='transform', l=True)
    trsNodes.sort(key=lambda x: len(x), reverse=True)
    deleted = []
    for trs in trsNodes:
        if mc.listRelatives(trs):
            continue
        if mc.listConnections(trs, s=1, d=1):
            continue
        mc.delete(trs)
        deleted.append(trs)
    print 'Deleted unused transform nodes bellow:'
    print '.................................................................'
    for n in deleted:
        print n
    print '.................................................................'


def deformers():
    for typ in ['tweak', 'bindPose', 'dagPose']:
        nodes = mc.ls(type=typ)
        if nodes:
            mc.delete(nodes)

    for skin in mc.ls(type='skinCluster'):
        mc.setAttr(skin+'.deformUserNormal', 0)


def meshes():
    for mesh in mc.ls(type='mesh'):
        mc.setAttr(mesh+'.displayColor', 0)
        mc.setAttr(mesh+'.displayBorder', 0)
        mc.setAttr(mesh+'.allowtopologyMod', 0)
        mc.setAttr(mesh+'.quadSplit', 0)
        mc.setAttr(mesh+'.reuseTriangles', 1)
        mc.setAttr(mesh+'.featureDisplacement', 0)
        mc.setAttr(mesh+'.doubleSided', 0)
        mc.setAttr(mesh+'.selectionChildHighlighting', 0)


# def removeResultJnts():
#     """
#     ik and fk blend to result joints. result jnts then connect to final skeleton.
#     To optimize the rig, we can connect ik and fk directly to final skeleton.
#     :return: N/A
#     """
#     rslJnts = mc.ls('*Rsl_JNT', type='joint')
#     for rslJnt in rslJnts:
#         jntOnSkel = rslJnt.replace('Rsl_JNT', 'JNT')
#
#         # delete constraint to final joint
#         cns = mc.parentConstraint(jntOnSkel, q=True)
#         if not cns:
#             continue
#         mc.delete(cns)
#
#         #
#
#     # deformLib.replaceInfluence('pCube1', srcJnts=['joint2'], tgtJnt='joint1', error=False)

def deleteMocapSkeleton():
    # TODO: transfer skinWeights from skeleton joints to result joints
    mc.delete('skeleton_GRP')
