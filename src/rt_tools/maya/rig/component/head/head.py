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
from . import buildHead
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildHead)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Head(buildHead.BuildHead):
    """
    base class for head template
    """
    def __init__(self, side='C', prefix='head',geo = '', headEdge = '', headMovement = '',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.geo = geo
        self.headEdge = headEdge
        self.headMovement = headMovement

        super(Head, self).__init__(**kwargs)

    def build(self):
        super(Head, self).build()
        # connect stuf to the group above squash joints
        self.buttomHeadCtl,self.headBotSquashDrvrModGrp
        [mc.connectAttr(self.buttomHeadCtl + '.{}{}'.format(a,v), self.globalBotJntModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.topHeadCtl + '.{}{}'.format(a,v), self.globalTopJntModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']

        funcs.createSquashStretch(curve = self.botSquashCurve, joints = self.buttomJntSquash)
        funcs.createSquashStretch(curve = self.topSquashCurve, joints = self.topJntSquash)

        # connect squash clts to the transforms above squash joints

        [mc.connectAttr(self.squashCtls[0] + '.{}{}'.format(a,v), self.headBotSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.squashCtls[1] + '.{}{}'.format(a,v), self.headMidSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.squashCtls[2] + '.{}{}'.format(a,v), self.headTopSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
