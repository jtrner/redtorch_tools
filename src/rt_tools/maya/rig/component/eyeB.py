
import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib
from ...lib import deformLib
from ...lib import keyLib
from ...lib import jntLib
from ...lib import connect
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


class EyeB(buildEye.BuildEye):
    """
    base class for eye template
    """
    def __init__(self, side='L', prefix='eye', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix


        super(EyeB, self).__init__(**kwargs)

    def build(self):
        super(EyeB, self).build()
        # connect stuf to the eyeMaster aim drvr socketMod grp
        [mc.connectAttr(self.squashCtl + '.{}{}'.format(a,v), self.socketModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']

        # aim stuf to the eyeMaster aim driver loc
        attrLib.addFloat(self.aimCtl, ln = 'aim', min = 0,max = 1,dv = 1)
        attrLib.addFloat(self.aimCtl, ln = 'fleshyEyes', min = 0,max = 1,dv = 1)

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


        # aim constraint eye iris ctl to the eyeMasterJntOriGrp
        mc.aimConstraint(self.irisCtl,self.eyeMasterJntOriGrp,  aimVector=[0,0,1],
                         upVector=[0, 1, 0], worldUpType="object",
                         worldUpObject=self.eyeMasterAimUpVecLoc, mo = True)[0]
        # connect Z attr of eyeris ctl to the eye pupil joint
        mc.connectAttr(self.irisCtl + '.z', self.eyeJoints[2] + '.translateZ')


    def connect(self):
        super(EyeB, self).connect()

        if self.side == 'R':
            rigPar = self.getOut('rigParent')
            if rigPar:
                mc.parent(self.eyeRigGrp, rigPar)


            aimPar = self.getOut('aimParent')
            if aimPar:
                mc.parent(self.eyeAimCtlOriGrp, aimPar)

        if self.side == 'L':
            l_eyeSocketJntModGrp = self.getOut('l_eyeSocketJntModGrp')
            if l_eyeSocketJntModGrp:
                [mc.connectAttr(self.squashCtl + '.{}{}'.format(a, v), l_eyeSocketJntModGrp + '.{}{}'.format(a, v)) for a in 'trs' for v in 'xyz']

        else:
            r_eyeSocketJntModGrp = self.getOut('r_eyeSocketJntModGrp')
            if r_eyeSocketJntModGrp:
                [mc.connectAttr(self.squashCtl + '.{}{}'.format(a, v), r_eyeSocketJntModGrp + '.{}{}'.format(a, v)) for a in 'trs' for v in 'xyz']

        eyelidSocketGrp = self.getOut('eyelidSocketGrp')
        if eyelidSocketGrp:
            [mc.connectAttr(self.squashCtl + '.{}{}'.format(a, v), eyelidSocketGrp + '.{}{}'.format(a, v)) for a in 'trs' for v in 'xyz']

        # add attr on squash ctl
        attrLib.addFloat(self.squashCtl, ln = 'blink', min = 0, max = 10, dv = 0)
        attrLib.addFloat(self.squashCtl, ln = 'blinkHeight', min = 0, max = 10, dv = 1.5)





    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(EyeB, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_rigParent', v='C_head.topSquashFirst')
        attrLib.addString(self.blueprintGrp, 'blu_aimParent', v='C_head.facialCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_l_eyeSocketJntModGrp', v='C_head.l_eyeSocketJntModGrp')
        attrLib.addString(self.blueprintGrp, 'blu_r_eyeSocketJntModGrp', v='C_head.r_eyeSocketJntModGrp')
        attrLib.addString(self.blueprintGrp, 'blu_eyelidSocketGrp', v=self.side + '_eyelid.eyelidSocketGrp')











