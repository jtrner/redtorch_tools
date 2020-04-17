import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os
import pkgutil
from pyclbr import readmodule
import collections
import cPickle as pickle
import importlib

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint
import logic.py_types as logic_py

from rig_tools.frankenstein import RIG_F_LOG

import rig_tools.utils.joints as rig_joints
import rig_tools.utils.nodes as rig_nodes
import rig_tools.utils.io as rig_io
from rig_tools.utils.io import DataIO
import rig_tools.utils.misc as rig_misc


def get_all_pack_options(ignore=None):
    """
    Get all buildable pack options based on the files found in the rig_tools/frankenstein package.
    
    :param ignore: (list of strs) - (optional) Build file names to ignore (ex: "limb")
        Default includes "master" and "code"
    
    :return: (dict) {PackName (str) : PackDefaultInfo (dict)}
        The PackDefaultInfo is based on the instanced pack class's available dict.
    """
    sub_dirs = [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)])]
    print sub_dirs
    if not ignore:
        ignore = []
    ignore += ["master", "code"]
    # ignore = list(set(ignore))

    build_packs = {}
    for subdir in sub_dirs:
        if subdir == "templates":
            continue
        pkgpath = os.path.dirname(__file__) + "\\" + subdir
        build_pack_modules = [name for _, name, _ in pkgutil.iter_modules([pkgpath]) if name not in ignore]
        for module in build_pack_modules:
            pack_imp = "rig_tools.frankenstein.%s.%s" % (subdir, module)
            rig_pack_mod = importlib.import_module(pack_imp)
            classes = readmodule(pack_imp).keys()  # Also gets classes imported in file
            for pack_class_nm in classes:
                pack_nn = pack_class_nm.replace("Build_", "")
                if pack_nn.lower() in ignore or pack_nn.lower().endswith("_master"):
                    continue
                pack_class = getattr(rig_pack_mod, pack_class_nm)
                pack_info = pack_class()
                if not pack_info:
                    RIG_F_LOG.warn("No info found for %s" % pack_nn)
                    continue
                build_packs[pack_nn] = pack_info.__dict__

    return build_packs


def get_all_template_options(ignore=None):
    """
    Get all buildable template options based on the files found in the rig_tools/frankenstein package.

    :param ignore: (list of strs) - (optional) Build file names to ignore (ex: "prop")
        Default includes "master"

    :return: (dict) {PackName (str) : PackDefaultInfo (dict)}
        The PackDefaultInfo is based on the instanced pack class's available dict.
    """
    templateDirPath = os.path.dirname(__file__) + "\\templates"

    # list of modules to ignore in templates directory
    if not ignore:
        ignore = ("master")

    # assemble template module names excluding ones in "ignore" list
    template_modules = [name for _, name, _ in pkgutil.iter_modules([templateDirPath]) if name.lower() not in ignore]

    templates = {}
    for module in template_modules:
        if module.lower() in ignore:
            continue
        template_imp = "rig_tools.frankenstein.templates.%s" % (module)
        rig_template_mod = importlib.import_module(template_imp)
        classes = readmodule(template_imp).keys()  # Also gets classes imported in file
        for template_class_nm in classes:
            template_nn = template_class_nm.replace("Template_", "").replace("_", " ")
            if template_nn.lower() in ignore:
                continue
            template_class = getattr(rig_template_mod, template_class_nm)
            template_info = template_class()
            if not template_info:
                RIG_F_LOG.warn("No info found for %s" % template_nn)
                continue
            templates[template_nn] = template_info.__dict__

    return templates


def get_model_size():
    """
    Get an estimated model size. Used primarily to determine pack build size.
    :return: (float) Pack size to be used.
    """
    pack_size = None

    scene_geo = cmds.ls(type="mesh")  # :note: keep cmds
    if scene_geo:
        model_geo = [geo for geo in scene_geo if "Face_Rig" not in geo]
        bbox = cmds.exactWorldBoundingBox(model_geo)
        bbox_x_range = round(abs(bbox[3] - bbox[0]), 3) / 2.0
        pack_size = round(bbox_x_range / 9.25, 3)  # :note: TTM Leo needs '/ 11.5"

    return pack_size


def test_basic():
    """
    Test build a basic character template.
    :return: None
    """
    import rig_tools.frankenstein.templates.character as tpt_c

    char = tpt_c.Template_Character()
    char.create()
    geos = char.group_geo_hi.relatives(c=True)
    cog_control = char.cog_pack_obj.cog_ctrl.last_tfm
    
    if geos:
        for geo in geos:
            i_constraint.constrain(cog_control, geo, mo=True, as_fn="parent")
            i_constraint.constrain(cog_control, geo, mo=True, as_fn="scale")

    i_utils.select(cog_control)

    return char


def test_template(template=None, with_geo=False):
    """
    Test build a specific template type.
    
    :param template: (str) - Template to build.
        Does not accept the basic template types: "character", "prop", "set", "vehicle", "master".
        Additionally Accepts "Biped_Alt" to use the non-default pack type options for things like head, spine, etc.
    :param with_geo: (bool) - Create and bind basic cylinder geo post-build?
    
    :return: None
    """
    # Turn on waitcursor
    cmds.waitCursor(state=True)

    # New scene
    cmds.file(new=True, f=True)

    # Get template information
    all_templates = get_all_template_options(ignore=["character", "prop", "set", "vehicle"])
    build_obj = get_pack_object(pack_defaults=all_templates.get(template.replace("_Alt", "")).copy())
    if template == "Biped_Alt":
        build_obj.head_type = "Head_Squash"
        build_obj.spine_type = "Spine_IkFk"
        build_obj.arm_type = "Arm_Watson"
        build_obj.leg_type = "Leg_Watson"
        build_obj.foot_type = "Foot_Watson"

    # Create Packs
    build_obj.create()

    # Get pack objects and in building order
    pack_info_nodes = sorted(build_obj.info_nodes.values() + build_obj.mirror_info_nodes.values())
    pack_objs = []
    cog_obj = None
    for info_node in sorted(pack_info_nodes):
        pack_obj = get_pack_object(info_node)
        if pack_obj.bit_built:
            continue
        pack_objs.append(pack_obj)
        if pack_obj.build_type == "Cog":
            cog_obj = pack_obj
    if cog_obj:
        pack_objs.remove(cog_obj)
        pack_objs.insert(0, cog_obj)

    # Unstitch All
    for pack_obj in pack_objs:
        pack_obj.unstitch_pack(raise_error=False)

    # Template pre-bits
    build_obj.pre_bits()

    # Build Bits
    for pack_obj in pack_objs:
        pack_obj.do_stitch = False  # Override because stitching is all happening at once
        pack_obj.create_bit()

    # Stitch
    for pack_obj in pack_objs:
        pack_obj.stitch_bit(raise_error=False)

    # Template post-bits
    build_obj.post_bits()

    # Clear selection
    i_utils.select(cl=True)

    # Add Geo
    if with_geo:
        pack_controls = [pack_obj.created_controls[0] for pack_obj in pack_objs
                         if pack_obj.build_type not in ["Cog"] and len(pack_obj.base_joints) > 1]
        i_utils.select(pack_controls)
        test_add_geo()

    # Frame
    i_utils.focus(type="joint")

    # Turn off waitcursor
    cmds.waitCursor(state=False)


def test_add_geo(all_packs=False):
    """
    Easy test ability of adding/skinning cylinder geo to a pack.
    
    :param all_packs: (bool) - Run on all in-scene packs (ignores Cogs)?
        If False - Uses packs by selection
    
    :return: None
    """
    # Get selected packs
    if all_packs:
        pack_info_nodes = [pin for pin in get_scene_packs(check_sel=False) if "COG" not in pin]
    else:
        pack_info_nodes = get_pack_from_obj_sel(dialog_error=True)
    if not pack_info_nodes:
        return
    
    # Create group
    test_geo_grp = i_node.create("transform", n="TEST_GEO_GRP", use_existing=True)

    # Loop
    geos = []
    for pack_info_node in pack_info_nodes:
        # - Vars
        pack_obj = get_pack_object(pack_info_node)
        if pack_obj.chain_indexes and pack_obj.chain_indexes[0] is not None:
            msg = "Building test geo for chain packs ('%s') not currently supported (%s)." % (pack_obj.build_type, pack_obj.chain_indexes)
            if len(pack_info_nodes) == 1:
                i_utils.error(msg, dialog=True)
                return
            else:
                RIG_F_LOG.warn(msg)
            continue
        ns = pack_info_node.split(":")[0] + ":" if ":" in pack_info_node else ""  # In case imported a scene (Steven) (AUTO-865)
        base_name = pack_obj.base_name
        base_joints = pack_obj.base_joints
        is_right = pack_obj.side == "R"
        build_type = pack_obj.build_type
        bind_joints = pack_obj.bind_joints
        sxz = pack_obj.joint_radius * 0.8
        # - Figure out geo section names
        joint_names = pack_obj.joint_names
        base_joint_name = None
        use_joint_names = True
        for jn in joint_names:
            num = logic_py.find_numbers_in_string(jn)
            if not num:
                continue
            bjn = jn.split(num[0])[0]
            if not base_joint_name:
                base_joint_name = bjn
            else:
                if bjn == base_joint_name:
                    use_joint_names = False
                    break
        if not use_joint_names:
            joint_names = [base_joint_name]
        geo_sects = [sect.capitalize() for sect in joint_names]
        # - Match the geo section with their joints
        geo_sect_joints = {}
        if use_joint_names:  # Individual sections
            # sy = (pack_obj.pack_size / (len(base_joints[:-1]))) * 1.5
            default_cyl_sy_eval = 2.0  # Hardocded bc it's 2 units
            for i, jnt in enumerate(base_joints[:-1]):
                if i != 0:
                    dist = i_utils.get_single_distance(from_node=base_joints[i - 1], to_node=jnt)
                else:
                    dist = i_utils.get_single_distance(from_node=jnt, to_node=base_joints[i + 1])
                sy = dist * (1.0 / default_cyl_sy_eval)
                geo_sect_joints[geo_sects[i]] = {"jnts" : [ns + jnt], "scale" : [sxz, sy, sxz]}
        else:  # One geo tube for whole pack
            sy = pack_obj.pack_size
            geo_sect_joints[geo_sects[0]] = {"jnts" : [ns + jnt for jnt in bind_joints], "scale" : [sxz, sy, sxz]}
        # - Build for each joint
        for geo_sect, info in geo_sect_joints.items():
            jnts = info.get("jnts")
            scale = info.get("scale")
            sect_name = base_name + "_" + geo_sect
            # - Create Geo
            cmds.select(cl=True)
            geo, pc = cmds.polyCylinder(name=sect_name + "_Geo", sy=10)
            cmds.select(cl=1)
            cmds.setAttr(pc + ".subdivisionsCaps", 1)
            piv = [0, -1, 0]
            if is_right:
                piv[1] *= -1
            cmds.move(piv[0], piv[1], piv[2], geo + ".scalePivot")  # Set pivot at bottom of geo
            cmds.move(piv[0], piv[1], piv[2], geo + ".rotatePivot")  # Set pivot at bottom of geo
            pac = i_constraint.constrain(jnts[0], geo, as_fn="parent")
            pac.delete()
            # i_node.copy_pose(snap_joint, geo, use_object_pivot=True)  # , attrs=["t", "r"], attrs=["r"]
            cmds.setAttr(geo + ".s", *scale)
            # - Skin
            cmds.select(cl=True)
            if build_type in ["Limb", "Arm", "Leg"]:
                sect_bind_joints = cmds.ls(ns + sect_name + "_Bend?_Bnd_Jnt")
                skin = cmds.skinCluster(sect_bind_joints, geo)
                cmds.skinCluster(skin, e=True, removeInfluence=ns + sect_name + "_Bend_Parent_Jnt")  # for some reason still skins...
            else:
                cmds.skinCluster(bind_joints, geo)
            # - Cleanup
            cmds.select(cl=True)
            geos.append(geo)
    
    # Parent
    if geos:
        i_utils.parent(geos, test_geo_grp)

    # Turn on wireframe
    model_panels = [mod_pan for mod_pan in pm.getPanel(vis=True) if cmds.getPanel(typeOf=mod_pan) == "modelPanel"]
    for mod_pan in model_panels:
        model_editor = cmds.modelPanel(mod_pan, q=True, modelEditor=True)
        cmds.modelEditor(model_editor, e=True, wireframeOnShaded=True)


def get_scene_template():
    """
    Get the in-scene template, if there is one.
    :return: (str) - Template type. Ex: "biped".
    """
    built_template = None
    top_grp = rig_nodes.get_top_group(raise_error=False)
    if top_grp:
        built_template = top_grp.build_template_type.get()
    return built_template


def get_template_object(template_type=None, template_defaults=None, scene_template=False, raise_error=True):
    """
    Get the instanced object for a template
    
    :param template_type: (str) - (optional) The type of template. If not defined, :param scene_template: must be True.
    :param template_defaults: (dict) - (optional) Default values to update the object's dict to
    :param scene_template: (bool) - Use the scene template? If False, :param template_type: must be used.
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (obj) - Template object
    """
    # Get template defaults
    all_template_defaults = get_all_template_options()
    if scene_template:
        template_type = get_scene_template()
    if template_type:
        template_defaults = all_template_defaults.get(template_type)
    
    # Check found
    if not template_defaults:
        i_utils.error("No defaults or template type given or found.", raise_err=raise_error, verbose=not(raise_error))
        return
    
    # Get object
    template_module = importlib.import_module(template_defaults.get("imp_module"))
    template_class = getattr(template_module, template_defaults.get("imp_class"))
    template_obj = template_class()

    # Update instantiated with data
    template_obj.__dict__.update(template_defaults)
    
    # Return
    return template_obj


def get_pack_object(pack_info_node=None, pack_defaults=None, non_setting=None, raise_error=True):
    """
    Get instanced pack object.
    
    :param pack_info_node: (iNode) - (optional) Pack's Info Node (ex: L_Leg_Info). If not defined, must use :param pack_defaults"
    :param pack_defaults: (dict) - (optional) Pack's defaults from the object's dict. If not defined, must use :param pack_info_node:
    :param non_setting: (list of strs) - (optional) Keys in the object's dict not to set.
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (obj) - Pack object
    """
    # Get stored data
    info_as_dict = None
    if pack_info_node:
        pin_exists = i_utils.check_arg(pack_info_node, "pack info node", exists=True, raise_error=raise_error)
        if not pin_exists:
            return
        RIG_F_LOG.debug("##VARCHECK pack_info_node: '%s' / type: '%s'" % (pack_info_node, type(pack_info_node).__name__))
        if not i_utils.check_exists(pack_info_node + ".build_data"):  # TEMP backwards compatibility (mostly for Cogs on EAV)
            RIG_F_LOG.warn("%s is old and does not have a 'build_data' attribute. Default data may be lost." % pack_info_node)
            imp_call = pack_info_node.pack_imp_call.get()
            info_as_dict = {"imp_module" : ".".join(imp_call.split(".")[:-1]), "imp_class" : imp_call.split(".")[-1]}
        else:
            info_as_dict = pickle.loads(pack_info_node.build_data.get())
    elif pack_defaults:
        info_as_dict = pack_defaults
    if not info_as_dict:
        i_utils.error("Need to define either pack_info_node or pack_defaults.")
    
    # Instantiate
    rig_pack_module = importlib.import_module(info_as_dict.get("imp_module"))
    pack_class = getattr(rig_pack_module, info_as_dict.get("imp_class"))
    pack_obj = pack_class()

    # Update instantiated with data
    # pack_obj.__dict__.update(info_as_dict)
    for k, v in info_as_dict.items():
        # - Do extra re-wrapping crap because the hashes on the stored_attrs when renaming nodes gets borked and is annoying
        # # :note: Cannot just use convert_data because some things need to stay strings even when there's a node in the scene with that name
        if non_setting and k in non_setting:
            continue
        elif k == "pack_joints" and v:  # Mostly for COG, which has a description and base joint named "COG", meaning the joint exists and gets confused
            new_v = collections.OrderedDict()
            for sub_k, sub_v in v.items():
                gen_sub_v = i_utils.convert_data(sub_v)
                conv_sub_v = i_utils.convert_data(gen_sub_v, to_generic=False)
                new_v[sub_k] = conv_sub_v
            setattr(pack_obj, str(k), new_v)
            continue
        elif k.endswith("_name") or k in ["side", "description"]:
            setattr(pack_obj, str(k), v)
            continue
        # try:
        gen_v = i_utils.convert_data(v)
        conv_v = i_utils.convert_data(gen_v, to_generic=False)
        if not conv_v:
            conv_v = v
        # except:  # Usually build objects from frankenstein (ex: "eye_pack_objs")
        #     RIG_F_LOG.warn("Failed to convert data for '%s'. (Type: '%s')" % (k, type(v).__name__))
        #     conv_v = v
        # # - Set attr on the object
        # setattr(pack_obj, str(k), v)
        setattr(pack_obj, str(k), conv_v)
    
    # Return
    return pack_obj


