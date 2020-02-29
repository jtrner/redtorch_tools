import maya.cmds as mc
import os
import tempfile

def history_on_off(state=0):
    """
    historically interesting
    history_on_off(state=1)
    """
    all_nodes = mc.ls(l=True)
    for node in all_nodes:
        mc.setAttr(node + '.isHistoricallyInteresting', state)


def getJointHierarchy(select=False):
    """
    select joint hierarchy
    getJointHierarchy(select=True)
    """
    sel = mc.ls(sl=1)
    if not sel:
        return
    sel = sel[0]
    jointsChildren = mc.listRelatives(sel, ad=1, type='joint')
    if jointsChildren and mc.nodeType(sel)=='joint':
        jointsChildren.append(sel)
    if jointsChildren:
        jointsChildren.reverse()
    if select:
        mc.select(jointsChildren)
    return jointsChildren


def exportClipboard():
    """
    exportClipboard()
    """
    nodes = mc.ls(sl=True)
    if not nodes:
        mc.warning('select objects to export to a temp directory')
        return
    outputDir = os.path.join(tempfile.tempdir, 'maya_temp_clipboard.ma')
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    mc.file(outputDir,
            force=True,
            options="v=0;",
            typ="mayaAscii",
            es=True)
    print 'Success: objects exported!'


def importClipboard():
    """
    importClipboard()
    """
    inputDir = os.path.join(tempfile.tempdir, 'maya_temp_clipboard.ma')
    content = mc.file(inputDir,
                      i=True,
                      type="mayaAscii",
                      options='v=0;',
                      ignoreVersion=True,
                      ra=True,
                      rpr="pasted_",
                      returnNewNodes=True,
                      mergeNamespacesOnClash=False)
    mc.select(content)
    print 'Success: objects imported!'


def addGrp(nodes=mc.ls(sl=True), parent=True, suffix=None):
    """
    add offset group
    addGrp(nodes=mc.ls(sl=True), parent=True, suffix='grp')
    """
    for n in nodes:
        grp = mc.createNode('transform')
        if suffix:
            grp = mc.rename(grp, n+'_'+suffix)
        mc.delete(mc.parentConstraint(n, grp))
        if parent:
            currentPar = mc.listRelatives(n, p=True)
            if currentPar:
                mc.parent(grp ,currentPar[0])
            mc.parent(n ,grp)


def removeOrigShapes(node):
    """
    kill orig nodes
    remove all (orig) shapes under given node except the main shape

    [removeOrigShapes(x) for x in mc.ls(sl=True, long=True)]

    :param node: string
        Name of the top node in the hierarchy that you wish to clean
    """
    toDeleteShape =[shape for shape in mc.listRelatives(node, ad=True, shapes=True, fullPath=True) \
                    if mc.getAttr('%s.intermediateObject' % shape)]
    if toDeleteShape:
        mc.delete(toDeleteShape)
