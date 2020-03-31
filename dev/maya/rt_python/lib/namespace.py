"""
name: namespace.py

Author: Ehsan Hassani Moghaddam

History:

04/21/16 (ehassani)     first release!

"""

import maya.cmds as mc


def removeAll():
    """
    remove one level of namespace
    run a couple of times to get rid of every namespace
    """
    ignoreList = ('sharedReferenceNode',)
    mc.namespace(set=':')
    nss = mc.namespaceInfo(listOnlyNamespaces=True) or []
    nss = [x for x in nss if x not in ['UI', 'shared']]

    for ref in mc.ls(type='reference'):
        if ref in ignoreList:
            continue
        ns = None
        try:
            ns = mc.referenceQuery(ref, namespace=True)
        except Exception as e:
            print(e)
            mc.lockNode(ref, lock=False)
            mc.delete(ref)
        if ns:
            print ns
            nss.remove(ns[1:])

    if nss:
        for ns in nss:
            mc.namespace(moveNamespace=(ns, ":"), force=True)
            mc.namespace(removeNamespace=ns)
        removeAll()


def replaceWithUnderscore(objs=None):
    """
    replace ":" for the selected objects names with "__"
    """
    if not objs:
        objs = mc.ls(sl=True)
    objs = mc.ls(objs)  # create a list from nested list of objects

    mc.namespace(setNamespace=":")
    for obj in objs:
        mc.rename(obj, obj.replace(':', '__'))