def force_reorient_base_joints(pack_info_node=None):
    """
    Reorient pack joints based on pack's orient joint information
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    
    :return: None
    """
    # Get pack object
    pack_obj = get_pack_object(pack_info_node=pack_info_node)

    # Unstitch
    pack_obj.unstitch_pack(raise_error=False)
    
    # Orientation Vars
    ori = pack_obj.orient_joints
    ori_up = pack_obj.orient_joints_up_axis
    if not ori and not ori_up:
        i_utils.error("No orientation information found for %s. Cannot force re-orient." % pack_info_node, dialog=True)
        return
    
    # Orient base joints (it is a single chain)
    rig_joints.orient_joints(joints=pack_obj.base_joints, orient_as=ori, up_axis=ori_up, freeze=False)

    # Orient chain joints
    chain_joints = pack_obj.base_joints_chains
    if chain_joints:
        for chain in chain_joints:
            rig_joints.orient_joints(joints=chain, orient_as=ori, up_axis=ori_up, freeze=False)

    # Restitch
    pack_obj.stitch_pack(raise_error=False)


def change_pack(pack_info_node=None, updated_dict=None, stitch_update_dict=None, do_mirror=False, dialog_error=False):
    """
    Change class object information on a pack
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    :param updated_dict: (dict) - Object information to update on the pack.
    :param stitch_update_dict: (dict) - Stitch information.
        Accepts: "children_add" / "children_rem" / "parent_type" / "parents_add" / "parents_rem" / "stitchable_pack_obj"
        :note: This should only be used for manual super hacking and not be accessible through Change Pack UI.
        To officially change the stitch - should use Frankenstein UI functionality (uses the Master class)
    :param do_mirror: (bool) - Also change the mirrored pack with updates?
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (obj) - Updated pack object
    """
    # Check
    i_utils.check_arg(pack_info_node, "pack info node", exists=True)
    
    # Var
    current_pack_obj = get_pack_object(pack_info_node=pack_info_node)
    
    # Normal Items
    if updated_dict:
        # Get current
        current_pack_data_str = pack_info_node.build_data.get()
        current_pack_data_eval = pickle.loads(str(current_pack_data_str))
        updated_dict_full = current_pack_obj.__dict__.copy()
        updated_dict_full.update(updated_dict)
        
        # Naming change
        # - Vars
        current_base_name = current_pack_obj.base_name
        updated_base_name = updated_dict.get("base_name")
        if not updated_base_name:
            updated_base_name = updated_dict.get("side", current_pack_obj.side) + "_" + updated_dict.get("description", current_pack_obj.description)
            updated_dict_full["base_name"] = updated_base_name
        # - Rename
        if updated_base_name and current_base_name != updated_base_name:
            updated_dict_full = rename_pack(pack_obj=current_pack_obj, new_base_name=updated_base_name)
            pack_info_node = i_node.Node(pack_info_node.replace(current_base_name, updated_base_name, 1))
        
        # Orientation
        changed_joint_orientation = False
        curr_ori = current_pack_obj.orient_joints
        curr_ori_up = current_pack_obj.orient_joints_up_axis
        if "orient_joints" in updated_dict.keys() or "orient_joints_up_axis" in updated_dict.keys():
            changed_ori = updated_dict.get("orient_joints", curr_ori) != curr_ori
            changed_up = updated_dict.get("orient_joints_up_axis", curr_ori_up) != curr_ori_up
            if changed_ori or changed_up:
                changed_joint_orientation = True
        
        # Store data on node
        updated_data_pickle = pickle.dumps(updated_dict_full)
        i_attr.create(node=pack_info_node, ln="build_data", at="string", dv=str(updated_data_pickle), l=True, use_existing=True)
        
        # Force Re-Orient
        if changed_joint_orientation:
            force_reorient_base_joints(pack_info_node=pack_info_node)
    
    # Stitch Items
    if stitch_update_dict:
        data_as_str = pack_info_node.stitch_data.get()
        stitch_data = pickle.loads(str(data_as_str)).__dict__
        upd_stitch_data = stitch_data.copy()
        
        orig_curr_stitched = pack_info_node.currently_stitched_packs.get()
        curr_stitched = str(orig_curr_stitched)
        if curr_stitched:
            curr_stitched = curr_stitched.split(", ")

        for pin_ls_type in ["parents", "children"]:
            # - Vars
            curr = stitch_data.get(pin_ls_type)
            new = list(curr)
            to_add = stitch_update_dict.get(pin_ls_type + "_add")
            to_rem = stitch_update_dict.get(pin_ls_type + "_rem")
            # - Upd
            if to_add:
                if not isinstance(to_add, (list, tuple)):
                    to_add = [to_add]
                new += to_add
                if pin_ls_type == "parents":
                    curr_stitched += [ta.name for ta in to_add if ta.name not in curr_stitched]
            if to_rem:
                if not isinstance(to_rem, (list, tuple)):
                    to_rem = [to_rem]
                for tr in to_rem:
                    if tr in new:
                        new.remove(tr)
                    if pin_ls_type == "parents":
                        if curr_stitched and str(tr) in curr_stitched:
                            curr_stitched.remove(str(tr))
            # - Store
            upd_stitch_data[pin_ls_type] = new
        
        for etc in ["parent_type", "stitchable_pack_obj"]:
            if etc in stitch_update_dict.keys():  # Needs to accept None or a specified string
                upd_stitch_data[etc] = stitch_update_dict.get(etc)
        
        if stitch_data != upd_stitch_data:
            RIG_F_LOG.info("Updating '%s' stitch data from" % pack_info_node, stitch_data, "to", upd_stitch_data)
            stitch_data_pickle = pickle.dumps(i_utils.Mimic(upd_stitch_data))
            i_attr.create(node=pack_info_node, ln="stitch_data", at="string", dv=str(stitch_data_pickle), l=True, use_existing=True)
            
            if orig_curr_stitched != curr_stitched:
                RIG_F_LOG.info("Updating '%s' 'currently stitched' from" % pack_info_node, orig_curr_stitched, "to", curr_stitched)
                curr_stitched_str = ", ".join(curr_stitched)
                i_attr.create(node=pack_info_node, ln="currently_stitched_packs", at="string", dv=curr_stitched_str, l=True, use_existing=True)
        
        else:
            RIG_F_LOG.warn("Given updated stitch data for '%s' but it matches existing data. Not updating." % pack_info_node)

    # Mirror?
    if not current_pack_obj.is_mirror:
        mirror = get_mirrored_connections(pack_info_node=pack_info_node, dialog_error=False, raise_error=False)
        if mirror:
            driver_pack_obj, mirrored_pack_obj = mirror
            if mirrored_pack_obj and (do_mirror or dialog_error):
                if dialog_error:
                    do_mirror = i_utils.message(title="Found Mirror", message="Also update mirrored pack '%s'?" % mirrored_pack_obj.base_name,
                                                button=["Yes", "No"])
                    if do_mirror == "Yes":
                        do_mirror = True
                if do_mirror:
                    # - Calc mirror reg dict
                    mirror_dict = {}
                    if updated_dict:
                        mirror_dict = updated_dict.copy()
                        mirror_dict["side"] = mirrored_pack_obj.side
                        if "base_name" in updated_dict.keys():
                            mirror_dict["base_name"] = mirrored_pack_obj.side + "_" + updated_dict.get("base_name")[2:]
                        mirror_dict["mirror_driver"] = pack_info_node
                    # - Calc mirror stitch dict
                    mirror_stitch_dict = {}
                    if stitch_update_dict:
                        for k, v in stitch_update_dict.items():
                            if isinstance(v, (i_node.Node, i_node._Node)):
                                if v.get_side() == "L":
                                    new_v = v.get_mirror()
                                else:
                                    new_v = v
                            elif isinstance(v, (list, tuple)):
                                new_v = []
                                for sub_v in v:
                                    if isinstance(sub_v, (i_node.Node, i_node._Node)):
                                        if sub_v.get_side() == "L":
                                            new_v.append(sub_v.get_mirror())
                                        else:
                                            new_v.append(sub_v)
                                    else:
                                        new_v.append(sub_v)
                            else:
                                new_v = v
                            mirror_stitch_dict[k] = new_v
                    # - Do It
                    change_pack(pack_info_node=mirrored_pack_obj.pack_info_node, updated_dict=mirror_dict, 
                                stitch_update_dict=mirror_stitch_dict, dialog_error=dialog_error)
    
    # Return
    new_pack_obj = get_pack_object(pack_info_node=pack_info_node)
    return new_pack_obj


def rename_pack(pack_obj=None, new_base_name=None):
    """
    Rename a pack object
    
    :param pack_obj: (obj) - The pack class instanced object
    :param new_base_name: (str) - New base name (side_description) for the pack
    
    :return: (dict) - Updated pack object info
    """
    # Vars
    current_base_name = pack_obj.base_name
    updated_pack_obj_dict = pack_obj.__dict__.copy()
    orig_pack_info_node = pack_obj.pack_info_node.name  # :note: Need .name to do comparison without the hash rename redefining
    
    # Verbose
    RIG_F_LOG.info("Renaming '%s' to '%s'..." % (current_base_name, new_base_name))
    
    # Name-based items
    updated_pack_obj_dict["base_name"] = new_base_name
    updated_pack_obj_dict["side"] = new_base_name.split("_")[0]
    updated_pack_obj_dict["description"] = "_".join(new_base_name.split("_")[1:])
    
    # Rename
    # created_nodes = pack_obj.created_nodes + pack_obj.pack_extras + pack_obj._get_all_base_joints()
    # created_nodes += [pack_obj.__dict__.get(pack_grp) for pack_grp in pack_obj.__dict__.keys() if
    #                   pack_grp.startswith("pack_") and pack_grp.endswith("_grp")]
    # created_nodes.append(pack_obj.pack_info_node)
    # for node in created_nodes:
    #     node.rename(node.replace(current_base_name, new_base_name, 1))
    
    for k, v in pack_obj.__dict__.items():
        # - Name
        new_v = None
        if isinstance(v, (i_node.Node, i_node._Node)) and v.startswith(current_base_name):
            v.rename(v.replace(current_base_name, new_base_name, 1))
            new_v = i_node.Node(v.name)
        elif isinstance(v, (str, unicode)) and v.startswith(current_base_name):
            new_v = v.replace(current_base_name, new_base_name, 1)
        elif isinstance(v, (list, tuple)):
            new_v = []
            for sub_v in v:
                if isinstance(sub_v, (i_node.Node, i_node._Node)) and sub_v.startswith(current_base_name):
                    sub_v.rename(sub_v.replace(current_base_name, new_base_name, 1))
                    sub_v = i_node.Node(sub_v.name)
                elif isinstance(sub_v, (str, unicode)) and sub_v.startswith(current_base_name):
                    sub_v = sub_v.replace(current_base_name, new_base_name, 1)
                new_v.append(sub_v)
            # v = new_v
        else:
            continue
        # - Update dict
        updated_pack_obj_dict[k] = new_v
    new_pack_info_node = pack_obj.pack_info_node
    
    # Affected stitches?
    stitch_info = pack_obj._get_stitch_data()
    stitch_parents = stitch_info.parents
    stitch_children = stitch_info.children
    affected_stitches = stitch_children + stitch_parents
    orig_stitchable_object = stitch_info.stitchable_pack_obj
    new_stitchable_object = orig_stitchable_object.replace(current_base_name, new_base_name, 1)
    if orig_stitchable_object != new_stitchable_object:
        new_stitch_info = stitch_info.__dict__.copy()
        new_stitch_info["stitchable_pack_obj"] = new_stitchable_object
        new_stitch_pickle = pickle.dumps(i_utils.Mimic(new_stitch_info))
        new_pack_info_node.stitch_data.set(str(new_stitch_pickle))
        # i_attr.create(new_pack_info_node, ln="stitch_data", at="string", dv=str(new_stitch_pickle), l=True, use_existing=True)
    if affected_stitches:
        for stitched_info_node in affected_stitches:
            # - Parents / Children
            stitched_obj = get_pack_object(stitched_info_node)
            stitched_obj_info = stitched_obj._get_stitch_data().__dict__
            new_stitch_info = stitched_obj_info.copy()
            if stitched_obj_info.get("do_parenting_pack") == orig_pack_info_node:
                new_stitch_info["do_parenting_pack"] = new_pack_info_node
            for ls in ["children", "parents"]:
                new_ls = []
                for orig in stitched_obj_info.get(ls):
                    new = orig
                    if orig == orig_pack_info_node:
                        new = new_pack_info_node
                    new_ls.append(new)
                new_stitch_info[ls] = new_ls
            if new_stitch_info != stitched_obj_info:
                new_stitch_pickle = pickle.dumps(i_utils.Mimic(new_stitch_info))
                i_attr.create(stitched_info_node, ln="stitch_data", at="string", dv=str(new_stitch_pickle), l=True, use_existing=True)
            # - Currently stitched
            # -- Temp hack renaming old attr
            curr_stitched_attr = stitched_info_node + ".currently_stitched_packs"
            if not i_utils.check_exists(curr_stitched_attr):
                curr_stitched_attr = stitched_info_node + ".currently_stitched_data"
                if i_utils.check_exists(curr_stitched_attr):
                    i_attr.Attr(curr_stitched_attr).rename("currently_stitched_packs")
            if not i_utils.check_exists(stitched_info_node + ".currently_stitched_packs"):  # Some packs aren't currently stitched to anything and don't have this attr
                continue
            curr_stitched = stitched_info_node.currently_stitched_packs.get().split(", ")
            # - New names
            new_curr_stitched = []
            for orig in curr_stitched:
                new = orig
                if orig == orig_pack_info_node:
                    new = new_pack_info_node.name
                new_curr_stitched.append(new)
            if curr_stitched != new_curr_stitched:
                i_attr.create(stitched_info_node, ln="currently_stitched_packs", at="string", dv=", ".join(new_curr_stitched), l=True, use_existing=True)
                # stitched_info_node.currently_stitched_packs.set(", ".join(new_curr_stitched))
    
    # Return
    return updated_pack_obj_dict


