from rig_factory.objects.standard_biped_objects.standard_leg import StandardLeg, StandardLegGuide


class TwistyLegGuide(StandardLegGuide):

    def __init__(self, **kwargs):
        super(TwistyLegGuide, self).__init__(**kwargs)
        self.toggle_class = TwistyLeg.__name__


class TwistyLeg(StandardLeg):

    def __init__(self, **kwargs):
        super(TwistyLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(TwistyLeg, cls).create(controller, **kwargs)

        """
        Create the Bendy Things
        """

