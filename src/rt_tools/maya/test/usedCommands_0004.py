

import maya.cmds as mc

nodeName = 'ehm_scatter'
pluginPath = 'D:/all_works/redtorch_tools/dev/maya/plugin/ehm_plugins/{0}/x64/Release/{0}.mll'.format(nodeName)
if mc.pluginInfo(pluginPath, q=True, loaded=True):
    mc.file(new=True, f=True)
    mc.unloadPlugin(nodeName)
mc.loadPlugin(pluginPath)



nodeName = 'ehm_locator'
pluginPath = 'D:/all_works/redtorch_tools/dev/maya/plugin/ehm_plugins/scriptedPlugin/{}.py'.format(nodeName)
if mc.pluginInfo(pluginPath, q=True, loaded=True):
    mc.file(new=True, f=True)
    mc.unloadPlugin(nodeName)
mc.loadPlugin(pluginPath)


scatter = mc.createNode("ehm_scatter")
sphere = mc.polySphere()[0]
sphere = mc.listRelatives(sphere, s=True)[0]
mc.setAttr(scatter + '.pointNumber', 10)
mc.connectAttr(sphere + '.outMesh', scatter + '.inputMesh')

print mc.getAttr(scatter + '.outPoints')
# locator = mc.createNode('ehm_locator')
#mc.connectAttr(scatter + '.outPoints', locator + '.inPoints')



from rt_python.lib import deformer
deformer.copySkin(useSelection=True)

from rt_python.lib import meshLib
meshLib.blendShapeGeosUnderTwoGroups(originalGroup='model_GRP', editedGroup='output_model_GRP', deleteHistory=True)

# twist joints display local axis
twist_jnts = mc.ls('?_elbow?_JNT', '?_shoulder?_JNT')
for jnt in twist_jnts:
    mc.setAttr(jnt+'.displayLocalAxis', 1)


for node in mc.ls():
    try: mc.setAttr(node+'.overrideEnabled', 0)
    except: pass

cmds.viewFit( all=True )

container.removeAll()

transform.removeOrigShapes(mc.ls(sl=True))
transform.insert(ctl)
transform.duplicateClean('L_eye_GRP')
transform.mirrorLikeJnt()

curve.replaceShape(nodes=mc.ls(sl=True), shape='square')
curve.mirror()

display.setColor(color='cyan')
display.setColor(color='pink')
display.setColor(color='yellow')
display.setColor(color='maroon')
display.setColor(obj=mc.ls(sl=True)[0], color='yellow')

from rt_python.lib import deformer
deformer.copySkin(useSelection=True)

planarizeJnts.adjustFingers()

pose.bipedArmGoToTPose()
pose.bipedArmGoToAPose()

shapeLib.extractTargets('C_head_BLS', neutral='C_head_GEO')

# import selected or all skinClusters in scene
geo = mc.ls(sl=True)[0]
path = mc.internalVar(uad=True)
wgtFile = os.path.join(path, '..', '..', 'Desktop', geo+'.wgt')
deformer.importSkin(wgtFile)
skincluster.Skincluster.importData(dataPath=wgtFiles)

# to do
# pose should support user defined attrs


import re
import python.lib.connect as connect
path = 'D:/all_works/01_projects/ehsan_projects/asset/dog_anatomy/task/rig/users/ehsan/v0003/data/constraints.json'
connect.exportConstraints(path=path, underNode='C_skeleton_GRP')
connect.importConstraints(path=path)


import python.general.workspace as workspace
reload(workspace)
#workspace.publishAsset(jobDir='D:/all_works/01_projects', job='ehsan_projects',
#    seq='asset', shot='dog_anatomy', task='model', ext=None)

workspace.publishAsset(jobDir='D:/all_works/01_projects', job='behnam_for_turbosquid',
    seq='asset', shot='lion', task='model', ext=None)


# anim export import
from rt_python.anim import exportImportAnim
reload(exportImportAnim)
animUI = exportImportAnim.ExportImportAnim()
animUI.UI()

animUI.importAnim( nameSpace=None, replaceString=None)


# lattice
import python.lib.deformer as deformer
reload(deformer)
for ffd in ['C_upperTeeth_FFD', 'L_eye_FFD']:
    ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
    deformer.exportFFD(ffd=ffd, path=ffd_json)

import python.lib.deformer as deformer
reload(deformer)
for ffd in ['upperTeeth_FFD']:  # 'R_eye_FFD'
    ffd_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', ffd+'.json')
    deformer.importFFD(path=ffd_json)

import python.lib.deformer as deformer
reload(deformer)
deformer.mirrorFFD(ffd='L_eye_FFD')

import python.lib.trsLib as trsLib
trsLib.mirror('L_Eye_00__GRP', copy=True)

# rename children
grps = mc.ls(sl=True)
for grp in grps:
    suffix = grp.split('C_mouth_GRP')[-1]
    children = mc.listRelatives(grp, f=1) or []
    for child in children:
        mc.rename(child, child.split('|')[-1]+suffix)


# copy Skin From Reference
import python.lib.deformer as deformer
reload(deformer)
deformer.copySkinFromReference()


# transfer In Connections
import maya.cmds as mc
import python.lib.attrLib as attrLib
reload(attrLib)
shape = 'scalpShape'
oldName = 'collection1'
newName = 'collection_updo'
attrs = [x for x in mc.listAttr(shape) if x.startswith(newName)]
attrs = [x for x in mc.listAttr(shape) if x.startswith(oldName)]
for attr in attrs:
    oldAttr = shape + '.' + attr
    newAttr = shape + '.' + attr.replace(oldName, newName, 1)
    attrLib.duplicateAttr(source=oldAttr, target=newAttr)
    attrLib.transferInConnections(source=oldAttr, target=newAttr)



# aim
import python.lib.jntLib as jntLib
reload(jntLib)
jntLib.orientLimb(jnts=mc.ls(sl=True), aimAxes='x', upAxes='-z')


# pole vector
import python.rig.command.pv as pv
pv.Pv(jnts=mc.ls(sl=True), distance=1.0, createLoc=True)


# intermediate
import maya.cmds as mc
cv = mc.ls(sl=True, fl=True)[0]
mc.setAttr(cv + ".intermediateObject", 0)
curves = mc.ls('mane_????_simCurveShape')
for crv in curves:
    mc.setAttr(crv + ".intermediateObject", 0)


# exportBlsWgts
import python.lib.deformer as deformer
reload(deformer)
bls = 'blendShape1'
bls_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', bls+'.json')
deformer.exportBlsWgts(bls=bls, path=bls_json)
deformer.getWgtsFromCrvAndAnimCrv(geo='C_Bottle_00__MSH', crv='lips_wgt_crv', curveType='mid')
deformer.getPoints(geo='C_Bottle_00__MSH', asMPoint=False)


# importDeformerWgts
import python.lib.deformer as deformer
reload(deformer)
a = mc.cluster()
deformer.createShrinkWrap(driver='L_Sclera_00__MSH',
                          driven='L_Pupils_00__MSH',
                          projection=4,
                          offset=0)
import python.lib.deformer as deformer
reload(deformer)
node = 'shrinkWrap1'
wgts_json = os.path.join(mc.internalVar(uad=True), '..', '..', 'Desktop', node+'.json')
deformer.exportDeformerWgts(node=node, path=wgts_json)
deformer.importDeformerWgts(path=wgts_json, newNode='shrinkWrap2')
for i, esm in enumerate(a):
    print i, esm