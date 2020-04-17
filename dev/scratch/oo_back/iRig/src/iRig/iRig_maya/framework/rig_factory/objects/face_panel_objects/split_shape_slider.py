from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.node_objects.depend_node import DependNode

import utilities as utl
from rig_math.matrix import Matrix


class SplitShapeSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(SplitShapeSliderGuide, self).__init__(**kwargs)
        self.toggle_class = SplitShapeSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SplitShapeSliderGuide, cls).create(controller, **kwargs)
        return this


class SplitShapeSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(SplitShapeSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SplitShapeSlider, cls).create(controller, **kwargs)
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
        matrix = Matrix(scale=[2.0, 1.0, 1.0])
        square_handle.plugs['shape_matrix'].set_value(matrix)

        square_handle.plugs['rotateX'].set_value(90)
        utl.set_color_index(square_handle, 1)  # black

        for attr in ['rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            square_handle.plugs[attr].set_locked(True)

        diamond_handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.5,
            side=side
        )
        diamond_handle.groups[0].plugs['translateY'].set_value(-0.5)

        right_shape_driver = diamond_handle.create_plug(
            'right_shape_driver',
            k=True,
            at='double',
            min=0.0,
            max=1.0
        )
        left_shape_driver = diamond_handle.create_plug(
            'left_shape_driver',
            k=True,
            at='double',
            min=0.0,
            max=1.0
        )

        left_multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_left' % root_name
        )

        right_multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_right' % root_name
        )

        left_remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_left' % root_name
        )

        right_remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_right' % root_name
        )

        right_remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        right_remap_node.plugs['value'].element(0).child(1).set_value(1.0)
        right_remap_node.plugs['value'].element(1).child(0).set_value(-1.0)
        right_remap_node.plugs['value'].element(1).child(1).set_value(0.0)

        left_remap_node.plugs['value'].element(0).child(0).set_value(0.0)
        left_remap_node.plugs['value'].element(0).child(1).set_value(1.0)
        left_remap_node.plugs['value'].element(1).child(0).set_value(1.0)
        left_remap_node.plugs['value'].element(1).child(1).set_value(0.0)

        diamond_handle.plugs['tx'].connect_to(right_remap_node.plugs['inputValue'])
        diamond_handle.plugs['tx'].connect_to(left_remap_node.plugs['inputValue'])

        left_remap_node.plugs['outValue'].connect_to(left_multiply_node.plugs['input1X'])
        diamond_handle.plugs['ty'].connect_to(left_multiply_node.plugs['input2X'])

        right_remap_node.plugs['outValue'].connect_to(right_multiply_node.plugs['input1X'])
        diamond_handle.plugs['ty'].connect_to(right_multiply_node.plugs['input2X'])

        # oops left is right, right is left
        left_multiply_node.plugs['outputX'].connect_to(right_shape_driver)
        right_multiply_node.plugs['outputX'].connect_to(left_shape_driver)

        utl.set_attr_limit(diamond_handle, 'TransY', 0.0, 1.0)
        utl.set_attr_limit(diamond_handle, 'TransX', -1.0, 1.0)

        for attr in ['translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            diamond_handle.plugs[attr].set_locked(True)
        return this
