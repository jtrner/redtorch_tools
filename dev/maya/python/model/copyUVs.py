# get number of uv shells and their Ids
import maya.OpenMaya as om
import maya.cmds as mc



def run():
    objs = mc.ls(sl=True)
    source = objs[0]
    target = objs[1]

    # create mesh Fn for source object
    sourceDag = getDagPath(source)
    sourceMesh = om.MFnMesh(sourceDag)

    # create mesh Fn for target object
    targetDag = getDagPath(target)
    targetMesh = om.MFnMesh(targetDag)

    # get UVs from source
    Us = om.MFloatArray()
    Vs = om.MFloatArray()
    sourceMesh.getUVs(Us,Vs)

    # set UVs for taget
    uvCounts = om.MIntArray()
    uvIds = om.MIntArray()
    sourceMesh.getAssignedUVs(uvCounts, uvIds)


    targetMesh.clearUVs()
    targetMesh.setUVs(Us, Vs)
    targetMesh.assignUVs(uvCounts,uvIds)

def getDagPath(obj):
    sel = om.MSelectionList()# create selection list
    sel.add(obj)# add object to selection    
    dag = om.MDagPath()# create path
    sel.getDagPath( 0, dag )# get path from selection list
    return dag