def check_is_pack_object(pack_obj=None, obj_checking=None, default_hierarchy=None):
    """
    Check if an object is related to specified pack
    
    :param pack_obj: (obj) - The pack class instanced object
    :param obj_checking: (iNode) - Object checking if related to :param pack_obj:
    :param default_hierarchy: (list of iNodes) - (optional) List of nodes to ignore as not actually part of the pack.
        This is typically a rigs default hierarchy, which a pack has included in its connections, but is not pack-specific.
        Such as the "Geo_Grp".
    
    :return: (list of iNodes) - [:param obj_checking:] if it is related to the pack, else []
    """
    # Verbose
    RIG_F_LOG.debug("##VARCHECK obj_checking:", obj_checking)
    obj_is_node_or_attr = isinstance(obj_checking, (str, unicode, i_node.Node, i_node._Node, i_attr._Attr, i_attr.Attr))
    
    # Exists?
    if obj_is_node_or_attr and not i_utils.check_exists(obj_checking):
        return []
    
    # Vars
    base_name = pack_obj.base_name
    is_cog = pack_obj.build_type == "Cog"  # Need to ignore the starting with base name to pick up some more generic nodes
    
    # Match by name because some things are out of the pack hiearchy and cannot be found another way if they weren't connected
    name_match = False
    if obj_is_node_or_attr:
        name_match = (obj_checking == base_name or obj_checking.startswith(base_name + "_")) and not obj_checking.endswith("_ExportData")
    
    # Ignore any model items (ex: mesh shapes that would not have namespaces when deformed)
    if isinstance(obj_checking, (str, unicode)) and i_utils.check_exists(obj_checking):
        obj_checking = i_utils.convert_data(obj_checking, to_generic=False)
    if isinstance(obj_checking, (i_node.Node, i_node._Node)):
        if obj_checking.is_referenced() or (obj_checking.is_shape() and obj_checking.relatives(0, p=True).is_referenced()):
            RIG_F_LOG.debug("'%s' is referenced. Not a pack-built node." % obj_checking)
            return []
    
    # Ignore things in default hierarchy
    if isinstance(obj_checking, (i_node.Node, i_node._Node)) and (name_match or is_cog):
        if default_hierarchy and obj_checking in default_hierarchy:
            RIG_F_LOG.debug("'%s' is in the default hierarchy. Not a pack-built node." % obj_checking)
            return []
        if obj_checking.is_mesh():
            obj_shp = obj_checking
            if not obj_checking.is_shape():
                obj_shp = obj_checking.relatives(0, s=True, type="mesh")
            obj_conn = obj_shp.inMesh.connections(s=True, d=False)
            if obj_conn and obj_conn[0].is_referenced():
                RIG_F_LOG.debug("'%s' is a mesh connected to referenced model. Not a pack-built node." % obj_checking)
                return []
        # - Exists and passes
        RIG_F_LOG.debug("'%s' passes all tests. Is considered a pack-built node." % obj_checking)
        return [obj_checking]
    
    # Nope
    RIG_F_LOG.debug("'%s' did not pass all tests. Not a pack-built node." % obj_checking)
    return []


def get_build_nodes_for_pack(pack_obj=None):
    """
    Get all iNode objects related to the pack
    
    :param pack_obj: (obj) - The pack class instanced object
    
    :return: (list of iNodes) - Related pack object nodes
    """
    def __is_pack_obj(obj):
        return check_is_pack_object(pack_obj=pack_obj, obj_checking=obj, default_hierarchy=default_hierarchy)

    # Vars
    objs = []
    base_name = pack_obj.base_name
    default_hierarchy = [] #pack_obj.default_hierarchy
    top_node = rig_nodes.get_top_group(raise_error=False)
    if top_node:
        if not i_utils.check_exists(top_node + ".RigHierarchy"):
            i_utils.error("Rig Hierarchy not stored on '%s'. Cannot get build nodes for pack. Need to hack top node.")
        rig_hierarchy = top_node.RigHierarchy.connections() + [top_node]
        default_hierarchy += rig_hierarchy
    possible_objs = pack_obj.__dict__.values()

    # Check that everything was found
    # :TODO: Figure out a way to get everything in class attrs so these aren't missed. This is a temp hack.
    also_exists = [obj for obj in i_utils.ls("%s*" % base_name) if obj not in possible_objs and not obj.is_shape()] 
    if also_exists:
        RIG_F_LOG.debug("Did not originally catch these nodes: %s." % ", ".join(i_utils.convert_data(also_exists)))
        possible_objs += also_exists

    # Unpack and find
    for v in possible_objs:
        if isinstance(v, (i_node.Node, i_node._Node)):
            objs += __is_pack_obj(v)
        elif isinstance(v, (list, tuple)):
            for sub_v in v:
                objs += __is_pack_obj(sub_v)
        elif isinstance(v, i_control.Control):
            ctrl_dict = v.__dict__
            for ctrl_v in ctrl_dict.values():
                if not ctrl_v:
                    continue
                elif isinstance(ctrl_v, (i_node.Node, i_node._Node)):
                    objs += __is_pack_obj(ctrl_v)
                elif isinstance(ctrl_v, (list, tuple)):
                    for sub_ctrl_v in ctrl_v:
                        objs += __is_pack_obj(sub_ctrl_v)
    
    # Return
    ret_objs = i_utils.convert_data(list(set(objs)), to_generic=False)
    return ret_objs


def get_packs_from_objs(pack_items=None, search=None, dialog_error=False):
    """
    Get pack objects from related build items.
    
    :param pack_items: (list of iNodes) - Nodes to find related pack objects of
    :param search: (dict) - (optional) Filtering of packs. Accepts value of :param search: in get_scene_packs()
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (list of iNodes) - Pack info nodes related to items.
    """
    pack_items = i_utils.check_arg(pack_items, "pack items", exists=True, check_is_type=list)

    pack_infos = []
    if len(pack_items) == 1 and pack_items[0] == "Utility_Grp":
        pack_items = [pack_grp for pack_grp in pack_items[0].relatives(c=True) if pack_grp.endswith("_Grp")]
    for sl in pack_items:
        pack_infos += [conn.node for conn in sl.message.connections(plugs=True) if conn.attr.startswith("build_objects")]
    
    if RIG_F_LOG.level == 10:
        if pack_infos:
            RIG_F_LOG.debug("Searching with filters through info nodes: %s" % pack_infos)
        else:
            RIG_F_LOG.debug("No pack infos found at the start (pre-search filter).")

    if pack_infos and search:
        RIG_F_LOG.debug("Search criteria:", search)
        pack_infos = get_scene_packs(pack_info_nodes=pack_infos, search=search)

    if not pack_infos:
        msg = "Could not find pack information for selected."
        if search:
            msg += "\nMatching search criteria:\n\n%s" % search
        i_utils.error(msg, dialog=dialog_error, raise_err=False)
        return None
    
    # Consolidate while keeping order
    pack_infos = logic_py.consolidate_list_in_order(pack_infos)

    return pack_infos


def get_pack_from_obj_sel(dialog_error=False, search=None):
    """
    Get the pack object from the selected related node
    
    :param search: (dict) - (optional) Filtering of packs. Accepts value of :param search: in get_scene_packs()
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (list of iNodes) - Pack info nodes related to items.
    """
    sel = i_utils.check_sel(raise_error=False, dialog_error=dialog_error)
    if not sel:
        i_utils.error("Select an object that is from a Frankenstein pack.", dialog=dialog_error, raise_err=False)
        return None

    pack_info_nodes = get_packs_from_objs(pack_items=sel, search=search, dialog_error=True)
    
    return pack_info_nodes


def sel_from_pack_obj(sel_item=None):
    """
    Select all objects of a class attr based on any pack object item selection.
    
    :param sel_item: (str) - Class attr getting from pack object to determine nodes to select.
    
    :return: None
    """
    info_nodes = get_pack_from_obj_sel()
    if not info_nodes:
        return
    
    sel_objs = []
    
    for info_node in info_nodes:
        pack_obj = get_pack_object(info_node)
        sel_obj = getattr(pack_obj, sel_item)
        if isinstance(sel_obj, (list, tuple)):
            sel_objs += sel_obj
        else:
            sel_objs.append(sel_obj)
    
    if not sel_objs:
        i_utils.error("Nothing found to select.", dialog=True)
        return
    
    i_utils.select(sel_objs)


def get_stitch_data(pack_obj=None, prompt=False):
    """
    Get stitch information for given :param pack_obj:
    
    :param pack_obj: (obj) - The pack class instanced object
    :param prompt: (bool) - Create a popup with information?
    
    :return: (dict) - Stitch information based on _get_stitch_data() and _get_currently_stitched_data()
    """
    # Get pack
    if not pack_obj:
        info_nodes = get_pack_from_obj_sel()
        if not info_nodes:
            return
        pack_obj = get_pack_object(info_nodes[0])
    
    # Get stitch data
    stitch_data = pack_obj._get_stitch_data().__dict__
    stitch_data["currently_stitched"] = pack_obj._get_currently_stitched_data()
    if not prompt:
        return stitch_data
    
    # Convert dict to prompt message
    stitch_data_str = "Stitch Data for: '%s'" % pack_obj.base_name
    for k, v in stitch_data.items():
        stitch_data_str += "\n-- %s: %s" % (k.replace("_", " ").capitalize(), v)

    # Prompt and verbose
    i_utils.message(stitch_data_str, title="Stitch Data")
    RIG_F_LOG.info(stitch_data_str)
    
    # Return
    return stitch_data


def force_restitch(pack_obj=None):
    """
    Force a pack to re-run stitch on its parent and children relations
    
    :param pack_obj: (obj) - The pack class instanced object
    
    :return: None
    """
    stitch_data = get_stitch_data(pack_obj=pack_obj)
    if not stitch_data:
        return
    
    pack_info_node = pack_obj.pack_info_node
    
    curr_stitched = stitch_data.get("currently_stitched")
    parents = stitch_data.get("parents")
    children = stitch_data.get("children")
    
    parents_unstitched = [par for par in parents if par not in curr_stitched]
    children_unstitched = [ch for ch in children if ch not in curr_stitched]
    
    if not parents_unstitched and not children_unstitched:
        return
    
    if parents_unstitched:
        RIG_F_LOG.info("Stitching '%s' to parents:" % pack_info_node, parents_unstitched)
        for par in parents_unstitched:
            pack_obj.stitch_bit(parent_info_node=par, force_restitch=True)
    
    if children_unstitched:
        RIG_F_LOG.info("Stitching '%s' children:" % pack_info_node, children_unstitched)
        for ch in children_unstitched:
            ch_obj = get_pack_object(ch)
            ch_obj.stitch_bit(parent_info_node=pack_info_node, force_restitch=True)


def force_restitch_sel():
    """Selection wrapper for force_restitch()"""
    pack_info_nodes = get_pack_from_obj_sel(dialog_error=True)
    if not pack_info_nodes:
        return
    
    for pin in pack_info_nodes:
        pack_obj = get_pack_object(pin)
        force_restitch(pack_obj=pack_obj)


def check_acceptable_stitch(pack_obj=None, prompt=False, prompt_error_only=False):
    """
    Check if all parent/children stitches connected are acceptable or if they will error at the bit stage.
    
    :param pack_obj: (obj) - The pack class instanced object
    :param prompt: (bool) - Give a popup with information
    :param prompt_error_only: (bool) - If :param prompt:, then only give prompt if there are errors. Otherwise stay silent.
    
    :return: (bool) - True/False for success
    """
    # Get pack
    if not pack_obj:
        info_nodes = get_pack_from_obj_sel()
        if not info_nodes:
            return
        pack_obj = get_pack_object(info_nodes[0])

    # Get stitch data
    stitch_data = get_stitch_data(pack_obj=pack_obj)
    stitch_parents = stitch_data.get("parents")
    if not stitch_parents:
        if prompt and not prompt_error_only:
            i_utils.message("All stitches accepted for '%s'." % pack_obj.base_name)
        return True
    
    # Check against accepted parent types
    accepted_stitch = pack_obj.accepted_stitch_types
    unaccepted = []
    for par_info_node in stitch_parents:
        par_obj = get_pack_object(par_info_node)
        par_type = par_obj.build_type
        par_name = par_obj.base_name
        if par_type not in accepted_stitch:
            unaccepted.append(par_obj)
    
    if not unaccepted:
        if prompt and not prompt_error_only:
            i_utils.message("All stitches accepted for '%s'." % pack_obj.base_name)
        return True
    
    # Prompt / Verbose
    i_utils.error("Cannot stitch a '%s' ('%s') to a '%s' type. ('%s')\n\nAccepted parent types: %s" % 
                  (unaccepted[0].build_type, unaccepted[0].base_name, pack_obj.build_type, pack_obj.base_name,
                   accepted_stitch), dialog=prompt, raise_err=False)
    
    # Final Return
    return False


def __get_scene_packs_all(dialog_error=True):
    """
    Get all pack info nodes found in the scene
    
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (list of iNodes) - Pack info nodes
    """
    # Vars
    pack_info_nodes = []
    
    # If there's a top node, query connections
    top_node = rig_nodes.get_top_group(raise_error=False)
    if top_node and i_utils.check_exists(top_node + ".info_nodes"):
        pack_info_nodes += top_node.attr("info_nodes").connections()

    # Get all pack groups
    group = "Utility_Grp"
    if not i_utils.check_exists(group):
        i_utils.error("%s does not exist. Are there Frankenstein packs in the scene?" % group, dialog=dialog_error, raise_err=False)
        return
    pack_grps = i_node.Node(group).relatives(c=True)

    # Get info nodes
    for pack_grp in pack_grps:
        if pack_grp in ["Utility_Cns_Grp", "Follow_Grp"]:
            continue
        children = pack_grp.relatives(c=True)
        pack_info_nodes += [child for child in children if child.endswith("_Info")]
    if i_utils.check_exists(i_node.info_node_name) and i_node.Node(i_node.info_node_name) in pack_info_nodes:
        pack_info_nodes.remove(i_node.Node(i_node.info_node_name))
    pack_info_nodes = list(set(pack_info_nodes))

    # Return
    return pack_info_nodes


def get_scene_packs(pack_info_nodes=None, check_sel=False, sel_only=False, search=None, ignore_build_types=None, 
                    dialog_error=False):
    """
    Get in-scene pack info nodes based on criteria
    
    :param pack_info_nodes: (list of iNodes) - (optional) Filter given info nodes. If not defined, finds all in scene.
    :param check_sel: (bool) - If :param pack_info_nodes: not defined, check selection before finding all in scene?
    :param sel_only: (bool) - If :param pack_info_nodes: not defined and nothing selected, stop process?
    :param search: (dict) - (optional) Search criteria to filter {PackClassAttr (str) : DesiredValue (any)}
    :param ignore_build_types: (list of strs) - (optional) Build types to ignore (match pack object's "build_type" attr)
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (list of iNodes) - Pack info nodes
    """
    # Get all pack info nodes (unfiltered)
    if not pack_info_nodes:
        if check_sel:
            dialog = True if (dialog_error and sel_only) else False
            pack_info_nodes = get_pack_from_obj_sel(search=search, dialog_error=dialog)
            if dialog and not pack_info_nodes:
                return
        if not sel_only and not pack_info_nodes:
            pack_info_nodes = __get_scene_packs_all(dialog_error=dialog_error)
        if not pack_info_nodes:
            return

    # Filter
    if search:
        # - Find packs that match criteria
        filtered_pack_info_nodes = []
        for info_node in pack_info_nodes:
            # - Instantiate pack
            pack_obj = get_pack_object(info_node)
            passes = True
            # - Check if ignoring that type
            if ignore_build_types and pack_obj.build_type in ignore_build_types:
                continue
            # - Check for desired values
            for k, v in search.items():
                if not hasattr(pack_obj, k) or getattr(pack_obj, k) != v:
                    passes = False
                    break
            # - Append
            if passes:
                filtered_pack_info_nodes.append(info_node)
        # - Override
        pack_info_nodes = filtered_pack_info_nodes

    # Check
    if not pack_info_nodes:
        i_utils.error("No packs found in scene.", dialog=dialog_error, raise_err=False)

    # Return
    return pack_info_nodes


