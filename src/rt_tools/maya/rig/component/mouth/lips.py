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
from . import buildLip
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
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
    def __init__(self, side='C', prefix='lip',geo = '', zippercrv = '',upLipLowRezcrv = '',
                 upLipMedRezcrv= '', upLipHiRezcrv = '',upLipZippercrv = '',lowLipLowRezcrv = '',
                 lowLipHiRezcrv = '',lowLipMedRezcrv= '',lowLipZippercrv = '',upBindJnts =[],
                 lowBindJnts = [],numJnts=20,**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.geo = geo
        self.zippercrv = zippercrv
        self.upLipLowRezcrv = upLipLowRezcrv
        self.upLipMedRezcrv = upLipMedRezcrv
        self.upLipHiRezcrv = upLipHiRezcrv
        self.upLipZippercrv = upLipZippercrv
        self.lowLipLowRezcrv = lowLipLowRezcrv
        self.lowLipHiRezcrv = lowLipHiRezcrv
        self.lowLipMedRezcrv = lowLipMedRezcrv
        self.lowLipZippercrv  = lowLipZippercrv
        self.upBindJnts = upBindJnts
        self.lowBindJnts = lowBindJnts
        self.numJnts = numJnts

        super(Lips, self).__init__(**kwargs)

    def build(self):
        super(Lips, self).build()
        # duplicate some stuff
        # duplicateCurves
        todup = [self.upLipLowRezcrv,self.upLipMedRezcrv,self.upLipHiRezcrv,self.upLipZippercrv,
                                self.lowLipLowRezcrv,self.lowLipMedRezcrv,self.lowLipHiRezcrv,self.lowLipZippercrv]

        for i in todup:
            output = trsLib.duplicate(i, search = 'local',replace = '',hierarchy = True )
            mc.move(0,-20, 0, output, r = True, ws = True)

        # duplicateZipBindJoints
        for i in range(2):
            output = trsLib.duplicate(self.upBindJnts[i-1], search = 'local',replace = '' )
            mc.move(0,-20, 0, output, r = True, ws = True)
        for i in range(2):
            output = trsLib.duplicate(self.lowBindJnts[i-1], search = 'local',replace = '')
            mc.move(0,-20, 0, output, r = True, ws = True)

        # delete stuf under notuchy
        for i in [self.upLipJntLocLowGrp,self.jntLocMedUp,self.jntLocHiUp,self.lowLipJntLocLowGrp,
                  self.jntLocMedLow,self.jntLocHiLow,'UpLipZipperTargetloc_GRP','LowLipZipperTargetloc_GRP']:
            i = self.cln(i)
            i = i.split('|')[-1]
            children = mc.listRelatives(i, children=True)
            mc.delete(children)

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

        #connect mouth squash driver loc to the mouthsquash ctlGrp
        connect.remapVal(self.mouthSquashDrvrLoc + '.ty', self.upsquashCtlMakro + '.ty', inputMin= 0,
                         inputMax =3.572,outputMin = 0,outputMax= 5.8, name = 'upLip_mouthSquashCtrlCo_RMV')

        connect.remapVal(self.mouthSquashDrvrLoc + '.ty', self.lowsquashCtlMakro + '.ty', inputMin= 0,
                         inputMax =3.572,outputMin = 0,outputMax= -5.8, name = 'lowLip_mouthSquashCtrlCo_RMV')

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
        funcs.connectBndZip(locali = True,leftLowCornerCtl=self.leftLowCornerCtl, rightLowCornerCtl=self.rightLowCornerCtl,
                       lowZipJnts=self.lowZipJnts, lowMicroJnts=self.lowMicroJnts,
                      leftUpCornerCtl=self.leftUpCornerCtl, rightUpCornerCtl=self.rightUpCornerCtl,
                     upZipJnts=self.upZipJnts, upMicroJnts=self.upMicroJnts)

        # connect the  micro controls to the local control
        for i in self.microUpCtls:
            [mc.connectAttr(self.cln(i) + '.{}{}'.format(t,a), i + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']
        for i in self.microLowCtls:
            [mc.connectAttr(self.cln(i) + '.{}{}'.format(t,a), i + '.{}{}'.format(t,a))for t in 'tr' for a in'xyz']

        funcs.drivenCornerLip(leftUpCtl=self.leftUpCornerCtl, leftLowCtl=self.leftLowCornerCtl,
                              rightUpCtl=self.rightUpCornerCtl,rightLowCtl=self.rightLowCornerCtl,
                              leftUpLoc=self.l_upLipCornerMod_loc, leftLowLoc=self.l_lowLipCornerMod_loc,
                              rightUpLoc=self.r_upLipCornerMod_loc, rightLowLoc=self.r_lowLipCornerMod_loc)

        # connect minor corner control to the corner bind loc
        [mc.connectAttr(self.leftUpMinorCornerCtl + '.{}{}'.format(t, a), self.l_upLip_cornerbnd + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.rightUpMinorCornerCtl + '.{}{}'.format(t, a), self.r_upLip_cornerbnd + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.leftLowMinorCornerCtl + '.{}{}'.format(t, a), self.l_lowLip_cornerbnd + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.rightLowMinorCornerCtl + '.{}{}'.format(t, a), self.r_lowLip_cornerbnd + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']

        # connect locator under squash transform to the joint Mid loc
        [mc.connectAttr(self.upJntCtlLoc+ '.{}{}'.format(t, a), self.upLipJntMidLoc+ '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']
        [mc.connectAttr(self.lowJntCtlLoc+ '.{}{}'.format(t, a), self.lowLipJntMidLoc+ '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']

        # connect locator under lip corner makro group to the lip corner joint
        leftRemapCornerMakro = connect.remapVal(self.l_cornerMakroLoc + '.ty',self.upLipLowRezBindJnts[2] + '.tz', name = 'L_lipCornerTZ_MAKRO',
                         inputMin = 0, inputMax=-6, outputMin=0, outputMax=-3)
        rightRemapCornerMakro = connect.remapVal(self.r_cornerMakroLoc + '.ty',self.upLipLowRezBindJnts[0] + '.tz', name = 'R_lipCornerTZ_MAKRO',
                         inputMin = 0, inputMax=-6, outputMin=0, outputMax=-3)

        mc.connectAttr(leftRemapCornerMakro + '.outValue',self.lowLipLowRezBindJnts[2] + '.tz')
        mc.connectAttr(rightRemapCornerMakro + '.outValue',self.lowLipLowRezBindJnts[0] + '.tz')

        rightUpSquash = connect.remapVal(self.mouthSquashDrvrLoc + '.ty',self.upSquashMak + '.ty', name = 'upLip_mouthSquashCtlCorr',
                         inputMin = 0, inputMax=3.527, outputMin=0, outputMax=5.8)

        rightUpSquash = connect.remapVal(self.mouthSquashDrvrLoc + '.ty',self.lowSquashMak+ '.ty', name = 'lowLip_mouthSquashCtlCorr',
                         inputMin = 0, inputMax=3.527, outputMin=0, outputMax=-6.5)

        # connect up mid lip ctl to the up lip jnt ctl loc
        for i in [self.uplipctl, self.lowlipctl,self.upJntCtlLoc, self.lowJntCtlLoc,self.cln(self.upJntCtlLoc),
                  self.cln(self.lowJntCtlLoc),self.cln(self.uplipctl),self.cln(self.lowlipctl)]:
            attrLib.addFloat(i, ln = 'lipRoll', dv = 0)

        for i in [self.uplipctl, self.lowlipctl,self.cln(self.uplipctl),self.cln(self.lowlipctl)]:
            attrLib.addFloat(i, ln = 'puff', dv = 0)
            attrLib.addFloat(i, ln = 'press', dv = 0)
            attrLib.addFloat(i, ln = 'squash', dv = 0)



        upCrvCompension = mc.createNode('multiplyDivide', name = 'upLip_CrvCompensation_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(upCrvCompension + '.' + i, 1.39)
        mc.connectAttr(self.uplipctl + '.translate', upCrvCompension + '.input1')
        mc.connectAttr(upCrvCompension + '.output', self.upJntCtlLoc + '.translate')

        upLipRollRev = mc.createNode('multiplyDivide', name = 'upLipRollReverse_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(upLipRollRev + '.' + i, -1)
        mc.connectAttr(self.uplipctl + '.lipRoll', upLipRollRev + '.input1X')
        mc.connectAttr(upLipRollRev + '.outputX', self.upJntCtlLoc + '.lipRoll')
        [mc.connectAttr(self.uplipctl + '.{}{}'.format(t, a), self.upJntCtlLoc + '.{}{}'.format(t, a)) for t in 'rs' for a in 'xyz']


        lowCrvCompension = mc.createNode('multiplyDivide', name = 'lowLip_CrvCompensation_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(lowCrvCompension + '.' + i, 1.39)
        mc.connectAttr(self.lowlipctl + '.translate', lowCrvCompension + '.input1')
        mc.connectAttr(lowCrvCompension + '.output', self.lowJntCtlLoc + '.translate')
        mc.connectAttr(self.lowlipctl + '.lipRoll', self.lowJntCtlLoc + '.lipRoll')
        [mc.connectAttr(self.lowlipctl + '.{}{}'.format(t, a), self.lowJntCtlLoc + '.{}{}'.format(t, a)) for t in 'rs' for a in 'xyz']

        #connect mid ctls to the local mid ctls
        [mc.connectAttr(self.cln(self.uplipctl) + '.{}{}'.format(t, a), self.uplipctl + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.cln(self.lowlipctl) + '.{}{}'.format(t, a), self.lowlipctl + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']

        for i in ['puff', 'press', 'squash', 'lipRoll']:
            mc.connectAttr(self.cln(self.uplipctl) + '.' + i,self.uplipctl + '.' + i)
            mc.connectAttr(self.cln(self.lowlipctl) + '.' + i,self.lowlipctl + '.' + i)

        # connect lip corner control to the local corner controls
        for i in [self.cln(self.leftUpCornerCtl), self.cln(self.rightUpCornerCtl),
                  self.cln(self.rightLowCornerCtl),self.cln(self.leftLowCornerCtl)]:
            attrLib.addFloat(i, ln = 'zip', min = 0,dv = 0)
            attrLib.addFloat(i, ln = 'Z', dv = 0)
            attrLib.addFloat(i, ln = 'puff', min = -10, max = 10,dv = 0)

        [mc.connectAttr(self.cln(self.leftUpCornerCtl) + '.{}{}'.format(t, a), self.leftUpCornerCtl + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']
        [mc.connectAttr(self.cln(self.leftLowCornerCtl) + '.{}{}'.format(t, a), self.leftLowCornerCtl + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']
        [mc.connectAttr(self.cln(self.rightUpCornerCtl) + '.{}{}'.format(t, a), self.rightUpCornerCtl + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']
        [mc.connectAttr(self.cln(self.rightLowCornerCtl) + '.{}{}'.format(t, a), self.rightLowCornerCtl + '.{}{}'.format(t, a)) for t in 't' for a in 'xy']
        for i,j in zip([self.cln(self.leftUpCornerCtl), self.cln(self.leftLowCornerCtl),self.cln(self.rightUpCornerCtl), self.cln(self.rightLowCornerCtl)]
                        ,[self.leftUpCornerCtl,self.leftLowCornerCtl, self.rightUpCornerCtl,self.rightLowCornerCtl]):
            mc.connectAttr(i + '.Z', j + '.Z')
            mc.connectAttr(i + '.zip', j + '.zip')
            mc.connectAttr(i + '.puff', j + '.puff')
            attrLib.lockHideAttrs(i, ['rx','ry','rz','tz'] ,lock = True, hide = True)
            attrLib.lockHideAttrs(j, ['rx','ry','rz','tz'] ,lock = True, hide = True)

        # connect minor corner controls to the local minor controls
        for i,j in zip([self.cln(self.leftUpMinorCornerCtl), self.cln(self.leftLowMinorCornerCtl),
                        self.cln(self.rightUpMinorCornerCtl),  self.cln(self.rightLowMinorCornerCtl)],
                       [self.leftUpMinorCornerCtl,self.leftLowMinorCornerCtl,  self.rightUpMinorCornerCtl,
                        self.rightLowMinorCornerCtl]):
            mc.connectAttr(i + '.' + 'tx', j + '.' + 'tx')
            mc.connectAttr(i + '.' + 'ty', j + '.' + 'ty')
            mc.connectAttr(i + '.' + 'tz', j + '.' + 'tz')
            attrLib.lockHideAttrs(i, ['rx','ry','rz'] ,lock = True, hide = True)
            attrLib.lockHideAttrs(j, ['rx','ry','rz'] ,lock = True, hide = True)

        # connect mid lip ctls to the roll locator undr lip ctl group
        for i,j in zip([self.uplipctl,self.lowlipctl],[self.upRoll_loc,self.lowRoll_loc]):
            mc.pointConstraint(i,j, mo = True)
            unit = mc.shadingNode('unitConversion', asUtility=True)
            mc.setAttr(unit + '.conversionFactor', 0.017)
            mc.connectAttr(i + '.lipRoll', unit + '.input')
            mc.connectAttr(unit + '.output', j + '.rx')

        # connect the rotate of mid ctls to the mid roll loc rotation
        [mc.connectAttr(self.uplipctl + '.{}{}'.format(t, a), self.upMidRollLoc + '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']
        [mc.connectAttr(self.lowlipctl + '.{}{}'.format(t, a), self.lowMidRollLoc + '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']

        #  create locs on global curves
        # move transforms above global locators that drives by the curves
        for i in [self.cln(self.jntLocHiUp),self.cln(self.jntLocHiLow),self.cln(self.upLipJntLocLowGrp),self.cln(self.lowLipJntLocLowGrp),
                  self.cln(self.jntLocMedUp),self.cln(self.jntLocMedLow),'UpLipZipperTargetloc_GRP','LowLipZipperTargetloc_GRP',]:
         mc.move( 0, 20, 0,i, r = True, ws = True)


        poses = [self.cln(i)for i in self.upLipLowRezBindJnts]
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.upLipJntLocLowGrp), numLocs = 3,
                                  crv = self.cln(self.upLipLowRezcrv), upCurve = self.tempCurve, paramStart = 0.8,paramEnd = 0.3,
                                  upAxis = 'y', posJnts = poses)
        # rename transfomrs that driven by uplowRezCrv
        self.l_UpLipDriverOutMod = mc.rename(tempList[0], 'L_UpLipDriverOutModify_LOC')
        self.m_UpLipDriverOutMod = mc.rename(tempList[1], 'm_UpLipDriverOutModify_LOC')
        self.r_UpLipDriverOutMod = mc.rename(tempList[2], 'r_UpLipDriverOutModify_LOC')

        poses = [self.cln(i)for i in self.lowLipLowRezBindJnts]
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.lowLipJntLocLowGrp), numLocs = 3,
                                  crv = self.cln(self.lowLipLowRezcrv), upCurve = self.tempCurve, paramStart = 0.8,paramEnd = 0.3,
                                  upAxis = 'y', posJnts = poses)

        # rename transfomrs that driven by lowlowRezCrv
        self.l_LowLipDriverOutMod = mc.rename(tempList[0], 'L_LowLipDriverOutModify_LOC')
        self.m_LowLipDriverOutMod = mc.rename(tempList[1], 'm_LowLipDriverOutModify_LOC')
        self.r_LowLipDriverOutMod = mc.rename(tempList[2], 'r_LowLipDriverOutModify_LOC')

        tempJnts = jntLib.create_on_curve(self.cln(self.upLipMedRezcrv), numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.jntLocMedUp), numLocs = 7, crv = self.cln(self.upLipMedRezcrv),
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.upSecModGlob = mc.rename(tempList[0],'L_UpLipMicroOutSecondaryModify_LOC')
        self.upmicroOutModGlob = mc.rename(tempList[1],'L_UpLipMicroOutModify_LOC')
        self.upmidSecModGlob = mc.rename(tempList[2],'L_UpLipMicroMidSecondaryModify_LOC')
        self.upMidModGlob = mc.rename(tempList[3],'UpLipMicroMidModify_LOC')
        self.upMidSecModLocGlob = mc.rename(tempList[4],'R_UpLipMicroMidSecondaryModify_LOC')
        self.microOutModLocUpGlob = mc.rename(tempList[5],'R_UpLipMicroOutModify_LOC')
        self.microOutSecModUpGlob = mc.rename(tempList[6],'R_UpLipMicroOutSecondaryModify_LOC')

        tempJnts = jntLib.create_on_curve(self.cln(self.lowLipMedRezcrv), numOfJoints = 7, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.jntLocMedLow), numLocs = 7, crv = self.cln(self.lowLipMedRezcrv),
                     upCurve = self.tempCurve, paramStart = 0.95,paramEnd = 0.15, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.lowSecModGlob = mc.rename(tempList[0],'L_LowLipMicroOutSecondaryModify_LOC')
        self.lowmicroOutModGlob = mc.rename(tempList[1],'L_LowLipMicroOutModify_LOC')
        self.lowmidSecModGlob = mc.rename(tempList[2],'L_LowLipMicroMidSecondaryModify_LOC')
        self.lowMidModGlob = mc.rename(tempList[3],'LowLipMicroMidModify_LOC')
        self.lowMidSecModLocGlob = mc.rename(tempList[4],'R_LowLipMicroMidSecondaryModify_LOC')
        self.microOutModLocLowGlob = mc.rename(tempList[5],'R_LowLipMicroOutModify_LOC')
        self.microOutSecModLowGlob = mc.rename(tempList[6],'R_LowLipMicroOutSecondaryModify_LOC')


        tempJnts = jntLib.create_on_curve(self.cln(self.upLipHiRezcrv), numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.jntLocHiUp), numLocs = 2, crv = self.cln(self.upLipHiRezcrv),
                     upCurve = self.tempCurve, paramStart = 0.97,paramEnd = 0.95, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.l_outUpTerModLocHiGlob = mc.rename(tempList[0], 'L_UpLipMicroOutTertiaryModify_LOC')
        self.r_outUpTerModLocHiGlob = mc.rename(tempList[1], 'R_UpLipMicroOutTertiaryModify_LOC')

        tempJnts = jntLib.create_on_curve(self.cln(self.lowLipHiRezcrv), numOfJoints = 2, parent = False, description='C_base', radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.cln(self.jntLocHiLow), numLocs = 2, crv = self.cln(self.lowLipHiRezcrv),
                     upCurve = self.tempCurve, paramStart = 0.97,paramEnd = 0.95, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        self.l_outLowTerModLocHiGlob = mc.rename(tempList[0], 'L_LowLipMicroOutTertiaryModify_LOC')
        self.r_outLowTerModLocHiGlob = mc.rename(tempList[1], 'R_LowLipMicroOutTertiaryModify_LOC')


        tempJnts = jntLib.create_on_curve(self.cln(self.upLipZippercrv), numOfJoints = 9, parent = False, description='C_base', radius = 0.1)
        upTargets = funcs.locOnCrv(name='result', parent='UpLipZipperTargetloc_GRP', numLocs=9, crv=self.cln(self.upLipZippercrv),
                            upCurve=self.tempCurve, paramStart=0.97, paramEnd=0.118, upAxis='y', posJnts=tempJnts)
        mc.delete(tempJnts)
        upZipJnts = [self.cln(i)for i in self.upZipJnts]
        for i,j in zip(upTargets,upZipJnts):
            mc.pointConstraint(i, j, mo = True)
        self.upZipOutLoc = mc.rename(upTargets[0], 'L_UpLipZipOutTertiary_LOC')
        self.upZipOutSecLoc = mc.rename(upTargets[1], 'L_UpLipZipOutSecondary_LOC')
        self.upRotDrvLoc = mc.rename(upTargets[2], 'L_UpLipOut_RotDrive_LOC')
        self.upZipMidSecLocleft = mc.rename(upTargets[3], 'L_UpLipZipMidSecondary_LOC')
        self.upMidLipDrvLoc = mc.rename(upTargets[4], 'C_UpLipDriverMid_LOC')
        self.upZipMidSecLocright = mc.rename(upTargets[5], 'R_UpLipZipMidSecondary_LOC')
        self.upLipZipOutLocRight = mc.rename(upTargets[6], 'R_UpLipZipOut_LOC')
        self.upLipZipOutSecLocRight = mc.rename(upTargets[7], 'R_UpLipZipOutSecondary_LOC')
        self.upLipZipOutTerLocRight = mc.rename(upTargets[8], 'R_UpLipZipOutTertiary_LOC')

        tempJnts = jntLib.create_on_curve(self.cln(self.lowLipZippercrv), numOfJoints = 9, parent = False, description='C_base', radius = 0.1)
        lowTargets = funcs.locOnCrv(name='result', parent='LowLipZipperTargetloc_GRP', numLocs=9, crv=self.cln(self.lowLipZippercrv),
                            upCurve=self.tempCurve, paramStart=0.97, paramEnd=0.118, upAxis='y', posJnts=tempJnts)
        mc.delete(tempJnts)
        lowZipJnts = [self.cln(i)for i in self.lowZipJnts]
        for i,j in zip(lowTargets,lowZipJnts):
            mc.pointConstraint(i, j, mo = True)
        self.lowZipOutLoc = mc.rename(lowTargets[0], 'L_LowLipZipOutTertiary_LOC')
        self.lowZipOutSecLoc = mc.rename(lowTargets[1], 'L_LowLipZipOutSecondary_LOC')
        self.lowRotDrvLoc = mc.rename(lowTargets[2], 'L_LowLipOut_RotDrive_LOC')
        self.lowZipMidSecLocleft = mc.rename(lowTargets[3], 'L_LowLipZipMidSecondary_LOC')
        self.lowMidLipDrvLoc = mc.rename(lowTargets[4], 'C_LowLipDriverMid_LOC')
        self.lowZipMidSecLocright = mc.rename(lowTargets[5], 'R_LowLipZipMidSecondary_LOC')
        self.lowLipZipOutLocRight = mc.rename(lowTargets[6], 'R_LowLipZipOut_LOC')
        self.lowLipZipOutSecLocRight = mc.rename(lowTargets[7], 'R_LowLipZipOutSecondary_LOC')
        self.lowLipZipOutTerLocRight = mc.rename(lowTargets[8], 'R_LowLipZipOutTertiary_LOC')

        # parent constraint locators on the curves to the transforms on top of global controls
        for i,j in zip([self.cln(self.l_UpLipDriverOutMod),self.cln(self.m_UpLipDriverOutMod),self.cln(self.r_UpLipDriverOutMod)],
                        [self.cln(self.l_localUpLipOutOrient_GRP),self.cln(self.m_localUpLipOutOrient_GRP), self.cln(self.r_localUpLipOutOrient_GRP)]):
            mc.parentConstraint(i, j , mo = True)
        for i,j in zip([self.cln(self.l_LowLipDriverOutMod),self.cln(self.m_LowLipDriverOutMod),self.cln(self.r_LowLipDriverOutMod)],
                        [self.cln(self.l_localLowLipOutOrient_GRP),self.cln(self.m_localLowLipOutOrient_GRP), self.cln(self.r_localLowLipOutOrient_GRP)]):
            mc.parentConstraint(i, j , mo = True)

        for i, j in zip([self.upSecModGlob,self.upmicroOutModGlob,self.upmidSecModGlob,self.upMidModGlob,
                      self.upMidSecModLocGlob,self.microOutModLocUpGlob,self.microOutSecModUpGlob,
                      self.cln(self.l_outUpTerModLocHi),self.cln(self.r_outUpTerModLocHi)],
                     [self.cln(self.upTerOrientGrp[1]),self.cln(self.upZipOutBndGrp[0]),self.cln(self.upTerOrientGrp[2]),
                      self.cln(self.upZipOutBndGrp[1]),self.cln(self.upTerOrientGrp[3]),self.cln(self.upZipOutBndGrp[2]),
                      self.cln(self.upTerOrientGrp[4]),self.cln(self.upTerOrientGrp[0]),self.cln(self.upTerOrientGrp[5])]):
            mc.parentConstraint(i, j, mo = True )

        for i, j in zip([self.lowSecModGlob,self.lowmicroOutModGlob,self.lowmidSecModGlob,self.lowMidModGlob,
                      self.lowMidSecModLocGlob,self.microOutModLocLowGlob,self.microOutSecModLowGlob,
                      self.cln(self.l_outLowTerModLocHi),self.cln(self.r_outLowTerModLocHi)],
                     [self.cln(self.lowTerOrientGrp[1]),self.cln(self.lowZipOutBndGrp[0]),self.cln(self.lowTerOrientGrp[2]),
                      self.cln(self.lowZipOutBndGrp[1]),self.cln(self.lowTerOrientGrp[3]),self.cln(self.lowZipOutBndGrp[2]),
                      self.cln(self.lowTerOrientGrp[4]),self.cln(self.lowTerOrientGrp[0]),self.cln(self.lowTerOrientGrp[5])]):
            mc.parentConstraint(i, j, mo = True )

        # skin joints to the global curves
        uplowrezBindJnts = [self.cln(i)for i in self.upLipLowRezBindJnts]
        upmedrezBindJnts = [self.cln(i)for i in self.upmedRezBindJnts]
        lowlowrezBindJnts = [self.cln(i)for i in self.lowLipLowRezBindJnts]
        lowmedrezBindJnts = [self.cln(i)for i in self.lowmedRezBindJnts]
        uphirezBindJnts = [self.cln(i)for i in self.upHirzBndJnts]
        lowhirezBindJnts = [self.cln(i)for i in self.lowHirzBndJnts]
        upZipperBindJnts = [self.cln(i)for i in self.upBindJnts]
        lowZipperBindJnts = [self.cln(i)for i in self.lowBindJnts]

        deformLib.bind_geo(geos = self.cln(self.upLipLowRezcrv), joints = uplowrezBindJnts)
        deformLib.bind_geo(geos = self.cln(self.upLipMedRezcrv), joints = upmedrezBindJnts)
        #bind joints to low lowrez and medrez curves
        deformLib.bind_geo(geos = self.cln(self.lowLipLowRezcrv), joints = lowlowrezBindJnts)
        deformLib.bind_geo(geos = self.cln(self.lowLipMedRezcrv), joints = lowmedrezBindJnts)
        # bind joints to the up highrez Curves
        deformLib.bind_geo(geos = self.cln(self.upLipHiRezcrv), joints = uphirezBindJnts)
        # bind joints to the low highrez Curves
        deformLib.bind_geo(geos = self.cln(self.lowLipHiRezcrv), joints = lowhirezBindJnts)
        # bind joints to the up Zipper Curves
        deformLib.bind_geo(geos = self.cln(self.upLipZippercrv), joints = upZipperBindJnts)
        # bind joints to the low zipper Curves
        deformLib.bind_geo(geos = self.cln(self.lowLipZippercrv), joints = lowZipperBindJnts)


        # connect up micro controls to the locator above the bind jnts
        microUpCtl = [self.cln(i)for i in self.microUpCtls]
        upLocMod = [self.cln(i)for i in self.upLocMod]
        microLowCtl = [self.cln(i)for i in self.microLowCtls]
        upLowMod = [self.cln(i)for i in self.lowLocMod]
        for ctl,loc in zip(microUpCtl,upLocMod):
            [mc.connectAttr(ctl + '.{}{}'.format(t, a),loc + '.{}{}'.format(t, a)) for t in 'trs' for a in 'xyz']

        # connect low micro controls to the locator above the bind jnts
        for ctl,loc in zip(microLowCtl,upLowMod):
            [mc.connectAttr(ctl + '.{}{}'.format(t, a),loc + '.{}{}'.format(t, a)) for t in 'trs' for a in 'xyz']

        # connect stuff to the global zip joints
        lowZipJnts = [self.cln(i)for i in self.lowZipJnts]
        upZipJnts = [self.cln(i)for i in self.upZipJnts]
        lowMicroJnts = [self.cln(i)for i in self.lowMicroJnts]
        upMicroJnts = [self.cln(i)for i in self.upMicroJnts]

        funcs.connectBndZip(locali = False,leftLowCornerCtl=self.cln(self.leftLowCornerCtl),
                            rightLowCornerCtl=self.cln(self.rightLowCornerCtl),
                            lowZipJnts=lowZipJnts, lowMicroJnts=lowMicroJnts,
                            leftUpCornerCtl=self.leftUpCornerCtl, rightUpCornerCtl=self.rightUpCornerCtl,
                            upZipJnts=upZipJnts, upMicroJnts= upMicroJnts)

        # set driven for corner joints
        funcs.drivenCornerLip(leftUpCtl=self.cln(self.leftUpCornerCtl), leftLowCtl=self.cln(self.leftLowCornerCtl),
                              rightUpCtl=self.cln(self.rightUpCornerCtl),rightLowCtl=self.cln(self.rightLowCornerCtl),
                              leftUpLoc=self.cln(self.l_upLipCornerMod_loc), leftLowLoc=self.cln(self.l_lowLipCornerMod_loc),
                              rightUpLoc=self.cln(self.r_upLipCornerMod_loc), rightLowLoc=self.cln(self.r_lowLipCornerMod_loc))
        # connect minor corner control to the corner bind loc
        [mc.connectAttr(self.cln(self.leftUpMinorCornerCtl) + '.{}{}'.format(t, a), self.cln(self.l_upLip_cornerbnd) + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.cln(self.rightUpMinorCornerCtl) + '.{}{}'.format(t, a), self.cln(self.r_upLip_cornerbnd) + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.cln(self.leftLowMinorCornerCtl) + '.{}{}'.format(t, a), self.cln(self.l_lowLip_cornerbnd) + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']
        [mc.connectAttr(self.cln(self.rightLowMinorCornerCtl) + '.{}{}'.format(t, a), self.cln(self.r_lowLip_cornerbnd) + '.{}{}'.format(t, a)) for t in 'tr' for a in 'xyz']

        # connect locator under lip corner makro group to the lip corner joint
        leftRemapCornerMakroGlob = connect.remapVal(self.cln(self.l_cornerMakroLoc) + '.ty',self.cln(self.upLipLowRezBindJnts[2]) + '.tz',
                                                    name = 'L_lipCornerTZ_MAKROGlob',
                         inputMin = 0, inputMax=-6, outputMin=0, outputMax=-3)
        rightRemapCornerMakroGlob = connect.remapVal(self.cln(self.r_cornerMakroLoc) + '.ty',self.cln(self.upLipLowRezBindJnts[0]) + '.tz',
                                                     name = 'R_lipCornerTZ_MAKROGlob',
                         inputMin = 0, inputMax=-6, outputMin=0, outputMax=-3)

        mc.connectAttr(leftRemapCornerMakroGlob + '.outValue',self.cln(self.lowLipLowRezBindJnts[2]) + '.tz')
        mc.connectAttr(rightRemapCornerMakroGlob + '.outValue',self.cln(self.lowLipLowRezBindJnts[0]) + '.tz')

        rightUpSquashGlob = connect.remapVal(self.cln(self.mouthSquashDrvrLoc) + '.ty',self.cln(self.upSquashMak) + '.ty',
                                             name = 'upLip_mouthSquashCtlCorrGlob',
                         inputMin = 0, inputMax=3.527, outputMin=0, outputMax=5.8)

        rightUpSquashGlob = connect.remapVal(self.cln(self.mouthSquashDrvrLoc) + '.ty',self.cln(self.lowSquashMak)+ '.ty',
                                             name = 'lowLip_mouthSquashCtlCorrGlob',
                         inputMin = 0, inputMax=3.527, outputMin=0, outputMax=-6.5)

        # connect up mid lip ctl to the up lip jnt ctl loc Glob
        upCrvCompensionGlob = mc.createNode('multiplyDivide', name = 'upLip_CrvCompensationGlob_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(upCrvCompensionGlob + '.' + i, 1.39)
        mc.connectAttr(self.cln(self.uplipctl) + '.translate', upCrvCompensionGlob + '.input1')
        mc.connectAttr(upCrvCompensionGlob + '.output', self.cln(self.upJntCtlLoc) + '.translate')

        upLipRollRevGlob = mc.createNode('multiplyDivide', name = 'upLipRollReverseGlob_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(upLipRollRevGlob + '.' + i, -1)
        mc.connectAttr(self.cln(self.uplipctl) + '.lipRoll', upLipRollRevGlob + '.input1X')
        mc.connectAttr(upLipRollRevGlob + '.outputX', self.cln(self.upJntCtlLoc) + '.lipRoll')
        [mc.connectAttr(self.cln(self.uplipctl) + '.{}{}'.format(t, a), self.cln(self.upJntCtlLoc) + '.{}{}'.format(t, a)) for t in 'rs' for a in 'xyz']

        lowCrvCompensionGlob = mc.createNode('multiplyDivide', name = 'lowLip_CrvCompensationGlob_MDN')
        for i in ['input2X', 'input2Y', 'input2Z']:
            mc.setAttr(lowCrvCompensionGlob + '.' + i, 1.39)
        mc.connectAttr(self.cln(self.lowlipctl) + '.translate', lowCrvCompensionGlob + '.input1')
        mc.connectAttr(lowCrvCompensionGlob + '.output', self.cln(self.lowJntCtlLoc) + '.translate')
        mc.connectAttr(self.cln(self.lowlipctl) + '.lipRoll', self.cln(self.lowJntCtlLoc) + '.lipRoll')
        [mc.connectAttr(self.cln(self.lowlipctl) + '.{}{}'.format(t, a), self.cln(self.lowJntCtlLoc) + '.{}{}'.format(t, a)) for t in 'rs' for a in 'xyz']

        # connect the locator under ctl placement to the locator under up roll modify global
        attrLib.addFloat(self.cln(self.upJntCtlLoc), ln = 'lipRoll', dv = 0)
        mc.pointConstraint(self.cln(self.upJntCtlLoc),self.cln(self.jntUpRollLoc), mo = True)
        unit = mc.shadingNode('unitConversion', asUtility = True )
        mc.setAttr(unit + '.conversionFactor', 0.017)
        mc.connectAttr(self.cln(self.upJntCtlLoc) + '.lipRoll', unit+ '.input')
        mc.connectAttr(unit + '.output', self.cln(self.jntUpRollLoc)+ '.rx')

        # connect the locator under ctl placement to the locator under low roll modify
        attrLib.addFloat(self.cln(self.lowJntCtlLoc), ln = 'lipRoll', dv = 0)
        mc.pointConstraint(self.cln(self.lowJntCtlLoc),self.cln(self.jntLowRollLoc), mo = True)
        unit = mc.shadingNode('unitConversion', asUtility = True )
        mc.setAttr(unit + '.conversionFactor', 0.017)
        mc.connectAttr(self.cln(self.lowJntCtlLoc) + '.lipRoll', unit+ '.input')
        mc.connectAttr(unit + '.output', self.cln(self.jntLowRollLoc)+ '.rx')

        # connect locator under squash transform to the joint Mid loc
        [mc.connectAttr(self.cln(self.upJntCtlLoc)+ '.{}{}'.format(t, a), self.cln(self.upLipJntMidLoc)+ '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']
        [mc.connectAttr(self.cln(self.lowJntCtlLoc)+ '.{}{}'.format(t, a), self.cln(self.lowLipJntMidLoc) + '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']

        # parent constraint one of locators under roll modify to the up transform above mid main jnt
        mc.parentConstraint(self.cln(self.upLipJntMidLoc),self.cln(self.middleUpMainMod), mo = True)
        # parent constraint one of locators under roll modify to the low transform above mid main jnt
        mc.parentConstraint(self.cln(self.lowLipJntMidLoc),self.cln(self.midLowMainMod), mo = True)

        #connect mouth squash driver loc to the mouthsquash ctlGrp global
        self.upsquashCtlMakro = self.upsquashCtlMakro.split('|')[-1]
        self.lowsquashCtlMakro = self.lowsquashCtlMakro.split('|')[-1]
        connect.remapVal(self.cln(self.mouthSquashDrvrLoc) + '.ty', self.cln(self.upsquashCtlMakro) + '.ty', inputMin= 0,
                         inputMax =3.572,outputMin = 0,outputMax= 5.8, name = 'upLip_mouthSquashCtrlCo_RMV')

        connect.remapVal(self.cln(self.mouthSquashDrvrLoc) + '.ty', self.cln(self.lowsquashCtlMakro) + '.ty', inputMin= 0,
                         inputMax =3.572,outputMin = 0,outputMax= -5.8, name = 'lowLip_mouthSquashCtrlCo_RMV')

        # connect mid lip ctls to the roll locator undr lip ctl group
        for i,j in zip([self.cln(self.uplipctl),self.cln(self.lowlipctl)],[self.cln(self.upRoll_loc),self.cln(self.lowRoll_loc)]):
            mc.pointConstraint(i,j, mo = True)
            unit = mc.shadingNode('unitConversion', asUtility=True)
            mc.setAttr(unit + '.conversionFactor', 0.017)
            mc.connectAttr(i + '.lipRoll', unit + '.input')
            mc.connectAttr(unit + '.output', j + '.rx')

        # connect the rotate of mid ctls to the mid roll loc rotation
        [mc.connectAttr(self.cln(self.uplipctl) + '.{}{}'.format(t, a), self.cln(self.upMidRollLoc) + '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']
        [mc.connectAttr(self.cln(self.lowlipctl) + '.{}{}'.format(t, a), self.cln(self.lowMidRollLoc) + '.{}{}'.format(t, a)) for t in 'r' for a in 'xyz']

        # connect upCorner controls to the lower corner controls
        for i in ['tx', 'ty', 'visibility','rotateOrder', 'zip', 'Z', 'puff']:
            mc.connectAttr(self.cln(self.leftUpCornerCtl) + '.' + i, self.cln(self.leftLowCornerCtl) + '.' + i)
            mc.connectAttr(self.cln(self.rightUpCornerCtl) + '.' + i, self.cln(self.rightLowCornerCtl) + '.' + i)

        #**********************************************************blendShapes*********************************************************
        mouthbls = mc.blendShape(self.geo, frontOfChain=True, n='mouth_bShp')[0]
        for i in ['L_CI','R_CI','L_CO','L_CD','L_CU','MODriver','R_CO','R_CD','R_CU','upLipPress','lowLipPress',
                  'upLipPuff','lowLipPuff','L_cheekPuff','R_cheekPuff','L_nostrilUp','R_nostrilUp','L_crowsFeet',
                  'R_crowsFeet','uplipThicken','lowLipThicken','upLipThin','lowLipThin','lowLipRollFwdCorr60',
                  'upLipRollFwdCorr60','upLipRollBackCorr60','lowLipRollBackCorr60',]:
            deformLib.blendShapeTarget(self.geo, i, mouthbls)

        upLowRezbls = mc.blendShape(self.upLipLowRezcrv, frontOfChain=True, n='upLowRezCrv_correcriveSneer_bShp')[0]
        lowLowRezbls = mc.blendShape(self.lowLipLowRezcrv, frontOfChain=True, n='lowLowRezCrv_correcriveSneer_bShp')[0]
        upLowRezblsGlob = mc.blendShape(self.cln(self.upLipLowRezcrv), frontOfChain=True, n='upGlobLowRezCrv_correcriveSneer_bShp')[0]
        lowLowRezblsGlob = mc.blendShape(self.cln(self.lowLipLowRezcrv), frontOfChain=True, n='lowGlobLowRezCrv_correcriveSneer_bShp')[0]

        for i in ['L_CornerIn6','R_CornerIn6','L_CornerOut10','R_CornerOut10']:
            deformLib.blendShapeTarget(self.upLipLowRezcrv, i, upLowRezbls)
            deformLib.blendShapeTarget(self.lowLipLowRezcrv, i, lowLowRezbls)
            deformLib.blendShapeTarget(self.cln(self.upLipLowRezcrv), i, upLowRezblsGlob)
            deformLib.blendShapeTarget(self.cln(self.lowLipLowRezcrv), i, lowLowRezblsGlob)

        upMedRezbls = mc.blendShape(self.upLipMedRezcrv, frontOfChain=True, n='upMedRezCrv_correcriveSneer_bShp')[0]
        lowMedRezbls = mc.blendShape(self.lowLipMedRezcrv, frontOfChain=True, n='lowMedRezCrv_correcriveSneer_bShp')[0]
        upMedRezblsGlob = mc.blendShape(self.cln(self.upLipMedRezcrv), frontOfChain=True, n='upGlobMedRezCrv_correcriveSneer_bShp')[0]
        lowMedRezblsGlob = mc.blendShape(self.cln(self.lowLipMedRezcrv), frontOfChain=True, n='lowGlobMedRezCrv_correcriveSneer_bShp')[0]

        for i in ['L_MedCornerIn6','R_MedCornerIn6','L_MedCornerOut20','R_MedCornerOut20']:
            deformLib.blendShapeTarget(self.upLipMedRezcrv, i, upMedRezbls)
            deformLib.blendShapeTarget(self.lowLipMedRezcrv, i, lowMedRezbls)
            deformLib.blendShapeTarget(self.cln(self.upLipMedRezcrv), i, upMedRezblsGlob)
            deformLib.blendShapeTarget(self.cln(self.lowLipMedRezcrv), i, lowMedRezblsGlob)

        # clean outliner
        self.noTuchyUp = self.noTuchyUp.split('|')[-1]
        self.noTuchyLow = self.noTuchyLow.split('|')[-1]
        for i in [self.cln(self.upLipLowRezcrv),self.cln(self.upLipMedRezcrv),self.cln(self.upLipHiRezcrv),
                  self.cln(self.upLipZippercrv),]:
            mc.parent(i,self.cln(self.noTuchyUp))
        for i in [self.upLipLowRezcrv,self.upLipMedRezcrv,self.upLipHiRezcrv,self.upLipZippercrv]:
            mc.parent(i,self.noTuchyUp)

        for i in [self.cln(self.lowLipLowRezcrv),self.cln(self.lowLipMedRezcrv),self.cln(self.lowLipHiRezcrv),self.cln(self.lowLipZippercrv)]:
            mc.parent(i, self.cln(self.noTuchyLow))
        for i in [self.lowLipLowRezcrv,self.lowLipMedRezcrv,self.lowLipHiRezcrv,self.lowLipZippercrv]:
            mc.parent(i, self.noTuchyLow)

        for i,j in zip([self.zippercrv,self.upBindJnts[1],self.upBindJnts[0],self.lowBindJnts[1],self.lowBindJnts[0]],
                     [self.localLipRigGrp,self.localMidZipBaseModGrp,self.localMidZipBasePlaceModGrp,
                     self.lowlocalMidZipBaseModGrp,self.localMidZipBasePlaceModGrp]):
            mc.parent(i,j)
        for i,j in zip([self.cln(self.upBindJnts[1]),self.cln(self.upBindJnts[0]),
                        self.cln(self.lowBindJnts[1]),self.cln(self.lowBindJnts[0])],
                        [self.cln(self.localMidZipBaseModGrp),self.cln(self.localMidZipBasePlaceModGrp),
                        self.cln(self.lowlocalMidZipBaseModGrp),self.cln(self.localMidZipBasePlaceModGrp)]):
            mc.parent(i,j)

        mc.parent(self.tempCurve,'Zipper_CRV1BaseWire' , 'Zipper_CRV1BaseWire1',self.noTuchyUp)



    def cln(self,node):
        node = node.replace('local', '')
        return node
