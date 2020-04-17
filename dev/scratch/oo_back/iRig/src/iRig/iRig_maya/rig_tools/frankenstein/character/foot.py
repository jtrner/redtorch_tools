import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.geometry as rig_geometry

from rig_tools.frankenstein.character.foot_master import Build_Foot_Master


class Build_Foot(Build_Foot_Master):
    def __init__(self):
        Build_Foot_Master.__init__(self)

        # # Set the pack info
        # self.base_joint_positions = [[0.5, 0.7, -0.31], #[17, 3, -5], 
        #                              [0.56, 0.29, 0.32], #[17, 1.5, 3.94], 
        #                              [0.59, 0.25, 0.88], #[17, 0, 9.53],
        #                              ]

    def _stitch_pack(self):
        Build_Foot_Master._stitch_pack(self)

        self.base_joints[0].joy.set(0)
        self.base_joints[0].joz.set(0)

    def _create_pack(self):
        Build_Foot_Master._create_pack(self)
        
        # Zero out ball joint orients
        if self.do_pack_positions:
            jo_zeroed = ["y", "z"]  # :TODO: May change if orientation changes
            for ax in jo_zeroed:
                self.base_joints[1].attr("jo" + ax).set(0)
    
    @classmethod  # Class method so the Limb can use it and foot code only exists once
    def create_foot_control(self, base_name=None, color=None, pack_size=1.0, foot_joint=None, parent=None, 
                            make_wedge=True, follow_name=None, rotate_order=None):
        # Create Control
        foot_size = pack_size * 1.5
        if follow_name:
            follow_name += "_Ik"
        end_ctrl = i_node.create("control", control_type='3D Cube', color=color, degree=1, name=base_name + "_Ik", 
                                 follow_name=follow_name, parent=parent, size=foot_size, position_match=foot_joint, 
                                 additional_groups=["Xtra"], match_rotation=False if make_wedge else True,
                                 rotate_order=rotate_order)

        # Make shape wedge-y
        if make_wedge:
            end_gimbal = end_ctrl.gimbal  # Gimbal
            end_control = end_ctrl.control  # Main Control

            controls = [end_control]
            if end_gimbal:
                controls.append(end_gimbal)
            lower_size = foot_size * -0.5
            further_size = foot_size * 2.0
            wider_size = further_size * 0.2
            for ctrl in controls:
                # Vars
                ctrl_shape = ctrl.relatives(0, s=True)
                wedge_cvs = [ctrl_shape.attr("cv[2:3]"), ctrl_shape.attr("cv[6:11]")]
                top_wedge_cvs = [ctrl_shape.attr("cv[6]"), ctrl_shape.attr("cv[8:9]"), ctrl_shape.attr("cv[11]")]
                btm_wedge_cvs = [ctrl_shape.attr("cv[0:4]"), ctrl_shape.attr("cv[7]"), ctrl_shape.attr("cv[10]"), ctrl_shape.attr("cv[13]")]
                # wedge_cvs = [ctrl_shape.cv[2:3], ctrl_shape.cv[6:11]]
                # top_wedge_cvs = [ctrl_shape.cv[6], ctrl_shape.cv[8:9], ctrl_shape.cv[11]]
                # btm_wedge_cvs = [ctrl_shape.cv[0:4], ctrl_shape.cv[7], ctrl_shape.cv[10], ctrl_shape.cv[13]]

                # - Make the front cvs reach further
                i_utils.xform(0, 0, further_size, wedge_cvs, r=True, ls=True, wd=True, as_fn="move")
                # - Make the top front cvs lower
                if ctrl == end_gimbal:
                    lower_size += 0.5
                i_utils.xform(0, lower_size, 0, top_wedge_cvs, r=True, ls=True, wd=True, as_fn="move")
                # - Make the front cvs wider
                i_utils.xform(wedge_cvs, 1, wider_size, 1, ls=True, r=True, as_fn="scale")
                # - Snap bottom to grid
                i_utils.xform(0, 0, 0, btm_wedge_cvs, moveY=True, ws=True, as_fn="move")

                # Clear selection
                i_utils.select(cl=True)

        # Return
        return end_ctrl
    
    
    def _ik_add_attrs(self):
        # Get control
        ik_end_ctrl = self.foot_ctrl.control
        
        # Divider
        i_attr.create_divider_attr(node=ik_end_ctrl, ln="Foot")
        
        # Roll
        roll_attr = i_attr.create(ik_end_ctrl, "BallRoll", k=True, at="double", dv=0.0)
        
        # RollBreak
        roll_break_attr = i_attr.create(ik_end_ctrl, "RollBreak", k=True, at="double", dv=30.0)

        # BallRoll
        ball_roll_attr = i_attr.create(ik_end_ctrl, "BallRollHelper", k=False, at="double", dv=0.0)
        ball_roll_cnd = i_node.create("condition", name=self.base_name + "_BallRoll_Cnd")
        ball_roll_cnd.operation.set(2)  # Greater Than
        ball_roll_cnd.colorIfFalseR.set(0)
        roll_attr.drive(ball_roll_cnd.firstTerm)
        roll_attr.drive(ball_roll_cnd.colorIfTrueR)
        ball_roll_cnd2 = i_node.create("condition", name=self.base_name + "_BallRollBreak_Cnd")
        ball_roll_cnd2.operation.set(4)  # Less Than
        roll_attr.drive(ball_roll_cnd2.firstTerm)
        roll_break_attr.drive(ball_roll_cnd2.secondTerm)
        roll_break_attr.drive(ball_roll_cnd2.colorIfFalseR)
        ball_roll_cnd.outColorR.drive(ball_roll_cnd2.colorIfTrueR)
        ball_roll_md = i_node.create("multiplyDivide", name=self.base_name + "_BallRoll_Md")
        ball_roll_md.input2.set([-1, -1, 1])
        ball_roll_cnd2.outColorR.drive(ball_roll_md.input1X)
        ball_roll_attr.drive(ball_roll_md.input1Y)
        ball_roll_adl = i_node.create("addDoubleLinear", name=self.base_name + "_BallRoll_Adl")
        ball_roll_md.outputX.drive(ball_roll_adl.input1)
        ball_roll_md.outputY.drive(ball_roll_adl.input2)
        rot = {"xyz": "rz", "yzx": "rx"}.get(self.orient_joints)
        # ball_roll_attr.drive(self.ball_driver_grp.attr(rot))
        ball_roll_adl.output.drive(self.ball_driver_grp.attr(rot))

        # HeelRoll
        heel_roll_attr = i_attr.create(ik_end_ctrl, "HeelRoll", k=True, at="double", dv=0.0)
        heel_roll_cnd = i_node.create("condition", name=self.base_name + "_HeelRoll_Cnd")
        heel_roll_cnd.operation.set(4)  # Less Than
        heel_roll_cnd.colorIfFalseR.set(0)
        roll_attr.drive(heel_roll_cnd.firstTerm)
        roll_attr.drive(heel_roll_cnd.colorIfTrueR)
        heel_roll_adl = i_node.create("addDoubleLinear", name=self.base_name + "_HeelRoll_Adl")
        heel_roll_cnd.outColorR.drive(heel_roll_adl.input1)
        # heel_roll_attr.drive(heel_roll_adl.input2)
        rot = {"xyz": "rx", "yzx": "rx"}.get(self.orient_joints)
        heel_roll_md = i_node.create("multiplyDivide", name=self.base_name + "_HeelRoll_Md")
        # heel_roll_adl.output.drive(heel_roll_md.input1X)
        # heel_roll_md.input2X.set(-1)
        # heel_roll_md.outputX.drive(self.heel_roll_grp.attr(rot))
        heel_roll_attr.drive(heel_roll_md.input1X)
        heel_roll_md.input2X.set(-1)
        heel_roll_md.outputX.drive(heel_roll_adl.input2)
        heel_roll_adl.output.drive(self.heel_roll_grp.attr(rot))

        # HeelPivot
        heel_pivot_attr = i_attr.create(ik_end_ctrl, "HeelPivot", k=True, at="double", dv=0.0)
        rot = {"xyz": "ry", "yzx": "ry"}.get(self.orient_joints)
        if self.is_mirror:
            heel_pivot_neg_md = i_node.create("multiplyDivide", n=self.base_name + "_HeelPivot_Neg_Md")
            heel_pivot_attr.drive(heel_pivot_neg_md.input1X)
            heel_pivot_neg_md.input2X.set(-1)
            heel_pivot_attr = heel_pivot_neg_md.outputX
        heel_pivot_attr.drive(self.heel_roll_grp.attr(rot))

        # ToeRoll
        toe_roll_attr = i_attr.create(ik_end_ctrl, "ToeRoll", k=True, at="double", dv=0.0)
        toe_roll_md = i_node.create("multiplyDivide", name=self.base_name + "_ToeRoll_Md")
        roll_break_attr.drive(toe_roll_md.input1X)
        toe_roll_md.input2X.set(-1)
        toe_roll_adl = i_node.create("addDoubleLinear", name=self.base_name + "_ToeRollBreak_Adl")
        roll_attr.drive(toe_roll_adl.input1)
        toe_roll_md.outputX.drive(toe_roll_adl.input2)
        toe_roll_cnd = i_node.create("condition", name=self.base_name + "_ToeRoll_Cnd")
        toe_roll_cnd.operation.set(2)  # Greater Than
        toe_roll_cnd.colorIfFalseR.set(0)
        roll_attr.drive(toe_roll_cnd.firstTerm)
        roll_break_attr.drive(toe_roll_cnd.secondTerm)
        toe_roll_adl.output.drive(toe_roll_cnd.colorIfTrueR)
        toe_roll_adl2 = i_node.create("addDoubleLinear", name=self.base_name + "_ToeRoll_Adl")
        toe_roll_attr.drive(toe_roll_adl2.input1)
        toe_roll_cnd.outColorR.drive(toe_roll_adl2.input2)
        rot = {"xyz": "rx", "yzx": "rx"}.get(self.orient_joints)
        # toe_roll_attr.drive(self.toe_driver_grp.attr(rot))
        # toe_roll_attr.drive(self.ball_toe_pivot_cns_grp.attr(rot))
        toe_roll_adl2.output.drive(self.ball_toe_pivot_cns_grp.attr(rot))
        toe_roll_adl2.output.drive(self.toe_driver_grp.attr(rot))

        # ToePivot
        toe_pivot_attr = i_attr.create(ik_end_ctrl, "ToePivot", k=True, at="double", dv=0.0)
        rot = {"xyz": "ry", "yzx": "ry"}.get(self.orient_joints)
        if self.is_mirror:
            toe_pivot_neg_md = i_node.create("multiplyDivide", n=self.base_name + "_ToePivot_Neg_Md")
            toe_pivot_attr.drive(toe_pivot_neg_md.input1X)
            toe_pivot_neg_md.input2X.set(-1)
            toe_pivot_attr = toe_pivot_neg_md.outputX
        toe_pivot_attr.drive(self.toe_driver_grp.attr(rot))
        toe_pivot_attr.drive(self.ball_toe_pivot_cns_grp.attr(rot))

        # ToeUpDown
        toe_updown_attr = i_attr.create(ik_end_ctrl, "ToeUpDown", k=True, at="double", dv=0.0)
        rot = {"xyz": "rz", "yzx": "rx"}.get(self.orient_joints)
        toe_updown_attr.drive(self.toe_ex_pivot.attr(rot))

        # ToeSide
        toe_side_attr = i_attr.create(ik_end_ctrl, "ToeSide", k=True, at="double", dv=0.0)
        rot = {"xyz": "ry", "yzx": "rz"}.get(self.orient_joints)
        toe_side_attr.drive(self.toe_ex_pivot.attr(rot))

        # ToeTwist
        toe_twist_attr = i_attr.create(ik_end_ctrl, "ToeTwist", k=True, at="double", dv=0.0)
        rot = {"xyz": "rx", "yzx": "ry"}.get(self.orient_joints)
        toe_twist_attr.drive(self.toe_ex_pivot.attr(rot))
        
    
    def _ik_foot_system(self):
        # self._create_subgroup(name="", parent="", xform_driver="", xform_attrs="")
        self.ik_ctrls = []
        control_size = self.ctrl_size * 0.5
        axis = {"xyz" : "y", "yzx" : "y"}.get(self.orient_joints)
        rot = "r" + axis
        tr = "t" + axis
        
        # System Offset Group
        self.sys_offset_grp = self._create_subgroup(name="System_Offset", parent=self.foot_ctrl.last_tfm)
        self.sys_offset_grp.attr(rot).set(self.foot_ctrl.xtra_grp.attr(rot).get() * -1)
        i_attr.create_vis_attr(node=self.foot_ctrl.control, drive=self.sys_offset_grp, ln="Extras", dv=0)
        
        # Heel Ik Control
        self.heel_ik_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color,
                                          name=self.base_name + "_Heel_Ik", position_match=self.heel_piv_loc,  # self.base_joints[0]
                                          with_gimbal=False, size=control_size, parent=self.sys_offset_grp, # with_cns_grp=False, 
                                          promote_rotate_order=False,)
        self.ik_ctrls.append(self.heel_ik_ctrl)
        
        # - Position Offset
        self.heel_ik_ctrl.offset_grp.attr(tr).set(self.foot_ctrl.offset_grp.attr(tr).get() * -1)
        # - Heel Roll
        self.heel_roll_grp = self._create_subgroup(name="Heel_Roll", parent=self.heel_ik_ctrl.last_tfm)
        # - Heel Pivot
        self.heel_pivot_grp = self._create_subgroup(name="Heel_Pivot", parent=self.heel_roll_grp)
        
        # Toe/Ball Driver Hierarchy
        # - Toe Driver Offset
        self.toe_driver_offset_grp = self._create_subgroup(name="Toe_Driver_Offset", parent=self.heel_roll_grp, 
                                                            xform_driver=self.base_joints[2], xform_attrs=["t"])
        # - Toe Driver Cns
        self.toe_driver_cns_grp = self._create_subgroup(name="Toe_Driver_Cns", parent=self.toe_driver_offset_grp)
        # - Toe Driver
        self.toe_driver_grp = self._create_subgroup(name="Toe_Driver", parent=self.toe_driver_cns_grp)
        # - Ball Driver Offset
        self.ball_driver_offset_grp = self._create_subgroup(name="Ball_Driver_Offset", parent=self.toe_driver_grp, 
                                                             xform_driver=self.base_joints[1], xform_attrs=["r"])
        # - Ball Driver Cns
        self.ball_driver_cns_grp = self._create_subgroup(name="Ball_Driver_Cns", parent=self.ball_driver_offset_grp)
        # - Ball Driver Xtra
        self.ball_driver_xtra_grp = self._create_subgroup(name="Ball_Driver_Xtra", parent=self.ball_driver_cns_grp)
        # - Ball Driver
        self.ball_driver_grp = self._create_subgroup(name="Ball_Driver", parent=self.ball_driver_xtra_grp)
        
        # Toes Aim Up
        self.toes_up_grp = self._create_subgroup(name="Toes_Aim_Up", parent=self.sys_offset_grp, 
                                                  xform_driver=self.base_joints[1], xform_attrs=["t"])
        self.toes_up_grp.attr(tr).set(self.base_joints[2].attr(tr).get() + (self.pack_size * 5))
        
        # Toe Tip Ik Control
        self.toe_tip_ik_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color,
                                             name=self.base_name + "_ToeTip_Ik", position_match=self.toe_piv_loc,  # self.base_joints[2]
                                             with_gimbal=False, size=control_size, parent=self.heel_pivot_grp, # with_cns_grp=False,
                                             promote_rotate_order=False,)
        self.ik_ctrls.append(self.toe_tip_ik_ctrl)
        # - Toe Pivot
        self.toe_pivot_grp = self._create_subgroup(name="Toe_Pivot", parent=self.toe_tip_ik_ctrl.last_tfm, 
                                                   xform_driver=self.toe_piv_loc, xform_attrs=["t"])
        
        # Toe Ik Control
        self.toe_ik_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color,
                                         name=self.base_name + "_Toe_Ik", position_match=self.base_joints[1],
                                         additional_groups=["Xtra"], with_gimbal=False, size=control_size, 
                                         parent=self.toe_pivot_grp, match_rotation=True, promote_rotate_order=False,)
        self.ik_ctrls.append(self.toe_ik_ctrl)
        # - Toe Ex Pivot Offset
        self.toe_ex_pivot_offset = self._create_subgroup(name="Toe_Ex_Pivot_Offset", parent=self.toe_ik_ctrl.last_tfm)
        self.toe_ex_pivot = self._create_subgroup(name="Toe_Ex_Pivot", parent=self.toe_ex_pivot_offset)
        self.toe_ikh.set_parent(self.toe_ex_pivot)
        i_node.copy_pose(driver=self.base_joints[-1], driven=self.toe_ikh, attrs=["t", "r"])
        
        # Ball Ik Control
        # - Parent groups
        self.ball_pivot_offset_grp = self._create_subgroup(name="Ball_Pivot_Offset", parent=self.heel_pivot_grp, 
                                                            xform_driver=self.base_joints[1], xform_attrs=["t", "r"])
        self.ball_toe_pivot_offset_grp = self._create_subgroup(name="Ball_Toe_Pivot_Offset", parent=self.ball_pivot_offset_grp, 
                                                                xform_driver=self.base_joints[2], xform_attrs=["t"])
        self.ball_toe_pivot_cns_grp = self._create_subgroup(name="Ball_Toe_Pivot_Cns", parent=self.ball_toe_pivot_offset_grp)
        # - Control
        self.ball_ik_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color, 
                                          name=self.base_name + "_Ball_Ik", position_match=self.base_joints[1], 
                                          promote_rotate_order=False, additional_groups=["Xtra"], # with_cns_grp=False,
                                          size=control_size * 1.5, match_rotation=True, with_gimbal=False, 
                                          parent=self.ball_toe_pivot_cns_grp)
        self.ik_ctrls.append(self.ball_ik_ctrl)
        # - Child groups
        self.ball_pivot_grp = self._create_subgroup(name="Ball_Pivot", parent=self.ball_ik_ctrl.last_tfm)
        
        # Ankle Ik Control
        # - Control
        # :note: There will be weird behaviour when just building the foot. It works properly when with the leg though.
        self.ankle_ik_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color, 
                                           name=self.base_name + "_Ankle_Ik", position_match=self.base_joints[0],
                                           additional_groups=["Xtra"], size=control_size, promote_rotate_order=False, # with_cns_grp=False,
                                           with_gimbal=False, parent=self.ball_ik_ctrl.last_tfm, match_rotation=False)
        self.ik_ctrls.append(self.ankle_ik_ctrl)
        
        # Ankle Ik Setup
        self.ankle_ik_move_offset_grp = self._create_subgroup(name="Ankle_Ik_Move_Offset", parent=self.ball_pivot_grp, 
                                                              xform_driver=self.base_joints[0], xform_attrs=["t"])
        self.ankle_ik_move_xtra_grp = self._create_subgroup(name="Ankle_Ik_Move_Xtra", parent=self.ankle_ik_move_offset_grp)
        self.ankle_ik_move_grp = self._create_subgroup(name="Ankle_Ik_Move", parent=self.ankle_ik_move_xtra_grp)
        self.ankle_ik_hdl_offset_grp = self._create_subgroup(name="Ankle_Ik_Hdl_Offset", parent=self.ankle_ik_move_grp)
        # # :note: This will be where the leg's ikh is parented under when the packs are connected
        # i_node.copy_pose(driver=self.ankle_ik_hdl_offset_grp, driven=self.ankle_ik_ctrl.top_tfm, attrs=["r"])
        # self.ankle_ik_ctrl.top_tfm.attr(rot).set(90)  #  * self.side_mult
        
        # - Ball Ik
        self.ball_ik_hdl_offset_grp = self._create_subgroup(name="Ball_Ik_Hdl_Offset", parent=self.ball_pivot_grp)
        self.ball_ikh.set_parent(self.ball_ik_hdl_offset_grp)
    
    
    def _ik_stretch_setup(self, section="", parent=None, xform_driver=None):
        stretch_offset_grp = self._create_subgroup(name=section + "_Ik_Stretch_Loc_Offset", parent=parent,
                                                   xform_driver=xform_driver, xform_attrs=["r"], zero_out=True)
        
        stretch_loc = i_node.create("locator", n=self.base_name + "_" + section + "_Ik_Stretch_Loc")
        stretch_loc.set_parent(stretch_offset_grp)
        stretch_loc.zero_out()
        stretch_loc.vis(0)
        
        return [stretch_offset_grp, stretch_loc]
    
    def create_stretch(self):
        # Vars
        self.stretch_nodes = {}
        section_names = ["Ankle_Ball", "Ball_Toes"]
        
        # Prep Ik Stretch with locators
        self.stretch_toes = self._ik_stretch_setup(section="Toes", parent=self.toe_pivot_grp, xform_driver=self.base_joints[2])
        self.stretch_ball = self._ik_stretch_setup(section="Ball", parent=self.ball_pivot_grp, xform_driver=self.base_joints[1])
        self.stretch_ankle = self._ik_stretch_setup(section="Ankle", parent=self.ankle_ik_hdl_offset_grp, xform_driver=self.base_joints[0])
        ik_stretch_locs_connect = [[self.stretch_ankle[1], self.stretch_ball[1]], 
                                   [self.stretch_ball[1], self.stretch_toes[1]]]
        
        # Loop
        for i in range(len(section_names)):
            # Vars
            result_jnt = self.base_joints[i]
            fk_jnt = self.fk_joints[i]
            ik_jnt = self.ik_joints[i]
            created = {}
            base_name = self.base_name + "_" + section_names[i]
            primary_axis = self.orient_joints[0]
            
            # Control Attrs
            fk_ctrl_stretch_attr = i_attr.create(node=self.fk_ctrls[i].control, ln="Stretch", at="double", k=True, dv=1.0, min=0.01)

            # Control Stretch
            control_stretch_md = i_node.create("multiplyDivide", n=base_name + "_Control_Foot_Stretch_Md")
            created["control_stretch_md"] = control_stretch_md
            control_stretch_md.operation.set(2)  # Divide
            control_stretch_md.input1X.set(1)  # :TODO: Set this connect from leg
            control_stretch_md.input2X.set(1)  # :TODO: Set this connect from leg
            
            # Result Joint
            result_jnt_stretch_attr = i_attr.create(node=result_jnt, ln="Stretch", at="double", k=True, dv=1.0, min=0.01)
            result_created = rig_joints.create_simple_stretch(stretch_attr=result_jnt_stretch_attr, jnt=result_jnt, 
                                                              base_name=base_name, control_stretch_node=control_stretch_md, 
                                                              stretch_axis=primary_axis)
            created["result"] = result_created
            
            # IK
            ik_jnt_stretch_attr = i_attr.create(node=ik_jnt, ln="Stretch", at="double", k=True, dv=1.0, min=0.01)
            ik_from_loc, ik_to_loc = ik_stretch_locs_connect[i]
            # - Distance Node
            distance_node = i_node.create("distanceBetween", n=base_name + "_Dist")
            created["distance_node"] = distance_node
            ik_from_loc.worldMatrix[0].drive(distance_node.inMatrix1)
            ik_to_loc.worldMatrix[0].drive(distance_node.inMatrix2)
            # - Default Length Curve
            curve_default_md = i_node.create("multiplyDivide", n=base_name + "_Curve_Default_Length_Md")
            created["curve_default_md"] = curve_default_md
            curve_default_md.operation.set(1)  # Multiply
            curve_default_md.input1X.set(1)  # :TODO: Set this connect from leg
            curve_default_md.input1Y.set(1)  # :TODO: Set this connect from leg
            curve_default_md.input2X.set(distance_node.distance.get())
            curve_default_md.input2Y.set(distance_node.distance.get())
            if self.scale_attr:
                self.scale_attr.drive(curve_default_md.input1X)
                self.scale_attr.drive(curve_default_md.input1Y)
            # - Curve Ratio Md
            curve_ratio_md = i_node.create("multiplyDivide", n=base_name + "_Curve_Ratio_Md")
            created["curve_ratio_md"] = curve_ratio_md
            curve_ratio_md.operation.set(2)  # Divide
            curve_default_md.outputX.drive(curve_ratio_md.input2X)
            curve_default_md.outputY.drive(curve_ratio_md.input2Y)
            distance_node.distance.drive(curve_ratio_md.input1X)
            curve_ratio_md.outputX.drive(ik_jnt_stretch_attr)
            # - Regular Bits
            ik_created = rig_joints.create_simple_stretch(stretch_attr=ik_jnt_stretch_attr, jnt=ik_jnt, 
                                                          base_name=base_name + "_Ik", stretch_axis=primary_axis, 
                                                          control_stretch_node=control_stretch_md)
            created["ik"] = ik_created
            
            # FK
            fk_jnt_stretch_attr = i_attr.create(node=fk_jnt, ln="Stretch", at="double", k=True, dv=1.0, min=0.01)
            fk_created = rig_joints.create_simple_stretch(stretch_attr=fk_jnt_stretch_attr, jnt=fk_jnt, 
                                                          base_name=base_name + "_Fk", stretch_axis=primary_axis,
                                                          control_stretch_node=control_stretch_md)
            created["fk"] = fk_created
            fk_ctrl_stretch_attr.drive(fk_jnt_stretch_attr)
            
            # Stretch
            stretch_blend = i_node.create("blendTwoAttr", n=base_name + "_Stretch_Blend")
            created["stretch_blend"] = stretch_blend
            fk_jnt_stretch_attr.drive(stretch_blend.input[0])
            ik_jnt_stretch_attr.drive(stretch_blend.input[1])
            stretch_blend.output.drive(result_jnt_stretch_attr)
            self.ikfk_switch_control.FKIKSwitch.drive(stretch_blend.attributesBlender)
            
            # Add to dict
            self.stretch_nodes[section_names[i]] = created

    def _ik_setup(self):
        # IK Joints and Group
        self.ik_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Ik", end_index=len(self.base_joints))
        self.ik_setup_grp = self._create_subgroup(name="Ik_Setup", children=self.ik_joints[0])

        # Ball IK
        self.ball_ikh, self.ball_eff = rig_joints.create_ikh_eff(start=self.ik_joints[0], end=self.ik_joints[1],
                                                                 ikh_parent=self.ik_setup_grp, solver="ikSCsolver")  # Gets parented properly later
        self.ball_ikh.poleVector.set([0, 0, 0])
        
        # Toe IK
        self.toe_ikh, self.toe_eff = rig_joints.create_ikh_eff(start=self.ik_joints[1], end=self.ik_joints[2],
                                                               ikh_parent=self.ik_setup_grp, solver="ikSCsolver")  # Gets parented properly later
        
        # Add items to be driven by utility vis attr
        self.utility_vis_objs += [self.ball_ikh, self.toe_ikh]
    
    def _ik_connect(self):
        # Constraints
        i_constraint.constrain(self.toe_tip_ik_ctrl.last_tfm, self.toes_up_grp, mo=True, as_fn="parent")
        i_constraint.constrain(self.base_joints[1], self.ball_driver_grp, mo=True, as_fn="point")
        i_constraint.constrain(self.toe_driver_grp, self.toe_pivot_grp, mo=True, as_fn="orient")
        i_constraint.constrain(self.toe_tip_ik_ctrl.last_tfm, self.ball_pivot_offset_grp, mo=True, as_fn="parent")
        i_constraint.constrain(self.ball_driver_grp, self.ball_pivot_grp, mo=True, as_fn="orient")
        
        # Direct Connections
        self.toe_tip_ik_ctrl.offset_grp.t.drive(self.toe_driver_offset_grp.t)
        self.toe_tip_ik_ctrl.control.r.drive(self.toe_driver_cns_grp.r)
        self.ball_ik_ctrl.xtra_grp.r.drive(self.ball_driver_cns_grp.r)
        self.ball_ik_ctrl.control.r.drive(self.ball_driver_xtra_grp.r)
        self.ball_ik_ctrl.xtra_grp.t.drive(self.toe_ik_ctrl.cns_grp.t)
        self.ball_ik_ctrl.control.t.drive(self.toe_ik_ctrl.xtra_grp.t)
        self.ankle_ik_ctrl.xtra_grp.t.drive(self.ankle_ik_move_xtra_grp.t)
        self.ankle_ik_ctrl.control.t.drive(self.ankle_ik_move_grp.t)
        
        # # Extra math connections
        # # :note: Math for this will change if orientation is not yzx
        # ankle_ik_md = i_node.create("multiplyDivide", name=self.base_name + "_Ankle_Ik_Md")
        # ankle_ik_md.operation.set(2)  # Divide
        # self.ankle_ik_ctrl.control.tx.drive(ankle_ik_md.input1X)
        # ankle_ik_md.input2X.set(-1)
        # ankle_ik_md.outputX.drive(self.ankle_ik_move_grp.ty)  # :note: yes, tx drives ty
        # self.ankle_ik_ctrl.control.ty.drive(self.ankle_ik_move_grp.tx)  # :note: yes, ty drives tx
        # self.ankle_ik_ctrl.control.tz.drive(self.ankle_ik_move_grp.tz)
    
    
    def create_ik(self):
        # Create Group
        self.ik_control_grp = self._create_subgroup(name="Ik_Controls")

        # Foot Control
        end_base_name = self.base_name + "_Foot" if self.description != "Foot" else self.base_name
        self.foot_ctrl = self.create_foot_control(base_name=end_base_name, pack_size=self.ctrl_size, 
                                                  foot_joint=self.base_joints[0], parent=self.ik_control_grp, 
                                                  color=self.side_color, rotate_order="xzy")
        
        # Add Anim Constraint
        self.anim_cns_control = rig_controls.create_anim_constraint_control(parent_ctrl=self.foot_ctrl,
                                                                            match_joint=self.base_joints[0],
                                                                            control_size=self.ctrl_size / 2.0,
                                                                            base_name=self.base_name,
                                                                            color=self.side_color_tertiary)
        
        # System Hierarchy
        self._ik_setup()
        self._ik_foot_system()

        # Attrs
        self._ik_add_attrs()
        
        # Connect
        self._ik_connect()
    
    
    def create_fk(self):
        # Vars
        self.fk_ctrls = []
        
        # Fk Joints and Group
        self.fk_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Fk")
        self.fk_setup_grp = self._create_subgroup(name="Fk_Setup", children=self.fk_joints[0])
        
        # Create Group
        self.fk_control_grp = self._create_subgroup(name="Fk_Controls")
        
        # Ankle Control
        self.ankle_fk_ctrl = i_node.create("control", control_type="3D Cube", degree=1, name=self.base_name + "_Ankle_Fk",
                                           with_gimbal=False, match_rotation=True, position_match=self.base_joints[0],
                                           additional_groups=["Xtra_01", "Xtra_02"],size=self.ctrl_size * 0.75, 
                                           color=self.side_color_scndy, parent=self.fk_control_grp)
        self.fk_ctrls.append(self.ankle_fk_ctrl)
        
        # Ball Control
        self.ball_fk_ctrl = i_node.create("control", control_type="3D Cube", degree=1, name=self.base_name + "_Ball_Fk",
                                          with_gimbal=False, match_rotation=True, position_match=self.base_joints[1],
                                          size=self.ctrl_size * 0.75, color=self.side_color_scndy, parent=self.ankle_fk_ctrl.last_tfm)
        self.fk_ctrls.append(self.ball_fk_ctrl)
        
        # Constrain
        ankle_fk_joint = self.fk_joints[0]
        ball_fk_joint = self.fk_joints[1]
        # i_constraint.constrain(ankle_fk_joint, self.ankle_fk_ctrl.top_tfm, as_fn="point")
        # i_constraint.constrain(ball_fk_joint, self.ball_fk_ctrl.top_tfm, as_fn="point")
        i_constraint.constrain(self.ankle_fk_ctrl.last_tfm, ankle_fk_joint, as_fn="point")
        i_constraint.constrain(self.ball_fk_ctrl.last_tfm, ball_fk_joint, as_fn="point")
        i_constraint.constrain(self.ankle_fk_ctrl.control, ankle_fk_joint, as_fn="orient")
        i_constraint.constrain(self.ball_fk_ctrl.control, ball_fk_joint, as_fn="orient")
    
    def create_ikfk_switch(self):
        # Find Ik Controls to drive
        ik_controls = [ik.control for ik in self.ik_ctrls]
        ik_controls += [ik.gimbal for ik in self.ik_ctrls if ik.gimbal]
        ik_controls += [self.foot_ctrl.control, self.foot_ctrl.gimbal]
        
        # Find Fk Controls to drive
        fk_controls = [fk.control for fk in self.fk_ctrls]
        fk_controls += [fk.gimbal for fk in self.fk_ctrls if fk.gimbal]
        
        # Create switch. Driving visibilities
        Build_Foot_Master._create_ikfk_switch(self, ik_controls=ik_controls, ik_joints=self.ik_joints, 
                                              fk_controls=fk_controls, fk_joints=self.fk_joints, 
                                              offset_distance=0.25 * self.side_mult, translation=True)
        
    def _cleanup_bit(self):
        # Cleanup Created Stuff & Store Class Attrs
        self.bind_joints = self.base_joints[:-1]

        # Lock and Hide
        i_attr.lock_and_hide(node=self.foot_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ankle_ik_ctrl.control, attrs=["r", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ball_ik_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.toe_ik_ctrl.control, attrs=["t", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.toe_tip_ik_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.heel_ik_ctrl.control, attrs=["s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ball_fk_ctrl.control, attrs=["s"], lock=True, hide=True)  # "t", 
        i_attr.lock_and_hide(node=self.ankle_fk_ctrl.control, attrs=["s"], lock=True, hide=True)  # "t", 
        
        # Parenting
        self.base_joints[0].set_parent(self.pack_bind_jnt_grp)
        i_utils.parent(self.ik_setup_grp, self.fk_setup_grp, self.pack_rig_jnt_grp)
        i_utils.parent(self.ik_control_grp, self.fk_control_grp, self.pack_ctrl_grp)

        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], unlock=True)
        i_constraint.constrain(self.base_joints[-1], self.ikfk_switch_control, mo=True, as_fn="parent")
        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], lock=True)
        
        # Hide locators group
        # - Delete constraint
        if not self.is_mirror:
            loc_grp_pac = i_constraint.get_constraint_by_driver(driven=self.loc_grp)[0].node
            i_utils.delete(loc_grp_pac)
        self.loc_grp.vis(0)
        
        # Force ik handle pv to keep from twisting
        self.ball_ikh.poleVector.set([0, 0, 0])
    
    
    def connect_elements(self):
        i_constraint.constrain(self.stretch_toes[1], self.toe_ik_ctrl.xtra_grp, mo=True, aim=[0, 1, 0], u=[0, 1, 0], # u=[0, 1, -1]
                          wut="object", wuo=self.toes_up_grp, wu=[0, 1, 0], as_fn="aim")

    def _create_bit(self):
        # Create
        self.create_ik()
        self.create_fk()
        self.create_ikfk_switch()
        self.create_stretch()
        self.create_helpers(foot_control=self.foot_ctrl.control)

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        # - Pack
        # -- Need to do this also because if stitch_bit() is called in different class instance, the self variables won't exist
        pack_ankle_base_joint = pack_obj.base_joints[0]
        pack_ankle_ik_joint = pack_obj.ik_joints[0]
        pack_ankle_fk_joint = pack_obj.fk_joints[0]
        pack_ankle_fk_ctrl_offset = pack_obj.ankle_fk_ctrl.top_tfm
        pack_ankle_fk_control = pack_obj.ankle_fk_ctrl.control
        pack_sys_offset_grp = pack_obj.sys_offset_grp
        pack_foot_ctrl_top = pack_obj.foot_ctrl.top_tfm
        pack_foot_ik_control = pack_obj.foot_ctrl.control
        pack_foot_ik_gimbal = pack_obj.foot_ctrl.gimbal
        pack_ankle_ikh_offset = pack_obj.ankle_ik_hdl_offset_grp
        pack_anim_cns_control = pack_obj.anim_cns_control
        
        if parent_build_type == "Leg":
            # Vars
            # :note: Do only for Leg, not Leg_Watson because they're build so differently
            # -- Use the ones manually added in Limb instead of the PackMaster default lasts. These account for quad.
            parent_base_joint = parent_obj.last_base_joint
            parent_ik_joint = parent_obj.last_ik_joint
            parent_fk_joint = parent_obj.last_fk_joint
            parent_ankle_fk_control = parent_obj.last_fk_control
            parent_ankle_ik_control = parent_obj.ik_end_ctrl.control
            parent_ankle_ik_gimbal = parent_obj.ik_end_ctrl.gimbal
            parent_ikh_follow_origin_grp = parent_obj.follow_end_origin_grp
            parent_dist_btm_loc = parent_obj.btm_locator
            parent_anim_cns_control = parent_obj.anim_cns_control
            parent_mid_fk_control = parent_obj.fk_ctrls[1].last_tfm
            if parent_obj.is_quad:
                parent_foot_fk_ctrl = parent_obj.fk_ctrls[-1].control
                parent_foot_fk_jnt = parent_obj.fk_joints[-1]
                parent_foot_ik_jnt = parent_obj.ik_joints[-1]
                parent_foot_base_jnt = parent_obj.base_joints[-1]
            
            # Parenting
            self.stitch_cmds.append({"parent" : {"child" : pack_ankle_base_joint, "parent" : parent_base_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_ik_joint, "parent": parent_ik_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_joint, "parent": parent_fk_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_ctrl_offset, "parent": parent_ankle_fk_control}})
            self.stitch_cmds.append({"parent": {"child": pack_sys_offset_grp, "parent": parent_ankle_ik_gimbal}})
            
            # Un-Constrain and store so unstitch can re-constrain & attach to foot instead
            # :note: Just turning off the influence doesn't work because then when move the consolidated foot control, everything pops. ugh. maya
            self.stitch_cmds.append({"delete_constraint": {"driven": parent_ikh_follow_origin_grp}})
            self.stitch_cmds.append({"parent": {"child": parent_ikh_follow_origin_grp, "parent": pack_ankle_ikh_offset}})  # Leg UNDER Foot, yes.
            self.stitch_cmds.append({"delete_constraint": {"driven": parent_dist_btm_loc}})
            self.stitch_cmds.append({"constrain": {"args": [pack_ankle_ikh_offset, parent_dist_btm_loc], "kwargs": {"as_fn": "point"}}})

            # Transfer foot attributes onto corresponding leg objects
            transfer_objs = [[pack_foot_ik_control, parent_ankle_ik_control], [pack_foot_ik_gimbal, parent_ankle_ik_gimbal],
                             [pack_anim_cns_control, parent_anim_cns_control]]
            if parent_obj.is_quad:
                transfer_objs.append([parent_foot_base_jnt, pack_ankle_base_joint])
            for objs in transfer_objs:
                pack_tfr_obj, parent_tfr_obj = objs
                self.stitch_cmds.append({"transfer_attributes": {"from": pack_tfr_obj, "to": parent_tfr_obj, "ignore": ["GimbalVis"]}})
            
            # Follow attrs
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "orient",
                                                "dv": parent_mid_fk_control, "options": parent_mid_fk_control}})

            # Hide shapes of foot control from foot pack
            force_vis = [pack_foot_ik_control, pack_foot_ctrl_top, pack_anim_cns_control]
            if parent_obj.is_quad:  # Quad
                force_vis += [parent_foot_fk_ctrl, parent_foot_fk_jnt, parent_foot_ik_jnt, parent_foot_base_jnt]
            else:
                force_vis.append(parent_ankle_fk_control)
            # - Do it
            self.stitch_cmds.append({"force_vis" : {"objects" : force_vis, "value" : 0}})

            # # Shift Follow Attrs to the bottom
            # self.stitch_cmds.append({"shift_follow_attrs": {"control": parent_ankle_ik_control}})
        
        elif parent_build_type == "Leg_Watson":  # :note: Will never be a quad. Leg_Watson doesn't support that.
            # Vars
            # :note: Do only for Leg, not Leg_Watson because they're build so differently
            # -- Use the ones manually added in Limb instead of the PackMaster default lasts. These account for quad.
            parent_base_joint = parent_obj.base_joints[-1]
            parent_ik_joint = parent_obj.ik_joints[-1]
            parent_fk_joint = parent_obj.fk_joints[-1]
            parent_ankle_fk_control = parent_obj.fk_ctrls[-1].control
            parent_ankle_ik_control = parent_obj.ik_end_ctrl.control
            parent_ankle_ik_gimbal = parent_obj.ik_end_ctrl.gimbal

            # Parenting
            self.stitch_cmds.append({"parent": {"child": pack_ankle_base_joint, "parent": parent_base_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_ik_joint, "parent": parent_ik_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_joint, "parent": parent_fk_joint}})
            self.stitch_cmds.append({"parent": {"child": pack_ankle_fk_ctrl_offset, "parent": parent_ankle_fk_control}})
            self.stitch_cmds.append({"parent": {"child": pack_sys_offset_grp, "parent": parent_ankle_ik_gimbal}})

            # Transfer foot control attributes
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_control, "to": parent_ankle_ik_control, "ignore": ["GimbalVis"]}})
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_foot_ik_gimbal, "to": parent_ankle_ik_gimbal, "ignore": ["GimbalVis"]}})
            
            # Hide foot things no longer needed because they're on the leg version
            self.stitch_cmds.append({"force_vis": {"objects": [pack_foot_ik_control, pack_foot_ik_gimbal], "value" : 0}})

            # # Shift Follow Attrs to the bottom
            # self.stitch_cmds.append({"shift_follow_attrs": {"control": parent_ankle_ik_control}})
        
        elif parent_build_type == "Cog":
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_control, "cns_type": "parent",
                                                "options": [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]}})
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "orient",
                                                "options": [parent_ground_ctrl, parent_root_ctrl]}})
        
        elif parent_build_type.startswith("Spine"):
            parent_hip_control = parent_obj.start_ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_control, "cns_type": "parent",
                                                "options": parent_hip_control}})
            self.stitch_cmds.append({"follow": {"driving": pack_ankle_fk_control, "cns_type": "orient",
                                                "options": parent_hip_control}})
        
        elif parent_build_type == "Hip":
            parent_control = parent_obj.ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_foot_ik_control, "cns_type": "parent",
                                                "dv": parent_control, "options": parent_control}})
