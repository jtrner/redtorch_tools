import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.controls as rig_controls

from rig_tools.frankenstein.core.master import Build_Master


class Build_Single(Build_Master):
    def __init__(self):
        super(Build_Single, self).__init__()

        self.build_is_inherited = False
        self.do_orient_joints = False
        
        self.rotate_order = None

        # Set the pack info
        self.joint_names = ["single"]
        self.description = "Single"
        self.length_max = 1
        self.base_joint_positions = ["incx1"]
    
    def create_controls(self):
        rot_adjustment = [0, 0, 0]
        if self.orient_joints == "xyz":  # :note: Rotation is to match control rot axis for spine_simple
            rot_adjustment = [0, 0, 90]
        fs = [x * -1 for x in rot_adjustment]
        
        self.ctrl = i_node.create("control", control_type="3D Cube", name=self.base_name, color=self.side_color, 
                                  size=self.ctrl_size, gimbal_color=self.side_color_scndy, position_match=self.base_joints[0],
                                  parent=self.pack_grp, constrain_geo=True, scale_constrain=True, follow_name=self.description,
                                  rotate_order=self.rotate_order, flip_shape=fs)
        self.ctrl.top_tfm.r.set(rot_adjustment)

    def _create_bit(self):
        self.create_controls()
