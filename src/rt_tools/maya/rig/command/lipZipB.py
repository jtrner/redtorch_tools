import os

import maya.cmds as mc

from ...lib import crvLib
from ...lib import jntLib
from ...lib import connect
from ...lib import attrLib
from ...lib import trsLib
from ...lib import strLib
from ...lib import deformLib
from ...lib import control

reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)

# upLipRibbon = mc.createNode('transform',name = 'upLipRibbon_GRP',  p = 'C_head_CTL')
# upJntDrvr = mc.createNode('transform', name = 'upJntDrvr_GRP', p = upLipRibbon)
# mc.delete(mc.parentConstraint('C_mouth_JNT', upJntDrvr, mo = False))
#
# upMidZipBase= mc.createNode('transform', name = 'upLipMidZipBaseModify_GRP', p = upJntDrvr)
# upMidZipPlace = mc.createNode('transform', name = 'upLipMidZipPlacementModify_GRP', p = upJntDrvr)
# mc.setAttr(upMidZipPlace + '.tz', 10)
#
# upLipMidZipBase = mc.joint(upMidZipBase, name = 'upLipMidZipBase_JNT' )
# upLipMidZipPlacement = mc.joint(upMidZipPlace, name = 'upLipMidZipPlacement_JNT' )
#
# jntLib.create_on_curve()
#
# upLipMakroJntCtl = mc.createNode('transform', name = 'upLipMakroJntCtrl_GRP', p = upJntDrvr)

