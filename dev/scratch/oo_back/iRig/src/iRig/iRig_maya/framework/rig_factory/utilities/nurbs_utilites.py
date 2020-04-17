
from rig_factory.objects.node_objects.dag_node import DagNode


def generate_arc_length_dimensions(nurbs_object, number_along_u=5, number_along_v=1):
    if nurbs_object.node_type == 'nurbsCurve':
        u_span = nurbs_object.plugs['spans'].get_value()
        v_span = None
    elif nurbs_object.node_type == 'nurbsSurface':
        u_span = nurbs_object.plugs['spansU'].get_value()
        v_span = nurbs_object.plugs['spansV'].get_value()
    else:
        raise Exception('Provided object not valid, only accepts "nurbsCurve" or "nurbsSurface" node type.')

    root_name = nurbs_object.root_name
    arc_dimensions = []
    for u in range(number_along_u):
        for v in range(number_along_v):
            # create
            if nurbs_object.node_type == 'nurbsSurface':
                arc_dimension_root_name = '{0}_{1:02d}U_{2:02d}V_ArcLength'.format(root_name, u, v)
            else:
                arc_dimension_root_name = '{0}_{1:02d}U_ArcLength'.format(root_name, u)
            arc_dimension = nurbs_object.parent.create_child(DagNode,
                                                             root_name=arc_dimension_root_name,
                                                             node_type='arcLengthDimension')
            # connect to nurb object
            nurbs_object.plugs['worldSpace'].element(0).connect_to(arc_dimension.plugs['nurbsGeometry'])
            # set uv values
            arc_dimension.plugs['uParamValue'].set_value((u/float(number_along_u-1)) * u_span)
            if v_span:
                arc_dimension.plugs['uParamValue'].set_value((v/float(number_along_u-1)) * v_span)
            # add to return list
            arc_dimensions.append(arc_dimension)
    return arc_dimensions
