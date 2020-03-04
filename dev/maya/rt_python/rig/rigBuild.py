import os
import sys

import maya.cmds as mc

from rt_python.rig import rigBuild_base
reload(rigBuild_base)



class RigBuild(rigBuild_base.RigBuild_base):

    def __init__(self, forceReload=True, **kwargs):
        super(RigBuild, self).__init__(forceReload=forceReload, **kwargs)

