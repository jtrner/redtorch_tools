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
                        'headTop_squashGuide_04':'headTop_squashGuide_04',
                        'Flood':'Flood',
                        'headTopSquashDrvrJnt':'headTopSquashDrvrJnt',
                        'headBotSquashDrvrJnt':'headBotSquashDrvrJnt',
                        'l_headMidSquashDrvrJnt': 'l_headMidSquashDrvrJnt',
                        'r_headMidSquashDrvrJnt': 'r_headMidSquashDrvrJnt'
                        }

    def createBlueprint(self):
        super(BuildHead, self).createBlueprint()
        self.blueprints['headTopSquashDrvrJnt'] = '{}_headTopSquashDrvrJnt_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headTopSquashDrvrJnt']):
            mc.joint(self.blueprintGrp, name=self.blueprints['headTopSquashDrvrJnt'])
            mc.xform(self.blueprints['headTopSquashDrvrJnt'], ws=True, t=(0, 183.472, -2.934))

        self.blueprints['headBotSquashDrvrJnt'] = '{}_headBotSquashDrvrJnt_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['headBotSquashDrvrJnt']):
            mc.joint(self.blueprintGrp, name=self.blueprints['headBotSquashDrvrJnt'])
            mc.xform(self.blueprints['headBotSquashDrvrJnt'], ws=True, t=(0, 165.226, -2.934))

        self.blueprints['l_headMidSquashDrvrJnt'] = 'l_headMidSquashDrvrJnt_BLU'
        if not mc.objExists(self.blueprints['l_headMidSquashDrvrJnt']):
            mc.joint(self.blueprintGrp, name=self.blueprints['l_headMidSquashDrvrJnt'])
            mc.xform(self.blueprints['l_headMidSquashDrvrJnt'], ws=True, t=(1.1, 175.214, -2.934))

        self.blueprints['r_headMidSquashDrvrJnt'] = 'r_headMidSquashDrvrJnt_BLU'
        if not mc.objExists(self.blueprints['r_headMidSquashDrvrJnt']):
            mc.joint(self.blueprintGrp, name=self.blueprints['r_headMidSquashDrvrJnt'])
            mc.xform(self.blueprints['r_headMidSquashDrvrJnt'], ws=True, t=(-1.1, 175.214, -2.934))

        self.blueprints['Flood'] = '{}_Flood_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['Flood']):
            mc.joint(self.blueprintGrp, name=self.blueprints['Flood'])
            mc.xform(self.blueprints['Flood'], ws=True, t=(0, 178.813, -5.773))

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
        self.headSquashDrvrJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('headTopSquashDrvrJnt', 'headBotSquashDrvrJnt','l_headMidSquashDrvrJnt','r_headMidSquashDrvrJnt'):
                continue
            jnt = '{}_JNT'.format(self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.headSquashDrvrJnts.append(jnt)

        par = self.moduleGrp
        self.headFloodJnt = []
        for alias, blu in self.blueprints.items():
            if not alias in ('Flood'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.headFloodJnt.append(jnt)

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

        self.setOut('squashFirst', self.buttomJntSquash[0])
        self.setOut('squashSecond', self.buttomJntSquash[1])
        self.setOut('squashThird', self.buttomJntSquash[2])

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

        self.setOut('topSquashFirst', self.topJntSquash[0])
        self.setOut('topSquashSecond', self.topJntSquash[1])


    def build(self):
        super(BuildHead, self).build()
        funcs.detachHead(geoName = self.geo,edge = self.headEdge,name = 'localEyeLid_GEO', movement = self.headMovement)
        self.setOut('eyelidsGeo', 'localEyeLid_GEO')

        self.localLipsGeo = mc.duplicate('localEyeLid_GEO', name = 'localLips_GEO')
        mc.move(0,self.headMovement, 0,self.localLipsGeo ,r = True, ws = True )
        self.setOut('lipsGeo', self.localLipsGeo[0] )

        self.localBrowsGeo = mc.duplicate('localLips_GEO', name = 'localBrow_GEO')
        mc.move(0,self.headMovement, 0,self.localBrowsGeo ,r = True, ws = True )
        self.setOut('eyebrowsGeo', self.localBrowsGeo[0] )

        self.localMiscGeo = mc.duplicate('localBrow_GEO', name = 'localMisc_GEO')
        mc.move(0,self.headMovement, 0,self.localMiscGeo ,r = True, ws = True )
        self.setOut('miscGeo', self.localMiscGeo[0] )


        # create head buttom ctl
        ctl,grp = funcs.createCtl(parent = self.headButtomCtlOriGrp,side = self.side,scale = [15,15,17])
        self.buttomHeadCtl = mc.rename(ctl, 'headBottom_CTL')
        self.buttomHeadCtlGrp = mc.rename(grp, 'headBottomCtlMod_GRP')
        mc.parent(self.buttomHeadCtlGrp, self.headButtomCtlOriGrp)
        self.setOut('ribbonCtlsParent', self.buttomHeadCtl )

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

        # duplicate buttom squash joints
        self.headBotGlobalJnts = trsLib.duplicate(self.buttomJntSquash[0], search = 'head', replace = 'global', hierarchy = True)
        mc.parent(self.headBotGlobalJnts[0],self.globalBotJntModGrp )

        # duplicate top squash joints
        self.headTopGlobalJnts = trsLib.duplicate(self.topJntSquash[0], search = 'head', replace = 'global', hierarchy = True)
        mc.parent(self.headTopGlobalJnts[0],self.globalTopJntModGrp )

        self.botSquashCurve = crvLib.fromJnts(self.buttomJntSquash, degree=3, name='headBotSquashIk_CRV')
        self.botSquashCurve = mc.listRelatives(self.botSquashCurve, parent = True)[0]
        mc.parent(self.botSquashCurve ,self.globalBotJntModGrp)


        self.topSquashCurve = crvLib.fromJnts(self.topJntSquash, degree=3, name='headTopSquashIk_CRV')
        self.topSquashCurve = mc.listRelatives(self.topSquashCurve, parent = True)[0]


        self.headTopIkHandle = mc.ikHandle(n='headTopSquash_IKH', sj=self.topJntSquash[0], ee=self.topJntSquash[-1],
                                           sol='ikSplineSolver',c=self.topSquashCurve, ccv=False)[0]
        mc.parent(self.topSquashCurve ,self.globalTopJntModGrp)
        mc.parent(self.headTopIkHandle ,self.headSquashMechanicGrp)

        self.headBotIkHandle = mc.ikHandle(n='headButtomSquash_IKH', sj=self.buttomJntSquash[0], ee=self.buttomJntSquash[-1],
                                           sol='ikSplineSolver', c=self.botSquashCurve, ccv=False)[0]
        mc.parent(self.botSquashCurve ,self.globalBotJntModGrp)
        mc.parent(self.headBotIkHandle ,self.headSquashMechanicGrp)

        # create hierarchy for squash drvr joints
        self.headMidSquashDrvrOriGrp = mc.createNode('transform', name = 'headMid_SquetchDriverOri_GRP', p = self.headSquashMechanicGrp)
        mc.delete(mc.parentConstraint(self.headSquashDrvrJnts[-1],self.headSquashDrvrJnts[-2], self.headMidSquashDrvrOriGrp ))
        self.headMidSquashDrvrModGrp = mc.createNode('transform', name = 'headMid_SquetchDriverMod_GRP', p = self.headMidSquashDrvrOriGrp)
        mc.parent(self.headSquashDrvrJnts[-1],self.headSquashDrvrJnts[-2], self.headMidSquashDrvrModGrp)

        self.headTopSquashDrvrOriGrp = mc.createNode('transform', name='headTop_SquetchDriverOri_GRP',p=self.headSquashMechanicGrp)
        mc.delete(mc.parentConstraint(self.headSquashDrvrJnts[0],  self.headTopSquashDrvrOriGrp))
        self.headTopSquashDrvrModGrp = mc.createNode('transform', name='headTop_SquetchDriverMod_GRP',p=self.headTopSquashDrvrOriGrp)
        mc.parent(self.headSquashDrvrJnts[0], self.headTopSquashDrvrModGrp)

        self.headBotSquashDrvrOriGrp = mc.createNode('transform', name='headBot_SquetchDriverOri_GRP',p=self.headSquashMechanicGrp)
        mc.delete(mc.parentConstraint(self.headSquashDrvrJnts[1],  self.headBotSquashDrvrOriGrp))
        self.headBotSquashDrvrModGrp = mc.createNode('transform', name='headBot_SquetchDriverMod_GRP',p=self.headBotSquashDrvrOriGrp)
        mc.parent(self.headSquashDrvrJnts[1], self.headBotSquashDrvrModGrp)

        # create curve on top and buttom squash joints
        self.buttomJntSquash.reverse()
        self.allJntsSquash =  self.buttomJntSquash + self.topJntSquash

        self.masterHeadCurve = crvLib.fromJnts(self.allJntsSquash, degree = 3 ,name = 'headSquetchMaster_CRV')
        self.masterHeadCurve = mc.listRelatives(self.masterHeadCurve, parent = True)[0]
        mc.parent(self.masterHeadCurve, self.headSquashMechanicGrp)

        # create wire for top and bot head squash curves
        for i in [self.topSquashCurve ,self.botSquashCurve ]:
            mc.select(i, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.masterHeadCurve)

        self.headSquashDrvrJnts.pop(-1)
        deformLib.bind_geo(geos = self.masterHeadCurve, joints = self.headSquashDrvrJnts)

        self.squashCtls = []
        self.squashGrps = []
        for i in [self.botSquashOriGrp,self.midSquashOriGrp,self.topSquashOriGrp]:
            ctl, grp = funcs.createCtl(parent = i ,side = 'C',scale = [1, 1, 1], shape = 'sphere')
            newName = i.replace('Ori_GRP', '_CTL')
            ctl = mc.rename(ctl, newName)
            self.squashCtls.append(ctl)
            newName = ctl.replace('_CTL', '_ZRO')
            grp = mc.rename(grp, newName)
            self.squashGrps.append(grp)
            mc.parent(grp, i)












