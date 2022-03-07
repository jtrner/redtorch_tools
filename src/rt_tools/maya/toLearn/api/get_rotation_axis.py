import maya.cmds as mc
import maya.api.OpenMaya as om


ringMattix = om.MMatrix(mc.xform('ring', q=1, ws=1, m=1))
bellMatrix = om.MMatrix(mc.xform('bell', q=1, ws=1, m=1))
print(ringMattix)
print(bellMatrix)
ring_y_axis = om.MVector([ringMattix.getElement(1,0), 
                          ringMattix.getElement(1,1), 
                          ringMattix.getElement(1,2)])
print(ring_y_axis)      

