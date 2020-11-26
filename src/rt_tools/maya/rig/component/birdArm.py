"""
name: arm.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import jntLib
from ...lib import trsLib
from ...lib import connect
from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import space
from ..command import fk
from ..command import ikArm
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
reload(fk)
reload(ikArm)
reload(ikStretch)
reload(twist)
reload(pv)
reload(template)


class BirdArm(template.Template):
    """
    class for creating spine rig for biped characters
    """

    def __init__(self, side="L", prefix="birdArm", mode='fkik',
                 useRibbon=True, **kwargs):

        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.mode = mode  # rig ik and fk
        self.useRibbon = useRibbon
        super(BirdArm, self).__init__(**kwargs)

    def createBlueprint(self):
        super(BirdArm, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        self.blueprints['clavicle'] = '{}_clavicle_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['clavicle']):
            mc.joint(self.blueprintGrp, name=self.blueprints['clavicle'])
            mc.xform(self.blueprints['clavicle'], ws=True, t=(1 * mult, 17, 0))

        self.blueprints['shoulder'] = '{}_shoulder_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['shoulder']):
            mc.joint(self.blueprints['clavicle'], name=self.blueprints['shoulder'])
            mc.xform(self.blueprints['shoulder'], ws=True, t=(3 * mult, 17, 0))

        self.blueprints['elbow'] = '{}_elbow_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['elbow']):
            mc.joint(self.blueprints['shoulder'], name=self.blueprints['elbow'])
            mc.xform(self.blueprints['elbow'], ws=True, t=(8 * mult, 17, 0))


        self.blueprints['hand'] = '{}_hand_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['hand']):
            mc.joint(self.blueprints['elbow'], name=self.blueprints['hand'])
            mc.xform(self.blueprints['hand'], ws=True, t=(13.7 * mult, 17, 0))

        self.blueprints['handEnd'] = '{}_handEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['handEnd']):
            mc.joint(self.blueprints['hand'], name=self.blueprints['handEnd'])
            mc.xform(self.blueprints['handEnd'], ws=True, t=(15 * mult, 17, 0))

        self.orientJnts(self.blueprints)

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)
        attrLib.setAttr(self.blueprintGrp + '.blu_inputs', self.blueprints)

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        # create joints
        par = self.moduleGrp
        armJnts = []
        for alias, blu in self.blueprints.items():
            jnt = blu.replace('BLU', 'JNT')
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt
            armJnts.append(jnt)

        self.shoulderJnt = armJnts[1]
        self.elbowJnt = armJnts[2]
        self.handJnt = armJnts[3]

        self.setOut('shoulderJnt' , self.shoulderJnt)
        self.setOut('elbowJnt', self.elbowJnt)
        self.setOut('handJnt', self.handJnt)


        self.orientJnts(self.joints)
        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):

        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']

        # orient clavicle
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts['clavicle'])
        mc.xform(upLoc, ws = True, t=(4.46 , 11.84, -3.47))
        jntLib.orientUsingAim(jnts=jnts.values(), upAim=upLoc,
                              aimAxes='z', upAxes='x', inverseUpAxes=inverseUpAxes)
        mc.delete(upLoc)

        # orient shoulder and elbow
        jntLib.orientLimb(jnts=jnts.values()[1:], aimAxes='z',
                          upAxes='x', inverseUpAxes=inverseUpAxes)

        # orient hand
        upLoc = mc.createNode('transform', p=jnts['elbow'])
        trsLib.match(upLoc, jnts['hand'])
        mc.move(0, mult, 0, upLoc, r=True, ls=True)
        jntLib.orientUsingAim(jnts=jnts.values()[3:], upAim=upLoc,
                              aimAxes='z', upAxes='y', inverseUpAxes=inverseUpAxes)
        mc.delete(upLoc)
    def build(self):
        """
        building necessary nodes
        """
        super(BirdArm, self).build()

        # set outputs
        self.setOut('handJnt', self.joints['hand'])

        # setting ctl
        size = trsLib.getDistance(self.joints['shoulder'], self.joints['hand'])
        mult = [1, -1][self.side == 'R']
        settingCtl = control.Control(descriptor=self.prefix + '_setting',
                                     side=self.side,
                                     parent=self.ctlGrp,
                                     shape='hand',
                                     scale=[size / 10, size / 10, size / 10],
                                     orient=[0, mult, 0],
                                     moveShape=[0, mult * size / 10, 0],
                                     lockHideAttrs=['t', 'r', 's', 'v'],
                                     trs=self.blueprintPoses['hand'])
        mc.parentConstraint(self.joints['hand'], settingCtl.zro, mo=True)
        settingCtl = settingCtl.name
        self.setOut('armSettingCtl' , settingCtl)
        # ==========================================================
        # clavicle
        # ==========================================================
        self.rig_clav()
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
            attrLib.addFloat(settingCtl, ln="fk_ik", min=0, max=1)
            jntLib.blend_fk_ik(self.fkJntList, self.ikJntList,
                               self.joints.values()[1:], settingCtl + ".fk_ik")

            # connect visibility settings
            attrLib.addEnum(settingCtl, ln="fk_vis", en=['off', 'on'], dv=1, k=False)
            attrLib.addEnum(settingCtl, ln="ik_vis", en=['off', 'on'], dv=0, k=False)

            fkZero = self.fkCtlList[0].replace('CTL', 'ZRO')
            mc.connectAttr(settingCtl + ".fk_vis", fkZero + '.v')

            ikHandZero = self.handIkCtl.replace('CTL', 'ZRO')
            mc.connectAttr(settingCtl + ".ik_vis", ikHandZero + '.v')

            ikElbowZero = self.elbowIkCtl.replace('CTL', 'ZRO')
            mc.connectAttr(settingCtl + ".ik_vis", ikElbowZero + '.v')

        # shoulder bendy/twist joints
        shoulderTwstGrp, shoulderTwstModuleGrp, startJnt,midJnt,endJnt,startCtlzro,midCtlzro,endCtlzro,startCtlname,midCtlname,endCtlname = twist.run(
            start=self.joints['shoulder'],
            end=self.joints['elbow'],
            nb=3,
            name=self.name + '_shoulder',
            reverse=True,
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(shoulderTwstGrp, self.ctlGrp)
        mc.parent(shoulderTwstModuleGrp, self.moduleGrp)

        firstShoulderTwistJnt = startJnt
        secondShoulderTwistJnt = midJnt
        thirdShoulderTwistJnt = endJnt

        startTwistShoulderCtlGrp = startCtlzro
        midTwistShoulderCtlGrp = midCtlzro
        endTwistShoulderCtlGrp = endCtlzro

        startTwistShoulderCtl = startCtlname
        midTwistShoulderCtl = midCtlname
        endTwistShoulderCtl = endCtlname

        self.setOut('startTwistShoulderCtlGrp', str(startTwistShoulderCtlGrp))
        self.setOut('midTwistShoulderCtlGrp', str(midTwistShoulderCtlGrp))
        self.setOut('endTwistShoulderCtlGrp', str(endTwistShoulderCtlGrp))

        self.setOut('startTwistShoulderCtl', str(startTwistShoulderCtl))
        self.setOut('midTwistShoulderCtl', str(midTwistShoulderCtl))
        self.setOut('endTwistShoulderCtl', str(endTwistShoulderCtl))


        self.setOut('firstShoulderTwistJnts', str(firstShoulderTwistJnt))
        self.setOut('secondShoulderTwistJnts', str(secondShoulderTwistJnt))
        self.setOut('thirdShoulderTwistJnts', str(thirdShoulderTwistJnt))



        # elbow bendy/twist joints
        twstCtlGrp,twstModuleGrp, startJnt, midJnt,endJnt,startCtlzro,midCtlzro,endCtlzro,startCtlname,midCtlname,endCtlname= twist.run(
            start=self.joints['elbow'],
            end=self.joints['hand'],
            nb=3,
            name=self.name + '_elbow',
            side=self.side,
            useRibbon=self.useRibbon)
        if self.useRibbon:
            mc.parent(twstCtlGrp, self.ctlGrp)
        mc.parent(twstModuleGrp, self.moduleGrp)

        firstElbowTwistJnt = startJnt
        secondElbowTwistJnt = midJnt
        thirdElbowTwistJnt = endJnt

        startTwistElbowCtlGrp = startCtlzro
        midTwistElbowCtlGrp = midCtlzro
        endTwistElbowCtlGrp = endCtlzro

        startTwistElbowCtl = startCtlname
        midTwistElbowCtl = midCtlname
        endTwistElbowCtl = endCtlname

        self.setOut('startTwistElbowCtlGrp', str(startTwistElbowCtlGrp))
        self.setOut('midTwistElbowCtlGrp', str(midTwistElbowCtlGrp))
        self.setOut('endTwistElbowCtlGrp', str(endTwistElbowCtlGrp))

        self.setOut('startTwistElbowCtl', str(startTwistElbowCtl))
        self.setOut('midTwistElbowCtl', str(midTwistElbowCtl))
        self.setOut('endTwistElbowCtl', str(endTwistElbowCtl))

        self.setOut('firstElbowTwistJnts', str(firstElbowTwistJnt))
        self.setOut('secondElbowTwistJnts', str(secondElbowTwistJnt))
        self.setOut('thirdElbowTwistJnts', str(thirdElbowTwistJnt))




        # twist visibility settings
        if self.useRibbon:
            attrLib.addEnum(settingCtl, ln="twist_vis", en=['off', 'on'], dv=0, k=False)
            mc.connectAttr(settingCtl + ".twist_vis", shoulderTwstGrp + '.v')
            mc.connectAttr(settingCtl + ".twist_vis", twstCtlGrp + '.v')

    def rig_clav(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # ik rig joints
        clavicleJnts = jntLib.extract_from_to(
            self.joints['clavicle'],
            self.joints['shoulder'],
            search="_JNT",
            replace="_ik_TRS")
        self.clavJnt = clavicleJnts[0]
        self.clavEnd = mc.rename(clavicleJnts[1], self.name + '_clavEnd_JNT')
        self.setOut('clavEnd', self.clavEnd)

        # add controls
        mult = [1, -1][self.side == 'R']
        self.clavCtl = control.Control(
            descriptor=self.prefix + '_clavicle',
            side=self.side,
            parent=self.ctlGrp,
            shape='cube',
            scale=[1, 1, 1],
            orient=[0, mult, 0],
            matchTranslate=self.clavJnt,
            matchRotate=self.clavJnt,
            matchScale=self.clavJnt,
            verbose=self.verbose).name

        # clavicle ik handle
        clavIkh_and_eff = mc.ikHandle(
            solver='ikSCsolver',
            startJoint=self.clavJnt,
            endEffector=self.clavEnd,
            name=self.name + '_clav_IKH')
        self.clavIkh = clavIkh_and_eff[0]

        # zero group for ikh
        ikZro = self.clavIkh.replace('IKH', 'ikh_ZRO')
        trsLib.insert(self.clavIkh, mode='parent', name=ikZro)

        # connect control to rig
        connect.multiConstraint(
            self.clavCtl,
            [ikZro],
            t=1, r=1, s=1,
            mo=True)

        # clean up outliner
        mc.parent(ikZro, self.moduleGrp)

        # connect rig to skeleton
        connect.direct(self.clavJnt, self.joints['clavicle'])

    def rig_ik(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # find poleVec position
        armJnts = self.joints['shoulder'], self.joints['elbow'], self.joints['hand']
        self.poleVec = pv.Pv(jnts=armJnts, distance=1.0, createLoc=True)[0]
        self.setOut('poleVec', self.poleVec)

        # ik rig joints
        self.ikJntList = jntLib.extract_from_to(
            self.joints['shoulder'],
            self.joints['handEnd'],
            search="_JNT",
            replace="_ik_TRS")

        handIkJnt = self.ikJntList[-2]
        elbowIkJnt = self.ikJntList[-3]

        self.setOut('handIkJnt', handIkJnt)
        self.setOut('elbowIkJnt', elbowIkJnt)



        self.setOut('ikJntList', str(self.ikJntList))

        self.ikCtlList, ikHandleList = ikArm.IkArm(
            joints=self.ikJntList,
            parent=self.ctlGrp,
            side=self.side,
            prefix=self.prefix,
            poleVec=self.poleVec,
            verbose=self.verbose)
        self.handIkCtl = self.ikCtlList[0].name
        self.elbowIkCtl = self.ikCtlList[1].name
        self.armIkh = ikHandleList[0]

        # set output
        self.setOut('handIkCtl', self.handIkCtl)
        self.setOut('elbowIkCtl', self.elbowIkCtl)
        self.setOut('armIkh', self.armIkh)

        # outliner clean up
        mc.parent(self.ikJntList[0], self.clavJnt)
        mc.parent(trsLib.getParent(self.armIkh), self.moduleGrp)
        mc.delete(self.poleVec)

    def rig_fk(self):
        # read attrs from asset node
        self.getAttrsFromBlueprint()

        # fk rig joints
        self.fkJntList = jntLib.extract_from_to(
            self.joints['shoulder'],
            self.joints['handEnd'],
            search="_JNT",
            replace="_fk_TRS")

        #add controls
        self.fkCtlList = fk.Fk(
            joints=self.fkJntList,
            parent=self.ctlGrp,
            shape="circle",
            movable= False,
            variableIconSize=False,
            upVector = [0,1,0] ,
            worldUp = [0,1,0],
            aimVec= 'z')

        self.fkCtlList = [x.name for x in self.fkCtlList]

        self.elbowFkCtl = self.fkCtlList[1]
        self.handFkCtl = self.fkCtlList[2]
        self.setOut('elbowfkCtl', self.elbowFkCtl)
        self.setOut('handfkCtl', self.handFkCtl)


        self.setOut('fkCtlList', self.fkCtlList)

        # outliner clean up
        mc.parent(self.fkJntList[0], self.clavJnt)

    def connect(self):
        """
        connection of created nodes
        """
        super(BirdArm, self).connect()

        # connect clav
        gs = self.getOut('globalScale')
        ikStretch.run(startCtl=self.clavCtl.replace('CTL', 'ZRO'),
                      pvCtl=None,
                      ctl=self.clavCtl,
                      ikh=self.clavIkh,
                      globalScaleAttr=gs + '.scaleY',
                      name=self.name)

        # fk point space
        fkZero = self.fkCtlList[0].replace('CTL', 'ZRO')
        mc.pointConstraint(self.clavEnd, fkZero)
        mc.pointConstraint(self.clavEnd, self.ikJntList[0])

        # fk orient space
        orientDrivers = self.getOut('fkOrient')
        space.orient(
            drivers=orientDrivers,
            drivens=[fkZero],
            control=self.fkCtlList[0],
            name=self.name + 'OrientSpace')

        # hand space
        handDrivers = self.getOut('handSpace')
        ikHandZero = self.handIkCtl.replace('CTL', 'ZRO')
        space.parent(
            drivers=handDrivers,
            drivens=[ikHandZero],
            control=self.handIkCtl,
            name=self.name + 'Space')

        # elbow space
        elbowDrivers = self.getOut('elbowSpace')
        ikElbowZero = self.elbowIkCtl.replace('CTL', 'ZRO')
        space.parent(
            drivers=elbowDrivers,
            drivens=[ikElbowZero],
            control=self.elbowIkCtl,
            name=self.name + 'Space')

        # attach controls
        jntParent = self.getOut('jntParent')
        connect.matrix(jntParent, self.moduleGrp)
        connect.matrix(jntParent, self.ctlGrp)

        fkZro = self.fkCtlList[0].replace('CTL', 'ZRO')
        #mc.connectAttr(gs + '.scaleY', fkZro + '.globalScale')

        # make ik stretchy
        ikStretch.run(startCtl=self.clavEnd,
                      pvCtl=self.elbowIkCtl,
                      ctl=self.handIkCtl,
                      ikh=self.armIkh,
                      globalScaleAttr=gs + '.scaleY',
                      name=self.name)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(BirdArm, self).createSettings()

        attrLib.addEnum(self.blueprintGrp, 'blu_mode', en=['fk', 'ik', 'fkik'], dv=2)
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_spine.chestCtl')
        attrLib.addString(self.blueprintGrp, 'blu_jntParent', v='C_spine.chestJnt')

        attrLib.addString(self.blueprintGrp, 'blu_fkOrient',
                          v={'drivers': [
                              self.name + '.clavEnd',
                              'C_spine.chestCtl',
                              'C_root.bodyCtl',
                              'C_root.mainCtl'],
                              'dv': 3})

        attrLib.addString(self.blueprintGrp, 'blu_handSpace',
                          v={'drivers': [
                              'C_spine.chestCtl',
                              'C_spine.hipCtl',
                              'C_root.bodyCtl',
                              'C_root.mainCtl'],
                              'dv': 3})

        attrLib.addString(self.blueprintGrp, 'blu_elbowSpace',
                          v={'drivers': [
                              'C_spine.chestCtl',
                              'C_spine.hipCtl',
                              'C_root.bodyCtl',
                              'C_root.mainCtl'],
                              'dv': 3})
