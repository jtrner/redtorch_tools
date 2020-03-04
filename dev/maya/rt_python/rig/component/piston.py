"""
name: piston.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import trsLib
from ...lib import crvLib
from ...lib import connect
from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import jntLib
from ...lib import display
from ..command import rope
from . import template

reload(trsLib)
reload(crvLib)
reload(connect)
reload(control)
reload(strLib)
reload(attrLib)
reload(jntLib)
reload(display)
reload(rope)
reload(template)


class Piston(template.Template):
    """
    class for creating piston rig for biped characters
    """

    def __init__(self, side="C", prefix="piston", stretch=False, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.stretch = stretch

        super(Piston, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Piston, self).createBlueprint()

        # add blueprint attrs
        # this data will be used to initialize the class later
        self.blueprints['start'] = '{}_start_BLU'.format(self.name)
        self.blueprints['up'] = '{}_up_BLU'.format(self.name)
        self.blueprints['end'] = '{}_end_BLU'.format(self.name)
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

        # create input blueprints
        if not mc.objExists(self.blueprints['start']):
            mc.joint(self.blueprintGrp, name=self.blueprints['start'])
            mc.xform(self.blueprints['start'], ws=True, t=(0, 0, 0))
        if not mc.objExists(self.blueprints['up']):
            mc.joint(self.blueprints['start'], name=self.blueprints['up'])
            mc.xform(self.blueprints['up'], ws=True, t=(0, 1, 0))
        if not mc.objExists(self.blueprints['end']):
            mc.joint(self.blueprints['start'], name=self.blueprints['end'])
            mc.xform(self.blueprints['end'], ws=True, t=(0, 0, 2))

        self.orientJnts(self.blueprints['start'],
                        self.blueprints['up'],
                        self.blueprints['end'])

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        self.joints['start'] = mc.createNode(
            'transform', n=self.name + '_start_SRT', p=self.moduleGrp)
        trsLib.setTRS(self.joints['start'], self.blueprintPoses['start'], space='world')

        self.joints['pistonJnt'] = mc.joint(self.joints['start'], n=self.name + '_start_JNT')
        trsLib.setTRS(self.joints['pistonJnt'], self.blueprintPoses['start'], space='world')
        self.setOut('pistonJnt', self.joints['start'])

        self.joints['up'] = mc.createNode(
            'transform', n=self.name + '_up_SRT', p=self.moduleGrp)
        trsLib.setTRS(self.joints['up'], self.blueprintPoses['up'], space='world')

        self.joints['end'] = mc.createNode(
            'transform', n=self.name + '_end_SRT', p=self.moduleGrp)
        trsLib.setTRS(self.joints['end'], self.blueprintPoses['end'], space='world')

    def orientJnts(self, start, up, end):
        jntLib.orientUsingAim(
            jnts=[start, end], upAim=up, aimAxes='x', upAxes='y', resetLast=False)

    def build(self):
        """
        building necessary nodes
        """
        super(Piston, self).build()

        # start and end drivers
        startDriver = self.getOut('startDriver')
        endDriver = self.getOut('endDriver')

        # aim start to end
        mc.aimConstraint(self.joints['end'], self.joints['pistonJnt'],
                         aim=(1, 0, 0),
                         upVector=(0, 1, 0),
                         worldUpType='object',
                         worldUpObject=self.joints['up'],
                         worldUpVector=(0, 1, 0))

        # stretch
        if self.stretch:
            dst = mc.createNode('distanceBetween', n=self.name + '_stretch_DST')
            mc.connectAttr(self.joints['start'] + '.worldMatrix', dst + '.inMatrix1')
            mc.connectAttr(self.joints['end'] + '.worldMatrix', dst + '.inMatrix2')

            gs = attrLib.addFloat(self.moduleGrp, ln='globalScale', min=0.001, dv=1)
            gsMdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_global_scale_MDN')
            mc.connectAttr(dst + '.distance', gsMdn + '.input1X')
            mc.connectAttr(gs, gsMdn + '.input2X')
            mc.setAttr(gsMdn + '.operation', 2)

            mdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_MDN')
            mc.connectAttr(gsMdn + '.outputX', mdn + '.input1X')
            dist = mc.getAttr(dst + '.distance')
            mc.setAttr(mdn + '.input2X', dist)
            mc.setAttr(mdn + '.operation', 2)

            mc.connectAttr(mdn + '.outputX', self.joints['pistonJnt'] + '.scaleX')

            volumeMdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_volume_MDN')
            mc.connectAttr(mdn + '.outputX', volumeMdn + '.input1X')
            mc.setAttr(volumeMdn + '.input2X', -1)
            mc.setAttr(volumeMdn + '.operation', 3)

            mc.connectAttr(volumeMdn + '.outputX', self.joints['pistonJnt'] + '.scaleY')
            mc.connectAttr(volumeMdn + '.outputX', self.joints['pistonJnt'] + '.scaleZ')

        # outliner clean up
        if startDriver:
            mc.parentConstraint(startDriver, self.joints['start'], mo=True)
        if endDriver:
            mc.parentConstraint(startDriver, self.joints['end'], mo=True)

    def connect(self):
        """
        connection of created nodes
        """
        super(Piston, self).connect()

        gs = self.getOut('globalScale')
        mc.connectAttr(gs + '.globalScale', self.moduleGrp + '.globalScale')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Piston, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_startDriver')
        attrLib.addString(self.blueprintGrp, 'blu_endDriver')
