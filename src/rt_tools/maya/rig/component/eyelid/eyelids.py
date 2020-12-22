"""
import sys
path = r'D:\all_works\redtorch_tools\src'
if not path in sys.path:
    sys.path.insert(0,path)


from rt_tools.maya.rig.component.eyelid import eyelids as eyelids
reload(eyelids)
eyelid = eyelids.Eyelids(upLidHdCrv = 'localL_upLidHD_CRV',lowLidHdCrv = 'localL_lowLidHD_CRV',
                 upLidLdCrv = 'localL_upLidLD_CRV',lowLidLdCrv = 'localL_lowLidLD_CRV',lidBlinkCrv = 'localL_lidBlink_CRV',
                 upLidBlink = 'localL_upLidBlink_CRV',lowLidBlink = 'localL_lowLidBlink_CRV',
                 upCreaseHd = 'localupCreaseHD_CRV',lowCreaseHd = 'localL_lowCreaseHD_CRV',
                 upCreaseLd = 'localL_upCreaseLD_CRV',lowCreaseLd = 'localL_lowCreaseLD_CRV')
eyelid.build()

"""

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
from . import buildEyelid
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildEyelid)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Eyelids(buildEyelid.BuildEyelid):
    """
    base class for eyelids template
    """
    def __init__(self, side='L', prefix='eyeLid',upLidHdCrv = '',lowLidHdCrv = '',
                 upLidLdCrv = '',lowLidLdCrv = '',lidBlinkCrv = '',upLidBlink = '',
                 lowLidBlink = '',upCreaseHd = '',lowCreaseHd = '',upCreaseLd = '',
                 lowCreaseLd = '',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.upLidHdCrv = upLidHdCrv
        self.lowLidHdCrv = lowLidHdCrv
        self.upLidLdCrv = upLidLdCrv
        self.lowLidLdCrv = lowLidLdCrv
        self.lidBlinkCrv = lidBlinkCrv
        self.upLidBlink = upLidBlink
        self.lowLidBlink = lowLidBlink
        self.upCreaseHd = upCreaseHd
        self.upCreaseLd = upCreaseLd
        self.lowCreaseHd = lowCreaseHd
        self.lowCreaseLd = lowCreaseLd



        super(Eyelids, self).__init__(**kwargs)

    def build(self):
        super(Eyelids, self).build()
        # create wire for up and low blink curve
        for i in [self.upLidBlink ,self.lowLidBlink ]:
            mc.select(i, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.lidBlinkCrv)

        # blend shape up and low ld curves to lid blink
        mc.blendShape(self.upLidLdCrv , self.lowLidLdCrv, self.lidBlinkCrv, tc=False, automatic=True, name=self.side + '_lidBlink_BLS' )
        mc.blendShape(self.side + '_lidBlink_BLS' , edit=True, w=[(0, 0.15), (1, 0.85)])


        # connect controls to the transform above upLd eyelid joints
        [mc.connectAttr(self.upLdCtls[-1] + '.{}{}'.format(a,v), self.modUpOnJoints[-1] + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        units = []
        for i in range(2):
            unit = mc.shadingNode('unitConversion', asUtility = True )
            mc.setAttr(unit + '.conversionFactor', 2)
            units.append(unit)
        mc.connectAttr(self.upLdCtls[2] + '.tx', units[0] + '.input')
        mc.connectAttr(self.upLdCtls[2] + '.ty', units[1] + '.input')
        mc.connectAttr(units[0] + '.output', self.modUpOnJoints[3] + '.tx')
        mc.connectAttr(units[1] + '.output', self.modUpOnJoints[3] + '.ty')

        [mc.connectAttr(self.upmidCtl + '.{}{}'.format(a,v), self.modUpOnJoints[2] + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        #TODO: connect the eye aim control to the makro mid transforms later
        units = []
        for i in range(2):
            unit = mc.shadingNode('unitConversion', asUtility = True )
            mc.setAttr(unit + '.conversionFactor', 2)
            units.append(unit)
        mc.connectAttr(self.upLdCtls[1] + '.tx', units[0] + '.input')
        mc.connectAttr(self.upLdCtls[1] + '.ty', units[1] + '.input')
        mc.connectAttr(units[0] + '.output', self.modUpOnJoints[1] + '.tx')
        mc.connectAttr(units[1] + '.output', self.modUpOnJoints[1] + '.ty')

        [mc.connectAttr(self.upLdCtls[0]+ '.{}{}'.format(a,v), self.modUpOnJoints[0] + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        # connect controls to the transform above lowLd eyelid joints
        units = []
        for i in range(2):
            unit = mc.shadingNode('unitConversion', asUtility = True )
            mc.setAttr(unit + '.conversionFactor', 2)
            units.append(unit)
        mc.connectAttr(self.lowLdCtls[1] + '.tx', units[0] + '.input')
        mc.connectAttr(self.lowLdCtls[1] + '.ty', units[1] + '.input')
        mc.connectAttr(units[0] + '.output', self.modLowOnJoints[2] + '.tx')
        mc.connectAttr(units[1] + '.output', self.modLowOnJoints[2] + '.ty')

        [mc.connectAttr(self.lowmidCtl + '.{}{}'.format(a,v), self.modLowOnJoints[1] + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        #TODO: connect the eye aim control to the makro mid transforms later
        units = []
        for i in range(2):
            unit = mc.shadingNode('unitConversion', asUtility = True )
            mc.setAttr(unit + '.conversionFactor', 2)
            units.append(unit)
        mc.connectAttr(self.lowLdCtls[0] + '.tx', units[0] + '.input')
        mc.connectAttr(self.lowLdCtls[0] + '.ty', units[1] + '.input')
        mc.connectAttr(units[0] + '.output', self.modLowOnJoints[0] + '.tx')
        mc.connectAttr(units[1] + '.output', self.modLowOnJoints[0] + '.ty')

        # connect up crease controls to the modGrp above shrp jnts
        units = []
        for i in range(5):
            for k in range(3):
                unit = mc.shadingNode('unitConversion', asUtility = True )
                if i == 0:
                    mc.setAttr(unit + '.conversionFactor', 1.6)
                else:
                    mc.setAttr(unit + '.conversionFactor', 2.5)
                units.append(unit)
        for i in range(0,5):
            mc.connectAttr(self.upCreaseCtls[i] + '.tx', units[i*3] + '.input')
            mc.connectAttr(self.upCreaseCtls[i] + '.ty', units[i*3+1] + '.input')
            mc.connectAttr(self.upCreaseCtls[i] + '.tz', units[i*3+2] + '.input')
            mc.connectAttr(units[i*3] + '.output', self.modUpCreaseOnJoints[i] + '.tx')
            mc.connectAttr(units[i*3+1] + '.output', self.modUpCreaseOnJoints[i] + '.ty')
            mc.connectAttr(units[i*3+2] + '.output', self.modUpCreaseOnJoints[i] + '.tz')

        #connect stuf to the makro above middle up shrp joint
        default = 1
        for i in [self.upmidCtl,self.lowmidCtl]:
            attrLib.addFloat(i, ln = 'creaseFollow',min = 0,max = 1, dv = default)
            default = 0.5

        self.upCreaseMakroMult = mc.createNode('multiplyDivide', name = self.side + '_upCreaseMAKRO_activate_MDN')
        mc.connectAttr(self.upCreaseMakroLoc + '.translate', self.upCreaseMakroMult + '.input1')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.connectAttr(self.upmidCtl + '.creaseFollow', self.upCreaseMakroMult + '.' + i)
        mc.connectAttr(self.upCreaseMakroMult + '.output', self.makroCreaseUpJntGrp + '.translate')



        # connect low crease controls to the modGrp above shrp jnts
        units = []
        for i in range(3):
            for k in range(3):
                unit = mc.shadingNode('unitConversion', asUtility = True )
                if i == 0:
                    mc.setAttr(unit + '.conversionFactor', 1.6)
                else:
                    mc.setAttr(unit + '.conversionFactor', 2.5)
                units.append(unit)
        for i in range(0,3):
            mc.connectAttr(self.lowCreaseCtls[i] + '.tx', units[i*3] + '.input')
            mc.connectAttr(self.lowCreaseCtls[i] + '.ty', units[i*3+1] + '.input')
            mc.connectAttr(self.lowCreaseCtls[i] + '.tz', units[i*3+2] + '.input')
            mc.connectAttr(units[i*3] + '.output', self.modLowCreaseOnJoints[i] + '.tx')
            mc.connectAttr(units[i*3+1] + '.output', self.modLowCreaseOnJoints[i] + '.ty')
            mc.connectAttr(units[i*3+2] + '.output', self.modLowCreaseOnJoints[i] + '.tz')

        #connect stuf to the makro above middle low shrp joint
        self.lowCreaseMakroMult = mc.createNode('multiplyDivide', name = self.side + '_lowCreaseMAKRO_activate_MDN')
        mc.connectAttr(self.lowCreaseMakroLoc + '.translate', self.lowCreaseMakroMult + '.input1')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.connectAttr(self.lowmidCtl + '.creaseFollow', self.lowCreaseMakroMult + '.' + i)
        mc.connectAttr(self.lowCreaseMakroMult + '.output', self.makroCreaseLowJntGrp + '.translate')

        # create wire for up and low Crease curve
        for i,j in zip([self.upCreaseLd ,self.lowCreaseLd],[self.upCreaseHd ,self.lowCreaseHd]):
            mc.select(j, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= i)

        # connect stuf to the cheekRaise under placement
        #TODO: connect cheek control to the stuf later

        # connect stuf to the locators under lid makro loc
        mc.pointConstraint(self.upEyelidBndJnts[6],self.upLidMakroLoc,mo = True)
        mc.pointConstraint(self.lowEyelidBndJnts[6],self.lowLidMakroLoc,mo = True)

        mc.pointConstraint(self.browMidMakroLoc, self.upCreaseMakroLoc, mo = True)

        mc.pointConstraint(self.lowLidMakroLoc,self.cheekRaiseMakro, self.lowCreaseMakroLoc, mo = True)

        mc.pointConstraint(self.browMidMakroDrvrLoc, self.browMidMakroLoc, mo = True)
        mc.pointConstraint(self.cheeckJoints[-1], self.cheekRaiseMakro, mo = True)

        # connect stuff to the groups under browMakro locGrp
        mc.pointConstraint(self.browOutLoc,self.browInLoc,self.browMidMakroDrvrOriGrp, mo = True)

        #TODO: connect eyebrow  controls to the brow  locs  under brow makro loc later

        # connect controls to the neighbor transform above controls
        mc.parentConstraint(self.upmidCtl,self.upLdCtls[0],self.upLdCtlGrps[1],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.upmidCtl,self.upLdCtls[-1],self.upLdCtlGrps[2],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowmidCtl,self.upLdCtls[0],self.lowLdCtlGrps[0],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowmidCtl,self.upLdCtls[-1],self.lowLdCtlGrps[1],weight = 0.5 ,mo = True)

        #TODO: connect stuf to the makro group above mid eyelid ctls later

        # connect controls to the neighbor transform above crease controls
        mc.parentConstraint(self.upCreaseCtls[0],self.upCreaseCtls[2],self.upCreaseLdCtlGrps[1],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.upCreaseCtls[2],self.upCreaseCtls[-1],self.upCreaseLdCtlGrps[3],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowCreaseCtls[1],self.upCreaseCtls[0],self.lowCreaseLdCtlGrps[0],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowCreaseCtls[1],self.upCreaseCtls[-1],self.lowCreaseLdCtlGrps[2],skipRotate='x',weight = 0.5 ,mo = True)











        # clean outliner
        # for i in [self.upLidHdCrv,self.upLidLdCrv,self.upLidBlink,
        #           self.lowLidHdCrv,self.lowLidLdCrv,self.lowLidBlink,self.lidBlinkCrv,self.tempCurve,
        #           'localL_lidBlink_CRVBaseWire','localL_lidBlink_CRVBaseWire1']:
        #     mc.parent(i,self.eyelidCrvGrp)
        #
        # for i in [self.upCreaseHd,self.lowCreaseHd,self.upCreaseLd,self.lowCreaseLd]:
        #     mc.parent(i,self.eyeCreaseCrvGrp)

