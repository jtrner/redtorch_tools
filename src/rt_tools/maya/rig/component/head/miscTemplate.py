import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from . import headTemplate

reload(headTemplate)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MiscTemplate(headTemplate.HeadTemplate):
    """
    base class for misc template
    """
    def __init__(self,  **kwargs ):
        super(MiscTemplate, self).__init__(**kwargs)

    def build(self):
        super(MiscTemplate, self).build()

    def createGroups(self):
        self.localMiscJntGrp = mc.createNode('transform', name = 'localMiscjnt_GRP')
        self.appleOriGrp = mc.createNode('transform', name = self.side + '_appleOri_GRP', p = self.localMiscJntGrp)
        self.appleModGrp = mc.createNode('transform', name = self.side + '_appleMod_GRP', p = self.appleOriGrp)

        self.nasalOriGrp = mc.createNode('transform', name = self.side + '_nasalOri_GRP', p = self.localMiscJntGrp)
        self.nasalModGrp = mc.createNode('transform', name = self.side + '_nasalMod_GRP', p = self.nasalOriGrp)

        self.browFleshOriGrp = mc.createNode('transform', name = self.side + '_browFleshOri_GRP', p = self.localMiscJntGrp)
        self.browFleshModGrp = mc.createNode('transform', name = self.side + '_browFleshMod_GRP', p = self.browFleshOriGrp)

        self.cheeckOriGrp = mc.createNode('transform', name = self.side + '_cheekOri_GRP', p = self.localMiscJntGrp)
        self.cheeckModGrp = mc.createNode('transform', name = self.side + '_cheekMod_GRP', p = self.cheeckOriGrp)

        self.nasalLabialOriGrp = mc.createNode('transform', name = self.side + '_nasalLabialOri_GRP', p = self.localMiscJntGrp)
        self.nasalLabialModGrp = mc.createNode('transform', name = self.side  + '_nasalLabialMod_GRP', p = self.nasalLabialOriGrp)

        self.orbitalUpperOriGrp = mc.createNode('transform', name = self.side + '_orbitalUpperOri_GRP', p = self.localMiscJntGrp)
        self.orbitalUpperModGrp = mc.createNode('transform', name = self.side + '_orbitalUpperMod_GRP', p = self.orbitalUpperOriGrp)

        self.orbitalLowerOriGrp = mc.createNode('transform', name = self.side + '_orbitalLowerOri_GRP', p = self.localMiscJntGrp)
        self.orbitalLowerModGrp = mc.createNode('transform', name = self.side + '_orbitalLowerMod_GRP', p = self.orbitalLowerOriGrp)

        self.cheekLowerOriGrp = mc.createNode('transform', name = self.side + '_cheekLowerOri_GRP', p = self.localMiscJntGrp)
        self.cheekLowerModGrp = mc.createNode('transform', name = self.side + '_cheekLowerMod_GRP', p = self.cheekLowerOriGrp)

        self.earOriGrp = mc.createNode('transform', name = self.side + '_earOri_GRP', p = self.localMiscJntGrp)
        self.oriModGrp = mc.createNode('transform', name = self.side + '_earMod_GRP', p = self.earOriGrp)


    def matches(self):
        trsLib.match(self.appleOriGrp, self.miscJnts[1])
        trsLib.match(self.nasalOriGrp, self.miscJnts[2])
        trsLib.match(self.browFleshOriGrp, self.miscJnts[3])
        trsLib.match(self.cheeckOriGrp, self.miscJnts[4])
        trsLib.match(self.nasalLabialOriGrp, self.miscJnts[5])
        trsLib.match(self.orbitalUpperOriGrp, self.miscJnts[6])
        trsLib.match(self.orbitalLowerOriGrp, self.miscJnts[7])
        trsLib.match(self.cheekLowerOriGrp, self.miscJnts[8])
        trsLib.match(self.earOriGrp, self.miscJnts[9])
        self.parenting()

    def parenting(self):
        mc.parent(self.miscJnts[1],self.appleModGrp)
        mc.parent(self.miscJnts[2],self.nasalModGrp)
        mc.parent(self.miscJnts[3],self.browFleshModGrp)
        mc.parent(self.miscJnts[4],self.cheeckModGrp)
        mc.parent(self.miscJnts[5],self.nasalLabialModGrp)
        mc.parent(self.miscJnts[6],self.orbitalUpperModGrp)
        mc.parent(self.miscJnts[7],self.orbitalLowerModGrp)
        mc.parent(self.miscJnts[8],self.cheekLowerModGrp)
        mc.parent(self.miscJnts[9],self.oriModGrp)

