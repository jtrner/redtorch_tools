from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.base_objects.properties import DataProperty


class PostScriptGuide(PartGuide):

    code = DataProperty(
        name='code',
        default_value='print "this is a PostScript for %s" % self'
    )

    default_settings = dict(
        root_name='post_script',
        code='print "this is a PostScript for %s" % self'
    )

    def __init__(self, **kwargs):
        super(PostScriptGuide, self).__init__(**kwargs)
        self.toggle_class = PostScript.__name__

    def get_toggle_blueprint(self):
        blueprint = super(PostScriptGuide, self).get_toggle_blueprint()
        blueprint['code'] = self.code
        return blueprint

    def get_blueprint(self):
        blueprint = super(PostScriptGuide, self).get_blueprint()
        blueprint['code'] = self.code
        return blueprint


class PostScript(Part):

    code = DataProperty(
        name='code',
        default_value='print "this is a PostScript for %s" % self'

    )

    def __init__(self, **kwargs):
        super(PostScript, self).__init__(**kwargs)

    def post_create(self, **kwargs):
        super(PostScript, self).post_create(**kwargs)
        if not self.controller.scene.mock:
            exec(self.code, dict(self=self.owner))

    def get_blueprint(self):
        blueprint = super(PostScript, self).get_blueprint()
        blueprint['code'] = self.code
        return blueprint
