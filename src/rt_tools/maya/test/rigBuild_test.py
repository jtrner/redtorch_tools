"""
from rt_tools.maya.rig import rigBuild_test
reload(rigBuild_test)
test = rigBuild_test.Test()
# test.deleteOldRig()
test.build()
test.connect()
"""
from ..rig.component import root
from ..rig.component import spine
from ..rig.component import arm
from ..rig.component import leg
from ..rig.component import legQuad
from ..rig.component import finger
from ..rig.component import chain
from ..rig.component import eye
from ..rig.component import eyes
from ..rig.component import neck
from ..rig.component import tail

reload(root)
reload(spine)
reload(arm)
reload(leg)
reload(legQuad)
reload(finger)
reload(chain)
reload(eye)
reload(eyes)
reload(neck)
reload(tail)


class Test(object):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self.rootA = root.Root()
        self.spineA = spine.Spine()
        self.neckA = neck.Neck(side='C', prefix='neck', numOfJnts=4)
        self.tailA = tail.Tail(side="C", prefix="tail", numOfFK=6, numOfJnts=8, hasMidCtl=True, addSpaces=True)
        # self.armL = arm.Arm()
        # self.armR = arm.Arm(side='R')
        # self.thumb = finger.Finger(side='L', prefix='thumb', numOfJnts=3)
        # self.ring = finger.Finger(side='L', prefix='ring')
        # self.legL = leg.Leg()
        # self.legR = leg.Leg(side='R')
        self.legQuadLF = legQuad.LegQuad(side='L', prefix='armQuad')
        self.legQuadRF = legQuad.LegQuad(side='R', prefix='armQuad')
        self.legQuadL = legQuad.LegQuad(side='L', isFront=False)
        self.legQuadR = legQuad.LegQuad(side='R', isFront=False)
        # self.chainA = chain.Chain()
        # self.eyeL = eye.Eye()
        # self.eyeR = eye.Eye(side='R')
        # self.eyesA = eyes.Eyes()

    def build(self):
        self. rootA.build()
        self.spineA.build()
        self.neckA.build()
        self.tailA.build()
        # self.armL.build()
        # self.armR.build()
        # self.ring.build()
        # self.thumb.build()
        # self.legL.build()
        # self.legR.build()
        self.legQuadLF.build()
        self.legQuadRF.build()
        self.legQuadL.build()
        self.legQuadR.build()
        # self.chainA.build()
        # self.eyeL.build()
        # self.eyeR.build()
        # self.eyesA.build()

    def connect(self):
        self.rootA.connect()
        self.spineA.connect()
        self.neckA.connect()
        self.tailA.connect()
        # self.armL.connect()
        # self.armR.connect()
        # self.ring.connect()
        # self.thumb.connect()
        # self.legL.connect()
        # self.legR.connect()
        self.legQuadLF.connect()
        self.legQuadRF.connect()
        self.legQuadL.connect()
        self.legQuadR.connect()
        # self.chainA.connect()
        # self.eyeL.connect()
        # self.eyeR.connect()
        # self.eyesA.connect()

    def deleteOldRig(self):
        self.rootA.deleteOldRig()
        self.spineA.deleteOldRig()
        self.neckA.deleteOldRig()
        self.tailA.deleteOldRig()
        # self.armL.deleteOldRig()
        # self.armR.deleteOldRig()
        # self.ring.deleteOldRig()
        # self.thumb.deleteOldRig()
        # self.legL.deleteOldRig()
        # self.legR.deleteOldRig()
        self.legQuadLF.deleteOldRig()
        self.legQuadRF.deleteOldRig()
        self.legQuadL.deleteOldRig()
        self.legQuadR.deleteOldRig()
        # self.chainA.deleteOldRig()
        # self.eyeL.deleteOldRig()
        # self.eyeR.deleteOldRig()
        # self.eyesA.deleteOldRig()
