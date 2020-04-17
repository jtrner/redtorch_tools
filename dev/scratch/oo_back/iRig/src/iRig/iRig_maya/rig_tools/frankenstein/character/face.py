import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.face as rig_face

from rig_tools.frankenstein.core.master import Build_Master


class Build_Face(Build_Master):
    def __init__(self):
        super(Build_Face, self).__init__()
        
        self.do_orient_joints = False
        
        # Changeable
        self.number_inner_lip_jnts = 3
        self.number_outer_lip_jnts = 2
        self.number_naso_jnts = 4
        self.number_brow_jnts = 3
        self.number_inner_eyes = 3
        self.number_outer_eyes = 3

        # Set the pack info
        self.joint_radius = 1.01  # Just so it stays big
        self.description = "Face"
        self.side = ""
        self.restricted_sides = i_node.side_options  # Only no side. Individual things get their side manually
        self.base_joint_positions = []
        self.joint_names = []
        self.accepted_stitch_types = ["Head_Simple", "Head_Squash", "Cog"]
        # - Ear
        self.joint_names += ["L_Ear"]
        self.base_joint_positions += [[1.308, 9.171, -0.882]]
        # - Nose
        self.joint_names += ["C_Nose_Bridge", "C_Nose", "C_Nose_Tip", "L_Nose_Nostril"]
        self.base_joint_positions += [[0.0, 9.576, 1.106], [0.0, 9.175, 1.007], [0.0, 8.857, 1.487], [0.162, 8.882, 1.184]]
        # - Naso
        naso_positions = [[0.373, 9.109, 0.959], [0.701, 8.776, 0.877], [0.8, 8.343, 0.77], [0.682, 7.992, 0.76]]
        for i in range(self.number_naso_jnts):
            pos = [i, 2, 0] if i > len(naso_positions) else naso_positions[i]
            self.joint_names.append("L_Nose_Nasolabial_%s" % str(i + 1).zfill(2))
            self.base_joint_positions.append(pos)
        # - Mouth
        self.joint_names += ["C_Mouth_Teeth_Upr", "C_Mouth_Teeth_Lwr", "L_Mouth_Lip_Corner"]
        self.base_joint_positions += [[0.0, 8.379, 1.062], [0.0, 8.095, 0.991], [0.6, 8.233, 0.946]]
        # -- Inner Lips
        inner_lwr_lip_positions = [[0.123, 8.192, 1.164], [0.316, 8.189, 1.121], [0.493, 8.202, 1.023]]
        inner_upr_lip_positions = [[0.114, 8.328, 1.209], [0.322, 8.311, 1.158], [0.496, 8.279, 1.057]]
        for i in range(self.number_inner_lip_jnts):
            lwr_pos = [i, 0, 0] if i > len(inner_lwr_lip_positions) else inner_lwr_lip_positions[i]
            upr_pos = [i, 1, 0] if i > len(inner_upr_lip_positions) else inner_upr_lip_positions[i]
            str_i = str(i + 1).zfill(2)
            self.joint_names += ["L_Mouth_Lip_Upr_%s" % str_i, "L_Mouth_Lip_Lwr_%s" % str_i]
            self.base_joint_positions += [upr_pos, lwr_pos]
        # -- Outer Lips
        outer_lwr_lip_positions = [[0.142, 7.859, 1.132], [0.384, 7.87, 1.003]]
        outer_upr_lip_positions = [[0.182, 8.61, 1.186], [0.409, 8.581, 1.112]]
        for i in range(self.number_outer_lip_jnts):
            lwr_pos = [i, 0, 0] if i > len(outer_lwr_lip_positions) else outer_lwr_lip_positions[i]
            upr_pos = [i, 1, 0] if i > len(outer_upr_lip_positions) else outer_upr_lip_positions[i]
            str_i = str(i + 1).zfill(2)
            self.joint_names += ["L_Mouth_OuterLip_Upr_%s" % str_i, "L_Mouth_OuterLip_Lwr_%s" % str_i]
            self.base_joint_positions += [upr_pos, lwr_pos]
        # - Jaw and Chin
        self.joint_names += ["C_Jaw", "C_Chin", "L_Chin"]
        self.base_joint_positions += [[0.0, 8.444, -0.352], [0.0, 7.459, 1.076], [0.482, 7.515, 0.839]]
        # - Eye
        self.joint_names += ["L_Eye_Socket", "L_Eye_Lid_Inner", "L_Eye_Lid_Outer"]
        self.base_joint_positions += [[0.643, 9.698, 0.442], [0.337, 9.546, 0.747], [0.961, 9.607, 0.629]]
        # -- Inner
        inner_lwr_eye_positions = [[0.472, 9.512, 0.742], [0.679, 9.488, 0.759], [0.839, 9.524, 0.71]]
        inner_upr_eye_positions = [[0.407, 9.729, 0.819], [0.66, 9.769, 0.856], [0.849, 9.726, 0.798]]
        for i in range(self.number_inner_eyes):
            lwr_pos = [i, 3, 0] if i > len(inner_lwr_eye_positions) else inner_lwr_eye_positions[i]
            upr_pos = [i, 4, 0] if i > len(inner_upr_eye_positions) else inner_upr_eye_positions[i]
            str_i = str(i + 1).zfill(2)
            self.joint_names += ["L_Eye_Lid_Upr_%s" % str_i, "L_Eye_Lid_Lwr_%s" % str_i]
            self.base_joint_positions += [upr_pos, lwr_pos]
        # -- Outer
        outer_lwr_eye_positions = [[0.473, 9.344, 0.874], [0.681, 9.329, 0.846], [0.9, 9.352, 0.769]]
        outer_upr_eye_positions = [[0.368, 9.856, 0.967], [0.677, 9.881, 0.939], [0.95, 9.808, 0.766]]
        for i in range(self.number_outer_eyes):
            lwr_pos = [i, 5, 0] if i > len(outer_lwr_eye_positions) else outer_lwr_eye_positions[i]
            upr_pos = [i, 6, 0] if i > len(outer_upr_eye_positions) else outer_upr_eye_positions[i]
            str_i = str(i + 1).zfill(2)
            self.joint_names += ["L_Eye_OuterLid_Upr_%s" % str_i, "L_Eye_OuterLid_Lwr_%s" % str_i]
            self.base_joint_positions += [upr_pos, lwr_pos]
        # - Brow
        self.joint_names += ["L_Brow_Ridge"]
        self.base_joint_positions += [[0.102, 9.856, 1.055]]
        brow_positions = [[0.311, 10.042, 1.088], [0.701, 10.047, 1.006], [1.073, 9.907, 0.666]]
        for i in range(self.number_brow_jnts):
            pos = [i, 7, 0] if i > len(brow_positions) else brow_positions[i]
            self.joint_names.append("L_Brow_%s" % str(i + 1).zfill(2))
            self.base_joint_positions.append(pos)
        # - Cheek
        self.joint_names += ["L_Cheek_Bone", "L_Cheek", "L_Cheek_Upr_Fr", 
                             "L_Cheek_Upr_Bk", "L_Cheek_Lwr_Fr", "L_Cheek_Lwr_Bk"]
        self.base_joint_positions += [[0.926, 9.076, 0.788], [1.189, 8.592, 0.194], [1.046, 8.73, 0.58],
                                      [1.248, 9.189, 0.242], [1.028, 8.041, 0.28], [1.202, 8.295, -0.242]]
        
        # Figure out info from the names/positions
        self.length = len(self.joint_names)
        self.length_min = self.length
        self.length_max = self.length

    def _class_prompts(self):
        # Prompt Items
        self.prompt_info["Brow Count"] = {"kw": "number_brow_jnts", "type": "int", "value": self.number_brow_jnts, "min": 1}
        self.prompt_info["Inner Eye Count"] = {"kw": "number_inner_eyes", "type": "int", "value": self.number_inner_eyes, "min": 1}
        self.prompt_info["Outer Eye Count"] = {"kw": "number_outer_eyes", "type": "int", "value": self.number_outer_eyes, "min": 1}
        self.prompt_info["Naso Count"] = {"kw": "number_naso_jnts", "type": "int", "value": self.number_naso_jnts, "min": 1}
        self.prompt_info["Inner Lip Count"] = {"kw" : "number_inner_lip_jnts", "type" : "int", "value" : self.number_inner_lip_jnts, "min" : 1}
        self.prompt_info["Outer Lip Count"] = {"kw": "number_outer_lip_jnts", "type": "int", "value": self.number_outer_lip_jnts, "min": 1}
    
    def _create_pack(self):
        # Hack so all base joints are treated as chains so they can be parented to the "world" and mirroring doesn't error
        self.base_joints_chains = [[jnt] for jnt in self.base_joints]  # :note: chains are a list in lists
        self.base_joints_roots = self.base_joints
        
        # Parent to group so they all float loose
        for jnt in self.base_joints:
            jnt.set_parent(self.pack_grp)
        
        # Reset joint orients
        if self.do_pack_positions:
            for jnt in self.base_joints:
                jnt.zero_out(t=False, jo=True)
        
        # Mirror
        left_names_indexes = [i for i, name in enumerate(self.joint_names) if name.startswith("L_")]
        self.left_base_joints = [self.base_joints[i] for i in left_names_indexes]
        # - Do Mirroring
        self.mirror_sym_nodes = []
        self.right_base_joints = []
        for l_jnt in self.left_base_joints:
            r_jnt = l_jnt.mirror(sr=["L_", "R_"])[0]
            self.right_base_joints.append(r_jnt)
            # - Mimic symmetry attach
            sym_nd = i_node.create("multiplyDivide", n="%s_T_Mirror_Symmetry_Md" % r_jnt, use_existing=True)
            self.mirror_sym_nodes.append(sym_nd)
            sym_nd.input2X.set(-1)
            for ax in ["x", "y", "z"]:
                l_jnt.attr("t" + ax).drive(sym_nd.attr("input1%s" % ax.upper()))
                sym_nd.attr("output%s" % ax.upper()).drive(r_jnt + ".t" + ax, raise_error=False)
            l_jnt.radius.drive(r_jnt.radius)
            for o_attr in ["overrideEnabled", "overrideDisplayType"]:
                r_jnt.attr(o_attr).set(1)
        
        # Combine base and right joints
        self.bind_joints = self.base_joints + self.right_base_joints

        # Clearer class variables from the base joints
        self.base_joints_ear = [jnt for jnt in self.bind_joints if "_Ear_" in jnt or jnt.endswith("_Ear")]
        self.base_joints_nose = [jnt for jnt in self.bind_joints if "_Nose_" in jnt or jnt.endswith("_Nose")]
        self.base_joints_mouth = [jnt for jnt in self.bind_joints if "_Mouth_" in jnt or jnt.endswith("_Mouth")]
        self.base_joints_jaw = [jnt for jnt in self.bind_joints if "_Jaw_" in jnt or jnt.endswith("_Jaw")]
        self.base_joints_chin = [jnt for jnt in self.bind_joints if "_Chin_" in jnt or jnt.endswith("_Chin")]
        self.base_joints_eye = [jnt for jnt in self.bind_joints if "_Eye_" in jnt or jnt.endswith("_Eye")]
        self.base_joints_brow = [jnt for jnt in self.bind_joints if "_Brow_" in jnt or jnt.endswith("_Brow")]
        self.base_joints_cheek = [jnt for jnt in self.bind_joints if "_Cheek_" in jnt or jnt.endswith("_Cheek")]

        # Group some of the bigger lists of joints
        nose_jnt_grp = self._create_subgroup(name="Nose_Joints", parent=self.pack_grp, children=self.base_joints_nose)
        mouth_jnt_grp = self._create_subgroup(name="Mouth_Joints", parent=self.pack_grp, children=self.base_joints_mouth)
        eye_jnt_grp = self._create_subgroup(name="Eye_Joints", parent=self.pack_grp, children=self.base_joints_eye)
        brow_jnt_grp = self._create_subgroup(name="Brow_Joints", parent=self.pack_grp, children=self.base_joints_brow)
        cheek_jnt_grp = self._create_subgroup(name="Cheek_Joints", parent=self.pack_grp, children=self.base_joints_cheek)
        self.pack_joint_subgroups = [nose_jnt_grp, mouth_jnt_grp, eye_jnt_grp, brow_jnt_grp, cheek_jnt_grp]

    def __detach_symmetry(self):
        i_utils.delete(self.mirror_sym_nodes)
        
        for i in range(len(self.left_base_joints)):
            left_jnt = self.left_base_joints[i]
            right_jnt = self.right_base_joints[i]
            i_utils.check_exists(left_jnt, raise_error=True)  # User accidentally deleted (AUTO-1406)
            i_utils.check_exists(right_jnt, raise_error=True)  # User accidentally deleted (AUTO-1406)
            left_jnt.radius.disconnect(right_jnt.radius)
            right_jnt.overrideDisplayType.set(0)
    
    def __check_in(self, opts_in_item=None, item_searching=None):
        for opt in opts_in_item:
            if opt in item_searching:
                return True
        return False
    
    def __create_tweak_controls(self):
        # Vars of controls to be identified
        self.jaw_ctrl = None
        self.nose_ctrl = None
        self.l_eye_socket_ctrl = None
        self.r_eye_socket_ctrl = None
        self.l_cheek_ctrl = None
        self.r_cheek_ctrl = None
        # last_inner_lip_name = "Mouth_Lip_<pos>_" + str(self.number_inner_lip_jnts).zfill(2)
        # last_outer_lip_name = "Mouth_OuterLip_<pos>_" + str(self.number_outer_lip_jnts).zfill(2)
        # last_naso_name = "Nasolabial_" + str(self.number_naso_jnts).zfill(2)
        # last_brow_name = "Brow_" + str(self.number_brow_jnts).zfill(2)
        # last_inner_eye_name = "Eye_Lid_<pos>_" + str(self.number_inner_eyes).zfill(2)
        # last_outer_eye_name = "Eye_OuterLid_<pos>_" + str(self.number_outer_eyes).zfill(2)
        self.l_naso_ctrls = []
        self.r_naso_ctrls = []
        self.l_mouth_corner_ctrl = None
        self.r_mouth_corner_ctrl = None

        lower_face_controls_opts = ["_Mouth_Lip_Lwr", "_Mouth_OuterLip_Lwr", "_Chin", "_Mouth_Teeth_Lwr"]
        self.lower_face_ctrls = []
        nose_controls_opts = ["_Nose_Tip", "_Nose_Nostril"]
        self.nose_ctrls = []
        self.l_eye_ctrls = []
        self.r_eye_ctrls = []
        cheek_controls_opts = ["_Cheek_Upr_Fr", "_Cheek_Upr_Bk", "_Cheek_Lwr_Fr", "_Cheek_Lwr_Bk"]
        l_cheek_opts = ["L" + opt for opt in cheek_controls_opts]
        r_cheek_opts = ["R" + opt for opt in cheek_controls_opts]
        # self.cheek_ctrls = []
        self.l_cheek_ctrls = []
        self.r_cheek_ctrls = []
        self.l_brow_ctrls = []
        self.r_brow_ctrls = []
        l_mouth_upr_ctrls = []
        l_mouth_lwr_ctrls = []
        r_mouth_upr_ctrls = []
        r_mouth_lwr_ctrls = []
        l_scndry_color_ctrls = []
        r_scndry_color_ctrls = []

        # Create Tweak Controls
        self.tweak_ctrls = []
        self.tweak_ctrl_grp = self._create_subgroup(name="Tweaks", parent=self.pack_ctrl_grp)
        for jnt in self.bind_joints:
            color = self.side_colors.get(jnt.replace(self.description + "_", "")[0])
            ctrl = i_node.create("control", control_type="3D Sphere", name=jnt + "_Tweak", color=color,
                                 with_gimbal=False, position_match=jnt, parent=self.tweak_ctrl_grp, constrain_geo=True,
                                 scale_constrain=True, size=self.ctrl_size * 0.25, 
                                 with_cns_grp=False, additional_groups=["Drv", "Cns"])
            self.tweak_ctrls.append(ctrl)
            # - Store in a Variable?
            if "C_Jaw" in jnt:
                self.jaw_ctrl = ctrl
            elif "C_Nose_Tweak" in ctrl.control:
                self.nose_ctrl = ctrl
            elif "L_Eye_Socket" in jnt:
                self.l_eye_socket_ctrl = ctrl
            elif "R_Eye_Socket" in jnt:
                self.r_eye_socket_ctrl = ctrl
            elif "L_Cheek_Tweak" in ctrl.control:
                self.l_cheek_ctrl = ctrl
            elif "R_Cheek_Tweak" in ctrl.control:
                self.r_cheek_ctrl = ctrl
            elif "L_Mouth_Lip_Corner" in jnt:
                self.l_mouth_corner_ctrl = ctrl
            elif "R_Mouth_Lip_Corner" in jnt:
                self.r_mouth_corner_ctrl = ctrl
            # - Store in a List?
            top = ctrl.top_tfm
            if self.__check_in(lower_face_controls_opts, top):
                self.lower_face_ctrls.append(ctrl)
            elif self.__check_in(nose_controls_opts, top):
                self.nose_ctrls.append(ctrl)
            elif "L_Eye_Lid" in top:
                self.l_eye_ctrls.append(ctrl)
            elif "R_Eye_Lid" in top:
                self.r_eye_ctrls.append(ctrl)
            elif "L_Nose_Nasolabial" in top:
                self.l_naso_ctrls.append(ctrl)
            elif "R_Nose_Nasolabial" in top:
                self.r_naso_ctrls.append(ctrl)
            elif self.__check_in(l_cheek_opts, top):
                self.l_cheek_ctrls.append(ctrl)
            elif self.__check_in(r_cheek_opts, top):
                self.r_cheek_ctrls.append(ctrl)
            elif "L_Brow" in top:
                self.l_brow_ctrls.append(ctrl)
            elif "R_Brow" in top:
                self.r_brow_ctrls.append(ctrl)

            if "L_Eye_Lid_Outer" in top or "L_Eye_Lid_Inner" in top:
                l_scndry_color_ctrls.append(ctrl.control)
            elif "R_Eye_Lid_Outer" in top or "R_Eye_Lid_Inner" in top:
                r_scndry_color_ctrls.append(ctrl.control)

            if "L_Mouth_Lip_Upr" in top:
                l_mouth_upr_ctrls.append(ctrl)
            elif "R_Mouth_Lip_Upr" in top:
                r_mouth_upr_ctrls.append(ctrl)
            elif "L_Mouth_Lip_Lwr" in top:
                l_mouth_lwr_ctrls.append(ctrl)
            elif "R_Mouth_Lip_Lwr" in top:
                r_mouth_lwr_ctrls.append(ctrl)

        # Change color of some
        i_control.set_color(controls=l_scndry_color_ctrls, color=self.side_scndry_colors.get("L"), override_default=True)
        i_control.set_color(controls=r_scndry_color_ctrls, color=self.side_scndry_colors.get("R"), override_default=True)

        # Parent some
        i_utils.parent([ctrl.top_tfm for ctrl in self.lower_face_ctrls] + 
                       [self.l_naso_ctrls[-1].top_tfm, self.r_naso_ctrls[-1].top_tfm], self.jaw_ctrl.last_tfm)
        i_utils.parent([ctrl.top_tfm for ctrl in self.nose_ctrls], self.nose_ctrl.last_tfm)
        i_utils.parent([ctrl.top_tfm for ctrl in self.l_eye_ctrls], self.l_eye_socket_ctrl.last_tfm)
        i_utils.parent([ctrl.top_tfm for ctrl in self.r_eye_ctrls], self.r_eye_socket_ctrl.last_tfm)
        
        # Constrain some
        # - Naso
        i_constraint.constrain(self.jaw_ctrl.last_tfm, self.l_naso_ctrls[-2].top_tfm, mo=True, as_fn="parent")
        i_constraint.constrain(self.jaw_ctrl.last_tfm, self.r_naso_ctrls[-2].top_tfm, mo=True, as_fn="parent")
        # - Cheek
        for l_cheek in self.l_cheek_ctrls:
            i_constraint.constrain(self.l_cheek_ctrl.last_tfm, l_cheek.top_tfm, mo=True, as_fn="parent")
        for r_cheek in self.r_cheek_ctrls:
            i_constraint.constrain(self.r_cheek_ctrl.last_tfm, r_cheek.top_tfm, mo=True, as_fn="parent")
        # - Mouth Corner
        i_constraint.constrain(self.jaw_ctrl.last_tfm, self.l_mouth_corner_ctrl.top_tfm, mo=True, as_fn="parent")
        i_constraint.constrain(self.jaw_ctrl.last_tfm, self.r_mouth_corner_ctrl.top_tfm, mo=True, as_fn="parent")

        # Create some extra groups
        # - Mouth groups
        self.mouth_tweak_groups = {}
        mouth_grps = {"C_Mid_Upr" : [l_mouth_upr_ctrls[0], r_mouth_upr_ctrls[0]],
                      "L_Upr" : [l_mouth_upr_ctrls[1], l_mouth_upr_ctrls[2]],
                      "R_Upr" : [r_mouth_upr_ctrls[1], r_mouth_upr_ctrls[2]],
                      "C_Mid_Lwr" : [l_mouth_lwr_ctrls[0], r_mouth_lwr_ctrls[0]],
                      "L_Lwr": [l_mouth_lwr_ctrls[1], l_mouth_lwr_ctrls[2]],
                      "R_Lwr": [r_mouth_lwr_ctrls[1], r_mouth_lwr_ctrls[2]],
                      }
        for desc, drivers in mouth_grps.items():
            # - Create
            drivers = [driver.top_tfm for driver in drivers]
            grp = i_node.create("transform", n=self.base_name + "_" + desc)
            offset = grp.create_zeroed_group(group_name_add="Offset")
            # - Position
            i_node.copy_pose(driver=drivers, driven=offset)
            if not desc.startswith("C_"):
                aim = i_constraint.constrain(drivers[1], offset, as_fn="aim")
                aim.delete()
            # - Parent
            if desc.endswith("_Upr"):
                par = drivers[0].relatives(0, p=True)
                offset.set_parent(par)
            else:
                offset.set_parent(self.jaw_ctrl.last_tfm)
            i_utils.parent(drivers, grp)
            # - Add to attr
            self.mouth_tweak_groups[desc.lower()] = {"offset" : offset, "grp" : grp}

    def __create_side_gui(self, side=None, kws=None, size=None, size_sm=None):
        # Vars
        sbn = self.base_name + "_" + side
        side_mult = -1.0 if side == "R" else 1.0
        side_ctrls = {}
        side_rot = None
        side_rot_45deg = [0, 0, -45 * side_mult]
        if side == "R":
            side_rot = [0, -180, 0]
            side_rot_45deg = [0, -180, -45 * side_mult]
        side_color = self.side_colors.get(side)
        side_color_secondary = self.side_scndry_colors.get(side)

        # Brow
        brow_ctrl = i_node.create("control", name=sbn + "_Brow", control_type="2D Pickle", color=17, r=side_rot, size=size * 0.7,
                                  lock_hide_attrs=["tz", "r", "s", "v"], t=[3.182 * side_mult, 4.331, 0], #scale_shape=[1.5, 1.0, 1.0],
                                  translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)
        brow_drop_kws = kws.copy()
        brow_drop_kws.update({"control_type" : "2D Drop", "color" : 13, "r" : side_rot, "size" : size * 0.7, "scale_shape" : [1.0, 1.3, 1.0],
                              "lock_hide_attrs" : ["tz", "rx", "ry", "s", "v"], "translate_limits" : [[-1.0, 1.0], [-1.0, 1.0], None],
                              "rotate_limits" : [None, None, [-90.0, 90.0]]})
        brow_in_ctrl = i_node.create("control", name=sbn + "_Brow_In", t=[2.124 * side_mult, 4.412, 0], **brow_drop_kws)
        brow_mid_ctrl = i_node.create("control", name=sbn + "_Brow_Mid", t=[3.177 * side_mult, 4.473, 0], **brow_drop_kws)
        brow_out_ctrl = i_node.create("control", name=sbn + "_Brow_Out", t=[4.231 * side_mult, 4.003, 0], **brow_drop_kws)
        # - Add
        side_ctrls.update({"brow_ctrl" : brow_ctrl, "brow_in_ctrl" : brow_in_ctrl, 
                           "brow_mid_ctrl" : brow_mid_ctrl, "brow_out_ctrl" : brow_out_ctrl})
        
        # Blink Slider
        slider_x = 11.0 if side == "L" else 7.0
        blink_ctrl = i_node.create("control", name=sbn + "_Eye_Blink", control_type="slider", slider_axis="xy", color=17,
                                   t=[slider_x, 1.536, 0], size=1.0, text=side + " Blink", **kws)
        i_utils.xform(blink_ctrl.control.get_cvs(), [1.5, 1.5, 1.5], as_fn="scale", r=True)
        # :TODO: Add the below slider functionality into the Control._create_slider
        # - Shift so control "starts at 0.25"
        i_utils.xform(blink_ctrl.slider_cage, blink_ctrl.slider_title, [0, -0.25, 0], as_fn="move", r=True, os=True)
        blink_ctrl.control.set_limits(ty=[-0.25, 0.75])
        # - Add additional line marker
        cage_cv_pos = [cv.xform(as_fn="pointPosition") for cv in [blink_ctrl.slider_cage.cv[0], blink_ctrl.slider_cage.cv[1]]]
        cage_line = i_node.create("curve", d=1, p=cage_cv_pos, parent=blink_ctrl.slider_group, n=blink_ctrl.slider_cage + "_Line")
        cage_line.fix_shape_names()
        cage_line.xform([0, 0.25, 0], r=True, as_fn="move")
        cage_line.set_display("Reference")
        # - Cp
        blink_ctrl.slider_group.xform(cp=True)
        # - Add
        side_ctrls["blink_ctrl"] = blink_ctrl
        
        # EyeLids
        lid_kws = kws.copy()
        lid_kws.update({"lock_hide_attrs" : ["tx", "tz", "rx", "ry", "s", "v"], 
                        "translate_limits" : [[-1.0, 1.0], None, None], "rotate_limits" : [None, None, [-90, 90]],
                        "size" : size_sm * 0.9, "color" : 9, "control_type" : "2D Drop", "r" : side_rot})
        for pos in ["upr", "lwr"]:
            # - Update vars
            ty = 2.898 if pos == "upr" else 1.512
            ty_lim = [-1.0, 0.25] if pos == "upr" else [-0.25, 1.0]
            lid_kws.get("translate_limits")[1] = ty_lim
            lid_fs = [0, 0, 180] if pos == "upr" else None
            lid_kws["flip_shape"] = None if pos == "upr" else [0, 0, 180]
            # - Name
            ctrl_pfx = "Eye_Lid_%s" % pos.capitalize()
            pfx = ctrl_pfx.lower()
            ctrl_pfx = sbn + "_" + ctrl_pfx
            # - Make controls
            lid_ctrl = i_node.create("control", name=ctrl_pfx, control_type="2D SmoothTrapezoid", color=27, size=size * 0.7,  # "2D SmoothRectangle"
                                     lock_hide_attrs=["tz", "r", "s", "v"], t=[2.846 * side_mult, ty, 0],
                                     translate_limits=[[-1.0, 1.0], ty_lim, None], flip_shape=lid_fs, **kws)
            lid_in_ctrl = i_node.create("control", name=ctrl_pfx + "_In", t=[2.038 * side_mult, ty, 0], **lid_kws)
            lid_mid_ctrl = i_node.create("control", name=ctrl_pfx + "_Mid", t=[2.865 * side_mult, ty, 0], **lid_kws)
            lid_out_ctrl = i_node.create("control", name=ctrl_pfx + "_Out", t=[3.692 * side_mult, ty, 0], **lid_kws)
            # - Add
            side_ctrls.update({pfx + "_ctrl" : lid_ctrl, pfx + "_in_ctrl" : lid_in_ctrl,
                               pfx + "_mid_ctrl" : lid_mid_ctrl, pfx + "_out_ctrl" : lid_out_ctrl})
        
        # Face Center
        nostril_ctrl = i_node.create("control", name=sbn + "_Nostril", control_type="2D TiltedSquare", color=9, r=side_rot, size=size,
                                     lock_hide_attrs=["tz", "r", "s", "v"], t=[0.735 * side_mult, -1.145, 0],
                                     translate_limits=[[0.0, 1.0], [-1.0, 1.0], None], **kws)
        squint_ctrl = i_node.create("control", name=sbn + "_Squint", control_type="2D StarTrekBadge", color=17, r=side_rot_45deg, size=size,
                                    lock_hide_attrs=["tx", "tz", "r", "s", "v"], t=[2.75 * side_mult, -0.25, 0], 
                                    translate_limits=[None, [-1.0, 1.0], None], **kws)
        cheek_ctrl = i_node.create("control", name=sbn + "_Cheek", control_type="2D Boomerang", color=17, r=side_rot, size=size,
                                   lock_hide_attrs=["ty", "tz", "r", "s", "v"], t=[4.198 * side_mult, -1.6, 0],
                                   translate_limits=[[-1.0, 1.0], None, None], **kws)
        # - Add
        side_ctrls.update({"nostril_ctrl" : nostril_ctrl, "squint_ctrl" : squint_ctrl, "cheek_ctrl" : cheek_ctrl})
        
        # Mouth
        lip_kws = kws.copy()
        lip_kws.update({"lock_hide_attrs": ["tx", "tz", "rx", "ry", "s", "v"],
                        "translate_limits": [None, [-1.0, 1.0], None], "rotate_limits": [None, None, [-90, 90]],
                        "size": size_sm, "color": 13, "control_type": "2D Drop", "r": side_rot})
        lip_upr_ctrl = i_node.create("control", name=sbn + "_Mouth_LipUpr", t=[1.436 * side_mult, -3.03, 0], **lip_kws)
        lip_lwr_ctrl = i_node.create("control", name=sbn + "_Mouth_LipLwr", t=[1.436 * side_mult, -4.83, 0], flip_shape=[0, 0, 180], **lip_kws)
        mouth_corner_ctrl = i_node.create("control", name=sbn + "_Mouth_Corner", control_type="2D Corner", color=13, r=side_rot, size=size,
                                          lock_hide_attrs=["tz", "r", "s", "v"], t=[2.723 * side_mult, -3.916, 0],
                                          translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)
        mouth_corner_pinch_ctrl = i_node.create("control", name=sbn + "_Mouth_CornerPinch", control_type="2D CornerPinch", color=17, r=side_rot, size=size,
                                                lock_hide_attrs=["ty", "tz", "r", "s", "v"], t=[2.723 * side_mult, -3.916, 0],
                                                translate_limits=[[-1.0, 1.0], None, None], move_shape=[1.0, 0, 0], **kws)
        # - Lip Curl Sliders
        # :note: Some slight hacking because it's two slider controls with 1 text/cage setup
        lip_curl_slider_ctrl = i_node.create("control", name=sbn + "_LipCurl", control_type="slider", slider_axis="y",
                                             color=side_color_secondary, text="Lip Curl", size=1.5, parent=kws.get("parent"))
        # -- Hack edit the created slider's control
        lip_curl_lwr_control = lip_curl_slider_ctrl.control
        lip_curl_lwr_control.set_limits(ty=[-1.5, 1.5])
        lip_curl_lwr_control.rename(lip_curl_lwr_control.replace("_LipCurl", "_LipCurl_Lwr"))
        i_control.replace_shape(transform=lip_curl_lwr_control, new_shape="2D SmoothTrapezoid")
        # -- Create lower control
        lip_slider_kws = kws.copy()
        lip_slider_kws.update({"with_offset_grp" : False, "parent" : lip_curl_slider_ctrl.slider_group})
        upr_limits = lip_curl_lwr_control.get_limits()
        lip_curl_upr_ctrl = i_node.create("control", name=sbn + "_LipCurl_Upr_Slider", control_type="2D SmoothTrapezoid", size=0.7 * 1.5,
                                          color=side_color, translate_limits=[upr_limits.tx, upr_limits.ty, upr_limits.tz],
                                          position_match=lip_curl_lwr_control, flip_shape=[180, 0, 0],
                                          lock_hide_attrs=["tx", "tz", "r", "s", "v"], **lip_slider_kws)
        setattr(lip_curl_slider_ctrl, "upr_ctrl", lip_curl_upr_ctrl)
        setattr(lip_curl_slider_ctrl, "lwr_control", lip_curl_lwr_control)
        # -- Make controls way smaller and offset positions
        upr_cvs = lip_curl_upr_ctrl.control.get_cvs()
        lwr_cvs = lip_curl_lwr_control.get_cvs()
        slider_cvs = upr_cvs + lwr_cvs
        i_utils.xform(slider_cvs, [0.3, 0.6, 0.3], as_fn="scale", r=True)
        i_utils.xform(upr_cvs, [0, 0.3, 0], as_fn="move", r=True)
        i_utils.xform(lwr_cvs, [0, -0.3, 0], as_fn="move", r=True)
        lip_curl_slider_ctrl.slider_cage.ty.set(-0.5)  # Centers between the controls
        lip_curl_slider_ctrl.slider_title.xform([0, 1.0, 0], as_fn="move", r=True)
        # -- Add "safe zone" cage
        safe_zone_cage = lip_curl_slider_ctrl.slider_cage.duplicate(name_sr=["_Cage", "_Safety_Cage"])[0]
        safe_zone_cage.set_display("Template")
        setattr(lip_curl_slider_ctrl, "slider_safe_cage", safe_zone_cage)
        safe_zone_cage.xform([0.7, 2.0, 0.7], as_fn="scale", r=True)
        # -- Expand real cage
        lip_curl_slider_ctrl.slider_cage.xform([1, 3.0, 1], as_fn="scale", ws=True, r=True)
        # -- If mirrored side
        if side == "R":
            # - Have only one title
            lip_curl_slider_ctrl.slider_title.delete()
            # - Offset the slider setup
            i_utils.xform(lip_curl_slider_ctrl.slider_group, [-1.2, 0, 0], r=True, as_fn="move")

        # - Add
        side_ctrls.update({"lip_upr_ctrl" : lip_upr_ctrl, "lip_lwr_ctrl" : lip_lwr_ctrl, "mouth_corner_ctrl" : mouth_corner_ctrl,
                           "mouth_corner_pinch_ctrl" : mouth_corner_pinch_ctrl, "lip_curl_slider" : lip_curl_slider_ctrl})

        # Templated "moved" markers
        template_curves_grp = self._create_subgroup(name=side + "_TemplateCurves")
        # - Lines
        for line_ctrl in [squint_ctrl, mouth_corner_pinch_ctrl]:
            i_control.create_template_limits_line(control=line_ctrl.control, parent=template_curves_grp)
        # - Dupe curves
        for dupe_ctrl in [nostril_ctrl]:
            dupe = dupe_ctrl.control.duplicate(name_sr=["_Ctrl", "_Template_Crv"])[0]
            dupe.set_display("Template")
            # dupe.set_parent(template_curves_grp)  # :note: don't do this because then the curve jumps
        # - Add
        side_ctrls["template_curves_grp"] = template_curves_grp

        # Return
        return i_utils.Mimic(side_ctrls)
    
    def __create_gui(self):
        # Vars
        size = 1.0 #self.ctrl_size
        size_sm = 0.75 * size
        
        # Create an overall parent group
        self.gui_control_group = self._create_subgroup(name="Gui_Controls", parent=self.pack_ctrl_grp)
        
        # Across-the-board kwargs
        kws = {"with_gimbal" : False, "with_cns_grp" : False, "promote_rotate_order" : False, "parent" : self.gui_control_group,
               "tags" : ["no_mirror"]}

        # Nose
        nose_ctrl = i_node.create("control", name=self.base_name + "_C_Nose", control_type="2D Nose", 
                                  color=9, size=size, lock_hide_attrs=["tz", "r", "s", "v"], t=[0, 0.186, 0],
                                  translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)

        # Jaw / Chin
        jaw_ctrl = i_node.create("control", name=self.base_name + "_C_Jaw", control_type="2D SmoothRectangle", 
                                 color=6, size=size, lock_hide_attrs=["tz", "r", "s", "v"], t=[0, -3.88, 0],
                                 translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], move_shape=[0, -2.578, 0], **kws)

        # Mouth
        lip_kws = kws.copy()
        lip_kws.update({"lock_hide_attrs": ["tx", "tz", "rx", "ry", "s", "v"],
                        "translate_limits": [None, [-1.0, 1.0], None], "rotate_limits": [None, None, [-90, 90]],
                        "size": size_sm, "color": 13, "control_type": "2D Drop"})
        c_lip_upr_ctrl = i_node.create("control", name=self.base_name + "_C_Mouth_LipUpr", t=[0, -2.833, 0], **lip_kws)
        c_lip_lwr_ctrl = i_node.create("control", name=self.base_name + "_C_Mouth_LipLwr", t=[0, -4.96, 0], flip_shape=[0, 0, 180], **lip_kws)
        c_lip_mv_ctrl = i_node.create("control", name=self.base_name + "_C_Lip_Move", control_type="2D InnerMouth", 
                                      color=13, size=size * 4.0, lock_hide_attrs=["tz", "rx", "ry", "s", "v"], t=[0, -3.88, 0],
                                      translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], rotate_limits=[None, None, [-45, 45]],
                                      scale_shape=[1.0, 2.0, 1.0], **kws)
        c_lip_upr_mv_ctrl = i_node.create("control", name=self.base_name + "_C_Mouth_LipUpr_Move", control_type="2D Lip", 
                                          color=17, size=size, lock_hide_attrs=["tz", "r", "s", "v"], t=[0, -2.833, 0],
                                          translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)
        c_lip_lwr_mv_ctrl = i_node.create("control", name=self.base_name + "_C_Mouth_LipLwr_Move", control_type="2D SmoothTrapezoid", 
                                          color=17, size=size, lock_hide_attrs=["tz", "r", "s", "v"], t=[0, -4.96, 0],
                                          translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)
        # - Teeth
        c_teeth_upr_ctrl = i_node.create("control", name=self.base_name + "_C_Teeth_Upr", control_type="2D Teeth Upper",
                                         color="white", size=size, t=[13.0, -5.1, 0], **kws)
        c_teeth_lwr_ctrl = i_node.create("control", name=self.base_name + "_C_Teeth_Lwr", control_type="2D Teeth Lower",
                                         color="white", size=size, t=[13.0, -5.1, 0], **kws)
        # - Mouth Sliders
        jaw_slider_ctrl = i_node.create("control", name=self.base_name + "_C_Jaw", control_type="slider", slider_axis="x",
                                        color="red", size=1.0, text="Jaw", t=[8.27, 0.25, 0], **kws)
        lip_slider_ctrl = i_node.create("control", name=self.base_name + "_C_LipSync", control_type="slider", slider_axis="xy",
                                        color="red", size=1.0, text="Lip Sync", t=[8.27, -1.936, 0], **kws)
        tongue_slider_ctrl = i_node.create("control", name=self.base_name + "_C_Tongue", control_type="slider", slider_axis="xy",
                                           color="red", size=1.0, text="Tongue", t=[8.27, -4.925, 0], **kws)
        # -- Change the limits and default [0, 0] representation
        for slider in [lip_slider_ctrl, tongue_slider_ctrl, jaw_slider_ctrl]:
            slider.control.set_limits(tx=[-1, 1], ty=[-1, 1])
            sc = [2, 2, 1] if slider in [lip_slider_ctrl, tongue_slider_ctrl] else [2, 1, 1]
            slider.slider_cage.xform(sc, as_fn="scale", r=True)
            i_node.copy_pose(driver=slider.control, driven=slider.slider_cage, attrs="t", use_object_pivot=True)
            slider.slider_title.xform([-0.5, 0, 0], as_fn="move", r=True)
            slider.slider_group.xform(cp=True)
            i_utils.xform(slider.control.get_cvs(), [1.5, 1.5, 1.5], as_fn="scale", r=True)
        # -- Add the extra controls for the tongue
        tongue_slider_extra_kws = kws.copy()
        tongue_slider_extra_kws.update({"parent" : tongue_slider_ctrl.slider_group,  # "position_match" : tongue_slider_ctrl.control,
                                        "size" : 0.3, "control_type" : "2D Circle", "flip_shape" : [90, 0, 0],
                                        "color" : "yellow", "translate_limits" : [[-1, 1], [-1, 1], None]})
        tongue_ty_ctrl = i_node.create("control", name=self.base_name + "_C_Tongue_UpDown",
                                       lock_hide_attrs=["tx", "tz", "r", "s", "v"], **tongue_slider_extra_kws)  # , t=[-1, 0, 0]
        tongue_ty_ctrl.top_tfm.zero_out()
        tongue_ty_ctrl.top_tfm.tx.set(-1)
        tongue_tx_ctrl = i_node.create("control", name=self.base_name + "_C_Tongue_Stretch",
                                       lock_hide_attrs=["ty", "tz", "r", "s", "v"], **tongue_slider_extra_kws)  # , t=[0, -1, 0]
        tongue_tx_ctrl.top_tfm.zero_out()
        tongue_tx_ctrl.top_tfm.ty.set(-1)

        # Brow
        brow_ctrl = i_node.create("control", name=self.base_name + "_C_Brow", control_type="2D SmoothStar", color=6, 
                                  size=size, lock_hide_attrs=["tz", "r", "s", "v"], #t=[0, 2.815, 0],
                                  translate_limits=[[-1.0, 1.0], [-1.0, 1.0], None], **kws)
        
        # Combine center controls into a side var
        c_gui_ctrls = {"nose_ctrl": nose_ctrl, "jaw_ctrl": jaw_ctrl,
                       "lip_upr_ctrl": c_lip_upr_ctrl, "lip_lwr_ctrl": c_lip_lwr_ctrl,
                       "lip_mv_ctrl": c_lip_mv_ctrl, "lip_upr_mv_ctrl": c_lip_upr_mv_ctrl,
                       "lip_lwr_mv_ctrl" : c_lip_lwr_mv_ctrl, "brow_ctrl" : brow_ctrl,
                       "teeth_upr_ctrl" : c_teeth_upr_ctrl, "teeth_lwr_ctrl" : c_teeth_lwr_ctrl,
                       "lip_slider_ctrl" : lip_slider_ctrl, "tongue_slider_ctrl" : tongue_slider_ctrl,
                       "jaw_slider_ctrl" : jaw_slider_ctrl}
        self.c_gui_ctrls = i_utils.Mimic(c_gui_ctrls)

        # Side Controls
        self.l_gui_ctrls = self.__create_side_gui(side="L", kws=kws, size=size, size_sm=size_sm)
        self.r_gui_ctrls = self.__create_side_gui(side="R", kws=kws, size=size, size_sm=size_sm)
        template_groups = [self.l_gui_ctrls.template_curves_grp, self.r_gui_ctrls.template_curves_grp]
        lr_ctrls = [self.l_gui_ctrls, self.r_gui_ctrls]

        # Parent templates (first to group so it gets repositioned like the rest, then to main control)
        i_utils.parent(template_groups, self.gui_control_group)

        # Position overall
        i_node.copy_pose(self.base_joints_jaw, self.gui_control_group, attrs="t")
        self.gui_control_group.xform([7.0 * self.pack_size, 0, 0], r=True, os=True, as_fn="move")

        # Position brow between brows
        i_node.copy_pose(driver=[self.l_gui_ctrls.brow_ctrl.top_tfm, self.r_gui_ctrls.brow_ctrl.top_tfm], driven=brow_ctrl.top_tfm, attrs="t")
        
        # Position sliders
        # - Eyes
        # -- Get tx based on other sliders
        i_node.copy_pose(driver=c_teeth_upr_ctrl.top_tfm, driven=self.l_gui_ctrls.blink_ctrl.slider_group, attrs="t", use_object_pivot=True)
        i_node.copy_pose(driver=jaw_slider_ctrl.slider_group, driven=self.r_gui_ctrls.blink_ctrl.slider_group, attrs="t", use_object_pivot=True)
        l_eye_slider_tx = self.l_gui_ctrls.blink_ctrl.slider_group.tx.get()
        r_eye_slider_tx = self.r_gui_ctrls.blink_ctrl.slider_group.tx.get()
        # -- Get ty based on eyes
        i_node.copy_pose(driver=self.l_gui_ctrls.eye_lid_upr_ctrl.top_tfm, driven=self.l_gui_ctrls.blink_ctrl.slider_group, attrs="t")
        i_node.copy_pose(driver=self.r_gui_ctrls.eye_lid_upr_ctrl.top_tfm, driven=self.r_gui_ctrls.blink_ctrl.slider_group, attrs="t")
        # -- Finalize position
        self.l_gui_ctrls.blink_ctrl.slider_group.tx.set(l_eye_slider_tx)
        self.r_gui_ctrls.blink_ctrl.slider_group.tx.set(r_eye_slider_tx)
        # -- Group
        eye_sliders = [ctrls.blink_ctrl.slider_group for ctrls in lr_ctrls]
        slider_eye_grp = self._create_subgroup(name="Eye_Slider_Controls", children=eye_sliders)
        slider_eye_grp.xform(cp=True)
        # - Lip Curls
        # -- Subgroup
        lip_sliders = [ctrls.lip_curl_slider.slider_group for ctrls in lr_ctrls]
        slider_lip_grp = self._create_subgroup(name="Lip_Slider_Controls", children=lip_sliders)
        slider_lip_grp.xform(cp=True)
        # -- Position title equally above both L and R sliders
        lip_slider_title = self.l_gui_ctrls.lip_curl_slider.slider_title
        lip_title_ty = lip_slider_title.ty.get()
        lip_curl_controls = [ctrls.lip_curl_slider.upr_ctrl.control for ctrls in lr_ctrls]
        lip_curl_controls += [ctrls.lip_curl_slider.lwr_control for ctrls in lr_ctrls]
        i_node.copy_pose(driver=lip_curl_controls, driven=lip_slider_title, attrs="t", use_object_pivot=True)
        lip_slider_title.ty.set(lip_title_ty)
        lip_slider_title.set_parent(slider_lip_grp)  # Directly under main group since it's not side-specific
        # -- Position whole group to the side
        slider_lip_grp.xform(cp=True)
        slider_lip_grp_ty = slider_lip_grp.ty.get()
        i_node.copy_pose(driver=[c_teeth_upr_ctrl.top_tfm, c_teeth_lwr_ctrl.top_tfm], driven=slider_lip_grp, attrs="t", use_object_pivot=True)
        slider_lip_grp.ty.set(slider_lip_grp_ty - 1.0)
        slider_lip_grp.xform([0.75, 0.75, 0.75], as_fn="scale", r=True)
        # - Parent
        # :note: Need to do this for scale/positioning before put it under the control
        i_utils.parent(slider_eye_grp, slider_lip_grp, self.gui_control_group)
        
        # Create an overall gui control
        self.gui_control_group.xform(cp=True)
        self.gui_ctrl = i_node.create("control", control_type="2D Square", name=self.base_name + "_Gui", with_gimbal=False, with_offset_grp=False,
                                      with_cns_grp=False, size=size * 7.5, lock_hide_attrs="all", parent=self.gui_control_group,
                                      position_match=self.gui_control_group, position_match_pivot="use_object_pivot",
                                      flip_shape=[90, 0, 0], scale_shape=[1.5 * size, 1, 1], color=self.side_color_scndy,
                                      )
        # - Parent controls under it
        for ctrls in [self.c_gui_ctrls, self.l_gui_ctrls, self.r_gui_ctrls]:
            side_ctrls = ctrls.__dict__
            for nm, ctrl in side_ctrls.items():
                if nm in ["blink_ctrl", "template_curves_grp"]:  # sliders, templates
                    continue
                ctrl.top_tfm.set_parent(self.gui_ctrl.last_tfm)
        slider_eye_grp.set_parent(self.gui_ctrl.last_tfm)
        i_utils.parent(template_groups, self.gui_ctrl.last_tfm)

        # Scale Overall
        # :note: Need to scale overall group rather than positioning/scaling indiv controls so transform limits don't make it travel too far
        gui_scale = self.pack_size * 0.5
        self.gui_control_group.xform([gui_scale, gui_scale, gui_scale], r=True, os=True, as_fn="scale")

        # Connect GUI
        self.__connect_gui()
    
    def __create_gui_follows(self, side_ctrls=None):
        follows = {}
        
        for k, ctrl in side_ctrls.__dict__.items():
            if k == "template_curves_grp":
                continue
            follow_tfm = i_node.create("transform", n=ctrl.control + "_AutoFollow_Tfm", parent=ctrl.control)
            follow_tfm.zero_out()
            follows[k] = follow_tfm
        
        return i_utils.Mimic(follows)

    def __connect_gui(self):
        # Vars
        c_ctrls = self.c_gui_ctrls
        l_ctrls = self.l_gui_ctrls
        r_ctrls = self.r_gui_ctrls
        # all_gui_ctrls = self.c_gui_ctrls.__dict__.values() + self.l_gui_ctrls.__dict__.values() + self.r_gui_ctrls.__dict__.values()

        # Create Follows
        c_follows = self.__create_gui_follows(self.c_gui_ctrls)
        l_follows = self.__create_gui_follows(self.l_gui_ctrls)
        r_follows = self.__create_gui_follows(self.r_gui_ctrls)
        
        # Side controls
        for side_ctrls, side_follows in {l_ctrls : l_follows, r_ctrls : r_follows}.items():
            # - Parenting
            i_utils.parent(side_ctrls.lip_lwr_ctrl.top_tfm, side_ctrls.mouth_corner_ctrl.top_tfm, c_ctrls.jaw_ctrl.last_tfm)
            i_utils.parent(side_ctrls.lip_upr_ctrl.top_tfm, c_ctrls.lip_mv_ctrl.last_tfm)
            side_ctrls.mouth_corner_pinch_ctrl.top_tfm.set_parent(c_ctrls.jaw_ctrl.last_tfm)
            side_follows.nostril_ctrl.set_parent(c_follows.nose_ctrl)
            side_follows.lip_upr_ctrl.set_parent(c_follows.lip_upr_mv_ctrl)
            side_follows.lip_lwr_ctrl.set_parent(c_follows.lip_lwr_mv_ctrl)
            i_utils.parent(side_follows.brow_in_ctrl, side_follows.brow_mid_ctrl, side_follows.brow_out_ctrl, side_follows.brow_ctrl)
            i_utils.parent(side_follows.eye_lid_upr_in_ctrl, side_follows.eye_lid_upr_mid_ctrl, side_follows.eye_lid_upr_out_ctrl, side_follows.eye_lid_upr_ctrl)
            i_utils.parent(side_follows.eye_lid_lwr_in_ctrl, side_follows.eye_lid_lwr_mid_ctrl, side_follows.eye_lid_lwr_out_ctrl, side_follows.eye_lid_lwr_ctrl)
            # - Constraints
            i_constraint.constrain(side_ctrls.mouth_corner_ctrl.last_tfm, side_ctrls.mouth_corner_pinch_ctrl.top_tfm, as_fn="point", mo=True)
            for ctrl_follow in ["lip_upr_ctrl", "lip_lwr_ctrl", "brow_in_ctrl", "brow_mid_ctrl", "brow_out_ctrl",
                                "eye_lid_upr_in_ctrl", "eye_lid_upr_mid_ctrl", "eye_lid_upr_out_ctrl", 
                                "eye_lid_lwr_in_ctrl", "eye_lid_lwr_mid_ctrl", "eye_lid_lwr_out_ctrl", "nostril_ctrl"]:
                follow, ctrl = getattr(side_follows, ctrl_follow), getattr(side_ctrls, ctrl_follow)
                i_constraint.constrain(follow, ctrl.top_tfm, as_fn="point")
            # - Additional controls
            self.__gui_extra_rot(control=side_ctrls.eye_lid_upr_ctrl.control, follow_parent=side_follows.eye_lid_upr_ctrl)
            self.__gui_extra_rot(control=side_ctrls.eye_lid_lwr_ctrl.control, follow_parent=side_follows.eye_lid_lwr_ctrl)

        # Center controls
        # - Parenting
        i_utils.parent(c_ctrls.lip_upr_mv_ctrl.top_tfm, c_ctrls.lip_upr_ctrl.top_tfm, c_ctrls.jaw_ctrl.top_tfm, c_ctrls.lip_mv_ctrl.last_tfm)
        i_utils.parent(c_ctrls.lip_lwr_ctrl.top_tfm, c_ctrls.lip_lwr_mv_ctrl.top_tfm, c_ctrls.jaw_ctrl.last_tfm)
        c_follows.lip_lwr_ctrl.set_parent(c_follows.lip_lwr_mv_ctrl)
        c_follows.lip_upr_ctrl.set_parent(c_follows.lip_upr_mv_ctrl)
        # - Constraints
        for ctrl_follow in ["lip_upr_ctrl", "lip_lwr_ctrl"]:
            follow, ctrl = getattr(c_follows, ctrl_follow), getattr(c_ctrls, ctrl_follow)
            i_constraint.constrain(follow, ctrl.top_tfm, as_fn="point")
        # - Additional controls
        self.__gui_extra_rot(control=c_ctrls.lip_upr_mv_ctrl.control, follow_parent=c_follows.lip_upr_mv_ctrl)
        self.__gui_extra_rot(control=c_ctrls.lip_lwr_mv_ctrl.control, follow_parent=c_follows.lip_lwr_mv_ctrl)

    def __connect_gui_tweaks(self):
        # Eyes and Brows
        for side in ["L", "R"]:
            gui_ctrls = self.l_gui_ctrls if side == "L" else self.r_gui_ctrls
            eye_tweak_ctrls = getattr(self, "%s_eye_ctrls" % side.lower())
            eye_tweak_upr_ctrls = [ctrl for ctrl in eye_tweak_ctrls if "Upr" in ctrl.control]
            eye_tweak_lwr_ctrls = [ctrl for ctrl in eye_tweak_ctrls if "Lwr" in ctrl.control]
            brow_ctrls = [ctrl for ctrl in getattr(self, "%s_brow_ctrls" % side.lower()) if "Ridge" not in ctrl.control]

            gui_tweak_con = {"eye_lid_upr_in_ctrl": eye_tweak_upr_ctrls[0],
                             "eye_lid_upr_mid_ctrl": eye_tweak_upr_ctrls[1],
                             "eye_lid_upr_out_ctrl": eye_tweak_upr_ctrls[2],
                             "eye_lid_lwr_in_ctrl": eye_tweak_lwr_ctrls[0],
                             "eye_lid_lwr_mid_ctrl": eye_tweak_lwr_ctrls[1],
                             "eye_lid_lwr_out_ctrl": eye_tweak_lwr_ctrls[2],
                             "brow_in_ctrl": brow_ctrls[0],
                             "brow_mid_ctrl": brow_ctrls[1],
                             "brow_out_ctrl": brow_ctrls[2],
                             }

            with_mult = True if side == "R" else False

            for gui_attr, tweak_ctrl in gui_tweak_con.items():
                gui_control = getattr(gui_ctrls, gui_attr).control
                driver = gui_control.rz
                if with_mult:
                    md = i_node.create("multiplyDivide", n="%s_%s_%s_Neg_Md" % (self.base_name, side, gui_attr))
                    driver.drive(md.input1X)
                    md.input2X.set(-1)
                    driver = md.outputX
                driver.drive(tweak_ctrl.cns_grp.rz)

        # Mouth
        for grp_desc in self.mouth_tweak_groups.keys():
            gui_ctrls = getattr(self, grp_desc[0].lower() + "_gui_ctrls")
            ctrl = getattr(gui_ctrls, "lip_%s_ctrl" % grp_desc.split("_")[-1].lower())
            grp = self.mouth_tweak_groups.get(grp_desc).get("grp")
            ctrl.control.rz.drive(grp.rz)

        # Vis
        i_attr.create_vis_attr(node=self.gui_ctrl.control, ln="OnFaceCtrl", drive=self.tweak_ctrl_grp)

    def __gui_extra_rot(self, control=None, follow_parent=None):
        control_type = i_control.get_curve_type(control=control)
        control_shape = control.relatives(0, s=True)
        control_color = i_control.get_color(control_shape=control_shape)
        blend_ctrl = i_node.create("control", name=control.replace("_Ctrl", "_Blend_Crv"), control_type=control_type,
                                   color=control_color, with_gimbal=False, with_offset_grp=False, with_cns_grp=False,
                                   parent=follow_parent, position_match=control, connect=False, match_convention_name=False)
        i_control.match_points(driver_shape=control_shape, driven_shape=blend_ctrl.control_shapes[0])
        blend_ctrl.control.freeze()

        fv = {-0.5: 45, 0: 0, 0.5: -45} if "Upr" in control else {-0.5: -45, 0: 0, 0.5: 45}

        anm_crv = self.__gui_anim_curve(sect_name=control.replace("_Ctrl", "_Rot"), fv=fv)
        control.tx.drive(anm_crv.input)
        anm_crv.output.drive(follow_parent.rz)

        bsh = i_node.create("blendShape", blend_ctrl.control, control, n=control + "_Bsh", origin="world")
        # - Turn on target
        bsh.attr(blend_ctrl.control).set(1)

        i_control.force_vis(blend_ctrl.control, v=0)

        return [blend_ctrl, anm_crv]

    def __create_drivers(self):
        # Vars
        self.driver_nulls = {}
        dirs = rig_face.get_face_directions()

        sect_attrs = {"Brow" : ["C_Brow_" + d for d in dirs.ud_dir + dirs.io_dir] + ["L_Brow_" + d for d in dirs.imo_udio_attrs] + ["R_Brow_" + d for d in dirs.imo_udio_attrs],
                      "Upr_Blink" : ["L_Blink_Upr_" + d for d in dirs.imo_ud_attrs] + ["R_Blink_Upr_" + d for d in dirs.imo_ud_attrs],
                      "Lwr_Blink": ["L_Blink_Lwr_" + d for d in dirs.imo_ud_attrs] + ["R_Blink_Lwr_" + d for d in dirs.imo_ud_attrs],
                      "Nose" : ["C_Nose_" + d for d in dirs.ud_dir + dirs.lr_dir] + ["L_Nostril_" + d for d in dirs.ud_dir + ["Flare"]] +
                               ["R_Nostril_" + d for d in dirs.ud_dir + ["Flare"]],
                      "Cheeks" : ["L_Squint_" + d for d in dirs.ud_dir] + ["R_Squint_" + d for d in dirs.ud_dir] +
                                 ["L_Cheek_" + d for d in dirs.io_dir] + ["R_Cheek_" + d for d in dirs.io_dir],
                      "Mouth" : ["C_Lips_Move_" + d for d in dirs.ud_dir + dirs.lr_dir] + ["C_Lips_Roll_" + d for d in dirs.lr_dir] +
                                ["C_Jaw_Move_" + d for d in dirs.ud_dir + dirs.lr_dir],
                      "Lips" : ["C_Lips_Upr_" + d for d in dirs.ud_dir] + ["L_Lips_Upr_" + d for d in dirs.ud_dir] + ["R_Lips_Upr_" + d for d in dirs.ud_dir] +
                               ["C_Lips_Lwr_" + d for d in dirs.ud_dir] + ["L_Lips_Lwr_" + d for d in dirs.ud_dir] + ["R_Lips_Lwr_" + d for d in dirs.ud_dir] +
                               ["L_Lips_Corner_" + d for d in dirs.ud_dir + dirs.io_dir + ["Pinch", "Unpinch"]] + ["R_Lips_Corner_" + d for d in dirs.ud_dir + dirs.io_dir + ["Pinch", "Unpinch"]]
                      }
        
        # Create main group
        driver_grp = self._create_subgroup(name="ControlDriver", parent=self.pack_utility_grp)
        
        for sect in sorted(sect_attrs.keys()):
            # - Create transform
            driver = i_node.create("transform", n=sect + "_ControlDriver", parent=driver_grp)
            self.driver_nulls[sect] = driver
            # - LH default attrs
            i_attr.lock_and_hide(node=driver, attrs="all", lock=True, hide=True)
            # - Add attrs
            attrs = sect_attrs.get(sect)
            for s_at in attrs:
                i_attr.create(node=driver, ln=s_at, at="double", k=True)
        
        # Connect drivers
        self.__connect_drivers()
    
    def __four_way_driver(self, sect_name=None, driver_nd=None, ctrl=None, attr_prefix=None, attr_directions=None):
        # Vars
        if not sect_name.startswith(self.base_name + "_"):
            sect_name = self.base_name + "_" + sect_name
        control = ctrl.control
        driver_attrs = [driver_nd.attr(attr_prefix + "_" + d) for d in attr_directions]

        # Md
        md = i_node.create("multiplyDivide", n=sect_name + "_Md")
        md.input2X.set(-1)
        md.input2Y.set(-1)
        
        # Up/Down Clamp
        ud_clamp = i_node.create("clamp", n="%s_%s_Clamp" % (sect_name, "".join(attr_directions[:2])))
        ud_clamp.maxR.set(1)
        ud_clamp.maxG.set(1)
        
        # In/Out or Left/Right Clamp
        iolr_clamp = i_node.create("clamp", n="%s_%s_Clamp" % (sect_name, "".join(attr_directions[3:])))
        iolr_clamp.maxR.set(1)
        iolr_clamp.maxG.set(1)
        
        # Connect
        control.tx.drive(md.input1X)
        control.ty.drive(md.input1Y)
        control.ty.drive(ud_clamp.inputR)
        md.outputY.drive(ud_clamp.inputG)
        control.tx.drive(iolr_clamp.inputR)
        md.outputX.drive(iolr_clamp.inputG)
        ud_clamp.outputR.drive(driver_attrs[0])
        ud_clamp.outputG.drive(driver_attrs[1])
        iolr_clamp.outputR.drive(driver_attrs[2])
        iolr_clamp.outputG.drive(driver_attrs[3])
        
        # Return
        return [md, ud_clamp, iolr_clamp]
    
    def __small_driver(self, sect_name=None, ctrl=None, control_attr=None, driver_attrs=None, connect=True):
        # Vars
        if not sect_name.startswith(self.base_name + "_"):
            sect_name = self.base_name + "_" + sect_name
        control = ctrl.control
        
        # Md
        md = i_node.create("multiplyDivide", n=sect_name + "_Md")
        md.input2X.set(-1)
        
        # Clamp
        clamp = i_node.create("clamp", n=sect_name + "_Clamp")
        clamp.max.set([1, 1, 1])
        
        # Connect
        if connect:
            if not control_attr:
                control_attr = "ty"
            control.attr(control_attr).drive(clamp.inputR)
            control.attr(control_attr).drive(md.input1X)
            if driver_attrs[0]:
                clamp.outputR.drive(driver_attrs[0])
            if len(driver_attrs) > 1:
                md.outputX.drive(clamp.inputG)
                clamp.outputG.drive(driver_attrs[1])
            if len(driver_attrs) == 3:
                control.tx.drive(clamp.inputB)
                clamp.outputB.drive(driver_attrs[2])
        
        # Return
        return [md, clamp]
    
    def __gui_anim_curve(self, sect_name=None, fv=None):
        mid_anm = i_node.create("animCurveUU", n=sect_name + "_Mid_Anm")
        if not fv:
            fv = {-1 : 0.5, 0 : 1, 1 : 0.5}
        for f in sorted(fv.keys()):
            mid_anm.set_key(f=f, v=fv.get(f))
        for i in [0, 1, 2]:
            mid_anm.key_tangent(index=(i, i), inTangentType="linear", outTangentType="linear")
        
        return mid_anm
    
    def __connect_drivers(self):
        # Vars
        ud_dir = ["Up", "Down"]
        io_dir = ["Out", "In"]  # :note: Yes, needs to be reversed
        lr_dir = ["Left", "Right"]
        
        # C Brow
        self.__four_way_driver(sect_name="C_Brow", driver_nd=self.driver_nulls.get("Brow"), ctrl=self.c_gui_ctrls.brow_ctrl,
                               attr_prefix="C_Brow", attr_directions=ud_dir + io_dir)

        # C Nose
        self.__four_way_driver(sect_name="Nose", driver_nd=self.driver_nulls.get("Nose"), ctrl=self.c_gui_ctrls.nose_ctrl, 
                               attr_prefix="C_Nose", attr_directions=ud_dir + lr_dir)

        # C Mouth
        self.__four_way_driver(sect_name="Mouth", driver_nd=self.driver_nulls.get("Mouth"), ctrl=self.c_gui_ctrls.lip_mv_ctrl, 
                               attr_prefix="C_Lips_Move", attr_directions=ud_dir + lr_dir)

        # C Jaw
        self.__four_way_driver(sect_name="Jaw", driver_nd=self.driver_nulls.get("Mouth"), ctrl=self.c_gui_ctrls.jaw_ctrl, 
                               attr_prefix="C_Jaw_Move", attr_directions=ud_dir + lr_dir)
        
        # LR Nose
        driver_nd = self.driver_nulls.get("Nose")
        for side in ["L", "R"]:
            ctrl = self.l_gui_ctrls.nostril_ctrl if side == "L" else self.r_gui_ctrls.nostril_ctrl
            driver_attrs = [driver_nd.attr(side + "_Nostril_" + d) for d in ud_dir + ["Flare"]]
            self.__small_driver(sect_name=side + "_Nostril", ctrl=ctrl, driver_attrs=driver_attrs)

        # LR Brow
        driver_nd = self.driver_nulls.get("Brow")
        for side in ["L", "R"]:
            # - Vars
            sect_name = self.base_name + "_" + side + "_Brow"
            side_ctrls = self.l_gui_ctrls if side == "L" else self.r_gui_ctrls
            main_ctrl = side_ctrls.brow_ctrl
            main_control = main_ctrl.control
            # - Main
            main_md, main_clamp = self.__small_driver(sect_name=sect_name, ctrl=main_ctrl, connect=False)
            main_md.input2Y.set(-1)
            main_control.tx.drive(main_md.input1X)
            main_control.ty.drive(main_md.input1Y)
            main_md.outputX.drive(main_clamp.inputG)
            main_md.outputY.drive(main_clamp.inputR)
            # - Loop Subsections
            for subsect in ["In", "Mid", "Out"]:
                # - Vars
                subsect_name = sect_name + subsect
                ctrl = getattr(side_ctrls, "brow_" + subsect.lower() + "_ctrl")
                control = ctrl.control
                # - Create Nodes
                created = self.__four_way_driver(sect_name=subsect_name, driver_nd=driver_nd, ctrl=ctrl,
                                                 attr_prefix=side + "_Brow_" + subsect, attr_directions=ud_dir + io_dir)
                sub_md, ud_clamp, io_clamp = created
                # - Insert ADLs
                up_adl = i_node.create("addDoubleLinear", n=subsect_name + "_Up_Adl")
                dn_adl = i_node.create("addDoubleLinear", n=subsect_name + "_Down_Adl")
                in_adl = i_node.create("addDoubleLinear", n=subsect_name + "_In_Adl")
                out_adl = i_node.create("addDoubleLinear", n=subsect_name + "_Out_Adl")
                # - Connect ADLs
                control.tx.drive(out_adl.input1)
                control.ty.drive(up_adl.input1)
                sub_md.outputX.drive(in_adl.input1)
                sub_md.outputY.drive(dn_adl.input1)
                up_adl.output.drive(ud_clamp.inputR, f=True)
                dn_adl.output.drive(ud_clamp.inputG, f=True)
                in_adl.output.drive(io_clamp.inputG, f=True)
                out_adl.output.drive(io_clamp.inputR, f=True)
                main_control.ty.drive(up_adl.input2)
                main_control.tx.drive(out_adl.input2)
                main_clamp.outputR.drive(dn_adl.input2)
                main_clamp.outputG.drive(in_adl.input2)

        # LR Blinks
        for side in ["L", "R"]:
            # - Vars
            sect_name = self.base_name + "_" + side + "_Blink"
            side_ctrls = self.l_gui_ctrls if side == "L" else self.r_gui_ctrls
            # - Blink Nodes
            # -- Vars
            blink_control = side_ctrls.blink_ctrl.control
            # -- Nodes
            blink_remap = i_node.create("remapValue", n=sect_name + "_Remap")
            blink_control.ty.drive(blink_remap.inputValue)
            blink_remap.inputMin.set(-0.25)
            blink_remap.inputMax.set(0.75)
            blink_remap.outputMin.set(0)
            blink_remap.outputMax.set(1)
            blink_rev = i_node.create("reverse", n=sect_name + "_Rev")
            blink_control.tx.drive(blink_rev.inputX)
            blink_remap.outValue.drive(blink_rev.inputY)
            # - Lid Nodes
            input_vals = {"Upr" : {"Up" : 4, "Down" : -1}, "Lwr" : {"Up" : 1, "Down" : -4}}
            upr_end_clamp = None
            lwr_end_rev = None
            for ul in ["Upr", "Lwr"]:
                # -- Vars
                driver_nd = self.driver_nulls.get(ul + "_Blink")
                ul_control = getattr(side_ctrls, "eye_lid_%s_ctrl" % ul.lower()).control
                ul_out_control = getattr(side_ctrls, "eye_lid_%s_out_ctrl" % ul.lower()).control
                ul_in_control = getattr(side_ctrls, "eye_lid_%s_in_ctrl" % ul.lower()).control
                ul_mid_control = getattr(side_ctrls, "eye_lid_%s_mid_ctrl" % ul.lower()).control
                ul_sect_name = sect_name + "_" + ul
                # -- Blink Md
                ul_blink_md = i_node.create("multiplyDivide", n=ul_sect_name + "_Md")
                if ul == "Upr":
                    blink_control.tx.drive(ul_blink_md.input1X)
                    blink_rev.outputY.drive(ul_blink_md.input2X)
                else:
                    blink_remap.outValue.drive(ul_blink_md.input1X)
                    blink_control.tx.drive(ul_blink_md.input2X)
                # -- Reverse
                if ul == "Lwr":
                    lwr_end_rev = i_node.create("reverse", n=ul_sect_name + "_Rev")
                # -- Up/Down Nodes
                for ud in ["Up", "Down"]:
                    # --- Vars
                    ud_sect_name = ul_sect_name + "_" + ud
                    ud_inp_v = input_vals.get(ul).get(ud)
                    driver_attr_pfx = "%s_Blink_%s" % (side, ul)
                    # --- Val Md
                    ul_md = i_node.create("multiplyDivide", n=ud_sect_name + "_Val_Md")
                    ul_md.input2.set([2, -2, ud_inp_v])
                    ul_control.tx.drive(ul_md.input1X)
                    ul_control.tx.drive(ul_md.input1Y)  # yes, tx > in1Y
                    ul_control.ty.drive(ul_md.input1Z)  # yes, ty > in1Z
                    # --- IO Adls
                    ul_out_adl = i_node.create("addDoubleLinear", n=ud_sect_name + "_Out_Adl")
                    ul_md.outputX.drive(ul_out_adl.input1)
                    ul_out_adl.input2.set(1)
                    ul_in_adl = i_node.create("addDoubleLinear", n=ud_sect_name + "_In_Adl")
                    ul_md.outputY.drive(ul_in_adl.input1)
                    ul_in_adl.input2.set(1)
                    # --- Mid Anim
                    ul_mid_anm = self.__gui_anim_curve(sect_name=ud_sect_name)
                    ul_control.tx.drive(ul_mid_anm.input)
                    # --- Clamp
                    ul_clamp = i_node.create("clamp", n=ud_sect_name + "_Clamp")
                    ul_out_adl.output.drive(ul_clamp.inputR)
                    ul_in_adl.output.drive(ul_clamp.inputG)
                    ul_md.outputZ.drive(ul_clamp.inputB)
                    ul_clamp.max.set([1, 1, 1])
                    # --- IO Md
                    ul_io_md = i_node.create("multiplyDivide", n=ud_sect_name + "_InOut_Md")
                    ul_clamp.outputR.drive(ul_io_md.input1X)
                    ul_mid_anm.output.drive(ul_io_md.input1Y)
                    ul_clamp.outputG.drive(ul_io_md.input1Z)
                    i_attr.connect_attr_3(driving_attr=ul_clamp.outputB, driven_attr=ul_io_md.input2)
                    # --- Override Md
                    ul_ovd_md = i_node.create("multiplyDivide", n=ud_sect_name + "_Override_Md")
                    ul_io_md.outputX.drive(ul_ovd_md.input1X)
                    ul_io_md.outputY.drive(ul_ovd_md.input1Y)
                    ul_io_md.outputZ.drive(ul_ovd_md.input1Z)
                    i_attr.connect_attr_3(driving_attr=blink_rev.outputX, driven_attr=ul_ovd_md.input2)
                    # --- Sepr Md
                    ul_sepr_md = i_node.create("multiplyDivide", n=ud_sect_name + "_Sepr_Md")
                    ul_out_control.ty.drive(ul_sepr_md.input1X)
                    ul_mid_control.ty.drive(ul_sepr_md.input1Y)
                    ul_in_control.ty.drive(ul_sepr_md.input1Z)
                    ul_sepr_md.input2.set([ud_inp_v, ud_inp_v, ud_inp_v])
                    # --- End Clamp (part 1)
                    ul_end_clamp = i_node.create("clamp", n=ud_sect_name + "_End_Clamp")
                    if ul == "Upr":
                        upr_end_clamp = ul_end_clamp
                    # --- Out/Mid/In Pmas
                    for i, imo in enumerate(["Out", "Mid", "In"]):
                        xyz = ["X", "Y", "Z"][i]
                        rgb = ["R", "G", "B"][i]
                        pma = i_node.create("plusMinusAverage", n=ud_sect_name + "_" + imo + "_Pma")
                        inp_01 = (ul == "Upr" and ud == "Up") or (ul == "Lwr" and ud == "Down")
                        if inp_01:
                            ul_ovd_md.attr("output" + xyz).drive(pma + ".input1D[0]")
                            ul_sepr_md.attr("output" + xyz).drive(pma + ".input1D[1]")
                        else:
                            ul_blink_md.outputX.drive(pma + ".input1D[0]")
                            ul_sepr_md.attr("output" + xyz).drive(pma + ".input1D[1]")
                            ul_ovd_md.attr("output" + xyz).drive(pma + ".input1D[2]")
                        pma.output1D.drive(ul_end_clamp.attr("input" + rgb))
                    # --- End Clamp (part 2)
                    if ul == "Upr" or (ul == "Lwr" and ud == "Down"):
                        ul_end_clamp.max.set([1, 1, 1])
                    else:  # Lwr & Up
                        lwr_end_rev.outputX.drive(ul_end_clamp.maxR)
                        lwr_end_rev.outputY.drive(ul_end_clamp.maxG)
                        lwr_end_rev.outputZ.drive(ul_end_clamp.maxB)
                    ul_end_clamp.outputR.drive(driver_nd.attr(driver_attr_pfx + "_Out_" + ud))
                    ul_end_clamp.outputG.drive(driver_nd.attr(driver_attr_pfx + "_Mid_" + ud))
                    ul_end_clamp.outputB.drive(driver_nd.attr(driver_attr_pfx + "_In_" + ud))
            # - Connect upper and lower lids
            upr_end_clamp.outputR.drive(lwr_end_rev.inputX)
            upr_end_clamp.outputG.drive(lwr_end_rev.inputY)
            upr_end_clamp.outputB.drive(lwr_end_rev.inputZ)
            
        # Cheeks
        driver_nd = self.driver_nulls.get("Cheeks")
        for side in ["L", "R"]:
            # - Vars
            sect_name = self.base_name + "_" + side
            ctrls = self.l_gui_ctrls if side == "L" else self.r_gui_ctrls
            # - Squint
            self.__small_driver(sect_name=sect_name + "_Squint", ctrl=ctrls.squint_ctrl, control_attr="ty", 
                                driver_attrs=[driver_nd.attr(side + "_Squint_" + d) for d in ud_dir])
            # - Cheek
            self.__small_driver(sect_name=sect_name + "_Cheek", ctrl=ctrls.cheek_ctrl, control_attr="tx", 
                                driver_attrs=[driver_nd.attr(side + "_Cheek_" + d) for d in io_dir])
        
        # Upr/Lwr Lips
        driver_nd = self.driver_nulls.get("Lips")
        for ul in ["Upr", "Lwr"]:
            move_control = self.c_gui_ctrls.lip_upr_mv_ctrl.control if ul == "Upr" else self.c_gui_ctrls.lip_lwr_mv_ctrl.control
            lcr_ctrls = [self.l_gui_ctrls.lip_upr_ctrl, self.c_gui_ctrls.lip_upr_ctrl, self.r_gui_ctrls.lip_upr_ctrl] if ul == "Upr" \
                else [self.l_gui_ctrls.lip_lwr_ctrl, self.c_gui_ctrls.lip_lwr_ctrl, self.r_gui_ctrls.lip_lwr_ctrl]            
            for ud in ["Up", "Down"]:
                # - Vars
                sect_name = "C_Mouth_Lip" + ul + "_" + ud
                # - Create nodes
                val_md = i_node.create("multiplyDivide", n=sect_name + "_Val_Md")
                val_md.input2X.set(2)
                val_md.input2Y.set(-2)
                if ud == "Down":
                    val_md.input2Z.set(-1)
                main_l_adl = i_node.create("addDoubleLinear", n=sect_name + "_MainL_Adl")
                main_l_adl.input2.set(1)
                main_r_adl = i_node.create("addDoubleLinear", n=sect_name + "_MainR_Adl")
                main_r_adl.input2.set(1)
                main_clamp = i_node.create("clamp", n=sect_name + "_Clamp")
                main_clamp.max.set([1, 1, 1])
                mid_anm = self.__gui_anim_curve(sect_name=sect_name)
                main_lr_md = i_node.create("multiplyDivide", n=sect_name + "_MainLR_Md")
                sep_md = i_node.create("multiplyDivide", n=sect_name + "_Sepr_Md")
                if ud == "Down":
                    sep_md.input2.set([-1, -1, -1])
                end_clamp = i_node.create("clamp", n=sect_name + "_End_Clamp")
                end_clamp.max.set([1, 1, 1])
                # - Connect
                move_control.tx.drive(val_md.input1X)
                move_control.tx.drive(val_md.input1Y)
                move_control.tx.drive(mid_anm.input)
                move_control.ty.drive(val_md.input1Z)
                val_md.outputX.drive(main_l_adl.input1)
                val_md.outputY.drive(main_r_adl.input1)
                main_l_adl.output.drive(main_clamp.inputR)
                main_r_adl.output.drive(main_clamp.inputG)
                val_md.outputZ.drive(main_clamp.inputB)
                main_clamp.outputR.drive(main_lr_md.input1X)
                mid_anm.output.drive(main_lr_md.input1Y)
                main_clamp.outputG.drive(main_lr_md.input1Z)
                i_attr.connect_attr_3(driving_attr=main_clamp.outputB, driven_attr=main_lr_md.input2)
                # - Individual LCR controls
                for i, lcr in enumerate(["L", "C", "R"]):
                    # -- Vars
                    xyz = ["X", "Y", "Z"][i]
                    rgb = ["R", "G", "B"][i]
                    control = lcr_ctrls[i].control
                    driver_attr = lcr + "_Lips_" + ul + "_" + ud
                    # -- Nodes
                    indiv_adl = i_node.create("addDoubleLinear", n=sect_name + "_Indiv%s_Adl" % lcr)
                    main_lr_md.attr("output" + xyz).drive(indiv_adl.input1)
                    control.ty.drive(sep_md.attr("input1" + xyz))
                    sep_md.attr("output" + xyz).drive(indiv_adl.input2)
                    indiv_adl.output.drive(end_clamp.attr("input" + rgb))
                    end_clamp.attr("output" + rgb).drive(driver_nd.attr(driver_attr))
        
        # LR Mouth Corner/Pinch
        driver_nd = self.driver_nulls.get("Lips")
        for side in ["L", "R"]:
            # - Vars
            sect_name = self.base_name + "_" + side + "_Lip"
            driver_attr_pfx = side + "_Lips_Corner"
            ctrls = self.l_gui_ctrls if side == "L" else self.r_gui_ctrls
            # - Corner
            self.__four_way_driver(sect_name=sect_name + "Corner", driver_nd=driver_nd, ctrl=ctrls.mouth_corner_ctrl,
                                   attr_prefix=driver_attr_pfx, attr_directions=ud_dir + io_dir)
            # - Pinch
            self.__small_driver(sect_name=sect_name + "Pinch", ctrl=ctrls.mouth_corner_pinch_ctrl, control_attr="tx",
                                driver_attrs=[driver_nd.attr(driver_attr_pfx + "_Unpinch"), driver_nd.attr(driver_attr_pfx + "_Pinch")])

        # C Mouth Additional
        control = self.c_gui_ctrls.lip_mv_ctrl.control
        driver_nd = self.driver_nulls.get("Mouth")
        for side in ["L", "R"]:
            side_long = "Left" if side == "L" else "Right"
            tilt_remap = i_node.create("remapValue", n=self.base_name + "_C_MouthTilt_%s_Rmv" % side_long)
            tilt_remap.inputMax.set(-45 if side == "L" else 45)
            control.rz.drive(tilt_remap.inputValue)
            tilt_remap.outValue.drive(driver_nd.attr("C_Lips_Roll_" + side_long))

    def _cleanup_bit(self):
        i_utils.parent(self.pack_joint_subgroups, self.base_joints_ear, self.base_joints_chin, self.base_joints_jaw, 
                       self.pack_bind_jnt_grp)

    def _create_bit(self):
        color_info = i_node.get_default("CtrlColorSide")
        self.side_colors = {"C": color_info.get("center"), "L": color_info.get("left"), "R": color_info.get("right")}
        self.side_scndry_colors = {"C": color_info.get("center_secondary"), "L": color_info.get("left_secondary"),
                                   "R": color_info.get("right_secondary")}

        self.__detach_symmetry()
        self.__create_tweak_controls()
        self.__create_gui()
        self.__create_drivers()
        self.__connect_gui_tweaks()
    
    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        if parent_build_type.startswith("Head"):
            # Vars
            parent_end_control = parent_obj.ctrl.last_tfm

            # Drive head > tweak controls
            # - Vars
            pack_tweak_control_group = pack_obj.tweak_ctrl_grp
            pack_control_constraints = pack_tweak_control_group.relatives(ad=True, type="constraint")
            # - Add head control as constraint driver
            for pac in pack_control_constraints:
                info = pac.get_constraint_info()
                pac = i_constraint.constrain(parent_end_control, info.driven, as_fn=info.type, mo=True)
                # - Set all driver weights to 0.5
                i_constraint.set_constraint_influence(constraints=pac, value=0.5)
            # - Constrain the main control group
            i_constraint.constrain(parent_end_control, pack_tweak_control_group, as_fn="parent", mo=True)

            # Drive head > gui controls
            pack_gui_control = pack_obj.gui_ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_gui_control, "options": parent_end_control}})

        elif parent_build_type == "Cog":
            pack_gui_control = pack_obj.gui_ctrl.control
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            self.stitch_cmds.append({"follow": {"driving": pack_gui_control, "dv": parent_root_ctrl, "options": parent_root_ctrl}})
