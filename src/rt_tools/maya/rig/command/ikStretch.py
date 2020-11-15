"""
name: ikStretch.py

Author: Ehsan Hassani Moghaddam

History:
    05/20/17 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import attrLib
from ...lib import trsLib
from ...lib import keyLib


def run(startCtl, pvCtl, ctl, ikh, globalScaleAttr, name, stretchMode='scale'):
    """
    """
    # get ikh zero
    ikhZro = ikh.replace('IKH', 'ikh_ZRO')

    # dist
    dist = mc.createNode('distanceBetween', n=name+'_DST')
    mc.connectAttr(startCtl+'.worldMatrix', dist+'.inMatrix1')
    mc.connectAttr(ikhZro+'.worldMatrix', dist+'.inMatrix2')

    # joints
    jnts = mc.ikHandle(ikh, q=True, jointList=True)

    if len(jnts) == 1:
        # attr
        sa = attrLib.addFloat(ctl, 'stretch', min=0, max=1, dv=1)

        # length of limb
        endJnt = mc.listRelatives(jnts[0])[0]
        length = trsLib.getDistance(jnts[0], endJnt)

        # gs
        gs = mc.createNode('multiplyDivide', n=name+'GlobalScale_MDN')
        mc.setAttr(gs+'.operation', 2)
        mc.connectAttr(dist+'.distance', gs+'.input1X')
        mc.connectAttr(globalScaleAttr, gs+'.input2X')
        
        # stretch mdn
        mdn = mc.createNode('multiplyDivide', n=name+'stretch_MDN')
        mc.setAttr(mdn+'.operation', 2)
        mc.setAttr(mdn+'.input2X', length)
        mc.connectAttr(gs+'.outputX', mdn+'.input1X')

        # blendStretch
        blendStretch = mc.createNode('blendTwoAttr', n=name+'blendStretch_BTA')
        mc.setAttr(blendStretch+'.input[0]', 1)
        mc.connectAttr(mdn+'.outputX', blendStretch+'.input[1]')
        mc.connectAttr(sa, blendStretch+'.attributesBlender')

        connectStretch(stretchResultAttr=blendStretch+'.output',
                       nodes=[jnts[0]],
                       mode=stretchMode)
        
        return

    # attr
    sda = attrLib.addFloat(ctl, 'softDist', min=0.001)
    sa = attrLib.addFloat(ctl, 'stretch', min=0, max=1, dv=1)
    la = attrLib.addFloat(ctl, 'lockPV', min=0, max=1, dv=0)

    # total length of limbs
    totalLen = 0  # length of all joints together
    jntLens = []  # save joints lengths for later use
    for j in jnts:
        child = mc.listRelatives(j, children=True)[0]
        length = trsLib.getDistance(j, child)
        jntLens.append(length)
        totalLen += length

    # da
    da = mc.createNode('plusMinusAverage', n=name+'Da_PMA')
    mc.setAttr(da+'.input1D[0]', totalLen)
    mc.setAttr(da+'.operation', 2)
    mc.connectAttr(sda, da+'.input1D[1]')

    # gs
    gs = mc.createNode('multiplyDivide', n=name+'GlobalScale_MDN')
    mc.setAttr(gs+'.operation', 2)
    mc.connectAttr(dist+'.distance', gs+'.input1X')
    mc.connectAttr(globalScaleAttr, gs+'.input2X')

    # xMinusDa
    xMinusDa = mc.createNode('plusMinusAverage', n=name+'XMinusDa_PMA')
    mc.setAttr(xMinusDa+'.operation', 2)
    mc.connectAttr(gs+'.outputX', xMinusDa+'.input1D[0]')
    mc.connectAttr(da+'.output1D', xMinusDa+'.input1D[1]')

    # negMinusDa
    negMinusDa = mc.createNode('multiplyDivide', n=name+'NegMinusDa_MDN')
    mc.setAttr(negMinusDa+'.input2X', -1)
    mc.connectAttr(xMinusDa+'.output1D', negMinusDa+'.input1X')

    # divBySoft
    divBySoft = mc.createNode('multiplyDivide', n=name+'DivBySoft_MDN')
    mc.setAttr(divBySoft+'.operation', 2)
    mc.connectAttr(negMinusDa+'.outputX', divBySoft+'.input1X')
    mc.connectAttr(sda, divBySoft+'.input2X')

    # powE
    powE = mc.createNode('multiplyDivide', n=name+'PowE_MDN')
    mc.setAttr(powE+'.operation', 3)
    mc.setAttr(powE+'.input1X', 2.7182)
    mc.connectAttr(divBySoft+'.outputX', powE+'.input2X')

    # oneMinusPowE
    oneMinusPowE = mc.createNode('plusMinusAverage', n=name+'OneMinusPowE_PMA')
    mc.setAttr(oneMinusPowE+'.operation', 2)
    mc.setAttr(oneMinusPowE+'.input1D[0]', 1)
    mc.connectAttr(powE+'.outputX', oneMinusPowE+'.input1D[1]')

    # softTimesSD
    softTimesSD = mc.createNode('multiplyDivide', n=name+'SoftTimesSD_MDN')
    mc.connectAttr(sda, softTimesSD+'.input1X')
    mc.connectAttr(oneMinusPowE+'.output1D', softTimesSD+'.input2X')

    # softPlusDa
    softPlusDa = mc.createNode('plusMinusAverage', n=name+'SoftPlusDa_PMA')
    mc.connectAttr(da+'.output1D', softPlusDa+'.input1D[0]')
    mc.connectAttr(softTimesSD+'.outputX', softPlusDa+'.input1D[1]')

    # daCnd
    daCnd = mc.createNode('condition', n=name+'da_CND')
    mc.connectAttr(gs+'.outputX', daCnd+'.firstTerm')
    mc.connectAttr(da+'.output1D', daCnd+'.secondTerm')
    mc.setAttr(daCnd+'.operation', 5)
    mc.connectAttr(gs+'.outputX', daCnd+'.colorIfTrueR')
    mc.connectAttr(softPlusDa+'.output1D', daCnd+'.colorIfFalseR')

    # ikMoveAmount
    ikMoveAmount = mc.createNode('plusMinusAverage', n=name+'IkMoveAmount_PMA')
    mc.setAttr(ikMoveAmount+'.operation', 2)
    mc.connectAttr(gs+'.outputX', ikMoveAmount+'.input1D[0]')
    mc.connectAttr(daCnd+'.outColorR', ikMoveAmount+'.input1D[1]')

    # stretch attr reverse
    stretchAttrRev = mc.createNode('reverse', n=name+'StretchAttr_REV')
    mc.connectAttr(sa, stretchAttrRev+'.inputX')

    # ikMoveSwtich
    ikMoveSwtich = mc.createNode('blendTwoAttr', n=name+'IkMoveSwtich_BTA')
    mc.setAttr(ikMoveSwtich+'.input[1]', 0)
    mc.connectAttr(ikMoveAmount+'.output1D', ikMoveSwtich+'.input[1]')
    mc.connectAttr(stretchAttrRev+'.outputX', ikMoveSwtich+'.attributesBlender')

    # aim ikh
    zro = mc.listRelatives(ikh, p=True)[0]
    mc.aimConstraint(startCtl, zro, aim=[0, 1, 0], u=[0, 1, 0])
    

    # stretch joints
    # ==========

    # softRatio
    softRatio = mc.createNode('multiplyDivide', n=name+'SoftRatio_MDN')
    mc.setAttr(softRatio+'.operation', 2)
    mc.connectAttr(gs+'.outputX', softRatio+'.input1X')
    mc.connectAttr(daCnd+'.outColorR', softRatio+'.input2X')

    # stretch
    stretch = mc.createNode('blendTwoAttr', n=name+'Stretch_BTA')
    mc.setAttr(stretch+'.input[0]', 1)
    mc.connectAttr(softRatio+'.outputX', stretch+'.input[1]')
    mc.connectAttr(sa, stretch+'.attributesBlender')

    # connect stretch result
    connectStretch(stretchResultAttr=stretch+'.output',
                   nodes=jnts,
                   mode=stretchMode)


    # lock pv
    # ==========

    # limb1Dist
    limb1Dist = mc.createNode('distanceBetween', n=name+'Limb1Dist_DST')
    mc.connectAttr(startCtl+'.worldMatrix', limb1Dist+'.inMatrix1')
    mc.connectAttr(pvCtl+'.worldMatrix', limb1Dist+'.inMatrix2')

    # limb1Gs
    limb1Gs = mc.createNode('multiplyDivide', n=name+'limb1GlobalScale_MDN')
    mc.setAttr(limb1Gs+'.operation', 2)
    mc.connectAttr(limb1Dist+'.distance', limb1Gs+'.input1X')
    mc.connectAttr(globalScaleAttr, limb1Gs+'.input2X')

    # limb2Dist
    limb2Dist = mc.createNode('distanceBetween', n=name+'Limb2Dist_DST')
    mc.connectAttr(pvCtl+'.worldMatrix', limb2Dist+'.inMatrix1')
    mc.connectAttr(ctl+'.worldMatrix', limb2Dist+'.inMatrix2')

    # limb2Gs
    limb2Gs = mc.createNode('multiplyDivide', n=name+'limb2GlobalScale_MDN')
    mc.setAttr(limb2Gs+'.operation', 2)
    mc.connectAttr(limb2Dist+'.distance', limb2Gs+'.input1X')
    mc.connectAttr(globalScaleAttr, limb2Gs+'.input2X')

    # limb1LockLen
    limb1LockLen = mc.createNode('multiplyDivide', n=name+'limb1LockLen_MDN')
    mc.setAttr(limb1LockLen+'.operation', 2)
    mc.connectAttr(limb1Gs+'.outputX', limb1LockLen+'.input1X')
    mc.setAttr(limb1LockLen+'.input2X', jntLens[0])

    # limb2LockLen
    limb2LockLen = mc.createNode('multiplyDivide', n=name+'limb2LockLen_MDN')
    mc.setAttr(limb2LockLen+'.operation', 2)
    mc.connectAttr(limb2Gs+'.outputX', limb2LockLen+'.input1X')
    mc.setAttr(limb2LockLen+'.input2X', jntLens[1])

    # limb1LockSwitch
    limb1LockSwitch = mc.createNode('blendTwoAttr', n=name+'limb1LockSwitch_BTA')
    mc.connectAttr(stretch+'.output', limb1LockSwitch+'.input[0]')
    mc.connectAttr(limb1LockLen+'.outputX', limb1LockSwitch+'.input[1]')
    mc.connectAttr(la, limb1LockSwitch+'.attributesBlender')

    # limb2LockSwitch
    limb2LockSwitch = mc.createNode('blendTwoAttr', n=name+'limb2LockSwitch_BTA')
    mc.connectAttr(stretch+'.output', limb2LockSwitch+'.input[0]')
    mc.connectAttr(limb2LockLen+'.outputX', limb2LockSwitch+'.input[1]')
    mc.connectAttr(la, limb2LockSwitch+'.attributesBlender')

    # connect pv lock stretch result
    connectStretch(stretchResultAttr=limb1LockSwitch+'.output',
                   nodes=jnts[0:2],
                   mode=stretchMode)

    # noSoftWhenLock
    noSoftWhenLock = mc.createNode('multiplyDivide', n=name+'noSoftWhenLock_MDN')
    mc.setAttr(noSoftWhenLock+'.operation', 2)
    mc.connectAttr(limb2Gs+'.outputX', noSoftWhenLock+'.input1X')
    mc.setAttr(noSoftWhenLock+'.input2X', jntLens[1])

    # lockPV attr reverse
    lockPVAttrRev = mc.createNode('reverse', n=name+'lockPVAttrRev_REV')
    mc.connectAttr(la, lockPVAttrRev+'.inputX')

    # noIkMoveWhenLockPV
    noIkMoveWhenLockPV = mc.createNode('blendTwoAttr', n=name+'noIkMoveWhenLockPV_BTA')
    mc.setAttr(noIkMoveWhenLockPV+'.input[0]', 0)
    mc.connectAttr(ikMoveSwtich+'.output', noIkMoveWhenLockPV+'.input[1]')
    mc.connectAttr(lockPVAttrRev+'.outputX', noIkMoveWhenLockPV+'.attributesBlender')

    # ikMove towards upper limb to prevent sudden straightening of limbs
    mc.connectAttr(noIkMoveWhenLockPV+'.output', ikh+'.translateY')


def connectStretch(stretchResultAttr, nodes, axes='x', mode='scale'):
    if mode == 'scale':
        for node in nodes:
            mc.connectAttr(
                stretchResultAttr, '{}.s{}'.format(node, axes), f=True)

    elif mode == 'translate':
        lastChild = mc.listRelatives(nodes[-1], type='joint')[0]
        nodes = nodes[1:] + [lastChild]
        for node in nodes:
            defaultDrivenVal = mc.getAttr('{}.t{}'.format(node, axes))
            attrLib.disconnectAttr('{}.t{}'.format(node, axes))
            keyLib.setDriven(drvr=stretchResultAttr,
                          drvn='{}.t{}'.format(node, axes),
                          drvrValues=(1.0, 100),
                          drvnValues=(defaultDrivenVal, defaultDrivenVal*100))
