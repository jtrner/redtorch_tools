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
from . import miscTemplate

reload(miscTemplate)
reload(funcs)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


class BulidMisc(miscTemplate.MiscTemplate):
    """Class for creating misc"""
    def __init__(self,  **kwargs ):
        super(BulidMisc, self).__init__(**kwargs)

        self.aliases = {'Flood':'Flood',
                        'Apple':'apple',
                        'nasal':'nasal',
                        'browFlesh':'browFlesh',
                        'cheek':'cheek',
                        'nasalLabial':'nasalLabial',
                        'orbitalUpper':'orbitalUpper',
                        'orbitalLower':'orbitalLower',
                        'cheekLower':'cheekLower',
                        'ear':'ear',
                        'earUpper':'earUpper',
                        'earLower':'earLower'}

    def createBlueprint(self):
        super(BulidMisc, self).createBlueprint()
        self.blueprints['Flood'] = '{}_Flood_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['Flood']):
            mc.joint(self.blueprintGrp, name=self.blueprints['Flood'])
            mc.xform(self.blueprints['Flood'], ws=True, t=(48.471, 358.916, -5.011))

        self.blueprints['Apple'] = '{}_Apple_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['Apple']):
            mc.joint(self.blueprintGrp, name=self.blueprints['Apple'])
            mc.xform(self.blueprints['Apple'], ws=True, t=(48.484, 343.205, -0.802))

        self.blueprints['nasal'] = '{}_nasal_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['nasal']):
            mc.joint(self.blueprintGrp, name=self.blueprints['nasal'])
            mc.xform(self.blueprints['nasal'], ws=True, t=(49.559, 356.724, 2.987))

        self.blueprints['browFlesh'] = '{}_browFlesh_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['browFlesh']):
            mc.joint(self.blueprintGrp, name=self.blueprints['browFlesh'])
            mc.xform(self.blueprints['browFlesh'], ws=True, t=(50.793, 358.822, 2.976))

        self.blueprints['cheek'] = '{}_cheek_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['cheek']):
            mc.joint(self.blueprintGrp, name=self.blueprints['cheek'])
            mc.xform(self.blueprints['cheek'], ws=True, t=(51.346, 354.757, 2.635))

        self.blueprints['nasalLabial'] = '{}_nasalLabial_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['nasalLabial']):
            mc.joint(self.blueprintGrp, name=self.blueprints['nasalLabial'])
            mc.xform(self.blueprints['nasalLabial'], ws=True, t=(51.06, 352.676, 2.962))

        self.blueprints['orbitalUpper'] = '{}_orbitalUpper_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['orbitalUpper']):
            mc.joint(self.blueprintGrp, name=self.blueprints['orbitalUpper'])
            mc.xform(self.blueprints['orbitalUpper'], ws=True, t=(53.327,358.318, 0.899))

        self.blueprints['orbitalLower'] = '{}_orbitalLower_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['orbitalLower']):
            mc.joint(self.blueprintGrp, name=self.blueprints['orbitalLower'])
            mc.xform(self.blueprints['orbitalLower'], ws=True, t=(53.357,356.045, 0.8))

        self.blueprints['cheekLower'] = '{}_cheekLower_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['cheekLower']):
            mc.joint(self.blueprintGrp, name=self.blueprints['cheekLower'])
            mc.xform(self.blueprints['cheekLower'], ws=True, t=(52.685,350.353, 0.718))

        self.blueprints['ear'] = '{}_ear_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['ear']):
            mc.joint(self.blueprintGrp, name=self.blueprints['ear'])
            mc.xform(self.blueprints['ear'], ws=True, t=(53.838,355.788, -5.669))

        self.blueprints['earUpper'] = '{}_earUpper_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['earUpper']):
            mc.joint(self.blueprintGrp, name=self.blueprints['earUpper'])
            mc.xform(self.blueprints['earUpper'], ws=True, t=(54.056,356.514, -6.992))

        self.blueprints['earLower'] = '{}_earLower_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['earLower']):
            mc.joint(self.blueprintGrp, name=self.blueprints['earLower'])
            mc.xform(self.blueprints['earLower'], ws=True, t=(54.028,354.785, -6.376))


    def createJoints(self):
        par = self.moduleGrp
        self.miscJnts = []
        for alias, blu in self.blueprints.items():
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            self.miscJnts.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
    def build(self):
        super(BulidMisc, self).build()

        self.earUpperOriGrp = mc.createNode('transform', name = self.side + '_earUpperOri_GRP', p = self.miscJnts[-3])
        self.earUpperModGrp = mc.createNode('transform', name = self.side + '_earUpperMod_GRP', p = self.earUpperOriGrp)
        trsLib.match(self.earUpperOriGrp,self.miscJnts[10])
        mc.parent(self.miscJnts[10],self.earUpperModGrp)

        self.earLowerOriGrp = mc.createNode('transform', name = self.side + '_earLowerOri_GRP', p = self.miscJnts[-3])
        self.earLowerModGrp = mc.createNode('transform', name = self.side + '_earUpperMod_GRP', p = self.earLowerOriGrp)
        trsLib.match(self.earLowerOriGrp,self.miscJnts[11])
        mc.parent(self.miscJnts[11],self.earLowerModGrp)

        # create transform for parenting control groups to them
        self.nasalLabialCtlOriGrp = mc.createNode('transform', name = self.side + '_nasalLabialCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.nasalLabialCtlOriGrp,self.miscJnts[5])
        self.cheekCtlOriGrp = mc.createNode('transform', name = self.side + '_cheekCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.cheekCtlOriGrp,self.miscJnts[4])
        self.browFleshCtlOriGrp = mc.createNode('transform', name = self.side + '_browFleshCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.browFleshCtlOriGrp,self.miscJnts[3])
        self.orbitalUpperCtlOriGrp = mc.createNode('transform', name = self.side + '_orbitalUpperCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.orbitalUpperCtlOriGrp,self.miscJnts[6])
        self.earCtlOriGrp = mc.createNode('transform', name = self.side + '_earCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.earCtlOriGrp,self.miscJnts[-3])
        self.nasalCtlOriGrp = mc.createNode('transform', name = self.side  + '_nasalCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.nasalCtlOriGrp,self.miscJnts[2])
        self.orbitalLowerCtlOriGrp = mc.createNode('transform', name = self.side + '_orbitalLowerCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.orbitalLowerCtlOriGrp,self.miscJnts[7])
        self.appleCtlOriGrp = mc.createNode('transform', name = self.side + '_appleCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.appleCtlOriGrp,self.miscJnts[1])
        self.cheekLowerCtlOriGrp = mc.createNode('transform', name = self.side + '_cheekLowerCtlOri_GRP', p = self.miscsCtlGrp)
        trsLib.match(self.cheekLowerCtlOriGrp,self.miscJnts[-4])

        # create controls
        self.miscCtls = []
        self.miscGrps = []
        for i in [self.nasalLabialCtlOriGrp,self.cheekCtlOriGrp,self.browFleshCtlOriGrp,self.orbitalUpperCtlOriGrp,
                  self.earCtlOriGrp,self.nasalCtlOriGrp,self.orbitalLowerCtlOriGrp,self.appleCtlOriGrp,self.cheekLowerCtlOriGrp]:
            i = i.split('|')[-1]
            ctl, grp = funcs.createCtl(parent = i, side = self.side)
            newName = i.replace('CtlOri_GRP', 'Mod_GRP')
            grp = mc.rename(grp, newName)
            self.miscGrps.append(grp)
            mc.parent(grp, i)
            newName = grp.replace('Mod_GRP', '_CTL')
            ctl = mc.rename(ctl,newName)
            self.miscCtls.append(ctl)

        # create lower and upper ear ctl
        self.earLowerCtlOriGrp = mc.createNode('transform', name = self.side + '_earLowerCtlOri_GRP', p = self.miscCtls[4])
        trsLib.match(self.earLowerCtlOriGrp,self.miscJnts[11])
        self.earUpperCtlOriGrp = mc.createNode('transform', name = self.side + '_earUpperCtlOri_GRP', p = self.miscCtls[4])
        trsLib.match(self.earUpperCtlOriGrp,self.miscJnts[10])

        for i in [self.earLowerCtlOriGrp,self.earUpperCtlOriGrp]:
            i = i.split('|')[-1]
            ctl, grp = funcs.createCtl(parent = i, side = self.side)
            newName = i.replace('CtlOri_GRP', 'Mod_GRP')
            grp = mc.rename(grp, newName)
            self.miscGrps.append(grp)
            mc.parent(grp, i)
            newName = grp.replace('Mod_GRP', '_CTL')
            ctl = mc.rename(ctl,newName)
            self.miscCtls.append(ctl)

        # create cheekRaise and cheekSub ctls
        self.cheekRaiseOriCtlGrp = mc.createNode('transform', name = self.side + '_cheekRaiseori_GRP', p = self.miscCtls[1])
        mc.move(0,1,0,self.cheekRaiseOriCtlGrp, r = True, ws = True)
        #TODO:cheekRaiseOriCtlGrp should be matched to the cheek joint which is in eyelid module
        self.cheekSubCtlOriGrp = mc.createNode('transform', name = self.side + '_cheekSubCtrlori_GRP', p = self.miscCtls[1])

        for i in [self.cheekRaiseOriCtlGrp,self.cheekSubCtlOriGrp]:
            i = i.split('|')[-1]
            ctl, grp = funcs.createCtl(parent = i, side = self.side, scale = [0.5,0.5,0.5])
            newName = i.replace('ori_GRP', 'Mod_GRP')
            grp = mc.rename(grp, newName)
            self.miscGrps.append(grp)
            mc.parent(grp, i)
            newName = grp.replace('Mod_GRP', '_CTL')
            ctl = mc.rename(ctl,newName)
            self.miscCtls.append(ctl)



