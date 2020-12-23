import maya.cmds as mc

from ....lib import crvLib
from ....lib import jntLib
from ....lib import connect
from ....lib import attrLib
from ....lib import trsLib
from ....lib import strLib
from ....lib import deformLib
from ....lib import control
from ....lib import keyLib


reload(keyLib)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)

def detachHead(geoName = '',edge = '',name = '', movement = 50):
    if edge:
        mc.select(edge)
    else:
        mc.ls(sl = True)
    mc.DetachComponent()
    mc.select(geoName)
    mc.polySeparate(n = name , ch = False)
    head = mc.duplicate(name)
    mc.select(name, r = True)
    mc.select(name + '1', add = True)
    mc.polyUnite(ch = False ,name = geoName, muv = 1)
    mc.select(geoName +'.vtx[:]')
    mc.polyMergeVertex(d = 0.01, am = True, ch = False)
    mc.select(cl = True)
    newName = mc.rename(head, name)
    mc.setAttr(newName + '.ty', movement)
    return newName

def createCtl(parent = '',side = 'L',scale = [1, 1, 1]):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,1,0),
                          shape="square",
                          color=control.SECCOLORS[side],
                          scale=scale,
                          moveShape=[0,0,0.7],
                          matchTranslate=parent,
                          matchRotate= parent)


    return ctl.name,ctl.zro


def locOnCrv(name = '', parent = '', numLocs = 3, crv = '',
             upCurve = '', paramStart = 0.5,paramEnd = 0.5, upAxis = 'y', posJnts = '',translate = False):
    param = paramStart
    tempList = []
    for i in range(numLocs):
        loc = mc.createNode('transform', name = name + '{}'.format(i), p = parent)
        pos = mc.xform(posJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = crv, upCurve = upCurve,param = param, upAxis = upAxis,translate = translate)
        param -= paramEnd
        tempList.append(loc)
    return tempList

def cheekRaiseHierarchy(name = '',parent = '',side = 'L', position= ''):
    cheekJntZ = mc.createNode('transform', name = side + '_cheeckRaiseJntZ',p = parent)
    cheekJntOri = mc.createNode('transform', name = side + '_cheekRaiseJntOri', p = cheekJntZ)
    trsLib.match(cheekJntOri, position)
    cheekJntMod = mc.createNode('transform', name = side + 'cheeckRaiseJntMod', p = cheekJntOri)
    return cheekJntMod,cheekJntZ

def sharpJntsHierarchy(name = '', parent = '',joint = '',middle = False):
    if middle:
        oriGrp = mc.createNode('transform', name = name + '_ori_GRP',p = parent)
        trsLib.match(oriGrp, joint)
        modGrp = mc.createNode('transform', name = name + '_mod_GRP', p = oriGrp)
        makroGrp = mc.createNode('transform', name = name + '_makro_GRP', p = modGrp)
        mc.parent(joint, makroGrp)
        makroGrp = makroGrp.split('|')[-1]
        return modGrp,makroGrp
    else:
        oriGrp = mc.createNode('transform', name = name + '_ori_GRP',p = parent)
        trsLib.match(oriGrp, joint)
        modGrp = mc.createNode('transform', name = name + '_mod_GRP', p = oriGrp)
        mc.parent(joint, modGrp)
        modGrp = modGrp.split('|')[-1]
        return modGrp

def createMiddleCtls(parent = '',side = 'L'):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,0,1),
                          shape="square",
                          color=control.SECCOLORS[side],
                          scale=[1, 0.2, 0.3],
                          moveShape=[0,0,0.5],
                          lockHideAttrs=['s'],
                          matchTranslate=parent,
                          matchRotate= parent)

    mc.parent(ctl.zro, parent)

    return ctl.name,ctl.zro

def createSecondaryCtls(parent = '',side = 'L',ctlPose = ''):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,0,1),
                          shape="triangle",
                          color=control.COLORS[side],
                          scale=[0.04, 0.04, 0.04],
                          moveShape=[0,0,0.3],
                          lockHideAttrs=['s'],
                          matchTranslate=ctlPose ,
                          matchRotate= ctlPose )


    mc.parent(ctl.zro, parent)

    return ctl.name,ctl.zro

