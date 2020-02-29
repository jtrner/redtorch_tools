"""
name: legQuad.py

Author: Ehsan Hassani Moghaddam

History:
    05/30/16 (ehassani)    first release!


"""
import maya.api.OpenMaya as om2
import maya.cmds as mc

from ...lib import jntLib
from ...lib import trsLib
from ...lib import connect
from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import space
from ...lib import display
from ..command import fk
from ..command import ikLegQuad
from ..command import ikStretch
from ..command import twist
from . import template

reload(jntLib)
reload(trsLib)
reload(connect)
reload(control)
reload(strLib)
reload(attrLib)
reload(space)
reload(display)
reload(fk)
reload(ikLegQuad)
reload(ikStretch)
reload(twist)
reload(template)


class LegQuad(template.Template):
    """
    class for creating spine rig for biped characters
    """

    def __init__(self, side="L", prefix="legQuad", mode='fkik',
                 isFront=True, useRibbon=False, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.mode = mode  # rig ik and fk
        self.useRibbon = useRibbon
        self.isFront = isFront
        self.aliases = {'hip': 'hip',
                        'knee': 'knee',
                        'foot': 'foot',
                        'ball': 'ball',
                        'ballEnd': 'ballEnd',
                        'heel': 'heel',
                        'footInside': 'footInside',
                        'footOutside': 'footOutside',
                        'leg': 'leg',
                        'parent': 'C_spine.hipCtl'}
        if isFront:
            self.aliases = {'hip': 'shoulder',
                            'scap': 'scapula',
                            'knee': 'elbow',
                            'foot': 'hand',
                            'ball': 'meta',
                            'ballEnd': 'metaEnd',
                            'heel': 'palm',
                            'footInside': 'handInside',
                            'footOutside': 'handOutside',
                            'leg': 'arm',
                            'parent': 'C_spine.chestCtl'}
        self.scapJnt = None
        self.scapEndJnt = None
        self.scapStartGrp = None

        super(LegQuad, self).__init__(**kwargs)

    def createBlueprint(self):
        super(LegQuad, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        par = self.blueprintGrp
        if self.isFront:
            self.blueprints['scap'] = '{}_{}_BLU'.format(self.name, self.aliases['scap'])
            if not mc.objExists(self.blueprints['scap']):
                mc.joint(self.blueprintGrp, name=self.blueprints['scap'])
                mc.xform(self.blueprints['scap'], ws=True, t=(2 * mult, 11, 4))
            par = self.blueprints['scap']

        self.blueprints['hip'] = '{}_{}_BLU'.format(self.name, self.aliases['hip'])
        if not mc.objExists(self.blueprints['hip']):
            mc.joint(par, name=self.blueprints['hip'])
            t = (2 * mult, 9, 5) if self.isFront else (2 * mult, 9, -5)
            mc.xform(self.blueprints['hip'], ws=True, t=t)

        self.blueprints['knee'] = '{}_{}_BLU'.format(self.name, self.aliases['knee'])
        if not mc.objExists(self.blueprints['knee']):
            mc.joint(self.blueprints['hip'], name=self.blueprints['knee'])
            t = (2 * mult, 7, 4) if self.isFront else (2 * mult, 6, -4)
            mc.xform(self.blueprints['knee'], ws=True, t=t)

        self.blueprints['foot'] = '{}_{}_BLU'.format(self.name, self.aliases['foot'])
        if not mc.objExists(self.blueprints['foot']):
            mc.joint(self.blueprints['knee'], name=self.blueprints['foot'])
            t = (2 * mult, 3.5, 4) if self.isFront else (2 * mult, 3, -6)
            mc.xform(self.blueprints['foot'], ws=True, t=t)

        self.blueprints['ball'] = '{}_{}_BLU'.format(self.name, self.aliases['ball'])
        if not mc.objExists(self.blueprints['ball']):
            mc.joint(self.blueprints['foot'], name=self.blueprints['ball'])
            t = (2 * mult, 1.3, 4) if self.isFront else (2 * mult, 1.3, -5)
            mc.xform(self.blueprints['ball'], ws=True, t=t)

        self.blueprints['ballEnd'] = '{}_{}_BLU'.format(self.name, self.aliases['ballEnd'])
        if not mc.objExists(self.blueprints['ballEnd']):
            mc.joint(self.blueprints['ball'], name=self.blueprints['ballEnd'])
            t = (2 * mult, 0.5, 4.5) if self.isFront else (2 * mult, 0.5, -4.5)
            mc.xform(self.blueprints['ballEnd'], ws=True, t=t)

        self.blueprints['tip'] = '{}_tip_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['tip']):
            mc.joint(self.blueprints['ballEnd'], name=self.blueprints['tip'])
            t = (2 * mult, 0, 5) if self.isFront else (2 * mult, 0, -4)
            mc.xform(self.blueprints['tip'], ws=True, t=t)
            display.setColor(self.blueprints['tip'], 'pink')

        self.blueprints['heel'] = '{}_{}_BLU'.format(self.name, self.aliases['heel'])
        if not mc.objExists(self.blueprints['heel']):
            mc.joint(self.blueprints['ballEnd'], name=self.blueprints['heel'])
            t = (2 * mult, 0, 4) if self.isFront else (2 * mult, 0, -5)
            mc.xform(self.blueprints['heel'], ws=True, t=t)
            display.setColor(self.blueprints['heel'], 'pink')

        self.blueprints['footInside'] = '{}_{}_BLU'.format(self.name, self.aliases['footInside'])
        if not mc.objExists(self.blueprints['footInside']):
            mc.joint(self.blueprints['ballEnd'], name=self.blueprints['footInside'])
            t = (1.5 * mult, 0, 4.5) if self.isFront else (1.5 * mult, 0, -4.5)
            mc.xform(self.blueprints['footInside'], ws=True, t=t)
            display.setColor(self.blueprints['footInside'], 'pink')

        self.blueprints['footOutside'] = '{}_{}_BLU'.format(self.name, self.aliases['footOutside'])
        if not mc.objExists(self.blueprints['footOutside']):
            mc.joint(self.blueprints['ballEnd'], name=self.blueprints['footOutside'])
            t = (2.5 * mult, 0, 4.5) if self.isFront else (2.5 * mult, 0, -4.5)
            mc.xform(self.blueprints['footOutside'], ws=True, t=t)
            display.setColor(self.blueprints['footOutside'], 'pink')

        self.orientJnts(self.blueprints)

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        # create joints
        par = self.moduleGrp
        for alias, blu in self.blueprints.items():
            if alias in ('heel', 'footInside', 'footOutside'):
                continue
            jnt = blu.replace('BLU', 'JNT')
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

        self.orientJnts(self.joints)

        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):
        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        # orient scapula
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts.values()[0])
        mc.move(100000 * mult, 0, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts.values(), upAim=upLoc,
                              aimAxes='x', upAxes='-z', inverseUpAxes=inverseUpAxes)
        mc.delete(upLoc)

        # orient hip, knee, ankle, ball and ballEnd
        mainChain = jnts.values()[:4]
        if self.isFront:
            mainChain = jnts.values()[1:5]

        # is knee pointing forward or backward?
        v1 = om2.MVector(mc.xform(mainChain[0], q=1, ws=1, t=1))
        v2 = om2.MVector(mc.xform(mainChain[1], q=1, ws=1, t=1))
        v3 = om2.MVector(mc.xform(mainChain[2], q=1, ws=1, t=1))
        pv_vec = ((v1 + v3) / 2) - v2
        dot = pv_vec * om2.MVector(0, 0, 1)
        if dot > 0:
            upAxes = '-y'
        else:
            upAxes = 'y'

        # orient main joints, eg: hip, knee, ankle
        jntLib.orientLimb(mainChain, aimAxes='x', upAxes=upAxes, inverseUpAxes=inverseUpAxes)

        # reset foot pivot joints' orientation
        for alias in ('tip', 'heel', 'footInside', 'footOutside'):
            if alias in jnts:
                jntLib.setOrientToWorld(jnts[alias])


    def build(self):
        """
        building necessary nodes
        """
        super(LegQuad, self).build()

        # setting ctl
        mult = [1, -1][self.side == 'R']
        self.size = trsLib.getDistance(self.joints['hip'], self.joints['ballEnd'])
        settingCtl = control.Control(descriptor=self.prefix + '_setting',
                                     side=self.side,
                                     parent=self.ctlGrp,
                                     shape="foot",
                                     color=control.SECCOLORS[self.side],
                                     scale=[self.size / 10 * mult, self.size / 10, self.size / 10],
                                     moveShape=[mult * self.size / 4, 0, 0],
                                     lockHideAttrs=['t', 'r', 's', 'v'],
                                     matchTranslate=self.joints['foot'])
        mc.parentConstraint(self.joints['ballEnd'], settingCtl.zro, mo=True)
        self.settingCtl = settingCtl.name

        # ==========================================================
        # scapula
        # ==========================================================
        if self.isFront:
            self.rig_scap()

        # ==========================================================
        # fk mode
        # ==========================================================       
        if self.mode == 'fk':
            self.rig_fk()

        # ==========================================================
        # ik mode
        # ==========================================================
        elif self.mode == 'ik':
            self.rig_ik()

        # ==========================================================
        # fkik modes
        # ==========================================================
        elif self.mode == 'fkik':
            # run both modes
            self.rig_ik()
            self.rig_fk()

            # blend between ik and fk
            attrLib.addFloat(self.settingCtl, ln="fk_ik", min=0, max=1, dv=1)

            blendJnts = [self.joints['hip'], self.joints['knee'],
                         self.joints['foot'], self.joints['ball'],
                         self.joints['ballEnd'], self.joints['tip']]
            jntLib.blend_fk_ik(self.fkJntList, self.ikJntList,
                               blendJnts, self.settingCtl + ".fk_ik")

            # connect visibility settings
            attrLib.addEnum(self.settingCtl, ln="fk_vis", en=['off', 'on'],
                            dv=0, k=False)
            attrLib.addEnum(self.settingCtl, ln="ik_vis", en=['off', 'on'],
                            dv=1, k=False)

            fkZero = self.fkCtlList[0].replace('CTL', 'ZRO')
            mc.connectAttr(self.settingCtl + ".fk_vis", fkZero + '.v')

            ikFootZero = self.footIkCtl.replace('CTL', 'ZRO')
            mc.connectAttr(self.settingCtl + ".ik_vis", ikFootZero + '.v')

            ikKneeZero = self.kneeIkCtl.replace('CTL', 'ZRO')
            mc.connectAttr(self.settingCtl + ".ik_vis", ikKneeZero + '.v')

        # hip bendy/twist joints
        hipTwstCtlGrp, hipTwstModuleGrp = twist.run(
            start=self.joints['hip'],
            end=self.joints['knee'],
            nb=3,
            name='{}_{}'.format(self.name, self.aliases['hip']),
            reverse=True,
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(hipTwstCtlGrp, self.ctlGrp)
        mc.parent(hipTwstModuleGrp, self.moduleGrp)

        # knee bendy/twist joints
        kneeTwstCtlGrp, kneeTwstModuleGrp = twist.run(
            start=self.joints['knee'],
            end=self.joints['foot'],
            nb=3,
            name='{}_{}'.format(self.name, self.aliases['knee']),
            reverse=False,
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(kneeTwstCtlGrp, self.ctlGrp)
        mc.parent(kneeTwstModuleGrp, self.moduleGrp)

        # ankle bendy/twist joints
        ankleTwstCtlGrp, ankleTwstModuleGrp = twist.run(
            start=self.joints['foot'],
            end=self.joints['ball'],
            nb=3,
            name='{}_{}'.format(self.name, self.aliases['foot']),
            reverse=False,
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(ankleTwstCtlGrp, self.ctlGrp)
        mc.parent(ankleTwstModuleGrp, self.moduleGrp)

        # twist visibility settings
        if self.useRibbon:
            attrLib.addEnum(self.settingCtl, ln="twist_vis", en=['off', 'on'],
                            dv=0, k=False)
            mc.connectAttr(self.settingCtl + ".twist_vis", hipTwstCtlGrp + '.v')
            mc.connectAttr(self.settingCtl + ".twist_vis", kneeTwstCtlGrp + '.v')
            mc.connectAttr(self.settingCtl + ".twist_vis", ankleTwstCtlGrp + '.v')

        # auto scap
        if self.isFront:
            scapZro = self.scapCtl.replace('CTL', 'ZRO')

            scapOrigPose = mc.createNode(
                'transform', n=self.name + '_scap_orig_pose_LOC', p=self.ctlGrp)
            aimToscapOrigPose = mc.createNode(
                'transform', n=self.name + '_aim_to_scap_orig_pose_LOC', p=self.ctlGrp)
            autoscapSrt = mc.createNode(
                'transform', n=self.name + '_auto_scap_LOC', p=aimToscapOrigPose)

            mc.pointConstraint(self.footIkCtl, aimToscapOrigPose)
            mc.aimConstraint(scapOrigPose, aimToscapOrigPose, aim=(0, 1, 0),
                             u=(1, 0, 0), wut="none")

            trsLib.match(scapOrigPose, scapZro)
            trsLib.match(autoscapSrt, scapZro)

            connect.blendConstraint(
                scapOrigPose, autoscapSrt, scapZro, blendNode=self.scapCtl,
                blendAttr='autoTranslate', type='pointConstraint')
            connect.blendConstraint(
                scapOrigPose, autoscapSrt, scapZro, blendNode=self.scapCtl,
                blendAttr='autoRotate', type='orientConstraint')

            mc.setAttr(self.scapCtl + '.autoTranslate', 0.1)
            mc.setAttr(self.scapCtl + '.autoRotate', 0.5)

    def rig_scap(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # ik rig joints
        scapulaJnts = jntLib.extract_from_to(
            self.joints['scap'],
            self.joints['hip'],
            search="_JNT",
            replace="_ik_TRS")
        self.scapJnt = scapulaJnts[0]
        self.scapEndJnt = mc.rename(scapulaJnts[1], self.name + '_scap_ik_end_TRS')

        # set outputs
        self.setOut('scapJnt', self.scapJnt)
        self.setOut('scapEndJnt', self.scapEndJnt)

        # add controls
        mult = [1, -1][self.side == 'R']
        self.scapCtl = control.Control(
            descriptor=self.prefix + "_scapula",
            side=self.side,
            parent=self.ctlGrp,
            shape="cube",
            scale=(self.size * 0.2, self.size * 0.2, self.size * 0.2),
            orient=[0, mult, 0],
            matchTranslate=self.scapJnt,
            matchScale=self.scapJnt,
            verbose=self.verbose).name

        # clean up outliner
        connect.multiConstraint(self.scapCtl, self.scapJnt, t=1, r=1, s=1, mo=True)

        # set outputs
        self.setOut('scapCtl', self.scapCtl)

        # connect rig to skeleton
        connect.direct(self.scapJnt, self.joints['scap'])

    def rig_ik(self):

        # read attrs from asset node
        self.getAttrsFromBlueprint()

        if self.isFront:
            self.scapStartGrp = mc.createNode('transform',
                                              n=self.name + '_scap_start_GRP',
                                              p=self.ctlGrp)
            trsLib.match(self.scapStartGrp, self.joints['scap'])

        self.legStartGrp = mc.createNode('transform',
                                         n=self.name + '_start_GRP',
                                         p=self.ctlGrp)
        trsLib.match(self.legStartGrp, self.joints['hip'])

        # ik rig joints
        self.ikJntList = jntLib.extract_from_to(self.joints['hip'],
                                                self.joints['tip'],
                                                search="_JNT",
                                                replace="_ik_TRS")
        if self.isFront:
            mc.parent(self.ikJntList[0], self.scapJnt)
        self.setOut('ikJntList', str(self.ikJntList))

        gs = attrLib.addFloat(self.moduleGrp, 'globalScale', dv=1)
        self.ikCtlList, ikHandleList, self.spring_jntsAndIk, ballAndToeIK = ikLegQuad.IkLegQuad(
            joints=self.ikJntList,
            ctlGrp=self.ctlGrp,
            moduleGrp=self.moduleGrp,
            side=self.side,
            prefix=self.prefix,
            isFront=self.isFront,
            globalScaleAttr=gs,
            scapJnt=self.scapJnt,
            scapEndJnt=self.scapEndJnt or self.legStartGrp,
            verbose=self.verbose)

        self.footIkCtl = self.ikCtlList[0].name
        self.kneeIkCtl = self.ikCtlList[1].name
        self.heelIkCtl = self.ikCtlList[2].name
        self.legIkh = ikHandleList[0]
        footIkh = ikHandleList[1]

        # set output
        self.setOut('footIkCtl', self.footIkCtl)
        self.setOut('kneeIkCtl', self.kneeIkCtl)
        self.setOut('legIkh', self.legIkh)
        self.setOut('footIkh', footIkh)

        # # outliner clean up
        # mc.parent(trsLib.getParent(self.legIkh), self.moduleGrp)
        # mc.parent(trsLib.getParent(footIkh), self.moduleGrp)
        # mc.parent(trsLib.getParent(self.spring_jntsAndIk), self.moduleGrp)
        # print ballAndToeIK, self.moduleGrp
        # mc.parent(ballAndToeIK, self.moduleGrp)

    def rig_fk(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # fk rig joints
        self.fkJntList = jntLib.extract_from_to(self.joints['hip'],
                                                self.joints['tip'],
                                                search="_JNT", replace="_fk_TRS")
        if self.isFront:
            mc.parent(self.fkJntList[0], self.scapJnt)
        self.setOut('fkJntList', str(self.fkJntList))

        # add controls
        self.fkCtlList = fk.Fk(joints=self.fkJntList,
                               parent=self.ctlGrp,
                               shape="circle")
        self.fkCtlList = [x.name for x in self.fkCtlList]
        self.setOut('fkCtlList', str(self.fkCtlList))

    def connect(self):
        """
        connection of created nodes
        """
        # make sure things we create go to self.blueprintGrp
        super(LegQuad, self).connect()

        # fk point space
        fkZero = self.fkCtlList[0].replace('CTL', 'ZRO')

        ikPar = self.scapEndJnt or self.legStartGrp
        mc.pointConstraint(ikPar, fkZero)
        mc.pointConstraint(ikPar, self.ikJntList[0])

        # fk orient space
        orientDrivers = self.getOut('fkOrient')
        space.orient(drivers=orientDrivers,
                     drivens=[fkZero],
                     control=self.settingCtl,
                     name=self.name + 'OrientSpace')

        # foot space
        orientDrivers = self.getOut('footSpace')
        ikHandZero = self.footIkCtl.replace('CTL', 'ZRO')
        space.parent(drivers=orientDrivers,
                     drivens=[ikHandZero],
                     control=self.footIkCtl,
                     name=self.name + 'Space')

        # knee space
        kneeDrivers = self.getOut('kneeSpace')
        ikKneeZero = self.kneeIkCtl.replace('CTL', 'ZRO')
        space.parent(drivers=kneeDrivers,
                     drivens=[ikKneeZero],
                     control=self.kneeIkCtl,
                     name=self.name + 'Space')

        # attach controls
        jntParent = self.getOut('jntParent')
        connect.matrix(jntParent, self.moduleGrp)
        connect.matrix(jntParent, self.ctlGrp)

        gs = self.getOut('globalScale')
        fkZro = self.fkCtlList[0].replace('CTL', 'ZRO')
        mc.connectAttr(gs + '.scaleY', fkZro + '.globalScale')

        # make ik stretchy
        ikStretch.run(startCtl=ikPar,
                      pvCtl=self.kneeIkCtl,
                      ctl=self.footIkCtl,
                      ikh=self.legIkh,
                      globalScaleAttr=gs + '.scaleY',
                      name=self.name,
                      stretchMode='translate')
        ikStretch.run(startCtl=ikPar,
                      pvCtl=self.kneeIkCtl,
                      ctl=self.footIkCtl,
                      ikh=self.spring_jntsAndIk[1],
                      globalScaleAttr=gs + '.scaleY',
                      name=self.name,
                      stretchMode='translate')

        mc.setAttr(self.footIkCtl + '.stretch', 0)
        attrLib.lockHideAttrs(self.footIkCtl, attrs=['lockPV'])

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(LegQuad, self).createSettings()

        parent = self.aliases['parent'].replace('[side]', self.side)

        attrLib.addEnum(self.blueprintGrp, 'blu_mode', en=['fk', 'ik', 'fkik'], dv=2)
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_jntParent', v=parent)
        attrLib.addBool(self.blueprintGrp, 'blu_isFront', v=self.isFront)

        attrLib.addString(self.blueprintGrp, 'blu_fkOrient',
                          v={'drivers': [parent,
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 2})

        attrLib.addString(self.blueprintGrp, 'blu_footSpace',
                          v={'drivers': ['C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 1})

        attrLib.addString(self.blueprintGrp, 'blu_kneeSpace',
                          v={'drivers': [parent,
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
