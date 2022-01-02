"""
name: eyeB.py

Author: Ehsan Hassani Moghaddam

History:
    05/13/17 (ehassani)    first release!

"""
import re

import maya.cmds as mc

from ...lib import trsLib
from ...lib import jntLib
from ...lib import attrLib
from ...lib import control
from ...lib import connect
from ...lib import strLib
from . import template

reload(trsLib)
reload(jntLib)
reload(attrLib)
reload(control)
reload(connect)
reload(strLib)
reload(template)


class Eye(template.Template):
    """Class for creating eye"""
    
    def __init__(self, side='L', prefix='eye', eyeJnt='', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.eyeJnt = eyeJnt
        super(Eye, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Eye, self).createBlueprint()

        # create input blueprints
        mult = [-1, 1][self.side == 'L']

        self.blueprints['ball'] = '{}_ball_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['ball']):
            mc.joint(self.blueprintGrp, name=self.blueprints['ball'])
            mc.xform(self.blueprints['ball'], ws=True, t=(mult, 20, 1))

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        # create joints
        self.joints['ball'] = '{}_ball_JNT'.format(self.name)
        mc.joint(self.moduleGrp, n=self.joints['ball'])
        trsLib.setTRS(self.joints['ball'], self.blueprintPoses['ball'], space='world')

        self.setOut('joints', str(self.joints))

    def build(self):
        """
        building necessary nodes
        """
        super(Eye, self).build()

        # set outputs
        self.setOut('jnt', self.joints['ball'])

        # estimate icon size based on eye and its parent (head joint)
        pos = self.blueprintPoses['ball'][0]
        iconSize = trsLib.getDistanceFromPoses(posA=[0, 0, 0], posB=pos) * 0.06

        # add controls
        self.eyeCtl = control.Control(
                                 descriptor=self.prefix + '_ball',
                                 side=self.side,
                                 parent=self.ctlGrp,
                                 shape="arrow",
                                 rotateShape=[90, 0, 0],
                                 scale=[iconSize, iconSize, iconSize],
                                 matchTranslate=self.joints['ball'],
                                 verbose=self.verbose
                                ).name
        connect.matrix(self.eyeCtl, self.joints['ball'])

        # keep in asset node for later use
        self.setOut('eyeCtl', self.eyeCtl)

        # add controls
        pos = [pos[0], pos[1], pos[2]+iconSize*5]
        self.eyeAimCtl = control.Control(
                                    descriptor=self.prefix + '_aim',
                                    side=self.side,
                                    parent=self.ctlGrp,
                                    translate=pos,
                                    rotateShape=[90, 0, 0],
                                    scale=[iconSize/2, iconSize/2, iconSize/2],
                                    matchTranslate=self.joints['ball'],
                                    verbose=self.verbose)

        # keep in asset node for later use
        self.setOut('eyeAimCtl', self.eyeAimCtl.name)

    def connect(self):
        """
        connection of created nodes 
        """
        super(Eye, self).connect()
        
        # attach controls
        ctlParent = self.getOut('ctlParent')
        if ctlParent:
            connect.matrix(ctlParent, self.moduleGrp)
            connect.matrix(ctlParent, self.ctlGrp)
        else:
            mc.warning('eye -> Can\'t parent controls!')

        # aim ctl setup
        eyeZero = self.eyeCtl.replace('CTL', 'ZRO')
        mc.aimConstraint(
                         self.eyeAimCtl.name,
                         eyeZero,
                         wuo=self.ctlGrp,
                         aim=[0, 0, 1],
                         u=[0, 1, 0],
                         wu=[0, 1, 0],
                        )

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Eye, self).createSettings()
        
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_neck.headJnt')
