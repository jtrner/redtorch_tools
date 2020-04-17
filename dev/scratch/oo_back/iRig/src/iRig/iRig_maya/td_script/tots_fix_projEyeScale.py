import pymel.core as pm
import maya.cmds as cmds


def fix(self):
    for side in ['L_', 'R_']:
        prnt = side+'Eye_Proj_Jnt'
        proj = side+'Eye_Projection_3DPlace'
        scaled = side+'Eye_Projection_3DPlace_Cons'
        zero = side+'Eye_Projection_3DPlace_Zero'

        if not cmds.objExists(zero):
            print "butts"
            if cmds.objExists(side+'Eye_Proxy_Jnt'):
                prnt = side+'Eye_Proxy_Jnt'

                zero = cmds.createNode('transform', name=zero, parent=prnt)

                cmds.setAttr(zero+'.translateX', 0)
                cmds.setAttr(zero+'.translateY', 0)
                cmds.setAttr(zero+'.translateZ', 0)
                cmds.setAttr(zero+'.scaleX', 1)
                cmds.setAttr(zero+'.scaleY', 1)
                cmds.setAttr(zero+'.scaleZ', 1)

                temp = cmds.orientConstraint(proj, zero, maintainOffset=False)
                cmds.delete(temp)

                cmds.parent(proj, prnt)
                cmds.parent(scaled, zero)
                cmds.parent(proj, scaled)
                if cmds.objExists(side+'Eye_Projection_3DPlace_parentConstraint1'):
                    cmds.delete(side+'Eye_Projection_3DPlace_parentConstraint1')



