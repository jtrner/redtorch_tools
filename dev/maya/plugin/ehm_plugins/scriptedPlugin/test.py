import maya.OpenMaya as om


normal_util = om.MScriptUtil()
# normal_util.createFromDouble(0)
normal_ptr = normal_util.asDouble4Ptr()

obj = getMObject( "pSphereShape1" )

geoItr = om.MItMeshVertex( obj )


while not geoItr.isDone():
    normal_util = om.MScriptUtil()
    normal_util.createFromList([1.0, 1.0, 1.0], 3)
    normal = om.MVector( normal_util.asDoublePtr() )
    geoItr.getNormal( normal , om.MSpace.kObject  )
    geoItr.next()
    
    
def getMObject( objs ):
    # get MObject of the given name
    
    if isinstance( objs, list ):
        nodes = []
        for obj in objs:
            selectionList = om.MSelectionList()
            selectionList.add( obj )
            node = om.MObject()
            selectionList.getDependNode( 0, node )
            nodes.append( node )
        return nodes
    else:
        selectionList = om.MSelectionList()
        selectionList.add( objs )
        node = om.MObject()
        selectionList.getDependNode( 0 , node ) 
        return node