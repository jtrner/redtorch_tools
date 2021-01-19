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
from . import buildMisc
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildMisc)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Misc(buildMisc.BulidMisc):
    """
    base class for misc template
    """
    def __init__(self,movement = 40, side='L',miscGeo = '', prefix='misc',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.miscGeo = miscGeo
        self.movement = movement * 4

        super(Misc, self).__init__(**kwargs)

    def build(self):
        super(Misc, self).build()
        # connect stuf to the transform above misc joints
        for i in [self.miscCtls[-1],self.miscCtls[1], self.miscCtls[-2]]:
            attrLib.addFloat(i, ln = 'Z', dv = 0)
        self.cheekSubPma = mc.createNode('plusMinusAverage', name = self.side + '_cheeksub_PMA')
        mc.connectAttr(self.miscCtls[-1] + '.tx', self.cheekSubPma + '.input3D[0].input3Dx')
        mc.connectAttr(self.miscCtls[-1] + '.ty', self.cheekSubPma + '.input3D[0].input3Dy')
        mc.connectAttr(self.miscCtls[1] + '.tx', self.cheekSubPma + '.input3D[1].input3Dx')
        mc.connectAttr(self.miscCtls[1] + '.ty', self.cheekSubPma + '.input3D[1].input3Dy')
        mc.connectAttr(self.miscCtls[1] + '.Z', self.cheekSubPma + '.input3D[1].input3Dz')
        for i, j in zip(['output3Dz', 'output3Dy', 'output3Dz'],['translateX', 'translateY', 'translateZ']):
            mc.connectAttr(self.cheekSubPma + '.' + i, self.cheeckModGrp + '.' + j)

        [mc.connectAttr(self.miscCtls[8] + '.{}{}'.format(a,v),self.cheekLowerModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[2] + '.{}{}'.format(a,v),self.browFleshModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[4] + '.{}{}'.format(a,v),self.oriModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[-4] + '.{}{}'.format(a,v),self.earLowerModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[-3] + '.{}{}'.format(a,v),self.earUpperModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[0] + '.{}{}'.format(a,v),self.nasalLabialModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[5] + '.{}{}'.format(a,v),self.nasalModGrp + '.{}{}'.format(a,v))for a in 't' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[7] + '.{}{}'.format(a,v),self.appleModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[3] + '.{}{}'.format(a, v), self.orbitalUpperModGrp + '.{}{}'.format(a, v)) for a in 't' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[6] + '.{}{}'.format(a, v), self.orbitalLowerModGrp + '.{}{}'.format(a, v)) for a in 't' for v in 'xyz']


    def connect(self):
        super(Misc, self).connect()

        ctlPar = self.getOut('ctlParent')
        if ctlPar:
            mc.parent(self.nasalCtlOriGrp , ctlPar)
            mc.move(0, -1 * (self.movement), 0, self.nasalCtlOriGrp, r=True, ws=True)
            mc.parent(self.earCtlOriGrp , ctlPar)
            mc.move(0, -1 * (self.movement), 0, self.earCtlOriGrp, r=True, ws=True)
            mc.parent(self.orbitalLowerCtlOriGrp , ctlPar)
            mc.move(0, -1 * (self.movement), 0, self.orbitalLowerCtlOriGrp, r=True, ws=True)


        ctlParB = self.getOut('ctlParentB')
        if ctlParB:
            mc.parent(self.browFleshCtlOriGrp , ctlParB)
            mc.move(0, -1 * (self.movement), 0, self.browFleshCtlOriGrp, r=True, ws=True)
            mc.parent(self.orbitalUpperCtlOriGrp , ctlParB)
            mc.move(0, -1 * (self.movement), 0, self.orbitalUpperCtlOriGrp, r=True, ws=True)


        ctlParC = self.getOut('ctlParentC')
        if ctlParC:
            mc.parent(self.nasalLabialCtlOriGrp , ctlParC)
            mc.move(0, -1 * (self.movement), 0, self.nasalLabialCtlOriGrp, r=True, ws=True)
            mc.parent(self.cheekCtlOriGrp , ctlParC)
            mc.move(0, -1 * (self.movement), 0, self.cheekCtlOriGrp, r=True, ws=True)

        ctlParD = self.getOut('ctlParentD')
        if ctlParD:
            mc.parent(self.cheekLowerCtlOriGrp , ctlParD)
            mc.move(0, -1 * (self.movement), 0, self.cheekLowerCtlOriGrp, r=True, ws=True)

        applePar = self.getOut('appleParent')
        if applePar:
            mc.parent(self.appleCtlOriGrp , applePar)
            mc.move(0, -1 * (self.movement), 0, self.appleCtlOriGrp, r=True, ws=True)

        if self.side == 'R':

            localPar = self.getOut('localParent')
            if localPar:
                mc.parent(self.localMiscJntGrp, localPar)

        cheekMod = self.getOut('cheekJntMod')
        cheekRaise = self.getOut('cheekRaiseJntZ')

        if cheekMod and cheekRaise:
            self.miscCtls[-2],self.miscCtls[1]
            cheekRaisePma = mc.createNode('plusMinusAverage', name = self.side + '_cheekRaise_PMA')
            mc.connectAttr(self.miscCtls[1] + '.tx', cheekRaisePma + '.input3D[0].input3Dx')
            mc.connectAttr(self.miscCtls[1] + '.ty', cheekRaisePma + '.input3D[0].input3Dy')
            mc.connectAttr(self.miscCtls[1] + '.Z', cheekRaisePma + '.input3D[0].input3Dz')

            mc.connectAttr(self.miscCtls[-2] + '.tx', cheekRaisePma + '.input3D[1].input3Dx')
            mc.connectAttr(self.miscCtls[-2] + '.ty', cheekRaisePma + '.input3D[1].input3Dy')
            mc.connectAttr(self.miscCtls[-2] + '.Z', cheekRaisePma + '.input3D[1].input3Dz')
            mc.connectAttr(cheekRaisePma + '.output3Dz', cheekRaise + '.translateZ')
            unit = mc.shadingNode('unitConversion', asUtility=True)
            mc.setAttr(unit + '.conversionFactor', -0.500)
            mc.connectAttr(cheekRaisePma + '.output3Dy', unit + '.input')
            mc.connectAttr(unit + '.output', cheekRaise + '.rotateX')

            unit = mc.shadingNode('unitConversion', asUtility=True)
            mc.setAttr(unit + '.conversionFactor', 0.400)
            mc.connectAttr(cheekRaisePma + '.output3Dx', unit + '.input')
            mc.connectAttr(unit + '.output', cheekMod + '.rotateZ')

        cheekRiseEntJnt = self.getOut('cheekRiseEndJnt')
        if cheekRiseEntJnt:
            trsLib.match(self.cheekRaiseOriCtlGrp, t =cheekRiseEntJnt )
            mc.move(0, -1 * (self.movement/4), 0.5, self.cheekRaiseOriCtlGrp, r=True, ws=True)

        miscGeo = self.getOut('miscGeo')
        eyebrowlocalMisc = self.getOut('eyebrowlocalMisc')
        if miscGeo:
            if self.side == 'L':
                deformLib.bind_geo(geos=miscGeo, joints=self.miscJnts)
            else:
                skin = mc.listHistory(miscGeo)
                if skin:
                    for i in skin:
                        if mc.objectType(i) == 'skinCluster':
                            self.miscJnts.pop(1)
                            for j in self.miscJnts:
                                mc.skinCluster(i, edit = True, ai = j)

        jntsToBindBrow = []
        for i in (0,1,2,3,5,6,7):
            jnt = self.miscJnts[i]
            jntsToBindBrow.append(jnt)
        if eyebrowlocalMisc:
            if self.side == 'L':
                deformLib.bind_geo(geos=eyebrowlocalMisc, joints=jntsToBindBrow)
            else:
                jntsToBindBrow.pop(0)
                skin = mc.listHistory(eyebrowlocalMisc)
                if skin:
                    for i in skin:
                        if mc.objectType(i) == 'skinCluster':
                            for j in jntsToBindBrow:
                                mc.skinCluster(i, edit = True, ai = j)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Misc, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_head.topSquashFirst')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParentB', v='C_head.topSquashSecond')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParentC', v='C_head.squashFirst')
        attrLib.addString(self.blueprintGrp, 'blu_ctlParentD', v='C_head.squashThird')
        attrLib.addString(self.blueprintGrp, 'blu_appleParent', v='C_head.facialCtlGrp')
        attrLib.addString(self.blueprintGrp, 'blu_localParent', v='C_head.localRigs')
        attrLib.addString(self.blueprintGrp, 'blu_miscGeo', v='C_head.miscGeo')
        attrLib.addString(self.blueprintGrp, 'blu_eyebrowlocalMisc', v='C_head.eyebrowlocalMisc')
        attrLib.addString(self.blueprintGrp, 'blu_cheekJntMod', v=self.side + '_eyelid.cheekJntMod')
        attrLib.addString(self.blueprintGrp, 'blu_cheekRaiseJntZ', v=self.side + '_eyelid.cheekRaiseJntZ')
        attrLib.addString(self.blueprintGrp, 'blu_cheekRiseEndJnt', v=self.side + '_eyelid.cheekRiseEndJnt')



