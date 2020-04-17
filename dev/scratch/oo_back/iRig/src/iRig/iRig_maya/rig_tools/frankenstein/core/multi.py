import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.controls as rig_controls

from rig_tools.frankenstein.core.master import Build_Master


class Build_Multi(Build_Master):
    def __init__(self):
        super(Build_Multi, self).__init__()

        self.build_is_inherited = False
        self.do_orient_joints = False
        
        self.control_type = "3D Cube"
        self.rotate_order = None

        # Set the pack info
        self.joint_names = ["multi"]
        self.description = "Multi"
        self.length = 5
        self.base_joint_positions = ["incx1"]

    def _class_prompts(self):
        all_control_types = i_control.get_curve_type_options(include_text=False, include_sliders=False)
        self.prompt_info["control_type"] = {"type": "option", "menu_items": all_control_types, "value": self.control_type}
    
    def _create_pack(self):
        # Hack so all base joints are treated as chains so they can be parented to the "world" and mirroring doesn't error
        self.base_joints_chains = [[jnt] for jnt in self.base_joints]  # :note: chains are a list in lists
        self.base_joints_roots = self.base_joints
        
        # Parent to group so they all float loose
        for jnt in self.base_joints:
            jnt.set_parent(self.pack_grp)
    
    def create_controls(self):
        self.ctrls = []
        
        for i, jnt in enumerate(self.base_joints):
            ctrl = i_node.create("control", control_type=self.control_type, name="%s%i" % (self.base_name, i), color=self.side_color, 
                                 size=self.ctrl_size, gimbal_color=self.side_color_scndy, position_match=jnt,
                                 parent=self.pack_ctrl_grp, constrain_geo=True, scale_constrain=True, 
                                 follow_name="%s%i" % (self.description, i), rotate_order=self.rotate_order)
            self.ctrls.append(ctrl)
    
    def _cleanup_bit(self):
        i_utils.parent(self.base_joints, self.pack_bind_jnt_grp)

    def _create_bit(self):
        self.create_controls()
