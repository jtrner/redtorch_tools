"""Provides user friendly way of building wire rigs in Maya"""

# import maya modules
from maya import cmds

# define custom modules
import icon_api.node as i_node
import icon_api.attr as i_attr

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "IL"
__version__ = "1.0.1"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def setup_cls(name="", cvs=[], add_contrls=True):
    """
    Sets up cluster control handles along a curve.
    :param name: <str> name to use for controller and cluster creation.
    :param cvs: <list> list of cvs.
    :returns: <list> cluster handles.
    """
    handles_ls = []
    ctrls_ls = []
    idx = 0
    for idx in range(0, len(cvs)):
        cv = cvs[idx]
        num_str = str(idx+1).zfill(2)
        new_name = "{}_Tweak_{}".format(name, num_str)
        print new_name, idx, num_str
        cls_hdl = cmds.cluster(cv, name='{}_Cls'.format(new_name))[-1]
        i_control = i_node.create("control", name=new_name, control_type="3D Sphere", with_gimbal=False,
                                  color="aqua")
        offset_grp = str(i_control.top_tfm)
        ctrl_name = str(i_control.control)
        cmds.xform(offset_grp, ws=1, t=cmds.xform(cv, ws=1, t=1, q=1))
        for t in ['.tx','.ty','.tz','.rx','.ry','.rz']:
            cmds.connectAttr(ctrl_name + t, cls_hdl + t)
        handles_ls.append(cls_hdl)
        ctrls_ls.append(offset_grp)
    cmds.group(ctrls_ls, name=new_name + '_Ctrl_Grp')
    cmds.group(handles_ls, name=new_name + '_Cls_Grp')
    return handles_ls


def do_it(name=''):
    """
    Creates a standarized wire setup.
    Select the nurbsCurve and the mesh, run this command
    :returns: <bool> True for success. <bool> False for failure.
    """
    if not name:
        name = raw_input("Please Enter a Name: ")
    if not name:
        cmds.warning('[Wire Setup] :: Please enter a name.')
        return 0

    # improve the name
    if "_" in name:
        name.replace("_", " ")
    name = name.title()
    name = name.replace(" ", "_")
    curve_name = name + '_Crv'

    # collect selection data
    my_list = cmds.ls(sl=1)
    my_wire = cmds.filterExpand(my_list, sm=9) or []
    my_cvs = cmds.filterExpand(my_list, sm=28) or []
    my_mesh = cmds.filterExpand(cmds.ls(sl=1), sm=12) or []

    if not any(my_list + my_wire):
        if not any(my_list + my_cvs):
            cmds.warning("[Wire Setup] :: No wire selected to continue with this operation.")
            return False

    # verify CV data
    if not my_wire and my_cvs:
        my_wire = cmds.listRelatives(cmds.listRelatives(my_cvs[0], p=1), p=1)
    if not my_cvs:
        my_cvs = cmds.ls(my_wire[0] + '.cv[*]', fl=1)

    # setup the curve with custers and controllers
    setup_cls(cvs=my_cvs, name=name)

    # rename the curve after the wire setup
    if not curve_name in my_wire[0]:
        print("\n[Wire Setup] :: Renaming nurbsCurve: {} >> {}".format(my_wire, curve_name))
        my_wire = cmds.rename(my_wire[0], curve_name)

    if my_mesh:
        # if mesh is in selection, install wire
        cmds.wire(my_mesh, my_wire, name=name+'_Wire')
    return True
