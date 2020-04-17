import os

import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
import rig_tools.utils.nodes as rig_nodes
from rig_tools.utils.io import DataIO

project = os.environ.get("TT_PROJCODE")
# :note: Temporarily projects have different control structures. Until info node used in all rigs, using additional
# conditions to do things like check if an object is a control and to get all controls for a character / scene.


def create_bendy_control_chain(from_joint=None, to_joint=None, base_name=None, scale=1, ikfk_extra=False,
                               with_bendy=True, ends_color="red", bendy_color="watermelon", mid_color="yellow",
                               ikfk_control=None):
    """
    Create a bendy control chain
    
    :param from_joint: (iNode) - Starting joint of the chain
    :param to_joint: (iNode) - Ending joint of the chain
    :param base_name: (str) - Base name to use in created nodes
    :param scale: (int, float) - Main control size (other created controls calculated based on this)
    :param ikfk_extra: (bool) - If true, create "Ik_Xtra" and "Fk_Xtra" groups. If false, only create "Xtra" group.
    :param with_bendy: (bool) - Create a "bendy" control as opposed to just a Start/Mid/End control setup?
    :param ends_color: (str, int) - (optional) Color of the "End" control
    :param bendy_color: (str, int) - (optional) Color of the "Bendy" control
    :param mid_color: (str, int) - (optional) Color of the "Mid" control
    :param ikfk_control: (iNode) - (optional) Control used to drive the Bendy setup controls' visibility
    
    :return: (dict) Created controls.
    - "top" : (iControl) - "Start" control
    - "mid" : (iControl) - "Mid" control
    - "end" : (iControl) - "End" control
    - "bendy" : (iControl) - "Bendy" control
    """
    def extra_joint(position_joint=None, ctrl=None):
        """
        Create an extra joint in the structure
        
        :param position_joint: (iNode) - Joint that has the position to match new joint to
        :param ctrl: (iControl) - Control class that will have the joint added to
        
        :return: None. Created items are added as attrs on the ctrl object itself.
        - "xtra_jnt" : (iNode) - The created joint
        - "jnt_cns" : (iNode) - The "Cns" offset group above the joint
        - "jnt_off" : (iNode) - The "Offste" offset group above the "Cns" group
        """
        # Extra joint
        i_utils.select(cl=True)
        xtra_jnt = i_node.create("joint", n=ctrl.control.replace("_Ctrl", "_Jnt"))
        xtra_jnt.radius.set(position_joint.radius.get() / 2)
        xtra_jnt.set_parent(ctrl.control)
        xtra_jnt.zero_out()
        jnt_cns = xtra_jnt.create_zeroed_group(group_name=xtra_jnt + "_Cns")
        jnt_off = jnt_cns.create_zeroed_group(group_name=xtra_jnt + "_Offset")
        
        # Update ctrl
        setattr(ctrl, "xtra_jnt", xtra_jnt)
        setattr(ctrl, "jnt_cns", jnt_cns)
        setattr(ctrl, "jnt_off", jnt_off)

    # Vars
    controls = {}
    if base_name.endswith("_"):
        base_name = base_name[:-1]

    # Top Joint control
    top_additional_grps = ["Xtra", "Aim"] if not ikfk_extra else ["Ik_Xtra", "Fk_Xtra", "Aim"]
    top_ctrl = i_node.create("control", control_type="3D Hemisphere", name=base_name + "_Start", color=ends_color,
                             with_gimbal=False, promote_rotate_order=False, size=scale / 3, position_match=from_joint,
                             additional_groups=top_additional_grps)  # match_rotation=False, 
    extra_joint(position_joint=from_joint, ctrl=top_ctrl)
    controls["top"] = top_ctrl

    # Mid Joint control
    pos = [from_joint, to_joint]
    mid_ctrl = i_node.create("control", control_type="2D Circle", name=base_name + "_Mid", color=mid_color, with_gimbal=False,
                             promote_rotate_order=False, size=scale / 4, match_rotation=False, additional_groups=["Xtra"])
    controls["mid"] = mid_ctrl
    avg_pos = i_utils.get_average_position(from_node=pos[0], to_node=pos[1])
    mid_ctrl.top_tfm.xform(t=avg_pos, ws=True)
    i_node.copy_pose(driver=pos[0], driven=mid_ctrl.top_tfm, attrs="r")

    # End Joint control
    end_ctrl = i_node.create("control", control_type="3D Hemisphere", name=base_name + "_End", color=ends_color,
                             with_gimbal=False, promote_rotate_order=False, size=scale / 3, position_match=to_joint,
                             match_rotation=False, additional_groups=["Xtra", "Aim"])
    i_node.copy_pose(driver=top_ctrl.top_tfm, driven=end_ctrl.top_tfm, attrs="r")
    extra_joint(position_joint=to_joint, ctrl=end_ctrl)
    controls["end"] = end_ctrl

    # End Bendy
    bendy_ctrl = None
    if with_bendy:
        bendy_ctrl = i_node.create("control", control_type="2D Twist Cuff", name=base_name + "_Bendy", color=bendy_color,
                                   with_gimbal=False, promote_rotate_order=False, lock_hide_attrs=["r", "v"],
                                   size=scale / 2, position_match=to_joint,
                                   match_rotation=False, additional_groups=["Xtra", "Aim"])
        i_node.copy_pose(driver=from_joint, driven=bendy_ctrl.top_tfm, attrs="r")
    controls["bendy"] = bendy_ctrl

    # Drive Visibility
    if ikfk_control:
        i_attr.create_vis_attr(node=ikfk_control, ln="BendyTweak", drive=[top_ctrl.control, end_ctrl.control],
                               use_existing=True)

    # Return
    return controls


