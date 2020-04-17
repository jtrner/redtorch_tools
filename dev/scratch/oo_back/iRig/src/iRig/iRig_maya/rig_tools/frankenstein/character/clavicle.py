import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.nodes as rig_nodes

from rig_tools.frankenstein.core.master import Build_Master


class Build_Clavicle(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        self.joint_radius *= 0.75

        self.build_is_inherited = False
        self.rotate_order = "yzx"
        self.orient_joints_up_axis = "zup"  # To match arms

        # Set the pack info
        self.joint_names = ["base"]
        self.side = "L"
        self.description = "Clavicle"
        self.length_max = 1
        self.base_joint_positions = [[0.2, 5.13, -0.13]] # [[0.0, 60.0, 0.0]]
        self.accepted_stitch_types = ["Spine_IkFk", "Spine_Simple", "Cog"]

    def _class_prompts(self):
        self.prompt_display_info["is_hip"] = "build_is_inherited"
    
    def _create_pack(self):
        if self.orient_joints_up_axis == "yup":
            return  # This is world-matching, which is default

        if self.do_pack_positions:
            jo_set = None
            if self.build_type == "Clavicle":
                jo_set = {"zup" : [-90 * self.side_mult, -90 * self.side_mult, 0]}.get(self.orient_joints_up_axis)
            elif self.build_type == "Hip":
                if self.is_mirror:
                    jo_set = {"zup" : [180, 0, 180]}.get(self.orient_joints_up_axis)
                else:
                    jo_set = {"zup" : [0, 0, -180]}.get(self.orient_joints_up_axis)
            
            if not jo_set:
                i_utils.error("%s manual joint orient not configured for '%s'" % (self.build_type, self.orient_joints_up_axis))

            self.base_joints[0].jo.set(jo_set)
    
    def create_controls(self):
        # Create main control
        rx = 180 if self.is_mirror else 0
        flip_shape = None
        tweak_flip = None
        control_rot = None
        if self.orient_joints_up_axis == "yup":
            flip_shape = [-1 * rx, 0, 0]
            tweak_flip = [0, 0, -90 * self.side_mult]
            control_rot = [rx, 0, 0]
        elif self.orient_joints_up_axis == "zup":
            if self.build_type == "Clavicle":
                flip_shape = [90 * self.side_mult, 0, 90 * self.side_mult]
            elif self.build_type == "Hip":
                flip_shape = [0, 0, 0] if self.is_mirror else [180, 0, 0]
                tweak_flip = [0, 0, -90]
        self.ctrl = i_node.create("control", control_type="3D Crescent", color=self.side_color, size=self.ctrl_size,
                                  with_gimbal=False, position_match=self.base_joints[0], 
                                  name=self.base_name, follow_name=self.description, flip_shape=flip_shape,
                                  parent=self.pack_grp, r=control_rot, rotate_order=self.rotate_order)
        # Create tweaks
        self.tweak_ctrls += rig_controls.create_tweaks(joints=self.base_joints, size=self.tweak_ctrl_size, 
                                                       flip_shape=tweak_flip, r=control_rot, match_rotation=True)
        tweak_tops = [ctrl.top_tfm for ctrl in self.tweak_ctrls]
        tweak_grp = self._create_subgroup(name="Tweak_Ctrl", parent=self.ctrl.last_tfm, children=tweak_tops)
        
        # Drive visibility of tweaks with ctrl
        i_attr.create_vis_attr(node=self.ctrl.control, ln="TweakCtrls", drive=tweak_grp)

    def _cleanup_bit(self):
        # Joint parenting
        self.base_joints[0].set_parent(self.pack_bind_jnt_grp)
        
        # Connect Rig Joint Vis
        self.joint_vis_objs += self.rig_joints

        # Lock and Hide
        i_attr.lock_and_hide(self.ctrl.control, attrs=["s"], lock=True, hide=True)

    def connect_elements(self):
        # Vars
        clav_control = self.ctrl.control
        tweak0_ctrl = self.tweak_ctrls[0].control
        # tweak1_ctrl = self.tweak_ctrls[1].control

        # Freeze Transforms
        self.pack_rig_jnt_grp.freeze(apply=True)

        # Constraints
        i_constraint.constrain(tweak0_ctrl, self.base_joints[0], mo=True, as_fn="parent")
        # i_constraint.constrain(tweak1_ctrl, self.base_joints[1], mo=True, as_fn="parent")

        i_constraint.constrain(self.rig_joints[0], self.tweak_ctrls[0].offset_grp, mo=True, as_fn="parent")
        # i_constraint.constrain(self.rig_joints[1], self.tweak_ctrls[1].offset_grp, mo=True, as_fn="parent")

        i_constraint.constrain(clav_control, self.rig_joints[0], mo=True, as_fn="point")
        i_constraint.constrain(self.ctrl.cns_grp, self.pack_rig_jnt_grp, mo=True, as_fn="parent")

        i_constraint.constrain(clav_control, self.rig_joints[0], mo=True, as_fn="orient")

        # Base Joint Scale
        tweak0_ctrl.s.drive(self.base_joints[0].s)
        # tweak1_ctrl.s.drive(self.base_joints[1].s)
        
        # # Rotate whole control/tweak/joint setup
        # self.ctrl.top_tfm.rz.set(-45 * self.side_mult)

    def _create_bit(self):
        # Create
        self.rig_joints = rig_joints.duplicate_joints(joints=self.base_joints, add_suffix="Rig")
        self.create_controls()

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_control = pack_obj.ctrl.control
        is_hip = pack_obj.build_is_inherited

        # Stitching to Spine?
        if parent_build_type.startswith("Spine"):
            # - Get parent control to use
            parent_end_control = parent_obj.start_ctrl.last_tfm if is_hip else parent_obj.end_ctrl.last_tfm
            # - Stitch
            self.stitch_cmds.append({"constrain" : {"args" : [parent_end_control, pack_obj.pack_rig_jnt_grp],
                                                    "kwargs" : {"mo" : True, "as_fn" : "parent"}}})
            self.stitch_cmds.append({"parent" : {"child" : pack_obj.pack_grp, "parent" : parent_end_control}})
            self.stitch_cmds.append({"constrain" : {"args" : [parent_end_control, pack_obj.pack_bind_jnt_grp],
                                                    "kwargs" : {"mo" : True, "as_fn" : "parent"}}})
            if not is_hip:  # Clavicle
                self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                    "dv": parent_end_control, "options": [parent_end_control]}})
        
        elif parent_build_type == "Cog":
            if is_hip:
                return 
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            opts = [parent_ground_ctrl, parent_root_ctrl]
            self.stitch_cmds.append({"follow" : {"driving" : pack_control, "cns_type" : "orient", "options" : opts}})
