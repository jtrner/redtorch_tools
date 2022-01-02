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
    
#**************
p_orig =om.MPoint(mc.xform('orig.vtx[233]', q = True, t = True, ws = True))
p_deformed =om.MPoint(mc.xform('deformed.vtx[233]', q = True, t = True, ws = True))
n_orig = getNormal('orig', 233)
n_deformed = getNormal('deformed', 233)

delta_vec = p_deformed - p_orig
dot = n_orig * delta_vec
dot *= -1.0

result = p_deformed + (n_deformed  * dot)

mc.xform('deformed.vtx[233]', ws = True, t = om.MVector(result))

    
#**************    
    
mesh ='pSphere1'
mesh2 ='pSphere2'     
     
pointA = om.MPoint(mc.xform(mesh + '.vtx[258]', q = 1, t = 1, ws= 1))
print(pointA)
normal = getNormal(mesh, 258)
print(normal) 
result = pointA + normal

mc.xform(mesh2, ws = 1, t = om.MVector(result))  
#**************    

A = om.MPoint(mc.xform('A', q = True, ws = True, t = True))
B = om.MPoint(mc.xform('B', q = True, ws = True, t=  True))

AB = om.MVector(B-A)
AB_len = AB.length()
normal =AB/ AB_len

result = A + normal

mc.xform('C', ws = True, t = om.MVector(result))
#**************  
pointA = om.MVector(mc.xform('A', q = True, ws = True, t= True))
pointB = om.MVector(mc.xform('B', q = True, ws = True, t=  True))  
pointC = om.MVector(mc.xform('C', q = True, ws = True, t=  True))  

AB = pointB - pointA
AC = pointC - pointA

ACNormalize = AC.normalize()

projLength = AB * ACNormalize

proj_vec = (ACNormalize * projLength) + pointA

PB = pointB - proj_vec
PBNorm = PB.normalize()

result = pointB + PBNorm * 10


mc.xform('pSphere1', t = result)
#**************  
pointA = om.MVector(mc.xform('pSphere1.vtx[213]', q = True, ws = True, t= True))
pointB = om.MVector(mc.xform('pSphere1.vtx[233]', q = True, ws = True, t=  True))  
pointC = om.MVector(mc.xform('pSphere1.vtx[234]', q = True, ws = True, t=  True))  
pointD = om.MVector(mc.xform('pSphere1.vtx[254]', q = True, ws = True, t=  True)) 


AB = pointB - pointA
AC = pointC - pointA

normalA = AC ^ AB
normalA = normalA.normalize()

DB = pointB - pointD
DC = pointC - pointD   
normalB = DB ^ DC
normalB = normalB.normalize()

result_norm = (normalA + normalB) / 2.0
result_point = (pointA + pointD) / 2.0


result =  result_point + result_norm 
mc.xform('pSphere2', t = result)  









