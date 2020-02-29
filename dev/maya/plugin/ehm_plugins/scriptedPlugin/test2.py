mc.file("D:/all_works/MAYA_DEV/EHM_tools/MAYA/plugin/ehm_plugins/scriptedPlugin/ehm_rigidTransform/test_001.mb", open=True, f=True)

mc.loadPlugin( "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin\\ehm_plugins\\scriptedPlugin\\ehm_rigidTransform\\ehm_rigidTransform" )
rigid = mc.deformer("pSphere2", type="ehm_rigidTransform", name="test")[0]
mc.connectAttr("pSphereShape1.outMesh", rigid+".refMesh")


mc.file(new=True, f=True)
mc.unloadPlugin("ehm_rigidTransform", f=True)

import maya.cmds as mc
import maya.OpenMaya as om
import numpy as np

mc.polyCube()
sel = om.MSelectionList()
om.MGlobal.getActiveSelectionList(sel)
dagPath = om.MDagPath()
sel.getDagPath(0, dagPath)
fnMesh = om.MFnMesh(dagPath)
pa = om.MPointArray()
fnMesh.getPoints(pa)

mat = npMatFromMPointArray(pa)


pointArray = om.MPointArray()
for i in xrange(mat.size/3):
    temp = [0,0,0,0]
    for j in xrange(3):
        temp[j] = mat[i,j]
    pointArray.append(*temp)
        
pa = MPointArrayFromNpMat(mat)

def npMatFromMPointArray(pointArray):
    array = []
    for i in xrange(pointArray.length()):
        array.extend([pointArray[i].x, pointArray[i].y, pointArray[i].z])
    return np.mat(array).reshape(len(array)/3,3)

def MPointArrayFromNpMat(npMat):
    ppointArray = om.MPointArray()
    for i in xrange(mat.size/3):
        temp = [0,0,0,0]
        for j in xrange(3):
            temp[j] = mat[i,j]
        pointArray.append(*temp)
    return pointArray    
    
    