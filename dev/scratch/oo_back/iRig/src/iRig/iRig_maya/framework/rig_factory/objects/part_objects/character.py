from rig_factory.objects.part_objects.container import Container, ContainerGuide


class CharacterGuide(ContainerGuide):

    default_settings = dict(
        root_name='character'
    )

    def __init__(self, **kwargs):
        kwargs['root_name'] = 'character'
        super(CharacterGuide, self).__init__(**kwargs)
        self.toggle_class = Character.__name__

    def post_create(self, **kwargs):
        super(CharacterGuide, self).post_create(**kwargs)


class Character(Container):

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)

    def post_create(self, **kwargs):
        super(Character, self).post_create(**kwargs)
