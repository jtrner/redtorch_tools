import maya.cmds as mc

from . import template
from ...lib import strLib
from ...lib import attrLib
from ...lib import trsLib
from ...lib import jntLib
from ...lib import control
from ...lib import connect
from ...lib import crvLib
from ...lib import display

reload(display)
reload(crvLib)
reload(connect)
reload(control)
reload(jntLib)
reload(trsLib)
reload(attrLib)
reload(template)
reload(template)


class Lips(template.Template):

    def __init__(self, side='C', prefix='lip', numJnts=6, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numJnts = numJnts

        self.aliases = {'allStart': 'allStart',
                        'all': 'all',
                        'sourceLeftCorner': 'sourceLeftCorner',
                        'sourceLeftCornerEnd':'sourceLeftCornerEnd',
                        'startLeftCorner': 'startLeftCorner',
                        'leftCorner': 'leftCorner',
                        'sourceRightCorner': 'sourceRightCorner',
                        'sourceRightCornerEnd': 'sourceRightCornerEnd',
                        'startRightCorner': 'startRightCorner',
                        'rightCorner': 'rightCorner',
                        'startUpMid': 'startUpMid',
                        'upMid': 'upMid',
                        'startUpLeft': 'startUpLeft',
                        'upLeft': 'upLeft',
                        'startUpRight': 'startUpRight',
                        'upRight': 'upRight',
                        'startButtomMid': 'startButtomMid',
                        'buttomMid': 'buttomMid',
                        'startButtomRight': 'startButtomRight',
                        'buttomRight': 'buttomRight',
                        'startButtomLeft': 'startButtomLeft',
                        'buttomLeft': 'buttomLeft'}

        super(Lips, self).__init__(**kwargs)

    def createBlueprint(self):

        super(Lips, self).createBlueprint()

        par = self.blueprintGrp

        # create blueprints
        self.blueprints['allStart'] = '{}_allStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['allStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['allStart'])
            mc.xform(self.blueprints['allStart'], ws=True, t=(0, 20, 2))
        par = self.blueprints['allStart']

        self.blueprints['all'] = '{}_all_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['all']):
            mc.joint(self.blueprints['allStart'], name=self.blueprints['all'])
            mc.xform(self.blueprints['all'], ws=True, t=(0, 20, 4))

        self.blueprints['sourceLeftCorner'] = '{}_sourceLeftCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['sourceLeftCorner']):
            mc.joint(par, name=self.blueprints['sourceLeftCorner'])
            mc.xform(self.blueprints['sourceLeftCorner'], ws=True, t=(0.7, 20, 2))

        self.blueprints['sourceLeftCornerEnd'] = '{}_sourceLeftCornerEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['sourceLeftCornerEnd']):
            mc.joint(self.blueprints['sourceLeftCorner'], name=self.blueprints['sourceLeftCornerEnd'])
            mc.xform(self.blueprints['sourceLeftCornerEnd'], ws=True, t=(0.7, 20, 2.8))

        self.blueprints['startLeftCorner'] = '{}_startLeftCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startLeftCorner']):
            mc.joint(self.blueprints['sourceLeftCorner'], name=self.blueprints['startLeftCorner'])
            mc.xform(self.blueprints['startLeftCorner'], ws=True, t=(0.7, 20, 2))

        self.blueprints['leftCorner'] = '{}_leftCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftCorner']):
            mc.joint(self.blueprints['startLeftCorner'], name=self.blueprints['leftCorner'])
            mc.xform(self.blueprints['leftCorner'], ws=True, t=(0.7, 20, 2.8))


        self.blueprints['sourceRightCorner'] = '{}_sourceRightCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['sourceRightCorner']):
            mc.joint(par, name=self.blueprints['sourceRightCorner'])
            mc.xform(self.blueprints['sourceRightCorner'], ws=True, t=(-0.7, 20, 2))

        self.blueprints['sourceRightCornerEnd'] = '{}_sourceRightCornerEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['sourceRightCornerEnd']):
            mc.joint(self.blueprints['sourceRightCorner'], name=self.blueprints['sourceRightCornerEnd'])
            mc.xform(self.blueprints['sourceRightCornerEnd'], ws=True, t=(-0.7, 20, 2.8))

        self.blueprints['startRightCorner'] = '{}_startRightCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startRightCorner']):
            mc.joint(self.blueprints['sourceRightCorner'], name=self.blueprints['startRightCorner'])
            mc.xform(self.blueprints['startRightCorner'], ws=True, t=(-0.7, 20, 2))

        self.blueprints['rightCorner'] = '{}_rightCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightCorner']):
            mc.joint(self.blueprints['startRightCorner'], name=self.blueprints['rightCorner'])
            mc.xform(self.blueprints['rightCorner'], ws=True, t=(-0.7, 20, 2.8))

        self.blueprints['startUpMid'] = '{}_startUpMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startUpMid']):
            mc.joint(par, name=self.blueprints['startUpMid'])
            mc.xform(self.blueprints['startUpMid'], ws=True, t=(0, 20, 2))

        self.blueprints['upMid'] = '{}_upMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upMid']):
            mc.joint(self.blueprints['startUpMid'], name=self.blueprints['upMid'])
            mc.xform(self.blueprints['upMid'], ws=True, t=(0, 20.3, 3))

        self.blueprints['startUpLeft'] = '{}_startUpLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startUpLeft']):
            mc.joint(par, name=self.blueprints['startUpLeft'])
            mc.xform(self.blueprints['startUpLeft'], ws=True, t=(0.4, 20, 2))

        self.blueprints['upLeft'] = '{}_upLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upLeft']):
            mc.joint(self.blueprints['startUpLeft'], name=self.blueprints['upLeft'])
            mc.xform(self.blueprints['upLeft'], ws=True, t=(0.4, 20.2, 2.9))

        self.blueprints['startUpRight'] = '{}_startUpRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startUpRight']):
            mc.joint(par, name=self.blueprints['startUpRight'])
            mc.xform(self.blueprints['startUpRight'], ws=True, t=(-0.4, 20, 2))

        self.blueprints['upRight'] = '{}_upRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upRight']):
            mc.joint(self.blueprints['startUpRight'], name=self.blueprints['upRight'])
            mc.xform(self.blueprints['upRight'], ws=True, t=(-0.4, 20.2, 2.9))

        self.blueprints['startButtomMid'] = '{}_startButtomMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startButtomMid']):
            mc.joint(par, name=self.blueprints['startButtomMid'])
            mc.xform(self.blueprints['startButtomMid'], ws=True, t=(0, 20, 2))

        self.blueprints['buttomMid'] = '{}_buttomMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomMid']):
            mc.joint(self.blueprints['startButtomMid'], name=self.blueprints['buttomMid'])
            mc.xform(self.blueprints['buttomMid'], ws=True, t=(0, 19.7, 3))

        self.blueprints['startButtomRight'] = '{}_startButtomRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startButtomRight']):
            mc.joint(par, name=self.blueprints['startButtomRight'])
            mc.xform(self.blueprints['startButtomRight'], ws=True, t=(-0.4, 20, 2))

        self.blueprints['buttomRight'] = '{}_buttomRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomRight']):
            mc.joint(self.blueprints['startButtomRight'], name=self.blueprints['buttomRight'])
            mc.xform(self.blueprints['buttomRight'], ws=True, t=(-0.4, 19.8, 2.9))

        self.blueprints['startButtomLeft'] = '{}_startButtomLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startButtomLeft']):
            mc.joint(par, name=self.blueprints['startButtomLeft'])
            mc.xform(self.blueprints['startButtomLeft'], ws=True, t=(0.4, 20, 2))

        self.blueprints['buttomLeft'] = '{}_buttomLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomLeft']):
            mc.joint(self.blueprints['startButtomLeft'], name=self.blueprints['buttomLeft'])
            mc.xform(self.blueprints['buttomLeft'], ws=True, t=(0.4, 19.8, 2.9))

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)

    def createJoints(self):

        self.endJnts = []
        self.startJnts = []
        par = self.moduleGrp
        self.mouthAll = []
        for alias, blu in self.blueprints.items():
            if not alias in ('allStart', 'all'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.mouthAll.append(jnt)
            par = self.mouthAll[0]

        self.endJnts.append(self.mouthAll[0])
        self.startJnts.append(self.mouthAll[0])

        self.orientJnts(self.mouthAll)
        mc.delete(self.mouthAll[-1])

        par = self.mouthAll[0]
        self.lipJnts = []
        self.leftCornerSourceJnt = []
        for alias, blu in self.blueprints.items():
            if not alias in ('sourceLeftCorner', 'sourceLeftCornerEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            self.leftCornerSourceJnt.append(jnt)
            par = self.lipJnts[0]

        self.orientJnts(self.lipJnts)
        mc.delete(self.leftCornerSourceJnt[-1])

        par = self.leftCornerSourceJnt[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startLeftCorner', 'leftCorner'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        self.rightCornerSourceJnt = []
        for alias, blu in self.blueprints.items():
            if not alias in ('sourceRightCorner', 'sourceRightCornerEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            self.rightCornerSourceJnt.append(jnt)
            par = self.lipJnts[0]

        self.orientJnts(self.lipJnts)
        mc.delete(self.rightCornerSourceJnt[-1])

        par = self.rightCornerSourceJnt[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startRightCorner', 'rightCorner'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startButtomLeft', 'buttomLeft'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startButtomRight', 'buttomRight'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startUpRight', 'upRight'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startUpLeft', 'upLeft'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startButtomMid', 'buttomMid'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)

        par = self.mouthAll[0]
        self.lipJnts = []
        for alias, blu in self.blueprints.items():
            if not alias in ('startUpMid', 'upMid'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.endJnts.append(self.lipJnts[-1])
        self.startJnts.append(self.lipJnts[0])
        self.orientJnts(self.lipJnts)
        print(self.endJnts)

        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):
        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        # orient middle joints
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 10000000 * mult, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='-x', upAxes='-y', inverseUpAxes=inverseUpAxes)

        mc.makeIdentity(jnts, apply=True, s=1, r=1, t=1)
        mc.delete(upLoc)

    def build(self):
        super(Lips, self).build()

        iconSize = trsLib.getDistance(self.joints['allStart'], self.joints['upMid'])

        # create controls
        self.ctlZros = {'ctlZros': []}
        ctls = {'ctls': []}
        for i, s in enumerate(self.startJnts):
            ctl = control.Control(descriptor='{}_{}'.format(self.prefix, i + 1),
                                  side=self.side,
                                  color='cyan',
                                  orient=[0, 0, 1],
                                  moveShape=(0, 0, 0.3),
                                  scale=[iconSize * 0.2] * 3,
                                  lockHideAttrs=['s', 'v', 'r'],
                                  parent=self.ctlGrp)
            self.ctlZros['ctlZros'].append(ctl.zro)
            ctls['ctls'].append(ctl.name)

        crvLib.moveShape(curve=ctls['ctls'][0], move=(0, 0, 1))
        crvLib.scaleShape(curve=ctls['ctls'][0], scale=(8, 4, 1))

        self.downCtl = control.Control(descriptor='{}_{}'.format(self.prefix, '_downCtl'),
                                       side=self.side,
                                       shape = 'sphere',
                                       color='yellow',
                                       orient=[0, 0, 1],
                                       moveShape=(0, 0, 0.3),
                                       scale=[iconSize * 0.2] * 3,
                                       lockHideAttrs=['s', 'v', 'r'],
                                       parent=self.ctlGrp)

        crvLib.moveShape(curve=self.downCtl.name, move=(0, -0.8, 1.6))
        crvLib.scaleShape(curve=self.downCtl.name, scale=(0.7, 0.7, 0.7))

        cns = connect.weightConstraint(self.mouthAll[0],
                                       self.downCtl.zro,
                                       type='pointConstraint',
                                       weights=[1, 1])
        mc.delete(cns)

        self.upCtl = control.Control(descriptor='{}_{}'.format(self.prefix, '_upCtl'),
                                       side=self.side,
                                       shape = 'sphere',
                                       color='yellow',
                                       orient=[0, 0, 1],
                                       moveShape=(0, 0, 0.3),
                                       scale=[iconSize * 0.2] * 3,
                                       lockHideAttrs=['s', 'v', 'r'],
                                       parent=self.ctlGrp)

        crvLib.moveShape(curve=self.upCtl.name, move=(0, 0.8, 1.6))
        crvLib.scaleShape(curve=self.upCtl.name, scale=(0.7, 0.7, 0.7))

        cns = connect.weightConstraint(self.mouthAll[0],
                                       self.upCtl.zro,
                                       type='pointConstraint',
                                       weights=[1, 1])
        mc.delete(cns)

        # match the position of controls to the joints
        for i, s in enumerate(self.endJnts):
            cns = connect.weightConstraint(s,
                                           self.ctlZros['ctlZros'][i],
                                           type='pointConstraint',
                                           weights=[1, 1])
            mc.delete(cns)

        # rename controls
        self.lipCtls = []

        self.up_lip_ctl = mc.rename(self.upCtl.name, self.name + '_up_CTL')
        self.down_lip_ctl = mc.rename(self.downCtl.name, self.name + '_down_CTL')
        self.all_lip_ctl = mc.rename(ctls['ctls'][0], self.name + '_all_CTL')
        display.setColor(self.all_lip_ctl, 'yellow')
        leftCornerCtl = mc.rename(ctls['ctls'][1], self.name + '_leftCorner_CTL')
        rightCornerCtl = mc.rename(ctls['ctls'][2], self.name + '_rightCorner_CTL')
        upMidCtl = mc.rename(ctls['ctls'][3], self.name + '_buttomLeft_CTL')
        self.upLeftCtl = mc.rename(ctls['ctls'][4], self.name + '_buttomRight_CTL')
        self.upRightLipCtl = mc.rename(ctls['ctls'][5], self.name + '_upRight_CTL')
        buttomMidCtl = mc.rename(ctls['ctls'][6], self.name + '_upLeft_CTL')
        self.buttomRightCtl = mc.rename(ctls['ctls'][7], self.name + '_buttomMid_CTL')
        self.buttomLeftCtl = mc.rename(ctls['ctls'][-1], self.name + '_upMid_CTL')

        mc.parent(self.downCtl.zro, self.all_lip_ctl)
        mc.parent(self.upCtl.zro, self.all_lip_ctl)

        self.lipCtls.append(self.all_lip_ctl)
        self.lipCtls.append(leftCornerCtl)
        self.lipCtls.append(rightCornerCtl)
        self.lipCtls.append(upMidCtl)
        self.lipCtls.append(self.upLeftCtl)
        self.lipCtls.append(self.upRightLipCtl)
        self.lipCtls.append(buttomMidCtl)
        self.lipCtls.append(self.buttomRightCtl)
        self.lipCtls.append(self.buttomLeftCtl)

        self.setOut('ctls', self.lipCtls)

        # rename control groups
        allLipZRO = mc.rename(self.ctlZros['ctlZros'][0], self.name + '_all_ZRO')
        self.leftCornerZRO = mc.rename(self.ctlZros['ctlZros'][1], self.name + '_leftCorner_ZRO')
        self.rightCornerZRO = mc.rename(self.ctlZros['ctlZros'][2], self.name + '_rightCorner_ZRO')
        buttomLeftZRO = mc.rename(self.ctlZros['ctlZros'][3], self.name + '_buttomLeft_ZRO')
        buttomRightZRO = mc.rename(self.ctlZros['ctlZros'][4], self.name + '_buttomRight_ZRO')
        upRightZRO = mc.rename(self.ctlZros['ctlZros'][5], self.name + '_upRight_ZRO')
        upLeftZRO = mc.rename(self.ctlZros['ctlZros'][6], self.name + '_upLeft_ZRO')
        buttomMidZRO = mc.rename(self.ctlZros['ctlZros'][7], self.name + '_buttomMid_ZRO')
        upMidZRO = mc.rename(self.ctlZros['ctlZros'][-1], self.name + '_upMid_ZRO')

        # create transform for corner controls

        self.leftCornerGRP = mc.createNode('transform', name=self.name + '_leftCorner_GRP',
                                           parent=self.name + '_leftCorner_ZRO')
        mc.parent(self.leftCornerGRP, world=True)
        mc.parent(self.name + '_leftCorner_ZRO', self.leftCornerGRP)

        self.rightCornerGRP = mc.createNode('transform', name=self.name + '_rightCorner_GRP',
                                            parent=self.name + '_rightCorner_ZRO')
        mc.parent(self.rightCornerGRP, world=True)
        mc.parent(self.name + '_rightCorner_ZRO', self.rightCornerGRP)

        # inverse scale for right controls for mirror behaviour
        mc.setAttr(upRightZRO + '.sx', -1)
        mc.setAttr(buttomRightZRO + '.sx', -1)
        mc.setAttr(self.rightCornerGRP + '.sx', -1)

        # connect controls to the joints
        connect.remapVal(self.lipCtls[0]  + '.ty', self.startJnts[0] + '.rz', inputMin=-1, inputMax=1,
                         outputMin=-100, outputMax=100, name=self.name +'_all_upDown')

        connect.remapVal(self.lipCtls[0]  + '.tx', self.startJnts[0] + '.ry', inputMin=-0.5, inputMax=0.5,
                         outputMin=-50, outputMax=50, name=self.name +'_all_side')
        # down_upDown

        # down_leftRight



        # upMid
        self.upSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_upSwitchMid_PMA')
        mc.connectAttr(self.lipCtls[-1] + '.ty', self.upSwitchMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl+ '.ty', self.upSwitchMidPls + '.input3D[0].input3Dx')

        self.upMidClamp = mc.createNode('clamp', name=self.name + '_upMid_CLM')
        mc.setAttr(self.upMidClamp + '.maxR', 100)

        connect.remapVal(self.upSwitchMidPls  + '.output3Dx', self.upMidClamp + '.inputR', inputMin=-1, inputMax=1,
                         outputMin=-100, outputMax=100, name=self.name +'_upSwitchMid_upDown')

        self.upMidPls = mc.createNode('plusMinusAverage', name=self.name + '_upMid_PMA')
        mc.setAttr(self.upMidPls + '.input3D[0].input3Dx', 0)


        mc.connectAttr(self.startJnts[-2] + '.rz', self.upMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.upMidPls + '.output3Dx', self.upMidClamp + '.minR')
        mc.connectAttr(self.upMidClamp + '.outputR', self.startJnts[-1] + '.rz')

        # upLeft
        self.upLeftSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_upLeftSwitch_PMA')
        mc.connectAttr(self.lipCtls[6] + '.ty', self.upLeftSwitchMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl+ '.ty', self.upLeftSwitchMidPls + '.input3D[0].input3Dx')

        self.upLeftClamp = mc.createNode('clamp', name=self.name + '_upLeft_CLM')
        mc.setAttr(self.upLeftClamp + '.maxR', 100)

        connect.remapVal(self.upLeftSwitchMidPls  + '.output3Dx', self.upLeftClamp + '.inputR', inputMin=-1, inputMax=1,
                         outputMin=-100, outputMax=100, name=self.name +'_upLeftSwitch_upDown')

        self.upLeftPls = mc.createNode('plusMinusAverage', name=self.name + '_upLeft_PMA')
        mc.setAttr(self.upLeftPls + '.input3D[0].input3Dx', 0)


        mc.connectAttr(self.startJnts[3] + '.rz', self.upLeftPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.upLeftPls + '.output3Dx', self.upLeftClamp + '.minR')
        mc.connectAttr(self.upLeftClamp + '.outputR', self.startJnts[-3] + '.rz')

        # upRight
        self.upRightSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_upRightSwitch_PMA')
        mc.connectAttr(self.lipCtls[5] + '.ty', self.upRightSwitchMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl+ '.ty', self.upRightSwitchMidPls + '.input3D[0].input3Dx')

        self.upRightClamp = mc.createNode('clamp', name=self.name + '_upRight_CLM')
        mc.setAttr(self.upRightClamp + '.maxR', 100)

        connect.remapVal(self.upRightSwitchMidPls  + '.output3Dx', self.upRightClamp + '.inputR', inputMin=-1, inputMax=1,
                         outputMin=-100, outputMax=100, name=self.name +'_upRightSwitch_upDown')

        self.upRightPls = mc.createNode('plusMinusAverage', name=self.name + '_upRight_PMA')
        mc.setAttr(self.upRightPls + '.input3D[0].input3Dx', 0)


        mc.connectAttr(self.startJnts[4] + '.rz', self.upRightPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.upRightPls + '.output3Dx', self.upRightClamp + '.minR')
        mc.connectAttr(self.upRightClamp + '.outputR', self.startJnts[-4] + '.rz')

        # upSides
        self.leftRightUpSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_leftRightUpSwitchMid_PMA')
        mc.connectAttr(self.lipCtls[-1] + '.tx', self.leftRightUpSwitchMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl+ '.tx', self.leftRightUpSwitchMidPls + '.input3D[0].input3Dx')

        connect.remapVal(self.leftRightUpSwitchMidPls  + '.output3Dx', self.startJnts[-1] + '.ry', inputMin=-0.5, inputMax=0.5,
                         outputMin=-50, outputMax=50, name=self.name +'_leftRightSwitchMid')

        self.leftSideUpSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_leftSideUpSwitchMid_PMA')
        mc.connectAttr(self.lipCtls[6] + '.tx', self.leftSideUpSwitchMidPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl+ '.tx', self.leftSideUpSwitchMidPls + '.input3D[0].input3Dx')

        connect.remapVal(self.leftSideUpSwitchMidPls  + '.output3Dx', self.startJnts[-3] + '.ry', inputMin=-0.5, inputMax=0.5,
                         outputMin=-50, outputMax=50, name=self.name +'_leftSideSwitchMid')

        self.sideUpRightSwitchPls = mc.createNode('plusMinusAverage', name=self.name + '_sideUpRightSwitch_PMA')
        self.sideUpRightMult = mc.createNode('multiplyDivide', name = self.name + '_sideUpRight_MDN')
        mc.connectAttr(self.lipCtls[5] + '.tx', self.sideUpRightMult + '.input1X')
        mc.setAttr(self.sideUpRightMult + '.input2X', -1)
        mc.connectAttr(self.sideUpRightMult + '.outputX', self.sideUpRightSwitchPls + '.input3D[1].input3Dx')
        mc.connectAttr(self.up_lip_ctl + '.tx', self.sideUpRightSwitchPls + '.input3D[0].input3Dx')

        connect.remapVal(self.sideUpRightSwitchPls  + '.output3Dx', self.startJnts[-4] + '.ry', inputMin=0.5, inputMax=-0.5,
                         outputMin=50, outputMax=-50, name=self.name +'_sideRightSwitch')


        # upDownCorners
        for i,j in zip(self.lipCtls, self.startJnts):
            if not i in ['C_lip_rightCorner_CTL', 'C_lip_leftCorner_CTL']:
                continue
            connect.remapVal(i + '.ty', j  + '.rz', inputMin=-1, inputMax=1,
                             outputMin=-100, outputMax=100, name=i + '_upDown')
        # side corners
        for i,j in zip(self.lipCtls, self.startJnts):
            if not i in ['C_lip_leftCorner_CTL']:
                continue
            connect.remapVal(i + '.tx', j  + '.ry', inputMin=-0.5, inputMax=0.5,
                             outputMin=-50, outputMax=50, name=i + '_upDown')

        for i,j in zip(self.lipCtls, self.startJnts):
            if not i in ['C_lip_rightCorner_CTL']:
                continue
            connect.remapVal(i + '.tx', j  + '.ry', inputMin=-0.5, inputMax=0.5,
                             outputMin=50, outputMax=-50, name=i + '_upDown')

        # connect leftCorner ctls to the source joint
        self.leftBlend = mc.createNode('blendColors', name = self.name + '_leftCorner_BCN')
        mc.connectAttr(self.startJnts[-3] + '.rz' , self.leftBlend + '.color1G')
        mc.connectAttr(self.startJnts[3] + '.rz' , self.leftBlend + '.color2G')
        mc.connectAttr(self.leftBlend + '.outputG', self.leftCornerSourceJnt[0] + '.rz')

        mc.connectAttr(self.startJnts[-3]  + '.ry', self.leftBlend + '.color1R')
        mc.connectAttr(self.startJnts[3]+ '.ry', self.leftBlend + '.color2R')
        mc.connectAttr(self.leftBlend + '.outputR', self.leftCornerSourceJnt[0] + '.ry')

        # connect side controls to the corner left
        mc.pointConstraint(self.lipCtls[6], self.lipCtls[3],self.leftCornerGRP ,mo = True)

        # connect side controls to the corner right
        mc.pointConstraint(self.lipCtls[5], self.lipCtls[4],self.rightCornerGRP ,mo = True)


        # connect rightCorner ctls to the source joint
        self.rightBlend = mc.createNode('blendColors', name = self.name + '_rightCorner_BCN')
        mc.connectAttr(self.startJnts[-4] + '.rz', self.rightBlend + '.color1G')
        mc.connectAttr(self.startJnts[4] + '.rz', self.rightBlend + '.color2G')
        mc.connectAttr(self.rightBlend + '.outputG', self.rightCornerSourceJnt[0] + '.rz')

        mc.connectAttr(self.startJnts[-4] + '.ry', self.rightBlend + '.color1R')
        mc.connectAttr(self.startJnts[4] + '.ry', self.rightBlend + '.color2R')
        mc.connectAttr(self.rightBlend + '.outputR', self.rightCornerSourceJnt[0] + '.ry')


        # create group for controls
        self.upperLipCtlsGrp = mc.createNode('transform', name=self.name + '_upCtls_ZRO', parent=self.name + '_all_CTL')
        mc.parent(self.upperLipCtlsGrp, world=True)
        mc.parent(self.upperLipCtlsGrp, self.ctlGrp)
        mc.makeIdentity(self.upperLipCtlsGrp, apply=True, r=True, t=True, s=True)
        mc.parent(upLeftZRO, upRightZRO, upMidZRO, self.upperLipCtlsGrp)

        self.lowerLipCtlsGrp = mc.createNode('transform', name=self.name + '_lowCtls_ZRO',
                                             parent=self.name + '_all_CTL')
        mc.parent(self.lowerLipCtlsGrp, world=True)
        mc.parent(self.lowerLipCtlsGrp, self.ctlGrp)
        mc.makeIdentity(self.lowerLipCtlsGrp, apply=True, r=True, t=True, s=True)
        mc.parent(buttomLeftZRO, buttomRightZRO, buttomMidZRO, self.lowerLipCtlsGrp)

        self.midLipCtlsGrp = mc.createNode('transform', name=self.name + '_midCtls_ZRO', parent=self.name + '_all_CTL')
        mc.parent(self.midLipCtlsGrp, world=True)
        mc.parent(self.midLipCtlsGrp, self.ctlGrp)
        mc.makeIdentity(self.midLipCtlsGrp, apply=True, r=True, t=True, s=True)
        mc.parent(self.rightCornerGRP, self.leftCornerGRP, self.midLipCtlsGrp)

        # parent lip controls under mouth global control
        mc.parent(self.upperLipCtlsGrp, self.midLipCtlsGrp, self.all_lip_ctl)
        mc.parent(self.lowerLipCtlsGrp, self.down_lip_ctl)
        mc.parent(self.upperLipCtlsGrp, self.up_lip_ctl)


    def connect(self):

        super(Lips, self).connect()

        par = self.getOut('ctlParent')
        if par:
            [mc.connectAttr(par + '.' + '{}{}'.format(i, s), self.downCtl.zro + '.' + '{}{}'.format(i, s)) for i in 'rt' for s in 'xyz']

            self.downSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_downSwitchMid_PMA')
            mc.connectAttr(self.lipCtls[7] + '.ty', self.downSwitchMidPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl+ '.ty', self.downSwitchMidPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.ty', self.downSwitchMidPls + '.input3D[3].input3Dx')
            self.jawMidDownMul = mc.createNode('multiplyDivide', name = self.name + '_jawDownSwitchMid_MDN')
            mc.setAttr(self.jawMidDownMul + '.input2X', -0.03)
            mc.connectAttr(par + '.rx', self.jawMidDownMul+ '.input1X')
            mc.connectAttr(self.jawMidDownMul + '.outputX', self.downSwitchMidPls + '.input3D[2].input3Dx')
            connect.remapVal(self.downSwitchMidPls  + '.output3Dx', self.startJnts[-2] + '.rz', inputMin=-1, inputMax=1,
                             outputMin=-100, outputMax=100, name=self.name +'_downSwitchMid_upDown')

            self.downLeftSwitchPls = mc.createNode('plusMinusAverage', name=self.name + '_downLeftSwitch_PMA')
            mc.connectAttr(self.lipCtls[3] + '.ty', self.downLeftSwitchPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl+ '.ty', self.downLeftSwitchPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.ty', self.downLeftSwitchPls + '.input3D[3].input3Dx')
            self.jawLeftSideMul = mc.createNode('multiplyDivide', name = self.name + '_jawLeftSideSwitchMid_MDN')
            mc.setAttr(self.jawLeftSideMul + '.input2X', -0.03)
            mc.connectAttr(par + '.rx', self.jawLeftSideMul+ '.input1X')
            mc.connectAttr(self.jawLeftSideMul + '.outputX', self.downLeftSwitchPls + '.input3D[2].input3Dx')
            connect.remapVal(self.downLeftSwitchPls  + '.output3Dx', self.startJnts[3] + '.rz', inputMin=-1, inputMax=1,
                             outputMin=-100, outputMax=100, name=self.name +'_downLeftSwitch_upDown')


            self.downRightSwitchPls = mc.createNode('plusMinusAverage', name=self.name + '_downRightSwitch_PMA')
            mc.connectAttr(self.lipCtls[4] + '.ty', self.downRightSwitchPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl+ '.ty', self.downRightSwitchPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.ty', self.downRightSwitchPls + '.input3D[3].input3Dx')
            self.jawRightSideMul = mc.createNode('multiplyDivide', name = self.name + '_jawRightSideSwitchMid_MDN')
            mc.setAttr(self.jawRightSideMul + '.input2X', -0.03)
            mc.connectAttr(par + '.rx', self.jawRightSideMul+ '.input1X')
            mc.connectAttr(self.jawRightSideMul + '.outputX', self.downRightSwitchPls + '.input3D[2].input3Dx')
            connect.remapVal(self.downRightSwitchPls  + '.output3Dx', self.startJnts[4] + '.rz', inputMin=-1, inputMax=1,
                             outputMin=-100, outputMax=100, name=self.name +'_downRightSwitch_upDown')

            #down side
            self.leftRightSwitchMidPls = mc.createNode('plusMinusAverage', name=self.name + '_leftRightSwitchMid_PMA')
            mc.connectAttr(self.lipCtls[7] + '.tx', self.leftRightSwitchMidPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl + '.tx', self.leftRightSwitchMidPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.tx', self.leftRightSwitchMidPls + '.input3D[3].input3Dx')
            self.jawdownMidSideMul = mc.createNode('multiplyDivide', name = self.name + '_jawDownMidSideSwitchMid_MDN')
            mc.setAttr(self.jawdownMidSideMul + '.input2X', 0.03)
            mc.connectAttr(par + '.ry', self.jawdownMidSideMul+ '.input1X')
            mc.connectAttr(self.jawdownMidSideMul + '.outputX', self.leftRightSwitchMidPls + '.input3D[2].input3Dx')
            connect.remapVal(self.leftRightSwitchMidPls + '.output3Dx', self.startJnts[-2] + '.ry', inputMin=-0.5,
                             inputMax=0.5,
                             outputMin=-50, outputMax=50, name=self.name + '_leftRightSwitchMid')

            self.sideLeftSwitchPls = mc.createNode('plusMinusAverage', name=self.name + '_sideLeftSwitch_PMA')
            mc.connectAttr(self.lipCtls[3] + '.tx', self.sideLeftSwitchPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl + '.tx', self.sideLeftSwitchPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.tx', self.sideLeftSwitchPls + '.input3D[3].input3Dx')
            self.jawdownLeftSideMul = mc.createNode('multiplyDivide', name = self.name + '_jawDownLeftSideSwitchMid_MDN')
            mc.setAttr(self.jawdownLeftSideMul + '.input2X', 0.03)
            mc.connectAttr(par + '.ry', self.jawdownLeftSideMul+ '.input1X')
            mc.connectAttr(self.jawdownLeftSideMul + '.outputX', self.sideLeftSwitchPls + '.input3D[2].input3Dx')
            connect.remapVal(self.sideLeftSwitchPls + '.output3Dx', self.startJnts[3] + '.ry', inputMin=-0.5,
                             inputMax=0.5,
                             outputMin=-50, outputMax=50, name=self.name + '_sideLeftSwitch')

            self.sideRightSwitchPls = mc.createNode('plusMinusAverage', name=self.name + '_sideRightSwitch_PMA')
            self.sideRightMult = mc.createNode('multiplyDivide', name=self.name + '_sideRight_MDN')
            mc.connectAttr(self.lipCtls[4] + '.tx', self.sideRightMult + '.input1X')
            mc.setAttr(self.sideRightMult + '.input2X', -1)
            mc.connectAttr(self.sideRightMult + '.outputX', self.sideRightSwitchPls + '.input3D[1].input3Dx')
            mc.connectAttr(self.down_lip_ctl + '.tx', self.sideRightSwitchPls + '.input3D[0].input3Dx')
            mc.connectAttr(par + '.tx', self.sideRightSwitchPls + '.input3D[3].input3Dx')
            self.jawdownRightSideMul = mc.createNode('multiplyDivide', name = self.name + '_jawDownRightSideSwitchMid_MDN')
            mc.setAttr(self.jawdownRightSideMul + '.input2X', 0.03)
            mc.connectAttr(par + '.ry', self.jawdownRightSideMul+ '.input1X')
            mc.connectAttr(self.jawdownRightSideMul + '.outputX', self.sideRightSwitchPls + '.input3D[2].input3Dx')
            connect.remapVal(self.sideRightSwitchPls + '.output3Dx', self.startJnts[4] + '.ry', inputMin=0.5,
                             inputMax=-0.5,
                             outputMin=50, outputMax=-50, name=self.name + '_sideRightSwitch')

        globPar = self.getOut('globalScale')
        if globPar:
            connect.matrix(globPar, self.moduleGrp)
            connect.matrix(globPar, self.ctlGrp)


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Lips, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_neck.headCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v=self.side + '_jaw.ctl')