def create_simple_template(template_type=None):
    """
    Create a template using the basic commands and default values
    
    :param template_type: (str) - Template type to create
    
    :return: None
    """
    # Create template
    tpt_obj = get_template_object(template_type)
    tpt_obj.create()
    
    # Pre-Bits
    tpt_obj.pre_bits()
    
    # Post-Bits
    tpt_obj.post_bits()


def create_pack_joints(pack_obj=None, length=0, calculate=True, use_custom_joints=False):
    """
    Create base joints for a pack
    
    :param pack_obj: (obj) - The pack class instanced object
    :param length: (int) - (optional) Specify the length of the joint chain. If not specified, uses :param pack_obj:'s defaults
    :param calculate: (bool) - Calculate the position of the joints based on pack size? If False uses :param pack_objs:'s defaults
    :param use_custom_joints: (bool, list of iNodes) - Use specified joints and position/name as opposed to creating joints
        If True - uses selection.
    
    :return: (dict) - {JointAliasName (str) : Joint (iNode)}
        The JointAliasName is determined by the :param pack_obj:'s "joint_names" attribute
        For chains, the JointAliasName ends in "_chain" and the Joint is a list of iNodes.
    """
    # Vars
    pack_joints = []
    chain_joints = {}

    # Get pack info need to create joints
    pack_joint_names = pack_obj.joint_names
    side = pack_obj.side
    if length == 0:
        length = pack_obj.length + pack_obj.add_length
    base_joint_positions = pack_obj.base_joint_positions
    base_joints_chain_positions = pack_obj.base_joints_chain_positions
    chain_indexes = pack_obj.chain_indexes
    chain_lengths = pack_obj.chain_lengths
    chain_inc = pack_obj.chain_inc
    side_mult = -1.0 if side == "R" else 1.0
    add_chain = chain_indexes and chain_lengths and chain_inc
    pack_size = pack_obj.pack_size

    # Create joints
    if use_custom_joints:
        if use_custom_joints == True:  # Not given a list of joints
            pack_joints = i_utils.check_sel(length_need=length)
            if not pack_joints:
                return
        else:
            pack_joints = use_custom_joints
        for jnt in pack_joints:
            if jnt.node_type() != "joint":
                i_utils.error("Must select joints. %s is a %s." % (jnt, jnt.node_type()), dialog=True)
                return
    else:
        # - Get position numbers from an incremental pack build
        if isinstance(base_joint_positions[0], (str, unicode)):
            default_x = 0
            if side == "L":
                default_x = 1
            elif side == "R":
                default_x = -1
            inc_info = base_joint_positions[0].split("inc")[1]
            inc_axis = inc_info[0].lower()
            if len(inc_info) == 1:
                inc_mult = default_x
            else:
                inc_mult = float(inc_info[1:])
            inc_mult *= side_mult
            # :note: Default X needs to not be 0 or else mirroring gets weird.
            if inc_axis == "x":
                base_joint_positions = [[i * inc_mult, 0, 0] for i in range(1, length + 1)]
            elif inc_axis == "y":
                base_joint_positions = [[default_x, i * inc_mult, 0] for i in range(length)]
            elif inc_axis == "z":
                base_joint_positions = [[default_x, 0, i * inc_mult] for i in range(length)]
        else:
            base_joint_positions = base_joint_positions[:length]
        # - Build the joint
        for j, pos in enumerate(base_joint_positions):
            if calculate:
                scaled_pos = [(float(pos[i]) * pack_size) for i in range(len(pos))]
            else:
                scaled_pos = pos
            base_jnt = i_node.create("joint", n="pack_joint%s" % str(j).zfill(2), position=scaled_pos)
            pack_joints.append(base_jnt)
            # - Chain Joint
            if add_chain and j in chain_indexes:
                ch_pos = None
                ch_jnts = []
                for k in range(chain_lengths[j]):
                    if calculate:
                        if not ch_pos:
                            ch_pos = [(float(pos[i]) + float(chain_inc[i])) * pack_size for i in range(len(pos))]
                        else:
                            ch_pos[0] += (float(chain_inc[0]) * pack_size)
                            ch_pos[1] += (float(chain_inc[1]) * pack_size)
                            ch_pos[2] += (float(chain_inc[2]) * pack_size)
                    else:
                        ch_pos = base_joints_chain_positions[j][k]
                    chn_jnt = i_node.create("joint", n="pack_joint%s_chain%s" % (str(j).zfill(2), str(k).zfill(2)), position=ch_pos)
                    ch_jnts.append(chn_jnt)
                i_utils.select(cl=True)  # To set next chain to world parent
                if not isinstance(ch_jnts, (list, tuple)):
                    ch_jnts = [ch_jnts]
                chain_joints[base_jnt] = ch_jnts
            # - If it's not a chain, it's still a root joint so shouldn't get next joint parented under it
            elif add_chain:
                i_utils.select(cl=True)
        i_utils.select(cl=True)
    
    # Store in returned dictionary with associated joint name
    # - Increment names if only given one
    if len(pack_joint_names) == 1 and len(pack_joints) > 1:  # Use one name and increment numbers (ex: FkChain, Spine)
        pack_joint_names = [pack_joint_names[0] + str(i + 1).zfill(2) for i in range(len(pack_joints) + 1)]
    # - Base Joints
    create_joints = collections.OrderedDict()
    for i, pack_jnt in enumerate(pack_joints):
        # - Base Joint
        create_joints[pack_joint_names[i]] = pack_jnt
        # - Chain Joints
        i_chain_joints = chain_joints.get(pack_jnt)
        if i_chain_joints:
            create_joints[pack_joint_names[i] + "_chain"] = i_chain_joints

    # Return
    return create_joints


def mirror_pack(pack_info_node=None, symmetry=True, do_stitch=True, dialog_error=False):
    """
    Create a Mirrored pack
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    :param symmetry: (bool) - Connect driver to mirrored pack so pack objects are driven symmetrically?
    :param do_stitch: (bool) - Include the stitch information from the driving pack on the mirrored?
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (iNode) - Pack info node of the created mirror pack
    """
    # Do we need to stitch?
    stitch = True if (do_stitch and i_utils.check_exists(pack_info_node + ".stitch_parent")) else False
    RIG_F_LOG.debug("Mirroring %s. Symmetrically - %s. Stitching - %s." % (pack_info_node, symmetry, stitch))

    # Get Pack
    pack_obj = get_pack_object(pack_info_node)
    driver_base_joints = pack_obj.base_joints
    if pack_obj.top_base_joint:  # :note: Would need to have all base joint children under it already (ex: hand)
        top_joints = [pack_obj.top_base_joint]
    elif hasattr(pack_obj, "base_joints_roots") and getattr(pack_obj, "base_joints_roots"):  # Backwards compatibility when not all packs had this attr
        top_joints = pack_obj.base_joints_roots
    else:
        top_joints = [driver_base_joints[0]]

    # Unstitch the driver pack
    if stitch:
        pack_obj.unstitch_pack(raise_error=False)

    # Get mirror info
    driver_side = pack_obj.side
    description = pack_obj.description
    mirror_side = i_node.mirror_side_match.get(driver_side)
    # - Check: Does this mirror name already exist
    existing_packs = get_scene_packs(dialog_error=False)
    if existing_packs:
        existing_pack_names = [pack.name for pack in existing_packs]
        mirror_info_name = mirror_side + "_" + description
        if mirror_info_name + "_Info" in existing_pack_names:
            i_utils.error("Pack with the name '%s' already exists." % mirror_info_name, dialog=dialog_error, raise_err=False)
            return

    # Mirror joints
    i_utils.select(cl=True)  # For maya's mirrorJoint()
    mirrored_joints = []
    for top_joint in top_joints:
        mirrored_things = top_joint.mirror(sr=[driver_side + "_", mirror_side + "_"], mb=True, myz=True)
        # - Break down and check mirrored
        mirrored_joints += [mj for mj in mirrored_things if mj.node_type() == "joint"]
        mirrored_top_joint = top_joint.replace(driver_side + "_", mirror_side + "_", 1)
        if mirrored_top_joint not in mirrored_joints:
            i_utils.error("%s was not created on mirroring. Unsure what to do now." % mirrored_top_joint)
        # - Parent
        i_node.Node(mirrored_top_joint).set_parent(w=True)
    
    # Delete mirrored constraints
    mirrored_constraints = []
    for cns_typ in i_constraint.get_types():
        for mirr_jnt in mirrored_joints:
            mirrored_constraints += mirr_jnt.relatives(ad=True, type=cns_typ)
    if mirrored_constraints:
        i_utils.delete(mirrored_constraints)
    
    # Create prep joints dictionary for mirrored side
    mirrored_pack_joints = collections.OrderedDict()
    # :note: Use pack joints instead of base joints to take care of chain joint children
    for joint_name, driver_joint in pack_obj.pack_joints.items():
        if not isinstance(driver_joint, (list, tuple)):  # Chains are a list
            driver_joint = [driver_joint]
        mirrored_pack_joint = []
        for dvr_jnt in driver_joint:
            mirr_jnt = dvr_jnt.get_mirror(check_exists=True, raise_error=True)
            mirrored_pack_joint.append(mirr_jnt)
        if not joint_name.endswith("_chain") and len(mirrored_pack_joint) == 1:  # Chains need to stay lists
            mirrored_pack_joint = mirrored_pack_joint[0]
        mirrored_pack_joints[joint_name] = mirrored_pack_joint

    # Instantiate Build Class
    rig_pack_mod = importlib.import_module(pack_obj.imp_module)
    rig_pack_class = getattr(rig_pack_mod, pack_obj.imp_class)
    mirrored_pack_obj = rig_pack_class()
    for k, v in pack_obj.__dict__.items():
        if isinstance(v, (i_node.Node, i_node._Node)) or (v and isinstance(v, (list, tuple)) and isinstance(v[0], (i_node.Node, i_node._Node))):
            continue
        setattr(mirrored_pack_obj, k, v)
    mirrored_pack_obj.side = mirror_side
    mirrored_pack_obj.do_orient_joints = False
    mirrored_pack_obj.is_mirror = True
    mirrored_pack_obj.mirror_driver = pack_info_node
    mirrored_pack_obj.pack_joints = mirrored_pack_joints
    mirrored_pack_obj.pack_extras = []
    mirrored_pack_obj.pack_extras_positions = {}

    # Create Mirror Pack
    mirrored_pack_obj.create_pack()
    mirror_pack_info_node = mirrored_pack_obj.pack_info_node

    # Clear selection
    i_utils.select(cl=True)

    # Connect as mirrored
    i_node.connect_to_info_node(info_attribute="pack_mirror", objects=mirror_pack_info_node, node=pack_info_node)

    # Symmetry
    if symmetry:
        mirrored_pack_obj = mirror_symmetry_attach(pack_info_node=pack_info_node)

    # Optionally do any additional things the pack has set up when mirroring
    mirrored_pack_obj.mirror_pack(driver_info_node=pack_info_node, mirrored_info_node=mirror_pack_info_node, symmetry=symmetry)

    # If there's a defined stitch, re-stitch (includes mirroring the stitch)
    if stitch:
        pack_obj.stitch_pack(raise_error=False)

    # Return
    return mirror_pack_info_node


def mirror_packs_sel(create=True, symmetry=True):
    """
    Selection wrapper for mirror_pack() / delete_mirror()
    
    :param create: (bool) True: Create / False: Delete
    :param symmetry: (bool) If :param create: create the mirror packs with symmetry?
    
    :return: (bool) - True/False for success
    """
    # Watson style?
    info_node = i_node.info_node_name
    is_watson = False
    sel = i_utils.check_sel(raise_error=False)
    if not sel:
        if i_utils.check_exists(info_node + ".G_Packs"):
            is_watson = True
    elif sel and [bp for bp in i_utils.ls(sel[0], l=True)[0].split("|") if bp.endswith("_BuildPack")]:
        is_watson = True
    if is_watson:
        if not create:
            i_utils.error("Legacy packs do not have delete mirror ability.", dialog=True, raise_err=False)
            return
        rig_misc.legacy_load_g_rigging()
        import Watson
        Watson.TemplateMirror()
        i_utils.select(cl=True)
        return

    # Franken style?
    driving_packs = get_scene_packs(dialog_error=False, check_sel=True, search={"bit_built" : False})
    if not driving_packs:
        i_utils.error("Found no Frankenstein packs to drive mirroring.\n\nIf mirroring Watson, select the '*_BuildPack'", dialog=True)
        return
    
    # Multi-filter accept sides mirrorable
    mirrorable_sides = i_node.mirror_side_match.keys()
    mirrorable_packs = []
    for pack_info_node in driving_packs:
        pack_obj = get_pack_object(pack_info_node)
        if pack_obj.side not in mirrorable_sides:
            continue
        mirrorable_packs.append(pack_info_node)
    
    if not mirrorable_packs:
        i_utils.error("Found no packs with mirrorable sides.\n\nMirrorable sides: %s" % ", ".join(mirrorable_sides), dialog=True)
        return

    if create:
        for pack in mirrorable_packs:
            mirror_pack(pack_info_node=pack, symmetry=symmetry, dialog_error=True)

    else:  # Delete
        for pack in mirrorable_packs:
            delete_mirror(pack_info_node=pack)

    # Success
    return True


def get_mirrored_connections(pack_info_node=None, dialog_error=False, raise_error=False):
    """
    Get the driver and mirror pack object pair
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info) of either the mirror or driver
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (list of objs) [DriverPackObj (obj), MirroredPackObj (obj)]
    """
    # Vars
    pack_obj = get_pack_object(pack_info_node, raise_error=raise_error)
    driver_pack_obj = None
    mirrored_pack_obj = None
    
    # Pack given is mirrored
    if pack_obj.is_mirror:
        mirrored_pack_obj = pack_obj
        driver_pack_info_node = mirrored_pack_obj.mirror_driver
        driver_pack_obj = get_pack_object(driver_pack_info_node, raise_error=raise_error)

    # Pack given is driver
    else:
        driver_pack_obj = pack_obj
        if i_utils.check_exists(pack_info_node + ".pack_mirror"):
            mirrored_pack_info_node = pack_info_node.pack_mirror.connections()
            if mirrored_pack_info_node:
                mirrored_pack_obj = get_pack_object(mirrored_pack_info_node[0], raise_error=raise_error)
    
    # Check
    if not driver_pack_obj or not mirrored_pack_obj:
        i_utils.error("Cannot determine mirroring relationship for '%s'." % pack_info_node, dialog=dialog_error, raise_err=raise_error)
        return

    # Return
    return [driver_pack_obj, mirrored_pack_obj]


