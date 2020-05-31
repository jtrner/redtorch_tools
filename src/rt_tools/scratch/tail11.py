"""
name: tail.py

Author: Ehsan Hassani Moghaddam

Usage:
import sys

path = "G:/Rigging/Shows/MAW"
while path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

from maw_scripts import tail
reload(tail)

a = tail.Tail()
a.build()
"""
# python modules
import logging

# maya modules
import maya.cmds as mc

# iRig modules
from iRig.iRig_maya.lib import connect
from iRig.iRig_maya.lib import attrLib
from iRig.iRig_maya.lib import trsLib
from iRig.iRig_maya.lib import jntLib
from iRig.iRig_maya.lib import crvLib
from iRig.iRig_maya.lib import space
from maw_scripts.component import rope
from maw_scripts.component import template

reload(connect)
reload(attrLib)
reload(trsLib)
reload(jntLib)
reload(crvLib)
reload(space)
reload(template)
reload(rope)

# constants
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Tail(template.Template):
    """
    class for creating tail rig for biped characters
    """

    def __init__(self, side="C", prefix="Tail", numOfCtls=6, numOfJnts=10,
                 jntsToRig=None, autoOrient=True, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numOfCtls = numOfCtls
        self.numOfJnts = numOfJnts
        self.jntsToRig = jntsToRig
        self.autoOrient = autoOrient

        super(Tail, self).__init__(**kwargs)

    def createGuide(self):
        super(Tail, self).createGuide()

        # create input guides
        par = self.guideGrp
        for i in range(self.numOfCtls):
            blu = '{}_{:03d}_Guide'.format(self.name, i + 1)
            self.guides['{:03d}'.format(i + 1)] = blu
            if not mc.objExists(blu):
                mc.joint(par, name=blu)
                mc.xform(blu, ws=True, t=(0, 10, (i + 1) * -1))
            par = blu

        self.orientJnts(self.guides.values())

        # delete extra guide joints
        all_guides = mc.ls('{}_???_Guide'.format(self.name))
        if len(all_guides) > self.numOfCtls:
            mc.error('tail.py: numOfCtls value is less than number of found guide joints!')
        attrLib.addString(self.guideGrp, ln='blu_inputs', v=self.guides)

    def createJoints(self):
        """
        create joints from guide poses
        :return:
        """

        # use existing joints
        if self.jntsToRig:
            self.joints['chainJnts'] = self.jntsToRig

        # or create joints
        else:
            crv = crvLib.fromJnts(jnts=self.guides.values(),
                                  degree=1, fit=False)[0]
            mc.rebuildCurve(crv, degree=3, spans=2)
            self.joints['chainJnts'] = []
            jnts = jntLib.create_on_curve(curve=crv, numOfJoints=self.numOfJnts,
                                          parent=True)
            mc.parent(jnts[0], self.jntGrp)
            for i in range(self.numOfJnts):
                jnt = '{}_{:03d}_Jnt'.format(self.name, i + 1)
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
        self.baseCtl, crvGrp, rsltGrp, ctls, tweakCtls, jnts, surf, flcs = rope.run(
            jnts=self.joints['chainJnts'],
            guides=self.guides.values(),
            numJnts=None,
            description=self.prefix,
            matchOrientation=True,
            addTweaks=True,
            fkMode=True)
        self.baseCtlZro = mc.listRelatives(self.baseCtl, p=1)[0]
        mc.parent(self.baseCtlZro, self.ctlGrp)
        mc.parent(crvGrp, rsltGrp, surf, flcs, self.originGrp)

    def connect(self):
        """
        connection of created nodes
        """
        super(Tail, self).connect()

        # outliner clean up
        hipCtl = self.getOut('hipCtl')
        connect.matrix(hipCtl, self.utilityGrp)
        connect.matrix(hipCtl, self.ctlGrp)

        # fk orient space
        orientDrivers = self.getOut('tailOrient')
        if orientDrivers:
            space.orient(
                drivers=orientDrivers,
                drivens=[self.baseCtlZro],
                control=self.baseCtl,
                name=self.name + 'OrientSpace'
            )

        # attach controls
        globalCtl = self.getOut('globalScale')
        if globalCtl:
            mc.scaleConstraint(globalCtl, self.jntGrp)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Tail, self).createSettings()

        attrLib.addInt(self.guideGrp, 'blu_numOfCtls', v=self.numOfCtls)
        attrLib.addInt(self.guideGrp, 'blu_numOfJnts', v=self.numOfJnts)
        attrLib.addBool(self.guideGrp, 'blu_autoOrient', v=self.autoOrient)
        attrLib.addString(self.guideGrp, 'blu_jntsToRig', v=self.jntsToRig or '')
        attrLib.addString(self.guideGrp, 'blu_bodyCtl', v='COG_Gimbal_Ctrl_Gimbal_Ctrl')
        attrLib.addString(self.guideGrp, 'blu_hipCtl', v='C_Spine_Hips_Ctrl')
        attrLib.addString(self.guideGrp, 'blu_globalScale', v='Root_Ctrl')

        attrLib.addString(self.guideGrp, 'blu_tailOrient', v={'drivers': [], 'dv': 0})
