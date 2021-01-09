
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
    def __init__(self,movement = 40, eyelidsGeo ='', side='L', prefix='eyelid', upLidHdEdge ='', lowLidHdEdge ='',
                 upLidLdEdge = '', lowLidLdEdge = '', lidBlinkEdge = '', uplidBlinkEdge = '',
                 lowlidBlinkEdge = '', upCreaseHdEdge = '', lowCreaseHdEdge = '', upCreaseLdEdge = '',
                 lowCreaseLdEdge = '', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.movement = movement
        self.eyelidsGeo = eyelidsGeo
        self.upLidHdEdge = upLidHdEdge
        self.lowLidHdEdge = lowLidHdEdge
        self.upLidLdEdge = upLidLdEdge
        self.lowLidLdEdge = lowLidLdEdge
        self.lidBlinkEdge = lidBlinkEdge
        self.uplidBlinkEdge = uplidBlinkEdge
        self.lowlidBlinkEdge = lowlidBlinkEdge
        self.upCreaseHdEdge = upCreaseHdEdge
        self.upCreaseLdEdge = upCreaseLdEdge
        self.lowCreaseHdEdge = lowCreaseHdEdge
        self.lowCreaseLdEdge = lowCreaseLdEdge



        super(Eyelids, self).__init__(**kwargs)

    def build(self):
        super(Eyelids, self).build()

        # create wire for up and low blink curve
        for i in [self.uplidBlinkEdge , self.lowlidBlinkEdge]:
            mc.select(i, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.lidBlinkEdge)

        # blend shape up and low ld curves to lid blink
        mc.blendShape(self.upLidLdEdge, self.lowLidLdEdge, self.lidBlinkEdge, tc=False, automatic=True, name=self.side + '_lidBlink_BLS')
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
        mc.connectAttr(self.upCreaseMakroMult + '.output', self.upCreaseMakroGrp + '.translate')


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
        mc.connectAttr(self.lowCreaseMakroMult + '.output', self.lowCreaseMakroGrp + '.translate')

        # create wire for up and low Crease curve
        for i,j in zip([self.upCreaseLdEdge , self.lowCreaseLdEdge], [self.upCreaseHdEdge , self.lowCreaseHdEdge]):
            mc.select(j, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= i)

        # create wire for up and low lids curve
        for i,j in zip([self.upLidLdEdge , self.lowLidLdEdge], [self.upLidHdEdge , self.lowLidHdEdge]):
            mc.select(j, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= i)

        # connect stuf to the locators under lid makro loc
        mc.pointConstraint(self.upEyelidBndJnts[6],self.upLidMakroLoc,mo = True)
        mc.pointConstraint(self.lowEyelidBndJnts[6],self.lowLidMakroLoc,mo = True)

        mc.pointConstraint(self.browMidMakroLoc, self.upLidMakroLoc,self.upCreaseMakroLoc, mo = True)

        mc.pointConstraint(self.lowLidMakroLoc,self.cheekRaiseMakro, self.lowCreaseMakroLoc, mo = True)

        mc.pointConstraint(self.cheeckJoints[-1], self.cheekRaiseMakro, mo = True)


        # connect controls to the neighbor transform above controls
        mc.parentConstraint(self.upmidCtl,self.upLdCtls[0],self.upLdCtlGrps[1],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.upmidCtl,self.upLdCtls[-1],self.upLdCtlGrps[2],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowmidCtl,self.upLdCtls[0],self.lowLdCtlGrps[0],weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowmidCtl,self.upLdCtls[-1],self.lowLdCtlGrps[1],weight = 0.5 ,mo = True)

        # connect controls to the neighbor transform above crease controls
        mc.parentConstraint(self.upCreaseCtls[0],self.upCreaseCtls[2],self.upCreaseLdCtlGrps[1],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.upCreaseCtls[2],self.upCreaseCtls[-1],self.upCreaseLdCtlGrps[3],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowCreaseCtls[1],self.upCreaseCtls[0],self.lowCreaseLdCtlGrps[0],skipRotate='x',weight = 0.5 ,mo = True)
        mc.parentConstraint(self.lowCreaseCtls[1],self.upCreaseCtls[-1],self.lowCreaseLdCtlGrps[2],skipRotate='x',weight = 0.5 ,mo = True)




        #clean outliner
        for i in [self.upLidHdEdge, self.upLidLdEdge, self.uplidBlinkEdge,
                  self.lowLidHdEdge, self.lowLidLdEdge, self.lowlidBlinkEdge, self.lidBlinkEdge, self.tempCurve, self.upCreaseHdEdge,
                  self.lowCreaseHdEdge, self.upCreaseLdEdge, self.lowCreaseLdEdge,
                  self.side + '_lidBlink_CRVBaseWire',self.side + '_lidBlink_CRVBaseWire1',
                  self.side + '_upCreaseLd_CRVBaseWire',self.side + '_lowCreaseLd_CRVBaseWire',
                  self.side + '_upLidLd_CRVBaseWire', self.side + '_lowLidLd_CRVBaseWire']:
            mc.parent(i,self.eyelidCrvGrp)

        mc.parent(self.eyelidCrvGrp, self.localEyelidRig)

        if self.side == 'R':
            mc.setAttr(self.eyelidCtlGrp + '.ty', -1 * (self.movement))

    def connect(self):
        super(Eyelids, self).connect()

        if self.side == 'R':
            ctlPar = self.getOut('ctlParent')
            if ctlPar:
                mc.parent(self.eyelidCtlGrp, ctlPar)

            localPar = self.getOut('localParent')
            if localPar:
                mc.parent(self.localEyelidRig, localPar)

        eyeAimCtl = self.getOut('eyeAimCtl')
        eyeMakroLoc = self.getOut('eyeMakroloc')
        if eyeAimCtl and eyeMakroLoc:
            self.lowFleshyEyesSwitchMult = mc.createNode('multiplyDivide', name = self.side + '_lowFleshyEyesSwitch_MDN')
            self.upFleshyEyesSwitchMult = mc.createNode('multiplyDivide', name = self.side + '_upFleshyEyesSwitch_MDN')

            for i in [self.lowFleshyEyesSwitchMult,self.upFleshyEyesSwitchMult]:
                for j in ['input2X', 'input2Y', 'input2Z']:
                    mc.connectAttr(eyeAimCtl + '.fleshyEyes', i + '.' + j)
            units = []
            fac = -0.800
            for i in range(2):
                unit = mc.shadingNode('unitConversion', asUtility=True)
                mc.setAttr(unit + '.conversionFactor', fac)
                units.append(unit)
                fac = 1.200
            mc.connectAttr(eyeMakroLoc + '.rx', units[0] + '.input')
            mc.connectAttr(eyeMakroLoc + '.ry', units[1] + '.input')
            mc.connectAttr(units[0] + '.output', self.lowFleshyEyesSwitchMult + '.input1X')
            mc.connectAttr(units[1] + '.output', self.lowFleshyEyesSwitchMult + '.input1Y')

            units = []
            fac = -1.800
            for i in range(2):
                unit = mc.shadingNode('unitConversion', asUtility=True)
                mc.setAttr(unit + '.conversionFactor', fac)
                units.append(unit)
                fac = 1.200
            mc.connectAttr(eyeMakroLoc + '.rx', units[0] + '.input')
            mc.connectAttr(eyeMakroLoc + '.ry', units[1] + '.input')
            mc.connectAttr(units[0] + '.output', self.upFleshyEyesSwitchMult + '.input1X')
            mc.connectAttr(units[1] + '.output', self.upFleshyEyesSwitchMult + '.input1Y')

            for i in [self.upmidCtlGrp, self.makroUpJntGrp]:
                mc.connectAttr(self.upFleshyEyesSwitchMult + '.outputX', i + '.ty')
                mc.connectAttr(self.upFleshyEyesSwitchMult + '.outputY', i + '.tx')

            for i in [self.lowmidCtlGrp, self.makroLowJntGrp]:
                mc.connectAttr(self.lowFleshyEyesSwitchMult + '.outputX', i + '.ty')
                mc.connectAttr(self.lowFleshyEyesSwitchMult + '.outputY', i + '.tx')


        inBrowCtl = self.getOut('inBrowCtl')
        if inBrowCtl:
            trsLib.match(self.browInOriGrp,inBrowCtl )

        outBrowCtl = self.getOut('outBrowCtl')
        if outBrowCtl:
            trsLib.match(self.browOutOriGrp,outBrowCtl )

        midBrowCtl = self.getOut('midBrowCtl')
        if midBrowCtl:
            trsLib.match(self.browMidMakroDrvrOriGrp,midBrowCtl )
            [mc.connectAttr(midBrowCtl + '.{}{}'.format(a, v), self.browMidMakroDrvrLoc + '.{}{}'.format(a, v)) for a in 'tr' for v in 'xyz']
        # connect stuff to the groups under browMakro locGrp
        mc.pointConstraint(self.browOutLoc,self.browInLoc,self.browMidMakroDrvrOriGrp, mo = True)
        mc.pointConstraint(self.browMidMakroDrvrLoc, self.browMidMakroLoc, mo = True)

        eyeSquashCtl = self.getOut('eyeSquashCtl')
        if eyeSquashCtl:
            # connect squash ctl to the socket group
            [mc.connectAttr(eyeSquashCtl + '.{}{}'.format(a, v), self.eyelidSocketGrp + '.{}{}'.format(a, v)) for a in 'trs' for v in 'xyz']



        eyelidGeo = self.getOut('eyelidsGeo')
        if eyelidGeo:
            if self.side == 'L':
                jntsToBindEyeLidGeo = self.upEyelidBndJnts + self.uplidCreaseBndJnts + self.lowEyelidBndJnts + self.lowlidCreaseBndJnts + self.eyelidFloodJnt
                jntsToBindEyeLidGeo.append(self.cheeckJoints[0])
                deformLib.bind_geo(geos=eyelidGeo, joints=jntsToBindEyeLidGeo)

            else:
                jntsToBindEyeLidGeo = self.upEyelidBndJnts + self.uplidCreaseBndJnts + self.lowEyelidBndJnts + self.lowlidCreaseBndJnts
                jntsToBindEyeLidGeo.append(self.cheeckJoints[0])
                skin = mc.listHistory(eyelidGeo)
                if skin:
                    for i in skin:
                        if mc.objectType(i) == 'skinCluster':
                            for j in jntsToBindEyeLidGeo:
                                mc.skinCluster(i, edit = True, ai = j)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Eyelids, self).createSettings()

        # attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_neck.headCtl')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_head.topSquashFirst')
        attrLib.addString(self.blueprintGrp, 'blu_localParent', v='C_head.localRigs')
        attrLib.addString(self.blueprintGrp, 'blu_eyeAimCtl', v=self.side + '_eye.eyeAimCtl')
        attrLib.addString(self.blueprintGrp, 'blu_eyeMakroloc', v=self.side + '_eye.eyeMakroloc')
        attrLib.addString(self.blueprintGrp, 'blu_midBrowCtl', v=self.side + '_eyebrows.midBrowCtl')
        attrLib.addString(self.blueprintGrp, 'blu_outBrowCtl', v=self.side + '_eyebrows.outBrowCtl')
        attrLib.addString(self.blueprintGrp, 'blu_inBrowCtl', v=self.side + '_eyebrows.inBrowCtl')
        attrLib.addString(self.blueprintGrp, 'blu_eyelidsGeo', v='C_head.eyelidsGeo')
        attrLib.addString(self.blueprintGrp, 'blu_eyeSquashCtl', v=self.side + '_eye.eyeSquashCtl')
        attrLib.addString(self.blueprintGrp, 'blu_upLidHdEdge', v=self.upLidHdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lowLidHdEdge', v=self.lowLidHdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_upLidLdEdge', v=self.upLidLdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lowLidLdEdge', v=self.lowLidLdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lidBlinkEdge', v=self.lidBlinkEdge)
        attrLib.addString(self.blueprintGrp, 'blu_uplidBlinkEdge', v=self.uplidBlinkEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lowlidBlinkEdge', v=self.lowlidBlinkEdge)
        attrLib.addString(self.blueprintGrp, 'blu_upCreaseHdEdge', v=self.upCreaseHdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_upCreaseLdEdge', v=self.upCreaseLdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lowCreaseHdEdge', v=self.lowCreaseHdEdge)
        attrLib.addString(self.blueprintGrp, 'blu_lowCreaseLdEdge', v=self.lowCreaseLdEdge)




