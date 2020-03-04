"""
name: spine.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import trsLib
from ...lib import crvLib
from ...lib import jntLib
from ...lib import connect
from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import display
from ..command import rope
from . import template

reload(trsLib)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(control)
reload(strLib)
reload(attrLib)
reload(display)
reload(rope)
reload(template)


class Spine(template.Template):
    """
    class for creating spine rig for biped characters
    """

    def __init__(self, side='C', prefix='spine', numOfFK=2, numOfJnts=6, quad=False, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numOfFK = numOfFK
        self.numOfJnts = numOfJnts
        self.quad = quad

        super(Spine, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Spine, self).createBlueprint()

        # add blueprint attrs
        # this data will be used to initialize the class later
        self.blueprints['start'] = '{}_start_BLU'.format(self.name)
        self.blueprints['mid'] = '{}_mid_BLU'.format(self.name)
        self.blueprints['end'] = '{}_end_BLU'.format(self.name)
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

        # create input blueprints
        if not mc.objExists(self.blueprints['start']):
            mc.joint(self.blueprintGrp, name=self.blueprints['start'])
            mc.xform(self.blueprints['start'], ws=True, t=(0, 10.5, 0))
        if not mc.objExists(self.blueprints['mid']):
            mc.joint(self.blueprintGrp, name=self.blueprints['mid'])
            mc.xform(self.blueprints['mid'], ws=True, t=(0, 13, 0))
        if not mc.objExists(self.blueprints['end']):
            mc.joint(self.blueprintGrp, name=self.blueprints['end'])
            mc.xform(self.blueprints['end'], ws=True, t=(0, 16, 0))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        moduleGrp = self.name + '_module_GRP'

        blueprints = self.blueprints['start'], self.blueprints['mid'], self.blueprints['end']
        crv = crvLib.fromJnts(jnts=blueprints, degree=1, fit=False)[0]
        mc.rebuildCurve(crv, degree=3, spans=2)

        # create spine base joint and move it a bit lower than first spine joint
        # to avoid skin mirroring issues when joints are on top of each other
        self.joints['baseJnt'] = mc.joint(moduleGrp, n=self.name + '_base_JNT')
        trsLib.setTRS(self.joints['baseJnt'], self.blueprintPoses['start'], space='world')
        mc.move(0, -0.01, 0, self.joints['baseJnt'], ws=True, r=True)

        # create other spine joints
        self.joints['spineJnts'] = []
        jnts = jntLib.create_on_curve(curve=crv, numOfJoints=self.numOfJnts, parent=True)
        mc.parent(jnts[0], self.joints['baseJnt'])
        for i in range(self.numOfJnts):
            jnt = '{}_{:02d}_JNT'.format(self.name, i+1)
            jnt = mc.rename(jnts[i], jnt)
            self.joints['spineJnts'].append(jnt)


        mc.delete(crv)

    def build(self):
        super(Spine, self).build()

        self.baseCtl, crvGrp, rsltGrp, ctls = rope.run(
            jnts=self.joints['spineJnts'], numCtls=5, guides=None, numJnts=None,
            addSpaces=False, description=self.prefix)

        iconSize = trsLib.getDistance(self.joints['spineJnts'][0], self.joints['spineJnts'][-1])

        # fk ctl
        lastFk = self.ctlGrp
        self.ctls = {'fkCtls': []}
        for i in xrange(self.numOfFK):
            ctl = control.Control(descriptor='{}_fk_{}'.format(self.prefix, i + 1),
                                  side=self.side,
                                  color='cyan',
                                  orient=[0, 1, 0],
                                  scale=[iconSize * 1.3] * 3,
                                  lockHideAttrs=['s', 'v'],
                                  parent=lastFk)
            pos = 1.0 / (self.numOfFK + 1) * (i + 1)

            cns = connect.weightConstraint(self.joints['spineJnts'][0],
                                           self.joints['spineJnts'][-1],
                                           ctl.zro,
                                           type='pointConstraint',
                                           weights=[1 - pos, pos])
            mc.delete(cns)
            lastFk = ctl.name
            self.ctls['fkCtls'].append(ctl.name)

        # set controls names, shapes, colors, etc
        # hip and chest control properties
        orient = [1, 0, 0]
        if self.quad:
            orient = [0, 0, 1]
        hipCtl = mc.rename(ctls[0], self.name + '_hip_CTL')
        crvLib.orientShape(hipCtl, orient)
        crvLib.editShape(hipCtl, shape='cube')
        display.setColor(hipCtl, 'yellow')
        crvLib.scaleShape(hipCtl, [iconSize, iconSize * 0.2, iconSize])
        attrLib.lockHideAttrs(hipCtl, attrs=['s', 'v'])
        self.setOut('hipCtl', hipCtl)
        hipZro = hipCtl.replace('CTL', 'ZRO')
        mc.rename(mc.listRelatives(hipCtl, p=1)[0], hipZro)

        chestCtl = mc.rename(ctls[-1], self.name + '_chest_CTL')
        crvLib.orientShape(chestCtl, orient)
        crvLib.editShape(chestCtl, shape='cube')
        display.setColor(chestCtl, 'yellow')
        crvLib.scaleShape(chestCtl, [iconSize, iconSize * 0.2, iconSize])
        attrLib.lockHideAttrs(chestCtl, attrs=['s', 'v'])
        self.setOut('chestCtl', chestCtl)
        chestZro = chestCtl.replace('CTL', 'ZRO')
        chestZro = mc.rename(mc.listRelatives(chestCtl, p=1)[0], chestZro)
        mc.parent(chestZro, lastFk)

        # mid control properties
        orient = [0, 1, 0]
        if self.quad:
            orient = [0, 0, 1]
        midCtl = mc.rename(ctls[2], self.name + '_mid_CTL')
        crvLib.orientShape(midCtl, orient)
        crvLib.editShape(midCtl, shape='circle')
        display.setColor(midCtl, 'redDark')
        crvLib.scaleShape(midCtl, [iconSize, iconSize , iconSize])
        attrLib.lockHideAttrs(midCtl, attrs=['s', 'v'])
        self.setOut('midCtl', midCtl)
        midZro = midCtl.replace('CTL', 'ZRO')
        midZro = mc.rename(mc.listRelatives(midCtl, p=1)[0], midZro)

        # keep mid control between hip and chest
        n = midZro + '_POC'
        mc.parentConstraint(chestCtl, hipCtl, midZro, mo=True, name=n)

        # hip and chest tanget control properties
        hipTanCtl = mc.rename(ctls[1], self.name + '_hipTangent_CTL')
        attrLib.lockHideAttrs(hipTanCtl, attrs=['s', 'v'])
        self.setOut('hipTanCtl', hipTanCtl)
        hipTanZro = hipTanCtl.replace('CTL', 'ZRO')
        hipTanZro = mc.rename(mc.listRelatives(hipTanCtl, p=1)[0], hipTanZro)
        mc.parent(hipTanZro, hipCtl)

        tanVisAt = attrLib.addEnum(hipCtl, 'tangentCtlVis', en=['OFF', 'ON'])
        attrLib.connectAttr(tanVisAt, hipTanZro+'.v')

        connect.blendConstraint(
            hipCtl, midCtl, hipTanZro, mo=True, blendNode=hipTanCtl,
            blendAttr='followMid', type='parentConstraint')
        mc.setAttr(hipTanCtl+'.followMid', 0.5)

        chestTanCtl = mc.rename(ctls[-2], self.name + '_chestTangent_CTL')
        attrLib.lockHideAttrs(chestTanCtl, attrs=['s', 'v'])
        self.setOut('chestTanCtl', chestTanCtl)
        chestTanZro = chestTanCtl.replace('CTL', 'ZRO')
        chestTanZro = mc.rename(mc.listRelatives(chestTanCtl, p=1)[0], chestTanZro)
        mc.parent(chestTanZro, chestCtl)

        tanVisAt = attrLib.addEnum(chestCtl, 'tangentCtlVis', en=['OFF', 'ON'])
        attrLib.connectAttr(tanVisAt, chestTanZro+'.v')

        connect.blendConstraint(
            chestCtl, midCtl, chestTanZro, mo=True, blendNode=chestTanCtl,
            blendAttr='followMid', type='parentConstraint')
        mc.setAttr(chestTanCtl+'.followMid', 0.5)

        # drive base joint
        firstJntDrvr = mc.parentConstraint(self.joints['spineJnts'][0], q=True, targetList=True)[0]
        mc.parentConstraint(firstJntDrvr, self.joints['baseJnt'],
                            mo=True, sr=('x', 'y', 'z'))
        mc.parentConstraint(hipCtl, self.joints['baseJnt'],
                            mo=True, st=('x', 'y', 'z'))

        # pevlis jnt
        guessed = 'C_pelvis_JNT'
        self.hipJnt = mc.ls(guessed)
        if self.hipJnt:
            self.hipJnt = self.hipJnt[0]
            self.setOut('hipJnt', self.hipJnt)

        # use child of last jnt as chest jnt
        chestJnt = self.joints['spineJnts'][-1]
        [attrLib.disconnectAttr(chestJnt + '.' + a) for a in ('r', 'rx', 'ry', 'rz')]
        mc.orientConstraint(chestCtl, chestJnt, mo=True, name=chestJnt + '_ORI')
        self.setOut('chestJnt', chestJnt)

        # outliner clean up
        mc.parent(crvGrp, rsltGrp, self.originGrp)

    def connect(self):
        """
        connection of created nodes
        """
        super(Spine, self).connect()

        # get handle to outputs
        ctlParent = self.getOut('ctlParent')

        # outliner clean up
        connect.matrix(ctlParent, self.moduleGrp)
        connect.matrix(ctlParent, self.ctlGrp)

        baseChildren = mc.listRelatives(self.baseCtl, type='transform')
        mc.parent(baseChildren, ctlParent)
        firstFkZro = trsLib.getParent(self.ctls['fkCtls'][0])
        mc.parent(firstFkZro, ctlParent)
        baseCtlZro = mc.listRelatives(self.baseCtl, p=1)[0]
        mc.delete(baseCtlZro)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Spine, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_root.bodyCtl')
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts or 6)
        attrLib.addInt(self.blueprintGrp, 'blu_numOfFK', v=self.numOfFK or 3)
