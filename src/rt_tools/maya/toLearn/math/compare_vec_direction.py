import maya.cmds as mc
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
from math import sqrt
#get dagPath
def getDagPath ( xform ):
    selectionList = om2.MSelectionList()
    selectionList.add( str(xform) )
    dagPath = om2.MDagPath()
    dagPath = selectionList.getDagPath(0)
    return dagPath

#get mesh FN
def getMeshFn(mesh):
    if mc.objectType(mesh) == 'transform':
        mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]

    meshPath = getDagPath(mesh)
    print (meshPath)
    meshFn = om2.MFnMesh(meshPath)
    return meshFn

def getNormal(mesh,vtxId,worldSpace=False):

    # Get MFnMesh
    meshFn = getMeshFn(mesh)
    # Determine sample space
    if worldSpace:
        sampleSpace = om2.MSpace.kWorld
    else:
        sampleSpace = om2.MSpace.kObject

    # Get Normals
    normal = om2.MVector()
    normal = meshFn.getVertexNormal(vtxId,sampleSpace)

    # Return result
    return normal
def floatMMatrixToMMatrix_(fm):
    mat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList ([
        fm[0],fm[1],fm[2],fm[3],
        fm[4],fm[5],fm[6],fm[7],
        fm[8],fm[9],fm[10],fm[11],
        fm[12],fm[13],fm[14],fm[15]], mat)
    return mat
    

mat = mc.xform('mat', q=True, m=True)
mat = floatMMatrixToMMatrix_(mat)


pos2 = mc.xform('pSphere1', q=True, t=True)
b = om.MVector(pos2[0], pos2[1], pos2[2])

c = om.MPoint(a[0], a[1], a[2]) * mat
c = c - om.MPoint(a[0], a[1], a[2])
c = om.MVector(c[0], c[1], c[2])
print(c[0], c[1], c[2])
pointA = om2.MPoint(mc.xform('pSphere1.vtx[254]', q=1,t=1, ws=1))
pointA = om.MVector(pointA[0], pointA[1], pointA[2])
print(pointA[0], pointA[1], pointA[2])

c.x = c.x if pointA.x > 0 and c.x > 0 or pointA.x < 0 and c.x < 0 else -1 * c.x
c.y = c.y if pointA.y > 0 and c.y > 0 or pointA.y < 0 and c.y < 0 else -1 * c.y
c.z = c.z if pointA.z > 0 and c.z > 0 or pointA.z < 0 and c.z < 0 else -1 * c.z
print(c[0], c[1], c[2])
print(pointA[0], pointA[1], pointA[2])

mc.xform('point', t=(c[0], c[1], c[2]))
