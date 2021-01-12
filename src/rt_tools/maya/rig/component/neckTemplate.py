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





    def matches(self):
        trsLib.match(self.neckHead, self.neckJnts[2])
        mc.move(0, 0, -3, self.neckHead, r = True, ws = True)
        mc.makeIdentity(self.neckHead, apply = True, r = True, t = True, s = True)
        trsLib.match(self.headOriGrp, self.headJnts[0])

        trsLib.match(self.neckBaseOriGrp, self.neckJnts[0])

        trsLib.match(self.neckTwisterGrp, self.neckJnts[0])
        mc.makeIdentity(self.neckTwisterGrp, apply = True, r = True, t = True, s  =True)
