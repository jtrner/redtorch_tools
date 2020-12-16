import maya.cmds as mc

from ....lib import crvLib
from ....lib import jntLib
from ....lib import connect
from ....lib import attrLib
from ....lib import trsLib
from ....lib import strLib
from ....lib import deformLib
from ....lib import control

reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)

def createCtlPlaceMent(name = '', parent = ''):
    squashMakro = mc.createNode('transform', name = name + 'MouthSquashMAKRO_GRP', p = parent)
    jntCtlLoc = mc.createNode('transform', name = name + 'JNTCtrl_LOC', p = squashMakro)
    jntCtlLocShape = mc.createNode('locator', name = name + 'JNTCtrlShape_LOC', p = jntCtlLoc)
    return jntCtlLoc


def createRollMod(name = '', parent = '', up = True):
    mult = [1, -1][up == True]
    jntRollLoc = mc.createNode('transform', name=name + 'JNTRoll_LOC', p=parent)
    jntRollLocShape = mc.createNode('locator', name=name + 'JNTRollShape_LOC', p=jntRollLoc)
    mc.setAttr(jntRollLoc + '.tz',  0.3)
    jntMidMod = mc.createNode('transform', name=name + 'JNTMidModify_GRP', p=jntRollLoc)
    mc.setAttr(jntMidMod + '.tz', 1)
    mc.setAttr(jntMidMod + '.ty', mult * 0.5)
    jntMidLoc = mc.createNode('transform', name=name + 'JNTMid_LOC', p=jntMidMod)
    jntMidLocShape = mc.createNode('locator', name=name + 'JNTMidShape_LOC', p=jntMidLoc)
    jntMidMod = mc.createNode('transform', name=name + 'JNTMidModify_GRP', p=jntRollLoc)
    midFlippedMod = mc.createNode('transform', name = name + 'JNTMidFlippedModify_GRP', p = jntMidLoc)
    mc.setAttr(midFlippedMod + '.sx', -1)
    jntMidFlippedLoc = mc.createNode('transform', name=name + 'JNTMidFlipped_LOC', p=midFlippedMod)
    jntMidFlippedLocShape = mc.createNode('locator', name=name + 'JNTMidFlippedShape_LOC', p=jntMidFlippedLoc)

    return jntRollLoc, jntMidLoc



def locOnCrv(name = '', parent = '', numLocs = 3, crv = '',
             upCurve = '', paramStart = 0.5,paramEnd = 0.5, upAxis = 'y', posJnts = ''):
    param = paramStart
    tempList = []
    for i in range(numLocs):
        loc = mc.createNode('transform', name = name + '{}'.format(i), p = parent)
        pos = mc.xform(posJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = crv, upCurve = upCurve,param = param, upAxis = upAxis)
        param -= paramEnd
        tempList.append(loc)
    return tempList

def createLocsJntDriver(name = '', parent = '',jntSnap = ''):
    midOrLoc = mc.createNode('transform', name=name.split('R_')[-1] + 'MidOrient_LOC', p=parent)
    midOrShape = mc.createNode('locator', name=name + 'MidOrientShape_LOC', p=midOrLoc)
    trsLib.match(midOrLoc, t = jntSnap)
    mc.makeIdentity(midOrLoc, apply = True, t = True, r = True, s = True)

    secOrLoc = mc.createNode('transform', name=name + 'SecondaryOrient_LOC', p=parent)
    secOrLocShape = mc.createNode('locator', name=name + 'SecondaryOrientShape_LOC', p=secOrLoc)
    trsLib.match(secOrLoc, t = jntSnap)
    mc.makeIdentity(secOrLoc, apply = True, t = True, r = True, s = True)
    mc.setAttr(secOrLoc + '.tx', -0.7)
    mc.setAttr(secOrLoc + '.tz', -1.2)

    outOrLoc = mc.createNode('transform', name=name + 'OutOrient_LOC', p=parent)
    outOrLocShape = mc.createNode('locator', name=name + 'OutOrientShape_LOC', p=outOrLoc)
    trsLib.match(outOrLoc, t = jntSnap)
    mc.makeIdentity(outOrLoc, apply = True, t = True, r = True, s = True)
    mc.setAttr(outOrLoc + '.tx', -1)
    mc.setAttr(outOrLoc + '.tz', -1.2)

    cornerOrLoc = mc.createNode('transform', name=name + 'CornerOrient_LOC', p=parent)
    cornerOrLocShape = mc.createNode('locator', name=name + 'CornerOrientShape_LOC', p=cornerOrLoc)
    trsLib.match(cornerOrLoc, t = jntSnap)
    mc.makeIdentity(cornerOrLoc, apply = True, t = True, r = True, s = True)
    mc.setAttr(cornerOrLoc + '.tx', -2)
    mc.setAttr(cornerOrLoc + '.tz', -1.2)
    return midOrLoc, secOrLoc, outOrLoc, cornerOrLoc