def createCtlPlaceMent(name = '', parent = ''):
    squashMakro = mc.createNode('transform', name = name + 'MouthSquashMAKRO_GRP', p = parent)
    jntCtlLoc = mc.createNode('transform', name = name + 'JNTCtrl_LOC', p = squashMakro)
    jntCtlLocShape = mc.createNode('locator', name = name + 'JNTCtrlShape_LOC', p = jntCtlLoc)
    return jntCtlLoc, squashMakro


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
    ZipperTargetLoc = mc.createNode('transform', name = name + 'ZipperTargetloc_GRP', p = parent)

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
    locMods = []
    outTerCtls = []
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
        outTerCtls.append(outTerCtl)
        mc.parent(outTerCtlGrp, terModGrp)
        mc.parent(posJnts[i], TerMode)
        BNDJNTS.append(bndJnt)
        locMods.append(TerMode)
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


    return BNDJNTS, tempList, outTerList, outBndList,locMods,outTerCtls,posJnts


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
    return  ctlRollMod, roll, midLoc


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
    return ctl.name, ctl.zro, squashMakro

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


    return ctl.name,ctl.zro,OutJnt, outModLocTrans

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

def createNoseCtls(name = '', parent = '',mainSnap = '', cummelaSnap = '', leftSnap = '', rightSnap = '',side = 'C'):
    noseCtlOri = mc.createNode('transform', name = 'noseCtrlBaseori_GRP', p = parent)
    trsLib.match(noseCtlOri, mainSnap)
    noseCtlMakro = mc.createNode('transform', name = 'noseCtrlMAKRO_GRP', p = noseCtlOri)

    ctls = []
    ctlGrp = []
    for i in range(5):
        ctl = control.Control(descriptor=name + '{}'.format(i),
                                 side=side,
                                 shape="triangle",
                                 orient = [0,0, 1],
                                 color=control.SECCOLORS[side],
                                 moveShape=[0, 0 , 0],
                                 scale=[0.05, 0.05, 0.05],
                                 lockHideAttrs=[],
                                 matchTranslate=noseCtlMakro,
                                 matchRotate = noseCtlMakro)
        ctls.append(ctl.name)
        ctlGrp.append(ctl.zro)
    print(ctls)
    print(ctlGrp)
    noseCtl = mc.rename(ctls[0], 'nose_CTL')
    noseCtlModGrp = mc.rename(ctlGrp[0], 'noseCtlMod_GRP')
    mc.parent(noseCtlModGrp, noseCtlMakro)

    noseCtlBase = mc.rename(ctls[1], 'noseCtlBase_CTL')
    noseCtlBaseGrp = mc.rename(ctlGrp[1], 'noseCtrlBaseModctl_GRP')

    cumellaCtl = mc.rename(ctls[2], 'columella_CTL')
    cumellaCtlModGrp = mc.rename(ctlGrp[2], 'noseCtlMod_GRP')

    r_nostrilCtl = mc.rename(ctls[3], 'R_nostril_CTL')
    r_nostrilCtlGrp = mc.rename(ctlGrp[3], 'R_nostrilCtrlMod_GRP')

    l_nostrilCtl = mc.rename(ctls[4], 'L_nostril_CTL')
    l_nostrilCtlGrp = mc.rename(ctlGrp[4], 'L_nostrilCtrlMod_GRP')

    noseCtlBaseOriGrp = mc.createNode('transform', name = 'noseCtrlBaseOri_GRP', p = noseCtl)
    mc.move(0,0,1, noseCtlBaseOriGrp, r = True, ws =  True)
    noseCtlBaseModGrp = mc.createNode('transform', name = 'noseCtlBaseMod_GRP', p = noseCtlBaseOriGrp)
    trsLib.match(noseCtlBaseGrp, noseCtlBaseModGrp)
    mc.parent(noseCtlBaseGrp, noseCtlBaseModGrp)

    culumelCtlOriGrp = mc.createNode('transform', name = 'columellaCtrlOri_GRP', p = noseCtlBase)
    trsLib.match(culumelCtlOriGrp, cummelaSnap)
    trsLib.match(cumellaCtlModGrp, culumelCtlOriGrp)
    mc.parent(cumellaCtlModGrp,culumelCtlOriGrp)

    r_nostrilCtlOri = mc.createNode('transform', name = 'R_nostrilCtrlOri_GRP', p = noseCtlBase)
    trsLib.match(r_nostrilCtlOri, rightSnap)
    r_nostrilMakro = mc.createNode('transform', name = 'R_nostrilCtrlMAKRO_GRP' , p = r_nostrilCtlOri)
    trsLib.match(r_nostrilCtlGrp, r_nostrilMakro)
    mc.parent(r_nostrilCtlGrp,r_nostrilMakro)

    l_nostrilCtlOri = mc.createNode('transform', name = 'L_nostrilCtrlOri_GRP', p = noseCtlBase)
    trsLib.match(l_nostrilCtlOri, leftSnap)
    l_nostrilMakro = mc.createNode('transform', name = 'L_nostrilCtrlMAKRO_GRP' , p = l_nostrilCtlOri)
    trsLib.match(l_nostrilCtlGrp, l_nostrilMakro)
    mc.parent(l_nostrilCtlGrp,l_nostrilMakro)
    mc.move(0, -18, 0, noseCtlOri, r=True, ws=True)

    noseCtl = noseCtl.split('|')[-1]
    noseCtlBase = noseCtlBase.split('|')[-1]
    cumellaCtl = cumellaCtl.split('|')[-1]
    return noseCtl, noseCtlBase, cumellaCtl


