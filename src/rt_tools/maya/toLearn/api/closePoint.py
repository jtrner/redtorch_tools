import maya.cmds as mc
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
from math import sqrt
#get dagPath
def getDagPath(xform):
    selectionList = om.MSelectionList()
    selectionList.add( str(xform) )
    dag = om.MDagPath()
    selectionList.getDagPath(0, dag)
    return dag
    
def getDependNode(obj):
    selectionList = om.MSelectionList()
    selectionList.add(obj)
    mobj = om.MObject()
    selectionList.getDependNode(0, mobj)
    return mobj    

#get mesh FN
def getMeshFn(mesh):
    if mc.objectType(mesh) == 'transform':
        mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]

    meshPath = getDagPath(mesh)
    meshFn = om.MFnMesh(meshPath)
    return meshFn

def floatMMatrixToMMatrix_(fm):
    mat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList ([
        fm[0],fm[1],fm[2],fm[3],
        fm[4],fm[5],fm[6],fm[7],
        fm[8],fm[9],fm[10],fm[11],
        fm[12],fm[13],fm[14],fm[15]], mat)
    return mat
    

mat = mc.xform('pSphere1', q=True, m=True)
mat = floatMMatrixToMMatrix_(mat)

inMeshFn = getMeshFn('pSphere1')

intersector = om.MMeshIntersector()
        
inPoints = om.MFloatPointArray()
inMeshFn.getPoints(inPoints, om.MSpace.kWorld)
colliderObject = getDependNode('pSphereShape1')
pointInfo = om.MPointOnMesh() 

try:
    intersector.create(colliderObject, mat)
    print('YAAAY')
except:
    pass
    
for k in range(inPoints.length()):
    if k == 1:
        point = om.MPoint(inPoints[k])
        mc.xform('pSphere2', t=(point[0], point[1], point[2]))
    point = om.MPoint(inPoints[k])

    if k == 2:
        try:
            intersector.getClosestPoint(point, pointInfo)
            mc.xform('pSphere3', t=(point[0], point[1], point[2]))
            break
    
        except:
            pass
    
    
