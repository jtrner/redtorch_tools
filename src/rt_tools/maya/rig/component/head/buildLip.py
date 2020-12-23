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
        self.upJntCtlLoc, self.upSquashMak = funcs.createCtlPlaceMent(name = 'localUpLip', parent = self.upjntCtlPlace)

        #create roll modify
        mc.move(0, 0.5,1.3, self.jntRollModupGrp, r=True, ws=True)
        self.jntUpRollLoc, self.upLipJntMidLoc = funcs.createRollMod(name = 'localUpLip', parent = self.jntRollModupGrp,up = True)

        self.upLipLowRezBindJnts = jntLib.create_on_curve(self.upLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius = 0.2)


        self.upmedRezBindJnts = []
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


        # create out up right joints hierarchy
        self.R_upLipOutCtl, self.R_upLipOutGrp, self.R_upLipOutJnt, self.R_upLipMidModLoc = funcs.createJntAndParent(name = 'R_localUpLip',
                                                                               parent = self.r_localUpLipOutOrient_GRP,
                                                                               side = 'R',up = True)
        self.R_upLipOutCtl = mc.rename(self.R_upLipOutCtl, 'R_localUpLipOut_CTL')
        self.R_upLipOutGrp = mc.rename(self.R_upLipOutGrp, 'R_localUpLipOutModify2_GRP')

        # create out up left joints hierarchy
        self.L_upLipOutCtl, self.L_upLipOutGrp, self.L_upLipOutJnt, self.L_upLipMidModLoc = funcs.createJntAndParent(name = 'L_localUpLip',
                                                                               parent = self.l_localUpLipOutOrient_GRP,
                                                                               side = 'L', up = True)
        self.L_upLipOutCtl = mc.rename(self.L_upLipOutCtl, 'L_localUpLipOut_CTL')
        self.L_upLipOutGrp = mc.rename(self.L_upLipOutGrp, 'L_localUpLipOutModify2_GRP')

        # create out up mid joints hierarchy
        self.M_upLipOutCtl, self.M_upLipOutGrp, self.M_upLipOutJnt,self.M_upLipMidModLoc = funcs.createJntAndParent(name = 'M_localUpLip',
                                                                               parent = self.m_localUpLipOutOrient_GRP,
                                                                               side = 'C',up = True)
        self.M_upLipOutCtl = mc.rename(self.M_upLipOutCtl, 'M_localUpLipOut_CTL')
        self.M_upLipOutGrp = mc.rename(self.M_upLipOutGrp, 'M_localUpLipOutModify2_GRP')

        # list for skinning to the up medrezCurve
        self.upmedRezBindJnts.append(self.upLipLowRezBindJnts[0])
        self.upmedRezBindJnts.append(self.upLipLowRezBindJnts[2])
        self.upmedRezBindJnts.append(self.R_upLipOutJnt)
        self.upmedRezBindJnts.append(self.L_upLipOutJnt)
        self.upmedRezBindJnts.append(self.M_upLipOutJnt)

        # create some nodes on upLowRez
        tempList = funcs.locOnCrv(name = 'result', parent = self.upLipJntLocLowGrp, numLocs = 3, crv = self.upLipLowRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.8,paramEnd = 0.3, upAxis = 'y', posJnts = self.upLipLowRezBindJnts)

        # rename transfomrs that driven by uplowRezCrv
        self.l_localUpLipDriverOutMod = mc.rename(tempList[0], 'L_localUpLipDriverOutModify_LOC')
        self.m_localUpLipDriverOutMod = mc.rename(tempList[1], 'm_localUpLipDriverOutModify_LOC')
        self.r_localUpLipDriverOutMod = mc.rename(tempList[2], 'r_localUpLipDriverOutModify_LOC')
        trsLib.match(self.r_localUpLipOutOrient_GRP, self.r_localUpLipDriverOutMod)
        trsLib.match(self.l_localUpLipOutOrient_GRP, self.l_localUpLipDriverOutMod)
        trsLib.match(self.m_localUpLipOutOrient_GRP, self.m_localUpLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.upLipMedRezcrv, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedUp, numLocs = 7, crv = self.upLipMedRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.upSecMod = mc.rename(tempList[0],'L_localUpLipMicroOutSecondaryModify_LOC')
        self.upmicroOutMod = mc.rename(tempList[1],'L_localUpLipMicroOutModify_LOC')
        self.upmidSecMod = mc.rename(tempList[2],'L_localUpLipMicroMidSecondaryModify_LOC')
        self.upMidMod = mc.rename(tempList[3],'localUpLipMicroMidModify_LOC')
        self.upMidSecModLoc = mc.rename(tempList[4],'R_localUpLipMicroMidSecondaryModify_LOC')
        self.microOutModLoc = mc.rename(tempList[5],'R_localUpLipMicroOutModify_LOC')
        self.microOutSecMod = mc.rename(tempList[6],'R_localUpLipMicroOutSecondaryModify_LOC')

        # create some nodes on HiRez
        tempJnts = jntLib.create_on_curve(self.upLipMedRezcrv, numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocHiUp, numLocs = 2, crv = self.upLipHiRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.97,paramEnd = 0.95, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.l_outUpTerModLocHi = mc.rename(tempList[0], 'L_localUpLipMicroOutTertiaryModify_LOC')
        self.r_outUpTerModLocHi = mc.rename(tempList[1], 'R_localUpLipMicroOutTertiaryModify_LOC')


        # create left up joint hierarchy
        self.l_upLipCornerMod_loc, self.leftUpMainMod = funcs.createMainHierarchyJnts(name='L_localUpLip', parent=self.leftUpMainJnt, middle=False)
        mc.parent(self.upLipLowRezBindJnts[2],self.l_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[2] = self.upLipLowRezBindJnts[2].split('|')[-1]
        [mc.setAttr(self.upLipLowRezBindJnts[2]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.upLipLowRezBindJnts[2] + '.jointOrientY', 0)

        l_upLip_rotdrvrLoc = mc.spaceLocator(name = 'L_localUpLipCorner_RotDrive_LOC')
        trsLib.match(l_upLip_rotdrvrLoc, t = self.upLipLowRezBindJnts[2])
        mc.parent(l_upLip_rotdrvrLoc, self.upLipLowRezBindJnts[2])

        self.l_upLip_cornerbnd = mc.spaceLocator(name = 'L_localUpLipcornerBnd_LOC')
        trsLib.match(self.l_upLip_cornerbnd, self.upLipLowRezBindJnts[2])
        mc.parent(self.l_upLip_cornerbnd, self.upLipLowRezBindJnts[2])
        self.l_upLip_cornerbnd = self.l_upLip_cornerbnd[0].split('|')[-1]

        self.upHirzBndJnts = []
        self.l_upLipcorner= mc.joint(self.l_upLip_cornerbnd, name = 'L_localUpLipCorner_BND', rad = 0.4 )
        self.l_upLipcornerminor = mc.joint(self.l_upLipcorner, name = 'L_localUpLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(self.l_upLipcornerminor + '.tx', 0.3)
        self.upHirzBndJnts.append(self.l_upLipcorner)

        # create right up joint hierarchy
        self.r_upLipCornerMod_loc, self.rightUpMainMod  = funcs.createMainHierarchyJnts(name='R_localUpLip', parent=self.rightUpMainJnt,  middle=False)
        mc.parent(self.upLipLowRezBindJnts[0],self.r_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[0] = self.upLipLowRezBindJnts[0].split('|')[-1]
        [mc.setAttr(self.upLipLowRezBindJnts[0]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.upLipLowRezBindJnts[0] + '.jointOrientY', 0)

        r_upLip_rotdrvrLoc = mc.spaceLocator(name = 'R_localUpLipCorner_RotDrive_LOC')
        trsLib.match(r_upLip_rotdrvrLoc, t = self.upLipLowRezBindJnts[0])
        mc.parent(r_upLip_rotdrvrLoc, self.upLipLowRezBindJnts[0])

        self.r_upLip_cornerbnd = mc.spaceLocator(name = 'R_localUpLipcornerBnd_LOC')
        trsLib.match(self.r_upLip_cornerbnd, self.upLipLowRezBindJnts[0])
        mc.parent(self.r_upLip_cornerbnd, self.upLipLowRezBindJnts[0])
        self.r_upLip_cornerbnd = self.r_upLip_cornerbnd[0].split('|')[-1]

        self.r_upLipcorner= mc.joint(self.r_upLip_cornerbnd, name = 'R_localUpLipCorner_BND', rad = 0.4 )
        self.r_upLipcornerminor = mc.joint(self.r_upLipcorner, name = 'R_localUpLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(self.r_upLipcornerminor + '.tx', 0.3)
        self.upHirzBndJnts.append(self.r_upLipcorner)


        # create middle up joint hierarchy
        self.m_upLipCornerMod_loc, self.middleUpMainMod  = funcs.createMainHierarchyJnts(name='m_localUpLip', parent= self.middleUpMainJnt,  middle=True)
        mc.parent(self.upLipLowRezBindJnts[1],self.m_upLipCornerMod_loc)
        self.upLipLowRezBindJnts[1] = self.upLipLowRezBindJnts[1].split('|')[-1]

        self.mouthCtlOr = mc.createNode('transform', name = 'mouthCtlOri_GRP', p = self.facialCtlGrp)
        trsLib.match( self.mouthCtlOr, self.mouthPiv)
        mc.setAttr(self.mouthCtlOr + '.tz', 6.5)
        mc.setAttr(self.mouthCtlOr + '.ty', 240.8)
        self.mouthCtl, self.mouthCtlGrp = funcs.createMouthCtl(name = 'mouthCtl', parent = self.mouthCtlOr,
                                                    snapJnt=self.mouthPiv, side = 'C')

        self.ctlupPlacement = mc.createNode('transform', name='localUpLipCtrlPlacement_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.ctlupPlacement, self.upLipLowRezBindJnts[1])
        self.uplipctl, self.uplipctlgrp, self.upsquashCtlMakro = funcs.createMiddleMainCtl(name = 'localUpLip', parent = self.ctlupPlacement ,
                                                    snapJnt=self.upLipLowRezBindJnts[1], side = 'C',up = True)
        self.uplipctlgrp = mc.rename(self.uplipctlgrp, 'localUpLipCtrlModify_GRP')

        # create left low main ctl
        self.leftUpLipCtlGrp = mc.createNode('transform', name= 'L_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.leftUpLipCtlGrp, self.upLipLowRezBindJnts[2])
        self.leftUpmainCtls,self.leftUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.leftUpLipCtlGrp ,
                                                              snapJnt = self.upLipLowRezBindJnts[2], side = 'L')
        self.leftUpCornerCtl = mc.rename(self.leftUpmainCtls[0], 'L_localUpLipCorner_CTL' )
        self.leftUpMinorCornerCtl = mc.rename(self.leftUpmainCtls[1], 'L_localUpLipCornerMinor_CTL' )
        self.leftCornerUpCtlGrp = mc.rename(self.leftUpMainCtlGrp[0], 'L_localUpLipCornerCtrlModify_GRP' )
        self.leftMinorCornerUpCtlGrp = mc.rename(self.leftUpMainCtlGrp[1], 'L_localUpLipCornerMinorModify_GRP' )

        # create right up main ctl
        self.rightUpLipCtlGrp = mc.createNode('transform', name='R_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.rightUpLipCtlGrp, self.upLipLowRezBindJnts[0])
        self.rightUpmainCtls,self.rightUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.rightUpLipCtlGrp,
                                                              snapJnt = self.upLipLowRezBindJnts[0], side = 'R')
        self.rightUpCornerCtl = mc.rename(self.rightUpmainCtls[0], 'R_localUpLipCorner_CTL' )
        self.rightUpMinorCornerCtl = mc.rename(self.rightUpmainCtls[1], 'R_localUpLipCornerMinor_CTL' )
        self.rightCornerLowCtlGrp = mc.rename(self.rightUpMainCtlGrp[0], 'R_localUpLipCornerCtrlModify_GRP' )
        self.rightMinorCornerLowCtlGrp = mc.rename(self.rightUpMainCtlGrp[1], 'R_localUpLipCornerMinorModify_GRP' )

        # create up roll
        self.upLipCtlRoll, self.upRoll_loc, self.upMidRollLoc = funcs.createRollHirarchy(name = 'localUpLip', parent = self.upLipCtlGrp, up = True)

        # create secondary zip joints
        zipUpSecJnts = jntLib.create_on_curve(self.upLipZippercrv, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        # create zipper joints
        self.upMicroJnts,self.upTerLocs,self.upTerOrientGrp,self.upZipOutBndGrp,self.upLocMod,self.microUpCtls,self.upZipJnts =  funcs.createZipperJnts(name='localUpLip',
                                                                                                         crv=self.upLipZippercrv,
                                                                                        upCurve=self.tempCurve,posJnts=zipUpSecJnts,
                                                                                  parent = self.noTuchyUp, jntParent = self.upMicroJntCtlGrp,
                                                                                  up = True)

        self.upLipMidLoc, self.r_upmidSecOr,self.r_upoutOrLoc,self.r_upcornerOr =  funcs.createLocsJntDriver(name = 'R_localUpLip',
                                                                            parent =self.upJntDrvr,  jntSnap = self.upBindJnts[0])

        #****************************************************lowPart******************************************

        #create roll modify
        mc.move(0, -0.5,1.3, self.jntRollModlowGrp, r=True, ws=True)
        self.jntLowRollLoc,self.lowLipJntMidLoc = funcs.createRollMod(name = 'localLowLip', parent = self.jntRollModlowGrp,up = False)

        # create ctlPlacement
        mc.move(0, 1, 5, self.lowjntCtlPlace, r=True, ws=True)
        self.lowJntCtlLoc, self.lowSquashMak = funcs.createCtlPlaceMent(name = 'localLowLip', parent = self.lowjntCtlPlace)

        self.lowLipLowRezBindJnts = jntLib.create_on_curve(self.lowLipLowRezcrv, numOfJoints = 3, parent = False, description='C_base', radius= 0.2)

        self.lowmedRezBindJnts = []
        self.lowLipLowRezBindJnts[0] = mc.rename(self.lowLipLowRezBindJnts[0],'R_localLowLipcorner_JNT')
        mc.setAttr(self.lowLipLowRezBindJnts[0] + '.ry', 130)
        self.lowLipLowRezBindJnts[1] = mc.rename(self.lowLipLowRezBindJnts[1],'localLowLipmain_JNT')
        self.lowLipLowRezBindJnts[2] = mc.rename(self.lowLipLowRezBindJnts[2],'L_localLowLipcorner_JNT')
        mc.setAttr(self.lowLipLowRezBindJnts[2] + '.ry', 50)

        trsLib.match(self.leftLowMainJnt, self.lowLipLowRezBindJnts[2])
        trsLib.match(self.rightLowMainJnt, self.lowLipLowRezBindJnts[0])
        trsLib.match(self.middleLowMainJnt, self.lowLipLowRezBindJnts[1])

        # create out low right joints hierarchy
        self.R_lowLipOutCtl, self.R_lowLipOutGrp, self.R_lowLipOutJnt,self.R_lowLipMidModLoc = funcs.createJntAndParent(name = 'R_localLowLip', parent = self.r_localLowLipOutOrient_GRP,
                                                                                  side = 'R', up = False)
        self.R_lowLipOutCtl = mc.rename(self.R_lowLipOutCtl, 'R_localLowLipOut_CTL')
        self.R_lowLipOutGrp = mc.rename(self.R_lowLipOutGrp, 'R_localLowLipOutModify2_GRP')

        # create out low left joints hierarchy
        self.L_lowLipOutCtl, self.L_lowLipOutGrp, self.L_lowLipOutJnt,self.L_lowLipMidModLoc = funcs.createJntAndParent(name = 'L_localLowLip', parent = self.l_localLowLipOutOrient_GRP, side = 'L',
                                                                                  up = False)
        self.L_lowLipOutCtl = mc.rename(self.L_lowLipOutCtl, 'L_localLowLipOut_CTL')
        self.L_lowLipOutGrp = mc.rename(self.L_lowLipOutGrp, 'L_localLowLipOutModify2_GRP')

        # create out low mid joints hierarchy
        self.M_lowLipOutCtl, self.M_lowLipOutGrp, self.M_lowLipOutJnt, self.M_lowLipMidModLoc = funcs.createJntAndParent(name = 'M_localLowLip', parent = self.m_localLowLipOutOrient_GRP,
                                                                                  side = 'C', up = False)
        self.M_lowLipOutCtl = mc.rename(self.M_lowLipOutCtl, 'M_localLowLipOut_CTL')
        self.M_lowLipOutGrp = mc.rename(self.M_lowLipOutGrp, 'M_localLowLipOutModify2_GRP')

        # list for skinning to the up medrezCurve
        self.lowmedRezBindJnts.append(self.lowLipLowRezBindJnts[0])
        self.lowmedRezBindJnts.append(self.lowLipLowRezBindJnts[2])
        self.lowmedRezBindJnts.append(self.R_lowLipOutJnt)
        self.lowmedRezBindJnts.append(self.L_lowLipOutJnt)
        self.lowmedRezBindJnts.append(self.M_lowLipOutJnt)

        # create some nodes on LowRez
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLipJntLocLowGrp, numLocs = 3, crv = self.lowLipLowRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.8,paramEnd = 0.3, upAxis = 'y', posJnts = self.lowLipLowRezBindJnts)

        # rename transfomrs that driven by lowRezCrv
        self.l_localLowLipDriverOutMod = mc.rename(tempList[0], 'L_localLowLipDriverOutModify_LOC')
        self.m_localLowLipDriverOutMod = mc.rename(tempList[1], 'm_localLowLipDriverOutModify_LOC')
        self.r_localLowLipDriverOutMod = mc.rename(tempList[2], 'r_localLowLipDriverOutModify_LOC')

        trsLib.match(self.r_localLowLipOutOrient_GRP, self.r_localLowLipDriverOutMod)
        trsLib.match(self.l_localLowLipOutOrient_GRP, self.l_localLowLipDriverOutMod)
        trsLib.match(self.m_localLowLipOutOrient_GRP, self.m_localLowLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezcrv, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedLow, numLocs = 7, crv = self.lowLipMedRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.lowSecMod = mc.rename(tempList[0],'L_localLowLipMicroOutSecondaryModify_LOC')
        self.lowmicroOutMod = mc.rename(tempList[1],'L_localLowLipMicroOutModify_LOC')
        self.lowmidSecMod = mc.rename(tempList[2],'L_localLowLipMicroMidSecondaryModify_LOC')
        self.lowMidMod = mc.rename(tempList[3],'localLowLipMicroMidModify_LOC')
        self.lowMidSecModLoc = mc.rename(tempList[4],'R_localLowLipMicroMidSecondaryModify_LOC')
        self.lowmicroOutModLoc = mc.rename(tempList[5],'R_localLowLipMicroOutModify_LOC')
        self.lowmicroOutSecMod = mc.rename(tempList[6],'R_localLowLipMicroOutSecondaryModify_LOC')

        # create some nodes on HiRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezcrv, numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocHiLow, numLocs = 2, crv = self.lowLipHiRezcrv,
                     upCurve = self.tempCurve, paramStart = 0.97,paramEnd = 0.95, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.l_outLowTerModLocHi = mc.rename(tempList[0], 'L_localLowLipMicroOutTertiaryModify_LOC')
        self.r_outLowTerModLocHi = mc.rename(tempList[1], 'R_localLowLipMicroOutTertiaryModify_LOC')


        # create left low joint hierarchy
        self.l_lowLipCornerMod_loc, self.leftLowMainMod  = funcs.createMainHierarchyJnts(name='L_localLowLip', parent=self.leftLowMainJnt, middle=False)
        mc.parent(self.lowLipLowRezBindJnts[2],self.l_lowLipCornerMod_loc)
        self.lowLipLowRezBindJnts[2] = self.lowLipLowRezBindJnts[2].split('|')[-1]
        [mc.setAttr(self.lowLipLowRezBindJnts[2]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.lowLipLowRezBindJnts[2] + '.jointOrientY', 0)

        l_LowLip_rotdrvrLoc = mc.spaceLocator(name = 'L_localLowLipCorner_RotDrive_LOC')
        trsLib.match(l_LowLip_rotdrvrLoc, t = self.lowLipLowRezBindJnts[2])
        mc.parent(l_LowLip_rotdrvrLoc, self.lowLipLowRezBindJnts[2])

        self.l_lowLip_cornerbnd = mc.spaceLocator(name = 'L_localLowLipcornerBnd_LOC')
        trsLib.match(self.l_lowLip_cornerbnd, self.lowLipLowRezBindJnts[2])
        mc.parent(self.l_lowLip_cornerbnd, self.lowLipLowRezBindJnts[2])
        self.l_lowLip_cornerbnd = self.l_lowLip_cornerbnd[0].split('|')[-1]

        self.lowHirzBndJnts = []
        self.l_lowLipcorner= mc.joint(self.l_lowLip_cornerbnd, name = 'L_localLowLipCorner_BND', rad = 0.4 )
        self.l_lowLipcornerminor = mc.joint(self.l_lowLipcorner, name = 'L_localLowLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(self.l_lowLipcornerminor + '.tx', 0.3)
        self.lowHirzBndJnts.append(self.l_lowLipcorner)


        # create right low joint hierarchy
        self.r_lowLipCornerMod_loc , self.rightLowMainMod = funcs.createMainHierarchyJnts(name='R_localLowLip', parent=self.rightLowMainJnt, middle=False)
        mc.parent(self.lowLipLowRezBindJnts[0],self.r_lowLipCornerMod_loc)
        self.lowLipLowRezBindJnts[0] = self.lowLipLowRezBindJnts[0].split('|')[-1]
        [mc.setAttr(self.lowLipLowRezBindJnts[0]+ '.{}{}'.format(r,a), 0) for r in 'r' for a in 'xyz']
        mc.setAttr(self.lowLipLowRezBindJnts[0] + '.jointOrientY', 0)

        r_lowLip_rotdrvrLoc = mc.spaceLocator(name = 'R_localLowLipCorner_RotDrive_LOC')
        trsLib.match(r_lowLip_rotdrvrLoc, t = self.lowLipLowRezBindJnts[0])
        mc.parent(r_lowLip_rotdrvrLoc, self.lowLipLowRezBindJnts[0])

        self.r_lowLip_cornerbnd = mc.spaceLocator(name = 'R_localLowLipcornerBnd_LOC')
        trsLib.match(self.r_lowLip_cornerbnd, self.lowLipLowRezBindJnts[0])
        mc.parent(self.r_lowLip_cornerbnd, self.lowLipLowRezBindJnts[0])
        self.r_lowLip_cornerbnd = self.r_lowLip_cornerbnd[0].split('|')[-1]

        self.r_LowLipcorner= mc.joint(self.r_lowLip_cornerbnd, name = 'R_localLowLipCorner_BND', rad = 0.4 )
        self.r_upLipcornerminor = mc.joint(self.r_LowLipcorner, name = 'R_localLowLipCornerMinor_BND' ,  rad = 0.4)
        mc.setAttr(self.r_upLipcornerminor + '.tx', 0.3)
        self.lowHirzBndJnts.append(self.r_LowLipcorner)


        # create middle low joint hierarchy
        self.m_lowLipCornerMod_loc, self.midLowMainMod  = funcs.createMainHierarchyJnts(name='m_localLowLip', parent=self.middleLowMainJnt, middle=True)
        mc.parent(self.lowLipLowRezBindJnts[1],self.m_lowLipCornerMod_loc)
        self.lowLipLowRezBindJnts[1] = self.lowLipLowRezBindJnts[1].split('|')[-1]

        # create middle low main ctl
        self.ctllowPlacement = mc.createNode('transform', name='localLowLipCtrlPlacement_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.ctllowPlacement,self.lowLipLowRezBindJnts[1])
        self.lowlipctl, self.lowlipctlgrp, self.lowsquashCtlMakro = funcs.createMiddleMainCtl(name = 'localLowLip', parent = self.ctllowPlacement,
                                                      snapJnt=self.lowLipLowRezBindJnts[1], side = 'C', up = False)
        self.lowlipctlgrp = mc.rename(self.lowlipctlgrp, 'localLowLipCtrlModify_GRP')

        # create left low main ctl
        self.leftLowLipCtlGrp = mc.createNode('transform', name='L_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.leftLowLipCtlGrp, self.lowLipLowRezBindJnts[2])
        self.leftLowmainCtls,self.leftLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.leftLowLipCtlGrp ,
                                                              snapJnt = self.lowLipLowRezBindJnts[2], side = 'L')
        self.leftLowCornerCtl = mc.rename(self.leftLowmainCtls[0], 'L_localLowLipCorner_CTL' )
        self.leftLowMinorCornerCtl = mc.rename(self.leftLowmainCtls[1], 'L_localLowLipCornerMinor_CTL' )
        self.leftCornerLowCtlGrp = mc.rename(self.leftLowMainCtlGrp[0], 'L_localLowLipCornerCtrlModify_GRP' )
        self.leftMinorCornerLowCtlGrp = mc.rename(self.leftLowMainCtlGrp[1], 'L_localLowLipCornerMinorModify_GRP' )

        # create right low main ctl
        self.rightLowLipCtlGrp = mc.createNode('transform', name='R_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.rightLowLipCtlGrp, self.lowLipLowRezBindJnts[0])
        self.rightLowmainCtls,self.rightLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.rightLowLipCtlGrp,
                                                                snapJnt = self.lowLipLowRezBindJnts[0], side = 'R')
        self.rightLowCornerCtl = mc.rename(self.rightLowmainCtls[0], 'R_localLowLipCorner_CTL' )
        self.rightLowMinorCornerCtl = mc.rename(self.rightLowmainCtls[1], 'R_localLowLipCornerMinor_CTL' )
        self.rightCornerLowCtlGrp = mc.rename(self.rightLowMainCtlGrp[0], 'R_localLowLipCornerCtrlModify_GRP' )
        self.rightMinorCornerLowCtlGrp = mc.rename(self.rightLowMainCtlGrp[1], 'R_localLowLipCornerMinorModify_GRP' )

        # create low roll
        self.lowLipCtlRoll, self.lowRoll_loc, self.lowMidRollLoc = funcs.createRollHirarchy(name = 'localLowLip', parent = self.lowLipCtlGrp, up = False)

        # create zipper joints
        zipLowSecJnts = jntLib.create_on_curve(self.upLipZippercrv, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        self.lowMicroJnts, self.lowTerLocs,self.lowTerOrientGrp,self.lowZipOutBndGrp,self.lowLocMod ,self.microLowCtls,self.lowZipJnts = funcs.createZipperJnts(name='localLowLip',
                                                                                                              crv=self.lowLipZippercrv, upCurve=self.tempCurve,
                         posJnts=zipLowSecJnts, parent = self.noTuchyLow, jntParent = self.lowMicroJntCtlGrp, up = False)
        # create locators under jntDriver
        self.lowLipMidLoc, self.r_lowmidSecOr,self.r_lowoutOrLoc,self.r_lowcornerOr = funcs.createLocsJntDriver(name = 'R_localLowLip',
                                                                                 parent =self.lowJntDrvr,  jntSnap = self.lowBindJnts[0])

        # create nose ctls
        self.noseCtl, self.noseCtlBase, self.columellaCtl = funcs.createNoseCtls(name = 'noseCtl',
                                                                                 parent = self.noseCtlGrp,
                                                                                 mainSnap = self.mouthAndJawMain[3],
                                                                                 cummelaSnap = self.mouthAndJawMain[4],
                                                                                 leftSnap = self.leftnostrils[0] ,
                                                                                 rightSnap = self.rightnostrils[0])

        # create jaw ctls
        self.jawCtlOriGrp = mc.createNode('transform' ,name = 'jawCtlOri_GRP', p = self.facialCtlGrp)
        trsLib.match(self.jawCtlOriGrp, self.mouthAndJawMain[1])
        self.jawCtlMakroGrp = mc.createNode('transform', name = 'jawCtlMakr_GRP', p = self.jawCtlOriGrp)

        ctl,grp = funcs.createCtl(parent = self.jawCtlMakroGrp, side = self.side )
        self.jawCtlModGrp = mc.rename(grp, 'jawCtlMod_GRP')
        self.jawCtl = mc.rename(ctl, 'jaw_CTL')
        mc.parent(self.jawCtlModGrp,self.jawCtlMakroGrp)

        self.jawCtlSecondaryCtlOriGrp = mc.createNode('transform', name = 'jawSecondaryCtlOri_GRP', p = self.jawCtl)
        trsLib.match(self.jawCtlSecondaryCtlOriGrp,self.jawSecBndJnt[0] )

        ctl,grp = funcs.createCtl(parent = self.jawCtlSecondaryCtlOriGrp , side = self.side)
        self.jawSecModCtlGrp = mc.rename(grp, 'jawSecondaryCtlMod_GRP')
        self.jawSecCtl = mc.rename(ctl, 'jawSecondary_CTL')
        mc.parent(self.jawSecModCtlGrp ,self.jawCtlSecondaryCtlOriGrp)

        ctl,grp = funcs.createCtl(parent = self.jawSecBndJnt[2], side = self.side)
        self.mentalisModCtlGrp = mc.rename(grp, 'mentalisCtlMod_GRP')
        self.mentalisCtl = mc.rename(ctl, 'mentalis_CTL')
        mc.parent(self.mentalisModCtlGrp, self.jawSecCtl)

        ctl,grp = funcs.createCtl(parent = self.jawSecBndJnt[1], side = self.side)
        self.chinModCtlGrp = mc.rename(grp, 'chinCtlMod_GRP')
        self.chinCtl = mc.rename(ctl, 'chin_CTL')
        mc.parent(self.chinModCtlGrp, self.jawSecCtl)

        self.jaw2ndFollowLoc = mc.createNode('transform', name = 'jaw2ndFollow_LOC',p = self.jawSecBndJnt[0])
        self.jaw2ndFollowLocShape = mc.createNode('transform', name = 'jaw2ndFollowShape_LOC',p = self.jaw2ndFollowLoc)
        self.lowMouthGrp = mc.createNode('transform', name = 'lowMouth_GRP')



        mc.parent(self.lowMouthGrp ,self.jaw2ndFollowLoc )



        # duplicate the local rig
        output = trsLib.duplicate(self.upLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -20)
        #mc.makeIdentity(output[0], apply = True, t = True)
        mc.parent(output[0], self.facialCtlGrp)
        output = trsLib.duplicate(self.lowLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -20)
        #mc.makeIdentity(output[0], apply = True, t = True)
        mc.parent(output[0], self.facialCtlGrp)



