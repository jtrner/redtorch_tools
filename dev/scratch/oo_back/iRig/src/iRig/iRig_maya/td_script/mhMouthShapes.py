################################################
# Mouth Shapes for Rigging
################################################
# Created By: Mitch Hutchinson
# Language: Python
# Version: 1.000
# Date: 29/01/2019
#-----------------------------------------------
# Description:
################################################

import maya.cmds as cmds

mayaVersion = float(cmds.about(version=True))

mouthShapes = ['Open_Smile_Wide','Open_Smile_Mid','Open_Smile_Narrow',
			   'Close_Smile_Wide','Close_Smile_Mid','Close_Smile_Narrow',
			   'Open_Frown_Wide','Open_Frown_Mid','Open_Frown_Narrow',
			   'Close_Frown_Wide','Close_Frown_Mid','Close_Frown_Narrow',
			   'Open_Default']
ctrlName = 'Mouth_Shape_Ctrl'
msGeoGrp = 'Mouth_Shape_GEO_Grp'
mainGrp = 'Mouth_Shape_Grp'

blankAttr = '[                  ]'

def texture(ms):
	imageDir = 'G:/Animation/scripts/mhScripts/misc/Mouth_Shapes/Mouth_Shapes_{}.png'.format(ms)
	
	if cmds.objExists( '{}_TEXTURE'.format(ms) ) == False:
		shaderNode = cmds.shadingNode('lambert', name='{}_TEXTURE'.format(ms), asShader=True)
		fileNode = cmds.shadingNode('file', name='{}_guideFileTexture'.format(ms), asTexture=True)
		cmds.setAttr( '{}_guideFileTexture.fileTextureName'.format(ms), imageDir, type="string")
		cmds.connectAttr( '{}_guideFileTexture.outColor'.format(ms), '{}_TEXTURE.color'.format(ms))
		cmds.connectAttr( '{}_guideFileTexture.outTransparency'.format(ms), '{}_TEXTURE.transparency'.format(ms))

	cmds.select( ms )
	cmds.hyperShade( assign='{}_TEXTURE'.format(ms) ) 

