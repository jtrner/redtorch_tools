import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Spine_Simple(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        self.ik_world = False
        self.fk_world = False
        
        # Changeable things
        self.ctrl_count = 0  # Number of ik/fk controls -- NOW DEFUNCT. Temp for backwards compatibility. Use ik_ctrl_count / fk_ctrl_count
        self.ik_ctrl_count = 2  # Number of ik controls
        self.fk_ctrl_count = 2  # Number of fk controls
        self.tweak_ctrl_count = 6
        self.pivot_ctrl_position = "end"
        self.is_neck = False
        self.start_rot_order = "xzy"
        self.end_rot_order = "xzy"

        # Set the pack info
        self.joint_names = ["spine"]
        self.description = "Spine"
        self.length = 7
        self.length_min = 7  # Get errors otherwise
        self.length_max = 7  # Get errors otherwise
        self.base_joint_positions = ["incy0.25"]
        self.accepted_stitch_types = ["Cog"]
        self.start_name = "Hips"
        self.start_follow_name = "Hips"
        self.end_name = "Chest"
        self.end_follow_name = "Chest"

    def _class_prompts(self):
        # self.prompt_info["ctrl_count"] = {"type": "int", "value": self.ctrl_count, "min": 2, "max": None}
        self.prompt_info["ik_ctrl_count"] = {"type": "int", "value": self.ik_ctrl_count, "min": 2, "max": None}
        self.prompt_info["fk_ctrl_count"] = {"type": "int", "value": self.fk_ctrl_count, "min": 2, "max": None}
        self.prompt_info["tweak_ctrl_count"] = {"type": "int", "value": self.tweak_ctrl_count, "min": 2, "max": None}
        self.prompt_info["pivot_ctrl_position"] = {"type" : "option", "menu_items" : ["start", "end"], "value" : self.pivot_ctrl_position}
        self.prompt_info["start_name"] = {"type" : "text", "text" : self.start_name}
        self.prompt_info["end_name"] = {"type" : "text", "text" : self.end_name}

    def create_controls(self):
        # End Ctrl
        self.end_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color, size=self.ctrl_size * 1.25,
                                        position_match=self.base_joints[-1], name=self.base_name + "_" + self.end_name, #match_rotation=False,
                                        gimbal_color=self.side_color_scndy, parent=self.pack_grp,  # Parent later
                                        follow_name=self.end_follow_name, flip_shape=self.flip_shape, rotate_order=self.end_rot_order)

        # Pivot Ctrl
        pivot_name = self.end_name
        pivot_match_i = -1
        if self.pivot_ctrl_position == "start":
            pivot_name = self.start_name
            pivot_match_i = 0
        pivot_name += "_Pivot"
        self.pivot_ctrl = i_node.create("control", control_type="3D Snowflake", color=self.side_color_tertiary,
                                              size=self.ctrl_size * 1.25, position_match=self.base_joints[pivot_match_i], #match_rotation=False,
                                              name=self.base_name + "_" + pivot_name, with_gimbal=False, follow_name=pivot_name,
                                              parent=self.pack_grp, flip_shape=self.flip_shape, rotate_order=self.end_rot_order)

        # Start Ctrl
        self.start_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color, size=self.ctrl_size * 1.25,
                                       position_match=self.base_joints[0], name=self.base_name + "_" + self.start_name,
                                       with_gimbal=False, follow_name=self.start_follow_name, parent=self.pivot_ctrl.last_tfm,
                                       flip_shape=self.flip_shape, rotate_order=self.start_rot_order)
        
        # Mid Ctrls
        self.fk_ctrls = []
        self.ik_ctrls = []
        self.mid_ctrls = []
        previous_fk = self.pivot_ctrl
        # - Get index numbers for ik controls
        ik_ctrl_joint_nums = range(len(self.base_joints))
        if self.ik_ctrl_count != len(self.base_joints):
            ik_ctrl_joint_nums = logic_py.get_evenly_divided(number_divisions=self.ik_ctrl_count, from_value=1, to_value=len(self.base_joints) - 1)
        if self.ik_ctrl_count == 2:  # Need to shift these down
            ik_ctrl_joint_nums = [num - 1 for num in ik_ctrl_joint_nums]
        # - Get index numbers for fk controls
        fk_ctrl_joint_nums = range(len(self.base_joints))
        if self.fk_ctrl_count != len(self.base_joints):
            fk_ctrl_joint_nums = logic_py.get_evenly_divided(number_divisions=self.fk_ctrl_count, from_value=1, to_value=len(self.base_joints) - 1)
        if self.fk_ctrl_count == 2:  # Need to shift these down
            fk_ctrl_joint_nums = [num - 1 for num in fk_ctrl_joint_nums]
        # - Create Controls
        ctrl_i = 1
        for jnt in self.base_joints[1:-1]:
            i = self.base_joints.index(jnt)  # Doesn't work well to enumerate when not doing full list
            # - Null for Non-Controls but they allow the cluster spline to work
            if i not in fk_ctrl_joint_nums:
                fk_ctrl = self._create_null_control_mimic(name="Fk_%02d" % i, position_match=jnt, parent=previous_fk.last_tfm)
            # - Fk Ctrl
            else:
                fk_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_scndy,
                                        size=self.ctrl_size * 0.75, position_match=jnt, with_gimbal=False, 
                                        name=self.base_name + "_Fk_%02d" % ctrl_i, parent=previous_fk.last_tfm,
                                        follow_name=self.description + "_Fk_%02d" % ctrl_i, 
                                        flip_shape=self.flip_shape, #match_rotation=False,
                                        lock_hide_attrs=["s", "v"], rotate_order="xzy")
                self.fk_ctrls.append(fk_ctrl)
            previous_fk = fk_ctrl
            
            # - Ik Ctrl
            if i not in ik_ctrl_joint_nums:
                ik_ctrl = self._create_null_control_mimic(name="Ik_%02d" % i, position_match=jnt, parent=fk_ctrl.last_tfm)
                ik_ctrl.control.zero_out()
            else:
                ik_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color,
                                        size=self.ctrl_size * 0.9, position_match=fk_ctrl.last_tfm, with_gimbal=False, 
                                        name=self.base_name + "_Ik_%02d" % ctrl_i, parent=fk_ctrl.last_tfm,
                                        follow_name=self.description + "_Ik_%02d" % ctrl_i, 
                                        flip_shape=self.flip_shape, #match_rotation=False,
                                        lock_hide_attrs=["r", "s", "v"], rotate_order="yzx",)
                self.ik_ctrls.append(ik_ctrl)
                ctrl_i += 1
            self.mid_ctrls.append([jnt, fk_ctrl, ik_ctrl])
        # - Parent the pivot control
        pivot_parent = previous_fk #if self.pivot_ctrl_position == "end" else self.start_ctrl
        self.end_ctrl.top_tfm.set_parent(pivot_parent.last_tfm)

        # Set World
        # - FK
        if self.fk_world:
            for ctrls in self.mid_ctrls:
                jnt, fk_ctrl, ik_ctrl = ctrls
                fk_ctrl.control.r.set([0, 0, 0])
                ik_ctrl.control.r.set([0, 0, 0])
        # - IK
        if self.ik_world:
            for ctrl in [self.start_ctrl, self.end_ctrl, self.pivot_ctrl]:
                ctrl.control.r.set([0, 0, 0])
    
    def create_ikfk(self):
        # Create IK Control
        # :note: Specify only controls, not the ik/fk transforms for visibility toggling
        self._create_ikfk_switch(ik_controls=[ctrl.control for ctrl in self.ik_ctrls],
                                ik_joints=[ctrls[0] for ctrls in self.mid_ctrls],
                                fk_controls=[ctrl.control for ctrl in self.fk_ctrls],
                                fk_joints=[ctrls[0] for ctrls in self.mid_ctrls],
                                driven_objs=False, position_match=self.base_joints[int(len(self.base_joints) / 2)],
                                offset_distance=[0, 0, -4], flip_shape=[90, 0, 0])
        
        # Prep Root Control Attrs
        self.ikfk_rev = i_node.create("reverse", n=self.base_name + "_IkFk_Rev")
        self.ikfk_blend_attr.drive(self.ikfk_rev.inputX)
        
        # Connect all the mids
        # :TODO: Values only really tested with default build of 2 controls and 5 base joints
        # offset = 1.0 / len(self.mid_ctrls)
        # chest_offset = offset
        # hips_offset = 1.0
        fk_tfm_locs = []
        fk_ctrl_locs = []
        first_ik_control = None
        ik_loc_cns = {}
        for i, ctrls in enumerate(self.mid_ctrls):
            # Vars
            jnt, fk_ctrl, ik_ctrl = ctrls
            fk_is_control = i_control.check_is_control(fk_ctrl.control, raise_error=False)
            ik_is_control = i_control.check_is_control(ik_ctrl.control, raise_error=False)

            # Create Locators
            ik_loc = i_node.create("locator", n=ik_ctrl.control + "_Loc")
            fk_loc = i_node.create("locator", n=fk_ctrl.control + "_Loc")
            ik_loc.v.set(0, l=True)
            fk_loc.v.set(0, l=True)
            i_node.copy_pose(driver=jnt, driven=[ik_loc, fk_loc])
            if not fk_is_control:
                fk_tfm_locs.append(fk_loc)
            else:
                fk_ctrl_locs.append(fk_loc)
            
            # Constrain IK
            # - Constrain
            ik_drivers = []
            if ik_is_control:
                ik_drivers = [self.start_ctrl.last_tfm, self.end_ctrl.last_tfm]
                if not first_ik_control:
                    ik_drivers = list(reversed(ik_drivers))
                    first_ik_control = ik_ctrl.control
            elif i == 0:
                ik_drivers = [self.start_ctrl.last_tfm, self.mid_ctrls[1][2].last_tfm]
            elif i == (len(self.mid_ctrls) - 1):
                ik_drivers = [self.mid_ctrls[i - 1][2].last_tfm, self.end_ctrl.last_tfm]
            else:
                ik_drivers = [self.mid_ctrls[i - 1][2].last_tfm, self.mid_ctrls[i + 1][2].last_tfm]
            ikfk_blend_cns = i_constraint.constrain(ik_drivers[0], ik_drivers[1], ik_loc, mo=True, as_fn="point")
            ik_loc_cns[ik_loc] = ikfk_blend_cns
            # - Parent Locs
            i_utils.parent(ik_loc, fk_loc, fk_ctrl.last_tfm)
            # - Add constraint to control
            cns_pac = i_constraint.constrain(ik_loc, fk_loc, ik_ctrl.top_tfm, mo=True, as_fn="parent")
            # - Drive and set weights
            self.ikfk_blend_attr.drive(cns_pac.w0)  # cns_pac.w1
            self.ikfk_rev.outputX.drive(cns_pac.w1)  # cns_pac.w0
            if ik_is_control:
                ikfk_blend_cns.w0.set(0.32)
                ikfk_blend_cns.w1.set(0.68)
                # ikfk_blend_cns.w0.set(chest_offset)
                # chest_offset += offset
                # ikfk_blend_cns.w1.set(hips_offset)
                # hips_offset -= offset
            else:
                ikfk_blend_cns.w0.set(0.6)
                ikfk_blend_cns.w1.set(0.6)
        
        # Constrain FK -- so when squash spine don't get flipping
        # :note: Only do this for fk items that are not controls
        fk_driver_controls = [self.start_ctrl.last_tfm] + fk_ctrl_locs + [self.end_ctrl.last_tfm]
        prev_i = 0
        for i, fk_loc in enumerate(fk_tfm_locs):
            fk_drivers = fk_driver_controls[prev_i:i + 2]
            i_constraint.constrain(fk_drivers, fk_loc, weight=0.5, as_fn="point")
            prev_i = i + 1
        
        # Fix the ik constraint's MO (gets borked after manually weighting)
        # - Zero out first
        for cns in ik_loc_cns.values():
            cns.offset.set([0, 0, 0])
        # - Negate
        for ik_loc, ikfk_blend_cns in ik_loc_cns.items():
            ikfk_blend_cns.offset.set([-1 * tr for tr in ik_loc.t.get()])
    
    def create_ribbon(self):
        # Create ribbon
        ribbon = rig_joints.joints_to_ribbon(name=self.base_name, joints=self.base_joints)
        
        # # Rename joints  # :TODO: Renaming base joints is messing with the attr class rename for some reason
        # for jnt in self.base_joints:
        #     jnt.rename("Orig_" + jnt.name)
        
        # Make Hi-Res joints from the Ribbon
        joint_count = len(self.base_joints) * 2 - 1  # 13
        self.hi_res_joints = rig_joints.ribbon_to_joints(name=self.base_name + "_HiRes", joint_count=joint_count, 
                                                         surface=ribbon, radius=self.joint_radius)
        rig_joints.orient_joints(joints=self.hi_res_joints, orient_as=self.orient_joints, up_axis=self.orient_joints_up_axis)
        for jnt in self.hi_res_joints: # :note: Not sure why this is done (doesn't say anything intentionally naming with '_Main', but it's in the orig code
            jnt.rename(jnt.name.replace("_Main", ""))
        if self.top_node:
            vis_attr = self.top_node + ".JointVis"
            if i_utils.check_exists(vis_attr):
                vis_attr = i_attr.Attr(vis_attr)
                for jnt in self.hi_res_joints:
                    vis_attr.drive(jnt + ".v")
        
        # Delete Ribbon
        ribbon.delete()

        # Create tweaks for Hi-Res Joints
        # self.tweak_ctrls += rig_controls.create_tweaks(joints=self.hi_res_joints[1:-1], flip_shape=self.flip_shape, size=self.tweak_ctrl_size)
        # for i, tweak in enumerate(self.tweak_ctrls):
        #     i_constraint.constrain(self.hi_res_joints[i + 1], tweak.top_tfm, as_fn="parent")
        
        tweak_joint_nums = logic_py.get_evenly_divided(number_divisions=self.tweak_ctrl_count, from_value=1, to_value=len(self.hi_res_joints) - 1)
        tweak_joints = [self.hi_res_joints[i] for i in tweak_joint_nums]
        self.tweak_ctrls += rig_controls.create_tweaks(joints=tweak_joints, flip_shape=self.flip_shape, size=self.tweak_ctrl_size,
                                                       name_match=self.base_name, name_num_start=1)
        self.tweak_jnt_match = {}
        twk_i = 0
        for i in tweak_joint_nums:
            self.tweak_jnt_match[self.hi_res_joints[i]] = self.tweak_ctrls[twk_i]
            i_constraint.constrain(self.hi_res_joints[i], self.tweak_ctrls[twk_i].top_tfm, as_fn="parent")
            twk_i += 1

        self.tweak_tops = [ctrl.top_tfm for ctrl in self.tweak_ctrls]
        self.tweak_grp = self._create_subgroup(name="Tweak_Ctrl", children=self.tweak_tops, parent=self.pack_ctrl_grp)

        # # Cleanup
        # self.hi_res_joints[0].freeze(a=True, t=True, r=True, s=True, n=0, pn=1)
    
    
    def create_spline(self):
        # Create Curve
        # :note: Need to keep this using base_joints, not hi_res_joints because the length of the curves cvs need to match
        # length of mid-controls created, which is based on base_joints
        self.spline_curve = rig_joints.create_curve_for_joints(joints=self.base_joints, name=self.base_name + "_Crv")
        cvs = self.spline_curve.get_cvs()
        
        # Create Clusters
        clusters = []
        for i, cv in enumerate(cvs):
            cd = i_deformer.CreateDeformer(name=self.base_name + "_%02d" % (i + 1), target=cv)
            clust = cd.cluster()
            clusters.append(clust[1])
        
        # Cluster Vars
        chest_cluster = clusters[-1]
        hips_cluster = clusters[0]
        mid_clusters = clusters[1:-1]
        
        # Connect Clusters to Controls
        i_constraint.constrain(self.start_ctrl.last_tfm, hips_cluster, as_fn="parent")
        i_constraint.constrain(self.end_ctrl.last_tfm, chest_cluster, as_fn="parent")
        for i, mid_clst in enumerate(mid_clusters):
            # - Create constraint
            ik, fk = self.mid_ctrls[i][2].last_tfm, self.mid_ctrls[i][1].last_tfm
            cls_cns = i_constraint.constrain(ik, fk, mid_clst, as_fn="parent")
            # - Connect constraint to ikfk switch
            self.ikfk_switch_control.FKIKSwitch.drive(cls_cns.w0)
            ikfk_switch_rev = self.ikfk_switch_control.connections(type="reverse")[0]
            ikfk_switch_rev.outputX.drive(cls_cns.w1)
        
        # Create Spline IKH
        ik_info = rig_joints.create_ik_spline(first_joint=self.hi_res_joints[0], curve=self.spline_curve, simple_curve=False) # self.base_joints
        self.spline_ikh = ik_info[0]
        
        # Cleanup
        self._create_subgroup(name="Cls", parent=self.pack_utility_grp, children=clusters)
        i_utils.parent(self.spline_ikh, self.spline_curve, self.pack_utility_grp)
    
    
    def create_bind_joints(self):
        self.bind_joints = []
        self.bind_jnt_match = {}
        
        # Create
        i_utils.select(cl=True)  # because of joints. yay.
        for i, hi_jnt in enumerate(self.hi_res_joints):
            # - Vars
            jnt_name = hi_jnt.name.replace("_HiRes", "")
            driver = None
            driver_is_tweak = False
            if i == 0:
                jnt_name = self.start_ctrl.control.replace("_Ctrl", "")
                driver = self.start_ctrl.last_tfm
            elif i + 1 == len(self.hi_res_joints):
                jnt_name = self.end_ctrl.control.replace("_Ctrl", "")
                driver = self.end_ctrl.last_tfm
            elif hi_jnt not in self.tweak_jnt_match.keys():  # "Don't want bind joints not driven by tweaks" - Steven
                continue
            else:
                driver_is_tweak = True
                driver = self.tweak_jnt_match.get(hi_jnt).last_tfm
            # - Create joint
            bnd_jnt = i_node.create("joint", n=jnt_name, radius=self.joint_radius * 1.5)
            i_utils.select(cl=True)  # because of joints. yay.
            i_node.copy_pose(driver=hi_jnt, driven=bnd_jnt)
            self.bind_joints.append(bnd_jnt)
            self.bind_jnt_match[hi_jnt] = bnd_jnt
            # - Constrain
            i_constraint.constrain(driver, bnd_jnt, mo=True, as_fn="parent")
            if driver_is_tweak or i == 0:
                i_constraint.constrain(driver, bnd_jnt, mo=True, as_fn="scale")
        
        # Parent
        i_utils.parent(self.bind_joints, self.pack_bind_jnt_grp)
    
    
    def create_stretch_volume(self):
        # :note: Volume is to work on the tweak control and the joint, but the joint is control * volume.
        
        stretch_attrs = list(self.orient_joints[1:])  # Only drive non-primary joint axis
        
        # Create stretch
        str_info = rig_joints.stretch_volume(joints=self.hi_res_joints, attr_obj=self.ikfk_switch_control, stretch_axis=stretch_attrs, 
                                            curve=self.spline_curve, volume=False, ref_curve_parent=self.pack_utility_cns_grp)
        
        # Create Volume
        vol_info = rig_joints.stretch_volume(joints=self.tweak_tops, attr_obj=self.ikfk_switch_control, stretch_axis=stretch_attrs, 
                                            curve=self.spline_curve, stretch=False, ref_curve_parent=self.pack_utility_cns_grp)
        
        # Tweak Scales
        for high_jnt, tweak_ctrl in self.tweak_jnt_match.items():
            # - Vars
            bind_jnt = self.bind_jnt_match.get(high_jnt)
            base_name = tweak_ctrl.control.replace("_Ctrl", "")
            # - Connect
            vol_md = i_node.create("multiplyDivide", n=base_name + "Volume_Md")
            tweak_ctrl.top_tfm.s.drive(vol_md.input1)
            tweak_ctrl.control.s.drive(vol_md.input2)
            vol_md.output.drive(bind_jnt.s)
    
    def create_twist(self):
        # Vars
        twist_ax_attr = "r" + self.twist_axis
        
        # Create group
        self.pin_grp = self._create_subgroup(name="Pin", parent=self.pack_utility_grp, children=self.hi_res_joints[0],
                                             xform_driver=self.start_ctrl.last_tfm)
        
        # :note: Spine should now be rooted on the curve.
        
        # Set up the twist math
        bn = self.base_name + "_" + self.start_name + self.end_name
        adl = i_node.create("addDoubleLinear", n=bn + "_Twist_Adl")
        md = i_node.create("multiplyDivide", n=bn + "_Twist_Md")
        self.start_ctrl.control.attr(twist_ax_attr).drive(md.input1X)
        md.outputX.drive(adl.input1)
        md.input2X.set(-1)
        self.end_ctrl.control.attr(twist_ax_attr).drive(adl.input2)
        prev_adl = adl
        for ctrl in self.mid_ctrls:
            fk_ctrl = ctrl[1]
            name = fk_ctrl.control.replace("Tweak", "Twist") + "_Adl"#.replace("Ctrl", "Adl").replace("Tfm", "Adl")
            fk_adl = i_node.create("addDoubleLinear", n=name)
            fk_ctrl.control.attr(twist_ax_attr).drive(fk_adl.input1)
            prev_adl.output.drive(fk_adl.input2)
            prev_adl = fk_adl
        
        # AutoTwist and Twist / Roll Offsets
        # - Add Control Attrs
        i_attr.create_divider_attr(node=self.ikfk_switch_control, ln="Twist")  # , en="Settings"
        auto_twist_attr = i_attr.create(node=self.ikfk_switch_control, ln="AutoTwist", dv=1, min=0, max=1, k=False)
        self.ikfk_switch_control.FKIKSwitch.drive(auto_twist_attr)
        twist_add_attr = i_attr.create(node=self.ikfk_switch_control, ln="TwistAdd", k=True, dv=0)
        spine_roll_attr = i_attr.create(node=self.ikfk_switch_control, ln="SpineRoll", k=True, dv=0)
        # - Create Math Nodes
        twist_add_adl = i_node.create("addDoubleLinear", n=self.base_name + "_TwistAdd_Adl")
        twist_onoff_bc = i_node.create("blendColors", n=self.base_name + "_TwistOnOff_Bc")
        roll_add_adl = i_node.create("addDoubleLinear", n=self.base_name + "_RollAdd_Adl")
        roll_md = i_node.create("multiplyDivide", n=self.base_name + "_Roll_Md")
        roll_offset_adl = i_node.create("addDoubleLinear", n=self.base_name + "_RollOffset_Adl")
        # - Connect: Twist On/Off
        prev_adl.output.drive(twist_onoff_bc.color1R)
        twist_onoff_bc.color2R.set(1)
        auto_twist_attr.drive(twist_onoff_bc.blender)
        # - Connect Twist Add
        twist_onoff_bc.outputR.drive(twist_add_adl.input1)
        twist_add_attr.drive(twist_add_adl.input2)
        # - Connect Spine Roll
        spine_roll_attr.drive(roll_add_adl.input2)
        self.pivot_ctrl.control.attr(twist_ax_attr).drive(roll_offset_adl.input1)
        self.start_ctrl.control.attr(twist_ax_attr).drive(roll_md.input1X)
        self.ikfk_switch_control.FKIKSwitch.drive(roll_md.input2X)
        roll_md.outputX.drive(roll_offset_adl.input2)
        roll_offset_adl.output.drive(roll_add_adl.input1)
        # self.start_ctrl.control.attr(twist_ax_attr).drive(roll_add_adl.input1)
        # - Connect FINAL
        twist_add_adl.output.drive(self.spline_ikh.twist)
        roll_add_adl.output.drive(self.spline_ikh.roll)
        
        # Twist: Twist as if it were fk rather than twisting the whole spine with each control
        # - Split tweaks
        # :note: Tweaks match with HiRes joints / Fk Controls match with base joints, but there's no relation btwn joints
        # So need to do this sloppy-ness.
        tweak_section_match = {"hips": [], "mid": [], "chest": []}
        first_fk_y = self.fk_ctrls[0].top_tfm.xform(q=True, t=True, ws=True)[1]
        last_fk_y = self.fk_ctrls[-1].top_tfm.xform(q=True, t=True, ws=True)[1]
        for tweak in self.tweak_ctrls:
            tweak_y = tweak.top_tfm.xform(q=True, t=True, ws=True)[1]
            if tweak_y < first_fk_y:
                tweak_section_match["hips"].append(tweak.cns_grp)
            elif tweak_y > last_fk_y:
                tweak_section_match["chest"].append(tweak.cns_grp)
            else:
                tweak_section_match["mid"].append(tweak.cns_grp)
        
        # - IkFk Twist MD
        ikfk_twist_md = i_node.create("multiplyDivide", n=self.base_name + "_TwistIkFk_Md")
        self.ikfk_rev.outputX.drive(ikfk_twist_md.input1X)
        ikfk_twist_md.input2X.set(0.5)
        
        # - End area
        chest_twist_pma = i_node.create("plusMinusAverage", n=self.base_name + "_TwistTweak%s_Pma" % self.end_name)
        i = 0  # Don't enumerate because could have multiple controls in loop
        for ctrl in [self.end_ctrl] + self.fk_ctrls:
            ctrl.control.attr(twist_ax_attr).drive(chest_twist_pma.attr("input1D[%i]" % i))
            i += 1
            if ctrl.gimbal:
                ctrl.gimbal.attr(twist_ax_attr).drive(chest_twist_pma.attr("input1D[%i]" % i))
                i += 1
        chest_twist_md = i_node.create("multiplyDivide", n=self.base_name + "_TwistTweak%s_Md" % self.end_name)
        chest_twist_pma.output1D.drive(chest_twist_md.input1X)
        ikfk_twist_md.outputX.drive(chest_twist_md.input2X)
        # -- Connect to tweaks
        for tweak in tweak_section_match.get("chest"):
            chest_twist_md.outputX.drive(tweak.attr(twist_ax_attr))
        
        # - Mid area
        mid_twist_md = i_node.create("multiplyDivide", n=self.base_name + "_TwistTweakMid_Md")
        self.fk_ctrls[0].control.attr(twist_ax_attr).drive(mid_twist_md.input1X)
        ikfk_twist_md.outputX.drive(mid_twist_md.input2X)
        # -- Connect to tweaks
        for tweak in tweak_section_match.get("mid"):
            mid_twist_md.outputX.drive(tweak.attr(twist_ax_attr))
        
        # - Start area
        hips_twist_md = i_node.create("multiplyDivide", n=self.base_name + "_TwistTweak%s_Md" % self.start_name)
        self.start_ctrl.control.attr(twist_ax_attr).drive(hips_twist_md.input1X)
        ikfk_twist_md.outputX.drive(hips_twist_md.input2X)
        # -- Connect to tweaks
        for tweak in tweak_section_match.get("hips"):
            hips_twist_md.outputX.drive(tweak.attr(twist_ax_attr))

    def _cleanup_bit(self):
        # Lock and Hide
        tweak_controls = [ctrl.control for ctrl in self.tweak_ctrls]
        for control in self.created_controls:
            if control in tweak_controls + [self.start_ctrl.control, self.start_ctrl.gimbal]:
                continue
            i_attr.lock_and_hide(node=control, attrs=["s"], lock=True, hide=True)
        
        # Parent the base joints into Pin group
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)
        self.base_joints[0].vis(0)
        # Not sure why original made these obsolete and used different joints or where they are deleted.
        # So I'm just hiding them instead
        i_utils.select(cl=True)

    def connect_elements(self):
        # Vis divider
        i_attr.create_divider_attr(node=self.ikfk_switch_control, ln="Vis")  # , en="Settings"

        # Drive visibility of some controls
        i_attr.create_vis_attr(node=self.ikfk_switch_control, ln="TweakCtrls", drive=self.tweak_grp)
        i_attr.create_vis_attr(node=self.ikfk_switch_control, ln=self.end_name + "Pivot", drive=self.pivot_ctrl.control_shapes)
        if self.is_neck:
            start_shapes = self.start_ctrl.control_shapes + self.start_ctrl.gimbal_shapes
            i_attr.create_vis_attr(node=self.ikfk_switch_control, ln="StartCtrl", drive=start_shapes, dv=0)
            end_shapes = self.end_ctrl.control_shapes + self.end_ctrl.gimbal_shapes
            i_attr.create_vis_attr(node=self.ikfk_switch_control, ln="EndCtrl", drive=end_shapes, dv=1)
        
        # Scaling
        if self.scale_attr:
            i_attr.connect_attr_3(self.scale_attr, self.tweak_grp.s)
            i_attr.connect_attr_3(self.scale_attr, self.pin_grp.s)


    def _create_bit(self):
        self.flip_shape = [0, 0, 0]
        if self.orient_joints[0] == "x":
            self.flip_shape = [0, 0, -90]
        
        if self.ctrl_count:  # Temp backwards compatibility - as described in __init__()
            self.ik_ctrl_count = self.ctrl_count
            self.fk_ctrl_count = self.ctrl_count

        self.twist_axis = self.orient_joints[0]

        # Create
        self.create_controls()
        self.create_ribbon()
        self.create_ikfk()
        self.create_spline()
        self.create_bind_joints()
        self.create_stretch_volume()
        self.create_twist()

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_pivot_control = pack_obj.pivot_ctrl.top_tfm
        pack_ikfk_switch_control = pack_obj.ikfk_switch_control
        pack_pin_grp = pack_obj.pin_grp
        
        # Stitch
        if parent_build_type == "Cog":
            # - Vars
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            # - Parent
            self.stitch_cmds.append({"parent": {"child": pack_pivot_control, "parent": parent_cog_gimbal}})
            # - Constrain
            self.stitch_cmds.append({"constrain": {"args": [parent_cog_gimbal, pack_ikfk_switch_control], "kwargs": {"mo": True, "as_fn": "parent"}}})
            self.stitch_cmds.append({"constrain": {"args": [parent_cog_gimbal, pack_pin_grp], "kwargs": {"mo": True, "as_fn": "parent"}}})
