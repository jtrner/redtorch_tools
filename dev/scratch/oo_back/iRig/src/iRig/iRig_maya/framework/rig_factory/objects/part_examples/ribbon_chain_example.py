from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from rig_math.vector import Vector


class RibbonChainGuide(SplineChainGuide):

    default_settings = dict(
        root_name='chain',
        size=1.0,
        side='center',
        joint_count=15,
        count=5
    )

    def __init__(self, **kwargs):
        super(RibbonChainGuide, self).__init__(**kwargs)
        self.toggle_class = RibbonChain.__name__
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(RibbonChainGuide, cls).create(controller, **kwargs)
        return this


class RibbonChain(Part):

    ribbon = ObjectProperty(
        name='ribbon'
    )
    up_vector = DataProperty(
        name='up_vector'
    )

    def __init__(self, **kwargs):
        super(RibbonChain, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        joint_matrices = kwargs.pop('joint_matrices', [])
        this = super(RibbonChain, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name
        size = this.size
        side = this.side
        positions = [x.get_translation() for x in matrices]
        ribbon = this.create_child(
            Ribbon,
            positions,
            index=1,
            vector=(Vector(this.up_vector)*(size*0.25)).data
        )
        ribbon.nurbs_surface.assign_shading_group(controller.root.shaders[side].shading_group)
        joints = []
        spline_joint_parent = this.joint_group
        segment_parameter = 1.0 / len(joint_matrices)
        for i, matrix in enumerate(joint_matrices):
            surface_point = this.create_child(
                SurfacePoint,
                root_name='{0}_follicle'.format(root_name),
                surface=ribbon.nurbs_surface,
                index=i,
            )
            surface_point.follicle.plugs['v'].set_value(0)
            surface_point.follicle.plugs['parameterU'].set_value(0.5)
            surface_point.follicle.plugs['parameterV'].set_value(segment_parameter*(i+1))
            handle = this.create_handle(
                index=i,
                parent=surface_point
            )
            joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_spline' % root_name,
                index=i,
                matrix=matrix
            )
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                visibility=0.0
            )
            joint.zero_rotation()
            controller.create_parent_constraint(
                handle,
                joint,
                mo=False
            )
            joints.append(joint)
        this.joints = joints
        this.ribbon = ribbon
        return this