class CurvesIO(DataIO):
    """Import/Export class for Curves"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="curves_data.json", **kwargs)

    def _get_objects(self, objects=None):
        """
        Get the objects to use

        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection. 
        If no selection, uses all nurbsCurves in scene.

        :return: (list) Objects
        """
        import rig_tools.frankenstein.utils as rig_frankenstein_utils  # Must import here
        
        # Get all objects to check
        given_objs = objects
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)
        if not objects:
            objects = []
            all_scene_objects = sel or i_utils.ls(type="nurbsCurve")
            for obj in all_scene_objects:
                if obj.relatives(s=True, type="nurbsCurve"):
                    objects.append(obj)
                elif obj.node_type() == "nurbsCurve":
                    objects.append(obj.relatives(0, p=True))
        
        # Filter out objects based on misc factors
        clean_curves = []
        if objects:
            for crv in objects:
                if crv.is_referenced() or ":" in crv:
                    continue
                if i_control.check_is_control(crv, raise_error=False):
                    continue
                clean_curves.append(crv)

        # Get pack-related objects so know to not record those
        if given_objs or sel and len(clean_curves) < 20:  # Able to use faster way than getting all scene pack things
            ret_objects = [crv for crv in clean_curves if not rig_frankenstein_utils.get_packs_from_objs(pack_items=[crv])]
        # - Easier to get all scene pack objects if no selection or defined objects
        else:
            scene_pack_info_nodes = rig_frankenstein_utils.get_scene_packs()
            scene_pack_objs = [rig_frankenstein_utils.get_pack_object(pin) for pin in scene_pack_info_nodes]
            all_pack_curves = []
            for pack_obj in scene_pack_objs:
                for nd in pack_obj.created_nodes:
                    if not i_utils.check_exists(nd):  # :note: Temp backwards compatibility pre-unique id fixes
                        continue
                    nd = i_node.Node(nd)  # :note: Temp backwards compatibility force Node() wrap
                    if nd.relatives(s=True, type="nurbsCurve"):
                        all_pack_curves.append(nd)
                    elif nd.node_type() == "nurbsCurve":
                        all_pack_curves.append(nd.relatives(0, p=True))
            ret_objects = [crv for crv in clean_curves if crv not in all_pack_curves]
        
        # Return
        if not ret_objects:
            self.log.warn("All curves found are associated with a pack and will not be recorded")
        
        return list(set(ret_objects))

    def _get(self, curves=None, raise_error=True):
        """
        Get the data of objects to store

        :param curves: (list) - Objects to get information on
        :param raise_error: (bool) - Intentionally raise error if any operations fail?

        :return: (dict) Json Dict of data to store
        """
        # Check
        if not i_utils.check_arg(curves, "curves", raise_error=raise_error):
            return
        
        import rig_tools.frankenstein.utils as rig_frankenstein_utils

        # Create dictionary
        json_dict = {}
        for crv in curves:
            # Prep
            json_dict[crv] = {}
            # Get
            shapes = crv.relatives(s=True)
            if not shapes:
                self.log.warn("'%s' has no shapes." % crv)
            raw_shape_info = i_control.get_curve_info(crvs=shapes)
            # Convert shape info keys so json doesn't fail
            json_dict[crv]["shape_info"] = {}
            for shape_name, info in raw_shape_info.items():
                json_dict[crv]["shape_info"][shape_name.name_short()] = info
            # - Transform-based shape type? (as opposed to shape-based)
            json_dict[crv]["shape_type"] = i_control.get_curve_type(control=crv, raise_error=False) # :note: Used only for controls
            # Must this be built with a pack?
            is_from_build = bool(rig_frankenstein_utils.get_packs_from_objs(pack_items=[crv]))
            json_dict[crv]["from_build"] = is_from_build
            # Transform Info
            transform_info = {}
            if not is_from_build:
                transform_info = {"t" : [round(i, 4) for i in crv.xform(q=True, t=True, ws=True)], 
                                  "r" : [round(i, 4) for i in crv.r.get()], 
                                  "s" : [round(i, 4) for i in crv.s.get()], 
                                  "rp" : [round(i, 4) for i in crv.xform(q=True, rp=True, ws=True)],
                                  "sp": [round(i, 4) for i in crv.xform(q=True, sp=True, ws=True)],
                                  "rotateOrder": crv.rotateOrder.get(),
                                  "parent" : crv.relatives(0, p=True),
                                  }
            json_dict[crv]["transform_info"] = transform_info

        # Return
        return json_dict

    def write(self, curves=None, color=True, shape=True, raise_error=True, **kwargs):
        """
        Write object data to a json file

        :param curves: (list) - (optional) Objects to get information on
        :param color: (bool) - Get the color information?
        :param shape: (bool) - Get the shape information?
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Used in DataIO.write()

        :return: (str) - Path to the json file exported
        """
        # Check
        curves = self._get_objects(curves)
        if not i_utils.check_arg(curves, "curves", exists=True, raise_error=raise_error):
            return

        # Get Json Values
        j_dict = self._get(curves=curves, raise_error=raise_error)
        if not j_dict:
            i_utils.error("Could not find json information.", log=self.log, raise_err=raise_error)
            return
        self.log.debug("##VARCHECK json_path", self.json_path)
        curr_dict = DataIO.read(self, path=self.json_path, raise_error=False)  # **kwargs not included. Need raise_error False
        new_dict = curr_dict.copy()
        new_dict.update(j_dict)

        # Consolidate
        if not (color and shape):
            if curr_dict:
                # Override curr_dict with j_dict items
                for crv in curr_dict.keys():
                    if not curr_dict.get(crv):
                        continue
                    # new_dict[crv] = curr_dict[crv]
                    for crv_shp in curr_dict.get(crv).get("shape_info").keys():
                        if not j_dict.get(crv):  # Control used to exist, now it doesn't
                            continue
                        if color:
                            new_dict[crv]["shape_info"][crv_shp]["color"] = j_dict.get(crv).get("shape_info").get(crv_shp).get("color")
                        if shape:
                            new_dict[crv]["shape_info"][crv_shp] = j_dict.get(crv).get("shape_info").get(crv_shp)
                            # :note: it's easier to do this than hardcode all the other shape keys
                            new_dict[crv]["shape_info"][crv_shp]["color"] = curr_dict.get(crv).get("shape_info").get(crv_shp).get("color")

        # Write
        DataIO.write(self, path=self.json_path, data=new_dict, verbose_nodes=curves, **kwargs)

        # Return
        return self.json_path

    def _set(self, json_info=None, color=True, shape=True, raise_error=True):
        """
        Set in-scene objects based on json info

        :param json_info: (dict) - Information from the json file (based on _get())
        :param color: (bool) - Set the color information?
        :param shape: (bool) - Set the shape information?
        :param raise_error: (bool) - Intentionally raise error if any operations fail?

        :return: None
        """
        # Check
        if not i_utils.check_arg(json_info, "json info", raise_error=raise_error):
            return
        
        watson_show = os.environ.get("TT_PROJCODE") in ["SMO", "EAV"]
        # :TODO: Better method to figure out if it's a Watson control, which means it's not from Frankenstein build but
        # it also shouldn't have the transform created if it does not exist

        # Set
        for crv in json_info.keys():
            set_transform = False
            set_shapes = False
            crv_exists = i_utils.check_exists(crv)
            
            # Curve Does not already exist
            if not crv_exists:
                # - Only create if control is not from a build
                set_transform = True
                crv_info = json_info.get(crv)
                from_build = crv_info.get("from_build", True)  # :note: Default true for backwards compatibility when only supported build controls
                if from_build:
                    self.log.warn("'%s' does not exist, but was stored as being from a Frankenstein build. Cannot create." % crv)
                    continue
                elif watson_show:
                    self.log.warn("'%s' does not exist, but the show is Watson-based, so out of safety - not creating." % crv)
                    continue
                else:
                    self.log.warn("'%s' does not exist. Creating." % crv)
                # - Create
                shape_info = crv_info.get("shape_info")
                stored_shapes = sorted(shape_info.keys())
                stored_shape_type = crv_info.get("shape_type")
                # - Using a transform-based shape type
                if stored_shape_type:
                    crv = i_node.create("curve", name=crv, control_type=stored_shape_type)
                    set_shapes = True
                # - Made outside of Create Control types
                else:
                    # - Create the transform
                    crv = i_node.create("transform", name=crv)
                    # - Create the shapes
                    crv_shapes = []
                    for stored_shape in stored_shapes:
                        # -- Vars
                        stored_shape_info = shape_info.get(stored_shape)
                        crv_create_info = {}
                        for shape_k in ["color", "spans", "form", "degree", "closed"]:
                            crv_create_info[shape_k] = stored_shape_info.get(shape_k)
                        crv_create_info["points"] = stored_shape_info.get("points_local")
                        crv_create_info["control_type"] = stored_shape_info.get("shape_type")
                        shp = i_node.create("curve", name=stored_shape, control_tfm=crv, **crv_create_info)
                        crv_shapes.append(shp)
            
            # Curve exists
            else:
                # - Use existing
                crv = i_node.Node(crv)
                crv_info = json_info.get(crv.name_short()) or json_info.get(crv.name)
                if not crv_info:
                    self.log.warn("Could not find stored info for %s." % crv)
                    continue
                shape_info = crv_info.get("shape_info")
                stored_shape_type = crv_info.get("shape_type")
                stored_shapes = sorted(shape_info.keys())
                from_build = crv_info.get("from_build", True)  # :note: Default true for backwards compatibility when only supported build controls
                if not (from_build or watson_show):
                    set_transform = True
                # - Check - in-scene is same as stored
                current_shapes = sorted(crv.relatives(s=True))
                current_shape_type = i_control.get_curve_type(control=crv, raise_error=False)
                if stored_shape_type and stored_shape_type == current_shape_type:
                    set_shapes = True
                elif not stored_shape_type or stored_shape_type != current_shape_type:
                    if len(current_shapes) == len(stored_shapes):
                        for i in range(len(stored_shapes)):
                            stored_shape_points = shape_info.get(stored_shapes[i]).get("points")
                            current_shape_points = current_shapes[i].get_cvs()
                            if len(stored_shape_points) == len(current_shape_points):
                                set_shapes = True
                            else:
                                set_shapes = False
                if not set_shapes:
                    self.log.warn("%s's current shape type (%s) or number of shapes / cvs does not match "
                                 "stored type (%s)." % (crv, current_shape_type, stored_shape_type))
                    continue
            
            # Set Transform
            transform_info = crv_info.get("transform_info")
            if set_transform and not transform_info:
                self.log.warn("Cannot set transform info on '%s'. None was exported. Re-export and try again." % crv)
                set_transform = False
            if set_transform:
                crv.xform(t=transform_info.get("t"), ws=True)
                crv.xform(rp=transform_info.get("rp"), ws=True)
                crv.xform(sp=transform_info.get("sp"), ws=True)
                crv.r.set(transform_info.get("r"))
                crv.s.set(transform_info.get("s"))
                crv.rotateOrder.set(transform_info.get("rotateOrder"))
                par = transform_info.get("parent")
                if par:
                    if i_utils.check_exists(par):
                        crv.set_parent(par)
                    else:
                        self.log.warn("Cannot parent '%s' to '%s'. '%s' does not exist." % (crv, par, par))

            # Set Shapes
            if set_shapes:
                current_shapes = sorted(crv.relatives(s=True))
                for i in range(len(stored_shapes)):
                    # Vars
                    scene_shape = current_shapes[i]
                    stored_shape = stored_shapes[i]
                    stored_shape_info = shape_info.get(stored_shape)
                    # Set Color
                    if color:
                        i_control.set_color(controls=scene_shape, color=stored_shape_info.get("color"))
                    # Set Points
                    if shape:
                        i_control.match_points(driver_points=stored_shape_info.get("points_local"), driven_shape=scene_shape, match_world=False)

    def read(self, curves=None, set=False, color=True, shape=True, raise_error=True, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.

        :param curves: (list) - (optional) Objects to get information on. If not given, queries selection.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param color: (bool) - Set the color information?
        :param shape: (bool) - Set the shape information?
        :param kwargs: (dict) - Used in DataIO.read()

        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read specific nodes only?
        if curves or i_utils.check_sel(raise_error=False, dialog_error=False):
            curves = self._get_objects(curves)

        # Read Json Values
        ret_dict = DataIO.read(self, path=self.json_path, specified_nodes=curves, raise_error=raise_error)  # **kwargs not included. Need raise_error False
        if not ret_dict:
            return

        # Set Values in Scene?
        if set:
            self._set(json_info=ret_dict, color=color, shape=shape, raise_error=raise_error)

        # Verbose
        self._message(action="import", set=set, successes=ret_dict.keys())

        # Return
        return ret_dict


class ControlsIO(CurvesIO):
    """Import/Export class for Controls"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="control_data.json", **kwargs)

    def _get_objects(self, objects=None):
        """
        Get the objects to use

        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection.
        If no selection, uses all controls in scene.

        :return: (list) Objects
        """
        if not objects:
            objects = i_control.get_controls(use_selection=True)
        
        if objects:
            objects = [control for control in objects if not control.is_referenced() and ":" not in control]
        
        return objects


