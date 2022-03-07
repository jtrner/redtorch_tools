import maya.OpenMaya as om

def getDagPath(node):
    sel = om.MSelectionList()
    sel.add(node)
    dag = om.MDagPath()
    sel.getDagPath(0, dag)
    return dag
pcounts = om.MIntArray()
pconnect = om.MIntArray()
colliderPointNormal = om.MVector()
offsetValue = 2       
dag = getDagPath('pSphere1')
meshFn = om.MFnMesh(dag)
polycount = meshFn.numPolygons()

colliderPoints = om.MFloatPointArray()
meshFn.getVertices(pcounts, pconnect)

meshFn.getPoints(colliderPoints, om.MSpace.kObject)
newColliderPoints = om.MFloatPointArray()
        

newColliderPoints.clear()
for i in range(colliderPoints.length()):
    meshFn.getVertexNormal(i, colliderPointNormal , om.MSpace.kObject)
    newColliderPoint = om.MFloatPoint(colliderPoints[i].x+colliderPointNormal.x*offsetValue, 
                                      colliderPoints[i].y+colliderPointNormal.y*offsetValue, 
                                      colliderPoints[i].z+colliderPointNormal.z*offsetValue)
    newColliderPoints.append(newColliderPoint)
                
meshFn.createInPlace(colliderPoints.length(), polycount,newColliderPoints,pcounts,pconnect)
