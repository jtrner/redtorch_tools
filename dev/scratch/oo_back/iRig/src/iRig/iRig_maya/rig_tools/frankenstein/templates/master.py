import cPickle as pickle
import collections

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools  # Need to have for the eval
from rig_tools.frankenstein import RIG_F_LOG

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.nodes as rig_nodes
import rig_tools.utils.controls as rig_controls
import rig_tools.frankenstein.utils as rig_frankenstein_utils
import rig_tools.frankenstein.core.cog as rig_cog


class Template_Master():

    def __init__(self):
        # Main Vars
        self.template_type = self.__class__.__name__.split("Template_")[1]
        self.top_group_name = self.template_type
        self.ctrl_size = 10
        self.pack_size = None
        self.do_stitch = True
        
        # Do certain actions?
        self.create_geo_res_groups = True
        self.do_proxy_setup = True
        self.do_vis_res_attrs = True
        self.do_scale_setup = True
        self.cleanup_all_attrs = False

        # Groups
        self.groups = []
        self.group_main = None
        self.group_geo = None
        self.group_geo_hi = None
        self.group_geo_lo = None
        self.ctrl_grp = None
        self.ctrl_cns_grp = None
        self.group_jnt = None
        self.group_jnt_no_inherit = None
        self.group_jnt_rig = None
        self.group_jnt_bind = None
        self.utility_grp = None
        self.utility_cns_grp = None
        self.group_helper_geo = None

        # Controls
        self.controls = []
        # - Changeable
        self.with_gimbals = True  # Only affects Root/Ground/Cog
        # - Root
        self.root_ctrl_shape = "Root Compass"
        self.root_ctrl_color = "black"
        self.root_ctrl_size_mult = 3.0
        # - Ground
        self.ground_ctrl_shape = "2D Twist Cuff"
        self.ground_ctrl_color = "black"
        self.ground_ctrl_size_mult = 2.0
        # - COG
        self.cog_ctrl_shape = "2D Arrow 4Way"
        self.cog_ctrl_color = i_node.get_default("CtrlColorSide", "center")
        self.cog_ctrl_gimbal_color = i_node.get_default("CtrlColorSide", "center_secondary")
        self.cog_ctrl_size_mult = 1.0

        # Misc Nodes/Attrs
        self.proxy_rev = None
        self.scale_xyz = None
        self.info_node = None
        
        # Gen pack overrides
        self.override_orientation = False
        self.orient_joints = "yzx"  # Most work with "xyz" or "yzx"
        self.orient_joints_up_axis = "yup"

        # For templates use
        self.pack_options = []
        self.packs = []
        self.pack_objects = {}
        self.pack_info_overrides = {}
        self.prompt_info = collections.OrderedDict()
        self.prompt_display_info = collections.OrderedDict()

        # Get import information
        self.imp_module = self.__module__
        self.imp_class = self.__class__.__name__
    
    def _class_prompts(self):
        return  # Optional for classes
    
    def get_prompt_info(self):
        # Master Prompt (chaneable) Info
        self.prompt_info["do_stitch"] = {"type": "checkBox", "value": self.do_stitch}
        
        # Master Prompt (display-only) Info
        if self.override_orientation:
            self.prompt_display_info["orient_joints"] = "orient_joints"
            self.prompt_display_info["orient_joints_up_axis"] = "orient_joints_up_axis"
        
        # Inherited by class
        self._class_prompts()

    def _check(self):
        return  # Optional check functionality for individual templates

    def check(self):
        # Already made a template?
        top_group = rig_nodes.get_top_group(raise_error=False)
        if top_group:
            statement = "Template already in scene. Delete the existing one before creating another."
            i_utils.message(title="Not building second template", message=statement, button=['Got It'])
            self.can_build = False
        else:
            self.can_build = True
        
        if not self.can_build:
            return
        
        self._check()

    def _define_build_type_option(self, cls_attr=None, options=None):
        opts_in_pack_options = [opt for opt in options if opt in self.pack_options]

        if len(opts_in_pack_options) == 1:  # Option choice overridden by Packs IO
            setattr(self, cls_attr, opts_in_pack_options[0])
            return

        curr = getattr(self, cls_attr)
        if curr is None or curr in options:  # Intentionally not defined
            setattr(self, cls_attr, curr)
            return
        if curr not in options:
            i_utils.error("%s type must be '%s' or '%s'. Given: '%s'" % (cls_attr.capitalize(), options[0], options[1], curr), dialog=True)
            self.can_build = False

    def _group(self, name=None, parent=None):
        grp = i_node.create("transform", n=name, use_existing=True, parent=parent)
        self.groups.append(grp)
        return grp
    
    def create_groups(self):
        # Main Group
        self.group_main = self._group(self.top_group_name)

        # Geo Groups
        self.group_geo = self._group("Geo_Grp", self.group_main)
        if self.create_geo_res_groups:
            self.group_geo_hi = self._group("HiRes_Geo_Grp", self.group_geo)
            self.group_geo_lo = self._group("LowRes_Geo_Grp", self.group_geo)
            scene_geo_shapes = i_utils.ls(type="mesh")
            if scene_geo_shapes:
                scene_geo = [shp.relatives(p=True, type="transform") for shp in scene_geo_shapes]
                world_geo = [geo for geo in scene_geo if not geo.relatives(p=True)]  # Ignores face things and groups
                if world_geo:
                    i_utils.parent(world_geo, self.group_geo_hi)

        # Control Groups
        self.ctrl_grp = self._group("Ctrl_Grp", self.group_main)
        self.ctrl_cns_grp = self._group("Ctrl_Cns_Grp", self.ctrl_grp)

        # Utility Groups
        self.utility_grp = self._group("Utility_Grp", self.group_main)
        self.utility_cns_grp = self._group("Utility_Cns_Grp", self.utility_grp)

        # Joint Groups
        self.group_jnt = self._group("Jnt_Grp", self.group_main)
        self.group_jnt_no_inherit = self._group("No_Inherit_Grp", self.group_jnt)
        self.group_jnt_no_inherit.inheritsTransform.set(0)
        self.group_jnt_rig = self._group("Rig_Jnt_Grp", self.group_jnt)
        self.group_jnt_bind = self._group("Bind_Jnt_Grp", self.group_jnt)

        # Export Data Group
        if i_utils.check_exists("ExportData"):
            i_utils.parent("ExportData", self.utility_grp)
        
        # Helper Geo Group
        self.group_helper_geo = self._group("Helper_Geo_Grp", self.group_main)

        # Info Node
        self.info_node = i_node.create_info_node(parent=self.group_main)
        
        # Connect to info node
        i_node.connect_to_info_node(info_attribute="Top_Group", objects=[self.group_main])
        i_node.connect_to_info_node(info_attribute="Geo_Group", objects=[self.group_geo])
        i_node.connect_to_info_node(info_attribute="Ctrl_Group", objects=[self.ctrl_grp])
        i_node.connect_to_info_node(info_attribute="Utility_Group", objects=[self.utility_grp])
        i_node.connect_to_info_node(info_attribute="Jnt_Group", objects=[self.group_jnt])
        i_node.connect_to_info_node(info_attribute="HelperGeo_Group", objects=[self.group_helper_geo])
        
        # Include in the hierarchy attr for queries
        i_node.connect_to_info_node(node=self.group_main, info_attribute="RigHierarchy", objects=self.groups)

    def _dupe_pack_overrides(self, build_type=None, upd_dict=None):
        if not self.pack_info_overrides.get(build_type):
            self.pack_info_overrides[build_type] = [upd_dict]

        elif isinstance(self.pack_info_overrides.get(build_type), dict):  # From UI
            orig_pack_ovrds = self.pack_info_overrides.get(build_type).copy()
            if not orig_pack_ovrds.get("description"):  # Not specified
                orig_pack_ovrds.update(upd_dict)
            self.pack_info_overrides[build_type] = [orig_pack_ovrds]

        elif len(self.pack_info_overrides.get(build_type)) < 2:
            orig_pack_ovrds = self.pack_info_overrides.get(build_type)[0].copy()
            orig_pack_ovrds.update(upd_dict)
            self.pack_info_overrides[build_type].append(orig_pack_ovrds)

    def _add_packs(self):
        self.packs.append(rig_cog.Build_Cog)  # Does Root, Ground and Cog
        
        if not self.pack_info_overrides.get("Cog"):
            self.pack_info_overrides["Cog"] = {"with_gimbal" : self.with_gimbals,
                                               "root_ctrl_shape": self.root_ctrl_shape,
                                               "root_ctrl_color": self.root_ctrl_color,
                                               "root_ctrl_size_mult": self.root_ctrl_size_mult * self.ctrl_size,
                                               "ground_ctrl_shape": self.ground_ctrl_shape,
                                               "ground_ctrl_color": self.ground_ctrl_color,
                                               "ground_ctrl_size_mult": self.ground_ctrl_size_mult * self.ctrl_size,
                                               "cog_ctrl_shape": self.cog_ctrl_shape,
                                               "cog_ctrl_color": self.cog_ctrl_color,
                                               "cog_ctrl_gimbal_color": self.cog_ctrl_gimbal_color,
                                               "cog_ctrl_size_mult": self.cog_ctrl_size_mult * self.ctrl_size * 5.5,
                                               "do_scale_setup" : self.do_scale_setup,
                                               "cleanup_all_attrs" : self.cleanup_all_attrs,
                                               }
    
    def _build_packs(self):
        # Vars
        self.info_nodes = {}
        self.left_packs = {}
        
        # Build
        pack_override_ind_built = {}
        for pk in self.packs:
            # - Update pack values
            build_type = pk.__name__.replace("Build_", "")
            pack_obj = pk()
            overrides = self.pack_info_overrides.get(build_type)
            override_i = None
            if overrides:
                if isinstance(overrides, (list, tuple)):  # Multiple packs of same type (ex: Quadruped has 2 sets of legs)
                    if build_type in pack_override_ind_built.keys():
                        override_i = pack_override_ind_built.get(build_type)[-1] + 1
                    else:
                        override_i = 0
                    overrides = overrides[override_i]
                for k, v in overrides.items():
                    setattr(pack_obj, k, v)
            # if not overrides or "pack_size" not in overrides.keys():  # :note: Don't do because then control size / joint radius won't update
            #     pack_obj.pack_size = self.pack_size
            if self.override_orientation:
                pack_obj.orient_joints = self.orient_joints
                pack_obj.orient_joints_up_axis = self.orient_joints_up_axis
            # - Build pack
            pack_obj.do_stitch = False  # Regardless of if template stitching, don't do stitch things per-pack. Need to do all at once
            pack_obj.create_pack()
            desc = pack_obj.description
            if pack_obj.side == "L":
                self.left_packs[desc] = pack_obj
            self.pack_objects[desc] = pack_obj
            self.info_nodes[desc] = pack_obj.pack_info_node
            if override_i is not None:
                if build_type not in pack_override_ind_built:
                    pack_override_ind_built[build_type] = []
                pack_override_ind_built[build_type].append(override_i)

        self.cog_pack_obj = self.pack_objects.get("COG")
    
    def create_bits(self):
        # Build the COG bit
        self.cog_pack_obj.create_bit()
        
        # Add pack infos to class attrs
        self.controls += self.cog_pack_obj.created_controls

    def _position_packs(self):
        return

    def _do_stitch_packs(self, driven_obj=None, driver_objs=None, parent_obj=None, do_parenting=None):
        if not driven_obj:
            return

        for driver in driver_objs:
            if not driver:
                continue
            dp = False if not parent_obj or driver != parent_obj else do_parenting
            driven_obj.stitch_pack(parent_info_node=driver.pack_info_node, do_parenting=dp)

    def _stitch_packs(self):
        return 
    
    def _post_stitch_packs(self):
        return

    def _mirror(self):
        # Check
        if not self.left_packs:
            return
        
        # :note: Need to do all (un)stitching of all packs all at once, so can't use the unstitch/stitch inside mirror_pack()

        # Unstitch
        if self.do_stitch:
            for pack_obj in self.pack_objects.values():
                pack_obj.unstitch_pack(raise_error=False)

        # Mirror. Do without stitching because parent won't always pre-exist
        self.mirror_info_nodes = {}
        self.mirror_pack_objects = {}
        for pack_desc, l_pack in self.left_packs.items():
            mirror_info_node = rig_frankenstein_utils.mirror_pack(pack_info_node=l_pack.pack_info_node, do_stitch=False)  # Force no stitch
            self.mirror_info_nodes[pack_desc] = mirror_info_node
            self.mirror_pack_objects[pack_desc] = rig_frankenstein_utils.get_pack_object(mirror_info_node)

        # Re-stitch
        # :note: Do after all mirrors built so everything can exist
        if self.do_stitch:
            for pack_obj in self.pack_objects.values():
                pack_obj.stitch_pack(raise_error=False)  # Takes care of mirror stitching too
    
    def __add_vis_res_attributes(self):
        # Geo Vis
        i_attr.create_vis_attr(node=self.group_main, ln='GeoVis', drive=self.group_geo, dv=1)
        self.group_geo.overrideEnabled.set(1)

        # Geo Lock
        # :note: Cannot use create_dis_attr() bc that's different
        geo_lock = i_attr.create(node=self.group_main, ln="GeoLock", at="enum", dv=2, en="Normal:Template:Reference:", k=False, cb=True)
        geo_lock.drive(self.group_geo.overrideDisplayType)

        # Ctrl Vis
        i_attr.create_vis_attr(node=self.group_main, ln='CtrlVis', drive=self.ctrl_grp, dv=1)

        # Joint Vis
        i_attr.create_vis_attr(node=self.group_main, ln='JointVis', drive=self.group_jnt, dv=0)
        i_attr.create_vis_attr(node=self.group_jnt_rig, ln='RIG', drive=self.group_jnt_rig, dv=1)
        i_attr.create_vis_attr(node=self.group_jnt_bind, ln='BindJoint', drive=self.group_jnt_bind, dv=1)

        # Utility Vis
        i_attr.create_vis_attr(node=self.group_main, ln='UtilityVis', drive=self.utility_grp, dv=0)
        
        # Helper Geo Vis
        i_attr.create_vis_attr(node=self.group_main, ln="PinkHelper", drive=self.group_helper_geo, dv=1)
        
        # Save Defaults
        i_attr.update_default_attrs(nodes=[self.group_main, self.group_jnt_rig, self.group_jnt_bind])
        
        # Set to rigger's visual
        rig_nodes.set_to_rigging_vis()

    def __add_proxy_setup(self):
        # Create Reverse
        self.proxy_rev = i_node.create("reverse", n="ProxyVisSwitch_REV", use_existing=True)
        if self.proxy_rev.existed:
            RIG_F_LOG.warn("%s already existed. Skipping additional connections and cleanup for it." % self.proxy_rev)
            return 

        # Add Proxy Vis attribute
        proxy_vis = i_attr.create_vis_attr(node=self.group_main, ln='ProxyVis', drive=self.group_geo_lo, dv=0)

        # Connect Attr to Rev
        proxy_vis.drive(self.proxy_rev.inputX)
        self.proxy_rev.outputX.drive(self.group_geo_hi.v)

        # Cleanup
        i_attr.lock_and_hide(node=self.proxy_rev, attrs=["inputX", "inputY", "inputZ"], lock=True, hide=True)
    
    def create(self):
        # Used for simpler setups (i.e. not Biped)
        self.create_packs()
        if not self.can_build:
            return 
        self.create_bits()
        self.cleanup()
    
    def _create_packs(self):
        return  # Optional for other templates to use
    
    def create_packs(self):
        # Check
        self.check()
        if not self.can_build:
            return
        
        # Previous Packs
        prev_pack_info_nodes = rig_frankenstein_utils.get_scene_packs()
        
        # Groups
        self.create_groups()

        # Add packs
        self._add_packs()
        
        # Get pack size
        self.pack_size = rig_frankenstein_utils.get_model_size() or 1.01
        # :note: ^ 1.01 so don't get warning about not able to calc bc that would be for every pack

        # Build Packs
        self._build_packs() 

        # Position joints
        self._position_packs()

        # Stitch
        if self.do_stitch:
            self._stitch_packs()
        
        # Post-Stitch
        self._post_stitch_packs()
        
        # Mirror
        self._mirror()
        
        # Optional additional packs in template
        self._create_packs()
        
        # If template made after individual packs, stitch previous packs to top node
        if prev_pack_info_nodes:
            i_node.connect_to_info_node(info_attribute="info_nodes", objects=prev_pack_info_nodes, node=self.group_main)
    
    def _cleanup(self):
        return  # Optional for templates to use. Happens at end of cleanup

    def cleanup(self):
        # Attributes
        if self.do_proxy_setup:
            self.__add_proxy_setup()
        if self.do_vis_res_attrs:
            self.__add_vis_res_attributes()
        i_attr.create(node=self.group_main, ln="build_template_type", dt="string", dv=self.template_type, l=True)

        # Lock and Hide group trs
        for grp in self.groups:
            if grp.endswith("_Cns") or grp.endswith("_Cns_Grp"):  # Animation request
                attrs = ["v"]
                if grp.name in [self.ctrl_cns_grp, self.utility_cns_grp]:
                    attrs += ["t", "r", "s"]
            else:
                attrs=["t", "r", "s", "v"]

            i_attr.lock_and_hide(node=grp, attrs=attrs, lock=True, hide=True)

        # Cleanup Pack Groups
        i_utils.select(cl=True)
        i_node.Node("BuildPack_Grp").set_parent(self.utility_grp)
        
        # Select cog offset
        if self.cog_pack_obj.bit_built:
            i_utils.select(self.cog_pack_obj.cog_ctrl.top_tfm)
        
        # Optional Template Cleanup
        self._cleanup()
        
        # Store data
        self.__store_data()
    
    def __store_data(self):
        # Vars
        template_data = {}
        
        # Get existing
        if i_utils.check_exists(self.group_main + ".template_data"):
            data_as_str = self.group_main.template_data.get()
            template_data = pickle.loads(str(data_as_str))
        
        # Class attrs
        template_data.update(self.__dict__.copy())
        
        # Remove Pack Objects from list. Will get the live ones when need
        for obj in ["pack_objects", "mirror_pack_objects"]:
            if obj in template_data.keys():
                del(template_data[obj])
        
        # Store
        template_data_pickle = pickle.dumps(template_data)
        i_attr.create(node=self.group_main, ln="template_data", at="string", dv=str(template_data_pickle), l=True, use_existing=True)
    
    def __get_data(self):
        if not self.group_main:
            self.group_main = i_node.Node(self.top_group_name)
        
        # Get stored
        data_as_str = self.group_main.template_data.get()
        data_eval = pickle.loads(str(data_as_str))
        for cls_attr, cls_val in data_eval.items():
            setattr(self, cls_attr, cls_val)
        
        # Re-get the pack things
        info_nodes = rig_frankenstein_utils.get_scene_packs(dialog_error=False)
        self.pack_objects = {}
        self.mirror_pack_objects = {}
        self.cog_pack_obj = None
        for pack_info_node in info_nodes:
            pack_obj = rig_frankenstein_utils.get_pack_object(pack_info_node)
            if pack_obj.is_mirror:
                self.mirror_pack_objects[pack_obj.description] = pack_obj
            else:
                self.pack_objects[pack_obj.description] = pack_obj
            if pack_obj.build_type == "Cog":
                self.cog_pack_obj = pack_obj
    
    def _pre_bits(self):
        return  # Optional for templates to use
    
    def pre_bits(self):
        self.__get_data()
        
        # Re-establish pack size
        self.pack_size = rig_frankenstein_utils.get_model_size() or 1.01
        
        self._pre_bits()
    
    def _post_bits(self):
        return  # Optional for templates to use
    
    def post_bits(self):
        self.__get_data()
        self._post_bits()
        rig_controls.set_all_vis_attrs(set=1)


