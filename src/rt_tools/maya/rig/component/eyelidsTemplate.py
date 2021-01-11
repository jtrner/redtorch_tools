import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib
from ..component import template

reload(template)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EyelidsTemplate(template.Template):

    def __init__(self,  **kwargs ):
        super(EyelidsTemplate, self).__init__(**kwargs)

    def build(self):
        super(EyelidsTemplate, self).build()
        self.createGroups()
        self.matches()

    def createGroups(self):
        if self.side == 'L':
            self.eyelidCtlGrp = mc.createNode('transform', name = 'eyeLidsCtl_GRP')
            self.localEyelidRig = mc.createNode('transform', name='localEyeLids_Rig')

        else:
            self.eyelidCtlGrp = 'eyeLidsCtl_GRP'
            self.localEyelidRig = 'localEyeLids_Rig'
        self.eyelidSocketGrp = mc.createNode('transform', name = self.side + '_eyeLidCtrlSocket_GRP',p = self.eyelidCtlGrp)
        self.eyelidsideCtlGrp = mc.createNode('transform', name = self.side + '_eyeLidCtrl_GRP',p = self.eyelidSocketGrp)

        self.setOut('eyelidSocketGrp', self.eyelidSocketGrp)

        if self.side == 'L':
            self.eyeCreaseGrp = mc.createNode('transform', name = 'eyeCrease_Rig', p = self.localEyelidRig)
        else:
            self.eyeCreaseGrp = 'eyeCrease_Rig'
        self.upcreaseLocGrp = mc.createNode('transform', name = self.side + '_UpCreaseLOC_GRP', p = self.eyeCreaseGrp)
        self.lowcreaseLocGrp = mc.createNode('transform', name = self.side + '_LowCreaseLOC_GRP', p = self.eyeCreaseGrp)
        self.creaseSharperJnt = mc.createNode('transform', name = self.side + '_CreaseShpJnt_ShaperJnt_GRP', p = self.eyeCreaseGrp)
        if self.side == 'L':
            self.eyelidLocalRig = mc.createNode('transform', name = 'eyeLids_Rig_GRP',p = self.localEyelidRig)
        else:
            self.eyelidLocalRig = 'eyeLids_Rig_GRP'
        self.eyelidSharperJntGrp = mc.createNode('transform', name = self.name + '_ShaperJnt_GRP', p = self.eyelidLocalRig)
        self.eyelidCrvGrp = mc.createNode('transform', name = self.name + '_Crv_GRP')
        self.upLidLocGrp = mc.createNode('transform',name = self.name + '_up_LOC', p = self.eyelidLocalRig  )
        self.lowLidLocGrp = mc.createNode('transform',name = self.name + '_low_LOC', p = self.eyelidLocalRig )
        self.uplidJntGrp = mc.createNode('transform', name = self.name + '_up_JNT_GRP', p = self.eyelidLocalRig)
        self.lowlidJntGrp = mc.createNode('transform', name = self.name + '_low_JNT_GRP', p = self.eyelidLocalRig)
        self.lidMakroLocGrp = mc.createNode('transform', name = self.name + '_makroLoc_GRP',p = self.eyelidLocalRig)
        self.browMakroDrvrLocGrp = mc.createNode('transform', name = self.side + '_browMAKRO_DriverLoc_GRP', p = self.eyelidLocalRig)
        self.browInOriGrp = mc.createNode('transform', name = self.side + '_browInOri_GRP', p = self.browMakroDrvrLocGrp)
        self.browMidMakroDrvrOriGrp = mc.createNode('transform', name = self.side + '_browMidMAKRO_DriverOri_GRP', p = self.browMakroDrvrLocGrp)
        self.browOutOriGrp = mc.createNode('transform', name = self.side + '_browOutOri_GRP', p = self.browMakroDrvrLocGrp)

        # create locators under brow stuf
        self.browInLoc = mc.createNode('transform', name = self.side + '_browIn_LOC', p = self.browInOriGrp)
        self.browInLocShape = mc.createNode('locator', name = self.side + '_browInShape_LOC', p = self.browInLoc)

        self.browOutLoc = mc.createNode('transform', name = self.side + '_browOut_LOC', p = self.browOutOriGrp)
        self.browOutLocShape = mc.createNode('locator', name = self.side + '_browOutShape_LOC', p = self.browOutLoc)

        self.browMidMakroDrvrLoc = mc.createNode('transform',name = self.side + '_browMidMAKRO_Driver_LOC', p = self.browMidMakroDrvrOriGrp)
        self.browMidMakroDrvrLocShape = mc.createNode('locator',name = self.side + '_browMidMAKRO_DriverShape_LOC', p = self.browMidMakroDrvrLoc)

        # create locators in lid makro loca
        self.upLidMakroLoc = mc.createNode('transform', name = self.side + '_upLidMakro_LOC', p = self.lidMakroLocGrp)
        self.upLidMakroLocShape = mc.createNode('locator', name = self.side + '_upLidMakroShape_LOC', p = self.upLidMakroLoc)

        self.upCreaseMakroLoc = mc.createNode('transform', name = self.side + '_upCreaseMakro_LOC', p = self.lidMakroLocGrp)
        self.upCreaseMakroLocShape = mc.createNode('locator', name = self.side + '_upCreaseMakroShape_LOC', p = self.upCreaseMakroLoc)

        self.browMidMakroLoc = mc.createNode('transform', name = self.side + '_browMidMakro_LOC', p = self.lidMakroLocGrp)
        self.browMidMakroLocShape = mc.createNode('locator', name = self.side + '_browMidMakroShape_LOC', p = self.browMidMakroLoc)

        self.lowCreaseMakroLoc = mc.createNode('transform', name = self.side +'_lowCreaseMakro_LOC', p = self.lidMakroLocGrp)
        self.lowCreaseMakroLocShape = mc.createNode('locator', name = self.side +'_lowCreaseMakroShape_LOC', p = self.lowCreaseMakroLoc)

        self.lowLidMakroLoc = mc.createNode('transform', name = self.side +'_lowLicMakro_LOC', p = self.lidMakroLocGrp)
        self.lowLidMakroLocShape = mc.createNode('locator', name = self.side +'_lowLicMakroShape_LOC', p = self.lowLidMakroLoc)

        self.cheekRaiseMakro = mc.createNode('transform', name = self.side +'_lowCheekRaiseMakro_LOC', p = self.lidMakroLocGrp)
        self.cheekRaiseMakroShape = mc.createNode('locator', name = self.side +'_lowCheekMakroShape_LOC', p = self.cheekRaiseMakro)

        mult = [-1, 1][self.side == 'L']
        mc.move(mult * 26.367,self.movement + 184.517,3.939,self.browMidMakroLoc,r = True, ws = True)
        mc.move(mult * 25.996,self.movement + 180.046,2.006,self.cheekRaiseMakro,r = True, ws = True)
        mc.move(mult * 25.877,self.movement + 180.954,2.092,self.lowCreaseMakroLoc,r = True, ws = True)
        mc.move(mult * 25.736,self.movement + 181.92,2.221,self.lowLidMakroLoc,r = True, ws = True)
        mc.move(mult * 25.726,self.movement + 183.427,2.455,self.upCreaseMakroLoc,r = True, ws = True)
        mc.move(mult * 26.208,self.movement + 183.094,2.271,self.upLidMakroLoc,r = True, ws = True)
        for i in [self.browMidMakroLoc,self.cheekRaiseMakro,self.lowCreaseMakroLoc,
                  self.lowLidMakroLoc,self.upCreaseMakroLoc,self.upLidMakroLoc]:
            mc.makeIdentity(i,apply = True,t = True, r = True, s = True)


    def matches(self):
        trsLib.match(self.eyelidSocketGrp, self.upeEyelidparent[0])
        mc.move(0,0,2,self.eyelidSocketGrp,r = True, ws = True)
        mc.makeIdentity(self.eyelidSocketGrp, apply = True, t = True,r = True, s = True)
