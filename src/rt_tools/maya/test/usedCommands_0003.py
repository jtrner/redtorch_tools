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

deformer.copySkin()

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


import python.lib.jntLib as jntLib
reload(jntLib)
jntLib.orientUsingAim(jnts=mc.ls(sl=1) , upAim='locator1', aimAxes='x')
jntLib.orientLimb(jnts=None, aimAxes='x', upAxes='y')

import python.general.workspace as workspace
reload(workspace)
#workspace.publishAsset(jobDir='D:/all_works/01_projects', job='ehsan_projects',
#    seq='asset', shot='dog_anatomy', task='model', ext=None)

workspace.publishAsset(jobDir='D:/all_works/01_projects', job='behnam_for_turbosquid',
    seq='asset', shot='lion', task='model', ext=None)


from rt_tools.maya.anim import exportImportAnim
reload(exportImportAnim)
animUI = exportImportAnim.ExportImportAnim()
animUI.UI()

animUI.importAnim( nameSpace=None, replaceString=None)