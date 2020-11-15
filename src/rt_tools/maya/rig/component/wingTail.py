import maya.cmds as mc
import maya.api.OpenMaya as om2
from collections import OrderedDict

from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import connect
from ...lib import trsLib
from ...lib import display
from ...lib import crvLib
from ...lib import jntLib
from . import template
from ..command import fk


reload(connect)
reload(attrLib)
reload(display)
reload(fk)
reload(control)
reload(crvLib)
reload(attrLib)
reload(jntLib)
reload(trsLib)
reload(template)


class WingTail(template.Template):

    def __init__(self, side='C', prefix='wingTail', **kwargs):

        kwargs['side'] = side
        kwargs['prefix'] = prefix

        self.aliases = {'firstPrimaryStart': 'firstPrimaryStart','firstPrimaryEnd': 'firstPrimaryEnd',
                        'feather_a_0' : 'feather_a_0','feather_a_1': 'feather_a_1',
                        'feather_a_2': 'feather_a_2','feather_b_0': 'feather_b_0',
                        'feather_b_1': 'feather_b_1','feather_b_2': 'feather_b_2',
                        'feather_c_0': 'feather_c_0','feather_c_1': 'feather_c_1',
                        'feather_c_2': 'feather_c_2','feather_d_0': 'feather_d_0',
                        'feather_d_1': 'feather_d_1', 'feather_d_2': 'feather_d_2',
                        'feather_e_2': 'feather_e_2','secondPrimaryStart': 'secondPrimaryStart',
                        'secondPrimaryEnd': 'secondPrimaryEnd','feather_f_0': 'feather_f_0',
                        'feather_e_0': 'feather_e_0', 'feather_e_1': 'feather_e_1',
                        'feather_f_1': 'feather_f_1','feather_f_2': 'feather_f_2',
                        'feather_g_0': 'feather_g_0','feather_g_1': 'feather_g_1',
                        'feather_g_2': 'feather_g_2','feather_h_0': 'feather_h_0',
                        'feather_h_1': 'feather_h_1', 'feather_h_2': 'feather_h_2',
                        'thirdPrimaryStart': 'thirdPrimaryStart', 'thirdPrimaryEnd': 'thirdPrimaryEnd'}

        super(WingTail, self).__init__(**kwargs)

    def createBlueprint(self):
        super(WingTail, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        par = self.blueprintGrp


        self.blueprints['firstPrimaryStart'] = '{}_firstPrimaryStart_BLU'.format(self.name)
        self.blueprints['firstPrimaryEnd'] = '{}_firstPrimaryEnd_BLU'.format(self.name)

        self.blueprints['feather_a_0'] = '{}_feather_a_0_BLU'.format(self.name)
        self.blueprints['feather_a_1'] = '{}_feather_a_1_BLU'.format(self.name)
        self.blueprints['feather_a_2'] = '{}_feather_a_2_BLU'.format(self.name)

        self.blueprints['feather_b_0'] = '{}_feather_b_0_BLU'.format(self.name)
        self.blueprints['feather_b_1'] = '{}_feather_b_1_BLU'.format(self.name)
        self.blueprints['feather_b_2'] = '{}_feather_b_2_BLU'.format(self.name)

        self.blueprints['feather_c_0'] = '{}_feather_c_0_BLU'.format(self.name)
        self.blueprints['feather_c_1'] = '{}_feather_c_1_BLU'.format(self.name)
        self.blueprints['feather_c_2'] = '{}_feather_c_2_BLU'.format(self.name)

        self.blueprints['feather_d_0'] = '{}_feather_d_0_BLU'.format(self.name)
        self.blueprints['feather_d_1'] = '{}_feather_d_1_BLU'.format(self.name)
        self.blueprints['feather_d_2'] = '{}_feather_d_2_BLU'.format(self.name)

        self.blueprints['feather_e_0'] = '{}_feather_e_0_BLU'.format(self.name)
        self.blueprints['feather_e_1'] = '{}_feather_e_1_BLU'.format(self.name)
        self.blueprints['feather_e_2'] = '{}_feather_e_2_BLU'.format(self.name)

        self.blueprints['secondPrimaryStart'] = '{}_secondPrimaryStart_BLU'.format(self.name)
        self.blueprints['secondPrimaryEnd'] = '{}_secondPrimaryEnd_BLU'.format(self.name)

        self.blueprints['feather_f_0'] = '{}_feather_f_0_BLU'.format(self.name)
        self.blueprints['feather_f_1'] = '{}_feather_f_1_BLU'.format(self.name)
        self.blueprints['feather_f_2'] = '{}_feather_f_2_BLU'.format(self.name)

        self.blueprints['feather_g_0'] = '{}_feather_g_0_BLU'.format(self.name)
        self.blueprints['feather_g_1'] = '{}_feather_g_1_BLU'.format(self.name)
        self.blueprints['feather_g_2'] = '{}_feather_g_2_BLU'.format(self.name)

        self.blueprints['feather_h_0'] = '{}_feather_h_0_BLU'.format(self.name)
        self.blueprints['feather_h_1'] = '{}_feather_h_1_BLU'.format(self.name)
        self.blueprints['feather_h_2'] = '{}_feather_h_2_BLU'.format(self.name)


        self.blueprints['thirdPrimaryStart'] = '{}_thirdPrimaryStart_BLU'.format(self.name)
        self.blueprints['thirdPrimaryEnd'] = '{}_thirdPrimaryEnd_BLU'.format(self.name)


        # create input blueprints
        if not mc.objExists(self.blueprints['firstPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['firstPrimaryStart'])
            mc.xform(self.blueprints['firstPrimaryStart'], ws=True,  t=(-0.5, 3, -1.5))

        if not mc.objExists(self.blueprints['firstPrimaryEnd']):
            mc.joint(self.blueprints['firstPrimaryStart'], name=self.blueprints['firstPrimaryEnd'])
            mc.xform(self.blueprints['firstPrimaryEnd'], ws=True, t=(-1.5, 3, -4.5))

        if not mc.objExists(self.blueprints['secondPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['secondPrimaryStart'])
            mc.xform(self.blueprints['secondPrimaryStart'], ws=True, t=(0, 3, -2))

        if not mc.objExists(self.blueprints['secondPrimaryEnd']):
            mc.joint(self.blueprints['secondPrimaryStart'], name=self.blueprints['secondPrimaryEnd'])
            mc.xform(self.blueprints['secondPrimaryEnd'], ws=True, t=(0, 3, -5))

        if not mc.objExists(self.blueprints['thirdPrimaryStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['thirdPrimaryStart'])
            mc.xform(self.blueprints['thirdPrimaryStart'], ws=True, t=(0.5, 3, -1.5))

        if not mc.objExists(self.blueprints['thirdPrimaryEnd']):
            mc.joint(self.blueprints['thirdPrimaryStart'], name=self.blueprints['thirdPrimaryEnd'])
            mc.xform(self.blueprints['thirdPrimaryEnd'], ws=True, t=(1.5, 3, -4.5))

        if not mc.objExists(self.blueprints['feather_a_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_a_0'])
            mc.xform(self.blueprints['feather_a_0'], ws=True, t=(-0.4, 3, -1.6))

        if not mc.objExists(self.blueprints['feather_a_1']):
            mc.joint(self.blueprints['feather_a_0'], name=self.blueprints['feather_a_1'])
            mc.xform(self.blueprints['feather_a_1'], ws=True, t=(-0.8, 3, -3))

        if not mc.objExists(self.blueprints['feather_a_2']):
            mc.joint(self.blueprints['feather_a_1'], name=self.blueprints['feather_a_2'])
            mc.xform(self.blueprints['feather_a_2'], ws=True, t=(-1.3, 3, -4.7))

        if not mc.objExists(self.blueprints['feather_b_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_b_0'])
            mc.xform(self.blueprints['feather_b_0'], ws=True, t=(-0.3, 3, -1.7))

        if not mc.objExists(self.blueprints['feather_b_1']):
            mc.joint(self.blueprints['feather_b_0'], name=self.blueprints['feather_b_1'])
            mc.xform(self.blueprints['feather_b_1'], ws=True, t=(-0.6, 3, -3.1))

        if not mc.objExists(self.blueprints['feather_b_2']):
            mc.joint(self.blueprints['feather_b_1'], name=self.blueprints['feather_b_2'])
            mc.xform(self.blueprints['feather_b_2'], ws=True, t=(-1, 3, -4.9))

        if not mc.objExists(self.blueprints['feather_c_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_c_0'])
            mc.xform(self.blueprints['feather_c_0'], ws=True, t=(-0.2, 3, -1.8))

        if not mc.objExists(self.blueprints['feather_c_1']):
            mc.joint(self.blueprints['feather_c_0'], name=self.blueprints['feather_c_1'])
            mc.xform(self.blueprints['feather_c_1'], ws=True, t=(-0.4, 3, -3.2))

        if not mc.objExists(self.blueprints['feather_c_2']):
            mc.joint(self.blueprints['feather_c_1'], name=self.blueprints['feather_c_2'])
            mc.xform(self.blueprints['feather_c_2'], ws=True, t=(-0.7, 3, -5))

        if not mc.objExists(self.blueprints['feather_d_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_d_0'])
            mc.xform(self.blueprints['feather_d_0'], ws=True, t=(-0.1 , 3, -1.9))

        if not mc.objExists(self.blueprints['feather_d_1']):
            mc.joint(self.blueprints['feather_d_0'], name=self.blueprints['feather_d_1'])
            mc.xform(self.blueprints['feather_d_1'], ws=True, t=(-0.2 , 3, -3.3))

        if not mc.objExists(self.blueprints['feather_d_2']):
            mc.joint(self.blueprints['feather_d_1'], name=self.blueprints['feather_d_2'])
            mc.xform(self.blueprints['feather_d_2'], ws=True, t=(-0.35, 3, -5))

        if not mc.objExists(self.blueprints['feather_e_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_e_0'])
            mc.xform(self.blueprints['feather_e_0'], ws=True, t=(0.1 , 3, -1.9))

        if not mc.objExists(self.blueprints['feather_e_1']):
            mc.joint(self.blueprints['feather_e_0'], name=self.blueprints['feather_e_1'])
            mc.xform(self.blueprints['feather_e_1'], ws=True, t=(0.2, 3, -3.3))

        if not mc.objExists(self.blueprints['feather_e_2']):
            mc.joint(self.blueprints['feather_e_1'], name=self.blueprints['feather_e_2'])
            mc.xform(self.blueprints['feather_e_2'], ws=True, t=(0.35 , 3, -5))

        if not mc.objExists(self.blueprints['feather_f_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_f_0'])
            mc.xform(self.blueprints['feather_f_0'], ws=True, t=(0.2, 3, -1.8))

        if not mc.objExists(self.blueprints['feather_f_1']):
            mc.joint(self.blueprints['feather_f_0'], name=self.blueprints['feather_f_1'])
            mc.xform(self.blueprints['feather_f_1'], ws=True, t=(0.4, 3, -3.2))

        if not mc.objExists(self.blueprints['feather_f_2']):
            mc.joint(self.blueprints['feather_f_1'], name=self.blueprints['feather_f_2'])
            mc.xform(self.blueprints['feather_f_2'], ws=True, t=(0.7, 3, -5))

        if not mc.objExists(self.blueprints['feather_g_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_g_0'])
            mc.xform(self.blueprints['feather_g_0'], ws=True, t=(0.3, 3, -1.7))

        if not mc.objExists(self.blueprints['feather_g_1']):
            mc.joint(self.blueprints['feather_g_0'], name=self.blueprints['feather_g_1'])
            mc.xform(self.blueprints['feather_g_1'], ws=True, t=(0.6, 3, -3.1))

        if not mc.objExists(self.blueprints['feather_g_2']):
            mc.joint(self.blueprints['feather_g_1'], name=self.blueprints['feather_g_2'])
            mc.xform(self.blueprints['feather_g_2'], ws=True, t=(1, 3, -4.9))

        if not mc.objExists(self.blueprints['feather_h_0']):
            mc.joint(self.blueprintGrp, name=self.blueprints['feather_h_0'])
            mc.xform(self.blueprints['feather_h_0'], ws=True, t=(0.4, 3, -1.6))

        if not mc.objExists(self.blueprints['feather_h_1']):
            mc.joint(self.blueprints['feather_h_0'], name=self.blueprints['feather_h_1'])
            mc.xform(self.blueprints['feather_h_1'], ws=True, t=(0.8, 3, -3))

        if not mc.objExists(self.blueprints['feather_h_2']):
            mc.joint(self.blueprints['feather_h_1'], name=self.blueprints['feather_h_2'])
            mc.xform(self.blueprints['feather_h_2'], ws=True, t=(1.3, 3, -4.7))



        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)

    def createJoints(self):

        # create joints
        par = self.moduleGrp
        self.firstPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('firstPrimaryStart', 'firstPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.firstPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.firstPrimaryJnts)


        par = self.moduleGrp
        self.secondPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('secondPrimaryStart', 'secondPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.secondPrimaryJnts.append(jnt)
            par = jnt

        self.orientJnts(self.secondPrimaryJnts)

        par = self.moduleGrp
        self.thirdPrimaryJnts =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('thirdPrimaryStart', 'thirdPrimaryEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.thirdPrimaryJnts.append(jnt)
            par = jnt
        self.orientJnts(self.thirdPrimaryJnts)

        par = self.moduleGrp
        self.firstFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_a_0', 'feather_a_1','feather_a_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.firstFeather.append(jnt)
            par = jnt
        self.orientJnts(self.firstFeather)

        par = self.moduleGrp
        self.secondFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_b_0', 'feather_b_1','feather_b_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.secondFeather.append(jnt)
            par = jnt
        self.orientJnts(self.secondFeather)

        par = self.moduleGrp
        self.thirdFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_c_0', 'feather_c_1','feather_c_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.thirdFeather.append(jnt)
            par = jnt
        self.orientJnts(self.thirdFeather)

        par = self.moduleGrp
        self.forthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_d_0', 'feather_d_1','feather_d_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.forthFeather.append(jnt)
            par = jnt
        self.orientJnts(self.forthFeather)

        par = self.moduleGrp
        self.fifthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_e_0', 'feather_e_1','feather_e_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.fifthFeather.append(jnt)
            par = jnt
        self.orientJnts(self.fifthFeather)

        par = self.moduleGrp
        self.sixFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_f_0', 'feather_f_1','feather_f_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.sixFeather.append(jnt)
            par = jnt
        self.orientJnts(self.sixFeather)

        par = self.moduleGrp
        self.seventhFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_g_0', 'feather_g_1','feather_g_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.seventhFeather.append(jnt)
            par = jnt
        self.orientJnts(self.seventhFeather)

        par = self.moduleGrp
        self.eightthFeather =  []
        for alias, blu in self.blueprints.items():
            if not alias in ('feather_h_0', 'feather_h_1','feather_h_2'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.eightthFeather.append(jnt)
            par = jnt

        self.orientJnts(self.eightthFeather)

        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):

        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        upLoc = mc.createNode('transform')
        mc.xform(upLoc, ws = True, t=(29.424, 8.59, -8.013))
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='z', inverseUpAxes=False)
        mc.delete(upLoc)


    def build(self):
        """
        building necessary nodes
        """
        super(WingTail, self).build()

        self.iconSize = trsLib.getDistance(self.joints['firstPrimaryStart'], self.joints['firstPrimaryEnd'])
        mult = [1, -1][self.side == 'R']


        # create primary controls
        self.PrimaryCtls = {'primaryCtls': []}
        self.firstPrimaryCtl = control.Control(descriptor=self.prefix + '_01_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['firstPrimaryStart'],
                                          matchRotate=self.joints['firstPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.firstPrimaryCtl.name, 'blue')

        mc.parentConstraint(self.firstPrimaryCtl.name,self.joints['firstPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.firstPrimaryCtl.name,self.joints['firstPrimaryStart'], mo =  True)

        self.PrimaryCtls['primaryCtls'].append(self.firstPrimaryCtl.name)
        self.secondPrimaryCtl = control.Control(descriptor=self.prefix + '_02_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['secondPrimaryStart'],
                                          matchRotate=self.joints['secondPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.secondPrimaryCtl.name, 'blue')


        mc.parentConstraint(self.secondPrimaryCtl.name,self.joints['secondPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.secondPrimaryCtl.name,self.joints['secondPrimaryStart'], mo =  True)


        self.PrimaryCtls['primaryCtls'].append(self.secondPrimaryCtl.name)
        self.thirdPrimaryCtl = control.Control(descriptor=self.prefix + '_03_primaryWing',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="cube",
                                          color=control.SECCOLORS[self.side],
                                          scale=[self.iconSize / 8 * mult, self.iconSize / 8, self.iconSize / 8],
                                          matchTranslate=self.joints['thirdPrimaryStart'],
                                          matchRotate=self.joints['thirdPrimaryStart'],
                                          lockHideAttrs=['v', 's', 't'])

        display.setColor(self.thirdPrimaryCtl.name, 'blue')


        mc.parentConstraint(self.thirdPrimaryCtl.name,self.joints['thirdPrimaryStart'], mo =  True)
        mc.scaleConstraint(self.thirdPrimaryCtl.name,self.joints['thirdPrimaryStart'], mo =  True)

        self.PrimaryCtls['primaryCtls'].append(self.thirdPrimaryCtl.name)

        self.setOut('primaryCtls', self.PrimaryCtls)

        self.primaryCtlsGrps  = {'primaryGrps':[]}
        self.primaryCtlsGrps['primaryGrps'].append(self.firstPrimaryCtl.zro)
        self.primaryCtlsGrps['primaryGrps'].append(self.secondPrimaryCtl.zro)
        self.primaryCtlsGrps['primaryGrps'].append(self.thirdPrimaryCtl.zro)

        self.primaryCtlOffsets = []
        for i in self.primaryCtlsGrps['primaryGrps']:
            primaryCtlOffset = mc.createNode('transform' , n  = i + '_offset')
            primaryCtlGrp= mc.createNode('transform' , n  = i + '_GRP')
            trsLib.match(primaryCtlOffset, i )
            trsLib.match(primaryCtlGrp,primaryCtlOffset)
            mc.parent(i,primaryCtlOffset )
            mc.parent(primaryCtlGrp ,self.ctlGrp)
            mc.parent(primaryCtlOffset,primaryCtlGrp )
            self.primaryCtlOffsets.append(primaryCtlOffset)
        for i in self.primaryCtlsGrps['primaryGrps']:
            attrLib.lockHideAttrs(i, ['t' , 's'], lock=True, hide=True)

        # create feather controls
        # first feather control
        featherFirstFKCtls = {'featherFKCtls' : []}
        feathersecondFKCtls = {'featherFKCtls' : []}
        self.firstFeatherFK = fk.Fk(joints=[self.joints['feather_a_0'],self.joints['feather_a_1'],
                      self.joints['feather_a_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.firstFeatherFKList = [x.name for x in self.firstFeatherFK]
        [crvLib.scaleShape(curve=x, scale=(0.3,0.3,0.3)) for x in self.firstFeatherFKList]




        # second feather control
        self.secondFeatherFK = fk.Fk(joints=[self.joints['feather_b_0'],self.joints['feather_b_1'],
                      self.joints['feather_b_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.secondFeatherFKList = [x.name for x in self.secondFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.secondFeatherFKList]


        # third feather control
        self.thirdFeatherFK = fk.Fk(joints=[self.joints['feather_c_0'],self.joints['feather_c_1'],
                      self.joints['feather_c_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.thirdFeatherFKList = [x.name for x in self.thirdFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.thirdFeatherFKList]

        featherforthFKCtls = {'featherFKCtls' : []}
        # forth feather control
        self.forthFeatherFK = fk.Fk(joints=[self.joints['feather_d_0'],self.joints['feather_d_1'],
                      self.joints['feather_d_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.forthFeatherFKList = [x.name for x in self.forthFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.forthFeatherFKList]


        # fifth feather control
        self.fifthFeatherFK = fk.Fk(joints=[self.joints['feather_e_0'],self.joints['feather_e_1'],
                      self.joints['feather_e_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.fifthFeatherFKList = [x.name for x in self.fifthFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.fifthFeatherFKList]

        # sixth feather control
        self.sixthFeatherFK = fk.Fk(joints=[self.joints['feather_f_0'],self.joints['feather_f_1'],
                      self.joints['feather_f_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.sixthFeatherFKList = [x.name for x in self.sixthFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.sixthFeatherFKList]


        # seventh feather control
        self.seventhFeatherFK = fk.Fk(joints=[self.joints['feather_g_0'],self.joints['feather_g_1'],
                      self.joints['feather_g_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.seventhFeatherFKList = [x.name for x in self.seventhFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.seventhFeatherFKList]


        # eights Feather control
        self.eightFeatherFK = fk.Fk(joints=[self.joints['feather_h_0'],self.joints['feather_h_1'],
                      self.joints['feather_h_2']],
                      parent="", shape="cube", scale=None, search='', replace='',
                      hideLastCtl=True, connectGlobalScale=True, movable=True,
                      lockHideAttrs=[], stretch=True, variableIconSize=False)

        self.eightFeatherFKList = [x.name for x in self.eightFeatherFK]
        [crvLib.scaleShape(curve = x, scale = (0.3,0.3,0.3)) for x in self.eightFeatherFKList]

        featherFirstFKCtls['featherFKCtls'].append(self.firstFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.secondFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.thirdFeatherFK[0].name)
        featherFirstFKCtls['featherFKCtls'].append(self.forthFeatherFK[0].name)
        count = 1
        for i in featherFirstFKCtls['featherFKCtls']:
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = count)
            count -= 0.2

        feathersecondFKCtls['featherFKCtls'].append(self.fifthFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.sixthFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.seventhFeatherFK[0].name)
        feathersecondFKCtls['featherFKCtls'].append(self.eightFeatherFK[0].name)

        count = 1
        for i in feathersecondFKCtls['featherFKCtls']:
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = count)
            count -= 0.2


        self.firstPartfeatherCtlsGrps  = {'featherGrps':[]}
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.firstFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.secondFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.thirdFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.forthFeatherFK[0].zro)
        self.firstPartfeatherCtlsGrps['featherGrps'].append(self.fifthFeatherFK[0].zro)

        self.firstFeatherPart = mc.createNode('transform', n = self.side +'_firstFeatherPart', parent = self.firstFeatherFK[0].name)
        mc.parent(self.firstFeatherPart, self.ctlGrp)


        for i in self.firstPartfeatherCtlsGrps['featherGrps']:
            firstFeatherCtlOffset = mc.createNode('transform' , n  = i + '_offset')
            firstFeatherCtlGrp= mc.createNode('transform' , n  = i + '_GRP')
            trsLib.match(firstFeatherCtlOffset, i )
            trsLib.match(firstFeatherCtlGrp,firstFeatherCtlOffset)
            mc.parent(i,firstFeatherCtlOffset )
            mc.parent(firstFeatherCtlOffset,firstFeatherCtlGrp )
            mc.parent(firstFeatherCtlGrp, self.firstFeatherPart)
            attrLib.addFloat(i, 'blend', min = 0, max = 1, dv = 0)



        self.secondPartfeatherCtlsGrps  = {'featherGrps':[]}
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.sixthFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.seventhFeatherFK[0].zro)
        self.secondPartfeatherCtlsGrps['featherGrps'].append(self.eightFeatherFK[0].zro)

        self.secondFeatherPart = mc.createNode('transform', n = self.side + '_secondFeatherPart', parent = self.sixthFeatherFK[0].name)
        mc.parent(self.secondFeatherPart, self.ctlGrp)

        for i in self.secondPartfeatherCtlsGrps['featherGrps']:
            firstFeatherCtlOffset = mc.createNode('transform', n=i + '_offset')
            secondFeatherCtlGrp = mc.createNode('transform', n=i + '_GRP')
            trsLib.match(firstFeatherCtlOffset, i)
            trsLib.match(secondFeatherCtlGrp, firstFeatherCtlOffset)
            mc.parent(i, firstFeatherCtlOffset)
            mc.parent(firstFeatherCtlOffset, secondFeatherCtlGrp)
            mc.parent(secondFeatherCtlGrp, self.secondFeatherPart )
            attrLib.addFloat(i, 'blend', min=0, max=1, dv=0)


        # connect blend attrs to their group blend attrs
        mc.connectAttr(self.firstFeatherFK[0].name + '.blend', self.firstFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.secondFeatherFK[0].name + '.blend', self.secondFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.thirdFeatherFK[0].name + '.blend', self.thirdFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.forthFeatherFK[0].name + '.blend', self.forthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.fifthFeatherFK[0].name + '.blend', self.fifthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.sixthFeatherFK[0].name + '.blend', self.sixthFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.seventhFeatherFK[0].name + '.blend', self.seventhFeatherFK[0].zro + '.blend')
        mc.connectAttr(self.eightFeatherFK[0].name + '.blend', self.eightFeatherFK[0].zro + '.blend')

        # connect first part feathers offset grps
        firstPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_01_PMA')
        mc.connectAttr(self.firstPrimaryCtl.name + '.rotate', firstPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.firstPrimaryCtl.zro + '.rotate', firstPrimaryPlusNode + '.input3D[1]')

        secondPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_02_PMA')
        mc.connectAttr(self.secondPrimaryCtl.zro + '.rotate', secondPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.secondPrimaryCtl.name + '.rotate', secondPrimaryPlusNode + '.input3D[1]')


        featherthirdFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherThird_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherthirdFKBlendNode + '.color1')
        mc.connectAttr(featherthirdFKBlendNode + '.output' , self.thirdFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.thirdFeatherFK[0].zro + '.blend' , featherthirdFKBlendNode + '.blender')


        self.secondPrimaryPlusNodeSwitch = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_switch_02_PMA')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , self.secondPrimaryPlusNodeSwitch + '.input3D[0]')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherthirdFKBlendNode + '.color2')

        featherForthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherForth_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherForthFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherForthFKBlendNode + '.color2')
        mc.connectAttr(featherForthFKBlendNode + '.output' , self.forthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.forthFeatherFK[0].zro + '.blend' , featherForthFKBlendNode + '.blender')

        featherFirstFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherFirst_BCN')
        mc.connectAttr(firstPrimaryPlusNode + '.output3D' , featherFirstFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch + '.output3D' , featherFirstFKBlendNode + '.color2')
        mc.connectAttr(featherFirstFKBlendNode + '.output' , self.firstFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.firstFeatherFK[0].zro + '.blend' , featherFirstFKBlendNode + '.blender')


        # connect second part feathers offset grps
        firstAndSecondPrimaryPlusNode = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_03_PMA')
        mc.connectAttr(self.thirdPrimaryCtl.zro + '.rotate', firstAndSecondPrimaryPlusNode + '.input3D[0]')
        mc.connectAttr(self.thirdPrimaryCtl.name + '.rotate', firstAndSecondPrimaryPlusNode + '.input3D[1]')

        self.thirdPrimaryPlusNodeSwitch = mc.createNode('plusMinusAverage', n  = self.name + '_primaryWing_switch_03_PMA')
        mc.connectAttr(firstAndSecondPrimaryPlusNode + '.output3D' , self.thirdPrimaryPlusNodeSwitch + '.input3D[0]')

        featherSecondFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSecond_BCN')
        mc.connectAttr(firstPrimaryPlusNode  + '.output3D' , featherSecondFKBlendNode + '.color1')
        mc.connectAttr(self.secondPrimaryPlusNodeSwitch  + '.output3D', featherSecondFKBlendNode + '.color2')
        mc.connectAttr(featherSecondFKBlendNode + '.output' , self.secondFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.secondFeatherFK[0].zro + '.blend' , featherSecondFKBlendNode + '.blender')

        featherFifthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherFifth_BCN')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherFifthFKBlendNode + '.color1')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch+ '.output3D', featherFifthFKBlendNode + '.color2')
        mc.connectAttr(featherFifthFKBlendNode + '.output' , self.fifthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.fifthFeatherFK[0].zro + '.blend' , featherFifthFKBlendNode + '.blender')


        featherSixFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSix_BCN')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherSixFKBlendNode + '.color1')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherSixFKBlendNode + '.color2')
        mc.connectAttr(featherSixFKBlendNode + '.output' , self.sixthFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.sixthFeatherFK[0].zro + '.blend' , featherSixFKBlendNode + '.blender')

        featherSeventhFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherSeven_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherSeventhFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherSeventhFKBlendNode + '.color1')
        mc.connectAttr(featherSeventhFKBlendNode + '.output' , self.seventhFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.seventhFeatherFK[0].zro + '.blend' , featherSeventhFKBlendNode + '.blender')

        featherEighthFKBlendNode = mc.createNode('blendColors', n = self.name + '_featherEight_BCN')
        mc.connectAttr(self.thirdPrimaryPlusNodeSwitch + '.output3D' , featherEighthFKBlendNode + '.color2')
        mc.connectAttr(secondPrimaryPlusNode + '.output3D' , featherEighthFKBlendNode + '.color1')
        mc.connectAttr(featherEighthFKBlendNode + '.output' , self.eightFeatherFK[0].zro + '.rotate')
        mc.connectAttr(self.eightFeatherFK[0].zro + '.blend' , featherEighthFKBlendNode + '.blender')


    def connect(self):

        super(WingTail, self).connect()

        ctlParent = self.getOut('ctlParent')
        connect.matrix(ctlParent, self.ctlGrp, world=True)




        #attrLib.addInt(armSettingCtl, 'featherExtraCtls', min = 0, max = 1)


        # if par:
        #     connect.matrix(par, self.ctlGrp, world=True)
        #     connect.matrix(par, self.moduleGrp, world=True)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(WingTail, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v= 'C_tail.lastCtl')