def controls_anim_blend(drivers=None, target=None, point=True, orient=True, pin=False):
    """
    Create control that blends between multiple controls.
    
    :param drivers: (list) - Driver objects
    :param target: (iControl) - Target control object
    :param point: (bool) - Point constrain drivers to target?
    :param orient: (bool) - Orient constrain drivers to target?
    :param pin: (bool) - Create a Pin Control for the target to also be a driver?
    
    :return: None
    """
    def po_attr(attr_name_replace=None, constraint=None):
        """
        Edit weight values and add driver attributes for the constraints
        
        :param attr_name_replace: (str) - "Replace" of a search/replace in naming the attribute based on target name
        :param constraint: (iNode) - The constraint to edit
        
        :return: None
        """
        i_attr.create(node=target_control, ln="%sCns" % attr_name_replace, at="enum", en="Blend:", k=False, l=True, cb=True)
        w_val = 0
        for loc in driver_list:
            attr_nm = loc.name_short().replace(target_control + "Blend", attr_name_replace)
            attr = i_attr.create(node=target_control, ln=attr_nm, dv=0, min=0, max=1, k=True)
            attr.drive(constraint + ".w%i" % w_val)
            w_val += 1
            if driver_list.index(loc) == 0:
                attr.set(1)
    
    # Vars
    target_top_grp = target.top_tfm
    target_control = target.control
    
    # Pin
    if pin:
        par = "Ctrl_Cns_Grp" if i_utils.check_exists("Ctrl_Cns_Grp") else None
        pin_parent = i_node.create("transform", n="PinBlend_Ctrl_Grp", use_existing=True, parent=par)
        
        pin_ctrl = i_node.create("control", control_type="2D Panel Circle", color="black", size=4, position_match=target_control,
                                 parent=pin_parent, name=target_control.name.replace("_Ctrl", "Pin_Ctrl"))
        
        i_attr.create_vis_attr(node=target_control, ln="Target", use_existing=True, drive=pin_ctrl.top_tfm)
        
        drivers.append(pin_ctrl)
    
    # Blend Group
    par = "Utility_Grp" if i_utils.check_exists("Utility_Grp") else None
    blend_grp = i_node.create("transform", n="Animation_BlendTarget_Grp", use_existing=True, parent=par)
    
    # Create Locators
    driver_list=[]
    for driver in drivers:
        driver_control = driver.control
        loc = i_node.create("locator", name=driver_control.name.replace("Ctrl", "") + target_control + "Blend")
        i_node.copy_pose(driver=target_control, driven=loc)
        i_constraint.constrain(driver_control, loc, mo=True, as_fn="parent")
        loc.set_parent(blend_grp)
        loc.vis(0)
        driver_list.append(loc)
    
    # Make a node between top_tfm and second tfm
    target_second_tfm = target_top_grp.relatives(0, c=True)
    target_grp = target_second_tfm.create_zeroed_group(group_name=target_control.name.replace("Ctrl", "Blender"))
    
    # Constrain
    if point:
        point_cns = i_constraint.constrain(driver_list, target_grp, mo=True, as_fn="point")
        po_attr(attr_name_replace="Point", constraint=point_cns)
    if orient:
        ori_cns = i_constraint.constrain(driver_list, target_grp, mo=True, as_fn="orient")
        ori_cns.interpType.set(2)
        po_attr(attr_name_replace="Orient", constraint=ori_cns)


