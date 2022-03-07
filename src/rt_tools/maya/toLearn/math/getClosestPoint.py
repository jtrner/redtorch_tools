#create an MFnMesh for the selected mesh
obj = cmds.ls(sl = True)[0]
selection_list = om.MSelectionList()
selection_list.add(obj)
print selection_list
obj= om.MObject()
dpath= om.MDagPath()
dpath= selection_list.getDagPath(0)
MObject=om.MFnMesh(dpath)

#get meshs transformation matrix
MMatrix =  dpath.inclusiveMatrix()

#calculate and display closest point
point=om.MPoint()
point = MMatrix*point
MPoint = MObject.getClosestPoint (point, 4)	
MPoint= MPoint[0]
displayedCurve = cmds.curve( p=[(0, 0, 0), (MPoint[0],MPoint[1],MPoint[2])] )