import collections
import os

from ToolPanel import tool_panel_utils as tpu

import logic.py_types as logic_py
import rig_tools.utils.dynamics as rig_dynamics

import widgets as rig_widgets

class ButtonGenerator(object):
    def __init__(self):
        super(ButtonGenerator, self).__init__()

        self.is_lead = False
        ugroups = os.environ.get("TT_USERGROUPS")
        if "Leads" in ugroups and ("Pipeline" in ugroups or "Rigging" in ugroups):
            self.is_lead = True

        self.pipedocs_url = "http://pipedocs.icon.local:8000/resources/tool/"

    def _button_setup(self):
        rcl = collections.OrderedDict()
        for tpt_type in ["Character", "Prop", "Set", "Vehicle"]:
            rcl[tpt_type] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.create_simple_template('%s')" % tpt_type
        if self.is_lead:
            rcl["TEST: Character"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_basic()"

        button = tpu.NoLabelIconButton(icon="rig/rig_setup.png",
                                       command="import rig_tools.frankenstein.templates.character as tpt_c;char = tpt_c.Template_Character();char.create()",
                                       label="Setup and Templates",
                                       tool_tip="Create setup and templates.\nLeft-Click: Character Setup\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_frankenstein(self):
        rcl = collections.OrderedDict()
        rcl["Select Info Node (from selected build obj)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.sel_from_pack_obj('pack_info_node')"
        rcl["Select Bind Joints (from selected build obj)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.sel_from_pack_obj('bind_joints')"
        rcl["Select Controls (from selected build obj)"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.sel_from_pack_obj('created_controls')"
        if self.is_lead:
            rcl["TEST: Print Joint Pos"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils._get_scene_pack_positions(joint_only=True)"
            rcl["TEST: Biped"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_template('Biped')"
            rcl["TEST: Biped + Geo"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_template('Biped', with_geo=True)"
            rcl["TEST: Biped - Alt"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_template('Biped_Alt')"
            rcl["TEST: Quadruped"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_template('Quadruped')"
            rcl["TEST: Quad + Geo"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_template('Quadruped', with_geo=True)"
            rcl["TEST: Geo for sel packs"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_add_geo()"
            rcl["TEST: Geo for ALL packs"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_add_geo(all_packs=True)"
            rcl["HACK: Referenced packs to Fresh packs"] = "import rig_tools.frankenstein.utils as rig_frankenstein_utils;rig_frankenstein_utils.test_repo_packjoints_from_ref()"
        button = tpu.NoLabelIconButton(icon="rig/rig_packs.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;tpu.PopOff(rig_f_ui.Frankenstein_Widget)",
                                       label="Open Frankenstein",
                                       tool_tip="Open Frankenstein",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_faces(self):
        rcl = collections.OrderedDict()
        rcl["-- Watson (Gen) --"] = ""
        rcl["Build Watson Face"] = "import rig_tools.utils.face as rig_face;rig_face.g_watson_face(action='build')"
        rcl["Store Slider Poses"] = "import rig_tools.utils.controls as rig_controls;rig_controls.an_mo_auto()"
        rcl["-- KNG --"] = ""
        rcl["Face Template - KNG"] = "import rig_tools.utils.face as rig_face;rig_face.g_watson_face(action='template', face_type='KNG')"
        rcl["Face Bake - KNG"] = "import rig_tools.utils.face as rig_face;rig_face.g_watson_face(action='bake', face_type='KNG')"
        rcl["-- SMO --"] = ""
        rcl["Face Template - SMO"] = "import rig_tools.utils.face as rig_face;rig_face.g_watson_face(action='template')"
        rcl["Face Bake - SMO"] = "import rig_tools.utils.face as rig_face;rig_face.g_watson_face(action='bake')"
        rcl["Proxy Eyes - SMO (select eye geos)"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.proxy_eyes_smo(dialog_error=True)"
        rcl["Face Bake: Check Bake Type"] = "import rig_tools.utils.face as rig_face;rig_face.g_check_face_bake_type()"
        rcl["Face Bake: Set to KNG"] = "import rig_tools.utils.face as rig_face;rig_face.g_specify_face_bake('KNG')"
        rcl["Face Bake: Set to SMO"] = "import rig_tools.utils.face as rig_face;rig_face.g_specify_face_bake('SMO')"
        rcl["Control Scale Up"] = "import rig_tools.utils.face as rig_face;rig_face.smo_face_control_scale()"
        rcl["-- TTM --"] = ""
        rcl["Face Connect"] = "import rig_tools.utils.face as rig_face;rig_face.musk_groups()"
        rcl["Face BSH (sel face geo)"] = "import rig_tools.utils.face as rig_face;rig_face.musk_bsh()"
        rcl["-- Frankenstein --"] = ""
        rcl["Face Bake"] = "import rig_tools.utils.face as rig_face;fb = rig_face.FaceBake();fb.run()"
        rcl["Face Bake - Advanced UI"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                         "from rig_tools import widgets;" \
                                         "tpu.PopOff(widgets.FaceBake_Widget)"
        rcl["-- EAV --"] = ""
        rcl["Proxy Eyes - EAV"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.proxy_eyes_eav(dialog_error=True)"
        rcl["Eyelash 1: Dupe and Attach Curves (sel one edge row)"] = "import rig_tools.utils.nodes as rig_nodes;rig_nodes.dupe_attach_curves_sel()"
        rcl["Eyelash 2: Loft, Foll, Joints (sel attach curves)"] = "import rig_tools.utils.face as rig_face;rig_face.eav_eyelash_setup()"
        rcl["Eyelash 3: Controls (sel follicles)"] = "import rig_tools.utils.controls as rig_controls;rig_controls.eyelash_tool()"
        rcl["Face Loc - Sel Locs"] = "import rig_tools.utils.controls as rig_controls;rig_controls.create_face_control_setup(locators=None, do_create_locators=False)"
        rcl["Face Loc - MAKE Locs"] = "import rig_tools.utils.controls as rig_controls;rig_controls.create_face_control_setup(locators=None, do_create_locators=True)"
        button = tpu.NoLabelIconButton(icon="rig/rig_faces.png",
                                       command=None,
                                       label="Face Rigs",
                                       tool_tip="Create face rigs. Right-click: All options to Create Face Rigs",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_hack(self):
        rcl = collections.OrderedDict()
        rcl["Watson Fixes for Pipe"] = "import rig_tools.legacy as rig_legacy;rig_legacy.g_watson_fix_for_current_pipe()"
        rcl["Open Scene Tester"] = "import rig_tools.legacy as rig_legacy;rig_legacy.g_scene_tester()"
        rcl["Remove Containers"] = "import rig_tools.utils.nodes as rig_nodes;rig_nodes.remove_node_containers()"
        rcl["LH AI Attrs on Controls"] = "import icon_api.control as i_control;i_control.silent_ai_attrs()"
        rcl["Make Frank know Watson"] = "import rig_tools.legacy as rig_legacy;rig_legacy.g_add_watson_info_attrs()"
        rcl["--- SMO ---"] = ""
        rcl["Clean Head Groups"] = "import rig_tools.legacy as rig_legacy;rig_legacy.g_clean_head_groups()"
        rcl["Add Jaw Squash"] = "import rig_tools.utils.face as rig_face;rig_face.smo_jaw_squash_add()"
        button = tpu.NoLabelIconButton(icon="rig/rig_hack.png",
                                       command=None,
                                       label="Hacky",
                                       tool_tip="Hack Things for Legacy to work with Frankenstein",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_io_import_export(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_io_import_export.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.IO_Widget)",
                                       label="Import Export",
                                       tool_tip="Import and Export Data",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_documentation(self):
        def url_fn(url=None):
            return "import webbrowser;url = '%s';webbrowser.open(url)" % url

        rcl = collections.OrderedDict()
        rcl["Rigging Hub"] = url_fn("http://hub.icon.local/documentation/docs/rigging/")
        rcl["Skinning Reference"] = url_fn("https://docs.google.com/a/iconcreativestudio.com/document/d/1mahYA1qhjT06RFU6eqm5shOtViOAkcAW0pQg1h7uRn8/edit?usp=sharing")
        rcl["Tools Help"] = url_fn(self.pipedocs_url + "rig_overview/")
        rcl["Learn Coding"] = url_fn("https://github.com/leelap/lpTools/wiki")

        button = tpu.NoLabelIconButton(icon="rig/rig_docs.png",
                                       # Left-click opens Code Formatting Guidelines
                                       command=url_fn('http://hub.icon.local/documentation/docs/rigging/'),
                                       label="Open Documentations",
                                       tool_tip="Open Hub and other documentation related to Rigging",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_controls(self):
        rcl = collections.OrderedDict()
        rcl["Replace Shape (UI)"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                    "from rig_tools import widgets;" \
                                    "tpu.PopOff(widgets.ReplaceControlShape_Widget)"
        rcl["Add Gimbal (Sel Driver)"] = "import icon_api.control as i_control;i_control.create_gimbal_sel()"
        rcl["Remove Gimbal (Sel Gimbal or Driver)"] = "import icon_api.control as i_control;i_control.remove_gimbal_sel()"
        rcl["Print Number of Cvs (Sel Curve(s))"] = "import rig_tools.utils.controls as rig_controls;rig_controls.get_cv_sel()"
        rcl["Select All Controls"] = "import rig_tools.utils.controls as rig_controls;rig_controls.select_all_controls()"
        button = tpu.NoLabelIconButton(icon="rig/rig_controls.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.CreateControl_Widget)",
                                       label="Create controls",
                                       tool_tip="Create controls",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_save_shape(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_save_shape.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.SaveControlShape_Widget)",
                                       label="Save control shape",
                                       tool_tip="Save control shape to be available for everyone to create",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_zeroed_group(self):
        rcl = collections.OrderedDict()
        rcl["Offset Group"] = "import icon_api.node as i_node;i_node.create_zeroed_group_sel(group_name_add='Offset')"
        rcl["Options"] = "from ToolPanel import tool_panel_utils as tpu;import maya_ui.top_group as ui;tpu.PopOff(widget=ui.AddTopGroup_Widget)"
        button = tpu.NoLabelIconButton(icon="rig/rig_zeroed_group.png",
                                       command="import rig_tools.utils.nodes as rig_nodes;rig_nodes.create_offset_cns()",
                                       label="Create Top Group",
                                       tool_tip="Create Zeroed Top Group\nLeft-click: 'Offset' and 'Cns' hierarchy\nRight-click: Define group name",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_control_color(self):
        rcl = collections.OrderedDict()
        rcl["Copy Color"] = "import icon_api.control as i_control;i_control.copy_color_sel()"
        rcl["Reset Color"] = "import icon_api.control as i_control;i_control.set_color_sel('default')"
        button = tpu.NoLabelIconButton(icon="rig/rig_color.png",
                                       command="import maya_ui.color_tone as cui;cct = cui.CurveColorTone_UI();cct.ui()",
                                       label="Control Color",
                                       tool_tip="Control Color\nLeft-click: Choose Color\nRight-click: Copy Color",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_map_controls(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_control_mapping.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.AIEControlMapping_Widget)",
                                       label="Map Names",
                                       tool_tip="Map Names\nSet up mapping of control names for animation to pick up in Import/Export",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_mirror_controls(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_control_mirror.png",
                                       command="import icon_api.control as i_control;i_control.mirror_sel()",
                                       label="Mirror Curves",
                                       tool_tip="Mirror Curves.\nSelect curves to go from L>R or R>L.\nNo selection does all L curves to R.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_multi_channelbox(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_multi_attr.png",
                                       command="import maya_ui.multi_cb as mui;mcb = mui.MultiChannelBox_UI();mcb.ui()",
                                       label="Multi CB",
                                       tool_tip="Multi CB.\nOpens UI to view multiple objects' channelboxes at once.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_lock_unlock_attrs(self):
        rcl = collections.OrderedDict()
        rcl["Lock (selected attributes)"] = "import icon_api.attr as i_attr;i_attr.lock_and_hide_sel(lock=True)"
        rcl["Lock & Hide (selected attributes)"] = "import icon_api.attr as i_attr;i_attr.lock_and_hide_sel(lock=True, hide=True)"
        rcl["Unlock (TRSV attributes for selected nodes)"] = "import icon_api.attr as i_attr;i_attr.lock_and_hide_sel(unlock=True)"
        rcl["Unlock & Unhide (TRSV attributes for selected nodes)"] = "import icon_api.attr as i_attr;i_attr.lock_and_hide_sel(unlock=True, unhide=True)"
        button = tpu.NoLabelIconButton(icon="rig/rig_lock_unlock.png",
                                       command="import icon_api.attr as i_attr;i_attr.lock_and_hide_sel(lock=True)",
                                       label="Lock and Hide",
                                       tool_tip="Lock and Hide Attributes.\nLeft-click: Lock selected attributes.\nRight-click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_quick_vis(self):
        rcl = collections.OrderedDict()
        rcl[
            "All Vis - ON"] = "import rig_tools.utils.controls as rig_controls;rig_controls.toggle_ctrl_vis_attrs(set=1)"
        rcl[
            "All Vis - OFF"] = "import rig_tools.utils.controls as rig_controls;rig_controls.toggle_ctrl_vis_attrs(set=0)"
        button = tpu.NoLabelIconButton(icon="rig/rig_vis_attr.png",
                                       command="import icon_api.attr as i_attr;i_attr.create_vis_attr_sel()",
                                       label="Quick Vis",
                                       tool_tip="Add a 'Vis' Attribute.\n(1) Select driver.\n(2) Optionally select driven.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_attr_up(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_arrow_up.png",
                                       command="import icon_api.attr as i_attr;i_attr.reorder_sel(direction='up')",
                                       label="Attr Up",
                                       tool_tip="Attr Up.\nMove selected channelBox attribute(s) up.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_attr_down(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_arrow_down.png",
                                       command="import icon_api.attr as i_attr;i_attr.reorder_sel(direction='down')",
                                       label="Attr Down",
                                       tool_tip="Attr Down.\nMove selected channelBox attribute(s) down.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_update_attrs(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_update_attrs.png",
                                       command="import icon_api.attr as i_attr;i_attr.default_attrs_sel(update=True)",
                                       label="Update Defaults",
                                       tool_tip="Update Defaults.\nUpdate default attributes for all controls or selected nodes.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_reset_attrs(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_reset_attrs.png",
                                       command="import icon_api.attr as i_attr;i_attr.default_attrs_sel(update=False)",
                                       label="Reset to Defaults",
                                       tool_tip="Reset to Defaults.\nReset all controls or selected nodes to default attribute values.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_follow_attr(self):
        rcl = collections.OrderedDict()
        rcl["Disconnect Follow Attr\nSelect:\n(1) the control with the attr,\n(2) the driving control(s)"] = \
            "import rig_tools.utils.attributes as rig_attributes;rig_attributes.delete_follow_attr_sel()"
        button = tpu.NoLabelIconButton(icon="rig/rig_psb.png",
                                       command="import rig_tools.utils.attributes as rig_attributes;rig_attributes.create_follow_attr_sel()",
                                       label="Set Up Follow Attr",
                                       tool_tip="Set Up Follow Attr.\n\nSelect:\n(1) the control for the attr,\n"
                                                "(2) object to be driven,\n(3) all the drivers.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_promote_attr(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_promote_attr.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.PromoteAttr_Widget)",
                                       label="Promote Attribute",
                                       tool_tip="Promote Attribute\nPromote defined attribute(s) onto selected objects",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_dynamics(self):
        rcl = collections.OrderedDict()
        rcl["Cloth - Assign as 'SkinForce'"] = "import rig_tools.utils.dynamics as rig_dynamics;rig_dynamics.assign_cloth_dupe(as_type='SkinForce')"
        rcl["Cloth - Assign as 'ClothSimMesh'"] = "import rig_tools.utils.dynamics as rig_dynamics;rig_dynamics.assign_cloth_dupe(as_type='ClothSimMesh')"
        rcl["Dynamic Settings UI"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                     "from rig_tools import widgets;" \
                                     "tpu.PopOff(widgets.DynamicSettings_Widget)"
        rcl["Attach Yeti Hair"] = "import assets;from groom_tools import groom_io;groom_io.reconnect_yeti_input(asset=assets.current())"
        button = tpu.NoLabelIconButton(icon="rig/rig_dynamics.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.CreateDynamics_Widget)",
                                       label="Create Dynamics",
                                       tool_tip="Create Dynamics\nLeft-click: Open UI\nRight-click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_dynamics_weights_import_export(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/out_assemblyReference.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.DynamicsWeightsImportExport_Widget)",
                                       label="Dynamics Weight Import Export",
                                       tool_tip="Dynamics Weight Import Export",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_paint_dynamics(self):
        rcl = collections.OrderedDict()
        map_options = sorted(rig_dynamics.PaintAttrs.nCloth)
        for opt in map_options:
            nn = logic_py.nice_name_from_camel_case(opt)
            rcl[nn] = "import rig_tools.utils.dynamics as rig_dynamics;rig_dynamics.paint_dynamics_sel(map='%s')" % opt
        button = tpu.NoLabelIconButton(icon="rig/rig_paint.png",
                                       command="import rig_tools.utils.dynamics as rig_dynamics;rig_dynamics.paint_dynamics_sel()",
                                       label="Paint Dynamics",
                                       tool_tip="Paint Dynamics",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_interactive_playback(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_interactive_playback.png",
                                       command="import maya.mel as mel;mel.eval('InteractivePlayback')",
                                       label="Interactive Playback",
                                       tool_tip="Interactive Playback\nShortcut to Maya's Interactive Playback.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_geometry_color(self):
        rcl = collections.OrderedDict()
        rcl["Copy (by face)"] = "import tex_utils;tex_utils.copy_shader_by_face_sel()"
        rcl[
            "EAV: Make Color Dupes"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.pre_color_dupe_sel()"
        button = tpu.NoLabelIconButton(icon="rig/rig_color.png",
                                       command="import maya_ui.color_tone as cui;ct = cui.ColorTone_UI();ct.ui()",
                                       label="Geo Color",
                                       tool_tip="Geo Color\nLeft-click: Assign color shaders to selected geometry.\n"
                                                "Right-click: More options.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_geometry_overrides(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_geo_overrides.png",
                                       command="import tex_utils;tex_utils.disable_drawing_overrides()",
                                       label="Geo Overrides",
                                       tool_tip="Turn Off Geo Overrides",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_import_references(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_imp_ref.png",
                                       command="import rig_tools.utils.geometry as rig_geometry;rig_geometry.import_to_reference_sel()",
                                       label="Import to Reference",
                                       tool_tip="Import to Reference\nUpdate references for selected imported geos.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_proxy_geo(self):
        rcl = collections.OrderedDict()
        rcl["Constrained Proxy"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.create_proxy_simple()"
        rcl["Create Helper Geo"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.create_helper_sel()"
        button = tpu.NoLabelIconButton(icon="rig/rig_proxy_geo.png",
                                       command="import rig_tools.utils.geometry as rig_geometry;rig_geometry.create_proxy_simple()",
                                       label="Proxy Geo",
                                       tool_tip="Create Proxy Geo",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_joint(self):
        rcl = collections.OrderedDict()
        rcl[
            "Apply Soft Sel as Weights (sel jnt and skinned verts)"] = "import rig_tools.utils.deformers as rig_deformers;rig_deformers.save_soft_selection()"
        rcl["Insert and Reskin (UI)"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                        "from rig_tools import widgets;" \
                                        "tpu.PopOff(widgets.JointInsertReskin_Widget)"
        rcl["Create Joints on Components (UI)"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                                  "from rig_tools import widgets;" \
                                                  "tpu.PopOff(widgets.JointsFromComponents_Widget)"
        rcl["FK Chain from Components (UI)"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                               "from rig_tools import widgets;" \
                                               "tpu.PopOff(widgets.FkFromEdges_Widget)"
        button = tpu.NoLabelIconButton(icon="rig/rig_insert_reskin.png",
                                       command="import rig_tools.utils.deformers as rig_deformers;rig_deformers.save_soft_selection()",
                                       label="Joint Tools",
                                       tool_tip="Left-Click: Apply Soft Selection as Weights (select joint and skinned verts)"
                                                "\nRight-Click: Other joint options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_skinning(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_skinning.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.Skinning_Widget)",
                                       label="Skinning Tools",
                                       tool_tip="Skinning Tools",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_mirror_joint(self):
        rcl = collections.OrderedDict()
        rcl["Force Mirror Radius"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_radius()"
        rcl["Force Mirror Joint Orient (1:1)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=True)"
        rcl["Force Mirror Joint Orient (0x, -z)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, axis_mult=[0, 1, -1])"
        rcl["Force Mirror Joint Orient (-180 x)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis='x')"
        rcl["Force Mirror Joint Orient (-180 y)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis='y')"
        rcl["Force Mirror Joint Orient (-180 z)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis='z')"
        rcl["Force Mirror Joint Orient (-180 xy)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis=['x', 'y'])"
        rcl["Force Mirror Joint Orient (-180 xz)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis=['x', 'z'])"
        rcl["Force Mirror Joint Orient (-180 yz)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis=['y', 'z'])"
        rcl["Force Mirror Joint Orient (-180 xyz)"] = "import rig_tools.utils.joints as rig_joints;rig_joints.force_mirror_jo(exact=False, sub_axis=['x', 'y', 'z'])"
        button = tpu.NoLabelIconButton(icon="rig/rig_mirror_joint.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.MirrorJoint_Widget)",
                                       label="Mirror Joint",
                                       tool_tip="Mirror Joints (UI)",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_select_bind_joints(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_selection.png",
                                       command="import rig_tools.utils.joints as rig_joints;rig_joints.select_bind_joints()",
                                       label="Select Bind Joints",
                                       tool_tip="Select Bind Joints",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_fix_geometry(self):
        rcl = collections.OrderedDict()
        rcl["Fix 'Shape' and 'ShapeOrig' Names"] = "import rig_tools.utils.deformers as rig_deformers;rig_deformers.fix_deform_shape_name_sel()"
        rcl["Swap Helper Poly for Nurbs"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.swap_helpers_sel()"
        rcl["Load Reference Check"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.reference_check('load')"
        rcl["Remove Reference Check"] = "import rig_tools.utils.geometry as rig_geometry;rig_geometry.reference_check('remove')"
        button = tpu.NoLabelIconButton(icon="rig/rig_fix_shape_names.png",
                                       command="import rig_tools.utils.deformers as rig_deformers;rig_deformers.fix_deform_shape_name_sel()",
                                       label="Fix Geometry",
                                       tool_tip="Fix Geometry\nRename shapes of selected transforms (includes hierarchy by default) to rename as 'Shape' and 'ShapeOrig' properly.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_box_lattice(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_box.png",
                                       command="import rig_tools.utils.deformers as rig_deformers;rig_deformers.create_box_lattice_sel()",
                                       label="Box Lattice",
                                       tool_tip="Make a Box Lattice on the Selected Geo.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_create_deformer(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_create_deformer.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.CreateDeformer_Widget)",
                                       label="Create Deformers",
                                       tool_tip="Create Deformers",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_paint_softcluster(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_paint.png",
                                       command="import rig_tools.utils.deformers as rig_deformers;rig_deformers.paint_cluster()",
                                       label="Paint Soft Cluster",
                                       tool_tip="Shortcut to paint tool for selected control's soft cluster.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_multi_smooth(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="anm/43Smooth.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;import maya_ui.multi_smooth as ui;tpu.PopOff(widget=ui.MultiSmooth_UI)",
                                       label="Multi-Smooth",
                                       tool_tip="Multi-Smooth UI as a shortcut for hitting the 'Smooth' button several times",
                                       )
        return button

    def _button_follicles(self):
        rcl = collections.OrderedDict()
        rcl["Conveyor Belt"] = "from ToolPanel import tool_panel_utils as tpu;" \
                               "from rig_tools import widgets;" \
                               "tpu.PopOff(widgets.ConveyorBelt_Widget)"
        rcl["Slider - Make a surface and follicle from 2 selected edges."] = "import rig_tools.utils.deformers as rig_deformers;rig_deformers.follicle_slider_sel()"
        rcl["Attach - Attach targets to driver. Select targets then driver."] = "import rig_tools.utils.deformers as rig_deformers;rig_deformers.follicle_attach_sel()"
        button = tpu.NoLabelIconButton(icon="rig/rig_follicles.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.ConveyorBelt_Widget)",
                                       label="Follicle Tools",
                                       tool_tip="Follicle Tools\nLeft-Click: Create Conveyor Belt\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_at_center(self):
        rcl = collections.OrderedDict()
        rcl["-- Locator --"] = ""
        rcl["Locator at collective center"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='locator')"
        rcl["Locator at each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='locator', parent_under=False, average_center=False)"
        rcl["Locator under each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='locator', average_center=False)"
        rcl["Locator at collective volume"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='locator', volume_center=True, average_center=False)"
        rcl["-- Joint --"] = ""
        rcl["Joint at collective center"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='joint')"
        rcl["Joint at each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='joint', parent_under=False, average_center=False)"
        rcl["Joint under each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='joint', average_center=False)"
        rcl["Joint at collective volume"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='joint', volume_center=True, average_center=False)"
        rcl["-- Transform --"] = ""
        rcl["Transform at collective center"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='transform')"
        rcl["Transform at each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='transform', parent_under=False, average_center=False)"
        rcl["Transform under each selected"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='transform', average_center=False)"
        rcl["Transform at collective volume"] = "import icon_api.node as i_node;i_node.build_at_center_sel(build_type='transform', volume_center=True, average_center=False)"
        button = tpu.NoLabelIconButton(icon="rig/rig_at_center.png",
                                       command="import icon_api.node as i_node;i_node.build_at_center_sel(typ='joint')",
                                       label="Build At Center",
                                       tool_tip="Build At Center of Components\nLeft-Click: Joint at collective center\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_apply_angle(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_apply_angle.png",
                                       command="import icon_api.utils as i_utils;i_utils.apply_average_rotation_sel()",
                                       label="Apply Angle",
                                       tool_tip="Apply Angle\nSelect two components or objects. Optionally a third item to apply rotation to (else, creates locator).",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_snap(self):
        rcl = collections.OrderedDict()
        rcl["TR"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='tr')"
        rcl["T"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='t')"
        rcl["R"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='r')"
        rcl["S"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='s')"
        rcl["TRS"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='m')"
        rcl["Radius"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='radius')"
        rcl["JO, Radius"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='jo')"
        rcl[
            "TRS and JO, Radius"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs=['m', 'jo', 'radius'])"
        button = tpu.NoLabelIconButton(icon="rig/rig_snap.png",
                                       command="import icon_api.node as i_node;i_node.copy_pose_sel(action='snap', attrs='tr')",
                                       label="Snap Position",
                                       tool_tip="Snap selected objects to the world position of the first selected object.\nLeft-Click: TR\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_connect(self):
        rcl = collections.OrderedDict()
        rcl["TR"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='tr')"
        rcl["T"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='t')"
        rcl["R"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='r')"
        rcl["S"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='s')"
        rcl["TRS"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='m')"
        button = tpu.NoLabelIconButton(icon="rig/rig_connect.png",
                                       command="import icon_api.node as i_node;i_node.copy_pose_sel(action='connect', attrs='tr')",
                                       label="Connect TRS",
                                       tool_tip="Direct connect the xyz channels of first selected object to rest of selected objects.\nLeft-Click: TR\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_constrain(self):
        rcl = collections.OrderedDict()
        rcl["-- Maintain Offset ON (Multi-Driver) --"] = ""
        rcl["TR (multi, on)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='tr', mo=True)"
        rcl["T (multi, on)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='t', mo=True)"
        rcl["R (multi, on)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='r', mo=True)"
        rcl["S (multi, on)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='s', mo=True)"
        rcl["TRS (multi, on)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='m', mo=True)"
        rcl["-- Maintain Offset OFF (Multi-Driver) --"] = ""
        rcl["TR (multi, off)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='tr', mo=False)"
        rcl["T (multi, off)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='t', mo=False)"
        rcl["R (multi, off)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='r', mo=False)"
        rcl["S (multi, off)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='s', mo=False)"
        rcl["TRS (multi, off)"] = "import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='m', mo=False)"
        button = tpu.NoLabelIconButton(icon="rig/rig_constrain.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;"
                                               "from rig_tools import widgets;"
                                               "tpu.PopOff(widgets.Constraints_Widget)",
                                       # command="import icon_api.node as i_node;i_node.copy_pose_sel(action='constrain', attrs='tr', mo=True)",
                                       label="Constrain TRS",
                                       tool_tip="Drive the selected objects with constraint(s).Left-Click: Opens UI\nRight-Click: Quicky options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_mirror_objects(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_control_mirror.png",
                                       command="import icon_api.utils as i_utils;i_utils.mirror_objects_sel()",
                                       label="Mirror Objects",
                                       tool_tip="Mirror Objects.\nSelect left objects to go from L>R.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_find_rigs(self):
        rcl = collections.OrderedDict()
        rcl["Define File Path"] = "from ToolPanel import tool_panel_utils as tpu;" \
                                  "from rig_tools import widgets;" \
                                  "tpu.PopOff(widgets.FindRigsToUpdate_Widget)"
        button = tpu.NoLabelIconButton(icon="rig/rig_find_rigs.png",
                                       command="import rig_tools.procs.find_rigs_to_update as find_rigs;find_rigs.find_rigs_update()",
                                       label="Find Rigs",
                                       tool_tip="Find rigs that need to be updated and display the information.",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_rename(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_search_replace.png",
                                       command="from ToolPanel import tool_panel_utils as tpu;import maya_ui.rename as ui;tpu.PopOff(widget=ui.Rename_Widget)",
                                       label="Rename Nodes",
                                       tool_tip="Open Rename UI",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_add_remove_sets(self):
        rcl = collections.OrderedDict()
        rcl["Add to Set (Select Set Last)"] = "import icon_api.utils as i_utils;i_utils.sets_member_edit_sel(add=True)"
        rcl[
            "Remove from Set (Select Set Last)"] = "import icon_api.utils as i_utils;i_utils.sets_member_edit_sel(add=False)"
        rcl[
            "Define Set Name (Instead of Selecting)"] = "from ToolPanel import tool_panel_utils as tpu;import maya_ui.sets_edit as ui;tpu.PopOff(widget=ui.SetMemberEdit_Widget)"
        button = tpu.NoLabelIconButton(icon="rig/rig_sets.png",
                                       command="import icon_api.utils as i_utils;i_utils.sets_member_edit_sel(add=True)",
                                       label="Set Member Edit",
                                       tool_tip="Set Member Edit\nLeft-Click: Add selected to set\nRight-Click: Other options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_fix_misc(self):
        rcl = collections.OrderedDict()
        rcl["Fix Shape Names"] = "import icon_api.node as i_node;i_node.fix_shape_names_sel()"
        rcl["Fix Constraint Target Names"] = "import icon_api.utils as i_utils;i_utils.rename_constraint_target_attrs_sel()"
        rcl["Clear Stored Nodes/Attrs"] = "import icon_api.utils as i_utils;i_utils.empty_scene_lists()"
        rcl["Fix SG Connections"] = "import tex_utils;tex_utils.connect_sg_to_partition()"
        button = tpu.NoLabelIconButton(icon="rig/rig_fix_shape_names.png",
                                       command="import icon_api.node as i_node;i_node.fix_shape_names_sel()",
                                       label="Fix Random Things",
                                       tool_tip="Fix Random Things\nLeft-Click: Rename shapes of selected transforms.\nRight-Click: More Options",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_set_smooth(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_set_smooth.png",
                                       command="import rig_tools.utils.geometry as rig_geometry;rig_geometry.set_smooth()",
                                       label="Set Smoothing",
                                       tool_tip="Set Smoothing",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_bone_on(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_bone_onoff.png",
                                       command="import rig_tools.utils.joints as rig_joints;rig_joints.bone_vis(1)",
                                       label="Bone On",
                                       tool_tip="Bone On",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _button_bone_off(self):
        rcl = collections.OrderedDict()
        button = tpu.NoLabelIconButton(icon="rig/rig_bone_onoff.png",
                                       command="import rig_tools.utils.joints as rig_joints;rig_joints.bone_vis(0)",
                                       label="Bone Off",
                                       tool_tip="Bone Off",
                                       right_click_buttons=rcl,
                                       )
        return button

    def _widget_control_slider(self):
        return rig_widgets.ControlSliderWidget()
