from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectDictProperty
from rig_factory.objects.base_objects.base_node import BaseNode
import weakref
import traceback

class Plug(BaseNode):

    create_data = DataProperty(
        name='create_data'
    )

    #value = DataProperty(
    #    name='value'
    #)

    create_kwargs = DataProperty(
        name='create_kwargs'
    )

    user_defined = DataProperty(
        name='user_defined'
    )

    array_plug = ObjectProperty(
        name='array_plug'
    )

    elements = ObjectDictProperty(
        name='elements'
    )

    child_plugs = ObjectDictProperty(
        name='child_plugs'
    )

    m_plug = None
    _in_connection = None
    out_connections = WeakList()

    @classmethod
    def create(cls, controller, **kwargs):
        parent = kwargs.get('parent', None)
        root_name = kwargs.get('root_name', None)
        if not parent:
            raise Exception(
                'You must provide a "parent" keyword argument to create a %s' % Plug.__name__
            )
        elif isinstance(parent, Plug):
            index = kwargs.get('index', None)
            if index is None:
                raise Exception(
                    'You must provide a "index" keyword argument to create an element or child plug'
                )
            kwargs['name'] = '%s[%s]' % (parent.name, index)
        else:
            if not root_name:
                raise Exception(
                    'You must provide a "root_name" keyword argument to create a %s' % Plug.__name__
                )
            kwargs['name'] = '%s.%s' % (parent.name, root_name)
        this = super(BaseNode, cls).create(controller, **kwargs)
        if this.array_plug:
            this.array_plug.elements[str(this.index)] = this
        elif isinstance(this.parent, Plug):
            this.parent.child_plugs[str(this.index)] = this
        else:
            this.parent.existing_plugs[this.root_name] = this
        this.create_in_scene()
        return this

    def create_in_scene(self):
        if self.user_defined:
            self.m_plug = self.controller.scene.create_plug(
                self.parent.m_object,
                self.root_name,
                **self.create_kwargs
            )
        else:
            if isinstance(self.parent, Plug):
                self.m_plug = self.controller.scene.initialize_plug(
                    self.parent.m_plug,
                    self.index
                )

            else:
                self.m_plug = self.controller.scene.initialize_plug(
                    self.parent.m_object,
                    self.root_name
                )

    def get_next_avaliable_index(self):
        return self.controller.scene.get_next_avaliable_plug_index(self.m_plug)

    def __init__(self, **kwargs):
        super(Plug, self).__init__(**kwargs)
        self.m_plug = None
        self._in_connection = None
        self.out_connections = WeakList()

    def __repr__(self):
        return '%s.%s' % (
            self.get_node().get_selection_string(),
            self.root_name
        )

    @property
    def in_connection(self):
        if self._in_connection:
            return self._in_connection()

    @in_connection.setter
    def in_connection(self, connection):
        if connection:
            self._in_connection = weakref.ref(connection)
        else:
            self._in_connection = None

    def is_element(self):
        return isinstance(self.array_plug, Plug)

    def is_array(self):
        return bool(self.elements)

    def set_value(self, value):
        self.controller.set_plug_value(self, value)

    def get_value(self, *args):
        return self.controller.get_plug_value(self, *args)

    def get_data(self):
        """
        This could use MPlug
        """
        scene = self.controller.scene
        node = self.get_node().name
        attribute = self.root_name
        plug_name = '%s.%s' % (node, attribute)
        attribute_type = scene.getAttr(plug_name, type=True)
        data = dict(
            node=node,
            name=attribute,
            long_name=scene.attributeQuery(attribute, node=node, longName=True),
            current_value=scene.getAttr(plug_name),
            locked=scene.getAttr(plug_name, lock=True),
            channelbox=scene.getAttr(plug_name, channelBox=True),
            keyable=scene.getAttr(plug_name, keyable=True),
            type=attribute_type
        )
        if self.m_plug.isDynamic():
            data['dv'] = scene.addAttr(plug_name, q=True, dv=True)
        if attribute_type == 'enum':
            data['listEnum'] = scene.attributeQuery(attribute, node=node, listEnum=True)[0]
        if scene.attributeQuery(attribute, node=node, minExists=True):
            data['min'] = scene.attributeQuery(attribute, node=node, min=True)[0]
        if scene.attributeQuery(attribute, node=node, maxExists=True):
            data['max'] = scene.attributeQuery(attribute, node=node, max=True)[0]
        return data

    def set_channel_box(self, value):
        if self.m_plug:
            return self.m_plug.setChannelBox(value)

    def element(self, index):
        if not isinstance(index, int):
            raise Exception('plug elements can only be retrieved by index integer, not "%s"' % type(index))
        if str(index) in self.elements:
            return self.elements[str(index)]
        return self.create_child(
            Plug,
            index=index,
            array_plug=self
        )

    def child(self, index):
        if not isinstance(index, int):
            raise Exception('plug children can only be retrieved by index integer, not "%s"' % type(index))
        if str(index) in self.child_plugs:
            return self.child_plugs[str(index)]
        return self.create_child(
            Plug,
            index=index,
        )

    def connect_to(self, plug):
        self.out_connections.append(plug)
        plug.in_connection = self
        try:
            self.controller.scene.connect_plugs(
                self.m_plug,
                plug.m_plug
            )
        except StandardError:
            traceback.print_exc()
            raise StandardError('Failed to connect %s to %s\nCheck the script editor for a stack-trace.' % (self, plug))

    def disconnect_from(self, plug):
        if plug not in self.out_connections:
            raise Exception('Plug "%s" not found in out connections of "%s"' % (plug, self))
        if plug.in_connection != self:
            raise Exception('"%s" is not the in_connection for "%s"' % (self, plug))
        self.out_connections.remove(plug)
        plug.in_connection = None
        self.controller.scene.disconnect_plugs(
            self.m_plug,
            plug.m_plug
        )

    def get_node(self):
        parent = self.parent
        while isinstance(parent, Plug):
            parent = parent.parent
        return parent

    def set_keyable(self, value):
        self.controller.scene.set_plug_keyable(self, value)

    def get_keyable(self, value):
        return self.controller.scene.get_plug_keyable(self, value)

    def set_locked(self, value):
        self.controller.scene.set_plug_locked(self, value)

    def set_hidden(self, value):
        self.controller.scene.set_plug_hidden(self, value)

    def get_locked(self):
        return self.controller.scene.get_plug_locked(self)

    def set_hidden(self, value):
        self.controller.set_plug_hidden(self, value)

    def get_hidden(self):
        return self.controller.get_plug_hidden(self)

    def teardown(self):
        self.controller.scene.deleteAttr(
            self.get_node().name,
            attribute=self.root_name
        )
        super(Plug, self).teardown()
