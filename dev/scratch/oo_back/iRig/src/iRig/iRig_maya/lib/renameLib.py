"""
name: renameLib.py

Author: Ehsan Hassani Moghaddam

"""

# python modules
import re

# maya modules
import maya.cmds as mc
import maya.mel as mm


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
        newName = removeEndNumbers(name=obj)
        newName = newName.split('|')[-1]
        renamedObjects.append(mc.rename(obj, newName))
    return renamedObjects


def removeEndNumbers(name=""):
    return re.split('(\d+)$', name)[0]


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
        shps = getShapes(obj, fullPath=True)
        name = obj.split('|')[-1]
        for shp in shps:
            mc.rename(shp, name+'Shape')


def removePasted():
    mm.eval('searchReplaceNames "pasted__" " " "all";')


def getShapes(node="", fullPath=False):
    """
    :return: returns all shape of the given node, plus itself if it's a shape too
    :return type: list of strings
    """
    if not mc.objExists(node):  # doesn't exist
        mc.error('"{}" does not exist.'.format(node))

    shape_list = mc.listRelatives(node, children=True, shapes=True, fullPath=True) or []

    # make sure node itself is in the list if it's a shape too
    if isShape(node):
        shape_list.append(node)

    if shape_list and (not fullPath):
        shape_list = [x.split('|')[-1] for x in shape_list]

    return shape_list


def isShape(node=""):
    """
    :return: True if given node is a shape else False
    :return type: bool
    """
    return 'shape' in mc.nodeType(node, inherited=True)
