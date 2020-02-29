import os

import maya.cmds as mc
import maya.mel as mm
import xgenm

from ..lib import crvLib


def isclose(a, b, rel_tol=0.0001, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def setGuideWidth():
    guides = mc.ls(type='xgmSplineGuide')
    if not guides:
        return

    width = mc.getAttr(guides[0] + '.width')
    if isclose(width, 0.01):
        width = 0.1
    elif isclose(width, 0.1):
        width = 1.0
    else:
        width = 0.01

    for g in guides:
        mc.setAttr(g + '.width', width)


def fixMissingXgen():
    scenePath = mc.file(sceneName=True, q=True)
    sceneName = os.path.splitext(os.path.basename(scenePath))[0]
    for col in mc.ls(type='xgmPalette'):
        mc.setAttr('{}.xgFileName'.format(col), "{}__collection.xgen".format(sceneName), type="string")
    mc.file(save=True)
    mc.file(scenePath, open=True)


def createGuide():
    mm.eval('XgGuideTool;')


def comb():
    xgenm.ui.createDescriptionEditor(False).guideSculptContext(False)


def hideShow():
    xgenm.toggleGuideDisplay(xgenm.ui.createDescriptionEditor(False).currentDescription())


def editMode():
    cmd = 'selectMode -component;'
    cmd += 'selectType -vertex true;'
    cmd += 'hilite `ls -sl`;'
    mm.eval(cmd)


def objMode():
    mm.eval('selectMode - object;')


def preview():
    mm.eval('XgPreview;')


def lenLockToggle():
    cmd = 'string $lockCtx = `currentCtx`;'
    cmd += 'if ($lockCtx == "xgmGuideSculptTool"){'
    cmd += 'int $lockState = `xgmGuideSculptContext - q - lockLength "xgmGuideSculptTool"`;'
    cmd += 'if ($lockState == 1){'
    cmd += 'xgmGuideSculptContext - e - lockLength 0 "xgmGuideSculptTool";}'
    cmd += 'else{xgmGuideSculptContext -e -lockLength 1 "xgmGuideSculptTool";}}'
    mm.eval(cmd)


def spiral_ui():
    from ..third_party import spiral_along_curve
    spiral_along_curve.spiralAlongCurveUI()


def averageAndDelete():
    crvLib.averageAndDelete()


def updatePref(nodes=None, useSelection=True):
    """
    updates xgen_Pref attribute based on current position for selected geos
    :return:
    """
    if not nodes:
        if useSelection:
            nodes = mc.ls(sl=True)
            if not nodes:
                mc.error('Select scalp geos to update xgen_Pref value!')
        else:
            mc.error('Select scalp geos to update xgen_Pref value!')

    for node in nodes:
        mesh = mc.listRelatives(node, shapes=True)[0]

        if not mc.attributeQuery('xgen_Pref', node=mesh, exists=True):
            print('"{}" does not have xgen_Pref, skipped'.format(node))
            continue

        num_verts = mc.polyEvaluate(mesh, v=True)
        vert_pos_list = [num_verts]
        for i in range(num_verts):
            pos = mc.xform('{}.vtx[{}]'.format(mesh, i), q=True, ws=True, t=True)
            vert_pos_list.append(pos)
        mc.setAttr(mesh + '.xgen_Pref', *vert_pos_list, type='vectorArray')
        print('xgen_Pref updated for "{}"'.format(node))


def exportCollections(xgenDir='D:/xgen_test/'):
    palettes = mc.ls(sl=True, type='xgmPalette')
    palettes = [str(x) for x in palettes]
    if not palettes:
        mc.error('select xgen collection to export')

    for palette in palettes:
        fileName = os.path.join(str(xgenDir), palette + '.xgen')
        xgenm.exportPalette(palette, fileName)


def importCollections(xgenDir='D:/xgen_test/', namespace=''):
    paletteNames = os.listdir(xgenDir)
    for paletteName in paletteNames:
        fileName = os.path.join(xgenDir, paletteName)
        fileName = fileName.replace('\\', '/')
        xgenm.importPalette(str(fileName), [], str(namespace))


# print palet
# desc = xgenm.descriptions(palette)
# print desc
# customAttrs = xgenm.customAttrs(palettes[0], descs[0])
# boundGeometry = xgenm.boundGeometry(palettes[0], descs[0])
# boundFaces = xgenm.boundFaces(palettes[0], descs[0], boundGeometry[0])
# print boundGeometry
# print boundFaces

# xgui.createDescriptionEditor(False).preview(False)
# xgg.DescriptionEditor.previewer.execute()
# xgmPreview -pb {"smallFur_desc_new","eyeLash_desc_new","mane_desc_new","tail_desc_new","whisker_desc_new"};
# xg.igExportMaps( ["smallFur_desc_new","eyeLash_desc_new","mane_desc_new","tail_desc_new","whisker_desc_new"] )
