from maya import cmds 
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import math



sel = cmds.ls(sl = 1)

start = cmds.xform('joint1',q= 1 ,ws = 1,t =1 )
mid = cmds.xform('joint2' ,q= 1 ,ws = 1,t =1 )
end = cmds.xform('joint3' ,q= 1 ,ws = 1,t =1 )

startV = om2.MVector(start)
midV = om2.MVector(mid)
endV = om2.MVector(end)

startEnd = endV - startV

startMid = midV - startV

dotP = startMid * startEnd
proj = float(dotP) / float(startEnd.length())
startEndN = startEnd.normal()
projV = startEndN * proj

#projV2 = dotP * startEndN
#projV2 = projV2/startEnd.length()
#another way for finding project vector 
#cmds.xform('locator1' ,ws = 1,t = projV2 )



arrowV = startMid - projV

arrowV*= 0.8
finalV = arrowV + midV
cmds.xform('locator3' ,ws = 1,t = finalV )
#rotation
cross1 = startEnd ^ startMid
cross1.normalize()

cross2 = cross1 ^ arrowV
cross2.normalize()
arrowV.normalize()

matrixV = [arrowV.x , arrowV.y , arrowV.z , 0 ,
cross1.x ,cross1.y , cross1.z , 0 ,
cross2.x , cross2.y , cross2.z , 0,
0,0,0,1]

matrixM = om.MMatrix()

om.MScriptUtil.createMatrixFromList(matrixV , matrixM)
matrixFn = om.MTransformationMatrix(matrixM)

#matrixM2 = om2.MMatrix(matrixV)
#rot = matrixFn.eulerRotation()
#matrixFn2 = om2.MTransformationMatrix(matrixM2)
#rot2 = matrixFn2.rotation()
#print(rot2)
#finding the euler rotaion in maya api 2 ^^^


loc = 'locator2'
cmds.xform(loc , ws =1 , t= (finalV))
print(rot.y * 180/math.pi)# converting radian to degree

cmds.xform ( loc , ws = 1 , rotation = ((rot.x * 180/math.pi),
                                        (rot.y * 180/math.pi),
                                        (rot.z * 180/math.pi)))
                                        
                                        
                                        