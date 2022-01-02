
import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import crvLib
from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib
from ...lib import deformLib
from ...lib import keyLib
from ...lib import jntLib
from ...lib import connect
from . import neckTemplate
from . import funcs

reload(jntLib)
reload(crvLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(neckTemplate)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NeckB(neckTemplate.NeckTemplate):
    """
    base class for neck template
    """
    def __init__(self, side='C', prefix='neck', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        super(NeckB, self).__init__(**kwargs)
        self.aliases = {'neck_01':'neck_01',
                        'neck_02':'neck_02',
                        'neck_03':'neck_03',
                        'neck_04':'neck_04',
                        'neck_05':'neck_05',
                        'headStart':'headStart',
                        'headEnd':'headEnd'}

    def createBlueprint(self):
        super(NeckB, self).createBlueprint()
        self.blueprints['neck_01'] = '{}_neck_01_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['neck_01']):
            mc.joint(self.blueprintGrp, name=self.blueprints['neck_01'])
            mc.xform(self.blueprints['neck_01'], ws=True, t=(0, 151.862, -5.118))

        self.blueprints['neck_02'] = '{}_neck_02_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['neck_02']):
            mc.joint(self.blueprints['neck_01'], name=self.blueprints['neck_02'])
            mc.xform(self.blueprints['neck_02'], ws=True, t=(0, 156.816, -5.118))

        self.blueprints['neck_03'] = '{}_neck_03_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['neck_03']):
            mc.joint(self.blueprints['neck_02'], name=self.blueprints['neck_03'])
            mc.xform(self.blueprints['neck_03'], ws=True, t=(0, 161.852, -5.118))

        self.blueprints['neck_04'] = '{}_neck_04_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['neck_04']):
            mc.joint(self.blueprints['neck_03'], name=self.blueprints['neck_04'])
            mc.xform(self.blueprints['neck_04'], ws=True, t=(0, 166.881, -5.118))

        self.blueprints['neck_05'] = '{}_neck_05_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['neck_05']):
            mc.joint(self.blueprints['neck_04'], name=self.blueprints['neck_05'])
            mc.xform(self.blueprints['neck_05'], ws=True, t=(0, 171.832, -5.118))

        self.blueprints['headStart'] = '{}_headStart_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['headStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['headStart'])
            mc.xform(self.blueprints['headStart'], ws=True, t=(0, 173.002, -5.118))

        self.blueprints['headEnd'] = '{}_headEnd_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['headEnd']):
            mc.joint(self.blueprints['headStart'], name=self.blueprints['headEnd'])
            mc.xform(self.blueprints['headEnd'], ws=True, t=(0, 185.65, -5.118))

    def createJoints(self):
        par = self.moduleGrp
        self.neckJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('neck_01', 'neck_02','neck_03','neck_04','neck_05'):
                continue
            jnt = '{}_{}_JNT'.format(self.side, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 1)
            self.neckJnts.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

        par = self.moduleGrp
        self.headJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('headStart', 'headEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.side, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 1)
            self.headJnts.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='z', upAxes='y')
        mc.delete(upLoc)

    def build(self):
        super(NeckB, self).build()
        mc.parent(self.neckJnts[0], self.neckJntGrp)

        # create headCtl
        ctl, grp = funcs.createCtl(parent = self.headOriGrp,side = 'C',scale = [15, 1, 15],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,12,0])
        name = self.headOriGrp.replace('Ori_GRP', '_GRP')
        self.headGrp = mc.rename(grp , name)
        name = self.headOriGrp.replace('Ori_GRP', '_CTL')
        self.headCtl = mc.rename(ctl, name)
        mc.parent(self.headGrp, self.headOriGrp)

        self.headGrpCtl = mc.createNode('transform', name = 'head_GRP', p = self.headCtl)
        mc.parent(self.headJnts[0], self.headGrpCtl)

        # create neck ctl
        ctl, grp = funcs.createCtl(parent = self.neckBaseOriGrp,side = 'C',scale = [15, 1, 15],shape = 'circle',
                                   orient = (0,1,0),moveShape=[0,8,0])

        name = self.neckBaseOriGrp.replace('Ori_GRP', '_GRP')
        self.neckStartCtlGrp = mc.rename(grp , name)
        mc.move(0,-4, 0,self.neckStartCtlGrp, r = True, ws = True )
        name = self.neckBaseOriGrp.replace('Ori_GRP', '_CTL')
        self.neckStartCtl = mc.rename(ctl, name)
        mc.parent(self.neckStartCtlGrp, self.neckBaseOriGrp)

        attrLib.addEnum(self.neckStartCtl, 'spaceSwitch', en = ['chest', 'body', 'global'], dv = 0)
        for i in ['L_sternoCleidomastoid', 'R_sternoCleidomastoid']:
            attrLib.addFloat(self.neckStartCtl, ln = i, min = 0, max = 10, dv = 0)


        self.neckIkButtomDrvrJnt = mc.joint(self.neckStartCtl, name = 'neckIkButtomDriver_JNT')
        trsLib.match(self.neckIkButtomDrvrJnt, self.neckJnts[0])

        self.neckButtomDrvrLoc = mc.createNode('transform', name  = 'neckTwisterButtomDrvr_LOC', p = self.neckIkButtomDrvrJnt)
        self.neckButtomDrvrLocShape = mc.createNode('locator', name  = 'neckTwisterButtomDrvrShape_LOC', p = self.neckButtomDrvrLoc)
        trsLib.match(self.neckButtomDrvrLoc, self.neckJnts[0])
        mc.move(0,0, -17,self.neckButtomDrvrLoc, r = True, ws = True )

        self.neckHeadDrvrLoc = mc.createNode('transform', name  = 'neckHeadDrvr_LOC', p = self.neckStartCtl)
        self.neckHeadDrvrLocShape = mc.createNode('locator', name  = 'neckHeadDrvrShape_LOC', p = self.neckHeadDrvrLoc)
        trsLib.match(self.neckHeadDrvrLoc, self.headJnts[0])


        self.neckIkBlenderOriGrp = mc.createNode('transform', name = 'neckIKBlenderOri_GRP', p = self.neckStartCtl)
        trsLib.match(self.neckIkBlenderOriGrp, self.neckJnts[2])

        # create neckIkBlenderCtl
        ctl, grp = funcs.createCtl(parent = self.neckIkBlenderOriGrp,side = 'C',scale = [15, 1, 15],shape = 'circle',
                                   orient = (0,1,0),moveShape=[0,0,0])

        name = self.neckIkBlenderOriGrp.replace('Ori_GRP', '_GRP')
        self.neckIkBlenderCtlGrp = mc.rename(grp , name)
        name = self.neckIkBlenderOriGrp.replace('Ori_GRP', '_CTL')
        self.neckIkBlenderCtl = mc.rename(ctl, name)
        mc.parent(self.neckIkBlenderCtlGrp, self.neckIkBlenderOriGrp)

        self.neckIkMiddleJnt = mc.joint(self.neckIkBlenderCtl, name = 'neckIkMiddleDriver_JNT')

        # create neckIk twist jnts
        self.neckIkTwisterJnt = mc.joint(self.neckTwisterGrp, name = 'neckIkTwister_JNT')
        trsLib.match(self.neckIkTwisterJnt, self.neckJnts[0])

        self.neckIkTwisterEndJnt = mc.joint(self.neckIkTwisterJnt, name = 'neckIkTwisterEnd_JNT')
        trsLib.match(self.neckIkTwisterEndJnt, self.headJnts[0])

        self.neckIkTopDrvrJnt = mc.joint(self.neckIkTwisterJnt, name = 'neckIkTopDrvr_JNT')
        trsLib.match(self.neckIkTopDrvrJnt, self.neckJnts[-1])

        self.neckTwisterTopDrvrLoc = mc.createNode('transform', name = 'neckTwister_topDrvr_LOC', p = self.neckIkTwisterJnt)
        self.neckTwisterTopDrvrLocShape = mc.createNode('locator', name = 'neckTwister_topDrvrShape_LOC', p = self.neckTwisterTopDrvrLoc)
        trsLib.match(self.neckTwisterTopDrvrLoc , self.neckJnts[-1])
        mc.move(0,0,-16,self.neckTwisterTopDrvrLoc, r = True, ws = True)

        # connect stuf togather
        self.neckTwisterIkh = mc.ikHandle(solver="ikSCsolver",startJoint=self.neckIkTwisterJnt,
                                          endEffector=self.neckIkTwisterEndJnt,
                                          name=self.name + "_ikTwister_IKH")[0]

        mc.parent(self.neckTwisterIkh, self.headJnts[0])

        # create ik for neck jnts
        self.neckIkCurve, self.neckIkCurveShape = crvLib.fromJnts(jnts= self.neckJnts, degree=3, name='neckIk_CRV')

        self.neckIkh = mc.ikHandle(sj = self.neckJnts[0] ,ee = self.neckJnts[-1] ,
                             name = self.name + '_IKH',solver = 'ikSplineSolver',
                             c = 'neckIk_CRV', ccv = False)[0]

        # parent,orient and scale constraint stuf to the headOriGrp
        attrLib.addEnum(self.headCtl, 'spaceSwitch', en = ['chest', 'body', 'global'], dv = 2)

        mc.pointConstraint(self.neckHeadDrvrLoc, self.headOriGrp, mo = True)
        #todo scale constraint the global ctl to the headOriGrp
        #todo orient constraint chest loc,global loc and body loc to the headOriGrp

        #todo scale constraint global ctl to the neckBaseOriGrp

        # aim constraint locators to the neckSpaceMaster loc
        neckSpaceAimCons = mc.aimConstraint([self.neckSpaceAimChestLoc,self.neckSpaceAimGlobalLoc,self.neckSpaceAimBodyLoc ],
                                   self.neckSpaceMasterLoc,
                                   aimVector=[1, 0, 0],
                                   upVector=[0, 1, 0],
                                   worldUpType="object",
                                   worldUpObject=self.neckSpaceAimUpLoc)[0]

        # connect stuf to the weight of aimConstraint targets

        keyLib.setDriven(self.neckStartCtl + '.spaceSwitch', neckSpaceAimCons + '.' + self.neckSpaceAimChestLoc + 'W0',
                         [0,1,2], [1,0,0], itt='auto',
                         ott='auto')

        keyLib.setDriven(self.neckStartCtl + '.spaceSwitch', neckSpaceAimCons + '.' + self.neckSpaceAimGlobalLoc + 'W1',
                         [0,1,2], [0,0,1], itt='auto',
                         ott='auto')

        keyLib.setDriven(self.neckStartCtl + '.spaceSwitch', neckSpaceAimCons + '.' + self.neckSpaceAimBodyLoc + 'W2',
                         [0,1,2], [0,1,0], itt='auto',
                         ott='auto')

        #todo parentConstraint spineBlendEnt jnt to the neckSpace aim loc  and neckSpaceAim chest later]

        #todo orientConstraint bodySpaceLoc to the neckSpaceAimBody loc

        #todo orient constraint global space loc to the neckSpaceAimGlobal point

        # parentConstraint neckSpaceMasterLoc to the neckBasMod grp
        mc.parentConstraint(self.neckSpaceMasterLoc, self.neckStartCtlGrp, mo = True)

        # add stretch on neck joints
        infoNode = mc.createNode('curveInfo', name = 'neckCurveDistance')

        mc.connectAttr(self.neckIkCurveShape + '.worldSpace[0]', infoNode + '.inputCurve')

        neckDistMult = mc.createNode('multiplyDivide', name = 'neckDist_MDN')
        mc.connectAttr(infoNode + '.arcLength', neckDistMult + '.input1X')

        inputVal = mc.getAttr(neckDistMult + '.input1X')
        mc.setAttr(neckDistMult + '.input2X', inputVal)

        mc.setAttr(neckDistMult + '.operation', 2)
        for i in self.neckJnts:
            for j in ['sx','sy','sz']:
                mc.connectAttr(neckDistMult + '.outputX', i + '.' + j)

        # scaleConstarint neckBaseCtl to the neckTwister transform
        mc.scaleConstraint(self.neckStartCtl,self.neckTwisterGrp, mo = True)

        #todo parentConstraint spineIk_chestDrvr and spineBlend to the neckIkTwister later

        mc.pointConstraint(self.headJnts[0], self.neckIkTopDrvrJnt, mo = True)












    def connect(self):
        super(NeckB, self).connect()


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(NeckB, self).createSettings()








