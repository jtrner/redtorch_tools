"""
name: leg.py

Author: Ehsan Hassani Moghaddam

History:
    05/30/16 (ehassani)    first release!


"""
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
from ..command import ikLeg
from ..command import ikStretch
from ..command import twist
from ..command import pv
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
reload(ikLeg)
reload(ikStretch)
reload(twist)
reload(pv)
reload(template)


class Leg(template.Template):
    """
    class for creating spine rig for biped characters
    """

    def __init__(self, side="L", prefix="leg", mode='fkik', useRibbon=False, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.regBuildShapeList = []
        self.mode = mode
        self.useRibbon = useRibbon

        super(Leg, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Leg, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        self.blueprints['hip'] = '{}_hip_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['hip']):
            mc.joint(self.blueprintGrp, name=self.blueprints['hip'])
            mc.xform(self.blueprints['hip'], ws=True, t=(2 * mult, 9, 0))

        self.blueprints['knee'] = '{}_knee_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['knee']):
            mc.joint(self.blueprints['hip'], name=self.blueprints['knee'])
            mc.xform(self.blueprints['knee'], ws=True, t=(2 * mult, 5, 0.2))

        self.blueprints['foot'] = '{}_foot_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['foot']):
            mc.joint(self.blueprints['knee'], name=self.blueprints['foot'])
            mc.xform(self.blueprints['foot'], ws=True, t=(2 * mult, 1, 0))

        self.blueprints['ball'] = '{}_ball_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['ball']):
            mc.joint(self.blueprints['foot'], name=self.blueprints['ball'])
            mc.xform(self.blueprints['ball'], ws=True, t=(2 * mult, 0.3, 1))

        self.blueprints['ballEnd'] = '{}_ballEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['ballEnd']):
            mc.joint(self.blueprints['ball'], name=self.blueprints['ballEnd'])
            mc.xform(self.blueprints['ballEnd'], ws=True, t=(2 * mult, 0.3, 2))

        self.blueprints['heel'] = '{}_heel_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['heel']):
            mc.joint(self.blueprints['foot'], name=self.blueprints['heel'])
            mc.xform(self.blueprints['heel'], ws=True, t=(2 * mult, 0, -0.5))
            display.setColor(self.blueprints['heel'], 'pink')

        self.blueprints['footInside'] = '{}_footInside_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['footInside']):
            mc.joint(self.blueprints['ball'], name=self.blueprints['footInside'])
            mc.xform(self.blueprints['footInside'], ws=True, t=(1.5 * mult, 0, 1))
            display.setColor(self.blueprints['footInside'], 'pink')

        self.blueprints['footOutside'] = '{}_footOutside_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['footOutside']):
            mc.joint(self.blueprints['ball'], name=self.blueprints['footOutside'])
            mc.xform(self.blueprints['footOutside'], ws=True, t=(2.5 * mult, 0, 1))
            display.setColor(self.blueprints['footOutside'], 'pink')

        self.orientJnts(self.blueprints)

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

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

        # orient hip and knee
        jntLib.orientLimb(jnts=jnts.values(), aimAxes='x',
                          upAxes='y', inverseUpAxes=inverseUpAxes)

        # orient foot
        upLoc = mc.createNode('transform', p=jnts['knee'])
        trsLib.match(upLoc, jnts['foot'])
        mc.move(0, mult, 0, upLoc, r=True, ls=True)
        jntLib.orientUsingAim(jnts=jnts.values()[2:5], upAim=upLoc,
                              aimAxes='x', upAxes='y', inverseUpAxes=inverseUpAxes)

    def build(self):
        """
        building necessary nodes
        """
        super(Leg, self).build()

        # setting ctl
        size = trsLib.getDistance(self.joints['hip'], self.joints['ballEnd'])
        mult = [1, -1][self.side == 'R']
        self.settingCtl = control.Control(descriptor=self.prefix + 'Setting',
                                          side=self.side,
                                          parent=self.ctlGrp,
                                          shape="foot",
                                          scale=[size / 10, size / 10, size / 10],
                                          orient=[mult, 0, 0],
                                          moveShape=[0, 0, -mult * size / 4],
                                          rotateShape=[0, 0, 90],
                                          lockHideAttrs=['t', 'r', 's', 'v'],
                                          matchTranslate=self.joints['foot'],
                                          matchRotate=self.joints['hip'])
        mc.parentConstraint(self.joints['foot'], self.settingCtl.zro, mo=True)
        self.settingCtl = self.settingCtl.name

        # ==========================================================
        # fk mode
        # ==========================================================
        if self.mode == 'fk':  # fk mode
            self.rig_fk()

        # ==========================================================
        # ik mode
        # ==========================================================
        elif self.mode == 'ik':  # ik mode
            self.rig_ik()

        # ==========================================================
        # fkik modes
        # ==========================================================
        elif self.mode == 'fkik':  # fkik mode
            # run both modes
            self.rig_ik()
            self.rig_fk()

            # blend between ik and fk
            attrLib.addFloat(self.settingCtl, ln="fk_ik", min=0, max=1, dv=1)
            jntLib.blend_fk_ik(self.fkJntList,
                               self.ikJntList,
                               self.joints.values(),
                               self.settingCtl + ".fk_ik")

            # connect visibility settings
            attrLib.addEnum(self.settingCtl, ln="fk_vis", en=['off', 'on'], dv=0, k=False)
            attrLib.addEnum(self.settingCtl, ln="ik_vis", en=['off', 'on'], dv=1, k=False)

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
            name=self.name + '_hip',
            reverse=True,
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(hipTwstCtlGrp, self.ctlGrp)
        mc.parent(hipTwstModuleGrp, self.moduleGrp)

        # knee bendy/twist joints
        twstCtlGrp, twstModuleGrp = twist.run(
            start=self.joints['knee'],
            end=self.joints['foot'],
            nb=3,
            name=self.name + '_knee',
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(twstCtlGrp, self.ctlGrp)
        mc.parent(twstModuleGrp, self.moduleGrp)

        # twist visibility settings
        if self.useRibbon:
            attrLib.addEnum(self.settingCtl, ln="twist_vis", en=['off', 'on'], dv=0, k=False)
            mc.connectAttr(self.settingCtl + ".twist_vis", hipTwstCtlGrp + '.v')
            mc.connectAttr(self.settingCtl + ".twist_vis", twstCtlGrp + '.v')

    def rig_ik(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # find poleVec position
        legJnts = self.joints['hip'], self.joints['knee'], self.joints['foot']
        self.poleVec = pv.Pv(jnts=legJnts, distance=1.0, createLoc=True)[0]
        self.setOut('poleVec', self.poleVec)

        # ik rig joints
        self.ikJntList = jntLib.extract_from_to(
            self.joints['hip'],
            self.joints['ballEnd'],
            search="_JNT",
            replace="_ik_JNT")
        self.setOut('ikJntList', str(self.ikJntList))

        self.ikCtlList, ikHandleList = ikLeg.IkLeg(joints=self.ikJntList,
                                                   parent=self.ctlGrp,
                                                   side=self.side,
                                                   prefix=self.prefix,
                                                   poleVec=self.poleVec,
                                                   heelPos=self.blueprints['heel'],
                                                   verbose=self.verbose)
        self.footIkCtl = self.ikCtlList[0].name
        self.kneeIkCtl = self.ikCtlList[1].name
        self.legIkh = ikHandleList[0]

        # set output
        self.setOut('footIkCtl', self.footIkCtl)
        self.setOut('kneeIkCtl', self.kneeIkCtl)
        self.setOut('legIkh', self.legIkh)

        # outliner clean up
        mc.parent(trsLib.getParent(self.legIkh), self.moduleGrp)
        mc.delete(self.poleVec)

    def rig_fk(self):
        # fk rig joints
        self.fkJntList = jntLib.extract_from_to(self.joints['hip'], self.joints['ballEnd'],
                                                search="_JNT", replace="Fk_JNT")
        self.setOut('fkJntList', self.fkJntList)

        # add controls
        self.fkCtlList = fk.Fk(joints=self.fkJntList,
                               parent=self.ctlGrp,
                               shape="circle"
                               )
        self.fkCtlList = [x.name for x in self.fkCtlList]
        self.setOut('fkCtlList', self.fkCtlList)

    def connect(self):
        """
        connection of created nodes
        """
        # make sure things we create go to self.blueprintGrp
        super(Leg, self).connect()

        # fk point space
        pointDrivers = self.getOut('fkPoint')
        if self.mode == 'fk' or self.mode == 'fkik':  # fk or fkik modes
            fkZero = self.fkCtlList[0].replace('CTL', 'ZRO')
            space.point(
                drivers=pointDrivers,
                drivens=[fkZero],
                control=self.settingCtl,
                name=self.name + 'PointSpace')
        if self.mode == 'ik' or self.mode == 'fkik':  # ik or fkik modes
            space.point(
                drivers=pointDrivers,
                drivens=[self.ikJntList[0]],
                control=self.settingCtl,
                name=self.name + 'PointSpace')

        # fk orient space
        orientDrivers = self.getOut('fkOrient')
        if self.mode == 'fk' or self.mode == 'fkik':  # fk or fkik modes
            space.orient(
                drivers=orientDrivers,
                drivens=[fkZero],
                control=self.settingCtl,
                name=self.name + 'OrientSpace')

        # foot space
        orientDrivers = self.getOut('footSpace')
        if self.mode == 'ik' or self.mode == 'fkik':  # ik or fkik modes
            ikHandZero = self.footIkCtl.replace('CTL', 'ZRO')
            space.parent(
                drivers=orientDrivers,
                drivens=[ikHandZero],
                control=self.footIkCtl,
                name=self.name + 'Space')

        # knee space
        kneeDrivers = self.getOut('kneeSpace')
        if self.mode == 'ik' or self.mode == 'fkik':  # ik or fkik modes
            ikKneeZero = self.kneeIkCtl.replace('CTL', 'ZRO')
            space.parent(
                drivers=kneeDrivers,
                drivens=[ikKneeZero],
                control=self.kneeIkCtl,
                name=self.name + 'Space')

        # attach controls
        jntParent = self.getOut('jntParent')
        connect.matrix(jntParent, self.moduleGrp)
        connect.matrix(jntParent, self.ctlGrp)
        gs = self.getOut('globalScale')

        if self.mode == 'fk' or self.mode == 'fkik':  # fk or fkik modes
            fkZro = self.fkCtlList[0].replace('CTL', 'ZRO')
            mc.connectAttr(gs + '.scaleY', fkZro + '.globalScale')

        # make ik stretchy
        legStartGrp = mc.createNode('transform', n=self.name + '_start_GRP', p=self.ctlGrp)
        trsLib.match(legStartGrp, self.joints['hip'])
        if self.mode == 'ik' or self.mode == 'fkik':  # ik or fkik modes
            ikStretch.run(startCtl=legStartGrp,
                          pvCtl=self.kneeIkCtl,
                          ctl=self.footIkCtl,
                          ikh=self.legIkh,
                          globalScaleAttr=gs + '.scaleY',
                          name=self.name)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Leg, self).createSettings()

        attrLib.addEnum(self.blueprintGrp, 'blu_mode', en=['fk', 'ik', 'fkik'], dv=2)
        attrLib.addString(self.blueprintGrp, 'blu_fkPoint', v='C_spine.hipCtl')
        attrLib.addString(self.blueprintGrp, 'blu_fkOrient',
                          v={'drivers': ['C_spine.hipCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 2})
        attrLib.addString(self.blueprintGrp, 'blu_footSpace',
                          v={'drivers': ['C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 1})
        attrLib.addString(self.blueprintGrp, 'blu_kneeSpace',
                          v={'drivers': ['C_spine.hipCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_jntParent', v='C_spine.hipCtl')