def get_mirror_sym_nodes(mirror_obj=None):
    """
    Get mirror symmetry nodes
    
    :param mirror_obj: (iNode) - The mirror pack's pack class instanced object
    
    :return: (dict) - {"t" : TranslateDriverNodes (list of iNodes), "r" : RotateDriverNodes (list of iNodes)}
    """
    mirror_sym_nodes = {"t": [], "r": []}
    if i_utils.check_exists(mirror_obj.pack_info_node + ".mirror_sym_nodes"):
        mirror_sym_nodes = pickle.loads(str(mirror_obj.pack_info_node.mirror_sym_nodes.get()))

    existing_mirror_sym_nodes = {"t": [], "r": []}
    for typ, nodes in mirror_sym_nodes.items():
        existing_mirror_sym_nodes[typ] = [nd for nd in nodes if nd.exists()]

    # Force getting unit conversion nodes that Maya makes
    existing_rotate = existing_mirror_sym_nodes.get("r")
    if existing_rotate:
        uc_nodes = []
        for r_md in existing_rotate:
            for ax in ["X", "Y", "Z"]:
                uc_nodes += r_md.attr("output" + ax).connections(s=False, d=True, scn=False, type="unitConversion")
        existing_mirror_sym_nodes["r"] += uc_nodes

    return existing_mirror_sym_nodes


def mirror_symmetry_attach(pack_info_node=None, dialog_error=False):
    """
    Attach symmetry to a mirror pack
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (obj) - Mirrored Pack Object
    """
    # Check if pack is driver/mirrored or has no mirroring
    mirrored_conns = get_mirrored_connections(pack_info_node, dialog_error=dialog_error)
    if not mirrored_conns:
        RIG_F_LOG.warn("No mirrored connections found for '%s'. Cannot attach symmetry." % pack_info_node)
        return
    driver_obj, mirror_obj = mirrored_conns[0], mirrored_conns[1]
    driver_pack_info_node = driver_obj.pack_info_node
    mirror_pack_info_node = mirror_obj.pack_info_node

    # Are they already mirrored symmetrically?
    if mirror_obj.is_mirror_sym:
        i_utils.error("'%s' is already driving '%s' symmetrically." % (driver_pack_info_node, mirror_pack_info_node), dialog=dialog_error)
        return

    # Driver / Mirror Vars
    driving_joints = driver_obj._get_all_base_joints()
    driving_top_joints = driver_obj.top_base_joint or driver_obj.base_joints_roots or driving_joints[0]
    if not isinstance(driving_top_joints, (list, tuple)):
        driving_top_joints = [driving_top_joints]
    mirror_joints = mirror_obj._get_all_base_joints()
    # mirror_top_joint = mirror_obj.top_base_joint or mirror_joints[0]
    mirror_base_name = mirror_obj.base_name

    # Get mirror sym nodes
    mirror_sym_nodes = get_mirror_sym_nodes(mirror_obj)

    # Attach each joint
    for i, driving_jnt in enumerate(driving_joints):
        # - Vars
        mirror_jnt = mirror_joints[i]
        mirror_name = mirror_base_name + "_" + "".join(mirror_jnt[2:].split("_")[1:])
        if mirror_name.endswith("_"):
            mirror_name = mirror_name[:-1]
        # - Verbose
        RIG_F_LOG.debug("Attaching Mirror Symmetry", driving_jnt, ">", mirror_jnt)
        # - Symmetry T/R
        for typ in ["t", "r"]:
            created_sym_mult = False
            sym_nd = mirror_sym_nodes.get(typ)
            if sym_nd and len(sym_nd) > i:
                sym_nd = sym_nd[i]
            else:
                sym_nd = i_node.create("multiplyDivide", n="%s_%s_Mirror_Symmetry_Md" % (mirror_name, typ.upper()), use_existing=True)
                mirror_sym_nodes[typ].append(sym_nd)
                created_sym_mult = True
            if typ == "t":
                sym_nd.input2X.set(-1)
                if driving_jnt not in driving_top_joints:
                    sym_nd.input2Y.set(-1)
                    sym_nd.input2Z.set(-1)
            if not created_sym_mult:
                continue
            if typ in ["t", "r"]:
                for ax in ["x", "y", "z"]:
                    driving_jnt.attr(typ + ax).drive(sym_nd.attr("input1%s" % ax.upper()))
                    sym_nd.attr("output%s" % ax.upper()).drive(mirror_jnt + "." + typ + ax, raise_error=False)
        # - Direct Connect Attrs
        dir_conn_attrs = ["radius"]
        for dc_attr in dir_conn_attrs:
            driving_jnt.attr(dc_attr).drive(mirror_jnt + "." + dc_attr, raise_error=False)
        # - Template
        for o_attr in ["overrideEnabled", "overrideDisplayType"]:
            mirror_jnt.attr(o_attr).set(1)
    
    # Store sym nodes
    i_attr.create(node=mirror_obj.pack_info_node, ln="mirror_sym_nodes", at="string", l=True, use_existing=True,
                  dv=str(pickle.dumps(mirror_sym_nodes)))

    # Set as symmetrically mirrored
    mirror_obj.is_mirror_sym = True
    mirror_obj._store_build_data()

    # Return
    return mirror_obj


def mirror_symmetry_detach(pack_info_node=None, dialog_error=False, clear_data=False):
    """
    Detach symmetry for mirrored pack
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param clear_data: 
    
    :return: 
    """
    # Check if pack is driver/mirrored or has no mirroring
    mirrored_conns = get_mirrored_connections(pack_info_node, dialog_error=dialog_error, raise_error=False)
    if not mirrored_conns:
        RIG_F_LOG.debug("No symmetry connections to detach for %s." % pack_info_node)
        return
    driver_obj, mirror_obj = mirrored_conns[0], mirrored_conns[1]
    driver_pack_info_node = driver_obj.pack_info_node
    mirror_pack_info_node = mirror_obj.pack_info_node

    # Get mirror sym nodes
    mirror_sym_nodes = get_mirror_sym_nodes(mirror_obj)

    # Are they mirrored symmetrically?
    if not mirror_sym_nodes:
        i_utils.error("'%s' is not driving '%s' symmetrically." % (driver_pack_info_node, mirror_pack_info_node), dialog=dialog_error)
        return

    # Driver / Mirror Vars
    driving_joints = driver_obj._get_all_base_joints()
    mirror_joints = mirror_obj._get_all_base_joints()
    mirror_joints_exist = True
    for mirror_jnt in mirror_joints:
        if not mirror_jnt.exists():
            mirror_joints_exist = False
            break
    if not mirror_joints_exist:
        i_utils.error("Mirror joints for '%s' do not exist. Pack may have been deleted. Cannot detach." % pack_info_node,
                      dialog=dialog_error, raise_err=False)
        return

    # Are any driven joints locked?
    mirror_lh = {}
    for jnt in mirror_joints:
        attrs = [atr for atr in ["t", "tx", "ty", "tz", "r", "rx", "ry", "rz", "s", "sx", "sy", "sz"] if jnt.attr(atr).get(l=True)]
        if attrs:
            mirror_lh[jnt] = attrs
    if mirror_lh:
        for nd, attrs in mirror_lh.items():
            i_attr.lock_and_hide(node=nd, attrs=attrs, unlock=True)

    # Disconnect / Delete Math Nodes
    for typ, nodes in mirror_sym_nodes.items():
        for math_nd in nodes:
            nt = math_nd.node_type()
            for ax in ["x", "y", "z"]:
                if nt == "multiplyDivide":
                    math_attr = math_nd.attr("output%s" % ax.upper())
                elif nt == "unitConversion":  # "r" uses conversion nodes
                    math_attr = math_nd.output
                else:
                    RIG_F_LOG.warn("Don't know how to disconnect symmetry for node type: '%s' ('%s')" % (nt, math_nd))
                    continue
                math_attr.disconnect()
            math_nd.delete()

    # Detach each Joint
    for i, driving_jnt in enumerate(driving_joints):
        # - Vars
        mirror_jnt = mirror_joints[i]
        RIG_F_LOG.debug("Detaching Mirror Symmetry", driving_jnt, ">", mirror_jnt)
        # - Disconnect direct connects
        i_node.disconnect_nodes_by_attributes(driver=driving_jnt, driven=mirror_jnt, delete_from_driver=False)
        # - Set drawing
        mirror_jnt.overrideDisplayType.set(0)  # Normal
        # mirror_jnt.overrideEnabled.set(0)  # This is then making it inherit parent, which could still be templated if stitched
    
    # Re-lock Joints
    if mirror_lh:
        for nd, attrs in mirror_lh.items():
            if not attrs:
                continue
            i_attr.lock_and_hide(node=nd, attrs=attrs, lock=True)

    # Set as not symmetrically mirrored
    if clear_data:  # As opposed to detaching to build bits, this is when we want it to stop ever being mirrored symmetrically
        mirror_obj.is_mirror_sym = False
        mirror_obj._store_build_data()
        if i_utils.check_exists(mirror_obj.pack_info_node + ".mirror_sym_nodes"):
            i_attr.Attr(mirror_obj.pack_info_node + ".mirror_sym_nodes").delete()

    # Return
    return mirror_obj


def delete_pack(pack_info_node=None, prompt=False):
    """
    Delete a pack from the scene
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info)
    :param prompt: (bool) - Confirm deletion is complete with a popup?
    
    :return: None
    """
    # Check
    if not i_utils.check_exists(pack_info_node, raise_error=False):
        RIG_F_LOG.warn("'%s' already does not exist." % pack_info_node)
        return 
    pack_info_node = i_utils.convert_data(pack_info_node, to_generic=False)

    # Vars
    pack_obj = get_pack_object(pack_info_node)
    message_name = "'%s'" % pack_obj.base_name

    # Find all created things
    pack_exclusive_objs = get_build_nodes_for_pack(pack_obj)
    
    # Unstitch
    pack_obj.unstitch_pack(clear_data=True, raise_error=False)

    # Get mirrored pack
    mirrored = get_mirrored_connections(pack_info_node=pack_info_node, dialog_error=False, raise_error=False)
    if mirrored:
        mirror_obj = mirrored[1]
        mirror_symmetry_detach(pack_info_node=pack_info_node, dialog_error=False)
        pack_exclusive_objs += get_build_nodes_for_pack(mirror_obj)
        message_name += " and '%s'" % mirror_obj.base_name

    # Verbose
    RIG_F_LOG.info("Deleting '%s'" % message_name)

    # Disconnect math nodes within the pack then reset the values (so don't get "divide by 0" errors)
    # :note: Can't actually avoid that 0 error because disconnecting in maya automatically sets it to 0...
    curr_vals = {}
    for obj in pack_exclusive_objs:
        if not obj.exists():
            continue
        if obj.node_type() not in ["multiplyDivide"]:
            continue
        for attr_name in obj.attrs():
            if attr_name in ["message"]:
                continue
            nd_attr = obj.attr(attr_name)
            if nd_attr.connections(s=True, d=False):
                curr_vals[nd_attr] = nd_attr.get()
            driven_conns = nd_attr.connections(s=False, d=True, plugs=True)
            if driven_conns:
                outer_pack_driven = [driven_attr for driven_attr in driven_conns if driven_attr.node not in pack_exclusive_objs]
                if outer_pack_driven:
                    for driven_nd_attr_name in outer_pack_driven:
                        driven_nd_attr = i_attr.Attr(driven_nd_attr_name)
                        curr_vals[driven_nd_attr] = driven_nd_attr.get()
    for obj in curr_vals.keys():
        obj.disconnect()
    for nd_attr, val in curr_vals.items():
        nd_attr.set(val)

    # Delete pack nodes
    # :note: Delete one by one for instances where deleted a hierarchy object and child no longer exists
    for obj in pack_exclusive_objs:
        # - Still exists?
        if not i_utils.check_exists(obj):
            continue
        # - Delete
        i_utils.delete(obj)

    # Message
    if prompt:
        i_utils.message("Deleted %s." % message_name)


def delete_mirror(pack_info_node=None, dialog_error=False):
    """
    Delete a mirrored pack
    
    :param pack_info_node: (iNode) - Pack's Info Node (ex: L_Leg_Info). Either the driver or mirrored's.
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: None
    """
    # Find Mirrored
    mirrored_conns = get_mirrored_connections(pack_info_node, dialog_error=dialog_error, raise_error=False)
    if not mirrored_conns:
        return
    driver_obj, mirror_obj = mirrored_conns[0], mirrored_conns[1]
    driver_pack_info_node = driver_obj.pack_info_node
    mirror_pack_info_node = mirror_obj.pack_info_node
    
    # Delete
    delete_pack(mirror_pack_info_node)

    # Remove attribute
    driver_pack_info_node.pack_mirror.delete()


def legacy_get_packs_and_bits():
    """
    Get legacy built pack and bit in-scene information
    :return: (list) - [LegacyPackAttr (str), LegacyPacks (list of strs), LegacyBitsAttr (str), LegacyBits (list of strs)]
    """
    # Vars
    info_node = i_node.info_node_name
    g_pack_attr, g_packs, g_bits_attr, g_bits = [None, None, None, None]

    # Found any?
    if i_utils.check_exists(info_node + ".G_Packs"):
        g_pack_attr = i_attr.create(node=info_node, ln="G_Packs", dt="string", use_existing=True)
        g_packs = g_pack_attr.get()
        if "None" in g_packs:  # Temp backwards compatibility
            if g_packs == "None":
                g_packs = []
            else:
                g_packs = [pk for pk in g_packs.replace(" ", "").split(",") if pk != "None"]
        g_bits_attr = i_attr.create(node=info_node, ln="G_Bits", dt="string", use_existing=True)
        g_bits = g_bits_attr.get()
        if "None" in g_bits:  # Temp backwards compatibility
            if g_bits == "None":
                g_bits = []
            else:
                g_bits = [bt for bt in g_bits.replace(" ", "").split(",") if bt != "None"]

    return [g_pack_attr, g_packs, g_bits_attr, g_bits]


