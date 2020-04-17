from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from rig_factory.objects.base_objects.base_object import BaseObject

import workflow.analytics.database as db


class Action(BaseObject):

    name = DataProperty(
        name='name'
    )

    parsed_name = DataProperty(
        name='parsed_name'
    )

    code = DataProperty(
        name='code'
    )

    break_point = DataProperty(
        name='break_point'
    )

    cache_scene = DataProperty(
        name='cache_scene'
    )

    parent = ObjectProperty(
        name='parent'
    )

    critical = DataProperty(
        name='critical'
    )

    warning = DataProperty(
        name='warning'
    )

    success = DataProperty(
        name='success'
    )

    file_path = DataProperty(
        name='file_path'
    )

    documentation = DataProperty(
        name='documentation'
    )

    cache_exists = DataProperty(
        name='cache_exists'
    )

    cache_path = DataProperty(
        name='cache_path'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        if not name:
            raise Exception(
                'invalid name: %s' % name
            )
        if parent is not None and not isinstance(parent, Action):
            raise Exception(
                'You must provide either a "%s" instance or None for parent argument not:  %s' % (
                    parent,
                    Action.__name__
                )
            )
        this = super(Action, cls).create(controller, **kwargs)
        return this

    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)
        self.return_value = None
        self.parse_name()
        self.database_object = None
        self.initialize_database_object()

    def parse_name(self, *args):
        if self.controller.entity:
            self.parsed_name = self.name.replace('<entity>', self.controller.entity.name)
        else:
            self.parsed_name = self.name

    def initialize_database_object(self):
        if self.controller and self.controller.database_object:
            self.database_object = db.get_action(
                self.controller.session,
                self.uuid
            )
            if not self.database_object:
                self.database_object = db.create_action(
                    self.controller.session,
                    workflow=self.controller.database_object,
                    id=self.uuid,
                    name=self.name
                )

    def create_child(self, object_type, **kwargs):
        if not kwargs.get('parent', None):
            kwargs['parent'] = self
        node = self.controller.create_object(object_type, **kwargs)
        return node

    def get_ancestors(self, include_self=False):
        ancestors = []
        if include_self:
            ancestors.append(self)
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
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())

        return descendants

    def set_parent(self, parent):
        self.controller.set_parent(self, parent)

    def unparent(self):
        self.controller.unparent(self)

    def insert_child(self, index, child):
        self.controller.insert_child(index, self, child)
