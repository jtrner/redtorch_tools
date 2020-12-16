import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from ....lib import deformLib
from ....lib import keyLib
from . import buildLip

reload(keyLib)
reload(deformLib)
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
        for i in [self.upLipZippercrv ,self.lowLipZippercrv ]:
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

        for i in [self.lowJntDrvr ,self.upjntCtlPlace ]:
            mc.parentConstraint(self.upLipJawFollowDrvr, i, mo = True)

        for i in [self.upJntDrvr ,self.ctlupPlacement  ]:
            mc.parentConstraint(self.lowLipJawFollowDrvr, i, mo = True)

        for i in [self.leftUpMainJnt ,self.leftLowMainJnt ,self.rightLowLipCtlGrp ,self.rightUpLipCtlGrp,
                  self.rightUpMainJnt,self.leftUpLipCtlGrp, self.rightLowMainJnt,self.leftLowLipCtlGrp  ]:
            mc.parentConstraint(self.LipCornerJawFollowDrvr, i, mo = True)

        for i in [self.cln(self.upJntDrvr), self.cln(self.ctlupPlacement)]:
            i = i.split('|')[-1]
            mc.parentConstraint(self.ctlupLipJawFollowDrvr, i, mo = True)

        for i in [self.cln(self.lowJntDrvr), self.cln(self.ctllowPlacement)]:
            i = i.split('|')[-1]
            mc.parentConstraint(self.ctllowLipJawFollowDrvr, i, mo = True)

        for i in [self.cln(self.leftUpMainJnt), self.cln(self.leftLowMainJnt),self.cln(self.rightLowLipCtlGrp),
                  self.cln(self.rightUpLipCtlGrp),self.cln(self.rightUpMainJnt),self.cln(self.leftUpLipCtlGrp),
                  self.cln(self.rightLowMainJnt),self.cln(self.leftLowLipCtlGrp),self.cln(self.mouthCtlOr)]:
            i = i.split('|')[-1]
            mc.parentConstraint(self.ctlLipCornerJawFollowDrvr, i, mo = True)

        # parent constraint stuff to the locators under upjntdrvr
        mc.parentConstraint(self.M_upLipOutJnt ,self.upLipMidLoc, mo = True)
        mc.parentConstraint(self.upLipLowRezBindJnts[0] ,self.r_upcornerOr , mo = True)
        mc.orientConstraint(self.upLipMidLoc, self.M_upLipOutJnt  ,self.r_upmidSecOr, weight = 0.5, mo = True)
        mc.orientConstraint(self.r_upcornerOr ,self.upLipMidLoc, self.r_upoutOrLoc,weight = 0.5, mo = True)

        # parent constraint stuff to the locators under lowjntdrvr
        mc.parentConstraint(self.M_lowLipOutJnt  ,self.lowLipMidLoc, mo = True)
        mc.parentConstraint(self.lowLipLowRezBindJnts[0],self.r_lowcornerOr , mo = True)
        mc.orientConstraint(self.lowLipMidLoc, self.M_lowLipOutJnt  ,self.r_lowmidSecOr, weight = 0.5, mo = True)
        mc.orientConstraint(self.r_lowcornerOr  ,self.lowLipMidLoc, self.r_lowoutOrLoc,weight = 0.5, mo = True)

        # parent constraint locators to the groups above upmakro controls
        mc.parentConstraint(self.r_localUpLipDriverOutMod ,self.r_localUpLipOutOrient_GRP, mo = True )
        mc.parentConstraint(self.m_localUpLipDriverOutMod ,self.m_localUpLipOutOrient_GRP, mo = True )
        mc.parentConstraint(self.l_localUpLipDriverOutMod ,self.l_localUpLipOutOrient_GRP, mo = True )

        # parent constraint locators to the groups above lowmakro controls
        mc.parentConstraint(self.r_localLowLipDriverOutMod ,self.r_localLowLipOutOrient_GRP , mo = True )
        mc.parentConstraint(self.m_localLowLipDriverOutMod ,self.m_localLowLipOutOrient_GRP, mo = True )
        mc.parentConstraint(self.l_localLowLipDriverOutMod ,self.l_localLowLipOutOrient_GRP, mo = True )

        # parent constraint locators on medrez curve to the  up micro groups
        mc.parentConstraint(self.upSecMod,self.upTerOrientGrp[1] , mo = True)
        mc.parentConstraint(self.upmicroOutMod , self.upZipOutBndGrp[0] , mo = True)
        mc.parentConstraint(self.upmidSecMod ,self.upTerOrientGrp[2] , mo = True)
        mc.parentConstraint(self.upMidMod ,self.upZipOutBndGrp[1], mo = True)
        mc.parentConstraint(self.upMidSecModLoc ,self.upTerOrientGrp[3] , mo = True)
        mc.parentConstraint(self.microOutModLoc ,self.upZipOutBndGrp[2]  , mo = True)
        mc.parentConstraint(self.microOutSecMod ,self.upTerOrientGrp[4], mo = True)
        mc.parentConstraint(self.l_outUpTerModLocHi,self.upTerOrientGrp[0], mo = True)
        mc.parentConstraint(self.r_outUpTerModLocHi,self.upTerOrientGrp[5], mo = True)

        # parent constraint locators on medrez curve to the  low micro groups
        mc.parentConstraint(self.lowSecMod,self.lowTerOrientGrp[1] , mo = True)
        mc.parentConstraint(self.lowmicroOutMod , self.lowZipOutBndGrp[0] , mo = True)
        mc.parentConstraint(self.lowmidSecMod ,self.lowTerOrientGrp[2] , mo = True)
        mc.parentConstraint(self.lowMidMod ,self.lowZipOutBndGrp[1], mo = True)
        mc.parentConstraint(self.lowMidSecModLoc ,self.lowTerOrientGrp[3] , mo = True)
        mc.parentConstraint(self.lowmicroOutModLoc ,self.lowZipOutBndGrp[2]  , mo = True)
        mc.parentConstraint(self.lowmicroOutSecMod ,self.lowTerOrientGrp[4], mo = True)
        mc.parentConstraint(self.l_outLowTerModLocHi,self.lowTerOrientGrp[0], mo = True)
        mc.parentConstraint(self.r_outLowTerModLocHi,self.lowTerOrientGrp[5], mo = True)

        #bind joints to up lowrez and medrez curves
        deformLib.bind_geo(geos = self.upLipLowRezcrv, joints = self.upLipLowRezBindJnts)
        deformLib.bind_geo(geos = self.upLipMedRezcrv, joints = self.upmedRezBindJnts)

        #bind joints to low lowrez and medrez curves
        deformLib.bind_geo(geos = self.lowLipLowRezcrv, joints = self.lowLipLowRezBindJnts)
        deformLib.bind_geo(geos = self.lowLipMedRezcrv, joints = self.lowmedRezBindJnts)

        # bind joints to the up highrez Curves
        for index,value in enumerate(self.upMicroJnts):
            if index in [0,5]:
                continue
            self.upHirzBndJnts.append(value)

        deformLib.bind_geo(geos = self.upLipHiRezcrv, joints = self.upHirzBndJnts)
        # bind joints to the low highrez Curves
        for index,value in enumerate(self.lowMicroJnts):
            if index in [0,5]:
                continue
            self.lowHirzBndJnts.append(value)

        deformLib.bind_geo(geos = self.lowLipHiRezcrv, joints = self.lowHirzBndJnts)

        # bind the mouth joint to the up curve temp(thouth not sure about it)

        deformLib.bind_geo(geos=self.tempCurve, joints=self.mouthAndJawMain[2])

        # connect the locator under ctl placement to the locator under up roll modify
        attrLib.addFloat(self.upJntCtlLoc, ln = 'lipRoll', dv = 0)
        mc.pointConstraint(self.upJntCtlLoc,self.jntUpRollLoc, mo = True)
        unit = mc.shadingNode('unitConversion', asUtility = True )
        mc.setAttr(unit + '.conversionFactor', 0.017)
        mc.connectAttr(self.upJntCtlLoc+ '.lipRoll', unit+ '.input')
        mc.connectAttr(unit + '.output', self.jntUpRollLoc+ '.rx')

        # connect the locator under ctl placement to the locator under low roll modify
        attrLib.addFloat(self.lowJntCtlLoc, ln = 'lipRoll', dv = 0)
        mc.pointConstraint(self.lowJntCtlLoc,self.jntLowRollLoc, mo = True)
        unit = mc.shadingNode('unitConversion', asUtility = True )
        mc.setAttr(unit + '.conversionFactor', 0.017)
        mc.connectAttr(self.lowJntCtlLoc+ '.lipRoll', unit+ '.input')
        mc.connectAttr(unit + '.output', self.jntLowRollLoc+ '.rx')

        # parent constraint one of locators under roll modify to the up transform above mid main jnt
        mc.parentConstraint(self.upLipJntMidLoc,self.middleUpMainMod, mo = True)
        # parent constraint one of locators under roll modify to the low transform above mid main jnt
        mc.parentConstraint(self.lowLipJntMidLoc,self.midLowMainMod, mo = True)

        # connect noseMakro locator to the nose Bend makro
        unit = mc.shadingNode('unitConversion', asUtility = True )
        mc.setAttr(unit + '.conversionFactor', -0.100)
        mc.connectAttr(self.noseMakroDrvrLoc + '.tz', unit+ '.input')
        mc.connectAttr(unit + '.output', self.noseBendMakro+ '.rx')

        # connect nose makro driver loc to the transfrom above the group of nose bind jnt
        units = []
        fact = 0.1
        for i in range(3):
            unit = mc.shadingNode('unitConversion', asUtility=True)
            mc.setAttr(unit + '.conversionFactor', fact)
            fact += 0.1
            units.append(unit)
        mc.setAttr(units[2] + '.conversionFactor', 0.060)
        mc.connectAttr(self.noseMakroDrvrLoc + '.tx', units[0]+ '.input')
        mc.connectAttr(self.noseMakroDrvrLoc + '.tx', units[2]+ '.input')
        mc.connectAttr(self.noseMakroDrvrLoc + '.ty', units[1]+ '.input')
        mc.connectAttr(units[0] + '.output', self.noseJntMakro+ '.tx')
        mc.connectAttr(units[2]+ '.output', self.noseJntMakro+ '.rz')
        mc.connectAttr(units[1] + '.output', self.noseJntMakro+ '.ty')

        # connect the nose ctl to the group above nose joint
        [mc.connectAttr(self.noseCtl + '.{}{}'.format(t,a), self.noseJntMod + '.{}{}'.format(t,a))for t in 'trs' for a in'xyz']

        #connect nose ctl base to the noseJnt base mod group
        [mc.connectAttr(self.noseCtlBase + '.{}{}'.format(t,a), self.noseJntBaseMod + '.{}{}'.format(t,a))for t in 'trs' for a in'xyz']

        # connect right lipCorner makro to the right nostril joint makro
        r_nostMakroMult = mc.createNode('multiplyDivide', name = 'R_nostrilMAKRO_MDN')
        at = 0.020
        for i in ['input2Z','input2X','input2Y']:
            mc.setAttr(r_nostMakroMult +'.' + i, at)
            at += 0.020
        r_nostMakroOneg = mc.createNode('multiplyDivide', name = 'R_nostrilMAKROneg_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(r_nostMakroOneg +'.' + i, -1)
        mc.connectAttr(self.r_cornerMakroLoc + '.tx', r_nostMakroMult + '.input1X')
        mc.connectAttr(self.r_cornerMakroLoc + '.ty', r_nostMakroMult + '.input1Y')
        mc.connectAttr(r_nostMakroMult + '.outputX', self.r_nostrilJntMakro + '.tx')
        mc.connectAttr(r_nostMakroMult + '.outputY', self.r_nostrilJntMakro + '.ty')

        unit1 = mc.shadingNode('unitConversion', asUtility=True)
        mc.setAttr(unit1 + '.conversionFactor', 0.200)
        unit2 = mc.shadingNode('unitConversion', asUtility=True)
        mc.setAttr(unit2 + '.conversionFactor', -0.300)
        mc.connectAttr(r_nostMakroMult + '.outputY', unit1 + '.input')
        mc.connectAttr(r_nostMakroMult + '.outputX', unit2 + '.input')

        mc.connectAttr(unit1 + '.output', self.r_nostrilJntMakro+ '.ry')
        mc.connectAttr(unit2 + '.output', self.r_nostrilJntMakro+ '.rx')

        mc.connectAttr(r_nostMakroMult + '.outputX', r_nostMakroOneg + '.input1X')
        mc.connectAttr(r_nostMakroOneg + '.outputX', self.r_nostrilJntMakro + '.tz')

        # connect left lipCorner makro to the left nostril joint makro
        l_nostMakroMult = mc.createNode('multiplyDivide', name = 'L_nostrilMAKRO_MDN')
        at = 0.020
        for i in ['input2Z','input2X','input2Y']:
            mc.setAttr(l_nostMakroMult +'.' + i, at)
            at += 0.020
        l_nostMakroOneg = mc.createNode('multiplyDivide', name = 'L_nostrilMAKROneg_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(l_nostMakroOneg +'.' + i, -1)
        mc.connectAttr(self.l_cornerMakroLoc + '.tx', l_nostMakroMult + '.input1X')
        mc.connectAttr(self.l_cornerMakroLoc + '.ty', l_nostMakroMult + '.input1Y')
        mc.connectAttr(l_nostMakroMult + '.outputX', self.l_nostrilJntMakro + '.tx')
        mc.connectAttr(l_nostMakroMult + '.outputY', self.l_nostrilJntMakro + '.ty')

        unit1 = mc.shadingNode('unitConversion', asUtility=True)
        mc.setAttr(unit1 + '.conversionFactor', 0.200)
        unit2 = mc.shadingNode('unitConversion', asUtility=True)
        mc.setAttr(unit2 + '.conversionFactor', -0.300)
        mc.connectAttr(l_nostMakroMult + '.outputY', unit1 + '.input')
        mc.connectAttr(l_nostMakroMult + '.outputX', unit2 + '.input')

        mc.connectAttr(unit1 + '.output', self.l_nostrilJntMakro+ '.ry')
        mc.connectAttr(unit2 + '.output', self.l_nostrilJntMakro+ '.rx')

        mc.connectAttr(l_nostMakroMult + '.outputX', l_nostMakroOneg + '.input1X')
        mc.connectAttr(l_nostMakroOneg + '.outputX', self.l_nostrilJntMakro + '.tz')

        # connect columella ctl to the group above columella joint
        [mc.connectAttr(self.columellaCtl + '.{}{}'.format(t,a), self.columJntMod + '.{}{}'.format(t,a))for t in 'trs' for a in'xyz']

        # TODO: connect jaw ctl to the group obove jaw joints later
        # connect up lip out ctls to the locals
        [mc.connectAttr(self.cln(self.R_upLipOutCtl) + '.{}{}'.format(t,a), self.R_upLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        [mc.connectAttr(self.cln(self.L_upLipOutCtl) + '.{}{}'.format(t,a), self.L_upLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        [mc.connectAttr(self.cln(self.M_upLipOutCtl) + '.{}{}'.format(t,a), self.M_upLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        # connect low lip out ctls to the locals
        [mc.connectAttr(self.cln(self.R_lowLipOutCtl) + '.{}{}'.format(t,a), self.R_lowLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        [mc.connectAttr(self.cln(self.L_lowLipOutCtl) + '.{}{}'.format(t,a), self.L_lowLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        [mc.connectAttr(self.cln(self.M_lowLipOutCtl) + '.{}{}'.format(t,a), self.M_lowLipOutCtl + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']

        # conect local upLip main modLoc to the upLipMidMod loc
        mc.orientConstraint(self.m_upLipCornerMod_loc,self.M_upLipMidModLoc, mo = True)
        mc.orientConstraint(self.m_lowLipCornerMod_loc,self.M_lowLipMidModLoc, mo = True)

        # connect up micro controls to the locator above the bind jnts
        for ctl,loc in zip(self.microUpCtls,self.upLocMod):
            [mc.connectAttr(ctl + '.{}{}'.format(t, a),loc + '.{}{}'.format(t, a)) for t in 'trs' for a in 'xyz']

        # connect low micro controls to the locator above the bind jnts
        for ctl,loc in zip(self.microLowCtls,self.lowLocMod):
            [mc.connectAttr(ctl + '.{}{}'.format(t, a),loc + '.{}{}'.format(t, a)) for t in 'trs' for a in 'xyz']

        # pointConstraint up zip target locators to the zip joints
        for ctl,loc in zip(self.upTerLocs,self.upZipJnts):
            mc.pointConstraint(ctl, loc , mo = True)

        # pointConstraint low zip target locators to the zip joints
        for ctl,loc in zip(self.lowTerLocs,self.lowZipJnts):
            mc.pointConstraint(ctl, loc , mo = True)
        # connect stuff to the zip joints
        attrLib.addFloat(self.leftUpCornerCtl, ln = 'zip', min = 0, dv = 0)
        attrLib.addFloat(self.rightUpCornerCtl, ln = 'zip', min = 0, dv = 0)


        upmults = []
        for i in self.upZipJnts:
            mult = mc.createNode('multiplyDivide', name  = i + '_MDN')
            upmults.append(mult)
        mult = mc.createNode('multiplyDivide', name  = 'R_outTertiaryZip_MD1')
        upmults.append(mult)
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.leftUpCornerCtl + '.zip', upmults[0] + '.' +  j, [0,11], [0,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.leftUpCornerCtl + '.zip', upmults[1] + '.' +  j, [0,6,9,18], [0,0.03,0.2,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.leftUpCornerCtl + '.zip', upmults[2] + '.' +  j, [0,4,8,14], [0,0.2,0.6,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.leftUpCornerCtl + '.zip', upmults[3] + '.' +  j, [0,3,17], [0,0,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.leftUpCornerCtl + '.zip', upmults[4] + '.' +  j, [4,8,20], [0,0.05,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.rightUpCornerCtl + '.zip', upmults[5] + '.' +  j, [4,8,20], [0,0.05,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.rightUpCornerCtl + '.zip', upmults[6] + '.' +  j, [0,3,17], [0,0,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.rightUpCornerCtl + '.zip', upmults[7] + '.' +  j, [0,4,8,14], [0,0.2,0.6,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.rightUpCornerCtl + '.zip', upmults[8] + '.' +  j, [0,6,9,18], [0,0.03,0.2,1],itt='auto', ott = 'auto')
        for j in ['input2X', 'input2Y', 'input2Z']:
            keyLib.setDriven(self.rightUpCornerCtl + '.zip', upmults[9] + '.' +  j, [0,11], [0,1],itt='auto', ott = 'auto')


        a = ['tx', 'ty', 'tz']
        b = ['input1X', 'input1Y', 'input1Z']
        c = ['input2X', 'input2Y', 'input2Z']
        upZipTemp = []
        upMultTemp = []
        for i in range(10):
            if i in [5]:
                continue
            uplip = self.upZipJnts[i-1]
            upZipTemp.append(uplip)
        for i in range(10):
            if i in [5,6]:
                continue
            upmult = upmults[i-1]
            upMultTemp.append(upmult)
        for i in range(8):
            for j,k in zip(a,b):
                mc.connectAttr(upZipTemp[i]+ '.' + j, upMultTemp[i] + '.' + k)
        for j,k in zip(a,b):
            mc.connectAttr(self.upZipJnts[4] + '.' + j,upmults[4] + '.' + k)
            mc.connectAttr(self.upZipJnts[4] + '.' + j,upmults[5] + '.' + k)
        l_mult = mc.createNode('multiplyDivide', name = 'L_midZipHalf_MDN')
        r_mult = mc.createNode('multiplyDivide', name = 'R_midZipHalf_MDN')

        for i in c:
            mc.setAttr(l_mult + '.' + i, 0.5)
            mc.setAttr(r_mult + '.' + i, 0.5)

        mc.connectAttr(upmults[4] + '.output' , l_mult + '.input1' )
        mc.connectAttr(upmults[5] + '.output' , r_mult + '.input1' )

        upMidZipPls = mc.createNode('plusMinusAverage', name = 'upmidZip_PMA')
        mc.connectAttr(l_mult + '.output',upMidZipPls + '.input3D[0]')
        mc.connectAttr(r_mult + '.output',upMidZipPls + '.input3D[1]')

        mc.connectAttr(upMultTemp[0] + '.output', self.upMicroJnts[5] + '.translate')
        mc.connectAttr(upMultTemp[1] + '.output', self.upMicroJnts[0] + '.translate')
        mc.connectAttr(upMultTemp[2] + '.output', self.upMicroJnts[1] + '.translate')
        mc.connectAttr(upMultTemp[3] + '.output', self.upMicroJnts[6] + '.translate')
        mc.connectAttr(upMultTemp[4] + '.output', self.upMicroJnts[2] + '.translate')
        mc.connectAttr(upMultTemp[5] + '.output', self.upMicroJnts[3] + '.translate')
        mc.connectAttr(upMultTemp[6] + '.output', self.upMicroJnts[8] + '.translate')
        mc.connectAttr(upMultTemp[7] + '.output', self.upMicroJnts[4] + '.translate')

    def cln(self,node):
        node = node.replace('local', '')
        return node
