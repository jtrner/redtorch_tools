import maya.cmds as mc

from ...lib import connect
from ...lib import jntLib

reload(jntLib)
reload(connect)

def run(jntBaseName='name', jntAmount=3, jntRadius=1, locSize=1, rotationFollow = False):
    curveSelected = mc.ls(sl=True)

    shapeNode = mc.listRelatives(curveSelected[0], shapes=True)
    type = mc.nodeType(shapeNode)
    # if type != 'nurbsCurve':
    #     mc.error('you should select a curve ')

    allJnts = mc.createNode('transform', name = jntBaseName + '_allJnts_GRP')
    locSize = float(locSize)
    jntRadius = float(jntRadius)
    jntAmount = int(jntAmount)
    for iter in range(0, jntAmount):
        jointName = jntBaseName + "_" + str(iter + 1).zfill(3) + '_JNT'
        if jntAmount == 1:
            uValue = 0.5
        else:
            uValue = 1.0 / (jntAmount - 1.0) * iter

        mc.select(cl=True)
        mc.joint(n=jointName, rad=jntRadius)
        jntGrp = jntLib.groupJntHierachy(jointName, locSize)[0]
        connect.motionPath(jntGrp, curveSelected, uValue)
        if not rotationFollow:
            for attr in ['.rx', '.ry' , '.rz']:
                mc.delete(jntGrp + attr, icn=True)
        mc.parent(jntGrp,allJnts)
        mc.setAttr(jntGrp +  '.inheritsTransform' , 0)
    mc.parent(curveSelected, allJnts)