import pymel.core as pm

import master
from master import Template_Master


class Template_Vehicle(Template_Master):

    def __init__(self):
        Template_Master.__init__(self)

        self.ctrl_size *= 5

        # Override some control settings
        # - Ground
        self.ground_ctrl_shape = "Root Cross"
        # - COG
        self.cog_ctrl_shape = "Root Cross"