def set_gimbal_vis(controls=None, set=1):
    """
    Set all control gimbal vis attributes in the scene
    
    :param controls: (list of iNodes) - (optional) Controls to set. If not defined, uses all in scene
    :param set: (int) - Value to set. Accepts 0 or 1
    
    :return: None
    """
    # Get controls
    if not controls:
        controls = i_control.get_controls()
    else:
        controls = [ctrl for ctrl in controls if i_control.check_is_control(ctrl)]
    if not controls:
        i_utils.error("No controls given or found")
        
    # Set
    # :note: Frankenstein is "GimbalVis" / Legacy is "Gimbal"
    gim_attrs = ["GimbalVis", "Gimbal"]
    for control in controls:
        gimbal_attrs = [g_attr for g_attr in gim_attrs if i_utils.check_exists(control + "." + g_attr)]
        if not gimbal_attrs:
            continue
        for g_attr in gimbal_attrs:
            control.attr(g_attr).set(set)


def set_all_vis_attrs(controls=None, set=1, include_top_group=True):
    """
    Set all control vis attributes in scene.
    
    :param controls: (list of iNodes) - (optional) Controls to set. If not defined, uses all in scene
    :param set: (int) - Value to set. Accepts 0 or 1
    :param include_top_group: (bool) - Set the rig's top group (ex: "Character") vis attrs as well?
    
    :return: None
    """
    # Get controls
    if not controls:
        controls = i_control.get_controls()
    else:
        controls = [ctrl for ctrl in controls if i_control.check_is_control(ctrl)]
    if not controls:
        i_utils.error("No controls given or found")
    
    # Vars
    ignore_attrs = ["Facial_Ctrl_Vis"]
    legacy_ctrl_attrs = ["Gimbal", "BendyCtrls", "TweakCtrls", "BaseIkCtrls", "IkFkBlend", "IkCtrls", "TipCtrls", 
                         "SubCtrls", "Offset", "Target", "BendCtrls"]
    
    # Set Attrs
    for control in controls:
        vis_attrs = [attr for attr in control.attrs(ud=True, se=True) if attr.endswith("Vis") and attr not in ignore_attrs]
        vis_attrs += [attr for attr in legacy_ctrl_attrs if i_utils.check_exists(control + "." + attr) and control.attr(attr).get(se=True)]
        if not vis_attrs:
            continue
        for vis_attr in vis_attrs:
            if not control.attr(vis_attr).get(settable=True):
                # RIG_LOG.warn("Cannot set %s.%s. It is not settable" % (control, vis_attr))
                continue
            control.attr(vis_attr).set(set)
    
    # Also do top group
    if include_top_group:
        if set == 0:
            top_group = rig_nodes.get_top_group(raise_error=False)
            if top_group:
                i_attr.set_to_default_attrs(nodes=[top_group])
        elif set == 1:
            rig_nodes.set_to_rigging_vis()


