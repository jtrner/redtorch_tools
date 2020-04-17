import uuid

from properties import DataProperty, ObjectProperty
from rig_factory.objects.base_objects.weak_list import WeakList


class BaseObject(object):
    """
    Base Object is the base class for all node_objects within the rigging api.
    Base node_objects have a data property "uuid" that is a unique id string that should never match another node_objects uuid.
    Base node_objects
    """

    uuid = DataProperty(
        name='uuid'
    )
    name = DataProperty(
        name='name'
    )
    parent = ObjectProperty(
        name='parent'
    )
    subclass_registry = dict()
    children = []
    controller = None

    @classmethod
    def create(cls, controller, **kwargs):
        name = controller.create_name(
                cls.__name__,
                **kwargs
            )
        kwargs.setdefault(
            'name',
            name

        )
        kwargs['controller'] = controller
        parent = kwargs.get('parent', None)

        if parent is not None and not isinstance(parent, BaseObject):
            raise Exception(
                'You must provide either a BaseNode instance or None for parent argument not:  %s type: "%s"' % (parent, type(parent))
            )
        index = kwargs.get('index', None)
        if index is not None and not isinstance(index, int):
            raise Exception(
                'index keyword argument must be either type(int) or None'
            )
        if parent:
            controller.start_parent_signal.emit(None, parent)

        this = cls(**kwargs)
        controller.named_objects[name] = this
        if parent:
            controller.end_parent_signal.emit(this, parent)

        return this

    def unparent(self):
        self.controller.unparent(self)


    def set_parent(self, parent):
        self.controller.set_parent(self, parent)

    def __repr__(self):
        if self.name:
            return self.name
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        self.controller = kwargs.pop(
            'controller',
            None
        )
        if not self.controller:
            raise Exception('You must provide a controller when creating a %s' % self.__class__.__name__)
        super(BaseObject, self).__init__()

        self.uuid = kwargs.get('uuid', str(uuid.uuid4()))
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

        if self.parent:
            self.parent.children.append(self)
        self.children = []
        self.subclass_registry[self.__class__.__name__] = self.__class__

    def set_name(self, name):
        self.controller.set_name(self, name)

    def delete(self):
        self.controller.delete_objects(WeakList([self]))

    def create_child(self, object_type, *args, **kwargs):

        node = self.controller.create_object(
            object_type,
            *args,
            **kwargs
        )
        return node

    def serialize(self):
        return self.controller.serialize(self)

    def get_ancestors(self):
        ancestors = [self]
        owner = self.parent
        while owner:
            ancestors.insert(0, owner)
            owner = owner.parent
        return ancestors

    def get_descendants(self, include_self=False):
        descendants = []
        if include_self:
            descendants.append(self)
        children = self.children
        descendants.extend(children)
        for child in children:
            descendants.extend(child.get_descendants())
        return descendants

    def teardown(self):
        if self.parent:
            self.unparent()

    def __delete__(self, *args, **kwargs):
        super(BaseObject, self).__delete__(*args, **kwargs)
