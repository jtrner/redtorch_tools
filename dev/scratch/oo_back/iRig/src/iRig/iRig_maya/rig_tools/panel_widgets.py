from QtCompat.QtWidgets import *
from QtCompat.QtGui import *
from QtCompat.QtCore import *
import maya.cmds as cmds
from functools import partial
import os
import traceback
import importlib

import io_utils
import qt_utils
from rig_tools import RIG_LOG
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import logic.modules as logic_mod
import logic.py_types as logic_py
import csv

import rig_tools.utils.deformers as rig_deformers
import rig_tools.utils.io as rig_io
import rig_tools.utils.dynamics as rig_dynamics
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.face as rig_face

from ToolPanel import tool_panel_utils as tpu

# ----------------------------------------------------------------------------------------------------------------------

bold_font = QFont()
italic_font = QFont()
sides = ["---", "C", "M", "L", "R", "Fr", "Bk", "Upr", "Lwr"]
all_control_colors = sorted([color for color in i_node.get_default("CurveColor").keys() if "_" not in color])

bold_font.setBold(True)
italic_font.setItalic(True)


def load_sel_line_edit(sel_kws=None, line_edit_obj=None):
    if not sel_kws:
        sel_kws = {}
    sel = i_utils.check_sel(**sel_kws)

    line_edit_obj.setText(", ".join(i_utils.convert_data(sel)))


def create_sel_line_edit_objs(default_text=None, text_tt=None, button_tt=None, sel_kws=None):
    layout = QHBoxLayout()

    line_edit_obj = QLineEdit(default_text)
    line_edit_obj.setMinimumWidth(200)
    line_edit_obj.setToolTip(str(text_tt))
    layout.addWidget(line_edit_obj)

    button = QPushButton("Sel")
    button.setToolTip(str(button_tt))
    button.clicked.connect(partial(load_sel_line_edit, sel_kws, line_edit_obj))
    layout.addWidget(button)

    return [layout, line_edit_obj, button]


def create_name_layout(tooltip=None, side_cc=None, default_text=None):
    # Layout
    layout = QHBoxLayout()
    if not tooltip:
        tooltip = ""
    else:
        tooltip = " to name " + tooltip

    # Sides Dropdown
    dropdown = QComboBox()
    dropdown.addItems(sides)
    dropdown.setCurrentIndex(0)
    dropdown.setToolTip("Side" + tooltip)
    dropdown.setMinimumWidth(40)
    if side_cc:
        dropdown.currentIndexChanged.connect(side_cc)
    layout.addWidget(dropdown)

    # Description Text
    text = QLineEdit(default_text or "Description")
    text.setToolTip("Description" + tooltip)
    layout.addWidget(text)

    return [layout, dropdown, text]


def create_control_objs(type_cc=None, add_default_color_opt=False):
    layout = QHBoxLayout()

    # Add control type dropdown
    type_dropdown = QComboBox()
    nice_shapes = i_control.get_curve_type_options(include_titles=True)
    type_dropdown.addItems(nice_shapes)
    default_index = nice_shapes.index("2D Circle")
    type_dropdown.setCurrentIndex(default_index)
    type_dropdown.setToolTip(str("Shape type to create."))
    if type_cc:
        type_dropdown.currentIndexChanged.connect(type_cc)
    layout.addWidget(type_dropdown)

    # Add color dropdown
    color_dropdown = QComboBox()
    color_opts = all_control_colors
    if add_default_color_opt:
        color_opts = ["default"] + color_opts
    color_dropdown.addItems(color_opts)
    color_dropdown.setCurrentIndex(0)
    color_dropdown.setToolTip(str("Color of shapes created."))
    layout.addWidget(color_dropdown)

    return [layout, type_dropdown, color_dropdown]


def separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator


# ----------------------------------------------------------------------------------------------------------------------

class CreateDynamics_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(CreateDynamics_Widget, self).__init__(parent)
        self.setMinimumWidth(300)

        self.name_text = QLineEdit("Dynamic Name")
        self.name_text.setToolTip(str("Base of the name to give dynamic nodes created."))

        self.type_dropdown = QComboBox()
        self.solver_dropdown = QComboBox()

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        self.button = tpu.IconButton(icon="rig/rig_create.png", command=partial(self.run),
                                     label="Create Dynamics", tool_tip="Create dynamics for selected")
        button_layout.addWidget(self.button)

        self.type_dropdown.currentIndexChanged.connect(self._tt_change)
        self.type_dropdown.setCurrentIndex(0)

        self.main_layout.addWidget(self.name_text)
        self.main_layout.addWidget(self.type_dropdown)
        self.main_layout.addWidget(self.solver_dropdown)
        self.main_layout.addLayout(button_layout)

        self._add_dynamics_options()
        self._add_solver_options()

    def _add_dynamics_options(self):
        opts = ["cloth", "collider", "hair"]

        self.type_dropdown.clear()
        self.type_dropdown.addItems(opts)

    def _add_solver_options(self, default=None):
        solvers = i_utils.ls(type="nucleus") + i_utils.ls(type="hairSystem")
        solver_options = ["--- Create New Solver ---"] + sorted(i_utils.convert_data(solvers))
        self.solver_dropdown.clear()
        self.solver_dropdown.addItems(solver_options)
        if len(solver_options) > 1:
            i = 1
            if default and default in solver_options:
                i = solver_options.index(default)
            self.solver_dropdown.setCurrentIndex(i)

    def _tt_change(self):
        dyn_type = self.type_dropdown.currentText()
        tt = {"cloth": "geo", "collider": "geo", "hair": "curve"}.get(dyn_type)
        tooltip = "Create dynamics for selected " + tt
        self.button.setToolTip(str(tooltip))

    def run(self, *args):
        dyn_type = self.type_dropdown.currentText()
        solver = None

        # Do It in a weird old way that has not been incorporated fully into pipe yet. This is messy af, but temporary.
        import rig_tools.utils.dynamics as rig_dynamics

        # - Selected
        sel = i_utils.check_sel()
        if not sel:
            return
        skin_force_mesh = None
        cloth_sim_mesh = None
        geo = None
        if dyn_type != "cloth":
            sel = sel[0]
        if dyn_type == "cloth":
            if len(sel) == 1:
                geo = sel[0]
            elif len(sel) != 3:
                i_utils.error(
                    "If defining existing SkinForce and ClothSimMesh, select both of these and the original geo.",
                    dialog=True)
                return
            if len(sel) == 3:
                for sl in sel:
                    if "SkinForce" in sl:
                        skin_force_mesh = sl
                    elif "ClothSimMesh" in sl:
                        cloth_sim_mesh = sl
                    else:
                        geo = sl
                if not (skin_force_mesh and cloth_sim_mesh and geo):
                    i_utils.error("Could not find rig geo, SkinForce and ClothSimMesh from selected.", dialog=True)
                    return
                    # - Nucleus info
        solver = self.solver_dropdown.currentText()
        if "Create New" in solver:
            solver = None
        if solver and not i_utils.check_exists(solver):
            RIG_LOG.warn("'%s' does not exist. Cannot use." % solver)
            solver = None
        # - Name
        name = self.name_text.text()
        if name == "Dynamic Name":
            name = None
        if not name:
            if dyn_type != "cloth":
                name = sel.name
            else:
                name = geo.name
            self.name_text.setText(name)
        # - Cloth / Collider
        if dyn_type in ["cloth", "collider"]:
            # - Instantiate Class
            cd = rig_dynamics.CreateDynamics(name=name)
            cd.popups = True
            # - Cloth
            if dyn_type == "cloth":
                info = cd.cloth(geo=geo, nucleus=solver, skin_force_mesh=skin_force_mesh, cloth_sim_mesh=cloth_sim_mesh)
                if not info:
                    return
                if solver is None:
                    solver = info[-1]
            # - Collider
            elif dyn_type == "collider":
                collider_type = None
                if solver:
                    solver = i_node.Node(solver)
                    col_type_cloth = "Cloth" if solver.connections(type="nCloth") else None
                    col_type_hair = "Hair" if solver.connections(type="nHair") else None
                    collider_type = col_type_cloth if col_type_cloth else col_type_hair
                info = cd.collider(geo=sel, nucleus=solver, collider_type=collider_type)
                if not info:
                    return
                if solver is None:
                    solver = info[-1]
        # - Hair
        elif dyn_type == "hair":
            hsm = rig_dynamics.create_yeti_hair(geo=sel, hair_system=name, dialog_error=True)
            # solver = hsm.nucleus
            if hsm:
                solver = hsm.system

        # Update known solvers to choose from
        self._add_solver_options(default=solver)


# ----------------------------------------------------------------------------------------------------------------------

class ConveyorBelt_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(ConveyorBelt_Widget, self).__init__(parent)
        layout = QHBoxLayout()

        self.name_text = QLineEdit("Name (optional)")
        self.name_text.setToolTip(str("Base Name to give follicles. Otherwise finds name from selected."))
        self.name_text.setMinimumWidth(150)
        layout.addWidget(self.name_text)

        self.iterations = QSpinBox()
        self.iterations.setMinimumWidth(75)
        self.iterations.setValue(10)
        self.iterations.setMinimum(1)
        self.iterations.setMaximum(10000)  # Otherwise by default it is max 99
        self.iterations.setToolTip(str("How many follicles would you like to create?"))
        layout.addWidget(self.iterations)

        button = tpu.IconButton(icon="rig/rig_create.png", label="Create Conveyor Belt", command=partial(self.run),
                                tool_tip="Create a conveyor belt setup on selected surface using follicles.")
        layout.addWidget(button)

        self.main_layout.addWidget(QLabel("Create Conveyor Belt"))
        self.main_layout.addLayout(layout)

    def run(self, *args):
        sel = i_utils.check_sel()
        if not sel:
            return

        name = self.name_text.text()
        if name == "Name (optional)":
            name = None
        if name:
            name = name.replace(" ", "")
        iterations = int(self.iterations.text())

        rig_deformers.create_conveyor_belt(surface=sel[0], iterations=iterations, name=name)


# ----------------------------------------------------------------------------------------------------------------------

class JointInsertReskin_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(JointInsertReskin_Widget, self).__init__(parent)

        input_layout = QHBoxLayout()
        label = QLabel("Joint Insert\n& Reskin")
        input_layout.addWidget(label)

        self.iterations = QSpinBox()
        self.iterations.setValue(1)
        self.iterations.setMinimum(1)
        self.iterations.setToolTip(str("How many joints would you like to add?"))
        input_layout.addWidget(self.iterations)

        self.do_reskin_checkbox = QCheckBox("Reskin")
        self.do_reskin_checkbox.setToolTip(str("Check box to reskin new joints"))
        self.do_reskin_checkbox.setCheckState(Qt.Checked)
        input_layout.addWidget(self.do_reskin_checkbox)

        button = tpu.IconButton(icon="rig/rig_create.png", label="Insert Joints", command=partial(self.run),
                                tool_tip="Select 2 joints and an amount of joints to add between them.")
        input_layout.addWidget(button)

        self.main_layout.addLayout(input_layout)

    def run(self):
        objs = i_utils.check_sel(length_need=2)
        if not objs:
            return
        iterations = int(self.iterations.text())

        do_skin = self.do_reskin_checkbox.isChecked()

        if do_skin == True:
            rig_joints.insert_joints_reskin(from_joint=objs[0], to_joint=objs[1], number_of_insertions=iterations)
        else:
            rig_joints.insert_joints(from_joint=objs[0], to_joint=objs[1], number_of_insertions=iterations)


# ----------------------------------------------------------------------------------------------------------------------

class PromoteAttr_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(PromoteAttr_Widget, self).__init__(parent)
        layout = QHBoxLayout()

        self.attribute_text = QLineEdit("Attribute Promoting")
        self.attribute_text.setMinimumWidth(200)
        self.attribute_text.setToolTip(str("The node.attribute 'promoting' to other nodes."))
        layout.addWidget(self.attribute_text)

        sel_attrs_button = QPushButton("Sel")
        sel_attrs_button.clicked.connect(partial(self._load_attribute))
        sel_attrs_button.setToolTip(str("Add selected channelbox attributes as drivers."))
        layout.addWidget(sel_attrs_button)

        btm_layout = QHBoxLayout()

        self.action_opt = QComboBox()
        self.action_opt.addItems(["Transfer", "Promote", "Copy"])
        self.action_opt.setToolTip("Action to do with the attrs.\n"
                                   "'transfer': Attrs stay on to_node and original attrs are direct connected to new attrs.\n"
                                   "'promote': Attrs moved from from_node to to_node. Original attrs deleted.\n"
                                   "'copy': Attrs stay on both to_node and from_node with no connection between the two.")
        btm_layout.addWidget(self.action_opt)

        button = tpu.IconButton(icon="rig/rig_create.png", label="Promote Attr", command=partial(self.run),
                                tool_tip="Transfer, Promote or Copy defined attribute(s) onto selected objects")
        btm_layout.addWidget(button)

        self.main_layout.addLayout(layout)
        self.main_layout.addLayout(btm_layout)

    def _load_attribute(self, *args):
        sel_cb = i_utils.check_sel(channelbox=True)
        self.attribute_text.setText(", ".join(i_utils.convert_data(sel_cb)))

    def run(self, *args):
        objs = i_utils.check_sel()
        if not objs:
            return

        action = self.action_opt.currentText().lower()
        ttl = {"transfer": "Transferring", "copy": "Copying", "promote": "Promoting"}.get(action) + " Attribute: "

        attrs_raw = self.attribute_text.text()
        if attrs_raw == "Attribute Promoting":
            i_utils.error("No attributes to %s are defined." % action, dialog=True)
            return
        attrs = attrs_raw.replace(", ", ",").split(",")
        # - Are attrs really attrs?
        not_attrs = [at for at in attrs if "." not in at]
        if not_attrs:
            i_utils.error("These are not attributes. Cannot %s.\n\n%s" % (action, ", ".join(not_attrs)), dialog=True)
            return

        for at in attrs:
            from_nd, attr = at.split(".")
            for to_nd in objs:
                RIG_LOG.info(ttl + "%s.%s onto %s." % (from_nd, attr, to_nd))
                i_attr.transfer_attributes(from_node=i_node.Node(from_nd), to_node=i_node.Node(to_nd),
                                           attrs=[attr], action=action, lock_hide_source=True)


