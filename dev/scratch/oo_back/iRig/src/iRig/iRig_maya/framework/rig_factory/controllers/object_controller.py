import weakref
import gc
import os
import json
import traceback
import PySignal
from rig_factory.objects.base_objects.base_node import BaseNode
import rig_factory.objects.base_objects.properties as prp
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.utilities.object_utilities.name_utilities as ntl
import rig_factory.objects as obs


class ObjectController(object):

    start_parent_signal = PySignal.ClassSignal()
    end_parent_signal = PySignal.ClassSignal()
    start_unparent_signal = PySignal.ClassSignal()
    end_unparent_signal = PySignal.ClassSignal()
    root_about_to_change_signal = PySignal.ClassSignal()
    root_finished_change_signal = PySignal.ClassSignal()
    item_changed_signal = PySignal.ClassSignal()
    start_ownership_signal = PySignal.ClassSignal()
    end_ownership_signal = PySignal.ClassSignal()
    start_disown_signal = PySignal.ClassSignal()
    end_disown_signal = PySignal.ClassSignal()
    progress_signal = PySignal.ClassSignal()
    failed_signal = PySignal.ClassSignal()
    deleted_signal = PySignal.ClassSignal()
    raise_warning_signal = PySignal.ClassSignal()
    raise_error_signal = PySignal.ClassSignal()
    disable_warnings = False
    accepts_duplicate_names = False
    garbage_collection = False  # garbage collect recursively for debugging
    strict_deserialization = True  # Stop  deserialization if anything goes wrong

    def __init__(self):
        super(ObjectController, self).__init__()
        self.root = None
        self.name_function = None
        self.objects = weakref.WeakValueDictionary()
        self.named_objects = weakref.WeakValueDictionary()
        self.deleted_object_names = []
        self.get_class_function = None
        self.DEBUG = os.getenv('PIPE_DEV_MODE')

    @classmethod
    def get_controller(cls):
        this = cls()
        this.name_function = ntl.create_name_string
        return this

    def reset(self, *args):
        self.set_root(None)
        gc.collect()
        # """
        # Shouldnt be neciserry to reset object weakdicts
        # """
        self.objects = weakref.WeakValueDictionary()
        self.named_objects = weakref.WeakValueDictionary()
        if self.named_objects:
            raise StandardError('named_objects is not empty')
        if self.objects:
            raise StandardError('objects is not empty')

    def create_name(self, *args, **kwargs):
        new_name = self.name_function(
            *args,
            **kwargs
        )
        if not self.accepts_duplicate_names and new_name in self.named_objects:
            raise StandardError(
                'A node with the name "%s" already exists.' % new_name
            )
        return new_name

    def create_object(self, object_type, *args, **kwargs):
        if isinstance(object_type, basestring):
            if object_type not in obs.classes:
                raise Exception('Object type "%s" not supported' % object_type)
            object_type = obs.classes[object_type]
        if self.get_class_function:
            object_type = self.get_class_function(object_type)
        this = object_type.create(self, *args, **kwargs)
        self.register_item(this)
        return this

    def set_root(self, root):
        self.root_about_to_change_signal.emit()
        self.root = root
        self.root_finished_change_signal.emit(root)

    def get_root(self):
        return self.root

    def register_item(self, item):
        self.objects[item.uuid] = item
        # Named node_objects is now getting added to in base object
        #self.named_objects[item.name] = item

    #def deregister_object(self, item, recursive=False):
    #    self.node_objects.pop(item.uuid)
    #    prp.DataProperty.map.pop(item, None)
    #    prp.ObjectProperty.map.pop(item, None)
    #    prp.ObjectListProperty.map.pop(item, None)
    #    prp.ObjectDictProperty.map.pop(item, None)
    #    if item == self.root:
    #        self.set_root(None)

    def unparent(self, child):
        if child.parent:
            parent = child.parent
            self.start_unparent_signal.emit(child, parent)
            child.parent.children.remove(child)
            child.parent = None
            self.end_unparent_signal.emit(child, parent)

    def set_parent(self, child, parent):
        if not isinstance(parent, BaseNode):
            raise Exception('Cannot parent to type "%s"' % type(parent))
        if child.parent == parent:
            raise Exception('%s is already parented to %s' % (child, child.parent))
        if child.parent:
            self.unparent(child)
        self.start_parent_signal.emit(child, parent)
        child.parent = parent
        parent.children.append(child)
        self.end_parent_signal.emit(child, parent)

    def set_name(self, item, name):
        self.named_objects.pop(item.name, None)
        self.named_objects[name] = item
        item.name = name
        self.item_changed_signal.emit(item)

    def serialize_and_open(self, item):
        file_name = '%s/test.json' % os.path.expanduser('~')
        with open(file_name, mode='w') as f:
            f.write(json.dumps(self.serialize(item), sort_keys=True, indent=4, separators=(',', ': ')))
        os.system('start %s' % file_name)

    def serialize(self):
        return dict(
            objects=[self.serialize_object(x) for x in self.objects.values()],
            root=self.root.uuid if self.root else None
        )

    def serialize_object(self, item):
        instance_properties = prp.DataProperty.map.get(item, dict())
        item_properties = prp.ObjectProperty.map.get(item, dict())
        item_list_properties = prp.ObjectListProperty.map.get(item, dict())
        item_dict_properties = prp.ObjectDictProperty.map.get(item, dict())
        objects = dict()
        for x in item_properties:
            y = item_properties[x]()
            if y:
                objects[x.name] = y.uuid
        for x in item_list_properties:
            list_properties = item_list_properties[x]
            item_list = []
            for z in list_properties:
                if z:
                    item_list.append(z.uuid)
            objects[x.name] = item_list
        for x in item_dict_properties:
            dict_properties = item_dict_properties[x]
            item_dict = dict()
            for key in dict_properties:
                item_dict[key] = dict_properties[key].uuid
            objects[x.name] = item_dict
        values = dict()
        for x in instance_properties:
            value = instance_properties[x]
            if self.DEBUG:
                try:
                    json.dumps(value)
                except StandardError, e:
                    print e.message
                    raise StandardError('ERROR:  %s %s %s was not serializable %s' % (item, type(item), x.name, value))
            values[x.name] = value

        if 'name' not in values:
            print 'Print property keys....'
            for i in prp.DataProperty.map[item].keys():
                print 'Property Key --->>>  ', i.name
            raise Exception('Serialization failed for %s. "name" property not found' % item)

        data = dict(
            klass=item.__class__.__name__,
            module=item.__module__,
            values=values,
            objects=objects,
            children=[x.uuid for x in item.children]
        )

        return data

    def deserialize(self, data):
        """
        I dont know if this is being used...

        :param data:
        :return:
        """
        root_uuid = data['root']
        object_data = data['objects']
        all_objects = []
        for x in object_data:
            try:
                all_objects.append(self.deserialize_object(x))
            except StandardError, e:
                self.raise_warning_signal.emit('Failed to deserialize object: %s' % x.get('name', 'unknown'))
        for x in self.deserialize_properties(object_data):
            pass
        self.set_root(self.objects.get(root_uuid, None))
        return all_objects

    def deserialize_properties(self, data):
        failed_properties = 0
        failed_property_data = []
        tracebacks = []

        for x in data:
            try:
                item = self.objects[x['values']['uuid']]
                children = x['children']
                if children:
                    for y in children:
                        if y not in self.objects:
                            raise Exception('Object Child not found %s, %s' % (item, y))
                        item.children.append(self.objects[y])
                objects_data = x['objects']
                for key in objects_data:
                    y = objects_data[key]
                    if isinstance(y, basestring):
                        setattr(item, key, self.objects[y])
                    elif isinstance(y, list):
                        setattr(item, key, prp.WeakList([self.objects[z] for z in y]))
                    elif isinstance(y, dict):
                        dict_data = weakref.WeakValueDictionary((z, self.objects[y[z]]) for z in y)
                        setattr(item, key,  dict_data)
                    else:
                        raise Exception('the key "%s" of "%s" has a serialized data type of "%s" which is not valid' % (key, type(item), type(y)))
                yield item
            except StandardError, e:
                if self.strict_deserialization:
                    raise e
                else:
                    failed_properties += 1
                    if failed_properties < 20:
                        failed_property_data.append(x)
                        tracebacks.append(traceback.format_exc())
        if failed_properties:
            print '%s properties failed to deserialize.  ' \
                  'The rig may need to be published with up to date source code' % failed_properties
            print 'The following are failed property kwargs'
            for k in range(len(failed_property_data)):
                print failed_property_data[k]
                print tracebacks[k]

    def deserialize_objects(self, data):
        for x in data:
            yield self.deserialize_object(x)

    def deserialize_object(self, data):
        module = __import__(data.get('module'), fromlist=['.'])
        this = module.__dict__[data.get('klass')](
            controller=self,
            **data['values']
        )
        self.objects[this.uuid] = this
        self.named_objects[this.name] = this
        return this

    def delete_objects(self, objects, collect=True, check_for_lurkers=True):
        self.deleted_object_names.extend([x.name for x in objects])

        if not isinstance(objects, (list, WeakList)):
            raise Exception('Delete node_objects argument must be weak list')
        for x in range(len(objects)):
            objects.pop(0).teardown()
        del objects
        if collect:
            gc.collect()
            if check_for_lurkers:
                lurk_log = ''
                lurkers = []
                for x in self.deleted_object_names:
                    if x in self.named_objects:
                        lurkers.append(self.named_objects[x])
                        for r in gc.get_referrers(self.named_objects[x]):
                            if isinstance(r, list):
                                r.remove(self.named_objects[x])

                self.deleted_object_names = []
                if lurkers:
                    for l in lurkers:
                        lurk_log = lurk_log + '\nInvalid object "%s" Found in referrer ----->> %s' % (l, gc.get_referrers(l))
                if lurk_log:
                    print lurk_log
                    file_path = '%s/lurkers.log' % os.environ['TEMP'].replace('\\', '/')
                    with open(file_path, mode='w') as f:
                        f.write(lurk_log)

    def raise_error(self, message):
        self.raise_error_signal.emit(message)
