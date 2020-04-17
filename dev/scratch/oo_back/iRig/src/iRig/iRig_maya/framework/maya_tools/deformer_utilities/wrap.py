import maya.cmds as mc


def get_wrap_data(wrap_node):


    ### NOTE Add weights


    """
    Create and return a dictionary of wrap deformer values:
        - name: wrap node's name
        - target_geometry: list of geometry shapes influencing the wrap deformer
        - source_geometry: list of geometry shapes affected by wrap deformer
        - plug_values: wrap node attribute values
    :param wrap_node: wrap deformer node
    :return: (dict) - wrap deformer node values
    """
    source_mesh = mc.listConnections('{node}.driverPoints'.format(node=wrap_node), s=True, d=False, sh=True)
    target_mesh = mc.listConnections('{node}.outputGeometry'.format(node=wrap_node), s=False, d=True, sh=True)[0]
    # get wrap deformer's attribute values in the channel box
    plug_values_dict = {}
    for attr in mc.listAttr(wrap_node, k=True, m=True):
        val = mc.getAttr('{node}.{attr}'.format(node=wrap_node, attr=attr))
        plug_values_dict[str(attr)] = val
    return dict(
        name=wrap_node,
        target_geometry=target_mesh,
        source_geometry=source_mesh,
        plug_values=plug_values_dict
        )


def create_wrap(data):

    ### NOTE Add weights


    """
    Set the node's wrap deformer with the wrap deformer dictionary
    :param data: (dict) - dictionary of values to pass onto node's wrap deformer
    :return: None
    """
    wrap_name = data['name']
    target_geo = data['target_geometry']
    source_geo = data['source_geometry']
    plug_values_dict = data['plug_values']
    if not mc.ls(wrap_name):
        mc.select(target_geo, source_geo)
        mc.CreateWrap()
    # set attributes of new wrap deformer
    for plug_key in plug_values_dict.keys():
        value = plug_values_dict[plug_key]
        mc.setAttr('{0}.{1}'.format(wrap_name, plug_key), value)
    mc.connectAttr('{node}.worldMatrix[0]'.format(node=target_geo),
                   '{wrap}.geomMatrix'.format(wrap=wrap_name),
                   force=True
                   )
