import os
import copy
import weakref
from weak_list import WeakList
DEBUG = os.getenv('PIPE_DEV_MODE')

class DataProperty(object):

    map = weakref.WeakKeyDictionary()
    default_value = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.default_value = kwargs.get(
            'default_value',
            copy.copy(self.__class__.default_value)
        )

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        return properties.setdefault(self, copy.copy(self.default_value))

    def __set__(self, instance, value):
        if DEBUG:
            import json
            try:
                json.dumps(value)
            except StandardError, e:
                raise StandardError('failed to serialize %s, %s' % (self.name, value))
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = value


class ObjectProperty(object):
    map = weakref.WeakKeyDictionary()

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        item = properties.get(self, None)
        if item:
            return item()

    def __set__(self, instance, value):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        if value:
            properties[self] = weakref.ref(value)
        else:
            properties.pop(self, None)


class ObjectListProperty(object):

    map = weakref.WeakKeyDictionary()

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        object_list = properties.get(self, None)
        if object_list:
            return object_list
        object_list = WeakList()
        properties[self] = object_list
        return object_list

    def __set__(self, instance, value):

        if not isinstance(value, (list, set, tuple)):
            raise Exception('You must use type(list) when setting class property : %s' % self.name)
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = WeakList(value)


class ObjectDictProperty(DataProperty):

    map = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        weak_dict = properties.get(self, None)
        if weak_dict:
            return weak_dict
        weak_dict = weakref.WeakValueDictionary()
        properties[self] = weak_dict
        return weak_dict

    def __set__(self, instance, value):
        if not isinstance(value, weakref.WeakValueDictionary):
            raise Exception('You must use type(WeakValueDictionary) when setting class property : %s' % self.name)
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = value
