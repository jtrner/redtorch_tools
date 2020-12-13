import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from ...component import template

reload(template)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LipsTemplate(template.Template):
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
        self.lowLipZippercrv = lowLipZippercrv
        self.upBindJnts= upBindJnts
        self.lowBindJnts= lowBindJnts
        self.numJnts = numJnts

        super(LipsTemplate, self).__init__(**kwargs)

    def runLip(self):
        self.createGroups()
        self.matches()

    def createGroups(self):
        self.rigGrp = mc.createNode('transform', name='lipRig_GRP')
        self.mouthPiv = mc.createNode('transform', name='MouthCtrlPivotMod_GRP', p=self.rigGrp)
        #jaw part
        self.mainJawGrp = mc.createNode('transform', name = 'jawMainJntOri_GRP', p = self.rigGrp)
        self.mainJawMakro = mc.createNode('transform', name = 'jawMainJntMAKRO_GRP', p = self.mainJawGrp)
        self.mainJntMod = mc.createNode('transform', name = 'jawMainJntMod_GRP', p = self.mainJawMakro)
        self.jawSecJntOr = mc.createNode('transform', name = 'jawSecondaryJntOri_GRP', p = self.mouthAndJawMain[1])
        self.jawSecJntMod = mc.createNode('transform', name = 'jawSecondaryJntMod_GRP', p = self.jawSecJntOr)
        self.chinJntMod = mc.createNode('transform', name = 'chinJntMod_GRP', p = self.jawSecBndJnt[0])
        self.mentalJntMod = mc.createNode('transform', name = 'mentalJntMod_GRP', p = self.jawSecBndJnt[0])

        #nostril part
        self.noseBendGrp = mc.createNode('transform', name = 'NoseBendOri_GRP', p = self.rigGrp)
        self.noseBendMakro = mc.createNode('transform', name = 'NoseBendMAKRO_GRP', p = self.noseBendGrp)
        self.noseJntOri= mc.createNode('transform', name = 'NoseJntOri_GRP', p = self.noseBendMakro)
        self.noseJntMakro= mc.createNode('transform', name = 'NoseJntMAKRO_GRP', p = self.noseJntOri)
        self.noseJntMod= mc.createNode('transform', name = 'NoseJntMod_GRP', p = self.noseJntMakro)
        self.noseJntBaseOr = mc.createNode('transform', name = 'noseJntBaseOri_GRP', p = self.mouthAndJawMain[3])
        mc.move(0, 0, 1, self.noseJntBaseOr, r = True, ws = True)
        self.noseJntBaseMakro= mc.createNode('transform', name = 'noseJntBaseMAKRO_GRP', p = self.noseJntBaseOr)
        self.noseJntBaseMod= mc.createNode('transform', name = 'noseJntBaseMod_GRP', p = self.noseJntBaseMakro)
        self.r_nostrilJntOri = mc.createNode('transform', name = 'R_nostrilJntOri_GRP', p = self.noseJntBaseMod)
        self.columJntOri = mc.createNode('transform', name = 'columellaJntOri_GRP', p = self.noseJntBaseMod)
        self.l_nostrilJntOri = mc.createNode('transform', name = 'L_nostrilJntOri_GRP', p = self.noseJntBaseMod)
        #rightNostril
        self.r_nostrilJntMakro = mc.createNode('transform', name = 'R_nostrilJntMAKRO_GRP', p = self.r_nostrilJntOri)
        self.r_nostrilJntMod= mc.createNode('transform', name = 'R_nostrilJntMod_GRP', p = self.r_nostrilJntMakro)
        self.r_nostrilJntMakroScale= mc.createNode('transform', name = 'R_nostrilMAKROscale_GRP', p = self.r_nostrilJntMod)
        self.r_nostrilFlareMod = mc.createNode('transform', name = 'R_nostrilFlareJntMod_GRP', p = self.rightnostrils[0])

        #leftNostril
        self.l_nostrilJntMakro = mc.createNode('transform', name = 'L_nostrilJntMAKRO_GRP', p = self.l_nostrilJntOri)
        self.l_nostrilJntMod= mc.createNode('transform', name = 'L_nostrilJntMod_GRP', p = self.l_nostrilJntMakro)
        self.l_nostrilJntMakroScale= mc.createNode('transform', name = 'L_nostrilMAKROscale_GRP', p = self.l_nostrilJntMod)
        self.l_nostrilFlareMod = mc.createNode('transform', name = 'L_nostrilFlareJntMod_GRP', p = self.leftnostrils[0])
        #midNostril
        self.columJntMod= mc.createNode('transform', name = 'columellaJntMod_GRP', p = self.columJntOri)

        # up part
        self.upLipRibbon = mc.createNode('transform', name='localUpLipRibbon_GRP', p=self.rigGrp)
        self.noTuchyUp = mc.createNode('transform', name='localUpLipNoTouchy_GRP', p=self.upLipRibbon)
        self.upJntDrvr = mc.createNode('transform', name='localUpJntDrvr_GRP', p=self.upLipRibbon)
        self.upLipCtlGrp = mc.createNode('transform', name='localUpLipCtrl_GRP', p=self.upLipRibbon)
        self.upMicroJntCtlGrp = mc.createNode('transform', name='localUpLipMicroJntCtrl_GRP', p=self.upJntDrvr)
        self.upjntCtlPlace = mc.createNode('transform', name='localUpLipJNTCtrlPlacement_GRP', p=self.upJntDrvr)
        self.jntRollModupGrp = mc.createNode('transform', name='localUpLipJNTRollModify_GRP', p=self.upJntDrvr)
        self.upLipMakroJntCtl = mc.createNode('transform', name='upLipMakroJntCtrl_GRP', p=self.upJntDrvr)
        self.upLipJntLocLowGrp = mc.createNode('transform', name='localUpLipJntLocLow_GRP', p=self.noTuchyUp)
        self.jntLocMedUp = mc.createNode('transform', name='localUpLipJntLocMed_GRP', p=self.noTuchyUp)
        self.r_localUpLipOutOrient_GRP = mc.createNode('transform', name='R_localUpLipOutOrient_GRP',
                                                       p=self.upLipMakroJntCtl)
        self.l_localUpLipOutOrient_GRP = mc.createNode('transform', name='L_localUpLipOutOrient_GRP',
                                                       p=self.upLipMakroJntCtl)
        self.m_localUpLipOutOrient_GRP = mc.createNode('transform', name='M_localUpLipOutOrient_GRP',
                                                       p=self.upLipMakroJntCtl)
        self.leftUpMainJnt = mc.createNode('transform', name='L_localUpLipCornerOrient_GRP', p=self.upJntDrvr)
        self.rightUpMainJnt = mc.createNode('transform', name='R_localUpLipCornerOrient_GRP', p=self.upJntDrvr)
        self.middleUpMainJnt = mc.createNode('transform', name='m_localUpLipCornerOrient_GRP', p=self.upJntDrvr)

        # low part
        self.lowLipRibbon = mc.createNode('transform', name='localLowLipRibbon_GRP', p=self.rigGrp)
        self.noTuchyLow = mc.createNode('transform', name='localLowLipNoTouchy_GRP', p=self.lowLipRibbon)
        self.lowJntDrvr = mc.createNode('transform', name='localLowJntDrvr_GRP', p=self.lowLipRibbon)
        self.lowLipCtlGrp = mc.createNode('transform', name='localLowLipCtrl_GRP', p=self.lowLipRibbon)
        self.lowLipMakroJntCtl = mc.createNode('transform', name='lowLipMakroJntCtrl_GRP', p=self.lowJntDrvr)
        self.lowMicroJntCtlGrp = mc.createNode('transform', name='localLowLipMicroJntCtrl_GRP', p=self.lowJntDrvr)
        self.jntRollModlowGrp = mc.createNode('transform', name='localLowLipJNTRollModify_GRP', p=self.lowJntDrvr)
        self.lowjntCtlPlace = mc.createNode('transform', name='localLowLipJNTCtrlPlacement_GRP', p=self.lowJntDrvr)
        self.lowLipJntLocLowGrp = mc.createNode('transform', name='localLowLipJntLocLow_GRP', p=self.noTuchyLow)
        self.jntLocMedLow = mc.createNode('transform', name='localLowLipJntLocMed_GRP', p=self.noTuchyLow)
        self.jntLocHiLow = mc.createNode('transform', name='localLowLipJntLocHi_GRP', p=self.noTuchyLow)
        self.r_localLowLipOutOrient_GRP = mc.createNode('transform', name='R_localLowLipOutOrient_GRP',
                                                        p=self.lowLipMakroJntCtl)
        self.l_localLowLipOutOrient_GRP = mc.createNode('transform', name='L_localLowLipOutOrient_GRP',
                                                        p=self.lowLipMakroJntCtl)
        self.m_localLowLipOutOrient_GRP = mc.createNode('transform', name='M_localLowLipOutOrient_GRP',
                                                        p=self.lowLipMakroJntCtl)
        self.leftLowMainJnt = mc.createNode('transform', name='L_localLowLipCornerOrient_GRP', p=self.lowJntDrvr)
        self.rightLowMainJnt = mc.createNode('transform', name='R_localLowLipCornerOrient_GRP', p=self.lowJntDrvr)
        self.middleLowMainJnt = mc.createNode('transform', name='m_localLowLipCornerOrient_GRP', p=self.lowJntDrvr)


    def matches(self):
        trsLib.match(self.mouthPiv, self.upBindJnts[-1])
        trsLib.match(self.mainJawGrp,self.mouthAndJawMain[1] )
        #jaw matches
        trsLib.match(self.jawSecJntOr, self.jawSecBndJnt[0])
        trsLib.match(self.chinJntMod, self.jawSecBndJnt[1])
        trsLib.match(self.mentalJntMod, self.jawSecBndJnt[2])
        #nose matches
        trsLib.match(self.noseBendGrp, self.mouthAndJawMain[3])
        mc.move(0,1.5, 0.5, self.noseBendGrp, r = True, ws = True)
        trsLib.match(self.noseJntOri, self.mouthAndJawMain[3])
        trsLib.match(self.r_nostrilJntOri,self.rightnostrils[0])
        trsLib.match(self.columJntOri,self.mouthAndJawMain[-1])
        trsLib.match(self.l_nostrilJntOri,self.leftnostrils[0])
        trsLib.match(self.r_nostrilFlareMod , self.rightnostrils[1])
        trsLib.match(self.l_nostrilFlareMod , self.leftnostrils[1])

        # upPart
        trsLib.match(self.upLipCtlGrp, self.upBindJnts[1])
        trsLib.match(self.upMicroJntCtlGrp, self.upBindJnts[1])
        trsLib.match(self.upjntCtlPlace, self.upBindJnts[1])
        trsLib.match(self.jntRollModupGrp, self.upBindJnts[1])
        trsLib.match(self.upLipMakroJntCtl, self.upBindJnts[1])

        # lowPart
        trsLib.match(self.lowLipCtlGrp, self.lowBindJnts[1])
        trsLib.match(self.lowLipMakroJntCtl, self.lowBindJnts[1])
        trsLib.match(self.lowMicroJntCtlGrp, self.lowBindJnts[1])
        trsLib.match(self.jntRollModlowGrp, self.lowBindJnts[1])
        trsLib.match(self.lowjntCtlPlace, self.lowBindJnts[1])
        self.parenting()

    def parenting(self):
        mc.parent(self.mouthAndJawMain[1], self.mainJntMod)
        mc.parent(self.jawSecBndJnt[0], self.jawSecJntMod)
        mc.parent(self.jawSecBndJnt[1],self.chinJntMod)
        mc.parent(self.jawSecBndJnt[2],self.mentalJntMod)
        mc.parent(self.mouthAndJawMain[3],self.noseJntMod)
        mc.parent(self.rightnostrils[0],self.r_nostrilJntMakroScale)
        mc.parent(self.rightnostrils[1],self.r_nostrilFlareMod)
        mc.parent(self.leftnostrils[0],self.l_nostrilJntMakroScale)
        mc.parent(self.leftnostrils[1],self.l_nostrilFlareMod)
        mc.parent(self.mouthAndJawMain[-1],self.columJntMod)