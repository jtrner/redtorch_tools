from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.node_objects.depend_node import DependNode

import utilities as utl
from rig_math.matrix import Matrix


class MouthComboSliderGuide(BaseSliderGuide):

    default_settings = dict(
        root_name='pucker'
    )

    def __init__(self, **kwargs):
        super(MouthComboSliderGuide, self).__init__(**kwargs)
        self.toggle_class = MouthComboSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthComboSliderGuide, cls).create(controller, **kwargs)
        return this


class MouthComboSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(MouthComboSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthComboSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        square_handle = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square',
            size=size,
            side=side
        )
        square_handle.plugs['overrideDisplayType'].set_value(2)
        matrix = Matrix(scale=[1.0, 1.0, 0.5])
        square_handle.plugs['shape_matrix'].set_value(matrix)
        square_handle.plugs['rotateX'].set_value(90)
        utl.set_color_index(square_handle, 1)  # black
        square_handle.plugs['tx'].set_value(0.5)

        for attr in ['rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            square_handle.plugs[attr].set_locked(True)

        diamond_handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.25,
            side=side
        )

        utl.set_attr_limit(diamond_handle, 'TransX', 0.0, 1.0)
        for attr in ['translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            diamond_handle.plugs[attr].set_locked(True)

        vertical_input_plug = this.create_plug(
            'vertical_input',
            k=False,
            at='double',
            min=-1.0,
            max=1.0
        )

        horizontal_input_plug = this.create_plug(
            'horizontal_input',
            k=False,
            at='double',
            min=-1.0,
            max=1.0
        )

        main_driver_plug = diamond_handle.create_plug(
            'main_input',  # errors?
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        blend_weighted_main = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_main' % this.root_name
        )
        # Calculate the abs value with power
        power_multiply_1 = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_power_1_x' % this.root_name
        )
        power_multiply_2 = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_power_2_x' % this.root_name
        )
        clamp = this.create_child(
            DependNode,
            node_type='clamp',
            root_name=this.root_name
        )
        reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name=this.root_name
        )
        pucker_pultiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_pucker' % this.root_name
        )
        power_multiply_1.plugs['operation'].set_value(3)
        power_multiply_2.plugs['operation'].set_value(3)
        vertical_input_plug.connect_to(power_multiply_1.plugs['input1Y'])
        horizontal_input_plug.connect_to(power_multiply_1.plugs['input1X'])
        power_multiply_1.plugs['outputX'].connect_to(power_multiply_2.plugs['input1X'])
        power_multiply_1.plugs['outputY'].connect_to(power_multiply_2.plugs['input1Y'])
        power_multiply_1.plugs['input2X'].set_value(2.0)
        power_multiply_1.plugs['input2Y'].set_value(2.0)
        power_multiply_2.plugs['input2X'].set_value(0.5)
        power_multiply_2.plugs['input2Y'].set_value(0.5)
        power_multiply_2.plugs['outputX'].connect_to(blend_weighted_main.plugs['input'].element(0))
        power_multiply_2.plugs['outputY'].connect_to(blend_weighted_main.plugs['input'].element(1))
        blend_weighted_main.plugs['output'].connect_to(clamp.plugs['inputR'])
        clamp.plugs['maxR'].set_value(1.0)
        clamp.plugs['minR'].set_value(0.0)
        clamp.plugs['outputR'].connect_to(reverse.plugs['inputX'])
        reverse.plugs['outputX'].connect_to(pucker_pultiply.plugs['input1X'])
        diamond_handle.plugs['tx'].connect_to(pucker_pultiply.plugs['input2X'])
        pucker_pultiply.plugs['outputX'].connect_to(main_driver_plug)

        # Mouth Up
        plug_name = 'mouth_up'

        driver_plug = diamond_handle.create_plug(
            plug_name,
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        combo_driver_plug = diamond_handle.create_plug(
            '%s_%s' % (plug_name, root_name),
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        blend_weighted_node = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        diamond_handle.plugs['tx'].connect_to(reverse.plugs['inputX'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1Y'])
        reverse.plugs['outputX'].connect_to(multiply.plugs['input2Y'])
        multiply.plugs['outputY'].connect_to(driver_plug)

        remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        remap_node.plugs['value'].element(1).child(0).set_value(1.0)
        remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        vertical_input_plug.connect_to(remap_node.plugs['inputValue'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1X'])
        diamond_handle.plugs['tx'].connect_to(multiply.plugs['input2X'])
        multiply.plugs['outputX'].connect_to(blend_weighted_node.plugs['input'].element(0))
        blend_weighted_node.plugs['output'].connect_to(combo_driver_plug)

        # Mouth Down
        plug_name = 'mouth_down'

        driver_plug = diamond_handle.create_plug(
            plug_name,
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        combo_driver_plug = diamond_handle.create_plug(
            '%s_%s' % (plug_name, root_name),
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        blend_weighted_node = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        diamond_handle.plugs['tx'].connect_to(reverse.plugs['inputX'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1Y'])
        reverse.plugs['outputX'].connect_to(multiply.plugs['input2Y'])
        multiply.plugs['outputY'].connect_to(driver_plug)

        remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        remap_node.plugs['value'].element(1).child(0).set_value(-1.0)
        remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        vertical_input_plug.connect_to(remap_node.plugs['inputValue'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1X'])
        diamond_handle.plugs['tx'].connect_to(multiply.plugs['input2X'])
        multiply.plugs['outputX'].connect_to(blend_weighted_node.plugs['input'].element(0))
        blend_weighted_node.plugs['output'].connect_to(combo_driver_plug)



        # Mouth Left
        plug_name = 'mouth_left'

        driver_plug = diamond_handle.create_plug(
            plug_name,
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        combo_driver_plug = diamond_handle.create_plug(
            '%s_%s' % (plug_name, root_name),
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        blend_weighted_node = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        diamond_handle.plugs['tx'].connect_to(reverse.plugs['inputX'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1Y'])
        reverse.plugs['outputX'].connect_to(multiply.plugs['input2Y'])
        multiply.plugs['outputY'].connect_to(driver_plug)
        remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        remap_node.plugs['value'].element(1).child(0).set_value(1.0)
        remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        horizontal_input_plug.connect_to(remap_node.plugs['inputValue'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1X'])
        diamond_handle.plugs['tx'].connect_to(multiply.plugs['input2X'])
        multiply.plugs['outputX'].connect_to(blend_weighted_node.plugs['input'].element(0))
        blend_weighted_node.plugs['output'].connect_to(combo_driver_plug)

        # Mouth Left
        plug_name = 'mouth_right'

        driver_plug = diamond_handle.create_plug(
            plug_name,
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        combo_driver_plug = diamond_handle.create_plug(
            '%s_%s' % (plug_name, root_name),
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        blend_weighted_node = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_%s' % (this.root_name, plug_name)
        )
        reverse = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_%s' % (this.root_name, plug_name)
        )

        diamond_handle.plugs['tx'].connect_to(reverse.plugs['inputX'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1Y'])
        reverse.plugs['outputX'].connect_to(multiply.plugs['input2Y'])
        multiply.plugs['outputY'].connect_to(driver_plug)
        remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        remap_node.plugs['value'].element(1).child(0).set_value(-1.0)
        remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        horizontal_input_plug.connect_to(remap_node.plugs['inputValue'])
        remap_node.plugs['outValue'].connect_to(multiply.plugs['input1X'])
        diamond_handle.plugs['tx'].connect_to(multiply.plugs['input2X'])
        multiply.plugs['outputX'].connect_to(blend_weighted_node.plugs['input'].element(0))
        blend_weighted_node.plugs['output'].connect_to(combo_driver_plug)

        return this
