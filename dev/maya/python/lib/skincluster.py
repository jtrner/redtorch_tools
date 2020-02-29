"""
name: skincluster.py

Author: Ehsan Hassani Moghaddam

Usage:

# export selected or all skinClusters in scene
wgtFiles = "C:/Users/Ehsan/Desktop/"
geos = mc.listRelatives('geometry_GRP', ad=True, type='mesh', ni=True)
geos = [mc.listRelatives(x, p=True)[0] for x in geos]
geos = list(set(geos))
selected = mc.ls(sl=True)
if selected:
    geos = selected
skincluster.exportData(geos=geos, dataPath=wgtFiles)

History:
04/24/16 (ehassani)     first release!

"""
import os

import maya.cmds as mc

from . import strLib
from . import deformer

reload(strLib)
reload(deformer)

suffix = 'SKN'


def importData(dataPath, ignoreNames=True):
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
        skinData = deformer.importSkin(wgtFile)

        # geo node
        node = skinData[0]
        if len(mc.ls(node)) > 1:
            mc.warning('registry.importSkin -> There are more than one "{}" in the scene, skipped!'.format(node))
            continue
        if not mc.objExists(node):
            mc.warning('registry.importSkin -> Could not find "{0}", skipped!'.format(node))
            continue

        # make sure skinCluster node exists and has the right name
        if ignoreNames:
            newName = node.rpartition('Shape')[0] + '_' + suffix
        else:
            newName = strLib.mergeSuffix(node) + '_' + suffix
        sknNode = deformer.getSkinCluster(node)
        if sknNode:
            mc.rename(sknNode, newName)
        else:
            for j in skinData[2]:
                if not mc.objExists(j):
                    mc.warning('registry.importSkin() -> joint "{0}" does not exist!'.format(j))
            infs = mc.ls(skinData[2])
            mc.skinCluster(infs, node, tsb=1, rui=0, n=newName)

        # assign weights
        deformer.setSkinData(skinData)


def exportData(geos, dataPath, ignoreNames=True):
    """
    export skincluster weights for given rig component asset nodes
    """
    notSkinnedGeos = []
    for node in geos:
        print 'Exporting skinculster for "{0}"'.format(node)
        sknNode = deformer.getSkinCluster(node)
        if not sknNode:
            notSkinnedGeos.append(node)
            continue
        if ignoreNames:
            newName = node.split('Shape')[0] + '_' + suffix
        else:
            newName = strLib.mergeSuffix(node) + '_' + suffix
        sknNode = mc.rename(sknNode, newName)
        skinData = deformer.getSkinData(sknNode)

        wgtFiles = os.path.join(dataPath, node + '.wgt')

        deformer.exportSkin(skinData, wgtFiles)

    if notSkinnedGeos:
        print 'No skincluster node found on nodes bellow, export skipped!'
        print '.................................................................'
        for x in notSkinnedGeos:
            print x
        print '.................................................................'


def createSkinCluster(geos):
    """
    :return: sets self.skins to a list of newly created skincluster nodes
    """
    skins = []
    for geometry in geos:
        skinName = strLib.camelCase(geometry)
        skinName = skinName.replace("shape", "")
        skinName += suffix
        skin = mc.skinCluster('C_root_JNT', geometry, name=skinName)
        skins.append(skin)
    return skins


def exportSkinToDesktop():
    """
    export selected or all skinClusters in scene
    """
    path = mc.internalVar(uad=True)
    wgtFiles = os.path.join(path, '..', '..', 'Desktop')
    selected = mc.ls(sl=True)
    if selected:
        geos = selected
    else:
        geos = mc.listRelatives('geometry_GRP', ad=True, type='mesh', ni=True)
        geos = [mc.listRelatives(x, p=True)[0] for x in geos]
        geos = list(set(geos))
    exportData(geos=geos, dataPath=wgtFiles)


def importSkinFromDesktop():
    """
    import skinClusters from desktop
    """
    path = mc.internalVar(uad=True)
    wgtFiles = os.path.join(path, '..', '..', 'Desktop')
    importData(dataPath=wgtFiles)
