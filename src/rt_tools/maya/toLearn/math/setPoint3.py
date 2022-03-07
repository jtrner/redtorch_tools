import maya.api.OpenMaya as om2

node = 'pSphere1'
# Get selected object

sel = om2.MSelectionList()
sel.add(node)
dag = sel.getDagPath(0)

# Attach to MFnMesh
MFnMesh = om2.MFnMesh(dag)

# Create empty point array to store new points
newPointArray = om2.MPointArray()

for i in range( MFnMesh.numVertices ):
    # Create a point, and mirror it
    newPoint = MFnMesh.getPoint(i)
    newPointArray.append(newPoint)
    source_points = [x for x in newPointArray if x.x > 0]
    target_points = [x for x in newPointArray if x.x < 0]

# Set new points to mesh all at once
print(source_points)
print(target_points)