def drivenCornerLip(leftUpCtl = '', leftLowCtl = '', rightUpCtl = '', rightLowCtl = '',
                        leftUpLoc = '', leftLowLoc = '', rightUpLoc = '', rightLowLoc = ''):
    # connect corner controls to the upCornerMod locators
    for i in [leftUpCtl,rightUpCtl]:
        attrLib.addFloat(i, ln = 'Z', dv = 0)
        attrLib.addFloat(i, ln = 'puff',min = -10, max = 10, dv = 0)
    pmas = []
    for i in [leftUpCtl,rightUpCtl]:
        pma = mc.createNode('plusMinusAverage', name = i + '_PMA')
        mc.connectAttr(i + '.Z', pma + '.input2D[1].input2Dx')
        pmas.append(pma)

    keyLib.setDriven(leftUpCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [-6], [-1.9], itt='spline',ott='spline')
    keyLib.setDriven(leftUpCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [0], [0], itt='auto',ott='auto')
    keyLib.setDriven(leftUpCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [15], [-4.702978], itt='spline',ott='spline')
    keyLib.setDriven(rightUpCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [-6], [1.9], itt='spline',ott='spline')
    keyLib.setDriven(rightUpCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [0], [0], itt='auto',ott='auto')
    keyLib.setDriven(rightUpCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [15], [4.702978], itt='spline',ott='spline')

    for i,s in zip([leftUpCtl,rightUpCtl],[leftUpLoc,rightUpLoc]):
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 's' for a in 'xyz']
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 'r' for a in 'xz']
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']

    keyLib.setDriven(leftUpCtl + '.translateX', leftUpLoc + '.ry', [-3], [6.640919], itt='spline', ott='spline')
    keyLib.setDriven(leftUpCtl + '.translateX', leftUpLoc + '.ry', [0], [0], itt='flat', ott='flat')
    keyLib.setDriven(leftUpCtl + '.translateX', leftUpLoc + '.ry', [6], [10], itt='spline', ott='spline')

    keyLib.setDriven(rightUpCtl + '.translateX', rightUpLoc + '.ry', [-3], [-6.640919], itt='spline', ott='spline')
    keyLib.setDriven(rightUpCtl + '.translateX', rightUpLoc + '.ry', [0], [0], itt='flat', ott='flat')
    keyLib.setDriven(rightUpCtl + '.translateX', rightUpLoc + '.ry', [6], [-10], itt='spline', ott='spline')
    animCurves = mc.listConnections(rightUpCtl, source=True, type="animCurve")
    animCurves2 = mc.listConnections(leftUpCtl, source=True, type="animCurve")
    for i in animCurves:
        mc.setAttr(i + '.preInfinity', 1)
        mc.setAttr(i + '.postInfinity', 1)
    for i in animCurves2:
        mc.setAttr(i + '.preInfinity', 1)
        mc.setAttr(i + '.postInfinity', 1)

    for i,s in zip(pmas,[leftUpLoc,rightUpLoc]):
        mc.connectAttr(i + '.output2D.output2Dx' , s + '.translateZ')

    # connect corner controls to the lowCornerMod locators
    for i in [leftLowCtl,rightLowCtl]:
        attrLib.addFloat(i, ln = 'Z', dv = 0)
        attrLib.addFloat(i, ln = 'puff',min = -10, max = 10, dv = 0)
    pmas = []
    for i in [leftLowCtl,rightLowCtl]:
        pma = mc.createNode('plusMinusAverage', name = i + '_PMA')
        mc.connectAttr(i + '.Z', pma + '.input2D[1].input2Dx')
        pmas.append(pma)

    keyLib.setDriven(leftLowCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [-6], [-1.9], itt='spline',ott='spline')
    keyLib.setDriven(leftLowCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [0], [0], itt='auto',ott='auto')
    keyLib.setDriven(leftLowCtl + '.translateX', pmas[0] + '.input2D[0].input2Dx', [15], [-4.702978], itt='spline',ott='spline')

    keyLib.setDriven(rightLowCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [-6], [1.9], itt='spline',ott='spline')
    keyLib.setDriven(rightLowCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [0], [0], itt='auto',ott='auto')
    keyLib.setDriven(rightLowCtl + '.translateX', pmas[1] + '.input2D[0].input2Dx', [15], [4.702978], itt='spline',ott='spline')

    for i,s in zip([leftLowCtl,rightLowCtl],[leftLowLoc,rightLowLoc]):
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 's' for a in 'xyz']
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 'r' for a in 'xz']
        [mc.connectAttr(i + '.{}{}'.format(t, a),s + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']
    keyLib.setDriven(leftLowCtl+ '.translateX', leftLowLoc+ '.ry', [-3], [6.640919], itt='spline',ott='spline')
    keyLib.setDriven(leftLowCtl + '.translateX', leftLowLoc + '.ry', [0], [0], itt='flat',ott='flat')
    keyLib.setDriven(leftLowCtl+ '.translateX', leftLowLoc+ '.ry', [6], [10], itt='spline',ott='spline')

    keyLib.setDriven(rightLowCtl + '.translateX', rightLowLoc+ '.ry', [-3], [-6.640919], itt='spline',ott='spline')
    keyLib.setDriven(rightLowCtl + '.translateX', rightLowLoc + '.ry', [0], [0], itt='spline',ott='spline')
    keyLib.setDriven(rightLowCtl+ '.translateX', rightLowLoc+ '.ry', [6], [-10], itt='spline',ott='spline')
    animCurves = mc.listConnections(rightLowCtl , source=True, type="animCurve")
    animCurves2 = mc.listConnections(leftLowCtl , source=True, type="animCurve")
    for i in animCurves:
        mc.setAttr(i + '.preInfinity', 1)
        mc.setAttr(i + '.postInfinity', 1)
    for i in animCurves2:
        mc.setAttr(i + '.preInfinity', 1)
        mc.setAttr(i + '.postInfinity', 1)

    for i,s in zip(pmas,[leftLowLoc,rightLowLoc]):
        mc.connectAttr(i + '.output2D.output2Dx' , s + '.translateZ')



def connectBndZip(locali = True,leftLowCornerCtl = '',rightLowCornerCtl = '',lowZipJnts = '', lowMicroJnts = '',
                  leftUpCornerCtl = '',rightUpCornerCtl = '', upZipJnts = '', upMicroJnts = ''):
    if locali:
        name = 'local'
    else:
        name = ''
    attrLib.addFloat(leftUpCornerCtl, ln='zip', min=0, dv=0)
    attrLib.addFloat(rightUpCornerCtl, ln='zip', min=0, dv=0)
    upmults = []
    for i in upZipJnts:
        mult = mc.createNode('multiplyDivide', name=name + i + '_MDN')
        upmults.append(mult)
    mult = mc.createNode('multiplyDivide', name=name + 'R_outTertiaryZip_MD1')
    upmults.append(mult)
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftUpCornerCtl + '.zip', upmults[0] + '.' + j, [0, 11], [0, 1], itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftUpCornerCtl + '.zip', upmults[1] + '.' + j, [0, 4, 8, 14], [0, 0.2, 0.6, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftUpCornerCtl + '.zip', upmults[2] + '.' + j, [0, 3, 17], [0, 0, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftUpCornerCtl + '.zip', upmults[3] + '.' + j, [0, 6, 9, 18], [0, 0.03, 0.2, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftUpCornerCtl + '.zip', upmults[4] + '.' + j, [4, 8, 20], [0, 0.05, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightUpCornerCtl + '.zip', upmults[5] + '.' + j, [4, 8, 20], [0, 0.05, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightUpCornerCtl + '.zip', upmults[6] + '.' + j, [0, 6, 9, 18], [0, 0.03, 0.2, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightUpCornerCtl + '.zip', upmults[7] + '.' + j, [0, 3, 17], [0, 0, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightUpCornerCtl + '.zip', upmults[8] + '.' + j, [0, 4, 8, 14], [0, 0.2, 0.6, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightUpCornerCtl + '.zip', upmults[9] + '.' + j, [0, 11], [0, 1], itt='auto', ott='auto')

    a = ['tx', 'ty', 'tz']
    b = ['input1X', 'input1Y', 'input1Z']
    c = ['input2X', 'input2Y', 'input2Z']
    upZipTemp = []
    upMultTemp = []
    for i in range(10):
        if i in [5]:
            continue
        uplip = upZipJnts[i - 1]
        upZipTemp.append(uplip)
    for i in range(10):
        if i in [5, 6]:
            continue
        upmult = upmults[i - 1]
        upMultTemp.append(upmult)
    for i in range(8):
        for j, k in zip(a, b):
            mc.connectAttr(upZipTemp[i] + '.' + j, upMultTemp[i] + '.' + k)
    for j, k in zip(a, b):
        mc.connectAttr(upZipJnts[4] + '.' + j, upmults[4] + '.' + k)
        mc.connectAttr(upZipJnts[4] + '.' + j, upmults[5] + '.' + k)
    l_mult = mc.createNode('multiplyDivide', name=name + 'L_midZipHalf_MDN')
    r_mult = mc.createNode('multiplyDivide', name=name + 'R_midZipHalf_MDN')

    for i in c:
        mc.setAttr(l_mult + '.' + i, 0.5)
        mc.setAttr(r_mult + '.' + i, 0.5)

    mc.connectAttr(upmults[4] + '.output', l_mult + '.input1')
    mc.connectAttr(upmults[5] + '.output', r_mult + '.input1')

    upMidZipPls = mc.createNode('plusMinusAverage', name=name + 'upmidZip_PMA')
    mc.connectAttr(l_mult + '.output', upMidZipPls + '.input3D[0]')
    mc.connectAttr(r_mult + '.output', upMidZipPls + '.input3D[1]')
    mc.connectAttr(upMultTemp[0] + '.output', upMicroJnts[5] + '.translate')
    mc.connectAttr(upMultTemp[1] + '.output', upMicroJnts[0] + '.translate')
    mc.connectAttr(upMultTemp[2] + '.output', upMicroJnts[1] + '.translate')
    mc.connectAttr(upMultTemp[3] + '.output', upMicroJnts[6] + '.translate')
    mc.connectAttr(upMultTemp[4] + '.output', upMicroJnts[2] + '.translate')
    mc.connectAttr(upMultTemp[5] + '.output', upMicroJnts[3] + '.translate')
    mc.connectAttr(upMultTemp[6] + '.output', upMicroJnts[8] + '.translate')
    mc.connectAttr(upMultTemp[7] + '.output', upMicroJnts[4] + '.translate')

    mc.connectAttr(upMidZipPls + '.output3D', upMicroJnts[7] + '.translate')

    attrLib.addFloat(leftLowCornerCtl, ln='zip', min=0, dv=0)
    attrLib.addFloat(rightLowCornerCtl, ln='zip', min=0, dv=0)
    upmults = []
    for i in lowZipJnts:
        mult = mc.createNode('multiplyDivide', name=name + i + '_MDN')
        upmults.append(mult)
    mult = mc.createNode('multiplyDivide', name=name + 'R_outTertiaryZip_MD1')
    upmults.append(mult)
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftLowCornerCtl + '.zip', upmults[0] + '.' + j, [0, 11], [0, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftLowCornerCtl + '.zip', upmults[1] + '.' + j, [0, 4, 8, 14], [0, 0.2, 0.6, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftLowCornerCtl + '.zip', upmults[2] + '.' + j, [0, 3, 17], [0, 0, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftLowCornerCtl + '.zip', upmults[3] + '.' + j, [0, 6, 9, 18], [0, 0.03, 0.2, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(leftLowCornerCtl + '.zip', upmults[4] + '.' + j, [4, 8, 20], [0, 0.05, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightLowCornerCtl + '.zip', upmults[5] + '.' + j, [4, 8, 20], [0, 0.05, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightLowCornerCtl + '.zip', upmults[6] + '.' + j, [0, 6, 9, 18], [0, 0.03, 0.2, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightLowCornerCtl + '.zip', upmults[7] + '.' + j, [0, 3, 17], [0, 0, 1], itt='auto',
                         ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightLowCornerCtl + '.zip', upmults[8] + '.' + j, [0, 4, 8, 14], [0, 0.2, 0.6, 1],
                         itt='auto', ott='auto')
    for j in ['input2X', 'input2Y', 'input2Z']:
        keyLib.setDriven(rightLowCornerCtl + '.zip', upmults[9] + '.' + j, [0, 11], [0, 1], itt='auto',
                         ott='auto')

    a = ['tx', 'ty', 'tz']
    b = ['input1X', 'input1Y', 'input1Z']
    c = ['input2X', 'input2Y', 'input2Z']
    upZipTemp = []
    upMultTemp = []
    for i in range(10):
        if i in [5]:
            continue
        uplip = lowZipJnts[i - 1]
        upZipTemp.append(uplip)
    for i in range(10):
        if i in [5, 6]:
            continue
        upmult = upmults[i - 1]
        upMultTemp.append(upmult)
    for i in range(8):
        for j, k in zip(a, b):
            mc.connectAttr(upZipTemp[i] + '.' + j, upMultTemp[i] + '.' + k)
    for j, k in zip(a, b):
        mc.connectAttr(lowZipJnts[4] + '.' + j, upmults[4] + '.' + k)
        mc.connectAttr(lowZipJnts[4] + '.' + j, upmults[5] + '.' + k)
    l_mult = mc.createNode('multiplyDivide', name=name + 'L_midZipHalf_MDN')
    r_mult = mc.createNode('multiplyDivide', name=name + 'R_midZipHalf_MDN')

    for i in c:
        mc.setAttr(l_mult + '.' + i, 0.5)
        mc.setAttr(r_mult + '.' + i, 0.5)

    mc.connectAttr(upmults[4] + '.output', l_mult + '.input1')
    mc.connectAttr(upmults[5] + '.output', r_mult + '.input1')

    upMidZipPls = mc.createNode('plusMinusAverage', name=name + 'upmidZip_PMA')
    mc.connectAttr(l_mult + '.output', upMidZipPls + '.input3D[0]')
    mc.connectAttr(r_mult + '.output', upMidZipPls + '.input3D[1]')
    mc.connectAttr(upMultTemp[0] + '.output', lowMicroJnts[5] + '.translate')
    mc.connectAttr(upMultTemp[1] + '.output', lowMicroJnts[0] + '.translate')
    mc.connectAttr(upMultTemp[2] + '.output', lowMicroJnts[1] + '.translate')
    mc.connectAttr(upMultTemp[3] + '.output', lowMicroJnts[6] + '.translate')
    mc.connectAttr(upMultTemp[4] + '.output', lowMicroJnts[2] + '.translate')
    mc.connectAttr(upMultTemp[5] + '.output', lowMicroJnts[3] + '.translate')
    mc.connectAttr(upMultTemp[6] + '.output', lowMicroJnts[8] + '.translate')
    mc.connectAttr(upMultTemp[7] + '.output', lowMicroJnts[4] + '.translate')

    mc.connectAttr(upMidZipPls + '.output3D', lowMicroJnts[7] + '.translate')




















