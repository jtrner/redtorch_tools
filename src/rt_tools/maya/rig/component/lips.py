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

    def __init__(self, side = 'C', prefix = 'lip', numJnts = 6, **kwargs ):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numJnts = numJnts

        self.aliases = {'all': 'all',
                        'leftCorner':'leftCorner',
                        'rightCorner':'rightCorner',
                        'upMid': 'upMid',
                        'upLeft': 'upLeft',
                        'upRight': 'upRight',
                        'buttomMid': 'buttomMid',
                        'buttomRight': 'buttomRight',
                        'buttomLeft': 'buttomLeft'}

        super(Lips, self).__init__(**kwargs)


    def createBlueprint(self):

        super(Lips, self).createBlueprint()

        par = self.blueprintGrp

        # create blueprints
        self.blueprints['all'] = '{}_all_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['all']):
            mc.joint(self.blueprintGrp, name = self.blueprints['all'])
            mc.xform(self.blueprints['all'], ws = True, t = (0, 20, 2))
        par = self.blueprints['all']

        self.blueprints['leftCorner'] = '{}_leftCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['leftCorner']):
            mc.joint(par,name = self.blueprints['leftCorner'])
            mc.xform(self.blueprints['leftCorner'], ws = True, t = (0.7, 20, 2.8))

        self.blueprints['rightCorner'] = '{}_rightCorner_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['rightCorner']):
            mc.joint(par, name=self.blueprints['rightCorner'])
            mc.xform(self.blueprints['rightCorner'], ws=True, t=(-0.7, 20, 2.8))

        self.blueprints['upMid'] = '{}_upMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upMid']):
            mc.joint(par,name = self.blueprints['upMid'])
            mc.xform(self.blueprints['upMid'], ws = True, t = (0, 20.3, 3))

        self.blueprints['upLeft'] = '{}_upLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upLeft']):
            mc.joint(par, name=self.blueprints['upLeft'])
            mc.xform(self.blueprints['upLeft'], ws=True, t=(0.4, 20.2, 2.9))

        self.blueprints['upRight'] = '{}_upRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upRight']):
            mc.joint(par, name=self.blueprints['upRight'])
            mc.xform(self.blueprints['upRight'], ws=True, t=(-0.4, 20.2, 2.9))

        self.blueprints['buttomMid'] = '{}_buttomMid_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomMid']):
            mc.joint(par, name=self.blueprints['buttomMid'])
            mc.xform(self.blueprints['buttomMid'], ws=True, t=(0, 19.7, 3))

        self.blueprints['buttomRight'] = '{}_buttomRight_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomRight']):
            mc.joint(par, name=self.blueprints['buttomRight'])
            mc.xform(self.blueprints['buttomRight'], ws=True, t=(-0.4, 19.8, 2.9))

        self.blueprints['buttomLeft'] = '{}_buttomLeft_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomLeft']):
            mc.joint(par, name=self.blueprints['buttomLeft'])
            mc.xform(self.blueprints['buttomLeft'], ws=True, t=(0.4, 19.8, 2.9))

        attrLib.addString(self.blueprintGrp, ln = 'blu_inputs', v = self.blueprints)

    def createJoints(self):

        par = self.moduleGrp
        self.lipJnts =  []
        for alias, blu in self.blueprints.items():
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.lipJnts.append(jnt)
            par = self.lipJnts[0]

        self.orientJnts(self.joints)

        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):
        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        # orient middle joints
        for i in jnts:
            if i not in ('all', 'upMid', 'buttomMid'):
                continue
            upLoc = mc.createNode('transform')
            trsLib.match(upLoc, jnts[i])
            mc.move(0, 10000000 * mult, 0, upLoc, r=True, ws=True)
            jntLib.orientUsingAim(jnts=jnts[i], upAim=upLoc,
                                  aimAxes='x', upAxes='-y', inverseUpAxes=inverseUpAxes)

            mc.makeIdentity(jnts[i], apply  = True , s = 1, r = 1, t = 1)
            mc.delete(upLoc)

        #orient left joints
        for i in jnts:
            if i not in ('upLeft', 'buttomLeft','leftCorner'):
                continue
            upLoc = mc.createNode('transform')
            upLoc2 = mc.createNode('transform')
            mc.parent(upLoc, upLoc2)
            trsLib.match(upLoc2, jnts[i])
            mc.setAttr(upLoc2 + '.ry', 25)
            mc.setAttr(upLoc + '.tx' , 10)
            mc.parent(upLoc, world = True)

            mc.delete(mc.aimConstraint(upLoc,jnts[i],
                                       aimVector = [1,0,0],
                                       upVector = [0,1,0],
                                       mo = False))

            mc.makeIdentity(jnts[i], apply  = True , s = 1, r = 1, t = 1)
            mc.delete(upLoc2, upLoc)

        # orient right joints
        for i in jnts:
            if i not in ('upRight', 'buttomRight','rightCorner'):
                continue
            upLoc = mc.createNode('transform')
            upLoc2 = mc.createNode('transform')
            mc.parent(upLoc, upLoc2)
            trsLib.match(upLoc2, jnts[i])
            mc.setAttr(upLoc2 + '.ry', -25)
            mc.setAttr(upLoc + '.tx' , -10)
            mc.parent(upLoc, world = True)

            mc.delete(mc.aimConstraint(upLoc,jnts[i],
                                       aimVector = [1,0,0],
                                       upVector = [0,1,0],
                                       mo = False))

            mc.makeIdentity(jnts[i], apply  = True , s = 1, r = 1, t = 1)
            mc.delete(upLoc2, upLoc)

        
    def build(self):
        super(Lips, self).build()

        iconSize = trsLib.getDistance(self.joints['all'], self.joints['upMid'])

        # create controls
        self.ctlZros = {'ctlZros':[]}
        ctls = {'ctls':[]}
        for i, s in enumerate(self.lipJnts):
            ctl = control.Control(descriptor='{}_{}'.format(self.prefix, i + 1),
                                  side=self.side,
                                  color='cyan',
                                  orient=[0, 0, 1],
                                  moveShape=(0, 0, 0.3),
                                  scale=[iconSize * 0.2] * 3,
                                  lockHideAttrs=['s', 'v'],
                                  parent=self.ctlGrp)
            self.ctlZros['ctlZros'].append(ctl.zro)
            ctls['ctls'].append(ctl.name)

        crvLib.moveShape(curve=ctls['ctls'][0], move=(0,0,1))
        crvLib.scaleShape(curve=ctls['ctls'][0], scale=(8,4,1))


        # match the position of controls to the joints
        print(self.lipJnts)
        for i, s in enumerate(self.lipJnts):
            cns = connect.weightConstraint(s,
                                           self.ctlZros['ctlZros'][i],
                                           type='pointConstraint',
                                           weights=[1, 1])
            mc.delete(cns)


        # rename controls
        self.lipCtls = []

        allLipCtl = mc.rename(ctls['ctls'][0], self.name + '_all_CTL')
        display.setColor(allLipCtl, 'yellow')
        leftCornerCtl = mc.rename(ctls['ctls'][1], self.name + '_leftCorner_CTL')
        rightCornerCtl = mc.rename(ctls['ctls'][2], self.name + '_rightCorner_CTL')
        upMidCtl = mc.rename(ctls['ctls'][3], self.name + '_upMid_CTL')
        upLeftCtl = mc.rename(ctls['ctls'][4], self.name + '_upLeft_CTL')
        upRightLipCtl = mc.rename(ctls['ctls'][5], self.name + '_upRight_CTL')
        buttomMidCtl = mc.rename(ctls['ctls'][6], self.name + '_buttomMid_CTL')
        buttomRightCtl = mc.rename(ctls['ctls'][7], self.name + '_buttomRight_CTL')
        buttomLeftCtl = mc.rename(ctls['ctls'][-1], self.name + '_buttomLeft_CTL')


        self.lipCtls.append(allLipCtl)
        self.lipCtls.append(leftCornerCtl)
        self.lipCtls.append(rightCornerCtl)
        self.lipCtls.append(upMidCtl)
        self.lipCtls.append(upLeftCtl)
        self.lipCtls.append(upRightLipCtl)
        self.lipCtls.append(buttomMidCtl)
        self.lipCtls.append(buttomRightCtl)
        self.lipCtls.append(buttomLeftCtl)

        self.setOut('ctls', self.lipCtls)

        # rename control groups
        allLipZRO = mc.rename(self.ctlZros['ctlZros'][0], self.name + '_all_ZRO')
        self.leftCornerZRO = mc.rename(self.ctlZros['ctlZros'][1], self.name + '_leftCorner_ZRO')
        self.rightCornerZRO = mc.rename(self.ctlZros['ctlZros'][2], self.name + '_rightCorner_ZRO')
        upMidZRO = mc.rename(self.ctlZros['ctlZros'][3], self.name + '_upMid_ZRO')
        upLeftZRO = mc.rename(self.ctlZros['ctlZros'][4], self.name + '_upLeft_ZRO')
        upRightZRO = mc.rename(self.ctlZros['ctlZros'][5], self.name + '_upRight_ZRO')
        buttomMidZRO = mc.rename(self.ctlZros['ctlZros'][6], self.name + '_buttomMid_ZRO')
        buttomRightZRO= mc.rename(self.ctlZros['ctlZros'][7], self.name + '_buttomRight_ZRO')
        buttomLeftZRO = mc.rename(self.ctlZros['ctlZros'][-1], self.name + '_buttomLeft_ZRO')

        # create transform for corner controls
        leftCornerGRP = mc.createNode('transform', name = self.name + '_leftCorner_GRP', parent = self.name + '_leftCorner_ZRO')
        mc.parent(leftCornerGRP, world = True)
        mc.parent(self.name + '_leftCorner_ZRO',leftCornerGRP)

        rightCornerGRP = mc.createNode('transform', name = self.name + '_rightCorner_GRP', parent = self.name + '_rightCorner_ZRO')
        mc.parent(rightCornerGRP, world = True)
        mc.parent(self.name + '_rightCorner_ZRO',rightCornerGRP)

        # rotate side controls
        mc.setAttr(upLeftZRO + '.ry',25)
        mc.setAttr(buttomLeftZRO  + '.ry',25)
        mc.setAttr(buttomRightZRO + '.ry',-25)
        mc.setAttr(upRightZRO + '.ry',-25)
        mc.setAttr(rightCornerGRP + '.ry',-25)
        mc.setAttr(leftCornerGRP + '.ry',25)

        # inverse scale for right controls for mirror behaviour
        mc.setAttr(upRightZRO + '.sx', -1)
        mc.setAttr(buttomRightZRO + '.sx', -1)
        mc.setAttr(rightCornerGRP + '.sx', -1)

        # connect controls to the joints
        connect.weightConstraint(allLipCtl,self.lipJnts[0] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(leftCornerCtl,self.lipJnts[1] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(rightCornerCtl,self.lipJnts[2] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(upMidCtl,self.lipJnts[3] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(upLeftCtl,self.lipJnts[4] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(upRightLipCtl,self.lipJnts[5],type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(buttomMidCtl,self.lipJnts[6] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(buttomRightCtl,self.lipJnts[7] ,type='parentConstraint', weights=[1, 1])
        connect.weightConstraint(buttomLeftCtl,self.lipJnts[-1] ,type='parentConstraint', weights=[1, 1])

        # create group for controls
        self.upperLipCtlsGrp = mc.createNode('transform', name = self.name + '_upCtls_ZRO',parent = self.blueprints['all'])
        mc.parent(self.upperLipCtlsGrp,self.ctlGrp)
        mc.parent(upLeftZRO,upRightZRO,upMidZRO,self.upperLipCtlsGrp)

        self.lowerLipCtlsGrp = mc.createNode('transform', name = self.name + '_lowCtls_ZRO',parent = self.blueprints['all'])
        mc.parent(self.lowerLipCtlsGrp,self.ctlGrp)
        mc.parent(buttomLeftZRO,buttomRightZRO,buttomMidZRO,self.lowerLipCtlsGrp)

        self.midLipCtlsGrp = mc.createNode('transform', name = self.name + '_midCtls_ZRO',parent = self.blueprints['all'])
        mc.parent(self.midLipCtlsGrp,self.ctlGrp)
        mc.parent(rightCornerGRP,leftCornerGRP,self.midLipCtlsGrp)

        # parent lip controls under mouth global control
        mc.parent(self.upperLipCtlsGrp,self.lowerLipCtlsGrp,self.midLipCtlsGrp, allLipCtl)

    def connect(self):

        super(Lips, self).connect()

        par = self.getOut('ctlParent')
        print par
        if par:
            [mc.connectAttr(par + '.{0}{1}'.format(c, v),self.lowerLipCtlsGrp + '.{0}{1}'.format(c, v)) for c in 'trs' for v in 'xyz']

        globPar = self.getOut('globalScale')
        if globPar:
            [mc.connectAttr(globPar + '.{0}{1}'.format(c, v),self.upperLipCtlsGrp + '.{0}{1}'.format(c, v)) for c in 'trs' for v in 'xyz']

        leftCon = mc.parentConstraint(par, globPar, self.leftCornerZRO, mo = True)[0]
        mc.setAttr(leftCon + '.' + par + 'W0', 1)
        mc.setAttr(leftCon +  '.' + globPar + 'W1', 5)

        rightCon = mc.parentConstraint(par, globPar, self.rightCornerZRO, mo = True)[0]
        mc.setAttr(rightCon + '.' + par + 'W0', 1)
        mc.setAttr(rightCon +  '.' + globPar + 'W1', 5)




    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Lips, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_neck.headCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v=self.side + '_jaw.ctl')
