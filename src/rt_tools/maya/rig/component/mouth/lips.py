import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from . import buildLip

reload(buildLip)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Lips(buildLip.BuildLip):
    """
    base class for lip template
    """
    def __init__(self, side='C', prefix='lip', zippercrv = '',upLipLowRezcrv = '',
                 upLipMedRezcrv= '', upLipHiRezcrv = '',upLipZippercrv = '',lowLipLowRezcrv = '',
                 lowLipHiRezcrv = '',lowLipMedRezcrv= '',lowLipZippercrv = '',upBindJnts = [],
                 lowBindJnts = [],numJnts=20,**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.zippercrv = zippercrv
        self.upLipLowRezcrv = upLipLowRezcrv
        self.upLipMedRezcrv = upLipMedRezcrv
        self.upLipHiRezcrv = upLipHiRezcrv
        self.upLipZippercrv = upLipZippercrv
        self.lowLipLowRezcrv = lowLipLowRezcrv
        self.lowLipHiRezcrv = lowLipHiRezcrv
        self.lowLipMedRezcrv = lowLipMedRezcrv
        self.lowLipZippercrv  = lowLipZippercrv
        self.upBindJnts= upBindJnts
        self.lowBindJnts= lowBindJnts
        self.numJnts = numJnts

        super(Lips, self).__init__(**kwargs)

    def build(self):
        super(Lips, self).build()
        # create wire for up and low zip curves
        for i in [self.upLipZippercrv ,self.lowLipLowRezcrv ]:
            mc.select(i, r=True)
            mc.wire(gw=False, en=1.000000, ce=0.000000, li=0.000000, w= self.zippercrv)

        # blend shape med rez curves to the zipper curve
        self.upLipMedRezcrv = self.upLipMedRezcrv.split('|')[-1]
        self.lowLipLowRezcrv = self.lowLipLowRezcrv.split('|')[-1]
        mc.blendShape(self.upLipMedRezcrv , self.lowLipMedRezcrv, self.zippercrv, tc=False, automatic=True, name='zipper_BLS' )
        mc.blendShape('zipper_BLS', edit=True, w=[(0, 0.5), (1, 0.5)])

        # connect mouth ctrl to the mouth pivot joint
        attrLib.addFloat(self.mouthCtl,ln = 'X', dv = 0)
        attrLib.addFloat(self.mouthCtl,ln = 'teethFollow',min = 0, max = 1, dv = 1)
        for i in ['tz', 'ty','rx', 'rz']:
            mc.connectAttr(self.mouthCtl + '.' + i, self.mouthAndJawMain[2] + '.' +  i)

        fact = 0.230
        units = []
        for i in ['tx', 'X']:
            unit = mc.shadingNode('unitConversion', asUtility = True )
            mc.setAttr(unit + '.conversionFactor', fact)
            fact = 0.100
            units.append(unit)
        mc.connectAttr(self.mouthCtl + '.tx', units[0] + '.input')
        mc.connectAttr(self.mouthCtl + '.X', units[1] + '.input')
        mc.connectAttr(units[0] + '.output', self.mouthAndJawMain[2] + '.ry')
        mc.connectAttr(units[1] + '.output', self.mouthAndJawMain[2] + '.tx')

        # connect mouth joint to the follow locators
        [mc.connectAttr(self.mouthAndJawMain[2] + '.{}{}'.format(c,v),self.upLipJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']
        [mc.connectAttr(self.mouthAndJawMain[2] + '.{}{}'.format(c,v),self.lowLipJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']
        [mc.connectAttr(self.mouthAndJawMain[2] + '.{}{}'.format(c,v),self.LipCornerJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']
        [mc.connectAttr(self.mouthAndJawMain[2] + '.{}{}'.format(c,v),self.mouthAncFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']

        [mc.connectAttr(self.mouthAncFollowDrvr + '.{}{}'.format(c,v),self.ctlupLipJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']
        [mc.connectAttr(self.mouthAncFollowDrvr + '.{}{}'.format(c,v),self.ctllowLipJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']
        [mc.connectAttr(self.mouthAncFollowDrvr + '.{}{}'.format(c,v),self.ctlLipCornerJawFollowDrvr + '.{}{}'.format(c,v))for c in 'trs' for v in 'xyz']

        # paret and orient constraint the follow locs to the groups

        for i in [self.jntRollModupGrp  ,self.upLipCtlRoll]:
            mc.orientConstraint(self.upLipJawFollowDrvr, i, mo = True)

        for i in [self.lowJntDrvr ,self.ctllowPlacement ]:
            mc.parentConstraint(self.upLipJawFollowDrvr, i, mo = True)

        for i in [self.upJntDrvr ,self.ctlupPlacement  ]:
            mc.parentConstraint(self.lowLipJawFollowDrvr, i, mo = True)

        for i in [self.leftUpMainJnt ,self.leftLowMainJnt ,self.rightLowLipCtlGrp ,self.rightUpLipCtlGrp,
                  self.rightUpMainJnt,self.leftUpLipCtlGrp, self.rightLowMainJnt,self.leftLowLipCtlGrp  ]:
            mc.parentConstraint(self.LipCornerJawFollowDrvr, i, mo = True)

        #self.ctlLipCornerJawFollowDrvr,self.ctlupLipJawFollowDrvr,self.ctllowLipJawFollowDrvr
        # should will parent constraint to the global groups
        for i in [self.cln(self.upJntDrvr), self.cln(self.ctlupPlacement)]:
            i = i.split('|')[-1]
            mc.orientConstraint(self.ctlupLipJawFollowDrvr, i, mo = True)

        for i in [self.cln(self.lowJntDrvr), self.cln(self.ctllowPlacement)]:
            i = i.split('|')[-1]
            mc.orientConstraint(self.ctllowLipJawFollowDrvr, i, mo = True)

        for i in [self.cln(self.leftUpMainJnt), self.cln(self.leftLowMainJnt),self.cln(self.rightLowLipCtlGrp),
                  self.cln(self.rightUpLipCtlGrp),self.cln(self.rightUpMainJnt),self.cln(self.leftUpLipCtlGrp),
                  self.cln(self.rightLowMainJnt),self.cln(self.leftLowLipCtlGrp),self.cln(self.mouthCtlOr)]:
            i = i.split('|')[-1]
            mc.orientConstraint(self.ctlLipCornerJawFollowDrvr, i, mo = True)


    def cln(self,node):
        node = node.replace('local', '')
        return node
