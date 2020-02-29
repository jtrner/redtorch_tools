import maya.cmds as mc

from . import strLib as libStr

from . import attrLib as libAttr


def create(name, parent=None, force=False):
    """
    create asset node and set it as current
    :param name: name of new container
    :param force: if True, will create a container without checking if it already exists
    :return: name of created asset node
    """
    if parent:
        setCurrent(parent)

    if not mc.objExists(name):  # asset doesn't exist, create it
        asset = mc.container(name=name, includeHierarchyBelow=True)
        # createChildrenAttr(asset)
        return asset
    else:  # asset exists
        if force:  # asset exists but force flag in True, we must create an asset anyway!
            newName = libStr.getUniqueName(name)
            mc.warning('node "{0}" already exists, created another one called "{1}"!'.format(name, newName))
            asset =  mc.container(name=newName, includeHierarchyBelow=True)
            # createChildrenAttr(asset)
            setCurrent(asset)
            return asset
        if mc.nodeType(name) != 'container':  # objects exists but is not a container, error!
            mc.error('node "{0}" already exists, but is not a container!'.format(name))


def setCurrent(asset=None):
    if not asset: # == 'noAsset':
        currentAsset =  mc.container(query=True, current=True)
        if currentAsset:
            mc.container(currentAsset, edit=True, current=False)
    elif mc.objExists(asset) and mc.nodeType(asset) == 'container':
        mc.container(asset, edit=True, current=True)
    else:
        mc.error('"{0}" is not an asset node!'.format(asset))


def createChildrenAttr(asset):
    libAttr.addString(asset, 'templatesList')


def addChildren(asset, child):
    """
    adds another container node as the child to asset container
    """
    currentChildren = mc.getAttr(asset+'.templatesList')
    currentChildren = eval(currentChildren)
    currentChildren.append(child)
    libAttr.setAttr(asset+'.templatesList', str(currentChildren))


def addNode(asset, node):
    mc.container(asset, edit=True, addNode=[node])


def removeAll():
    """ empty and remove containers """

    # code below has a bug, it error if container is empty
    # [mc.container(x, e=True, removeContainer=True) for x in rtms]

    rtms = mc.ls(type='container')
    for x in rtms:
        nodes = mc.container(x, q=True, nodeList=True)
        if nodes:
            mc.container(x, e=True, removeNode=nodes)
        mc.delete(x)
