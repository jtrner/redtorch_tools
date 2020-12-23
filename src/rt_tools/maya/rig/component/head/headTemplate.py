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
        self.facialCtlGrp = mc.createNode('transform', name = 'facialCTL_GRP')
        self.mouthCtlGrp = mc.createNode('transform', name = 'mouthCtl_GRP', p = self.facialCtlGrp)
        self.headTopCtlOriGrp = mc.createNode('transform', name = 'headTopCtlOri_GRP', p = self.mouthCtlGrp)
        self.headButtomCtlOriGrp = mc.createNode('transform', name = 'headButtomCtlOri_GRP', p = self.mouthCtlGrp)

    def matches(self):
        trsLib.match(self.facialCtlGrp, self.buttomJntSquash[0])
        trsLib.match(self.headTopCtlOriGrp, self.topJntSquash[0])
        trsLib.match(self.headButtomCtlOriGrp, self.buttomJntSquash[0])