def create_vis_control(parent=None, use_existing=True, position_match=None, size=1):
    """
    Create rig's vis control
    
    :param parent: (iNode) - (optional) Node to parent the created control under
    :param use_existing: (bool) - Use existing control or create a new one if found?
    :param position_match: (iNode, list of iNodes) - (optional) Match the created control's position to in-scene nodes?
    :param size: (int, float) - Control size
    
    :return: (iControl) - Created control
    """
    # Already Exists?
    ctrl_name = "Control_Ctrl"
    if i_utils.check_exists(ctrl_name):
        if not use_existing:
            return
        # - Recreate necessary parts of the control info dict to replicate i_node.create("control")
        control = i_node.Node(ctrl_name)
        offset_grp = control.relatives(p=True)  # Only doesn't have if the Control_Ctrl was made with Watson. Yay, legacy.
        ctrl = i_control.mimic_control_class(control=control, offset_grp=offset_grp, top_tfm=offset_grp)
        # - Parent
        if parent:
            top_tfm = ctrl.top_tfm
            curr_par = top_tfm.relatives(p=True)
            if (curr_par and curr_par[0] != parent) or not curr_par:
                top_tfm.set_parent(parent)
        return ctrl

    # Create
    control_kws = {"control_type": "Eye",# "text",
                   "color": "black",
                   "name": ctrl_name,
                   "parent": parent,
                   "with_cns_grp": False,
                   "with_offset_grp": True,
                   "with_gimbal": False,
                   "with_gimbal_zro": False,
                   "size": float(size) * 0.05,  # :note: Text version should be just "size"
                   "lock_hide_attrs": ['t', 'r', 's', 'v']
                   }
    ctrl = i_node.create("control", **control_kws)

    if position_match:
        i_node.copy_pose(driver=position_match, driven=ctrl.top_tfm, attrs="t")

    # Add visibility attribute
    i_attr.create_vis_attr(node=ctrl.top_tfm, ln="ControlVis", drive=ctrl.control, dv=1)

    # Add info attribute
    i_node.connect_to_info_node(info_attribute="vis_ctrl", objects=ctrl.control)

    # Return
    return ctrl


def an_mo_auto(controls=None, driver_obj=None, driver_attr=None):
    """
    Create "AnMo" Setup for Watson slider poses
    
    :param controls: (list of iNodes or str) - (optional) Controls posed to be triggered with sliders.
        If not defined, checks selection or uses all controls in scene.
    :param driver_obj: (iNode) - (optional) Node that drives the triggers. If not defined, creates.
    :param driver_attr: (str) - (optional) Attr name on the :param driver_obj: that drives the position.
    
    :return: None
    """
    # Check 
    if not driver_obj:
        driver_obj = "AnMoDriver"
        if i_utils.check_exists(driver_obj):
            driver_obj = i_node.Node(driver_obj)
    if not i_utils.check_exists(driver_obj):
        i_utils.error("Driver object: '%s' does not exist." % driver_obj, dialog=True)
        return 
    if not controls:
        controls = i_control.get_controls(use_selection=True)
    if not controls:
        i_utils.error("No controls given, selected or found.", dialog=True)
        return

    # Have controls been moved from zeroed out position?
    moved_controls = []
    default_attr_vals = {"t": 0, "r": 0, "s": 1}
    for control in controls:
        # - Convert
        control = i_node.Node(control)
        # - Ignore some controls
        if "Sldr" in control.name or control in ["Control_Ctrl", "Facial_Ctrl", "WingMaster_Ctrl"]:
            # :note: Original code did not exclude WingMaster_Ctrl, but it fails the Cns/Offset group check
            continue
        # - Loop through attrs
        for trs, default_val in default_attr_vals.items():
            if not control.attr(trs).get(settable=True):
                continue
            for xyz in ["x", "y", "z"]:
                val = control.attr(trs + xyz).get()
                if val != default_val:
                    moved_controls.append(control)

    # Find driver attr if not given
    if not driver_attr:
        # - Get possibilities
        all_attrs = [attr for attr in driver_obj.attrs(ud=True) if attr not in ["assetID", "objectID"]
                     and not attr.endswith("Manual")]
        possible_attrs = []
        for attr in all_attrs:
            val = driver_obj.attr(attr).get()
            if isinstance(val, (int, float)) and val > 0:
                possible_attrs.append(attr)
        # - Check results
        if not possible_attrs:
            i_utils.error("No Slider Active (set to non-0)", dialog=True)
            return
        if len(possible_attrs) > 1:
            i_utils.error("Too many Slider Attributes Active (set to non-0)", dialog=True)
            return
        driver_attr = possible_attrs[0]

    # Check current driver value
    driver_attr_val = driver_obj.attr(driver_attr).get()
    if driver_attr_val == 0:
        i_utils.error("Cannot make pose at 0 because this will make the starting point non-0 default.", dialog=True)
        return

    # Actually make
    for control in moved_controls:
        an_mo_make(driver_obj=driver_obj, driver_attr=driver_attr, driver_attr_val=driver_attr_val, target=control)


