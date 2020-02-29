# get time range
import maya.cmds as mc
import maya.mel as mel


def getTimeRange():
	# get time range
	timeRange = mel.eval( 'timeControl -q -rangeArray $gPlayBackSlider' )
	if timeRange[1] - timeRange[0] < 2.0:
		timeRange =  [ mc.playbackOptions( q=True, minTime=True), mc.playbackOptions( q=True, maxTime=True) ]
	return timeRange


def convertAnimatedGroomToCurve():
	yetiNode = mc.ls( sl=True )[0]

	timeRange = getTimeRange()

	# convert guides to curves for each frame
	for i in range( int(timeRange[0]), int(timeRange[1]) ):
		mc.currentTime( i )
		mc.select( yetiNode,  r=True )
		mel.eval( 'pgYetiConvertGroomToCurves' )


	# create groups from curves
	yetiCurves = mc.ls( 'pgYetiGroom1Shape_strand_*', type='nurbsCurve' )

	# create a blend shape for each set of curves
	curveGroups = []
	numOfCurveInEachGroup = len(yetiCurves) / int(timeRange[1]-timeRange[0])
	numOfGroups = int(timeRange[1]-timeRange[0])

	for i in range(1,numOfGroups+1):
		curveGroups.append(  mc.group( yetiCurves[numOfCurveInEachGroup*(i-1):numOfCurveInEachGroup*i] , name='%s__%s'%(yetiNode.name(), i ) ) )

	mc.select( curveGroups, r=True )

	"""
	mc.select( clear=True )
	for i in range( 1, len(curveGroups) ):
		mc.select( curveGroups[i], add=True )



	blendNode = mc.blendShape( ib=True)
	"""
	# mc.expression( s="%s.%s = frame;"%(blendNode, curveGroups[-1].name()), o=blendNode, ae=1, uc='all' )