def createZipperJnts(name = '', crv = '',upCurve = '' ,posJnts = '', parent = '', jntParent = '', up = True):
    ZipperTargetLoc = mc.createNode('transform', name = name + 'ZipperTargetLoc_GRP', p = parent)

    tempList = locOnCrv(name = 'result', parent = ZipperTargetLoc, numLocs = 9, crv = crv,
                 upCurve = upCurve, paramStart =0.97 ,paramEnd = 0.118, upAxis = 'y', posJnts = posJnts)
    for i in range(9):
        trsLib.match(posJnts[i-1], tempList[i-1])
        mc.makeIdentity(posJnts[i-1], apply = True, t = True, r = True, s = True)

    tempList[0] = mc.rename(tempList[0], 'L_' + name + 'ZipOutTertiary_LOC')
    tempList[1] =mc.rename(tempList[1], 'L_' + name + 'ZipOutSecondary_LOC')
    tempList[2] =mc.rename(tempList[2],'L_' +  name + 'Out_RotDrive_LOC')
    tempList[3] =mc.rename(tempList[3], 'L_' + name + 'ZipMidSecondary_LOC')
    tempList[4] =mc.rename(tempList[4], 'C_' + name + 'DriverMid_LOC')
    tempList[5] =mc.rename(tempList[5], 'R_' + name + 'ZipMidSecondary_LOC')
    tempList[6] =mc.rename(tempList[6], 'R_' +name + 'ZipOut_LOC')
    tempList[7] =mc.rename(tempList[7], 'R_' +name + 'ZipOutSecondary_LOC')
    tempList[8] =mc.rename(tempList[8], 'R_' +name + 'ZipOutTertiary_LOC')

    posJnts[0] = mc.rename(posJnts[0], 'L_' + name + 'outTertiaryZip_JNT')
    posJnts[0] = posJnts[0].split('|')[-1]
    posJnts[1] = mc.rename(posJnts[1], 'L_' + name + 'outSecondaryZip_JNT')
    posJnts[1] = posJnts[1].split('|')[-1]
    posJnts[2] = mc.rename(posJnts[2], 'L_' + name + 'outZip_JNT')
    posJnts[2] = posJnts[2].split('|')[-1]
    posJnts[3] = mc.rename(posJnts[3], 'L_' + name + 'midSecondaryZip_JNT')
    posJnts[3] = posJnts[3].split('|')[-1]
    posJnts[4] = mc.rename(posJnts[4], 'C_' + name + 'midZip_JNT')
    posJnts[4] = posJnts[4].split('|')[-1]
    posJnts[5] = mc.rename(posJnts[5], 'R_' + name + 'midSecondaryZip_JNT')
    posJnts[5] = posJnts[5].split('|')[-1]
    posJnts[6] = mc.rename(posJnts[6], 'R_' + name + 'outZip_JNT')
    posJnts[6] = posJnts[6].split('|')[-1]
    posJnts[7] = mc.rename(posJnts[7], 'R_' + name + 'outSecondaryZip_JNT')
    posJnts[7] = posJnts[7].split('|')[-1]
    posJnts[8] = mc.rename(posJnts[8], 'R_' + name + 'outTertiaryZip_JNT')
    posJnts[8] = posJnts[8].split('|')[-1]


    outTerList= []
    BNDJNTS = []
    for i in (0,1,3,5,7,8):
        niceName = posJnts[i].split('_JNT')[0]
        outTer = mc.createNode('transform', name = niceName + 'Orient_GRP', p = jntParent)
        trsLib.match(outTer, posJnts[i])
        outTerList.append(outTer)
        outTerMode = mc.createNode('transform', name = niceName + 'Modify_GRP', p = outTer)
        outTerMode2 = mc.createNode('transform', name = niceName + 'Modify_GRP2', p = outTerMode)
        TerMode = mc.createNode('transform', name=niceName + 'Modify_LOC', p=outTerMode2)
        outModLocShape = mc.createNode('locator', name=niceName + 'ModifyShape_LOC', p= TerMode)
        bndJnt = mc.joint(TerMode, name = niceName + '_BND', rad = 0.2)
        terOrGrp = mc.createNode('transform', name = niceName + 'Orient2_GRP', p = outTerMode2)
        terModGrp = mc.createNode('transform', name = niceName + 'ModifyB_GRP', p = terOrGrp)
        outTerCtl,outTerCtlGrp = createTerCtl(name = niceName , parent = posJnts[i], up = up)
        mc.parent(outTerCtlGrp, terModGrp)
        mc.parent(posJnts[i], TerMode)
        BNDJNTS.append(bndJnt)
        if i in (1,7):
            outSecLoc = mc.createNode('transform', name=niceName + 'RotDrive_LOC',)
            trsLib.match(outSecLoc, t = bndJnt)
            outSecLocShape = mc.createNode('locator', name=niceName + 'RotDriveShape_LOC', p=outSecLoc)
            if i == 7:
                mc.setAttr(outSecLoc + '.ry', 180)
            mc.parent(outSecLoc, bndJnt)

    outBndList =  []
    for i in (2,4,6):
        niceName = posJnts[i].split('_JNT')[0]
        outBnd = mc.createNode('transform', name = niceName + 'OutBnd_GRP', p = jntParent)
        trsLib.match(outBnd, posJnts[i])
        outBndList.append(outBnd)
        outBndLoc = mc.createNode('transform', name=niceName + 'OutBnd_LOC', p=outBnd)
        outBndLocShape = mc.createNode('locator', name=niceName + 'OutBndShape_LOC', p= outBndLoc)
        bndJnt = mc.joint(outBnd, name = niceName + '_BND', rad = 0.2)
        BNDJNTS.append(bndJnt)
        mc.parent(posJnts[i], outBnd)


    return BNDJNTS, tempList, outTerList, outBndList