def eav_position_packs():
    """
    Position packs for Elena (EAV) for the small bipeds show.
    :return: None
    """
    # Spine
    cmds.xform("Spine_01", t=[0.0, 6.876, 0.0], ws=True)
    cmds.xform("Spine_02", t=[0.0, 8.514, 0.408], ws=True)
    cmds.xform("Spine_03", t=[0.0, 10.152, 0.63], ws=True)
    cmds.xform("Spine_04", t=[0.0, 11.789, -0.056], ws=True)

    # Neck
    cmds.xform("Neck_01", t=[0.0, 12.548, -0.056], ws=True)
    pm.setAttr("Neck_01.r", [5.129, 0.0, 0.0])
    
    cmds.xform("Neck_02", t=[0.0, 13.436, 0.024], ws=True)
    cmds.xform("Neck_03", t=[0.0, 14.324, 0.104], ws=True)

    # Head
    cmds.xform("Head", t=[0.0, 14.425, 0.127], ws=True)
    cmds.xform("Head_Wire", t=[0.0, 14.746, 0.263], ws=True)
    cmds.xform("Head_Volume", t=[0.0, 14.746, 0.263], ws=True)
    pm.setAttr("Head_Wire.s", [0.619, 0.631, 0.631])
    pm.setAttr("Head_Volume.s", [0.619, 0.631, 0.631])

    # Clavicle
    cmds.xform("L_Clav", t=[0.433, 11.789, -0.056], ws=True)
    pm.setAttr("L_Clav.r", [-9.95, 0.0, -11.801])
    
    cmds.xform("L_ClavTip", t=[2.465, 11.365, -0.42], ws=True)

    # Hip
    cmds.xform("L_Hip", t=[0.366, 6.947, -0.0], ws=True)
    pm.setAttr("L_Hip.r", [0.0, 180.0, -11.306])
    
    cmds.xform("L_HipTip", t=[1.125, 6.796, -0.0], ws=True)

    # Arm
    cmds.xform("L_UprArm", t=[2.962, 11.175, -0.519], ws=True)
    pm.setAttr("L_UprArm.rz", -44.511)
    
    cmds.xform("L_LwrArm", t=[4.259, 9.9, -0.519], ws=True)
    cmds.xform("L_Wrist", t=[5.911, 8.276, -0.519], ws=True)
    cmds.xform("L_WristEnd", t=[7.667, 6.549, -0.519], ws=True)

    # Leg
    cmds.xform("L_UprLeg", t=[1.381, 6.746, 0.0], ws=True)
    pm.setAttr("L_UprLeg.r", [-5.633, 0.0, 0.0])
    
    cmds.xform("L_LwrLeg", t=[1.381, 3.721, 0.298], ws=True)
    pm.setAttr("L_LwrLeg.rx", 19.558)
    
    cmds.xform("L_Foot", t=[1.381, 1.192, -0.329], ws=True)
    pm.setAttr("L_Foot.rx", -14.881)
    
    cmds.xform("L_FootEnd", t=[1.381, 0.004, -0.309], ws=True)

    # Hand
    # - Extras 1
    cmds.xform("L_Palm", t=[5.911, 8.276, -0.519], ws=True)
    pm.setAttr("L_Palm.r", [-134.401, -90.0, 0.0])
    
    cmds.xform("L_OutterCup", t=[6.132, 8.059, -0.701], ws=True)
    pm.setAttr("L_OutterCup.r", [0.0, 180.0, 180.0])
    
    # - Ring
    cmds.xform("L_Ring_01", t=[6.799, 7.625, -0.768], ws=True)
    pm.setAttr("L_Ring_01.r", [1.767, 0.016, -13.53])
    
    cmds.xform("L_Ring_02", t=[7.143, 7.266, -0.888], ws=True)
    cmds.xform("L_Ring_03", t=[7.357, 7.042, -0.962], ws=True)
    pm.setAttr("L_Ring_03.r", [1.646, 0.0, 0.0])
    
    cmds.xform("L_RingEnd", t=[7.575, 6.8, -1.041], ws=True)
    # - Pinky
    cmds.xform("L_Pinky_01", t=[6.689, 7.648, -1.016], ws=True)
    pm.setAttr("L_Pinky_01.r", [2.795, 0.0, -22.563])
    
    cmds.xform("L_Pinky_02", t=[6.969, 7.343, -1.188], ws=True)
    pm.setAttr("L_Pinky_02.r", [3.505, 0.0, 0.0])
    
    cmds.xform("L_Pinky_03", t=[7.116, 7.161, -1.284], ws=True)
    cmds.xform("L_PinkyEnd", t=[7.297, 6.935, -1.404], ws=True)
    # - Extras 2
    cmds.xform("L_InnerCup", t=[6.197, 8.098, -0.31], ws=True)
    pm.setAttr("L_InnerCup.r", [0.0, 180.0, 0.0])
    
    # - Thumb
    cmds.xform("L_Thumb_01", t=[6.181, 7.814, -0.108], ws=True)
    pm.setAttr("L_Thumb_01.r", [-1.082, 54.11, 47.547])
    
    cmds.xform("L_Thumb_02", t=[6.36, 7.644, 0.17], ws=True)
    cmds.xform("L_Thumb_03", t=[6.537, 7.477, 0.443], ws=True)
    cmds.xform("L_ThumbEnd", t=[6.72, 7.303, 0.729], ws=True)
    # - Index
    cmds.xform("L_Index_01", t=[6.782, 7.569, -0.131], ws=True)
    pm.setAttr("L_Index_01.r", [-2.301, 0.0, 11.617])
    
    cmds.xform("L_Index_02", t=[7.125, 7.26, -0.036], ws=True)
    cmds.xform("L_Index_03", t=[7.36, 7.047, 0.029], ws=True)
    cmds.xform("L_IndexEnd", t=[7.565, 6.862, 0.086], ws=True)
    # - Middle
    cmds.xform("L_Middle_01", t=[6.868, 7.649, -0.466], ws=True)
    pm.setAttr("L_Middle_01.r", [1.371, -0.0, -2.232])
    
    cmds.xform("L_Middle_02", t=[7.255, 7.251, -0.488], ws=True)
    cmds.xform("L_Middle_03", t=[7.503, 6.998, -0.501], ws=True)
    cmds.xform("L_MiddleEnd", t=[7.726, 6.769, -0.514], ws=True)

    # Foot
    cmds.xform("L_Ankle", t=[1.381, 1.192, -0.329], ws=True)
    pm.setAttr("L_Ankle.r", [129.3, 0.0, 0.0])
    
    cmds.xform("L_Ball", t=[1.381, 0.229, 0.848], ws=True)
    pm.setAttr("L_Ball.r", [-38.237, 0.0, 0.0])
    
    cmds.xform("L_BallEnd", t=[1.381, 0.21, 1.879], ws=True)
    cmds.xform("L_Heel_PivotPlace", t=[1.409, -0.001, -0.634], ws=True)
    cmds.xform("L_Toe_PivotPlace", t=[1.438, 0.0, 1.615], ws=True)
    cmds.xform("L_In_PivotPlace", t=[0.955, -0.005, 1.243], ws=True)
    cmds.xform("L_Out_PivotPlace", t=[1.878, 0.013, 1.174], ws=True)
    cmds.xform("R_Heel_PivotPlace", t=[-1.409, -0.001, -0.634], ws=True)
    cmds.xform("R_Toe_PivotPlace", t=[-1.438, 0.0, 1.615], ws=True)
    cmds.xform("R_In_PivotPlace", t=[-0.955, -0.005, 1.243], ws=True)
    cmds.xform("R_Out_PivotPlace", t=[-1.878, 0.013, 1.174], ws=True)

    # Eye
    cmds.xform("L_Eye", t=[0.305, 14.957, 0.779], ws=True)
    cmds.delete("R_Eye")


def legacy_build_pack(pack=None):
    """
    Build a legacy pack and include some functionality that lets Frankenstein and Pipeline tools recognize builds
    
    :param pack: (str) - Based on the commands labels in the UI that use this function
    
    :return: None
    """
    # Building one pack or a multi
    single_pack = True
    if pack in ["W: KNG Biped", "W: SMO Biped"] or pack.startswith("GB2: "):
        single_pack = False

    # Get build command
    # :note: Do this so can use a try/except easier because legacy g code is not maintained and sometimes errors
    build_cmd = {"W: Simple Spine" : "Watson.TemplateSimpleSpine()",
                 "W: Simple Neck" : "Watson.TemplateSimpleNeck()",
                 "W: Simple Head": "Watson.TemplateSimpleHead()",
                 "W: Simple Hand": "Watson.TemplateSimpleHand()",
                 "W: Clav": "Watson.TemplateClav()",
                 "W: Arm": "Watson.TemplateArm()",
                 "W: Leg": "Watson.TemplateLeg()",
                 "W: Foot": "Watson.TemplateFoot()",
                 "W: Eye": "Watson.TemplateEye()",
                 "W: Wheel": "import Wheels;Wheels.WatsonWheelTemplate()",
                 "W: IK FK Spine": "Watson.TemplateIkFkSpineChain()",
                 "W: Python": "Watson.PythonTemplate()",
                 "W: Cable": "import Cable;Cable.Cable()",
                 "W: Dynamic Chain": "Watson.TemplateDynamicChain()",
                 "W: Ribbon": "rig_frankenstein_utils.legacy_ribbon()",
                 "H: Squash": "import WillsRigScrips as wrs;wrs.SquashBuildPack()",
                 "H: Wings": "import WillWing as wing;wing.WatsonWingTemplate()",
                 "H: Muscles": "import MuscleWindow as mw;mw.MusUI()",
                 "H: Ribbon": "rig_frankenstein_utils.legacy_ribbon_b()",
                 "W: KNG Biped": "Watson.TemplateBiped()",
                 "W: SMO Biped": "Watson.TemplateBipedSMO()",
                 "W: EAV Small Biped": "Watson.TemplateBipedSMO()",
                 }

    if pack.startswith("W:") or pack.startswith("H:"):
        cmd = build_cmd.get(pack)
        rig_misc.legacy_load_g_rigging()
        rig_misc.legacy_load_g_rigging_will()
        succ = False
        if cmd.startswith("rig_frankenstein_utils."):
            exec("succ = %s" % cmd.replace("rig_frankenstein_utils.", ""))
        else:
            succ = rig_misc.legacy_try("import Watson;reload(Watson);" + cmd)
        if not succ:
            return False

    elif pack.startswith("GB2: "):
        file_path = rig_io.data_path + "/template_gb2_" + pack.replace("GB2: ", "").lower().replace(" ", "_") + ".mb"
        RIG_F_LOG.info(file_path)
        cmds.file(file_path, i=True)
    
    # Additional Stuff
    if pack == "W: EAV Small Biped":
        eav_position_packs()

    # Add info of pack built to info node so can build the bit later
    info_node = i_node.create_info_node()
    g_pack_attr = i_attr.create(node=info_node, ln="G_Packs", dt="string", use_existing=True)
    val = g_pack_attr.get()
    if val == "None":
        val = None
    if single_pack:
        if val:
            val += ", " + pack
        else:
            val = pack
        g_pack_attr.set(val)

    # Add info of template built to info node
    else:
        # - First, for Watson only, add all the now-built packs to info node like do with single pack
        if pack.startswith("W: "):
            new_packs = [pk.replace("_BuildPack", "") for pk in i_utils.ls("*_BuildPack") if "_Python_" not in pk]
            if val:
                curr_packs = val.split(", ")
                val += ", ".join([pk for pk in new_packs if pk not in curr_packs])
            else:
                val = ", ".join(new_packs)
            g_pack_attr.set(val)
        # - Also indicate a template was built. This will be just for mirroring because the bits will build based on packs
        g_template_attr = i_attr.create(node=info_node, ln="G_Templates", dt="string", use_existing=True)
        t_val = g_template_attr.get()
        if t_val == "None":
            t_val = None
        if t_val:
            t_val += ", " + pack
        else:
            t_val = pack
        g_template_attr.set(t_val)

    # Frame
    i_utils.focus(type="joint")


def legacy_build_bits():
    """
    Build the bits of the legacy system
    :return: (bool) - True/False for success
    """
    # Are there G Packs in the scene to build?
    g_pack_attr, g_packs, g_bits_attr, g_bits = legacy_get_packs_and_bits()
    # if (g_packs and g_bits) and (len(g_packs) == len(g_bits)):  # All were built
    #     return
    if not g_bits and not g_packs:
        RIG_F_LOG.debug("No legacy found.")
        return None  # No legacy here.
    if RIG_F_LOG.level == 10:
        if g_packs:
            RIG_F_LOG.debug("G Packs found: %s" % g_packs)
        if g_bits:
            RIG_F_LOG.debug("G Bits found: %s" % g_bits)

    # Import Watson
    rig_misc.legacy_load_g_rigging()
    # succ = rig_misc.legacy_try("import Watson;reload(Watson)")
    # if not succ:
    #     return False  # Found legacy, but failed

    # Var
    do_full_build = True
    do_watson_build = True

    # Rename bind joint group to Watson way so it builds without stupid hardcode error
    bind_jnt_grp = None
    if i_utils.check_exists("Bind_Jnt_Grp"):
        bind_jnt_grp = i_node.Node("Bind_Jnt_Grp")
        bind_jnt_grp.rename("Bnd_Jnt_Grp")
    
    # Rename rig joint group to Watson way so it builds without stupid hardcode error
    rig_jnt_grp = None
    if i_utils.check_exists("Rig_Jnt_Grp"):
        rig_jnt_grp = i_node.Node("Rig_Jnt_Grp")
        rig_jnt_grp.rename("RIG")

    # Make a Node Containers group so it builds without stupid hardcode errors
    if not i_utils.check_exists("NodeContainers"):
        i_node.create("transform", name="NodeContainers")

    # If there are not any Frankenbits in the scene, can use the full Watson build. Otherwise that errors.
    franken_packs = get_scene_packs(dialog_error=False)
    if franken_packs or g_bits:
        do_full_build = False

    # Squash is different and wasn't set up properly in watson. So do something extra here.
    if "H: Squash" in g_packs and "H: Squash" not in g_bits:
        rig_misc.legacy_load_g_rigging_will()
        succ = rig_misc.legacy_try("import WillsRigScrips;reload(WillsRigScrips);WillsRigScrips.SquashRig()")
        if not succ:
            return False  # Found legacy, but failed
        if not [bit for bit in g_bits if bit not in ["H: Squash", "W: Dynamic Chain"]]:
            do_full_build = False
            do_watson_build = False

    # Are we creating a dyn chain when one already exists? Then just do:
    if "W: Dynamic Chain" in g_packs and (g_bits and "W: Dynamic Chain" in g_bits):
        succ = rig_misc.legacy_try("import DynamicToolBox;reload(DynamicToolBox);DynamicToolBox.ChainAdd()")
        if not succ:
            return False  # Found legacy, but failed

    # Build bits when none exist
    elif do_full_build:
        succ = rig_misc.legacy_try("import Watson;reload(Watson);Watson.WatsonJobsCheck()")
        if not succ:
            return False  # Found legacy, but failed
        # :note: For reference, real building of Watson's bits is in Watson L 2027
        # eval(cmds.getAttr(BuildPack+'.Script')+'Trigger(object = "'+e+'")')

    # Build bits when some already exist ("add to rig" method)
    elif do_watson_build:
        succ = rig_misc.legacy_try("import Watson;reload(Watson);Watson.Watson(False)")
        if not succ:
            return False  # Found legacy, but failed

    # Weirdly creates extra groups. Delete these
    definite_dups = [dup for dup in ["Ctrl_Cns_Grp1", "Utility_Grp1"] if i_utils.check_exists(dup)]
    if definite_dups:
        i_utils.delete(definite_dups)

    # Update the bits attr to match the packs
    g_bits_attr.set(g_packs)

    # Run Pipe Fix
    i_utils.select(cl=True)  # To find all controls without filtering selection
    legacy_watson_fix_for_current_pipe(dialog_error=False)
    i_utils.select(cl=True)

    # Rename bind joint group back to Frankenstein style
    if bind_jnt_grp:
        bind_jnt_grp.rename("Bind_Jnt_Grp")
    
    # Rename rig joint group back to Frankenstein style
    if rig_jnt_grp:
        rig_jnt_grp.rename("Rig_Jnt_Grp")

    # Frame
    i_utils.focus(type="joint")

    # Return True because it found g things to do
    return True 


