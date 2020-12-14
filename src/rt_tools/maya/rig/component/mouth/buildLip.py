import os

import maya.cmds as mc

from ....lib import crvLib
from ....lib import jntLib
from ....lib import connect
from ....lib import attrLib
from ....lib import trsLib
from ....lib import strLib
from ....lib import deformLib
from ....lib import control
from . import funcs
from . import lipsTemplate

reload(lipsTemplate)
reload(funcs)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


class BuildLip(lipsTemplate.LipsTemplate):
    """Class for creating lip"""
    def __init__(self,  **kwargs ):
        super(BuildLip, self).__init__(**kwargs)

        self.aliases = {'mouthFlood': 'mouthFlood',
                        'jawMain':'jawMain',
                        'jawSecondary':'jawSecondary',
                        'chin': 'chin',
                        'mentalis':'mentalis',
                        'mouth': 'mouth',
                        'nose': 'nose',
                        'columella': 'columella',
                        'leftnostril': 'leftnostril',
                        'leftnostrilFlare': 'leftnostrilFlare',
                        'rightnostril': 'rightnostril',
                        'rightnostrilFlare': 'rightnostrilFlare'
                        }

    def createBlueprint(self):
        super(BuildLip, self).createBlueprint()
        par = self.blueprintGrp
        self.noseSide = 'R'
        mult = [-1, 1][self.noseSide == 'R']
        self.blueprints['mouthFlood'] = '{}_mouthFlood_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mouthFlood']):
            mc.joint(self.blueprintGrp, name = self.blueprints['mouthFlood'])
            mc.xform(self.blueprints['mouthFlood'], ws = True, t = (30, 270, -3))

        self.blueprints['jawMain'] = '{}_jawMain_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['jawMain']):
            mc.joint(self.blueprintGrp, name = self.blueprints['jawMain'])
            mc.xform(self.blueprints['jawMain'], ws = True, t = (30, 265, -12))

        self.blueprints['jawSecondary'] = '{}_jawSecondary_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['jawSecondary']):
            mc.joint(self.blueprintGrp, name = self.blueprints['jawSecondary'])
            mc.xform(self.blueprints['jawSecondary'], ws = True, t = (30, 260, -3.5))

        self.blueprints['chin'] = '{}_chin_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['chin']):
            mc.joint(self.blueprints['jawSecondary'] , name = self.blueprints['chin'])
            mc.xform(self.blueprints['chin'], ws = True, t = (30, 257, 4))

        self.blueprints['mentalis'] = '{}_mentalis_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mentalis']):
            mc.joint(self.blueprints['jawSecondary'] , name = self.blueprints['mentalis'])
            mc.xform(self.blueprints['mentalis'], ws = True, t = (30, 254, 2.7))

        self.blueprints['mouth'] = '{}_mouth_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mouth']):
            mc.joint(self.blueprintGrp, name = self.blueprints['mouth'])
            mc.xform(self.blueprints['mouth'], ws = True, t = (30, 260.8, 1.52))

        self.blueprints['nose'] = '{}_nose_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['nose']):
            mc.joint(self.blueprintGrp, name = self.blueprints['nose'])
            mc.xform(self.blueprints['nose'], ws = True, t = (30, 263, 2.3))

        self.blueprints['columella'] = '{}_columella_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['columella']):
            mc.joint(self.blueprintGrp, name = self.blueprints['columella'])
            mc.xform(self.blueprints['columella'], ws = True, t = (30, 262, 2.3))

        self.blueprints['leftnostril'] = '{}_leftnostril_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftnostril']):
            mc.joint(self.blueprintGrp, name = self.blueprints['leftnostril'])
            mc.xform(self.blueprints['leftnostril'], ws = True, t = (30.5, 262.4, 2.3))

        self.blueprints['leftnostrilFlare'] = '{}_leftnostrilFlare_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftnostrilFlare']):
            mc.joint(self.blueprints['leftnostril'] , name = self.blueprints['leftnostrilFlare'])
            mc.xform(self.blueprints['leftnostrilFlare'], ws = True, t = (30.25, 262.14, 2.9))

        self.blueprints['rightnostril'] = '{}_rightnostril_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightnostril']):
            mc.joint(self.blueprintGrp, name = self.blueprints['rightnostril'])
            mc.xform(self.blueprints['rightnostril'], ws = True, t = (29.4, 262.4, 2.3))

        self.blueprints['rightnostrilFlare'] = '{}_rightnostrilFlare_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightnostrilFlare']):
            mc.joint(self.blueprints['rightnostril'] , name = self.blueprints['rightnostrilFlare'])
            mc.xform(self.blueprints['rightnostrilFlare'], ws = True, t = (29.6, 262.14, 2.9))


    def createJoints(self):
        par = self.moduleGrp
        self.mouthAndJawMain = []
        for alias, blu in self.blueprints.items():
            if not alias in ('mouthFlood', 'jawMain', 'mouth', 'nose', 'columella'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.mouthAndJawMain.append(jnt)

        self.jawSecBndJnt = []
        for alias, blu in self.blueprints.items():
            if not alias in ('jawSecondary','chin','mentalis'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.jawSecBndJnt.append(jnt)
            par = self.jawSecBndJnt[0]

        par = self.moduleGrp
        self.leftnostrils = []
        for alias, blu in self.blueprints.items():
            if not alias in ('leftnostril','leftnostrilFlare'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.leftnostrils.append(jnt)
            par = self.leftnostrils[0]

        par = self.moduleGrp
        self.rightnostrils = []
        for alias, blu in self.blueprints.items():
            if not alias in ('rightnostril','rightnostrilFlare'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.rightnostrils.append(jnt)
            par = self.rightnostrils[0]


    def build(self):
        super(BuildLip, self).build()
        self.tempCurve = mc.duplicate(self.upLipLowRezcrv)[0]
        [mc.setAttr(self.tempCurve + '.{}{}'.format(a,v), lock = False) for a in 'trs' for v in 'xyz']
        mc.setAttr(self.tempCurve + '.ty', 2)

        # create mouth control pivot
        #mc.joint(self.mouthPiv, name = 'MouthCtrlPivot_JNT', rad = 1.2)

        #****************************************************upPart******************************************

        mc.move(0, 1, 5, self.upjntCtlPlace, r=True, ws=True)
        funcs.createCtlPlaceMent(name = 'localUpLip', parent = self.upjntCtlPlace)

        #create roll modify
        mc.move(0, 0.5,1.3, self.jntRollModupGrp, r=True, ws=True)
        funcs.createRollMod(name = 'localLowLip', parent = self.jntRollModupGrp,up = True)

        self.upLipLowRezBindJnts = jntLib.create_on_curve(self.upLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius = 0.2)


        self.upLipLowRezBindJnts[0] = mc.rename(self.upLipLowRezBindJnts[0],'R_localUpLipcorner_JNT')
        mc.setAttr(self.upLipLowRezBindJnts[0] + '.ry', 130)
        self.upLipLowRezBindJnts[1] = mc.rename(self.upLipLowRezBindJnts[1],'localUpLipmain_JNT')
        self.upLipLowRezBindJnts[2] = mc.rename(self.upLipLowRezBindJnts[2],'L_localUpLipcorner_JNT')
        mc.setAttr(self.upLipLowRezBindJnts[2] + '.ry', 50)

        # matches nodes from lips template to the side joints
        trsLib.match(self.leftUpMainJnt, self.upLipLowRezBindJnts[2])
        trsLib.match(self.rightUpMainJnt, self.upLipLowRezBindJnts[0])
        trsLib.match(self.middleUpMainJnt, self.upLipLowRezBindJnts[1])

        trsLib.match(self.r_lipCornerMakroDrvr , self.upLipLowRezBindJnts[0])
        mc.move(10,0,0,self.r_lipCornerMakroDrvr , r = True, ws = True)
        trsLib.match(self.l_lipCornerMakroDrvr , self.upLipLowRezBindJnts[2])
        mc.move(10,0,0,self.l_lipCornerMakroDrvr , r = True, ws = True)


        #bind joints to low curves
        deformLib.bind_geo(geos = self.upLipLowRezcrv, joints = self.upLipLowRezBindJnts)

        # create some nodes on upLowRez
        param = 0.8
        tempList = []
        for i in range(3):
            loc = mc.createNode('transform', name = 'rslt' + '{}'.format(i), p = self.upLipJntLocLowGrp)
            pos = mc.xform(self.upLipLowRezBindJnts[i-1], q=True, ws=True, t=True)
            mc.setAttr(loc + '.t', *pos)
            crvLib.attach(node = loc, curve = self.upLipLowRezcrv, upCurve = self.tempCurve,param = param, upAxis = 'y')
            param -= 0.3
            tempList.append(loc)

        # rename transfomrs that driven by uplowRezCrv
        l_localUpLipDriverOutMod = mc.rename(tempList[0], 'L_localUpLipDriverOutModify_LOC')
        m_localUpLipDriverOutMod = mc.rename(tempList[1], 'm_localUpLipDriverOutModify_LOC')
        r_localUpLipDriverOutMod = mc.rename(tempList[2], 'r_localUpLipDriverOutModify_LOC')
        trsLib.match(self.r_localUpLipOutOrient_GRP, r_localUpLipDriverOutMod)
        trsLib.match(self.l_localUpLipOutOrient_GRP, l_localUpLipDriverOutMod)
        trsLib.match(self.m_localUpLipOutOrient_GRP, m_localUpLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.upLipMedRezcrv, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedUp, numLocs = 7, crv = self.upLipMedRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        upSecMod = mc.rename(tempList[0],'L_localUpLipMicroOutSecondaryModify_LOC')
        upmicroOutMod = mc.rename(tempList[1],'L_localUpLipMicroOutModify_LOC')
        upmidSecMod = mc.rename(tempList[2],'L_localUpLipMicroMidSecondaryModify_LOC')
        upMidMod = mc.rename(tempList[3],'localUpLipMicroMidModify_LOC')
        upMidSecModLoc = mc.rename(tempList[4],'R_localUpLipMicroMidSecondaryModify_LOC')
        microOutModLoc = mc.rename(tempList[5],'R_localUpLipMicroOutModify_LOC')
        microOutSecMod = mc.rename(tempList[6],'R_localUpLipMicroOutSecondaryModify_LOC')

        # create out up right joints hierarchy
        R_upLipOutCtl, R_upLipOutGrp, R_upLipOutJnt = funcs.createJntAndParent(name = 'R_localUpLip',
                                                                               parent = self.r_localUpLipOutOrient_GRP,
                                                                               side = 'R',up = True)
        R_upLipOutCtl = mc.rename(R_upLipOutCtl, 'R_localUpLipOut_CTL')
        R_upLipOutGrp = mc.rename(R_upLipOutGrp, 'R_localUpLipOutModify2_GRP')

        # create out up left joints hierarchy
        L_upLipOutCtl, L_upLipOutGrp, L_upLipOutJnt = funcs.createJntAndParent(name = 'L_localUpLip',
                                                                               parent = self.l_localUpLipOutOrient_GRP,
                                                                               side = 'L', up = True)
        L_upLipOutCtl = mc.rename(L_upLipOutCtl, 'L_localUpLipOut_CTL')
        L_upLipOutGrp = mc.rename(L_upLipOutGrp, 'L_localUpLipOutModify2_GRP')

        # create out up mid joints hierarchy
        M_upLipOutCtl, M_upLipOutGrp, M_upLipOutJnt = funcs.createJntAndParent(name = 'M_localUpLip',
                                                                               parent = self.m_localUpLipOutOrient_GRP,
                                                                               side = 'C',up = True)
        M_upLipOutCtl = mc.rename(M_upLipOutCtl, 'M_localUpLipOut_CTL')
        M_upLipOutGrp = mc.rename(M_upLipOutGrp, 'M_localUpLipOutModify2_GRP')

        # create left up joint hierarchy
        l_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='L_localUpLip', parent=self.leftUpMainJnt, middle=False)
        mc.parent(self.upLipLowRezBindJnts[2],l_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[2] = self.upLipLowRezBindJnts[2].split('|')[-1]
        [mc.setAttr(self.upLipLowRezBindJnts[2]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.upLipLowRezBindJnts[2] + '.jointOrientY', 0)

        l_upLip_rotdrvrLoc = mc.spaceLocator(name = 'L_localUpLipCorner_RotDrive_LOC')
        trsLib.match(l_upLip_rotdrvrLoc, t = self.upLipLowRezBindJnts[2])
        mc.parent(l_upLip_rotdrvrLoc, self.upLipLowRezBindJnts[2])

        l_upLip_cornerbnd = mc.spaceLocator(name = 'L_localUpLipcornerBnd_LOC')
        trsLib.match(l_upLip_cornerbnd, self.upLipLowRezBindJnts[2])
        mc.parent(l_upLip_cornerbnd, self.upLipLowRezBindJnts[2])
        l_upLip_cornerbnd = l_upLip_cornerbnd[0].split('|')[-1]
        l_upLipcorner= mc.joint(l_upLip_cornerbnd, name = 'L_localUpLipCorner_BND', rad = 0.4 )
        l_upLipcornerminor = mc.joint(l_upLipcorner, name = 'L_localUpLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(l_upLipcornerminor + '.tx', 0.3)


        # create right up joint hierarchy
        r_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='R_localUpLip', parent=self.rightUpMainJnt,  middle=False)
        mc.parent(self.upLipLowRezBindJnts[0],r_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[0] = self.upLipLowRezBindJnts[0].split('|')[-1]
        [mc.setAttr(self.upLipLowRezBindJnts[0]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.upLipLowRezBindJnts[0] + '.jointOrientY', 0)

        r_upLip_rotdrvrLoc = mc.spaceLocator(name = 'R_localUpLipCorner_RotDrive_LOC')
        trsLib.match(r_upLip_rotdrvrLoc, t = self.upLipLowRezBindJnts[0])
        mc.parent(r_upLip_rotdrvrLoc, self.upLipLowRezBindJnts[0])

        r_upLip_cornerbnd = mc.spaceLocator(name = 'R_localUpLipcornerBnd_LOC')
        trsLib.match(r_upLip_cornerbnd, self.upLipLowRezBindJnts[0])
        mc.parent(r_upLip_cornerbnd, self.upLipLowRezBindJnts[0])
        r_upLip_cornerbnd = r_upLip_cornerbnd[0].split('|')[-1]
        r_upLipcorner= mc.joint(r_upLip_cornerbnd, name = 'R_localUpLipCorner_BND', rad = 0.4 )
        r_upLipcornerminor = mc.joint(r_upLipcorner, name = 'R_localUpLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(r_upLipcornerminor + '.tx', 0.3)

        # create middle up joint hierarchy
        m_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='m_localUpLip', parent= self.middleUpMainJnt,  middle=True)
        mc.parent(self.upLipLowRezBindJnts[1],m_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[1] = self.upLipLowRezBindJnts[1].split('|')[-1]

        self.mouthCtlOr = mc.createNode('transform', name = 'mouthCtlOri_GRP',p = self.facialCtrlGrp)
        trsLib.match( self.mouthCtlOr, self.mouthPiv)
        mc.setAttr(self.mouthCtlOr + '.tz', 6.5)
        mc.setAttr(self.mouthCtlOr + '.ty', 240.8)
        self.mouthCtl, self.mouthCtlGrp = funcs.createMouthCtl(name = 'mouthCtl', parent = self.mouthCtlOr,
                                                    snapJnt=self.mouthPiv, side = 'C')

        self.ctlupPlacement = mc.createNode('transform', name='localUpLipCtrlPlacement_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.ctlupPlacement, self.upLipLowRezBindJnts[1])
        uplipctl, uplipctlgrp = funcs.createMiddleMainCtl(name = 'localUpLip', parent = self.ctlupPlacement ,
                                                    snapJnt=self.upLipLowRezBindJnts[1], side = 'C',up = True)
        uplipctlgrp = mc.rename(uplipctlgrp, 'localUpLipCtrlModify_GRP')

        # create left low main ctl
        self.leftUpLipCtlGrp = mc.createNode('transform', name= 'L_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.leftUpLipCtlGrp, self.upLipLowRezBindJnts[2])
        leftUpmainCtls,leftUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.leftUpLipCtlGrp ,
                                                              snapJnt = self.upLipLowRezBindJnts[2], side = 'L')
        leftUpCornerCtl = mc.rename(leftUpmainCtls[0], 'L_localUpLipCorner_CTL' )
        leftUpMinorCornerCtl = mc.rename(leftUpmainCtls[1], 'L_localUpLipCornerMinor_CTL' )
        leftCornerUpCtlGrp = mc.rename(leftUpMainCtlGrp[0], 'L_localUpLipCornerCtrlModify_GRP' )
        leftMinorCornerUpCtlGrp = mc.rename(leftUpMainCtlGrp[1], 'L_localUpLipCornerMinorModify_GRP' )

        # create right up main ctl
        self.rightUpLipCtlGrp = mc.createNode('transform', name='R_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.rightUpLipCtlGrp, self.upLipLowRezBindJnts[0])
        rightUpmainCtls,rightUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.rightUpLipCtlGrp,
                                                              snapJnt = self.upLipLowRezBindJnts[0], side = 'R')
        rightCornerCtl = mc.rename(rightUpmainCtls[0], 'R_localUpLipCorner_CTL' )
        rightMinorCornerCtl = mc.rename(rightUpmainCtls[1], 'R_localUpLipCornerMinor_CTL' )
        rightCornerLowCtlGrp = mc.rename(rightUpMainCtlGrp[0], 'R_localUpLipCornerCtrlModify_GRP' )
        rightMinorCornerLowCtlGrp = mc.rename(rightUpMainCtlGrp[1], 'R_localUpLipCornerMinorModify_GRP' )

        # create up roll
        self.upLipCtlRoll = funcs.createRollHirarchy(name = 'localUpLip', parent = self.upLipCtlGrp, up = True)

        # create secondary zip joints
        zipUpSecJnts = jntLib.create_on_curve(self.upLipZippercrv, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        # create zipper joints
        funcs.createZipperJnts(name='localUpLip', crv=self.upLipZippercrv, upCurve=self.tempCurve,
                         posJnts=zipUpSecJnts, parent = self.noTuchyUp, jntParent = self.upMicroJntCtlGrp, up = True)

        funcs.createLocsJntDriver(name = 'R_localUpLip', parent =self.upJntDrvr,  jntSnap = self.upBindJnts[0])

        #****************************************************lowPart******************************************

        #create roll modify
        mc.move(0, -0.5,1.3, self.jntRollModlowGrp, r=True, ws=True)
        funcs.createRollMod(name = 'localLowLip', parent = self.jntRollModlowGrp,up = False)

        # create ctlPlacement
        mc.move(0, 1, 5, self.lowjntCtlPlace, r=True, ws=True)
        funcs.createCtlPlaceMent(name = 'localLowLip', parent = self.lowjntCtlPlace)

        lowLipLowRezBindJnts = jntLib.create_on_curve(self.lowLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius= 0.2)

        lowLipLowRezBindJnts[0] = mc.rename(lowLipLowRezBindJnts[0],'R_localLowLipcorner_JNT')
        mc.setAttr(lowLipLowRezBindJnts[0] + '.ry', 130)
        lowLipLowRezBindJnts[1] = mc.rename(lowLipLowRezBindJnts[1],'localLowLipmain_JNT')
        lowLipLowRezBindJnts[2] = mc.rename(lowLipLowRezBindJnts[2],'L_localLowLipcorner_JNT')
        mc.setAttr(lowLipLowRezBindJnts[2] + '.ry', 50)

        trsLib.match(self.leftLowMainJnt, lowLipLowRezBindJnts[2])
        trsLib.match(self.rightLowMainJnt, lowLipLowRezBindJnts[0])
        trsLib.match(self.middleLowMainJnt, lowLipLowRezBindJnts[1])

        deformLib.bind_geo(geos = self.lowLipLowRezcrv, joints = lowLipLowRezBindJnts)
        # create some nodes on LowRez

        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLipJntLocLowGrp, numLocs = 3, crv = self.lowLipLowRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.8,paramEnd = 0.3, upAxis = 'y', posJnts = lowLipLowRezBindJnts)

        # rename transfomrs that driven by lowRezCrv
        l_localLowLipDriverOutMod = mc.rename(tempList[0], 'L_localLowLipDriverOutModify_LOC')
        m_localLowLipDriverOutMod = mc.rename(tempList[1], 'm_localLowLipDriverOutModify_LOC')
        r_localLowLipDriverOutMod = mc.rename(tempList[2], 'r_localLowLipDriverOutModify_LOC')

        trsLib.match(self.r_localLowLipOutOrient_GRP, r_localLowLipDriverOutMod)
        trsLib.match(self.l_localLowLipOutOrient_GRP, l_localLowLipDriverOutMod)
        trsLib.match(self.m_localLowLipOutOrient_GRP, m_localLowLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezcrv, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedLow, numLocs = 7, crv = self.lowLipMedRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        lowSecMod = mc.rename(tempList[0],'L_localLowLipMicroOutSecondaryModify_LOC')
        lowmicroOutMod = mc.rename(tempList[1],'L_localLowLipMicroOutModify_LOC')
        lowmidSecMod = mc.rename(tempList[2],'L_localLowLipMicroMidSecondaryModify_LOC')
        lowMidMod = mc.rename(tempList[3],'localLowLipMicroMidModify_LOC')
        lowMidSecModLoc = mc.rename(tempList[4],'R_localLowLipMicroMidSecondaryModify_LOC')
        lowmicroOutModLoc = mc.rename(tempList[5],'R_localLowLipMicroOutModify_LOC')
        lowmicroOutSecMod = mc.rename(tempList[6],'R_localLowLipMicroOutSecondaryModify_LOC')

        # create some nodes on HiRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezcrv, numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocHiLow, numLocs = 2, crv = self.lowLipHiRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.97,paramEnd = 0.95, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        l_utTerModLocHi = mc.rename(tempList[0], 'L_localLowLipMicroOutTertiaryModify_LOC')
        r_outTerModLocHi = mc.rename(tempList[1], 'R_localLowLipMicroOutTertiaryModify_LOC')



        # create out low right joints hierarchy
        R_lowLipOutCtl, R_lowLipOutGrp, R_lowLipOutJnt = funcs.createJntAndParent(name = 'R_localLowLip', parent = self.r_localLowLipOutOrient_GRP,
                                                                                  side = 'R', up = False)
        R_lowLipOutCtl = mc.rename(R_lowLipOutCtl, 'R_localLowLipOut_CTL')
        R_lowLipOutGrp = mc.rename(R_lowLipOutGrp, 'R_localLowLipOutModify2_GRP')

        # create out low left joints hierarchy
        L_lowLipOutCtl, L_lowLipOutGrp, L_lowLipOutJnt = funcs.createJntAndParent(name = 'L_localLowLip', parent = self.l_localLowLipOutOrient_GRP, side = 'L',
                                                                                  up = False)
        L_lowLipOutCtl = mc.rename(L_lowLipOutCtl, 'L_localLowLipOut_CTL')
        L_lowLipOutGrp = mc.rename(L_lowLipOutGrp, 'L_localLowLipOutModify2_GRP')

        # create out low mid joints hierarchy
        M_lowLipOutCtl, M_lowLipOutGrp, M_lowLipOutJnt = funcs.createJntAndParent(name = 'M_localLowLip', parent = self.m_localLowLipOutOrient_GRP,
                                                                                  side = 'C', up = False)
        M_lowLipOutCtl = mc.rename(M_lowLipOutCtl, 'M_localLowLipOut_CTL')
        M_lowLipOutGrp = mc.rename(M_lowLipOutGrp, 'M_localLowLipOutModify2_GRP')

        # create left low joint hierarchy
        l_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='L_localLowLip', parent=self.leftLowMainJnt, middle=False)
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
        r_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='R_localLowLip', parent=self.rightLowMainJnt, middle=False)
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
        m_upLipCornerMod_loc = funcs.createMainHierarchyJnts(name='m_localLowLip', parent=self.middleLowMainJnt, middle=True)
        mc.parent(lowLipLowRezBindJnts[1],m_upLipCornerMod_loc)
        lowLipLowRezBindJnts[1] = lowLipLowRezBindJnts[1].split('|')[-1]

        # create middle low main ctl
        self.ctllowPlacement = mc.createNode('transform', name='localLowLipCtrlPlacement_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.ctllowPlacement,lowLipLowRezBindJnts[1])
        lowlipctl, lowlipctlgrp = funcs.createMiddleMainCtl(name = 'localLowLip', parent = self.ctllowPlacement,
                                                      snapJnt=lowLipLowRezBindJnts[1], side = 'C', up = False)
        lowlipctlgrp = mc.rename(lowlipctlgrp, 'localLowLipCtrlModify_GRP')

        # create left low main ctl
        self.leftLowLipCtlGrp = mc.createNode('transform', name='L_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.leftLowLipCtlGrp, lowLipLowRezBindJnts[2])
        leftLowmainCtls,leftLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.leftLowLipCtlGrp ,
                                                              snapJnt = lowLipLowRezBindJnts[2], side = 'L')
        leftCornerCtl = mc.rename(leftLowmainCtls[0], 'L_localLowLipCorner_CTL' )
        leftMinorCornerCtl = mc.rename(leftLowmainCtls[1], 'L_localLowLipCornerMinor_CTL' )
        leftCornerLowCtlGrp = mc.rename(leftLowMainCtlGrp[0], 'L_localLowLipCornerCtrlModify_GRP' )
        leftMinorCornerLowCtlGrp = mc.rename(leftLowMainCtlGrp[1], 'L_localLowLipCornerMinorModify_GRP' )

        # create right low main ctl
        self.rightLowLipCtlGrp = mc.createNode('transform', name='R_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.rightLowLipCtlGrp, lowLipLowRezBindJnts[0])
        rightLowmainCtls,rightLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.rightLowLipCtlGrp,
                                                                snapJnt = lowLipLowRezBindJnts[0], side = 'R')
        rightCornerCtl = mc.rename(rightLowmainCtls[0], 'R_localLowLipCorner_CTL' )
        rightMinorCornerCtl = mc.rename(rightLowmainCtls[1], 'R_localLowLipCornerMinor_CTL' )
        rightCornerLowCtlGrp = mc.rename(rightLowMainCtlGrp[0], 'R_localLowLipCornerCtrlModify_GRP' )
        rightMinorCornerLowCtlGrp = mc.rename(rightLowMainCtlGrp[1], 'R_localLowLipCornerMinorModify_GRP' )

        # create low roll
        self.lowLipCtlRoll = funcs.createRollHirarchy(name = 'localLowLip', parent = self.lowLipCtlGrp, up = False)

        # create zipper joints
        zipLowSecJnts = jntLib.create_on_curve(self.upLipZippercrv, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        funcs.createZipperJnts(name='localLowLip', crv=self.lowLipZippercrv, upCurve=self.tempCurve,
                         posJnts=zipLowSecJnts, parent = self.noTuchyLow, jntParent = self.lowMicroJntCtlGrp, up = False)
        # create locators under jntDriver
        funcs.createLocsJntDriver(name = 'R_localLowLip', parent =self.lowJntDrvr,  jntSnap = self.lowBindJnts[0])

        # duplicate the local rig
        output = trsLib.duplicate(self.upLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -20)
        mc.parent(output[0], self.facialCtrlGrp)
        output = trsLib.duplicate(self.lowLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -20)
        mc.parent(output[0], self.facialCtrlGrp)


