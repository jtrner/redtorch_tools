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


class NeckTemplate(template.Template):
    """
    base class for neck template
    """
    def __init__(self,  **kwargs ):
        super(NeckTemplate, self).__init__(**kwargs)

    def build(self):
        super(NeckTemplate, self).build()
        self.createGroups()
        self.matches()

    def createGroups(self):
        self.neckHead = mc.createNode('transform', name = 'neckHead_GRP')
        self.neckJntGrp = mc.createNode('transform', name = 'neckJnt_GRP', p = self.neckHead)
        mc.move(0, 0, 3, self.neckJntGrp, r = True, ws = True)

        self.headOriGrp = mc.createNode('transform', name = 'headOri_GRP', p = self.neckHead )

        self.neckBaseOriGrp = mc.createNode('transform', name = 'neckBaseOri_GRP', p = self.neckHead)

        self.neckTwisterGrp = mc.createNode('transform', name = 'neckTwister_GRP', p = self.neckHead)

        self.neckSpaceLocGrp = mc.createNode('transform', name = 'neckSpaceLoc_GRP')

        self.neckSpaceMasterLoc = mc.createNode('transform', name = 'neckSpaceMaster_LOC',
                                                p = self.neckSpaceLocGrp)
        self.neckSpaceMasterLocShape = mc.createNode('locator', name = 'neckSpaceMasterShape_LOC',
                                                     p = self.neckSpaceMasterLoc)
        mc.move(0, -4, 0, self.neckSpaceMasterLoc, r = True, ws = True)
        mc.setAttr(self.neckSpaceMasterLoc + '.rx', -90)
        mc.setAttr(self.neckSpaceMasterLoc + '.rz', 90)

        self.neckSpaceAimUpLoc = mc.createNode('transform', name = 'neckSpaceAim_upVector_LOC',
                                               p = self.neckSpaceLocGrp)
        self.neckSpaceAimUpLocShape = mc.createNode('locator', name = 'neckSpaceAim_upVectorShape_LOC',
                                                    p = self.neckSpaceAimUpLoc)
        mc.move(0, 0, -17, self.neckSpaceAimUpLoc, r=True, ws=True)

        self.neckSpaceAimChestLoc = mc.createNode('transform', name = 'neckSpaceAimChest_LOC',
                                                  p = self.neckSpaceLocGrp)
        self.neckSpaceAimChestLocShape = mc.createNode('locator', name = 'neckSpaceAimChestShape_LOC',
                                                       p = self.neckSpaceAimChestLoc)

        self.neckSpaceAimBodyPointLoc = mc.createNode('transform', name = 'neckSpaceAimBodyPoint_LOC',
                                                      p = self.neckSpaceLocGrp)
        self.neckSpaceAimBodyPointLocShape = mc.createNode('locator', name = 'neckSpaceAimBodyPointShape_LOC',
                                                           p = self.neckSpaceAimBodyPointLoc)

        self.neckSpaceAimBodyLoc = mc.createNode('transform', name = 'neckSpaceAimBody_LOC',
                                                      p = self.neckSpaceAimBodyPointLoc)
        self.neckSpaceAimBodyLocShape = mc.createNode('locator', name = 'neckSpaceAimBodyShape_LOC',
                                                           p = self.neckSpaceAimBodyLoc)

        self.neckSpaceAimGlobalPointLoc = mc.createNode('transform', name = 'neckSpaceAimGlobalPoint_LOC',
                                                        p = self.neckSpaceLocGrp)
        self.neckSpaceAimGlobalPointLocShape = mc.createNode('locator', name = 'neckSpaceAimGlobalPointShape_LOC',
                                                        p = self.neckSpaceAimGlobalPointLoc)

        self.neckSpaceAimGlobalLoc = mc.createNode('transform', name = 'neckSpaceAimGlobal_LOC',
                                                        p = self.neckSpaceAimGlobalPointLoc)
        self.neckSpaceAimGlobalLocShape = mc.createNode('locator', name = 'neckSpaceAimGlobalShape_LOC',
                                                        p = self.neckSpaceAimGlobalLoc)

    def matches(self):
        trsLib.match(self.neckHead, self.neckJnts[2])
        mc.move(0, 0, -3, self.neckHead, r = True, ws = True)
        mc.makeIdentity(self.neckHead, apply = True, r = True, t = True, s = True)
        trsLib.match(self.headOriGrp, self.headJnts[0])
        trsLib.match(self.neckBaseOriGrp, self.neckJnts[0])
        trsLib.match(self.neckTwisterGrp, self.neckJnts[0])
        mc.makeIdentity(self.neckTwisterGrp, apply = True, r = True, t = True, s  =True)
        trsLib.match(self.neckSpaceLocGrp, self.neckJnts[0])
        trsLib.match(self.neckSpaceAimChestLoc, self.neckJnts[-1])
        trsLib.match(self.neckSpaceAimBodyPointLoc, self.neckJnts[0])
        trsLib.match(self.neckSpaceAimBodyLoc, self.neckJnts[-1])
        trsLib.match(self.neckSpaceAimGlobalLoc, self.neckJnts[-1])