def deconstruct_packs(pack_info_nodes=None, dialog_error=False):
    """
    Deconstruct bits to their pack stage
    
    :param pack_info_nodes: (list of iNodes) - Pack Info Nodes (ex: L_Leg_Info)
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: None
    """
    # Vars
    given_pack_objs = [get_pack_object(pack_info_node) for pack_info_node in pack_info_nodes]
    
    # Check if pack is even at the bit stage
    not_bits = []
    mirr_objs = []
    pack_objs = []
    for pack_obj in given_pack_objs:
        if not pack_obj.bit_built:
            not_bits.append(pack_obj.base_name)
        elif pack_obj.is_mirror:
            mirr_objs.append(pack_obj.base_name)
        else:
            pack_objs.append(pack_obj)
    if not_bits:
        i_utils.error("Following are not bits and cannot be deconstructed: %s" % ", ".join(not_bits), raise_err=False, verbose=True)
    if mirr_objs:
        i_utils.error("Following are mirrors and cannot be deconstructed separately from drivers: %s" % ", ".join(mirr_objs), raise_err=False, verbose=True)
    if not pack_objs:
        i_utils.error("No deconstructable pack objects found.", dialog=dialog_error)
        return

    # Wait Cursor
    if dialog_error:
        cmds.waitCursor(state=True)

    # Get mirrored info
    mirror_data = {}
    for pack_obj in pack_objs:
        mirror_pack_data = get_mirrored_connections(pack_info_node=pack_obj.pack_info_node, raise_error=False)
        if mirror_pack_data:
            mirror_obj = mirror_pack_data[1]
            mirror_sym = mirror_obj.is_mirror_sym
            mirror_data[pack_obj.pack_info_node] = {"mirror" : mirror_pack_data[1], "sym" : mirror_sym}
    
    # Get current joint / pack object placements
    for pack_obj in pack_objs:
        pack_obj._update_position_data()

    # :note: These deconstruct steps that change the in-scene information must be all at once per step, not looping each pack obj and doing everything
    # Otherwise it will break because of stitching issues when things do not exist.

    # Get stitch data so can restitch after deleted
    stitch_data = {}
    for pack_obj in pack_objs:
        stitch_data[pack_obj.pack_info_node] = pack_obj._get_stitch_data()
        RIG_F_LOG.debug("##VARCHECK stitch_data (%s)" % pack_obj.pack_info_node, stitch_data[pack_obj.pack_info_node].__dict__)

    # Unstitch
    for pack_obj in pack_objs:
        RIG_F_LOG.debug("Unstitching '%s'" % pack_obj.pack_info_node)
        pack_obj.unstitch_bit(unstitch_children=True, raise_error=False, clear_data=False)
        RIG_F_LOG.debug("##VARCHECK post-unstitch stitch_data (%s)" % pack_obj.pack_info_node, pack_obj._get_stitch_data().__dict__)
    
    # raise RuntimeError("baba")

    # # Re-get pack objs from scene since some packs (like eyes) delete others (like eyes_master) when unstitched
    # scene_pack_info_nodes = get_scene_packs(pack_info_nodes=pack_info_nodes, search={"bit_built" : True, "is_mirror" : False})
    # pack_objs = [get_pack_object(pack_info_node) for pack_info_node in scene_pack_info_nodes]
    
    # Delete the pack and bit
    # - Get info needed to rebuild pack
    deconed_info_nodes = []
    deconed_cog = False
    all_pack_defaults = get_all_pack_options()
    pack_obj_info = {}
    for pack_obj in pack_objs:
        pack_info_node = pack_obj.pack_info_node
        if pack_obj.build_type == "Eyes_Master":
            continue
        if pack_obj.build_type == "Cog":
            deconed_cog = True
        deconed_info_nodes.append(pack_info_node)
        
        # - Get all the info
        pack_defaults = all_pack_defaults.get(pack_obj.build_type)
        pack_inscene = pack_obj.__dict__.copy()
        pack_info = {}
        
        # - Filter to usable type of info
        # This is important to not have bit-built nodes in the pack_obj items because then when reconstruct, the objs won't exist
        # -- Start with the blank slate
        pack_info.update(pack_defaults)
        # -- Add non-nodes / non-attrs
        for k, v in pack_inscene.items():
            # First check with basics
            if not v:
                continue
            if "_ctrl" in k:  # Known k names that have nodes that may not be caught below
                continue
            if isinstance(v, (i_node.Node, i_node._Node, i_attr.Attr, i_attr._Attr)):
                continue
            elif isinstance(v, (list, tuple)):
                if isinstance(v[0], (i_node.Node, i_node._Node, i_attr.Attr, i_attr._Attr)):
                    continue
            elif isinstance(v, (dict, collections.OrderedDict)):
                if isinstance(v.values()[0], (i_node.Node, i_node._Node, i_attr.Attr, i_attr._Attr)):
                    continue
            
            # Then another round of check. This check alone would not catch single items because node/attr __repr__
            v_generic = i_utils.convert_data(v, to_generic=True)
            if v == v_generic:  # Nothing node/attr
                RIG_F_LOG.debug("Storing in details: %s >>" % k, v)
                pack_info[k] = v
        
        # - Include usable data in overall dict
        pack_obj_info[pack_info_node] = pack_info
    # - Do Deletion
    RIG_F_LOG.info("Deconstructed Info Nodes:", deconed_info_nodes)
    for pack_info_node in deconed_info_nodes:
        delete_pack(pack_info_node)  # :note: Also deletes mirror

    # Rebuild Packs
    pack_objs = []
    for pack_info_node in deconed_info_nodes:
        details = pack_obj_info.get(pack_info_node)
        details.update({"do_stitch" : False, "do_pack_positions" : False})
        RIG_F_LOG.info("Rebuilding... '%s' from '%s'" % (details.get("base_name"), pack_info_node))
        RIG_F_LOG.info("Details using:", details)
        pack_obj = get_pack_object(pack_defaults=details)
        pack_obj.create_pack()
        pack_objs.append(pack_obj)
    RIG_F_LOG.info("Rebuilt packs:", [obj.base_name for obj in pack_objs])
    
    # Rebuild Mirror
    if mirror_data:
        for pack_info_node, mirror_pack_data in mirror_data.items():
            mirror_pack(pack_info_node=pack_info_node, symmetry=mirror_pack_data.get("sym"))

    # Re-Stitch
    if stitch_data:
        for pack_obj in pack_objs:
            pack_stitch_data = stitch_data.get(pack_obj.pack_info_node)
            RIG_F_LOG.debug("##VARCHECK restitching with stitch_data (%s)" % pack_obj.pack_info_node, pack_stitch_data.__dict__)
            pack_obj.stitch_pack(raise_error=False, stitch_data=pack_stitch_data)
            RIG_F_LOG.debug("##VARCHECK post-restitch stitch_data (%s)" % pack_obj.pack_info_node, pack_obj._get_stitch_data().__dict__)

    # If biped, hide the cog
    template = get_scene_template()
    if template == "Biped":
        cog_pack = [pack_obj for pack_obj in pack_objs if pack_obj.build_type == "Cog"]
        if cog_pack:
            cog_joints = cog_pack[0].base_joints
            for jnt in cog_joints:  # Hiding or Deleting messes up stitching, so just let it chill
                jnt.drawStyle.set(2)  # None
    
    # If cog, remove attrs from info node
    if deconed_cog:
        nd_attrs = [i_node.info_node_name + "." + attr_name for attr_name in ["root_ctrl", "ground_ctrl", "cog_ctrl", "vis_ctrl"]]
        i_utils.delete(nd_attrs)

    # Clear Selection
    i_utils.select(cl=True)
    
    # Wait Cursor
    if dialog_error:
        cmds.waitCursor(state=False)


