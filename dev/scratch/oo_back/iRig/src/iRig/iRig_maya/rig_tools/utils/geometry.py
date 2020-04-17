import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import math
import os
import random

import maya_utils
import tex_utils
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO


def check_is_model(obj_checking=None, mesh_only=True, ignore_face=True, raise_error=False):
    """
    Check if given object is from the model.
    
    :param obj_checking: (iNode, str) - Object querying
    :param mesh_only: (bool) - Only consider meshes as a part of the model (as opposed to things like groups and locators)
    :param ignore_face: (bool) - Ignore items that are in-scene as a part of the face rig?
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (iNode, bool) - The object if it is successfully a model geo, else False
    """
    # Exists?
    exists = i_utils.check_arg(obj_checking, "object", exists=True, raise_error=False)
    if not exists:
        i_utils.error("'%s' is not a model geo: It does not exist." % obj_checking, raise_err=raise_error)
        return False

    # Force as i_node
    obj_checking = i_node.Node(obj_checking)

    # If given a shape, need to use the transform for checking namespaces because shapes don't always have them (ex: Deformed shapes)
    nt = obj_checking.node_type()
    if nt != "transform":
        msg = "'%s' is a %s, not a transform." % (obj_checking, obj_checking.node_type())
        if nt == "mesh":  # Only try when given a mesh. Sometimes given a fosterParent type and don't want the group above it
            par = obj_checking.relatives(p=True, type="transform")
            if par:
                RIG_LOG.debug(msg + " Using parent transform: '%s' instead." % par)
                obj_checking = par
        else:
            i_utils.error(msg, raise_err=raise_error)
            return False
    
    # EAV specific (no namespaces)
    if i_utils.is_eav:
        # - Watson rigs
        geo_grp = "HiRes_Geo_Grp"
        if i_utils.check_exists(geo_grp):
            if geo_grp not in obj_checking.name_long().split("|"):
                i_utils.error("'%s' is not a model geo: It is not parented under '%s'." % (obj_checking, geo_grp), raise_err=raise_error)
                return False
        # - Arc rigs there's no way to know, so just grab everything
        else:
            RIG_LOG.debug("Cannot determine model geo at all for Arc rigs. Grabbing all scene meshes.")
    
    # All other shows use references
    else:
        # - Referenced / Namespaced
        if not obj_checking.is_referenced() and ":" not in obj_checking:
            i_utils.error("'%s' is not a model geo: It is not referenced or has no namespace." % obj_checking, raise_err=raise_error)
            return False
        # - Namespace Vars
        asset = os.environ.get("TT_ENTNAME")
        ns = obj_checking.split(":")[0]
        # - Face Rig?
        if ignore_face and ns.startswith(asset + "_Face_Rig_"):
            i_utils.error("'%s' is not a model geo: It is a part of the 'Face_Rig' reference." % obj_checking, raise_err=raise_error)
            return False
        # - Actual model-style namespace?
        if not ns.startswith(asset + "_"):
            i_utils.error("'%s' is not a model geo: It does not have a namespace of the asset (%s)." % (obj_checking, asset), raise_err=raise_error)
            return False
        ns_num = ns.split(asset + "_")[1]
        if not ns_num.isdigit():  # Ex: <asset>_Face_Rig_<num>:
            i_utils.error("'%s' is not a model geo: It does not have a namespace of the asset (%s) and a number." % (obj_checking, asset), raise_err=raise_error)
            return False
    
    # Is mesh?
    if mesh_only:
        is_mesh = i_node.check_is_mesh(obj_checking)
        if not is_mesh:
            i_utils.error("%s is not a model geo: It is not a mesh." % obj_checking, raise_err=raise_error)
            return False
    
    # Passed
    RIG_LOG.debug("Success! %s is a model geo." % obj_checking)
    return obj_checking


def pre_color_dupe(geos=None):
    """
    EAV-specific process to duplicate model geos for them to be colored. 
    See: http://pipedocs.icon.local:8000/resources/tool/rig_ios/#eav-mesh-tone
    
    :param geos: (list) - (optional) Geos to duplicate. If not provided uses all model geos in scene.
        :note: If asset is an environment, first gives confimation popup since duplicating all geos in a large environment
        can take a long time. (ex: City of Avalor)
    
    :return: (list of iNodes) - Duplicates created
    """
    if not i_utils.is_eav:
        i_utils.error("This is an EAV-only process.", dialog=True)
        return
    
    if not geos:
        # - If it's a set, super confirm with user because could be duping thousands
        if os.environ.get("TT_ASSTYPE") == "Environment":
            do_it = i_utils.message(title="Confirm", button=["Yes", "No"], 
                                    message="Without a selection, duping all geo in a set could take a lot of time.\n\n"
                                            "Are you sure this is your choice in life?")
            if do_it != "Yes":
                return
        # - Get all model geos in scene
        all_geos = [mesh.relatives(0, p=True) for mesh in i_utils.ls(type="mesh") if check_is_model(mesh, raise_error=False)]
        if not all_geos:
            i_utils.error("Cannot find model geos and nothing was selected.", dialog=True)
            return
        geos = all_geos
    
    # Check that there aren't accidental "_RIG_COLOR_TEMP" geos in there
    orig_temp_geos = [geo for geo in geos if "_RIG_COLOR_TEMP" in geo]
    if orig_temp_geos:
        do_del = i_utils.message(title="Found Temps as Models", button=["Yes", "No"],
                                 message="Found '_RIG_COLOR_TEMP' geos that are being treated as model geos (parented under"
                                         "Geo_Grp). These should not be here.\n\nShall I delete them for you?")
        if do_del == "Yes":
            geos = [geo for geo in geos if geo not in orig_temp_geos]
            i_utils.delete(orig_temp_geos)
    
    # Dup
    dupes = []
    geos = list(set(geos))
    for geo in geos:
        # - Do Dup
        dup = geo.duplicate(add_suffix="_RIG_COLOR_TEMP")[0]
        # - Clear any children (ex: if original geo had constraints)
        dup_chdn = dup.relatives(s=False, c=True)
        if dup_chdn:
            RIG_LOG.warn("Deleting duplicate's children (%s)" % dup_chdn)
            i_utils.delete(dup_chdn)
        # - Append
        dupes.append(dup)
    
    # Group
    grp = i_node.create("transform", n="COLOR_DUPES_TEMP", use_existing=True)
    i_utils.parent(dupes, grp)
    
    # Return
    return dupes


def pre_color_dupe_sel():
    """
    Selection wrapper for pre_color_dupe()
    
    :return: None
    """
    # Get Geos
    geos = i_utils.check_sel(raise_error=False, dialog_error=False)
    # :note: selection is not required
    
    # Dupe
    pre_color_dupe(geos)


