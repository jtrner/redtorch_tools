from rig_tools.frankenstein.character.limb import Build_Limb_IkFk


class Build_Leg(Build_Limb_IkFk):
    def __init__(self):
        Build_Limb_IkFk.__init__(self)

        self.end_ctrl_wedge = True
        self.ikfk_switch_offset = [0, 0, self.pack_size * -1.0] #   * -0.25
        self.ik_rot_order = "xzy"

        self.orient_joints_up_axis = "zup"

        # Set the pack info
        self.joint_names = ["hip", "knee", "ankle", "foot"]  # :note: "foot" is for quad legs
        self.description = "Leg"
        # :note: Limb's base_joint_positions are actually the legs, since there's no in-between really
