import os
import collections
from functools import partial
import maya.cmds as cmds

import icon_api.node as i_node
import icon_api.control as i_control
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint
import io_utils

from rig_tools import RIG_LOG
import rig_tools.frankenstein.utils as rig_frankenstein_utils
import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.misc as rig_misc
import rig_tools.utils.nodes as rig_nodes
import rig_tools.utils.deformers as rig_deformers
import rig_tools.utils.io as rig_io
from rig_tools.utils.io import DataIO


def legacy_specify_face_bake(show=None):
    """
    For Watson face bakes. Able to override which type of bake it uses in the pubtask
    
    :param show: (str) - Showcode to use the bake on. See legacy_watson_face() for acceptable showcodes.
    
    :return: None
    """
    nd = i_node.create("transform", name="Face_Rig", use_existing=True)
    i_attr.create(node=nd, ln="Face_Type", at="string", dv=show, l=True, use_existing=True)


def legacy_check_face_bake_type():
    """
    For Watson face bakes. Check what bake type is specified in the rig and prompt the information.
    
    :return: None
    """
    bake_type = os.environ.get("TT_PROJCODE")

    face_type_attr = "Face_Rig.Face_Type"
    if i_utils.check_exists(face_type_attr):
        bake_type = i_attr.Attr(face_type_attr).get()

    i_utils.message(title="Face Bake Type", message="Bake type: '%s'" % bake_type)


def smo_jaw_squash_add():
    """
    Add Jaw Squash specific to SMO (Super Monsters).
    
    :return: None
    """
    # Check for selection of point to match
    sel_match = i_utils.check_sel()
    if not sel_match:
        return

    # Create Control
    jaw_ctrl = i_node.create("control", control_type="3D Sphere", color="yellow", name="Jaw_Squash", with_gimbal=False,
                             position_match=sel_match)

    # Create / Find FaceBender things
    bender = "FaceBender"
    bender_ctrl = "FaceBender_Ctrl"
    for bend_obj in [bender, bender_ctrl]:
        if not i_utils.check_exists(bend_obj):
            i_utils.error("'%s' does not exist." % bend_obj, dialog=True)
            return
    bender = i_node.Node(bender)
    bender_ctrl = i_node.Node(bender_ctrl)
    bender_ctrl_offset = i_control.get_top_tfm(bender_ctrl)
    bender_offset_grp = bender.create_zeroed_group(group_name_add="Offset", use_existing=True)  # "FaceBender_Offset_Grp"
    if not bender_offset_grp.existed:
        i_node.copy_pose(driver=bender_ctrl, driven=bender_offset_grp, attrs="pivots")

    # Create math nodes
    # - Squash Pma
    squash_pma = i_node.create("plusMinusAverage", n="JS_Squash_PMA", use_existing=True)
    squash_pma.attr("input2D[0].input2Dx").set(1)
    # - Squash Md
    squash_md = i_node.create("multiplyDivide", n="JS_Squash_MD", use_existing=True)
    squash_md.input2X.set(-0.1)
    # - Average Pma
    avg_pma = i_node.create("plusMinusAverage", n="JS_Average_PMA", use_existing=True)
    avg_pma.attr("input2D[0].input2Dx").set(1.1)
    # - Equalize Pma/Md (So result is always 1)
    eq_pma = i_node.create("plusMinusAverage", n="JS_Equalizing_PMA", use_existing=True)
    eq_pma.operation.set(2)  # Sub
    eq_pma.attr("input2D[0].input2Dx").set(1.0)
    # - RX Md
    rx_md = i_node.create("multiplyDivide", n="JS_RotateX_MD", use_existing=True)
    rx_md.input2X.set(3.4)
    # - RZ Md
    rz_md = i_node.create("multiplyDivide", n="JS_RotateZ_MD", use_existing=True)
    rz_md.input2X.set(-2)

    # Connect Things
    jaw_ctrl.control.ty.drive(squash_pma.attr("input2D[1].input2Dx"))
    jaw_ctrl.control.tx.drive(rx_md.input1X)
    jaw_ctrl.control.tz.drive(rz_md.input1X)
    squash_md.input2X.drive(eq_pma.attr("input2D[1].input2Dx"))
    eq_pma.output2Dx.drive(avg_pma.attr("input2D[0].input2Dx"))
    squash_pma.output2Dx.drive(squash_md.input1X)
    squash_md.outputX.drive(avg_pma.attr("input2D[1].input2Dx"))
    avg_pma.output2Dx.drive(bender_offset_grp.sy, f=True)
    avg_pma.output2Dx.drive(bender_ctrl_offset.sy, f=True)
    rx_md.outputX.drive(bender_offset_grp.rz, f=True)
    rx_md.outputX.drive(bender_ctrl_offset.rz, f=True)
    rz_md.outputX.drive(bender_offset_grp.rx, f=True)
    rz_md.outputX.drive(bender_ctrl_offset.rx, f=True)

    # Cleanup
    if bender_offset_grp.existed:
        i_utils.parent("L_Jowl_01_Offset_Grp", "M_Jowl_Offset_Grp", "R_Jowl_01_Offset_Grp", bender)
    else:
        i_utils.parent("L_Jowl_01", "M_Jowl", "R_Jowl_01", bender)
    i_utils.parent("L_Jowl_01_Ctrl_Offset_Grp", "M_Jowl_Ctrl_Offset_Grp", "R_Jowl_01_Ctrl_Offset_Grp", bender_ctrl)


