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


class EyeTemplate(headTemplate.HeadTemplate):
    """
    base class for head template
    """
    def __init__(self,  **kwargs ):
        super(EyeTemplate, self).__init__(**kwargs)

    def build(self):
        super(EyeTemplate, self).build()

    def createGroups(self):
        self.eyeRigGrp = mc.createNode('transform', name = 'eyeRig_GRP')
        mc.move(0,173,0, self.eyeRigGrp, r = True, ws = True)
        self.eyeMasterAimDrvrSocketOriGrp = mc.createNode('transform', name = self.side + '_eyeMasterAimDrvrSocketOri_GRP',p = self.eyeRigGrp)
        self.eyeSquashCtlOriGrp = mc.createNode('transform', name = self.side + '_eyeSquetchCtrlOriGRP', p = self.eyeRigGrp)
        self.eyeMakroDrvrLocGrp = mc.createNode('transform', name = 'eyeRotMAKRO_DrvrLoc_GRP', p = self.eyeRigGrp)
        #create locators under eyeMakroDrvrLocGrp
        self.eyeMasterMakroOriGrp = mc.createNode('transform', name = self.side  + '_eyeMasterMAKROOri_GRP', p = self.eyeMakroDrvrLocGrp)
        self.eyeMasterMakroLoc = mc.createNode('transform', name = self.side + '_eyeMasterMakro_LOC', p = self.eyeMasterMakroOriGrp)
        self.eyeMasterMakroShape = mc.createNode('locator', name = self.side + '_eyeMasterMakroShape_LOC', p = self.eyeMasterMakroLoc)

        # create locators under eyeRigGrp
        self.eyeMasterAimUpVecLoc = mc.createNode('transform', name = self.side + '_eyeMasterAimUpVec_LOC', p = self.eyeRigGrp)
        self.eyeAimUpVecShape = mc.createNode('locator', name = self.side + '_eyeMasterAimUpVecShape_LOC', p = self.eyeMasterAimUpVecLoc)

        self.eyeMasterAimOffTargetLoc = mc.createNode('transform', name = self.side + '_eyeMasterAimOffTarget_LOC',p = self.eyeRigGrp)
        self.eyeAimOffTargetShape = mc.createNode('locator', name = self.side + '_eyeMasterAimOffTargetShape_LOC',p = self.eyeMasterAimOffTargetLoc)

    def matches(self):
        trsLib.match(self.eyeMasterAimDrvrSocketOriGrp, self.eyeJoints[0])
        trsLib.match(self.eyeSquashCtlOriGrp, self.eyeJoints[0])
        mc.move(5,0,0, self.eyeSquashCtlOriGrp, r = True, ws = True)

        trsLib.match(self.eyeMasterAimUpVecLoc, self.eyeJoints[0])
        mc.move(0,4,0, self.eyeMasterAimUpVecLoc, r = True, ws = True)

        trsLib.match(self.eyeMasterAimOffTargetLoc, self.eyeJoints[0])
        mc.move(0,0,1.5, self.eyeMasterAimOffTargetLoc, r = True, ws = True)

        trsLib.match(self.eyeMasterMakroOriGrp, self.eyeJoints[0])
