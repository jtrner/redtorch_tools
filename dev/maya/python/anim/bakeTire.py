# calculata car wheel rotation and bakes it
import maya.cmds as mc
# dt = mc.datatypes
import maya.mel as mel


def BakeTire():

	# tire = mc.PyNode( 'tire' ) # wheel node
	tire = mc.ls(sl=True)[0]
	diameter = 2.0

	try:
		diameter = tire.getShape().boundingBoxMaxZ.get() - tire.getShape().boundingBoxMinZ.get()
	except:
		mc.warning('Object\'s diamater could not be found, default of 2.0 was used.')   



	circumference = 3.14 * diameter
	carFront = mc.group( empty=True )
	carFrontGrp = mc.group()
	carFront.translateZ.set(1)
	mc.pointConstraint( tire, carFrontGrp)
	mc.orientConstraint( tire, carFrontGrp, skip=('x','z'))




	def getVectorChange( obj=None, obj2=None ):
		mc.currentTime( mc.currentTime(query=True)-1, e=True)
		Vec = dt.Vector( mc.xform( obj, q=True, ws=True, t=True) )
		FrontVec = dt.Vector( mc.xform( obj2, q=True, ws=True, t=True) )
		mc.currentTime( mc.currentTime(query=True)+1, e=True)
		return dt.Vector( FrontVec - Vec )

	def getTranslateChange( obj=None ):
		mc.currentTime( mc.currentTime(query=True)-1, e=True)
		Vec = dt.Vector( mc.xform( obj, q=True, ws=True, t=True) )
		mc.currentTime( mc.currentTime(query=True)+1, e=True) 
		FrontVec = dt.Vector( mc.xform( obj, q=True, ws=True, t=True) )      
		return dt.Vector( FrontVec - Vec )

	def getPreviousRotateX( obj=None):
		mc.currentTime( mc.currentTime(query=True)-1, e=True)
		rot = ( mc.xform( obj, q=True, ws=True, ro=True) )
		mc.currentTime( mc.currentTime(query=True)+1, e=True) 
		return rot[0]


	timeRange = mel.eval( 'timeControl -q -rangeArray $gPlayBackSlider' )
	if timeRange[1] - timeRange[0] < 2.0:
		timeRange =  [ 0, mc.playbackOptions( q=True, maxTime=True) ]
	
	mc.currentTime( timeRange[0] , edit=True)

	
	for frame in range( int(timeRange[0]),int(timeRange[1]) ):
		mc.currentTime( mc.currentTime(query=True)+1, e=True) 

		defaultVec = getVectorChange( tire, carFront ) # find how much car direction has changed from previous frame
		translateChange = getTranslateChange( tire ) # find how much car has moved
		translateInMult = translateChange.normal().dot( defaultVec ) # find a multiplier that shows how much car has moved forward.
		
		translateInZ = translateChange.length() * translateInMult # find how much has car moved forward.
		
		oldRx = getPreviousRotateX( tire ) # find wheel rotation in previous frame
		newRx = ( translateInZ / circumference * 360 ) +oldRx # calculate wheel's relative to previous frame rotation 
		tire.rotateX.set(newRx) # set new rotation for the wheel
		
		mc.setKeyframe( tire.rotateX ) # set a key for wheel's rotation

	mc.currentTime( timeRange[0], edit=True)

	mc.delete( carFrontGrp ) 