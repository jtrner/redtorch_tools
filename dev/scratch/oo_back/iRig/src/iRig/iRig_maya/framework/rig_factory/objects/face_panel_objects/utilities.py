from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.node_objects.depend_node import DependNode


def create_teardrop_handles(this, root_name, side, drop_translations, drop_scale):
    # type: (classmethod, str, str, tuple, tuple) -> list
    """
    Create teardrop handles using the passed translation, scale and color override values
    :param this: (classmethod) a class creating a handle that needs teardrop handles
    :param root_name: (str) the handle's name
    :param side: (str) the handle's side
    :param drop_translations: (tuple) translation values for the teardrop handle
    :param drop_scale: (tuple) scale values for the teardrop handle
    :return: (list) list of the created handles
    """
    handles = []
    for ind, position in enumerate(['in', 'mid', 'out']):
        drop_matrix = Matrix(scale=drop_scale)
        drop_handle = this.create_handle(
            root_name=root_name,
            shape='teardrop',
            size=this.size,
            side=side
        )
        drop_handle.plugs['shape_matrix'].set_value(drop_matrix)
        drop_handle.groups[-1].plugs['translate'].set_value(drop_translations[ind])
        handles.append(drop_handle)
    return handles


def create_line(controller, this, root_name, side, locator_translations):
    # type: (classmethod, classmethod, str, str, tuple) -> None
    """
    Creates 2 locators and a line. The locators are translated then their world position attribute is
    connected to the line's control point attribute.
    :param controller: (classmethod) sets up the maya scene
    :param this: (classmethod) the control handle that needs teardrop handles
    :param root_name: (str) the control handle's name
    :param side: (str) the control handle's side
    :param locator_translations: (tuple) translation values for the locators
    :return: None
    """
    if len(locator_translations) != 2:
        print 'Error! Needs exactly 2 translations.'
        return

    line = controller.create_object(
        Line,
        root_name='{0}_line'.format(root_name),
        index=1,
        parent=this
    )

    for ind, position in enumerate(['start_pos', 'end_pos']):
        locator_transform = controller.create_object(
            Transform,
            root_name='{0}_{1}'.format(root_name, position),
            side=side,
            parent=this
        )
        locator_transform.plugs['translate'].set_value(locator_translations[ind])

        locator = this.create_child(
            Locator,
            root_name='{0}_{1}'.format(root_name, position),
            side=side,
            parent=locator_transform
        )
        locator_transform.plugs['visibility'].set_value(False)
        locator.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(ind))


def set_attr_limit(handle, attr_name, min_limit, max_limit):
    # type: (classmethod, str, float, float) -> None
    """
    Creates min and max limits for the given attribute on the given handle.
    :param handle: (classmethod) the control handle
    :param attr_name: (str) the name of the attribute to set the limit on
    :param min_limit: (float) the minimum limit value
    :param max_limit: (float) the maximum limit value
    :return: None
    """
    for min_max_str in ['min', 'max']:
        limit_attr = min_max_str + attr_name + 'Limit'
        limit_enable = limit_attr + 'Enable'
        handle.plugs[limit_enable].set_value(True)
        if min_max_str == 'min':
            handle.plugs[limit_attr].set_value(min_limit)
        elif min_max_str == 'max':
            handle.plugs[limit_attr].set_value(max_limit)


def set_color_index(handle, color_index):
    # type: (classmethod, int) -> None
    """
    Sets the override color for the given handle
    :param handle: (classmethod) the control handle
    :param color_index: (int) color's index number in Drawing Overrides (Display > Drawing Overrides)
    :return: None
    """
    handle.plugs['overrideEnabled'].set_value(True)
    handle.plugs['overrideRGBColors'].set_value(0)
    handle.plugs['overrideColor'].set_value(color_index)


def create_corrective_driver(plug_1, plug_2, in_value_1, out_value_1, in_value_2, out_value_2, **kwargs):
    node = plug_1.get_node()
    condition_node = node.create_child(
        DependNode,
        node_type='condition',
        **kwargs
    )

    root_name = kwargs.pop('root_name')
    kwargs['root_name'] = '%s_first' % root_name
    remap_node_1 = node.create_child(
        DependNode,
        node_type='remapValue',
        **kwargs
    )
    kwargs['root_name'] = '%s_second' % root_name
    remap_node_2 = node.create_child(
        DependNode,
        node_type='remapValue',
        **kwargs
    )
    remap_node_1.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_1.plugs['value'].element(0).child(1).set_value(0.0)
    remap_node_1.plugs['value'].element(1).child(0).set_value(in_value_1)
    remap_node_1.plugs['value'].element(1).child(1).set_value(out_value_1)
    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(1).child(0).set_value(in_value_2)
    remap_node_2.plugs['value'].element(1).child(1).set_value(out_value_2)
    plug_1.connect_to(remap_node_1.plugs['inputValue'])
    plug_2.connect_to(remap_node_2.plugs['inputValue'])
    condition_node.plugs['operation'].set_value(5)

    remap_node_1.plugs['outValue'].connect_to(condition_node.plugs['firstTerm'])
    remap_node_2.plugs['outValue'].connect_to(condition_node.plugs['secondTerm'])
    remap_node_1.plugs['outValue'].connect_to(condition_node.plugs['colorIfTrueR'])
    remap_node_2.plugs['outValue'].connect_to(condition_node.plugs['colorIfFalseR'])

    combo_plug = node.create_plug(
        root_name,
        k=True,
        at='double'
    )
    blend_node = node.create_child(
        DependNode,
        node_type='blendWeighted',
        **kwargs
    )

    condition_node.plugs['outColorR'].connect_to(blend_node.plugs['input'].element(0))
    blend_node.plugs['output'].connect_to(combo_plug)