def an_mo_make(driver_obj=None, driver_attr=None, driver_attr_val=None, target=None):
    """
    Part of the "AnMo" Setup for Watson slider poses
    :note: This is used by an_mo_auto(). To make the setup, use an_mo_auto() instead of an_mo_make() directly.
    
    :param driver_obj: (iNode) - Node that drives the triggers.
    :param driver_attr: (str) - Attr name on the :param driver_obj: that drives the position.
    :param driver_attr_val: (int, float) - Position value of the pose
    :param target: (iNode) - Control to be driven
    
    :return: None
    """
    # Check
    target_parents = target.name_long().split("|")[1:]
    target_cns = [grp for grp in target_parents if "Cns" in grp and target.replace("_Ctrl", "") in grp]
    target_ofs = [grp for grp in target_parents if "Offset" in grp and target.replace("_Ctrl", "") in grp]
    if not (target_cns and target_ofs):
        i_utils.error("%s has no Cns and/or Offset group." % target)
    target_cns = target_cns[0]
    target_ofs = target_ofs[0]

    # Loc Group?
    target_loc_grp = target + "_" + driver_attr + "_AnMoLoc_Grp"
    if not i_utils.check_exists(target_loc_grp):
        target_loc_grp = None

    # Loc Group DOESN'T exist
    if not target_loc_grp:
        # - Set up loc group and connect
        loc = i_node.create("locator", n=target + "_" + driver_attr + "_%03d_Loc" % (driver_attr_val * 100))
        grp_parent = "AnMoLoc_Grp"
        if not i_utils.check_exists(grp_parent):
            grp_parent = i_node.create("transform", n=grp_parent, p="Utility_Grp")
        grp_parent = i_node.Node(grp_parent)
        target_loc_grp = i_node.create("group", loc, n=target + "_" + driver_attr + "_AnMoLoc_Grp", p=grp_parent)
        i_constraint.constrain(target_ofs, target_loc_grp, mo=False, as_fn="parent")
        vis_cnd = i_node.create("condition", n=target + "_AnMoLoc_Vis_Cnd")
        driver_obj.attr(driver_attr).drive(vis_cnd.firstTerm)
        vis_cnd.secondTerm.set(0)
        vis_cnd.outColorR.drive(target_loc_grp.v)
        # - Match position of locator to target
        i_node.copy_pose(driver=target, driven=loc)
        # - Zero out control
        target.zero_out()
        # - Create Color Ramps by position
        ramps = []
        for trs in ["t", "r", "s"]:
            ramp = i_node.create("ramp", n=target + "_" + driver_attr + "_%s_Ramp" % trs.upper())
            ramps.append(ramp)
            if trs in ["t", "r"]:
                ramp.colorEntryList[0].color.set([0, 0, 0])
            elif trs in ["s"]:
                ramp.colorEntryList[0].color.set([1, 1, 1])
            ramp.colorEntryList[0].position.set(0)
            loc.attr(trs).drive(ramp.colorEntryList[1].color)
            ramp.colorEntryList[1].position.set(driver_attr_val)
            driver_obj.attr(driver_attr).drive(ramp.vCoord)
        # - Find / Create blend/avg nodes
        blend_nodes = {}
        blends_exist = i_utils.check_exists(target + "_MotionData_TX_Blend")
        rgb = ["R", "G", "B"]
        if blends_exist:
            for i, trs in enumerate(["T", "R", "S"]):
                # - Find blends
                if trs in ["T", "R"]:
                    blends = sorted(i_utils.ls(target + "_MotionData_%s*_Blend" % trs))
                elif trs in ["S"]:
                    blends = sorted(i_utils.ls(target + "_MotionData_%s*_Avg" % trs))
                blend_nodes[trs] = blends
        else:
            for i, trs in enumerate(["T", "R", "S"]):
                # - Create blends
                blends = []
                blend_name = target + "_MotionData_%s*" % trs
                for xyz in ["X", "Y", "Z"]:
                    if trs in ["T", "R"]:
                        blend = i_node.create("blendWeighted", n=blend_name.replace("*", xyz) + "_Blend")
                    elif trs in ["S"]:
                        blend = i_node.create("plusMinusAverage", n=blend_name.replace("*", xyz) + "_Avg")
                        blend.operation.set(3)
                    blends.append(blend)
                blend_nodes[trs] = blends
        # - Find next index
        next_i = blend_nodes.get("T")[0].output.get_next_index()
        # - Create Top group
        top_grp = target_cns.create_zeroed_group(group_name=target + "_AnMoDriver_Grp")
        # - Connect blends to ramps and top group
        for i, trs in enumerate(["T", "R", "S"]):
            # - Vars
            ramp = ramps[i]
            blends = blend_nodes.get(trs)
            for j, blend in enumerate(blends):
                # - Vars
                xyz = ["X", "Y", "Z"][j]
                # - Connect to ramp & top group
                if trs in ["T", "R"]:
                    ramp.attr("outColor%s" % rgb[j]).drive(blend.input[next_i])
                    blend.output.drive(top_grp.attr(trs.lower() + xyz.lower()))
                elif trs in ["S"]:
                    ramp.attr("outColor%s" % rgb[j]).drive(blend.input1D[next_i])
                    blend.output1D.drive(top_grp.attr(trs.lower() + xyz.lower()))

    # Loc Group DOESN'T exist
    else:
        # - Find ramps
        ramps = []
        for trs in ["t", "r", "s"]:
            ramp = i_node.create("ramp", n=target + "_" + driver_attr + "_%s_Ramp" % trs.upper())
            ramps.append(ramp)
        # - Does locator exist?
        loc = target + "_" + driver_attr + "_%03d_Loc" % (driver_attr_val * 100)
        # - Locator DOES exist
        if i_utils.check_exists(loc):
            loc = i_node.Node(loc)
            # - Get combined values to set
            set_vals = {}
            for trs in ["t", "r", "s"]:
                for xyz in ["x", "y", "z"]:
                    set_val = loc.attr(trs + xyz).get() + target.attr(trs + xyz).get()
                    if trs == "s":
                        set_val -= 1
                    set_vals[trs + xyz] = set_val
            # - Set values in separate loop
            for trs in ["t", "r", "s"]:
                for xyz in ["x", "y", "z"]:
                    loc.attr(trs + xyz).set(set_vals.get(trs + xyz))
            # - Reset Control
            target.zero_out()

        # - Locator DOESN'T exist
        else:
            # - Create locator
            loc = i_node.create("locator", n=target + "_" + driver_attr + "_%03d_Loc" % (driver_attr_val * 100))
            grp_parent = "AnMoLoc_Grp"
            if not i_utils.check_exists(grp_parent):
                grp_parent = i_node.create("transform", n=grp_parent, p="Utility_Grp")
            grp_parent = i_node.Node(grp_parent)
            if not target_loc_grp:
                target_loc_grp = i_node.create("group", loc, n=target + "_" + driver_attr + "_AnMoLoc_Grp", p=grp_parent)
            loc.set_parent(target_loc_grp)
            i_node.copy_pose(driver=target, driven=loc)
            # - Connect
            for i, ramp in enumerate(ramps):
                next_i = ramp.colorEntryList.get_next_index()
                loc.attr(["t", "r", "s"][i]).drive(ramp.colorEntryList[next_i].color)
                ramp.colorEntryList[next_i].position.set(driver_attr_val)


