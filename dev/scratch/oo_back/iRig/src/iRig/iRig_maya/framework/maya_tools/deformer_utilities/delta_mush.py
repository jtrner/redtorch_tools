import maya_tools.deformer_utilities.general as gtl
import maya_tools.utilities.decorators as dec
import maya.cmds as mc


@dec.m_object_arg
def get_delta_mush_data(mesh):
    """
    Create and return a dictionary of delta mush values:
        - name: delta mush node's name
        - geometry: nodes effected by the delta mush
        - plug_values: delta mush node attribute values
        - weights: delta mush weights (list)
    :param mesh: (transform) - node to retrieve delta mesh data from
    :return: (dict) - delta mush data
    """
    node_name = gtl.get_selection_string(mesh)
    delta_mush_node = gtl.find_deformer_node(mesh, 'deltaMush')
    if not delta_mush_node:
        return None
    # get delta mush's attribute values in the channel box
    plug_values_dict = {}
    for attr in mc.listAttr(delta_mush_node, keyable=True, m=True):
        val = mc.getAttr('{node}.{attr}'.format(node=delta_mush_node, attr=attr))
        plug_values_dict[str(attr)] = val
    return dict(
        name=delta_mush_node,
        geometry=mc.deltaMush(node_name, geometry=True, q=True),
        plug_values=plug_values_dict,
        weights=gtl.get_deformer_weights(delta_mush_node)
        )


def set_delta_mush_data(data):
    """
    Set the node's delta mush with the delta mush dictionary
    :param data: (dict) - dictionary of values to pass onto node's delta mush
    :return: None
    """
    plug_values_dict = data['plug_values']
    weights = data['weights']
    delta_mush_node = mc.deltaMush(
        data['geometry'],
        name=data['name']
    )[0]

    # set attributes of new delta mush
    for plug_key in plug_values_dict.keys():
        value = plug_values_dict[plug_key]
        mc.setAttr('{0}.{1}'.format(delta_mush_node, plug_key), value)
    gtl.set_deformer_weights(delta_mush_node, weights)

