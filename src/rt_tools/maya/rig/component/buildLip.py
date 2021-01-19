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
                        'localupLipStart':'localupLipStart',
                        'localupLipEnd':'localupLipEnd',
                        'locallowLipStart':'locallowLipStart',
                        'locallowLipEnd':'locallowLipEnd',
                        'nose': 'nose',
                        'columella': 'columella',
                        'leftnostril': 'leftnostril',
                        'leftnostrilFlare': 'leftnostrilFlare',
                        'rightnostril': 'rightnostril',
                        'rightnostrilFlare': 'rightnostrilFlare',
                        'tongueBase':'tongueBase',
                        'tongue_01':'tongue_01',
                        'tongue_02':'tongue_02',
                        'tongue_03':'tongue_03',
                        'tongue_04':'tongue_04',
                        'tongue_05':'tongue_05',
                        'topTeeth': 'topTeeth',
                        'lowTeeth': 'lowTeeth',
                        'upTeethWireMid':'upTeethWireMid',
                        'upTeethWireLeft':'upTeethWireLeft',
                        'upTeethWireRight':'upTeethWireRight',
                        'lowTeethWireMid':'lowTeethWireMid',
                        'lowTeethWireLeft':'lowTeethWireLeft',
                        'lowTeethWireRight':'lowTeethWireRight',}

    def createBlueprint(self):
        super(BuildLip, self).createBlueprint()
        par = self.blueprintGrp
        self.noseSide = 'R'
        mult = [-1, 1][self.noseSide == 'R']
        self.blueprints['mouthFlood'] = '{}_mouthFlood_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mouthFlood']):
            mc.joint(self.blueprintGrp, name = self.blueprints['mouthFlood'])
            mc.xform(self.blueprints['mouthFlood'], ws = True, t = (0, self.movement + 180, -3))

        self.blueprints['jawMain'] = '{}_jawMain_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['jawMain']):
            mc.joint(self.blueprintGrp, name = self.blueprints['jawMain'])
            mc.xform(self.blueprints['jawMain'], ws = True, t = (0, self.movement + 175, -12))

        self.blueprints['jawSecondary'] = '{}_jawSecondary_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['jawSecondary']):
            mc.joint(self.blueprintGrp, name = self.blueprints['jawSecondary'])
            mc.xform(self.blueprints['jawSecondary'], ws = True, t = (0, self.movement + 170, -3.5))

        self.blueprints['chin'] = '{}_chin_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['chin']):
            mc.joint(self.blueprints['jawSecondary'] , name = self.blueprints['chin'])
            mc.xform(self.blueprints['chin'], ws = True, t = (0, self.movement + 165, 3))

        self.blueprints['mentalis'] = '{}_mentalis_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mentalis']):
            mc.joint(self.blueprints['jawSecondary'] , name = self.blueprints['mentalis'])
            mc.xform(self.blueprints['mentalis'], ws = True, t = (0, self.movement + 169, 2.8))

        self.blueprints['mouth'] = '{}_mouth_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['mouth']):
            mc.joint(self.blueprintGrp, name = self.blueprints['mouth'])
            mc.xform(self.blueprints['mouth'], ws = True, t = (0, self.movement + 171, 1.52))

        self.blueprints['localupLipStart'] = '{}_localupLipStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['localupLipStart']):
            mc.joint(self.blueprintGrp, name = self.blueprints['localupLipStart'])
            mc.xform(self.blueprints['localupLipStart'], ws = True, t = (0, self.movement + 171, 1.52))

        self.blueprints['localupLipEnd'] = '{}_localupLipEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['localupLipEnd']):
            mc.joint(self.blueprints['localupLipStart'], name = self.blueprints['localupLipEnd'])
            mc.xform(self.blueprints['localupLipEnd'], ws = True, t = (0, self.movement + 171, 3.52))

        self.blueprints['locallowLipStart'] = '{}_locallowLipStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['locallowLipStart']):
            mc.joint(self.blueprintGrp, name = self.blueprints['locallowLipStart'])
            mc.xform(self.blueprints['locallowLipStart'], ws = True, t = (0, self.movement + 171, 1.52))

        self.blueprints['locallowLipEnd'] = '{}_locallowLipEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['locallowLipEnd']):
            mc.joint(self.blueprints['locallowLipStart'], name = self.blueprints['locallowLipEnd'])
            mc.xform(self.blueprints['locallowLipEnd'], ws = True, t = (0, self.movement + 171, 3.52))

        self.blueprints['nose'] = '{}_nose_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['nose']):
            mc.joint(self.blueprintGrp, name = self.blueprints['nose'])
            mc.xform(self.blueprints['nose'], ws = True, t = (0, self.movement + 174, 4.3))

        self.blueprints['columella'] = '{}_columella_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['columella']):
            mc.joint(self.blueprintGrp, name = self.blueprints['columella'])
            mc.xform(self.blueprints['columella'], ws = True, t = (0, self.movement + 173, 4.3))

        self.blueprints['leftnostril'] = '{}_leftnostril_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftnostril']):
            mc.joint(self.blueprintGrp, name = self.blueprints['leftnostril'])
            mc.xform(self.blueprints['leftnostril'], ws = True, t = (1,self.movement  + 173.5, 3.7))

        self.blueprints['leftnostrilFlare'] = '{}_leftnostrilFlare_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftnostrilFlare']):
            mc.joint(self.blueprints['leftnostril'] , name = self.blueprints['leftnostrilFlare'])
            mc.xform(self.blueprints['leftnostrilFlare'], ws = True, t = (0.5, self.movement  + 173, 5.5))

        self.blueprints['rightnostril'] = '{}_rightnostril_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightnostril']):
            mc.joint(self.blueprintGrp, name = self.blueprints['rightnostril'])
            mc.xform(self.blueprints['rightnostril'], ws = True, t = (-1,self.movement  + 173.5, 3.7))

        self.blueprints['rightnostrilFlare'] = '{}_rightnostrilFlare_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightnostrilFlare']):
            mc.joint(self.blueprints['rightnostril'] , name = self.blueprints['rightnostrilFlare'])
            mc.xform(self.blueprints['rightnostrilFlare'], ws = True, t = (-0.5, self.movement  + 173, 5.5))

        self.blueprints['tongueBase'] = '{}_tongueBase_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongueBase']):
            mc.joint(self.blueprintGrp, name = self.blueprints['tongueBase'])
            mc.xform(self.blueprints['tongueBase'], ws = True, t = (0, self.movement + 90.5, -2.437))

        self.blueprints['tongue_01'] = '{}_tongue_01_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongue_01']):
            mc.joint(self.blueprints['tongueBase'], name = self.blueprints['tongue_01'])
            mc.xform(self.blueprints['tongue_01'], ws = True, t = (0, self.movement + 90.5, -1.041))

        self.blueprints['tongue_02'] = '{}_tongue_02_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongue_02']):
            mc.joint(self.blueprints['tongue_01'], name = self.blueprints['tongue_02'])
            mc.xform(self.blueprints['tongue_02'], ws = True, t = (0, self.movement + 90.5, 0.255))

        self.blueprints['tongue_03'] = '{}_tongue_03_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongue_03']):
            mc.joint(self.blueprints['tongue_02'], name = self.blueprints['tongue_03'])
            mc.xform(self.blueprints['tongue_03'], ws = True, t = (0, self.movement + 90.5, 1.554))

        self.blueprints['tongue_04'] = '{}_tongue_04_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongue_04']):
            mc.joint(self.blueprints['tongue_03'], name = self.blueprints['tongue_04'])
            mc.xform(self.blueprints['tongue_04'], ws = True, t = (0, self.movement + 90.5, 2.69))

        self.blueprints['tongue_05'] = '{}_tongue_05_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tongue_05']):
            mc.joint(self.blueprints['tongue_04'], name = self.blueprints['tongue_05'])
            mc.xform(self.blueprints['tongue_05'], ws = True, t = (0, self.movement + 90.5, 3.648))

        self.blueprints['topTeeth'] = '{}_topTeeth_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['topTeeth']):
            mc.joint(self.blueprintGrp, name = self.blueprints['topTeeth'])
            mc.xform(self.blueprints['topTeeth'], ws = True, t = (0, self.movement + 91.5, 3.466))

        self.blueprints['lowTeeth'] = '{}_lowTeeth_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['lowTeeth']):
            mc.joint(self.blueprintGrp, name = self.blueprints['lowTeeth'])
            mc.xform(self.blueprints['lowTeeth'], ws = True, t = (0, self.movement + 90, 3.466))

        self.blueprints['upTeethWireMid'] = '{}_upTeethWireMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upTeethWireMid']):
            mc.joint(self.blueprintGrp, name = self.blueprints['upTeethWireMid'])
            mc.xform(self.blueprints['upTeethWireMid'], ws = True, t = (0, self.movement + 91.5, 3.444))

        self.blueprints['upTeethWireLeft'] = '{}_upTeethWireLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upTeethWireLeft']):
            mc.joint(self.blueprintGrp, name = self.blueprints['upTeethWireLeft'])
            mc.xform(self.blueprints['upTeethWireLeft'], ws = True, t = (3.755, self.movement + 91.5,-1.083))

        self.blueprints['upTeethWireRight'] = '{}_upTeethWireRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upTeethWireRight']):
            mc.joint(self.blueprintGrp, name = self.blueprints['upTeethWireRight'])
            mc.xform(self.blueprints['upTeethWireRight'], ws = True, t = (-3.755, self.movement + 91.5, -1.083))

        self.blueprints['lowTeethWireMid'] = '{}_lowTeethWireMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['lowTeethWireMid']):
            mc.joint(self.blueprintGrp, name = self.blueprints['lowTeethWireMid'])
            mc.xform(self.blueprints['lowTeethWireMid'], ws = True, t = (0, self.movement + 90, 3.444))

        self.blueprints['lowTeethWireLeft'] = '{}_lowTeethWireLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['lowTeethWireLeft']):
            mc.joint(self.blueprintGrp, name = self.blueprints['lowTeethWireLeft'])
            mc.xform(self.blueprints['lowTeethWireLeft'], ws = True, t = (3.755, self.movement + 90,-1.083))

        self.blueprints['lowTeethWireRight'] = '{}_lowTeethWireRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['lowTeethWireRight']):
            mc.joint(self.blueprintGrp, name = self.blueprints['lowTeethWireRight'])
            mc.xform(self.blueprints['lowTeethWireRight'], ws = True, t = (-3.755, self.movement + 90, -1.083))


    def createJoints(self):
        par = self.moduleGrp
        self.upTeethWire = []
        for alias, blu in self.blueprints.items():
            if not alias in ('upTeethWireMid','upTeethWireLeft', 'upTeethWireRight'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.upTeethWire.append(jnt)
        self.lowTeethWire = []
        for alias, blu in self.blueprints.items():
            if not alias in ('lowTeethWireMid', 'lowTeethWireLeft','lowTeethWireRight',):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lowTeethWire.append(jnt)

        par = self.moduleGrp
        self.teethJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('topTeeth', 'lowTeeth'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.teethJnts.append(jnt)

        par = self.moduleGrp
        self.upLipBindJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('localupLipStart', 'localupLipEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.upLipBindJnts.append(jnt)

        self.orientJnts(self.upLipBindJnts)
        mc.parent(self.upLipBindJnts[-1], world = True)

        par = self.moduleGrp
        self.lowLipBindJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('locallowLipStart', 'locallowLipEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lowLipBindJnts.append(jnt)

        self.orientJnts(self.lowLipBindJnts)
        mc.parent(self.lowLipBindJnts[-1], world=True)


        par = self.moduleGrp
        self.tongueJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('tongueBase', 'tongue_01', 'tongue_02', 'tongue_03', 'tongue_04', 'tongue_05'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.tongueJnts.append(jnt)
            par = jnt

        self.orientJnts(self.tongueJnts)


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

        self.orientJnts(self.leftnostrils)

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

        self.orientJnts(self.rightnostrils)


    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='z', upAxes='y')
        mc.delete(upLoc)


    def build(self):
        super(BuildLip, self).build()

        # connect edge datas to the curves
        self.upperTeethEdge = crvLib.edgeToCurve(geo = self.upperteeth, edges =self.upperTeethEdge, name ='localupTeeth')
        self.lowerTeethEdge = crvLib.edgeToCurve(geo = self.lowerteeth, edges = self.lowerTeethEdge, name ='locallowTeeth')
        self.zipperCrvEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.zipperCrvEdge, name ='localzipper')
        self.uplipLowRezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.uplipLowRezEdge, name ='localupLipLowRez')
        self.uplipMedRezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.uplipMedRezEdge, name ='localupLipMedRez')
        self.uplipHirezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.uplipHirezEdge, name ='localupLipHiRez')
        self.uplipZipperEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.uplipZipperEdge, name ='localupLipZipper')
        self.lowLipLowRezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.lowLipLowRezEdge, name ='locallowLipLowRez')
        self.lowLipHirezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.lowLipHirezEdge, name ='locallowLipHiRez')
        self.lowLipMedRezEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.lowLipMedRezEdge, name ='locallowLipMedRez')
        self.lowLipZipperEdge = crvLib.edgeToCurve(geo = self.lipsGeo, edges = self.lowLipZipperEdge, name = 'locallowLipZipper')

        for i in [self.upperTeethEdge,self.lowerTeethEdge,self.zipperCrvEdge,self.uplipLowRezEdge,self.uplipMedRezEdge,
                  self.uplipHirezEdge,self.uplipZipperEdge,self.lowLipLowRezEdge,self.lowLipHirezEdge,
                  self.lowLipMedRezEdge,self.lowLipZipperEdge]:
            mc.select(i, r = True)
            crv = mc.rebuildCurve(i, ch= False, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=0, kt=1, s=6, d=3, tol=0.01)[0]
            tempJnts = jntLib.create_on_curve(curve=crv, numOfJoints=3, parent=False, description='C_base', radius=1)
            startTx = mc.getAttr(tempJnts[0] + '.tx')
            endTx = mc.getAttr(tempJnts[-1] + '.tx')
            if startTx > endTx:
                crv = mc.reverseCurve(crv, ch=1, rpo=1)[0]
            i = crv
            mc.delete(tempJnts)
            center = mc.objectCenter(i, gl = True)
            mc.xform(i , pivots=center)

        self.tempCurve = mc.duplicate(self.uplipLowRezEdge)[0]
        [mc.setAttr(self.tempCurve + '.{}{}'.format(a,v), lock = False) for a in 'trs' for v in 'xyz']
        mc.setAttr(self.tempCurve + '.ty', 10)

        # create mouth control pivot
        #mc.joint(self.mouthPiv, name = 'MouthCtrlPivot_JNT', rad = 1.2)

        #****************************************************upPart******************************************
        mc.move(0, 0, 0, self.upjntCtlPlace, r=True, ws=True)
        self.upJntCtlLoc, self.upSquashMak = funcs.createCtlPlaceMent(name = 'localUpLip', parent = self.upjntCtlPlace)

        #create roll modify
        mc.move(0, 0.5,-2, self.jntRollModupGrp, r=True, ws=True)
        self.jntUpRollLoc, self.upLipJntMidLoc = funcs.createRollMod(name = 'localUpLip', parent = self.jntRollModupGrp,up = True)

        self.upLipLowRezBindJnts = jntLib.create_on_curve(self.uplipLowRezEdge, numOfJoints = 3, parent = False, description='C_base', radius = 0.2)


        self.upmedRezBindJnts = []
        self.upLipLowRezBindJnts[0] = mc.rename(self.upLipLowRezBindJnts[0],'R_localUpLipcorner_JNT')
        mc.setAttr(self.upLipLowRezBindJnts[0] + '.ry', 130)
        self.upLipLowRezBindJnts[1] = mc.rename(self.upLipLowRezBindJnts[1],'localUpLipmain_JNT')
        self.upLipLowRezBindJnts[2] = mc.rename(self.upLipLowRezBindJnts[2],'L_localUpLipcorner_JNT')
        mc.setAttr(self.upLipLowRezBindJnts[2] + '.ry', 50)


        # matches nodes from lips template to the side joints
        trsLib.match(self.leftUpMainJnt, t = self.upLipLowRezBindJnts[2],r = self.upLipLowRezBindJnts[2])
        trsLib.match(self.rightUpMainJnt, t = self.upLipLowRezBindJnts[0],r = self.upLipLowRezBindJnts[0])
        trsLib.match(self.middleUpMainJnt, t = self.upLipLowRezBindJnts[1],r = self.upLipLowRezBindJnts[1])

        trsLib.match(self.r_lipCornerMakroDrvr , t = self.upLipLowRezBindJnts[0],r = self.upLipLowRezBindJnts[0])
        mc.move(10,0,0,self.r_lipCornerMakroDrvr , r = True, ws = True)
        trsLib.match(self.l_lipCornerMakroDrvr , t = self.upLipLowRezBindJnts[2],r = self.upLipLowRezBindJnts[2])
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
        tempList = funcs.locOnCrv(name = 'result', parent = self.upLipJntLocLowGrp, numLocs = 3, crv = self.uplipLowRezEdge,
                                  upCurve = self.tempCurve, paramStart = 4.5, paramEnd = 1.5, upAxis = 'y', posJnts = self.upLipLowRezBindJnts)

        # rename transfomrs that driven by uplowRezCrv
        self.l_localUpLipDriverOutMod = mc.rename(tempList[0], 'L_localUpLipDriverOutModify_LOC')
        self.m_localUpLipDriverOutMod = mc.rename(tempList[1], 'm_localUpLipDriverOutModify_LOC')
        self.r_localUpLipDriverOutMod = mc.rename(tempList[2], 'r_localUpLipDriverOutModify_LOC')

        trsLib.match(self.r_localUpLipOutOrient_GRP, t =self.r_localUpLipDriverOutMod,r = self.r_localUpLipDriverOutMod)
        trsLib.match(self.l_localUpLipOutOrient_GRP, t = self.l_localUpLipDriverOutMod,r = self.l_localUpLipDriverOutMod)
        trsLib.match(self.m_localUpLipOutOrient_GRP, t = self.m_localUpLipDriverOutMod,r = self.m_localUpLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.uplipMedRezEdge, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedUp, numLocs = 7, crv = self.uplipMedRezEdge,
                                  upCurve = self.tempCurve, paramStart = 5.4, paramEnd = 0.80, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        
        self.upSecMod = mc.rename(tempList[0],'L_localUpLipMicroOutSecondaryModify_LOC')
        self.upmicroOutMod = mc.rename(tempList[1],'L_localUpLipMicroOutModify_LOC')
        self.upmidSecMod = mc.rename(tempList[2],'L_localUpLipMicroMidSecondaryModify_LOC')
        self.upMidMod = mc.rename(tempList[3],'localUpLipMicroMidModify_LOC')
        self.upMidSecModLoc = mc.rename(tempList[4],'R_localUpLipMicroMidSecondaryModify_LOC')
        self.microOutModLoc = mc.rename(tempList[5],'R_localUpLipMicroOutModify_LOC')
        self.microOutSecMod = mc.rename(tempList[6],'R_localUpLipMicroOutSecondaryModify_LOC')

        # create some nodes on HiRez
        tempJnts = jntLib.create_on_curve(self.uplipMedRezEdge, numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocHiUp, numLocs = 2, crv = self.uplipHirezEdge,
                                  upCurve = self.tempCurve, paramStart = 5.8, paramEnd = 5.6, upAxis = 'y', posJnts = tempJnts)
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
        trsLib.match(self.l_upLip_cornerbnd, t = self.upLipLowRezBindJnts[2],r = self.upLipLowRezBindJnts[2])
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
        trsLib.match(self.r_upLip_cornerbnd, t = self.upLipLowRezBindJnts[0],r = self.upLipLowRezBindJnts[0])
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

        self.mouthCtlOr = mc.createNode('transform', name = 'mouthCtlOri_GRP')
        trsLib.match(self.mouthCtlOr, self.mouthPiv)
        mc.move(0, -1 * float(self.movement) , 6.5, self.mouthCtlOr, r = True, ws = True)
        self.mouthCtl, self.mouthCtlGrp = funcs.createMouthCtl(name = 'mouthCtl', parent = self.mouthCtlOr,
                                                    snapJnt=self.mouthPiv, side = 'C')

        self.ctlupPlacement = mc.createNode('transform', name='localUpLipCtrlPlacement_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.ctlupPlacement, t = self.upLipLowRezBindJnts[1],r =self.upLipLowRezBindJnts[1] )
        self.uplipctl, self.uplipctlgrp, self.upsquashCtlMakro = funcs.createMiddleMainCtl(name = 'localUpLip', parent = self.ctlupPlacement ,
                                                    snapJnt=self.upLipLowRezBindJnts[1], side = 'C',up = True)
        self.uplipctlgrp = mc.rename(self.uplipctlgrp, 'localUpLipCtrlModify_GRP')

        # create left low main ctl
        self.leftUpLipCtlGrp = mc.createNode('transform', name= 'L_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.leftUpLipCtlGrp, t = self.upLipLowRezBindJnts[2],r = self.upLipLowRezBindJnts[2] )
        self.leftUpmainCtls,self.leftUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.leftUpLipCtlGrp ,
                                                              snapJnt = self.upLipLowRezBindJnts[2], side = 'L')
        self.leftUpCornerCtl = mc.rename(self.leftUpmainCtls[0], 'L_localUpLipCorner_CTL' )
        self.leftUpMinorCornerCtl = mc.rename(self.leftUpmainCtls[1], 'L_localUpLipCornerMinor_CTL' )
        self.leftCornerUpCtlGrp = mc.rename(self.leftUpMainCtlGrp[0], 'L_localUpLipCornerCtrlModify_GRP' )
        self.leftMinorCornerUpCtlGrp = mc.rename(self.leftUpMainCtlGrp[1], 'L_localUpLipCornerMinorModify_GRP' )

        # create right up main ctl
        self.rightUpLipCtlGrp = mc.createNode('transform', name='R_localUpLipCornerCtrlOrient_GRP', p=self.upLipCtlGrp)
        trsLib.match(self.rightUpLipCtlGrp, t = self.upLipLowRezBindJnts[0],r = self.upLipLowRezBindJnts[0])
        self.rightUpmainCtls,self.rightUpMainCtlGrp = funcs.createSideMainCtl(name = 'localUpLip', parent = self.rightUpLipCtlGrp,
                                                              snapJnt = self.upLipLowRezBindJnts[0], side = 'R')
        self.rightUpCornerCtl = mc.rename(self.rightUpmainCtls[0], 'R_localUpLipCorner_CTL' )
        self.rightUpMinorCornerCtl = mc.rename(self.rightUpmainCtls[1], 'R_localUpLipCornerMinor_CTL' )
        self.rightCornerLowCtlGrp = mc.rename(self.rightUpMainCtlGrp[0], 'R_localUpLipCornerCtrlModify_GRP' )
        self.rightMinorCornerLowCtlGrp = mc.rename(self.rightUpMainCtlGrp[1], 'R_localUpLipCornerMinorModify_GRP' )

        # create up roll
        self.upLipCtlRoll, self.upRoll_loc, self.upMidRollLoc = funcs.createRollHirarchy(name = 'localUpLip', parent = self.upLipCtlGrp, up = True)

        # create secondary zip joints
        zipUpSecJnts = jntLib.create_on_curve(self.uplipZipperEdge, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        # create zipper joints
        self.upMicroJnts,self.upTerLocs,self.upTerOrientGrp,self.upZipOutBndGrp,self.upLocMod,self.microUpCtls,self.upZipJnts,self.upZipperTargetLoc =  funcs.createZipperJnts(name='localUpLip',
                                                                                                                                                        crv=self.uplipZipperEdge,
                                                                                                                                                        upCurve=self.tempCurve, posJnts=zipUpSecJnts,
                                                                                                                                                        parent = self.noTuchyUp, jntParent = self.upMicroJntCtlGrp,
                                                                                                                                                        up = True)
        self.upLipMidLoc, self.r_upmidSecOr,self.r_upoutOrLoc,self.r_upcornerOr =  funcs.createLocsJntDriver(name = 'R_localUpLip',
                                                                                                             parent =self.upJntDrvr, jntSnap = self.upLipBindJnts[0])

        #****************************************************lowPart******************************************

        #create roll modify
        mc.move(0, -0.5,-2, self.jntRollModlowGrp, r=True, ws=True)
        self.jntLowRollLoc,self.lowLipJntMidLoc = funcs.createRollMod(name = 'localLowLip', parent = self.jntRollModlowGrp,up = False)

        # create ctlPlacement
        mc.move(0, 0, 0, self.lowjntCtlPlace, r=True, ws=True)
        self.lowJntCtlLoc, self.lowSquashMak = funcs.createCtlPlaceMent(name = 'localLowLip', parent = self.lowjntCtlPlace)

        self.lowLipLowRezBindJnts = jntLib.create_on_curve(self.lowLipLowRezEdge, numOfJoints = 3, parent = False, description='C_base', radius= 0.2)

        self.lowmedRezBindJnts = []
        self.lowLipLowRezBindJnts[0] = mc.rename(self.lowLipLowRezBindJnts[0],'R_localLowLipcorner_JNT')
        mc.setAttr(self.lowLipLowRezBindJnts[0] + '.ry', 130)
        self.lowLipLowRezBindJnts[1] = mc.rename(self.lowLipLowRezBindJnts[1],'localLowLipmain_JNT')
        self.lowLipLowRezBindJnts[2] = mc.rename(self.lowLipLowRezBindJnts[2],'L_localLowLipcorner_JNT')
        mc.setAttr(self.lowLipLowRezBindJnts[2] + '.ry', 50)

        trsLib.match(self.leftLowMainJnt, t = self.lowLipLowRezBindJnts[2],r = self.lowLipLowRezBindJnts[2])
        trsLib.match(self.rightLowMainJnt, t = self.lowLipLowRezBindJnts[0],r = self.lowLipLowRezBindJnts[0])
        trsLib.match(self.middleLowMainJnt, t = self.lowLipLowRezBindJnts[1],r = self.lowLipLowRezBindJnts[1])

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
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLipJntLocLowGrp, numLocs = 3, crv = self.lowLipLowRezEdge,
                                  upCurve = self.tempCurve, paramStart = 4.5, paramEnd = 1.5, upAxis = 'y', posJnts = self.lowLipLowRezBindJnts)

        # rename transfomrs that driven by lowRezCrv
        self.l_localLowLipDriverOutMod = mc.rename(tempList[0], 'L_localLowLipDriverOutModify_LOC')
        self.m_localLowLipDriverOutMod = mc.rename(tempList[1], 'm_localLowLipDriverOutModify_LOC')
        self.r_localLowLipDriverOutMod = mc.rename(tempList[2], 'r_localLowLipDriverOutModify_LOC')

        trsLib.match(self.r_localLowLipOutOrient_GRP, t = self.r_localLowLipDriverOutMod, r = self.r_localLowLipDriverOutMod)
        trsLib.match(self.l_localLowLipOutOrient_GRP, t = self.l_localLowLipDriverOutMod,r = self.l_localLowLipDriverOutMod)
        trsLib.match(self.m_localLowLipOutOrient_GRP, t = self.m_localLowLipDriverOutMod,r = self.m_localLowLipDriverOutMod)

        # create some nodes on medRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezEdge, numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocMedLow, numLocs = 7, crv = self.lowLipMedRezEdge,
                                  upCurve = self.tempCurve, paramStart = 5.4, paramEnd = 0.80, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.lowSecMod = mc.rename(tempList[0],'L_localLowLipMicroOutSecondaryModify_LOC')
        self.lowmicroOutMod = mc.rename(tempList[1],'L_localLowLipMicroOutModify_LOC')
        self.lowmidSecMod = mc.rename(tempList[2],'L_localLowLipMicroMidSecondaryModify_LOC')
        self.lowMidMod = mc.rename(tempList[3],'localLowLipMicroMidModify_LOC')
        self.lowMidSecModLoc = mc.rename(tempList[4],'R_localLowLipMicroMidSecondaryModify_LOC')
        self.lowmicroOutModLoc = mc.rename(tempList[5],'R_localLowLipMicroOutModify_LOC')
        self.lowmicroOutSecMod = mc.rename(tempList[6],'R_localLowLipMicroOutSecondaryModify_LOC')

        # create some nodes on HiRez
        tempJnts = jntLib.create_on_curve(self.lowLipMedRezEdge, numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.jntLocHiLow, numLocs = 2, crv = self.lowLipHirezEdge,
                                  upCurve = self.tempCurve, paramStart = 5.8, paramEnd = 5.6, upAxis = 'y', posJnts = tempJnts)
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
        trsLib.match(self.l_lowLip_cornerbnd, t = self.lowLipLowRezBindJnts[2], r = self.lowLipLowRezBindJnts[2])
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
        trsLib.match(self.r_lowLip_cornerbnd, t = self.lowLipLowRezBindJnts[0],r = self.lowLipLowRezBindJnts[0])
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
        trsLib.match(self.ctllowPlacement,t = self.lowLipLowRezBindJnts[1],r = self.lowLipLowRezBindJnts[1])
        self.lowlipctl, self.lowlipctlgrp, self.lowsquashCtlMakro = funcs.createMiddleMainCtl(name = 'localLowLip', parent = self.ctllowPlacement,
                                                      snapJnt=self.lowLipLowRezBindJnts[1], side = 'C', up = False)
        self.lowlipctlgrp = mc.rename(self.lowlipctlgrp, 'localLowLipCtrlModify_GRP')

        # create left low main ctl
        self.leftLowLipCtlGrp = mc.createNode('transform', name='L_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.leftLowLipCtlGrp, t = self.lowLipLowRezBindJnts[2],r = self.lowLipLowRezBindJnts[2])
        self.leftLowmainCtls,self.leftLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.leftLowLipCtlGrp ,
                                                              snapJnt = self.lowLipLowRezBindJnts[2], side = 'L')
        self.leftLowCornerCtl = mc.rename(self.leftLowmainCtls[0], 'L_localLowLipCorner_CTL' )
        self.leftLowMinorCornerCtl = mc.rename(self.leftLowmainCtls[1], 'L_localLowLipCornerMinor_CTL' )
        self.leftCornerLowCtlGrp = mc.rename(self.leftLowMainCtlGrp[0], 'L_localLowLipCornerCtrlModify_GRP' )
        self.leftMinorCornerLowCtlGrp = mc.rename(self.leftLowMainCtlGrp[1], 'L_localLowLipCornerMinorModify_GRP' )

        # create right low main ctl
        self.rightLowLipCtlGrp = mc.createNode('transform', name='R_localLowLipCornerCtrlOrient_GRP', p=self.lowLipCtlGrp)
        trsLib.match(self.rightLowLipCtlGrp, t = self.lowLipLowRezBindJnts[0],r= self.lowLipLowRezBindJnts[0])
        self.rightLowmainCtls,self.rightLowMainCtlGrp = funcs.createSideMainCtl(name = 'localLowLip', parent = self.rightLowLipCtlGrp,
                                                                snapJnt = self.lowLipLowRezBindJnts[0], side = 'R')
        self.rightLowCornerCtl = mc.rename(self.rightLowmainCtls[0], 'R_localLowLipCorner_CTL' )
        self.rightLowMinorCornerCtl = mc.rename(self.rightLowmainCtls[1], 'R_localLowLipCornerMinor_CTL' )
        self.rightCornerLowCtlGrp = mc.rename(self.rightLowMainCtlGrp[0], 'R_localLowLipCornerCtrlModify_GRP' )
        self.rightMinorCornerLowCtlGrp = mc.rename(self.rightLowMainCtlGrp[1], 'R_localLowLipCornerMinorModify_GRP' )

        # create low roll
        self.lowLipCtlRoll, self.lowRoll_loc, self.lowMidRollLoc = funcs.createRollHirarchy(name = 'localLowLip', parent = self.lowLipCtlGrp, up = False)

        # create zipper joints
        zipLowSecJnts = jntLib.create_on_curve(self.uplipZipperEdge, numOfJoints = 9, parent = False, description='C_base', radius = 0.1)

        self.lowMicroJnts, self.lowTerLocs,self.lowTerOrientGrp,self.lowZipOutBndGrp,self.lowLocMod ,self.microLowCtls,self.lowZipJnts ,self.lowZipperTargetLoc= funcs.createZipperJnts(name='localLowLip',
                                                                                                              crv=self.lowLipZipperEdge, upCurve=self.tempCurve,
                         posJnts=zipLowSecJnts, parent = self.noTuchyLow, jntParent = self.lowMicroJntCtlGrp, up = False)
        # create locators under jntDriver
        self.lowLipMidLoc, self.r_lowmidSecOr,self.r_lowoutOrLoc,self.r_lowcornerOr = funcs.createLocsJntDriver(name = 'R_localLowLip',
                                                                                                                parent =self.lowJntDrvr, jntSnap = self.lowLipBindJnts[0])



        # create nose ctls
        self.noseCtl, self.noseCtlBase, self.columellaCtl,self.r_nostrilCtl, self.l_nostrilCtl = funcs.createNoseCtls(name = 'noseCtl',
                                                                                 parent = self.noseCtlGrp,
                                                                                 mainSnap = self.mouthAndJawMain[3],
                                                                                 cummelaSnap = self.mouthAndJawMain[4],
                                                                                 leftSnap = self.leftnostrils[0] ,
                                                                                 rightSnap = self.rightnostrils[0],
                                                                                 movement = self.movement)


        # create jaw ctls
        self.jawCtlOriGrp = mc.createNode('transform' ,name = 'jawCtlOri_GRP')
        trsLib.match(self.jawCtlOriGrp, t = self.mouthAndJawMain[1],r =self.mouthAndJawMain[1] )
        mc.move(0,-1 * float(self.movement), 0, self.jawCtlOriGrp, r = True, ws = True )
        self.jawCtlMakroGrp = mc.createNode('transform', name = 'jawCtlMakr_GRP', p = self.jawCtlOriGrp)

        ctl,grp = funcs.createCtl(parent = self.jawCtlMakroGrp, side = self.side )
        self.jawCtlModGrp = mc.rename(grp, 'jawCtlMod_GRP')
        self.jawCtl = mc.rename(ctl, 'jaw_CTL')
        mc.parent(self.jawCtlModGrp,self.jawCtlMakroGrp)

        self.jawCtlSecondaryCtlOriGrp = mc.createNode('transform', name = 'jawSecondaryCtlOri_GRP', p = self.jawCtl)
        trsLib.match(self.jawCtlSecondaryCtlOriGrp,t = self.jawSecBndJnt[0] ,r = self.jawSecBndJnt[0])
        mc.move(0,-1 * float(self.movement), 0, self.jawCtlSecondaryCtlOriGrp, r = True, ws = True )


        ctl,grp = funcs.createCtl(parent = self.jawCtlSecondaryCtlOriGrp , side = self.side)
        self.jawSecModCtlGrp = mc.rename(grp, 'jawSecondaryCtlMod_GRP')
        self.jawSecCtl = mc.rename(ctl, 'jawSecondary_CTL')
        mc.parent(self.jawSecModCtlGrp ,self.jawCtlSecondaryCtlOriGrp)

        ctl,grp = funcs.createCtl(parent = self.jawSecBndJnt[2], side = self.side)
        self.mentalisModCtlGrp = mc.rename(grp, 'mentalisCtlMod_GRP')
        self.mentalisCtl = mc.rename(ctl, 'mentalis_CTL')
        mc.parent(self.mentalisModCtlGrp, self.jawSecCtl)
        mc.move(0,-1 * float(self.movement), 0, self.mentalisModCtlGrp, r = True, ws = True )


        ctl,grp = funcs.createCtl(parent = self.jawSecBndJnt[1], side = self.side)
        self.chinModCtlGrp = mc.rename(grp, 'chinCtlMod_GRP')
        self.chinCtl = mc.rename(ctl, 'chin_CTL')
        mc.parent(self.chinModCtlGrp, self.jawSecCtl)
        mc.move(0,-1 * float(self.movement), 0, self.chinModCtlGrp, r = True, ws = True )


        self.jaw2ndFollowLoc = mc.createNode('transform', name = 'jaw2ndFollow_LOC',p = self.jawSecCtl )
        self.jaw2ndFollowLocShape = mc.createNode('locator', name = 'jaw2ndFollowShape_LOC',p = self.jaw2ndFollowLoc)
        self.lowMouthGrp = mc.createNode('transform', name = 'lowMouth_GRP')


        #create teeth hierarchy
        self.upTeethOriGrp = mc.createNode('transform', name = 'topTeethOri_GRP' )
        trsLib.match(self.upTeethOriGrp, t = self.teethJnts[0],r = self.teethJnts[0])

        self.lowTeethOriGrp = mc.createNode('transform', name = 'lowTeethOri_GRP', p = self.lowMouthGrp)
        trsLib.match(self.lowTeethOriGrp, t = self.teethJnts[1],r = self.teethJnts[1])



        self.upTeethMakroGrp, self.upteethCtls,self.upteethGrps,self.upTeethSquashMakro = funcs.createTeethHierarchy(jnt=self.teethJnts[0],
                                                                                 parent=self.upTeethOriGrp,movement = self.movement, side=self.side,
                                   scale=[1, 1, 1],prefix = 'top',leftPos= self.upTeethWire[1], rightPos = self.upTeethWire[2])
        self.lowTeethMakroGrp ,self.lowteethCtls,self.lowteethGrps, self.lowTeethSquashMakro= funcs.createTeethHierarchy(jnt=self.teethJnts[1],
                                                                                 parent=self.lowTeethOriGrp,movement = self.movement, side=self.side,
                                   scale=[1, 1, 1],prefix = 'low',leftPos= self.lowTeethWire[1], rightPos = self.lowTeethWire[2])

        # wire curves to the gums
        mc.select(self.upperteeth, r=True)
        mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.upperTeethEdge)
        shape = mc.listRelatives(self.upperteeth, shapes=True)[0]
        wire = mc.listConnections(shape + '.inMesh', d=False, s=True)[0]
        mc.setAttr(wire + '.dropoffDistance[0]', 20)
        mc.select(self.lowerteeth, r=True)
        mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.lowerTeethEdge)
        shape = mc.listRelatives(self.lowerteeth, shapes=True)[0]
        wire = mc.listConnections(shape + '.inMesh', d=False, s=True)[0]
        mc.setAttr(wire + '.dropoffDistance[0]', 20)

        # connect stuff to the teeth makro grp
        attrLib.addFloat(self.mouthCtl, ln = 'teethFollow', min = 0, max = 1, dv = 1)
        teethMult = mc.createNode('multiplyDivide', name = 'TeethFollowAct_MDN')
        mc.connectAttr(self.mouthCtl + '.teethFollow', teethMult + '.input1X')
        mc.connectAttr(self.mouthCtl + '.teethFollow', teethMult + '.input1Y')
        mc.connectAttr(self.mouthAncFollowDrvr + '.tx', teethMult + '.input2X')
        mc.connectAttr(self.mouthAncFollowDrvr + '.ty', teethMult + '.input2Y')
        mc.connectAttr(teethMult + '.outputX', self.upTeethMakroGrp + '.tx')
        mc.connectAttr(teethMult+ '.outputY', self.upTeethMakroGrp + '.ty')
        mc.connectAttr(teethMult + '.outputX', self.lowTeethMakroGrp + '.tx')
        mc.connectAttr(teethMult+ '.outputY', self.lowTeethMakroGrp + '.ty')


        self.tongueCtls = []
        self.tongueGrps = []
        par = self.lowTeethMakroGrp
        for i in self.tongueJnts:
            ctl, grp = funcs.createTongueHierarchy(jnt=i, parent= par , name= i, side = self.side, scale = [1,1,1])
            newName = i.replace('_JNT', '_CTL')
            ctl = mc.rename(ctl, newName)
            mc.parent(i, ctl)
            self.tongueCtls.append(ctl)
            newName = ctl.replace('_CTL', '_GRP')
            grp = mc.rename(grp, newName)
            self.tongueGrps.append(grp)
            par = i

        mc.parent(self.lowMouthGrp ,self.jaw2ndFollowLoc )

        # skin wire joints to the teeth curve
        deformLib.bind_geo(geos = self.upperTeethEdge, joints = self.upTeethWire)
        deformLib.bind_geo(geos = self.lowerTeethEdge, joints = self.lowTeethWire)


        # parent wire joints under hierarchy
        self.teethStuffGrp = mc.createNode('transform', name='TeethStuff_GRP')

        self.l_lowTeethWireModGrp,self.r_lowTeethWireModGrp,self.m_lowTeethWireModGrp,self.l_upTeethWireOriGrp,self.r_upTeethWireOriGrp,self.m_upTeethWireOriGrp,self.lowwireModGrp,self.upwireModGrp = funcs.createTeethJntHierarchy(pos=self.mouthPiv,upTeethWire=self.upTeethWire,
                                                                                          lowTeethWire=self.lowTeethWire, parent = self.teethStuffGrp)


        # connect stuff to the modgrps above teeth ctls
        [mc.connectAttr(self.lowteethCtls[1] + '.{}{}'.format(a,v), self.l_lowTeethWireModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']
        [mc.connectAttr(self.lowteethCtls[2] + '.{}{}'.format(a,v), self.r_lowTeethWireModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']
        [mc.connectAttr(self.lowteethCtls[0] + '.{}{}'.format(a,v), self.m_lowTeethWireModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']
        [mc.connectAttr(self.upteethCtls[1] + '.{}{}'.format(a,v), self.l_upTeethWireOriGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']
        [mc.connectAttr(self.upteethCtls[2] + '.{}{}'.format(a,v), self.r_upTeethWireOriGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']
        [mc.connectAttr(self.upteethCtls[0] + '.{}{}'.format(a,v), self.m_upTeethWireOriGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']


        # duplicate the local rig
        output = trsLib.duplicate(self.upLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -1 * float(self.movement))
        #mc.makeIdentity(output[0], apply = True, t = True)
        # mc.parent(output[0], self.facialCtlGrp)
        output = trsLib.duplicate(self.lowLipRibbon, search = 'local',replace = '', hierarchy= True )
        mc.setAttr(output[0] + '.ty', -1 * float(self.movement))
        #mc.makeIdentity(output[0], apply = True, t = True)
        # mc.parent(output[0], self.facialCtlGrp)
