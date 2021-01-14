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


class SpineTemplate(template.Template):
    """
    base class for neck template
    """
    def __init__(self,  **kwargs ):
        super(SpineTemplate, self).__init__(**kwargs)

    def build(self):
        super(SpineTemplate, self).build()
        self.createGroups()
        self.matches()

    def createGroups(self):
        self.spineGrp = mc.createNode('transform', name = 'spine_GRP')
        self.spineIkGrp = mc.createNode('transform', name = 'spineIk_GRP', p = self.spineGrp)
        self.spineFkGrp = mc.createNode('transform', name = 'spineFk_GRP', p = self.spineGrp)
        self.spineIkDriversGrp = mc.createNode('transform', name = 'spineIkDrivers_GRP', p = self.spineIkGrp)
        self.spineIkHipDrvrOriGrp = mc.createNode('transform', name = 'spineIk_hipDriverOri_GRP', p = self.spineIkDriversGrp)

        self.spineIkChestDrvrOriGrp = mc.createNode('transform', name = 'spineIkChestDrvrOri_GRP', p = self.spineIkGrp)

        self.spineIkWaistDrvrOriGrp = mc.createNode('transform', name = 'spineIkWaistOri_GRP', p = self.spineIkGrp)


        self.spineBlendJntGrp = mc.createNode('transform', name = 'spineBlendJnt_GRP', p = self.spineGrp)
        self.hipBlendOriGrp = mc.createNode('transform', name = 'hipBlendOri_GRP', p = self.spineBlendJntGrp)
        self.hipBlendModGrp = mc.createNode('transform', name = 'hipBlendMod_GRP', p = self.hipBlendOriGrp)

        self.extrasGrp = mc.createNode('transform', name = self.name + '_extras_GRP')


    def matches(self):
        trsLib.match(self.spineBlendJntGrp, self.spineIkJnts[0])
        trsLib.match(self.spineIkDriversGrp, self.spineIkJnts[0])
        mc.makeIdentity(self.spineIkDriversGrp, apply = True, t = True, r = True, s = True)
        trsLib.match(self.spineIkChestDrvrOriGrp, self.spineIkJnts[-1])
        trsLib.match(self.spineIkWaistDrvrOriGrp, self.spineIkJnts[2])
