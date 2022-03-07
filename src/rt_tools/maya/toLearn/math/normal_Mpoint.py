import maya.api.OpenMaya as om
import maya.cmds as mc

# A
__startIndex__ = {0:0,
                  1:4,
                  2:8,
                  3:12}
                  
def setMatrixRow(row=0,vec=None,matrix=None):
    matrix[__startIndex__[row]] = vec[0]
    matrix[__startIndex__[row]+1] = vec[1]
    matrix[__startIndex__[row]+2] = vec[2]

def getMatrixRow(row=0,inMat=None):
    outVec = om2.MVector(inMat[__startIndex__[row]],
                        inMat[__startIndex__[row]+1],
                        inMat[__startIndex__[row]+2])
    return outVec
    
def getMatrix(transform,matAttr = "worldMatrix[0]"):
    matData = cmds.getAttr(transform+'.'+matAttr)
    mat = om2.MMatrix(matData)
    return mat


def getRotationQuaternion(transform):
    matA = getMatrix(transform)
    tm_inMat = om2.MTransformationMatrix(matA)
    py_quat = tm_inMat.rotationComponents(asQuaternion=True)
    quat = om2.MQuaternion(py_quat)
    return quat
    
#get dagPath
def getDagPath ( xform ):
    selectionList = om.MSelectionList()
    selectionList.add( str(xform) )
    dagPath = om.MDagPath()
    dagPath = selectionList.getDagPath(0)
    return dagPath

#get mesh FN
def getMeshFn(mesh):
    if mc.objectType(mesh) == 'transform':
        mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]

    meshPath = getDagPath(mesh)
    print (meshPath)
    meshFn = om.MFnMesh(meshPath)
    return meshFn

def getNormal(mesh,vtxId,worldSpace=False):

    # Get MFnMesh
    meshFn = getMeshFn(mesh)
    # Determine sample space
    if worldSpace:
        sampleSpace = om.MSpace.kWorld
    else:
        sampleSpace = om.MSpace.kObject

    # Get Normals
    normal = om.MVector()
    normal = meshFn.getVertexNormal(vtxId,sampleSpace)

    # Return result
    return normal
    
pointA = om.MPoint(mc.xform('mesh.vtx[232]', q=1,t=1, ws=1))
normal = getNormal('mesh', 232)
mc.xform('y_point_end', t=normal, ws=1)
result = pointA + om.MVector(normal)
mc.xform('point', ws=1, t=om.MVector(result))    