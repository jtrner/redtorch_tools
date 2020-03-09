import maya.cmds as mc

import control
import transform
import mCurve


def curveLiveAttach(drvr, drvn, curve, name):
    curveShape = mCurve.getShapes(curve)[0]
    mop = mc.createNode('motionPath', n=name+'_mop')
    
    mc.connectAttr(mop+'.rotateX', drvn+'.rotateX')
    mc.connectAttr(mop+'.rotateY', drvn+'.rotateY')
    mc.connectAttr(mop+'.rotateZ', drvn+'.rotateZ')
    mc.connectAttr(mop+'.xCoordinate', drvn+'.translateX')
    mc.connectAttr(mop+'.yCoordinate', drvn+'.translateY')
    mc.connectAttr(mop+'.zCoordinate', drvn+'.translateZ')

    mc.connectAttr(curveShape+'.worldSpace[0]', mop+'.geometryPath')


    poc = mc.createNode('nearestPointOnCurve', n=name+'_mop')
    loc = mc.spaceLocator(n=name+'_world_loc')[0]
    mc.delete(mc.parentConstraint(drvr, loc))
    mc.parent(loc, drvr)
    locShape = mc.listRelatives(loc, s=True)[0]
    mc.setAttr(locShape+'.localScale', 0.1, 0.1, 0.1)

    mc.connectAttr(curveShape+'.worldSpace[0]', poc+'.inputCurve')
    mc.connectAttr(locShape+'.worldPosition', poc+'.inPosition')
    mc.connectAttr(poc+'.parameter', mop+'.uValue')

    return loc, mop, poc


def surfaceLiveAttach(drvr, drvn, surf, name):
    surfShape = transform.getShapes(surf)[0]
    flc = mc.createNode('follicle', n=name+'_flc')
    
    mc.connectAttr(flc+'.outRotateX', drvn+'.rotateX')
    mc.connectAttr(flc+'.outRotateY', drvn+'.rotateY')
    mc.connectAttr(flc+'.outRotateZ', drvn+'.rotateZ')
    mc.connectAttr(flc+'.outTranslateX', drvn+'.translateX')
    mc.connectAttr(flc+'.outTranslateY', drvn+'.translateY')
    mc.connectAttr(flc+'.outTranslateZ', drvn+'.translateZ')

    mc.connectAttr(surfShape+'.local', flc+'.inputSurface')
    mc.connectAttr(surfShape+'.worldMatrix[0]', flc+'.inputWorldMatrix')


    cps = mc.createNode('closestPointOnSurface', n=name+'_flc')
    loc = mc.spaceLocator(n=name+'_world_loc')[0]
    mc.hide(loc)
    mc.delete(mc.parentConstraint(drvr, loc))
    mc.parent(loc, drvr)
    locShape = mc.listRelatives(loc, s=True)[0]
    mc.setAttr(locShape+'.localScale', 0.1, 0.1, 0.1)

    mc.connectAttr(surfShape+'.worldSpace[0]', cps+'.inputSurface')
    mc.connectAttr(locShape+'.worldPosition', cps+'.inPosition')
    mc.connectAttr(cps+'.parameterU', flc+'.parameterU')
    mc.connectAttr(cps+'.parameterV', flc+'.parameterV')


def jntOnNode(node, name):
    jnt = mc.joint(node, n=name)
    mc.delete(mc.parentConstraint(node, jnt))
    return jnt


def rigCrvs():
    ver_crvs = ['l_inn_brow_crv',
                'l_mid_brow_crv',
                'l_out_brow_crv']
    
    hor_crv = 'l_hor_brow_crv'

    locs = ['l_inn_brow_loc',
            'l_mid_brow_loc',
            'l_out_brow_loc']

    for ver_crv, loc in zip(ver_crvs, locs):

        ctl = control.bundle(ver_crv.replace('_crv', ''),
                             shape='cube',
                             matchPose=loc,
                             scale=0.03)
        
        ver_jnt = mc.joint(None, n=loc.replace('_loc', '_ver_jnt'))
        transform.matchPose(ver_jnt, loc)
        ver_grp = mc.createNode('transform', n=loc.replace('_loc','_ver_grp'))
        curveLiveAttach(drvr=ctl, drvn=ver_grp, curve=ver_crv, name=ver_jnt)

        hor_jnt = mc.joint(None, n=loc.replace('_loc', '_hor_jnt'))
        transform.matchPose(hor_jnt, loc)
        hor_grp = mc.createNode('transform', n=loc.replace('_loc', '_hor_grp'))
        curveLiveAttach(drvr=ctl, drvn=hor_grp, curve=hor_crv, name=hor_jnt)


def main():
    surface = 'r_brow_srf'
    locs = mc.ls('r_???_brow_loc')

    for loc in locs:
        ctl = loc.replace('_loc', '_ctrl')
        # ctl = control.bundle(loc.replace('_loc', ''),
        #                      shape='cube',
        #                      matchPose=loc,
        #                      scale=0.03)
        
        surfaceLiveAttach(drvr=ctl, drvn=loc, surf=surface, name=ctl)
        jnt = jntOnNode(loc, name=loc.replace('_loc', '_jnt'))
        # twstJnt = jntOnNode(loc, name=loc.replace('_loc', '_twist_jnt'))
