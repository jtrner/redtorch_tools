#importing the OpenMaya Module
from maya.api import OpenMaya as om
#converting selected object into MObject and MFnMesh functionset
mSel=om.MSelectionList()
mSel.add(cmds.ls(sl=1)[0])
mObj=mSel.getDagPath(0)
mfnMesh=om.MFnMesh(mObj)
#getting our basePoints
baseShape = mfnMesh.getPoints()
#this function can be used to revert the object back to the baseShape
mfnMesh.setPoints(baseShape)
#getting l and r verts
mtol=0.02# this will be our mid tolerance, if the mesh is not completely symmetric on the mid
lVerts=[]#for storing left Verts
rVerts=[]#for storing right Verts
mVerts=[]#for storing mid Verts
corrVerts={} #for storing correspondign verts
for i in range(mfnMesh.numVertices): #iteratign through all the verts on the mesh
    thisPoint = mfnMesh.getPoint(i) #getting current point position
    if thisPoint.x>0+mtol: # if pointValue on x axis is bigger than 0+midTolerance
        lVerts.append((i, thisPoint))#append to left vert storage list(i = vert index, thisPoint = vert Mpoint position)
    elif thisPoint.x<0-mtol: #opposite of left vert calculation
        rVerts.append((i, thisPoint))
    else: #if none of the above, assign to mid verts
        mVerts.append((i, thisPoint))
rVertspoints=[i for v,i in rVerts] #getting the vert mPoint positions of the right side
for vert, mp in lVerts: #going through our left points, unpacking our vert index and mPoint position()
    nmp=om.MPoint(-mp.x, mp.y, mp.z) #storing the reversed mpoint of the left side vert
    rp = mfnMesh.getClosestPoint(nmp)#getting the closest point on the mesh
    if rp[0] in rVertspoints: #cheking if the point is in the right side
        corrVerts[vert] = rVerts[rVertspoints.index(rp[0])][0] #adding it if it is true
    else:#if it is not, calculate closest vert
        #iterating through rVertspoints and find smallest distance
        dList=[nmp.distanceTo(rVert) for rVert in rVertspoints]#distance list for each vert based on input point
        mindist = min(dList)#getting the closest distance
        corrVerts[vert] = rVerts[dList.index(mindist)][0]#adding the vert
#now the corrVerts will have stored the corresponding vertices from left to right
a = [x for x in corrVerts]
print(corrVerts)
    