def LipZipB(zippercrv = '', upLipLowRezcrv = '', upLipMedRezcrv= '', upLipHiRezcrv = '',upLipZippercrv = '',
            lowLipLowRezcrv = '', lowLipMedRezcrv= '', lowLipHiRezcrv = '',lowLipLipZippercrv = '',
            upBindJnts = [] , lowBindJnts = [], numJnts=20, name='C_lipZip'):

    tempCurve = mc.duplicate(upLipLowRezcrv)[0]
    [mc.setAttr(tempCurve + '.{}{}'.format(a,v), lock = False) for a in 'trs' for v in 'xyz']
    mc.setAttr(tempCurve + '.ty', 2)

    # create mouth control pivot
    mouthPiv = mc.createNode('transform', name = 'MouthCtrlPivotMod_GRP')
    trsLib.match(mouthPiv, upBindJnts[-1])
    mc.joint(mouthPiv, name = 'MouthCtrlPivot_JNT', rad = 1.2)


    #****************************************************upPart******************************************

    upLipRibbon = mc.createNode('transform',name = 'localUpLipRibbon_GRP')

    noTuchyUp = mc.createNode('transform', name = 'localUpLipNoTouchy_GRP', p = upLipRibbon)

    upJntDrvr = mc.createNode('transform', name = 'localUpJntDrvr_GRP', p = upLipRibbon)

    upLipCtlGrp = mc.createNode('transform', name='localUpLipCtrl_GRP', p = upLipRibbon)
    trsLib.match(upLipCtlGrp, upBindJnts[1])

    upMicroJntCtlGrp = mc.createNode('transform', name = 'localUpLipMicroJntCtrl_GRP', p = upJntDrvr)


    upLipMakroJntCtl = mc.createNode('transform', name='upLipMakroJntCtrl_GRP', p = upJntDrvr)
    trsLib.match(upLipMakroJntCtl, upBindJnts[1])

    upLipLowRezBindJnts = jntLib.create_on_curve(upLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius = 0.2)



    upLipLowRezBindJnts[0] = mc.rename(upLipLowRezBindJnts[0],'R_localUpLipcorner_JNT')
    mc.setAttr(upLipLowRezBindJnts[0] + '.ry', 130)
    upLipLowRezBindJnts[1] = mc.rename(upLipLowRezBindJnts[1],'localUpLipmain_JNT')
    upLipLowRezBindJnts[2] = mc.rename(upLipLowRezBindJnts[2],'L_localUpLipcorner_JNT')
    mc.setAttr(upLipLowRezBindJnts[2] + '.ry', 50)


    #bind joints to low curves
    deformLib.bind_geo(geos = upLipLowRezcrv, joints = upLipLowRezBindJnts)

    # create some nodes on upLowRez
    upLipJntLocLowGrp = mc.createNode('transform',name = 'localUpLipJntLocLow_GRP', p = noTuchyUp)
    param = 0.8
    tempList = []
    for i in range(3):
        loc = mc.createNode('transform', name = 'rslt' + '{}'.format(i), p = upLipJntLocLowGrp)
        pos = mc.xform(upLipLowRezBindJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = upLipLowRezcrv, upCurve = tempCurve,param = param, upAxis = 'y')
        param -= 0.3
        tempList.append(loc)

    # rename transfomrs that driven by uplowRezCrv
    l_localUpLipDriverOutMod = mc.rename(tempList[0], 'L_localUpLipDriverOutModify_LOC')
    m_localUpLipDriverOutMod = mc.rename(tempList[1], 'm_localUpLipDriverOutModify_LOC')
    r_localUpLipDriverOutMod = mc.rename(tempList[2], 'r_localUpLipDriverOutModify_LOC')


    r_localUpLipOutOrient_GRP = mc.createNode('transform' , name = 'R_localUpLipOutOrient_GRP', p = upLipMakroJntCtl)
    trsLib.match(r_localUpLipOutOrient_GRP, r_localUpLipDriverOutMod)

    l_localUpLipOutOrient_GRP = mc.createNode('transform' , name = 'L_localUpLipOutOrient_GRP', p = upLipMakroJntCtl)
    trsLib.match(l_localUpLipOutOrient_GRP, l_localUpLipDriverOutMod)

    m_localUpLipOutOrient_GRP = mc.createNode('transform' , name = 'M_localUpLipOutOrient_GRP', p = upLipMakroJntCtl)
    trsLib.match(m_localUpLipOutOrient_GRP, m_localUpLipDriverOutMod)

    # create out up right joints hierarchy
    R_upLipOutCtl, R_upLipOutGrp, R_upLipOutJnt = createJntAndParent(name = 'R_localUpLip', parent = r_localUpLipOutOrient_GRP, side = 'R')
    R_upLipOutCtl = mc.rename(R_upLipOutCtl, 'R_localUpLipOut_CTL')
    R_upLipOutGrp = mc.rename(R_upLipOutGrp, 'R_localUpLipOutModify2_GRP')

    # create out up left joints hierarchy
    L_upLipOutCtl, L_upLipOutGrp, L_upLipOutJnt = createJntAndParent(name = 'L_localUpLip', parent = l_localUpLipOutOrient_GRP, side = 'L')
    L_upLipOutCtl = mc.rename(L_upLipOutCtl, 'L_localUpLipOut_CTL')
    L_upLipOutGrp = mc.rename(L_upLipOutGrp, 'L_localUpLipOutModify2_GRP')

    # create out up mid joints hierarchy
    M_upLipOutCtl, M_upLipOutGrp, M_upLipOutJnt = createJntAndParent(name = 'M_localUpLip', parent = m_localUpLipOutOrient_GRP, side = 'C')
    M_upLipOutCtl = mc.rename(M_upLipOutCtl, 'M_localUpLipOut_CTL')
    M_upLipOutGrp = mc.rename(M_upLipOutGrp, 'M_localUpLipOutModify2_GRP')

    # create left up joint hierarchy
    leftUpMainJnt = mc.createNode('transform', name = 'L_localUpLipCornerOrient_GRP', p = upJntDrvr)
    trsLib.match(leftUpMainJnt, upLipLowRezBindJnts[2])
    l_upLipCornerMod_loc = createMainHierarchyJnts(name='L_localUpLip', parent=leftUpMainJnt, middle=False)
    mc.parent(upLipLowRezBindJnts[2],l_upLipCornerMod_loc)
    upLipLowRezBindJnts[2] = upLipLowRezBindJnts[2].split('|')[-1]
    [mc.setAttr(upLipLowRezBindJnts[2]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
    mc.setAttr(upLipLowRezBindJnts[2] + '.jointOrientY', 0)

    l_upLip_rotdrvrLoc = mc.spaceLocator(name = 'L_localUpLipCorner_RotDrive_LOC')
    trsLib.match(l_upLip_rotdrvrLoc, t = upLipLowRezBindJnts[2])
    mc.parent(l_upLip_rotdrvrLoc, upLipLowRezBindJnts[2])

    l_upLip_cornerbnd = mc.spaceLocator(name = 'L_localUpLipcornerBnd_LOC')
    trsLib.match(l_upLip_cornerbnd, upLipLowRezBindJnts[2])
    mc.parent(l_upLip_cornerbnd, upLipLowRezBindJnts[2])
    l_upLip_cornerbnd = l_upLip_cornerbnd[0].split('|')[-1]
    l_upLipcorner= mc.joint(l_upLip_cornerbnd, name = 'L_localUpLipCorner_BND', rad = 0.4 )
    l_upLipcornerminor = mc.joint(l_upLipcorner, name = 'L_localUpLipCornerMinor_BND' ,  rad = 0.4)
    mc.setAttr(l_upLipcornerminor + '.tx', 0.3)


    # create right up joint hierarchy
    rightUpMainJnt = mc.createNode('transform', name = 'R_localUpLipCornerOrient_GRP', p = upJntDrvr)
    trsLib.match(rightUpMainJnt, upLipLowRezBindJnts[0])
    r_upLipCornerMod_loc = createMainHierarchyJnts(name='R_localUpLip', parent=rightUpMainJnt,  middle=False)
    mc.parent(upLipLowRezBindJnts[0],r_upLipCornerMod_loc)
    upLipLowRezBindJnts[0] = upLipLowRezBindJnts[0].split('|')[-1]
    [mc.setAttr(upLipLowRezBindJnts[0]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
    mc.setAttr(upLipLowRezBindJnts[0] + '.jointOrientY', 0)

    r_upLip_rotdrvrLoc = mc.spaceLocator(name = 'R_localUpLipCorner_RotDrive_LOC')
    trsLib.match(r_upLip_rotdrvrLoc, t = upLipLowRezBindJnts[0])
    mc.parent(r_upLip_rotdrvrLoc, upLipLowRezBindJnts[0])

    r_upLip_cornerbnd = mc.spaceLocator(name = 'R_localUpLipcornerBnd_LOC')
    trsLib.match(r_upLip_cornerbnd, upLipLowRezBindJnts[0])
    mc.parent(r_upLip_cornerbnd, upLipLowRezBindJnts[0])
    r_upLip_cornerbnd = r_upLip_cornerbnd[0].split('|')[-1]
    r_upLipcorner= mc.joint(r_upLip_cornerbnd, name = 'R_localUpLipCorner_BND', rad = 0.4 )
    r_upLipcornerminor = mc.joint(r_upLipcorner, name = 'R_localUpLipCornerMinor_BND' ,  rad = 0.4)
    mc.setAttr(r_upLipcornerminor + '.tx', 0.3)

    # create middle up joint hierarchy
    middleUpMainJnt = mc.createNode('transform', name = 'm_localUpLipCornerOrient_GRP', p = upJntDrvr)
    trsLib.match(middleUpMainJnt, upLipLowRezBindJnts[1])
    m_upLipCornerMod_loc = createMainHierarchyJnts(name='m_localUpLip', parent=middleUpMainJnt,  middle=True)
    mc.parent(upLipLowRezBindJnts[1],m_upLipCornerMod_loc)
    upLipLowRezBindJnts[1] = upLipLowRezBindJnts[1].split('|')[-1]

    uplipctl, uplipctlgrp = createMiddleMainCtl(name = 'localUpLip', parent = upLipCtlGrp,
                                                snapJnt=upLipLowRezBindJnts[1], side = 'C',up = True)
    uplipctlgrp = mc.rename(uplipctlgrp, 'localUpLipCtrlModify_GRP')

    # create left low main ctl
    leftUpmainCtls,leftUpMainCtlGrp = createSideMainCtl(name = 'localUpLip', parent = upLipCtlGrp,
                                                          snapJnt = upLipLowRezBindJnts[2], side = 'L')
    leftUpCornerCtl = mc.rename(leftUpmainCtls[0], 'L_localUpLipCorner_CTL' )
    leftUpMinorCornerCtl = mc.rename(leftUpmainCtls[1], 'L_localUpLipCornerMinor_CTL' )
    leftCornerUpCtlGrp = mc.rename(leftUpMainCtlGrp[0], 'L_localUpLipCornerCtrlModify_GRP' )
    leftMinorCornerUpCtlGrp = mc.rename(leftUpMainCtlGrp[1], 'L_localUpLipCornerMinorModify_GRP' )

    # create right up main ctl
    rightUpmainCtls,rightUpMainCtlGrp = createSideMainCtl(name = 'localUpLip', parent = upLipCtlGrp,
                                                          snapJnt = upLipLowRezBindJnts[0], side = 'R')
    rightCornerCtl = mc.rename(rightUpmainCtls[0], 'R_localUpLipCorner_CTL' )
    rightMinorCornerCtl = mc.rename(rightUpmainCtls[1], 'R_localUpLipCornerMinor_CTL' )
    rightCornerLowCtlGrp = mc.rename(rightUpMainCtlGrp[0], 'R_localUpLipCornerCtrlModify_GRP' )
    rightMinorCornerLowCtlGrp = mc.rename(rightUpMainCtlGrp[1], 'R_localUpLipCornerMinorModify_GRP' )

    # create up roll
    createRollHirarchy(name = 'localUpLip', parent = upLipCtlGrp, up = True)

    zipUpSecJnts = jntLib.create_on_curve(upLipZippercrv, numOfJoints = 9, parent = False, description='C_base', radius = 0.2)

    # create secondary zip joints
    uplipZipperTargetLoc = mc.createNode('transform', name = 'localLowLipZipperTargetLoc_GRP')
    param = 0.8
    tempList = []
    for i in range(9):
        loc = mc.createNode('transform', name = 'rslt' + '{}'.format(i), p = uplipZipperTargetLoc)
        pos = mc.xform(upLipLowRezBindJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = upLipZippercrv, upCurve = tempCurve,param = param, upAxis = 'y')
        param -= 0.1
        tempList.append(loc)



    #****************************************************lowPart******************************************
    lowLipRibbon = mc.createNode('transform',name = 'localLowLipRibbon_GRP')
    noTuchyLow= mc.createNode('transform', name = 'localLowLipNoTouchy_GRP', p = lowLipRibbon)

    lowJntDrvr = mc.createNode('transform', name = 'localLowJntDrvr_GRP', p = lowLipRibbon)

    lowLipCtlGrp = mc.createNode('transform', name='localLowLipCtrl_GRP', p = lowLipRibbon)
    trsLib.match(lowLipCtlGrp, lowBindJnts[1])

    lowLipMakroJntCtl = mc.createNode('transform', name='lowLipMakroJntCtrl_GRP', p = lowJntDrvr)
    trsLib.match(lowLipMakroJntCtl, lowBindJnts[1])

    lowLipLowRezBindJnts = jntLib.create_on_curve(lowLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius= 0.2)

    lowLipLowRezBindJnts[0] = mc.rename(lowLipLowRezBindJnts[0],'R_localLowLipcorner_JNT')
    mc.setAttr(lowLipLowRezBindJnts[0] + '.ry', 130)
    lowLipLowRezBindJnts[1] = mc.rename(lowLipLowRezBindJnts[1],'localLowLipmain_JNT')
    lowLipLowRezBindJnts[2] = mc.rename(lowLipLowRezBindJnts[2],'L_localLowLipcorner_JNT')
    mc.setAttr(lowLipLowRezBindJnts[2] + '.ry', 50)

    deformLib.bind_geo(geos = lowLipLowRezcrv, joints = lowLipLowRezBindJnts)


    # create some nodes on LowRez
    lowLipJntLocLowGrp = mc.createNode('transform',name = 'localLowLipJntLocLow_GRP', p = noTuchyLow)
    param = 0.8
    tempList = []
    for i in range(3):
        loc = mc.createNode('transform', name = 'rslt' + '{}'.format(i), p = lowLipJntLocLowGrp)
        pos = mc.xform(lowLipLowRezBindJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = lowLipLowRezcrv, upCurve = tempCurve,param = param, upAxis = 'y')
        param -= 0.3
        tempList.append(loc)


    # rename transfomrs that driven by lowRezCrv
    l_localLowLipDriverOutMod = mc.rename(tempList[0], 'L_localLowLipDriverOutModify_LOC')
    m_localLowLipDriverOutMod = mc.rename(tempList[1], 'm_localLowLipDriverOutModify_LOC')
    r_localLowLipDriverOutMod = mc.rename(tempList[2], 'r_localLowLipDriverOutModify_LOC')

    r_localLowLipOutOrient_GRP = mc.createNode('transform' , name = 'R_localLowLipOutOrient_GRP', p = lowLipMakroJntCtl)
    trsLib.match(r_localLowLipOutOrient_GRP, r_localLowLipDriverOutMod)

    l_localLowLipOutOrient_GRP = mc.createNode('transform' , name = 'L_localLowLipOutOrient_GRP', p = lowLipMakroJntCtl)
    trsLib.match(l_localLowLipOutOrient_GRP, l_localLowLipDriverOutMod)

    m_localLowLipOutOrient_GRP = mc.createNode('transform' , name = 'M_localLowLipOutOrient_GRP', p = lowLipMakroJntCtl)
    trsLib.match(m_localLowLipOutOrient_GRP, m_localLowLipDriverOutMod)

    # create out low right joints hierarchy
    R_lowLipOutCtl, R_lowLipOutGrp, R_lowLipOutJnt = createJntAndParent(name = 'R_localLowLip', parent = r_localLowLipOutOrient_GRP, side = 'R')
    R_lowLipOutCtl = mc.rename(R_lowLipOutCtl, 'R_localLowLipOut_CTL')
    R_lowLipOutGrp = mc.rename(R_lowLipOutGrp, 'R_localLowLipOutModify2_GRP')

    # create out low left joints hierarchy
    L_lowLipOutCtl, L_lowLipOutGrp, L_lowLipOutJnt = createJntAndParent(name = 'L_localLowLip', parent = l_localLowLipOutOrient_GRP, side = 'L')
    L_lowLipOutCtl = mc.rename(L_lowLipOutCtl, 'L_localLowLipOut_CTL')
    L_lowLipOutGrp = mc.rename(L_lowLipOutGrp, 'L_localLowLipOutModify2_GRP')

    # create out low mid joints hierarchy
    M_lowLipOutCtl, M_lowLipOutGrp, M_lowLipOutJnt = createJntAndParent(name = 'M_localLowLip', parent = m_localLowLipOutOrient_GRP, side = 'C')
    M_lowLipOutCtl = mc.rename(M_lowLipOutCtl, 'M_localLowLipOut_CTL')
    M_lowLipOutGrp = mc.rename(M_lowLipOutGrp, 'M_localLowLipOutModify2_GRP')

    # create left low joint hierarchy
    leftLowMainJnt = mc.createNode('transform', name = 'L_localLowLipCornerOrient_GRP', p = lowJntDrvr)
    trsLib.match(leftLowMainJnt, lowLipLowRezBindJnts[2])
    l_upLipCornerMod_loc = createMainHierarchyJnts(name='L_localLowLip', parent=leftLowMainJnt, middle=False)
    mc.parent(lowLipLowRezBindJnts[2],l_upLipCornerMod_loc)
    lowLipLowRezBindJnts[2] = lowLipLowRezBindJnts[2].split('|')[-1]
    [mc.setAttr(lowLipLowRezBindJnts[2]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
    mc.setAttr(lowLipLowRezBindJnts[2] + '.jointOrientY', 0)

    l_LowLip_rotdrvrLoc = mc.spaceLocator(name = 'L_localLowLipCorner_RotDrive_LOC')
    trsLib.match(l_LowLip_rotdrvrLoc, t = lowLipLowRezBindJnts[2])
    mc.parent(l_LowLip_rotdrvrLoc, lowLipLowRezBindJnts[2])

    l_LowLip_cornerbnd = mc.spaceLocator(name = 'L_localLowLipcornerBnd_LOC')
    trsLib.match(l_LowLip_cornerbnd, lowLipLowRezBindJnts[2])
    mc.parent(l_LowLip_cornerbnd, lowLipLowRezBindJnts[2])
    l_LowLip_cornerbnd = l_LowLip_cornerbnd[0].split('|')[-1]
    l_lowLipcorner= mc.joint(l_LowLip_cornerbnd, name = 'L_localLowLipCorner_BND', rad = 0.4 )
    l_lowLipcornerminor = mc.joint(l_lowLipcorner, name = 'L_localUpLipCornerMinor_BND' ,  rad = 0.4)
    mc.setAttr(l_lowLipcornerminor + '.tx', 0.3)


    # create right low joint hierarchy
    rightLowMainJnt = mc.createNode('transform', name = 'R_localLowLipCornerOrient_GRP', p = lowJntDrvr)
    trsLib.match(rightLowMainJnt, lowLipLowRezBindJnts[0])
    r_upLipCornerMod_loc = createMainHierarchyJnts(name='R_localLowLip', parent=rightLowMainJnt, middle=False)
    mc.parent(lowLipLowRezBindJnts[0],r_upLipCornerMod_loc)
    lowLipLowRezBindJnts[0] = lowLipLowRezBindJnts[0].split('|')[-1]
    [mc.setAttr(lowLipLowRezBindJnts[0]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
    mc.setAttr(lowLipLowRezBindJnts[0] + '.jointOrientY', 0)

    r_lowLip_rotdrvrLoc = mc.spaceLocator(name = 'R_localLowLipCorner_RotDrive_LOC')
    trsLib.match(r_lowLip_rotdrvrLoc, t = lowLipLowRezBindJnts[0])
    mc.parent(r_lowLip_rotdrvrLoc, lowLipLowRezBindJnts[0])

    r_lowLip_cornerbnd = mc.spaceLocator(name = 'R_localLowLipcornerBnd_LOC')
    trsLib.match(r_lowLip_cornerbnd, lowLipLowRezBindJnts[0])
    mc.parent(r_lowLip_cornerbnd, lowLipLowRezBindJnts[0])
    r_lowLip_cornerbnd = r_lowLip_cornerbnd[0].split('|')[-1]
    r_LowLipcorner= mc.joint(r_lowLip_cornerbnd, name = 'R_localLowLipCorner_BND', rad = 0.4 )
    r_upLipcornerminor = mc.joint(r_LowLipcorner, name = 'R_localLowLipCornerMinor_BND' ,  rad = 0.4)
    mc.setAttr(r_upLipcornerminor + '.tx', 0.3)

    # create middle low joint hierarchy
    middleLowMainJnt = mc.createNode('transform', name = 'm_localLowLipCornerOrient_GRP', p = lowJntDrvr)
    trsLib.match(middleLowMainJnt, lowLipLowRezBindJnts[1])
    m_upLipCornerMod_loc = createMainHierarchyJnts(name='m_localLowLip', parent=middleLowMainJnt, middle=True)
    mc.parent(lowLipLowRezBindJnts[1],m_upLipCornerMod_loc)
    lowLipLowRezBindJnts[1] = lowLipLowRezBindJnts[1].split('|')[-1]

    # create middle low main ctl
    lowlipctl, lowlipctlgrp = createMiddleMainCtl(name = 'localLowLip', parent = lowLipCtlGrp,
                                                  snapJnt=lowLipLowRezBindJnts[1], side = 'C', up = False)
    lowlipctlgrp = mc.rename(lowlipctlgrp, 'localLowLipCtrlModify_GRP')

    # create left low main ctl
    leftLowmainCtls,leftLowMainCtlGrp = createSideMainCtl(name = 'localLowLip', parent = lowLipCtlGrp,
                                                          snapJnt = lowLipLowRezBindJnts[2], side = 'L')
    leftCornerCtl = mc.rename(leftLowmainCtls[0], 'L_localLowLipCorner_CTL' )
    leftMinorCornerCtl = mc.rename(leftLowmainCtls[1], 'L_localLowLipCornerMinor_CTL' )
    leftCornerLowCtlGrp = mc.rename(leftLowMainCtlGrp[0], 'L_localLowLipCornerCtrlModify_GRP' )
    leftMinorCornerLowCtlGrp = mc.rename(leftLowMainCtlGrp[1], 'L_localLowLipCornerMinorModify_GRP' )

    # create right low main ctl
    rightLowmainCtls,rightLowMainCtlGrp = createSideMainCtl(name = 'localLowLip', parent = lowLipCtlGrp,
                                                          snapJnt = lowLipLowRezBindJnts[0], side = 'R')
    rightCornerCtl = mc.rename(rightLowmainCtls[0], 'R_localLowLipCorner_CTL' )
    rightMinorCornerCtl = mc.rename(rightLowmainCtls[1], 'R_localLowLipCornerMinor_CTL' )
    rightCornerLowCtlGrp = mc.rename(rightLowMainCtlGrp[0], 'R_localLowLipCornerCtrlModify_GRP' )
    rightMinorCornerLowCtlGrp = mc.rename(rightLowMainCtlGrp[1], 'R_localLowLipCornerMinorModify_GRP' )

    # create low roll
    createRollHirarchy(name = 'localLowLip', parent = lowLipCtlGrp, up = False)


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


def createSideMainCtl(name = '', parent = '', snapJnt = '', side = 'L'):
    ctlOr = mc.createNode('transform', name = name + 'CornerCtrlOrient_GRP', p = parent)
    trsLib.match(ctlOr, snapJnt)

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
                              matchTranslate=ctlOr)

        ctls.append(ctl.name)
        ctlsGrp.append(ctl.zro)

    crvLib.scaleShape(curve=ctls[0], scale=(0.8, 0.8, 0.8))
    crvLib.scaleShape(curve=ctls[1], scale=(0.3, 0.3, 0.3))

    par = ctlOr
    mult = [1, -1][side == 'R']
    for i in range(2):
        mc.setAttr(ctlsGrp[i] + '.ry', -80)
        mc.makeIdentity(ctlsGrp[i], apply=True, r=True, t=True)
        trsLib.match(ctlsGrp[i], ctlOr)
        mc.parent(ctlsGrp[i], par)
        mc.makeIdentity(ctlsGrp[i], apply=True, r=True, t=True)
        crvLib.moveShape(curve=ctls[i], move=(mult * 0.6, 0,  0.3))
        par = ctls[0]

    return ctls, ctlsGrp



def createMiddleMainCtl(name = '', parent = '', snapJnt = '', side = 'C',up = True):
    ctlPlacement = mc.createNode('transform', name = name + 'CtrlPlacement_GRP',p = parent)
    trsLib.match(ctlPlacement, snapJnt)
    squashMakro = mc.createNode('transform', name = name + 'CtrlMouthSquashMAKRO_GRP',  p = ctlPlacement)
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
                             color=control.SECCOLORS[side],
                             scale=[2, 0.3, 1],
                             lockHideAttrs=['s'],
                             matchTranslate=ctlOr)
    mc.parent(ctl.zro, ctlOr)
    mc.makeIdentity(ctl.zro, apply = True, r = True, t = True)
    return ctl.name, ctl.zro



def createJntAndParent(name = '',parent = '', side = 'C'):
    outMod = mc.createNode('transform' , name = name + 'OutModify_GRP',p = parent)
    outMod2 = mc.createNode('transform' , name = name + 'OutModify2_GRP',p = outMod)
    outModLocTrans = mc.createNode('transform',  name = name + 'OutModify_LOC', p = outMod2)
    outModLocShape = mc.createNode('locator',  name = name + 'OutModifyShape_LOC', p = outModLocTrans)
    outerOr = mc.createNode('transform', name = name + 'OuterOrient_GRP', p = outModLocTrans)
    outerMod = mc.createNode('transform', name = name + 'OuterModify_GRP', p = outerOr)

    ctl = control.Control(descriptor=name,
                             side='C',
                             shape="sphere",
                             color=control.SECCOLORS[side],
                             moveShape=[0, 0, 0.7],
                             scale=[0.2, 0.2, 0.2],
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
        return outModLocTrans

    else:
        mainMod = mc.createNode('transform' , name = name + 'MainModify_GRP',p = parent)
        outModLocTrans = mc.createNode('transform',  name = name + 'MainModify_LOC', p = mainMod)
        outModLocShape = mc.createNode('locator', name=name + 'ModifyShape_LOC', p=outModLocTrans)
        return  outModLocTrans









