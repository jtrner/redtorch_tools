import weakref
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.base_objects.properties import ObjectDictProperty, DataProperty
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.weak_list import WeakList


class DependNode(BaseNode):

    existing_plugs = ObjectDictProperty(
        name='existing_plugs'
    )

    node_type = DataProperty(
        name='node_type'
    )

    plugs = []
    m_object = None

    def __init__(self, **kwargs):
        super(DependNode, self).__init__(**kwargs)
        self.plugs = Plugs(self)
        self.m_object = None

    @classmethod
    def create(cls, controller, **kwargs):
        root_name = kwargs.get('root_name', None)
        if root_name is not None and '.' in root_name and 'root_name':
            raise Exception('The keyword argument "root_name" has an invalid character : %s' % root_name)
        m_object = kwargs.pop('m_object', None)
        if m_object:
            kwargs['name'] = controller.scene.get_selection_string(m_object)
        this = super(DependNode, cls).create(controller, **kwargs)
        this.m_object = m_object
        if not this.m_object:
            this.create_in_scene()
        return this

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_depend_node(
            self.node_type,
            self.name
        )

    def initialize_plug(self, key):
        if key in self.existing_plugs:
            return self.existing_plugs[key]
        else:
            return self.create_child(
                Plug,
                root_name=key
            )

    def create_plug(self, name, **kwargs):
        if name in self.existing_plugs:
            raise Exception('The node "%s" already has a plug named "%s"' % (self, name))
        return self.create_child(
            Plug,
            root_name=name,
            create_kwargs=kwargs,
            user_defined=True
        )

    def get_selection_string(self):
        #if self.controller.scene.mock or not self.m_object:
        #    return self.name
        return self.controller.scene.get_selection_string(self.m_object)

    def __str__(self):
        return self.get_selection_string()

    def teardown(self):
        selection_string = self.get_selection_string()
        self.m_object = None
        self.controller.scene.delete(selection_string)
        super(DependNode, self).teardown()

    def is_visible(self):
        return self.controller.check_visibility(self)


class Plugs(object):
    def __init__(self, owner):
        self.owner = weakref.ref(owner)

    def __getitem__(self, key):
        owner = self.owner()
        if owner:
            if key in owner.existing_plugs:
                return owner.existing_plugs[key]
            else:
                new_plug = owner.initialize_plug(key)
                owner.existing_plugs[key] = new_plug
                return new_plug

    def __setitem__(self, key, val):
        owner = self.owner()
        if owner:
            owner.existing_plugs[key] = val

    def set_values(self, **kwargs):
        for key in kwargs:
            self[key].set_value(kwargs[key])

    def set_locked(self, **kwargs):
        for key in kwargs:
            self[key].set_locked(kwargs[key])

    def get(self, *args):
        return WeakList([self[x] for x in args])
