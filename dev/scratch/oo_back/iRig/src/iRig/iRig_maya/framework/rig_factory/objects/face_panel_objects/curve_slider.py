from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.rig_objects.text_curve import TextCurve
from rig_math.matrix import Matrix
import utilities as utl


class CurveSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(CurveSliderGuide, self).__init__(**kwargs)
        self.toggle_class = CurveSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(CurveSliderGuide, cls).create(controller, **kwargs)
        return this


class CurveSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(CurveSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(CurveSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        root = this.get_root()
        circle_translations = (-2.0, 0.5, 0.0), (0.0, 0.0, 0.0), (2.0, -0.5, 0.0)
        x_min_limit = 0.0, -2.0, -2.0
        x_max_limit = 2.0, 2.0, 0.0
        z_min_limit = 0.0, -0.5, -1.0
        z_max_limit = 1.0, 0.5, 0.0
        locators = []
        square_handle = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square_line',
            size=size,
            side=side
        )
        square_handle.plugs['overrideDisplayType'].set_value(2)

        matrix = Matrix(scale=[4.0, 1.0, 1.0])
        square_handle.plugs['shape_matrix'].set_value(matrix)
        square_handle.plugs['rotateX'].set_value(90)
        utl.set_color_index(square_handle, 1)  # black

        for position_ind, position in enumerate(['A', 'B', 'C']):
            circle_handle = this.create_handle(
                root_name='{0}{1}_Dyn'.format(root_name, position),
                shape='circle',
                size=size,
                side=side,
            )
            matrix = Matrix(scale=[0.1, 1.0, 0.1])
            circle_handle.plugs['shape_matrix'].set_value(matrix)
            circle_handle.groups[-1].plugs['translate'].set_value(circle_translations[position_ind])
            circle_handle.groups[-1].plugs['rotateX'].set_value(90)
            circle_handle.groups[0].set_parent(square_handle)
            utl.set_attr_limit(circle_handle, 'TransX', x_min_limit[position_ind], x_max_limit[position_ind])
            utl.set_attr_limit(circle_handle, 'TransZ', z_min_limit[position_ind], z_max_limit[position_ind])
            root.add_plugs(
                [
                    circle_handle.plugs['tx'],
                    circle_handle.plugs['tz'],
                    circle_handle.plugs['sx'],
                    circle_handle.plugs['sy'],
                    circle_handle.plugs['sz']
                ]
            )
            locator = this.create_child(
                Locator,
                root_name='{0}_{1}'.format(root_name, position),
                side=side,
                parent=circle_handle
            )
            locator.plugs['visibility'].set_value(False)
            locators.append(locator)

        ab_line = controller.create_object(
            Line,
            root_name='{0}_AB_line'.format(root_name),
            index=1,
            parent=this
        )

        bc_line = controller.create_object(
            Line,
            root_name='{0}_BC_line'.format(root_name),
            index=1,
            parent=this
        )

        locators[0].plugs['worldPosition'].element(0).connect_to(ab_line.curve.plugs['controlPoints'].element(0))
        locators[1].plugs['worldPosition'].element(0).connect_to(ab_line.curve.plugs['controlPoints'].element(1))

        locators[1].plugs['worldPosition'].element(0).connect_to(bc_line.curve.plugs['controlPoints'].element(0))
        locators[2].plugs['worldPosition'].element(0).connect_to(bc_line.curve.plugs['controlPoints'].element(1))


        # Text
        slider_text = this.create_child(
            TextCurve,
            root_name='{0}_text'.format(root_name),
            text_input='{0}_{1}'.format(side, root_name)
        )
        slider_text.set_size(0.75)
        utl.set_color_index(slider_text, 1)  # black
        slider_text.plugs['overrideDisplayType'].set_value(2)
        # calculates center height of control and moves text
        translate = square_handle.plugs['boundingBoxSizeY'].get_value()
        translate = translate - ((translate - 1) / 2.0)
        slider_text.plugs['translateY'].set_value(translate)

        return this