# ----------------------------------------------------------------------------------------------------------------------

class AIEControlMapping_Widget(qt_utils.MainWindow):
    def __init__(self, parent=qt_utils.get_main_window()):
        super(AIEControlMapping_Widget, self).__init__(parent)

        self.setWindowTitle("Control Mapping")
        self.role = os.environ["TT_STEPCODE"]

        scroll_area = QScrollArea()
        grid_widget = QWidget()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(grid_widget)

        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.addWidget(QLabel("Original Control"), 0, 0)
        self.grid_layout.addWidget(QLabel("New Control"), 0, 1)
        self.grid_layout.setHorizontalSpacing(10)  # Spacing between columns
        self.grid_layout.setColumnMinimumWidth(0, 200)
        self.grid_layout.setColumnMinimumWidth(1, 200)
        self.add_lines(num=20)

        add_rows_lyt = QHBoxLayout()
        add_rows_lyt.addWidget(QLabel("Add more lines"))
        self.add_num = QSpinBox()
        self.add_num.setValue(5)
        add_rows_lyt.addWidget(self.add_num)
        add_btn = QPushButton("+")
        add_btn.clicked.connect(partial(self.add_more_lines))
        add_rows_lyt.addWidget(add_btn)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        save_button = tpu.IconButton(icon="rig/rig_create.png", label="Save Control Map", command=partial(self.save))
        button_layout.addWidget(save_button)

        self.resize(470, 400)
        self.main_layout.addWidget(scroll_area)
        self.main_layout.addLayout(add_rows_lyt)
        self.main_layout.addLayout(button_layout)

    def add_lines(self, num=15):
        if num == 0:
            return

        row_num = self.grid_layout.rowCount()

        for i in range(row_num, row_num + num):
            f_tx = QLineEdit("Control Name")
            self.grid_layout.addWidget(f_tx, i, 0)
            setattr(self, "from_text_%i" % i, f_tx)

            t_tx = QLineEdit("Control Name")
            self.grid_layout.addWidget(t_tx, i, 1)
            setattr(self, "to_text_%i" % i, t_tx)

    def add_more_lines(self):
        self.add_lines(num=int(self.add_num.text()))

    def save(self):
        # Import here instead of top of module to avoid any cyclical imports
        import anm_tools.procs.import_export as aie

        control_map_dict = {}
        from_text_keys = [txt for txt in self.__dict__ if txt.startswith("from_text_")]

        # Get dict info
        for f_txt in from_text_keys:
            i = f_txt.split("_")[-1]
            from_text_obj = getattr(self, f_txt)
            t_txt = "to_text_" + i
            to_text_obj = getattr(self, t_txt)
            from_text = from_text_obj.text()
            to_text = to_text_obj.text()
            if from_text == "Control Name" or to_text == "Control Name":
                continue
            if from_text == to_text:
                continue
            if from_text.split(":")[-1] in control_map_dict.keys():
                RIG_LOG.warn("Duplicate Control Name: %s. Cannot store twice." % from_text)
                continue
            if self.role == "rig" or ":" not in from_text:
                control_map_dict[from_text] = to_text
            else:
                ns = "_".join(from_text.split(":")[0].split("_")[:-1])  # Strip namespace and number
                from_text = from_text.split(":")[-1]
                to_text = to_text.split(":")[-1]
                if ns not in control_map_dict.keys():
                    control_map_dict[ns] = {}
                control_map_dict[ns][from_text] = to_text

        # Save
        if self.role == "rig":
            map_paths = [aie.find_rig_json_path() + "\\control_mapping"]
        else:
            map_path_base = aie.find_shot_json_path() + "\\control_mapping"
            map_paths = [map_path_base + "\\" + ns for ns in control_map_dict.keys()]

        # Loop map paths (for each namespace)
        did_it_msg = ""
        for map_path in map_paths:
            # Get Map Dict
            map_dict = control_map_dict
            ns = ""
            if not control_map_dict:
                continue
            if isinstance(control_map_dict.values()[0], dict):  # Uses namespaces
                ns = map_path.split("\\")[-1]
                map_dict = control_map_dict.get(ns)

            # Check if already exists
            if os.path.exists(map_path):
                curr_map = io_utils.read_file(map_path)
                map_statements = [fr_k + " > " + curr_map.get(fr_k) for fr_k in curr_map.keys()]
                map_statement = "\n".join(sorted(map_statements))
                merge_dicts = i_utils.message(title='Combine maps?',
                                              message='Found an existing map:\n\n' + map_statement +
                                                      "\n\nCombine these with newly defined controls?",
                                              button=['Combine', 'Discard'])
                if merge_dicts == "Combine":
                    for k, v in curr_map.items():
                        if k in map_dict.keys():
                            continue
                        map_dict[k] = v

            # Write
            io_utils.write_file(path=map_path, data=map_dict)
            if ns:
                did_it_msg += "## " + ns + "\n"
            did_it_msg += "\n".join(sorted([fr_k + " > " + map_dict.get(fr_k) for fr_k in map_dict.keys()]))
            if map_paths.index(map_path) != len(map_paths) - 1:
                did_it_msg += "\n--------\n\n"

        # Confirm Success
        if did_it_msg:
            i_utils.message(title="Success", message="Stored map info:\n\n" + did_it_msg, button=["Got It"])
        else:
            i_utils.message(title="Whoops!", message="There was no map info to store.", button=["My Bad"])


# ----------------------------------------------------------------------------------------------------------------------

class SaveControlShape_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(SaveControlShape_Widget, self).__init__(parent)

        layout = QHBoxLayout()

        self.shape_name_text = QLineEdit("Shape Name")
        self.shape_name_text.setToolTip(str("The name to save as the control shape type."))
        self.shape_name_text.setMinimumWidth(200)
        layout.addWidget(self.shape_name_text)

        button = tpu.IconButton(icon="rig/rig_save_shape.png", label="Save Control Shape", command=partial(self.run),
                                tool_tip="Save Selected transforms as a Control Shape Type")
        layout.addWidget(button)

        # Does the user have permissions to save the shape to the real repo?
        self.in_repo_cb = None
        repo_option = "Pipeline" in os.environ.get("TT_USERGROUPS")
        if repo_option:
            layout_b = QHBoxLayout()
            self.in_repo_cb = QCheckBox("Save in real Repository?")
            self.in_repo_cb.setCheckState(Qt.Checked)
            layout_b.addWidget(self.in_repo_cb)

        self.main_layout.addWidget(QLabel("Save as Control Shapes"))
        self.main_layout.addLayout(layout)
        if repo_option:
            self.main_layout.addLayout(layout_b)

    def run(self, *args):
        transforms = i_utils.check_sel()
        if not transforms:
            return
        shape_name = self.shape_name_text.text()
        if shape_name == "Shape Name":
            i_utils.error("Shape Name not defined.", dialog=True)
            return

            # Run
        save_to_beta = True
        if self.in_repo_cb and self.in_repo_cb.isChecked():
            save_to_beta = False
        i_control.save_curve_as_type(shape_name=shape_name, control_transforms=transforms, save_to_beta=save_to_beta)


# ----------------------------------------------------------------------------------------------------------------------

class ReplaceControlShape_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(ReplaceControlShape_Widget, self).__init__(parent)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Replace Shape"))

        self.type_dropdown = QComboBox()
        nice_shapes = i_control.get_curve_type_options(include_text=True, include_sliders=False, include_titles=True)
        default_index = nice_shapes.index("2D Circle")
        self.type_dropdown.addItems(nice_shapes)
        self.type_dropdown.setCurrentIndex(default_index)
        self.type_dropdown.setToolTip(str("Shape type to create."))
        layout.addWidget(self.type_dropdown)

        button = tpu.IconButton(icon="rig/rig_create.png", label="Replace Control Shape",
                                tool_tip="Replace selected control's shapes with chosen shape.",
                                command=partial(self.run))
        layout.addWidget(button)

        self.main_layout.addLayout(layout)

    def run(self):
        tfms = i_utils.check_sel()
        if not tfms:
            return
        shape = self.type_dropdown.currentText()

        text = None
        if shape == "Text":
            text = i_utils.name_prompt(title="Text Shape Replace", default="Text")

        for tfm in tfms:
            i_control.replace_shape(transform=tfm, new_shape=shape, text=text, dialog_error=True)


# ----------------------------------------------------------------------------------------------------------------------

class FkFromEdges_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(FkFromEdges_Widget, self).__init__(parent)

        # Edges
        self.main_layout.addWidget(QLabel("Define Geo Edges"))
        # - Base Edges
        base_edge_objs = create_sel_line_edit_objs(default_text="Base Edges", sel_kws={"fl": True},
                                                   text_tt="The edge loop for placing the base joints of the chains.",
                                                   button_tt="Add selected edge loop as base edges.")
        base_edge_layout, self.base_edge_text, base_edge_button = base_edge_objs
        self.main_layout.addLayout(base_edge_layout)
        # - End Edges
        end_edge_objs = create_sel_line_edit_objs(default_text="End Edges", sel_kws={"fl": True},
                                                  text_tt="The edge loop for placing the end joints of the chains.",
                                                  button_tt="Add selected edge loop as end edges.")
        end_edge_layout, self.end_edge_text, end_edge_button = end_edge_objs
        self.main_layout.addLayout(end_edge_layout)

        # Name Details
        self.main_layout.addWidget(separator())
        self.main_layout.addWidget(QLabel("Name"))
        name_objs = create_name_layout(tooltip="Controls and Joints")
        layout_name, self.side_dropdown, self.name_text = name_objs
        self.main_layout.addLayout(layout_name)

        # Control Details Label
        self.main_layout.addWidget(separator())
        self.main_layout.addWidget(QLabel("Control Details"))
        control_basic_objs = create_control_objs()
        layout_control, self.control_type_dropdown, self.control_color_dropdown = control_basic_objs
        self.main_layout.addLayout(layout_control)

        # Joint Numbers
        self.main_layout.addWidget(separator())
        self.main_layout.addWidget(QLabel("Number of Joints"))
        joint_num_layout = QHBoxLayout()
        # - Across
        joint_num_layout.addWidget(QLabel("Across"))
        self.num_across_box = QSpinBox()
        self.num_across_box.setMinimum(1)
        joint_num_layout.addWidget(self.num_across_box)
        # - Down
        joint_num_layout.addWidget(QLabel("Down"))
        self.num_down_box = QSpinBox()
        self.num_down_box.setMinimum(1)
        joint_num_layout.addWidget(self.num_down_box)
        # - Add layout
        self.main_layout.addLayout(joint_num_layout)

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button = tpu.IconButton(icon="rig/rig_create.png", label="Create Fk Chains", command=partial(self.run),
                                tool_tip="Create Fk Chain joints")
        button_layout.addWidget(button)
        self.main_layout.addLayout(button_layout)

    def run(self):
        # Get edges
        base_edges = self.base_edge_text.text().replace(", ", ",").split(",")
        end_edges = self.end_edge_text.text().replace(", ", ",").split(",")
        if not (base_edges and end_edges) or base_edges == "Base Edges" or end_edges == "End Edges":
            i_utils.error("Must have both base and end edges.", dialog=True)
            return
        base_edges = i_utils.convert_data(base_edges, to_generic=False)
        end_edges = i_utils.convert_data(end_edges, to_generic=False)

        # Get name
        name_side = self.side_dropdown.currentText()
        if name_side == sides[0]:
            name_side = ""
        name_desc = self.name_text.text()
        if name_desc == "Description":
            name_desc = ""
        name = ""
        if name_side and name_desc:
            name = name_side + "_" + name_desc
        elif name_desc:
            name = name_desc
        else:
            name = base_edges[0].split(".")[0]

        # Get control info
        control_type = self.control_type_dropdown.currentText()
        control_color = self.control_color_dropdown.currentText()

        # Get joint numbers
        num_across = int(self.num_across_box.text())
        num_down = int(self.num_down_box.text())

        # Run
        rig_controls.fk_chain_from_edges(base_edges=base_edges, end_edges=end_edges, name=name,
                                         number_joints_across=num_across, number_joints_down=num_down,
                                         orient_as="yzx", up_axis="yup", control_type=control_type,
                                         control_color=control_color)


# ----------------------------------------------------------------------------------------------------------------------

