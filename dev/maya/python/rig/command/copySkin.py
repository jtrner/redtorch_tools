import maya.cmds as mc

# copy skin from referenced to last selected
def copySkinFromReference():
    """
    copySkinFromReference()
    """
    sels = mc.ls(sl=True)
    source = sels[0]
    target = sels[1]
    infs = mc.skinCluster(source, q=True, inf=True)
    
    infs = mc.ls([x.split(':')[-1] for x in infs])
    mc.skinCluster(infs, target, tsb=True)
    # mc.select(infs, target)
    # mm.eval('newSkinCluster "-tsb -bm 0 -nw 1 -wd 0 -mi 5 -omi true -dr 4 -rui false";')
    
    mc.copySkinWeights(source,
                       target,
                       noMirror=True,
                       surfaceAssociation='closestPoint',
                       influenceAssociation=['label', 'name', 'closestJoint'])


# copy skin from last selected to all other selected geos
def copySkin(src, dest):
    srcSkn = getDeformer(src, "skinCluster")
    destSkn = getDeformer(dest, "skinCluster")
    if srcSkn and destSkn:
        copySkinWeights(src, dest)
    elif srcSkn:
        inf = mc.skinCluster(srcSkn, q=True, wi=True)
        skn = mc.skinCluster(inf, dest, tsb=True)
        mc.rename(skn[0], dest+"_scls")
        copySkinWeights(src, dest)
    else:
        mc.error('{0} must be skinned'.format(src))

def copySkinWeights(src, dest):
    mc.copySkinWeights(src,
                   dest,
                   noMirror=True,
                   surfaceAssociation='closestPoint',
                   influenceAssociation=['label', 'name', 'closestJoint'])

def getDeformer(node="", type_=""):    
    history = mc.listHistory(node)
    for historyNode in history:
        historyTypes = mc.nodeType(historyNode, inherited=True)
        if ('geometryFilter' in historyTypes) and (type_ in historyTypes):
            return historyNode

if __name__ == '__main__':
    sel = mc.ls(sl=True)
    src = sel[-1]
    dests = sel[:-1]
    for dest in dests:
        copySkin(src, dest)
    mc.select(sel)
