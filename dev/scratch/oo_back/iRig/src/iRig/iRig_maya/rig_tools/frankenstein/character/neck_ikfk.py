from rig_tools.frankenstein.character.spine_simple import Build_Spine_Simple


class Build_Neck_IkFk(Build_Spine_Simple):
    def __init__(self):
        Build_Spine_Simple.__init__(self)
        
        # Specify Spine_Simple params
        self.start_name = "Base"
        self.end_name = "End"
        self.pivot_ctrl_position = "start"
        self.is_neck = True
        self.end_rot_order = "zxy"

        # Set the pack info
        self.joint_names = ["neck"]
        self.description = "Neck"
        self.accepted_stitch_types = ["Spine_Simple", "Spine_IkFk", "Cog"]

    def _create_pack(self):
        Build_Spine_Simple._create_pack(self)
        
        # Position it similar to the regular neck
        if self.do_pack_positions:
            self.base_joints[0].t.set([0.0, 5.43, -0.37])
        
        # Calc follow names
        self.start_follow_name = self.description + " " + self.start_name
        self.end_follow_name = self.description + " " + self.end_name

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_base_ctrl_top = pack_obj.pivot_ctrl.top_tfm
        pack_base_control = pack_obj.pivot_ctrl.control
        pack_end_control = pack_obj.end_ctrl.control
        pack_ikfk_switch_control = pack_obj.ikfk_switch_control
        pack_pin_grp = pack_obj.pin_grp
        pack_pivot_control = pack_obj.pivot_ctrl.top_tfm

        # Spine
        if parent_build_type.startswith("Spine"):
            # - Stitch
            parent_end_control = parent_obj.end_ctrl.control
            self.stitch_cmds.append({"parent": {"child": pack_base_ctrl_top, "parent": parent_end_control}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_base_control, "cns_type": "orient",
                                                "dv": parent_end_control, "options": parent_end_control}})

        # Cog
        elif parent_build_type == "Cog":
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            # - Parent
            self.stitch_cmds.append({"parent": {"child": pack_pivot_control, "parent": parent_cog_gimbal}})
            # - Constrain
            self.stitch_cmds.append({"constrain": {"args": [parent_cog_gimbal, pack_ikfk_switch_control], "kwargs": {"mo": True, "as_fn": "parent"}}})
            self.stitch_cmds.append({"constrain": {"args": [parent_cog_gimbal, pack_pin_grp], "kwargs": {"mo": True, "as_fn": "parent"}}})
            # - Add COG-driven follows
            self.stitch_cmds.append({"follow": {"driving": pack_base_control, "cns_type": "orient",
                                                "options": [parent_ground_ctrl, parent_root_ctrl]}})
            self.stitch_cmds.append({"follow": {"driving": pack_end_control, "cns_type": "orient",
                                                "options": [parent_ground_ctrl, parent_root_ctrl], 
                                                "dv" : parent_ground_ctrl}})
            # - Add a "fake follow" so the neck can follow its default hierarchy
            self.stitch_cmds.append(
                {"unique": {"cmd": "rig_attributes.create_follow_null(i_node.Node('%s'))" % pack_end_control, 
                            "unstitch": "rig_attributes.delete_follow_null(i_node.Node('%s'))" % pack_end_control}})

