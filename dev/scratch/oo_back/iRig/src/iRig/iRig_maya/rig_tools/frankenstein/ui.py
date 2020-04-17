from QtCompat.QtWidgets import *
from QtCompat.QtGui import *
from QtCompat.QtCore import *
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import collections
import traceback

import tool_panel
import qt_utils
import icon_api.node as i_node
import icon_api.utils as i_utils
import logic.py_types as logic_py

from rig_tools.frankenstein import RIG_F_LOG
import maya_ui.code_snippet as cs

import rig_tools.utils.io as rig_io
import rig_tools.frankenstein.utils as rig_frankenstein_utils
import rig_tools.frankenstein.core.code as rig_code_build


bold_font = QFont()
bold_font.setBold(True)

italic_font = QFont()
italic_font.setItalic(True)

def separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator


class Frankenstein_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(Frankenstein_Widget, self).__init__(parent)

        # Vars
        overlay_img = "rig/rig_overlay_rightclick.png"
        
        ################################ BUILD SECTION

        # Create layout
        build_layout = QHBoxLayout()

        # Section Label
        build_sect_label = QLabel("Build")
        build_sect_label.setFont(bold_font)
        build_sect_label.setAlignment(Qt.AlignCenter)
        build_sect_label.setContentsMargins(0, 0, 0, 0)
        build_sect_label.setToolTip(str("Build Packs / Frankenbits"))
        self.main_layout.addWidget(build_sect_label)
        
        # Pack Dropdown
        # - Get options
        pack_options = ["---Choose a Pack Type---"]
        # -- Frankenstein
        self.build_packs = rig_frankenstein_utils.get_all_pack_options()
        self.build_packs["Code"] = None  # Manually add bc it can't be inspected like normal packs bc the structure is different
        pack_options += sorted(self.build_packs.keys())
        # -- Watson (temporary until can remove legacy)
        w_packs = ["Simple Neck", "Simple Head", "Clav", "Simple Hand", "Eye", "Wheel", "Simple Spine", "IK FK Spine",
                   "Arm", "Leg", "Cable", "Dynamic Chain", "Foot", "Python", "Ribbon"]
        pack_options += ["---Watson---"] + sorted(["W: " + pk for pk in w_packs])
        # -- Hive (temporary until can remove legacy)
        h_packs = ["Squash", "Wings", "Muscles", "Ribbon"]
        pack_options += ["---Hive---"] + sorted(["H: " + pk for pk in h_packs])
        # -- Multi-Packs
        # ---- Frankenstein
        self.build_templates = rig_frankenstein_utils.get_all_template_options(ignore=["character", "prop", "set", "vehicle"])
        pack_options += ["---Multi-Pack---"] + sorted(self.build_templates.keys())
        # ---- Watson (temporary until can remove legacy)
        pack_options += sorted(["W: " + tpt for tpt in ["KNG Biped", "SMO Biped", "EAV Small Biped"]])
        # ---- Goldie (temporary until can remove legacy)
        pack_options += sorted(["GB2: " + tpt for tpt in ["Dress", "Face", "Fairy Wings", "Universal Rig"]])
        # - Create dropdown
        self.type_dropdown = QComboBox()  # :TODO: rename self.build_pack_dropdown
        self.type_dropdown.addItems(pack_options)
        self.type_dropdown.setCurrentIndex(0)
        self.type_dropdown.setToolTip(str("Pack type to build."))
        self.type_dropdown.setMinimumWidth(80)
        self.type_dropdown.currentIndexChanged.connect(self.__update_pack_dropdown)
        build_layout.addWidget(self.type_dropdown)
        
        # Pack Side
        self.side_dropdown = QComboBox()
        self.sides = ["---"] + i_node.side_options
        self.side_dropdown.addItems(self.sides)
        self.side_dropdown.setCurrentIndex(0)
        self.side_dropdown.setToolTip("Side of pack to build.")
        self.side_dropdown.setMinimumWidth(40)
        self.pack_side = self.side_dropdown.currentText()
        build_layout.addWidget(self.side_dropdown)
        
        # Pack Description
        self.description_txt = QLineEdit("Description")
        self.description_txt.setToolTip("Description of pack to build.")
        self.pack_desc = self.description_txt.text()
        build_layout.addWidget(self.description_txt)
        
        # Reset Defaults button
        self.reset_name_button = QPushButton("R")
        self.reset_name_button.setToolTip("Set side and description to pack's default values.")
        self.reset_name_button.clicked.connect(partial(self.__update_pack_dropdown, True))
        build_layout.addWidget(self.reset_name_button)

        # Button layout
        build_button_layout = QHBoxLayout()
        alpha = 100
        
        # Build Pack button
        rcl_pack = collections.OrderedDict()
        rcl_pack["Assign own joints as Pack"] = partial(self.build_pack, True)
        rcl_pack["Force Re-orient Pack Joints"] = partial(self.force_reorient)
        rcl_pack["Change Pack (Selected)"] = partial(tool_panel.PopOff, None, ChangePack_Widget)
        rcl_pack["Delete Pack"] = partial(self.delete_pack)
        build_pack_button = tool_panel.IconButton(icon="rig/rig_lightning.png", icon_rgb=[237, 227, 69, alpha],
                                                  label="Build\nPack", command=partial(self.build_pack),
                                                  right_click_buttons=rcl_pack,
                                                  overlay_image=overlay_img,
                                                  tool_tip="Build Pack (joints setup).")
        build_button_layout.addWidget(build_pack_button)
        
        # Mirror Pack button
        rcl_mirror = collections.OrderedDict()
        rcl_mirror["Connect Symmetry"] = partial(self.mirror_symmetry, True)
        rcl_mirror["Break Symmetry"] = partial(self.mirror_symmetry, False)
        rcl_mirror["Delete Mirrored"] = partial(self.mirror_pack, False)
        mirror_button = tool_panel.IconButton(icon="rig/rig_pack_mirror.png", icon_rgb=[237, 165, 69, alpha],
                                              label="Mirror\nPack", command=partial(self.mirror_pack),
                                              right_click_buttons=rcl_mirror,
                                              overlay_image=overlay_img,
                                              tool_tip="Mirror selected pack (with symmetry).")
        build_button_layout.addWidget(mirror_button)
        
        # Build Bits button
        build_bits_button = tool_panel.IconButton(icon="rig/rig_pack_build.png", icon_rgb=[69, 226, 237, alpha],
                                                  label="Build\nFrankenbits", command=partial(self.build_bits),
                                                  tool_tip="Build Frankenbit for selected Pack (or Pack joints).", )
        build_button_layout.addWidget(build_bits_button)
        
        # Deconstruct button
        decon_button = tool_panel.IconButton(icon="rig/rig_pack_decon.png", icon_rgb=[218, 69, 69, alpha],
                                             label="Deconstruct\nto Packs", command=partial(self.deconstruct),
                                             tool_tip="Break down selected Frankenbits to Pack stage.")
        build_button_layout.addWidget(decon_button)
        
        # Reconstruct button
        recon_button = tool_panel.IconButton(icon="rig/rig_pack_recon.png", icon_rgb=[82, 237, 69, alpha],
                                             label="Reconstruct\nFrankenbits", command=partial(self.reconstruct),
                                             tool_tip="Build selected Packs into Frankenbits and import available IO data.")
        build_button_layout.addWidget(recon_button)
        
        # Add to layout
        self.main_layout.addLayout(build_layout)
        self.main_layout.addLayout(build_button_layout)

        ################################ SEPARATOR

        # Separator
        stitch_sect_line = QFrame()
        stitch_sect_line.setFrameShape(QFrame.HLine)
        stitch_sect_line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(stitch_sect_line)

        ################################ STITCH SECTION

        # Create layout
        stitch_layout = QVBoxLayout()

        # Section Label
        stitch_sect_label = QLabel("Stitch")
        stitch_sect_label.setFont(bold_font)
        stitch_sect_label.setAlignment(Qt.AlignCenter)
        stitch_sect_label.setContentsMargins(0, 0, 0, 0)
        stitch_sect_label.setToolTip(str("Connect Packs or Frankenbits"))

        # Labels
        stitch_label_layout = QHBoxLayout()
        parent_label = QLabel("Parent")
        parent_label.setAlignment(Qt.AlignLeft)
        parent_label.setMaximumWidth(200)
        parent_label.setContentsMargins(0, 0, 0, 0)
        stitch_label_layout.addWidget(parent_label)
        
        child_label = QLabel("Child")
        child_label.setAlignment(Qt.AlignLeft)
        child_label.setMaximumWidth(200)
        child_label.setContentsMargins(0, 0, 0, 0)
        stitch_label_layout.addWidget(child_label)

        # Options/Buttons
        stitch_button_layout = QHBoxLayout()

        # Parent dropdown
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("--- Parent ---")
        self.parent_combo.setMinimumWidth(150)
        self.parent_combo.setContentsMargins(0, 0, 0, 0)
        stitch_button_layout.addWidget(self.parent_combo)

        # Parent Sel Button
        parent_sel_button = QPushButton("S")
        s_color = tool_panel.OverlayColors.blue_mid
        parent_sel_button.setStyleSheet("background-color: rgb(%i, %i, %i, 150)" % (s_color[0], s_color[1], s_color[2]))
        parent_sel_button.clicked.connect(partial(self.refresh_stitch, self.parent_combo, False))
        parent_sel_button.setToolTip(str("Load selected Pack or Frankenbit as the Parent"))
        parent_sel_button.setContentsMargins(0, 0, 0, 0)
        stitch_button_layout.addWidget(parent_sel_button)

        # Arrow
        arrow = QLabel("->")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setMinimumWidth(30)
        stitch_button_layout.addWidget(arrow)

        # Child dropdown
        self.child_combo = QComboBox()
        self.child_combo.addItem("--- Child ---")
        self.child_combo.setMinimumWidth(150)
        self.child_combo.setContentsMargins(0, 0, 0, 0)
        stitch_button_layout.addWidget(self.child_combo)

        # Child Sel Button
        child_sel_button = QPushButton("S")
        child_sel_button.setStyleSheet("background-color: rgb(%i, %i, %i, 150)" % (s_color[0], s_color[1], s_color[2]))
        child_sel_button.clicked.connect(partial(self.refresh_stitch, self.child_combo, False))
        child_sel_button.setToolTip(str("Load selected Pack or Frankenbit as the Child"))
        child_sel_button.setContentsMargins(0, 0, 0, 0)
        stitch_button_layout.addWidget(child_sel_button)

        # Stitch button
        stitch_rcl = collections.OrderedDict()
        stitch_rcl["Unstitch (Selected or defined packs)"] = partial(self.unstitch)
        stitch_rcl["Prompt Stitch Info (Selected pack)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.get_stitch_data(prompt=True)"
        stitch_rcl["Prompt Stitch Check (Selected pack)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.check_acceptable_stitch(prompt=True)"
        stitch_rcl["Force Restich (Selected pack)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.force_restitch_sel()"
        stitch_button = tool_panel.IconButton(icon="rig/rig_stitch.png", resize=[30, 30], no_padding=True,
                                              tool_tip="Stitch (Connect) the chosen Parent to drive the chosen Child.",
                                              command=partial(self.stitch), right_click_buttons=stitch_rcl,
                                              overlay_image=overlay_img, hotkey_label="Stitch")
        stitch_button_layout.addWidget(stitch_button)

        # Refresh button
        refresh_button = tool_panel.IconButton(icon="rig/rig_search_replace.png", icon_rgb=tool_panel.OverlayColors.red,
                                               command=partial(self.refresh_stitches), resize=[20, 20],
                                               tool_tip="Refresh pack options in stitches menus.", no_padding=True,
                                               hotkey_label="Refresh Packs")
        stitch_button_layout.addWidget(refresh_button)

        # Add to stitch layout
        stitch_layout.addLayout(stitch_label_layout)
        stitch_layout.addLayout(stitch_button_layout)

        # Load dropdowns with scene packs
        self.refresh_stitches()

        # Add to window
        self.main_layout.addWidget(stitch_sect_label)
        self.main_layout.addLayout(stitch_layout)


    def __update_pack_dropdown(self, force_reset=False):
        # Vars
        pack_type = self.type_dropdown.currentText()
        tt = "Pack type to build."
        pack_is_legacy = ":" in pack_type and pack_type.split(":")[0] in ["W", "H", "GB2"]
        pack_is_template = pack_type in self.build_templates.keys()
        
        # Check not a divider option
        if pack_type.startswith("---"):
            return 

        # Color for legacy to really flag it.
        ss = ""
        enable = True
        if pack_is_legacy:
            tt += "\n\nThis pack is legacy. Are you sure? Did you check with your lead?"
            ss = "QComboBox {background-color: maroon} QToolTip {color: white} QToolTip {background-color: maroon}"
            enable = False
        elif pack_is_template:
            tt += "Template type to build."
            enable = False
            self.side_dropdown.setCurrentIndex(0)
            self.description_txt.setText("Description")
        self.type_dropdown.setStyleSheet(ss)
        for ui_obj in [self.side_dropdown, self.description_txt, self.reset_name_button]:
            ui_obj.setEnabled(enable)
        
        # Get tooltip
        pack_defaults = self.build_packs.get(pack_type)
        if pack_defaults and pack_type in self.build_packs.keys():  # Ex of no pack_defaults: Code Pack
            default_joints = pack_defaults.get("joint_names")
            min_length = pack_defaults.get("length_min")
            req_joints = default_joints[:min_length]
            tt += "\nIf using own joints, select in order of: %s." % ", ".join(i_utils.convert_data(req_joints))
            if len(default_joints) != len(req_joints):
                opt_joints = list(set(default_joints) - set(req_joints))
                tt += "\n(Optional) Additionally select: %s." % ", ".join(i_utils.convert_data(opt_joints))
        
        # Set Tooltip
        self.type_dropdown.setToolTip(tt)
        
        # End for non-Frankenstein Packs
        if pack_is_template or pack_is_legacy or not pack_defaults:
            return 
        
        # Update Description to default
        current_description = self.description_txt.text()
        if not current_description or current_description == "Description" or force_reset:
            pack_description = pack_defaults.get("description", "Description")
            self.description_txt.setText(str(pack_description))
        
        # Update Side to default
        current_side = self.side_dropdown.currentText()
        if current_side == "---" or force_reset:
            pack_side = pack_defaults.get("side", "---")  # Some default to no side
            side_index = self.side_dropdown.findText(pack_side)
            self.side_dropdown.setCurrentIndex(side_index)
    
    def build_pack(self, use_custom_joints=False):
        # Get vars
        pack_type = self.type_dropdown.currentText()
        pack_is_legacy = ":" in pack_type and pack_type.split(":")[0] in ["W", "H", "GB2"]

        # Check not a divider option
        if pack_type.startswith("---"):
            i_utils.error("'%s' is not an actual pack or template." % pack_type, dialog=True)
            return

        # Watson / Hive
        if pack_is_legacy:
            rig_frankenstein_utils.legacy_build_pack(pack=pack_type)
            return

        # Code Pack? Just open UI
        if pack_type == "Code":
            tool_panel.PopOff(widget=CodePack_Widget)
            return
        
        # Frankenstein
        side = self.side_dropdown.currentText()
        if side == "---":
            side = ""
        description = self.description_txt.text()
        if description == "Description":
            description = ""
        
        # Prompt for details
        build_details_widget = BuildDetails_Widget(parent=self)
        build_details_widget.side = side
        build_details_widget.description = description
        build_details_widget.build_type = pack_type
        build_details_widget.use_custom_joints = use_custom_joints
        build_details_widget.closeEvent = partial(self.details_close, BuildDetails_Widget)
        build_details_widget.ui()

    def details_close(self, widget, event):
        self.description_txt.setText("Description")
        self.side_dropdown.setCurrentIndex(0)
        self.refresh_stitches()
        # widget.closeEvent(widget, event)  # Doesn't work but appears to not be needed anyway

    def force_reorient(self):
        # Get Sel Pack(s)
        sel_pack_infos = rig_frankenstein_utils.get_pack_from_obj_sel(dialog_error=True)
        if not sel_pack_infos:
            return
        
        # Do it
        for pi in sel_pack_infos:
            rig_frankenstein_utils.force_reorient_base_joints(pack_info_node=pi)

    def delete_pack(self):
        # Get Sel Pack(s)
        sel_pack_infos = rig_frankenstein_utils.get_pack_from_obj_sel(dialog_error=True)
        if not sel_pack_infos:
            return

        # Do it
        for sel in sel_pack_infos:
            rig_frankenstein_utils.delete_pack(pack_info_node=sel, prompt=True)

    def refresh_stitch(self, dropdown=None, clear=True, load_sel=True):
        # Clear
        if clear:
            default = {self.parent_combo: "--- Parent ---", self.child_combo: "--- Child ---"}.get(dropdown)
            dropdown.clear()
            dropdown.addItem(default)

        # Get all in-scene packs
        pack_infos = rig_frankenstein_utils.get_scene_packs(check_sel=load_sel, dialog_error=False)
        if not pack_infos:
            return

        # Get selected pack
        sel_pack_info = None
        if load_sel:
            sel_pack_info = pack_infos[0]
        sel_pack_opt = None

        # Add all options to menu
        current_dropdown_items = [dropdown.itemText(i) for i in range(dropdown.count())]
        add_items = []
        for info_node in pack_infos:
            pack_display_name = info_node.replace("_Info", "")
            if not (current_dropdown_items and pack_display_name in current_dropdown_items):
                add_items.append(pack_display_name)
            # - Is this pack selected?
            if load_sel and info_node == sel_pack_info:
                sel_pack_opt = pack_display_name
        # - Do the actual adding
        if add_items:
            dropdown.addItems(sorted(add_items))

        # Choose selected
        if load_sel and sel_pack_opt:
            sel_pack_opt_i = dropdown.findText(sel_pack_opt)
            dropdown.setCurrentIndex(sel_pack_opt_i)

    def refresh_stitches(self):
        self.refresh_stitch(dropdown=self.parent_combo, load_sel=False)
        self.refresh_stitch(dropdown=self.child_combo, load_sel=False)

    def mirror_pack(self, create=True, symmetry=True):
        success = rig_frankenstein_utils.mirror_packs_sel(create=create, symmetry=symmetry)
        if not success:
            return 
        self.refresh_stitches()

    def mirror_symmetry(self, attach=True):
        driving_packs = rig_frankenstein_utils.get_pack_from_obj_sel()
        if not driving_packs:
            i_utils.error("Frankenstein Pack(s) not selected. Cannot mirror symmetry.", dialog=True)
            return
        
        if attach:
            for pack in driving_packs:
                rig_frankenstein_utils.mirror_symmetry_attach(pack_info_node=pack)
        else:  # detach
            for pack in driving_packs:
                rig_frankenstein_utils.mirror_symmetry_detach(pack_info_node=pack, clear_data=True)

    def prebuild_bits(self):
        # move the cog guide to where the spline root is, not ideal... but Frank sucks.
        pack_type = self.type_dropdown.currentText()
        if pack_type == 'Biped':
            pos = cmds.xform('C_Spine_Spine01', q=True, ws=True, t=True)
            cmds.xform('COG', ws=True, t=pos)

    def build_bits(self):
        # Get pack infos
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)
        pack_info_nodes = rig_frankenstein_utils.get_scene_packs(dialog_error=False, check_sel=True, search={"bit_built" : False})
        
        # Building from template?
        scene_template = rig_frankenstein_utils.get_scene_template()
        if scene_template in ["character", "prop", "set", "vehicle"]:
            scene_template = None
        template = rig_frankenstein_utils.get_template_object(scene_template=scene_template, raise_error=False)
        
        # Also build mirrored? (If selected)
        if sel and pack_info_nodes:
            sym_mirrored_pis = []
            for pi in pack_info_nodes:
                mirrored_info = rig_frankenstein_utils.get_mirrored_connections(pi, dialog_error=False, raise_error=False)
                if mirrored_info:
                    mirrored_obj = mirrored_info[1]
                    mirrored_pin = mirrored_obj.pack_info_node
                    if mirrored_obj.is_mirror_sym and mirrored_pin != pi:
                        sym_mirrored_pis.append(mirrored_pin)
            if sym_mirrored_pis:
                do_it = i_utils.message(title="Found Mirrored", button=["Yes", "No", "Cancel"], dismissString="Cancel", 
                                        message="Found Symmetrically mirrored packs:\n\n- %s" % "\n- ".join([mpi.name for mpi in sym_mirrored_pis])
                                        + "\n\nAlso build mirrored bits?")
                if do_it == "Cancel":
                    return
                if do_it == "Yes":
                    pack_info_nodes += sym_mirrored_pis
        
        # Prep Progress Bar
        # - Find Maya's main bar
        main_progress_bar = mel.eval('$tmp = $gMainProgressBar')
        # - Clear existing progress
        cmds.progressBar(main_progress_bar, e=True, endProgress=True)
        main_progress_bar = mel.eval('$tmp = $gMainProgressBar')  # Redeclare to refresh?
        # - Update progress bar
        additional = 6 if template else 4
        bar_amt = additional
        if pack_info_nodes:
            bar_amt += len(pack_info_nodes)
        cmds.progressBar(main_progress_bar, e=True, beginProgress=True, isInterruptable=False,
                         status='Franken-Building ...', maxValue=bar_amt + additional)
        
        # First try and build any G (Watson/Hive) Bits. Needs to be first or else that legacy code gets cranky
        cmds.progressBar(main_progress_bar, e=True, step=1, status="Building Legacy Packs")
        g_bits = rig_frankenstein_utils.legacy_build_bits()
        if g_bits is False:  # Something failed and user was prompted. Do not continue (will return None if no packs found)
            cmds.waitCursor(state=False)
            cmds.progressBar(main_progress_bar, e=True, endProgress=True)
            return 
        
        # Get Frankenstein Packs
        if not pack_info_nodes:
            if not g_bits:
                i_utils.error("No Legacy or Frankenstein packs found to build bits.", dialog=True)
            cmds.progressBar(main_progress_bar, e=True, endProgress=True)
            return
        
        # Get pack objects and in building order
        pack_objs = []
        cog_obj = None
        for info_node in sorted(pack_info_nodes):
            pack_obj = rig_frankenstein_utils.get_pack_object(info_node, non_setting=["accepted_stitch_types"])
            if pack_obj.bit_built:
                continue
            pack_objs.append(pack_obj)
            if pack_obj.build_type == "Cog":
                cog_obj = pack_obj
        if cog_obj:
            pack_objs.remove(cog_obj)
            pack_objs.insert(0, cog_obj)
        
        # Check stitches made in pack stage before spend time building bits
        accepted = True
        for pack_obj in pack_objs:
            is_good = rig_frankenstein_utils.check_acceptable_stitch(pack_obj=pack_obj, prompt=True, prompt_error_only=True)
            if not is_good:
                accepted = False
                break
        if not accepted:
            cmds.progressBar(main_progress_bar, e=True, endProgress=True)
            return
        
        # Unstitch All
        cmds.progressBar(main_progress_bar, e=True, step=1, status="Unstitching")
        for pack_obj in pack_objs:
            pack_obj.unstitch_pack(raise_error=False)
            # succ = pack_obj.unstitch_pack(raise_error=False, dialog_error=True)
            # if not succ:
            #     return
        
        # Run Template Pre-Bits
        if template:
            # - Update progress bar
            cmds.progressBar(main_progress_bar, e=True, step=1, status="Template Pre-Build")
            # - Do it
            template.pre_bits()
        
        # Create Frankenstein Bits
        for pack_obj in pack_objs:
            # - Update progress bar
            cmds.progressBar(main_progress_bar, e=True, step=1, status="Building %s" % pack_obj.base_name)
            # - Create
            pack_obj.do_stitch = False  # Override because stitching is all happening at once
            pack_obj.create_bit()
        
        # Restitch All
        cmds.progressBar(main_progress_bar, e=True, step=1, status="Stitching")
        for pack_obj in pack_objs:
            pack_obj.stitch_bit(raise_error=False)
            # succ = pack_obj.stitch_bit(raise_error=False, dialog_error=True)
            # if not succ:
            #     return
        
        # Run Template Post-Bits
        if template:
            # - Update progress bar
            cmds.progressBar(main_progress_bar, e=True, step=1, status="Template Post-Build")
            # - Do it
            template.post_bits()
        
        # Frame
        cmds.progressBar(main_progress_bar, e=True, step=1, status='Frankenstein Cleaning Up ...')
        i_utils.focus(type="joint")

        # Update UI
        self.refresh_stitches()
        
        # End
        cmds.progressBar(main_progress_bar, e=True, endProgress=True)
        

    def deconstruct(self):
        # Get pack infos
        pack_info_nodes = rig_frankenstein_utils.get_scene_packs(dialog_error=False, check_sel=True, 
                                                                 search={"bit_built" : True, "is_mirror" : False})
        if not pack_info_nodes:
            i_utils.error("No builds found that are in the pack stage.", dialog=True)
            return

        # Are we also exporting data?
        export_data = False
        do_data = i_utils.message(title="Export Data?", message="Export scene data before deconstruct?",
                                  button=["Yes", "No", "Cancel"], dismissString="Cancel")
        if do_data == "Yes":
            export_data = True
        elif do_data == "Cancel":
            return

        # Wait Cursor
        cmds.waitCursor(state=True)

        # Export Data
        if export_data:
            i_utils.select(cl=True)
            rig_io.all_ios(action="export", force=True)
            i_utils.select(cl=True)

        # Deconstruct
        pack_info_nodes.sort()  # Do in order for mirror attaching
        RIG_F_LOG.info("Deconstructing packs:", pack_info_nodes)
        rig_frankenstein_utils.deconstruct_packs(pack_info_nodes, dialog_error=True)
        
        # Wait Cursor
        cmds.waitCursor(state=False)

    def reconstruct(self):
        # Wait Cursor
        cmds.waitCursor(state=True)

        # Build Bits
        self.build_bits()

        # Import Data
        i_utils.select(cl=True)
        rig_io.all_ios(action="import", force=True)
        i_utils.select(cl=True)

        # Wait Cursor
        cmds.waitCursor(state=False)

    def check_stitchable(self):
        # Vars
        stitchable = True
        tooltip = ""

        # Check Valid Dropdowns chosen
        # - Labels
        parent_label = self.parent_combo.currentText()
        child_label = self.child_combo.currentText()
        # - Check
        if parent_label.startswith("---") or child_label.startswith("---"):
            stitchable = False
            tooltip = "Must define both a parent and a child"
        elif parent_label == child_label:
            stitchable = False
            tooltip = "A Pack/Frankenbit cannot stitch to itself."
        else:
            for label in [parent_label, child_label]:
                if not i_utils.check_exists(label + "_Info"):
                    stitchable = False
                    tooltip = "%s does not exist.\n\nTry refreshing the stitch menus." % (label + "_Info")
                    break
        # - Failed
        if not stitchable:
            i_utils.error(tooltip, dialog=True)
            return False
        
        parent_info_node = i_node.Node(parent_label + "_Info")
        child_info_node = i_node.Node(child_label + "_Info")

        # Check that either both are packs or both are bits
        parent_obj = rig_frankenstein_utils.get_pack_object(parent_info_node)
        child_obj = rig_frankenstein_utils.get_pack_object(child_info_node)
        # if parent_obj.bit_built != child_obj.bit_built:  # Don't do this here since the stitch checks this and still stores data regardless
        #     i_utils.error("%s is a %s. %s is a %s.\n\nThey need to match in order to stitch or unstitch." %
        #                   (child_obj.pack_info_node, "bit" if child_obj.bit_built else "pack",
        #                    parent_obj.pack_info_node, "bit" if parent_obj.bit_built else "pack"),
        #                   dialog=True)
        #     return False

        # All passed
        return [parent_obj, child_obj]

    def stitch(self):
        # Check stitching / Get stitch info
        stitch_info = self.check_stitchable()
        if not stitch_info:
            return
        parent_obj, child_obj = stitch_info
        is_parent_bit = parent_obj.bit_built
        is_child_bit = child_obj.bit_built
        state_not_match = is_parent_bit != is_child_bit  # Storing the stitch data but not actually taking action?

        # Stitch Packs
        if (not is_parent_bit and not is_parent_bit) or state_not_match:
            parent_as_ask = i_utils.message(title="Parenting?",
                                            message="Which end to Parent %s to %s?" % 
                                                    (child_obj.pack_info_node, parent_obj.pack_info_node),
                                            button=["Start", "End", "Default", "Do Not Parent"])
            if parent_as_ask == "Do Not Parent":
                parent_as = False
            elif parent_as_ask in ["Start", "End"]:
                parent_as = parent_as_ask.lower()
            elif parent_as_ask == "Default":
                parent_as = None
            else:  # Cancelled
                return
            success = child_obj.stitch_pack(parent_info_node=parent_obj.pack_info_node, do_parenting=parent_as, dialog_error=True)
            if not success:
                return
        
        # Stitch Bits
        else:
            success = child_obj.stitch_bit(parent_info_node=parent_obj.pack_info_node, dialog_error=True)
            if not success:
                return

        # Cleanup
        i_utils.select(cl=True)
        i_utils.message(title="Stitched", message="Stitched %s >> %s." % (parent_obj.base_name, child_obj.base_name))

    def unstitch(self):
        # Vars
        sel_pack_info_nodes = rig_frankenstein_utils.get_pack_from_obj_sel()
        unstitch_children = False
        unstitch_parent = True
        pack_objs = []

        # Selection: All Children / Parents of that pack can be unstitched at once
        if sel_pack_info_nodes:
            pack_objs = [rig_frankenstein_utils.get_pack_object(pack_info_node) for pack_info_node in
                         sel_pack_info_nodes]
            found_msg = "Found:\n- %s" % ("\n- ".join([pack_obj.base_name for pack_obj in pack_objs]))

            do_it = i_utils.message(title="Unstitch What?", message="%s\n\nUnstitch what types of packs?\n" % found_msg,
                                    button=["Parent", "Child", "All", "Cancel"], dismissString="Cancel")
            if do_it == "Cancel":
                return
            if do_it in ["Parent", "All"]:
                unstitch_parent = True
            if do_it in ["Child", "All"]:
                unstitch_children = True

        # Specified via dropdown
        else:
            stitch_info = self.check_stitchable()
            if not stitch_info:
                return
            unstitch_parent = stitch_info[0]  # Parent object
            pack_objs = [stitch_info[1]]  # Child object
        
        if unstitch_parent in [None, False]:  # isinstance(unstitch_parent, bool) or unstitch_parent is None
            i_utils.error("No parent found for unstitching. Try selecting something from a pack/bit.", dialog=True)
            return

        # Unstitch
        par = unstitch_parent.pack_info_node if unstitch_parent is not True else None
        for pack_obj in pack_objs:
            # - Do it
            if pack_obj.bit_built:
                fn = pack_obj.unstitch_bit
            else:
                fn = pack_obj.unstitch_pack
            success = fn(parent_info_node=par, unstitch_children=unstitch_children,
                         dialog_error=True, raise_error=False, clear_data=True)
            if not success:
                return 

        # Message
        i_utils.message(title="Unstitched",
                        message="Unstitched %s." % (", ".join([pack_obj.base_name for pack_obj in pack_objs])))


class ChangePack_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(ChangePack_Widget, self).__init__(parent)
        
        # Pack Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Changing Pack:"))
        self.title_lbl = QLabel("SELECT AND REFRESH")
        self.pack_obj = None
        title_layout.addWidget(self.title_lbl)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Build Type Title
        btype_layout = QHBoxLayout()
        btype_layout.addWidget(QLabel("Build Type:"))
        self.btype_lbl = QLabel("SELECT AND REFRESH")
        btype_layout.addWidget(self.btype_lbl)
        btype_layout.setAlignment(Qt.AlignCenter)

        # Renaming
        # - Layout
        name_layout = QHBoxLayout()
        # - Side
        side_layout = QVBoxLayout()
        side_layout.addWidget(QLabel("Side"))
        self.side_dropdown = QComboBox()
        self.sides = ["---", "C", "M", "L", "R", "Fr", "Bk", "Upr", "Lwr"]
        self.side_dropdown.addItems(self.sides)
        self.side_dropdown.setCurrentIndex(0)
        self.side_dropdown.setToolTip(str("Side of pack to rename as."))
        self.side_dropdown.setMinimumWidth(40)
        side_layout.addWidget(self.side_dropdown)
        name_layout.addLayout(side_layout)
        # - Description
        description_layout = QVBoxLayout()
        description_layout.addWidget(QLabel("Description"))
        self.description_txt = QLineEdit("Description")
        self.description_txt.setToolTip(str("Description of pack to rename as."))
        self.description_txt.setMinimumWidth(150)
        description_layout.addWidget(self.description_txt)
        name_layout.addLayout(description_layout)
        
        # Prep a Details Layout
        # :note: To be populated when load a pack
        self.ui_objects = {}
        self.details_layout = QVBoxLayout()

        # Add button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        do_it_button = tool_panel.IconButton(icon="rig/rig_create.png", command=partial(self.run), #label="Change Pack",
                                             tool_tip="Change details of pack")
        button_layout.addWidget(do_it_button)
        # refresh_button = tool_panel.IconButton(icon="anm/11Replace.png", command=partial(self.load_sel), label="",
        #                                        tool_tip="Refresh UI with selected pack", resize=[20, 20], 
        #                                        icon_rgb=tool_panel.OverlayColors.blue)
        # button_layout.addWidget(refresh_button)

        # Add to layout
        self.main_layout.addLayout(title_layout)
        self.main_layout.addLayout(btype_layout)
        self.main_layout.addWidget(separator())
        self.main_layout.addLayout(name_layout)
        self.main_layout.addLayout(self.details_layout)
        self.main_layout.addLayout(button_layout)

        # Load sel into UI
        self.load_sel(error=False)

    def _get_pack(self, error=True):
        sel = rig_frankenstein_utils.get_pack_from_obj_sel(dialog_error=error)  # search={"bit_built" : False}, 
        if not sel:
            return

        if len(sel) > 1:
            if error:
                i_utils.error("Only select object from one pack.", dialog=True)
            return

        return sel[0]

    def load_sel(self, error=True):
        # Get/Check selected
        pack_info_node = self._get_pack(error=error)
        if not pack_info_node:
            return
        
        # Get pack object
        self.pack_obj = rig_frankenstein_utils.get_pack_object(pack_info_node)
        is_bit = self.pack_obj.bit_built
        is_mirror_sym = self.pack_obj.is_mirror_sym
        build_type = self.pack_obj.build_type
        defaults = rig_frankenstein_utils.get_all_pack_options().get(build_type)
        
        # Title label
        self.title_lbl.setText(self.pack_obj.base_name)
        self.btype_lbl.setText(build_type)
        
        # Name
        # - Side
        side = self.pack_obj.side
        side_i = 0
        if side in self.sides:  # Has a defined side
            side_i = self.sides.index(side)
        self.side_dropdown.setCurrentIndex(side_i)
        if is_bit:
            self.side_dropdown.setEnabled(False)
        # - Description
        desc = self.pack_obj.description
        self.description_txt.setText(desc)
        if is_bit:
            self.description_txt.setEnabled(False)
        
        # Specific Details
        # # - Clear  :TODO:
        # if self.ui_objects:
        #     for label, obj in self.ui_objects.items():
        #         obj.delete()
        
        # - Populate
        pack_prompt_infos, pack_prompt_displays = _get_prompt_info(self.pack_obj)
        # - Changeable Things
        for label, details in pack_prompt_infos.items():
            if " " in label:  # This is the nn
                label = label.replace(" ", "_").lower()
            dv = defaults.get(label)
            # - Update default value based on pack's current value
            if not hasattr(self.pack_obj, label):
                RIG_F_LOG.warn("'%s' has no attribute '%s'. Cannot add to Change UI." % (self.pack_obj.base_name, label))
                continue
            curr_value = getattr(self.pack_obj, label)
            details["value"] = curr_value
            # - Add object
            nn = " ".join([lb[0].upper() + lb[1:] for lb in label.split("_")])
            if dv == curr_value or label in ["pack_size", "ctrl_size", "joint_radius"]:
                dv = None
            obj = _add_ui_obj(label=nn, details=details, parent=self.details_layout, dv_alt=dv, display_dv_check=True)
            kw = details.get("kw", label)
            self.ui_objects[kw] = obj
            if is_bit:
                obj.setEnabled(False)
            elif is_mirror_sym and kw in ["ctrl_size", "orient_joints", "orient_joints_up_axis", "do_orient_joints", 
                                          "pack_size", "joint_radius", "ikfk_switch_mirror_offset", "ikfk_default_mode"]:
                obj.setEnabled(False)
        # - Non-Changeable Things
        self.details_layout.addWidget(separator())
        non_change_lyt = QVBoxLayout()
        non_change_lyt.setAlignment(Qt.AlignCenter)
        nc_ttl = QLabel("Non-Changeable Data (for display only):")
        nc_ttl.setFont(bold_font)
        non_change_lyt.addWidget(nc_ttl)
        for label, cls_attr in pack_prompt_displays.items():
            # - Update default value based on pack's current value
            value = getattr(self.pack_obj, cls_attr)
            if isinstance(value, (list, tuple)):
                value = ", ".join(value)
            # - Add object
            obj = QLabel("%s : %s" % (label, str(value)))
            obj.setWordWrap(True)
            non_change_lyt.addWidget(obj)
            # self.ui_objects[cls_attr] = obj
        self.details_layout.addLayout(non_change_lyt)
    
    def __decipher_ui_results(self):
        ui_obj_info = {}

        for obj_kw, obj in self.ui_objects.items():
            ui_obj_info[obj_kw] = _get_value(obj)

        return ui_obj_info

    def run(self):
        # Get pack info node
        if not self.pack_obj:
            i_utils.error("No pack object found.", dialog=True)
            return
        pack_info_node = self.pack_obj.pack_info_node
        
        # Vars
        updated_dict = {}
        
        # Name
        # - Side
        new_side = self.side_dropdown.currentText()
        if new_side == "---":
            new_side = ""
        updated_dict["side"] = new_side
        # - Description
        new_desc = self.description_txt.text()
        if new_desc == "Description":
            new_desc = ""
        updated_dict["description"] = new_desc
        
        # Prompt Info
        from_ui = self.__decipher_ui_results()
        updated_dict.update(from_ui)
        
        # Change Pack
        rig_frankenstein_utils.change_pack(pack_info_node=pack_info_node, updated_dict=updated_dict, dialog_error=True)

        # # Close Window
        # self.close()
        # # # Refresh UI
        # # self.load_sel(error=False)


class CodePack_Widget(cs.Code_Widget):
    def __init__(self, parent=None, default_code_info=None):
        super(CodePack_Widget, self).__init__(parent)

        # Find Data path to save snippets to
        self.data_path = rig_io.get_data_path()

        # Find existing code packs info
        existing_code_packs = rig_frankenstein_utils.get_scene_packs(dialog_error=False, search={"pack_type" : "Code"})
        existing_code = {}
        if existing_code_packs:
            for info_node in existing_code_packs:
                name = info_node.replace("_Info", "").capitalize()
                existing_code[name] = {"script_name": info_node.pack_description.get(),
                                       "script_author": info_node.script_author.get(),
                                       "ui_execute_option": ["File", "Snippet"][info_node.execute_option.get()],
                                       "exec_file_path": info_node.execute_file_path.get(),
                                       "exec_script": info_node.execute_script.get(),
                                       }

        # Run
        self.load_existing_code(existing_code=existing_code)
        if default_code_info:
            self._load_code_info(code_info=default_code_info)

    def _snippet_save_extra(self, code_info=None):
        # Create/Update Info Node
        bc = rig_code_build.Build_Code()
        bc.pack_side = ""
        bc.pack_description = code_info.get("formatted_name")
        bc.script_author = self.author
        bc.ui_execute_option = code_info.get("exec_type")
        bc.exec_file_path = code_info.get("file_path")
        bc.exec_script = code_info.get("file_script")
        bc.create_bit()

        # Increment Save Path
        self.data_path = rig_io.increment_version_data_path(data_path=self.data_path)


def _get_prompt_info(pack_obj=None):
    pack_obj.get_prompt_info()
    pack_prompt_info = pack_obj.prompt_info
    pack_prompt_display_info = pack_obj.prompt_display_info
    return [pack_prompt_info, pack_prompt_display_info]


def _add_ui_obj(label=None, details=None, parent=None, dv_alt=None, display_dv_check=False):
    # Object-specific Layout
    layout = QHBoxLayout()

    # Label
    label_obj = QLabel(label)
    label_obj.setMinimumWidth(100)
    layout.addWidget(label_obj)

    # Create
    obj_type = details.get("type")
    obj = None
    if obj_type == "text":
        obj = QLineEdit()
        txt = details.get("text")
        if txt:
            if isinstance(txt, (list, tuple)):
                txt = ", ".join(txt)
            obj.setText(txt)
    elif obj_type == "float":
        obj = QLineEdit()
        val = details.get("value")
        if val:
            obj.setText(str(val))
    elif obj_type == "int":
        obj = QSpinBox()
        value, min_v, max_v = details.get("value"), details.get("min"), details.get("max")
        if min_v is None:
            min_v = -50  # Otherwise can't have negative numbers
        if min_v is not None:
            obj.setMinimum(min_v)
        if max_v is not None:
            obj.setMaximum(max_v)
        if value is not None:  # Set last in case default is negative
            obj.setValue(value)
        if min_v == max_v == value:
            obj.setEnabled(False)
    elif obj_type == "option":
        obj = QComboBox()
        options = details.get("menu_items")
        obj.addItems(options)
        dv = details.get("value", 0)
        if dv:
            i = options.index(dv)
            obj.setCurrentIndex(i)
    elif obj_type == "checkBox":
        obj = QCheckBox()
        if details.get("value"):
            obj.setCheckState(Qt.Checked)
    else:
        i_utils.error("Cannot determine how to add a '%s' type to the UI." % obj_type)

    # Add to layout
    obj.setMinimumWidth(200)
    layout.addWidget(obj)
    
    # Add Default
    if display_dv_check:
        if dv_alt is not None:  # Accept False and 0
            layout.addWidget(QLabel("Default: %s" % str(dv_alt)))
        else:
            md_label = QLabel("(matches default)")
            md_label.setFont(italic_font)
            md_label.setEnabled(False)
            layout.addWidget(md_label)

    # Add to parent
    parent.addLayout(layout)

    # Return
    return obj


def _get_value(obj=None):
    value = None
    # - Text
    if isinstance(obj, QLineEdit):
        value = obj.text()
        if value.isdigit():
            value = int(value)
        elif "." in value and value.split(".")[0].isdigit():
            value = float(value)
        elif "," in value:
            spl_val = value.replace(", ", ",").split(",")
            conv_val = []
            for val in spl_val:
                if val.isdigit():
                    if "." in val:
                        conv_val.append(float(val))
                    else:
                        conv_val.append(int(val))
                else:
                    conv_val.append(val)
            value = conv_val
    # - Int
    elif isinstance(obj, QSpinBox):
        value = int(obj.text())
    # - Options
    elif isinstance(obj, QComboBox):
        value = obj.currentText()
    # - Checkbox
    elif isinstance(obj, QCheckBox):
        value = obj.isChecked()
    else:
        i_utils.error("Cannot determine how to read a '%s' type from the UI." % type(obj).__name__)
    # - Return
    return value


class BuildDetails_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(BuildDetails_Widget, self).__init__(parent)
        
        # Vars
        self.side = None
        self.description = None
        self.build_type = None
        self.use_custom_joints = False  # Give list of joints
        
        self.all_tplt_defaults = rig_frankenstein_utils.get_all_template_options()
        self.all_pack_defaults = rig_frankenstein_utils.get_all_pack_options()
        self.prompt_type = None
    
    def closeEvent(self, event):
        super(BuildDetails_Widget, self).closeEvent(event)
    
    def __get_obj_prompt_info(self, obj_dict=None):
        ui_items = collections.OrderedDict()
        prompt_info = obj_dict.get("prompt_info")
        if prompt_info:
            for label, info in prompt_info.items():
                if "kw" not in info.keys():
                    info["kw"] = label
                    label = " ".join([word.capitalize() for word in label.split("_")])
                ui_items[label] = info
        
        return ui_items
    
    def __get_pack_prompt_info(self, build_type=None):
        # Vars
        if not build_type:
            build_type = self.build_type

        # Get defaults
        defaults = self.all_pack_defaults.get(build_type)
        if self.prompt_type == "Template":
            side = defaults.get("side")
            description = defaults.get("description")
        else:
            side = self.side
            description = self.description
        
        # Check if pack already exists and works with pack restrictions
        name = rig_frankenstein_utils.check_pack_name(build_type=build_type, side=side, description=description, dialog_error=True)
        if not name:
            return False
        side, description = name
        
        # Override known values
        if side is not None:  # To work with blank sides
            defaults["side"] = side
        if description:
            defaults["description"] = description
        
        # Mirror default
        obj_dict = defaults.copy()
        pack_obj = rig_frankenstein_utils.get_pack_object(pack_defaults=obj_dict)
        mirror_opts = ["None", "with symmetry", "no symmetry"]
        mirror = 1 if pack_obj.side == "L" else 0
        
        # UI Items
        ui_items = collections.OrderedDict()
        # - Defaults for all
        ui_items["Number of Joints"] = {"kw" : "length", "type" : "int", "min" : obj_dict.get("length_min"),
                                        "max" : obj_dict.get("length_max"), "value" : obj_dict.get("length")}
        ui_items["Mirror"] = {"kw" : "mirror", "type" : "option", "menu_items" : mirror_opts,
                              "value" : mirror_opts[mirror]}
        ui_items["Joint Names"] = {"kw" : "joint_names", "type" : "text", "text" : obj_dict.get("joint_names")}
        # - Pack specifics
        raw_prompt_info, raw_prompt_display_info = _get_prompt_info(pack_obj)
        obj_dict["prompt_info"] = raw_prompt_info
        obj_dict["prompt_display_info"] = raw_prompt_display_info
        prompt_info = self.__get_obj_prompt_info(obj_dict=obj_dict)
        ui_items.update(prompt_info)
        
        # Store defaults
        if build_type == self.build_type:
            self.defaults = defaults
        
        # Return
        return ui_items
    
    def __get_template_prompt_info(self):
        # Check that the template was not already built
        built_template = rig_frankenstein_utils.get_scene_template()
        if built_template == self.build_type:
            i_utils.error("Already built a %s template. Cannot build again." % self.build_type, dialog=True)
            return

        # Get defaults
        self.defaults = self.all_tplt_defaults.get(self.build_type)
        obj_dict = self.defaults.copy()

        # UI Items
        ui_items = collections.OrderedDict()
        # - Template specifics
        template_obj = rig_frankenstein_utils.get_template_object(template_defaults=obj_dict)
        raw_prompt_info, raw_prompt_display_info = _get_prompt_info(template_obj)
        obj_dict["prompt_info"] = raw_prompt_info
        obj_dict["prompt_display_info"] = raw_prompt_display_info
        prompt_info = self.__get_obj_prompt_info(obj_dict=obj_dict)
        ui_items.update(prompt_info)
        # - Template-used builds
        indiv_builds = obj_dict.get("pack_options")
        if indiv_builds:
            indiv_builds_info = collections.OrderedDict()
            for build_nn in sorted(indiv_builds):
                build_info = self.__get_pack_prompt_info(build_type=build_nn)
                if not build_info:  # A pack already exists with default naming
                    return 
                indiv_builds_info[build_nn] = build_info
            ui_items["Individual Packs"] = indiv_builds_info
        
        # Return
        return ui_items
    
    def __get_prompt_info(self):
        # Pack or Template?
        prompt_info = None
        if self.build_type in self.all_pack_defaults.keys():
            self.prompt_type = "Pack"
            prompt_info = self.__get_pack_prompt_info()
        elif self.build_type in self.all_tplt_defaults.keys():
            self.prompt_type = "Template"
            prompt_info = self.__get_template_prompt_info()
        
        if not prompt_info:
            return 
        
        # Return
        return prompt_info
    
    def _opt_cc(self, opt_menu=None, label=None, *args):
        # Vars
        chosen = label + "_" + opt_menu.currentText()
        alt_chosen = [opt for opt in self.pack_widget_tree_items.keys() if opt.startswith(label) and opt != chosen]
        alt_tree_item = None
        if alt_chosen:
            alt_tree_item = self.pack_widget_tree_items.get(alt_chosen[0])
        tree_item = self.pack_widget_tree_items.get(chosen)
        
        # Toggle Visibility
        if tree_item:
            tree_item.setHidden(False)
        if alt_tree_item:
            alt_tree_item.setHidden(True)
    
    def __add_ui_obj(self, label=None, details=None, parent=None):
        # Add
        obj = _add_ui_obj(label=label, details=details, parent=parent)
        
        # Connect change type to trigger show/hide of Individual Packs for templates
        if self.prompt_type == "Template" and label.endswith(" Type"):
            obj.currentIndexChanged.connect(partial(self._opt_cc, obj, label.replace(" Type", "")))

        # Return
        return obj
    
    def __decipher_ui_results(self):
        ui_obj_info = {}
        
        if self.prompt_type == "Template":
            ui_obj_info["pack_info_overrides"] = {}
        
        for obj_kw, obj in self.ui_objects.items():
            value = _get_value(obj)
            if obj_kw.startswith("pack_") and "_param_" in obj_kw:  # Template Packs are "pack_%s_param_%s" % (pack_label, class_attr)
                pack_name, pack_kw = obj_kw.split("pack_", 1)[1].split("_param_")  # :note: split only first for "pack_size" etc
                if pack_name not in ui_obj_info["pack_info_overrides"].keys():
                    ui_obj_info["pack_info_overrides"][pack_name] = {}
                ui_obj_info["pack_info_overrides"][pack_name][pack_kw] = value
            else:
                ui_obj_info[obj_kw] = value

        return ui_obj_info
    
    def _build_pack(self, build_obj=None, extra_info=None):
        # Create the pack joints
        if self.use_custom_joints:
            pack_joints = rig_frankenstein_utils.create_pack_joints(pack_obj=build_obj, use_custom_joints=self.use_custom_joints)
            build_obj.pack_joints = pack_joints
        
        # Create
        build_obj.create_pack()
        
        # Mirror
        mirror_type = extra_info.get("mirror")
        if mirror_type in ["with symmetry", "no symmetry"]:
            symmetry = True if mirror_type == "with symmetry" else False
            rig_frankenstein_utils.mirror_pack(pack_info_node=build_obj.pack_info_node, symmetry=symmetry)
    
    def _build_template(self, build_obj=None, extra_info=None):
        # Create
        build_obj.create()
        
        # Warn
        if extra_info:
            RIG_F_LOG.warn("Extra info given for template, but nothing to account for.")
    
    def run(self):
        # Wait Cursor
        cmds.waitCursor(state=True)
        
        # Get Build Object
        build_obj = rig_frankenstein_utils.get_pack_object(pack_defaults=self.defaults.copy())
        # - Update Object with UI info
        ui_based_info = self.__decipher_ui_results()
        extra_info = {}
        for k, v in ui_based_info.items():
            if not hasattr(build_obj, k):
                extra_info[k] = v  # ex: the mirroring option
                continue
            setattr(build_obj, k, v)

        # Create Build object
        if self.prompt_type == "Pack":
            self._build_pack(build_obj, extra_info)
        elif self.prompt_type == "Template":
            self._build_template(build_obj, extra_info)
            if not build_obj.can_build:
                cmds.waitCursor(state=False)
                return 

        # Clear Selection
        i_utils.select(cl=True)

        # Close Window
        self.close()

        # Frame
        i_utils.focus(type="joint")
        
        # Wait Cursor
        cmds.waitCursor(state=False)
    
    def ui(self):
        # Get prompt info
        prompt_info = self.__get_prompt_info()
        if not prompt_info:
            return 

        # Window Name 
        self.setWindowTitle(self.prompt_type + " Details")

        # Layout
        layout = QVBoxLayout()

        # Add the Info
        template_pack_comboboxes = []
        self.pack_widget_tree_items = {}
        self.ui_objects = {}
        self.tree_which_holds_widgets = None
        self.created_widgets = list()
        for label, details in prompt_info.items():
            if label == "Individual Packs":  # Templates able to display individual packs
                self.tree_which_holds_widgets = QTreeWidget()
                self.tree_which_holds_widgets.setColumnCount(1)
                self.tree_which_holds_widgets.header().hide()
                # - Setup collapsible subsection
                ind_packs_item = QTreeWidgetItem()
                ind_packs_item.setData(0, 0, "Individual Packs")
                self.tree_which_holds_widgets.addTopLevelItem(ind_packs_item)
                
                for pack_label, pack_info in details.items():
                    pack_layout = QVBoxLayout()
                    for sub_label, sub_details in pack_info.items():
                        if sub_label in ["Mirror"]:  # Template doesn't have option for these, so don't lie to rigger
                            continue
                        obj = self.__add_ui_obj(label=sub_label, details=sub_details, parent=pack_layout)
                        self.ui_objects["pack_%s_param_%s" % (pack_label, sub_details.get("kw", sub_label))] = obj
                    parent_item = QTreeWidgetItem()
                    parent_item.setData(0, 0, pack_label)
                    ind_packs_item.addChild(parent_item)
                    # self.tree_which_holds_widgets.addTopLevelItem(parent_item)
                    self.pack_widget_tree_items[pack_label] = parent_item

                    child_item = QTreeWidgetItem()
                    parent_item.addChild(child_item)
                    
                    temp_widget = QWidget()
                    temp_widget.setLayout(pack_layout)
                    self.created_widgets.append(temp_widget)
                    
                    self.tree_which_holds_widgets.setItemWidget(child_item, 0, temp_widget)
            else:
                obj = self.__add_ui_obj(label=label, details=details, parent=layout)
                self.ui_objects[details.get("kw")] = obj
                if self.prompt_type == "Template" and label.endswith(" Type"):
                    template_pack_comboboxes.append(obj)
        # - Set template individual pack options to default hide non-chosen
        # :TODO: This is working for biped, but not the Quadruped template (Leg / Leg_Watson)
        if template_pack_comboboxes:
            for obj in template_pack_comboboxes:
                obj.setCurrentIndex(1)
                obj.setCurrentIndex(0)

        # Build button
        button_layout = QHBoxLayout()
        button = tool_panel.IconButton(icon="rig/rig_create.png", label="Build " + self.prompt_type,
                                       command=partial(self.run))
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(button)

        # Add layout to master
        self.main_layout.addLayout(layout)
        if self.tree_which_holds_widgets:
            self.main_layout.addWidget(self.tree_which_holds_widgets)
        self.main_layout.addLayout(button_layout)
        
        # Show
        self.show()
        # self.setFixedWidth(self.sizeHint().width())


