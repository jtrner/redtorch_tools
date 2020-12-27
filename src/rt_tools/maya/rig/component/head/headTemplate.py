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


class HeadTemplate(template.Template):
    """
    base class for head template
    """
    def __init__(self,  **kwargs ):
        super(HeadTemplate, self).__init__(**kwargs)

    def build(self):
        super(HeadTemplate, self).build()
        self.createGroups()
        self.matches()

    def createGroups(self):
        self.faceRigGrp = mc.createNode('transform', name = 'faceRig_GRP')
        self.facialCtlGrp = mc.createNode('transform', name = 'facialCTL_GRP', p = self.faceRigGrp)
        self.setOut('facialCtlGrp', self.facialCtlGrp)
        self.facialRigGrp = mc.createNode('transform', name = 'facialRig_GRP', p = self.faceRigGrp)
        self.setOut('facialRigGrp', self.facialRigGrp)
        self.globalRigGrp = mc.createNode('transform', name = 'global_Rig', p = self.facialRigGrp )
        self.setOut('globalRigGrp', self.globalRigGrp)
        self.localRigsGrp = mc.createNode('transform', name = 'localRigs_GRP', p = self.facialRigGrp)
        self.setOut('localRigs', self.localRigsGrp)
        self.headSquashMechanicGrp = mc.createNode('transform', name = 'headSquetchMechanics_GRP', p = self.globalRigGrp)
        self.globalBotJntOriGrp = mc.createNode('transform', name = 'globalHeadBotJntOri_GRP', p = self.globalRigGrp)
        self.globalBotJntModGrp = mc.createNode('transform', name = 'globalHeadBotJntMod_GRP', p = self.globalBotJntOriGrp)
        self.globalTopJntOriGrp = mc.createNode('transform', name = 'globalHeadTopJntOri_GRP', p = self.globalRigGrp)
        self.globalTopJntModGrp = mc.createNode('transform', name = 'globalHeadTopJntMod_GRP', p = self.globalTopJntOriGrp)
        self.headSquashCtlGrp = mc.createNode('transform', name = 'headSquatchCtl_GRP', p = self.facialCtlGrp)

        self.botSquashOriGrp = mc.createNode('transform', name = 'botSquatchOri_GRP', p = self.headSquashCtlGrp)
        self.midSquashOriGrp = mc.createNode('transform', name = 'midSquatchOri_GRP', p = self.headSquashCtlGrp)
        self.topSquashOriGrp = mc.createNode('transform', name = 'topSquatchOri_GRP', p = self.headSquashCtlGrp)

        self.mouthCtlGrp = mc.createNode('transform', name = 'mouthCtl_GRP', p = self.facialCtlGrp)
        self.headTopCtlOriGrp = mc.createNode('transform', name = 'headTopCtlOri_GRP', p = self.mouthCtlGrp)
        self.headButtomCtlOriGrp = mc.createNode('transform', name = 'headButtomCtlOri_GRP', p = self.mouthCtlGrp)

    def matches(self):
        trsLib.match(self.facialCtlGrp, self.buttomJntSquash[0])
        trsLib.match(self.headTopCtlOriGrp, self.topJntSquash[0])
        trsLib.match(self.headButtomCtlOriGrp, self.buttomJntSquash[0])
        trsLib.match(self.globalBotJntOriGrp, self.buttomJntSquash[0])
        trsLib.match(self.globalTopJntOriGrp, self.topJntSquash[0])

        trsLib.match(self.botSquashOriGrp, self.headSquashDrvrJnts[1])
        mc.move(0,-1,10, self.botSquashOriGrp, r = True, ws = True)
        trsLib.match(self.topSquashOriGrp, self.headSquashDrvrJnts[0])
        mc.move(0,1,10, self.topSquashOriGrp, r = True, ws = True)

        mc.delete(mc.parentConstraint(self.headSquashDrvrJnts[-1],self.headSquashDrvrJnts[-2], self.midSquashOriGrp))
        mc.move(0,0,10, self.midSquashOriGrp, r = True, ws = True)



