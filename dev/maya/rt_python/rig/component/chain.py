"""
name: chain.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import attrLib
from ...lib import connect
from ...lib import trsLib
from ...lib import jntLib
from ...lib import space
from ..command import fk
from . import template

reload(attrLib)
reload(connect)
reload(trsLib)
reload(jntLib)
reload(space)
reload(fk)
reload(template)


class Chain(template.Template):
    """Class for creating chain"""

    def __init__(self, side='C', prefix='chain', hideLastCtl=False, movable=False, numOfJnts=6, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.hideLastCtl = hideLastCtl
        self.movable = movable
        self.numOfJnts = numOfJnts
        super(Chain, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Chain, self).createBlueprint()

        # create input blueprints
        par = self.blueprintGrp
        for i in range(self.numOfJnts):
            blu = '{}_{:03d}_BLU'.format(self.name, i + 1)
            self.blueprints['{:03d}'.format(i + 1)] = blu
            if not mc.objExists(blu):
                mc.joint(par, name=blu)
                mc.xform(blu, ws=True, t=(0, 0, (i + 1) * -1))
            par = blu

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        self.joints['chainJnts'] = []
        par = self.moduleGrp
        for i in range(self.numOfJnts):
            jnt = '{}_{:03d}_JNT'.format(self.name, i + 1)
            mc.joint(par, name=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses['{:03d}'.format(i + 1)], space='world')
            par = jnt
            self.joints['chainJnts'].append(jnt)

    def build(self):
        """
        building necessary nodes
        """
        super(Chain, self).build()

        # add controls
        ctls = fk.Fk(
            joints=self.joints['chainJnts'],
            parent=self.ctlGrp,
            shape='sphere',
            hideLastCtl=self.hideLastCtl,
            connectGlobalScale=True,
            movable=self.movable)

        if not self.hideLastCtl and self.numOfJnts > 1:
            connect.direct(ctls[-1].name, self.joints['chainJnts'][-1], attrs=['r'])

        # keep in asset node for later use
        self.controls['chainCtls'] = [x.name for x in ctls]
        self.setOut('chainCtls', str(ctls))


    def connect(self):
        """
        connection of created nodes 
        """
        super(Chain, self).connect()

        # attach controls
        globalCtl = self.getOut('globalScale')
        if globalCtl:
            connect.matrix(globalCtl, self.moduleGrp)
            connect.matrix(globalCtl, self.ctlGrp)
        else:
            mc.warning('chain -> Can\'t parent controls!')

        # point space
        pointDrivers = self.getOut('spacePoint')
        if pointDrivers:
            ctlZero = self.controls['chainCtls'][0].replace('CTL', 'ZRO')
            space.point(
                drivers=pointDrivers,
                drivens=[ctlZero],
                control=self.controls['chainCtls'][0],
                name=self.name + 'PointSpace',
            )
        else:
            mc.warning('chain -> Can\'t pointConstraint chain!')

        # orient space
        orientDrivers = self.getOut('spaceOrient')
        if orientDrivers:
            space.orient(
                drivers=orientDrivers,
                drivens=[ctlZero],
                control=self.controls['chainCtls'][0],
                name=self.name + 'OrientSpace',
            )
        else:
            mc.warning('chain -> Can\'t orientConstraint chain!')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Chain, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts)
        attrLib.addString(self.blueprintGrp, 'blu_spacePoint', v={'drivers': [], 'dv': 0})
        attrLib.addString(self.blueprintGrp, 'blu_spaceOrient', v={'drivers': [], 'dv': 0})
