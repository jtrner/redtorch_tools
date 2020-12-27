
import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from ....lib import deformLib
from ....lib import keyLib
from ....lib import jntLib
from ....lib import connect
from . import buildEye
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildEye)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Eye(buildEye.BuildEye):
    """
    base class for eye template
    """
    def __init__(self, side='L', prefix='eye', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix


        super(Eye, self).__init__(**kwargs)

    def build(self):
        super(Eye, self).build()
        # connect stuf to the eyeMaster aim drvr socketMod grp
        self.squashCtl,self.socketModGrp
        [mc.connectAttr(self.squashCtl + '.{}{}'.format(a,v), self.socketModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']

        # aim stuf to the eyeMaster aim driver loc
        attrLib.addFloat(self.aimCtl, ln = 'aim', min = 0,max = 1,dv = 1)

        aimCons = mc.aimConstraint([self.eyeMasterAimTargetLoc,self.eyeMasterAimOffTargetLoc ], self.eyeMasterAimDrvrLoc, aimVector=[0,0,1],
                         upVector=[0, 1, 0], worldUpType="object",
                         worldUpObject=self.eyeMasterAimUpVecLoc, mo = True)[0]

        mc.connectAttr(self.aimCtl + '.aim', aimCons + '.' + '{}'.format(self.eyeMasterAimTargetLoc) + 'W0')
        revNode = mc.createNode('reverse', name = 'aim_REN')
        mc.connectAttr(self.aimCtl + '.aim', revNode + '.inputX')
        mc.connectAttr(revNode + '.outputX', aimCons + '.' + '{}'.format(self.eyeMasterAimOffTargetLoc) + 'W1')

        # connect stuf to the irisJntModGrp
        attrLib.addFloat(self.irisCtl, ln = 'z', dv = 0)
        for i, j in zip(['scale', 'z'],['scale', 'translateZ']):
            mc.connectAttr(self.irisCtl + '.' + i,self.irisJntModGrp + '.' + j)

        self.pupilCtlGrp = self.pupilCtlGrp.split('|')[-1]
        [mc.connectAttr(self.irisCtl + '.{}{}'.format(a,v), self.pupilCtlGrp + '.{}{}'.format(a,v))for a in 's'for v in 'xyz']

        # connect master eye joint to the eyeMasterMakro locator
        mc.orientConstraint(self.eyeJoints[0],self.eyeMasterMakroLoc, mo = True)