class JointsFromComponents_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(JointsFromComponents_Widget, self).__init__(parent)

        # Name Details
        self.main_layout.addWidget(QLabel("Name"))
        name_objs = create_name_layout(tooltip="Controls and Joints")
        layout_name, self.side_dropdown, self.name_text = name_objs
        self.name_text.setMinimumWidth(150)
        self.main_layout.addLayout(layout_name)

        # Joint details
        self.main_layout.addWidget(separator())
        joint_details_layout = QHBoxLayout()
        # - Number of joints
        joint_details_layout.addWidget(QLabel("# Joints"))
        self.num_box = QSpinBox()
        self.num_box.setMinimum(1)
        self.num_box.setToolTip("How many joints along selected components?")
        joint_details_layout.addWidget(self.num_box)
        # - Spacer
        joint_details_layout.addWidget(QLabel("       "))
        # - As Chain
        self.as_chain_cb = QCheckBox("As Chain")
        self.as_chain_cb.setCheckState(Qt.Unchecked)
        self.as_chain_cb.setToolTip("Parent created joints into one chain?")
        joint_details_layout.addWidget(self.as_chain_cb)
        # - Add to main layout
        self.main_layout.addLayout(joint_details_layout)

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button = tpu.IconButton(icon="rig/rig_create.png", label="Create Joints", command=partial(self.run),
                                tool_tip="Create Joints evenly along selected components")
        button_layout.addWidget(button)
        self.main_layout.addLayout(button_layout)

    def run(self):
        # Check sel
        sel = i_utils.check_sel(fl=True)
        if not sel:
            return

        # Get name
        name_side = self.side_dropdown.currentText()
        if name_side == sides[0]:
            name_side = ""
        name_desc = self.name_text.text()
        if name_desc == "Description":
            name_desc = ""
        name = ""
        if name_side and name_desc:
            name = name_side + "_" + name_desc
        elif name_desc:
            name = name_desc
        else:
            name = sel[0].split(".")[0]

        # Get joint info
        number_of_joints = int(self.num_box.text())
        as_chain = self.as_chain_cb.isChecked()

        # Run
        rig_joints.joints_from_components(sel, name=name, number_of_joints=number_of_joints, as_chain=as_chain)


# ----------------------------------------------------------------------------------------------------------------------

class CreateControl_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(CreateControl_Widget, self).__init__(parent)

        top_layout = QHBoxLayout()

        # Add text field for control name
        layout_name = QVBoxLayout()
        layout_name.addWidget(QLabel("Create Control"))
        name_objs = create_name_layout(tooltip="Control", side_cc=self._side_color, default_text="Control Name")
        layout_name_inp, self.control_side_dpt, self.control_name_text = name_objs
        layout_name.addLayout(layout_name_inp)
        top_layout.addLayout(layout_name)

        # Add control type / color dropdowns
        self.color_info = i_node.get_default("CtrlColorSide")
        control_basic_objs = create_control_objs(type_cc=self.shape_possibilities, add_default_color_opt=True)
        layout_dropdowns, self.type_dropdown, self.color_dropdown = control_basic_objs
        self.previous_control_type = self.type_dropdown.currentText().lower()

        # Top group checkboxes
        layout_boxes = QHBoxLayout()
        self.cns_grp_checkbox = QCheckBox("CNS Grp")
        self.cns_grp_checkbox.setCheckState(Qt.Checked)
        layout_boxes.addWidget(self.cns_grp_checkbox)
        self.offset_grp_checkbox = QCheckBox("Offset Grp")
        self.offset_grp_checkbox.setCheckState(Qt.Checked)
        layout_boxes.addWidget(self.offset_grp_checkbox)

        # Constraint checkbox
        self.pac_checkbox = QCheckBox("Parent Cns")
        self.pac_checkbox.setToolTip(str("Drive selected object(s) with parent constraint?"))
        layout_boxes.addWidget(self.pac_checkbox)
        self.scale_cns_checkbox = QCheckBox("Scale Cns")
        self.scale_cns_checkbox.setToolTip(str("Drive selected object(s) with scale constraint?"))
        layout_boxes.addWidget(self.scale_cns_checkbox)

        layout_end = QHBoxLayout()
        # Pivot and Gimbal
        sublayout_end = QVBoxLayout()
        last_boxes_layout = QHBoxLayout()
        # - Gimbal
        self.gimbal_checkbox = QCheckBox("Gimbal")
        self.gimbal_checkbox.setCheckState(Qt.Checked)
        last_boxes_layout.addWidget(self.gimbal_checkbox)
        # - Joint
        self.joint_bind_checkbox = QCheckBox("Joint")
        self.joint_bind_checkbox.setToolTip(str("Create a joint at center of control and bind it to selected geo?"))
        last_boxes_layout.addWidget(self.joint_bind_checkbox)

        # Direct connect checkbox
        self.connect_checkbox = QCheckBox("Connect")
        self.connect_checkbox.setToolTip(str("Drive selected object(s) with direct connection TRS?"))
        last_boxes_layout.addWidget(self.connect_checkbox)
        # - Count
        lb = QLabel("Count")
        lb.setAlignment(Qt.AlignRight)
        last_boxes_layout.addWidget(lb)
        self.iterations = QSpinBox()
        self.iterations.setValue(1)
        last_boxes_layout.addWidget(self.iterations)
        sublayout_end.addLayout(last_boxes_layout)
        # - Pivot
        self.pivot_dropdown = QComboBox()
        pivot_options = ["-- Pivot Type --", "Transform Pivot", "Transform Center", "Mesh Components Center"]
        self.pivot_dropdown.addItems(pivot_options)
        self.pivot_dropdown.setCurrentIndex(2)  # Default matching i_node.copy_pose()
        self.pivot_dropdown.setToolTip(str("What part of the selected object should the control position snap to?"))
        sublayout_end.addWidget(self.pivot_dropdown)
        layout_end.addLayout(sublayout_end)
        # Add run button
        button = tpu.IconButton(icon="rig/rig_create.png", label="Create Control", command=partial(self.run),
                                tool_tip="Create Control using specified information")
        layout_end.addWidget(button)

        # Add to window
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(layout_dropdowns)
        self.main_layout.addLayout(layout_boxes)
        self.main_layout.addLayout(layout_end)

        # Run start of shape possibilities
        self.shape_possibilities()

    def _disable_option(self, option_widget=None):
        control_type = self.type_dropdown.currentText()
        option_widget.setCheckState(Qt.Unchecked)
        option_widget.setEnabled(False)
        option_widget.setToolTip("%s does not support this option" % control_type)

    def _restore_option(self, option_widget=None, state=None):
        option_widget.setEnabled(True)
        option_widget.setCheckState(state)
        option_widget.setToolTip("")

    def _side_color(self):
        curr_color = self.color_dropdown.currentText()
        side = {"C": "center", "L": "left", "R": "right"}.get(self.control_side_dpt.currentText(), "x")
        color = self.color_info.get(side, "default")
        if curr_color == color or color not in all_control_colors:
            return
        color_ind = 1 + all_control_colors.index(color)  # Add 1 because first item is "default"
        self.color_dropdown.setCurrentIndex(color_ind)

    def shape_possibilities(self):
        # Vars
        control_type = self.type_dropdown.currentText().lower()

        # Get states
        # :note: Must do this first before any editing of options. Only do for non slider/text because those are set to Unchecked
        # - Text
        if self.previous_control_type == "text":
            self.stored_offset_grp_state = Qt.Checked if self.offset_grp_checkbox.isChecked() else Qt.Unchecked
            self.stored_cns_grp_state = Qt.Checked if self.cns_grp_checkbox.isChecked() else Qt.Unchecked
        # - Slider
        elif self.previous_control_type.startswith("slider"):
            pass
        # - Anything Else
        else:
            self.stored_gimbal_state = Qt.Checked if self.gimbal_checkbox.isChecked() else Qt.Unchecked
            self.stored_offset_grp_state = Qt.Checked if self.offset_grp_checkbox.isChecked() else Qt.Unchecked
            self.stored_cns_grp_state = Qt.Checked if self.cns_grp_checkbox.isChecked() else Qt.Unchecked

        # Set states
        # - Text
        if control_type == "text":
            self._disable_option(self.gimbal_checkbox)
        # - Slider
        elif control_type.startswith("slider"):
            self._disable_option(self.gimbal_checkbox)
            self._disable_option(self.offset_grp_checkbox)
            self._disable_option(self.cns_grp_checkbox)
        # - Anything Else
        else:
            self._restore_option(self.gimbal_checkbox, self.stored_gimbal_state)
            self._restore_option(self.offset_grp_checkbox, self.stored_offset_grp_state)
            self._restore_option(self.cns_grp_checkbox, self.stored_cns_grp_state)

        # Store as previous shape
        self.previous_control_type = control_type

    def build_one(self, control_name=None, snap_pos=False, parent=None):
        # Check
        i_utils.check_arg(control_name, "control name")
        # - Remove joint-related suffixes
        control_name = control_name.replace("_Jnt", "").replace("_Bnd", "")
        # - Remove namespace
        if ":" in control_name:
            control_name = control_name.split(":")[1]

        # Vars
        control_type = self.type_dropdown.currentText()
        text = None
        with_gimbal = self.gimbal_checkbox.isChecked()
        if control_type == "Text":
            text = control_name
            with_gimbal = False
            control_type = None
        elif "Slider" in control_type:
            control_type = "slider_" + control_type.split("(")[1].split(")")[0]
        else:
            if not control_name.endswith("_Ctrl"):
                control_name += "_Ctrl"
            control_name = i_node.get_unique_name(control_name, keep_suffix="Ctrl", dialog_error=True)
            if not control_name:
                return False
            control_type = control_type.lower().replace("(", "_").replace(")", "")

        # Find control color
        control_color = self.color_dropdown.currentText()
        if control_color == "default":
            control_color = None
        gimbal_color = None
        if control_color:
            color_side = logic_py.dict_key_from_value(dictionary=self.color_info, value=control_color,
                                                      raise_error=False)
            gimbal_side = None
            if color_side:
                if color_side.endswith("_secondary"):
                    gimbal_side = color_side.replace("_secondary", "_tertiary")
                elif not color_side.endswith("_tertiary"):
                    gimbal_side = color_side + "_secondary"
            if gimbal_side:
                gimbal_color = self.color_info.get(gimbal_side)

        # Create CNS group?
        create_cns = self.cns_grp_checkbox.isChecked()

        # Create Offset group?
        create_offset = self.offset_grp_checkbox.isChecked()

        # Constrain Obj?
        constrain_geo = self.pac_checkbox.isChecked()
        scale_cns = self.scale_cns_checkbox.isChecked()

        # Direct Connect Obj?
        connect_obj = self.connect_checkbox.isChecked()

        # Find position match pivot type
        pivot_type = self.pivot_dropdown.currentText()
        pivot_kw_dict = {"-- Pivot Type --": None, "Transform Pivot": "use_object_pivot",
                         "Transform Center": "use_object_center", "Mesh Components Center": "use_components"}
        pivot_kw = pivot_kw_dict.get(pivot_type)

        # If creating joints, create them and constrain to them instead of the geo
        if self.create_bind_joints:
            # - Create joint
            i_utils.select(cl=True)  # yay maya
            jnt = i_node.create("joint", n=control_name + "_Bnd_Jnt")
            i_utils.select(cl=True)  # yay maya
            RIG_LOG.debug("Created control joint: '%s'" % jnt)
            if snap_pos:
                RIG_LOG.debug("Copy Pose from '%s' to joint. Pivot type: %s" % (snap_pos, pivot_kw))
                # - Position joint
                cp_kws = {}
                if pivot_kw:
                    cp_kws = {pivot_kw: True}
                i_node.copy_pose(driver=snap_pos, driven=jnt, **cp_kws)
                # - Skin
                if not isinstance(snap_pos, (list, tuple)):
                    snap_pos = [snap_pos]
                geos_to_skin = [geo for geo in snap_pos if i_node.Node(geo).relatives(s=True, type="mesh")]
                if geos_to_skin:
                    for geo in geos_to_skin:
                        i_node.create("skinCluster", jnt, geo, n=control_name + "_Skn")
                    i_utils.select(cl=True)
                # - Change snap and constrain info to joint
                snap_pos = jnt
            if constrain_geo:
                constrain_geo = jnt
            if connect_obj:
                connect_obj = jnt

        # Run
        ctrl = i_node.create("control", control_type=control_type, color=control_color, name=control_name,
                             with_cns_grp=create_cns,
                             with_offset_grp=create_offset, with_gimbal=with_gimbal, position_match=snap_pos,
                             position_match_pivot=pivot_kw, constrain_geo=constrain_geo, scale_constrain=scale_cns,
                             text=text,
                             match_rotation=True, connect_obj=connect_obj, parent=parent, gimbal_color=gimbal_color)

        # Return
        return ctrl

    def run(self, *args):
        # Vars
        self.create_bind_joints = self.joint_bind_checkbox.isChecked()
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)
        # - Find control name
        given_control_name = ""
        side = self.control_side_dpt.currentText()
        if side != sides[0]:  # Is not empty
            given_control_name = side + "_"
        name = self.control_name_text.text()
        if name == "Control Name" and side:
            name = "test"
        if name:
            given_control_name += name

        # Wait Cursor
        cmds.waitCursor(state=True)

        # Build with selection
        if sel:
            # Name change to selected (prep)
            if given_control_name == "test":
                given_control_name = None
            # Check snap type
            which_snap = "One Control"
            if len(sel) > 1:
                which_snap = i_utils.message(title="How Many Controls",
                                             message="Multiple objects selected.\nDo you want"
                                                     " to build one control to drive all selected"
                                                     " objects\nor build multiple controls"
                                                     " (one per object)?",
                                             button=["One Control", "Multiple Controls - World",
                                                     "Multiple Controls - Chain"],
                                             dismissString="Cancel", )
                if which_snap == "Cancel":
                    cmds.waitCursor(state=False)
                    return
            # Force snaps to transforms (AUTO-519)
            snaps = []
            cannot_snap = []
            for sl in sel:
                if sl.node_type() == "mesh":
                    RIG_LOG.warn("Selected a mesh shape: '%s'. Forcing to use the transform so can snap position." % sl)
                    sl = sl.relatives(0, p=True, type="transform")
                elif sl.node_type() not in ["transform", "joint"]:
                    cannot_snap.append(sl)
                    continue
                snaps.append(sl)
            if cannot_snap:
                i_utils.error(
                    "The following objects selected are not transforms and cannot get position for controls:\n\n%s"
                    % ", ".join(i_utils.convert_data(cannot_snap)), dialog=True)
                cmds.waitCursor(state=False)
                return
                # Do It
            if which_snap.startswith("Multiple Controls"):
                as_chain = which_snap.endswith("Chain")
                parent = None
                for obj in snaps:
                    if not given_control_name:
                        control_name = obj
                    else:
                        control_name = given_control_name or obj.split(":")[-1] + "_Ctrl"  # Use Selected
                    ctrl = self.build_one(control_name=control_name, snap_pos=obj, parent=parent)
                    if not ctrl:
                        cmds.waitCursor(state=False)
                        return
                    if as_chain:
                        parent = ctrl.last_tfm
            elif which_snap == "One Control":
                control_name = given_control_name or snaps[0].split(":")[-1] + "_Ctrl"  # Use Selected
                ctrl = self.build_one(control_name=control_name, snap_pos=snaps)
                if not ctrl:
                    cmds.waitCursor(state=False)
                    return

        # Build one control, no selection
        else:
            iterations = int(self.iterations.text())
            if iterations == 1:
                self.build_one(control_name=given_control_name)
                cmds.waitCursor(state=False)
                return
            base_name = given_control_name.replace("_Ctrl", "")
            for i in range(iterations):
                ctrl = self.build_one(control_name=base_name + str(i))
                if not ctrl:
                    cmds.waitCursor(state=False)
                    return

            # Set field
            self.control_side_dpt.setCurrentIndex(sides.index(side))
            self.control_name_text.setText(given_control_name)

        # Wait Cursor
        cmds.waitCursor(state=False)


