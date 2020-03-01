"""
name: finger.py

Author: Ehsan Hassani Moghaddam

History:
    06/02/16 (ehassani)    first release!

"""
import maya.cmds as mc

from ...lib import connect
from ...lib import strLib
from ...lib import trsLib
from ...lib import attrLib
from ..command import fk
from . import template

reload(connect)
reload(strLib)
reload(trsLib)
reload(attrLib)
reload(fk)
reload(template)


class Finger(template.Template):
    """
    class for creating finger
    """

    def __init__(self, side="L", prefix="index", numOfJnts=4, movable=False, lockHideAttrs=['s', 'v'], **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.lockHideAttrs = lockHideAttrs
        self.numOfJnts = numOfJnts
        self.movable = movable
        super(Finger, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Finger, self).createBlueprint()

        name = self.getName()

        z = 0
        if self.prefix == 'thumb':
            z = 1
        elif self.prefix == 'index':
            z = 0.5
        elif self.prefix == 'middle':
            z = 0
        elif self.prefix == 'ring':
            z = -0.5
        elif self.prefix == 'pinky':
            z = -1

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        self.blueprints['meta'] = '{}_meta_BLU'.format(name)
        if not mc.objExists(self.blueprints['meta']):
            mc.joint(self.blueprintGrp, name=self.blueprints['meta'])
            mc.xform(self.blueprints['meta'], ws=True, t=(15.5 * mult, 17, z))

        par = self.blueprints['meta']
        for i in range(self.numOfJnts):
            blu = '{}_{}_BLU'.format(name, strLib.ALPHABET[i])
            self.blueprints[strLib.ALPHABET[i]] = blu
            if not mc.objExists(blu):
                mc.joint(par, name=blu)
                mc.xform(blu, ws=True, t=((16 + (0.2 * i)) * mult, 17, z))
            par = blu

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        # create joints
        par = self.moduleGrp
        for alias, blu in self.blueprints.items():
            jnt = blu.replace('BLU', 'JNT')
            jnt = mc.joint(par, n=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt

        self.setOut('joints', str(self.joints))

        # todo: orient joints

    def build(self):
        """
        building necessary nodes
        """
        super(Finger, self).build()

        par = self.getOut('ctlParent')

        # add controls
        fingerCtls = fk.Fk(joints=self.joints.values(),
                           parent=par,
                           shape="circle",
                           lockHideAttrs=self.lockHideAttrs,
                           movable=self.movable)

        # outliner clean up
        mc.parent(fingerCtls[0].zro, self.ctlGrp)

    def connect(self):
        """
        connection of created nodes 
        """
        super(Finger, self).connect()

        par = self.getOut('ctlParent')
        if par:
            connect.matrix(par, self.ctlGrp, world=True)
            connect.matrix(par, self.moduleGrp, world=True)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Finger, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v=self.side + '_arm.handJnt')
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts)
        attrLib.addBool(self.blueprintGrp, 'blu_movable', v=self.movable)
