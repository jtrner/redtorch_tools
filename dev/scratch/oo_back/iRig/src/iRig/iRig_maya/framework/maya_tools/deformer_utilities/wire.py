import maya_tools.deformer_utilities.general as gtl
import maya.cmds as mc

def get_wire_data(m_object):
    # Get geometry, weights, plug values from wire deformer

    return dict()


def create_wire_deformer(curve, *geometry, **kwargs):

    deformer_name, _ = mc.wire(*geometry, wire=curve, **kwargs)

    attribute = deformer_name + '.baseWire'
    base_wire_name = mc.listConnections(attribute)[0]
    base_wire_shape_name = mc.listConnections(attribute, shapes=True)[0]

    deformer = gtl.get_m_object(deformer_name)
    base_wire = gtl.get_m_object(base_wire_name)
    base_wire_shape = gtl.get_m_object(base_wire_shape_name)

    set_m_object = gtl.oma.MFnGeometryFilter(deformer).deformerSet()

    return deformer, base_wire, base_wire_shape, set_m_object

