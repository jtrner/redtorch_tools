"""
Author: Ehsan Hassani Moghddam (hm.ehsan@yahoo.com)

History:
    07-10-16 (ehsan)    first release


"""
import sys
path = "F:\\softwares\\numpy.1.9.2"
if path not in sys.path:
    sys.path.append( path )

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import numpy as np

pluginName = 'ehm_rigidTransform'
pluginId = OpenMaya.MTypeId(0x0011E18A)


class ehm_rigidTransform(OpenMayaMPx.MPxDeformerNode):

    aRefMesh = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, data, itGeo, localToWorldMatrix, geomIndex):

        # envelope
        envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        envelopeHandle = data.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()
        if not envelopeValue:
            return None

        # get ref mesh
        hRefMesh = data.inputValue(self.aRefMesh)
        oRefMesh = hRefMesh.asMesh()
        if oRefMesh.isNull():
            return None

        """
        # get input mesh
        input = OpenMayaMPx.cvar.MPxDeformerNode_input
        inputHandle_array = data.outputArrayValue(input)
        inputHandle_array.jumpToElement(geomIndex)
        inputValue_element = inputHandle_array.outputValue()
        inputGeo = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        hInputMesh = inputValue_element.child(inputGeo)
        oInputGeom = hInputMesh.asMesh()
        """

        # get points of current mesh
        origPoses = OpenMaya.MPointArray()
        itGeo.allPositions(origPoses, OpenMaya.MSpace.kObject)

        # get points of reference mesh
        fnMesh = OpenMaya.MFnMesh(oRefMesh)
        refPoses = OpenMaya.MPointArray()
        fnMesh.getPoints(refPoses, OpenMaya.MSpace.kObject)
        
        # get rigid transform matrix
        refPosesArray = npMatFromMPointArray(refPoses)
        origPosesArray = npMatFromMPointArray(origPoses)
        r, t = rigid_transform_3D( refPosesArray, origPosesArray )
        mat = createMatrixFromRT(r, t)

        # transform each point by rigid transform matrix
        finalPosesArray = refPosesArray * mat
        finalPoses = mPointArrayFromNpMat(finalPosesArray)
        
        # set points
        itGeo.setAllPositions(finalPoses)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ehm_rigidTransform())


def nodeInitializer():
    # reference mesh
    tAttr = OpenMaya.MFnTypedAttribute()
    ehm_rigidTransform.aRefMesh = tAttr.create("refMesh", "refMesh", OpenMaya.MFnData.kMesh)
    ehm_rigidTransform.addAttribute(ehm_rigidTransform.aRefMesh)

    # attribute effects
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    ehm_rigidTransform.attributeAffects( ehm_rigidTransform.aRefMesh, outputGeom )

    # make deformer paintable
    OpenMaya.MGlobal.executeCommand("makePaintable -attrType multiFloat -sm deformer ehm_rigidTransform ws;")


def initializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(pluginName, pluginId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write('Load plugin failed: %s' % pluginName)


def uninitializePlugin(mObj):
    plugin = OpenMayaMPx.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(pluginId)
    except:
        sys.stderr.write('Unload plugin failed: %s' % pluginName)


def printMatrix(mat):
    for i in xrange(4):
        tmp=[]
        for j in xrange(4):
            tmp.append("{0:0.1f}".format(mat(i, j)))
        print tmp


def printNpMatrix(mat):
    for i in xrange(4):
        tmp=[]
        for j in xrange(4):
            tmp.append("{0:0.1f}".format(mat[i, j]))
        print tmp


def npMatFromMPointArray(pointArray):
    array = []
    for i in xrange(pointArray.length()):
        array.extend([pointArray[i].x, pointArray[i].y, pointArray[i].z, 1])
    return np.mat(array).reshape(len(array)/4,4)


def mPointArrayFromNpMat(npMat):
    pointArray = OpenMaya.MPointArray()
    for i in xrange(npMat.size/4):
        tmp = [0,0,0,0]
        for j in xrange(4):
            tmp[j] = npMat[i,j]
        pointArray.append(*tmp)
    return pointArray


def rigid_transform_3D( A, B ):
    assert len(A) == len(B)

    N = A.shape[0] # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # centre the points
    AA = A - centroid_A #np.tile(centroid_A, (N, 1))
    BB = B - centroid_B #np.tile(centroid_B, (N, 1))

    # covariance matrix
    H = AA.T.dot(BB)
    #printNpMatrix(H)

    # SVD
    U, S, Vt = np.linalg.svd(H)

    # rotation
    R = Vt.T * U.T

    # special reflection case
    
    if np.linalg.det(R) < 0: #if reflection detected
       Vt[2,:] *= -1
       R = Vt.T * U.T

    """
    if determinant(R) &lt; 0
        multiply 3rd column of V by -1
        recompute R
    end if

    or better?

    if determinant(R) &lt; 0
        multiply 3rd column of R by -1
    end if

        No, Second method makes sudden flips when rotation is reversed.
        First method doesn't make sudden flips.
    """

    # translation
    t = -R*centroid_A.T + centroid_B.T

    return R, t


def createMatrixFromRT(r, t):
    rtMatAsList = [ 1,0,0,0
                   ,0,1,0,0
                   ,0,0,1,0
                   ,0,0,0,1 ]

    # add rotate values to matrix
    for i in xrange(3):
        for j in xrange(3):
            rtMatAsList[i*4 + j] = r[j, i]

    # add translate values to matrix
    for i in xrange(3):
            rtMatAsList[12+i] = t[i,0]

    # create the matrix
    mat = OpenMaya.MMatrix()
    util = OpenMaya.MScriptUtil()
    util.createMatrixFromList(rtMatAsList, mat)

    return mat

"""
mc.file(new=True, f=True)
if mc.pluginInfo("ehm_rigidTransform", q=True, loaded=True):
    mc.unloadPlugin("ehm_rigidTransform", f=True)


mc.file("D:/all_works/MAYA_DEV/EHM_tools/MAYA/plugin/ehm_plugins/scriptedPlugin/ehm_rigidTransform/test_001.mb", open=True, f=True)
mc.loadPlugin( "D:\\all_works\\MAYA_DEV\\EHM_tools\\MAYA\\plugin\\ehm_plugins\\scriptedPlugin\\ehm_rigidTransform\\ehm_rigidTransform" )
rigid = mc.deformer("pSphere2", type="ehm_rigidTransform", name="test")[0]
mc.connectAttr("pSphereShape1.outMesh", rigid+".refMesh")
"""