# ----------------------------------------------------------------------------------------------------------------------

class CreateDeformer_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(CreateDeformer_Widget, self).__init__(parent)

        layout = QHBoxLayout()

        start = QVBoxLayout()
        start.addWidget(QLabel("Create"))

        self.type_dropdown = QComboBox()
        cl_fns = logic_mod.get_class_functions(cl=i_deformer.CreateDeformer)
        self.manual_additions = ["soft_cluster__with_rivet", "soft_cluster__without_rivet"]
        manual_removals = ["soft_cluster"]
        fns = [fn.replace("__", " - ").replace("_", " ").capitalize() for fn in cl_fns + self.manual_additions if
               fn not in manual_removals]
        self.type_dropdown.addItem("---")
        self.type_dropdown.addItems(sorted(fns))
        self.type_dropdown.setCurrentIndex(0)
        self.type_dropdown.setToolTip(str("Deformer type to create."))
        start.addWidget(self.type_dropdown)

        layout.addLayout(start)

        mid = QVBoxLayout()
        mid.addWidget(QLabel(""))
        self.name_text = QLineEdit("Name")
        self.name_text.setToolTip(str("Base Name to give deformer."))
        mid.addWidget(self.name_text)

        layout.addLayout(mid)

        button = tpu.IconButton(icon="rig/rig_create.png", label="Create\nDeformer", command=partial(self.run),
                                tool_tip="Create deformers by specified type.\n"
                                         "Selection of driven object optional for some deformer types.\n"
                                         "Select TARGETS then DRIVER")
        layout.addWidget(button)

        self.main_layout.addLayout(layout)

    def run(self, export=True):
        # Prep
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)
        name = self.name_text.text()
        if name == "Name":
            name = "Test"
        deformer_type_nn = self.type_dropdown.currentText()
        if deformer_type_nn == "---":
            deformer_type_nn = None
        if not deformer_type_nn:
            i_utils.error("No deformer type selected.", dialog=True)
            return
        create_one = False
        create_multiple = False
        converted_deformer_type = deformer_type_nn.replace(" - ", "__").replace(" ", "_").lower()
        deformer_kwargs = {}
        if converted_deformer_type in self.manual_additions:
            con_d_spl = converted_deformer_type.split("__")
            deformer_kw = con_d_spl[1].replace("with_", "").replace("without_", "").split(" ")
            if "with_" in con_d_spl[1]:
                deformer_kwargs = {k: True for k in deformer_kw}
            elif "without_" in con_d_spl[1]:
                deformer_kwargs = {k: False for k in deformer_kw}
            converted_deformer_type = con_d_spl[0]

        # Does type require a driver? If so, break down the selection
        use_driver = converted_deformer_type in i_deformer.CreateDeformer.uses_driver
        targets = None
        driver = None
        if sel:
            if len(sel) == 1:
                targets = sel
            else:
                if use_driver:
                    targets = sel[:-1]
                    driver = sel[-1]
                else:
                    targets = sel

        # Can the deformer work with multiple targets
        accepts_multiple_targets = converted_deformer_type in i_deformer.CreateDeformer.accepts_multiple_targets

        # Build with selection
        if sel and not use_driver:  # If use driver always build one because there's no way to interpret breaking of targets/drivers
            # Check if making one total or one per-selection
            which_snap = "One %s" % deformer_type_nn
            if len(sel) > 1 and accepts_multiple_targets:
                which_snap = i_utils.message(title="How Many %ss" % deformer_type_nn,
                                             message="Multiple objects selected.\nDo you want"
                                                     " to build one %s to drive all selected"
                                                     " objects\nor build multiple %ss"
                                                     " (one per object)?" % (deformer_type_nn, deformer_type_nn),
                                             button=["One %s" % deformer_type_nn, "Multiple %ss" % deformer_type_nn],
                                             dismissString="Cancel")
                if which_snap == "Cancel":
                    return
            # Do It
            if which_snap.startswith("Multiple"):
                create_multiple = True
            elif which_snap.startswith("One"):
                create_one = True

        # No limits on amount to create. Determine what to do.
        if not (create_one or create_multiple):
            if accepts_multiple_targets or not targets:
                create_one = True
            elif targets:
                create_multiple = True

        # Run
        if create_one:
            create_deformer = i_deformer.CreateDeformer(name=name, target=targets, driver=driver, dialog_errors=True)
            fn = getattr(create_deformer, converted_deformer_type)
            fn(**deformer_kwargs)
        elif create_multiple:
            for targ in targets:
                create_deformer = i_deformer.CreateDeformer(name=name, target=targ, driver=driver, dialog_errors=True)
                fn = getattr(create_deformer, converted_deformer_type)
                fn(**deformer_kwargs)
        else:
            i_utils.error("Could not create deformer.", dialog=True)
            return

        # Clear Selection
        i_utils.select(cl=True)


# ----------------------------------------------------------------------------------------------------------------------

