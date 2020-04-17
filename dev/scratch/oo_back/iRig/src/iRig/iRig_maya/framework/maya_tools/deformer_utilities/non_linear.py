import maya_tools.deformer_utilities.general as gtl
import maya.cmds as mc


def create_nonlinear_deformer(deformer_type, geometry, **kwargs):
    if len(geometry) == 0:
        raise Exception('You must provide geometry to create_nonlinear_deformer')
    bend_name, bend_handle_name = mc.nonLinear(type=deformer_type, *geometry, **kwargs)
    bend_handle_shape_name = mc.listRelatives(bend_handle_name, c=True)[0]
    bend_deformer = gtl.get_m_object(bend_name)
    bend_handle_shape = gtl.get_m_object(bend_handle_shape_name)
    bend_handle = gtl.get_m_object(bend_handle_name)
    geometry_functions = gtl.oma.MFnGeometryFilter(bend_deformer)
    set_m_object = geometry_functions.deformerSet()
    return bend_deformer, bend_handle, bend_handle_shape, set_m_object

