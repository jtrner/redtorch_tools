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


class EyebrowsTemplate(template.Template):
    """
    base class for lip template
    """
    def __init__(self,  **kwargs ):
        super(EyebrowsTemplate, self).__init__(**kwargs)

    def build(self):
        super(EyebrowsTemplate, self).build()

    def createGroups(self):
        self.localBrowsGrp = mc.createNode('transform', name = 'localBrows_GRP')
        self.browJntGrp = mc.createNode('transform', name = 'browJnt_GRP',p = self.localBrowsGrp)
        self.browInOrientGrp = mc.createNode('transform', name = self.side + '_browInOrient_GRP', p = self.browJntGrp)
        self.browMidOrientGrp = mc.createNode('transform', name = self.side + '_browMidOrient_GRP', p = self.browJntGrp)
        self.browOutOrientGrp = mc.createNode('transform', name = self.side + '_browOutOrient_GRP', p = self.browJntGrp)
        self.browInModGrp = mc.createNode('transform', name = self.side + '_browinModify_GRP', p = self.browInOrientGrp)
        self.browMidModGrp = mc.createNode('transform', name = self.side + '_browMidModify_GRP', p = self.browMidOrientGrp)
        self.browOutModGrp = mc.createNode('transform', name = self.side + '_browOutModify_GRP', p = self.browOutOrientGrp)

        self.browCtlGrp = mc.createNode('transform', name = 'browCtrl_GRP')
        self.browOutCtlOrientGrp = mc.createNode('transform', name = self.side + '_browOutCtrlOrient_GRP', p = self.browCtlGrp)
        self.browInCtlOrientGrp = mc.createNode('transform', name = self.side + '_browInCtrlOrient_GRP', p = self.browCtlGrp)
        self.browMidCtlOrientGrp = mc.createNode('transform', name = self.side + '_browMidCtrlOrient_GRP', p = self.browCtlGrp)


    def matches(self):
        trsLib.match(self.browInOrientGrp,self.browJnts[1])
        trsLib.match(self.browMidOrientGrp,self.browJnts[4])
        trsLib.match(self.browOutOrientGrp,self.browJnts[-1])
        trsLib.match(self.browOutCtlOrientGrp,self.browJnts[-1])
        trsLib.match(self.browInCtlOrientGrp,self.browJnts[1])
        trsLib.match(self.browMidCtlOrientGrp,self.browJnts[4])

        self.parenting()

    def parenting(self):
        mc.parent(self.browJnts[1],self.browInModGrp)
        mc.parent(self.browJnts[4],self.browMidModGrp)
        mc.parent(self.browJnts[-1],self.browOutModGrp)
        mc.parent(self.browJnts[0], self.browJntGrp)