def legacy_watson_face(action=None, face_type=None, dialog_error=True, log=None):
    """
    Create or Bake a Watson Face.
    
    :param action: (str) - What action doing. Options: "template", "bake", "build".
    :param face_type: (str) - Showcode type. Only necessary if "KNG". Only used in "template" and "bake" action.
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param log: (logger) - (optional) Specify a log? Otherwise uses default RIG_LOG.
    
    :return: (bool) True/False for success
    """
    rig_misc.legacy_load_g_rigging()
    import Watson
    
    if action == "template":
        tpt_type = "BasicFace"
        if face_type == "KNG":
            tpt_type = "KongFace"
        success = rig_misc.legacy_try(partial(Watson.BasicFaceTemplate, None, False, tpt_type), dialog_error=dialog_error, log=log)
        return success
    
    elif action == "bake":
        mode = 1
        if face_type == "KNG":
            mode = 2
        success = rig_misc.legacy_try(partial(Watson.FaceBaker, mode), dialog_error=dialog_error, log=log)
        return success
    
    elif action == "build":
        face_pack_nd = "Face_BuildPack"
        if not i_utils.check_exists(face_pack_nd):
            i_utils.error("'%s' does not exist." % face_pack_nd, dialog=True)
            return False

        script_typ = i_node.Node(face_pack_nd).Script.get()
        if script_typ == "KongFace":
            success = rig_misc.legacy_try(partial(Watson.KongFaceTrigger, face_pack_nd), dialog_error=dialog_error, log=log)
            return success
        elif script_typ == "BasicFace":
            success = rig_misc.legacy_try(partial(Watson.BasicFaceTrigger, face_pack_nd), dialog_error=dialog_error, log=log)
            return success
        else:
            i_utils.error("Do not recognize script type: '%s'. Expected: 'KongFace' or 'BasicFace'." % script_typ, dialog=dialog_error, raise_err=False)
            return False
    
    else:
        i_utils.error("Action must be 'template', 'build', or 'bake'. Given: %s" % action)


def ttm_groups():
    """
    Create Goldie/Musketeers face groups.
    
    :return: None
    """
    # Find Face Rig namespace
    char = os.environ.get("TT_ENTNAME")
    face_ns = i_utils.ls(char + "_Face_Rig*:*")
    if not face_ns:
        i_utils.error("Cannot find Face Rig namespace for %s." % char, dialog=True)
        return
    face_ns = face_ns[0].split(":")[0]

    # Find Face Rig groups
    fr_visual_system = face_ns + ":VisualSystem"
    fr_facial_system = face_ns + ":FacialSystem"
    fr_utils = face_ns + ":Face_Utils"
    fr_geo = face_ns + ":Geo"
    bad_fr_groups = [fr_grp for fr_grp in [fr_visual_system, fr_facial_system, fr_utils, fr_geo] if not i_utils.check_exists(fr_grp)]
    if bad_fr_groups:
        i_utils.error("Could not find the following Face Rig groups. Is everything named properly?\n\n%s" ", ".join(bad_fr_groups), dialog=True)
        return

    # Parent face rig groups
    info_node = i_node.info_node_name
    # - Facial System
    fr_facial_system = i_node.create("group", fr_facial_system, n="Face_Ctrl_Grp")
    i_utils.select(cl=True)
    head_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type" : "Head_Simple"})
    head_info = rig_frankenstein_utils.get_pack_object(pack_info_node=head_info_node[0])
    head_control = head_info.ctrl.control
    head_gim_ctrl = head_info.ctrl.gimbal
    fr_facial_system.set_parent(head_gim_ctrl)
    # - Visual System
    ctrl_grp = "Ctrl_Grp"
    if i_utils.check_exists(info_node + ".Ctrl_Group"):
        ctrl_grp = info_node.Ctrl_Group.connections()[0]
    fr_visual_system.set_parent(ctrl_grp)
    # - Face Utils / Geo
    utility_grp = "Utility_Grp"
    if i_utils.check_exists(info_node + ".Utility_Group"):
        utility_grp = info_node.Utility_Group.connections()[0]
    i_utils.parent(fr_utils, fr_geo, utility_grp)

    # Connect Visibility
    face_vis = i_attr.create_vis_attr(node=head_control, drive=fr_facial_system, ln="Face_Ctrls", dv=0)
    i_attr.update_default_attrs(nodes=[head_control])
    face_vis.set(1)  # For rigging purposes
    # - Reorder
    attrs = i_attr.get_channelbox_attrs(node=head_control, ud_only=True)
    follow_attrs = rig_attributes.get_follow_attrs(control=head_control)
    non_follow_attrs = [attr for attr in attrs if attr not in follow_attrs]
    new_attr_order = non_follow_attrs + follow_attrs
    i_attr.reorder(node=head_control, new_order=new_attr_order)

    # Hide some groups
    fr_utils.v.set(0)


def ttm_bsh():
    """
    Create Musketeers Face blendshapes to the rig geo
    
    :return: None
    """
    # Check selection
    sel = i_utils.check_sel()
    if not sel:
        return

    # Find Face Rig namespace
    char = os.environ.get("TT_ENTNAME")
    face_ns = i_utils.ls(char + "_Face_Rig*:*")
    if not face_ns:
        i_utils.error("Cannot find Face Rig namespace for %s." % char, dialog=True)
        return
    face_ns = face_ns[0].split(":")[0]

    # Loop selection
    for sl in sel:
        rig_geo = [geo for geo in i_utils.ls("*:" + sl.split(":")[1].replace("Face_", "", 1)) if not geo.startswith(face_ns + ":")]
        if not rig_geo:
            i_utils.error("'%s' does not have a rig geo equivalent." % sl, dialog=True)
            return
        if len(rig_geo) > 1:
            i_utils.error("Found more than one rig geo for '%s'." % sl, dialog=True)
            return
        rig_geo = rig_geo[0]
        bsh = i_node.create("blendShape", sl, rig_geo, n=rig_geo.split(":")[-1] + "_BSH")
        bsh.w[0].set(1)
        i_utils.select(cl=True)


