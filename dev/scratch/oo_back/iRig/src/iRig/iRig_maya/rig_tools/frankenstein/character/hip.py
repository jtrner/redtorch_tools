import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes

from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.character.clavicle import Build_Clavicle


class Build_Hip(Build_Clavicle):
    def __init__(self):
        Build_Clavicle.__init__(self)
        
        # Specify inherited params
        self.build_is_inherited = True
        self.rotate_order = "xzy"

        # Set the pack info
        self.description = "Hip"
        self.base_joint_positions[0] = [0.15, 3.43, -0.09]  #[1.0, 35.0, 0.0]
