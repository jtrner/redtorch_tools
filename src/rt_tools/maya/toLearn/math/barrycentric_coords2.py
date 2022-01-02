import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
 
meshName = "pSphereShape1"
locName = "locatorShape1"
defName = "cluster1"
 
list = OpenMaya.MSelectionList()
list.add(meshName)
list.add(locName)
list.add(defName)
 
meshDag = OpenMaya.MDagPath()
locDag = OpenMaya.MDagPath()
defObj = OpenMaya.MObject()
 
list.getDagPath(0, meshDag)
list.getDagPath(1, locDag)
list.getDependNode(2, defObj)

#So that now we have the basic information we need, let’s get our hands dirty and dive into this.

#First let’s get weights of the deformer i.e,”cluster1" in this example.

#We create MFnDependencyNode of the cluster so that we can get to the Attribute Plug and extract all the weights per vertex.

defFn = OpenMaya.MFnDependencyNode(defObj)
weightsPlug = defFn.findPlug("weightList") # "cluster1.weightList"
 
for i in range(weightsPlug.numElements()):
    weightIdxPlug = weightsPlug.elementByPhysicalIndex(i) # "cluster1.weightList[0]"
 
for j in range(weightIdxPlug.numChildren()):
    weights = weightIdxPlug.child(j) # "cluster1.weightList[0].weights"
 
weightList = {}
 
for i in range(weights.numElements()):
    val = weights.elementByPhysicalIndex(i).asFloat()
    weightList[i] = val
print('weightList:' , weightList)    

#Now that we have weights of each vertex in our dictionary “weightList”, 
#we can start the process to work barycentric coordinates using the position of the locator.

#So for this we are going to use MMeshIntersector.closestPoint() API function, 
#as this is faster than MFnMesh.closestPoint() and we get way more information from MMeshIntersector that we need.

# Creating the MMeshIntersector and PointOnMesh
meshIntersector = OpenMaya.MMeshIntersector()
pointInfo = OpenMaya.MPointOnMesh()
 
meshIntersector.create(meshDag.node(), meshDag.exclusiveMatrix())

#So now as we have created out MMeshIntersector, lets get the locator’s position as well in our next step.

# Getting the matrix of the locator to get its exact position in world space
mMatrix = locDag.exclusiveMatrix()
locMatrix = OpenMaya.MTransformationMatrix( mMatrix )
locPoint = OpenMaya.MPoint( locMatrix.getTranslation( OpenMaya.MSpace.kWorld ))

#Now next, we need to create our MScriptUtil for extracting the u and v coordinates.

uUtil = OpenMaya.MScriptUtil(0.0)
uPtr = uUtil.asFloatPtr()
vUtil = OpenMaya.MScriptUtil(0.0)
vPtr = vUtil.asFloatPtr()
 
dummy = OpenMaya.MScriptUtil()
dummyIntPtr = dummy.asIntPtr()

#Alright now let’s get the u and v coords, also from this we will get the face index and 
#triangle index of that corresponding face closest to the position of our locator.

meshIntersector.getClosestPoint(locPoint, pointInfo)
 
pointInfo.getBarycentricCoords(uPtr,vPtr)
u = uUtil.getFloat(uPtr)
v = vUtil.getFloat(vPtr)
w = 1-u-v
print('u:', u)
print('v:', v)
print('w:', w)
 
faceId = pointInfo.faceIndex()
triId = pointInfo.triangleIndex()

#For those who don’t understand barycentric coordinates, you can search on wiki or just google it and there are tons of information on it.

#Alright so now as we have our face and triangle index let use MItMeshPolygon iterator to get the vertex ids of that triangle.

currentFace = OpenMaya.MItMeshPolygon(meshDag)
 
pointArray = OpenMaya.MPointArray()
vertIdList = OpenMaya.MIntArray()
 
currentFace.setIndex(faceId, dummyIntPtr)
currentFace.getTriangle(triId, pointArray, vertIdList, OpenMaya.MSpace.kWorld )

#Now that we got out vertices of the triangle and we have already calculated the 
#weights of these points from before in our dictionary weightList


P0 = weightList[vertIdList[0]]
P1 = weightList[vertIdList[1]]
P2 = weightList[vertIdList[2]]
print('p0:', P0)
print('p1:', P1)
print('p2:', P2)
 
P = u*P0 + v*P1 + w*P2
print('p:', P)
print('*********************************************************')

#*********************************************************