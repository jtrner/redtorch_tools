
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

        # parent blendSpine jnts under stuf
        mc.parent(self.spineBlendJnts[0],self.hipBlendModGrp)
        #todo create left and right hip space locators on leg module and parent them under hipBlendJnts

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
        mc.parent()


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

    def connect(self):
        super(SpineB, self).connect()


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(SpineB, self).createSettings()








