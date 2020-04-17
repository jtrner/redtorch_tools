from rig_tools.frankenstein.character.limb import Build_Limb_IkFk


class Build_Arm(Build_Limb_IkFk):
    def __init__(self):
        Build_Limb_IkFk.__init__(self)

        self.is_arm = True
        self.pv_pos_mult *= -1
        
        self.ikfk_switch_offset = [0, self.pack_size * -2 * (-1 * self.side_mult), 0]
        self.ikfk_default_mode = 0
        self.fk_rot_orders = ["zyx", "xyz", "xzy"]
        self.ik_rot_order = "xyz"

        # Set the pack info
        self.joint_names = ["shoulder", "elbow", "wrist"]
        self.description = "Arm"
        self.length_max = 3
        self.base_joint_positions = [[0.58, 5.26, -0.4], #[4.52525822677956, 18.315199853044447, -0.10655110146064395],
                                     [1.89, 5.25, -0.43], #[11.350084845934237, 17.023042871754043, -3.639944137307932],
                                     [2.98, 5.24, -0.33], #[15.351450463398809, 14.726073394522242, -0.08571608115967022],
                                     ]