def create_anim_constraint_control(parent_ctrl=None, match_joint=None, control_size=None, base_name=None, color=None):
    """
    Create additional control animation uses to add constraints (Anim Constraint Control)
    
    :param parent_ctrl: (iControl) - Ctrl object to parent the new control to
        :note: Expects parent_ctrl to have "xtra_grp" attr
    :param match_joint: (iNode) - Object to match the created control's position to
    :param control_size: (int, float) - Created control size
    :param base_name: (str) - Base name for created objects
    :param color: (str, int) - Created control color
    
    :return: (iControl) - Created control
    """
    # Create
    ctrl = i_node.create("control", control_type="2D Circle", name=base_name + "_AnimConstraint",
                         size=control_size, position_match=match_joint, match_rotation=True,
                         color=color, with_gimbal=False, with_offset_grp=False,
                         with_cns_grp=False, follow_name="Anim_Constraint")
    anim_cns_ctrl = ctrl.control
    anim_cns_ctrl.set_parent(parent_ctrl.xtra_grp)

    # Connect visibility of shape (tfm connected in PackMaster's create_ikfk_switch)
    i_attr.create_vis_attr(node=parent_ctrl.control, ln="AnimConstraint", drive=anim_cns_ctrl.relatives(s=True), dv=0)

    # Add xtra group
    xtra_grp = anim_cns_ctrl.create_zeroed_group(group_name=parent_ctrl.control + "_CN_xtra")

    # Rotate shape to match joint
    shape_cvs = anim_cns_ctrl.get_cvs()
    i_node.copy_pose(driver=match_joint, driven=shape_cvs, attrs="r")

    # Parent into hierarchy
    xtra_grp.set_parent(parent_ctrl.xtra_grp)

    # Parent end control under anim cns ctrl
    parent_ctrl.control.set_parent(anim_cns_ctrl)

    # Lock Hide
    i_attr.lock_and_hide(node=xtra_grp, attrs=["t", "s", "v"], lock=True, hide=True)
    i_attr.lock_and_hide(node=anim_cns_ctrl, attrs=["s", "v"], lock=True, hide=True)

    # Return
    return anim_cns_ctrl


def create_tweaks(joints=None, name_remove=None, constrain=None, name_match=None, name_num_start=None, **kwargs):
    """
    Create Tweak Controls setup
    
    :param joints: (list of iNodes) - Joints to create tweaks controls for
    :param name_remove: (str, list) - (optional) Tweak names come from joint names. Use to additionally remove parts of that name string.
    :param constrain: (iNode, list of iNode) - (optional) Drive tweak control using a constraint
        If using a list, the index of the constraint driver must match the index of the joints. List lengths must also match.
    :param name_match: (str) - (optional) Specify tweak name as opposed to using the joint name entirely.
        :note: All other naming-based params will still be applied. This value is simply the alternative starting point.
    :param name_num_start: (int) - (optional) Define first number used in tweak names. If not defined will use 0.
    :param kwargs: (dict) - (optional) Accepts all kwargs in i_control.Control.create()
    
    :return: (list of iControls) Created tweak controls
    """
    # Vars
    i_utils.check_arg(joints, "joints")
    if not isinstance(joints, (list, tuple)):
        joints = [joints]
    
    # Turn off match rotation by default
    if "match_rotation" not in kwargs:
        kwargs["match_rotation"] = False

    # Create
    tweak_ctrls = []
    for i, obj_match in enumerate(joints):
        nm = name_match or obj_match
        if name_remove:
            if isinstance(name_remove, (str, unicode)):
                nm = obj_match.replace(name_remove, "")
            elif isinstance(name_remove, (list, tuple)):
                for nr in name_remove:
                    nm = nm.replace(nr, "")
        nm = i_utils.convert_data(nm)
        nm_nums = logic_py.find_numbers_in_string(string=nm, raise_error=False)
        if nm_nums and "".join(nm_nums) in nm.split("_"):
            nm_nums = "_" + "".join(nm_nums)
            nm = nm.replace(nm_nums, "")
        elif name_num_start is not None:
            nm_nums = str(name_num_start)
        else:
            nm_nums = ""
        nm = nm.replace("__", "_")  # Final catch
        nm = nm.replace("_Ctrl", "")  # In case given a name match of a control
        cons = constrain
        if isinstance(constrain, (list, tuple)):
            cons = constrain[i]
        ctrl = i_node.create("control", control_type="2D Twist Gear", position_match=obj_match, color=9,  # color is neon pink
                             name=nm + "_Tweak" + nm_nums, with_gimbal=False, lock_hide_attrs=["v"], 
                             constrain_geo=cons, **kwargs)
        tweak_ctrls.append(ctrl)

    # Return
    return tweak_ctrls


