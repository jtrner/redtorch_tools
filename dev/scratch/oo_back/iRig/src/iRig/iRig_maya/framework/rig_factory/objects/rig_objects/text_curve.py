from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty


class TextCurve(Transform):

    text_input = DataProperty(
        name='text_input',
        default_value='text'
    )
    current_font = DataProperty(
        name='current_font',
        default_value='Lucida Sans Unicode'
    )
    transform = ObjectProperty(
        name='transform'
    )

    def __init__(self, **kwargs):
        super(TextCurve, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(TextCurve, cls).create(controller, **kwargs)
        root_name = this.root_name
        text_input = this.text_input
        current_font = this.current_font
        transform = this.create_child(
            Transform,
            root_name='text_{0}'.format(root_name)
        )
        add_text_curves(
            root_name,
            text_input,
            current_font,
            transform
        )
        # calculates center of text so "this" is centered at zero
        for translation in ['X', 'Y', 'Z']:
            min_val = transform.plugs['boundingBoxMin{0}'.format(translation)].get_value()
            max_val = transform.plugs['boundingBoxMax{0}'.format(translation)].get_value()
            translate = (min_val + max_val) / -2.0
            transform.plugs['translate{0}'.format(translation)].set_value(translate)

        this.transform = transform
        return this

    def set_size(self, size):
        if type(size) != float:
            raise TypeError('Invalid type. Size must be a float value. Got {0}'.format(size))
        self.plugs['scale'].set_value([size, size, size])


def add_text_curves(name, text, font, parent):
    for curve in parent.controller.scene.create_text_curve(name, text, font, parent.name):
        parent.create_child(
            NurbsCurve,
            m_object=curve
        )
