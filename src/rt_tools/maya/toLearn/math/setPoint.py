import maya.OpenMaya as OpenMaya

# Get selected object
mSelList = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(mSelList)
sel = OpenMaya.MItSelectionList(mSelList)
path = OpenMaya.MDagPath()
sel.getDagPath(path)

# Attach to MFnMesh
MFnMesh = OpenMaya.MFnMesh(path)

# Create empty point array to store new points
newPointArray = OpenMaya.MPointArray()

for i in range( MFnMesh.numVertices() ):
    # Create a point, and mirror it
    newPoint = OpenMaya.MPoint()
    MFnMesh.getPoint(i, newPoint)
    newPoint.z = -newPoint.z
    newPointArray.append(newPoint)

# Set new points to mesh all at once
MFnMesh.setPoints(newPointArray)