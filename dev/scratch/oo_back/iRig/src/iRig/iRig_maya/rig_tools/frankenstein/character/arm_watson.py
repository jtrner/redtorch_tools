import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.character.limb_watson import Build_Limb_Watson


class Build_Arm_Watson(Build_Limb_Watson):
    def __init__(self):
        Build_Limb_Watson.__init__(self)

        # Limb things
        self.limb_type = "arm"
        self.bend_ori = "xz"
        self.mid_nice_name = "elbow"

        # Set the pack info
        self.base_joint_positions = [[0.58, 5.26, -0.4], #[6, 60, 0], 
                                     [1.89, 5.26, -0.4], #[20, 60, 0], 
                                     [2.97, 5.26, -0.4], #[34, 60, 0], 
                                     [3.32, 5.26, -0.4], #[38, 60, 0],
                                     ]
        self.joint_names[2] = "wrist"
        self.description = "Arm"

    def _create_pack(self):
        # Orient the joints
        if not self.is_mirror:
            rig_joints.orient_joints(joints=self.base_joints, orient_as=self.orient_joints, up_axis=self.orient_joints_up_axis)
        # - That pesky last joint
        if not self.is_mirror and self.do_pack_positions:
            self.base_joints[-1].ry.set(-90 * self.side_mult)

        # Rotate so X points down, Z forward and Y down chain # Need to do AFTER orient joints
        if not self.is_mirror and self.do_pack_positions:
            # - Rotate
            self.base_joints[0].ry.set(90)
            self.base_joints[-1].rx.set(-90)
            # - Freeze
            self.base_joints[0].freeze(a=True, r=True, t=False, s=False)
            self.base_joints[-1].freeze(a=True, r=True, t=False, s=False)

        # Lock/Hide
        i_attr.lock_and_hide(node=self.base_joints[0], attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[1], attrs=["tx", "tz", "ry", "rz", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[2], attrs=["tx", "tz", "ry", "rz", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[3], attrs=["tx", "tz", "r", "s"], lock=True, hide=True)
        
        # Make sure to not orient joints after lock/hide
        self.do_orient_joints = False

