from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class Connection(BaseNode):

    plug_1 = ObjectProperty(
        name='plug_1'
    )

    plug_2 = ObjectProperty(
        name='plug_2'
    )

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.layer = 'connection'

    @classmethod
    def create(cls, controller, **kwargs):
        plug_1 = kwargs.get('plug_1', None)
        plug_2 = kwargs.get('plug_2', None)
        if not plug_1 and plug_2:
            raise Exception(
                'You must provide a both a "plug_1" and "plug_2" keyword arguments to create a %s' % Connection.__name__
            )
        kwargs['root_name'] = '%s_%s' % (plug_1.name, plug_2.name)
        this = super(Connection, cls).create(controller, **kwargs)
        plug_1.out_connections.append(this)
        plug_2.in_connection = this
        this.create_in_scene()
        return this

    def teardown(self):
        self.controller.scene.disconnect_plugs(
            self.plug_1.m_plug,
            self.plug_2.m_plug
        )

    def create_in_scene(self):
        self.controller.scene.connect_plugs(
            self.plug_1.m_plug,
            self.plug_2.m_plug
        )