class PacksIO(DataIO):
    """Import/Export class for Packs"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="packs_data.json", **kwargs)

    def _get(self, pack_info_nodes=None):
        """
        Get the data of objects to store

        :param pack_info_nodes: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Check
        i_utils.check_arg(pack_info_nodes, "pack info nodes")

        # Create dictionary
        json_dict = {}

        # Template info
        json_dict["template"] = get_scene_template()
        json_dict["local_rotations"] = {}
        json_dict["joint_orients"] = {}

        # Pack info
        for pack_info_node in pack_info_nodes:
            # - Get object
            pack_obj = get_pack_object(i_node.Node(pack_info_node))
            # - Ignore mirrored
            if pack_obj.is_mirror_sym:
                continue
            # - Update base joint positions with in-scene positions
            pack_obj._update_position_data()
            # - Add obj data to dict writing
            pack_data = pack_obj.__dict__.copy()
            store_pack_data = {}
            for k, v in pack_data.items():
                if k.startswith("created_"):
                    continue
                if "_ctrl" in k:
                    continue
                store_pack_data[k] = i_utils.convert_data(v)
            json_dict[pack_info_node.name] = store_pack_data
            # - Get additional positioning info for the joints
            # :TODO: If get this working with applying stored rot/jo, then put this into the pack class obj itself
            pack_rotations = {}
            pack_jos = {}
            all_joints = pack_obj._get_all_base_joints()
            for joint in all_joints:
                pack_rotations[joint] = joint.r.get()
                pack_jos[joint] = joint.jo.get()
            json_dict["local_rotations"][pack_info_node] = pack_rotations
            json_dict["joint_orients"][pack_info_node] = pack_jos

        # Return
        return json_dict

    def write(self, pack_info_nodes=None, **kwargs):
        """
        Write object data to a json file

        :param pack_info_nodes: (list) - (optional) Objects to get information on
        :param kwargs: (dict) - Used in DataIO.write()

        :return: (str) - Path to the json file exported
        """
        # Check
        if not pack_info_nodes:
            pack_info_nodes = get_scene_packs()
        raise_error = kwargs.get("raise_error", True)
        pack_info_nodes = i_utils.check_arg(pack_info_nodes, "pack info nodes", raise_error=raise_error)
        if not pack_info_nodes:  # raise_error is False
            return

        # Get Json Values
        j_dict = self._get(pack_info_nodes=pack_info_nodes)
        if not j_dict:
            i_utils.error("Could not find json information.")

        # Write
        DataIO.write(self, path=self.json_path, data=j_dict, **kwargs)

        # Return
        return self.json_path

    def _set(self, json_info=None):
        """
        Set in-scene objects based on json info

        :param json_info: (dict) - Information from the json file (based on _get())

        :return: None
        """
        # Check
        i_utils.check_arg(json_info, "json info")

        # Vars
        start_inscene_pack_info_nodes = get_scene_packs()
        template = json_info.get("template")
        rotations = json_info.get("local_rotations")
        joint_orients = json_info.get("joint_orients")
        stored_pack_info_nodes = [nd for nd in json_info.keys() if nd not in ["template", "local_rotations", "joint_orients"]]
        stored_pack_obj_dicts = [json_info.get(pack_info_node) for pack_info_node in stored_pack_info_nodes]

        # Vars for message
        successes = []
        errors = {}

        # Build the template / packs
        template_in_scene = get_scene_template()
        if not template_in_scene:
            # - Vars
            template_pack_overrides = {}
            # stored_build_types = []
            # - Get template obj
            template_info = get_all_template_options().get(template)
            template_obj = get_pack_object(pack_defaults=template_info.copy())
            template_build_options = template_obj.pack_options
            template_stored_types = []
            # - Pack Build Type overrides
            for pack_obj_dict in stored_pack_obj_dicts:
                # - Check if it is a part of the template or an extra pack
                pack_build_type = pack_obj_dict.get("build_type")
                if pack_build_type not in template_build_options:
                    continue
                # - Manually create pack joints with stored info
                pack_joints = create_pack_joints(pack_obj=i_utils.Mimic(pack_obj_dict), calculate=False)
                pack_obj_dict["pack_joints"] = pack_joints
                # - Clear lists so can append actually-created items (esp for chains)
                pack_obj_dict["top_base_joint"] = None
                pack_obj_dict["base_joints"] = []
                pack_obj_dict["base_joints_chains"] = []
                # - Store override for template
                template_stored_types.append(pack_build_type)
                template_pack_overrides[pack_build_type] = pack_obj_dict
                successes.append(pack_obj_dict.get("pack_info_node"))
            # - Any template packs not stored? (Deleted packs)
            # :note: Filter so don't add any additionally stored packs that are not in the template
            template_obj.pack_options = template_stored_types
            # - Declare pack overrides
            template_obj.pack_info_overrides = template_pack_overrides
            # - Create
            template_obj.create()

        # Else position existing packs
        else:
            start_inscene_pack_objs = [get_pack_object(pack_info_node) for pack_info_node in start_inscene_pack_info_nodes]
            # - Unstitch (else positioning pack things gets messed up)
            for pack_obj in start_inscene_pack_objs:
                pack_obj.unstitch_pack(raise_error=False, clear_data=False)
            # - Update positions
            for pack_obj in start_inscene_pack_objs:
                stored_pack_info = json_info.get(pack_obj.pack_info_node)
                if not stored_pack_info:
                    errors[pack_obj.pack_info_node] = "No stored positions to load"
                    continue
                radius = stored_pack_info.get("joint_radius")
                # - Top Joint
                top_joint = pack_obj.top_base_joint
                top_joint_position = stored_pack_info.get("top_base_joint_position")
                if top_joint_position:  # Only stored when top_base_joint is not part of base_joints already (ex: Hand)
                    top_joint.xform(t=top_joint_position, ws=True)
                    top_joint.radius.set(radius)
                # - Base Joints
                base_joints = pack_obj.base_joints
                base_joint_positions = stored_pack_info.get("base_joint_positions")
                for i, jnt in enumerate(base_joints):
                    jnt.xform(t=base_joint_positions[i], ws=True)
                    jnt.radius.set(radius)
                # - Chain Joints
                base_joints_chains = pack_obj.base_joints_chains
                base_joints_chain_positions = stored_pack_info.get("base_joints_chain_positions")
                for j, chain_ls in enumerate(base_joints_chains):
                    for k, chain_jnt in enumerate(chain_ls):
                        chain_jnt.xform(t=base_joints_chain_positions[j][k], ws=True)
                        chain_jnt.radius.set(radius)
                # - Store success
                successes.append(pack_obj.pack_info_node)
            # - Restitch
            for pack_obj in start_inscene_pack_objs:
                pack_obj.stitch_pack(raise_error=False)
            # - Re-Force Mirror Radius
            rig_joints.force_mirror_radius()

        # Build additional packs
        postbuild_inscene_pack_info_nodes = get_scene_packs(search={"is_mirror_sym" : False})  # :note: stored only non-mirror-sym
        if len(stored_pack_info_nodes) > len(postbuild_inscene_pack_info_nodes):
            non_built_info_nodes = list(set(stored_pack_info_nodes) - set(postbuild_inscene_pack_info_nodes))
            for pack_info_node in non_built_info_nodes:
                pack_obj = get_pack_object(pack_defaults=json_info.get(pack_info_node))
                pack_obj.create_pack()
                successes.append(pack_info_node)

        # # After all worldspace translation placed, do the rotations and joint orients
        # pack_objs = [get_pack_object(pack_info_node) for pack_info_node in postbuild_inscene_pack_info_nodes]
        # # - Unstitch (else positioning pack things gets messed up)
        # for pack_obj in pack_objs:
        #     pack_obj.unstitch_pack(raise_error=False, clear_data=False)
        # # - Rotate/Joint Orient
        # for pack_obj in pack_objs:
        #     # - Get rotations
        #     if pack_obj.is_mirror_sym:
        #         continue
        #     pack_rotations = rotations.get(pack_obj.pack_info_node.name)
        #     pack_joint_orients = joint_orients.get(pack_obj.pack_info_node.name)
        #     if not pack_rotations or not pack_joint_orients:
        #         self.log.warn("No rotations or joint orient information stored for '%s'" % pack_obj.pack_info_node)
        #         continue
        #     # - Get all joints
        #     all_joints = pack_obj._get_all_base_joints()
        #     # - Set
        #     for jnt in all_joints:
        #         jnt.r.set(pack_rotations.get(jnt))
        #         # jnt.jo.set(pack_joint_orients.get(jnt))
        # # - Restitch
        # for pack_obj in pack_objs:
        #     pack_obj.stitch_pack(raise_error=False)

        # Update pack object info back from json-friendly strings to i_nodes / i_attrs
        created_pack_info_nodes = get_scene_packs()
        if start_inscene_pack_info_nodes:
            created_pack_info_nodes = list(set(created_pack_info_nodes) - set(start_inscene_pack_info_nodes))
        if created_pack_info_nodes:
            for pack_info_node in created_pack_info_nodes:
                pack_obj = get_pack_object(pack_info_node)
                upd_data = {}
                for k, v in pack_obj.__dict__.items():
                    upd_data[str(k)] = i_utils.convert_data(v, to_generic=False)
                # upd_data = i_utils.convert_data(pack_obj.__dict__, to_generic=False)
                # - Force some things to be strings and not nodes
                for k in ["base_name"]:
                    upd_data[str(k)] = i_utils.convert_data(upd_data.get(k))
                upd_data_pickle = pickle.dumps(upd_data)
                i_attr.create(node=pack_obj.pack_info_node, ln="build_data", at="string", dv=str(upd_data_pickle),
                              l=True, use_existing=True)

        # Frame
        i_utils.focus(type="joint")

        # Verbose
        # - Convert errors to expected message format
        if errors:
            errors_converted = []
            for info_node, messages in errors.items():
                info_msgs = "\n- ".join(messages)
                errors_converted.append([info_node, info_msgs])
            errors = errors_converted
        # - Print / Popup
        self._message(action="import", set=True, errors=errors, successes=sorted(successes))

    def read(self, pack_info_nodes=None, set=False, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.

        :param pack_info_nodes: (list) - (optional) Objects to get information on. If not given, queries selection.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param kwargs: (dict) - Used in DataIO.read()

        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read specific nodes only?
        if not pack_info_nodes:
            pack_info_nodes = get_scene_packs(check_sel=True, search={"bit_built" : False})

        # Read Json Values
        ret_dict = DataIO.read(self, path=self.json_path, specified_nodes=pack_info_nodes, **kwargs)
        if not ret_dict:
            return None

        # Set Values in Scene?
        if set:
            self._set(json_info=ret_dict)

        # Verbose - only if not set. The set verbose is very specific, so that happens in ._set()
        else:
            self._message(action="import", successes=ret_dict.keys())

        # Return
        return ret_dict


def check_pack_name(build_type=None, side=None, description=None, dialog_error=False):
    """
    Check that a pack's name is acceptable formatting in general and based on the pack's restricted sides (if it has any)
    
    :param build_type: (str) - Pack type (ex: "Limb")
    :param side: (str) - Side checking
    :param description: (str) - Description checking
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (list of strs) [AcceptableSide (str), AcceptableDescription (str)]
    """
    # Get pack defaults
    # :TODO: See if can store this information in a module attr when __main__ so don't always have to query
    pack_defaults = get_all_pack_options().get(build_type)

    # Check Side
    restricted_sides = pack_defaults.get("restricted sides")
    if restricted_sides and side in restricted_sides:
        approved_sides = ["'" + sd + "'" for sd in i_node.side_options if sd not in restricted_sides]
        i_utils.error("%s cannot build with side: '%s'\n\nPlease choose from: %s" %
                      (build_type, side, ", ".join(approved_sides)), dialog=dialog_error)
        return False
    
    # Check Description
    if not description:
        i_utils.error("Must provide pack description.", dialog=dialog_error)
        return False
    
    # Format Description
    if " " in description:
        description = "".join([pd[0].upper() + pd[1:] for pd in description.split(" ")])
    description = description[0].upper() + description[1:]

    # Check a pack with this name does not already exist
    all_scene_pack_infos = get_scene_packs(dialog_error=False)
    if all_scene_pack_infos:
        base_name = ""
        if side:
            base_name += side + "_"
        base_name += description
        if base_name + "_Info" in all_scene_pack_infos:
            i_utils.error("There is already a pack named %s." % base_name, dialog=dialog_error)
            return False

    # All passed
    return [side, description]

def _get_scene_pack_positions(joint_only=False):
    """
    Get in-scene pack position data
    Mostly for dev use so can make new pack default joint positions based on selected in-scene joints
    
    :param joint_only: (bool) - Only care about joints? Or also about other pack-created objects?
    
    :return: None
    """
    objs = i_utils.check_sel(type="joint" if joint_only else None)
    if not objs:
        return 
    
    for obj in objs:
        # - Translation
        trans = [round(i, 3) for i in obj.xform(q=True, t=True, ws=True)]
        RIG_F_LOG.info("%s >> T: %s" % (obj, trans))
        # - Rotation
        rot = [round(i, 3) for i in obj.r.get()]
        if rot != [0, 0, 0]:
            RIG_F_LOG.info("%s >> R: %s" % (obj, rot))
        # - Joint Orient
        if joint_only or obj.node_type() == "joint":
            jo = [round(i, 3) for i in obj.jo.get()]
            if jo != [0, 0, 0]:
                RIG_F_LOG.info("%s >> JO: %s" % (obj, jo))


def _get_scene_control_limits():
    """
    Get selected object's transform limits and verbose log them.
    This is just a dev tool mostly.
    :return: None
    """
    sel = i_utils.check_sel()
    if not sel:
        return

    for nd in sel:
        limits = nd.get_limits()
        t_lim = "translate_limits=[%s, %s, %s]" % (str(limits.tx), str(limits.ty), str(limits.tz))
        r_lim = "rotate_limits=[%s, %s, %s]" % (str(limits.rx), str(limits.ry), str(limits.rz))
        RIG_F_LOG.info("%s >> %s, %s" % (nd, t_lim, r_lim))


def test_repo_packjoints_from_ref():
    """
    Temp for hacking when packs io isn't great.
    - Build a new biped (etc).
    - Reference in the packs with good positions.
    - Run this (no selection)
    """
    # Get top nodes
    top_node = rig_nodes.get_top_group(raise_error=False)
    top_node_ref = i_utils.ls("*:" + top_node)
    if not top_node_ref:
        i_utils.error("No reference node with '%s' in name found." % top_node)
    top_node_ref = top_node_ref[0]
    ref_ns = top_node_ref.namespace()

    # Get joints
    top_joints = []
    build_grp_ch = i_node.Node("BuildPack_Grp").relatives(c=True)
    for grp in build_grp_ch:
        top_joints += grp.relatives(c=True, type="joint")
    # - Force adding the subgrouped face joints
    if i_utils.check_exists(ref_ns + ":Face_Grp") and i_utils.check_exists("Face_Grp"):
        fresh_face_grp = i_node.Node("Face_Grp")
        fresh_face_subgrps = fresh_face_grp.relatives(c=True, type="transform")
        for subgrp in fresh_face_subgrps:
            top_joints += subgrp.relatives(c=True, type="joint")

    # Match ref to fresh build joints
    for top_jnt in top_joints:
        # - Find children
        fresh_joints = [top_jnt] + top_jnt.relatives(ad=True)  # :note: does not return in fullPath because of Node() wrap. See fn for note.
        # - Sorted - in order for proper copying and jo positioning
        fresh_joints_ordered = sorted([jnt.name_long() for jnt in fresh_joints])
        fresh_joints_nodes = i_utils.convert_data(fresh_joints_ordered, to_generic=False)

        # - Copy
        fresh_mirrors = []
        for fresh_jnt in fresh_joints_nodes:
            if fresh_jnt.tx.connections(d=False):  # Mirror driven. Do not try and place
                fresh_mirrors.append(fresh_jnt)  # Will need to do joint orients
                continue
            ref_jnt = ref_ns + ":" + fresh_jnt.name_local()
            if not i_utils.check_exists(ref_jnt):
                RIG_F_LOG.warn("'%s' does not exist. Cannot copy position onto '%s'." % (ref_jnt, fresh_jnt))
                continue
            ref_jnt = i_node.Node(ref_jnt)
            RIG_F_LOG.info("Copying position: '%s' >> '%s'" % (ref_jnt, fresh_jnt))
            i_node.copy_pose(driver=ref_jnt, driven=fresh_jnt, attrs=['t', 'r', 'jo', 'radius'])
        
        if fresh_mirrors:
            for fresh_jnt in fresh_mirrors:
                ref_jnt = ref_ns + ":" + fresh_jnt.name_local()
                if not i_utils.check_exists(ref_jnt):
                    RIG_F_LOG.warn("'%s' does not exist. Cannot copy position onto '%s'." % (ref_jnt, fresh_jnt))
                    continue
                i_node.copy_pose(driver=ref_jnt, driven=fresh_jnt, attrs=['jo', 'radius'])
    
    # For the foot locators
    # :TODO: Use the "pack_extras" if this script is needed for more robust things. Hardcoded for now bc this should be very rare to be used.
    loc_grp = i_utils.ls("L_Foot_Locators_Grp")
    ref_loc_grp = i_utils.ls(ref_ns + ":L_Foot_Locators_Grp")
    if loc_grp and ref_loc_grp:
        locs = [loc for loc in loc_grp[0].relatives(c=True) if loc.relatives(s=True, type="locator")]  # ignore constraint in group
        for loc in locs:
            ref_loc = i_node.Node(ref_ns + ":" + loc)
            i_node.copy_pose(driver=ref_loc, driven=loc, attrs='t')


# def get_stitch_by_selection(pack_build_type=None):
#     """ For things like DynamicChain and FkChain, which can stitch to anything using a constraint.
#     User selects what pack they want to stitch to (what should drive) and then gets popup of options
#     Returns item to include in the stitch cmds
#     """
#     # Get parent and pack objects
#     sel = i_utils.check_sel(length_need=2)  # Store the specific selected driver item
#     if not sel:
#         return
#     sel_info_nodes = get_packs_from_objs(sel)
#     parent_driver_item = sel[0]
#     parent_obj = get_pack_object(sel_info_nodes[0])
#     pack_obj = get_pack_object(sel_info_nodes[1])
# 
#     # Check if driven is expected build type
#     if pack_obj.build_type != pack_build_type:
#         i_utils.error("'%s' is not a '%s' it is a '%s'. Cannot stitch." %
#                       (pack_obj.base_name, pack_build_type, pack_obj.build_type), dialog=True)
#         return
# 
#     # Which part of parent pack stitching to?
#     parent_stitch_area = None
#     do_par_st_area = i_utils.message(title="Manual Stitching",
#                                      button=["first jnt", "first ctrl", "last jnt", "last ctrl", "this jnt",
#                                              "this ctrl", "Cancel"],
#                                      message="Which part of '%s' should drive '%s'?" % (
#                                      parent_obj.base_name, pack_obj.base_name))
#     parent_joints = parent_obj.bind_joints
#     # parent_ctrls
#     if do_par_st_area == "first jnt":
#         parent_stitch_area = None
#     elif do_par_st_area == "first ctrl":
#         parent_stitch_area = None
#     elif do_par_st_area == "last jnt":
#         parent_stitch_area = None
#     elif do_par_st_area == "last ctrl":
#         parent_stitch_area = parent_obj.created_controls
#     elif do_par_st_area == "this jnt":
#         pass
#     elif do_par_st_area == "this ctrl":
#         pass
#     else:
#         return
# 
#     # Return
#     return parent_stitch_area


def legacy_add_watson_info_attrs():
    """
    Add attrs to the Rig Info node to recognize what G (Watson-built) packs and bits are in the scene
    :return: None
    """
    info_node = i_node.create("transform", n=i_node.info_node_name, use_existing=True)
    packs_attr = i_attr.create(info_node, ln="G_Packs", at="string", use_existing=True)
    bits_attr = i_attr.create(info_node, ln="G_Bits", at="string", use_existing=True)

    all_packs = []
    watson_pack_groups = i_utils.ls("*_BuildPack")
    if not watson_pack_groups:
        i_utils.error("Nothing found with name '*_BuildPack'", dialog=True)
        return

    for pg in watson_pack_groups:
        # - Get Watson Pack's name
        name = pg.split("_BuildPack")[0]
        name_attr = pg + ".Name"
        if i_utils.check_exists(name_attr):
            name = i_attr.Attr(name_attr).get()
        # - Add
        all_packs.append(name)

    if all_packs:
        packs_str = ", ".join(["W: %s" % pn for pn in list(set(all_packs))])
        packs_attr.set(packs_str)


def legacy_clean_head_groups():
    """
    Delete unused nodes and head-specific items that needed to be cleaned
    :return: None
    """
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    head_sq_things = [obj for obj in ['Head_Utl_Grp', 'HeadMushy_Ctrl_Grp'] if i_utils.check_exists(obj)]
    if head_sq_things:
        i_utils.delete(head_sq_things)

    # legacy_watson_fix_for_current_pipe()


def legacy_watson_fix_for_current_pipe(dialog_error=True):
    """
    Create info node and necessary attributes/connections for scripts to recognize Watson rig items like they do with Frankenstein

    :param dialog_error: (bool) - Give popup when errors arise to alert user?

    :return: None
    """
    # Vars
    msg = ""

    # Get nodes that should be tracked
    tracked = rig_nodes.get_tracked_nodes()
    top_group = tracked.get("top_group")
    controls = tracked.get("controls")
    if not top_group:
        msg += "\nCannot find top group."
    if not controls:
        msg += "\nCannot find controls."
    if not top_group and not controls:
        i_utils.error(msg, dialog=dialog_error, raise_err=False)
        return

        # Create Info Node
    info_node = i_node.info_node_name
    if not i_utils.check_exists(info_node):
        i_node.create_info_node(parent=top_group)

    # Check Info Node Connections
    not_connected = rig_nodes.check_info_connections(top_group=top_group, controls=controls)
    if not_connected:
        msg += "\nConnecting to info node:\n\n"
        for attr, objs in not_connected.items():
            obj_names = i_utils.convert_data(objs)
            msg += "\n- ".join(obj_names)
            i_node.connect_to_info_node(info_attribute=attr, objects=objs)

    # Update default attrs
    missing_defaults = [nd for nd in controls + [top_group] if nd and not i_attr.check_defaults_stored(nd)]
    if missing_defaults:
        obj_names = i_utils.convert_data(missing_defaults)
        msg += "\nUpdating current values as defaults on:\n\n- " + "\n- ".join(obj_names)
        i_attr.update_default_attrs(nodes=missing_defaults)

    # Message prompt?
    if msg:
        i_utils.error(msg, dialog=dialog_error, raise_err=False)


def legacy_ribbon():
    """
    Legacy version of Import Ribbon
    This has been migrated into pipeline as the "Ribbon" build through Frankenstein
    :return: None
    """
    rig_misc.legacy_load_g_rigging()
    import AnimDeformerTools
    rig_misc.legacy_try(AnimDeformerTools.RibbonImport)
    # AnimDeformerTools.RibbonImport()


def legacy_ribbon_b():
    """
    Legacy version of Create Ribbon
    This has been migrated into pipeline: rig_tools.utils.deformers.create_ribbon_b_sel()
    :return: (bool) - True/False for success
    """
    # Temporary. 
    rig_misc.legacy_load_g_rigging_will()
    import WillsRigScrips
    succ = rig_misc.legacy_try(WillsRigScrips.Ribbon)
    # WillsRigScrips.Ribbon()
    return succ


def create_master_center_of_geo():
    import rig_tools.frankenstein.templates.character as tpt_c
    meshObjs = []
    for mesh in cmds.ls(type='mesh'):
        trans = cmds.listRelatives(mesh, p=True)[0]
        if trans not in meshObjs and cmds.getAttr('{0}.v'.format(trans)):
            meshObjs.append(trans)

    char = tpt_c.Template_Character()
    char.create()

    if len(meshObjs):
        if cmds.objExists('COG_Ctrl_Offset_Grp'):
            pos = i_utils.get_center_of_volume(meshObjs)
            cmds.xform('COG_Ctrl_Offset_Grp', ws=True, t=[0.0, pos[1], 0.0])
        if cmds.objExists('Control_Ctrl_Offset_Grp'):
            bb = i_utils.get_bounding_box_of_collection(meshObjs)
            cmds.xform('Control_Ctrl_Offset_Grp', ws=True, t=[0.0, bb[4]*1.1, 0.0])
