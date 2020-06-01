import os
from collections import OrderedDict

import maya.cmds as mc

from rt_tools.maya.rig import rigBuild_base

reload(rigBuild_base)

# constants
instances = OrderedDict()
JOBS_DIR = os.getenv('JOBS_DIR', '')
job = os.getenv('JOB', '')
shot = os.getenv('SHOT', '')


class RigBuild(rigBuild_base.RigBuild_base):

    def __init__(self, **kwargs):
        super(RigBuild, self).__init__(**kwargs)

    def pre(self):
        super(RigBuild, self).pre()

    def build(self):
        super(RigBuild, self).build()

    def deform(self):
        super(RigBuild, self).deform()

    def post(self):
        super(RigBuild, self).post()
