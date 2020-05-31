"""
name: piston.py

Author: Ehsan Hassani Moghaddam
"""
import maya.cmds as mc

from iRig.iRig_maya.lib import trsLib
from iRig.iRig_maya.lib import attrLib
from iRig.iRig_maya.lib import jntLib
from iRig.iRig_maya.lib import control
from maw_scripts.component import template

reload(trsLib)
reload(attrLib)
reload(jntLib)
reload(control)
reload(template)


class Piston(template.Template):
    """
    class for creating piston rig for biped characters
    """
    def __init__(
            self,
            side="C",
            prefix="Piston",
            stretch=False,
            createStartCtl=False,
            createUpCtl=False,
            createEndCtl=False,
            **kwargs):

        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.stretch = stretch
        self.createStartCtl = createStartCtl
        self.createUpCtl = createUpCtl
        self.createEndCtl = createEndCtl

        super(Piston, self).__init__(**kwargs)

    def createGuide(self):
        super(Piston, self).createGuide()

        # add guide attrs
        # this data will be used to initialize the class later
        self.guides['start'] = '{}_Start_Guide'.format(self.name)
        self.guides['up'] = '{}_Up_Guide'.format(self.name)
        self.guides['end'] = '{}_End_Guide'.format(self.name)
        attrLib.addString(self.guideGrp, ln='blu_inputs', v=str(self.guides))

        # create input guides
        if not mc.objExists(self.guides['start']):
            mc.joint(self.guideGrp, name=self.guides['start'])
            mc.xform(self.guides['start'], ws=True, t=(0, 0, 0))

        if not mc.objExists(self.guides['up']):
            mc.joint(self.guides['start'], name=self.guides['up'])
            mc.xform(self.guides['up'], ws=True, t=(0, 1, 0))

        if not mc.objExists(self.guides['end']):
            mc.joint(self.guides['start'], name=self.guides['end'])
            mc.xform(self.guides['end'], ws=True, t=(0, 0, 2))

        self.orientJnts(self.guides['start'],
                        self.guides['up'],
                        self.guides['end'])

    def createJoints(self):
        """
        create joints from guide poses
        :return:
        """
        self.joints['start'] = mc.createNode(
            'transform', n=self.name + '_start_Srt', p=self.utilityGrp)
        trsLib.setTRS(self.joints['start'], self.guidePoses['start'], space='world')

        self.joints['pistonJnt'] = mc.joint(self.joints['start'], n=self.name + '_start_Jnt')
        trsLib.setTRS(self.joints['pistonJnt'], self.guidePoses['start'], space='world')
        self.setOut('pistonJnt', self.joints['start'])

        self.joints['up'] = mc.createNode(
            'transform', n=self.name + '_up_Srt', p=self.utilityGrp)
        trsLib.setTRS(self.joints['up'], self.guidePoses['up'], space='world')

        self.joints['end'] = mc.createNode(
            'transform', n=self.name + '_end_Srt', p=self.utilityGrp)
        trsLib.setTRS(self.joints['end'], self.guidePoses['end'], space='world')

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
        size = 1.0
        if self.stretch:
            dst = mc.createNode('distanceBetween', n=self.name + '_stretch_Dist')
            mc.connectAttr(self.joints['start'] + '.worldMatrix', dst + '.inMatrix1')
            mc.connectAttr(self.joints['end'] + '.worldMatrix', dst + '.inMatrix2')

            gs = attrLib.addFloat(self.utilityGrp, ln='globalScale', min=0.001, dv=1)
            gsMdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_global_scale_Mdn')
            mc.connectAttr(dst + '.distance', gsMdn + '.input1X')
            mc.connectAttr(gs, gsMdn + '.input2X')
            mc.setAttr(gsMdn + '.operation', 2)

            mdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_Mdn')
            mc.connectAttr(gsMdn + '.outputX', mdn + '.input1X')
            dist = mc.getAttr(dst + '.distance')
            mc.setAttr(mdn + '.input2X', dist)
            mc.setAttr(mdn + '.operation', 2)
            size = dist

            mc.connectAttr(mdn + '.outputX', self.joints['pistonJnt'] + '.scaleX')

            volumeMdn = mc.createNode('multiplyDivide', n=self.name + '_stretch_volume_Mdn')
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

        # create controls
        if self.createStartCtl:
            startCtl = control.Control(
                side=self.side,
                descriptor='{}_Start'.format(self.prefix),
                shape='cube',
                size=size * 1.0,
                parent=self.ctlGrp,
                matchTranslate=self.joints['start'],
                matchRotate=self.joints['pistonJnt']
            )
            mc.pointConstraint(startCtl.name, self.joints['start'])

        if self.createUpCtl:
            upCtl = control.Control(
                side=self.side,
                descriptor='{}_Up'.format(self.prefix),
                shape='cube',
                size=size * 0.2,
                parent=self.ctlGrp,
                matchTranslate=self.joints['up'],
                matchRotate=self.joints['pistonJnt']
            )
            mc.parentConstraint(upCtl.name, self.joints['up'])

        if self.createEndCtl:
            endCtl = control.Control(
                side=self.side,
                descriptor='{}_End'.format(self.prefix),
                shape='cube',
                size=size * 0.8,
                parent=self.ctlGrp,
                matchTranslate=self.joints['end'],
                matchRotate=self.joints['pistonJnt']
            )
            mc.parentConstraint(endCtl.name, self.joints['end'])

    def connect(self):
        """
        connection of created nodes
        """
        super(Piston, self).connect()

        gs = self.getOut('globalScale')
        mc.connectAttr(gs + '.globalScale', self.utilityGrp + '.globalScale')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Piston, self).createSettings()

        attrLib.addString(self.guideGrp, 'blu_globalScale', v='Ground_Gimbal_Ctrl')
        attrLib.addString(self.guideGrp, 'blu_startDriver')
        attrLib.addString(self.guideGrp, 'blu_endDriver')