def createTerCtl(name = '', parent = '', side = 'C', up = True):

    mult = [-1, 1][up == True]
    ctl = control.Control(descriptor=name,
                          side=side,
                          orient=(0,0,mult * 1),
                          shape="triangle",
                          color=control.COLORS[side],
                          scale=[0.03, 0.03, 0.03],
                          moveShape=[0,mult * 0.5,0.5],
                          lockHideAttrs=['s'],
                          matchTranslate=parent,
                          matchRotate= parent)

    ctl.name = ctl.name.split('C_')[-1]

    return ctl.name,ctl.zro




def createRollHirarchy(name = '', parent = '', up = True ):
    mult = [-1, 1][up == True]
    ctlRollMod = mc.createNode('transform', name = name + 'ctlRollModify_GRP', p = parent)
    mc.setAttr(ctlRollMod + '.ty', 0.5)
    roll= mc.createNode('transform',  name = name + 'Roll_LOC', p = ctlRollMod)
    rollLocShape = mc.createNode('locator',  name = name + 'rollShape_LOC', p = roll)
    mc.setAttr(roll + '.tz', 2.5)
    if not up:
        mc.setAttr(roll + '.ty', -1)
    midMod = mc.createNode('transform', name=name + 'MidModify_GRP', p=roll)
    mc.setAttr(midMod + '.ty', -0.5)
    midLoc= mc.createNode('transform',  name = name + 'Mid_LOC', p = midMod)
    midLocShape = mc.createNode('locator',  name = name + 'MidShape_LOC', p = midLoc)
    flippedMod = mc.createNode('transform', name = name + 'localUpLipMidFlippedModify_GRP', p = midLoc)
    flippedLoc= mc.createNode('transform',  name = name + 'MidFlipped_LOC', p = flippedMod)
    mc.setAttr(flippedMod + '.sx', -1)
    flippedLocShape = mc.createNode('locator',  name = name + 'MidFlippedShape_LOC', p = flippedLoc)
    return  ctlRollMod