def get_cv_sel():
    """
    Selection wrapper for getting cv information on selected curves and printing the results
    
    :return: None
    """
    sel = i_utils.check_sel()
    if not sel:
        return

    for curve in sel:
        cvs = curve.get_cvs()
        RIG_LOG.info("%s > CVs: %i" % (curve, len(cvs)))


def get_ground_gimbal():
    """
    Get the in-scene Ground Gimbal control
    
    :return: (iControl) Ground Gimbal control - or None if none found
    """
    info_node = i_node.info_node_name
    if i_utils.check_exists(info_node + ".ground_ctrl"):
        ground_control = i_attr.Attr(info_node + ".ground_ctrl").connections()
        if not ground_control:
            return None
        return i_control.get_gimbal(ground_control[0])


def fk_chain_from_edges(base_edges=None, end_edges=False, name=None, number_joints_across=1, number_joints_down=1,
                        orient_as="yzx", up_axis="yup", control_type=None, control_color=None):
    """
    Create Fk chain setup from geo edges
    
    :param base_edges: (list of iNodes) - Components that create the "base" joints
    :param end_edges: (list of iNodes) - Components that create the "end" joints
    :param name: (str) - Base name for created objects
    :param number_joints_across: (int) - Number of joints across
    :param number_joints_down: (int) - Number of joints down
    :param orient_as: (str) - Joint orientation to run on created chains. String comprised of "x", "y" and "z"
    :param up_axis: (str) - Joint orientation up axis. String comrised of "x", "y", "z" and "up" or "down"
    :param control_type: (str) - Control shape type of controls created
    :param control_color: (str, int) - Color of controls created
    
    :return: (list of iControls) Created controls
    """
    import rig_tools.utils.joints as rig_joints  # Need to import here
    
    # Create rows of joints
    base_joints = rig_joints.joints_from_components(components=base_edges, name=name + "_Base", number_of_joints=number_joints_across)
    end_joints = rig_joints.joints_from_components(components=end_edges, name=name + "_End", number_of_joints=number_joints_across)
    
    # Create joint chains
    chains = []
    for i in range(number_joints_across):
        base_jnt, end_jnt = base_joints[i], end_joints[i]
        # - Parent bottoms to tops
        end_jnt.set_parent(base_jnt)
        # - Insert Joints
        inserted = rig_joints.insert_joints(from_joint=base_jnt, to_joint=end_jnt, number_of_insertions=number_joints_down)
        chain = [base_jnt] + inserted + [end_jnt]
        chains.append(chain)
        # - Orient
        rig_joints.orient_joints(joints=chain, orient_as=orient_as, up_axis=up_axis)
    
    # Create controls
    chain_ctrls = []
    control_size = base_joints[0].radius.get() * 2.0
    for i, chain in enumerate(chains):
        ctrls = []
        for j, jnt in enumerate(chain):
            ctrl = i_node.create("control", name=name + "_" + str(i).zfill(2) + "_" + str(j).zfill(2), color=control_color,
                                 control_type=control_type, with_gimbal=False, position_match=jnt, constrain_geo=True,
                                 scale_constrain=True, size=control_size)
            if j > 0:
                ctrl.top_tfm.set_parent(ctrls[-1].last_tfm)
            ctrls.append(ctrl)
        chain_ctrls.append(ctrls)
    
    # Return
    return chain_ctrls


def create_color_feedback(control=None, toggle_attr=None, base_name=None):
    """
    Create condition-based feedback from an attribute to change a control shape's colors
    
    :param control: (iNode) - Control transform with shape colors to be driven and that has the toggle attribute
    :param toggle_attr: (str) - Attribute name that drives the condition
    :param base_name: (str) - Base name for created objects
    
    :return: (iNode) Created condition node
    """
    # Check
    i_utils.check_arg(control, "control", exists=True)
    i_utils.check_arg(toggle_attr, "toggle attr")
    toggle_attr = control + "." + toggle_attr
    if not i_utils.check_exists(toggle_attr):
        RIG_LOG.warn("%s does not exist. Cannot create color feedback toggle." % toggle_attr)
        return
    toggle_attr = i_attr.Attr(toggle_attr)
    
    # Create condition
    cnd = i_node.create("condition", n=base_name + "_ColorFeedback_CND", use_existing=True)
    toggle_attr.drive(cnd.firstTerm)
    cnd.colorIfTrueR.set(13)
    ctrl_color = i_control.get_color(control_shape=control)
    cnd.colorIfFalseR.set(ctrl_color)
    
    # Drive control shape colors with condition
    ctrl_shapes = control.relatives(s=True)
    for shp in ctrl_shapes:
        shp.overrideEnabled.set(1)
        cnd.outColorR.drive(shp.overrideColor)
    
    # Return
    return cnd


def select_all_controls():
    """
    Select all controls in the scene
    
    :return: None
    """
    top_node = i_node.get_top_nodes()
    if top_node:
        top_node = top_node[0]
    
    controls = i_control.get_controls(top_node=top_node)
    
    if not controls:
        i_utils.error("No controls found.", dialog=True)
        return 
    
    i_utils.select(controls)
