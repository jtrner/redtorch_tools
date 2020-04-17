import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.character.limb_watson import Build_Limb_Watson


class Build_Leg_Watson(Build_Limb_Watson):
    def __init__(self):
        Build_Limb_Watson.__init__(self)

        # Limb things
        self.limb_type = "leg"
        self.bend_ori = "xx"
        self.mid_nice_name = "knee"
        self.ikfk_default_state = 1
        self.is_leg = True

        # Set the pack info
        self.joint_names = ["upr", "lwr", "ankle", "end"]
        self.description = "Leg"
        # :note: Limb's base_joint_positions are actually the legs, since there's no in-between really

    def _create_pack(self):
        if self.do_pack_positions:
            # Orient the joints
            if not self.is_mirror:
                rig_joints.orient_joints(joints=self.base_joints, orient_as=self.orient_joints, 
                                         up_axis=self.orient_joints_up_axis, freeze=False)
            # - That pesky last joint
            if not self.is_mirror:
                self.base_joints[-1].r.set([180 * self.side_mult, -180 * self.side_mult, 0])
        
        self.foot_base_jnt = self.base_joints[-1]
        
        # Orienting doesn't actually get it working. Don't know why. Hopefully this hack is just temporary?
        if self.do_pack_positions:
            if not self.is_mirror:
                self.base_joints[0].xform(0, 180, 0, r=True, os=True, as_fn="rotate")
                self.base_joints[1].rx.set(self.base_joints[1].rx.get() * -1)
                self.base_joints[2].rx.set(self.base_joints[2].rx.get() * -1)

        # Lock/Hide
        i_attr.lock_and_hide(node=self.base_joints[0], attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[1], attrs=["tx", "tz", "ry", "rz", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[2], attrs=["tx", "tz", "ry", "rz", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.base_joints[3], attrs=["tx", "tz", "r", "s"], lock=True, hide=True)

        # Make sure to not orient joints after lock/hide
        self.do_orient_joints = False

