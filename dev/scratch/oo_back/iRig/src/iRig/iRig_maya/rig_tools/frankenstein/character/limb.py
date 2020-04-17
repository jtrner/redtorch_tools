import pymel.core as pm
import collections

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints
import rig_tools.frankenstein.utils as rig_frankenstein_utils

from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.character.foot import Build_Foot


class Build_Limb_IkFk(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        self.pv_pos_mult = 1  #2
        self.create_buffer_joints = True
        self.create_world_switch = False
        self.offset_control_to_locator = False
        self.end_ctrl_wedge = False
        
        self.ikfk_switch_offset = [0, 0, 0.5]
        self.ikfk_switch_mirror_offset = False

        self.fk_rot_orders = [None, None, None, None]  # Allows it to be default - this is optional
        self.ik_rot_order = None  # Allows it to be default - this is optional

        self.right_side_fix = True
        self.right_side_fix_axis = "x"

        self.joints = []
        self.number_bend_joints = 5
        self.attach_joints = True
        self.auto_control_visibility = True
        self.buffer_joints = []
        self.is_quad = False

        self.bend_controls = []
        self.start_point_ctrl = None

        self.is_arm = False

        # Set the pack info
        self.joint_names = ["a", "b", "c", "d"]
        self.side = "L"
        self.description = "Limb"
        self.length = 3
        self.length_min = self.length
        self.length_max = 4
        self.base_joint_positions = [[0.41, 2.98, -0.14], #[18.6959, 46.0794, -2.27707],
                                     [0.46, 1.64, -0.22], #[18.3696, 32.5577, 5.14266],
                                     [0.5, 0.7, -0.31], #[18.0399, 19.0707, -9.5952],
                                     [0.5, 0.6, -0.31], #[17.6747, 3.7642, -5.0342],
                                    ] # :TODO: There isn't a quad position equivalent for TTM Leo yet. Will need eventually
        self.accepted_stitch_types = ["Clavicle", "Hip", "Cog", "Spine_Simple", "Spine_IkFk", "Head_Simple", "Head_Squash"]

    def _class_prompts(self):
        self.prompt_info["pv_pos_mult"] = {"type": "int", "value": self.pv_pos_mult, "min": None, "max": None}
        self.prompt_display_info["is_arm"] = "is_arm"

    def _stitch_pack(self):
        self.base_joints[0].joz.set(0)

    def _create_pack(self):
        # Zero out the mid joint(s)
        mid_jnts = self.base_joints[1:-1]
        
        jo_zeroed = ["x", "y", "z"]
        if self.orient_joints_up_axis == "zup":  # Leg
            jo_zeroed.remove("x")
        else:  # Arm
            jo_zeroed.remove("z")
        
        for jnt in mid_jnts:
            for axis in jo_zeroed:
                jnt.attr("jo" + axis).set(0)
    
    def _ik_setup(self):
        # Vars
        ik_jnt_tops = []
        follow_name = self.joint_names[2].capitalize()

        # Regular Ik
        self.ik_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Ik", end_index=len(self.base_joints))
        ik_jnt_tops.append(self.ik_joints[0])

        # Base Ik
        self.follow_end_origin_grp = self._create_subgroup(name="IkHdl_Follow_%s_Origin" % follow_name)
        ik_jnt_tops.append(self.follow_end_origin_grp)
        self.follow_end_offset_grp = self._create_subgroup(name="IkHdl_Follow_%s_Offset" % follow_name, parent=self.follow_end_origin_grp)
        if self.is_quad:
            self.ik_base_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Base_Ik", end_index=len(self.base_joints))
            ik_jnt_tops.append(self.ik_base_joints[0])
            self.base_ikh, self.base_eff = rig_joints.create_ikh_eff(start=self.ik_base_joints[0],
                                                                     end=self.ik_base_joints[-1],
                                                                     ikh_parent=self.follow_end_origin_grp
                                                                     )
        else:
            self.base_ikh, self.base_eff = rig_joints.create_ikh_eff(start=self.ik_joints[0],
                                                                     end=self.ik_joints[-1],
                                                                     ikh_parent=self.follow_end_origin_grp
                                                                     )
        i_node.copy_pose(driver=self.base_ikh, driven=self.follow_end_offset_grp)
        self.base_ikh.set_parent(self.follow_end_offset_grp)

        self.utility_vis_objs.append(self.base_ikh)

        # Sway Ik
        if self.is_quad:
            sway_start_jnt = self.base_joints[2].duplicate(n=self.base_joints[2] + "_Sway_Ik", parentOnly=True)[0]
            sway_start_jnt.set_parent(w=True)
            sway_end_jnt = self.base_joints[3].duplicate(n=self.base_joints[3] + "_Sway_Ik", parentOnly=True)[0]
            sway_end_jnt.set_parent(w=True)
            self.ik_sway_joints = [sway_start_jnt, sway_end_jnt]
            self.ik_sway_grp = self._create_subgroup(name="IkHdl_Follow_Sway_%s_Offset" % follow_name)
            i_node.copy_pose(driver=self.base_joints[3], driven=self.ik_sway_grp)
            ik_jnt_tops.append(self.ik_sway_grp)
            i_utils.select(sway_end_jnt)
            # - Aim the end towards the start
            aim = i_constraint.constrain(sway_start_jnt, sway_end_jnt, aim=[-1, 0, 0], as_fn="aim")
            aim.delete()
            # - Parent
            sway_start_jnt.set_parent(sway_end_jnt)  # Reverse hierarchy positions
            # - IKH
            self.sway_ikh, self.sway_eff = rig_joints.create_ikh_eff(start=sway_end_jnt, end=sway_start_jnt,
                                                                     ikh_parent=self.ik_sway_grp)
            self.sway_ikh.poleVector.set([0, 0, -2])
            ik_jnt_tops.append(sway_end_jnt)
            self.utility_vis_objs.append(self.sway_ikh)

        # Offset Ik
        self.ik_offset_joints, self.offset_ikh, self.offset_eff = None, None, None
        if self.is_quad:
            offset_end = len(self.base_joints) - 1
            self.ik_offset_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Offset_Ik", end_index=offset_end)
            ik_jnt_tops.append(self.ik_offset_joints[0])
            offset_parent = self.ik_sway_joints[0]
            self.offset_ikh, self.offset_eff = rig_joints.create_ikh_eff(start=self.ik_offset_joints[0],
                                                                         end=self.ik_offset_joints[-1],
                                                                         ikh_parent=offset_parent)
            self.utility_vis_objs.append(self.offset_ikh)

        # Pole
        if self.is_quad:
            self.pole_top = self.base_joints[0].duplicate(n=self.base_joints[0] + "_PoleTop_Ik", parentOnly=True)[0]
            self.pole_top.set_parent(w=True)
            self.pole_btm = self.base_joints[-1].duplicate(n=self.base_joints[-1] + "_PoleBtm_Ik", parentOnly=True)[0]
            self.pole_btm.set_parent(w=True)
            self.pole_btm.set_parent(self.pole_top)
            self.follow_pack_grp = self._create_subgroup(name="IkHdl_Follow_%s_Offset" % self.description)
            ik_jnt_tops.append(self.follow_pack_grp)
            self.pole_ikh, self.pole_eff = rig_joints.create_ikh_eff(start=self.pole_top, end=self.pole_btm,
                                                                     ikh_parent=self.follow_pack_grp)
            self.ik_pole_joints = [self.pole_top, self.pole_btm]
            ik_jnt_tops.append(self.pole_top)
            self.utility_vis_objs.append(self.pole_ikh)

        # Cleanup joints
        self.ik_setup_grp = self._create_subgroup(name="Ik_Setup", children=ik_jnt_tops)
    
    
    def _ik_create_control_end(self):
        # Create Controls
        last_jnt_name = self.joint_names[len(self.base_joints) - 1].capitalize()
        end_name = self.base_name + "_" + last_jnt_name
        self.ik_end_ctrl = Build_Foot.create_foot_control(base_name=end_name, pack_size=self.ctrl_size * 0.25, 
                                                          foot_joint=self.base_joints[-1], color=self.side_color,
                                                          parent=self.ik_control_grp, make_wedge=self.end_ctrl_wedge,
                                                          follow_name=last_jnt_name, rotate_order=self.ik_rot_order)
        if not self.end_ctrl_wedge:  # Re-force position match
            i_node.copy_pose(driver=self.base_joints[-1], driven=self.ik_end_ctrl.top_tfm)

        # Create Offset Control
        self.ik_end_offset_ctrl = None
        if self.is_quad:
            dist = i_utils.get_single_distance(from_node=self.base_joints[-2], to_node=self.base_joints[-1])
            tx = -1 * (dist / 4)
            if self.is_mirror:
                tx *= -1
            self.ik_end_offset_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color, 
                                                    degree=3, name=end_name + "Offset_Ctrl", parent=self.ik_control_grp,
                                                    size=self.ctrl_size * 0.25, position_match=self.base_joints[-1], 
                                                    additional_groups=["Xtra"], flip_shape=[0, 0, 90], move_shape=[tx, 0, 0],)
            # Match translation/rotation to second-to-last joint
            i_node.copy_pose(driver=self.base_joints[-2], driven=self.ik_end_offset_ctrl.top_tfm, attrs="tr")
            # Move offset's cns group back to real joint position
            i_node.copy_pose(driver=self.base_joints[-1], driven=self.ik_end_offset_ctrl.cns_grp, attrs="t")
        
        # Drive Items
        if self.is_quad:
            i_constraint.constrain(self.ik_end_ctrl.last_tfm, self.ik_base_joints[-1], mo=True, as_fn="orient")  # Need to keep joint alignment.
        else:
            # offs = [180, 0, 0] if self.is_mirror else [0, 0, 0]
            i_constraint.constrain(self.ik_end_ctrl.last_tfm, self.ik_joints[-1], mo=True, as_fn="orient") # , o=offs # Need to keep joint alignment.
        i_constraint.constrain(self.ik_end_ctrl.last_tfm, self.follow_end_origin_grp, mo=True, as_fn="parent")  # must be mo True
        if self.is_quad:
            i_constraint.constrain(self.ik_end_ctrl.last_tfm, self.follow_pack_grp, mo=True, as_fn="parent")  # must be mo True

        # Drive Items
        if self.is_quad:
            i_constraint.constrain(self.ik_end_offset_ctrl.last_tfm, self.ik_sway_joints[1], mo=False, as_fn="parent")
            i_constraint.constrain(self.ik_end_offset_ctrl.last_tfm, self.ik_sway_grp, mo=True, as_fn="parent")  # need to keep mo True
    
    def _ik_create_control_pv(self):
        # Create Control
        pv_pos_match = self.base_joints[2] if self.is_quad else self.base_joints[1]
        self.ik_pv_ctrl = i_node.create("control", control_type='2D Arrow Single', color=self.side_color,
                                        name=self.base_name + "_PoleVector", degree=1, parent=self.ik_control_grp, # parent=self.ctrl_grp, 
                                        size=self.ctrl_size, flip_shape=[180, 90, 0], match_rotation=False, with_gimbal=False,
                                        position_match=pv_pos_match)
        offset_axis_opts = {"x" : "y", "y" : "z"}
        pv_offset_axis = offset_axis_opts.get(self.orient_joints[0])
        if not pv_offset_axis:
            i_utils.error("Building '%s'. Unsure how to proceed with unexpected primary orient axis: '%s'. Expect from options: %s" % 
                          (self.base_name, self.orient_joints[0], offset_axis_opts.keys()))
        pv_offset = self.ik_pv_ctrl.top_tfm.attr("t" + pv_offset_axis).get() + (self.pack_size * 4 * self.pv_pos_mult)
        self.ik_pv_ctrl.top_tfm.attr("t" + pv_offset_axis).set(pv_offset)
        if self.is_mirror:
            self.ik_pv_ctrl.top_tfm.sx.set(-1)  # Mirror behaviour only achievable through scale. Sad.

        # Pole Vector Constraint
        conn = i_constraint.constrain(self.ik_pv_ctrl.last_tfm, self.base_ikh, as_fn="poleVector")
        # conn.attr("offset").set(self.ik_pv_ctrl.top_tfm.t.get())
        # conn.attr("offset" + pv_offset_axis.upper()).set(pv_offset)  # :note: poleVectorConstraint doesn't have maintainOffset flag :TODO: This sucks
        # :note: ^ was offsetY originally (hardcoded)
        if self.is_quad:
            i_constraint.constrain(self.ik_pv_ctrl.last_tfm, self.offset_ikh, as_fn="poleVector")

    def _ik_create_control_start_point(self):
        start_jnt_name = self.joint_names[0].capitalize()
        ctrl_name = self.base_name + "_" + start_jnt_name + "Point"
        self.start_point_ctrl = i_node.create("control", control_type='3D Locator', color=self.side_color, name=ctrl_name,
                                              degree=1, parent=self.ik_control_grp, size=self.ctrl_size / 3.0,
                                              match_rotation=False, position_match=self.base_joints[0], with_gimbal=False)
        if self.is_quad:
            i_constraint.constrain(self.start_point_ctrl.control, self.pole_top, as_fn="point")
            i_constraint.constrain(self.start_point_ctrl.control, self.ik_base_joints[0], as_fn="parent")
        else:
            i_constraint.constrain(self.start_point_ctrl.control, self.ik_joints[0], as_fn="parent")
    
    def create_ik(self):
        # Create Joints / IKH
        self._ik_setup()
        
        # Create Group
        self.ik_control_grp = self._create_subgroup(name="Ik_Controls", parent=self.ground_gimbal_control)
        
        # Create Controls
        self._ik_create_control_end()
        self._ik_create_control_pv()
        self._ik_create_control_start_point()
        self.anim_cns_control = rig_controls.create_anim_constraint_control(match_joint=self.base_joints[-1],
                                                                            parent_ctrl=self.ik_end_ctrl,
                                                                            control_size=self.ctrl_size / 2.0,
                                                                            base_name=self.base_name,
                                                                            color=self.side_color_tertiary)
        # Connect
        if self.is_quad:
            i_constraint.constrain(self.ik_base_joints[-1], self.ik_joints[-1], mo=True, as_fn="orient")  # End  # mo must be True
            i_constraint.constrain(self.ik_offset_joints[2], self.ik_joints[2], mo=True, as_fn="parent")  # End  # mo must be True
            i_constraint.constrain(self.ik_offset_joints[1], self.ik_joints[1], mo=False, as_fn="parent")  # Mid
            i_constraint.constrain(self.ik_offset_joints[0], self.ik_joints[0], mo=False, as_fn="parent")  # Start
            i_constraint.constrain(self.ik_sway_joints[-1], self.ik_offset_joints[-1], mo=True, as_fn="orient")  # End  # mo must be True
            i_constraint.constrain(self.ik_base_joints[0], self.ik_offset_joints[0], mo=False, as_fn="parent")  # Start
            i_constraint.constrain(self.ik_end_offset_ctrl.last_tfm, self.ik_sway_joints[-1], mo=False, as_fn="parent")  # End  # mo may need to be True for BLC

            for i in range(len(self.ik_joints)):
                main_jnt = self.ik_joints[i]
                base_jnt = self.ik_base_joints[i]
                offs_jnt = None
                if self.is_quad:
                    offs_jnt = self.ik_offset_joints[i] if i < len(self.ik_offset_joints) else None
    
                for axis in ["X", "Y", "Z"]:
                    main_jnt.attr("scale" + axis).drive(base_jnt.attr("scale" + axis))
                    if offs_jnt:
                        main_jnt.attr("scale" + axis).drive(offs_jnt.attr("scale" + axis))

            for axis in ["X", "Y", "Z"]:
                self.base_joints[2].attr("scale" + axis).drive(self.ik_sway_joints[1].attr("scale" + axis))
    
    
    def create_fk(self):
        # Joints
        # - Create
        # :note: Need to duplicate the ik joints and not the base because the ik joint positions are what will drive the base and
        # if duplicate base before they're driven by ik/fk, the fk joint positions won't match the ik
        self.fk_joints = rig_joints.duplicate_joints(joints=self.ik_joints, name_sr=["Ik", "Fk"], 
                                                     end_index=len(self.base_joints))  # self.base_joints
        
        # Group
        self.fk_setup_grp = self._create_subgroup(name="Fk_Setup", children=self.fk_joints[0])
        self.fk_controls_grp = self._create_subgroup(name="Fk_Controls")
        
        # Controls
        self.fk_ctrls = []
        ctrl_parent = self.fk_controls_grp
        joint_names = self.joint_names
        for i, jnt in enumerate(self.fk_joints):
            # - Create
            base_name = self.base_name + "_" + joint_names[i].capitalize() + "_Fk"
            do_gim = True if i == 0 else False
            ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy, name=base_name,
                                 position_match=jnt, match_rotation=True, parent=ctrl_parent, #lock_hide_attrs=["t", "v"]
                                 size=self.ctrl_size * 0.5, with_gimbal=do_gim, follow_name=joint_names[i].capitalize() + "_Fk", 
                                 scale_shape=[self.ctrl_size * 0.25, 1, 1], rotate_order=self.fk_rot_orders[i])
            self.fk_ctrls.append(ctrl)
            ctrl_parent = ctrl.last_tfm
            # - Constrain
            # i_constraint.constrain(jnt, ctrl.top_tfm, mo=True, as_fn="point")
            i_constraint.constrain(ctrl.last_tfm, jnt, mo=True, as_fn="point")
            i_constraint.constrain(ctrl.last_tfm, jnt, mo=True, as_fn="orient")


    def _bend_create(self, from_joint=None, to_joint=None, bend_position=""):
        # Create subgroup
        subgroup = i_node.create("transform", n=self.base_name + "_Bend" + bend_position + "_Grp")
        subgroup.set_parent(self.bend_grp)
        
        # Joints
        if bend_position == "Top":
            base_jnt = self.base_joints[self.base_joints.index(from_joint)]
            base_jnt_pos = base_jnt.xform(q=True, t=True, ws=True)
            parent_pos = [base_jnt_pos[0] - (self.pack_size / 3), base_jnt_pos[1], base_jnt_pos[2]]
        else:
            # Makes the Mid-Bend_Parent Joint be in the position of the Top-Bend_Parent Joint. Rigging's request. Unsure why.
            prev_base_jnt = self.base_joints[self.base_joints.index(from_joint) - 1]
            parent_pos = prev_base_jnt.xform(q=True, t=True, ws=True)
        
        bend_joints = self._create_bend_joints(from_joint=from_joint, to_joint=to_joint, parent_pos=parent_pos)
        # if bend_position != "Top":
        #     chldn = bend_joints[0].relatives(c=True)
        #     i_utils.parent(chldn, w=True)
        #     i_node.copy_pose(driver=prev_base_jnt, driven=bend_joints[0], attrs="r")
        #     i_utils.parent(chldn, bend_joints[0])
        bend_joints[0].set_parent(subgroup)
        
        # Controls
        with_bendy = True
        if bend_position == "Btm":
            with_bendy = False
        base_name = self.base_name + "_" + bend_position + "_Bend"
        ikfk_extra = True if self.base_joints.index(from_joint) == 0 else False
        controls = rig_controls.create_bendy_control_chain(from_joint=from_joint, to_joint=to_joint,
                                                           base_name=base_name, with_bendy=with_bendy,
                                                           ikfk_extra=ikfk_extra, scale=self.ctrl_size,
                                                           ends_color=self.side_color_scndy, 
                                                           bendy_color=self.side_color, 
                                                           mid_color=self.side_color_tertiary, 
                                                           ikfk_control=self.ikfk_switch_control)
        bend_skin_joints = []
        for section, ctrl in controls.items():
            if not ctrl:  # Last section has no bend control
                continue
            self.bend_controls.append(ctrl.control)
            ctrl.top_tfm.set_parent(subgroup)
            if self.scale_attr:
                i_attr.connect_attr_3(self.scale_attr, ctrl.top_tfm.s)
            if hasattr(ctrl, "xtra_jnt"):
                bend_skin_joints.append(ctrl.xtra_jnt)
                if section == "end":
                    ctrl.xtra_jnt.attr("jo" + self.orient_joints[0]).set(180)
                
        controls["bend_skin_joints"] = bend_skin_joints  # Store before reverse so it skins in proper order
        self.joint_vis_objs += bend_skin_joints
        # if bend_position == "Btm":
        #     bend_skin_joints = list(reversed(bend_skin_joints))  # Don't do .reverse() bc it messes with storing in controls

        # Curve
        positions = ["Top", "Mid", "Btm"] if self.is_quad else ["Top", "Btm"]
        fk_control = self.fk_ctrls[positions.index(bend_position)].control
        up_tw_pos = True
        # if not self.is_arm and bend_position == positions[-1]:
        #     up_tw_pos = False
        bend_curve, bend_blc = rig_joints.create_bend_curve(bend_joints=bend_joints[1:],
                                                            name=self.base_name + "_" + bend_position + "Bend",
                                                            parent=subgroup,
                                                            ikfk_switch=self.ikfk_switch_control,
                                                            ik_attr_control = self.ik_end_ctrl.control,
                                                            fk_control=fk_control,
                                                            bend_start_end=bend_skin_joints,  # [from_joint, to_joint]
                                                            orientation=self.orient_joints,
                                                            scale_attr=self.scale_attr,
                                                            up_twist_positive=up_tw_pos)
        bend_grp = bend_curve.relatives(0, p=True)
        self.utility_vis_objs.append(bend_grp)
        controls["bend_curve"] = bend_curve
        controls["bend_blc"] = bend_blc
        controls["bend_joints"] = bend_joints
        
        # Rotate mid control for mirror behaviour
        if self.is_mirror:
            mid_xtra_grp = controls.get("mid").xtra_grp
            mid_xtra_grp.rx.set(-180)
        
        # Return
        return controls
    
    def _bend_connect(self, bends=None, upr_upv=None, mid_upv=None, btm_upv=None):
        # Vars
        # - Based on sections
        upper = bends.get("Top")
        mid = bends.get("Mid")
        btm = bends.get("Btm")
        positions = [upper, btm]
        upper_joint = self.base_joints[0]
        position_base_joints = [upper_joint]
        if mid:
            positions.insert(1, mid)
            mid_joint = self.base_joints[1]
            btm_joint = self.base_joints[2]
            position_base_joints += [mid_joint, btm_joint]
        else:
            mid_joint = None
            btm_joint = self.base_joints[1]
            position_base_joints.append(btm_joint)
            btm_upv = mid_upv
        # - Axis based on joint orientation
        primary_axis = self.orient_joints[0]
        primary_aim = [0, 0, 0]
        neg_primary_aim = [0, 0, 0]
        up_aim = [0, 0, 0]
        neg_up_aim = [0, 0, 0]
        zero_offset = [0, 0, 0]
        pr_offset = [0, 0, 0]
        up_offset = [0, 0, 0]
        pr_i = ["x", "y", "z"].index(primary_axis)
        up_axis = {"xyz": "y", "yzx": "z"}.get(self.orient_joints)
        if not up_axis:
            i_utils.error("Up axis unknown for orientation '%s'." % self.orient_joints)
        up_i = ["x", "y", "z"].index(up_axis)
        primary_aim[pr_i] = 1
        neg_primary_aim[pr_i] = -1
        up_aim[up_i] = 1
        neg_up_aim[up_i] = -1
        pr_offset[pr_i] = 180
        up_offset[up_i] = 180
        
        # Upper Section
        # Top Ctrl
        i_constraint.constrain(upper_joint, upper.get("top").top_tfm, as_fn="point")
        i_constraint.constrain(upper_joint, upper.get("top").top_tfm, as_fn="orient")
        i_constraint.constrain(upper.get("mid").control, upper.get("top").aim_grp, wut="objectrotation", wu=up_aim,
                          aim=primary_aim, u=up_aim, wuo=upr_upv, as_fn="aim", skip=primary_axis)
        upper.get("top").top_tfm.zero_out(t=False, r=True, s=False)
        # Mid Ctrl
        i_constraint.constrain(upper_joint, upper.get("bendy").control, upper.get("mid").top_tfm, as_fn="point")
        upr_mid_aim_offset = pr_offset if self.is_mirror else zero_offset  # UprMid Aim Offset - 180y for mirror / 0 non
        i_constraint.constrain(upper.get("bendy").control, upper.get("mid").top_tfm, o=upr_mid_aim_offset,
                          wut="objectrotation", wuo=upr_upv, aim=primary_aim, wu=up_aim, u=up_aim, as_fn="aim")
        # End Ctrl
        i_constraint.constrain(upper.get("bendy").control, upper.get("end").xtra_grp, as_fn="point")
        i_constraint.constrain(upper.get("mid").control, upper.get("end").xtra_grp, o=pr_offset,
                          wut="objectrotation", wuo=upr_upv, wu=up_aim, aim=neg_primary_aim, u=up_aim, as_fn="aim")
        next_joint = mid_joint or btm_joint
        i_constraint.constrain(next_joint, upper.get("end").top_tfm, as_fn="point")
        i_constraint.constrain(upper_joint, upper.get("end").top_tfm, as_fn="orient")
        # Bendy
        i_constraint.constrain(next_joint, upper.get("bendy").top_tfm, mo=True, as_fn="point")
        i_constraint.constrain(upper_joint, upper.get("bendy").top_tfm, mo=True, as_fn="orient")
        # End Offset
        upper.get("end").top_tfm.zero_out()
        # Define bottom's previous section
        prev_section = upper
        
        # Mid Section
        if mid:
            # Top Ctrl
            i_constraint.constrain(upper.get("bendy").control, mid.get("top").xtra_grp, as_fn="point")
            i_constraint.constrain(mid_joint, mid.get("top").top_tfm, as_fn="point")
            i_constraint.constrain(mid_joint, mid.get("top").top_tfm, o=[-90, 0, 90], as_fn="orient")
            i_constraint.constrain(mid.get("mid").control, mid.get("top").xtra_grp, wut="objectrotation",
                              aim=primary_aim, u=neg_up_aim, wu=up_aim, wuo=mid_upv, o=pr_offset, as_fn="aim")
            # Mid Ctrl
            i_constraint.constrain(upper.get("bendy").control, mid.get("mid").top_tfm, wu=up_aim,
                              wut="objectrotation", wuo=mid_upv, aim=neg_primary_aim, u=up_aim, as_fn="aim")  # , o=[0, 0, 90]
            i_constraint.constrain(upper.get("bendy").control, mid.get("bendy").control, mid.get("mid").top_tfm, as_fn="point")
            # End Ctrl
            i_constraint.constrain(mid.get("bendy").control, mid.get("end").xtra_grp, as_fn="point")
            i_constraint.constrain(mid.get("mid").control, mid.get("end").xtra_grp, wut="objectrotation",
                              wu=up_aim, aim=neg_primary_aim, u=up_aim, wuo=mid_upv, o=pr_offset, as_fn="aim")
            i_constraint.constrain(btm_joint, mid.get("end").top_tfm, as_fn="point")
            i_constraint.constrain(mid_joint, mid.get("end").top_tfm, o=[-90, 0, 90], as_fn="orient")
            # Bendy
            i_constraint.constrain(btm_joint, mid.get("bendy").top_tfm, mo=True, as_fn="point")
            i_constraint.constrain(mid_joint, mid.get("bendy").top_tfm, mo=True, as_fn="orient")
            # End Offset
            mid.get("end").top_tfm.zero_out()
            # Define bottom's previous section
            prev_section = mid
        
        # Btm Section
        # Top Ctrl
        i_constraint.constrain(prev_section.get("bendy").control, btm.get("top").xtra_grp, as_fn="point")
        i_constraint.constrain(btm.get("mid").control, btm.get("top").xtra_grp, wut="objectrotation",
                          aim=primary_aim, u=up_aim, wu=up_aim, wuo=btm_upv, as_fn="aim")
        i_constraint.constrain(btm_joint, btm.get("top").top_tfm, as_fn="point")
        i_constraint.constrain(btm_joint, btm.get("top").top_tfm, as_fn="orient")
        # Mid Ctrl
        i_constraint.constrain(self.base_joints[-1], prev_section.get("bendy").control, btm.get("mid").top_tfm, as_fn="point")
        mid_aim_offset = pr_offset if self.is_mirror else zero_offset  # BtmMidAim Offset - 180y for mirror / 0 non
        i_constraint.constrain(prev_section.get("bendy").control, btm.get("mid").top_tfm, o=mid_aim_offset,
                          wut="objectrotation", wuo=btm_upv, aim=neg_primary_aim, wu=up_aim, u=up_aim, as_fn="aim")
        # End Ctrl
        i_constraint.constrain(self.base_joints[-1], btm.get("end").top_tfm, as_fn="point")
        btm_ori_offset = zero_offset if (not self.is_arm and self.is_mirror) else up_offset  # BtmEndAim Offset - RLeg 0 else 1z
        i_constraint.constrain(btm_joint, btm.get("end").top_tfm, o=btm_ori_offset, as_fn="orient")
        btm_aim_offset = pr_offset if (self.is_mirror and not self.is_arm) else zero_offset  # BtmEndAim Offset - 180y for R Leg / 0 for all else
        btm_aim_skip = "" if self.is_arm else primary_axis # BtmEndAim Skip - y for leg / none for arm
        btm_aim_up = up_aim if (self.is_mirror and not self.is_arm) else neg_up_aim  # BtmEndAim Up - 1y for R Leg / -1y for all else
        i_constraint.constrain(btm.get("mid").control, btm.get("end").aim_grp, wut="objectrotation", wu=up_aim, 
                          aim=neg_primary_aim, o=btm_aim_offset, u=btm_aim_up, as_fn="aim", wuo=btm_upv, skip=btm_aim_skip)
        if btm_aim_skip:
            val = 180 if self.is_mirror else 0
            btm.get("end").aim_grp.attr("r" + primary_axis).set(val)  # BtmEndAimGrp - Manually set ry for Leg (180 R / 0 L) / None for leg

    def create_stretch(self):
        # Create group
        self.stretch_grp = self._create_subgroup(name="Distance_Setup")

        # Kill the first ikfk blc because it creates cycles. Replace by adding to constraint
        trans_blc = self.base_joints[0].t.connections(type="blendColors")
        if trans_blc:
            trans_blc[0].delete()
            i_constraint.constrain(self.fk_ctrls[0].last_tfm, self.base_joints[0], as_fn="point")
        
        # Create stretch
        stretch_info = rig_joints.create_stretch(start_driver=self.base_joints[0],
                                                 end_driver=self.base_joints[-1],
                                                 driven=self.ik_end_ctrl.last_tfm,
                                                 base_name=self.base_name,
                                                 parent=self.stretch_grp,
                                                 ik_control=self.ik_end_ctrl.control,
                                                 ikh=self.follow_end_offset_grp,
                                                 ik_joints=self.ik_joints,
                                                 fk_joints=self.fk_joints,
                                                 fk_controls=self.fk_ctrls,
                                                 result_joints=self.base_joints,
                                                 ikfk_switch=self.ikfk_switch_control,
                                                 section_names=self.joint_names,
                                                 stretch_axis=self.orient_joints[0],
                                                 )
        self.top_locator = stretch_info.get("start_locator")
        self.btm_locator = stretch_info.get("end_locator")
        
        fk_vol_attrs = stretch_info.get("fk_things").get("volume_attrs")
        fk_str_attrs = stretch_info.get("fk_things").get("stretch_attrs")
        for fk_attr in fk_vol_attrs + fk_str_attrs:
            fk_attr.set(k=False, l=True)
    
    def _create_bend_joints(self, from_joint=None, to_joint=None, parent_pos=None):
        # Vars
        if parent_pos is None:
            parent_pos = [0, 0, 0]

        # Duplicate Chain
        bend_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Bend",
                                                  start_index=self.base_joints.index(from_joint),
                                                  end_index=self.base_joints.index(to_joint) + 1)
        rig_joints.orient_joints(bend_joints, orient_as=self.orient_joints, up_axis=self.orient_joints_up_axis)

        # Insert Bendy Joints
        bend_joint_chn = rig_joints.create_bend_joints(from_joint=bend_joints[0], to_joint=bend_joints[1],
                                                       number_of_insertions=self.number_bend_joints,
                                                       parent=self.pack_grp, parent_pos=parent_pos)
        
        # Rename end joint to end with "_Bend_End"
        end_bend_joint = bend_joint_chn[-1]
        end_bend_joint.rename(end_bend_joint[:-1] + "_End")

        # Add to lists
        self.bend_joints += bend_joint_chn

        # Return
        return bend_joint_chn

    def create_bend(self):
        # Vars
        self.bends = collections.OrderedDict()
        
        # Create group
        self.bend_grp = self._create_subgroup(name="Bend_Setup", parent=self.pack_ctrl_grp)
        # - Connect visibility
        # :note: Show by default so rigging doesn't forget about them
        i_attr.create_vis_attr(node=self.ikfk_switch_control, ln="Bendy", drive=self.bend_grp, dv=0)

        # Start > Mid
        self.bends["Top"] = self._bend_create(from_joint=self.base_joints[0], to_joint=self.base_joints[1], bend_position="Top")

        # Mid > End
        mid_end_ind = -2 if self.is_quad else -1  # Never include quad end joint
        position = "Mid" if self.is_quad else "Btm"
        self.bends[position] = self._bend_create(from_joint=self.base_joints[1], to_joint=self.base_joints[mid_end_ind], bend_position=position)

        # End > Quad End
        if self.is_quad:
            self.bends["Btm"] = self._bend_create(from_joint=self.base_joints[2], to_joint=self.base_joints[-1], bend_position="Btm")
        
        # Up Vector Nodes
        up_vecs = []
        t_inc = 5 * self.pack_size  #  * self.side_mult
        trans = [0, t_inc, 0] if self.is_arm else [0, 0, t_inc]
        for i in range(len(self.base_joints[:-1])):
            upv_name = self.base_name + "_" + self.joint_names[i].capitalize() + "_Bendy_CtrlUpVec_Tfm"
            upv = i_node.create("transform", n=upv_name)
            up_vecs.append(upv)
            i_node.copy_pose(driver=self.base_joints[i], driven=upv, attrs="tr")
            upv.xform(t=trans, r=True)
            upv.set_parent(self.bend_grp)
            i_constraint.constrain(self.base_joints[i], upv, mo=True, as_fn="parent")

        # Constrain
        self._bend_connect(bends=self.bends, upr_upv=up_vecs[0], mid_upv=up_vecs[1], btm_upv=up_vecs[-1])
        
        # Loop through each bend section
        for position in self.bends.keys():
            # - Skin
            bend_position_info = self.bends.get(position)
            curve = bend_position_info.get("bend_curve")
            skin_joints = bend_position_info.get("bend_skin_joints")
            rig_joints.skin_curve(curve=curve, skin_joints=skin_joints)
            # - Lock and Hide
            i_attr.lock_and_hide(node=bend_position_info.get("top").control, attrs=["t", "s"], lock=True, hide=True)
            i_attr.lock_and_hide(node=bend_position_info.get("mid").control, attrs=["r", "s"], lock=True, hide=True)
            i_attr.lock_and_hide(node=bend_position_info.get("end").control, attrs=["t", "s"], lock=True, hide=True)
            if bend_position_info.get("bendy"):
                i_attr.lock_and_hide(node=bend_position_info.get("bendy").control, attrs=["s"], lock=True, hide=True)
        
        # Reposition Cvs
        sections = self.bends.keys()
        top_ctrls = [self.bends.get(sect).get("top").control for sect in sections]
        end_ctrls = [self.bends.get(sect).get("end").control for sect in sections]

        for ctrl in end_ctrls:  # top_ctrls + 
            rz = 180 #-180 if ctrl in top_ctrls else 180 # Inward
            # rz = 90 if ctrl in top_ctrls else -90 # Outward
            cvs = ctrl.get_cvs()
            i_utils.xform(cvs, 0, 0, rz, r=True, as_fn="rotate")

        # Set up the end follow
        # - End Aim
        last_control = self.bends["Btm"].get("end").control
        aa_name_add = "%s_AutoAim_%s" % (self.joint_names[-1].capitalize(), self.joint_names[0].capitalize())
        end_autoaim_xtra_grp = last_control.create_zeroed_group(group_name_add=aa_name_add + "_Xtra", zero_out_created_group=False)  # , zero_out_created_group=False
        end_parent = end_autoaim_xtra_grp.relatives(0, p=True)
        end_autoaim_offs_grp = i_node.create("transform", n=end_autoaim_xtra_grp.replace("_Xtra", "_Offset"), p=end_parent)
        i_node.copy_pose(self.base_joints[-1], end_autoaim_offs_grp, attrs="tr")
        end_autoaim_grp = i_node.create("transform", n=end_autoaim_xtra_grp.replace("_Xtra", ""), p=end_autoaim_offs_grp)
        end_autoaim_grp.zero_out()
        end_autoaim_xtra_grp.set_parent(end_autoaim_grp)
        sr = list("xyz".replace(self.orient_joints[0], ""))
        # :note: Need to have "Decompose near object" on (not in maya docs) - may be a 2017 thing?
        i_constraint.constrain(self.base_joints[-1], end_autoaim_grp, as_fn="parent", skipRotate=sr, dr=True, mo=True)
        # - Upper Aim
        first_control = self.bends["Top"].get("top").control
        upper_autoaim_grp = first_control.create_zeroed_group(group_name_add="%s_AutoAim_%s" % (self.joint_names[0].capitalize(), self.joint_names[-1].capitalize()),
                                                              zero_out_created_group=False)
        # - Upper Twist
        upper_fk_control = self.fk_ctrls[0].last_tfm
        upper_twist_tfm = i_node.create("transform", n=self.base_name + "_%s_Twist_Tfm" % self.joint_names[0].capitalize(), parent=self.bend_grp)
        upper_twist_offset_grp = upper_twist_tfm.create_zeroed_group(group_name_add="Offset")
        upper_twist_offset_grp.set_parent(self.start_point_ctrl.last_tfm)
        i_node.copy_pose(self.fk_ctrls[0].top_tfm, upper_twist_offset_grp, attrs="tr")
        i_constraint.constrain(upper_fk_control, upper_twist_tfm, as_fn="parent", skipRotate=sr, dr=True, mo=True)
        if self.ground_gimbal_control:
            i_constraint.constrain(self.ground_gimbal_control, upper_twist_offset_grp, as_fn="parent", mo=True)

        # - Math
        twist_neg_md = i_node.create("multiplyDivide", n=self.base_name + "_%s_TwistNeg_Md" % self.joint_names[0].capitalize())
        upper_twist_tfm.ry.drive(twist_neg_md.input1X)
        twist_neg_md.input2X.set(self.side_mult * -1)
        twist_md = i_node.create("multiplyDivide", n=self.base_name + "_%s_Twist_Md" % self.joint_names[0].capitalize())
        twist_neg_md.outputX.drive(twist_md.input1X)
        ikfk_rev = i_node.create("reverse", n=self.base_name + "_IkFk_Rev")
        self.ikfk_switch_control.FKIKSwitch.drive(ikfk_rev.inputX)
        ikfk_rev.outputX.drive(twist_md.input2X)
        # - Driver upper aim
        twist_md.outputX.drive(upper_autoaim_grp.attr("r" + self.orient_joints[0]))


    def connect_elements(self):
        i_constraint.constrain(self.start_point_ctrl.last_tfm, self.base_joints[0], mo=False, as_fn="point")
        if self.is_quad:
            i_constraint.constrain(self.ik_base_joints[-2], self.ik_end_offset_ctrl.top_tfm, mo=True, as_fn="parent")

        # Add Attrs
        # - Vars
        joint_names = self.joint_names
        ln_nn = {"Upper": joint_names[0].capitalize(),
                 "Mid": joint_names[1].capitalize(),
                 "Lower": joint_names[len(self.base_joints) - 1].capitalize()}
        # - MidDirection
        mid_direction_attr = i_attr.create(node=self.ik_end_ctrl.control, ln="MidDirection", k=True,
                                           at="double", dv=0.0, nn=ln_nn.get("Mid") + " Direction")
        mid_direction_attr.drive(self.base_ikh.twist)
        # - UpperTwist
        upper_twist_attr = i_attr.create(self.ikfk_switch_control, "UpperTwist", k=True,  # self.ik_end_ctrl.control, 
                                         at="double", dv=0.0, nn=ln_nn.get("Upper") + " Twist")
        upper_twist_attr.drive(self.bends.get("Top").get("top").ik_xtra_grp.attr("r" + self.orient_joints[0]))
        if self.is_quad:
            # :TODO: May need to change to "s" + self.orient_joints[0]
            self.ik_joints[-2].sx.drive(self.ik_end_offset_ctrl.top_tfm.scaleX)

        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], unlock=True)
        i_constraint.constrain(self.base_joints[-1], self.ikfk_switch_control, mo=True, as_fn="parent")
        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r"], lock=True)
        
        # Update the Fk wrist rot constraint to have offset that make it match ik. No idea why it's being weird and cannot
        # even have the offset set when the constraint is created. Should look into this. :TODO:
        end_fk_cns = i_constraint.get_constraint_by_driver(driven=self.fk_joints[-1], cns_type="orient")[0].node
        end_ik_rot = self.ik_joints[-1].r.get()
        for i, axis in enumerate(["X", "Y", "Z"]):
            end_fk_cns.attr("offset" + axis).set(end_ik_rot[i])
        
        # Create group for auto aims to use in stitching
        self.autoaim_origin_grp = self._create_subgroup(name=self.joint_names[0].capitalize() + "_AutoAim_Origin", use_existing=True)

        # Follow
        if self.is_arm:
            rig_attributes.create_follow_attr(driving=self.ik_pv_ctrl.control, dv=self.ik_end_ctrl.last_tfm,
                                              options=[self.ik_end_ctrl.last_tfm], cns_type="point", 
                                              pack_info_node=self.pack_info_node, driver_pack_info_node=self.pack_info_node)
        else:
            pv_rot_skip = [ax for ax in ["x", "y", "z"] if ax != self.orient_joints[0]]
            rig_attributes.create_follow_attr(driving=self.ik_pv_ctrl.control, dv=self.ik_end_ctrl.last_tfm,
                                              options=[self.ik_end_ctrl.last_tfm], cns_type="point",
                                              pack_info_node=self.pack_info_node, driver_pack_info_node=self.pack_info_node)
            rig_attributes.create_follow_attr(driving=self.ik_pv_ctrl.control, dv=self.ik_end_ctrl.last_tfm,
                                              options=[self.ik_end_ctrl.last_tfm], cns_type="orient", skip=pv_rot_skip,
                                              pack_info_node=self.pack_info_node, driver_pack_info_node=self.pack_info_node)
            # - Make an extra offset positioned at the pv control so control can stay zeroed out while follow groups positioned at ik_end control
            self.ik_pv_ctrl.control.create_zeroed_group(group_name_add="Xtra", zero_out_created_group=False)
        rig_attributes.create_follow_attr(driving=self.ik_end_ctrl.control, options=[self.anim_cns_control], cns_type="parent", 
                                          pack_info_node=self.pack_info_node, driver_pack_info_node=self.pack_info_node)
        # Drive constraint weights with IkFk switch
        top_fk_attr = i_constraint.get_constraint_by_driver(driven=self.base_joints[0], drivers=self.fk_ctrls[0].last_tfm)
        top_point_attr = i_constraint.get_constraint_by_driver(driven=self.base_joints[0], drivers=self.start_point_ctrl.last_tfm)
        # - outColorG: Fk / outColorR: Ik
        if top_point_attr and top_fk_attr:
            self.ikfk_vis_con.outColorR.drive(top_point_attr[0])
            self.ikfk_vis_con.outColorG.drive(top_fk_attr[0])
    
    def _cleanup_bit(self):
        # Attrs needed for stitching
        stitch_i = -2 if self.is_quad else -1
        # - Store stuff
        self.last_fk_control = self.fk_ctrls[stitch_i].control
        self.last_ik_joint = self.ik_joints[stitch_i]
        self.last_fk_joint = self.fk_joints[stitch_i]
        self.last_base_joint = self.base_joints[stitch_i]
        if self.is_quad:
            self.foot_fk_ctrl = self.fk_ctrls[-1].control
            self.foot_fk_jnt = self.fk_joints[-1]
            self.foot_ik_jnt = self.ik_joints[-1]
            self.foot_base_jnt = self.base_joints[-1]
            self.mid_fk1_ctrl = self.fk_ctrls[1].last_tfm
            self.mid_fk2_ctrl = self.fk_ctrls[2].last_tfm
        else:
            self.mid_fk_ctrl = self.fk_ctrls[1].last_tfm

        # Cleanup Created Stuff & Store Class Attrs
        self.bind_joints = []  # Re-empty
        for jnt in self.bend_joints:
            if "_Bend_Parent" in jnt or "_Bend_End" in jnt:
                self.joint_vis_objs.append(jnt)
            else:
                self.bind_joints.append(jnt)
        
        # Lock and Hide
        i_attr.lock_and_hide(node=self.ik_end_ctrl.control, attrs=["s", "v"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.ik_pv_ctrl.control, attrs=["r", "s", "v"], lock=True, hide=True)
        fk_ctrls_conn = [fk.control for fk in self.fk_ctrls]
        fk_ctrls_conn += [fk.gimbal for fk in self.fk_ctrls if fk.gimbal]
        for ctrl in fk_ctrls_conn:
            i_attr.lock_and_hide(node=ctrl, attrs=["s", "v"], lock=True, hide=True)  # "t", 
        
        # Parenting
        i_utils.parent(self.base_joints[0], self.ik_setup_grp, self.fk_setup_grp, self.pack_rig_jnt_grp)
        self.stretch_grp.set_parent(self.pack_utility_grp)

    def _create_bit(self):
        # Is this pack for a quad limb?
        if len(self.base_joints) == 4:
            self.is_quad = True
        
        # Create all the elements
        self.create_ik()
        self.create_fk()
        ik_controls = [self.ik_end_ctrl.control, self.ik_end_ctrl.gimbal, self.anim_cns_control, self.ik_pv_ctrl.control]
        if self.is_quad:
            ik_controls.append(self.ik_end_offset_ctrl.control)
        fk_controls = [fk.control for fk in self.fk_ctrls] + [fk.gimbal for fk in self.fk_ctrls if fk.gimbal]
        self._create_ikfk_switch(ik_controls=ik_controls, ik_joints=self.ik_joints, pv_control=self.ik_pv_ctrl.control, 
                                 fk_controls=fk_controls, fk_joints=self.fk_joints, offset_distance=self.ikfk_switch_offset,
                                 translation=True)
        self.create_bend()
        self.create_stretch()

        # Connect different elements together
        # :note: These are things that can't happen at individual creation stages.
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_joint_grp = pack_obj.pack_rig_jnt_grp
        pack_fk_ctrl_grp = pack_obj.fk_controls_grp
        pack_point_top_grp = pack_obj.start_point_ctrl.top_tfm
        pack_pv_control = pack_obj.ik_pv_ctrl.control
        pack_fk_controls = [pack_obj.fk_ctrls[0].control, pack_obj.fk_ctrls[1].control, pack_obj.fk_ctrls[-1].control]
        pack_mid_fk_controls = [pack_fk_controls[1]]
        if pack_obj.is_quad:
            pack_fk_controls[1] = pack_obj.fk_ctrls[1].control
            pack_fk_controls.insert(2, pack_obj.fk_ctrls[2].control)
            pack_mid_fk_controls.append(pack_fk_controls[2])
        pack_ik_end_control = pack_obj.ik_end_ctrl.control
        pack_ik_end_lasttfm = pack_obj.ik_end_ctrl.last_tfm
        pack_autoaim_origin_grp = pack_obj.autoaim_origin_grp

        # Stitch
        if parent_build_type in ["Clavicle", "Hip"]:
            parent_control = parent_obj.ctrl.control
            parent_tweak_last = parent_obj.tweak_ctrls[0].last_tfm
            self.stitch_cmds.append({"parent": {"child": pack_fk_ctrl_grp, "parent": parent_control}})  # pack_ik_ctrl_grp
            self.stitch_cmds.append({"constrain": {"args": [parent_control, pack_joint_grp], "kwargs": {"mo": True, "as_fn": "parent"}}})
            self.stitch_cmds.append({"parent": {"child": pack_point_top_grp, "parent": parent_tweak_last}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_fk_controls[0], "cns_type": "orient",
                                                "options": parent_control}})
            if not pack_obj.is_arm:
                self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                    "options": parent_control}})
            
            # Create an autoaim setup for the limb end
            # - Vars
            upr_name = pack_obj.joint_names[0].capitalize()
            end_name = "Hand" if pack_obj.is_arm else "Foot"  # pack_obj.joint_names[-1].capitalize()
            parent_tweak_cns = parent_obj.tweak_ctrls[0].cns_grp
            # - Create Groups
            autoaim_offset_grp = self._create_subgroup(name=upr_name + "_AutoAim_Offset", parent=pack_autoaim_origin_grp, use_existing=True)
            if not autoaim_offset_grp.existed:
                i_node.copy_pose(driver=parent_tweak_last, driven=autoaim_offset_grp)
                autoaim_grp = self._create_subgroup(name=upr_name + "_AutoAim", parent=autoaim_offset_grp)
                # - Create Up Loc
                loc_parent = pack_obj.ground_gimbal_control or pack_obj.pack_grp
                autoaim_upvec_loc = i_node.create("locator", name=pack_obj.base_name + "_" + upr_name + "_AutoAim_UpVec_Loc", 
                                                  parent=loc_parent, use_existing=True)
                i_node.copy_pose(driver=parent_obj.base_joints[0], driven=autoaim_upvec_loc, attrs="tr")
                self._utility_cleanup(autoaim_upvec_loc)
                # autoaim_upvec_loc.xform([0, (5 * pack_obj.pack_size), 0], ws=True, as_fn="move")  # :note: doesn't work right
                autoaim_upvec_loc.s.set(pack_obj.loc_size)
                # - Aim Constraint
                primary_i = "xyz".index(self.orient_joints[0])
                primary_aim = [0, 0, 0]
                primary_aim[primary_i] = 1 * self.side_mult
                up_i = "xyz".index({"xyz" : "y", "yzx" : "z"}.get(self.orient_joints))
                up_aim = [0, 0, 0]
                up_aim[up_i] = 1 * self.side_mult
                aim_cns = i_constraint.constrain([pack_ik_end_lasttfm, autoaim_grp], mo=True, as_fn="aim", aim=primary_aim,
                                            u=up_aim, wu=up_aim, wut="objectRotation", wuo=autoaim_upvec_loc)
                if pack_obj.is_mirror:  # :TODO: Why does this hack need to happen to 0 out rotation when mo=True?
                    i_node.zero_out_trs_to_offsets(constrained_obj=autoaim_grp, constraint=aim_cns, trs="r")
                # - Create Control Attribute
                autoaim_dv = 0.0 if pack_obj.is_arm else 1.0
                autoaim_attr = i_attr.create(parent_control, ln=end_name + "_AutoAim", k=True, min=0.0, max=1.0, dv=autoaim_dv, at="double", use_existing=True)                
                # - Create Blend
                autoaim_blc = i_node.create("blendColors", name=pack_obj.base_name + "_" + end_name + "_AutoAim_Blc", use_existing=True)
                autoaim_grp.r.drive(autoaim_blc.color1)
                autoaim_blc.color2.set([0, 0, 0])
                autoaim_blc.output.drive(parent_tweak_cns.r)
                # - Create Md
                autoaim_md = i_node.create("multiplyDivide", name=pack_obj.base_name + "_" + end_name + "_AutoAim_Md", use_existing=True)
                autoaim_attr.drive(autoaim_md.input1X)
                pack_obj.ikfk_switch_control.FKIKSwitch.drive(autoaim_md.input2X)
                autoaim_md.outputX.drive(autoaim_blc.blender)
                # - Store unstitch commands
                self.stitch_cmds.append({"delete": {"unstitch": [autoaim_attr, autoaim_blc, autoaim_md, aim_cns]}})
                self.stitch_cmds.append({"unique": {"unstitch": "i_node.copy_pose(driver='%s', driven='%s')" % (pack_autoaim_origin_grp, autoaim_offset_grp)}})
                # - Connect created to info node
                i_node.connect_to_info_node(info_attribute="build_objects", node=pack_obj.pack_info_node,
                                            objects=[autoaim_offset_grp, autoaim_grp, autoaim_upvec_loc, aim_cns, autoaim_blc, autoaim_md])
            
            # # Shift follow attrs
            # self.stitch_cmds.append({"shift_follow_attrs": {"control": parent_control}})
        
        elif parent_build_type == "Cog":
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            cog_drivers = [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]
            pv_drivers = cog_drivers if pack_obj.is_arm else cog_drivers[1:]
            if pack_obj.is_arm:
                self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "point",
                                                    "options": pv_drivers}})
                self.stitch_cmds.append({"follow": {"driving": pack_fk_controls[0], "cns_type": "orient",
                                                    "dv" : parent_ground_ctrl, "options": cog_drivers}})
            else:
                self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "point",
                                                    "options": pv_drivers}})
                self.stitch_cmds.append({"follow": {"driving": pack_pv_control, "cns_type": "orient",
                                                    "options": pv_drivers}})
                self.stitch_cmds.append({"follow": {"driving": pack_fk_controls[0], "cns_type": "orient",
                                                    "options": cog_drivers[1:]}})
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "dv": parent_ground_ctrl, "options": cog_drivers}})
        
        elif parent_build_type.startswith("Spine"):
            # - Follow attrs
            parent_control = parent_obj.end_ctrl.control if pack_obj.is_arm else parent_obj.start_ctrl.control
            if not pack_obj.is_arm:
                self.stitch_cmds.append({"follow": {"driving": pack_fk_controls[0], "cns_type": "orient",
                                                    "dv": parent_control, "options": parent_control}})
            ik_drivers = [parent_control]
            if pack_obj.is_arm:
                ik_drivers.append(parent_obj.start_ctrl.control)
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": ik_drivers}})
            
            # - Finishing the end autoaim
            self.stitch_cmds.append({"parent" : {"child" : pack_autoaim_origin_grp, "parent" : parent_control}})
        
        elif parent_build_type.startswith("Head"):
            parent_control = parent_obj.ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_ik_end_control, "cns_type": "parent",
                                                "options": parent_control}})