class IO_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None, default_io=None):
        super(IO_Widget, self).__init__(parent)

        layout = QHBoxLayout()

        input_layout = QVBoxLayout()

        lbl = QLabel("Choose IO Type")
        lbl.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(lbl)
        # - Find All available data types
        self.ios = {"control_all": {"display": "Controls - All Info",
                                    "prep_call": ["rig_tools.utils.controls", "ControlsIO"],
                                    },
                    "control_shapes": {"display": "Controls - Shapes Only",
                                       "prep_call": ["rig_tools.utils.controls", "ControlsIO"],
                                       "action_kwargs": {"color": False},
                                       },
                    "control_colors": {"display": "Controls - Colors Only",
                                       "prep_call": ["rig_tools.utils.controls", "ControlsIO"],
                                       "action_kwargs": {"shape": False},
                                       },
                    "curves": {"display": "Curves - Non-Controls/Builds Only",
                               "prep_call": ["rig_tools.utils.controls", "CurvesIO"],
                               },
                    "joints": {"display": "Joints - Non-Builds Only",
                               "prep_call": ["rig_tools.utils.joints", "JointsIO"],
                               },
                    "transforms": {"display": "Transforms - Non-Builds Only",
                                   "prep_call": ["rig_tools.utils.nodes", "TransformsIO"],
                                   },
                    "mesh_tone": {"display": "Mesh Tone - for Rigs",
                                  "prep_call": ["rig_tools.utils.geometry", "MeshToneIO"],
                                  },
                    "mesh_tone_b": {"display": "Mesh Tone - for SFN",
                                    "prep_call": "import rig_tools.utils.geometry as rig_geometry;",
                                    "import_call": False,
                                    "export_call": "rig_geometry.mesh_tone_for_sfn()",
                                    },
                    "mesh_tone_c": {"display": "Mesh Tone - Proxy from MOD",
                                    "prep_call": "import tex_utils;",
                                    "import_call": "tex_utils.import_model_proxy_shaders()",
                                    "export_call": False,
                                    },
                    "dynamics": {"display": "Dynamics",  # This will eventually be split, like deformers
                                 "prep_call": ["rig_tools.utils.dynamics", "DynamicsIO"],
                                 },
                    "packs": {"display": "Packs - Non-bits Only",
                              "prep_call": ["rig_tools.frankenstein.utils", "PacksIO"],
                              },
                    "anim_curves": {"display": "Animation Curves",
                                    "prep_call": ["rig_tools.utils.nodes", "AnimCurvesIO"],
                                    },
                    "face_curves": {"display": "Face Bake - Curves",
                                    "prep_call": ["rig_tools.utils.face", "FaceBakeCurvesIO"],
                                    },
                    "attributes": {"display": "Attributes - Ud Sel Only",
                                   "prep_call": ["rig_tools.utils.attributes", "AttributesIO"],
                                   },
                    "constraints": {"display": "Constraints - Non-Builds Only",
                                    "prep_call": ["rig_tools.utils.nodes", "ConstraintsIO"]
                                    },
                    }
        # -- Individual Deformers
        deformer_cl_fns = logic_mod.get_class_functions(cl=rig_deformers.DeformersIO, include_private=True)
        deformer_types = [dfm[1:].replace('_get', '') for dfm in deformer_cl_fns if
                          dfm.endswith('_get') and dfm != '_get']
        for deformer in deformer_types:
            self.ios["deformer_%s" % deformer] = {"display": "Deformer - %s" % deformer,
                                                  "prep_call": ["rig_tools.utils.deformers", "DeformersIO"],
                                                  "action_kwargs": {"deformer_type": deformer},
                                                  }
        # -- Specific deformer override
        self.ios["deformer_skinCluster_mesh"] = self.ios.get("deformer_skinCluster")
        self.ios["deformer_skinCluster_mesh"]["display"] += " - Mesh Only"
        self.ios["deformer_skinCluster_mesh"]["action_kwargs"]["node_types"] = ["mesh"]
        del (self.ios["deformer_skinCluster"])

        # -- Sort
        io_options = ["---", "All", "Multi"] + sorted([self.ios.get(k).get("display") for k in self.ios.keys()])
        # - Add menu
        self.io_type_dropdown = QComboBox()
        self.io_type_dropdown.addItems(io_options)
        self.io_type_dropdown.setMinimumWidth(215)
        self.io_type_dropdown.setToolTip(str("Data type to Import/Export."))
        self.io_type_dropdown.currentIndexChanged.connect(self._io_type_changed)
        input_layout.addWidget(self.io_type_dropdown)
        # - Add to main layout
        layout.addLayout(input_layout)

        # Import Section
        import_layout = QVBoxLayout()
        # - Button
        import_button = tpu.IconButton(icon="rig/rig_import.png", command=partial(self.run, "import"),
                                       tool_tip="Import IO")
        import_layout.addWidget(import_button)
        # - "Force" Checkbox
        self.force_import_cb = QCheckBox("Force")
        self.force_import_cb.setToolTip(
            str("Override existing in-scene data with exported data.\nOnly available for some IOs."))
        import_layout.addWidget(self.force_import_cb)
        # - Add to main layout
        layout.addLayout(import_layout)

        # Export Section
        export_layout = QVBoxLayout()
        # - Button
        export_button = tpu.IconButton(icon="rig/rig_export.png", command=partial(self.run, "export"),
                                       tool_tip="Export IO", )
        export_layout.addWidget(export_button)
        # - "Delete" Checkbox
        self.delete_export_cb = QCheckBox("Delete")
        self.delete_export_cb.setToolTip(str("Delete exported data."))
        export_layout.addWidget(self.delete_export_cb)

        # - Add to main layout
        layout.addLayout(export_layout)

        # Add to layout
        self.io_type_dropdown.setCurrentIndex(0)
        self.main_layout.addLayout(layout)

        # Add separator
        self.main_layout.addWidget(separator())

        # Specify Location layout
        specify_ttl_lyt = QHBoxLayout()
        specify_ttl_lyt.addWidget(QLabel("Specify Location"))
        specify_dpdn_refresh = QPushButton("R")
        specify_dpdn_refresh.clicked.connect(self._load_projs)
        specify_dpdn_refresh.setToolTip("Refresh the asset dropdowns that have available data")
        specify_dpdn_refresh.setMaximumWidth(20)
        specify_ttl_lyt.addWidget(specify_dpdn_refresh)
        self.main_layout.addLayout(specify_ttl_lyt)

        # Add specified location by asset info
        # - Layout
        browse_dpdn_layout = QHBoxLayout()
        # - Project
        self.show_dpdn = QComboBox()
        self.show_dpdn.setMaximumWidth(50)
        self.show_dpdn.addItem("---")
        self.show_dpdn.currentIndexChanged.connect(partial(self._dropdown_change, self.show_dpdn))
        browse_dpdn_layout.addWidget(self.show_dpdn)
        # - Asset Type
        self.atype_dpdn = QComboBox()
        self.atype_dpdn.addItem("---")
        self.atype_dpdn.setMinimumWidth(75)
        self.atype_dpdn.currentIndexChanged.connect(partial(self._dropdown_change, self.atype_dpdn))
        browse_dpdn_layout.addWidget(self.atype_dpdn)
        # - Asset
        self.asset_dpdn = QComboBox()
        self.asset_dpdn.addItem("---")
        self.asset_dpdn.setMinimumWidth(125)
        self.asset_dpdn.currentIndexChanged.connect(partial(self._dropdown_change, self.asset_dpdn))
        browse_dpdn_layout.addWidget(self.asset_dpdn)
        # - Data Version
        self.data_ver_dpdn = QComboBox()
        self.data_ver_dpdn.addItem("---")
        self.data_ver_dpdn.setMinimumWidth(50)
        browse_dpdn_layout.addWidget(self.data_ver_dpdn)
        # - Add to layout
        self.dropdown_order = [self.show_dpdn, self.atype_dpdn, self.asset_dpdn, self.data_ver_dpdn]
        for ddn in self.dropdown_order:
            ddn.setEnabled(False)
            ddn.setToolTip("Click the 'R' refresh button to gain access to show available data.")
        self.main_layout.addLayout(browse_dpdn_layout)

        # Add specified location by file path
        browse_file_layout = QHBoxLayout()
        self.default_directory = rig_io.get_data_path()
        self.default_directory_addition = ""
        if not os.path.exists(self.default_directory):  # No data exported, yet
            spl = self.default_directory.split("\\rig_data")
            self.default_directory = spl[0]
            self.default_directory_addition = "\\rig_data" + spl[1]
        self.browse_path_text = QLineEdit()
        self.browse_path_text.setMinimumWidth(300)
        self.browse_path_btn = QPushButton("Browse")
        self.browse_path_btn.setToolTip("Optionally specify an override for import or export path")
        self.browse_path_btn.clicked.connect(self._browse_path)
        browse_file_layout.addWidget(self.browse_path_text)
        browse_file_layout.addWidget(self.browse_path_btn)
        self.main_layout.addLayout(browse_file_layout)

        # Set default io
        if default_io:
            self.io_type_dropdown.setCurrentIndex(io_options.index(default_io))

    def _load_projs(self):
        cmds.waitCursor(state=True)

        lbls = ["Project", "Asset Type", "Asset", "Data Version"]
        for i, ddn in enumerate(self.dropdown_order):
            ddn.setEnabled(True)
            ddn.setToolTip(lbls[i])

        self.dpdn_lookup = rig_io.get_data_by_show()
        projs = sorted(self.dpdn_lookup.keys())

        self.show_dpdn.clear()
        self.show_dpdn.addItem("---")
        self.show_dpdn.addItems(projs)
        curr_proj = os.environ.get("TT_PROJCODE")
        if curr_proj in projs:
            self.show_dpdn.setCurrentIndex(projs.index(curr_proj) + 1)

        cmds.waitCursor(state=False)

    def _get_dropdown_texts(self):
        proj = self.show_dpdn.currentText()
        if proj == "---":
            proj = None
        asset_typ = self.atype_dpdn.currentText()
        if asset_typ == "---":
            asset_typ = None
        asset = self.asset_dpdn.currentText()
        if asset == "---":
            asset = None
        data_ver = self.data_ver_dpdn.currentText()
        if data_ver == "---":
            data_ver = None
        current_info = [proj, asset_typ, asset, data_ver]

        return current_info

    def _dropdown_change(self, combo_box=None, *args):
        # Get Current Info
        current_info = self._get_dropdown_texts()
        proj, asset_typ, asset, data_ver = current_info

        # Did the combobox change to something readable?
        dpdn_i = self.dropdown_order.index(combo_box)
        if not current_info[dpdn_i]:
            return

        # Get next combobox's data
        next_combo_box = self.dropdown_order[dpdn_i + 1]
        vals_add = []
        if next_combo_box == self.atype_dpdn:
            vals_add = self.dpdn_lookup.get(proj).keys()
        elif next_combo_box == self.asset_dpdn:
            vals_add = self.dpdn_lookup.get(proj).get(asset_typ).keys()
        elif next_combo_box == self.data_ver_dpdn:
            vals_add = self.dpdn_lookup.get(proj).get(asset_typ).get(asset)

        # Add values
        next_combo_box.clear()
        next_combo_box.addItem("---")
        next_combo_box.addItems(sorted(vals_add))

    def _browse_path(self):
        dialog = QFileDialog(self, "Browse", self.default_directory)
        # dialog.setFileMode(QFileDialog.DirectoryOnly)  # Doesn't display files if have this
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            if os.path.isfile(path):  # May need to turn off the DirectoryOnly
                path = os.path.dirname(path)
            path = path.replace("\\", "/")
            pth_spl = path.split("/")
            # - If default path had version number and a version number folder is chosen, fix the path
            if rig_io.check_is_version_folder(pth_spl[-1]) and rig_io.check_is_version_folder(pth_spl[-2]):
                path = "/".join(pth_spl[:-1])
            # - If there's a subfolder for the IO chosen, remove it to just see the version number folder
            pth_spl = path.split("/")
            v_folder = [fld for fld in pth_spl if rig_io.check_is_version_folder(fld)][0]
            v_folder_i = pth_spl.index(v_folder)
            if v_folder_i != len(pth_spl):
                path = "/".join(pth_spl[:v_folder_i + 1])
            path = path.replace("\\", "/")
            self.browse_path_text.setText(path)

    def _io_type_changed(self):
        # Vars
        io_type = self.io_type_dropdown.currentText()

        # Force Import available?
        force_enabled = False
        if io_type.startswith("Deformer -"):
            force_enabled = True
        self.force_import_cb.setEnabled(force_enabled)

    def _delete_io_data(self, path=None):
        # Find jsons
        if os.path.isdir(path):
            jsons = [fl for fl in os.listdir(path) if fl.endswith(".json")]
            full_jsons = []
            if jsons:
                for json in jsons:
                    full_jsons.append(os.path.abspath(path + "/" + json))
        elif os.path.isfile(path):
            full_jsons = [path]
        elif os.path.isfile(path + ".json"):
            full_jsons = [path + ".json"]
        else:
            i_utils.error("%s is not an IO file or a directory." % path, dialog=True)
            return

            # Confirm with User
        do_it = i_utils.message(title="Delete IO Datas?", message="Are you sure you want to delete these forever?\n\n" +
                                                                  "\n".join(full_jsons), button=["Yes", "No"])
        if do_it == "No":
            return

            # Delete
        deleted = ""
        for json in full_jsons:
            os.remove(json)
            deleted += "\n" + json

        # Confirm
        if deleted:
            msg = "Successfully deleted IOs:\n\n" + deleted
        else:
            msg = "No jsons found to delete."
        i_utils.message(title="Deleted IOs", message=msg)

    def multi_opts(self, action):
        # Close existing window
        name = "MultiIO"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        # Prep Window
        self.multi_window = qt_utils.MainWindow()
        self.multi_window.setWindowTitle("Multi IO")
        self.multi_window.setObjectName(name)
        self.multi_window.main_layout.setContentsMargins(0, 0, 0, 0)

        # Loop creation of checkboxes
        for k in sorted(self.ios.keys()):
            data = self.ios.get(k)
            cb = QCheckBox(data.get("display"))
            data["checkbox"] = cb
            self.multi_window.main_layout.addWidget(cb)

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button = tpu.IconButton(icon="rig/rig_create.png", command=partial(self.multi_run, action))
        button_layout.addWidget(button)
        self.multi_window.main_layout.addLayout(button_layout)

        # Show
        self.multi_window.show()

    def multi_run(self, action):
        # Vars
        run_io_types = []

        # Get the chosen
        for k, data in self.ios.items():
            cb = data.get("checkbox")
            if cb.isChecked():
                run_io_types.append(data.get("display"))

        # Check chosen types
        # - Any?
        if not run_io_types:
            i_utils.error("No IO types chosen", dialog=True)
            return
        # - Duplicates?
        if "Controls - All Info" in run_io_types:
            if "Controls - Colors Only" in run_io_types or "Controls - Shapes Only" in run_io_types:
                i_utils.error("Cannot import 'All' control types as well as 'Only' shapes or colors.", dialog=True)
                return

        # Run
        for io_type in run_io_types:
            self.run(action=action, io_type_label=io_type, force_recursive=True)

        # Close window
        self.multi_window.close()

    def run(self, action=None, io_type_label=None, force_recursive=False):
        # UI Info
        if not io_type_label:
            io_type_label = self.io_type_dropdown.currentText()
        import_force_available = self.force_import_cb.isEnabled()
        import_force = import_force_available and self.force_import_cb.isChecked()
        export_delete = self.delete_export_cb.isChecked()

        # Check
        if io_type_label == "---":
            i_utils.error("Choose an IO type.", dialog=True)
            return

            # Multi?
        if io_type_label == "Multi":
            self.multi_opts(action=action)
            return

        # Waiting
        cmds.waitCursor(state=True)

        # Get path from UI
        # - File browse
        point_path = self.browse_path_text.text()
        if point_path and point_path != self.default_directory:  # Force version numbering
            point_path = rig_io.get_data_path(base_path=point_path)
        # - Dropdown browse
        current_info = self._get_dropdown_texts()
        proj, asset_typ, asset, data_ver = current_info
        dropdown_path = None
        if proj and asset_typ and asset:
            dropdown_path = rig_io.get_data_base_path(project=proj, asset_type=asset_typ, asset=asset,
                                                      data_version=data_ver)
        # - Check don't have multiple paths specified
        if dropdown_path and point_path:
            i_utils.error("Cannot specify both a dropdown-based file and a browsed file location.", dialog=True)
            return
        # - Final path
        RIG_LOG.debug("Point Path: %s" % point_path)
        RIG_LOG.debug("Dropdown Path: %s" % dropdown_path)
        path = point_path or dropdown_path or (self.default_directory + self.default_directory_addition)
        RIG_LOG.debug("Path from UI: '%s'" % path)

        # Run "All"
        if io_type_label == "All":
            if export_delete:
                self._delete_io_data(path=path)
                cmds.waitCursor(state=False)
                return
            rig_io.all_ios(action=action, force=import_force, progress_bar=True, json_path=path)
            cmds.waitCursor(state=False)
            return

        # Get IO Data
        io_type = [k for k in self.ios.keys() if self.ios.get(k).get("display") == io_type_label][0]
        io_data = self.ios.get(io_type)
        action_kwargs = io_data.get("action_kwargs", {})
        prep_call = io_data.get("prep_call")
        action_call = io_data.get("%s_call" % action)

        # Check Action Call
        if action_call is False:  # Means this action has no code to run
            i_utils.error("There is no '%s' action available for '%s'." % (action, io_type_label), dialog=True)
            return

        # Is it a mock io? Those just execute
        if isinstance(prep_call, (str, unicode)):
            exec (prep_call + action_call)
            cmds.waitCursor(state=False)
            return

        # Inst
        RIG_LOG.debug("Importing:", prep_call[0])
        io_mod = importlib.import_module(prep_call[0])
        RIG_LOG.debug("Getting attr:", prep_call[1])
        io_class = getattr(io_mod, prep_call[1])

        # Kwargs
        if action == "import":
            if import_force:
                action_kwargs["force"] = True
            if ("recursive_path_check" not in action_kwargs) or force_recursive:
                action_kwargs["recursive_path_check"] = True
            if "set" not in action_kwargs:
                action_kwargs["set"] = True

        # Specify Json Path?
        inst_kwargs = {}
        io = None
        if path:
            inst_kwargs["json_path"] = path

        # Inst
        if not io:
            RIG_LOG.debug("Class Inst Kwargs (B):", inst_kwargs)
            io = io_class(**inst_kwargs)
            io.pop_ups = True

        RIG_LOG.debug("IO Json Path:", io.json_path)

        # Just deleting the exported?
        if export_delete:
            self._delete_io_data(path=io.json_path)
            return

            # Execute
        RIG_LOG.debug("Action Kwargs:", action_kwargs)
        if action == "import":
            io.read(**action_kwargs)
        else:  # export
            io.write(**action_kwargs)

        # Waiting
        cmds.waitCursor(state=False)


# ----------------------------------------------------------------------------------------------------------------------

