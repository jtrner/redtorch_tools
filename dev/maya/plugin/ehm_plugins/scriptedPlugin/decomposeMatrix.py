import math
import maya.OpenMaya as om


# def that prints values of the given matrix
def printMatrix( mat ):
    for i in range(4):
        tmp = []
        for j in range(4):
            if mat(i,j) < 0.00001 and mat(i,j) > -0.00001:
                tmp.append( 0.0 )
            else:
                tmp.append( mat(i,j) )
        print  tmp 



# get the current selection
selectionList = om.MSelectionList()
om.MGlobal.getActiveSelectionList( selectionList )

# find the dag path
dagPath = om.MDagPath() 
selectionList.getDagPath(0, dagPath )

# create an MFn that can retrieve the matrix
dagNodefn = om.MFnDagNode( dagPath )
m = dagNodefn.transformationMatrix()

# decompose scale matrix from transform matrix
scaleX = om.MVector(m(0,0),m(0,1),m(0,2)).length()
scaleY = om.MVector(m(1,0),m(1,1),m(1,2)).length()
scaleZ = om.MVector(m(2,0),m(2,1),m(2,2)).length()
sValList = (scaleX,0,0,0, 0,scaleY,0,0, 0,0,scaleZ,0, 0,0,0,1 )
s = om.MMatrix()
om.MScriptUtil.createMatrixFromList( sValList, s )


# decompose rotate matrix
r = s.inverse() * m

# print scale matrix
printMatrix( r )
