import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib
from ...lib import deformLib
from ...lib import keyLib
from ...lib import jntLib
from ...lib import connect
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
    def __init__(self, side='C', prefix='head',geo = '',eye = '',eyebrow = '', headEdge = '', headMovement = 40 ,**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.geo = geo
        self.eye = eye
        self.eyebrow = eyebrow
        self.headEdge = headEdge
        self.headMovement = headMovement

        super(Head, self).__init__(**kwargs)

    def build(self):
        super(Head, self).build()
        # connect stuf to the group above squash joints
        [mc.connectAttr(self.buttomHeadCtl + '.{}{}'.format(a,v), self.globalBotJntModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.topHeadCtl + '.{}{}'.format(a,v), self.globalTopJntModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']

        funcs.createSquashStretch(curve = self.botSquashCurve, joints = self.headBotGlobalJnts)
        funcs.createSquashStretch(curve = self.topSquashCurve, joints = self.headTopGlobalJnts)

        for i,j in zip(self.headBotGlobalJnts,self.buttomJntSquash):
            [mc.connectAttr(i + '.{}{}'.format(a, v), j + '.{}{}'.format(a, v))for a in 'trs' for v in 'xyz']

        for i,j in zip(self.headTopGlobalJnts,self.topJntSquash):
            [mc.connectAttr(i + '.{}{}'.format(a, v), j + '.{}{}'.format(a, v))for a in 'trs' for v in 'xyz']

        # connect squash clts to the transforms above squash joints

        [mc.connectAttr(self.squashCtls[0] + '.{}{}'.format(a,v), self.headBotSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.squashCtls[1] + '.{}{}'.format(a,v), self.headMidSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']
        [mc.connectAttr(self.squashCtls[2] + '.{}{}'.format(a,v), self.headTopSquashDrvrModGrp + '.{}{}'.format(a,v))for a in 'trs'for v in 'xyz']

        # create blendShapes
        self.faceBshp = mc.blendShape(self.facialRigBustGeo,self.geo ,topologyCheck = False, n='face_bShp')[0]
        mc.setAttr(self.faceBshp + '.' + self.facialRigBustGeo, 1)

        self.localRigsBshp = mc.blendShape(self.localEyeLidsGeo,self.localLipsGeo ,self.localBrowsGeo,self.localMiscGeo,
                                      self.facialRigBustGeo,topologyCheck = False,n='localRigs_bShp')[0]

        for i in [self.localEyeLidsGeo,self.localLipsGeo,self.localBrowsGeo,self.localMiscGeo]:
            mc.setAttr(self.localRigsBshp + '.' + i, 1)

        # blendShapeEyebrows
        self.BrowBrowBshp = mc.blendShape(self.eyebrowlocalMisc,self.eyebrowlocalBrow ,self.facialRigBrow,
                                           topologyCheck = False,n='browBrow_bShp')[0]
        for i in [self.eyebrowlocalMisc,self.eyebrowlocalBrow ]:
            mc.setAttr(self.BrowBrowBshp + '.' + i, 1)

        self.localBrowBshp = mc.blendShape(self.facialRigBrow,self.eyebrow,
                                           topologyCheck = False,n='localRigBrow_bShp')[0]
        mc.setAttr(self.localBrowBshp + '.' + self.facialRigBrow, 1)


        # skin joints to the head
        self.facialBustBindJnts = self.headBotGlobalJnts + self.headTopGlobalJnts
        for i in [self.headFloodJnt[0],self.eyeSocketJnts[1],self.eyeSocketJnts[0]]:
            self.facialBustBindJnts.append(i)

        deformLib.bind_geo(geos=self.facialRigBustGeo, joints=self.facialBustBindJnts)


    def connect(self):
        super(Head, self).connect()



    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Head, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_geo', v=self.geo)
        attrLib.addString(self.blueprintGrp, 'blu_eye', v=self.eye)
        attrLib.addString(self.blueprintGrp, 'blu_eyebrow', v=self.eyebrow)
        attrLib.addString(self.blueprintGrp, 'blu_headEdge', v=self.headEdge)
        attrLib.addString(self.blueprintGrp, 'blu_headMovement', v=self.headMovement)