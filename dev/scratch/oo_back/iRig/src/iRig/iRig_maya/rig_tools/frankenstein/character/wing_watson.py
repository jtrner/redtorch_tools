import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.deformers as rig_deformers
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Wing_Watson(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # self.number_feathers = 10  # This is just the length actually
        self.number_controls_per_feather = 4  #12
        
        self.orient_joints = "zxy"  # We're hacking together the chains in create_pack()
        self.joint_radius *= 2.0

        # Set the pack info
        self.joint_names = ["feather_Root"]
        self.side = "L"
        self.description = "Wing"
        self.length = 10
        self.base_joint_positions = ["incx3"]
        self.accepted_stitch_types = ["Arm", "Arm_Watson", "Wing_Watson"]

    def _class_prompts(self):
        self.prompt_info["number_controls_per_feather"] = {"type" : "int", "value" : self.number_controls_per_feather, "min" : 1, "max" : None}

    def _create_pack(self):
        # Turn off orienting joints so it doesn't auto-reorient after this point. We will be manually hacking.
        self.do_orient_joints = False
        
        # Define number of feathers based on base joint length
        self.number_feathers = len(self.base_joints)
        
        # Redefine some things from default joint creation
        # :note: If used mirroring, then these are already taken care of
        if not self.is_mirror:
            # - Rename joints the reverse number (so #1 becomes - ex - #4 and #4 becomes #1)
            # :note: Need to do this first
            # :note: Add Jnt suffix to keep unique naming
            new_root_names = [self.base_joints[len(self.base_joints) - i - 1] + "_Jnt" for i in range(len(self.base_joints))]
            for i, root_jnt in enumerate(self.base_joints):
                root_jnt.rename(new_root_names[i])
            # - Rotate entire chain so X points down where the child joints will be
            if self.do_pack_positions:
                self.base_joints[0].rz.set(-90)
        
        # Per-joint editing 
        all_base_joints = []
        self.base_joints_chains = []
        self.feather_root_joints = []
        self.feather_tip_joints = []
        for i, root_jnt in enumerate(self.base_joints):
            # - Unparent start joint
            if i != 0:
                root_jnt.set_parent(self.pack_grp)
            # - Now that renaming was done, remove the "_Jnt" suffix to not mess up name appends
            root_jnt.rename(root_jnt.replace("_Jnt", ""))
            # - Create / Find end joint
            if self.is_mirror:  # Joint will have been created through mirrorJoint()
                tip_jnt = root_jnt.relatives(0, c=True, type="joint")
                # root_jnt.rx.set(-90)
            else:
                i_utils.select(cl=True)  # yay maya
                tip_jnt = i_node.create("joint", n=root_jnt.replace("Root", "Tip"), radius=self.joint_radius)
                i_utils.select(cl=True)  # yay maya
                tip_jnt.radius.set(self.joint_radius)
                # - Parent / Position end joint
                tip_jnt.set_parent(root_jnt)
                if self.do_pack_positions:
                    tip_jnt.zero_out()
                    tip_jnt.tx.set(10)
                    # - Rotate to fix orientation
                    tip_jnt.ry.set(90)
            # - Include in base joints
            chn = [root_jnt, tip_jnt]
            all_base_joints += chn
            self.base_joints_chains.append(chn)
            self.feather_root_joints.append(root_jnt)
            self.feather_tip_joints.append(tip_jnt)
            # # - Freeze transforms
            # root_jnt.freeze(a=True, t=True, r=True, s=True, n=0, pn=1)
            # tip_jnt.freeze(a=True, t=True, r=True, s=True, n=0, pn=1)
        self.base_joints = all_base_joints
        self.base_joints_roots = self.feather_root_joints  # For the sake of mirroring to work, redefine
        if not self.is_mirror and self.do_pack_positions:
            for jnt in self.base_joints:
                jnt.freeze(a=True, t=True, r=True, s=True, n=0, pn=1)
        
        # Make it known that all new root joints are the top base joints
        i_node.connect_to_info_node(info_attribute="prep_top_base_joint", node=self.pack_info_node, objects=self.feather_root_joints)
        
        # Create Front / Back Surface
        self.front_surface = i_node.create("nurbsPlane", ch=False, ax=[0, 1, 0], w=10, lr=0.1, u=12, n=self.base_name + "_Fr_DRV_Surface")
        self.back_surface = i_node.create("nurbsPlane", ch=False, ax=[0, 1, 0], w=20, lr=0.05, u=6, n=self.base_name + "_Bk_DRV_Surface")
        
        # Set Nurbs Plane Attrs
        # :note: Don't change based on side_mult because then the number foll/number joint names don't match up.
        # self.front_surface.t.set([10, 0, 0])
        front_sx = -1 * (1.0 + (float(self.number_feathers) / float(len(self.base_joints))))
        self.front_surface.s.set([front_sx, 1, 1])
        # self.back_surface.t.set([12, 0, -12])
        self.back_surface.s.set([front_sx, 1, 1])
        
        # Position surfaces to match joints
        avg_start_position = i_utils.get_center_of_transforms(nodes=self.feather_root_joints)
        avg_end_position = i_utils.get_center_of_transforms(nodes=self.feather_tip_joints)
        self.front_surface.tx.set(avg_start_position[0][0])
        self.front_surface.tz.set(avg_start_position[0][2])
        self.back_surface.tx.set(avg_end_position[0][0])
        self.back_surface.tz.set(avg_end_position[0][2])
        
        # Create Feathers
        feather_store_names = self.create_pack_feathers()
        # - Constrain back to front
        # -- Match the numbers for joints to follicles:
        bk_feather_tips = sorted(self.bk_flc_grp.relatives(c=True, type="transform"), reverse=True)
        for i, bk_tip in enumerate(bk_feather_tips):
            i_constraint.constrain(bk_tip, self.feather_tip_joints[i], mo=False, as_fn="point")
        fr_feather_roots = sorted(self.fr_flc_grp.relatives(c=True, type="transform"), reverse=True)
        for i, fr_root in enumerate(fr_feather_roots):
            i_constraint.constrain(fr_root, self.feather_root_joints[i], mo=False, as_fn="parent") 
        # - Orient Joints
        rig_joints.orient_joints(joints=self.feather_root_joints, orient_as="yzx", up_axis="yup")
        self.do_orient_joints = False
        # - Cleanup
        self.pack_flc_grp = self._create_subgroup(name="Flc", children=[self.fr_flc_grp, self.bk_flc_grp]) 
        # Create Mid Surface
        self.mid_surface, mid_loft = i_node.create("loft", self.front_surface.relatives(0, s=True).attr("v[1]"),
                                                   self.back_surface.relatives(0, s=True).attr("v[0]"),
                                                   n=self.base_name + "_Md_DRV_Surface")
        mid_loft.rename(self.mid_surface + "_Loft")
        self.pack_mid_utl_grp = self._create_subgroup(name=self.mid_surface, add_base_name=False, parent=self.pack_utility_grp, 
                                                      children=[self.mid_surface, self.pack_flc_grp])
        
        # Parent
        i_utils.parent(self.front_surface, self.back_surface, self.pack_utility_grp)
        
        # Clear selection
        i_utils.select(cl=True)
    
        # Lock and hide channels for joints and surfaces, since these are only meant to be positioned by surface verts
        i_attr.lock_and_hide(node=self.front_surface, attrs="all", lock=True, hide=True)
        i_attr.lock_and_hide(node=self.mid_surface, attrs="all", lock=True, hide=True)
        i_attr.lock_and_hide(node=self.back_surface, attrs="all", lock=True, hide=True)
        # :note: Can't lock/hide here because it messes with mirror joints. :TODO: Make better way for lh base joint attrs
        # for jnt in self.base_joints:
        #     i_attr.lock_and_hide(node=jnt, attrs="all", lock=True, hide=True)
        
    def create_pack_feathers(self):
        # Vars
        self.fr_folls = []
        self.bk_folls = []
        feather_root_top_grps = []
        step = 1.0 / float(self.number_feathers)  # Must stay floats or else math rounds down to int
        u_val = 1.0 - (step / 2)
        
        feather_range = range(self.number_feathers)
        if self.is_mirror:
            feather_range = sorted(feather_range, reverse=True)
        
        # Create Follicles
        for i in feather_range:  # range(self.number_feathers)
            # - Vars
            name_num = "_%02d" % (self.number_feathers - i)
            # if self.is_mirror:
            #     name_num = "_%02d" % (i + 1)
            # - Front
            fr_foll = i_node.create_single_follicle(surface=self.front_surface, name=self.front_surface + name_num,
                                                           u_value=u_val, v_value=0.95)
            self.fr_folls.append(fr_foll)
            # - Back
            bk_foll = i_node.create_single_follicle(surface=self.back_surface, name=self.back_surface + name_num,
                                                           u_value=u_val, v_value=0.05)
            self.bk_folls.append(bk_foll)
            # - Update U Value
            u_val -= step
            # - Up Loc
            up_loc = i_node.create("locator", n=self.front_surface + name_num + "_Up_Loc")
            up_loc.v.set(0)
            up_loc.set_parent(fr_foll)
            up_loc.zero_out(s=False)
            up_loc.tz.set(-1)
            # Connect to Joints
            # - Get related Base Joints
            root_jnt = self.feather_root_joints[i]
            # - Create Top Groups
            offset_grp = i_node.create("group", root_jnt, n=root_jnt + "_Offset_Grp")
            i_node.copy_pose(root_jnt, offset_grp, "pivots")  # Move pivot from avg of root/tip to root
            # :note: Using create_zeroed_group or creating a transform, then parenting makes everything freak out when mirroring
            # offset_grp = root_jnt.create_zeroed_group(group_name=root_jnt + "_Offset", zero_out_created_group=False)
            aim_grp = offset_grp.create_zeroed_group(group_name=root_jnt + "_Aim", zero_out_created_group=False)
            cnx_grp = aim_grp.create_zeroed_group(group_name=root_jnt + "_Cns", zero_out_created_group=False)
            feather_root_top_grps.append(cnx_grp)
            # - Constrain
            i_constraint.constrain(fr_foll, cnx_grp, mo=True, as_fn="parent")
            i_constraint.constrain(bk_foll, aim_grp, mo=True, aim=[0, 1, 0], u=[0, 0, -1], wut="object", wuo=up_loc, as_fn="aim")
            # - Color
            root_jnt.overrideEnabled.set(1)
            if i == 0:
                root_jnt.overrideColor.set(14)
            else:
                root_jnt.overrideColor.set(6)
        
        # Cleanup
        self.fr_rig_grp = self._create_subgroup(name=self.front_surface + "_Rig", add_base_name=False, 
                                                children=feather_root_top_grps, parent=self.pack_rig_jnt_grp)
        self.fr_flc_grp = self._create_subgroup(name=self.front_surface + "_Flc", add_base_name=False,
                                                children=self.fr_folls)
        self.bk_flc_grp = self._create_subgroup(name=self.back_surface + "_Flc", add_base_name=False,
                                                children=self.bk_folls)
        
        # Return names of class variables to store in prepped
        return ["fr_folls", "bk_folls", "fr_rig_grp", "fr_flc_grp", "bk_flc_grp"]
    
    
    def create_bit_feathers(self):
        # Vars
        self.comb_jnts = []
        self.blend_jnts = {}
        self.master_ctrls = []
        self.blend_ctrls = []
        self.tip_point_constraints = []  # :note: Original deletes after loop, but that causes problems. Deleting long after.
        self.root_parent_constraints = []

        # Which feather rows get the master controls?
        master_feather_inds = [0, len(self.feather_root_joints) - 1]  # First and last feather
        master_feather_inds += range(0, len(self.feather_root_joints), 2)

        # Create
        prev_master = None
        prev_blend = None
        for i, root_jnt in enumerate(self.feather_root_joints):
            # Vars
            tip_jnt = root_jnt.relatives(0, c=True, type="joint")
            with_master = True if i in master_feather_inds else False
            # Delete constraint
            # i_attr.lock_and_hide(node=tip_jnt, attrs="all", unlock=True)
            tip_pc = tip_jnt.connections(type="pointConstraint", d=False)
            self.tip_point_constraints += tip_pc
            root_pac = root_jnt.connections(type="parentConstraint", d=False)
            self.root_parent_constraints += root_pac
            # Create Feathers
            feather_info = self.create_single_feather(root_jnt=root_jnt, master=with_master)
            bnd_jnt, master_ctrls, blend_ctrls = feather_info
            # Add to lists etc
            self.master_ctrls += master_ctrls
            self.blend_ctrls += blend_ctrls
            if with_master:
                self.comb_jnts.append(root_jnt)
                prev_master = root_jnt
            else:
                prev_blend = root_jnt
            if prev_blend:  # Have we only had masters up until now?
                if prev_blend not in self.blend_jnts.keys():  # Already know one master control
                    self.blend_jnts[prev_blend] = []
                if len(self.blend_jnts[prev_blend]) != 2:  # Cap out at 2 drivers
                    self.blend_jnts[prev_blend].append(prev_master)
            self.bind_joints.append(bnd_jnt)

    def create_single_feather(self, root_jnt=None, master=True):
        # Vars
        tip_jnt = root_jnt.relatives(0, c=True, type="joint")
        master_ctrls = []
        blend_ctrls = []
        base_name = root_jnt.name.replace("Fr_DRV_Surface_", "").replace("_Root", "_")
        
        # Create Joint Chain
        # - Dup
        dup_chain = rig_joints.duplicate_joints(joints=[root_jnt, tip_jnt], add_suffix="_")  # Add temp suffix to avoid warnings
        # - Insert
        inserted = rig_joints.insert_joints(from_joint=dup_chain[0], to_joint=dup_chain[1], 
                                            number_of_insertions=self.number_controls_per_feather)
        joints = [dup_chain[0]] + inserted + [dup_chain[1]]
        for i, jnt in enumerate(joints):
            jnt.rename(base_name + "_" + str(i + 1).zfill(2))
        
        # Create controls
        feather_parent = self.sub_ctrl_grp
        master_parent = self.bend_ctrl_grp
        for i in range(self.number_controls_per_feather):
            # - Vars
            constrain = True
            size = self.ctrl_size * 0.5
            if i == 0:  # Root
                constrain = False
                size = self.ctrl_size * 0.75
            # - Feather Ctrl
            feather_ctrl = i_node.create("control", control_type="2D Pin Circle", color=self.side_color_scndy,
                                         size=size, position_match=joints[i], name=joints[i], with_gimbal=False, parent=feather_parent,
                                         additional_groups=["Cns", "Driver"], with_cns_grp=False, constrain_geo=constrain, 
                                         scale_constrain=False, flip_shape=[90, 0, 0])
            blend_ctrls.append(feather_ctrl)
            feather_parent = feather_ctrl.last_tfm
            # -- Root control constrain/position
            if not constrain:  # Root
                i_constraint.constrain(root_jnt, feather_ctrl.top_tfm, mo=False, as_fn="parent")
                i_constraint.constrain(feather_ctrl.last_tfm, joints[0], mo=False, as_fn="parent")
            # - Master Feather Ctrl
            if master:
                master_feather_ctrl = i_node.create("control", control_type="2D Square", color=self.side_color,
                                                    size=size, position_match=joints[i], name=joints[i] + "_Bend", 
                                                    with_gimbal=False, parent=master_parent)
                master_ctrls.append(master_feather_ctrl)
                master_parent = master_feather_ctrl.last_tfm
                master_feather_ctrl.control.r.drive(feather_ctrl.driver_grp.r)
                master_feather_ctrl.control.t.drive(feather_ctrl.driver_grp.t)
                # - Drive First Bend
                if i == 0:  # Root
                    i_constraint.constrain(root_jnt, master_feather_ctrl.top_tfm, mo=False, as_fn="parent")
        
        # Return
        return [joints[0], master_ctrls, blend_ctrls]

    def blend_feather_chains(self):
        """Blend the chains together - the ones without the master controls being driven"""
        # Loop
        for blnd_root, master_roots in self.blend_jnts.items():
            # - Vars of Chain first joint (not just the Root/Tip chain, but the full joints)
            # :TODO: Get these in a not stupid way.
            blnd_root = i_node.Node(blnd_root.replace("_Root", "_") + "_01")
            master_roots[0] = i_node.Node(master_roots[0].replace("_Root", "_") + "_01")
            master_roots[1] = i_node.Node(master_roots[1].replace("_Root", "_") + "_01")
            # - Find full Chains
            blend_joints = blnd_root.relatives(ad=True, type="joint")[1:] + [blnd_root]
            master_a_joints = master_roots[0].relatives(ad=True, type="joint")[1:] + [master_roots[0]]
            master_b_joints = master_roots[1].relatives(ad=True, type="joint")[1:] + [master_roots[1]]
            # Blend
            for i in range(len(blend_joints)):
                # - Vars
                # :TODO: Get these in a not stupid way.
                blend_jnt = blend_joints[i]
                master_a_jnt = master_a_joints[i]
                master_b_jnt = master_b_joints[i]
                blend_dvr_grp = i_node.Node(blend_jnt.replace("Jnt", "Ctrl_Driver_Grp"))
                master_a_blend_ctrl = i_node.Node(master_a_jnt.replace("Jnt", "Blend_Ctrl"))
                master_b_blend_ctrl = i_node.Node(master_b_jnt.replace("Jnt", "Blend_Ctrl"))
                # -- Create Blend
                pb = i_node.create("pairBlend", n=blend_jnt.name.replace("Jnt", "Comb_Pb"))
                # -- Connect
                master_a_blend_ctrl.t.drive(pb.inTranslate1)
                master_a_blend_ctrl.r.drive(pb.inRotate1)
                master_b_blend_ctrl.t.drive(pb.inTranslate2)
                master_b_blend_ctrl.r.drive(pb.inRotate2)
                pb.outTranslate.drive(blend_dvr_grp.t)
                pb.outRotate.drive(blend_dvr_grp.r)
                # -- Set weight
                pb.weight.set(0.5)
        
        # return 
        
        
        # ### This is the original 1:1 migrated code, which doesn't do anything. Keeping here temporarily.
        # 
        # # Comb Joints
        # for i, current_jnt in enumerate(self.comb_jnts[:-1]):
        #     # Vars
        #     # - About this joint
        #     current_jnt_num = int(logic_py.find_numbers_in_string(string=current_jnt)[0])
        #     current_jnt_first = current_jnt.name.replace("Fr_DRV_Surface_", "").replace("Jnt", "01_Jnt")
        #     current_blend_jnt_chain = current_jnt_first.relatives(ad=True, type="joint")[1:] + [current_jnt_first]
        #     # - About next joint
        #     next_jnt = self.comb_jnts[i + 1]
        #     next_jnt_num = int(logic_py.find_numbers_in_string(string=next_jnt)[0])
        #     next_jnt_first = next_jnt.name.replace("Fr_DRV_Surface_", "").replace("Jnt", "01_Jnt")
        #     next_blend_jnt_chain = next_jnt_first.relatives(ad=True, type="joint")[1:] + [next_jnt_first]
        #     # - About numbers
        #     skip_count = next_jnt_num - current_jnt_num
        #     blend_skip = 1.0 / skip_count
        #     section_name = "_".join(current_jnt.name.replace("Fr_DRV_Surface_", "").replace("_Jnt", "").split("_")[:-1])
        #     section_root_jnts = []
        #     blend_step = blend_skip
        # 
        #     # Blend Joints
        #     for j in range(current_jnt_num + 1, next_jnt_num):
        #         # - Vars
        #         section_jnt_first = section_name + "_%02d_01_Jnt" % j
        #         section_root_jnts.append(section_jnt_first)
        #         blend_jnt_chain = section_jnt_first.relatives(ad=True, type="joint")[1:] + [section_jnt_first]
        #         # - Blend each joint
        #         for k, blend_jnt in enumerate(blend_jnt_chain):
        #             # -- Vars
        #             ctrl_dvr_grp = blend_jnt.name.replace("Jnt", "Ctrl_Driver_Grp")
        #             current_blend_ctrl = current_blend_jnt_chain[k].name.replace("Jnt", "Blend_Ctrl")
        #             next_blend_ctrl = next_blend_jnt_chain[k].name.replace("Jnt", "Blend_Ctrl")
        #             # -- Create Blend
        #             pb = i_node.create("pairBlend", n=blend_jnt.name.replace("Jnt", "Comb_Pb"))
        #             # -- Connect
        #             current_blend_ctrl.t.drive(pb.inTranslate1)
        #             current_blend_ctrl.r.drive(pb.inRotate1)
        #             next_blend_ctrl.t.drive(pb.inTranslate2)
        #             next_blend_ctrl.r.drive(pb.inRotate2)
        #             pb.outTranslate.drive(ctrl_dvr_grp.t)
        #             pb.outRotate.drive(ctrl_dvr_grp.r)
        #             # -- Set weight
        #             pb.weight.set(blend_step)
        # 
        #     # Increase steps
        #     blend_step += blend_skip
    
    
    def create_arm(self):
        # arm = Build_Arm_Watson(build_type=self.build_type, description=self.description, side=self.side)
        # arm.create_bit()
        # 
        # self.arm_base_joints = arm.base_joints
        
        # Create Palm joints
        i_utils.select(cl=True)  # Yay maya
        self.palm_jnt = i_node.create("joint", n=self.base_name + "_Wing_Palm", radius=self.joint_radius)
        i_utils.select(cl=True)  # Yay maya
        self.bind_joints.append(self.palm_jnt)
        self.palm_jnt.set_parent(self.pack_wing_rig_grp)
        # i_constraint.constrain(self.arm_base_joints[2], self.palm_jnt, mo=False, as_fn="parent")
        
        # Delete surface history
        i_utils.delete(self.back_surface, self.front_surface, history=True)
        
        # Skin
        # i_node.create("skinCluster", self.arm_base_joints, self.back_surface, n=self.back_surface + "_Skn", tsb=True, dr=8.5)
        # i_node.create("skinCluster", arm.upr_tweak_joints, arm.lwr_tweak_joints, self.palm_jnt, self.front_surface, n=self.front_surface + "_Skn")
    
    def create_ribbon(self):
        # Create Ribbon
        ribbon_info = rig_deformers.auto_ribbon_rig(object=self.back_surface, name=self.back_surface.name.replace("Root_", ""),
                                                    num_base_ctrl=5, num_sub_ctrl=1, driver=True, 
                                                    ctrl_colors=[self.side_color, self.side_color_scndy]) 
        main_ctrls, sub_ctrls, skin_mesh, back_ribbon_name, self.final_surface, ribbon_rig_grp, ribbon_utl_grp, \
        ribbon_ctrl_grp, ribbon_driver_surface_grp, self.back_surface_jnts = ribbon_info
        
        # Connect ribbon
        for flc in self.bk_folls:
            self.final_surface.relatives(0, s=True).local.drive(flc.relatives(0, s=True).inputSurface, f=True)
        
        # Connect visibility displays
        rig_attributes.create_dis_attr(ln=self.base_name + "_EdgeMain", drive=[ctrl.control for ctrl in main_ctrls], dv=1,
                                       node=self.wing_master_ctrl.control)
        rig_attributes.create_dis_attr(ln=self.base_name + "_EdgeSub", drive=[ctrl.control for ctrl in sub_ctrls], dv=1,
                                       node=self.wing_master_ctrl.control)
        rig_attributes.create_dis_attr(ln=self.base_name + "_FeatherMain", drive=[ctrl.control for ctrl in self.master_ctrls],
                                       node=self.wing_master_ctrl.control)
        rig_attributes.create_dis_attr(ln=self.base_name + "_FeatherSub", drive=[ctrl.control for ctrl in self.blend_ctrls],
                                       dv=2, node=self.wing_master_ctrl.control)
        
        # Parent
        ribbon_rig_grp.set_parent(self.pack_wing_rig_grp)
        ribbon_utl_grp.set_parent(self.pack_utility_grp)
        ribbon_ctrl_grp.set_parent(self.pack_ctrl_grp)
        ribbon_driver_surface_grp.set_parent(self.utility_grp)

    def create_controls(self):
        # Create
        fs = [0, 0, 0] if self.side_mult == 1 else [0, 180, 0]
        self.vis_ctrl = rig_controls.create_vis_control(use_existing=True)
        wing_master_control = i_node.create("transform", name="WingMaster_Ctrl", use_existing=True, parent=self.vis_ctrl.control)
        wing_master_shp = i_node.create("curve", control_type="2D Wing", color="pink", size=self.ctrl_size * 0.25,
                                        name=self.side + "_WingMaster", flip_shape=fs, parent=wing_master_control)
        wing_master_shp.zero_out()
        wing_master_shp.relatives(0, s=True).set_parent(wing_master_control, r=True, s=True)
        wing_master_shp.delete()
        self.wing_master_ctrl = i_control.mimic_control_class(control=wing_master_control)
        self.wing_master_ctrl.top_tfm.zero_out()
        
        # # Average position  # :note: Doesn't work well bc mirror packs. Figure it out. Maybe similar to eyes_master?
        # avg_start_position = i_utils.get_center_of_transforms(nodes=self.feather_root_joints)
        # dist_between = i_utils.get_single_distance(from_node=self.feather_root_joints[0], to_node=self.feather_tip_joints[0])
        # ctrl_t = [avg_start_position[0][0], self.base_joints[0].ty.get(), dist_between * -0.5]
        # self.wing_master_ctrl.top_tfm.t.set(ctrl_t)
    
    def create_slider_controls(self):
        # Create slider
        slider = i_node.create("control", control_type="slider", name=self.base_name + "Fold", slider_axis="y")
        self.slider_group = slider.slider_group
        
        # Position group
        i_node.copy_pose(driver=self.wing_master_ctrl.top_tfm, driven=self.slider_group, attrs="t")
        self.slider_group.xform(t=[-3 * self.pack_size, 0, 0], r=True, os=True)
        
        # Parent
        self.slider_group.set_parent(self.pack_ctrl_grp)
        
        # Create AnMoDriver
        an_mo_driver_grp = self._create_subgroup(name="AnMoDriver", add_base_name=False, parent=self.utility_grp, grp_suffix=False)
        fold_attr = i_attr.create(an_mo_driver_grp, ln=self.base_name + "Fold", dv=0, min=0, max=1, k=True)
        
        # Connect
        slider.control.ty.drive(fold_attr)

    def _cleanup_bit(self):
        # Parent
        i_utils.parent(self.bind_joints, self.pack_bind_jnt_grp)

    def connect_elements(self):
        # Create center curve for lofting
        md_loft_crv = i_node.duplicate(self.front_surface.relatives(0, s=True).attr("v[1]"), ch=False, n=self.base_name + "_Md_Loft_Crv", as_curve=True)[0]
        temp_curve = i_node.duplicate(self.final_surface.relatives(0, s=True).attr("v[0]"), ch=False, n=self.base_name + "_Md_TEMPBLEND_Crv", as_curve=True)[0]
        bs = i_node.create("blendShape", temp_curve, md_loft_crv)
        bs.w[0].set(0.5)
        i_utils.delete(md_loft_crv, history=True)
        temp_curve.delete()
        
        # # Loft
        # # :note: Was supposed to do stuff in original, but wasn't able to be finished
        # md_loft = i_node.create("loft", self.final_surface.relatives(0, s=True).attr("v[0]"), md_loft_crv, self.front_surface.relatives(0, s=True).attr("v[1]"), 
        #                   n=self.base_name + "_WingSurface")
        
        # Parent
        md_loft_crv.set_parent(self.pack_utility_grp) # md_loft, 
    
    def _presetup_bit(self):
        self.do_orient_joints = False

    def _create_bit(self):
        # Make sure number_controls_per_feather is int. UI will give float, even when specify int.
        self.number_controls_per_feather = int(self.number_controls_per_feather)

        # Create groups
        self.bend_ctrl_grp = self._create_subgroup(name="Bend_Ctrl", parent=self.pack_ctrl_grp)
        self.sub_ctrl_grp = self._create_subgroup(name="Sub_Ctrl", parent=self.pack_ctrl_grp)
        self.pack_wing_rig_grp = self._create_subgroup(name="Wing_Rig", parent=self.pack_rig_jnt_grp)

        # Create
        self.create_controls()
        self.create_bit_feathers()
        self.blend_feather_chains()
        # self.create_arm()
        self.create_ribbon()
        i_utils.delete(self.tip_point_constraints + self.root_parent_constraints)
        self.create_slider_controls()

        # Connect
        self.connect_elements()

    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # Vars
        driver_obj, mirror_obj = super(Build_Wing_Watson, self).mirror_pack(driver_info_node=driver_info_node, mirrored_info_node=mirrored_info_node)

        # Set class values
        self.number_controls_per_feather = driver_obj.number_controls_per_feather

        # Rest is only for symmetry
        if not symmetry:
            return

        # Blendshape Original > Mirror
        surface_match = {driver_obj.front_surface : mirror_obj.front_surface, 
                         driver_obj.back_surface : mirror_obj.back_surface}
        for orig_surf, mirr_surf in surface_match.items():
            bsh = i_node.create("blendShape", orig_surf, mirr_surf)
            bsh.w[0].set(1)
        
        # Connect follicle attrs
        # - Front
        for i in range(len(driver_obj.fr_folls)):
            orig_flc_shp = driver_obj.fr_folls[i].relatives(0, s=True)
            mirr_flc_shp = mirror_obj.fr_folls[i].relatives(0, s=True)
            orig_flc_shp.parameterU.drive(mirr_flc_shp.parameterU)
            orig_flc_shp.parameterV.drive(mirr_flc_shp.parameterV)
        # - Back
        for i in range(len(driver_obj.bk_folls)):
            orig_flc_shp = driver_obj.bk_folls[i].relatives(0, s=True)
            mirr_flc_shp = mirror_obj.bk_folls[i].relatives(0, s=True)
            orig_flc_shp.parameterU.drive(mirr_flc_shp.parameterU)
            orig_flc_shp.parameterV.drive(mirr_flc_shp.parameterV)
        
        # Clear selection
        i_utils.select(cl=True)

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_front_surface = pack_obj.front_surface
        pack_back_surface = pack_obj.back_surface
        pack_palm_jnt = pack_obj.palm_jnt
        pack_slider_grp = pack_obj.slider_group
        pack_wing_ctrl = pack_obj.wing_master_ctrl.control
        
        # WillWing L818 sets Driver, which may be same as "Parent"? to DRV[0],DRV[1],DRV[2]. DRV being given parameter.
        # If DRV is not given, uses ['L_UprArm','L_LwrArm','L_Wrist']
        # Cannot find in-code where that is used, so asked Will how wings are stitched to arms.
        # 1) Skin the front surface to the three arm joints
        # 2) Parent the wing fk controls & wing green sphere controls to joint of their corresponding arm section
        
        # There's also WillWing L592-607
        
        # Stitch
        if parent_build_type.startswith("Arm"):
            # Vars
            parent_base_joints = parent_obj.base_joints
            # Constrain palm joint
            self.stitch_cmds.append({"constrain": {"args": [parent_base_joints[-1], pack_palm_jnt], "kwargs": {"mo": False, "as_fn": "parent"}}})
            # Clean surfaces
            i_utils.delete(pack_front_surface, pack_back_surface, history=True)
            # Skin front surface
            back_skin = i_node.create("skinCluster", parent_base_joints, pack_back_surface, n=self.base_name + "_Bk_DRV_Skn")
            front_skin = i_node.create("skinCluster", parent_base_joints + [pack_palm_jnt], pack_front_surface, n=self.base_name + "_Fr_DRV_Skn")
            self.stitch_cmds.append({"unique" : {"cmd" : None,
                                                 "unstitch" : "i_utils.delete('%s', '%s')" % (front_skin, back_skin)}})
        
        elif parent_build_type == "Wing_Watson":
            # Vars
            parent_slider_grp = parent_obj.slider_group
            parent_wing_ctrl = parent_obj.wing_master_ctrl.control
            # Wing control
            # - Position wing controls in center
            avg_control_position = i_utils.get_average_position(from_node=parent_wing_ctrl, to_node=pack_wing_ctrl)
            parent_wing_ctrl.t.set(avg_control_position)
            pack_wing_ctrl.t.set(avg_control_position)
            pack_wing_cvs = pack_wing_ctrl.get_cvs()
            i_utils.xform(pack_wing_cvs, ro=[0, -180, 0], os=True)
            # :TODO: Add unstitchability ^
            # - Transfer Attrs
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_wing_ctrl, "to": parent_wing_ctrl, "ignore": None}})
            # - Combine shapes
            i_control.merge_shapes(curve_transforms=[pack_wing_ctrl, parent_wing_ctrl])
            # :TODO: Add unstitchability ^
            
            # Slider controls
            # - Position in center
            # - Translate down under wing control
            i_node.copy_pose(driver=parent_wing_ctrl, driven=[parent_slider_grp, pack_slider_grp])
            parent_slider_grp.xform(-2, -3, 0, os=True, r=True, as_fn="move")
            pack_slider_grp.xform(2, -3, 0, os=True, r=True, as_fn="move")
            # :TODO: Add unstitchability ^
