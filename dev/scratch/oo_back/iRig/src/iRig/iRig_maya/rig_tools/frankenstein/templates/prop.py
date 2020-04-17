import pymel.core as pm

import master
from master import Template_Master


class Template_Prop(Template_Master):

    def __init__(self):
        Template_Master.__init__(self)

        self.ctrl_size *= 0.25

        # Override some control settings
        # - Root
        self.root_ctrl_shape = "Root Cross"
        # - Ground
        self.ground_ctrl_shape = "Root Cross"