class MeshToneIO(DataIO):
    """Import/Export class for Rig Geo MeshTones"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="meshtone_data.json", **kwargs)
        self.temp_dupe_shapes = []

    def _get(self):
        """
        Get the data of objects to store

        :return: (dict) Json Dict of data to store
        """
        # Get with shaders as keys
        shader_info = tex_utils.get_shader_info()
        json_dict = shader_info.copy()
        
        # Find transforms for each member.
        # This is because shapes could be the Deformed shape, but when Import those shapes may not exist, so using
        # transform info as a backup to get current in-scene shapes to apply shaders
        # - Get shapes
        shape_members = []
        for shader, info in json_dict.items():
            shader_mems = info.get("members")
            if not shader_mems:
                self.log.info("Shader '%s' has no members." % shader)
                continue
            clean_mems = [mem.replace("_RIG_COLOR_TEMP", "") for mem in shader_mems]  # Clean off the temp name for EAV
            if clean_mems != shader_mems:
                self.temp_dupe_shapes += shader_mems
                info["members"] = clean_mems
                shader_mems = clean_mems
            for mem in shader_mems:
                shape_members.append(mem.split(".")[0])
        shape_members = list(set(shape_members))
        shape_members = i_utils.convert_data(shape_members, to_generic=False)
        # - Get transforms
        json_dict["shape_transforms"] = {}
        for shape in shape_members:
            if not isinstance(shape, (i_node.Node, i_node._Node)):
                self.log.warn("'%s' no longer exists. Cannot store as a shaded object." % shape)
                continue
            json_dict["shape_transforms"][shape] = shape.relatives(p=True)
        
        # Return
        return json_dict

    def write(self, meshes=None, **kwargs):
        """
        Write object data to a json file

        :param meshes: (list) - (optional) Objects to get information on
        :param kwargs: (dict) - Used in DataIO.write()

        :return: (str) - Path to the json file exported
        """
        # Get Json Values
        j_dict = self._get()
        raise_error = kwargs.get("raise_error", True)
        if not j_dict:
            i_utils.error("Could not find json information.", raise_err=raise_error, log=self.log)
            return 
        # curr_dict = DataIO.read(self, path=self.json_path, **kwargs)
        # new_dict = curr_dict.copy()
        # new_dict.update(j_dict)
        
        # Write
        DataIO.write(self, path=self.json_path, data=j_dict, **kwargs) # new_dict
        
        # Prompt to delete dupe group
        if self.temp_dupe_shapes:
            do_it = i_utils.message(title="Delete Dupes?", message="Delete the temp dupe geos?", button=["Yes", "No"])
            if do_it == "Yes":
                temp_shapes = i_utils.convert_data(self.temp_dupe_shapes, to_generic=False)
                temp_tfms = [shp.relatives(0, p=True) for shp in temp_shapes]
                i_utils.delete(temp_tfms)

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
        shape_transforms = json_info.get("shape_transforms")
        ent_name = os.environ.get("TT_ENTNAME")

        # Encountered some Texture publishing crashing in Maya when RMAN shaders were applied
        # to rigged meshes, so now applying a native standard lambert prior to per-face
        # shader assignments.
        self.set_base_shader_for_meshtone(json_info)

        # Set
        for shader in json_info.keys():
            self.log.debug('Applying MeshTone shader:', shader)
            # Check
            if shader == "shape_transforms":
                continue
            # Vars
            shader_info = json_info.get(shader).copy()
            # Update members to geo that exists
            mems = shader_info.get("members")
            if mems:
                existing_members = []
                for mem in mems:
                    # - Exists as-is
                    if i_utils.check_exists(mem):
                        existing_members.append(mem)
                    # - Exists with different namespace
                    elif ":" in mem:
                        existing_members += i_utils.ls("*:" + mem.split(":")[-1])
                    # - Exists with different shape name (not "Orig" or "Deformed")
                    elif "Shape" in mem:
                        tfm = shape_transforms.get(mem.split(".")[0])
                        if tfm and ":" in tfm:
                            tfm = i_utils.ls("*:" + tfm.split(":")[-1])
                            if len(tfm) > 1:  # Face rig also in scene, so same geo with multiple namespaces
                                tfm = [tf for tf in tfm if tf.split(":")[0].split(ent_name + "_")[1].isdigit()]
                            if len(tfm) == 1:
                                tfm = tfm[0]
                        if not tfm or not i_utils.check_exists(tfm):
                            continue
                        tfm = i_node.Node(tfm)
                        shps = tfm.relatives(s=True)
                        if not shps:
                            self.log.warn("'%s' has no shapes. Cannot get members." % tfm)
                            continue
                        shp = shps[-1]
                        if "." in mem:
                            shp += "." + mem.split(".")[-1]
                        existing_members.append(shp)
                    # - What to do
                    else:
                        self.log.info("Don't know what to do to find in-scene for: '%s'" % mem)
                if not existing_members:
                    self.log.warn("No existing in-scene members found for %s.\n- Looking for: %s" % (shader, ", ".join(i_utils.convert_data(mems))))
                shader_info["members"] = existing_members
            # Create
            tex_utils.create_shader_from_info(shader_name=shader, shader_info=shader_info)
        self.log.debug('Completed setting MeshTone from data exported from Rig step.')

    def set_base_shader_for_meshtone(self, json_info):
        member_list = list()
        for shader, shader_info in json_info.items():
            member_list.extend(shader_info.get('members', list()))

        if member_list:
            tex_utils.apply_base_shader(shader_name='rigProxy_SHDR', geo=member_list, log=self.log)

    def read(self, set=False, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.

        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param kwargs: (dict) - Used in DataIO.read()

        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read Json Values
        ret_dict = DataIO.read(self, path=self.json_path, **kwargs)
        if not ret_dict:
            return None
        
        # Set Values in Scene?
        if set:
            self._set(json_info=ret_dict)

        # Verbose
        self._message(action="import", set=set, successes=ret_dict.keys())

        # Return
        return ret_dict


def mesh_tone_for_sfn():
    """
    Export rig shaders for shot finaling.
    Wrapper for both the legacy and non-legacy process
    
    :return: (bool) - True/False for success
    """
    if not i_utils.is_legacy:  # Legacy pipe doesn't have these files
        try:
            from taskmaster.pub_tasks.asset.rig import proxy_shader_export
            proxy_exp = proxy_shader_export.ExportProxyShaders()
            proxy_exp.run()
        except Exception as e:
            i_utils.error("Could not export SFN Shaders. Error: %s" % e, raise_err=False)
            return False
    
    else:  # This is where Legacy has its files -- same as wrs.RigShader()
        try:
            import rig_shaders
            rig_shaders.write_network()
        except Exception as e:
            i_utils.error("Could not export SFN Shaders. Error: %s" % e, raise_err=False)
            return False
    
    return True  # Successful


def get_geo_helpers(geo_helpers=None, raise_error=True):
    """
    Get the rig's geo helpers
    
    :param geo_helpers: (list, iNode) - (optional) Items to check if geo helpers. If not defined, finds all in scene
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (list of iNodes) - Objects that are confirmed geo helpers
    """
    # None given. Find them all
    if not geo_helpers:
        geo_helpers = i_utils.ls("*Helper_Geo")
        if not geo_helpers:
            geo_helper_grp = i_utils.ls("Helper_Grp")
            if geo_helper_grp:
                geo_helpers = geo_helper_grp[0].relatives(c=True)
        if not geo_helpers:
            if raise_error:
                i_utils.error("Nothing given and found nothing named '*Helper_Geo'.", dialog=True)
            return

    # Convert to list
    if not isinstance(geo_helpers, (list, tuple)):
        geo_helpers = [geo_helpers]

    # Check if the given are real helper geos
    confirmed_helpers = []
    for geo in geo_helpers:
        # - Naming / Hierarchy convention?
        if not geo.endswith("Helper_Geo") and "Helper_Grp" not in geo.name_long():
            continue
        # - Is Geo?
        if geo.node_type() == "mesh" or (geo.node_type() == "transform" and geo.relatives(s=True, type="mesh")):
            confirmed_helpers.append(geo)

    # Return
    return confirmed_helpers


def swap_helpers(geo_helpers=None):
    """
    Swap multiple geo helpers from polys to nurbsSurfaces. This is for backwards compatibility of updating legacy rigs.
    
    :param geo_helpers: (list, iNode) - (optional) Items to check if geo helpers. If not defined, finds all in scene
    
    :return: None
    """
    # Find helper geos
    geo_helpers = get_geo_helpers(geo_helpers)
    if not geo_helpers:
        return

    # Swap
    successes = []
    RIG_LOG.info("Swapping geo helpers:", geo_helpers)
    for geo_helper in geo_helpers:
        nurbs_helper = swap_helper(geo_helper=geo_helper)
        if nurbs_helper:
            successes.append(nurbs_helper.name)

    # Clear selection
    i_utils.select(cl=True)

    # Tell user successes
    if successes:
        i_utils.message(title="Helper Geo Swapped", button=["Ok"],
                         message="Swapped geos for nurbsSurfaces:\n\n" + "\n".join(successes))
    else:
        i_utils.message(title="Helper Geo Swapped", button=["Ok"],
                         message="Found no poly helper geos to swap.")


def swap_helpers_sel():
    """
    Selection wrapper for swap_helpers()
    :return: None
    """
    helper_geo = i_utils.check_sel(raise_error=False, dialog_error=False)
    swap_helpers(geo_helpers=helper_geo)


def swap_helper(geo_helper=None, raise_error=True):
    """
    Swap one geo helper from poly type to nurbsSurface
    
    :param geo_helper: (iNode) - The geo helper
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (iNode, bool) - New geo or False if failed to convert
    """
    # Temp function to swap a poly "Helper_Geo" for a nurbs version.
    # Is this already nurbs?
    if geo_helper.relatives(s=True, type="nurbsSurface"):
        i_utils.error(geo_helper + " is already a nurbsSurface.", raise_err=raise_error)
        return False
    
    # Find the easy info
    name = geo_helper + "_NEW"
    parent = geo_helper
    par = geo_helper.relatives(0, p=True)
    if par:
        parent = par
    vis_driven = parent or geo_helper
    vis_driver = vis_driven.v.connections(d=False) or None
    if vis_driver:
        vis_driver = vis_driver[0]
    driver = geo_helper.relatives(type="parentConstraint")
    if driver:
        driver = driver[0].attr("target[0].targetTranslate").connections(d=False)[0]
    do_scale_cns = geo_helper.relatives(type="scaleConstraint")
    
    # Find the scale
    # :note: The geo would have been frozen, so need to do a slightly complex route
    # - Scale X
    sx_x1, sx_y1, sx_z1 = geo_helper.attr("vtx[3]").xform(q=True, os=True, t=True)
    sx_x2, sx_y2, sx_z2 = geo_helper.attr("vtx[2]").xform(q=True, os=True, t=True)
    sx_dist = math.hypot(sx_x2 - sx_x1, sx_y2 - sx_y1)
    # - Scale Y
    sy_x1, sy_y1, sy_z1 = geo_helper.attr("vtx[3]").xform(q=True, os=True, t=True)
    sy_x2, sy_y2, sy_z2 = geo_helper.attr("vtx[1]").xform(q=True, os=True, t=True)
    sy_dist = math.hypot(sy_x2 - sy_x1, sy_y2 - sy_y1)
    # - Scale Z
    sz_x1, sz_y1, sz_z1 = geo_helper.attr("vtx[5]").xform(q=True, os=True, t=True)
    sz_x2, sz_y2, sz_z2 = geo_helper.attr("vtx[3]").xform(q=True, os=True, t=True)
    sz_dist = math.hypot(sz_z2 - sz_z1, sz_y2 - sz_y1)
    # - Combine
    scale_xyz = [sx_dist, sy_dist, sz_dist]
    
    # Create
    new_geo = create_helper(name=name, scale_xyz=scale_xyz, parent=parent, driver=driver, vis_driver=vis_driver,
                            scale_constrain=do_scale_cns, position_match=geo_helper)
    
    # Delete original
    geo_helper.delete()
    
    # Rename new geo
    new_geo.rename(new_geo.name.replace("_NEW", ""))
    
    # Return
    return new_geo


def create_helper(name=None, size=1, scale_xyz=None, parent=None, position_match=None, driver=None, vis_driver=None,
                  position_attrs=None, scale_constrain=True):
    """
    Create a helper geo (pink nurbsSurface cube, such as those under a biped's feet)
    
    :param name: (str) - Base name for created objects
    :param size: (int, float) - Initial width of the cube
    :param scale_xyz: (list of int/float) - (optional) Scale offset of the cube post-construction
    :param parent: (iNode) - (optional) Parent of the created geo
    :param position_match: (iNode) - (optional) Item to match position of created geo to
    :param driver: (iNode) - (optional) Constraint driver of created geo. If defined, parent constrains.
    :param vis_driver: (iNode) - (optional) Node to give an attribute driving visibility of created geo
    :param position_attrs: (str, list of str) - (optional) Attrs to use in position matching to :param position_match:
    :param scale_constrain: (bool) - Additionally scale constraint the :param driver: to created geo?
    
    :return: (iNode) - Created helper geo
    """
    # Create
    # :note: Don't use the ratio attrs because it's hard to figure out the right height/length to give.
    if not name.endswith("_"):
        name += "_"
    name = name.replace("_Helper_Geo", "")  # Just in case it was provided with that
    helper_geo = i_node.create("nurbsCube", n=name + "Helper_Geo", w=size, ch=False)
    i_utils.select(cl=True)
    
    # Consolidate shapes
    helper_shps = []
    children = helper_geo.relatives(c=True, type="transform")
    for ch in children:
        helper_shps += ch.relatives(s=True)
    i_utils.parent(helper_shps, helper_geo, r=True, s=True)
    i_utils.delete(children)
    helper_shps = helper_geo.relatives(s=True)

    # Position
    if position_match:
        if not position_attrs:
            position_attrs = "t"
        i_node.copy_pose(driver=position_match, driven=helper_geo, attrs=position_attrs)

    # Pivot at top of geo. Hacky but doing clean using the cvs doesn't work.
    # - Position below grid
    helper_geo.ty.set(float(size) * -0.5)
    # - Pivots at origin
    helper_geo.xform(pivots=[0, -1 * helper_geo.ty.get(), 0])
    # - Freeze so position matching works
    helper_geo.freeze(apply=True)

    # Scale
    if scale_xyz:
        helper_geo_cvs = helper_geo.get_cvs()
        i_utils.xform(helper_geo_cvs, scale_xyz, as_fn="scale")

    # Turn off render attrs
    render_attrs = ["castsShadows", "receiveShadows", "holdOut", "motionBlur", "primaryVisibility", "smoothShading", 
                    "visibleInReflections", "visibleInRefractions", "doubleSided", "opposite"]
    for helper_shp in helper_geo.relatives(s=True):
        for ren_attr in render_attrs:
            if not i_utils.check_exists(helper_shp + "." + ren_attr):  # non-2017 doesn't have these all
                continue
            helper_shp.attr(ren_attr).set(0)

    # Parent
    driven = parent or helper_geo
    if parent:
        helper_geo.set_parent(parent)

    # Create / Find Shader
    shader = tex_utils.apply_shader(shader_name='Contact_Helper_Shdr', rgb=[1, 0, 1], geo=helper_geo.name, shader_type='surfaceShader')
    shader.outTransparency.set([0.5, 0.5, 0.5])
    helper_geo.overrideEnabled.set(1)
    helper_geo.overrideDisplayType.set(2)
    
    # Add Vis Attr
    if vis_driver:
        vis_attr = i_attr.create_vis_attr(node=vis_driver, drive=driven, ln="PinkHelper")
        # - Connect attr to hideOnPlayback
        if i_utils.is_2017:
            vis_attr.drive(helper_geo.overridePlayback)
            for shp in helper_shps:
                vis_attr.drive(shp.hideOnPlayback)
    
    # Lock and Hide
    if parent:
        i_attr.lock_and_hide(parent, attrs="all", lock=True)
    
    # Constrain
    if driver:
        i_constraint.constrain(driver, helper_geo, mo=True, as_fn="parent")
        if scale_constrain:
            i_constraint.constrain(driver, helper_geo, mo=True, as_fn="scale")
    
    # Return
    return helper_geo


def create_helper_sel():
    """
    Selection wrapper for create_helper()
    
    Select the vis driver. Name will be given via a prompt and the created geo will be driven by a created locator.
    
    :return: None
    """
    # Selection
    sel = i_utils.check_sel()
    if not sel:
        return
    vis_driver = sel[0]

    # Name prompt
    name = i_utils.name_prompt(title="Helper Geo", default="HelpMe")
    if not name:
        return

    # Create a locator that will drive the helper
    loc = i_node.create("locator", n=name + "_Helper_LOC")
    i_node.copy_pose(driver=vis_driver, driven=loc)

    # Run
    create_helper(name=name, parent=loc, position_match=loc, driver=loc, vis_driver=vis_driver, position_attrs=["t", "r"])

    # Select
    i_utils.select(loc)


def reference_check(action):
    """
    For EAV, load or remove the "Elena_Scale_Ref.mb" file to check in-scene rig/model for scaling reference.
    
    :param action: (str) - Action to do with the mb file. Accepts: "load", "remove".
    
    :return: None
    """
    # Get path
    pth = None
    proj = os.environ.get("TT_PROJCODE")
    if i_utils.is_eav:
        pth = "Y:/EAV/assets/type/Character/elena_v2/elems/Rigging/Scale_Ref/Elena_Scale_Ref.mb"

    # Check path
    if not pth:
        i_utils.error("Cannot find path to object for show '%s'" % proj)

    # Do it
    if action == "load":
        cmds.file(pth, reference=True)
    elif action == "remove":
        cmds.file(pth, removeReference=True)
    else:
        i_utils.error("Action must be 'load' or 'remove'. Given: %s" % action)


def proxy_eyes_eav(dialog_error=False):
    """
    Create EAV-specific proxy eyes
    
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: None
    """
    # Vars
    eye_group = "MTM_eyes"
    proxy_eyes = "Proxy_Eyes"

    # Check
    if not i_utils.check_exists(eye_group):
        i_utils.error("Wrong Eye group name.\n\nChange to '%s' and try again." % eye_group, dialog=dialog_error)
        return
    else:
        eye_group = i_node.Node(eye_group)
    if not i_utils.check_exists(proxy_eyes):
        i_utils.error("Proxy Eyes ('%s') not in scene." % proxy_eyes, dialog=dialog_error)
        return
    elif len(i_utils.ls(proxy_eyes)) > 1:
        i_utils.error("More than one object: '%s' in scene. Cannot determine what to do." % proxy_eyes, dialog=dialog_error)
        return
    else:
        proxy_eyes = i_node.Node(proxy_eyes)

    # More Vars
    eye_control = i_node.Node("Eye_Root_Ctrl")
    dfm_flare = i_node.Node("Head_A_Flare")
    dfm_twist = i_node.Node("Head_B_Twist")
    dfn_wire = i_node.Node("Head_C_Wire")

    # Add Attrs
    vis_attr = i_attr.create_vis_attr(node=eye_control, ln="Proxy", as_enum=True, drive=proxy_eyes)
    acc_attr = i_attr.create(node=eye_control, ln="Proxy_Accuracy", k=True, at="enum", en="Low:High:")

    # Create Reverses
    vis_rev = i_node.create("reverse", name="Proxy_Vis_Rev")
    acc_rev = i_node.create("reverse", name="Proxy_Accuracy_Rev")

    # Connect Attrs
    # - Vis
    vis_attr.drive(vis_rev.inputX)
    vis_rev.outputX.drive(eye_group.v, f=True)
    # - Accuracy
    acc_attr.drive(acc_rev.inputX)

    # Loop left and right
    for side in ["L", "R"]:
        # - Vars
        try:
            low_geo = [i_node.Node(side + geo) for geo in ["_Proxy_Eyeball", "_Proxy_Low_Iris", "_Proxy_Low_Pupil"]]
            high_geo = [i_node.Node(side + geo) for geo in ["_Proxy_High_Pupil", "_Proxy_High_Iris"]]
            acc_high_grp = i_node.Node(side + "_Eye_High_Accuracy_Grp")
            acc_low_grp = i_node.Node(side + "_Eye_Low_Accuracy_Grp")
            bnd_joint = i_node.Node(side + "_Eye_Bnd")
            pin_joint = i_node.Node(side + "_Eye_Pin_Jnt")
            pin_foll = i_node.Node(side + "_Eye_Pin_Flc")
            proj_grp = i_node.Node("eye_projections_%s_grp" % side)
        except RuntimeError as e:
            if str(e).endswith("does not exist"):
                i_utils.error(e, dialog=dialog_error)
                return
            i_utils.error(e)
        
        # - Accuracy
        acc_attr.drive(acc_high_grp.v)
        acc_rev.outputX.drive(acc_low_grp.v)

        # - Skin
        i_node.create("skinCluster", low_geo, bnd_joint, tsb=True)
        i_node.create("skinCluster", high_geo, pin_joint, tsb=True)

        # - Constrain
        i_constraint.constrain(pin_foll, proj_grp, mo=True, as_fn="parent")
        i_constraint.constrain(pin_foll, proj_grp, mo=True, as_fn="scale")

        # - Squash
        for geo in low_geo:
            cmds.deformer(dfm_flare.name, e=True, g=geo.name)
            cmds.deformer(dfm_twist.name, e=True, g=geo.name)
            cmds.deformer(dfn_wire.name, e=True, g=geo.name)

    # Parent
    i_utils.parent("Eye_Flc_Util_Grp", "Utility_Grp")
    i_utils.parent("Proxy_Eyes", "Character")


def proxy_eyes_smo(eyes=None, dialog_error=False):
    """
    Create EAV-specific proxy eyes
    
    :param eyes: (list of iNodes/str, iNode, str) - Eye geos to create proxy setup on
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: None
    """
    # Check for eyes
    if not eyes:
        eyes = i_utils.check_sel()
        if not eyes:
            return
        # - Clear selection
        i_utils.select(cl=True)

    # Create eye groups
    eye_grp = i_node.create("group", eyes, n="Eye_Geo_Grp", r=True, use_existing=True)
    if eye_grp.existed:
        i_utils.error("SMO Eye proxy already in scene.", dialog=dialog_error)
        return
    proxy_eyes = i_node.duplicate(eye_grp, add_prefix="Proxy", renameChildren=True)
    proxy_eye_grp = proxy_eyes[0]

    # Get shaders
    export_data = i_node.Node("ExportData")
    export_data_chldn = export_data.relatives(c=True)
    eye_geos = eye_grp.relatives(c=True)
    proxy_eye_geos = proxy_eyes[1:]
    # - Get iris color to use
    iris_color_dict = {"blue": (0, 0.6, 0.85), "brown": (0.22, 0.1, 0), "green": (0, 0.675, 0), "gold": (0.65, 0.55, 0),
                       "purple": (0.35, 0.15, 0.65), "pink": (1, 0.25, 1)}
    iris_color = None
    for export_chld in export_data_chldn:
        for color in iris_color_dict.keys():
            if color in export_chld.name.lower():
                iris_color = color
                break
    iris_color_value = iris_color_dict.get(iris_color)
    if not iris_color_value:
        RIG_LOG.warn("No iris color found. Supported colors: %s" % sorted(iris_color_dict.keys()))

    # Add Proxy Attr
    eye_root_control = i_node.Node("Eye_Root_Ctrl")
    eye_root_res_attr = i_attr.create(node=eye_root_control, ln="Texture_Resolution", k=True, at="enum", en="Proxy:Texture", use_existing=True)

    # Dilate / Dialate
    dilate_name = "Dilate"
    if os.environ.get("TT_PROJCODE") in ["SMO", "EAV", "KNG"]:
        dilate_name = "Dialate"  # :note: Need to keep typo for consistency

    # Build on each side
    for side in ["L", "R"]:
        # - Add control attr
        aim_control = i_node.Node(side + "_Eye_Aim_Ctrl")
        control_dilate_attr = i_attr.create(aim_control, ln=dilate_name, k=True, at="long", min=0, max=100, dv=50)

        # - Place 2d
        placement_nd = i_node.create("place2dTexture", n=side + "_Eye_Proxy_2DPlace")
        placement_nd.wrapU.set(0)
        placement_nd.wrapV.set(0)

        # - Ramp
        ramp_nd = i_node.create("ramp", n=side + "_Eye_Ramp")
        ramp_nd.type.set(4)
        ramp_nd.interpolation.set(0)
        ramp_nd.attr("colorEntryList[1].position").set(0.305)
        # -- Color
        if iris_color_value:
            ramp_nd.attr("colorEntryList[1].color").set(iris_color_value)
        ramp_nd.attr("colorEntryList[2].position").set(0.647)
        ramp_nd.attr("colorEntryList[2].color").set([1, 1, 1])
        ramp_nd.attr("colorEntryList[3].position").set(0)
        ramp_nd.attr("colorEntryList[3].color").set([0, 0, 0])
        ramp_nd.defaultColor.set([1, 1, 1])
        # -- Add attrs
        ramp_ren_attr = i_attr.create_vis_attr(ramp_nd, ln="Render", as_enum=True, dv=0)
        ramp_dilate_attr = i_attr.create(ramp_nd, ln=dilate_name, k=True, at="long", min=0, max=100, dv=50)
        ramp_res_attr = i_attr.create(ramp_nd, ln="Texture_Resolution", k=False, cb=True, at="enum", en="Proxy:Texture")

        # - Remap
        remap_nd = i_node.create("remapValue", n=side + "_" + dilate_name + "_Ramp_Rmap")
        remap_nd.inputMax.set(100)
        remap_nd.outputMin.set(0.05)
        remap_nd.outputMax.set(0.56)

        # - UnitCon
        uttc_nd = i_node.create("unitToTimeConversion", n=side + "_EyeRamp_UC")
        uttc_nd.conversionFactor.set(250)

        # - Projection
        projection_nd = i_node.create("projection", n=side + "_Eye_Projection")

        # - Place 3d
        cube_prj_nd = i_node.create("place3dTexture", n=side + "_Eye_Projection_3DPlace")

        # - Anim Curves
        ramp_ac = i_node.create("animCurveTU", n=side + "_Eye_Ramp_Input_AnimCurve")
        ramp_ac.useCurveColor.set(1)
        ramp_ac.curveColor.set([1, 1, 0])
        proj_ac = i_node.create("animCurveTU", n=side + "_Eye_Projection_Resolution")
        proj_ac.useCurveColor.set(1)
        proj_ac.curveColor.set([0, 0, 0])

        side_shdr = tex_utils.create_shader(shader_name=side + "_Eye_Proxy_Shdr", shader_type="lambert", use_existing=True)
        side_shdr = i_node.Node(side_shdr)

        # - Key
        file_export_data = i_utils.ls(side + "_*_DIFF_CLR_file1_ExportData")
        if not file_export_data:
            i_utils.error("Nothing found with name '%s_*_DIFF_CLR_file1_ExportData'" % side, dialog=True)
            return
        file_export_data = file_export_data[0]
        frame_offset = file_export_data.frameOffset.get()
        for tv in [[0, 0], [50, frame_offset], [100, 100]]:
            ramp_ac.set_key(t=tv[0], v=tv[1], itt="linear", ott="linear")
        proj_ac.set_key(t=0, v=32, itt="auto", ott="step")
        proj_ac.set_key(t=1, v=64, itt="auto", ott="step")
        ramp_ac.key_tangent(e=True, wt=False)
        proj_ac.key_tangent(e=True, wt=False)

        # - Connect
        placement_nd.outUV.drive(ramp_nd.uvCoord)
        placement_nd.outUvFilterSize.drive(ramp_nd.uvFilterSize)
        remap_nd.outValue.drive(ramp_nd.attr("colorEntryList[1].position"))
        ramp_dilate_attr.drive(uttc_nd.input)
        ramp_nd.outColor.drive(projection_nd.image)
        cube_prj_nd.worldInverseMatrix[0].drive(projection_nd.placementMatrix)
        uttc_nd.output.drive(ramp_ac.input)
        ramp_ac.output.drive(remap_nd.inputValue)
        ramp_res_attr.drive(proj_ac.input)
        projection_nd.outColor.drive(side_shdr.color)
        control_dilate_attr.drive(ramp_dilate_attr)
        ramp_ac.output.drive(file_export_data.frameOffset)
        eye_root_res_attr.drive(ramp_res_attr)

        # - Drive Place nodes
        diff_placement_nds = i_utils.ls(side + "_*_DIFF_CLR_place3dTexture_ExportData")
        if diff_placement_nds:
            diff_place_nd = diff_placement_nds[0]
            for trs in ["t", "r", "s"]:
                for axis in ["x", "y", "z"]:
                    cube_prj_nd.attr(trs + axis).set(diff_place_nd.attr(trs + axis).get())
            i_constraint.constrain(cube_prj_nd, diff_place_nd, mo=True, as_fn="parent")

        # - Assign shaders
        side_geos = [geo.name for geo in eye_geos + proxy_eye_geos if geo.startswith("Proxy_" + side) or ":" + side + "_" in geo]
        tex_utils.apply_shader(shader_name=side_shdr.name, geo=side_geos)

    # Drive Proxy Vis
    proxy_vis_rev = i_node.create("reverse", n="Proxy_Vis_Reverse", use_existing=True)
    eye_root_res_attr.drive(eye_grp.v)
    eye_root_res_attr.drive(proxy_vis_rev.inputX)
    proxy_vis_rev.outputX.drive(proxy_eye_grp.v)

    # Clear selection
    i_utils.select(cl=True)

    # Bake Proxy Textures
    mel.eval("performSurfaceSampling 1;")
    mel.eval("surfaceSamplingChangeXResolutionChCmd 1024 0;")


def set_smooth():
    """
    Set the geo smoothing level to smooth. Uses selection.
    Migrated from legacy - SetSmooth()
    
    :return: None
    """
    # Get selected
    sel = i_utils.check_sel()
    if not sel:
        return

    # Get shapes
    shapes = []
    for obj in sel:
        shapes += obj.relatives(s=True, type="mesh")

    # Check
    if not shapes:
        i_utils.error("No mesh shapes found for selection.", dialog=True)
        return

    # Set attrs
    for shp in shapes:
        shp.displaySmoothMesh.set(l=False)
        shp.smoothLevel.set(3, f=True)
        shp.useSmoothPreviewForRender.set(0, f=True)
        shp.renderSmoothLevel.set(3, f=True)


def create_proxy_simple():
    """
    Create cylinder-based proxy geos and constrain to the rig joints
    Migrated from legacy AutoProxy()
    
    :return: None
    """
    # Check attr exists
    proxy_vis = i_utils.ls("*.ProxyVis")
    if not proxy_vis:
        i_utils.error("There is no ProxyVis attr on the rig. Cannot create proxy.", dialog=True)
        return
    proxy_vis = proxy_vis[0]

    # Vars
    import rig_tools.utils.joints as rig_joints  # :note: Need to import here. Top of module causes errors in SMO
    bind_joints = rig_joints.get_bind_joints()
    if not bind_joints:
        return
    # all_proxy_geo = []
    new_proxy_geo = []

    # Create geo
    for jnt in bind_joints:
        if jnt.endswith("End_Bnd"):  # Don't make a proxy for ends
            continue
        geo = i_node.create("polyCylinder", n=jnt.replace("_Bnd", "_PRX"), r=1, h=2, sx=10, sy=2, sz=1, ch=False, use_existing=True)
        # all_proxy_geo.append(geo)
        if not geo.existed:
            i_constraint.constrain(jnt, geo, as_fn="parent")
            i_constraint.constrain(jnt, geo, as_fn="scale")
            new_proxy_geo.append(geo)

    # Check if new geo made
    if not new_proxy_geo:
        RIG_LOG.warn("No new proxy geo made.")
        return

    # Turn on proxy vis
    proxy_vis.set(1)

    # Create / Get Proxy group
    proxy_grp = i_node.create("transform", n="PRX_GRP", p="LowRes_Geo_Grp", use_existing=True)
    i_utils.parent(new_proxy_geo, proxy_grp)

    # Create / Assign Shader
    rgb = [random.uniform(0.2, 1.0) for i in range(0, 3)]
    tex_utils.apply_shader(shader_name="PRX_Shdr", rgb=rgb, shader_type="lambert", geo=new_proxy_geo)

    # Lock and Hide
    for proxy in new_proxy_geo:
        i_attr.lock_and_hide(proxy, attrs="all", lock=True, hide=True)

    # Clear selection
    i_utils.select(cl=True)


def get_model_geo(obj_checking=None, raise_error=True):
    """
    Get the model geo version of given object, or all in-scene model geos
    
    :param obj_checking: (iNode) - (optional) Object getting the model equivalent of. If not specified, finds all model geos in scene.
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (list of iNodes, iNode, bool) - List of iNodes if no :param obj_checking:, iNode of found model geo equivalent, or False if failed
    """
    # Vars
    ns = "" if i_utils.is_eav else "*:"
    
    # Find all if none given to check
    if not obj_checking:
        all_meshes = i_utils.ls(ns + "*", type="mesh")
        all_model_geo = []
        for mesh in all_meshes:
            model_geo = check_is_model(mesh)
            if model_geo:
                all_model_geo.append(model_geo)
        return list(set(all_model_geo))
    
    # Already is scene model geo?
    if i_utils.check_exists(obj_checking, raise_error=False):  # Check for when setting (as opposed to getting)
        is_model = check_is_model(obj_checking=i_node.Node(obj_checking), raise_error=raise_error)
        if is_model:
            return i_node.Node(obj_checking)
    
    # Find all with object name
    all = i_utils.ls(ns + obj_checking, l=True)
    if not all:
        ns_msg = "(regardless of namespace) " if ns else ""
        i_utils.error("No object %snamed '%s'." % (ns_msg, obj_checking), raise_err=raise_error)
        return False

    # Only found one item and it is a model geo.
    if len(all) == 1 and check_is_model(all[0]):  # May have found matching name, but not model geo
        return i_node.Node(all[0])
    
    # EAV checks end
    if i_utils.is_eav:
        i_utils.error("Could not find model equivalent of '%s'." % obj_checking, raise_err=raise_error)
        return False

    # Filter out face rig geo, which have their skins referenced in
    rse = raise_error if len(all) == 1 else False  # use to give more specific error message about why failed
    all_filtered = [nd for nd in all if check_is_model(nd, raise_error=rse)]
    if not all_filtered:
        i_utils.error("No namespace model geos with name '%s' found.\nChecked: %s" % (obj_checking, all), raise_err=raise_error)
        return False
    elif len(all_filtered) == 1:
        return i_node.Node(all_filtered[0])
    else:
        i_utils.error("Multiple namespace model geos with name '%s' found: %s" % (obj_checking, ", ".join(i_utils.convert_data(all_filtered))), raise_err=raise_error)
        return False


def get_reference_mesh(imported_mesh=None, reference_meshes=None):
    """
    Get the matching reference node for an imported mesh
    
    :param imported_mesh: (str, iNode) - Imported mesh
    :param reference_meshes: (list of strs/iNodes) - Reference meshes checking
    
    :return: (iNode) - Reference mesh
    """
    imp_nodes = imported_mesh.split("|")
    RIG_LOG.debug("##VARCHECK imp_nodes: %s" % imp_nodes)

    for ref_mesh in reference_meshes:
        ref_nodes = [x.rsplit(":", 1)[-1] for x in ref_mesh.split("|")]
        RIG_LOG.debug("##VARCHECK ref_nodes: %s" % ref_nodes)

        for ref_nd in ref_nodes:
            if ref_nd in imp_nodes:
                RIG_LOG.debug("Found match: (Imported) '%s' > (Referenced) '%s'" % (imported_mesh, ref_mesh))
                return ref_mesh
        # if all(imp == ref for imp, ref in izip_longest(imp_nodes, ref_nodes)):   # Doesn't work if imp_nodes is non-unique
        #     RIG_LOG.debug("Found match: '%s' > '%s'" % (imported_mesh, ref_mesh))
        #     return ref_mesh

    # Failed to find
    i_utils.error("Could not find reference match for: '%s'." % imported_mesh, raise_err=False)


def swap_rig_mesh(source_mesh=None, target_mesh=None, dialog_error=False, raise_error=True):
    """
    Swap rig mesh from :param source_mesh: to :param target_mesh:.
    
    :param source_mesh: (iNode) - Source mesh. The geo that will replace :param target_mesh:
    :param target_mesh: (iNode) - Target mesh. The geo that will be replaced by :param source_mesh:
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (iNode) Updated target mesh
    """
    RIG_LOG.debug("Swapping '%s' > '%s'" % (source_mesh, target_mesh))

    # Gather source elements
    source_xform = source_mesh.relatives(0, p=True)
    source_xform_children = source_xform.relatives(c=True)
    source_xform_grp = source_xform.relatives(0, p=True)
    source_constraints = [chld for chld in source_xform_children if chld.node_type().endswith("Constraint")]
    source_orig_mesh_list = [mesh for mesh in source_xform_children if mesh.is_intermediate()]
    target_xform = target_mesh.relatives(0, p=True)
    target_deform_mesh = i_node.create("mesh", n=target_mesh.split(":")[-1] + "Deformed", parent=target_xform)

    RIG_LOG.debug("##VARCHECK source_mesh: %s" % source_mesh)
    RIG_LOG.debug("##VARCHECK source_xform: %s" % source_xform)
    RIG_LOG.debug("##VARCHECK source_xform_children: %s" % source_xform_children)
    RIG_LOG.debug("##VARCHECK source_xform_grp: %s" % source_xform_grp)
    RIG_LOG.debug("##VARCHECK source_constraints: %s" % source_constraints)
    RIG_LOG.debug("##VARCHECK source_orig_mesh_list: %s" % source_orig_mesh_list)
    RIG_LOG.debug("##VARCHECK target_mesh: %s" % target_mesh)
    RIG_LOG.debug("##VARCHECK target_xform: %s" % target_xform)
    RIG_LOG.debug("##VARCHECK target_deform_mesh: %s" % target_deform_mesh)
    
    # Constraints to delete and recreate?
    cns_infos = {}
    if source_constraints:
        for cns in source_constraints:
            cns_infos[cns] = cns.get_constraint_info()
        i_utils.delete(source_constraints)
    
    # Delete excess non-connected source shapes
    if len(source_orig_mesh_list) > 1:
        deletable_shapes = [shp for shp in source_orig_mesh_list if not shp.connections()]
        if deletable_shapes:
            RIG_LOG.warn("Deleting extra non-connected shapes: %s" % deletable_shapes)
            i_utils.delete(deletable_shapes)
        # - Redeclare and check
        source_orig_mesh_list = [mesh for mesh in source_xform_children if mesh.exists() and mesh.is_intermediate()]
        if len(source_orig_mesh_list) > 1:  # :TODO:
            vb = True if not raise_error and not dialog_error else False
            i_utils.error("Not set up to handle multiple input meshes just yet. (%s > %s)\n\nFound: %s" % 
                          (source_mesh, target_mesh, source_orig_mesh_list), raise_err=raise_error, dialog=dialog_error,
                          verbose=vb)
            return
        source_xform = source_orig_mesh_list[0].relatives(0, p=True)

    # Transfer orig connections
    if source_orig_mesh_list:
        source_orig_mesh = source_orig_mesh_list[0]
        RIG_LOG.debug("##VARCHECK source_orig_mesh: %s" % source_orig_mesh)
        RIG_LOG.debug("##VARCHECK target_mesh: %s" % target_mesh)
        maya_utils.transfer_connections(pm.PyNode(source_orig_mesh.name), pm.PyNode(target_mesh.name))

    # Transfer 'rigged' connections
    RIG_LOG.debug("##VARCHECK source_mesh: %s (%s)" % (source_mesh, type(source_mesh).__name__))
    RIG_LOG.debug("##VARCHECK target_deform_mesh: %s (%s)" % (target_deform_mesh, type(target_deform_mesh).__name__))
    maya_utils.transfer_connections(pm.PyNode(source_mesh), pm.PyNode(target_deform_mesh))

    # Transfer transform connections
    RIG_LOG.debug("##VARCHECK source_xform: %s" % source_xform)
    RIG_LOG.debug("##VARCHECK target_xform: %s" % target_xform)
    maya_utils.transfer_connections(pm.PyNode(source_xform), pm.PyNode(target_xform))

    # Cleanup
    target_mesh.set_intermediate(1)

    # try:
    target_xform.set_parent(source_xform_grp)
    # except RuntimeError:
    #     i_utils.error("Issue with re-parenting '%s'. Likely the target is a grouped reference object." % target_xform, raise_err=False)
    RIG_LOG.debug("Deleting: %s" % source_xform)
    source_xform.delete()
    
    # Re-constrain
    if source_constraints:
        for cns, info in cns_infos.items():
            i_constraint.constrain(constraint_info=info)
            # kws = {}
            # if info.type != "parentConstraint":
            #     for info_attr in ["offset"]:
            #         val = getattr(info, info_attr)
            #         if val:
            #             kws[info_attr] = val
            # cns = i_constraint.constrain(info.drivers, target_xform, mo=True, as_fn=info.type, **kws)
            # if info.type == "parentConstraint":
            #     cns.interpType.set(info.interpType)
    
    # Return
    return target_mesh


def import_to_reference(nodes=None, dialog_error=False, raise_error=True):
    """
    Finds matching referenced nodes and transfer connections from the imported 'deformed' meshes.
    Effectively replacing the imported geo with referenced geo.

    :param nodes: (list of iNodes) - Nodes to replace from their imported to their referenced version
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: 
    """
    # Check
    i_utils.check_arg(nodes, "nodes")

    # Get imported meshes from selected
    import_mesh_list = []
    for node_orig in nodes:
        # - Is this node unique in scene? Sometimes there are dupe geos in a rig of same name
        node_ls = i_utils.ls(node_orig.name_short(), referencedNodes=False)
        if len(node_ls) > 1:
            RIG_LOG.warn("'%s' is not unique. There are multiples found: %s" % (node_orig, node_ls))
        elif not node_ls:
            RIG_LOG.warn("'%s' does not exist (even the short name). Cannot swap import to reference." % node_orig)
            continue
        # - Loop all
        for node in node_ls:
            # - Is mesh?
            meshes = i_node.check_is_mesh(node)
            if not meshes:
                continue
            if not isinstance(meshes, (list, tuple)):
                meshes = [meshes]
            RIG_LOG.debug("'%s' has meshes: %s" % (node, meshes))
            for mesh in meshes:
                # - Is Arnold Stand-in?
                standins = i_utils.ls(mesh.relatives(siblings=True), dag=True, type="aiStandIn")
                if standins or "placement" in mesh.name.lower():
                    RIG_LOG.debug("-- '%s' is an arnold standin." % mesh)
                    continue
                # - Is intermediate or referenced?
                if mesh.is_intermediate() or mesh.is_referenced():
                    RIG_LOG.debug("-- '%s' is intermediate or referenced." % mesh)
                    continue
                # - Append
                RIG_LOG.debug("* '%s' is a valid mesh of transform: '%s'" % (mesh, node))
                import_mesh_list.append(mesh)
    import_mesh_list = list(reversed(import_mesh_list))
    if not import_mesh_list:
        i_utils.error("No imported meshes found from given nodes: %s" % nodes, dialog=dialog_error, raise_err=raise_error)
        return

    # Get all reference meshes in scene
    ref_mesh_list = [mesh for mesh in i_utils.ls(referencedNodes=True, type="mesh") if not mesh.is_intermediate()]
    if not ref_mesh_list:
        i_utils.error("No referenced meshes found in scene to target.", dialog=dialog_error, raise_err=raise_error)
        return

    # Verbose
    RIG_LOG.debug("##VARCHECK import_mesh_list: %s" % import_mesh_list)
    RIG_LOG.debug("##VARCHECK ref_mesh_list: %s" % ref_mesh_list)

    # Transfer meshes
    result_tfms = []
    failed_tfr = []
    for import_mesh in import_mesh_list:
        # - Get matching reference node
        ref_mesh = get_reference_mesh(import_mesh, ref_mesh_list)
        if not ref_mesh:
            continue
        
        # - Stupid check if exists. Why sometimes doesn't?? ugh.
        if not import_mesh.exists():
            RIG_LOG.debug("'%s' no longer exists. Not transferring to '%s'." % (import_mesh, ref_mesh))
            continue
        elif not ref_mesh.exists():
            RIG_LOG.debug("'%s' no longer exists. Not transferring from '%s'." % (ref_mesh, import_mesh))
            continue

        # - Verbose
        RIG_LOG.debug("Retargetting '%s' to '%s'." % (import_mesh, ref_mesh))

        # - Swap
        import_mesh = i_node.check_is_mesh(import_mesh)
        ref_mesh = i_node.check_is_mesh(ref_mesh)
        result_mesh = swap_rig_mesh(import_mesh, ref_mesh, dialog_error=False, raise_error=False)
        if not result_mesh:
            failed_tfr.append([import_mesh, ref_mesh])
            continue
        result_tfm = result_mesh.relatives(0, p=True)
        result_tfms.append(result_tfm)
    
    # Errors?
    if failed_tfr and dialog_error:
        i_utils.error("Failed to transfer some meshes. See script editor for details:\n\n%s" % failed_tfr, dialog=True)
    
    # Return
    return result_tfms


def import_to_reference_sel():
    """
    Selection wrapper for import_to_reference()
    Also runs fix_deform_shape_name() on selection to avoid errors.
    :return: None
    """
    # Check is EAV
    if i_utils.is_eav:
        i_utils.error('EAV cannot run this functionality', dialog=True)
        return
    
    # Get selection
    sel = i_utils.check_sel(dialog_error=True)
    if not sel:
        return

    # Fix shape names
    i_deformer.fix_deform_shape_name(objects=sel, include_hierarchy=False)

    # Import to reference
    results = import_to_reference(nodes=sel, dialog_error=True)
    
    # Re-Select
    if results:
        i_utils.select(results)

