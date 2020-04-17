from rig_factory.objects.part_objects.container import Container, ContainerGuide


class VehicleGuide(ContainerGuide):

    default_settings = dict(
        root_name='vehicle'
    )

    def __init__(self, **kwargs):
        kwargs['root_name'] = 'vehicle'
        super(VehicleGuide, self).__init__(**kwargs)
        self.toggle_class = Vehicle.__name__

    def post_create(self, **kwargs):
        super(VehicleGuide, self).post_create(**kwargs)


class Vehicle(Container):

    def __init__(self, **kwargs):
        super(Vehicle, self).__init__(**kwargs)

    def post_create(self, **kwargs):
        super(Vehicle, self).post_create(**kwargs)
