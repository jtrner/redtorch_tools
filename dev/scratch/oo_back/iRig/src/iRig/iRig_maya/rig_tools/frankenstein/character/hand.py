import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.frankenstein.utils as rig_frankenstein_utils
from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.core.fk_chain import Build_FkChain

import rig_tools.utils.joints as rig_joints


class Build_Hand(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        self.joint_radius *= 0.5
        
        # :note: Orient Joints ONLY works with "yzx" or "xyz". If using another, need to adjust the code in Build_Hand()
        self.base_joints_hand = None
        self.base_joints_roots = None

        # Set the pack info
        self.joint_names = ["thumb", "index", "middle", "ring", "pinky"]
        self.side = "L"
        self.description = "Hand"
        self.length = 5
        self.length_max = 5
        self.base_joint_positions = [[2.99, 5.14, -0.1], #[33.5, 60.0, 2.0], 
                                     [3.0, 5.24, -0.18], #[34.25, 60.0, 1.0], 
                                     [2.98, 5.28, -0.32], #[34.25, 60.0, 0.0], 
                                     [2.97, 5.28, -0.45], #[34.25, 60.0, -1.0], 
                                     [2.97, 5.25, -0.59], #[34.25, 60.0, -2.0]
                                     ]
        # :note: These ^ are just the base fingers. Rest made in create_pack()
        self.chain_indexes = [0, 1, 2, 3, 4]
        self.chain_lengths = [3, 4, 4, 4, 4]
        self.chain_inc = [0.35, 0, 0]  # Increment of each chain in [x, y, z]
        self.accepted_stitch_types = ["Arm_Watson", "Arm"]

    def _class_prompts(self):
        self.prompt_info["chain_lengths"] = {"type": "text", "text": ", ".join([str(i) for i in self.chain_lengths])}

    def _create_pack(self):
        # Make / Find hand joint
        if not self.is_mirror:
            self.base_joints_hand = i_node.create("joint", name=self.base_name)
            if self.top_base_joint_position:
                self.base_joints_hand.xform(t=self.top_base_joint_position, ws=True)
            else:
                i_node.copy_pose(driver=self.base_joints_roots, driven=self.base_joints_hand)
                # - Orient so hand is actually matching world
                jo = [0, 0, 0]
                if self.orient_joints == "yzx":
                    jo = [-90, -90, 0]
                self.base_joints_hand.jo.set(jo)
        else:
            self.base_joints_hand = self.base_joints_roots[0].relatives(0, p=True, type="joint")
        
        # Rename base joints
        if not self.is_mirror:
            for jnt in self.base_joints_roots:
                jnt.rename(jnt.replace("_Start", "_Meta"))
        
        # Parent hand to group
        self.base_joints_hand.set_parent(self.pack_grp)
        self.base_joints_hand.radius.set(self.joint_radius)
        self.top_base_joint = self.base_joints_hand

        # Parent fixing
        if not self.is_mirror:
            i_utils.parent(self.base_joints_roots, self.base_joints_hand)
        
        # # Rotate Thumb
        # if not self.top_base_joint_position:  # Positions were not loaded from Packs IO
        #     if len(self.base_joints_roots) == 5:  # Assume human hand
        #         self.base_joints_roots[0].rx.set(70)
        #         self.base_joints_roots[0].rz.set(-30)

        # Clear selection
        i_utils.select(cl=True)

        # # Orient Hand Fixing
        # self.base_joints_hand.jo.set([0, 0, 0])
        # # for root in self.base_joints_roots:
        # #     root.jo.set([0, 0, 0])
        # i_utils.select(cl=True)
    
    def create_controls(self):
        # Root Ctrl
        fs = [0, 0, 0]
        if self.orient_joints == "xyz":
            pass
        elif self.orient_joints == "yzx":
            fs = [90, 0, 0]
        if self.is_mirror:
            fs[["x", "y", "z"].index(self.orient_joints[0])] = 180
        # fs = [180, 0, 0] if self.is_mirror else [0, 0, 0]
        self.hand_root_ctrl = i_node.create("control", control_type="3D Pin Cube", name=self.base_name, color=self.side_color, 
                                            size=self.ctrl_size, position_match=self.base_joints_hand, match_rotation=True,
                                            parent=self.pack_grp, with_gimbal=False, flip_shape=fs, # Keep scalable
                                            rotate_order="zyx")
        
        # Make scalable with rig
        if self.scale_attr:
            i_attr.connect_attr_3(self.scale_attr, self.hand_root_ctrl.top_tfm.s)
        
        # Finger Controls
        self.finger_root_ctrls = []
        # - Vars based on orientation
        move_shape_val = (self.pack_size * 0.25 * self.side_mult)
        move_shape = [0, 0, 0]
        front_cvs = []
        back_cvs = []
        move_cv_i = None
        if self.orient_joints == "xyz":
            move_shape[1] = move_shape_val
            front_cvs = [1, 2]
            back_cvs = [0, 3, 4]
            move_cv_i = 0
        elif self.orient_joints == "yzx":
            move_shape[2] = move_shape_val
            front_cvs = [2, 3]
            back_cvs = [0, 1, 4]
            move_cv_i = 1
        # - Loop
        for i, finger in enumerate(self.base_joints_roots):
            fk_pack = Build_FkChain()
            fk_pack.build_type = self.build_type
            fk_pack.side = self.side
            fk_pack.description = self.description + "_" + self.joint_names[i].capitalize()
            fk_pack.base_name = fk_pack.side + "_" + fk_pack.description
            fk_pack.direct_connect = False
            fk_pack.tweak = False
            # fk_pack.tweak_vis = self.hand_root_ctrl.control
            # fk_pack.tweak_ctrl_color = "purple"
            fk_pack.main_ctrl_type = "2D Square"
            fk_pack.main_ctrl_color = self.side_color
            fk_pack.pack_info_node = self.pack_info_node
            fk_pack.pack_grp = self.pack_grp
            fk_pack.pack_size = self.pack_size
            fk_pack.ctrl_size = (self.ctrl_size * 0.25)
            fk_pack.ctrl_size_mult = 0.6
            fk_pack.flip_shape = fs
            fk_pack.move_shape = move_shape
            fk_pack.first_ctrl_name = "Meta"
            fk_pack.end_ctrl_name = "End"
            # fk_pack.build_is_inherited = True
            fk_pack.build_is_subbuild = True
            # Redefine base joints so FkChain builds on just that finger
            fk_pack.base_joints = getattr(self, "base_joints_chain_%i" % i)
            fk_pack.do_orient_joints = False if i == 0 else True  # False
            fk_pack.do_stitch = self.do_stitch
            # Build
            fk_pack.create_bit()
            self.finger_root_ctrls.append(fk_pack.root)
            # Parent under Hand Control
            fk_pack.root.top_tfm.set_parent(self.hand_root_ctrl.last_tfm)
            # Redefine base joints, which have had their names updated
            setattr(self, "base_joints_chain_%i" % i, fk_pack.base_joints)
            # Move Cvs of control to stretch to next joint
            for i, jnt in enumerate(fk_pack.base_joints[:-1]):
                # - Vars
                ctrl = fk_pack.fk_ctrls[i].control
                ctrl_shape = ctrl.relatives(0, s=True)
                front_move_i = fk_pack.base_joints[i + 1].attr("t" + self.orient_joints[0]).get() * 0.75
                if i == 0:
                    front_move_i = fk_pack.base_joints[i + 2].attr("t" + self.orient_joints[0]).get() * 0.75
                back_move = [0, 0, 0]
                back_move[move_cv_i] = 0.5
                front_move = [0, 0, 0]
                front_move[move_cv_i] = front_move_i
                # - Move
                for cv in front_cvs:
                    i_utils.xform(front_move, ctrl_shape + ".cv[%i]" % cv, r=True, os=True, as_fn="move")
                for cv in back_cvs:
                    i_utils.xform(back_move, ctrl_shape + ".cv[%i]" % cv, r=True, os=True, as_fn="move")

    def _cleanup_bit(self):
        # Declare bind joints
        self.bind_joints = self._get_all_base_joints()
        
        # Lock and Hide
        # None to do at this time.
        
        # Parent bind joints
        self.base_joints_hand.set_parent(self.pack_bind_jnt_grp)
        
        # Turn off inherit transform on bind joint group
        self.pack_bind_jnt_grp.inheritsTransform.set(0)
        
        # # Turn of scale compensate so globally scales properly
        # all_joints = self._get_all_base_joints()
        # for jnt in all_joints:
        #     jnt.segmentScaleCompensate.set(0)

    def connect_elements(self):
        i_constraint.constrain(self.hand_root_ctrl.control, self.base_joints_hand, mo=True, as_fn="parent")
        i_constraint.constrain(self.hand_root_ctrl.control, self.base_joints_hand, mo=True, as_fn="scale")

        self.hand_root_ctrl.top_tfm.set_parent(self.pack_ctrl_grp)

    def _presetup_bit(self):
        # Turn off override orient
        # :note: Cannot orient top joint because of the thumb. Will need to use rigger's placement. Fk chains will orient everything else
        self.do_orient_joints = False
    
    def _create_bit(self):
        # Force Hand to be single item
        if isinstance(self.base_joints_hand, list):
            self.base_joints_hand = self.base_joints_hand[0]

        # Create
        self.create_controls()

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        parent_wrist_jnt = parent_obj.base_joints[-1]
        pack_root_ctrl_top = pack_obj.hand_root_ctrl.top_tfm
        
        # Stitch
        if parent_build_type.startswith("Arm"):
            # i_constraint.constrain(parent_wrist_jnt, pack_root_ctrl_top, mo=True, as_fn="parent")
            self.stitch_cmds.append({"constrain": {"args": [parent_wrist_jnt, pack_root_ctrl_top], "kwargs": {"mo": True, "as_fn": "parent"}}})
