for node in mc.ls():
    try: mc.setAttr(node+'.overrideEnabled', 0)
    except: pass

cmds.viewFit( all=True )

container.removeAll()

transform.removeOrigShapes(mc.ls(sl=True))
transform.insert(ctl)
transform.duplicateClean('L_eye_GRP')
transform.mirrorLikeJnt()

deformLib.copySkin()
deformLib.copySkin()

planarizeJnts.adjustFingers()

pose.bipedArmGoToTPose()
pose.bipedArmGoToAPose()

shapeLib.extractTargets('C_head_BLS', neutral='C_head_GEO')

# import selected or all skinClusters in scene
geo = mc.ls(sl=True)[0]
path = mc.internalVar(uad=True)
wgtFile = os.path.join(path, '..', '..', 'Desktop', geo+'.wgt')
deformLib.importSkin(wgtFile)
deformLib..importData(dataPath=wgtFiles)

# to do
# pose should support user defined attrs
