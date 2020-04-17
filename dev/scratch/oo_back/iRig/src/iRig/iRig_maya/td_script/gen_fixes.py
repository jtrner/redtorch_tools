import icon_api.node as i_node
import icon_api.control as i_control
import icon_api.utils as i_utils


def create_fake_template_curves():
    gui_control = "Face_Gui_Ctrl"
    if not i_utils.check_exists(gui_control):
        i_utils.error("'%s' does not exist" % gui_control, dialog=True)
        return
    gui_control = i_node.Node("Face_Gui_Ctrl")
    for side in ["L", "R"]:
       base_name = "Face_" + side
       # Templated "moved" markers
       template_curves_grp = i_node.create("transform", name=base_name + "_TemplateCurves", parent=gui_control, use_existing=True)
       if template_curves_grp.existed:
           print("'%s' already existed. Was this hack already used?" % template_curves_grp)
           continue
       # - Lines
       for line_control in ["Squint_Ctrl", "Mouth_CornerPinch_Ctrl"]:
           i_control.create_template_limits_line(control=i_node.Node(base_name + "_" + line_control), parent=template_curves_grp)
       # - Dupe curves
       for dupe_control in ["Nostril_Ctrl"]:
           dupe = i_node.Node(base_name + "_" + dupe_control).duplicate(name_sr=["_Ctrl", "_Template_Crv"])[0]
           dupe.set_display("Template")
           # :note: don't parent this into the template group because then the curve jumps. Just leave it with same as orig's parent
