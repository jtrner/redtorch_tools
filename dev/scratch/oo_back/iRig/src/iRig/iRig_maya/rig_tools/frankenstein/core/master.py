import maya.cmds as cmds
import collections
import cPickle as pickle
import traceback

import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools.frankenstein import RIG_F_LOG

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.nodes as rig_nodes
import rig_tools.frankenstein.utils as rig_frankenstein_utils


class Build_Master(object):
    def __init__(self):
        # Declare on instantiating
        self.side = "C"
        self.description = "Master"
        # - Optional
        self.ctrl_size = 1.0
        self.tweak_ctrl_size = self.ctrl_size * 0.5
        self.orient_joints = "yzx"  # Most packs with: "yzx" or "xyz"
        self.orient_joints_up_axis = "yup"
        self.do_orient_joints = True  # Actual do orienting? False when mirror to keep behaviour
        self.pack_size = 1.0
        self.joint_radius = 0.25
        self.ikfk_switch_mirror_offset = True
        self.ikfk_default_mode = 1
        self.build_is_inherited = False  # Just inheriting the class (so it doesn't make extra Info node / pack setup)
        self.build_is_subbuild = False  # This build is used inside the main build (so it doesn't requery build data, but uses given instead)
        self.chain_indexes = []
        self.chain_lengths = []
        self.chain_inc = []
        self.pack_joints = None  # Result from create_pack_joints {"name" : "joint"}
        self.do_stitch = True
        
        # Defaults (used for UI building)
        self.length = 1  # originally named "default length"
        self.length_min = 1  # originally named "minimum length"
        self.length_max = None  # originally named "maximum length"
        self.add_length = 0
        self.restricted_sides = None
        self.joint_names = []
        self.base_joint_positions = None  # List of each joint's xyz position [[a_x, a_y, a_z], [b_x, b_y, b_z]]
        self.prompt_info = {}
        
        # Store some backup defaults
        self.original_joint_radius = self.joint_radius
        self.original_ctrl_size = self.ctrl_size

        # Declare for now. Populate later
        self.side_mult = 1.0
        self.bit_built = False
        self.is_mirror = False
        self.is_mirror_sym = False
        self.pack_grp = None
        self.pack_info_node = None
        self.build_pack_grp = None
        self.base_joints = []
        self.base_joints_roots = []  # Just used for builds that have chains to define the root joints
        self.base_joints_chains = []  # List of lists of chain children only [[a1_jnt, a2_jnt], [b1_jnt, b2_jnt]]
        self.base_joints_full_chains = []  # List of lists of chain root and children [[a0_jnt, a1_jnt, a2_jnt], [b0_jnt, b1_jnt, b2_jnt]]
        self.base_joints_chain_positions = []  # List mimicking base_joint_positions [[[a0_x, a0_y, a0_z], [a1_x, a1_y, a2_z]], [[b1_x, b1_y, b1_z]]]
        self.do_pack_positions = True  # Set to False when given base_joints_positions that should not be adjusted in create_pack() (ex: Deconstruct / Packs IO)
        self.bend_joints = []
        self.bind_joints = []
        self.created_joints = []
        self.created_controls = []
        self.created_nodes = []
        self.tweak_ctrls = []
        self.ground_gimbal_control = None
        self.scale_attr = None
        self.ctrl_grp = None
        self.pack_ctrl_grp = None
        self.ikfk_switch_control = None
        self.top_node = None
        self.control_vis_driven = []
        self.mirror_driver = None
        self.top_base_joint = None
        self.top_base_joint_position = []
        self.ik_ctrls = []
        self.fk_ctrls = []
        self.ik_joints = []
        self.fk_joints = []
        self.side_color = "yellow"
        self.side_color_scndy = "yellow"
        self.side_color_tertiary = "yellow"
        self.loc_size = [1.0, 1.0, 1.0]
        self.pack_extras = []
        self.pack_extras_positions = {}
        self.default_hierarchy = []
        self.utility_vis_objs = []
        self.joint_vis_objs = []

        self.pack_utility_grp = None
        self.pack_utility_cns_grp = None
        self.pack_bind_jnt_grp = None
        self.pack_rig_jnt_grp = None
        self.pack_ctrl_grp = None
        
        # Stitching
        self.stitch_cmds = []
        self.accepted_stitch_types = []
        self.consolidate_ik_fk_switch = False
        self.consolidate_ik_fk_switch_to_child = False
        
        # Get import information
        self.imp_module = self.__module__
        self.imp_class = self.__class__.__name__
        self._non_override_attrs = ["do_stitch", "do_orient_joints", "do_pack_positions", "accepted_stitch_types",
                                    "side_color", "side_color_scndy", "side_color_tertiary"]
        # :note: Need to not override these ^ using pickle-stored info or class instance overrides will mean nothing

        # Get build type
        self.build_type = self.imp_class.split("Build_")[1]
        
        # Master-Level Prompt info
        self.prompt_info = collections.OrderedDict()
        self.prompt_display_info = collections.OrderedDict()
        
        # Misc
        self.ikfk_switch_control_type = "2D Twist Gear"
        self.ikfk_switch_control_color = "black"
        self.ikfk_switch_name = "IKFKSwitch"
    
    def _class_prompts(self):
        return   # Optional for classes
    
    def get_prompt_info(self):
        # Master Prompt (changeable) Info
        self.prompt_info["do_orient_joints"] = {"type": "checkBox", "value": self.do_orient_joints}
        self.prompt_info["orient_joints"] = {"type": "option", "menu_items": ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"], "value": self.orient_joints}
        self.prompt_info["orient_joints_up_axis"] = {"type": "option", "menu_items": ["xup", "xdown", "yup", "ydown", "zup", "zdown"], "value": self.orient_joints_up_axis}
        self.prompt_info["pack_size"] = {"type": "float", "value": self.pack_size, "min": None, "max": None}
        self.prompt_info["ctrl_size"] = {"type": "float", "value": self.ctrl_size, "min": None, "max": None}
        self.prompt_info["joint_radius"] = {"type": "float", "value": self.joint_radius, "min": None, "max": None}
        self.prompt_info["ikfk_default_mode"] = {"type": "int", "value": self.ikfk_default_mode, "min": 0, "max": 1}
        
        # Master Prompt (display-only) Info
        self.prompt_display_info["length"] = "length"
        self.prompt_display_info["joint_names"] = "joint_names"
        
        # Inherited by class
        self._class_prompts()

    def __check(self):
        # Given values needed?
        i_utils.check_arg(self.side, "side")
        i_utils.check_arg(self.description, "description")
        
        # Side formatting / valid?
        if not self.side or self.side == "None":
            self.side = ""
        else:
            self.side = self.side.capitalize()  # If its len() is 1, it makes it uppercase. Else makes first letter upper, rest lower. So it works regardless.
        accepted_sides = ["L", "R", "C", "M", "", "Fr", "Bk", "Upr", "Lwr"]  # Also accepts nothing
        if self.side and (self.side not in accepted_sides):
            i_utils.error("Pack side must be one of the following: %s. Not %s." % (", ".join(accepted_sides), self.side))
        
        # Description Formatting
        if " " in self.description:
            self.description = "".join([pd[0].upper() + pd[1:] for pd in self.description.split(" ")])
        self.description = self.description[0].upper() + self.description[1:]
    
    def __set_vars(self):
        # Get Side Mult
        self.side_mult = -1.0 if self.side.upper() == "R" else 1.0

        # Get Colors
        side_longname = "center"
        if self.side == "L":
            side_longname = "left"
        elif self.side == "R":
            side_longname = "right"
        color_info = i_node.get_default("CtrlColorSide")
        self.side_color = color_info.get(side_longname)
        self.side_color_scndy = color_info.get(side_longname + "_secondary")
        self.side_color_tertiary = color_info.get(side_longname + "_tertiary")

        # Get the pack base name
        self.base_name = ""
        if self.side:
            self.base_name += self.side + "_"
        self.base_name += self.description
        
        # Node Names
        self.info_node_name = self.base_name + "_Info"
        self.pack_grp_name = self.base_name + "_Grp"
        self.ikfk_switch_name = self.base_name + "_IKFKSwitch"
        
        # # Force some py obj types
        # for ls_type in ["joint_names", "chain_indexes", "chain_lengths", "chain_inc"]:
        #     curr = getattr(self, ls_type)
        #     if not isinstance(curr, (list, tuple)):
        #         new = [curr] if curr else []
        #         setattr(self, ls_type, new)
        
        # Control Size
        self.ctrl_size = float(self.ctrl_size)
        self.tweak_ctrl_size = self.ctrl_size * 0.5
        
        # Build Structure
        if self.build_is_subbuild:
            self.build_is_inherited = True
        
        # Force some py obj types
        for class_attr in ["joint_names", "chain_indexes", "chain_lengths", "chain_inc"]:
            curr = getattr(self, class_attr)
            if not isinstance(curr, (list, tuple)):
                new = [curr] if curr else []
                setattr(self, class_attr, new)
        # if self.chain_indexes and not isinstance(self.chain_indexes, (list, tuple)):
        #     self.chain_indexes = [self.chain_indexes]
        # if self.chain_lengths and not isinstance(self.chain_lengths, (list, tuple)):
        #     self.chain_lengths = [self.chain_lengths]
        # if self.chain_inc and not isinstance(self.chain_inc, (list, tuple)):
        #     self.chain_inc = [self.chain_inc]

    def _create_subgroup(self, name="", parent="", xform_driver="", xform_attrs=None, zero_out=False, children=None,
                         add_base_name=True, use_existing=True, grp_suffix=True):
        if add_base_name and not name.startswith(self.base_name + "_"):
            name = self.base_name + "_" + name
        if not name.endswith("_Grp") and grp_suffix:
            name += "_Grp"
        grp = i_node.create("transform", n=name, keep_suffix="_Grp" if grp_suffix else None, use_existing=use_existing)
        if grp.existed and use_existing:
            return grp
        self.created_nodes.append(grp)
        # exists = i_utils.check_exists(name)
        # if exists and use_existing:
        #     grp = i_node.Node(name)
        # elif exists and not use_existing:
        #     grp = i_node.create("transform", n=i_node.get_unique_name(name, keep_suffix="_Grp" if grp_suffix else None))
        # else:
        #     grp = i_node.create("transform", n=name)
        if not parent and parent != "world":
            parent = self.pack_grp
            if not self.pack_grp:  # Super rare
                parent = self.build_pack_grp
        if parent == "world":
            parent = None
        if parent:
            if not i_utils.check_exists(parent):
                i_utils.error("'%s' does not exist. Cannot parent '%s' to it." % (parent, grp))
            parent = i_node.Node(parent)
            if not parent.node_type() == "transform":
                i_utils.error("'%s' is not a transform. Cannot parent '%s' to it." % (parent, grp))
            grp.set_parent(parent)

        if xform_driver:
            if not xform_attrs:
                xform_attrs = ["t", "r", "s"]
            i_node.copy_pose(driver=xform_driver, driven=grp, attrs=xform_attrs)
            if zero_out:
                grp.zero_out()
        else:
            grp.zero_out()

        i_utils.select(cl=True)

        if children:
            i_utils.parent(children, grp)

        i_utils.select(cl=True)

        return grp
    
    def __create_hierarchy(self):
        # Build Pack Group
        self.build_pack_grp = i_node.create("transform", n="BuildPack_Grp", use_existing=True)
        if not self.build_pack_grp.existed:
            i_attr.lock_and_hide(node=self.build_pack_grp, attrs=["t", "r", "s", "v"], lock=True, hide=True)

        # Get Rig's Top Node
        if not self.top_node:
            self.top_node = rig_nodes.get_top_group(raise_error=False)
        top_parent = self.top_node or "world"
        
        # Rig Hierarchy
        self.jnt_grp = self._create_subgroup(name="Jnt", add_base_name=False, parent=top_parent)
        self.bind_jnt_grp = self._create_subgroup(name="Bind_Jnt", add_base_name=False, parent=self.jnt_grp)
        self.rig_jnt_grp = self._create_subgroup(name="Rig_Jnt", add_base_name=False, parent=self.jnt_grp)
        self.utility_grp = self._create_subgroup(name="Utility", add_base_name=False, parent=top_parent)
        self.utility_cns_grp = self._create_subgroup(name="Utility_Cns", add_base_name=False, parent=self.utility_grp)
        self.ctrl_grp = self._create_subgroup(name="Ctrl", add_base_name=False, parent=top_parent)
        self.ctrl_cns_grp = self._create_subgroup(name="Ctrl_Cns", add_base_name=False, parent=top_parent)
        self.helper_grp = self._create_subgroup(name="Helper_Geo", add_base_name=False, parent=top_parent)
        if self.top_node:
            i_node.connect_to_info_node(node=self.top_node, info_attribute="RigHierarchy", 
                                        objects=[self.jnt_grp, self.bind_jnt_grp, self.rig_jnt_grp, self.utility_grp,
                                                 self.utility_cns_grp, self.ctrl_grp, self.ctrl_cns_grp, self.helper_grp,
                                                 self.build_pack_grp])

        # Individual Build Pack Group
        self.pack_grp = i_node.create("transform", n=self.pack_grp_name, use_existing=True)
        if not self.pack_grp.existed:
            self.pack_grp.set_parent(self.build_pack_grp)

        # Pack Rig Hierarchy Groups
        self.pack_utility_grp = self._create_subgroup(name="Utl", parent=self.utility_grp)
        self.pack_utility_cns_grp = self._create_subgroup(name="Utl_Cns", parent=self.utility_cns_grp)
        self.pack_bind_jnt_grp = self._create_subgroup(name="Bind_Jnt", parent=self.bind_jnt_grp)
        self.pack_rig_jnt_grp = self._create_subgroup(name="Rig_Jnt", parent=self.rig_jnt_grp)
        self.pack_ctrl_grp = self._create_subgroup(name="Ctrl", parent=self.ctrl_grp)
        
        # Pack Info Node
        self.pack_info_node = i_node.create("transform", n=self.info_node_name, parent=self.pack_utility_grp, use_existing=True)
        if not self.pack_info_node.existed:
            i_attr.lock_and_hide(self.pack_info_node, attrs=["t", "r", "s", "v"], lock=True, hide=True)
        
        # Note these are the default groups (for easier filtering)
        self.default_hierarchy = [self.pack_grp, self.pack_utility_grp, self.pack_utility_cns_grp, self.pack_bind_jnt_grp,
                                  self.pack_rig_jnt_grp, self.pack_ctrl_grp, self.pack_info_node]
    
    def __assign_base_joints(self):
        # Check
        pack_joints_exist = True
        if self.pack_joints:
            for pj in self.pack_joints.values():
                if not isinstance(pj, (list, tuple)):  # Chains are lists
                    pj = [pj]
                for pack_jnt in pj:
                    if not i_utils.check_exists(pack_jnt):
                        pack_joints_exist = False
                        break
        if not self.pack_joints or not pack_joints_exist:
            calc = False if self.pack_joints or not self.do_pack_positions else True  # If expected to be found, positions are already considered
            self.pack_joints = rig_frankenstein_utils.create_pack_joints(pack_obj=self, calculate=calc)
        root_keys = [k for k in self.pack_joints.keys() if not k.endswith("_chain")]
        if not self.joint_names or (len(self.joint_names) == 1 and len(root_keys) > 1):
            # :note: This is for either when there's no joint names or if define one joint name to be incremented on all pack joints
            self.joint_names = root_keys
        
        # Get base joints
        # - Reset first
        self.base_joints = []
        if self.chain_indexes:
            self.base_joints_chains = []
            self.base_joints_full_chains = []
            # - Find
        for i, joint_label in enumerate(self.joint_names):
            base_jnt = self.pack_joints.get(joint_label)
            chain_children = i_utils.convert_data(self.pack_joints.get(joint_label + "_chain"), to_generic=False)
            if not base_jnt:
                if self.joint_names.index(joint_label) < self.length:
                    RIG_F_LOG.warn("No joint found for label: '%s'" % joint_label)
                continue
            base_jnt = i_node.Node(base_jnt)  # for Packs IO
            # - Renaming
            if not self.is_mirror:
                # - Name Root joint
                joint_name = self.base_name
                if joint_label.lower() != self.description.lower():
                    joint_name += "_" + joint_label[0].upper() + joint_label[1:]
                if chain_children:
                    joint_name += "_Start"
                base_jnt.rename(joint_name)
                # - Name Chain joints
                if chain_children:
                    chain_base_name = joint_name.replace("_Start", "")
                    chain_end_ind = self.chain_lengths[i] - 1
                    for j, child in enumerate(chain_children):
                        name_suff = "End" if j == chain_end_ind else str(j).zfill(2)
                        child.rename(chain_base_name + "_" + name_suff)
            # - Add to lists
            self.base_joints.append(base_jnt)
            if chain_children:
                self.base_joints_chains.append(chain_children)  # :note: Do not include the root for sake of base_joints_chains_positions setting
                self.base_joints_full_chains.append([base_jnt] + chain_children)
                setattr(self, "base_joints_chain_%i" % i, [base_jnt] + chain_children)

        # Reassign so var easier to understand in class
        if self.chain_indexes:
            self.base_joints_roots = self.base_joints
        
        # Get all joints
        all_joints = self._get_all_base_joints()
        
        # Set Radius
        if self.joint_radius != 1.0:
            for jnt in all_joints:
                jnt.radius.set(self.joint_radius)
        
        # Parent top joint
        # :note: Unless top joint is under another joint (manually parented in create_pack - for mirrors)
        top_joints = self.base_joints_roots or [self.base_joints[0]]
        for top_jnt in top_joints:
            is_parent_jnt = top_jnt.relatives(0, p=True, type="joint")
            if not is_parent_jnt:
                top_jnt.set_parent(self.pack_grp)
        
        # Orient
        if self.do_orient_joints and not self.is_mirror:
            rig_joints.orient_joints(joints=all_joints, orient_as=self.orient_joints,
                                     up_axis=self.orient_joints_up_axis, force_last_joint=True)
            if self.base_joints_chains:
                # :note: Re-force each chain end as 0 orientation because orient_joints()'s force last is just for last in total list
                chain_ends = [chn_ls[-1] for chn_ls in self.base_joints_chains]
                for chain_end_jnt in chain_ends:
                    chain_end_jnt.jo.set([0, 0, 0])
        else:
            RIG_F_LOG.debug("Not orienting joints for '%s'." % self.base_name)
    
    def _get_all_base_joints(self, ignore_joints=None):
        # Vars
        all_joints = []
        
        # Check
        if not self.base_joints:  # No base joints, means no joints at all
            RIG_F_LOG.info("No base joints defined")
            return all_joints
        
        # Base Joints
        all_joints += self.base_joints
        
        # Top Joint
        if self.top_base_joint and self.top_base_joint not in self.base_joints:
            all_joints.insert(0, self.top_base_joint)
        
        # Chain Joints
        if self.base_joints_chains:
            for chn_ls in self.base_joints_chains:
                all_joints += chn_ls

        # Ignore
        if ignore_joints:
            good_joints = [jnt for jnt in all_joints if jnt not in ignore_joints]
            all_joints = good_joints

        # Consolidate while keeping order
        all_joints = logic_py.consolidate_list_in_order(all_joints)
        
        return all_joints
    
    def _update_position_data(self):
        # Base Joints
        base_joint_positions = []
        for base_joint in self.base_joints:
            i_utils.check_exists(base_joint, raise_error=True)
            base_joint_positions.append([round(i, 4) for i in base_joint.xform(q=True, t=True, ws=True)])
        self.base_joint_positions = base_joint_positions
        
        # Top Joint
        if self.top_base_joint and self.top_base_joint not in self.base_joints:
            self.top_base_joint_position = [round(i, 4) for i in self.top_base_joint.xform(q=True, t=True, ws=True)]

        # Chain Joints
        if self.base_joints_chains:
            base_joints_chain_positions = []
            for chn_ls in self.base_joints_chains:
                chn_positions = []
                for chn_jnt in chn_ls:
                    chn_positions.append([round(i, 4) for i in chn_jnt.xform(q=True, t=True, ws=True)])
                base_joints_chain_positions.append(chn_positions)
            self.base_joints_chain_positions = base_joints_chain_positions
        
        # Pack Non-base-joint items
        if self.pack_extras:
            self.pack_extras = i_utils.convert_data(self.pack_extras, to_generic=False)
            for extra in self.pack_extras:
                if not isinstance(extra, (i_node.Node, i_node._Node)):
                    continue
                self.pack_extras_positions[extra] = {"t" : extra.xform(q=True, t=True, ws=True)}
                if extra.is_dag():
                    self.pack_extras_positions[extra]["r"] = extra.r.get()
                    self.pack_extras_positions[extra]["s"] = extra.s.get()
    
    def _store_build_data(self, info_node=None, include_class_data=True, additional_data=None):
        # Vars
        build_data = {}
        if not info_node:
            info_node = self.pack_info_node
        
        # Get existing
        if additional_data and not include_class_data and i_utils.check_exists(info_node + ".build_data"):
            data_as_str = self.pack_info_node.build_data.get()
            build_data = pickle.loads(str(data_as_str))
        
        # Class attrs
        if include_class_data:
            # - Pack-Specific positions
            if not self.bit_built:
                self._update_position_data()
            # - Update
            build_data.update(self.__dict__.copy())
        
        # Additional Data
        if additional_data:
            build_data.update(additional_data)
        
        # Store remaining as an info node attr
        try:
            build_data_pickle = pickle.dumps(build_data)
        except pickle.PicklingError as e:
            msg = "Cannot pickle build data for %s." % self.base_name
            if e == "Can't pickle <class 'icon_api.node._Node'>: it's not the same object as icon_api.node._Node":
                i_utils.error(msg + " i_node was reloaded and sometimes pickle doesn't like it. Try re-clearing scene_nodes.")
            else:
                i_utils.error("%s\n\n%s" % (msg, e))
            return
        i_attr.create(node=info_node, ln="build_data", at="string", dv=str(build_data_pickle), l=True, use_existing=True)
    
    def __get_build_data(self):
        data_as_str = self.pack_info_node.build_data.get()
        data_eval = pickle.loads(str(data_as_str))
        for cls_attr, cls_val in data_eval.items():
            if cls_attr in self._non_override_attrs:
                continue
            setattr(self, cls_attr, cls_val)
    
    def _get_pack_object(self, pack_info_node):
        # Var
        if not pack_info_node:
            pack_info_node = self.pack_info_node

        # # Store local overrides that should not be changed from the pickle data
        # local_overrides = {}
        # if pack_info_node == self.pack_info_node:
        #     for k in self._non_override_attrs:
        #         local_overrides[k] = getattr(self, k)
        #         print "Start - ", k, ">>", getattr(self, k)

        # Get the object per-pickle data
        RIG_F_LOG.debug("##VARCHECK pack_info_node: '%s' / type: '%s'" % (pack_info_node, type(pack_info_node).__name__))
        pack_obj = rig_frankenstein_utils.get_pack_object(pack_info_node, non_setting=self._non_override_attrs)

        # # Override the stored
        # print "\n\nLOCAL OVERRIDES:", local_overrides
        #
        # if local_overrides:
        #     for k, v in local_overrides.items():
        #         print "* Going from (", k, ")", getattr(pack_obj, k), ">>", v
        #         setattr(pack_obj, k, v)

        # Return
        return pack_obj

    def __clear_stitch_data(self, pack_info_node=None, parent_info_node=None):
        # Vars
        if not pack_info_node:
            pack_info_node = self.pack_info_node
        
        # Clear from pack
        pack_stitch_data = self._get_stitch_data(pack_info_node=pack_info_node)
        if parent_info_node in pack_stitch_data.parents:
            pack_stitch_data.parents.remove(parent_info_node)
        if pack_stitch_data.do_parenting_pack == parent_info_node:
            pack_stitch_data.do_parenting_pack = None
        # - Store
        pack_stitch_data_pickle = pickle.dumps(pack_stitch_data)
        i_attr.create(node=self.pack_info_node, ln="stitch_data", at="string", dv=str(pack_stitch_data_pickle), l=True)
        
        # Clear from parent
        parent_stitch_data = self._get_stitch_data(pack_info_node=parent_info_node)
        if pack_info_node in parent_stitch_data.children:
            parent_stitch_data.children.remove(pack_info_node)
        # - Store
        parent_stitch_data_pickle = pickle.dumps(parent_stitch_data)
        i_attr.create(node=parent_info_node, ln="stitch_data", at="string", dv=str(parent_stitch_data_pickle), l=True, use_existing=True)
        
        # Clear from current
        self.__store_currently_stitched_data(pack_info_node=pack_info_node, packs_remove=parent_info_node)

    def _get_stitch_data(self, pack_info_node=None):
        # Vars
        if not pack_info_node:
            pack_info_node = self.pack_info_node
            pack_obj = self
        else:
            pack_obj = self._get_pack_object(pack_info_node)
        stitch_data = {"parents": [], "children": [], "parent_type": None, "do_parenting_pack": None}

        # Get existing data
        if i_utils.check_exists(pack_info_node + ".stitch_data"):
            data_as_str = pack_info_node.stitch_data.get()
            stitch_data = pickle.loads(str(data_as_str)).__dict__

        # Get stitchable pack object
        stitchable_pack_obj = pack_obj.top_base_joint or pack_obj.base_joints[0]
        if not stitchable_pack_obj:  # Some packs (like Muscle) don't have base joints
            all_grp_children = pack_obj.pack_grp.relatives(c=True)
            if all_grp_children:
                pack_children = [child for child in all_grp_children if child.startswith(pack_obj.base_name)]  # Only count this pack's things
                if len(pack_children) > 1:  # More than just base joints were made. Need to parent whole group, not just base joint
                    stitchable_pack_obj = pack_obj.pack_grp
        stitch_data["stitchable_pack_obj"] = stitchable_pack_obj

        return i_utils.Mimic(stitch_data)

    def __store_stitch_data(self, parent_info_node=None, do_parenting=False, current=True):
        # Convert to list for ease
        parent_info_node = i_utils.convert_data(parent_info_node, to_generic=False)
        
        # Store parent on the current pack
        # - Get data
        pack_stitch_data = self._get_stitch_data()
        # - Update
        if parent_info_node not in pack_stitch_data.parents:  # Only add if new, otherwise the order gets messed up
            pack_stitch_data.parents.append(parent_info_node)
        if do_parenting:
            pack_stitch_data.do_parenting_pack = parent_info_node
            pack_stitch_data.parent_type = do_parenting
        # - Store
        pack_stitch_data_pickle = pickle.dumps(pack_stitch_data)
        i_attr.create(node=self.pack_info_node, ln="stitch_data", at="string", dv=str(pack_stitch_data_pickle), l=True)
        
        # Store current pack as child on parent
        # for parent in parent_info_node:
        # - Get data
        parent_stitch_data = self._get_stitch_data(parent_info_node)
        # - Update
        if self.pack_info_node not in parent_stitch_data.children:  # Only add if new, otherwise the order gets messed up
            parent_stitch_data.children.append(self.pack_info_node)
        # - Store
        parent_stitch_data_pickle = pickle.dumps(parent_stitch_data)
        i_attr.create(node=parent_info_node, ln="stitch_data", at="string", dv=str(parent_stitch_data_pickle), l=True, use_existing=True)
        
        # Store as currently stitched
        if current:  # This would be false if a bit and pack need data to say they expect to stitch but could not be stitched at that time
            self.__store_currently_stitched_data(packs_add=parent_info_node)
    
    def __get_unstitch_data(self, pack_info_node=None):
        # Vars
        if not pack_info_node:
            pack_info_node = self.pack_info_node
        unstitch_data = {}

        # Get existing data
        if i_utils.check_exists(pack_info_node + ".unstitch_data"):
            data_as_str = pack_info_node.unstitch_data.get()
            unstitch_data = pickle.loads(str(data_as_str))
        
        # Return
        return unstitch_data

    def __store_unstitch_data(self, unstitch_data=None):
        # Get current data
        orig_unstitch_data = self.__get_unstitch_data()
        
        # Update data
        new_unstitch_data = orig_unstitch_data.copy()
        new_unstitch_data.update(unstitch_data)
        
        # Store
        unstitch_data_pickle = pickle.dumps(new_unstitch_data)
        i_attr.create(node=self.pack_info_node, ln="unstitch_data", at="string", dv=str(unstitch_data_pickle), l=True, use_existing=True)
    
    def _get_all_currently_stitched_data(self, pack_info_node=None):
        # Vars
        if not pack_info_node:
            pack_info_node = self.pack_info_node
        currently_stitched_data = {}
        
        # TEMP (June 9, 2018) Backwards compatibility -- :TODO:
        del_old_attr = None
        if i_utils.check_exists(pack_info_node + ".currently_stitched_data"):
            stage = "bits" if self.bit_built else "packs"
            data_as_str = pack_info_node.currently_stitched_data.get()
            current_data = data_as_str.split(", ")
            currently_stitched_data[stage] = current_data
            del_old_attr = pack_info_node.currently_stitched_data

        # Get existing data
        for stage in ["packs", "bits"]:
            current_data = currently_stitched_data.get(stage, [])
            if i_utils.check_exists(pack_info_node + ".currently_stitched_%s" % stage):
                data_as_str = pack_info_node.attr("currently_stitched_%s" % stage).get()
                if data_as_str:
                    current_data = data_as_str.split(", ")
            currently_stitched_data[stage] = current_data
        
        # TEMP (June 9, 2018) Backwards compatibility -- :TODO:
        if del_old_attr:
            del_old_attr.delete()
        
        # Return
        return currently_stitched_data
    
    def _get_currently_stitched_data(self):
        # All currently stitched data - regardless of if stitched in bit or pack stage
        currently_stitched_data = self._get_all_currently_stitched_data()
        
        # Of build's current type
        currently_stitched = currently_stitched_data.get("bits" if self.bit_built else "packs")
        
        # Convert the strings to useable nodes
        currently_stitched = i_utils.convert_data(currently_stitched, to_generic=False)

        # Return
        return currently_stitched

    def __store_currently_stitched_data(self, pack_info_node=None, packs_add=None, packs_remove=None):
        # Check
        if not pack_info_node:
            pack_info_node = self.pack_info_node
        if not packs_add and not packs_remove:
            RIG_F_LOG.warn("No packs to add or remove.")
            return 
        if packs_add and not isinstance(packs_add, (list, tuple)):
            packs_add = [packs_add]
        if packs_remove and not isinstance(packs_remove, (list, tuple)):
            packs_remove = [packs_remove]
        
        # Get current data
        orig_currently_stitched_data = self._get_all_currently_stitched_data(pack_info_node=pack_info_node)

        # Update data
        new_currently_stitched_data = orig_currently_stitched_data.copy()
        if packs_add:
            for info_node in packs_add:
                RIG_F_LOG.debug("##VARCHECK info_node: '%s' / type: '%s'" % (info_node, type(info_node).__name__))
                pack_obj = self._get_pack_object(info_node)
                stage = "bits" if pack_obj.bit_built else "packs"
                if info_node.name not in new_currently_stitched_data[stage]:
                    new_currently_stitched_data[stage].append(info_node.name)
        if packs_remove:
            for info_node in packs_remove:
                RIG_F_LOG.debug("##VARCHECK info_node: '%s' / type: '%s'" % (info_node, type(info_node).__name__))
                pack_obj = self._get_pack_object(info_node)
                stage = "bits" if pack_obj.bit_built else "packs"
                if info_node.name in new_currently_stitched_data[stage]:
                    new_currently_stitched_data[stage].remove(info_node.name)

        # Store
        for stage in ["packs", "bits"]:
            stage_data_str = ", ".join(new_currently_stitched_data.get(stage))
            i_attr.create(node=pack_info_node, ln="currently_stitched_%s" % stage, at="string", dv=stage_data_str, 
                          l=True, use_existing=True)
    
    def __setup_pack(self):
        # Check args
        self.__check()
        
        # Set class attrs based on given
        self.__set_vars()

        # Create Structure
        self.__create_hierarchy()

        # Get character size from placed packs
        self.__calculate_pack_size()

        # Create/Assign Base Joints
        self.__assign_base_joints()
    
    def _create_pack(self):
        return  # This is just so other Builds can override
    
    def _cleanup_pack(self):
        return  # This is just so other Builds can override
    
    def create_pack(self):
        self.__setup_pack()
        self._create_pack()
        self._cleanup_pack()
        self.__complete_pack()

    def __complete_pack(self):
        # Enforce that the bit is not built
        self.bit_built = False

        # Get all built items
        build_items = rig_frankenstein_utils.get_build_nodes_for_pack(pack_obj=self)
        
        # Get pack extras
        self.pack_extras = [obj for obj in build_items if obj.exists() and obj.node_type() not in ["joint", "nurbsCurve"] + i_constraint.get_types() 
                            and obj not in self.default_hierarchy]
        RIG_F_LOG.debug("##VARCHECK pack_extras", self.pack_extras)
        
        # Position pack extras (if exist and stored - for Packs IO)
        RIG_F_LOG.debug("##VARCHECK pack_extras_positions", self.pack_extras_positions)
        if self.pack_extras_positions:
            for extra_obj, pos_info in self.pack_extras_positions.items():
                extra_obj = i_node.Node(extra_obj)
                extra_obj.xform(t=pos_info.get("t"), ws=True)
                r, s = pos_info.get("r"), pos_info.get("s")
                if r:
                    extra_obj.r.set(pos_info.get("r"), f=True)
                if s:
                    extra_obj.s.set(pos_info.get("s"), f=True)

        # Cleanup extra nodes
        self.__nodes_cleanup()

        # Clear selection
        i_utils.select(cl=True)

        # Store Prepped
        self._store_build_data()
        
        # Connect items to info node (for get_pack_from_obj_sel())
        i_node.connect_to_info_node(info_attribute="build_objects", objects=build_items, node=self.pack_info_node)

        # Connect to top group
        if self.top_node:
            i_node.connect_to_info_node(info_attribute="info_nodes", objects=self.pack_info_node, node=self.top_node)

    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # :note: Mostly done in the frankenstein.utils.mirror_pack(). Have empty fn here so the packs that need to override
        # are able to inherit and don't get errors running any pack's .mirror_pack() fn.
        driver_obj = self._get_pack_object(driver_info_node)
        mirror_obj = self._get_pack_object(mirrored_info_node)
        return [driver_obj, mirror_obj]
    
    def __get_stitch_parent_obj(self, parent_info_node=None, raise_error=True, dialog_error=False):
        stitch_data = self._get_stitch_data()
        if not parent_info_node:
            parent_info_node = stitch_data.parents
            if not parent_info_node:
                i_utils.error("Parent Info Node not defined and %s does not have attr: 'stitch_parent'." % self.pack_info_node,
                              raise_err=raise_error, dialog=dialog_error)
                return False
            parent_info_node = parent_info_node[0]
        parent_obj = self._get_pack_object(i_node.Node(parent_info_node))
        
        return parent_obj
    
    def __get_stitch_mirror_data(self, parent_obj=None):
        # Is the pack itself mirrored?
        if self.is_mirror:
            return

        # Is it even driving a mirrored?
        mirrored_info = rig_frankenstein_utils.get_mirrored_connections(self.pack_info_node)
        if not mirrored_info:
            return
        
        # Vars
        mirrored_obj = mirrored_info[1]
        mirrored_parent_info_node = parent_obj.pack_info_node.replace(parent_obj.side + "_", mirrored_obj.side + "_", 1)
        if not i_utils.check_exists(mirrored_parent_info_node):
            mirrored_parent_info_node = parent_obj.pack_info_node
        
        # Get Symmetry Info
        top_sym_nodes = {}
        if mirrored_obj.is_mirror_sym:
            mirror_sym_nodes = rig_frankenstein_utils.get_mirror_sym_nodes(mirrored_obj)
            # mirror_sym_nodes = pickle.loads(str(mirrored_obj.pack_info_node.mirror_sym_nodes.get()))
            if mirror_sym_nodes:
                mirror_base_joints = mirrored_obj.base_joints
                mirror_top_joint = mirrored_obj.top_base_joint or mirror_base_joints[0]
                t_sym_md = mirror_sym_nodes.get("t")
                if t_sym_md:
                    top_sym_nodes["t"] = [md for md in t_sym_md if mirror_top_joint in md.connections(s=False, d=True)][0]
        
        # Return
        return i_utils.Mimic({"mirrored_obj" : mirrored_obj, "mirrored_parent_info_node" : mirrored_parent_info_node,
                              "top_sym_nodes" : top_sym_nodes})
    
    def _stitch_pack(self):
        return  # Placeholder for optional individual pack use
    
    def stitch_pack(self, parent_info_node=None, do_parenting=None, stitch_data=None, dialog_error=False, raise_error=True):
        """
        :param parent_info_node: (node) - (optional) if not defined, stitches to stored parent (if stored)
        :param do_parenting: (str) - "start" / "end" / False / None
        - "start" / "end": which parent joint to parent first pack joint to
        - None: use default - either what was stored as the parenting type or "end" if not stored
        - False: do not parent
        :return: 
        """
        # No parent defined, do all
        if not parent_info_node:
            if not stitch_data:
                stitch_data = self._get_stitch_data()  # {"parents": [], "children": [], "parent_type": None, "do_parenting_pack": None}
            if stitch_data.parents:
                RIG_F_LOG.debug("No parent given. Stitching pack: '%s' to all pre-defined parents." % self.pack_info_node)
                parenting_pack = stitch_data.do_parenting_pack
                if isinstance(parenting_pack, (list, tuple)):
                    parenting_pack = parenting_pack[0]
                RIG_F_LOG.debug("##VARCHECK parents", stitch_data.parents)
                for parent in stitch_data.parents:
                    parent_obj = self._get_pack_object(parent)
                    do_parenting = False if (parenting_pack and parent_obj.pack_info_node != parenting_pack) else stitch_data.parent_type
                    self.stitch_pack(parent_info_node=parent, do_parenting=do_parenting, dialog_error=dialog_error, raise_error=raise_error)
            if stitch_data.children:
                RIG_F_LOG.debug("##VARCHECK children", stitch_data.children)
                for child in stitch_data.children:
                    child_obj = self._get_pack_object(child)
                    child_obj.stitch_pack(parent_info_node=self.pack_info_node, dialog_error=dialog_error, raise_error=raise_error)
            else:
                RIG_F_LOG.warn("No parent given or found to stitch pack: '%s'." % self.pack_info_node)
            return
        
        # Get parent obj
        parent_obj = self.__get_stitch_parent_obj(parent_info_node=parent_info_node, raise_error=raise_error)
        if not parent_obj:
            return 
        
        # Check if both are in pack stage
        if self.bit_built or parent_obj.bit_built:
            i_utils.error("%s and %s must both be packs (not bits) to stitch.\n\nStoring info, but not currently stitching." 
                          % (self.pack_info_node, parent_info_node), raise_err=raise_error, dialog=dialog_error, verbose=not(raise_error))
            # - Still store the data. This is esp important for deconstruct, which rebuilds where some are packs and some are bits
            # but where we don't expect the child pack to actually have in-scene parenting
            self.__store_stitch_data(parent_info_node=parent_info_node, do_parenting=do_parenting, current=False)
            return
        
        # Verbose
        RIG_F_LOG.debug("Stitching Pack: %s > %s. (Parenting: %s)" % (parent_obj.base_name, self.base_name, do_parenting))
        
        # Parenting? (If not doing parenting, then stitching is just so bits know later)
        stitch_data = self._get_stitch_data()
        parenting_pack = stitch_data.do_parenting_pack
        if isinstance(parenting_pack, (list, tuple)):
            parenting_pack = parenting_pack[0]
        # - Check and find legit parenting info
        if do_parenting is None and parenting_pack == parent_info_node:
            do_parenting = stitch_data.parent_type
            RIG_F_LOG.debug("Do Parent is set to 'None'. Using stored stitch type: '%s' for parent: '%s'" % (do_parenting, parent_info_node))
        parent_joint = None
        if do_parenting == "start":
            parent_joint = parent_obj.base_joints[0]
        elif do_parenting == "end":
            parent_joint = parent_obj.base_joints[-1]
        elif do_parenting is not False:
            i_utils.error("Parenting options must be 'start' or 'end'. Cannot understand: %s, (%s). Stitching: '%s' > '%s'" %
                          (do_parenting, type(do_parenting).__name__, parent_obj.base_name, self.base_name), 
                          raise_err=raise_error, dialog=dialog_error, verbose=not(raise_error))
            do_parenting = False
            if dialog_error:
                return 
        if do_parenting and (parenting_pack and parent_info_node != parenting_pack):  # This was already defined as parented pack
            i_utils.error("%s is already parented under %s. Cannot define a second stitch parent (%s) that involves actual parenting."
                          % (self.pack_info_node, parenting_pack, parent_info_node), raise_err=raise_error, dialog=dialog_error, verbose=not(raise_error))
            if dialog_error:
                return 
            do_parenting = False
        # - Do Parenting
        if do_parenting:
            RIG_F_LOG.debug("Stitching '%s' > '%s' with do parenting: '%s'" % (parent_info_node, self.pack_info_node, do_parenting))
            # stitch_joint = stitch_data.stitchable_pack_obj
            stitch_data.stitchable_pack_obj.set_parent(parent_joint)
            # - Optionally do post-stitch
            self._stitch_pack()
        
        # Store Stitch Data
        RIG_F_LOG.debug("Storing stitch data.")
        self.__store_stitch_data(parent_info_node=parent_info_node, do_parenting=do_parenting)
        
        # Mirror Stitching
        if not self.is_mirror:
            mirrored_info = self.__get_stitch_mirror_data(parent_obj=parent_obj)
            if mirrored_info:
                # - Stitch
                mirrored_obj = mirrored_info.mirrored_obj
                mirrored_obj.stitch_pack(parent_info_node=mirrored_info.mirrored_parent_info_node,
                                         do_parenting=do_parenting, raise_error=raise_error, dialog_error=dialog_error)
                # - Account for Symmetry
                sym_nodes = mirrored_info.top_sym_nodes
                if sym_nodes:
                    mirror_base_joints = mirrored_obj.base_joints
                    mirror_orientation = mirrored_obj.orient_joints
                    new_mult = None
                    if len(mirror_base_joints) > 1:
                        new_mult = [-1, -1, -1]
                    elif len(mirror_base_joints) == 1:
                        new_mult = {"x": [1, -1, 1], "y": [-1, 1, 1]}.get(mirror_orientation[0])
                    if new_mult:
                        sym_nodes.get("t").input2.set(new_mult)
            else:
                if self.side == "L":
                    RIG_F_LOG.debug("No mirrored stitch data found for '%s'. Cannot mirror stitching." % self.pack_info_node)
        
        # Return success
        return True
    
    def __unstitch_children(self, stitch_data=None, clear_data=False, raise_error=True, dialog_error=False):
        # Vars
        RIG_F_LOG.debug("Unstitching children")
        if not stitch_data:
            stitch_data = self._get_stitch_data()
        children_info_nodes = stitch_data.children
        
        # Check
        if not children_info_nodes:
            RIG_F_LOG.debug("No children found for '%s'." % self.pack_info_node)
            return 
        
        # Unstitch
        RIG_F_LOG.debug("##VARCHECK children_info_nodes", children_info_nodes)
        pack_is_bit = self.bit_built
        for child_info_node in children_info_nodes:
            # - Var
            if not child_info_node.exists():  # :TODO: Why did it not clear the child data?
                RIG_F_LOG.warn("Child: '%s' no longer exists. Cannot unstitch from '%s'." % (child_info_node, self.base_name))
                continue
            child_obj = self._get_pack_object(child_info_node)
            # - Check Modes Match
            if pack_is_bit != child_obj.bit_built:
                i_utils.error("%s and %s must both be packs or both be bits to unstitch." % (self.base_name, child_obj.base_name),
                              raise_err=raise_error, dialog=dialog_error, verbose=not(raise_error))
                continue
            # - Unstitch Pack
            if not pack_is_bit:
                child_obj.unstitch_pack(parent_info_node=self.pack_info_node, clear_data=clear_data,
                                        unstitch_children=False, raise_error=raise_error, dialog_error=dialog_error)
            # - Unstitch Bit
            else:
                child_obj.unstitch_bit(parent_info_node=self.pack_info_node, clear_data=clear_data,
                                       unstitch_children=False, raise_error=raise_error, dialog_error=dialog_error)
        
        # Success Return
        return True
    
    def unstitch_pack(self, parent_info_node=None, clear_data=False, unstitch_children=True, dialog_error=False, raise_error=True):  # unstitch_children=False
        # No parent defined, do all
        if parent_info_node is None:
            stitched_parents = self._get_currently_stitched_data()
            if stitched_parents:
                RIG_F_LOG.debug("No parent given. Unstitching from all pre-defined parents.")
                for parent in stitched_parents:
                    if not i_utils.check_exists(parent):
                        RIG_F_LOG.warn("Cannot unstitch '%s' from '%s'. '%s' does not exist." % (self.pack_info_node, parent, parent))
                        continue
                    self.unstitch_pack(parent_info_node=i_node.Node(parent), clear_data=clear_data, unstitch_children=unstitch_children, 
                                      dialog_error=dialog_error, raise_error=raise_error)
            else:
                RIG_F_LOG.debug("No parents found or given to unstitch.")
            return

        # Not unstitching parent? Only unstitching children?
        if parent_info_node is False and unstitch_children:
            self.__unstitch_children(clear_data=clear_data, raise_error=raise_error, dialog_error=dialog_error)
            return
        
        # Get parent obj
        parent_obj = self.__get_stitch_parent_obj(parent_info_node=parent_info_node, raise_error=raise_error, dialog_error=dialog_error)
        if not parent_obj:
            return
        parent_info_node = i_node.Node(parent_info_node)

        # Check if both are in pack stage
        if self.bit_built or parent_obj.bit_built:
            i_utils.error("%s and %s must both be packs (not bits) to unstitch." % (self.pack_info_node, parent_info_node),
                          raise_err=raise_error, dialog=dialog_error)
            return

        # Verbose
        RIG_F_LOG.debug("Unstitching Pack: %s > %s." % (parent_obj.base_name, self.base_name))
        
        # Unparent
        stitch_data = self._get_stitch_data()
        pack_child = stitch_data.stitchable_pack_obj
        pack_grp = self.pack_grp
        # - Check if pack group matches pack child - this happens if there was more to the pack than base joints
        if pack_child == pack_grp:
            pack_grp = self.build_pack_grp
        # - Parent back to pack's group
        i_utils.parent(pack_child, pack_grp, a=True)  # :note: pack_child isn't always a Node
        
        # Mirror Unstitching
        mirrored_info = self.__get_stitch_mirror_data(parent_obj=parent_obj)
        if mirrored_info:
            # - Account for Symmetry
            sym_nodes = mirrored_info.top_sym_nodes
            if sym_nodes:
                sym_nodes.get("t").input2.set([-1, 1, 1])
            # - UnStitch
            mirrored_obj = mirrored_info.mirrored_obj
            succ = mirrored_obj.unstitch_pack(parent_info_node=mirrored_info.mirrored_parent_info_node, clear_data=clear_data,
                                       unstitch_children=unstitch_children, raise_error=raise_error, dialog_error=dialog_error)
            if not succ:
                return
        
        # Children Unstitching
        if unstitch_children:
            succ = self.__unstitch_children(stitch_data=stitch_data, clear_data=clear_data, raise_error=raise_error, dialog_error=dialog_error)
            if not succ:
                return 
        
        # Clear Data
        if clear_data:
            self.__clear_stitch_data(parent_info_node=parent_info_node)
        else:
            self.__store_currently_stitched_data(packs_remove=parent_info_node)
        
        # Success Return
        return True

    def __calculate_pack_size(self):
        # Vars
        newly_defined = True
        
        # Find Pack Size
        # if self.is_mirror:
        #     newly_defined = False
        #     # return  # Everything is already defined. No need to waste time calculating or f up dependent var calcs
        if self.pack_size != 1:  # Pre-defined (will always happen if building bit)
            newly_defined = False
            # return #pass
            # RIG_F_LOG.info("Predefined Pack Size for '%s'. Not calculating." % self.base_name)
        elif len(self.base_joints) == 1:
            if self.joint_radius != self.original_joint_radius:
                self.pack_size = float(float(self.joint_radius) * 2.0)
            elif len(cmds.ls(type="joint")) > 2:  # More than one pack in the scene (accounts for mirrored)
                joint_bbox = cmds.exactWorldBoundingBox(cmds.ls(type="joint"))
                self.pack_size = round(joint_bbox[4] / 9.25, 3)  #round(joint_bbox[4] / 9.25, 3)
            else:
                self.pack_size = 5.0
        elif self.base_joints:
            dist = i_utils.get_single_distance(from_node=self.base_joints[0], to_node=self.base_joints[-1])
            self.pack_size = float(dist) / 2.0
        else:
            pack_size = rig_frankenstein_utils.get_model_size()
            if pack_size:
                self.pack_size = pack_size
            else:
                RIG_F_LOG.debug("No pack size defined. No geo or pack joints found to calculate pack size for '%s'. "
                                "Using default." % self.base_name)
        
        # Update dependent vars
        if newly_defined:  # :note: Need to start from original for sake of mirroring to not be calculated twice, but above calcs are needed
            self.joint_radius = self.original_joint_radius * float(self.pack_size / 2.0)  # / 5.0
            self.ctrl_size = self.original_ctrl_size * float(self.pack_size)
        self.tweak_ctrl_size = (self.ctrl_size / 2.0)  # :note: Temp also defined in setup_bit()
        ls = round(self.pack_size * 0.25, 3)
        self.loc_size = [ls, ls, ls]
    
    def _create_null_control_mimic(self, name=None, include_base_name=True, position_match=None, parent=None):
        # Create
        if include_base_name:
            name = self.base_name + "_" + name
        null = i_node.create("transform", n=name + "_Tfm")
        i_node.copy_pose(driver=position_match, driven=null)
        null.set_parent(parent)
        
        # Mimic control class
        ctrl = i_utils.Mimic({"control": null, "top_tfm": null, "last_tfm": null, "offset_grp" : null, "cns_grp" : null})
        
        # Return
        return ctrl

    def _create_ikfk_switch(self, ik_controls=None, ik_joints=None, fk_controls=None, fk_joints=None,
                           driven_objs=None, position_match=None, offset_distance=None, watson_blend=False,
                           ikfk_switch=None, translation=False, pv_control=None, flip_shape=None, dv=None):
        # Check
        if not ik_controls and self.ik_ctrls:
            ik_controls = [ik.control for ik in self.ik_ctrls]
            ik_controls += [ik.gimbal for ik in self.ik_ctrls if ik.gimbal]
        ik_controls = i_utils.check_arg(ik_controls, "ik controls", exists=True, check_is_type=list)
        ik_joints = i_utils.check_arg(ik_joints, "ik joints", exists=True, check_is_type=list)
        if not fk_controls and self.fk_ctrls:
            fk_controls = [fk.control for fk in self.fk_ctrls]
            fk_controls += [fk.gimbal for fk in self.fk_ctrls if fk.gimbal]
        fk_controls = i_utils.check_arg(fk_controls, "fk controls", exists=True, check_is_type=list)
        fk_joints = i_utils.check_arg(fk_joints, "fk joints", exists=True, check_is_type=list)
        if driven_objs is None:
            driven_objs = self.base_joints
        if not position_match and driven_objs:
            position_match = driven_objs[-1]
        if dv is None:
            dv = self.ikfk_default_mode

        # Vars
        # - Connect info things to the switch for Anim's IkFkMatch to know what to work with
        info_connect = {"ik_controls": ik_controls, "ik_joints": ik_joints,
                        "fk_controls": fk_controls, "fk_joints": fk_joints}
        if pv_control:  # Feet won't have
            info_connect["pv_control"] = pv_control
        if len(fk_controls) == 1:  # Watson just gives a group
            # :note: Need to keep in order so the ik/fk match script knows upper/mid/lower
            fk_children_in_order = list(reversed(fk_controls[0].relatives(ad=True, type="transform")))
            fk_ctrls = [ctrl for ctrl in fk_children_in_order if i_control.check_is_control(ctrl)]
            info_connect["fk_controls"] = fk_ctrls

        # Resize base Joints so Ik/Fk joints stand out
        for jnt in self.base_joints:
            if not jnt.radius.get(settable=True):
                continue
            jnt.radius.set(jnt.radius.get() * 0.5)

        # Create Switch
        if not offset_distance:
            offset_distance = [0, 0, 0.5]
        elif not isinstance(offset_distance, (tuple, list)):
            offset_distance = [0, 0, offset_distance * (self.pack_size / 10.0)]
        if self.is_mirror and self.ikfk_switch_mirror_offset:
            offset_distance = [od * -1 * (self.pack_size / 10.0) for od in offset_distance]
        self.ikfk_switch_control = ikfk_switch
        if not ikfk_switch:
            ikfk_switch_ctrl = i_node.create("control", control_type=self.ikfk_switch_control_type, 
                                             color=self.ikfk_switch_control_color,
                                             name=self.ikfk_switch_name, size=self.ctrl_size,
                                             position_match=position_match, promote_rotate_order=False,
                                             move_shape=offset_distance, match_rotation=False,
                                             flip_shape=flip_shape,  # lock_hide_attrs=["t", "r", "s", "v"],
                                             with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
            # Store class attr
            self.ikfk_switch_control = ikfk_switch_ctrl.control
            # Connect to info node as FKIKSwitch to be able to query in stitching and other functions
            i_node.connect_to_info_node(info_attribute="IKFKSwitch_Ctrl", objects=self.ikfk_switch_control,
                                        node=self.pack_info_node)

        # Add attribute
        self.ikfk_blend_attr = i_attr.create(self.ikfk_switch_control, ln="FKIKSwitch", at="double", min=0.0, max=1.0, k=True, dv=dv)
        # # Clean up other attributes
        # i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r", "s", "v"], lock=True, hide=True)

        # Connect scale
        if self.scale_attr:
            i_attr.connect_attr_3(self.scale_attr, self.ikfk_switch_control.s)

        # Connect Positions
        self.ikfk_blcs = []
        if driven_objs:
            for i, obj in enumerate(driven_objs):
                # Vars
                base_name = self.base_name + "_" + self.joint_names[i].capitalize()
                driven = driven_objs[i]
                ik_jnt = ik_joints[i]
                fk_jnt = fk_joints[i]

                # - Watson Blend. Translation and Rotation
                if watson_blend:
                    blend_nd = i_node.create("pairBlend", n=base_name + "_IkFk_TR_Pb")
                    self.ikfk_blcs.append(blend_nd)
                    blend_nd.rotInterpolation.set(0)

                    blend_nd.outTranslate.drive(driven.t)
                    blend_nd.outRotate.drive(driven.r)

                    ik_jnt.t.drive(blend_nd.inTranslate2)
                    ik_jnt.r.drive(blend_nd.inRotate2)
                    fk_jnt.t.drive(blend_nd.inTranslate1)
                    fk_jnt.r.drive(blend_nd.inRotate1)

                    self.ikfk_blend_attr.drive(blend_nd.weight)

                # - Frankenstein Blend.
                else:
                    blc_node = i_node.create("blendColors", n=base_name + "_IkFk_Rot_Blc")
                    self.ikfk_blcs.append(blc_node)
                    ik_jnt.rotate.drive(blc_node.color1)
                    fk_jnt.rotate.drive(blc_node.color2)
                    self.ikfk_blend_attr.drive(blc_node.blender)
                    blc_node.output.drive(driven.rotate)
                    # - Translation
                    if translation:
                        blc_node = i_node.create("blendColors", n=base_name + "_IkFk_Trans_Blc")
                        self.ikfk_blcs.append(blc_node)
                        ik_jnt.translate.drive(blc_node.color1)
                        fk_jnt.translate.drive(blc_node.color2)
                        self.ikfk_blend_attr.drive(blc_node.blender)
                        blc_node.output.drive(driven.translate)

        # Connect to Vis
        self.ikfk_vis_con = rig_attributes.vis_attr_condition(attr=self.ikfk_blend_attr, nodes_vis_at_0=fk_controls, nodes_vis_at_1=ik_controls)
        # # - Create Setup
        # self.ikfk_vis_con = i_node.create("condition", n=self.base_name + "_IkFk_Vis_Cond")
        # self.ikfk_blend_attr.drive(self.ikfk_vis_con.firstTerm)
        # self.ikfk_vis_con.secondTerm.set(0.5)
        # self.ikfk_vis_con.colorIfTrueR.set(1)
        # self.ikfk_vis_con.colorIfTrueG.set(0)
        # self.ikfk_vis_con.colorIfTrueB.set(0)
        # self.ikfk_vis_con.colorIfFalseR.set(0)
        # self.ikfk_vis_con.colorIfFalseG.set(1)
        # self.ikfk_vis_con.colorIfFalseB.set(1)
        # self.ikfk_vis_con.operation.set(3)
        # # -- Unlock (to be able to connect)
        # for ctrl in ik_controls + fk_controls:
        #     ctrl.v.set(l=False)
        # # -- Connect
        # for ik_ctrl in ik_controls:
        #     shps = ik_ctrl.relatives(s=True)
        #     if not shps:  # Not really a control (ex: Limb_Watson)
        #         i_attr.multi_drive_visibility(driving_attr=self.ikfk_vis_con.outColorR, node_to_drive=ik_ctrl)
        #         continue
        #     for shp in shps:  # Controls
        #         i_attr.multi_drive_visibility(driving_attr=self.ikfk_vis_con.outColorR, node_to_drive=shp)
        # for fk_ctrl in fk_controls:
        #     shps = fk_ctrl.relatives(s=True)
        #     if not shps:  # Not really a control (ex: Limb_Watson)
        #         i_attr.multi_drive_visibility(driving_attr=self.ikfk_vis_con.outColorG, node_to_drive=fk_ctrl)
        #         continue
        #     for shp in shps:  # Controls
        #         i_attr.multi_drive_visibility(driving_attr=self.ikfk_vis_con.outColorG, node_to_drive=shp)
        
        # Drive / Parent
        # driver = self.ground_gimbal_control or self.pack_ctrl_grp
        # i_constraint.constrain(driver, self.ikfk_switch_control, as_fn="parent", mo=True)
        # par = self.pack_ctrl_grp if driver != self.pack_ctrl_grp else self.ctrl_grp
        # self.ikfk_switch_control.set_parent(par)
        self.ikfk_switch_control.set_parent(self.ctrl_grp)
        # -- Lock (now driven, should never be touched)
        for ctrl in ik_controls + fk_controls:
            ctrl.v.set(l=True)
        i_attr.lock_and_hide(node=self.ikfk_switch_control, attrs=["t", "r", "s", "v"], lock=True, hide=True)

        # Connect attrs used in animation's ikfk match tool
        for attr, objs in info_connect.items():
            i_node.connect_to_info_node(info_attribute=attr, node=self.ikfk_switch_control, objects=objs)
    
    def _setup_bit(self):
        # Get stored data
        if not self.build_is_subbuild:
            self.__get_build_data()

        # Get attrs based on given
        # :note: This will cause some stored to be overriden. At this time, this is intentional for things like changing 
        # side color defaults
        self.__set_vars()

        # Get Scale Attr
        scale_attr = "Root_Ctrl.ScaleXYZ"
        if i_utils.check_exists(scale_attr):
            self.scale_attr = i_attr.Attr(scale_attr)

        # Disconnect pack mirroring
        rig_frankenstein_utils.mirror_symmetry_detach(pack_info_node=self.pack_info_node, dialog_error=False)

        # Unstitch packs
        if self.do_stitch:
            self.unstitch_pack(raise_error=False)

        # Get character size from placed packs
        self.__calculate_pack_size()

        # Re-Orient
        if self.do_orient_joints and not self.is_mirror:
            all_joints = self._get_all_base_joints()
            rig_joints.orient_joints(joints=all_joints, orient_as=self.orient_joints, up_axis=self.orient_joints_up_axis)
        
        # Get Ground Gimbal for parenting
        if not self.ground_gimbal_control:
            self.ground_gimbal_control = rig_controls.get_ground_gimbal()

    def _presetup_bit(self):
        return  # This is just so other Builds can override

    def _create_bit(self):
        return  # This is just so other Builds can override
    
    def _cleanup_bit(self):
        return  # This is just so other Builds can override

    def create_bit(self):
        self._presetup_bit()
        self._setup_bit()
        self._create_bit()
        self._cleanup_bit()
        self._complete_bit()
    
    def __get_created_nodes(self):
        # Find literally everything
        all_created_nodes = rig_frankenstein_utils.get_build_nodes_for_pack(pack_obj=self)
        all_joints = self._get_all_base_joints()
        
        # Sort into created types
        for created_node in all_created_nodes:
            if not created_node.exists():  # Was deleted
                continue
            if created_node.node_type() == "joint":
                if created_node in all_joints:  # Don't include base or chain joints
                    continue
                self.created_joints.append(created_node)
            elif i_control.check_is_control(created_node) and created_node not in self.created_controls:
                self.created_controls.append(created_node)
            else:
                self.created_nodes.append(created_node)
    
    def __joint_cleanup(self):
        # Vars
        if not self.bind_joints:
            if self.bind_joints is None:  # Some intentionally have no bind joints
                self.bind_joints = []
            else:
                self.bind_joints = self.base_joints
        
        # Get all joints
        all_joints = self._get_all_base_joints()
        all_joints += self.created_joints + self.bind_joints
        if not all_joints:
            return 
        all_joints = list(set(all_joints))

        # Add Suffix
        for jnt in all_joints:
            if not jnt.exists():
                RIG_F_LOG.warn("'%s' no longer exists. Cannot rename." % jnt)
                continue
            # - First clean it off in case given suffix in pack code
            jnt_name_clean = jnt.replace("_Bnd", "").replace("_Jnt", "")
            # - Find the real suffix to give
            suff = "_Jnt"
            if jnt in self.bind_joints:
                suff = "_Bnd" + suff
            # - Rename
            if not jnt.endswith(suff):
                jnt.rename(jnt_name_clean + suff)

        # Lock/Hide
        for jnt in self.created_joints:
            i_attr.lock_and_hide(node=jnt, attrs=["v", "radius"], hide=True)
        
        # Force vis connection
        if self.joint_vis_objs and self.top_node:
            if i_utils.check_exists(self.top_node + ".JointVis"):
                for obj in self.joint_vis_objs:
                    self.top_node.JointVis.drive(obj.v)
            else:
                RIG_F_LOG.warn("'%s' has no attribute '%s'. Cannot drive visibility of: %s" % (self.top_node, "JointVis", self.joint_vis_objs))
        
        # # Force radius on randomly left-behind-at-1 joints
        # # :note: Turned off because it's flaky as-is and having to put the rewrap in just makes things take longer. ugh.
        # for jnt in all_joints:
        #     if not jnt.exists():
        #         continue
        #     # if i_utils.is_legacy:
        #     jnt = i_node.Node(jnt)  # Re-wrap for the sake of the attr. The issue is rare, mostly 2015, but sometimes elsewhere (AUTO-1407)
        #     if jnt.radius.get() == 1.0:
        #         jnt.radius.set(self.joint_radius)

    def __control_cleanup(self):
        # Vars
        if not self.control_vis_driven:
            self.control_vis_driven = self.created_controls
        if self.ikfk_switch_control:
            self.control_vis_driven.append(self.ikfk_switch_control)

        # # Directly drive visibility of any joints found in the controls group
        # # :note: Originally tried to do this on just self.created_joints, but not all created joints are being included
        # top_nodes = i_node.get_top_nodes()
        # jnt_vis_attr = None
        # if top_nodes:
        #     for tn in top_nodes:
        #         if i_utils.check_exists(tn + ".JointVis"):
        #             jnt_vis_attr = tn.attr("JointVis")
        #             break
        # if jnt_vis_attr:
        #     jnts_in_ctrls = self.pack_ctrl_grp.relatives(ad=True, type="joint")  # "Ctrl_Grp"
        #     if jnts_in_ctrls:
        #         for jnt in jnts_in_ctrls:
        #             if not i_utils.check_connected(jnt_vis_attr, jnt + ".v"):
        #                 jnt_vis_attr.drive(jnt + ".v", f=True)
        # :note: Commented out. This may not be the best way of finding these items.
        
        # Add vis dis attr
        if not self.build_is_inherited:
            self.vis_ctrl = rig_controls.create_vis_control(use_existing=True)
            self.pack_dis_attr = rig_attributes.create_dis_attr(node=self.vis_ctrl.control, ln=self.base_name,
                                                                drive=self.control_vis_driven, drive_shapes=True, dv=1)

        # Update defaults
        if self.created_controls:  # Temp. When testing may not have made controls, yet
            # - Temp turn off extra vis so can save that as default
            rig_controls.set_all_vis_attrs(controls=self.created_controls, set=0)
            # - Save as default
            i_attr.update_default_attrs(nodes=self.created_controls)
            # - Turn on extra vis so rigger can see them
            rig_controls.set_all_vis_attrs(controls=self.created_controls, set=1)
    
    def __nodes_cleanup(self):
        # Remove deleted items from created nodes
        self.created_nodes = [nd for nd in self.created_nodes if nd.exists()]
        
        # Locator size
        created_locators = [nd for nd in self.created_nodes if nd.relatives(s=True, type="locator")]
        for loc in created_locators:
            loc.localScale.set(self.loc_size)

    def _utility_cleanup(self, objs=None):
        if not self.top_node:
            return 
        
        if not objs:
            objs = self.utility_vis_objs
        if not objs:
            return
        if not isinstance(objs, (list, tuple)):
            objs = [objs]

        if i_utils.check_exists(self.top_node + ".UtilityVis"):
            for obj in objs:
                self.top_node.UtilityVis.drive(obj + ".v")
        else:
            RIG_F_LOG.warn("'%s' has no attribute '%s'. Cannot drive visibility of: %s" % (self.top_node, "UtilityVis", objs))
    
    def _complete_bit(self):
        # Get Created Nodes
        self.__get_created_nodes()
        
        # Cleanup joints
        self.__joint_cleanup()
        
        # Drive Visibility
        self.__control_cleanup()

        # Cleanup extra nodes
        self.__nodes_cleanup()

        # Drive Visibility of utilities
        self._utility_cleanup()

        # Declare it has been built
        self.bit_built = True

        # Store Bit
        self._store_build_data()

        # Connect items to info node (for get_pack_from_obj_sel())
        objs = self.created_joints + self.created_controls + self.created_nodes
        i_node.connect_to_info_node(info_attribute="build_objects", objects=objs, node=self.pack_info_node)

        # Stitch bit if stitching was defined in packs
        if self.do_stitch:
            self.stitch_bit(raise_error=False)
        
        # Clear selection
        i_utils.select(cl=True)
    
    def stitch_bit(self, parent_info_node=None, dialog_error=False, raise_error=True, force_restitch=False):
        # No parent defined, do all
        if not parent_info_node:
            stitch_data = self._get_stitch_data()
            if stitch_data.parents:
                RIG_F_LOG.debug("No parent given. Stitching bit: '%s' to all pre-defined parents." % self.pack_info_node)
                for parent in stitch_data.parents:
                    self.stitch_bit(parent_info_node=parent, dialog_error=dialog_error, raise_error=raise_error)
            return
        
        # Check not already stitched
        stitched_parents = self._get_currently_stitched_data()
        if stitched_parents and parent_info_node in stitched_parents and not force_restitch:
            msg = "'%s' is already stitched to parent: '%s'" % (self.pack_info_node, parent_info_node)
            if dialog_error:
                do_it = i_utils.message(title="Already Stitched", message=msg + ". Force Restitch?",
                                        button=["Yes", "No"])
                if do_it == "Yes":
                    force_restitch = True
            if not force_restitch:
                RIG_F_LOG.debug(msg + " and force_restitch is False. Not Restitching.")
                return True

        # Check stitch ability and get build objects
        stitch_info = self.__setup_stitch(parent_info_node=parent_info_node, dialog_error=dialog_error)
        if not stitch_info:
            i_utils.error("No stitch info found for '%s' to use." % self.pack_info_node, dialog=dialog_error, raise_err=raise_error)
            return False
        parent_obj, pack_obj, parent_build_type = stitch_info
        
        # Clear stitch commands so it can be stored just for that parent
        self.stitch_cmds = []
        
        # Individual Build Stitching
        success = self._stitch_bit(parent_obj=parent_obj, pack_obj=pack_obj, parent_build_type=parent_build_type)
        if success is False:  # Most won't return, but if actually have issues, return False
            return False
        
        # Execute and Store data
        self._complete_stitch(parent_info_node=parent_info_node)
        
        # Success
        return True
    
    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        """
        When adding stitch information to the Build classes, use this dictionary method for anything that will require
        unstitching. This way it can be maintained in one place and have automated processes for less maintenance.
        
        # Parent
        self.stitch_cmds.append({"parent" : {"child" : None, "parent" : None}})
        
        # Delete an object/attribute
        self.stitch_cmds.append({"delete" : {"stitch" : [None, None], "unstitch" : [None, None]}})
        
        # Constrain
        self.stitch_cmds.append({"constrain" : {"args" : [None, None], "kwargs": {"mo" : True, "as_fn" : "parent"}}})
        
        # Delete Constraint
        self.stitch_cmds.append({"delete_constraint" : {"driven" : None}})
        
        # Follow
        self.stitch_cmds.append({"follow" : {"driving" : None, "cns_type" : "parent", "dv" : None, "options" : None}})
        
        # Force Vis
        self.stitch_cmds.append({"force_vis" : {"objects" : None, "value" : 0}})
        
        # Transfer Attributes
        self.stitch_cmds.append({"transfer_attributes" : {"from" : None, "to" : None, "ignore" : None}})
        
        # Drive
        self.stitch_cmds.append({"drive" : {"driver" : None, "driven" : None}})
        
        # Shift Follow Attrs
        self.stitch_cmds.append({"shift_follow_attrs" : {"control" : None}})
        
        # Unique
        self.stitch_cmds.append({"unique" : {"cmd" : None, "unstitch" : None}})
        """
        return  # This is just so other Builds can override
    
    def __setup_stitch(self, parent_info_node=None, dialog_error=False):
        # Vars
        i_utils.check_arg(parent_info_node, "parent info node", exists=True)
        parent_obj = self._get_pack_object(parent_info_node)
        pack_obj = self._get_pack_object(self.pack_info_node)

        # Is the parent bit built?
        if not parent_obj.bit_built:
            RIG_F_LOG.info("'%s' is not built. Cannot stitch %s to it, yet. Try again after building the bit." % (parent_info_node, self.pack_info_node))
            return False

        # Check if pack type is accepted
        parent_build_type = parent_obj.build_type
        if self.accepted_stitch_types != "all" and self.accepted_stitch_types and parent_build_type not in self.accepted_stitch_types:
            i_utils.error("Can only stitch '%s' to: %s. Not '%s' ('%s')." % 
                          (self.build_type, self.accepted_stitch_types, parent_build_type, parent_info_node), dialog=dialog_error)
            return False

        # Verbose
        RIG_F_LOG.debug("Stitching Bit '%s' > '%s'." % (parent_obj.base_name, self.base_name))

        # Consolidate IKFKSwitch controls
        if self.consolidate_ik_fk_switch:
            current_ikfk_switch = pack_obj.ikfk_switch_control
            parent_ikfk_switch = parent_obj.ikfk_switch_control
            if current_ikfk_switch and parent_ikfk_switch:
                # - Vars
                driving_switch = parent_ikfk_switch
                driven_switch = current_ikfk_switch
                if self.consolidate_ik_fk_switch_to_child:
                    driving_switch = current_ikfk_switch
                    driven_switch = parent_ikfk_switch
                # - Attr Connect
                driving_switch.FKIKSwitch.drive(driven_switch.FKIKSwitch)
                # - Attr Transfer
                i_attr.transfer_attributes(from_node=driven_switch, to_node=driving_switch, action="promote", ignore_attrs=["FKIKSwitch"])
                # - Lock and Hide driven
                i_control.force_vis(driven_switch, 0)
        
        # Return
        return [parent_obj, pack_obj, parent_build_type]
    
    def _complete_stitch(self, parent_info_node=None, stitch_cmds=None):
        # Vars
        unstitch_cmds = []
        if not stitch_cmds:
            stitch_cmds = self.stitch_cmds
        
        # Execute
        for cmd in stitch_cmds:
            for cmd_type, cmd_info in cmd.items():
                unstitch_cmd_info = None
                # - Follow Attr
                if cmd_type == "follow":
                    # - Do it
                    if not cmd_info.get("pack_info_node"):
                        cmd_info["pack_info_node"] = self.pack_info_node
                    if not cmd_info.get("driver_pack_info_node"):
                        cmd_info["driver_pack_info_node"] = parent_info_node
                    rig_attributes.create_follow_attr(**cmd_info)
                    # - Compute unstitch command
                    unstitch_cmd_info = {"control" : cmd_info.get("driving"), "drivers" : cmd_info.get("options")}
                
                # - Parenting
                elif cmd_type == "parent":
                    # - Do it
                    child = cmd_info.get("child")
                    par = cmd_info.get("parent")
                    curr_par = child.relatives(0, p=True)
                    i_utils.parent(child, par)
                    # - Compute unstitch command
                    unstitch_cmd_info = {"child" : child, "parent" : curr_par}
                
                # - Constraining
                elif cmd_type == "constrain":
                    # - Do it
                    constraint = i_constraint.constrain(*cmd_info.get("args"), **cmd_info.get("kwargs"))
                    # - Compute unstitch command
                    unstitch_cmd_info = {"driven" : cmd_info.get("args")[-1], "driver" : cmd_info.get("args")[:-1],
                                         "constraints" : constraint, "cns_type" : cmd_info.get("kwargs").get("cns_type")}
                
                # - Delete Constraint
                elif cmd_type == "delete_constraint":
                    # - Do it
                    driven = cmd_info.get("driven")
                    cns = i_constraint.get_constraint_by_driver(driven=driven)
                    if not cns:
                        RIG_F_LOG.warn("No constraint driving '%s' to delete." % driven)
                        continue
                    cns = cns[0].node
                    cns_driver = list(set(cns.connections(s=True, d=False)))
                    for not_driver in [cns, driven]:
                        if not_driver in cns_driver:
                            cns_driver.remove(not_driver)
                    cns_type = cns.node_type()
                    cns_offset = False
                    if cns_type != "parentConstraint":  # Parent doesn't have offset attr
                        cns_offset = True if cns.offset.get() != [0, 0, 0] else False
                    # :TODO: May need to query more information in order to rebuild constraint on unstitch
                    i_utils.delete(cns)
                    # - Compute unstitch command
                    unstitch_cmd_info = {"driver" : cns_driver, "driven" : driven, "cns_type" : cns_type, "cns_offset" : cns_offset}
                
                # - Force Vis
                elif cmd_type == "force_vis":
                    # - Do it
                    objects = cmd_info.get("objects")
                    if not isinstance(objects, (list, tuple)):
                        objects = [objects]
                    value = cmd_info.get("value")
                    for obj in objects:
                        i_control.force_vis(obj, value)
                    # - Compute unstitch command
                    unstitch_cmd_info = {"objects" : objects, "value" : 0 if value is 1 else 1}
                
                # - Transfer Attributes
                elif cmd_type == "transfer_attributes":
                    # - Do it
                    from_node = cmd_info.get("from")
                    to_node = cmd_info.get("to")
                    i_attr.transfer_attributes(from_node=from_node, to_node=to_node,
                                               ignore_attrs=cmd_info.get("ignore"), action="promote")
                    # - Compute unstitch command
                    unstitch_cmd_info = {"from" : to_node, "to" : from_node}  # Reverse bc to_node is driving from_node
                
                # - Drive
                elif cmd_type == "drive":
                    # - Do it
                    driver = i_attr.Attr(cmd_info.get("driver"))
                    driven = i_attr.Attr(cmd_info.get("driven"))
                    orig_driver = driven.connections(s=True, d=False, plugs=True)
                    if orig_driver:
                        orig_driver = orig_driver[0]
                    driver.drive(driven, f=True)
                    # - Compute unstitch command
                    unstitch_cmd_info = {"driver" : driver, "driven" : driven, "orig_driver" : orig_driver}
                
                # - Shift follow attrs
                elif cmd_type == "shift_follow_attrs":
                    # - Do it
                    rig_attributes.shift_follow_attrs(control=cmd_info.get("control"))
                    # - Compute unstitch command
                    # :note: nothing is needed
                    continue
                
                # - Deleting things
                elif cmd_type == "delete":
                    # - Do it
                    stitch_del = cmd_info.get("stitch")
                    if stitch_del:
                        i_utils.delete(stitch_del)
                    # - Compute unstitch command
                    unstitch_del = cmd_info.get("unstitch")
                    if unstitch_del:
                        unstitch_cmd_info = {"objects" : unstitch_del}
                
                # - Something else
                elif cmd_type == "unique":
                    # - Do it
                    cmd = cmd_info.get("cmd")
                    if cmd:
                        try:
                            exec(cmd)
                        except Exception as e:
                            traceback.print_exc()
                            i_utils.error("Could not execute custom stitch command:\n%s\nError:\n%s" % (cmd, e))
                    # - Compute unstitch command
                    unstitch_cmd_info = {"cmd" : cmd_info.get("unstitch")}
                
                # - Add to unstitch info
                unstitch_cmds.append({cmd_type : unstitch_cmd_info})

        # Store Data
        self.__store_stitch_data(parent_info_node=parent_info_node)
        self.__store_unstitch_data(unstitch_data={parent_info_node : unstitch_cmds})
    
    def unstitch_bit(self, parent_info_node=None, clear_data=False, unstitch_children=False, dialog_error=False, raise_error=True):
        # No parent defined, do all
        if parent_info_node is None:
            stitched_parents = self._get_currently_stitched_data()
            RIG_F_LOG.debug("##VARCHECK stitched_parents:", stitched_parents)
            RIG_F_LOG.debug("##VARCHECK stitched_parents (types):", [type(par).__name__ for par in stitched_parents])
            if stitched_parents:
                RIG_F_LOG.debug("No parent given. Unstitching from all pre-defined parents.")
                for parent in stitched_parents:
                    RIG_F_LOG.debug("##VARCHECK parent: '%s' / type: '%s'" % (parent, type(parent).__name__))
                    self.unstitch_bit(parent_info_node=parent, clear_data=clear_data, unstitch_children=unstitch_children, 
                                      dialog_error=dialog_error, raise_error=raise_error)
            else:
                RIG_F_LOG.debug("No parents found or given to unstitch.")
            if not unstitch_children:
                return
        
        # Not unstitching parent? Only unstitching children?
        RIG_F_LOG.debug("##VARCHECK parent_info_node", parent_info_node)
        RIG_F_LOG.debug("##VARCHECK unstitch_children", unstitch_children)
        if not parent_info_node and unstitch_children:
            self.__unstitch_children(clear_data=clear_data, raise_error=raise_error, dialog_error=dialog_error)
            return

        # Get data
        unstitch_data = self.__get_unstitch_data()
        if parent_info_node not in unstitch_data.keys():
            i_utils.error("'%s' is not stitched to '%s'." % (parent_info_node, self.pack_info_node), dialog=dialog_error)
            return False
        parent_unstitch_data = unstitch_data.get(parent_info_node)

        # Verbose
        RIG_F_LOG.debug("Unstitching Bit: %s > %s." % (parent_info_node, self.pack_info_node))

        # Execute
        for cmd in parent_unstitch_data:
            for cmd_type, cmd_info in cmd.items():
                # - Follow Attr
                if cmd_type == "follow":
                    rig_attributes.delete_follow_attr(**cmd_info)
                
                # - Parenting
                elif cmd_type == "parent":
                    child = cmd_info.get("child")
                    parent = cmd_info.get("parent")
                    if not child.exists():
                        RIG_F_LOG.warn("Cannot unstitch parenting '%s' from '%s'. '%s' does not exist." % (child, parent, child))
                        continue
                    if not parent.exists():  # Parent pack deleted
                        RIG_F_LOG.warn("Cannot unstitch parenting '%s' from '%s'. '%s' does not exist." % (child, parent, parent))
                        parent = self.pack_grp
                        if not parent.exists():
                            i_utils.parent(child, w=True)
                            continue
                    i_utils.parent(child, parent)
                
                # - Constraining
                elif cmd_type == "constrain":
                    i_constraint.disconnect_constraint_by_driver(**cmd_info)

                # - Delete Constraint
                elif cmd_type == "delete_constraint":
                    driven = cmd_info.get("driven")
                    if not i_utils.check_exists(driven):
                        RIG_F_LOG.warn("Cannot unstitch constraint: '%s' does not exist." % driven)
                        continue
                    drivers = cmd_info.get("driver")
                    drivers_exist = True
                    for driver in drivers:
                        if not i_utils.check_exists(driver):
                            RIG_F_LOG.warn("Cannot unstitch constraint: '%s' does not exist." % driver)
                            drivers_exist = False
                    if not drivers_exist:
                        continue
                    i_constraint.constrain(drivers, driven, as_fn=cmd_info.get("cns_type"), mo=cmd_info.get("cns_offset"))

                # - Force Vis
                elif cmd_type == "force_vis":
                    objects = cmd_info.get("objects")
                    value = cmd_info.get("value")
                    for obj in objects:
                        i_control.force_vis(obj, value)

                # - Transfer Attributes
                elif cmd_type == "transfer_attributes":
                    from_node = cmd_info.get("from")
                    to_node = cmd_info.get("to")
                    i_node.disconnect_nodes_by_attributes(driver=from_node, driven=to_node)

                # - Drive
                elif cmd_type == "drive":
                    driven = cmd_info.get("driven")
                    if not i_utils.check_exists(driven):
                        RIG_F_LOG.warn("Cannot unstitch direct connection: '%s' does not exist." % driven)
                        continue
                    driver = cmd_info.get("driver")
                    if i_utils.check_exists(driver):
                        driver.disconnect(driven)
                    orig_driver = cmd_info.get("orig_driver")
                    if orig_driver:
                        if not i_utils.check_exists(orig_driver):
                            RIG_F_LOG.warn("Cannot direct connect post-unstitch: '%s' does not exist." % orig_driver)
                            continue
                        orig_driver.drive(driven)
                
                # - Delete
                elif cmd_type == "delete":
                    objects = cmd_info.get("objects")
                    i_utils.delete(objects)
                
                # - Something else
                elif cmd_type == "unique":
                    command = cmd_info.get("cmd")
                    try:
                        exec(command)
                    except Exception as e:
                        i_utils.error("Cannot unstitch '%s' from '%s' with custom command:\n%s\nError: '%s'." % 
                                      (self.base_name, parent_info_node.replace("_Info", ""), command, e), 
                                      raise_err=raise_error, verbose=not(raise_error))

        # Remove from currently stitched
        if not clear_data:  # This will already remove it from currently stitched
            RIG_F_LOG.debug("##VARCHECK pack_info_node: '%s' / type: '%s'" % (parent_info_node, type(parent_info_node).__name__))
            self.__store_currently_stitched_data(packs_remove=parent_info_node)

        # Return Passed
        return True