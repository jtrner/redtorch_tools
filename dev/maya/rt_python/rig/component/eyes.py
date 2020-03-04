"""
name: eyes.py

Author: Ehsan Hassani Moghaddam

History:
    05/13/17 (ehassani)    first release!

"""
import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import control
from ...lib import connect
from ...lib import strLib
from ...lib import space
from . import template

reload(trsLib)
reload(attrLib)
reload(control)
reload(connect)
reload(strLib)
reload(space)
reload(template)


class Eyes(template.Template):
    """Class for creating eyes"""

    def __init__(self, side='C', prefix='eyes', eyeAimCtls=[], **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.eyeAimCtls = eyeAimCtls
        super(Eyes, self).__init__(**kwargs)

    def build(self):
        """
        building necessary nodes
        """
        super(Eyes, self).build()

        # estimate icon size based on eyes distance
        self.eyeAimCtls = self.getOut('eyeAimCtls')
        print self.eyeAimCtls
        iconSize = 1
        pos = mc.xform(self.eyeAimCtls[0], q=True, ws=True, t=True)
        if len(self.eyeAimCtls) > 1:
            iconSize = trsLib.getDistance(self.eyeAimCtls[0], self.eyeAimCtls[-1])
            pos = trsLib.getPoseBetween(self.eyeAimCtls[0], self.eyeAimCtls[-1])

        # add controls
        self.eyesCtl = control.Control(
            descriptor=self.prefix + 'master',
            side=self.side,
            parent=self.ctlGrp,
            shape="square",
            translate=pos,
            rotateShape=[90, 0, 0],
            scale=[iconSize * 2, iconSize * 2, iconSize / 1.5],
            verbose=self.verbose).name
        for x in self.eyeAimCtls:
            xZero = x.replace('CTL', 'ZRO')
            connect.matrix(self.eyesCtl, xZero)

        # keep in asset node for later use
        self.setOut('eyesCtl', self.eyesCtl)

    def connect(self):
        """
        connection of created nodes 
        """
        super(Eyes, self).connect()

        # attach controls
        headCtl = self.getOut('globalScale')
        if headCtl:
            connect.matrix(headCtl, self.moduleGrp)
            connect.matrix(headCtl, self.ctlGrp)

        # fk orient space
        parentDrivers = self.getOut('space')
        if parentDrivers:
            eyesZero = self.eyesCtl.replace('CTL', 'ZRO')
            space.parent(
                drivers=parentDrivers,
                drivens=[eyesZero],
                control=self.eyesCtl,
                name=self.name + 'ParentSpace',
            )

        # vis switch
        attrLib.addSeparator(self.eyesCtl, 'settings')
        a = attrLib.addEnum(self.eyesCtl, 'ikVis', en=['off', 'on'], dv=1)
        b = attrLib.addEnum(self.eyesCtl, 'fkVis', en=['off', 'on'])
        for ik in self.eyeAimCtls:
            ikZro = ik.replace('aim_CTL', 'aim_ZRO')
            fkZro = ik.replace('aim_CTL', 'ball_ZRO')
            mc.connectAttr(a, ikZro + '.v')
            mc.connectAttr(b, fkZro + '.v')

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Eyes, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale',
                          v='C_root.mainCtl')
        attrLib.addString(self.blueprintGrp, 'blu_eyeAimCtls',
                          v=['L_eye.eyeAimCtl', 'R_eye.eyeAimCtl'])
        attrLib.addString(self.blueprintGrp, 'blu_space',
                          v={'drivers': ['C_neck.headCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