class BlendSnapper_UI():
    # :TODO: Convert from Maya Cmds UI to PyQt Widget
    def __init__(self):
        self.window_name = "BlendSnapper"
        self.window_display_name = " ".join(logic_py.split_camel_case_string(string=self.window_name))

        self.ori_ls = []
        self.pt_ls = []
        self.follow_ls = []
        self.blend_ctrl = None

        self.simple_frame = None
        self.advd_frame = None

        self.ori_menu = None
        self.ori_menu_items = []
        self.pt_menu = None
        self.pt_menu_items = []

    def _get_ui_info(self):
        # Check selection
        sel = i_utils.check_sel()
        if not sel:
            return None
        self.blend_ctrl = sel[0]

        # Get list of attributes
        attrs = self.blend_ctrl.attrs()
        self.ori_ls = [atr for atr in attrs if atr.endswith("_Orient")]
        self.pt_ls = [atr for atr in attrs if atr.endswith("_Point")]
        self.follow_ls = [atr for atr in attrs if atr.startswith("Follow_")]

        # Make an advanced section?
        self.do_advd_section = False
        if self.ori_ls and self.pt_ls:
            self.do_advd_section = True

        # Get button names
        self.button_names = sorted(
            list(set([lbl.replace("_Point", "").replace("_Orient", "") for lbl in self.ori_ls + self.pt_ls])))
        self.button_names += [lbl for lbl in self.follow_ls]

        # Get window height based on buttons
        self.win_h = 230  # Keep sizeable because # targets vary. This defaults for 3.
        if self.button_names:
            self.win_h = len(self.button_names) * 40
            if self.do_advd_section:
                self.win_h += 40

        # Return as successful
        return True

    def refresh(self, *args):
        # Simply rebuild whole UI
        if i_utils.is_2017:
            # :note: Don't use for 2017. When used, it will close UI but not rebuild it.
            self.ui()
            return

            # Things get tricky. Rebuild parts of the UI
        # - Check
        check_succeeded = self._get_ui_info()
        if not check_succeeded:
            return
        # - Change text label
        cmds.text(self.blender_text, e=True, l=self.blend_ctrl.name)
        # - Recreate sections
        self._create_simple_section()
        self._create_advanced_section()
        # - Edit window height
        cmds.window(self.win, e=True, height=self.win_h)

    def run(self, target=None, *args):
        if target:
            pt = target + "_Point" if i_utils.check_exists(self.blend_ctrl + "." + target + "_Point") else None
            ori = target + "_Orient" if i_utils.check_exists(self.blend_ctrl + "." + target + "_Orient") else None
            follow = target if i_utils.check_exists(self.blend_ctrl + "." + target) else None
        else:
            pt = cmds.optionMenu(self.pt_menu, q=True, v=True)
            ori = cmds.optionMenu(self.ori_menu, q=True, v=True)
            follow = None

        if not ori and not pt and not follow:
            i_utils.error("Cannot Find Driver to Snap to.", dialog=True)
            return

        rig_deformers.blend_snapper(orient=ori, point=pt, follow=follow, blend_ctrl=self.blend_ctrl)

    def _create_simple_section(self):
        # Clear
        if self.simple_frame:
            cmds.deleteUI(self.simple_frame, layout=True)

        # Create
        self.simple_frame = cmds.frameLayout(label="Simple", bv=False, cll=True, cl=False, w=self.win_w - 5, p=self.col)
        simple_lyt = cmds.columnLayout(columnAttach=('both', 5), rowSpacing=5, w=self.win_w, p=self.simple_frame)
        for target in self.button_names:
            label = target.replace("_", " ")
            if "Follow_" in target:
                label = self.blend_ctrl.attr(target).get(nn=True)
            cmds.button(l=label, c=partial(self.run, target), w=self.win_w - 15, p=simple_lyt)

    def _create_advanced_section(self):
        # Clear
        if self.advd_frame:
            cmds.deleteUI(self.advd_frame, layout=True)

        # Create
        # - Check
        if not self.do_advd_section:
            return
            # - Frame
        self.advd_frame = cmds.frameLayout(label="Advanced", bv=False, cll=True, cl=True, w=self.win_w - 5, p=self.col)
        # - Orient
        if self.ori_ls:
            self.ori_menu = cmds.optionMenu(label="Ori", bgc=(0.4, 0.4, 0.4), w=self.win_w - 25, p=self.advd_frame)
            for ori in self.ori_ls:
                cmds.menuItem(label=ori, parent=self.ori_menu)
        # - Point
        if self.pt_ls:
            self.pt_menu = cmds.optionMenu(label="Point", bgc=(0.4, 0.4, 0.4), w=self.win_w - 25, p=self.advd_frame)
            for pt in self.pt_ls:
                cmds.menuItem(label=pt, parent=self.pt_menu)
        # - Snap Button
        cmds.button(l="Snap", c=self.run, p=self.advd_frame)

    def ui(self):
        # Close existing
        if cmds.window(self.window_name, ex=True):
            cmds.deleteUI(self.window_name)

        # Layout setup
        self.win_w = 225
        self.win = cmds.window(self.window_name, title=self.window_display_name, w=self.win_w)
        self.col = cmds.columnLayout()

        # Check
        check_succeeded = self._get_ui_info()
        if not check_succeeded:
            return

        # Refresh button
        refresh_layout = cmds.rowColumnLayout(nc=3, cw=[(1, 50), (2, 5), (3, self.win_w - 55)])
        cmds.button(l="Refresh", c=self.refresh, p=refresh_layout)
        cmds.text(l="", p=refresh_layout)
        self.blender_text = cmds.text(l=self.blend_ctrl.name, p=refresh_layout)

        # Simple section
        self._create_simple_section()

        # Advanced section
        self._create_advanced_section()

        # Show window
        cmds.window(self.win, e=True, widthHeight=[self.win_w, self.win_h])
        cmds.showWindow(self.win)


# ----------------------------------------------------------------------------------------------------------------------

class FindRigsToUpdate_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(FindRigsToUpdate_Widget, self).__init__(parent)

        layout = QHBoxLayout()

        layout.addWidget(QLabel("Find Rigs"))

        # Add path to where to save file
        self.default_text = "File Path to Save Info to (optional)"
        self.file_path_text = QLineEdit(self.default_text)
        self.file_path_text.setMinimumWidth(200)
        self.file_path_text.setToolTip(str("File path to save the info to.\n"
                                           "If not specified, goes to your Desktop in a 'rig_updates' folder."))
        layout.addWidget(self.file_path_text)

        # Add button
        button = tpu.IconButton(icon="rig/rig_create.png", label="Find Rigs",
                                tool_tip="Find the rigs that need updating. Save in specified file name.",
                                command=partial(self.run))
        layout.addWidget(button)

        # Add to main window
        self.main_layout.addLayout(layout)

    def run(self):
        file_path = self.file_path_text.text()
        if file_path == self.default_text:
            file_path = None

        import rig_tools.procs.find_rigs_to_update as find_rigs
        find_rigs.find_rigs_update(file_path=file_path)


# ----------------------------------------------------------------------------------------------------------------------

class MirrorJoint_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(MirrorJoint_Widget, self).__init__(parent)

        # Mirror Orientation
        m_ori_lyt = QHBoxLayout()
        m_ori_lyt.addWidget(QLabel("Mirror Orientation"))
        self.m_ori_btn_grp = QButtonGroup(self)

        xy_btn = QRadioButton("XY")
        self.m_ori_btn_grp.addButton(xy_btn)

        yz_btn = QRadioButton("YZ")
        yz_btn.setChecked(True)
        self.m_ori_btn_grp.addButton(yz_btn)

        xz_btn = QRadioButton("XZ")
        self.m_ori_btn_grp.addButton(xz_btn)

        m_ori_lyt.addWidget(xy_btn)
        m_ori_lyt.addWidget(yz_btn)
        m_ori_lyt.addWidget(xz_btn)

        # Mirror Function
        m_fn_lyt = QHBoxLayout()
        m_fn_lyt.addWidget(QLabel("Mirror Function"))
        self.m_fn_btn_grp = QButtonGroup(self)
        behavior_btn = QRadioButton("Behavior")
        behavior_btn.setChecked(True)
        self.m_fn_btn_grp.addButton(behavior_btn)

        orientation_btn = QRadioButton("Orientation")
        self.m_fn_btn_grp.addButton(orientation_btn)

        m_fn_lyt.addWidget(behavior_btn)
        m_fn_lyt.addWidget(orientation_btn)

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        do_button = tpu.IconButton(icon="rig/rig_create.png", label="Mirror Joint", command=partial(self.run))
        button_layout.addWidget(do_button)

        # Add to Layout
        self.main_layout.addLayout(m_ori_lyt)
        self.main_layout.addLayout(m_fn_lyt)
        self.main_layout.addLayout(button_layout)

    def run(self, *args):
        sel = i_utils.check_sel()
        if not sel:
            return

        mirror_axis = self.m_ori_btn_grp.checkedButton().text()
        mirror_type = self.m_fn_btn_grp.checkedButton().text()

        mib = False
        if mirror_type == "Behavior":
            mib = True

        axis_flag = mirror_axis.lower()
        axis_kw = {str("m" + axis_flag): True}

        for joint in sel:
            joint.mirror(sr=["L_", "R_"], mb=mib, **axis_kw)


# ----------------------------------------------------------------------------------------------------------------------

class DynamicSettings_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(DynamicSettings_Widget, self).__init__(parent)

        # Window Basics
        self.setWindowTitle("Dynamics Settings")
        role = os.environ.get("TT_STEPCODE")
        proj = os.environ.get("TT_PROJCODE")
        ugroups = os.environ.get("TT_USERGROUPS")
        # as_dev = False  # FOR TESTING ONLY
        as_dev = True if (i_utils.is_eav and role == "tex" and ("Rigging" in ugroups or "Pipeline" in ugroups)) \
                         or (not i_utils.is_eav and role == "rig") else False
        image_path = os.environ.get("PIPE_EXTERNAL") + "/images"

        # Get dynamic settings available
        dyn_settings = ["--- Create New ---"] if as_dev else []
        avail_dyn_settings = []
        top_nodes = i_node.get_top_nodes()
        for nd in top_nodes:
            avail_dyn_settings += [attr.replace("DynamicsSettings_", "").replace("_", " ")
                                   for attr in nd.attrs(ud=True) if attr.startswith("DynamicsSettings_")]
        if avail_dyn_settings:
            dyn_settings += sorted(list(set(avail_dyn_settings)))
        if not as_dev and not dyn_settings:
            dyn_settings = ["No Dynamic Settings Found"]

        # Combo Box layout
        combo_layout = QHBoxLayout()

        # Dynamics Options
        self.dyn_opt = QComboBox()
        self.dyn_opt.addItems(dyn_settings)
        combo_layout.addWidget(self.dyn_opt, 0, 0)
        self.dyn_opt.setMinimumWidth(250)  # So window title is visible

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        # Load button
        load_button = tpu.IconButton(label="Load Dynamics", icon=os.path.join(image_path, 'passsquare.png'),
                                     command=partial(self.load_setting))
        button_layout.addWidget(load_button)

        if as_dev:
            # Save button
            save_button = tpu.IconButton(label="Save Dynamics", icon=os.path.join(image_path, 'warningsquare.png'),
                                         command=partial(self.save_setting))
            button_layout.addWidget(save_button)

            # Delete button
            del_button = tpu.IconButton(label="Delete Dynamics", icon=os.path.join(image_path, 'errorsquare.png'),
                                        command=partial(self.delete_setting))
            button_layout.addWidget(del_button)

        # Add to window
        self.main_layout.addLayout(combo_layout)
        self.main_layout.addLayout(button_layout)

    def _check_dynamic_setting(self, dialog_error=True):
        setting_name = self.dyn_opt.currentText()
        if setting_name in ["--- Create New ---", "No Dynamic Settings Found"]:
            i_utils.error("'%s' is not a dynamics setting." % setting_name, dialog=dialog_error, raise_err=False)
            return False
        return setting_name

    def load_setting(self):
        # Get name
        setting_name = self._check_dynamic_setting()
        if not setting_name:
            return

        # Run
        rig_dynamics.load_dyn_settings(setting_name=setting_name)

    def save_setting(self):
        # Check selection. Nodes are needed
        sel = i_utils.check_sel()
        if not sel:
            return

        # Get name
        setting_name = self._check_dynamic_setting(dialog_error=False)
        new_setting = False
        if not setting_name:
            setting_name = i_utils.name_prompt(title="Dynamic Setting",
                                               message="What name should the dynamic setting have?")
            new_setting = True
            if not setting_name:
                return

        # Run
        rig_dynamics.save_dyn_settings(nodes=sel, setting_name=setting_name)

        # Add to option
        if new_setting:
            self.dyn_opt.addItem(setting_name)

        # Success Prompt
        i_utils.message(title="Settings Saved", message="Settings saved as: '%s'" % setting_name)

    def delete_setting(self):
        # Get name
        setting_name = self._check_dynamic_setting()
        if not setting_name:
            return

        # Confirm
        do_it = i_utils.message(title="Delete Setting?", message="Delete dynamic setting: '%s'?" % setting_name,
                                button=["Yes", "No"])
        if do_it != "Yes":
            return

        # Save current index item so can remove optionally
        i = self.dyn_opt.currentIndex()

        # Check selection. Nodes are optional
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)

        # Run
        rig_dynamics.delete_dyn_settings(nodes=sel, setting_name=setting_name)

        # Remove from options
        if not sel:  # Option may not be fully deleted, but only off of some items
            self.dyn_opt.setCurrentIndex(0)
            self.dyn_opt.removeItem(i)

        # Success Prompt
        i_utils.message(title="Deleted Setting", message="Deleted dynamics setting: '%s'" % setting_name)


# ----------------------------------------------------------------------------------------------------------------------

