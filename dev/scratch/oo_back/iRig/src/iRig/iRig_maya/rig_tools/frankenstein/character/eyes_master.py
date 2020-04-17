import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

from rig_tools.frankenstein import RIG_F_LOG

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.nodes as rig_nodes

import rig_tools.frankenstein.utils as rig_frankenstein_utils
from rig_tools.frankenstein.core.master import Build_Master


class Build_Eyes_Master(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Vars
        self.eye_pack_objs = []  # The pack object(s) to be driven by the master aim control
        
        # Set the pack info
        self.joint_names = ["master"]
        self.description = "Eye"
        self.length_max = 1
        self.base_joint_positions = [[0.0, 4.0, 0.00]] #[[0.0, 80.0, 5.0]]
    
    def create_controls(self):
        # Vars
        self.eye_aim_controls = [eye_pack.aim_ctrl.control for eye_pack in self.eye_pack_objs]
        
        # Create
        self.aim_ctrl = i_node.create("control", control_type="2D Square", color="aqua",  # Hardcode color
                                      size=self.ctrl_size, with_gimbal=True, name=self.base_name + "_Root",
                                      lock_hide_attrs=["s", "v"], parent=self.pack_grp, flip_shape=[90, 0, 0],
                                      gimbal_color="darkAqua", position_match=self.eye_aim_controls, scale_shape=[1, 0.5, 1])

    def connect_elements(self):
        # Cross Eyes Attr
        crosseye_attr = i_attr.create(node=self.aim_ctrl.control, ln="CrossEye", dv=0, k=True)
        
        # Vars
        eye_dist = i_utils.get_single_distance(from_node=self.eye_aim_controls[0], to_node=self.eye_aim_controls[1]) / 2

        # Connect each eye sim
        for eye_pack in self.eye_pack_objs:
            # - Insert group
            cns_grp = eye_pack.aim_ctrl.cns_grp
            xeye_grp = cns_grp.create_zeroed_group(group_name=cns_grp.replace("_Cns", "_XEye"))
            # - MD
            crosseye_md = i_node.create("multiplyDivide", eye_pack.base_name + "_CrossEye_Md")
            crosseye_attr.drive(crosseye_md.input1X)
            crosseye_md.outputX.drive(xeye_grp.tx)
            crosseye_md.input2X.set(eye_dist)
            # - Parent
            offs_grp = eye_pack.aim_ctrl.offset_grp
            offs_grp.set_parent(self.aim_ctrl.last_tfm)
            # - Connect to info node
            i_node.connect_to_info_node(info_attribute="eye_master", node=eye_pack.pack_info_node, objects=[self.pack_info_node])
            i_node.connect_to_info_node(info_attribute="build_objects", node=eye_pack.pack_info_node, objects=[xeye_grp, crosseye_md])
    
    def _create_bit(self):
        # Create
        self.create_controls()

        # Connect
        self.connect_elements()

    def _cleanup_bit(self):
        # Vars
        self.bind_joints = None

        # Lock and Hide
        i_attr.lock_and_hide(self.aim_ctrl.control, attrs=["s", "v"], lock=True, hide=True)
        i_attr.lock_and_hide(self.aim_ctrl.gimbal, attrs=["s", "v"], lock=True, hide=True)
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)
        # i_utils.hide(self.base_joints)  # Hiding or Deleting messes up stitching, so just let it chill
        for jnt in self.base_joints:
            jnt.drawStyle.set(2)  # None
