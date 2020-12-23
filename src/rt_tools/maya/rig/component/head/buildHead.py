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
from . import headTemplate

reload(headTemplate)
reload(funcs)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


class BuildHead(headTemplate.HeadTemplate):
    """Class for creating head"""
    def __init__(self,  **kwargs ):
        super(BuildHead, self).__init__(**kwargs)

        self.aliases = {'headBot_squashGuide_01':'headBot_squashGuide_01',
                        'headBot_squashGuide_02':'headBot_squashGuide_02',
                        'headBot_squashGuide_03':'headBot_squashGuide_03',
                        'headBot_squashGuide_04':'headBot_squashGuide_04',
                        'headBot_squashGuide_05':'headBot_squashGuide_05',
                        'headTop_squashGuide_01':'headTop_squashGuide_01',
                        'headTop_squashGuide_02':'headTop_squashGuide_02',
                        'headTop_squashGuide_03':'headTop_squashGuide_03',
                        'headTop_squashGuide_04':'headTop_squashGuide_04',}

    def createBlueprint(self):
        super(BuildHead, self).createBlueprint()
        self.blueprints['headBot_squashGuide_01'] = '{}_headBot_squashGuide_01_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBot_squashGuide_01']):
            mc.joint(self.blueprintGrp, name=self.blueprints['headBot_squashGuide_01'])
            mc.xform(self.blueprints['headBot_squashGuide_01'], ws=True, t=(0, 175.224, -2.934))

        self.blueprints['headBot_squashGuide_02'] = '{}_headBot_squashGuide_02_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBot_squashGuide_02']):
            mc.joint(self.blueprints['headBot_squashGuide_01'] , name=self.blueprints['headBot_squashGuide_02'])
            mc.xform(self.blueprints['headBot_squashGuide_02'], ws=True, t=(0, 172.734, -2.934))

        self.blueprints['headBot_squashGuide_03'] = '{}_headBot_squashGuide_03_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBot_squashGuide_03']):
            mc.joint(self.blueprints['headBot_squashGuide_02'] , name=self.blueprints['headBot_squashGuide_03'])
            mc.xform(self.blueprints['headBot_squashGuide_03'], ws=True, t=(0, 170.196, -2.934))

        self.blueprints['headBot_squashGuide_04'] = '{}_headBot_squashGuide_04_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBot_squashGuide_04']):
            mc.joint(self.blueprints['headBot_squashGuide_03'] , name=self.blueprints['headBot_squashGuide_04'])
            mc.xform(self.blueprints['headBot_squashGuide_04'], ws=True, t=(0, 167.735, -2.934))

        self.blueprints['headBot_squashGuide_05'] = '{}_headBot_squashGuide_05_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBot_squashGuide_05']):
            mc.joint(self.blueprints['headBot_squashGuide_04'] , name=self.blueprints['headBot_squashGuide_05'])
            mc.xform(self.blueprints['headBot_squashGuide_05'], ws=True, t=(0, 165.226, -2.934))

        self.blueprints['headTop_squashGuide_01'] = '{}_headTop_squashGuide_01_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headTop_squashGuide_01']):
            mc.joint(self.blueprintGrp , name=self.blueprints['headTop_squashGuide_01'])
            mc.xform(self.blueprints['headTop_squashGuide_01'], ws=True, t=(0, 175.988, -2.934))

        self.blueprints['headTop_squashGuide_02'] = '{}_headTop_squashGuide_02_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headTop_squashGuide_02']):
            mc.joint(self.blueprints['headTop_squashGuide_01'] , name=self.blueprints['headTop_squashGuide_02'])
            mc.xform(self.blueprints['headTop_squashGuide_02'], ws=True, t=(0, 178.484, -2.934))

        self.blueprints['headTop_squashGuide_03'] = '{}_headTop_squashGuide_03_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headTop_squashGuide_03']):
            mc.joint(self.blueprints['headTop_squashGuide_02'] , name=self.blueprints['headTop_squashGuide_03'])
            mc.xform(self.blueprints['headTop_squashGuide_03'], ws=True, t=(0, 180.99, -2.934))

        self.blueprints['headTop_squashGuide_04'] = '{}_headTop_squashGuide_04_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headTop_squashGuide_04']):
            mc.joint(self.blueprints['headTop_squashGuide_03'] , name=self.blueprints['headTop_squashGuide_04'])
            mc.xform(self.blueprints['headTop_squashGuide_04'], ws=True, t=(0, 183.472, -2.934))

    def createJoints(self):
        par = self.moduleGrp
        self.buttomJntSquash = []
        for alias, blu in self.blueprints.items():
            if not alias in ('headBot_squashGuide_01', 'headBot_squashGuide_02', 'headBot_squashGuide_03',
                             'headBot_squashGuide_04', 'headBot_squashGuide_05'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.buttomJntSquash.append(jnt)
            par = jnt
        par = self.moduleGrp
        self.topJntSquash = []
        for alias, blu in self.blueprints.items():
            if not alias in ('headTop_squashGuide_01', 'headTop_squashGuide_02', 'headTop_squashGuide_03',
                             'headTop_squashGuide_04', 'headTop_squashGuide_05'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.topJntSquash.append(jnt)
            par = jnt


    def build(self):
        super(BuildHead, self).build()
        # funcs.detachHead(geoName = self.geo,edge = self.headEdge,name = 'localEyeLid_GEO', movement = self.headMovement)
        #
        # self.localLipsGeo = mc.duplicate('localEyeLid_GEO', name = 'localLips_GEO')
        # mc.move(0,50, 0,self.localLipsGeo ,r = True, ws = True )
        #
        # self.localBrowsGeo = mc.duplicate('localLips_GEO', name = 'localBrow_GEO')
        # mc.move(0,50, 0,self.localBrowsGeo ,r = True, ws = True )
        #
        # self.localMiscGeo = mc.duplicate('localBrow_GEO', name = 'localMisc_GEO')
        # mc.move(0,50, 0,self.localMiscGeo ,r = True, ws = True )


        # create head buttom ctl
        ctl,grp = funcs.createCtl(parent = self.headButtomCtlOriGrp,side = self.side,scale = [15,15,17])
        self.buttomHeadCtl = mc.rename(ctl, 'headBottom_CTL')
        self.buttomHeadCtlGrp = mc.rename(grp, 'headBottomCtlMod_GRP')
        mc.parent(self.buttomHeadCtlGrp, self.headButtomCtlOriGrp)

        # create head top ctl
        ctl,grp = funcs.createCtl(parent = self.headTopCtlOriGrp,side = self.side,scale = [15,15,17])
        self.topHeadCtl = mc.rename(ctl, 'headTop_CTL')
        self.topHeadCtlGrp = mc.rename(grp, 'headTopCtlMod_GRP')
        mc.parent(self.topHeadCtlGrp, self.headTopCtlOriGrp)

        self.headBotSquashCtlOriGrp = mc.createNode('transform' , name = 'headBotSquatchCtrlGuideOri_GRP', p = self.buttomHeadCtl)
        self.headBotSquashCtlModGrp = mc.createNode('transform' , name = 'headBotSquatchCtrlGuideMod_GRP', p = self.headBotSquashCtlOriGrp)
        mc.parent(self.buttomJntSquash[0] ,self.headBotSquashCtlModGrp )

        self.headTopSquashCtlOriGrp = mc.createNode('transform' , name = 'headTopSquatchCtrlGuideOri_GRP', p = self.topHeadCtl)
        self.headTopSquashCtlModGrp = mc.createNode('transform' , name = 'headTopSquatchCtrlGuideMod_GRP', p = self.headTopSquashCtlOriGrp)
        mc.parent(self.topJntSquash[0] ,self.headTopSquashCtlModGrp )