def smo_face_control_scale():
    """
    Scale the SMO Face Controls. Optionally used as a fix when they are too big.
    
    :return: None
    """
    # Set attr values
    # - Get values to set
    scale_settings = {}
    zeroed_scale = ["Temp_Brows_CrvObj", "Temp_Eyes_CrvObj", "Temp_Mouth_CrvObj", "Temp_Teeth_Tounge_CrvObj"]
    for obj in zeroed_scale:
        scale_settings[obj + ".scale"] = [1, 1, 1]
    scale_settings["Temp_Lip_Curls_CrvObj.scale"] = [0.368, 0.27, 0.721]
    scale_settings["Temp_Mouth_Corners_CrvObj.scale"] = [0.431, 0.431, 0.431]
    scale_settings["L_Blink_Title.scaleX"] = 0.4
    scale_settings["R_Blink_Title.scaleX"] = 0.4
    small_sx = ["MPB_Title", "TDS_Title", "SH_Title", "FV_Title", "TH_Title", "LL_Title", "Aa_Title", "Ee_Title", 
                "OH_Title", "Oo_Title", "Uu_Title"]
    for obj in small_sx:
        scale_settings[obj + ".scaleX"] = 0.3
    # - Set them
    for node_attr, val in scale_settings.items():
        if not i_utils.check_exists(node_attr):
            RIG_LOG.warn("%s does not exist. Cannot set to %s" % (node_attr, str(val)))
            continue
        node_attr = i_attr.Attr(node_attr)
        if not node_attr.get(settable=True):
            RIG_LOG.warn("%s is not settable. Cannot set to %s" % (node_attr, str(val)))
            continue
        node_attr.set(val)


