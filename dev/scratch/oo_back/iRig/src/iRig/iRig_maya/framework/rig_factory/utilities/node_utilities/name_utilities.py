import rig_factory
import re


def create_name_string(class_name, **kwargs):
    root_name = kwargs.get('root_name', None)
    name = kwargs.get('name', None)
    if name:
        #if not re.match("^[\.\[\]A-Za-z0-9_-]*$", name):
        #     raise Exception('Invalid characters in name: %s' % name)
        return name
    if root_name is None:
        raise AttributeError(
            'You must provide a root_name keyword argument'
        )

    # EXCLUDE COLON FOR NAMESPACED OBJECTS
    #if not re.match("^[\.\[\]A-Za-z0-9_-]*$", root_name):
    #    raise Exception('Invalid characters in root_name: %s' % root_name)

    name = root_name
    side = kwargs.get('side', None)
    index = kwargs.get('index', None)
    node_type = kwargs.get('node_type', None)
    if side in rig_factory.settings_data['side_prefixes']:
        name = '%s_%s' % (rig_factory.settings_data['side_prefixes'][side], name)
    if index is not None:
        name = '%s_%s' % (name, rig_factory.index_dictionary[index])
    if class_name in rig_factory.settings_data['class_suffixes']:
        name = '%s_%s' % (name, rig_factory.settings_data['class_suffixes'][class_name])
    elif node_type in rig_factory.settings_data['type_suffixes']:
        name = '%s_%s' % (name, rig_factory.settings_data['type_suffixes'][node_type])

    return name
