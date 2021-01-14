
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
from . import spineTemplate
from . import funcs

reload(jntLib)
reload(crvLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(spineTemplate)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SpineB(spineTemplate.SpineTemplate):
    """
    base class for neck template
    """
    def __init__(self, side='C', prefix='spine', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        super(SpineB, self).__init__(**kwargs)
        self.aliases = {'hipIk':'hipIk',
                        'spineIk1':'spineIk1',
                        'spineIk2':'spineIk2',
                        'spineIk3':'spineIk3',
                        'spineIkEnd':'spineIkEnd',
                        'crotch':'crotch',
                        'blend1Breather':'blend1Breather',
                        'blend2Breather':'blend2Breather'}

    def createBlueprint(self):
        super(SpineB, self).createBlueprint()

        self.blueprints['hipIk'] = '{}_hipIk_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['hipIk']):
            mc.joint(self.blueprintGrp, name=self.blueprints['hipIk'])
            mc.xform(self.blueprints['hipIk'], ws=True, t=(0, 100.261, -5.118))

        self.blueprints['spineIk1'] = '{}_spineIk1_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['spineIk1']):
            mc.joint(self.blueprints['hipIk'], name=self.blueprints['spineIk1'])
            mc.xform(self.blueprints['spineIk1'], ws=True, t=(0, 110.322, -5.118))

        self.blueprints['spineIk2'] = '{}_spineIk2_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['spineIk2']):
            mc.joint(self.blueprints['spineIk1'], name=self.blueprints['spineIk2'])
            mc.xform(self.blueprints['spineIk2'], ws=True, t=(0, 124.155, -5.118))

        self.blueprints['spineIk3'] = '{}_spineIk3_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['spineIk3']):
            mc.joint(self.blueprints['spineIk2'], name=self.blueprints['spineIk3'])
            mc.xform(self.blueprints['spineIk3'], ws=True, t=(0, 137.968, -5.118))

        self.blueprints['spineIkEnd'] = '{}_spineIkEnd_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['spineIkEnd']):
            mc.joint(self.blueprints['spineIk3'], name=self.blueprints['spineIkEnd'])
            mc.xform(self.blueprints['spineIkEnd'], ws=True, t=(0, 151.864, -5.118))

        self.blueprints['crotch'] = '{}_crotch_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['crotch']):
            mc.joint(self.blueprintGrp, name=self.blueprints['crotch'])
            mc.xform(self.blueprints['crotch'], ws=True, t=(0, 97.812, 2.837))

        self.blueprints['blend1Breather'] = '{}_blend1Breather_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['blend1Breather']):
            mc.joint(self.blueprintGrp, name=self.blueprints['blend1Breather'])
            mc.xform(self.blueprints['blend1Breather'], ws=True, t=(0, 110.355, 3.416))

        self.blueprints['blend2Breather'] = '{}_blend2Breather_BLU'.format(self.side)
        if not mc.objExists(self.blueprints['blend2Breather']):
            mc.joint(self.blueprintGrp, name=self.blueprints['blend2Breather'])
            mc.xform(self.blueprints['blend2Breather'], ws=True, t=(0, 124.161, 3.416))


    def createJoints(self):
        par = self.moduleGrp
        self.spineIkJnts = []
        for alias, blu in self.blueprints.items():
            if  alias in ('crotch','blend1Breather','blend2Breather' ):
                continue
            jnt = '{}_{}_JNT'.format(self.side, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 1)
            self.spineIkJnts.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

        par = self.moduleGrp
        self.crotchJnt = []
        for alias, blu in self.blueprints.items():
            if  not alias in ('crotch'):
                continue
            jnt = '{}_{}_JNT'.format(self.side, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 1)
            self.crotchJnt.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

        par = self.moduleGrp
        self.blendBreatherJnts = []
        for alias, blu in self.blueprints.items():
            if  not alias in ('blend1Breather','blend2Breather'):
                continue
            jnt = '{}_{}_JNT'.format(self.side, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 1)
            self.blendBreatherJnts.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt



    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='z', upAxes='y')
        mc.delete(upLoc)

    def build(self):
        super(SpineB, self).build()

        # spine fk joints
        self.spineFkJnts = trsLib.duplicate(self.spineIkJnts[0],search='Ik', replace='Fk', hierarchy=True)
        self.spineFkJnts.sort()

        self.spineBlendJnts = trsLib.duplicate(self.spineIkJnts[0],search='Ik', replace='Blend', hierarchy=True)
        self.spineBlendJnts.sort()

        # create ikHandle for spine ik jnts
        self.spineIkCurve, self.spineIkCurveShape = crvLib.fromJnts(jnts= self.spineIkJnts, degree=3, name='spineIk_CRV')

        self.spineIkh = mc.ikHandle(sj = self.spineIkJnts[0] ,ee = self.spineIkJnts[-1] ,
                             name = self.name + '_IKH',solver = 'ikSplineSolver',
                             c = 'spineIk_CRV', ccv = False)[0]

        # spine stretch
        funcs.spineStretch(name=self.name , jnts= self.spineIkJnts, curve= self.spineIkCurveShape)


        # parent blendSpine jnts under stuf
        mc.parent(self.spineBlendJnts[0],self.hipBlendModGrp)
        #todo create left and right hip space locators on leg module and parent them under hipBlendJnts
        #todo parent left twister ik Handles under hipBlend joint later

        # create stuf on crotch position
        self.crotchJnt = self.crotchJnt[0]
        self.crotchOriGrp = mc.createNode('transform', name =  'crotchOri_GRP', p = self.spineBlendJnts[0])
        trsLib.match(self.crotchOriGrp, self.crotchJnt)

        # create crotch ctl
        ctl, grp = funcs.createCtl(parent = self.crotchOriGrp,side = 'C',scale = [1, 1, 1],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,0,3])
        name = self.crotchOriGrp.replace('Ori_GRP', '_GRP')
        self.crotchCtlGrp = mc.rename(grp , name)
        name = self.crotchOriGrp.replace('Ori_GRP', '_CTL')
        self.crotchCtl = mc.rename(ctl, name)
        mc.parent(self.crotchCtlGrp, self.crotchOriGrp)

        self.crotchJntOriGrp = mc.createNode('transform', name = 'crotchJntOriGrp', p = self.crotchCtl)
        self.crotchJntModGrp = mc.createNode('transform', name = 'crotchJntModGrp', p = self.crotchJntOriGrp)
        mc.parent(self.crotchJnt, self.crotchJntModGrp)

        self.spineBlend1OriGrp = mc.createNode('transform' , name = 'spineBlend1Ori_GRP', p = self.spineBlendJntGrp)
        trsLib.match(self.spineBlend1OriGrp,self.spineBlendJnts[1])
        self.spineBlend1ModGrp = mc.createNode('transform' , name = 'spineBlend1Mod_GRP', p = self.spineBlend1OriGrp)
        mc.parent(self.spineBlendJnts[1], self.spineBlend1ModGrp)

        self.spineBlend2OriGrp = mc.createNode('transform' , name = 'spineBlend2Ori_GRP', p = self.spineBlendJntGrp)
        trsLib.match(self.spineBlend2OriGrp,self.spineBlendJnts[2])
        self.spineBlend2ModGrp = mc.createNode('transform' , name = 'spineBlend2Mod_GRP', p = self.spineBlend2OriGrp)
        mc.parent(self.spineBlendJnts[2], self.spineBlend2ModGrp)

        self.spineBlend3OriGrp = mc.createNode('transform' , name = 'spineBlend3Ori_GRP', p = self.spineBlendJntGrp)
        trsLib.match(self.spineBlend3OriGrp,self.spineBlendJnts[3])
        self.spineBlend3ModGrp = mc.createNode('transform' , name = 'spineBlend3Mod_GRP', p = self.spineBlend3OriGrp)
        mc.parent(self.spineBlendJnts[3], self.spineBlend3ModGrp)

        self.spineBlend4OriGrp = mc.createNode('transform' , name = 'spineBlend4Ori_GRP', p = self.spineBlendJnts[3])
        trsLib.match(self.spineBlend4OriGrp,self.spineBlendJnts[4])
        self.spineBlend4ModGrp = mc.createNode('transform' , name = 'spineBlend4Mod_GRP', p = self.spineBlend4OriGrp)
        mc.parent(self.spineBlendJnts[4], self.spineBlend4ModGrp)


        # create transform for breath joints
        self.spineBlendBreatherOriGrp = mc.createNode('transform', name = self.name + '_blend1BreatherOri_GRP',
                                                      p = self.spineBlendJnts[1])
        trsLib.match(self.spineBlendBreatherOriGrp, self.blendBreatherJnts[0])
        self.spineBlendBreatherModGrp = mc.createNode('transform', name = self.name + '_blend1BreatherMod_GRP',
                                                      p = self.spineBlendBreatherOriGrp)
        mc.parent(self.blendBreatherJnts[0], self.spineBlendBreatherModGrp)

        self.spineBlendBreather2OriGrp = mc.createNode('transform', name = self.name + '_blend2BreatherOri_GRP',
                                                      p = self.spineBlendJnts[2])
        trsLib.match(self.spineBlendBreather2OriGrp, self.blendBreatherJnts[1])
        self.spineBlendBreather2ModGrp = mc.createNode('transform', name = self.name + '_blend2BreatherMod_GRP',
                                                      p = self.spineBlendBreather2OriGrp)
        mc.parent(self.blendBreatherJnts[1], self.spineBlendBreather2ModGrp)

        # create spine ik hip ctl
        ctl, grp = funcs.createCtl(parent = self.spineIkHipDrvrOriGrp,side = 'C',scale = [30, 5, 30],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,0,0])
        name = self.spineIkHipDrvrOriGrp.replace('Ori_GRP', '_GRP')
        self.spineIkHipCtlGrp = mc.rename(grp , name)
        name = self.spineIkHipDrvrOriGrp.replace('Ori_GRP', '_CTL')
        self.spineIkHipCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkHipCtlGrp, self.spineIkHipDrvrOriGrp)

        # create spine ik offset ctl
        ctl, grp = funcs.createCtl(parent = self.spineIkHipCtl,side = 'C',scale = [28, 5, 28],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,0,0])
        name = self.spineIkHipCtl.replace('_CTL', '_offset_CTL')
        self.spineIkHipOffsetCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkHipOffsetCtl, self.spineIkHipCtl)
        mc.delete(grp)

        self.spineIkHipDrvrJnt = mc.joint(self.spineIkHipOffsetCtl, name = 'spineIkHipDrvr_JNT')

        # create locators under offsetCtl
        self.spineIkTwistButtomLoc = mc.createNode('transform', name = 'spineIkTwist_pivot_LOC', p = self.spineIkHipOffsetCtl)
        self.spineIkTwistButtomLocShape = mc.createNode('locator', name = 'spineIkTwist_pivotShape_LOC', p = self.spineIkTwistButtomLoc)
        mc.move(0,0,-44, self.spineIkTwistButtomLoc,r = True, ws = True)

        self.spineIkHipPivotLoc = mc.createNode('transform', name = 'spineIkHip_pivot_LOC', p = self.spineIkHipOffsetCtl)
        self.spineIkHipPivotLocShape = mc.createNode('locator', name = 'spineIkHip_pivotShape_LOC', p = self.spineIkHipPivotLoc)

        # create spine ik chest ctl
        ctl, grp = funcs.createCtl(parent = self.spineIkChestDrvrOriGrp,side = 'C',scale = [35, 17, 30],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,-10,0])
        name = self.spineIkChestDrvrOriGrp.replace('Ori_GRP', '_GRP')
        self.spineIkChestCtlGrp = mc.rename(grp , name)
        name = self.spineIkChestDrvrOriGrp.replace('Ori_GRP', '_CTL')
        self.spineIkChestCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkChestCtlGrp, self.spineIkChestDrvrOriGrp)

        # create spineIkChestOffsetCtl
        ctl, grp = funcs.createCtl(parent = self.spineIkChestCtl,side = 'C',scale = [26, 15, 26],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,-10,0])
        name = self.spineIkChestCtl.replace('_CTL', '_offset_CTL')
        self.spineIkChestOffsetCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkChestOffsetCtl, self.spineIkChestCtl)
        mc.delete(grp)

        # create spineIkChestOffsetTopCtl
        ctl, grp = funcs.createCtl(parent = self.spineIkChestOffsetCtl,side = 'C',scale = [24, 13, 24],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,-5,0])
        name = self.spineIkChestOffsetCtl.replace('offset', 'offsetTop')
        self.spineIkChestOffsetTopCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkChestOffsetTopCtl, self.spineIkChestOffsetCtl)
        mc.delete(grp)

        self.spineIkChestDrvrJnt = mc.joint(self.spineIkChestOffsetTopCtl, name = 'spineIk_chestDrvr_JNT')

        self.spineIkTwistTopLoc = mc.createNode('transform', name = 'spineIkTwistTop_LOC', p = self.spineIkChestOffsetTopCtl)
        self.spineIkTwistTopLocShape = mc.createNode('locator', name = 'spineIkTwistTopShape_LOC', p = self.spineIkTwistTopLoc)
        mc.move(0,0,-44, self.spineIkTwistTopLoc,r = True, ws = True)

        self.spineIkChestPivotLoc = mc.createNode('transform', name = 'spineIkChest_pivot_LOC', p = self.spineIkChestOffsetCtl)
        self.spineIkChestPivotLocShape = mc.createNode('locator', name = 'spineIkChest_pivotShape_LOC', p = self.spineIkChestPivotLoc)

        # create spine ik waist ctl
        ctl, grp = funcs.createCtl(parent = self.spineIkWaistDrvrOriGrp,side = 'C',scale = [35, 3, 30],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,0,0])
        name = self.spineIkWaistDrvrOriGrp.replace('Ori_GRP', '_GRP')
        self.spineIkWaistCtlGrp = mc.rename(grp , name)
        name = self.spineIkWaistDrvrOriGrp.replace('Ori_GRP', '_CTL')
        self.spineIkWaistCtl = mc.rename(ctl, name)
        mc.parent(self.spineIkWaistCtlGrp, self.spineIkWaistDrvrOriGrp)

        self.spineIkWaistDrvrJnt = mc.joint(self.spineIkWaistCtl, name = 'spineIkWaistDrvr_JNT')

        # create fk ctls
        self.fkOriGrps = []
        self.fkCtlGrps = []
        self.fkCtls = []
        par = self.spineFkGrp
        for i in self.spineFkJnts[1:-1]:
            n = i.split('JNT')[0]
            oriGrp = mc.createNode('transform', name  = n + 'ori_GRP', p  = par)
            self.fkOriGrps.append(oriGrp)
            trsLib.match(oriGrp, i)
            ctl, grp = funcs.createCtl(parent=oriGrp, side='C', scale=[35, 3, 30], shape='circle',
                                       orient=(0, 1, 0), moveShape=[0, 0, 0])
            ctl = mc.rename(ctl, n + 'CTL')
            grp = mc.rename(grp, n + 'GRP')
            self.fkCtlGrps.append(grp)
            self.fkCtls.append(ctl)
            mc.parent(grp, oriGrp)
            mc.parent(i, ctl)
            par = i

        # create hipFk ctl
        self.hipFkOriGrp = mc.createNode('transform', name = 'hipFKOri_GRP', p = self.spineFkGrp)
        trsLib.match(self.hipFkOriGrp, self.spineFkJnts[0])
        ctl, grp = funcs.createCtl(parent = self.hipFkOriGrp,side = 'C',scale = [35, 17, 30],shape = 'cube',
                                   orient = (0,1,0),moveShape=[0,0,0])
        name = self.hipFkOriGrp.replace('Ori_GRP', '_GRP')
        self.spineFkHipCtlGrp = mc.rename(grp , name)
        name = self.hipFkOriGrp.replace('Ori_GRP', '_CTL')
        self.spineFKHipCtl = mc.rename(ctl, name)
        mc.parent(self.spineFkHipCtlGrp, self.hipFkOriGrp)
        mc.parent(self.spineFkJnts[0],self.spineFKHipCtl )

        # ***************connect stuf****************
        # parent and scale constraint hip fk and ik joints to hip blendOriGrp
        mc.parentConstraint(self.spineFkJnts[0],self.spineIkJnts[0],self.hipBlendOriGrp, mo = True)
        mc.scaleConstraint(self.spineFkJnts[0],self.spineIkJnts[0],self.hipBlendOriGrp, mo = True)

        for i in ['sx', 'sy', 'sz']:
            mc.connectAttr(self.hipBlendOriGrp + '.' + i,self.hipBlendModGrp + '.' + i)

        # parent and scale constraint spine ik and fk joints tp spineBlendOri grp
        mc.parentConstraint(self.spineFkJnts[1], self.spineIkJnts[1],self.spineBlend1OriGrp, mo = True)
        mc.scaleConstraint(self.spineFkJnts[1], self.spineIkJnts[1],self.spineBlend1OriGrp, mo = True)

        # create breath ctls
        self.breathOriGrps = []
        self.breathGrps = []
        self.breathCtls = []
        for i, j  in zip(self.spineFkJnts[1:4], ['low', 'mid', 'top']):
            n = self.name + '_breath_' + '{}'.format(j)
            oriGrp = mc.createNode('transform', name  = n + 'Ori_GRP', p  = self.extrasGrp)
            trsLib.match(oriGrp, i)
            self.breathOriGrps.append(oriGrp)
            ctl, grp = funcs.createCtl(parent=oriGrp, side='C', scale=[1, 1, 1], shape='cube',
                                       orient=(0, 1, 0), moveShape=[0, 0, 0])
            ctl = mc.rename(ctl, n + '_CTL')
            grp = mc.rename(grp, n + '_GRP')
            self.breathGrps.append(grp)
            self.breathCtls.append(ctl)
            mc.parent(grp, oriGrp)
            mc.move(0, 0, 20, oriGrp, r=True, ws=True)

        mc.setAttr(self.breathOriGrps[2] + '.rx', 65)
        mc.move(0, 8, -3, self.breathOriGrps[2], r=True, ws=True)

        # connect breath low ctl to the spineBlend breathMod grp
        [mc.connectAttr(self.breathCtls[0] + '.{}{}'.format(a, v), self.spineBlendBreatherModGrp + '.{}{}'.format(a, v)) for a in'trs' for v in 'xyz']

        # parent and scale constraint spine2 ik and fk to the spine blend 2 grp
        mc.parentConstraint(self.spineFkJnts[2], self.spineIkJnts[2],self.spineBlend2OriGrp, mo = True)
        mc.scaleConstraint(self.spineFkJnts[2], self.spineIkJnts[2],self.spineBlend2OriGrp, mo = True)

        # connect breath mic ctl to the spineBlend breathMod grp
        [mc.connectAttr(self.breathCtls[1] + '.{}{}'.format(a, v), self.spineBlendBreather2OriGrp + '.{}{}'.format(a, v)) for a in'trs' for v in 'xyz']

        # parent and scale constraint spine3 ik and fk to the spine blend 3 grp
        mc.parentConstraint(self.spineFkJnts[3], self.spineIkJnts[3],self.spineBlend3OriGrp, mo = True)
        mc.scaleConstraint(self.spineFkJnts[3], self.spineIkJnts[3],self.spineBlend3OriGrp, mo = True)

        # parent and scale constraint spine4 ik and fk to the spine blend 4 grp
        mc.parentConstraint(self.spineFkJnts[4], self.spineIkJnts[4],self.spineBlend4OriGrp, mo = True)
        mc.scaleConstraint(self.spineFkJnts[4], self.spineIkJnts[4],self.spineBlend4OriGrp, mo = True)

        #todo scale constraint global ctl to the spineIkdrivers grp later

        #todo parent constraint body and global locas to the spine hip drvrOri grp later

        # add attr on spineIkHipCtl and spineIkOffsetHipCtl
        attrLib.addFloat(self.spineIkHipCtl, ln = 'offsetCtl', min = 0, max = 1, dv = 0)
        attrLib.addFloat(self.spineIkHipCtl, ln = 'globalScale', min = 0, max = 1, dv = 0)
        attrLib.addFloat(self.spineIkHipCtl, ln = 'rotPivotHeight', min = 4, max = 16, dv = 4)

        attrLib.addFloat(self.spineIkHipOffsetCtl, ln = 'globalScale', min = 0, max = 1, dv = 0)

        # connect spineIkHipCtl to the spineIkHipPivotLoc
        mc.connectAttr(self.spineIkHipCtl + '.rotPivotHeight',self.spineIkHipPivotLoc + '.ty')

        #todo parent constraint body and global locas to the spine chest drvrOri grp later
        attrLib.addFloat(self.spineIkChestCtl, ln = 'offsetCtl', min = 0, max = 1, dv = 0)
        attrLib.addFloat(self.spineIkChestCtl, ln = 'globalScale', min = 0, max = 1, dv = 0)
        attrLib.addFloat(self.spineIkChestCtl, ln = 'offsetTopCtl', min = 0, max = 1, dv = 0)
        attrLib.addFloat(self.spineIkChestCtl, ln = 'rotPivotHeight', min = -30, max = 0, dv = -30)

        # connect spineIkChestCtl to the spineIkChestPivotLoc
        mc.connectAttr(self.spineIkChestCtl + '.rotPivotHeight',self.spineIkChestPivotLoc + '.ty')

        # parent constraint chest and hip ctl to the spineIkWaistDrvrGrp
        mc.parentConstraint(self.spineIkChestCtl,self.spineIkHipCtl,self.spineIkWaistDrvrOriGrp, mo = True)

        #todo scale constarint global ctl to the spine ik jnt grp later
        #todo scale constarint global ctl to the spine fk jnt grp later

        #todo parent constraint bodyOffset ctl to the spineFK1OriGrp and hip fk ori grp later



    def connect(self):
        super(SpineB, self).connect()


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(SpineB, self).createSettings()