class Skinning_Widget(qt_utils.MainWindow):
    def __init__(self, parent=qt_utils.get_main_window()):
        super(Skinning_Widget, self).__init__(parent)

        self.weight_info = {}

        # Copy Weights
        cw_label_layout = QHBoxLayout()
        cw_label = QLabel("Copy Skins from one to many meshes/verts")
        cw_label.setFont(bold_font)
        cw_label_layout.addWidget(cw_label)
        cw_label_layout.setAlignment(Qt.AlignCenter)
        cw_layout = QHBoxLayout()
        cw_rcl = {"SkinAs": "import rig_tools.load_mel as rlm;rlm.exec_skin_as()"}
        cw_button = tpu.IconButton(label="Copy Skins", command=partial(self._copy_skins), icon="anm/19IKFKMatch.png",
                                   tool_tip="Copy Skins from first selected to rest selected",
                                   right_click_buttons=cw_rcl)
        cw_layout.addWidget(cw_button)
        self.cw_force_cb = QCheckBox("Force")
        self.cw_force_cb.setCheckState(Qt.Unchecked)
        self.cw_force_cb.setToolTip(
            "Force the copying - detaching existing skin from destination objects before copying")
        cw_layout.addWidget(self.cw_force_cb)
        self.cw_rui_cb = QCheckBox("RUI")
        self.cw_rui_cb.setCheckState(Qt.Checked)
        self.cw_rui_cb.setToolTip("Remove unused influences on source skin before copying?")
        cw_layout.addWidget(self.cw_rui_cb)

        # Copy/Paste/Average Weighting
        # - Label
        cpw_label_layout = QHBoxLayout()
        cpw_label = QLabel("Store and Paste weights for multiple verts")
        cpw_label.setFont(bold_font)
        cpw_label_layout.addWidget(cpw_label)
        cpw_label_layout.setAlignment(Qt.AlignCenter)
        # - Buttons
        cpw_layout = QHBoxLayout()
        cpw_layout.setAlignment(Qt.AlignCenter)
        # cpw_rcl = {"Store Average" : partial(self._store_weights, True)}
        cpw_store_button = tpu.IconButton(label="Store", command=partial(self._store_weights),
                                          icon="rig/rig_import.png",
                                          tool_tip="Stores weights of selected verts",
                                          # right_click_buttons=cpw_rcl, overlay_image="rig/rig_overlay_rightclick.png"
                                          )

        cpw_avg_button = tpu.IconButton(label="Store\nAverage", command=partial(self._store_weights, True),
                                        icon="rig/rig_import.png",
                                        tool_tip="Stores averaged weights of selected verts", )

        cpw_paste_button = tpu.IconButton(label="Paste", command=partial(self._paste_weights),
                                          icon="rig/rig_export.png",
                                          tool_tip="Pastes stored weight values onto selected verts",
                                          )

        io_ui_button = tpu.IconButton(icon="rig/rig_io_import_export.png",
                                      command=partial(self._open_io_ui), label="Imp/Exp",
                                      tool_tip="Import and Export Data",
                                      )

        cpw_layout.addWidget(cpw_store_button)
        cpw_layout.addWidget(cpw_paste_button)
        cpw_layout.addWidget(cpw_avg_button)
        cpw_layout.addWidget(io_ui_button)

        # Painting Tools
        # - Label
        paint_label_layout = QHBoxLayout()
        paint_label = QLabel("Painting Tools")
        paint_label.setFont(bold_font)
        paint_label_layout.addWidget(paint_label)
        paint_label_layout.setAlignment(Qt.AlignCenter)
        # - Buttons
        paint_layout = QHBoxLayout()
        paint_layout.setAlignment(Qt.AlignCenter)
        # - Multi-Smooth
        multi_smooth_button = tpu.IconButton(label="Multi\nSmooth",
                                             command="from ToolPanel import tool_panel_utils as tpu;import maya_ui.multi_smooth as ui;tpu.PopOff(widget=ui.MultiSmooth_UI)",
                                             icon="anm/43Smooth.png",
                                             tool_tip="Multi-Smooth UI as a shortcut for hitting the 'Smooth' button several times", )
        paint_layout.addWidget(multi_smooth_button)
        # - Soft Selection Weights
        soft_sel_weights_button = tpu.IconButton(label="Soft Sel\nWeights",
                                                 command="import icon_api.deformer as i_deformer;i_deformer.save_soft_selection()",
                                                 icon="rig/feather.png",
                                                 tool_tip="Apply Soft Selection as Weights (select joint and skinned verts)",
                                                 )
        paint_layout.addWidget(soft_sel_weights_button)
        # - Force Normal
        normal_button = tpu.IconButton(label="Normalize",
                                       command="import icon_api.deformer as i_deformer;i_deformer.force_normalize_skins()",
                                       icon="rig/rig_normal.png",
                                       tool_tip="Force all skins in scene to normalize and set to interactive.",
                                       )
        paint_layout.addWidget(normal_button)

        # Misc Tools
        misc_label_layout = QHBoxLayout()
        misc_label = QLabel("Misc Skinning Tools")
        misc_label.setFont(bold_font)
        misc_label_layout.addWidget(misc_label)
        misc_label_layout.setAlignment(Qt.AlignCenter)
        misc_layout = QHBoxLayout()
        misc_layout.setAlignment(Qt.AlignCenter)
        # - Kill RGB
        kill_rgb_button = tpu.IconButton(label="Kill RGB\nConnections", command=partial(self._kill_rgb),
                                         icon="rig/rig_color.png",
                                         tool_tip="Select skin or geo. If no selection, run on all skinned joints.",
                                         )
        misc_layout.addWidget(kill_rgb_button)
        # - RUI
        rui_button = tpu.IconButton(label="Remove Unused\nInfluences", command=partial(self._rui),
                                    icon="rig/rig_insert_reskin.png",
                                    tool_tip="Select skin or geo. If no selection, run on all skins.",
                                    )
        misc_layout.addWidget(rui_button)
        # - Clean Unbind
        unbind_button = tpu.IconButton(label="Clean\nUnbind",
                                       command="import icon_api.deformer as i_deformer;i_deformer.clean_unbind_sel()",
                                       icon="rig/rig_clean_unbind.png",
                                       tool_tip="Clean Unbind (delete Orig Shape Maya leaves behind). Sel geos.",
                                       )
        misc_layout.addWidget(unbind_button)

        # Skin Checks
        check_label_layout = QHBoxLayout()
        check_label = QLabel("Skin Checking Tools")
        check_label.setFont(bold_font)
        check_label_layout.addWidget(check_label)
        check_label_layout.setAlignment(Qt.AlignCenter)
        # - Skin Checked
        self.skin_checked_text = QLabel("No Skin Checked")
        self.skin_checked_text.setAlignment(Qt.AlignCenter)
        self.skin_checked_text.setFont(italic_font)
        # - Mode
        skin_mode_layout = QHBoxLayout()
        mode_label = QLabel("Skin Mode:")
        mode_label.setAlignment(Qt.AlignRight)
        mode_label.setFont(bold_font)
        skin_mode_layout.addWidget(mode_label)
        self.skin_mode_text = QLabel("No Selection")
        skin_mode_layout.addWidget(self.skin_mode_text)
        # - Button
        skin_check_button = QPushButton("Check Sel")
        skin_check_button.setToolTip("Select either a skinned mesh or skinned verts.\n\nInfo will appear in text above")
        skin_check_button.clicked.connect(self._check_skin)

        # Add to main layout
        # - Copy Skins
        self.main_layout.addLayout(cw_label_layout)
        self.main_layout.addLayout(cw_layout)
        # - SEP
        self.main_layout.addWidget(separator())
        # - Copy/Paste/Average Weights
        self.main_layout.addLayout(cpw_label_layout)
        self.main_layout.addLayout(cpw_layout)
        # - SEP
        self.main_layout.addWidget(separator())
        # - Paint
        self.main_layout.addLayout(paint_label_layout)
        self.main_layout.addLayout(paint_layout)
        # - SEP
        self.main_layout.addWidget(separator())
        # - Misc Skin Tools
        self.main_layout.addLayout(misc_label_layout)
        self.main_layout.addLayout(misc_layout)
        # - SEP
        self.main_layout.addWidget(separator())
        # - Check Tools
        self.main_layout.addLayout(check_label_layout)
        self.main_layout.addWidget(self.skin_checked_text)
        self.main_layout.addLayout(skin_mode_layout)
        self.main_layout.addWidget(skin_check_button)

    def _open_io_ui(self):
        tpu.PopOff(widget=IO_Widget("Deformer - skinCluster - Mesh Only"))

    def _copy_skins(self):
        force = self.cw_force_cb.isChecked()
        rui = self.cw_rui_cb.isChecked()
        i_deformer.copy_skin_sel(force=force, rui=rui)

    def __get_sel_skin_info(self, require_verts=False):
        # Check sel
        sel = i_utils.check_sel(fl=True)
        if not sel:
            return

        # Get verts
        verts = [vtx for vtx in sel if ".vtx[" in vtx]
        if require_verts and not verts:
            i_utils.error("No verts selected.", dialog=True)
            return

        # Get mesh
        mesh = None
        if verts:
            mesh = i_node.Node(verts[0].split(".")[0])
        elif sel:
            mesh = sel[0]

        # Get skin
        skin = i_deformer.get_skin(obj=mesh, raise_error=False, dialog_error=True)
        if not skin:
            return

        # Return
        return {"verts_sel": sel, "verts": verts, "mesh": mesh, "skin": skin}

    def __get_skin_mode(self, skin=None):
        # Get skin
        if not skin:
            skin_info = self.__get_sel_skin_info()
            if not skin_info:
                return
            skin = skin_info.get("skin")

        # Get mode
        skin_mode = ["none", "interactive", "post"][cmds.skinCluster(skin.name, q=True, normalizeWeights=True)]

        # Return
        return skin_mode

    def __get_sel_vert_info(self):
        # Get skin
        skin_info = self.__get_sel_skin_info(require_verts=True)
        if not skin_info:
            return
        skin = skin_info.get("skin")

        # Check skin mode (only interactive works)
        skin_mode = self.__get_skin_mode(skin=skin)
        if skin_mode != "interactive":
            i_utils.error(
                "Store and Paste vert weights requires interactive mode.\n\n'%s' is in mode: '%s'." % (skin, skin_mode),
                dialog=True)
            return

        # Get influences
        influences = cmds.skinCluster(skin.name, q=True, inf=True)
        skin_info["influences"] = influences

        # Return
        return i_utils.Mimic(skin_info)

    def _check_skin(self):
        # Get skin
        skin_info = self.__get_sel_skin_info()
        if not skin_info:
            return
        skin = skin_info.get("skin")

        # Edit name
        self.skin_checked_text.setText(skin.name)

        # Skin mode
        skin_mode = self.__get_skin_mode(skin=skin)
        self.skin_mode_text.setText(skin_mode.capitalize())

    def _store_weights(self, average=False):
        """
        Copies the influences of the first selected vertex and stores the influence in "weight_info"

        :param: average (bool) - Average the influence on all selected vertices?
        """
        # Empty var
        self.weight_info = {}

        # Get skin info
        skin_info = self.__get_sel_vert_info()
        if not skin_info:
            return

        # Get percentages
        if average:
            per_vert_percents = [i_deformer.skin_percent(skin_info.skin, vert, q=True, v=True) for vert in
                                 skin_info.verts]
            if not per_vert_percents:
                i_utils.error("Cannot find skin percent information for '%s'." % skin_info.skin, dialog=True)
                return
            weight_percents = logic_py.average_nested_list(per_vert_percents)
        else:
            weight_percents = i_deformer.skin_percent(skin_info.skin, skin_info.verts[0], q=True, v=True)

        # Store weight info
        for i, inf in enumerate(skin_info.influences):
            self.weight_info[i_node.Node(inf)] = weight_percents[i]

        # Confirmation
        RIG_LOG.info("Skin Weights Copied for:\n\n%s" % (", ".join(i_utils.convert_data(skin_info.verts_sel))))

    def _paste_weights(self):
        # Check stored weights
        if not self.weight_info:
            i_utils.error("No weight info stored. Copy first.", dialog=True)
            return

            # Get skin info
        skin_info = self.__get_sel_vert_info()
        if not skin_info:
            return

        # Disable Normalize
        skin_info.skin.normalizeWeights.set(0)

        # Convert weight info into list of lists so Maya can read it
        influence_weights = map(list, self.weight_info.items())

        # Apply weights
        for vert in skin_info.verts:
            i_deformer.skin_percent(skin_info.skin, vert, transformValue=influence_weights)

        # Enable Normalize
        skin_info.skin.normalizeWeights.set(1)

        # Confirmation
        RIG_LOG.info("Skin Weights Pasted to:\n\n%s" % (", ".join(i_utils.convert_data(skin_info.verts_sel))))

    def _kill_rgb(self):
        sel = i_utils.check_sel(dialog_error=False, raise_error=False)
        if sel:
            i_deformer.disconnect_skin_rgb_sel()
        else:
            i_deformer.disconnect_skin_rgb_all()

    def _rui(self):
        sel = i_utils.check_sel(dialog_error=False, raise_error=False)
        if sel:
            i_deformer.remove_unused_influences_sel()
        else:
            i_deformer.remove_unused_influences_all()


# ----------------------------------------------------------------------------------------------------------------------

class BlendControls_Widget(qt_utils.MainWindow):
    def __init__(self, parent=qt_utils.get_main_window()):
        super(BlendControls_Widget, self).__init__(parent)

        # Make a new widget window
        self.setWindowTitle("Create Blend Controls")

        # Layout
        widget_layout = QVBoxLayout()

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name"))
        self.name_text = QLineEdit("")
        self.name_text.setToolTip(str("Base name to give created controls"))
        name_layout.addWidget(self.name_text)

        # Count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Controls"))
        self.count = QSpinBox()
        self.count.setValue(3)
        self.count.setMinimum(1)
        self.count.setToolTip(str("Number of Controls to make"))
        count_layout.addWidget(self.count)

        # Color Vars
        color_names = [" ".join(logic_py.split_camel_case_string(string=color)) for color in all_control_colors]
        color_titles = [color[0].upper() + color[1:] for color in color_names]

        # Blend Color
        blend_color_layout = QHBoxLayout()
        blend_color_layout.addWidget(QLabel("Blend Color"))
        self.blend_color_dropdown = QComboBox()
        self.blend_color_dropdown.addItems(color_titles)
        blend_default_i = all_control_colors.index("red")
        self.blend_color_dropdown.setCurrentIndex(blend_default_i)
        self.blend_color_dropdown.setToolTip(str("Color of Blend control created."))
        blend_color_layout.addWidget(self.blend_color_dropdown)

        # Target Color
        target_color_layout = QHBoxLayout()
        target_color_layout.addWidget(QLabel("Target Color"))
        self.target_color_dropdown = QComboBox()
        self.target_color_dropdown.addItems(color_titles)
        target_default_i = all_control_colors.index("green")
        self.target_color_dropdown.setCurrentIndex(target_default_i)
        self.target_color_dropdown.setToolTip(str("Color of Target control created."))
        target_color_layout.addWidget(self.target_color_dropdown)

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button = tpu.IconButton(icon="rig/rig_create.png", label="Create", command=partial(self.run))
        button_layout.addWidget(button)

        # Add to Layout
        widget_layout.addLayout(name_layout)
        widget_layout.addLayout(count_layout)
        widget_layout.addLayout(target_color_layout)
        widget_layout.addLayout(blend_color_layout)
        widget_layout.addLayout(button_layout)

        # Show window
        self.main_layout.addLayout(widget_layout)
        self.show()

        # Make not resizeable
        # :note: Must be done only after window is shown to get proper dimensions
        self.setFixedSize(300, self.size().height())

    def run(self):
        name = self.name_text.text()
        sel = i_utils.check_sel(raise_error=False)
        if not name and sel:
            name = sel[0].replace(":", "_")
        count = int(self.count.text())
        blend_color = all_control_colors[self.blend_color_dropdown.currentIndex()]
        target_color = all_control_colors[self.target_color_dropdown.currentIndex()]

        try:  # Temp wrap to get more info to solve error ticket: AUTO-239
            rig_deformers.create_blend_control(name=name, count=count, blend_color=blend_color,
                                               target_color=target_color)
        except:
            i_utils.error(
                "Could not create blend control.\nSel: %s\nName: %s\nCount: %i\nBlend Color: %s\nTarget Color: %s"
                "\n\nError:\n%s" % (sel, name, count, blend_color, target_color, traceback.format_exc()))

        self.close()


