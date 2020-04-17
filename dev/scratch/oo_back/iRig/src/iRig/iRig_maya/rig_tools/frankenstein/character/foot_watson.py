import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.geometry as rig_geometry
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.character.foot_master import Build_Foot_Master


class Build_Foot_Watson(Build_Foot_Master):
    def __init__(self):
        Build_Foot_Master.__init__(self)

        # Set the pack info
        self.joint_names[-1] = "end"
        # self.base_joint_positions = [[5.0, 4.0, 0.0], [5.0, 1.88, 2.12], [5.0, 1.88, 5.12]]

    def create_controls(self):
        # Create Control
        self.ik_ctrl = i_node.create("control", control_type='3D Cube', color=self.side_color, 
                                     name=self.base_name + "_Foot_Ik", degree=1, parent=self.pack_grp, 
                                     size=self.ctrl_size * 2.0, position_match=self.base_joints[0],
                                     additional_groups=["Xtra"], match_rotation=False, gimbal_color=self.side_color_scndy)
        ik_end_control = self.ik_ctrl.control  # Main Ctrl 
        
        # Add attributes
        self.roll_attr = i_attr.create(node=ik_end_control, ln="Roll", dv=0, k=True)
        self.toe_roll_attr = i_attr.create(node=ik_end_control, ln="ToeRoll", dv=0, k=True)
        self.roll_break_ball_attr = i_attr.create(node=ik_end_control, ln="RollBreakBall", dv=30, k=True)
        self.toe_curl_attr = i_attr.create(node=ik_end_control, ln="ToeCurl", dv=0, k=True)
        self.heel_pivot_attr = i_attr.create(node=ik_end_control, ln="HeelPivot", dv=0, k=True)
        self.ball_pivot_attr = i_attr.create(node=ik_end_control, ln="BallPivot", dv=0, k=True)
        self.toe_pivot_attr = i_attr.create(node=ik_end_control, ln="ToePivot", dv=0, k=True)
        self.bank_attr = i_attr.create(node=ik_end_control, ln="Bank", dv=0, k=True)
    
    
    def setup_ikfk(self):
        # Duplicate the foot joint
        self.ik_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="_Ik")
        self.fk_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="_Fk")
        
        # # Rename base joints with "Blend" in name  # :TODO: Renaming base joints is messing with the attr class rename for some reason
        # for jnt in self.base_joints:
        #     jnt.rename(jnt + "_Blend")
    
    
    def create_fk(self):
        # Create Ankle Ctrl
        self.fk_ankle_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy, size=self.ctrl_size, 
                                           position_match=self.fk_joints[0], name=self.fk_joints[0], with_gimbal=False,
                                           with_cns_grp=False, additional_groups=["Cns", "Drv"], parent=self.pack_grp, 
                                           constrain_geo=True, scale_constrain=False)
        
        # Create Toe Ctrl
        self.fk_toe_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy, size=self.ctrl_size, 
                                         position_match=self.fk_joints[1], name=self.fk_joints[1], with_gimbal=False,
                                         with_cns_grp=False, additional_groups=["Cns", "Drv"], parent=self.fk_ankle_ctrl.last_tfm, 
                                         constrain_geo=True, scale_constrain=False)
    
    
    def setup_groups_and_attrs(self):
        # Create Groups
        self.toe_roll_grp = self._create_subgroup(name="ToeRoll", xform_driver=self.toe_piv_loc)
        self.heel_roll_grp = self._create_subgroup(name="HeelRoll", xform_driver=self.heel_piv_loc)
        self.in_bank_grp = self._create_subgroup(name="InBank", xform_driver=self.in_piv_loc)
        self.out_bank_grp = self._create_subgroup(name="OutBank", xform_driver=self.out_piv_loc)
        self.toe_curl_grp = self._create_subgroup(name="ToeCurl", xform_driver=self.ik_joints[1])
        self.ball_roll_grp = self._create_subgroup(name="BallRoll", xform_driver=self.ik_joints[1])
        self.ball_pivot_grp = self._create_subgroup(name="BallPivot", xform_driver=self.ik_joints[1])
        self.toe_peel_grp = self._create_subgroup(name="ToePeel", xform_driver=self.toe_piv_loc)
        self.foot_root_grp = self._create_subgroup(name="FootRoot", xform_driver=self.out_bank_grp)
        
        # Parent
        i_utils.parent(self.toe_curl_grp, self.ball_roll_grp, self.ball_pivot_grp)
        self.ball_pivot_grp.set_parent(self.toe_peel_grp)
        if self.is_mirror:
            self.ball_pivot_grp.zero_out(t=False, s=False, r=True)
        self.ball_pivot_grp.ry.set(-180)
        self.toe_peel_grp.set_parent(self.toe_roll_grp)
        self.toe_roll_grp.set_parent(self.heel_roll_grp)
        self.heel_roll_grp.set_parent(self.in_bank_grp)
        self.in_bank_grp.set_parent(self.out_bank_grp)
        self.out_bank_grp.set_parent(self.foot_root_grp)
        self.foot_root_grp.set_parent(self.ik_ctrl.last_tfm)
        
        # Drive everything with conditions
        # - Create
        # -- Roll Neg Cnd
        self.roll_neg_cnd = i_node.create("condition", n=self.base_name + "_RollNeg_Cnd")
        self.roll_neg_cnd.colorIfFalseR.set(0)
        self.roll_neg_cnd.operation.set(4)
        # -- Bank Pos Cnd
        self.bank_pos_cnd = i_node.create("condition", n=self.base_name + "_BankPos_Cnd")
        self.bank_pos_cnd.colorIfFalseR.set(0)
        self.bank_pos_cnd.operation.set(4)  # Less Than
        # -- Bank Neg Cnd
        self.bank_neg_cnd = i_node.create("condition", n=self.base_name + "_BankNeg_Cnd")
        self.bank_neg_cnd.colorIfFalseR.set(0)
        self.bank_neg_cnd.operation.set(2)  # Greater Than
        # -- Roll for Ball Cnd
        self.roll_for_ball_cnd = i_node.create("condition", n=self.base_name + "_RollForwardBall_Cnd")
        self.roll_for_ball_cnd.operation.set(4)
        roll_ball_out = self.roll_for_ball_cnd.outColorR
        if not self.is_mirror:  # Left
            roll_ball_md = i_node.create("multiplyDivide", n=self.base_name + "_RollForwardBall_Md")
            roll_ball_md.input2X.set(-1)
            roll_ball_out.drive(roll_ball_md.input1X)
            roll_ball_out = roll_ball_md.outputX
        # -- Roll Toe Flip Cnd
        self.roll_toe_flip_cnd = i_node.create("condition", n=self.base_name + "_RollToeFlip_Cnd")
        self.roll_toe_flip_cnd.colorIfFalseR.set(0)
        self.roll_toe_flip_cnd.operation.set(2)
        # -- Toe Roll Cnd
        self.toe_roll_cnd = i_node.create("condition", n=self.base_name + "_ToeRoll_Cnd")
        self.toe_roll_cnd.colorIfFalseR.set(0)
        self.toe_roll_cnd.operation.set(2)
        # -- Toe Roll Md
        self.toe_roll_md = i_node.create("multiplyDivide", n=self.base_name + "_ToeRoll_Md")
        self.toe_roll_md.input1X.set(-1)
        # -- Bank Md
        bank_out = self.bank_attr
        if self.is_mirror:
            bank_md = i_node.create("multiplyDivide", n=self.base_name + "_Bank_Md")
            bank_md.input2X.set(-1)
            bank_out.drive(bank_md.input1X)
            bank_out = bank_md.outputX
        # -- Toe Roll Adl
        self.toe_roll_adl = i_node.create("addDoubleLinear", n=self.base_name + "_ToeRoll_Adl")
        
        # Drive the foot joint and the main ikh
        self.bank_attr.drive(self.bank_pos_cnd.firstTerm)
        self.bank_attr.drive(self.bank_neg_cnd.firstTerm)
        self.bank_pos_cnd.outColorR.drive(self.in_bank_grp.rz)
        self.bank_neg_cnd.outColorR.drive(self.out_bank_grp.rz)
        self.roll_attr.drive(self.roll_toe_flip_cnd.firstTerm)
        bank_out.drive(self.bank_pos_cnd.colorIfTrueR)
        bank_out.drive(self.bank_neg_cnd.colorIfTrueR)
        self.heel_pivot_attr.drive(self.heel_roll_grp.ry)
        self.toe_pivot_attr.drive(self.toe_roll_grp.ry)
        self.ball_pivot_attr.drive(self.ball_pivot_grp.ry)
        self.toe_curl_attr.drive(self.toe_curl_grp.rx)
        self.toe_roll_attr.drive(self.toe_roll_grp.rx)
        
        # Set up the roll system.
        # - Back Roll
        self.roll_attr.drive(self.roll_neg_cnd.firstTerm)
        self.roll_attr.drive(self.roll_neg_cnd.colorIfTrueR)
        self.roll_neg_cnd.outColorR.drive(self.heel_roll_grp.rx)
        # - Front Roll
        self.roll_attr.drive(self.roll_for_ball_cnd.firstTerm)
        self.roll_break_ball_attr.drive(self.roll_for_ball_cnd.secondTerm)
        self.roll_toe_flip_cnd.outColorR.drive(self.roll_for_ball_cnd.colorIfTrueR)
        self.roll_break_ball_attr.drive(self.roll_for_ball_cnd.colorIfFalseR)
        roll_ball_out.drive(self.ball_roll_grp.rx)
        # - Toe Roll
        self.roll_attr.drive(self.toe_roll_cnd.firstTerm)
        self.roll_break_ball_attr.drive(self.toe_roll_cnd.secondTerm)
        self.roll_break_ball_attr.drive(self.toe_roll_md.input2X)
        self.roll_attr.drive(self.toe_roll_adl.input1)
        self.toe_roll_md.outputX.drive(self.toe_roll_adl.input2)
        self.toe_roll_adl.output.drive(self.toe_roll_cnd.colorIfTrueR)
        self.toe_roll_cnd.outColorR.drive(self.toe_peel_grp.rx)
        
        # Drive the Ik Joints with the Groups
        i_constraint.constrain(self.toe_curl_grp, self.ik_joints[1], mo=True, as_fn="parent")
        i_constraint.constrain(self.ball_roll_grp, self.ik_joints[0], mo=True, as_fn="parent")
    
    def blend_ikfk(self):
        # Create IK FK Blend Control
        self._create_ikfk_switch(ik_controls=self.ik_ctrl.control, ik_joints=self.ik_joints, fk_joints=self.fk_joints, 
                                fk_controls=[self.fk_toe_ctrl.control, self.fk_ankle_ctrl.control],
                                position_match=self.base_joints[-1], offset_distance=1.5 * self.side_mult, watson_blend=True)

    def _cleanup_bit(self):
        # Cleanup Created Stuff & Store Class Attrs
        self.bind_joints = self.base_joints[:-1]
        
        # # Delete last tweak
        # self.tweak_ctrls[-1].top_tfm.delete()
        
        # Parent
        self.base_joints[0].set_parent(self.pack_bind_jnt_grp)
        # for jnt in self.base_joints:
        #     jnt.set_parent(self.pack_bind_jnt_grp)
        self.ik_joints[0].set_parent(self.pack_rig_jnt_grp)
        self.fk_joints[0].set_parent(self.pack_rig_jnt_grp)
        
        # Lock and Hide
        i_attr.lock_and_hide(self.fk_ankle_ctrl.control, attrs=["s", "v"], lock=True, hide=True)
        i_attr.lock_and_hide(self.fk_toe_ctrl.control, attrs=["s", "v"], lock=True, hide=True)

    def connect_elements(self):
        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], unlock=True)
        i_constraint.constrain(self.ik_ctrl.last_tfm, self.ikfk_switch_control, mo=True, as_fn="parent")
        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], lock=True) 

    def _create_bit(self):
        # Create
        self.create_controls()
        self.setup_ikfk()
        self.create_fk()
        self.setup_groups_and_attrs()
        # self.tweak_ctrls += rig_controls.create_tweaks(joints=self.base_joints, size=self.tweak_ctrl_size * 3.0, constrain=True)  # :note: Build for each so ikfk blend works. Then delete last.
        self.blend_ikfk()
        self.create_helpers(foot_control=self.ik_ctrl.control)

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        # - Pack
        # -- Need to do this also because if stitch_bit() is called in different class instance, the self variables won't exist
        pack_ankle_fk_control = pack_obj.fk_ankle_ctrl.control
        pack_ankle_fk_ctrl_offset = pack_obj.fk_ankle_ctrl.top_tfm
        pack_foot_ik_ctrl_top = pack_obj.ik_ctrl.top_tfm
        pack_foot_ik_ctrl = pack_obj.ik_ctrl.control
        pack_foot_ik_gimbal = pack_obj.ik_ctrl.gimbal
        pack_ball_roll_grp = pack_obj.ball_roll_grp

        if parent_build_type == "Leg_Watson":
            # Vars
            parent_ankle_fk_control = parent_obj.fk_ctrls[-1].control
            parent_ankle_ik_control = parent_obj.ik_end_ctrl.control
            parent_ankle_ik_gimbal = parent_obj.ik_end_ctrl.gimbal
            
            # # Parenting
            self.stitch_cmds.append({"parent": {"child": pack_foot_ik_ctrl_top, "parent": parent_ankle_ik_gimbal}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_ctrl_offset, "parent": parent_ankle_fk_control}})

            # Transfer foot control attributes
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_ctrl, "to": parent_ankle_ik_control, "ignore": ["GimbalVis"]}})
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_gimbal, "to": parent_ankle_ik_gimbal, "ignore": ["GimbalVis"]}})

            # Hide shapes of foot control from foot pack
            self.stitch_cmds.append({"force_vis": {"objects": pack_foot_ik_ctrl, "value" : 0}})

            # # Shift Follow Attrs to the bottom
            # self.stitch_cmds.append({"shift_follow_attrs": {"control": parent_ankle_ik_control}})
        
        elif parent_build_type == "Leg":
            # Vars
            # :note: Do only for Leg, not Leg_Watson because they're build so differently
            # -- Use the ones manually added in Limb instead of the PackMaster default lasts. These account for quad.
            # Parenting
            self.stitch_cmds.append({"parent": {"child": pack_foot_ik_ctrl_top, "parent": parent_obj.ik_end_ctrl.gimbal}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_ctrl_offset, "parent": parent_obj.last_fk_control}})
            
            # Constrain
            self.stitch_cmds.append({"constrain": {"args": [pack_ball_roll_grp, parent_obj.btm_locator], "kwargs": {"mo": True, "as_fn": "point"}}})
            self.stitch_cmds.append({"constrain": {"args": [pack_ball_roll_grp, parent_obj.follow_end_origin_grp], "kwargs": {"mo": True, "as_fn": "parent"}}})
            if parent_obj.is_quad:
                self.stitch_cmds.append({"constrain": {"args": [pack_ball_roll_grp, parent_obj.follow_end_origin_grp], "kwargs": {"mo": True, "as_fn": "parent"}}})
            
            # Transfer foot control attributes
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_ctrl, "to": parent_obj.ik_end_ctrl.control, "ignore": ["GimbalVis"]}})
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_gimbal, "to": parent_obj.ik_end_ctrl.gimbal, "ignore": ["GimbalVis"]}})

            # Hide shapes of foot control from foot pack
            self.stitch_cmds.append({"force_vis": {"objects": pack_foot_ik_ctrl, "value" : 0}})

            # # Shift Follow Attrs to the bottom
            # self.stitch_cmds.append({"shift_follow_attrs": {"control": parent_obj.ik_end_ctrl.control}})

        elif parent_build_type == "Cog":
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_ctrl, "cns_type": "parent",
                                                "options": [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]}})
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "parent",
                                                "options": [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]}})

        elif parent_build_type.startswith("Spine"):
            parent_hip_control = parent_obj.hip_ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_ctrl, "cns_type": "parent",
                                                "options": parent_hip_control}})
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "parent",
                                                "options": parent_hip_control}})

        elif parent_build_type == "Hip":
            parent_control = parent_obj.ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_ctrl, "cns_type": "parent",
                                                "options": parent_control}})
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "orient",
                                                "options": parent_control}})