def createSideMainCtl(name = '', parent = '', snapJnt = '', side = 'L'):

    ctls = []
    ctlsGrp = []
    for i in range(2):
        ctl = control.Control(descriptor=name + '{}'.format(i),
                              side=side,
                              orient=(1,0,0),
                              shape="triangle",
                              color=control.SECCOLORS[side],
                              scale=[0.1, 0.1, 0.1],
                              lockHideAttrs=['s'],
                              matchTranslate=parent,
                              matchRotate = parent)

        ctls.append(ctl.name)
        ctlsGrp.append(ctl.zro)

    crvLib.scaleShape(curve=ctls[0], scale=(0.8, 0.8, 0.8))
    crvLib.scaleShape(curve=ctls[1], scale=(0.3, 0.3, 0.3))

    par = parent
    mult = [1, -1][side == 'R']
    for i in range(2):
        mc.setAttr(ctlsGrp[i] + '.ry', -80)
        mc.makeIdentity(ctlsGrp[i], apply=True, r=True, t=True)
        trsLib.match(ctlsGrp[i], par)
        mc.parent(ctlsGrp[i], par)
        mc.makeIdentity(ctlsGrp[i], apply=True, r=True, t=True)
        crvLib.moveShape(curve=ctls[i], move=(mult * 0.6, 0,  0.3))
        par = ctls[0]

    return ctls, ctlsGrp



def createMiddleMainCtl(name = '', parent = '', snapJnt = '', side = 'C',up = True):

    squashMakro = mc.createNode('transform', name = name + 'CtrlMouthSquashMAKRO_GRP',  p = parent)
    ctlOr = mc.createNode('transform', name = name + 'CtrlOrient_GRP',  p = squashMakro)

    mc.setAttr(ctlOr + '.tz', 2.5)
    if up:
        mc.setAttr(ctlOr + '.ty', 1)
    else:
        mc.setAttr(ctlOr + '.ty', -1)

    ctl = control.Control(descriptor=name,
                             side= side,
                             orient=(0, 0, 1),
                             shape="square",
                             color=control.COLORS[side],
                             scale=[2, 0.1, 1],
                             lockHideAttrs=['s'],
                             matchTranslate=ctlOr)
    mc.parent(ctl.zro, ctlOr)
    mc.makeIdentity(ctl.zro, apply = True, r = True, t = True)
    return ctl.name, ctl.zro

def createMouthCtl(name = '', parent = '', snapJnt = '', side = 'C'):

    ctl = control.Control(descriptor=name,
                             side= side,
                             orient=(0, 0, 1),
                             shape="square",
                             color=control.COLORS[side],
                             scale=[1, 0.2, 1],
                             lockHideAttrs=['s'],
                             matchTranslate=parent,
                             matchRotate= parent )

    mc.parent(ctl.zro, parent)
    mc.makeIdentity(ctl.zro, apply = True, r = True, t = True)

    return ctl.name, ctl.zro






def createJntAndParent(name = '',parent = '', side = 'C',up = True):
    outMod = mc.createNode('transform' , name = name + 'OutModify_GRP',p = parent)
    outMod2 = mc.createNode('transform' , name = name + 'OutModify2_GRP',p = outMod)
    outModLocTrans = mc.createNode('transform',  name = name + 'OutModify_LOC', p = outMod2)
    outModLocShape = mc.createNode('locator',  name = name + 'OutModifyShape_LOC', p = outModLocTrans)
    outerOr = mc.createNode('transform', name = name + 'OuterOrient_GRP', p = outModLocTrans)
    outerMod = mc.createNode('transform', name = name + 'OuterModify_GRP', p = outerOr)

    mult = [1, -1][up == False]
    ctl = control.Control(descriptor=name,
                             side='C',
                             shape="triangle",
                             orient = [0,0, mult],
                             color=control.SECCOLORS[side],
                             moveShape=[0, mult * 0.5 , 0.5],
                             scale=[0.05, 0.05, 0.05],
                             lockHideAttrs=['s'],
                             matchTranslate=parent)
    mc.parent(ctl.zro, outerMod)
    mc.makeIdentity(ctl.zro, apply = True, r = True, t = True)

    OutJnt = mc.joint(ctl.name, name = name + '_JNT', rad = 0.4)


    return ctl.name,ctl.zro,OutJnt

def createMainHierarchyJnts(name = '', parent = '', middle = False):
    if not middle:
        cornerMod = mc.createNode('transform' , name = name + 'CornerModify_GRP',p = parent)
        outModLocTrans = mc.createNode('transform',  name = name + 'OutModify_LOC', p = cornerMod)
        outModLocShape = mc.createNode('locator', name=name + 'OutModifyShape_LOC', p=outModLocTrans)
        return outModLocTrans, cornerMod

    else:
        mainMod = mc.createNode('transform' , name = name + 'MainModify_GRP',p = parent)
        outModLocTrans = mc.createNode('transform',  name = name + 'MainModify_LOC', p = mainMod)
        outModLocShape = mc.createNode('locator', name=name + 'ModifyShape_LOC', p=outModLocTrans)
        return  outModLocTrans, mainMod