def create(*arg):
	if cmds.objExists( mainGrp ):
		cmds.delete( mainGrp )

	cmds.group( n='Close_Smile_Grp', em=True )
	cmds.group( n='Close_Frown_Grp', em=True )
	cmds.group( 'Close_Smile_Grp', 'Close_Frown_Grp', n='Close_Jaw_Grp' )

	cmds.group( n='Open_Smile_Grp', em=True )
	cmds.group( n='Open_Frown_Grp', em=True )
	cmds.group( 'Open_Frown_Grp', 'Open_Smile_Grp', n='Open_Jaw_Grp' )

	cmds.group( 'Open_Jaw_Grp', 'Close_Jaw_Grp', n=msGeoGrp )

	cmds.curve( n=ctrlName, d=1, p=[(-6,0,-6),(6,0,-6),(6,0,6),(-6,0,6),(-6,0,-6)], k=[0,1,2,3,4] )

	cmds.setAttr( '{}.overrideEnabled'.format(ctrlName), 1 )
	if mayaVersion >= 2016:
		cmds.setAttr( '{}.overrideRGBColors'.format(ctrlName), 0 )
	cmds.setAttr( '{}.overrideColor'.format(ctrlName), 14 )

	cmds.group( msGeoGrp,ctrlName, n=mainGrp )

	cmds.addAttr( ctrlName, ln='Scale', at='double', min=0.1, dv=1 )
	cmds.setAttr( '{}.Scale'.format(ctrlName), e=True, keyable=True )

	cmds.addAttr( ctrlName, ln='_', at='enum', en='{}:'.format(blankAttr) )
	cmds.setAttr( '{}._'.format(ctrlName), e=True, keyable=True, lock=True )

	cmds.addAttr( ctrlName, ln='Jaw_Default', at='bool', dv=1 )
	cmds.setAttr( '{}.Jaw_Default'.format(ctrlName), e=True, keyable=True )

	cmds.addAttr( ctrlName, ln='__', at='enum', en='{}:'.format(blankAttr) )
	cmds.setAttr( '{}.__'.format(ctrlName), e=True, keyable=True, lock=True )

	cmds.addAttr( ctrlName, ln='JawOpen', at='bool', dv=1 )
	cmds.setAttr( '{}.JawOpen'.format(ctrlName), e=True, keyable=True )
	cmds.addAttr( ctrlName, ln='_Shape', at='enum', en="Smile:Frown:" )
	cmds.setAttr( '{}._Shape'.format(ctrlName), e=True, keyable=True )
	cmds.addAttr( ctrlName, ln='_Width', at='enum', en="Wide:Mid:Narrow:" )
	cmds.setAttr( '{}._Width'.format(ctrlName), e=True, keyable=True )

	cmds.addAttr( ctrlName, ln='___', at='enum', en='{}:'.format(blankAttr) )
	cmds.setAttr( '{}.___'.format(ctrlName), e=True, keyable=True, lock=True )

	cmds.addAttr( ctrlName, ln='JawClose', at='bool', dv=0 )
	cmds.setAttr( '{}.JawClose'.format(ctrlName), e=True, keyable=True )
	cmds.addAttr( ctrlName, ln='__Shape', at='enum', en="Smile:Frown:" )
	cmds.setAttr( '{}.__Shape'.format(ctrlName), e=True, keyable=True )
	cmds.addAttr( ctrlName, ln='__Width', at='enum', en="Wide:Mid:Narrow:" )
	cmds.setAttr( '{}.__Width'.format(ctrlName), e=True, keyable=True )

	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleX'.format(ctrlName) )
	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleY'.format(ctrlName) )
	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleZ'.format(ctrlName) )

	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleX'.format(msGeoGrp) )
	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleY'.format(msGeoGrp) )
	cmds.connectAttr( '{}.Scale'.format(ctrlName), '{}.scaleZ'.format(msGeoGrp) )

	cmds.connectAttr( '{}.translateX'.format(ctrlName), '{}.translateX'.format(msGeoGrp) )
	cmds.connectAttr( '{}.translateY'.format(ctrlName), '{}.translateY'.format(msGeoGrp) )
	cmds.connectAttr( '{}.translateZ'.format(ctrlName), '{}.translateZ'.format(msGeoGrp) )

	cmds.connectAttr( '{}.rotateX'.format(ctrlName), '{}.rotateX'.format(msGeoGrp) )
	cmds.connectAttr( '{}.rotateY'.format(ctrlName), '{}.rotateY'.format(msGeoGrp) )
	cmds.connectAttr( '{}.rotateZ'.format(ctrlName), '{}.rotateZ'.format(msGeoGrp) )

	cmds.connectAttr( '{}.JawOpen'.format(ctrlName), '{}.visibility'.format('Open_Jaw_Grp') )
	cmds.connectAttr( '{}.JawClose'.format(ctrlName), '{}.visibility'.format('Close_Jaw_Grp') )


	for jaw in [['Close','__'],['Open','_']]:
		cmds.setAttr( '{}.{}Shape'.format(ctrlName,jaw[1]), 0 )
		cmds.setAttr( '{}.visibility'.format('{}_Smile_Grp'.format(jaw[0])), 1 )
		cmds.setAttr( '{}.visibility'.format('{}_Frown_Grp'.format(jaw[0])), 0 )
		cmds.setDrivenKeyframe( '{}.visibility'.format('{}_Smile_Grp'.format(jaw[0])), cd='{}.{}Shape'.format(ctrlName,jaw[1]) )
		cmds.setDrivenKeyframe( '{}.visibility'.format('{}_Frown_Grp'.format(jaw[0])), cd='{}.{}Shape'.format(ctrlName,jaw[1]) )
		
		cmds.setAttr( '{}.{}Shape'.format(ctrlName,jaw[1]), 1 )
		cmds.setAttr( '{}.visibility'.format('{}_Smile_Grp'.format(jaw[0])), 0 )
		cmds.setAttr( '{}.visibility'.format('{}_Frown_Grp'.format(jaw[0])), 1 )
		cmds.setDrivenKeyframe( '{}.visibility'.format('{}_Smile_Grp'.format(jaw[0])), cd='{}.{}Shape'.format(ctrlName,jaw[1]) )
		cmds.setDrivenKeyframe( '{}.visibility'.format('{}_Frown_Grp'.format(jaw[0]), cd='{}.{}Shape'.format(ctrlName,jaw[1])) )
		
		cmds.setAttr( '{}.{}Shape'.format(ctrlName,jaw[1]), 0 )

	for ms in mouthShapes:
		cmds.polyPlane( n=ms, h=10, w=10, sx=1, sy=1 )
		cmds.setAttr( '{}.overrideEnabled'.format(ms), 1 )
		cmds.setAttr( '{}.overrideDisplayType'.format(ms), 2 )
		cmds.setAttr( '{}Shape.overrideEnabled'.format(ms), 1 )
		cmds.setAttr( '{}Shape.overrideDisplayType'.format(ms), 2 )

		if 'Default' in ms:
			cmds.parent( ms, msGeoGrp )
		elif 'Open' in ms:
			if 'Smile' in ms:
				cmds.parent( ms, 'Open_Smile_Grp' )
			elif 'Frown' in ms:
				cmds.parent( ms, 'Open_Frown_Grp' )
		elif 'Close' in ms:
			if 'Smile' in ms:
				cmds.parent( ms, 'Close_Smile_Grp' )
			elif 'Frown' in ms:
				cmds.parent( ms, 'Close_Frown_Grp' )

		if 'Open' in ms:
			x = '_'
		elif 'Close' in ms:
			x = '__'
		else:
			x = None

		if x != None:
			if 'Wide' in ms:
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 0 )
				cmds.setAttr( '{}.visibility'.format(ms), 1 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 1 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 2 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
			elif 'Mid' in ms:
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 0 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 1 )
				cmds.setAttr( '{}.visibility'.format(ms), 1 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 2 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
			elif 'Narrow' in ms:
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 0 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 1 )
				cmds.setAttr( '{}.visibility'.format(ms), 0 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )
				cmds.setAttr( '{}.{}Width'.format(ctrlName,x), 2 )
				cmds.setAttr( '{}.visibility'.format(ms), 1 )
				cmds.setDrivenKeyframe( '{}.visibility'.format(ms), cd='{}.{}Width'.format(ctrlName,x) )

		texture(ms)

	cmds.connectAttr( '{}.Jaw_Default'.format(ctrlName), '{}.visibility'.format('Open_Default') )

	cmds.setAttr( '{}.rotateX'.format(ctrlName), 90 )
	cmds.setAttr( '{}.translateY'.format(ctrlName), 90 )
	cmds.setAttr( '{}.translateZ'.format(ctrlName), 30 )
	cmds.setAttr( '{}.JawOpen'.format(ctrlName), 0 )
	cmds.setAttr( '{}._Width'.format(ctrlName), 1 )
	cmds.setAttr( '{}.__Width'.format(ctrlName), 1 )


	cmds.setAttr( '{}.translateY'.format(ctrlName), keyable=False, channelBox=True )
	cmds.setAttr( '{}.translateZ'.format(ctrlName), keyable=False, channelBox=True )
	cmds.setAttr( '{}.Scale'.format(ctrlName), keyable=False, channelBox=True )

	cmds.setAttr( '{}.rotateX'.format(ctrlName), lock=True )

	cmds.setAttr( '{}.translateX'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.rotateY'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.rotateZ'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.scaleX'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.scaleY'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.scaleZ'.format(ctrlName), lock=True, keyable=False, channelBox=False )
	cmds.setAttr( '{}.visibility'.format(ctrlName), lock=True, keyable=False, channelBox=False )

	for a in ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']:
		cmds.setAttr( '{}.{}'.format(msGeoGrp,a), lock=True, keyable=False, channelBox=False )
		cmds.setAttr( '{}.{}'.format(mainGrp,a), lock=True, keyable=False, channelBox=False )

		for ms in mouthShapes:
			cmds.setAttr( '{}.{}'.format(ms,a), lock=True, keyable=False, channelBox=False )

	cmds.select( ctrlName )


def delete(*arg):
	if cmds.objExists( mainGrp ):
		cmds.delete( mainGrp )

	for ms in mouthShapes:
		if cmds.objExists( '{}_TEXTURE'.format(ms) ):
			cmds.delete( '{}_TEXTURE'.format(ms) )
			
		if cmds.objExists( '{}_guideFileTexture'.format(ms) ):
			cmds.delete( '{}_guideFileTexture'.format(ms) )

def toggle(*arg):
	if cmds.objExists( mainGrp ):
		delete()
	else:
		create()