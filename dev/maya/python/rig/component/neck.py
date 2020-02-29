"""
name: neck.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import control
from ...lib import trsLib
from ...lib import crvLib
from ...lib import connect
from ...lib import strLib
from ...lib import attrLib
from ...lib import display
from ...lib import space
from ...lib import jntLib
from ..command import rope
from . import template

reload(control)
reload(trsLib)
reload(crvLib)
reload(connect)
reload(strLib)
reload(attrLib)
reload(display)
reload(space)
reload(jntLib)
reload(rope)
reload(template)


class Neck(template.Template):
    """
    class for creating neck rig for biped characters
    """

    def __init__(self, side='C', prefix='neck', numOfJnts=4, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numOfJnts = numOfJnts

        super(Neck, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Neck, self).createBlueprint()

        # add blueprint attrs
        # this data will be used to initialize the class later
        self.blueprints['start'] = '{}_start_BLU'.format(self.name)
        self.blueprints['mid'] = '{}_mid_BLU'.format(self.name)
        self.blueprints['end'] = '{}_end_BLU'.format(self.name)
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

        # create input blueprints
        if not mc.objExists(self.blueprints['start']):
            mc.joint(self.blueprintGrp, name=self.blueprints['start'])
            mc.xform(self.blueprints['start'], ws=True, t=(0, 16.5, 0))
        if not mc.objExists(self.blueprints['mid']):
            mc.joint(self.blueprintGrp, name=self.blueprints['mid'])
            mc.xform(self.blueprints['mid'], ws=True, t=(0, 17, 0))
        if not mc.objExists(self.blueprints['end']):
            mc.joint(self.blueprintGrp, name=self.blueprints['end'])
            mc.xform(self.blueprints['end'], ws=True, t=(0, 17.5, 0))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """

        blueprints = self.blueprints['start'], self.blueprints['mid'], self.blueprints['end']
        crv = crvLib.fromJnts(jnts=blueprints, degree=1, fit=False)[0]
        mc.rebuildCurve(crv, degree=3, spans=2)

        self.joints['neckJnts'] = []
        jnts = jntLib.create_on_curve(curve=crv, numOfJoints=self.numOfJnts, parent=True)
        mc.parent(jnts[0], self.moduleGrp)
        for i in range(self.numOfJnts):
            jnt = '{}_{:02d}_JNT'.format(self.name, i+1)
            jnt = mc.rename(jnts[i], jnt)
            self.joints['neckJnts'].append(jnt)

        mc.delete(crv)

    def build(self):
        super(Neck, self).build()

        self.baseCtl, crvGrp, rsltGrp, ctls = rope.run(
            jnts=self.joints['neckJnts'], numCtls=5, guides=None, numJnts=None,
            addSpaces=False, description='neck')

        iconSize = trsLib.getDistance(self.joints['neckJnts'][0], self.joints['neckJnts'][-1])

        # baseCtl properties
        crvLib.scaleShape(self.baseCtl, [iconSize * 0.5]*3)
        self.setOut('baseCtl', self.baseCtl)

        # neckStart control properties
        self.startCtl = mc.rename(ctls[0], ctls[0].replace('CTL', 'GRP'))
        startCtlS = crvLib.getShapes(self.startCtl)
        mc.delete(startCtlS)
        attrLib.lockHideAttrs(self.startCtl, attrs=['t', 'r', 's', 'v'])
        self.setOut('startCtl', self.startCtl)
        neckStartZro = self.name + '_neckStartGrp_ZRO'
        mc.rename(mc.listRelatives(self.startCtl, p=1)[0], neckStartZro)


        # end control properties
        self.endCtl = mc.rename(ctls[-1], self.name + '_end_CTL')
        crvLib.orientShape(self.endCtl, [1, 0, 0])
        crvLib.editShape(self.endCtl, shape='cube')
        display.setColor(self.endCtl, 'yellow')
        crvLib.scaleShape(self.endCtl, [iconSize, iconSize * 0.2, iconSize])
        attrLib.lockHideAttrs(self.endCtl, attrs=['s', 'v'])
        self.setOut('endCtl', self.endCtl)
        endZro = self.endCtl.replace('CTL', 'ZRO')
        mc.rename(mc.listRelatives(self.endCtl, p=1)[0], endZro)

        # mid control properties
        midCtl = mc.rename(ctls[2], self.name + '_mid_CTL')
        crvLib.orientShape(midCtl, [0, 1, 0])
        crvLib.editShape(midCtl, shape='circle')
        display.setColor(midCtl, 'redDark')
        crvLib.scaleShape(midCtl, [iconSize, iconSize, iconSize])
        attrLib.lockHideAttrs(midCtl, attrs=['s', 'v'])
        self.setOut('midCtl', midCtl)
        midZro = midCtl.replace('CTL', 'ZRO')
        midZro = mc.rename(mc.listRelatives(midCtl, p=1)[0], midZro)

        connect.pointAim(start=self.startCtl, end=self.endCtl, driven=midZro, addAttrTo=midCtl)

        # neckStart and end tanget control properties
        neckStartTanCtl = mc.rename(ctls[1], self.name + '_start_tangent_CTL')
        attrLib.lockHideAttrs(neckStartTanCtl, attrs=['s', 'v'])
        self.setOut('neckStartTanCtl', neckStartTanCtl)
        neckStartTanZro = mc.rename(mc.listRelatives(neckStartTanCtl, p=1)[0],
                                    neckStartTanCtl.replace('CTL', 'ZRO'))
        mc.parent(neckStartTanZro, self.startCtl)

        connect.pointAim(start=self.startCtl, end=midCtl, driven=neckStartTanZro, addAttrTo=neckStartTanCtl)

        endTanCtl = mc.rename(ctls[-2], self.name + '_end_tangent_CTL')
        attrLib.lockHideAttrs(endTanCtl, attrs=['s', 'v'])
        self.setOut('endTanCtl', endTanCtl)
        endTanZro = mc.rename(mc.listRelatives(endTanCtl, p=1)[0],
                                  endTanCtl.replace('CTL', 'ZRO'))
        mc.parent(endTanZro, self.endCtl)

        tanVisAt = attrLib.addEnum(self.endCtl, 'tangentCtlVis', en=['OFF', 'ON'])
        attrLib.connectAttr(tanVisAt, neckStartTanZro + '.v')
        attrLib.connectAttr(tanVisAt, endTanZro + '.v')

        connect.pointAim(start=self.endCtl, end=midCtl, driven=endTanZro, addAttrTo=endTanCtl)

        # head control
        self.headCtl = control.Control(
            descriptor=self.prefix + '_head',
            side=self.side,
            parent=self.endCtl,
            shape='circle',
            color='cyan',
            scale=[iconSize * 2, iconSize * 2, iconSize * 2],
            matchTranslate=self.joints['neckJnts'][-1],
            lockHideAttrs=['t', 's', 'v'],
            verbose=self.verbose
        ).name
        self.setOut('headCtl', self.headCtl)

        # use child of last jnt as head jnt
        headJnt = self.joints['neckJnts'][-1]
        cns = headJnt + '_ORI'
        [attrLib.disconnectAttr(headJnt + '.r' + x) for x in 'xyz']
        mc.orientConstraint(self.headCtl, headJnt, mo=True, name=cns)
        self.setOut('headJnt', headJnt)

        # outliner clean up
        mc.parent(crvGrp, rsltGrp, self.originGrp)
        ctlParent = self.getOut('ctlParent')
        startCtlZro = mc.listRelatives(self.baseCtl, p=1)[0]
        mc.parent(startCtlZro, ctlParent)

    def connect(self):
        """
        connection of created nodes
        """
        super(Neck, self).connect()

        # outliner clean up
        ctlParent = self.getOut('ctlParent')
        connect.matrix(ctlParent, self.moduleGrp)
        connect.matrix(ctlParent, self.ctlGrp)

        # head orient space
        orientDrivers = self.getOut('headOrient')
        if orientDrivers:
            headZero = self.headCtl.replace('CTL', 'ZRO')
            space.orient(
                drivers=orientDrivers,
                drivens=[headZero],
                control=self.headCtl,
                name=self.name + 'OrientSpace',
            )
        else:
            mc.warning('neck -> Can\'t orientConstraint Head!')

        # neck start orient space
        orientDrivers = self.getOut('neckStartOrient')
        if orientDrivers:
            neckZero = self.baseCtl.replace('CTL', 'ZRO')
            space.orient(
                drivers=orientDrivers,
                drivens=[neckZero],
                control=self.startCtl,
                name=self.name + 'OrientSpace',
            )
        else:
            mc.warning('neck -> Can\'t orientConstraint Neck Start!')

        # neck end point space
        endPointDrivers = self.getOut('endPoint')
        if orientDrivers:
            endZero = self.endCtl.replace('CTL', 'ZRO')
            space.point(
                drivers=endPointDrivers,
                drivens=[endZero],
                control=self.endCtl,
                name=self.name + 'PointSpace',
            )
        else:
            mc.warning('neck -> Can\'t pointConstraint Neck End!')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Neck, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_spine.chestCtl')
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts or 6)

        attrLib.addString(self.blueprintGrp, 'blu_neckStartOrient',
                          v={'drivers': ['C_spine.chestCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 2})

        attrLib.addString(self.blueprintGrp, 'blu_endPoint',
                          v={'drivers': [self.name + '.startCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})

        attrLib.addString(self.blueprintGrp, 'blu_headOrient',
                          v={'drivers': [self.name + '.endCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
