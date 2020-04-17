from base_object import BaseObject
from properties import DataProperty


class BaseNode(BaseObject):

    root_name = DataProperty(
        name='root_name'
    )
    size = DataProperty(
        name='size',
        default_value=1.0
    )
    side = DataProperty(
        name='side'
    )
    index = DataProperty(
        name='index'
    )

    def __setattr__(self, name, value):
        if hasattr(self, name):
            try:
                super(BaseObject, self).__setattr__(name, value)
            except StandardError:
                raise StandardError(
                    'The property "%s" on the node "%s" could not be set to: %s.' % (name, self, value)
                )

        else:
            raise Exception('The "%s" attribute is not registered with the %s class' % (
                name,
                self.__class__.__name__
            ))

    def __init__(self, *args, **kwargs):
        if not kwargs.get('controller', None):
            raise Exception(
                'You must provide a controller when creating a %s' % self.__class__.__name__
            )
        super(BaseNode, self).__init__(*args, **kwargs)

    def create_child(self, object_type, *args, **kwargs):
        for key in ['root_name', 'side', 'size', 'index']:
            if key not in kwargs:
                kwargs[key] = self.__getattribute__(key)
        if not kwargs.get('parent', None):
            kwargs['parent'] = self
        return super(BaseNode, self).create_child(object_type, *args, **kwargs)
