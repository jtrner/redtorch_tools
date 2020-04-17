import maya_tools.deformer_utilities.general as gtl
import maya.cmds as mc


def create_lattice(*geometry, **kwargs):

    deformer_name, lattice_name, lattice_base_name = (
        mc.lattice(*geometry, **kwargs)
        if geometry else
        mc.lattice(geometry, **kwargs)
    )
    lattice_shape_name = mc.listRelatives(lattice_name, c=True)[0]
    lattice_base_shape_name = mc.listRelatives(lattice_base_name, c=True)[0]
    deformer = gtl.get_m_object(deformer_name)
    lattice = gtl.get_m_object(lattice_name)
    base_lattice = gtl.get_m_object(lattice_base_name)

    lattice_shape = gtl.get_m_object(lattice_shape_name)
    base_lattice_shape = gtl.get_m_object(lattice_base_shape_name)

    geometry_functions = gtl.oma.MFnGeometryFilter(deformer)
    set_m_object = geometry_functions.deformerSet()
    return deformer, lattice, base_lattice, lattice_shape, base_lattice_shape, set_m_object