class FaceBake(object):
    """Bake a Frankenstein Face"""
    def __init__(self):
        self.given_driver_attrs = {}
        
        self.driver_attr_nodes = {}
        self.drive_attrs_dict = {}
        self.con_attrs_dict = {}
        self.face_pack_obj = None
        self.dialog_errors = False

        self.attr_dv = {"t": 0, "r": 0, "s": 1}

    def _get_face_pack_obj(self):
        """
        Get the Frankenstein pack object that is the Face type
        
        :return: (bool) True/False for success
        """
        # Get the face pack
        face_pack_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type": "Face"})
        if not face_pack_info_node:
            i_utils.error("No Face packs found.", dialog=self.dialog_errors, verbose=True)
            return False
        
        # Is it a pack or a bit?
        self.face_pack_obj = rig_frankenstein_utils.get_pack_object(face_pack_info_node[0])
        if not self.face_pack_obj.bit_built:
            i_utils.error("'%s' is not a bit. Cannot bake." % self.face_pack_obj.base_name, dialog=self.dialog_errors, verbose=True)
            return False
        
        # Verbose
        RIG_LOG.debug("##VARCHECK face_pack_obj", self.face_pack_obj.base_name)

        # Success
        return True
    
    def __get_driver_nulls(self):
        """
        Get all of the driver nulls created as a part of the face pack
        
        :return: (list) Driver nulls
        """
        # Specified?
        if self.given_driver_attrs:
            face_driver_nulls = self.given_driver_attrs.keys()
        
        # All
        else:
            face_drivers = self.face_pack_obj.driver_nulls
            face_driver_nulls = face_drivers.values()

        RIG_LOG.debug("##VARCHECK face_driver_nulls", face_driver_nulls)
        
        return face_driver_nulls
    
    def __get_driver_attrs(self, driver=None):
        """
        Get all of the attrs on given driver null
        
        :param driver: (iNode) - Driver node querying
        
        :return: (list) Attributes
        """
        # Specified?
        if self.given_driver_attrs:
            face_attrs = self.given_driver_attrs.get(driver)
            if not isinstance(face_attrs, (list, tuple)):
                face_attrs = [face_attrs]
        
        # All
        else:
            face_attrs = driver.attrs(ud=True, cb=True, type="double")

        RIG_LOG.debug("##VARCHECK driver %s >> face_attrs %s" % (driver, face_attrs))
        
        return face_attrs
    
    def _get_drivers(self):
        """
        Get the triggered driver nulls.
        :note: Triggered Drivers stored in self.drive_attrs_dict and self.driver_attr_nodes:
        self.drive_attrs_dict - {face_attr : percentage}
        self.driver_attr_nodes - {face_attr : driver}
        
        :return: (bool) True/False for success
        """
        # Get the drivers
        face_driver_nulls = self.__get_driver_nulls()

        # Get triggered driver null attrs
        for driver in face_driver_nulls:
            # - Get face attrs
            face_attrs = self.__get_driver_attrs(driver=driver)
            # - Get which attrs have values
            driver_triggered_attrs = {}
            for face_attr in face_attrs:
                if face_attr.startswith("R_"):
                    continue
                val = driver.attr(face_attr).get()
                if val != 0.0:
                    driver_triggered_attrs[face_attr] = val
            # - Get per
            portion = float(sum(driver_triggered_attrs.values()))
            for face_attr, val in driver_triggered_attrs.items():
                perc = round(val / portion, 3)
                self.drive_attrs_dict[face_attr] = perc
                self.driver_attr_nodes[face_attr] = driver
                mirror_face_attr = None
                if face_attr.startswith("L_"):
                    mirror_face_attr = face_attr.replace("L_", "R_", 1)
                elif "Left" in face_attr:
                    mirror_face_attr = face_attr.replace("Left", "Right", 1)
                if mirror_face_attr:
                    self.drive_attrs_dict[mirror_face_attr] = perc
        
        # Verbose
        RIG_LOG.debug("##VARCHECK drive_attrs_dict", self.drive_attrs_dict)
        RIG_LOG.debug("##VARCHECK driver_attr_nodes", self.driver_attr_nodes)

        # Success
        return True

    def _get_driven(self):
        """
        Get the triggered on-face controls
        
        :note: Triggered Controls stored in self.con_attrs_dict:
        self.con_attrs_dict - {ctrl : attr_vals_dict}
            attr_vals_dict - {trs_xyz : attr_val}
        
        :return: (bool) True/False for success
        """
        # Get the controls
        face_tweak_ctrls = self.face_pack_obj.tweak_ctrls
        RIG_LOG.debug("##VARCHECK face_tweak_ctrls", face_tweak_ctrls)

        # Get control attr (set) info
        triggered_ctrls = []
        for ctrl in face_tweak_ctrls:
            triggered = False
            control = ctrl.control
            for trs in ["t", "r", "s"]:
                dv = self.attr_dv.get(trs)
                for xyz in ["x", "y", "z"]:
                    val = control.attr(trs + xyz).get()
                    if val != dv:
                        triggered = True
                        break
                if triggered:
                    break
            if triggered:
                triggered_ctrls.append(ctrl)
        RIG_LOG.debug("##VARCHECK triggered_ctrls", triggered_ctrls)

        # Get control attr (xform) info
        for ctrl in triggered_ctrls:
            # # - Get new xform info  # :note: This can be used for translation, but rotation gives diff results
            # drive_t = ctrl.drv_grp.xform(q=True, t=True, ws=True)
            # drive_r = ctrl.drv_grp.xform(q=True, ro=True, ws=True)
            # ctrl_t = ctrl.control.xform(q=True, t=True, ws=True)
            # ctrl_r = ctrl.control.xform(q=True, ro=True, ws=True)
            
            # - Create temp locators
            drive_loc = i_node.create("locator", n="driveX")  # ctrl.drv_grp + "_X"
            ctrl_loc = i_node.create("locator", n="ctrlX")  # ctrl.control + "_X"
            i_node.copy_pose(ctrl.drv_grp, drive_loc)
            i_node.copy_pose(ctrl.control, ctrl_loc)
            # i_utils.delete(par1, par2)
            locs = [drive_loc, ctrl_loc]
            parent = ctrl.top_tfm.relatives(0, p=True)
            if parent and i_control.check_is_control(parent):
                parent_loc = i_node.create("locator", n="parX")  # ctrl.control + "_ParentX"
                locs.append(parent_loc)
                i_node.copy_pose(parent, parent_loc, attrs="trs")
                i_utils.parent(drive_loc, ctrl_loc, parent_loc)
            # - Get new xform info
            drive_t = drive_loc.xform(q=True, t=True)
            drive_r = drive_loc.xform(q=True, ro=True)
            ctrl_t = ctrl_loc.xform(q=True, t=True)
            ctrl_r = ctrl_loc.xform(q=True, ro=True)
            RIG_LOG.debug("##VARCHECK drv_grp t:", drive_t, "r:", drive_r)
            RIG_LOG.debug("##VARCHECK control t:", drive_t, "r:", drive_r)
            # - Delete locs
            i_utils.delete(locs)
            
            # - Math attrs vals
            attr_vals = []
            for tr in [[drive_t, ctrl_t], [drive_r, ctrl_r]]:
                for i in [0, 1, 2]:
                    val = round(tr[1][i], 3) - round(tr[0][i], 3)
                    attr_vals.append(round(val, 3))
            attr_vals += [round(val, 3) for val in ctrl.control.s.get()]
            attr_vals_dict = {}
            for i, trs_xyz in enumerate(["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]):
                attr_vals_dict[trs_xyz] = attr_vals[i]
            self.con_attrs_dict[ctrl] = attr_vals_dict

        # Success
        RIG_LOG.debug("##VARCHECK con_attrs_dict", self.con_attrs_dict)
        return True

    def _bake(self):
        """
        Bake face position based on queried information
        
        :return: (bool) True/False for success
        """
        for driver_attr, init_percent in self.drive_attrs_dict.items():
            RIG_LOG.debug("##VARCHECK driver_attr", driver_attr, "init_percent", init_percent)
            for ctrl, orig_attr_vals in self.con_attrs_dict.items():
                # - Vars
                drivers = [driver_attr]
                invert = 1
                r_invert = True
                this_percent = init_percent
                control = ctrl.control
                controls = [control]  # In case it's not an L or R
                control_side = control.get_side()
                lr_controls = [control] if control else []
                mirr_control = None
                if control_side == "L":
                    mirr_control = control.get_mirror(check_exists=True)
                    if mirr_control:
                        lr_controls += [mirr_control]
                mirr_driver_attr = driver_attr.replace("L_", "R_", 1)
                # - Get starting info
                if "L_" in driver_attr:
                    if control_side == "L":
                        controls = lr_controls
                        r_invert = True
                    elif control_side not in ["L", "R"]:
                        controls = [control] if control else []
                        drivers = [driver_attr, mirr_driver_attr]
                        this_percent = init_percent * 0.5
                elif "R_" in driver_attr:
                    controls = []
                elif "Left" in driver_attr:
                    controls = [control] if control else []
                    r_invert = False
                elif "Right" in driver_attr:
                    r_invert = False
                    invert = -1
                    if control_side in ["L", "R"]:
                        controls = [mirr_control] if mirr_control else []
                    else:
                        controls = [control] if control else []
                # - Check
                if not controls:
                    if control_side != "R" and not self.given_driver_attrs:
                        RIG_LOG.warn("No controls found from given '%s'. Cannot bake." % control)
                    continue
                # - 
                # controls = sorted(controls)  # Just for ease of looking at debug prints
                RIG_LOG.debug("##VARCHECK controls", controls)
                RIG_LOG.debug("##VARCHECK this_percent", this_percent)
                RIG_LOG.debug("##VARCHECK invert", invert)
                for driver_at in drivers:
                    driver_node = self.driver_attr_nodes.get(driver_at)
                    if not driver_node and driver_at.startswith("R_"):
                        driver_node = self.driver_attr_nodes.get(driver_at.replace("R_", "L_", 1))
                    for x_control in controls:
                        RIG_LOG.debug("##VARCHECK driver_at %s, driver_node %s, control %s" % (driver_at, driver_node, x_control))
                        # -- Calc inverse
                        inv = invert
                        if r_invert and x_control.get_side() == "R":
                            driver_at = driver_at.replace("L_", "R_", 1)
                            inv = -1
                        # -- Update attr vals by percent
                        new_vals = {"tx": orig_attr_vals.get("tx") * this_percent * inv,
                                    "ty": orig_attr_vals.get("ty") * this_percent,
                                    "tz": orig_attr_vals.get("tz") * this_percent,
                                    "rx": orig_attr_vals.get("rx") * this_percent,
                                    "ry": orig_attr_vals.get("ry") * this_percent * inv,
                                    "rz": orig_attr_vals.get("rz") * this_percent * inv,
                                    "sx": (orig_attr_vals.get("sx") - 1) * this_percent,
                                    "sy": (orig_attr_vals.get("sy") - 1) * this_percent,
                                    "sz": (orig_attr_vals.get("sz") - 1) * this_percent}
                        for k, v in new_vals.items():
                            new_vals[k] = round(v, 3)
                        RIG_LOG.debug("##VARCHECK orig_attr_vals:", orig_attr_vals)
                        RIG_LOG.debug("##VARCHECK new_vals:", new_vals)
                        # -- 
                        for atr, new_val in new_vals.items():
                            dv = self.attr_dv.get(atr[0])
                            channel = {"t": "trans", "r": "rot"}.get(atr[0])
                            if new_val == 0.0:
                                RIG_LOG.debug("'%s.%s' New Val is 0. Orig Val: %s. Setting and not baking." %
                                              (x_control, atr, str(orig_attr_vals.get(atr))))
                                x_control.attr(atr).set(dv)
                                continue
                            RIG_LOG.debug("'%s' found with attr values not the default. Baking." % x_control)
                            drv_grp_attr = i_attr.Attr(x_control.replace("Ctrl", "Ctrl_Drv_Grp") + "." + atr)
                            connector = drv_grp_attr.connections(scn=True)
                            ind = round(driver_node.attr(driver_at).get(), 3)
                            if not ind:
                                mirr_driver_at = driver_at.replace("Right", "Left")
                                if i_utils.check_exists(driver_node + "." + mirr_driver_at):
                                    ind = round(driver_node.attr(mirr_driver_at).get(), 3)
                            if connector:
                                connector = connector[0]
                                RIG_LOG.info("Connector found: '%s'" % connector)
                                ac_name = driver_at + "_to_" + connector.replace("_Blend", "_Anm")
                                if i_utils.check_exists(ac_name):
                                    RIG_LOG.info("AnimCurve: '%s' already exists. Updating." % ac_name)
                                    ac = i_node.Node(ac_name)
                                    for_key = ac.output.connections(p=True)[0]
                                    driver_keys = ac.key(q=True, floatChange=True)
                                    driver_dict = {}
                                    for i, k in enumerate(driver_keys):
                                        driver_dict[i] = round(k, 3)
                                    old_val = 0.0
                                    index_req = 0
                                    match = False
                                    for ki, iv in driver_dict.items():
                                        if iv == ind:
                                            match = True
                                            index_req = ki
                                            break
                                    if not match:
                                        for_key.set_key(f=ind)
                                        new_keys = ac.key(q=True, floatChange=True)
                                        new_driver_dict = {}
                                        for i, k in enumerate(new_keys):
                                            new_driver_dict[i] = round(k, 3)
                                        for new_ki, new_iv in new_driver_dict.items():
                                            if new_iv == ind:
                                                index_req = new_ki
                                    new_key = ac.key(q=True, valueChange=True)
                                    old_v = round(new_key[index_req], 3)
                                    new_v = old_v + new_val
                                    ac.key(option="over", index=(index_req, index_req), absolute=1, valueChange=new_v)
                                    if not match:
                                        ac.key_tangent(index=(index_req, index_req), inTangentType="linear", outTangentType="linear")
                                else:
                                    RIG_LOG.info("AnimCurve: '%s' does not exist. Creating." % ac_name)
                                    fresh_ac = i_node.create("animCurveUA", n=ac_name)
                                    driver_node.attr(driver_at).drive(fresh_ac.input)
                                    cur = connector.current.get() + 1
                                    in_num = connector.input.get_next_index()
                                    new_input_blend = connector + ".input[%i]" % in_num
                                    fresh_ac.output.drive(new_input_blend)
                                    new_input_blend = i_attr.Attr(new_input_blend)
                                    connector.current.set(cur)
                                    new_input_blend.set_key(f=0, v=0)
                                    new_input_blend.set_key(f=ind, v=new_val)
                                    fresh_ac.key_tangent(index=(0, 0), inTangentType="linear", outTangentType="linear")
                                    fresh_ac.key_tangent(index=(1, 1), inTangentType="linear", outTangentType="linear")
                            else:
                                cur = 3.0 + dv
                                channel_name = x_control.replace("Ctrl", channel) + atr[1].upper()
                                ac_name = driver_at + "_to_" + channel_name + "_Anm"
                                RIG_LOG.debug("AnimCurve '%s' and BlendWeighted node do not exist. Creating." % ac_name)
                                fresh_ac = i_node.create("animCurveUA", n=ac_name)
                                driver_node.attr(driver_at).drive(fresh_ac.input)
                                drv_grp_attr.set(l=False, k=True)
                                fresh_blend = i_node.create("blendWeighted", n=channel_name + "_Blend")
                                fresh_blend.current.set(cur)
                                fresh_blend_inp = fresh_blend.attr("input[0]")
                                fresh_ac.output.drive(fresh_blend_inp)
                                if atr[0] == "s":
                                    fresh_ac.output.disconnect(fresh_blend_inp)
                                    fresh_blend_inp.set(1)
                                    fresh_blend_inp = fresh_blend.attr("input[1]")
                                    fresh_ac.output.drive(fresh_blend_inp)
                                fresh_blend.output.drive(drv_grp_attr)
                                fresh_blend_inp.set_key(f=0, v=0)
                                fresh_blend_inp.set_key(f=ind, v=new_val)
                                fresh_ac.key_tangent(index=(0, 0), inTangentType="linear", outTangentType="linear")
                                fresh_ac.key_tangent(index=(1, 1), inTangentType="linear", outTangentType="linear")
                                drv_grp_attr.set(l=True)

                            x_control.attr(atr).set(dv)

        # Return success
        return True

    def run(self):
        """
        Full query in-scene info and do bake process
        
        :return: None
        """
        cmds.waitCursor(state=True)

        RIG_LOG.debug("##VARCHECK given_driver_attrs", self.given_driver_attrs)
        
        succ = self._get_face_pack_obj()
        if not succ:
            cmds.waitCursor(state=False)
            return

        succ = self._get_drivers()
        if not succ:
            cmds.waitCursor(state=False)
            return

        succ = self._get_driven()
        if not succ:
            cmds.waitCursor(state=False)
            return

        self._bake()
        cmds.waitCursor(state=False)


class FaceBakeCurvesIO(rig_nodes.AnimCurvesIO):
    """Import/Export class for FaceBake Animation Curves"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="facebakecurves_data.json", **kwargs)

    def _get(self, objects=None):
        """
        Get the data of objects to store

        :param objects: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Get bake-specific anim curves
        acs = self._get_objects(objects=objects)
        if not acs:
            return
        face_pack_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type" : "Face"})
        if not face_pack_info_node:
            self.log.warn("No face found in scene.")
            return
        face_pack_info_node = face_pack_info_node[0]
        all_face_conns = face_pack_info_node.build_objects.connections()
        all_face_acs = [conn for conn in all_face_conns if conn.node_type().startswith("animCurve")]
        # non_pack_acs = []
        # for ac in acs:
        #     if ac in all_face_acs:
        #         continue
        #     # - From any other pack? (Limbs have the SoftIk using anim curves)
        #     from_pack = rig_frankenstein_utils.get_packs_from_objs(pack_items=[ac])
        #     if from_pack:
        #         continue
        #     non_pack_acs.append(ac)
        # 
        # if not non_pack_acs:
        #     self.log.warn("No animCurves outside of face pack found.")
        #     return
        
        # Get basic anim curve info
        ac_dict = rig_nodes.AnimCurvesIO._get(self, objects=all_face_acs)
        if not ac_dict:
            return
        
        # Copy
        json_dict = {"animcurves" : ac_dict.copy(), "blends" : {}}
        
        # Add info about FaceBake-specific nodes
        for obj, obj_info in ac_dict.items():
            obj_inp = obj_info.get("input")
            obj_out = obj_info.get("output")
            obj_blends = [io.node for io in [obj_inp, obj_out] if io and io.node_type() == "blendWeighted" and io.node not in json_dict.get("blends").keys()]
            if obj_blends:
                for blend in obj_blends:
                    curr = blend.current.get()
                    inputs = {}
                    for i in [0, 1]:
                        inp_attr = "input[%i]" % i
                        if not i_utils.check_exists(blend + "." + inp_attr):
                            continue
                        inputs[inp_attr] = i_attr.Attr(blend + "." + inp_attr).get()
                    keys_info = i_node.get_keyframe_info(obj=blend)
                    output = blend.output.connections(plugs=True)[0]
                    json_dict["blends"][blend] = {"current" : curr, "inputs" : inputs, "keys" : keys_info, "output" : output}
        
        self.verbose_nodes = json_dict.get("blends").keys() + json_dict.get("animcurves").keys()
        
        # Return
        return json_dict

    def _set(self, json_info=None):
        """
        Set in-scene objects based on json info

        :param json_info: (dict) - Information from the json file (based on _get())

        :return: None
        """
        # Check
        i_utils.check_arg(json_info, "json info")
        
        # First create / update the blends
        blends_info = json_info.get("blends")
        if blends_info:
            for blend, blend_info in blends_info.items():
                # - Create
                blend = i_node.create("blendWeighted", n=blend, use_existing=True)
                # - Set Attrs
                blend.current.set(blend_info.get("current"))
                # - Input
                for inp_attr, inp_val in blend_info.get("inputs").items():
                    i_attr.Attr(blend + "." + inp_attr).set(inp_val)
                # - Output
                outp = blend_info.get("output")
                if i_utils.check_exists(outp):
                    blend.output.drive(outp)
                else:
                    self.log.warn("'%s' does not exist. Cannot drive with anim curve's ('%s') output." % (outp, blend))
                # - Keys
                i_node.set_keyframe_from_info(obj=blend, keys_info=blend_info.get("keys"))
        
        # Then create / update the anim curves (which sometimes connect to the blends)
        rig_nodes.AnimCurvesIO._set(self, json_info=json_info.get("animcurves"))

        self.verbose_nodes = json_info.get("blends").keys() + json_info.get("animcurves").keys()


def get_face_directions():
    """
    Get all of the possible direction combinations for face positioning
    
    :return: (iMimic) of direction full names. Attrs available:
    - "ud_dir" : (list) - Up/Down Direction
    - "lr_dir": (list) - Left/Right Direction
    - "io_dir": (list) - In/Out Direction
    - "imo_attrs": (list) - In/Mid/Out Direction
    - "imo_ud_attrs": (list) - In/Mid/Out/Up/Down Direction
    - "imo_udio_attrs": (list) - In/Mid/Out/Up/Down/Up_InMidOut/Down_InMidOut Direction
    - ""ul_imo_ud_attrs: (list) - Upr/Lwr/In/Mid/Out Direction
    """
    ud_dir = ["Up", "Down"]
    lr_dir = ["Left", "Right"]
    io_dir = ["In", "Out"]

    imo_attrs = []
    imo_ud_attrs = []
    imo_udio_attrs = []
    for imo in ["In", "Mid", "Out"]:
        imo_attrs.append(imo)
        for ud in ud_dir:
            imo_ud_attrs.append(imo + "_" + ud)
        for bd in ud_dir + io_dir:
            imo_udio_attrs.append(imo + "_" + bd)

    ul_imo_ud_attrs = []
    for ul in ["Upr", "Lwr"]:
        for imo in ["In", "Mid", "Out"]:
            for ud in ud_dir:
                ul_imo_ud_attrs.append(ul + "_" + imo + "_" + ud)
    
    return i_utils.Mimic({"ud_dir" : ud_dir, "lr_dir" : lr_dir, "io_dir" : io_dir,
                          "imo_attrs" : imo_attrs, "imo_ud_attrs" : imo_ud_attrs, "imo_udio_attrs" : imo_udio_attrs,
                          "ul_imo_ud_attrs" : ul_imo_ud_attrs})


def eav_eyelash_setup(name=None, attached_curves=None):
    """
    Setup the EAV-specific eyelash system
    
    :param name: (str) - (optional) Base name for created objects. If not defined, uses first attached_curves.
    :param attached_curves: (list) - (optional) Curves. If not defined, checks selection.
    
    :return: None
    """
    # :note: Intended to first use rig_nodes.dupe_attach_curves()

    # Get attached curves
    if not attached_curves:
        attached_curves = i_utils.check_sel(fl=True)
        if not attached_curves:
            return
    
    # Name check
    ac_par = attached_curves[0].relatives(0, p=True)
    if not name:
        if ac_par:
            name = ac_par.replace("_CurvesAttach_Grp", "")
        else:
            name = attached_curves[0].split("_e")[0]
    
    # Loft attached curves
    unq_name = i_node.get_unique_name(name + "_Loft", keep_suffix="_Loft")
    loft = i_node.create("loft", attached_curves, n=unq_name)[0]
    
    # Follicles
    loft_surfacepoints = i_utils.ls(loft + ".sf[0][*]", fl=True)
    follicle_things = i_node.create_follicles(loft, iterations=len(loft_surfacepoints), start_u_value=0, v_value=0, spread_v=True)
    follicles = follicle_things[1]
    # i_utils.select(loft_surfacepoints)
    # mel.eval("createHair 8 8 10 0 0 0 0 5 0 2 2 2;")  # Create NURBS curves with "At selected surface points/faces" and "Static"

    # Joints
    foll_jnt_grp = i_node.create("transform", n=name + "_Foll_Jnt_Grp")
    i_utils.select(cl=True)
    for foll in follicles:
        i_utils.select(cl=True)
        jnt = i_node.build_at_center(objects=foll, name=foll.replace("_Flc", "_Jnt"), build_type="joint", parent_under=False, average_center=False)
        i_constraint.constrain(foll, jnt, as_fn="parent", mo=False)
        i_constraint.constrain(foll, jnt, as_fn="scale", mo=False)
        jnt.set_parent(foll_jnt_grp)
    
    # Find the dupe curves from attached curves
    att_curve_create = attached_curves[0].create.connections()[0]
    dupe_curves = att_curve_create.connections(s=True, d=False)
    dupe_crv_grp = dupe_curves[0].relatives(0, p=True)
    
    # Cleanup
    main_grp = i_node.create("transform", n=name + "_Setup_Grp")
    i_utils.parent([ac_par, dupe_crv_grp, follicle_things[0], foll_jnt_grp, loft], main_grp)


def eav_controls_create(locators=None, do_create_locators=False):
    """
    Create the control setup for EAV faces

    :param locators: (list) - (optional) Existing locators to use in creation. If not defined, checks selection.
    :param do_create_locators: (bool) - Create locators if none defined or found?

    :note: Must either have locators defined/selected or do_create_locators set to True

    :return: None
    """

    def create_locators():
        """
        Create the locators
        :return: (list of iNodes) - Locators created
        """
        default_loc_info_path = rig_io.tracked_data_path + "/face_locators.json"
        loc_data = io_utils.read_file(path=default_loc_info_path)

        if not loc_data:
            i_utils.error("No Face Locator Data found at %s." % default_loc_info_path, dialog=True)
            return

        locators = []
        for loc in loc_data.keys():
            loc_nm = loc
            if i_utils.check_exists(loc):
                RIG_LOG.warn("Name of locator (%s) already exists. Adding '_NEW' Suffix." % loc_nm)
                loc_nm += "_NEW"
            locator = i_node.create("locator", n=loc_nm)
            locator.xform(ws=True, m=loc_data.get(loc))
            locator.set_parent(loc_grp)
            locators.append(locator)

        return locators

    def create_circle_controls(locator=None):
        """
        Create controls for locator

        :param locator: (iNode) - Locator to create controls for

        :return: (list) - Created items [OuterCircleOffsetGroup (iNode), OuterCircle (iNode), InnerCircle (iNode)]
        """
        outer_radius = 0.05

        origin_nm = "Origin" if not i_utils.is_eav else "Oragin"  # :note: EAV needs typo to match convention

        # inner circle
        inner_circle = i_node.create("circle", n=locator + "_Gimbal_Ctrl_%s" % origin_nm, radius=outer_radius / 2,
                                     constructionHistory=False)
        inner_circle_shape = inner_circle.relatives(0, s=True)
        inner_circle_shape.overrideEnabled.set(1)
        inner_circle_shape.overrideColor.set(17)

        # inner circle groups
        inner_cns_grp = i_node.create("group", inner_circle,
                                      n=inner_circle.name_short().replace("_%s" % origin_nm, "_Cns_%s" % origin_nm))
        inner_ofs_grp = i_node.create("group", inner_cns_grp, n=inner_circle.name_short().replace("_%s" % origin_nm, "_Offset_Grp_%s" % origin_nm))

        # outer circle
        outer_circle = i_node.create("circle", n=locator + "_Ctrl_%s" % origin_nm, radius=outer_radius, constructionHistory=False)
        outer_circle_shape = outer_circle.relatives(0, s=True)
        outer_circle_shape.overrideEnabled.set(1)
        outer_circle_shape.overrideColor.set(13)

        # outer circle groups
        inner_ofs_grp.set_parent(outer_circle, r=True)
        outer_cns_grp = i_node.create("group", outer_circle,
                                      n=outer_circle.name_short().replace("_%s" % origin_nm, "_Cns_%s" % origin_nm))
        outer_ofs_grp = i_node.create("group", outer_cns_grp, n=outer_circle.name_short().replace("_%s" % origin_nm, "_Offset_Grp_%s" % origin_nm))

        # control attr extras
        for ctrl in [inner_circle, outer_circle]:
            ctrl.rotateOrder.set(cb=True)
            ctrl.visibility.set(k=False, l=True)
            i_attr.create(ctrl, ln="ShapeCode", dt="string", dv="D2Circle")

        # snap to locator
        source_m = locator.xform(q=True, ws=True, m=True)
        outer_ofs_grp.xform(ws=True, m=source_m)

        # parent top group
        outer_ofs_grp.set_parent(origin_grp)

        # return
        return [outer_ofs_grp, outer_circle, inner_circle]

    def create_joint(locator=None):
        """
        Create joint for locator

        :param locator: (iNode) - Locator to create joint for

        :return: (iNode) joint
        """
        # create
        jnt = i_node.create("joint", n=locator + "_Jnt", radius=0.2)
        jnt.set_parent(jnt_grp)

        # snap to locator
        source_m = locator.xform(q=True, ws=True, m=True)
        jnt.xform(ws=True, m=source_m)

        # return
        return jnt

    # Check
    if not do_create_locators and not locators:
        locators = i_utils.check_sel(raise_error=False)
        if not locators:
            i_utils.error("No locators selected. 'Create Locators' option not on.", dialog=True)
            return

    # Create groups
    origin_nm = "Origin" if not i_utils.is_eav else "Oragin"  # :note: EAV needs typo to match convention
    etc_grp = "etc_grp"
    if not i_utils.check_exists(etc_grp):
        etc_grp = i_node.create("transform", n=etc_grp)
    loc_grp = "Face_Locators"
    if not i_utils.check_exists(loc_grp):
        loc_grp = i_node.create("transform", n=loc_grp)
        loc_grp.set_parent(etc_grp)
    xtra_grp = "Face_Xtra_Grp"
    if not i_utils.check_exists(xtra_grp):
        xtra_grp = i_node.create("transform", n=xtra_grp)
        xtra_grp.set_parent(etc_grp)
    jnt_grp = "Face_Jnts"
    if not i_utils.check_exists(jnt_grp):
        jnt_grp = i_node.create("transform", n=jnt_grp)
        jnt_grp.set_parent(xtra_grp)
    origin_grp = "%s_Ctrls" % origin_nm
    if not i_utils.check_exists(origin_grp):
        origin_grp = i_node.create("transform", n=origin_grp)
        origin_grp.set_parent(xtra_grp)
    xtra_nonorigin_grp = "Xtra_Face_Ctrls"
    if not i_utils.check_exists(xtra_nonorigin_grp):
        xtra_nonorigin_grp = i_node.create("transform", n=xtra_nonorigin_grp)
        xtra_nonorigin_grp.set_parent(etc_grp)

    # Create locators
    if do_create_locators:
        locators = create_locators()

    # Check
    if not locators:
        i_utils.error("No locators found or created.", dialog=True)
        return

    # Loop through locators
    for loc in locators:
        # Parent locator
        loc_par = loc.relatives(p=True)
        if not loc_par or loc_grp != loc_par:
            loc.set_parent(loc_grp)

        # Create joint
        jnt = create_joint(locator=loc)

        # Add control hierachy
        top_grp_origin, outer_control_origin, inner_control_origin = create_circle_controls(locator=loc)

        # Constrain inner_circle > jnt
        i_constraint.constrain(inner_control_origin, jnt, mo=True, as_fn="parent")
        i_constraint.constrain(inner_control_origin, jnt, mo=True, as_fn="scale")

        # Duplicate control structure
        top_grp_dup = top_grp_origin.duplicate(n=top_grp_origin.replace("_%s" % origin_nm, ""))[0]
        dup_nodes = top_grp_dup.relatives(ad=True, type="transform")
        inner_control_dup = None
        outer_control_dup = None
        for dup in dup_nodes:
            dup.rename(dup.split("|")[-1].split("_%s" % origin_nm)[0])
            if dup.name_short().endswith("_Ctrl"):
                if dup.name_short().endswith("_Gimbal_Ctrl"):
                    inner_control_dup = dup
                else:
                    outer_control_dup = dup
        top_grp_dup.set_parent(xtra_nonorigin_grp)

        # Drive original controls with duplicate
        for trs in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            inner_control_dup.attr(trs).drive(inner_control_origin + "." + trs)
            outer_control_dup.attr(trs).drive(outer_control_origin + "." + trs)


def eav_eyelash_controls(follicles=None, control_size=4):
    """
    Create EAV Eyelash Controls

    :param follicles: (list of iNodes) - (optional) Follicles to use. If not defined, checks selection
    :param control_size: (float, int) - Size of the created controls

    :return: None
    """
    # Check
    if not follicles:
        follicles = i_utils.check_sel()
        if not follicles:
            return

    # Vars
    controls = []
    jnts = []

    for flc in follicles:
        # Create joint
        i_utils.select(cl=True)  # yay maya
        jnt = i_node.create("joint", n=flc.replace("Flc", "Jnt"))
        i_utils.select(cl=True)  # yay maya
        # - Drive joint
        flc.t.drive(jnt.t)
        # - Offset groups
        jnt_cns_grp = jnt.create_zeroed_group(group_name=flc.replace("Flc", "Cns_Grp"))
        jnt_off_grp = jnt_cns_grp.create_zeroed_group(group_name=jnt_cns_grp.replace("Cns", "Offset"))
        jnt_zer_grp = jnt_off_grp.create_zeroed_group(group_name=jnt_off_grp.replace("Offset", "Zero"))
        jnts.append(jnt_zer_grp)

        # Create control
        ctrl = i_node.create("control", control_type="2D Pin Circle", color="yellow", size=control_size,
                             name=flc.replace("Flc", "Ctrl"), with_gimbal=False, position_match=jnt_zer_grp)
        controls.append(ctrl.top_tfm)
        # - Connect control
        flc.t.drive(ctrl.top_tfm.t)
        ctrl.control.t.drive(jnt_off_grp.t)
        ctrl.control.r.drive(jnt.r)
        ctrl.control.s.drive(jnt.s)

    # Connect follicles to Head
    head_control = ""
    for head in ["Head_Gimbal_Ctrl", "head_2_sub_ctrl"]:
        if i_utils.check_exists(head):
            head_control = i_node.Node(head)
    if head_control:
        for flc in follicles:
            r_driver = flc.r.connections()
            flc.r.disconnect()
            i_constraint.constrain(head_control, flc, mo=True, as_fn="orient")
    else:
        RIG_LOG.warn("Head control not found in scene. Connect to follicles manually.")

    # Cleanup
    eyelash_grp = i_node.create("group", controls, n="Eye_Lash_Grp")
    i_node.create("group", jnts, n="Eye_Lash_Jnt_Grp")
    skull_control = "Skull_Ctrl"
    if i_utils.check_exists(skull_control):
        eyelash_grp.set_parent(skull_control)

