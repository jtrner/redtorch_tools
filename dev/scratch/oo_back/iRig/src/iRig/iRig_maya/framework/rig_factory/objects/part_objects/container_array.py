from rig_factory.objects.part_objects.container import ContainerGuide, Container


class ContainerArrayGuide(ContainerGuide):

    def __init__(self, **kwargs):
        super(ContainerArrayGuide, self).__init__(**kwargs)
        self.toggle_class = ContainerArray.__name__

    def create_members(self):
        pass


class ContainerArray(Container):

    def __init__(self, **kwargs):
        super(ContainerArray, self).__init__(**kwargs)