# ----------------------------------------------------------------------------------------------------------------------

class FaceBake_Widget(qt_utils.MainWindow):
    def __init__(self, parent=qt_utils.get_main_window()):
        super(FaceBake_Widget, self).__init__(parent)

        # Vars
        self.all_drivers = i_utils.ls("*_ControlDriver")
        if not self.all_drivers:
            i_utils.error("No Face 'ControlDriver' nodes found. Is there a face in the scene?", dialog=True)
            return
        self.sides = {}
        self.sections = {}
        self.sub_directions = {}
        self.directions = {}

        for driver in self.all_drivers:
            driver_attrs = driver.attrs(ud=True, cb=True)
            for dattr in driver_attrs:
                # - Dissect the attr name
                spl = dattr.split("_")
                side = spl[0]
                direc = spl[-1]
                sect = "_".join(spl[1:-1])
                subdir = None
                if len(spl[1:-1]) == 3 or spl[-2] in ["In", "Mid", "Out"]:
                    subdir = spl[-2]
                    sect = "_".join(spl[1:-2])
                # - Add to main vars
                self.add_to(side, driver + "." + dattr, "sides")
                self.add_to(sect, driver + "." + dattr, "sections")
                self.add_to(subdir, driver + "." + dattr, "sub_directions")
                self.add_to(direc, driver + "." + dattr, "directions")

        # Dropdown Layout
        dpdn_layout = QHBoxLayout()

        # Side dropdown
        self.side_dpdn = QComboBox()
        self.side_dpdn.addItems(["--Side--"] + sorted(self.sides.keys()))
        dpdn_layout.addWidget(self.side_dpdn)

        # Section dropdown
        self.sect_dpdn = QComboBox()
        self.sect_dpdn.addItems(["--Section--"] + sorted(self.sections.keys()))
        dpdn_layout.addWidget(self.sect_dpdn)

        # SubDirection dropdown
        self.subdir_dpdn = QComboBox()
        self.subdir_dpdn.addItems(["--SubDirection--"] + sorted(self.sub_directions.keys()))
        dpdn_layout.addWidget(self.subdir_dpdn)

        # Direction dropdown
        self.dir_dpdn = QComboBox()
        self.dir_dpdn.addItems(["--Direction--"] + sorted(self.directions.keys()))
        dpdn_layout.addWidget(self.dir_dpdn)

        # Button
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn = tpu.IconButton(label="Bake", command=partial(self.run), icon="rig/rig_cake.png",
                             tool_tip="Bake the in-scene shape to the defined area drivers only.",
                             )
        btn_layout.addWidget(btn)

        # Add to window
        self.main_layout.addLayout(dpdn_layout)
        self.main_layout.addLayout(btn_layout)

    def add_to(self, opt, val, dict_attr):
        dictionary = getattr(self, dict_attr)
        if opt not in dictionary:
            dictionary[opt] = []
        dictionary[opt].append(val)

    def run(self):
        # Get the driver node and attr from dropdowns
        side = self.side_dpdn.currentText()
        if side.startswith("-"):
            side = None
        sect = self.sect_dpdn.currentText()
        if sect.startswith("-"):
            sect = None
        subd = self.subdir_dpdn.currentText()
        if subd.startswith("-"):
            subd = None
        direc = self.dir_dpdn.currentText()
        if direc.startswith("-"):
            direc = None

        # Get the node/attr that matches criteria
        filters = []
        if side:
            filters.append(set(self.sides.get(side)))
        if sect:
            filters.append(set(self.sections.get(sect)))
        if subd:
            filters.append(set(self.sub_directions.get(subd)))
        if direc:
            filters.append(set(self.directions.get(direc)))
        filtered = set.intersection(*filters)
        if not filtered:
            i_utils.error("No attribute matches filter choices. Choose other dropdowns.", dialog=True)
            return

        # Convert filtered to Bake-usable args
        filtered_driver_attrs = {}
        for nd_at in list(filtered):
            nd, at = nd_at.split(".")
            if nd not in filtered_driver_attrs.keys():
                filtered_driver_attrs[nd] = []
            filtered_driver_attrs[nd].append(at)
        filtered_driver_attrs = i_utils.convert_data(filtered_driver_attrs, to_generic=False)

        # Run
        fb = rig_face.FaceBake()
        fb.given_driver_attrs = filtered_driver_attrs
        fb.run()


# ----------------------------------------------------------------------------------------------------------------------

class Constraints_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(Constraints_Widget, self).__init__(parent)

        # Constraint Types
        cns_layout = QHBoxLayout()
        cns_label = QLabel("Constraint Type")
        cns_label.setAlignment(Qt.AlignCenter)
        self.pac_cb = QCheckBox("Parent")
        self.pac_cb.setCheckState(Qt.Checked)
        cns_layout.addWidget(self.pac_cb)
        self.pc_cb = QCheckBox("Point")
        cns_layout.addWidget(self.pc_cb)
        self.oc_cb = QCheckBox("Orient")
        cns_layout.addWidget(self.oc_cb)
        self.sc_cb = QCheckBox("Scale")
        cns_layout.addWidget(self.sc_cb)
        self.main_layout.addWidget(cns_label)
        self.main_layout.addLayout(cns_layout)
        # - Default Pac/Sc
        self.pac_cb.setCheckState(Qt.Checked)
        self.sc_cb.setCheckState(Qt.Checked)

        self.main_layout.addWidget(separator())

        # Maintain Offset?
        mo_layout = QHBoxLayout()
        self.mo_cb = QCheckBox("Maintain Offset")
        self.mo_cb.setCheckState(Qt.Checked)
        mo_layout.addWidget(self.mo_cb)
        mo_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(mo_layout)

        self.main_layout.addWidget(separator())

        # Number of drivers
        driver_layout = QHBoxLayout()
        self.drivers_btn_grp = QButtonGroup()
        driver_single_btn = QRadioButton("Single Driver")
        self.drivers_btn_grp.addButton(driver_single_btn)
        driver_layout.addWidget(driver_single_btn)
        driver_multi_btn = QRadioButton("Multi Driver")
        self.drivers_btn_grp.addButton(driver_multi_btn)
        driver_multi_btn.setChecked(True)
        driver_layout.addWidget(driver_multi_btn)
        self.main_layout.addLayout(driver_layout)

        self.main_layout.addWidget(separator())

        # Button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button = tpu.IconButton(icon="rig/rig_constrain.png", label="Constrain",
                                command=partial(self.run))
        button_layout.addWidget(button)
        self.main_layout.addLayout(button_layout)

    def run(self, *args):
        # Get UI Info
        # - Attrs
        pac = self.pac_cb.isChecked()
        pc = self.pc_cb.isChecked()
        oc = self.oc_cb.isChecked()
        sc = self.sc_cb.isChecked()
        attrs = ""
        if pac or pc:
            attrs += "t"
        if pac or oc:
            attrs += "r"
        if sc:
            attrs += "s"
        # - Maintain Offset?
        mo = self.mo_cb.isChecked()
        # - Single or Multi Driver
        driver_type = self.drivers_btn_grp.checkedButton().text()
        one_driver = True if driver_type == "Single Driver" else False

        # Run
        i_node.copy_pose_sel(action="constrain", attrs=attrs, mo=mo, one_driver=one_driver)


# ----------------------------------------------------------------------------------------------------------------------

class ControlSliderWidget(QHBoxLayout):
    def __init__(self):
        super(ControlSliderWidget, self).__init__()
        lyt = QVBoxLayout()

        lyt.addWidget(QLabel("Scale Control Size"))

        slider_layout = QHBoxLayout()

        self._lcd = QLCDNumber(3)
        self._lcd.setDigitCount(3)
        self._lcd.setStyleSheet("background-color: grey")
        self._lcd.setMaximumWidth(30)
        slider_layout.addWidget(self._lcd)

        # Add Slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(1, 500)
        self.connect(self._slider, SIGNAL("valueChanged(int)"), self._lcd, SLOT("display(int)"))
        self.connect(self._slider, SIGNAL("valueChanged(int)"), self, SIGNAL("valueChanged(int)"))
        self._prev_slider_value = 1.0
        self._slider.setValue(100)  # This is scale of 1.0
        self._slider.valueChanged[int].connect(self._widget_control_slider_run)
        slider_layout.addWidget(self._slider)

        reset_button = QPushButton("R")
        reset_button.setToolTip("Reset slider to scale 1.00.")
        reset_button.clicked.connect(partial(self._slider.setValue, 100))
        slider_layout.addWidget(reset_button)

        lyt.addLayout(slider_layout)
        self.addLayout(lyt)

    def _widget_control_slider_run(self):
        controls_resizing = i_control.get_controls(info_connections_only=False, dialog_error=False)
        if not controls_resizing:
            return

        slider_value = float(self._slider.value()) / 100  # :note: Sliders do not work on floats so got to fake it
        if slider_value == self._prev_slider_value:
            return

        slider_scale = [max(float(slider_value) / float(self._prev_slider_value), 0.25) for i in range(3)]
        self._prev_slider_value = slider_value

        cvs = []
        for control in controls_resizing:
            cvs += control.get_cvs()
        i_utils.xform(cvs, slider_scale, as_fn="scale")


# ----------------------------------------------------------------------------------------------------------------------

class DynamicsWeightsImportExport_Widget(qt_utils.MainWindow):
    def __init__(self, parent=None):
        super(DynamicsWeightsImportExport_Widget, self).__init__(parent)

        self._set_window_pref()
        self._add_layouts()
        self._add_widgets()

    def _set_window_pref(self):
        self.setMinimumWidth(600)

    def _add_layouts(self):
        self.mainLayout = QVBoxLayout()
        self.main_layout.addLayout(self.mainLayout)
        self.pathLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.pathLayout)
        self.btnsLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.btnsLayout)

    def _add_widgets(self):
        # pathLayout
        self.pthButton = QPushButton("Path:")
        self.pthButton.clicked.connect(self._query_path)
        self.pthButton.setMinimumWidth(60)
        self.pathLayout.addWidget(self.pthButton)

        self.pthText = QLineEdit('C:\\Users\\{0}\\Desktop'.format(os.environ["USERNAME"]))
        self.pathLayout.addWidget(self.pthText)

        # btnsLayout
        self.expButton = QPushButton("Export")
        self.expButton.clicked.connect(self._export_csv_pre)
        self.expButton.setToolTip('Select ONE node to export weights to file path.')
        self.btnsLayout.addWidget(self.expButton)

        self.impButton = QPushButton("Import")
        self.impButton.clicked.connect(self._import_csv_pre)
        self.impButton.setToolTip('Select node(s) to import weights from file path.')
        self.btnsLayout.addWidget(self.impButton)

    def _query_path(self):
        dialog = QFileDialog(self, "Browse", self.pthText.text())
        dialog.setNameFilters(["CSV files (*.csv)"])
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0].replace("/", "\\")
            if path[-4:].lower() != '.csv':
                path += '.csv'
            self.pthText.setText(path)

    def _export_csv_pre(self):
        if len(cmds.ls(sl=True)) and self.pthText.text():
            self._export_csv(cmds.ls(sl=True)[0], self.pthText.text().replace('\\', '/'))

    def _import_csv_pre(self):
        if len(cmds.ls(sl=True)) and self.pthText.text():
            self._import_csv(cmds.ls(sl=True, fl=True), self.pthText.text().replace('\\', '/'))

    def _export_csv(self, nodeName, filePath):
        valuesList = cmds.percent(nodeName, q=True, v=True)
        with open(filePath, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for value in valuesList:
                csv_writer.writerow([value])
        csv_file.close()

    def _import_csv(self, selItems, filePath):
        if not os.path.isfile(filePath):
            i_utils.error('File path does not exsist: {0}'.format(filePath))
        else:
            valuesList = []
            with open(filePath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for value in csv_reader:
                    valuesList.append(float(value[0]))
            csv_file.close()

            deformerList = []
            indexList = []  # list of two items, 1st(int): index to fetch in csv file. 2nd: the vtx name to set the value on
            for selItem in selItems:
                if cmds.objectType(selItem) == 'nonLinear':
                    deformerList.append(selItem)
                elif '.vtx[' in selItem:
                    selIndexNum = int(selItem.split('.vtx[')[-1][:-1])
                    indexList.append((selIndexNum, selItem))
                else:
                    if cmds.objectType(selItem) == 'transform':
                        if cmds.objectType(cmds.listRelatives(selItem, shapes=True)[0]) == 'mesh':
                            totalVtx = cmds.polyEvaluate(selItem, v=True)
                            indexList.extend([(i, '{0}.vtx[{1}]'.format(selItem, i)) for i in range(totalVtx)])

            for deformer in deformerList:
                for ind in indexList:
                    cmds.percent(deformer, ind[1], v=valuesList[ind[0]])
