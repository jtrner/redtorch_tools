import maya.cmds as cmds

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Limb_Watson(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # Changeable pack-specific things
        self.limb_type = "limb"
        self.bend_ori = "xz"
        self.mid_nice_name = "mid"
        self.ikfk_default_state = 0
        self.is_leg = False
        
        # Vars
        self.bind_joints = []

        # Set the pack info
        self.joint_names = ["upr", "lwr", "btm", "end"]
        self.side = "L"
        self.description = "Limb"
        self.length = 4
        self.length_min = 4
        self.length_max = 4
        self.base_joint_positions = [[0.41, 2.98, -0.14], #[5.0, 32.0, 0.0], 
                                     [0.41, 1.64, -0.14], #[5.0, 18.0, 0.0], 
                                     [0.41, 0.71, -0.14], #[5.0, 4.0, 0.0], 
                                     [0.41, 0.46, -0.14], #[5.0, 0.0, -0.0],
                                     ]
        self.accepted_stitch_types = ["Clavicle", "Hip", "Cog", "Spine_Simple", "Spine_IkFk", "Head_Simple", "Head_Squash"]

    def _class_prompts(self):
        self.prompt_info["bend_ori"] = {"type": "option", "menu_items": ["xz", "zx", "xx", "zz"]}

    def create_controls(self):
        # End Xtra control
        self.end_xtra_ctrl = i_node.create("control", control_type="3D Snowflake", color="black", size=self.ctrl_size * 0.475, 
                                           position_match=self.base_joints[2], name=self.end_name + "_Xtra", with_gimbal=False,
                                           with_offset_grp=False, with_cns_grp=False, parent=self.blend_switch_grp)
        # self.end_xtra_ctrl.top_tfm.rx.set(0)

        # Constrain
        i_constraint.constrain(self.base_joints[2], self.end_xtra_ctrl.control, mo=True, as_fn="parent")
        
        # Connect to info node as IKFKSwitch to be able to query in stitching and other functions
        i_node.connect_to_info_node(info_attribute="IKFKSwitch_Ctrl", objects=self.end_xtra_ctrl.control, node=self.pack_info_node)
    
    def setup_ikfk(self):
        # # Freeze first joint
        # self.base_joints[0].freeze(a=True, t=True, r=True, s=True)
        
        # Duplicate
        self.ik_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="_Ik")
        self.fk_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="_Fk")
    
    def complete_ikfk(self):
        ik_vis_drive = [self.ik_ctrl_grp, self.ik_base_ctrl.top_tfm, self.pole_help_grp]
        fk_vis_drive = [self.fk_ctrls[0].top_tfm]
        
        Build_Master._create_ikfk_switch(self, ik_controls=ik_vis_drive, ik_joints=self.ik_joints,
                                         fk_joints=self.fk_joints, fk_controls=fk_vis_drive, 
                                         driven_objs=self.base_joints, watson_blend=True,
                                         ikfk_switch=self.end_xtra_ctrl.control, pv_control=self.ik_pv_ctrl.control)
    
    def create_fk(self):
        # Vars
        previous_fk = self.pack_ctrl_grp
        self.fk_ctrls = []
        
        # Loop
        for fk_jnt in self.fk_joints[:-1]:
            fk_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy, size=self.ctrl_size * 0.8, 
                                    rotate_order=2, position_match=fk_jnt, name=fk_jnt, parent=previous_fk, 
                                    constrain_geo=True, lock_hide_attrs=["s"])
            # :note: Original Watson has gimbals without offset/cns groups. Rigging wants these in though, so changed here.
            self.fk_ctrls.append(fk_ctrl)
            previous_fk = fk_ctrl.last_tfm
    
    def create_ik(self):
        """
        :note: From original script, there was a note:
        
        "Pole Vector Hack. Tried a vector math system, but it failed. So I am using this locator, and leave it for later
        use in ik/fk matching. Did a direct parent to the Lwr Arm Joint and it failed for getting the ik pole position
        properly."
        """ 
        # Create Pole Vector Target
        # - Loc
        self.pv_target_loc = i_node.create("locator", n=self.end_name + "_Pole_Target_Loc")
        # - Positions
        upr_pos = self.base_joints[0].xform(q=True, ws=True, rp=1)
        lwr_pos = self.base_joints[1].xform(q=True, ws=True, rp=1)
        end_pos = self.base_joints[2].xform(q=True, ws=True, rp=1)
        # - Curves
        self.pole_loft_upr_curve = i_node.create("curve", n=self.start_name + "PoleLoft", d=1, p=[upr_pos, lwr_pos])
        self.pole_loft_lwr_curve = i_node.create("curve", n=self.mid_name + "PoleLoft", d=1, p=[end_pos, lwr_pos])
        # - Loft
        self.pole_loft_nodes = i_node.create("loft", self.pole_loft_upr_curve, self.pole_loft_lwr_curve, ar=False, n=self.pv_target_loc + "_Surface")
        self.pole_loft = self.pole_loft_nodes[0]
        self.pole_loft_nodes[1].rename(self.start_name + "_Pole_Loft")
         
        # Flex System
        # - Add attrs
        self.flex_input_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln=self.limb_type + "FlexInput", dv=0)
        self.flex_min_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln=self.limb_type + "FlexMin", dv=0, min=0)
        self.flex_max_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln=self.limb_type + "FlexMax", dv=0, min=0)
        self.flex_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln=self.limb_type + "Flex", dv=0)
        # - Create Curve and Info
        flex_curve, flex_curve_cfs = i_node.duplicate(self.pole_loft.relatives(0, s=True).attr("v[0]"), n=self.base_name + "_Flex_Crv", as_curve=True) # self.start_name.replace("Upr", "Flex_")
        flex_ci = i_node.create("curveInfo", n=self.base_name + "_Flex_Ci")
        flex_curve_cfs.rename(self.base_name + "_Flex_CurveFromSurface")
        flex_curve.relatives(0, s=True).worldSpace.drive(flex_ci.inputCurve)
        flex_curve.set_parent(self.end_utl_grp)
        # - Remap
        flex_remap = i_node.create("remapValue", n=self.base_name + "_Flex_Rmap")
        flex_ci.arcLength.drive(self.flex_input_attr)
        flex_ci.arcLength.drive(flex_remap.inputValue)
        flex_remap.outputMax.set(0)
        flex_remap.outputMin.set(1)
        # - Scale Md
        flex_scale_md = i_node.create("multiplyDivide", n=self.base_name + "_Flex_Scl_Md")
        self.flex_min_attr.drive(flex_scale_md.input1X)
        self.flex_max_attr.drive(flex_scale_md.input1Y)
        flex_scale_md.outputX.drive(flex_remap.inputMin)
        flex_scale_md.outputY.drive(flex_remap.inputMax)
        # - Set ctrl attrs
        self.flex_min_attr.set(flex_ci.arcLength.get() * 0.33)
        self.flex_max_attr.set(flex_ci.arcLength.get() * 0.85)
        # - Final connection
        flex_remap.outValue.drive(self.flex_attr)
        
        # Drive Pole Loft with Clusters
        start_cd = i_deformer.CreateDeformer(name=self.base_name + "_PoleLoft_Start", 
                                                target=self.pole_loft_upr_curve.cv[0], parent=self.base_joints[0])
        start_clus = start_cd.cluster()
        mid_cd = i_deformer.CreateDeformer(name=self.base_name + "_PoleLoft_Mid", 
                                              target=[self.pole_loft_upr_curve.cv[1], self.pole_loft_lwr_curve.cv[1]], parent=self.base_joints[1])
        mid_clus = mid_cd.cluster()
        lwr_cd = i_deformer.CreateDeformer(name=self.base_name + "_PoleLoft_End", 
                                              target=self.pole_loft_lwr_curve.cv[0], parent=self.base_joints[2])
        lwr_clus = lwr_cd.cluster()
        
        # Follicle to drive Loc
        self.pole_loft_foll = i_node.create_single_follicle(surface=self.pole_loft, u_value=0.5, v_value=0.75, 
                                                                   name=self.base_name + "_Pole_Target") #  + "_PoleLoft"
        pole_move = i_utils.get_single_distance(from_node=self.base_joints[0], to_node=self.base_joints[2])
        i_node.copy_pose(driver=self.pole_loft_foll, driven=self.pv_target_loc, attrs=["t", "r"])
        self.pv_target_loc.tz.set(self.pv_target_loc.tz.get() - (pole_move * 0.6))
        i_constraint.constrain(self.pole_loft_foll, self.pv_target_loc, mo=True, as_fn="parent") # :note: doing at end to get it in the right spot.
        
        # Controls
        biggest_size = self.ctrl_size * 0.475
        # - Base
        self.ik_base_ctrl = i_node.create("control", control_type="3D Sphere", color=self.side_color, size=biggest_size, 
                                          position_match=self.ik_joints[0], name=self.ik_joints[0] + "_Base",
                                          parent=self.pack_ctrl_grp, with_gimbal=False)
        # - End
        self.ik_end_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color, size=biggest_size, 
                                         match_rotation=False, position_match=self.ik_joints[2], name=self.ik_joints[2],
                                         parent=self.pack_grp, with_gimbal=True)
        self.ik_end_ctrl.control.ro.set(2)
        # - Offset
        self.ik_offset_ctrl = i_node.create("control", control_type="3D Sphere", color=self.side_color, size=biggest_size * 1.02, #  * 0.85
                                            position_match=self.ik_joints[2], name=self.ik_joints[2] + "_Offset",
                                            parent=self.ik_end_ctrl.last_tfm, with_gimbal=True)
        self.ik_offset_ctrl.control.ro.set(2)
        # self.ik_offset_ctrl.gimbal.ro.set(2)
        # - Pv
        self.ik_pv_ctrl = i_node.create("control", control_type="3D Sphere", color=self.side_color, size=biggest_size, 
                                        position_match=self.pv_target_loc, match_rotation=False, 
                                        name=self.base_name + "_Pole_Ik", parent=self.pack_grp, with_gimbal=False)
        mlt = -1 if self.is_leg else 1  # not the best way to force the pv in front, but idk why it's not matching position atm.
        self.ik_pv_ctrl.top_tfm.tz.set(self.ik_pv_ctrl.top_tfm.tz.get() * mlt * 2)
        
        # Add Visibility attrs
        self.base_ik_vis_attr = rig_attributes.create_dis_attr(node=self.end_xtra_ctrl.control, ln="BaseIkCtrls", drive=self.ik_base_ctrl.control)
        i_attr.create_vis_attr(node=self.ik_end_ctrl.control, ln="Offset", drive=self.ik_offset_ctrl.control)
        i_attr.create_vis_attr(node=self.ik_end_ctrl.control, ln="Gimbal", drive=self.ik_offset_ctrl.gimbal)
        i_attr.create_vis_attr(node=self.ik_end_ctrl.control, ln="Target")  # This is not connected, but added in orig?
        
        # Prep for Ori Fix for Root Control
        temp_loc = i_node.create("locator", n="TempKill")
        temp_loc.set_parent(self.ik_end_ctrl.last_tfm)
        temp_loc.zero_out(s=False)
        temp_loc.rz.set(90)
        
        # Make Pv Help Curve
        pv_help_curve = i_node.create("curve", n=self.start_name + "_PoleHelp", d=1, p=[(0, 0, 0), (0, 0, 1)])
        help_a_cd = i_deformer.CreateDeformer(name=self.base_name + "_PoleHelpA_Upr",
                                                 target=pv_help_curve.cv[0], parent=self.helper_utl_grp)
        help_a_clus = help_a_cd.cluster()
        help_b_cd = i_deformer.CreateDeformer(name=self.base_name + "_PoleHelpB_Upr",
                                                 target=pv_help_curve.cv[1], parent=self.helper_utl_grp)
        help_b_clus = help_b_cd.cluster()
        i_constraint.constrain(self.ik_pv_ctrl.last_tfm, help_a_clus, mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_joints[1], help_b_clus, mo=False, as_fn="parent")
        pv_help_curve.relatives(0, s=True).overrideEnabled.set(0, l=True)
        pv_help_curve.set_parent(self.pole_help_grp)
        
        # Joint Settings
        self.ik_joints[1].jointTypeY.set(0)
        self.ik_joints[1].jointTypeZ.set(0)
        self.ik_joints[1].preferredAngleX.set(5)
        i_attr.lock_and_hide(node=self.ik_joints[1], attrs=["ry", "rz", "preferredAngle"], lock=True)
        
        # IKH
        ikh, eff = rig_joints.create_ikh_eff(start=self.ik_joints[0], end=self.ik_joints[2])
        ikh.set_parent(self.end_utl_grp)
        
        # Constrain
        i_constraint.constrain(self.ik_pv_ctrl.last_tfm, ikh, as_fn="poleVector")
        i_constraint.constrain(self.ik_base_ctrl.last_tfm, self.ik_joints[0], mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_offset_ctrl.gimbal, ikh, mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_offset_ctrl.gimbal, self.ik_joints[2], mo=True, as_fn="orient")
        
        # Group controls
        ik_ctrl_tops = [ctrl.top_tfm for ctrl in [self.ik_end_ctrl, self.ik_pv_ctrl]]
        self.ik_end_ctrl_grp = self._create_subgroup(name=self.end_name + "_Ik_Ctrl", add_base_name=False, children=ik_ctrl_tops)
        self.ik_ctrl_grp = self._create_subgroup(name="Ik_Ctrl", children=self.ik_end_ctrl_grp, parent=self.ctrl_grp)
        
        # Delete Temp Loc
        # :note: Not really sure why this was made since it doesn't seem to do anything, but it's in the original code
        temp_loc.delete()
    
    def connect_ikfk_bendy(self):
        # Create Locators
        ik_base_target_loc = i_node.create("locator", n=self.ik_base_ctrl.control + "_Target_Loc")
        ik_end_target_loc = i_node.create("locator", n=self.ik_end_ctrl.control + "_Target_Loc")
        fk0_target_loc = i_node.create("locator", n=self.fk_ctrls[0].control + "_Target_Loc")
        fk1_target_loc = i_node.create("locator", n=self.fk_ctrls[1].control + "_Target_Loc")
        fk2_target_loc = i_node.create("locator", n=self.fk_ctrls[2].control + "_Target_Loc")
        
        # Create Follicles
        ik_base_target_foll = i_node.create_single_follicle(surface=self.pole_loft, u_value=0.5, v_value=0.5, 
                                                                   name=self.ik_base_ctrl.control + "_Target")
        ik_end_target_foll = i_node.create_single_follicle(surface=self.pole_loft, u_value=0.5, v_value=0.5, 
                                                                  name=self.ik_end_ctrl.control + "_Target")
        fk0_target_foll = i_node.create_single_follicle(surface=self.upr_loft[0], u_value=0, v_value=0.5,
                                                               name=self.fk_ctrls[0].control + "_Target")
        fk1_target_foll = i_node.create_single_follicle(surface=self.lwr_loft[0], u_value=0, v_value=0.5,
                                                               name=self.fk_ctrls[1].control + "_Target")
        fk2_target_foll = i_node.create_single_follicle(surface=self.lwr_loft[0], u_value=1, v_value=0.5,
                                                               name=self.fk_ctrls[2].control + "_Target")
        
        # Constrain
        i_constraint.constrain(self.ik_base_ctrl.control, ik_base_target_loc, mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_end_ctrl.control, ik_end_target_loc, mo=False, as_fn="parent")
        i_constraint.constrain(fk0_target_foll, fk0_target_loc, mo=False, as_fn="parent")
        i_constraint.constrain(fk1_target_foll, fk1_target_loc, mo=False, as_fn="parent")
        i_constraint.constrain(self.fk_ctrls[2].control, fk2_target_loc, mo=False, as_fn="parent")
        
        # Store values as a string attribute
        # Eventually, when the IkFk Match script in animation is rewritten to be more consolidated and stable, will
        # want to change these from a string attribute to multiple message attribute connections
        ikfk_rot = fk2_target_loc.r.get()
        stored_data = {"UprFk" : fk0_target_loc, "LwrFk" : fk1_target_loc, "EndFk" : fk2_target_loc,
                       "BaseIk" : ik_base_target_loc, "EndIk" : ik_end_target_loc, "PoleIk" : self.pv_target_loc,
                       "BaseIkCtrl" : self.ik_base_ctrl.control, "EndIkCtrl" : self.ik_end_ctrl.control,
                       "PoleIkCtrl" : self.ik_pv_ctrl.control, "UprJnt" : self.base_joints[0],
                       "LwrJnt" : self.base_joints[1], "EndJnt" : self.base_joints[2], "UprFkCtrl" : self.fk_ctrls[0].control,
                       "LwrFkCtrl" : self.fk_ctrls[1].control, "EndFkCtrl" : self.fk_ctrls[2].control,
                       "FkWristOffsetRX" : ikfk_rot[0], "FkWristOffsetRY" : ikfk_rot[1], "FkWristOffsetRZ" : ikfk_rot[2]}
        for dk, dv in stored_data.items():
            dv = i_utils.convert_data(dv)
            stored_data[dk] = dv
        self.match_data_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="IkFkMatchData", dt="string", use_existing=True, dv=str(stored_data))
        
        # Cleanup
        self.pole_vec_grp = self._create_subgroup(name=self.end_name + "_PoleVec_Grp", parent=self.end_utl_grp,
                                                        children=[self.pole_loft_foll, self.pole_loft_upr_curve, self.pole_loft_lwr_curve, 
                                                                  self.pole_loft, ik_base_target_foll, ik_end_target_foll, 
                                                                  fk0_target_foll, fk1_target_foll, fk2_target_foll])
        i_utils.parent(self.pv_target_loc, ik_base_target_loc, ik_end_target_loc, fk0_target_loc, fk1_target_loc, fk2_target_loc, self.ikfk_data_grp)
    
    def create_stretch(self):
        # Add Attrs
        self.lwr_lenadd_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="Lwr" + self.limb_type + "LengthAdd", dv=0, k=True)
        self.upr_lenadd_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="Upr" + self.limb_type + "LengthAdd", dv=0, k=True)
        self.str_onoff_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="StretchOnOff", dv=1, min=0, max=1, k=True)
        
        # Vars
        end_ik_name = self.ik_joints[2].name
        
        # Locators
        base_str_loc = i_node.create("locator", n=end_ik_name + "_BaseStretch_Loc")
        end_str_loc = i_node.create("locator", n=end_ik_name + "_EndStretch_Loc")
        self.base_ref_loc = i_node.create("locator", n=end_ik_name + "_BaseRef_Loc")
        self.end_ref_loc = i_node.create("locator", n=end_ik_name + "_EndRef_Loc")
        mid_lock_loc = i_node.create("locator", n=end_ik_name + "_PoleLock_Loc")
        # - Group
        self.ik_str_loc_grp = self._create_subgroup(name=self.end_name + "_Stretch_Loc_Grp", add_base_name=False,
                                                          children=[base_str_loc, mid_lock_loc, end_str_loc], parent=self.end_utl_grp)
        self.end_scale_grp = self._create_subgroup(name=self.end_name + "_Scale_Grp", add_base_name=False,
                                                         children=[self.base_ref_loc], parent=self.pack_utility_cns_grp)
        
        # Constrain and Position
        i_constraint.constrain(self.ik_pv_ctrl.control, mid_lock_loc, mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_base_ctrl.control, base_str_loc, mo=False, as_fn="parent")
        i_constraint.constrain(self.ik_offset_ctrl.gimbal, end_str_loc, mo=False, as_fn="parent")
        i_node.copy_pose(driver=self.ik_base_ctrl.control, driven=self.base_ref_loc, attrs=["t", "r"])
        i_node.copy_pose(driver=self.ik_end_ctrl.control, driven=self.end_ref_loc, attrs=["t", "r"])
        
        # Create Math Nodes
        str_db = i_node.create("distanceBetween", n=end_ik_name + "_Stretch_Db")
        ref_db = i_node.create("distanceBetween", n=end_ik_name + "_Ref_Db")
        upr_db = i_node.create("distanceBetween", n=end_ik_name + "_Upr_Db")
        lwr_db = i_node.create("distanceBetween", n=end_ik_name + "_Lwr_Db")
        str_main_md = i_node.create("multiplyDivide", n=end_ik_name + "_StretchMain_Md")
        str_calc_md = i_node.create("multiplyDivide", n=end_ik_name + "_StretchCalc_Md")
        str_calc_md.operation.set(2)
        str_limit_cnd = i_node.create("condition", n=end_ik_name + "_StretchLimit_Md")
        str_limit_cnd.operation.set(2)
        str_limit_cnd.secondTerm.set(1)
        upr_len_adl = i_node.create("addDoubleLinear", n=end_ik_name + "_UprLength_Adl")
        lwr_len_adl = i_node.create("addDoubleLinear", n=end_ik_name + "_LwrLength_Adl")
        
        # Connect
        self.base_ref_loc.worldMatrix.drive(ref_db.inMatrix1)
        self.end_ref_loc.worldMatrix.drive(ref_db.inMatrix2)
        base_str_loc.worldMatrix.drive(str_db.inMatrix1)
        end_str_loc.worldMatrix.drive(str_db.inMatrix2)
        str_db.distance.drive(str_calc_md.input1X)
        ref_db.distance.drive(str_calc_md.input2X)
        str_calc_md.outputX.drive(str_limit_cnd.firstTerm)
        str_calc_md.outputX.drive(str_limit_cnd.colorIfTrueR)
        
        # Get Limb Scale
        self.limb_scale = int(ref_db.distance.get()) * 0.5
        
        # Convert Stretch to Joint Translate Y
        jnt_scl_val_md = i_node.create("multiplyDivide", n=end_ik_name + "_TranslateYScale_Md")
        jnt_scl_val_md.input1X.set(1)
        jnt_scl_val_md.input1Y.set(1)
        jnt_scl_val_md.input2X.set(self.ik_joints[1].ty.get())
        jnt_scl_val_md.input2Y.set(self.ik_joints[2].ty.get())
        jnt_trn_val_md = i_node.create("multiplyDivide", n=end_ik_name + "_TranslateY_Md")
        jnt_scl_val_md.outputX.drive(jnt_trn_val_md.input2X)
        jnt_scl_val_md.outputY.drive(jnt_trn_val_md.input2Y)
        str_limit_cnd.outColorR.drive(jnt_trn_val_md.input1X)
        str_limit_cnd.outColorR.drive(jnt_trn_val_md.input1Y)
        
        # Stretch On/Off
        str_onoff_bc = i_node.create("blendColors", n=end_ik_name + "_StretchOnOff_Bc")
        jnt_trn_val_md.outputX.drive(str_onoff_bc.color1R)
        jnt_trn_val_md.outputY.drive(str_onoff_bc.color1G)
        jnt_scl_val_md.outputX.drive(str_onoff_bc.color2R)
        jnt_scl_val_md.outputY.drive(str_onoff_bc.color2G)
        self.str_onoff_attr.drive(str_onoff_bc.blender)
        str_onoff_bc.outputR.drive(upr_len_adl.input1)
        str_onoff_bc.outputG.drive(lwr_len_adl.input1)
        
        # Side-Specific
        if self.side_mult == -1:
            flip_md = i_node.create("multiplyDivide", n=end_ik_name + "_Flip_Md")
            self.upr_lenadd_attr.drive(flip_md.input1X)
            self.lwr_lenadd_attr.drive(flip_md.input1Y)
            flip_md.input2X.set(-1)
            flip_md.input2Y.set(-1)
            flip_md.outputX.drive(upr_len_adl.input2)
            flip_md.outputY.drive(lwr_len_adl.input2)
        else:
            self.upr_lenadd_attr.drive(upr_len_adl.input2)
            self.lwr_lenadd_attr.drive(lwr_len_adl.input2)
        
        # Add in the knee lock override
        base_str_loc.worldMatrix.drive(upr_db.inMatrix1)
        mid_lock_loc.worldMatrix.drive(upr_db.inMatrix2)
        end_str_loc.worldMatrix.drive(lwr_db.inMatrix1)
        mid_lock_loc.worldMatrix.drive(lwr_db.inMatrix2)
        
        # Drive the TranslateY of the lower and end joints
        # Need a blend to run this when set to 1, and a static when not
        # Need a blend to override the joint scale for basic stretch to turn it off when this is turned on, but also
        # keep the upper/lower length behaviour
        pv_lock_onoff_bc = i_node.create("blendColors", n=end_ik_name + "_PoleLockOnOff_Bc")
        # Side-Specific
        if self.side_mult == -1:
            pole_flip_md = i_node.create("multiplyDivide", n=self.base_name + "_EndIk_PoleFlip_Md")
            upr_db.distance.drive(pole_flip_md.input1X)
            lwr_db.distance.drive(pole_flip_md.input1Y)
            pole_flip_md.input2X.set(-1)
            pole_flip_md.input2Y.set(-1)
            pole_flip_md.outputX.drive(pv_lock_onoff_bc.color1R)
            pole_flip_md.outputY.drive(pv_lock_onoff_bc.color1G)
        else:
            upr_db.distance.drive(pv_lock_onoff_bc.color1R)
            lwr_db.distance.drive(pv_lock_onoff_bc.color1G)

        upr_len_adl.output.drive(pv_lock_onoff_bc.color2R)
        lwr_len_adl.output.drive(pv_lock_onoff_bc.color2G)

        self.pole_lock_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln=self.mid_nice_name + "PoleLock", dv=0, min=0, max=1, k=True)
        self.pole_lock_attr.drive(pv_lock_onoff_bc.blender)

        pv_lock_onoff_bc.outputR.drive(self.ik_joints[1].ty)
        pv_lock_onoff_bc.outputG.drive(self.ik_joints[2].ty)
    
    def create_bendy(self):
        # Create Curves
        # - Starting Vars
        l_val_aa = [-1, 0, 0]
        l_val_ab = [1, 0, 0]
        l_val_ba = [-1, 0, 0]
        l_val_bb = [1, 0, 0]
        # - Get bone lengths
        upr_len = self.base_joints[1].ty.get() * 0.05
        if upr_len < 0:
            upr_len *= -1
        upr_len_min = upr_len * -1
        lwr_len = self.base_joints[2].ty.get() * 0.05
        if lwr_len < 0:
            lwr_len *= -1
        lwr_len_min = lwr_len * -1
        # - Round
        upr_len = round(upr_len, 3)
        upr_len_min = round(upr_len_min, 3)
        lwr_len = round(lwr_len, 3)
        lwr_len_min = round(lwr_len_min, 3)
        # - Update based on limb ori
        if self.bend_ori[0].upper() == "X":
            l_val_aa = [upr_len_min, 0, 0]
            l_val_ab = [upr_len, 0, 0]
        elif self.bend_ori[0].upper() == "Z":
            l_val_aa = [0, 0, upr_len_min]
            l_val_ab = [0, 0, upr_len]
        if self.bend_ori[1].upper() == "X":
            l_val_ba = [lwr_len_min, 0, 0]
            l_val_bb = [lwr_len, 0, 0]
        elif self.bend_ori[1].upper() == "Z":
            l_val_ba = [0, 0, lwr_len_min]
            l_val_bb = [0, 0, lwr_len]
        # - Create Curves
        curve_a = i_node.create("curve", n=self.start_name + "_LimbLoft_Crv", d=1, p=[l_val_aa, l_val_ab])
        curve_b = i_node.create("curve", n=self.mid_name + "_LimbLoftA_Crv", d=1, p=[l_val_aa, l_val_ab])
        curve_c = i_node.create("curve", n=self.mid_name + "_LimbLoftB_Crv", d=1, p=[l_val_ba, l_val_bb])
        curve_d = i_node.create("curve", n=self.end_name + "_LimbLoft_Crv", d=1, p=[l_val_ba, l_val_bb])
        
        # Constrain
        ribbon_pac = i_constraint.constrain(self.base_joints[0], curve_a, mo=False, n=curve_a.name.replace("_Crv", "_RibbonDriver_Pac"), as_fn="parent")
        
        # Root Twist Driver Setup
        self.root_auto_twist_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="RootAutoTwist", dv=1, min=0, max=1, k=True)
        root_twist_md = i_node.create("multiplyDivide", n=self.start_name + "_Twist_Md")
        root_twist_onoff_md = i_node.create("multiplyDivide", n=self.start_name + "_TwistOnOff_Md")
        root_twist_md.input2X.set(-1)
        self.base_joints[0].ry.drive(root_twist_md.input1X)
        root_twist_md.outputX.drive(root_twist_onoff_md.input1X)
        root_twist_onoff_md.outputX.drive(ribbon_pac + ".target[0].targetOffsetRotateY")  # :note: pymel needs this string
        self.root_auto_twist_attr.drive(root_twist_onoff_md.input2X)
        
        # Constrain More
        i_constraint.constrain(self.base_joints[1], curve_b, mo=False, n=curve_b.name.replace("_Crv", "_RibbonDriver_Poc"), as_fn="point")
        i_constraint.constrain(self.base_joints[1], curve_b, mo=False, n=curve_b.name.replace("_Crv", "_RibbonDriver_Oc"), as_fn="orient")
        i_constraint.constrain(self.base_joints[1], curve_c, mo=False, n=curve_c.name.replace("_Crv", "_RibbonDriver_Pac"), as_fn="parent")
        i_constraint.constrain(self.base_joints[2], curve_d, mo=False, n=curve_d.name.replace("_Crv", "_RibbonDriver_Pac"), as_fn="parent")
        
        # Loft
        self.upr_loft = i_node.create("loft", curve_a, curve_b, n=self.start_name + "_TwistRibbon", ar=False)
        self.upr_loft[1].rename(self.upr_loft[0].name + "_Loft")
        self.lwr_loft = i_node.create("loft", curve_c, curve_d, n=self.mid_name + "_TwistRibbon", ar=False)
        self.lwr_loft[1].rename(self.lwr_loft[0].name + "_Loft")
        
        # Follicles
        # - Upper
        upr_base_foll = i_node.create_single_follicle(surface=self.upr_loft[0], u_value=0, v_value=0.5,
                                                             name=self.start_name + "_Base_" + self.limb_type)
        upr_mid_foll = i_node.create_single_follicle(surface=self.upr_loft[0], u_value=0.5, v_value=0.5,
                                                            name=self.start_name + "_Mid_" + self.limb_type)
        upr_end_foll = i_node.create_single_follicle(surface=self.upr_loft[0], u_value=1.0, v_value=0.5,
                                                            name=self.start_name + "_End_" + self.limb_type)
        # - Lower
        lwr_base_foll = i_node.create_single_follicle(surface=self.lwr_loft[0], u_value=0, v_value=0.5,
                                                             name=self.mid_name + "_Base_" + self.limb_type)
        lwr_mid_foll = i_node.create_single_follicle(surface=self.lwr_loft[0], u_value=0.5, v_value=0.5,
                                                            name=self.mid_name + "_Mid_" + self.limb_type)
        lwr_end_foll = i_node.create_single_follicle(surface=self.lwr_loft[0], u_value=1.0, v_value=0.5,
                                                            name=self.mid_name + "_End_" + self.limb_type)
        folls = [upr_base_foll, upr_mid_foll, upr_end_foll, lwr_base_foll, lwr_mid_foll, lwr_end_foll]
        
        # Group
        self.twist_utl_grp = self._create_subgroup(name=self.end_name + "_Twist_Utl", parent=self.end_utl_grp,
                                                         children=folls + [self.upr_loft[0], self.lwr_loft[0], curve_a, curve_b,
                                                                           curve_c, curve_d])
        
        # Locators
        # - Upper
        upr_base_loc = i_node.create("locator", n=self.mid_name + "_Base_" + self.limb_type + "_Up_Loc")
        upr_mid_loc = i_node.create("locator", n=self.start_name + "_Mid_" + self.limb_type + "_Pos_Loc")
        upr_end_loc = i_node.create("locator", n=self.mid_name + "_End_" + self.limb_type + "_Up_Loc")
        # - Lower
        lwr_base_loc = i_node.create("locator", n=self.start_name + "_Base_" + self.limb_type + "_Up_Loc")
        lwr_mid_loc = i_node.create("locator", n=self.mid_name + "_Mid_" + self.limb_type + "_Pos_Loc")
        lwr_end_loc = i_node.create("locator", n=self.start_name + "_End_" + self.limb_type + "_Up_Loc")
        # - Clear Selection
        i_utils.select(cl=True)
        # - Parent / Set Attrs
        # -- Upper Base
        upr_base_loc.set_parent(upr_base_foll)
        upr_base_loc.zero_out(s=False)
        upr_base_loc.tz.set(self.limb_scale)
        # -- Upper Mid
        upr_mid_loc.set_parent(upr_mid_foll)
        upr_mid_loc.zero_out(s=False)
        # -- Upper End
        upr_end_loc.set_parent(upr_end_foll)
        upr_end_loc.zero_out(s=False)
        upr_end_loc.tz.set(self.limb_scale)
        # -- Lower Base
        lwr_base_loc.set_parent(lwr_base_foll)
        lwr_base_loc.zero_out(s=False)
        lwr_base_loc.tz.set(self.limb_scale)
        # -- Lower Mid
        lwr_mid_loc.set_parent(lwr_mid_foll)
        lwr_mid_loc.zero_out(s=False)
        # -- Lower End
        lwr_end_loc.set_parent(lwr_end_foll)
        lwr_end_loc.zero_out(s=False)
        lwr_end_loc.tz.set(self.limb_scale)
        
        # This results in a nurbs plane with twist vector system. Later these are packed as Limb Ribbons
        
        # Create Controls
        bend_size = self.ctrl_size * 0.45
        ctrl_rot = [0, 0, 0] if self.is_leg else [0, 270, -90]
        self.upr_bend_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color_tertiary,
                                           size=bend_size, position_match=upr_mid_loc, name=self.base_name + "_Upr_Bend",
                                           with_gimbal=False, parent=self.mid_bend_ctrl_grp, lock_hide_attrs=["sx", "sz", "rx", "rz", "ro"])
        self.upr_bend_ctrl.top_tfm.xform(ctrl_rot[0], ctrl_rot[1], ctrl_rot[2], r=True, os=True, as_fn="rotate")
        
        self.lwr_bend_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color_tertiary,
                                           size=bend_size, position_match=lwr_mid_loc, name=self.base_name + "_Lwr_Bend",
                                           with_gimbal=False, parent=self.mid_bend_ctrl_grp, lock_hide_attrs=["sx", "sz", "rx", "rz", "ro"])
        self.lwr_bend_ctrl.top_tfm.xform(ctrl_rot[0], ctrl_rot[1], ctrl_rot[2], r=True, os=True, as_fn="rotate")
        
        self.mid_bend_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color_tertiary,
                                           size=bend_size, position_match=self.base_joints[1], name=self.base_name + "_Md_Bend",
                                           with_gimbal=False, parent=self.mid_bend_ctrl_grp, lock_hide_attrs=["s", "rx", "rz", "ro"])
        
        # Constrain Controls
        md_oc_offset = [0, 0, 0] if self.is_leg else [0, 0, 90]
        oc = i_constraint.constrain(self.base_joints[0], self.base_joints[1], self.mid_bend_ctrl.top_tfm, mo=False, offset=md_oc_offset, as_fn="orient")
        oc.interpType.set(2)
        i_constraint.constrain(self.base_joints[1], self.mid_bend_ctrl.top_tfm, mo=False, as_fn="point")
        i_constraint.constrain(upr_mid_loc, self.upr_bend_ctrl.top_tfm, mo=True, as_fn="parent")
        i_constraint.constrain(lwr_mid_loc, self.lwr_bend_ctrl.top_tfm, mo=True, as_fn="parent")
        
        # Ribbons now need joints to run the real ribbon geometry that will drive the bind joints
        # 3 joints for each ribbon
        i_utils.select(cl=True)
        upr_base_ribbon_drv_jnt = i_node.create("joint", n=self.start_name + "_BaseRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        upr_mid_ribbon_drv_jnt = i_node.create("joint", n=self.start_name + "_MidRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        upr_end_ribbon_drv_jnt = i_node.create("joint", n=self.start_name + "_EndRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        lwr_base_ribbon_drv_jnt = i_node.create("joint", n=self.mid_name + "_BaseRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        lwr_mid_ribbon_drv_jnt = i_node.create("joint", n=self.mid_name + "_MidRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        lwr_end_ribbon_drv_jnt = i_node.create("joint", n=self.mid_name + "_EndRibbon_Drv_Jnt", radius=self.joint_radius)
        i_utils.select(cl=True)
        # - Parent
        drv_jnts = [upr_base_ribbon_drv_jnt, upr_mid_ribbon_drv_jnt, upr_end_ribbon_drv_jnt,
                    lwr_base_ribbon_drv_jnt, lwr_mid_ribbon_drv_jnt, lwr_end_ribbon_drv_jnt]
        self.ribbon_drv_jnt_grp = self._create_subgroup(name="Driver_Jnt", children=drv_jnts)
        
        # Create Controls for Base and End joints of the bendy
        self.upr_base_bend_ctrl = i_node.create("control", control_type="3D Hemisphere", color=self.side_color_tertiary,
                                                size=bend_size * 0.7, position_match=upr_base_ribbon_drv_jnt, with_offset_grp=False, 
                                                additional_groups=["Driver"], parent=self.mid_bend_ctrl_grp, with_gimbal=False,
                                                name=self.start_name + "_BaseBend", lock_hide_attrs=["sx", "sz", "t", "ro"])
        
        self.upr_end_bend_ctrl = i_node.create("control", control_type="3D Hemisphere", color=self.side_color_tertiary,
                                               size=bend_size * 0.7, position_match=upr_end_ribbon_drv_jnt, with_offset_grp=False, 
                                               additional_groups=["Driver"], parent=self.mid_bend_ctrl_grp, with_gimbal=False,
                                               name=self.start_name + "_EndBend", flip_shape=[180, 0, 0], 
                                               lock_hide_attrs=["sx", "sz", "t", "ro"])
        # self.upr_end_bend_ctrl.top_tfm.rx.set(180)
        
        self.lwr_base_bend_ctrl = i_node.create("control", control_type="3D Hemisphere", color=self.side_color_tertiary, 
                                                size=bend_size * 0.7, position_match=lwr_base_ribbon_drv_jnt, with_offset_grp=False,
                                                additional_groups=["Driver"], parent=self.mid_bend_ctrl_grp, with_gimbal=False,
                                                name=self.mid_name + "_BaseBend", lock_hide_attrs=["sx", "sz", "t", "ro"])
        
        self.lwr_end_bend_ctrl = i_node.create("control", control_type="3D Hemisphere", color=self.side_color_tertiary,
                                               size=bend_size * 0.7, position_match=lwr_end_ribbon_drv_jnt, with_offset_grp=False,
                                               additional_groups=["Driver"], parent=self.mid_bend_ctrl_grp, with_gimbal=False,
                                               name=self.mid_name + "_EndBend", flip_shape=[180, 0, 0],
                                               lock_hide_attrs=["sx", "sz", "t", "ro"])
        # self.lwr_end_bend_ctrl.top_tfm.rx.set(180)
        # - Shape Tweaking
        base_cvs = []
        end_cvs = []
        cv_indexes = ["0:10", "0:7", "0:10"]
        upr_base_shapes = self.upr_base_bend_ctrl.control_shapes
        lwr_base_shapes = self.lwr_base_bend_ctrl.control_shapes
        upr_end_shapes = self.upr_end_bend_ctrl.control_shapes
        lwr_end_shapes = self.lwr_end_bend_ctrl.control_shapes
        for i in range(len(upr_base_shapes)):
            cv = ".cv[%s]" % cv_indexes[i]
            base_cvs += [upr_base_shapes[i] + cv, lwr_base_shapes[i] + cv]
            end_cvs += [upr_end_shapes[i] + cv, lwr_end_shapes[i] + cv]
        i_utils.xform(0, -0.33, 0, end_cvs, r=True, os=True, as_fn="move")
        i_utils.xform(0, 0.33, 0, base_cvs, r=True, os=True, as_fn="move")
        
        # Point drivers to follicles
        i_constraint.constrain(upr_base_foll, self.upr_base_bend_ctrl.driver_grp, mo=False, as_fn="point")
        i_constraint.constrain(self.mid_bend_ctrl.last_tfm, self.upr_end_bend_ctrl.driver_grp, mo=False, as_fn="point")
        i_constraint.constrain(self.mid_bend_ctrl.last_tfm, self.lwr_base_bend_ctrl.driver_grp, mo=False, as_fn="point")
        i_constraint.constrain(lwr_end_foll, self.lwr_end_bend_ctrl.driver_grp, mo=False, as_fn="point")
        
        # Aim drivers to BendyControl / Up Locs. Follow the mid ctrl to help control arch.
        i_constraint.constrain(upr_mid_ribbon_drv_jnt, self.upr_base_bend_ctrl.driver_grp, aim=[0, 1, 0], u=[0, 0, -1],
                          wut="object", wuo=upr_base_loc, mo=False, as_fn="aim")
        i_constraint.constrain(upr_mid_ribbon_drv_jnt, self.upr_end_bend_ctrl.driver_grp, aim=[0, -1, 0], u=[0, 0, -1],
                          wut="object", wuo=upr_end_loc, mo=False, as_fn="aim")
        i_constraint.constrain(lwr_mid_ribbon_drv_jnt, self.lwr_base_bend_ctrl.driver_grp, aim=[0, 1, 0], u=[0, 0, -1],
                          wut="object", wuo=lwr_base_loc, mo=False, as_fn="aim")
        i_constraint.constrain(lwr_mid_ribbon_drv_jnt, self.lwr_end_bend_ctrl.driver_grp, aim=[0, -1, 0], u=[0, 0, -1],
                          wut="object", wuo=lwr_end_loc, mo=False, as_fn="aim")
        
        # Constrain/Connect joints to controls
        i_constraint.constrain(self.upr_base_bend_ctrl.last_tfm, upr_base_ribbon_drv_jnt, mo=False, as_fn="parent")
        i_constraint.constrain(self.upr_end_bend_ctrl.last_tfm, upr_end_ribbon_drv_jnt, mo=False, as_fn="parent")
        i_constraint.constrain(self.lwr_base_bend_ctrl.last_tfm, lwr_base_ribbon_drv_jnt, mo=False, as_fn="parent")
        i_constraint.constrain(self.lwr_end_bend_ctrl.last_tfm, lwr_end_ribbon_drv_jnt, mo=False, as_fn="parent")
        self.upr_base_bend_ctrl.control.sy.drive(upr_base_ribbon_drv_jnt.sy)
        self.upr_end_bend_ctrl.control.sy.drive(upr_end_ribbon_drv_jnt.sy)
        self.lwr_base_bend_ctrl.control.sy.drive(lwr_base_ribbon_drv_jnt.sy)
        self.lwr_end_bend_ctrl.control.sy.drive(lwr_end_ribbon_drv_jnt.sy)
        i_constraint.constrain(self.upr_bend_ctrl.last_tfm, upr_mid_ribbon_drv_jnt, mo=False, as_fn="parent")
        i_constraint.constrain(self.lwr_bend_ctrl.last_tfm, lwr_mid_ribbon_drv_jnt, mo=False, as_fn="parent")
        
        # Make nurbs planes and skin to these and run our real follicles / do the volume system
        self.upr_bind_loft = i_node.create("loft", curve_a, curve_b, n=self.start_name + "_BindRibbon_Crv", ar=False, ch=False, ss=2)
        self.lwr_bind_loft = i_node.create("loft", curve_c, curve_d, n=self.mid_name + "_BindRibbon_Crv", ar=False, ch=False, ss=2)
        i_utils.select(cl=True)
        i_node.create("skinCluster", upr_base_ribbon_drv_jnt, upr_mid_ribbon_drv_jnt, upr_end_ribbon_drv_jnt, self.upr_bind_loft, 
                      n=self.upr_bind_loft + "_Skin")
        i_node.create("skinCluster", lwr_base_ribbon_drv_jnt, lwr_mid_ribbon_drv_jnt, lwr_end_ribbon_drv_jnt, self.lwr_bind_loft, 
                      n=self.lwr_bind_loft + "_Skin")
        
        # Add twist ability
        upr_twist_grp = self._create_subgroup(name=upr_end_loc.name + "_Twist_Grp", children=upr_end_loc,
                                                    zero_out=False, parent=upr_end_foll)
        lwr_twist_grp = self._create_subgroup(name=lwr_end_loc.name + "_Twist_Grp", children=lwr_end_loc,
                                                    zero_out=False, parent=lwr_base_foll)
        self.mid_bend_ctrl.control.ry.drive(upr_twist_grp.rx)
        self.mid_bend_ctrl.control.ry.drive(lwr_twist_grp.rx)
        
        # Add visibility attr
        bend_ctrls = [self.upr_bend_ctrl, self.lwr_bend_ctrl, self.mid_bend_ctrl, self.upr_base_bend_ctrl, 
                      self.upr_end_bend_ctrl, self.lwr_base_bend_ctrl, self.lwr_end_bend_ctrl]
        self.bendy_vis_attr = rig_attributes.create_dis_attr(node=self.end_xtra_ctrl.control, ln="BendyCtrls", drive=[ctrl.control for ctrl in bend_ctrls])
        
        # Bendy Arch Scale
        self.upr_bend_ctrl.control.sy.drive(upr_mid_ribbon_drv_jnt.sy)
        self.lwr_bend_ctrl.control.sy.drive(lwr_mid_ribbon_drv_jnt.sy)
        
        # Group
        i_utils.parent(self.upr_bind_loft, self.lwr_bind_loft, self.bend_utl_grp)
        
        # Clear selection
        i_utils.select(cl=True)
        
    def create_tweak_rig(self):
        # Skin mid
        self.mid_skin_jnt = i_node.create("joint", n=self.base_name + "_Mid_Bend_Bnd", radius=self.joint_radius)
        # :note: Watson named joint would be self.base_name + "_Upr_" + self.mid_nice_name + "_Bnd", but
        # because tweaks are made to match joint names, we're changing the name of the joint to fit the control
        # then renaming after control built
        i_node.copy_pose(driver=self.mid_bend_ctrl.control, driven=self.mid_skin_jnt)
        self.bind_joints.append(self.mid_skin_jnt)

        # Make special tweak for mid
        twk_rot = [0, 0, 0] if self.is_leg else [0, 270, -90]
        self.tweak_ctrls += rig_controls.create_tweaks(joints=self.mid_skin_jnt, parent=self.tweak_ctrl_grp, name_remove="_Bnd", r=twk_rot, size=self.tweak_ctrl_size)
        self.mid_tweak_ctrl = self.tweak_ctrls[0]
        self.mid_skin_jnt.rename(self.base_name + "_Upr_" + self.mid_nice_name + "_Bnd")
        
        # Constrain
        i_constraint.constrain(self.mid_tweak_ctrl.last_tfm, self.mid_skin_jnt, mo=False, as_fn="parent")
        i_constraint.constrain(self.mid_bend_ctrl.last_tfm, self.mid_tweak_ctrl.top_tfm, mo=False, as_fn="parent")
        
        # Follicles and Joints
        u_val = 1.0 / 6.0
        self.upr_folls = []
        self.lwr_folls = []
        self.upr_tweak_joints = []
        self.lwr_tweak_joints = []
        for i in range(1, 6):
            # - Upper
            upr_foll = i_node.create_single_follicle(surface=self.upr_bind_loft, u_value=u_val * i, v_value=0.5,
                                                            name=self.start_name + "_Ribbon_%02d" % i)
            self.upr_folls.append(upr_foll)
            # - Lower
            lwr_foll = i_node.create_single_follicle(surface=self.lwr_bind_loft, u_value=u_val * i, v_value=0.5,
                                                            name=self.mid_name + "_Ribbon_%02d" % i)
            self.lwr_folls.append(lwr_foll)
            # - Joint
            i_utils.select(cl=True)
            upr_jnt = i_node.create("joint", n=self.start_name + "_Twist_%02d_Bnd" % i, radius=self.joint_radius)
            i_utils.select(cl=True)
            self.upr_tweak_joints.append(upr_jnt)
            lwr_jnt = i_node.create("joint", n=self.mid_name + "_Twist_%02d_Bnd" % i, radius=self.joint_radius)
            i_utils.select(cl=True)
            self.lwr_tweak_joints.append(lwr_jnt)
            
        self.bind_joints += self.upr_tweak_joints + self.lwr_tweak_joints
        
        # Create tweak for each follicle joint
        self.tweak_ctrls += rig_controls.create_tweaks(joints=self.upr_folls + self.lwr_folls, r=twk_rot,
                                                       name_remove=["_Ribbon", "_Flc"], parent=self.tweak_ctrl_grp, size=self.tweak_ctrl_size)
        
        # Drive visibilities
        self.tweak_vis_attr = rig_attributes.create_dis_attr(node=self.end_xtra_ctrl.control, ln="TweakCtrls",
                                                               drive=[ctrl.control for ctrl in self.tweak_ctrls])
        
        # Drive the tweak controls
        for i, ctrl in enumerate(self.tweak_ctrls[1:]):
            foll = self.upr_folls[i] if i < len(self.upr_folls) else self.lwr_folls[i - len(self.upr_folls)]
            jnt = self.upr_tweak_joints[i] if i < len(self.upr_tweak_joints) else self.lwr_tweak_joints[i - len(self.upr_tweak_joints)]
            i_constraint.constrain(foll, ctrl.top_tfm, mo=True, as_fn="parent")
            i_constraint.constrain(ctrl.last_tfm, jnt, mo=False, as_fn="parent")
        
        # :note: (from Watson) May need to add some more shoulder/hip joints to help with rotation twist and volume preservation?
        
        # Parent
        i_utils.parent(self.upr_folls + self.lwr_folls, self.bend_utl_grp)
        i_utils.parent([self.mid_skin_jnt] + self.upr_tweak_joints + self.lwr_tweak_joints, self.mid_bnd_grp)
    
    def create_volume(self):
        # Add Attrs
        self.vol_sep_attr = i_attr.create(node=self.end_xtra_ctrl.control, ln="Volume", at="enum",
                                            en="Control:", k=False, cb=True, l=True)
        self.vol_onoff_attr = i_attr.create(node=self.end_xtra_ctrl.control, dv=1, min=0, max=1, k=True,
                                              ln="VolumeOnOff")
        self.upr_vol_add_attr = i_attr.create(node=self.end_xtra_ctrl.control, dv=0, min=-5, max=5, k=True,
                                                ln="Upr" + self.limb_type + "VolumeAdd", )
        self.lwr_vol_add_attr = i_attr.create(node=self.end_xtra_ctrl.control, dv=0, min=-5, max=5, k=True,
                                                ln="Lwr" + self.limb_type + "VolumeAdd",)
        
        # Duplicate Curves
        # - Upper Stretch Curve
        upr_str_crv = i_node.duplicate(self.upr_bind_loft.relatives(0, s=True).attr("v[0.5]"), ch=1, rn=0, local=0, name=self.upr_bind_loft + "_Stretch_Crv", as_curve=True)
        upr_str_crv[1].rename(self.start_name + "_CurveFromSurface")
        # - Lower Stretch Curve
        lwr_str_crv = i_node.duplicate(self.lwr_bind_loft.relatives(0, s=True).attr("v[0.5]"), ch=1, rn=0, local=0, name=self.lwr_bind_loft + "_Stretch_Crv", as_curve=True)
        lwr_str_crv[1].rename(self.mid_name + "_CurveFromSurface")
        # - Upper Rest Curve
        upr_rest_crv = i_node.duplicate(upr_str_crv[0], n=self.upr_bind_loft.name.replace("_Crv", "_Rest_Crv"), as_curve=True)[0]
        # - Lower Rest Curve
        lwr_rest_crv = i_node.duplicate(lwr_str_crv[0], n=self.lwr_bind_loft.name.replace("_Crv", "_Rest_Crv"), as_curve=True)[0]
        # - Parent
        i_utils.parent(upr_rest_crv, lwr_rest_crv, self.end_scale_grp)
        self.volume_crv_grp = self._create_subgroup(name=self.end_name + "_Volume_Crv", add_base_name=False,
                                                          children=[upr_str_crv[0], lwr_str_crv[0]], parent=self.end_utl_grp)
        
        # Curve Infos
        # - Create
        upr_str_ci = i_node.create("curveInfo", n=self.upr_bind_loft + "_Stretch_Ci")
        lwr_str_ci = i_node.create("curveInfo", n=self.lwr_bind_loft + "_Stretch_Ci")
        upr_rest_ci = i_node.create("curveInfo", n=self.upr_bind_loft + "_Rest_Ci")
        lwr_rest_ci = i_node.create("curveInfo", n=self.lwr_bind_loft + "_Rest_Ci")
        # - Connect Input Curve
        upr_str_crv[0].worldSpace.drive(upr_str_ci.inputCurve)
        lwr_str_crv[0].worldSpace.drive(lwr_str_ci.inputCurve)
        upr_rest_crv.worldSpace.drive(upr_rest_ci.inputCurve)
        lwr_rest_crv.worldSpace.drive(lwr_rest_ci.inputCurve)
        # - Volume Calc
        self.vol_md = i_node.create("multiplyDivide", n=self.end_name + "_VolCalc_Md")
        self.vol_md.operation.set(2)
        upr_rest_ci.arcLength.drive(self.vol_md.input1X)
        upr_str_ci.arcLength.drive(self.vol_md.input2X)
        lwr_rest_ci.arcLength.drive(self.vol_md.input1Z)
        lwr_str_ci.arcLength.drive(self.vol_md.input2Z)
        # - Volume OnOff
        vol_onoff_bc = i_node.create("blendColors", n=self.end_name + "_VolOnOff_Bc")
        self.vol_onoff_attr.drive(vol_onoff_bc.blender)
        vol_onoff_bc.color2.set([1, 1, 1])
        self.vol_md.output.drive(vol_onoff_bc.color1)
        
        # Add in an offset and multiply that by the scale of each control before it goes into its joint
        upr_vol_adl = i_node.create("addDoubleLinear", n=self.start_name + "_VolAdd_Adl")
        lwr_vol_adl = i_node.create("addDoubleLinear", n=self.mid_name + "_VolAdd_Adl")
        vol_onoff_bc.outputR.drive(upr_vol_adl.input1)
        vol_onoff_bc.outputB.drive(lwr_vol_adl.input1)
        self.upr_vol_add_attr.drive(upr_vol_adl.input2)
        self.lwr_vol_add_attr.drive(lwr_vol_adl.input2)
        # - Tweak Ctrls split
        upr_tweak_ctrls = self.tweak_ctrls[1:len(self.upr_folls) + 1]  # First tweak control is the mid
        lwr_tweak_ctrls = self.tweak_ctrls[len(self.upr_folls) + 1:]
        # - Upper
        for i, ctrl in enumerate(upr_tweak_ctrls):
            # - Vars
            tweak_control = ctrl.control
            tweak_top = ctrl.top_tfm
            tweak_jnt = self.upr_tweak_joints[i]
            # - Create Node
            twk_vol_md = i_node.create("multiplyDivide", n=tweak_control.name.replace("_Ctrl", "_TweakVol_Md"))
            twk_vol_md.input1Y.set(1)
            twk_vol_md.input2Y.set(1)
            # - Connect
            upr_vol_adl.output.drive(twk_vol_md.input1X)
            upr_vol_adl.output.drive(twk_vol_md.input1Z)
            tweak_control.sx.drive(twk_vol_md.input2X)
            tweak_control.sz.drive(twk_vol_md.input2Z)
            twk_vol_md.output.drive(tweak_jnt.s)
            upr_vol_adl.output.drive(tweak_top.sx)
            upr_vol_adl.output.drive(tweak_top.sz)
        # - Lower
        for i, ctrl in enumerate(lwr_tweak_ctrls):
            # - Vars
            tweak_control = ctrl.control
            tweak_top = ctrl.top_tfm
            tweak_jnt = self.lwr_tweak_joints[i]
            # - Create Node
            twk_vol_md = i_node.create("multiplyDivide", n=tweak_control.name.replace("_Ctrl", "_TweakVol_Md"))
            twk_vol_md.input1Y.set(1)
            # - Connect
            lwr_vol_adl.output.drive(twk_vol_md.input1X)
            lwr_vol_adl.output.drive(twk_vol_md.input1Z)
            tweak_control.s.drive(twk_vol_md.input2)
            twk_vol_md.output.drive(tweak_jnt.s)
            lwr_vol_adl.output.drive(tweak_top.sx)
            lwr_vol_adl.output.drive(tweak_top.sz)
        
        # Handle the blend of the volume of upper and lower and push it to the mid
        # - Volume
        mid_vol_blc = i_node.create("blendColors", n=self.mid_tweak_ctrl.control.replace("_Ctrl", "_Vol_Blc"))
        upr_vol_adl.output.drive(mid_vol_blc.color1R)
        lwr_vol_adl.output.drive(mid_vol_blc.color2R)
        mid_vol_blc.outputR.drive(self.mid_tweak_ctrl.top_tfm.sx)
        mid_vol_blc.outputR.drive(self.mid_tweak_ctrl.top_tfm.sz)
        # - Volume Offset
        mid_vol_offset_md = i_node.create("multiplyDivide", n=self.mid_tweak_ctrl.control.replace("_Ctrl", "_Vol_Md"))
        self.mid_tweak_ctrl.control.sx.drive(mid_vol_offset_md.input1X)
        self.mid_tweak_ctrl.control.sy.drive(mid_vol_offset_md.input1Y)
        self.mid_tweak_ctrl.control.sz.drive(mid_vol_offset_md.input1Z)
        mid_vol_blc.outputR.drive(mid_vol_offset_md.input2X)
        mid_vol_blc.outputR.drive(mid_vol_offset_md.input2Z)
        mid_vol_offset_md.outputX.drive(self.mid_skin_jnt.sx)
        mid_vol_offset_md.outputY.drive(self.mid_skin_jnt.sy)
        mid_vol_offset_md.outputZ.drive(self.mid_skin_jnt.sz)
        
        # Adjust the rest length for the limb to the length of the limb joints combined
        self.end_ref_loc.set_parent(self.base_ref_loc)
        # # :note: Original code does this change to the loc's t, but that makes things freak out??? ToonBuilder L 1579
        # limb_len = self.vol_md.input1X.get() + self.vol_md.input1Z.get() * 0.9999
        # self.end_ref_loc.ty.set(limb_len)

    def create_groups(self):
        self.pole_help_grp = self._create_subgroup(name="PoleHelp", parent=self.ctrl_cns_grp)
        self.pole_help_grp.inheritsTransform.set(0)
        self.pole_help_grp.overrideEnabled.set(1)
        self.pole_help_grp.overrideDisplayType.set(2)
        
        self.helper_utl_grp = self._create_subgroup(name="Helper_Utl", parent=self.utility_grp)
        
        self.blend_switch_grp = self._create_subgroup(name="BlendSwitch", parent=self.ctrl_cns_grp)
        cmds.reorder(self.blend_switch_grp.name, f=True)

        self.end_utl_grp = self._create_subgroup(name=self.end_name + "_Utl", add_base_name=False, parent=self.pack_utility_grp)

        self.bend_utl_grp = self._create_subgroup(name=self.end_name + "_Bend_Utl", add_base_name=False, parent=self.end_utl_grp)

        self.pack_ctrl_grp = self._create_subgroup(name="Ctrl")

        self.mid_bnd_grp = self._create_subgroup(name=self.end_name + "_Bnd", add_base_name=False, parent=self.pack_bind_jnt_grp)
        
        self.mid_bend_ctrl_grp = self._create_subgroup(name=self.end_name + "_Bend_Ctrl", add_base_name=False, parent=self.pack_ctrl_grp)
        
        self.tweak_ctrl_grp = self._create_subgroup(name=self.end_name + "_Tweak_Ctrl", add_base_name=False, parent=self.pack_ctrl_grp)
        
        self.ikfk_data_grp = self._create_subgroup(name="IKFK_Data", parent=self.pack_utility_grp)
        cmds.reorder(self.ikfk_data_grp.name, f=True)

    def _cleanup_bit(self):
        # Re-order Xtra Control attributes
        extra_attrs = [self.ikfk_blend_attr, self.root_auto_twist_attr, self.bendy_vis_attr, self.tweak_vis_attr, 
                       self.base_ik_vis_attr, self.str_onoff_attr, self.pole_lock_attr, self.lwr_lenadd_attr, self.upr_lenadd_attr, 
                       self.vol_sep_attr, self.vol_onoff_attr, self.upr_vol_add_attr, self.lwr_vol_add_attr]
        i_attr.reorder(node=self.end_xtra_ctrl.control, new_order=[nd_attr.split(".")[1] for nd_attr in extra_attrs])

        # Lock and Hide
        i_attr.lock_and_hide(node=self.ik_base_ctrl.control, attrs=["s", "r", "ro"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ik_end_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ik_pv_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ik_offset_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ik_offset_ctrl.gimbal, attrs=["s"], lock=True, hide=True)
        cns_grps = [ctrl.cns_grp for ctrl in self.fk_ctrls + self.tweak_ctrls + 
                    [self.ik_base_ctrl, self.ik_pv_ctrl, self.ik_end_ctrl, self.upr_bend_ctrl, self.lwr_bend_ctrl, 
                     self.mid_bend_ctrl, self.mid_tweak_ctrl]]
        for cns in cns_grps:
            i_attr.lock_and_hide(node=cns, attrs=["s", "v"], lock=True, hide=True)
        for control in self.created_controls:
            i_attr.lock_and_hide(node=control, attrs=["v"], lock=True, hide=True)
        for fk_ctrl in self.fk_ctrls:
            i_attr.lock_and_hide(node=fk_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.end_xtra_ctrl.control, attrs=["t", "r", "s"], lock=True, hide=True)
        
        # # Connect Extra
        # extra_controls = [control for control in self.created_controls if control != self.end_xtra_ctrl.control]
        # self.connect_extra(xtra=self.end_xtra_ctrl.control, objects=extra_controls, master=True)
        
        # Grouping
        self.offset_grp = self._create_subgroup(name="Offset", parent=self.ribbon_drv_jnt_grp, 
                                                children=[self.fk_joints[0], self.ik_joints[0], self.base_joints[0]])

    def connect_elements(self):
        self.connect_ikfk_bendy()
        
        # # Need to do this at the end or else the target loc goes to the wrong spot.
        # i_constraint.constrain(self.pole_loft_foll, self.pv_target_loc, mo=True, as_fn="parent")

    def _create_bit(self):
        # Vars
        # - Capitalize given mid nice name
        self.mid_nice_name = self.mid_nice_name.capitalize()
        # - Make 'state' Better string for use in naming
        self.limb_type = self.limb_type.capitalize()
        # - Get joint base names
        self.start_name = self.base_name + "_" + self.joint_names[0].capitalize()  # Upper
        self.mid_name = self.base_name + "_" + self.joint_names[1].capitalize()  # Lower
        self.end_name = self.base_name + "_" + self.joint_names[2].capitalize()  # Wrist / Ankle
        # :note: The 4th joint is "end", but never really need that name, so don't need to make it a var.

        # Create
        self.create_groups()
        self.create_controls()
        self.setup_ikfk()
        self.create_fk()
        self.create_ik()
        self.complete_ikfk()
        self.create_stretch()
        self.create_bendy()
        self.create_tweak_rig()
        self.create_volume()
        
        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_ctrl_grp = pack_obj.pack_ctrl_grp
        pack_joint_offset_grp = pack_obj.offset_grp
        pack_pv_control = pack_obj.ik_pv_ctrl.control
        pack_fk_controls = [pack_obj.fk_ctrls[0].last_tfm, pack_obj.fk_ctrls[1].last_tfm, pack_obj.fk_ctrls[-1].last_tfm]
        pack_ik_end_control = pack_obj.ik_offset_ctrl.control

        # Stitch
        if parent_build_type in ["Clavicle", "Hip"]:
            parent_control = parent_obj.ctrl.control
            self.stitch_cmds.append({"parent": {"child": pack_ctrl_grp, "parent": parent_control}})
            self.stitch_cmds.append({"constrain": {"args": [parent_control, pack_joint_offset_grp], 
                                                   "kwargs": {"mo": True, "as_fn": "parent"}}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "point",
                                                "options": parent_control}})
            for fk_control in pack_fk_controls:
                self.stitch_cmds.append({"follow": {"driving": fk_control, "cns_type": "orient",
                                                    "options": parent_control}})
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": parent_control}})

        elif parent_build_type == "Cog":
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            cog_drivers = [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]
            self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "point",
                                                "options": cog_drivers}})
            for fk_control in pack_fk_controls:
                self.stitch_cmds.append({"follow": {"driving": fk_control, "cns_type": "orient",
                                                    "options": cog_drivers}})
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": cog_drivers}})

        elif parent_build_type.startswith("Spine"):
            parent_chest_control = parent_obj.end_ctrl.control
            parent_hip_control = parent_obj.start_ctrl.control
            spine_drivers = [parent_chest_control, parent_hip_control]
            self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "point",
                                                "options": spine_drivers}})
            for fk_control in pack_fk_controls:
                self.stitch_cmds.append({"follow": {"driving": fk_control, "cns_type": "orient",
                                                    "options": spine_drivers}})
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": spine_drivers}})

        elif parent_build_type.startswith("Head"):
            parent_control = parent_obj.ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": parent_control}})

