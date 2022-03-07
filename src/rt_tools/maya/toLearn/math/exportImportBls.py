import maya.cmds as mc
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2

def getMObject(obj):
    mSel = om2.MSelectionList()
    mSel.add(obj)
    mobj = mSel.getDependNode(0)
    return mobj
    
def getGeomIndex(geometry,deformer):	
	geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
	geomObj = getMObject(geometry)
	
	deformerObj = getMObject(deformer)
	deformerFn = oma2.MFnGeometryFilter(deformerObj)
	geomIndex = deformerFn.indexForOutputShape(geomObj)
	return geomIndex

def getTargetWeights(blendShape,target,geometry=''):
	aliasList = mc.aliasAttr(blendShape,q=True)
	aliasTarget = aliasList[(aliasList.index(target)+1)]
	targetIndex = aliasTarget.split('[')[-1]
	targetIndex = int(targetIndex.split(']')[0])
	
	geomIndex = 0
	if geometry: geomIndex = getGeomIndex(geometry,blendShape)
	
	wt = mc.getAttr(blendShape+'.it['+str(geomIndex)+'].itg['+str(targetIndex)+'].tw')[0]
	
	return list(wt)
	
weight = getTargetWeights('blendShape1','pSphere3',geometry='pSphere1')	
print(weight)

def setTargetWeights(blendShape,target,wt,geometry=''):

	aliasList = mc.aliasAttr(blendShape,q=True)
	aliasTarget = aliasList[(aliasList.index(target)+1)]
	targetIndex = aliasTarget.split('[')[-1]
	targetIndex = int(targetIndex.split(']')[0])
	
	geomIndex = 0
	if geometry: geomIndex = getGeomIndex(geometry,blendShape)

	mc.setAttr(blendShape+'.it['+str(geomIndex)+'].itg['+str(targetIndex)+'].tw[0:'+str(len(wt)-1)+']',*wt)
	
setTargetWeights('blendShape1','pSphere3',weight,geometry='pSphere1')	
