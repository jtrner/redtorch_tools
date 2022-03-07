import maya.cmds as mc
import maya.api.OpenMaya as om

p = om.MPoint(*mc.xform('p', q=1, ws=1, t=1))

dMesh = om.MSelectionList().add('refPlane').getDagPath(0).extendToShape()
intersector = om.MMeshIntersector()
intersector.create(dMesh.node(), dMesh.exclusiveMatrix())

pom = intersector.getClosestPoint(p)
print('Maya', pom.barycentricCoords)
mc.xform('pProjectionMaya', t = list(pom.point)[:3], ws=1)