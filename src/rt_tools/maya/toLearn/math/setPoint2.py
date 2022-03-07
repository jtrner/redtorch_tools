import maya.api.OpenMaya as om2

# Get selected object
srcs_sel = om2.MGlobal.getActiveSelectionList()
srcs_it = om2.MItSelectionList(srcs_sel)

path = om2.MDagPath()
srcs_it.getDagPath()

# Attach to MFnMesh
MFnMesh = om2.MFnMesh(dag)

# Create empty point array to store new points
newPointArray = om2.MPointArray()

for i in range( MFnMesh.numVertices ):
    # Create a point, and mirror it
    newPoint = MFnMesh.getPoint(i)
    newPoint.x = -newPoint.x
    newPointArray.append(newPoint)
# Set new points to mesh all at once
MFnMesh.setPoints(newPointArray)