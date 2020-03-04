"""
name: common.py

Author: Ehsan Hassani Moghaddam

History:

04/21/16 (ehassani)     first release!

"""

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.api.OpenMaya as om2

from . import strLib
from . import trsLib

reload(strLib)
reload(trsLib)


def getDagPath(node):
    """
    return dag path of given object or list of objects
    """
    # if isinstance(node, list):
    #     oNodeList = []
    #     for o in node:
    #         selectionList = om.MSelectionList()
    #         selectionList.add(o)
    #         oNode = om.MDagPath()
    #         selectionList.getDagPath(0, oNode)
    #         oNodeList.append(oNode)
    #     return oNodeList
    # else:
    selectionList = om.MSelectionList()
    selectionList.add(node)
    oNode = om.MDagPath()
    selectionList.getDagPath(0, oNode)
    return oNode


def getDagPath2(node):
    """
    return dag path of given object or list of objects
    """
    selectionList = om2.MSelectionList()
    selectionList.add(node)
    oNode = selectionList.getDagPath(0)
    return oNode


def renameReplace(objs=None, search='', replace='', num=1):
    objs = mc.ls(objs)
    if not objs:
        objs = mc.ls(sl=True)

    # sort objs from child to parent
    objs.sort(key=lambda x: x.count('|'))
    objs.reverse()

    renamedObjects = []
    for obj in objs:
        newName = obj.split('|')[-1].replace(search, replace, num)
        renamedObjects.append(mc.rename(obj, newName))
    return renamedObjects


def renameAdd(objs=None, prefix='', suffix=''):
    objs = mc.ls(objs)
    if not objs:
        objs = mc.ls(sl=True)

    # sort objs from child to parent
    objs.sort(key=lambda x: x.count('|'))
    objs.reverse()

    renamedObjects = []
    for obj in objs:
        newName = prefix + obj.split('|')[-1] + suffix
        renamedObjects.append(mc.rename(obj, newName))
    return renamedObjects


def rename(objs=None, name=None, pad=None, startNum=1, prefix='', suffix='', hierarchyMode=False):
    """
    a series of codes used for renaming nodes
    :param pad: number of digits. If None, doesn't add numbers at all.
                eg: (pad=None -> C_tail_JNT) or (pad=4 -> C_tail_0001_JNT)
    :usage:
        import python.lib.common as common
        reload(common)
        common.rename(objs=mc.ls(sl=1), name='tail', pad=4, prefix="C",
                      suffix="JNT", hierarchyMode=False)
    """
    objs = mc.ls(objs)
    if not objs:
        objs = mc.ls(sl=True)
    if not objs:
        mc.error('ehm_tools...Rename: No object to rename!')
    if hierarchyMode:
        mc.select(objs[0], hierarchy=True)
        objs = mc.ls(sl=True, long=True)

    # sort objs from child to parent
    objs.sort(key=lambda x: x.count('|'))
    objs.reverse()

    #
    renamedObjects = []
    for i, obj in enumerate(objs):
        newName = ""
        if prefix:
            newName = prefix + "_"
        if name is not None:
            newName += name
        else:
            newName += objs[i]
        if pad is not None:
            zeros = str(len(objs) - i - 1 + startNum).zfill(pad)
            newName += zeros
        if suffix:
            newName += ("_" + suffix)

        # safe = 10000
        # i = 0
        # while mc.objExists(newName):
        #     newName = strLib.incrementEndNumber(newName)
        #     i += 1
        #     if i > safe:
        #         break
        print(objs[i], newName)
        renamedObjects.append(mc.rename(objs[i], newName))
    return renamedObjects


def numRename(nodes=None, name='test_#_GEO'):
    if not nodes:
        nodes = mc.ls(sl=True)
    name = name.replace('#', '{:04}')
    for i in range(len(nodes)):
        mc.rename(nodes[i], name.format(i + 1))


def removeEndNumber(objs=None):
    objs = mc.ls(objs)
    if not objs:
        objs = mc.ls(sl=True)

    # sort objs from child to parent
    objs.sort(key=lambda x: x.count('|'))
    objs.reverse()

    renamedObjects = []
    for obj in objs:
        newName = strLib.removeEndNumbers(name=obj)
        newName = newName.split('|')[-1]
        renamedObjects.append(mc.rename(obj, newName))
    return renamedObjects


def fixShapeNames(objs=None):
    objs = mc.ls(objs)
    if not objs:
        objs = mc.ls(sl=True)
    if not objs:
        mc.warning('No object was selected, skipped!')
        return
    # sort objs from child to parent
    objs.sort(key=lambda x: x.count('|'))
    objs.reverse()

    for obj in objs:
        shps = trsLib.getShapes(obj, fullPath=True)
        name = obj.split('|')[-1]
        for shp in shps:
            mc.rename(shp, name+'Shape')


def removePasted():
    mm.eval('searchReplaceNames "pasted__" " " "all";')
