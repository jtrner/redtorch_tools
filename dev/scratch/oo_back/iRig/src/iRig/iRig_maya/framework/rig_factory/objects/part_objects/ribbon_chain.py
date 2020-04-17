
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_factory.objects.rig_objects.surface_point import SurfacePoint


class RibbonChainGuide(SplineChainGuide):

    default_settings = {
        'count': 5,
        'root_name': 'ribbon_chain',
        'size': 1.0,
        'side': 'center',
    }

    def __init__(self, **kwargs):
        super(RibbonChainGuide, self).__init__(**kwargs)
        self.toggle_class = RibbonChain.__name__
        self.joint_chain = True


class RibbonChain(Part):

    ribbon = ObjectProperty(
        name='ribbon'
    )

    def __init__(self, **kwargs):
        super(RibbonChain, self).__init__(**kwargs)
        self.joint_chain = True

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(RibbonChain, cls).create(controller, **kwargs)

        positions = [x.get_translation() for x in this.matrices]
        root_name = this.root_name
        joint_count = len(this.matrices)
        follicle_parameter = 1.0 / (joint_count - 1)

        ribbon = this.create_child(
            Ribbon,
            positions,
            root_name=root_name + '_ribbon',
            degree=3,
        )
        ribbon.plugs['v'].set_value(False)

        follicle_transform = this.create_child(
            Transform,
            root_name=root_name + '_follicles'
        )

        joints = []
        parent = None
        for i in range(joint_count):

            follicle = this.create_child(
                SurfacePoint,
                index=i,
                parent=follicle_transform,
                surface=ribbon.nurbs_surface,
            )
            follicle.follicle.plugs['v'].set_value(0)
            follicle.follicle.plugs['parameterU'].set_value(0.5)
            follicle.follicle.plugs['parameterV'].set_value(follicle_parameter * i)

            handle = this.create_handle(
                index=i,
                parent=follicle,
                shape='cube',
            )

            joint = this.joint_group.create_child(
                Joint,
                index=i,
                parent=parent,
            )
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                visibility=0.0,
            )
            joint.zero_rotation()
            controller.create_parent_constraint(
                handle,
                joint,
                mo=False,
            )

            joints.append(joint)
            parent = joint

        root = this.get_root()
        root.geometry[ribbon.nurbs_surface.name] = ribbon.nurbs_surface
        this.joints = joints
        this.ribbon = ribbon

        return this
