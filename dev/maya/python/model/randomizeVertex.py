import maya.cmds as mc
import random as random

def RandomizeVertex( objs = None, displace = 0.5 ):
	
	if objs==None:
		objs = mc.ls( sl=True )
	else:
		objs = mc.ls( objs )
	
	for obj in objs:
		
		shape = obj.getShape()
		numOfVtxs = mc.polyEvaluate( shape, vertex=True )
		
		for i in range( numOfVtxs ):

			currentDisp = random.uniform( -displace , displace )
			axis =  random.randint( 0 , 2 )
			if axis == 0:
				shape.vtx[i].translateBy( (currentDisp,0,0) )
			if axis == 1:
				shape.vtx[i].translateBy( (0,currentDisp,0) )
			if axis == 2:
				shape.vtx[i].translateBy( (0,0,currentDisp) )