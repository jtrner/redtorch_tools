"""
name: tail.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import connect
from ...lib import strLib
from ...lib import attrLib
from ...lib import trsLib
from ...lib import jntLib
from ...lib import crvLib
from ...lib import space
from ..command import rope
from . import template

reload(connect)
reload(strLib)
reload(attrLib)
reload(trsLib)
reload(jntLib)
reload(crvLib)
reload(rope)
reload(space)
reload(template)


class Tail(template.Template):
    """
    class for creating tail rig for biped characters
    """

    def __init__(self, side="C", prefix="tail", numOfCtls=6, numOfJnts=10,
                 jntsToRig=None, hasMidCtl=True, autoOrient=True, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.hasMidCtl = hasMidCtl
        self.numOfCtls = numOfCtls
        self.numOfJnts = numOfJnts
        self.jntsToRig = jntsToRig
        self.autoOrient = autoOrient

        super(Tail, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Tail, self).createBlueprint()

        # create input blueprints
        par = self.blueprintGrp
        for i in range(self.numOfCtls):
            blu = '{}_{:03d}_BLU'.format(self.name, i + 1)
            self.blueprints['{:03d}'.format(i + 1)] = blu
            if not mc.objExists(blu):
                mc.joint(par, name=blu)
                mc.xform(blu, ws=True, t=(0, 10, (i + 1) * -1))
            par = blu

        self.orientJnts(self.blueprints.values())

        # delete extra blueprint joints
        all_blueprints = mc.ls('{}_???_BLU'.format(self.name))
        if len(all_blueprints) > self.numOfCtls:
            mc.error('tail.py: numOfCtls value is less than number of found blueprint joints!')
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=self.blueprints)

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """

        # use existing joints
        if self.jntsToRig:
            self.joints['chainJnts'] = self.jntsToRig

        # or create joints
        else:
            crv = crvLib.fromJnts(jnts=self.blueprints.values(),
                                  degree=1, fit=False)[0]
            mc.rebuildCurve(crv, degree=3, spans=2)
            self.joints['chainJnts'] = []
            jnts = jntLib.create_on_curve(curve=crv, numOfJoints=self.numOfJnts,
                                          parent=True)
            mc.parent(jnts[0], self.moduleGrp)
            for i in range(self.numOfJnts):
                jnt = '{}_{:03d}_JNT'.format(self.name, i + 1)
                jnt = mc.rename(jnts[i], jnt)
                self.joints['chainJnts'].append(jnt)
            mc.delete(crv)


        # orient joints
        if self.autoOrient:
            self.orientJnts(self.joints['chainJnts'])

    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='y')
        mc.delete(upLoc)

    def build(self):
        super(Tail, self).build()
        self.baseCtl, crvGrp, rsltGrp, ctls, tweakCtls, jnts = rope.run(
            jnts=self.joints['chainJnts'],
            guides=self.blueprints.values(),
            numJnts=None,
            description=self.prefix,
            matchOrientation=True,
            addTweaks=True,
            fkMode=True,aim = 'y')

        self.lastCtl = ctls[-1]
        self.setOut('lastCtl', self.lastCtl)
        self.baseCtlZro = mc.listRelatives(self.baseCtl, p=1)[0]
        mc.parent(self.baseCtlZro, self.ctlGrp)
        mc.parent(crvGrp, rsltGrp, self.originGrp)

    def connect(self):
        """
        connection of created nodes
        """
        super(Tail, self).connect()

        # outliner clean up
        hipCtl = self.getOut('hipCtl')
        connect.matrix(hipCtl, self.moduleGrp)
        connect.matrix(hipCtl, self.ctlGrp)

        # fk orient space
        orientDrivers = self.getOut('tailOrient')
        if orientDrivers:
            space.orient(
                drivers=orientDrivers,
                drivens=[self.baseCtlZro],
                control=self.baseCtl,
                name=self.name + 'OrientSpace')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Tail, self).createSettings()

        attrLib.addInt(self.blueprintGrp, 'blu_numOfCtls', v=self.numOfCtls)
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts)
        attrLib.addBool(self.blueprintGrp, 'blu_autoOrient', v=self.autoOrient)
        attrLib.addString(self.blueprintGrp, 'blu_jntsToRig', v=self.jntsToRig or '')
        attrLib.addString(self.blueprintGrp, 'blu_bodyCtl', v='C_root.bodyCtl')
        attrLib.addString(self.blueprintGrp, 'blu_hipCtl', v='C_spine.hipCtl')
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')

        attrLib.addString(self.blueprintGrp, 'blu_tailOrient',
                          v={'drivers': ['C_spine.hipCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
