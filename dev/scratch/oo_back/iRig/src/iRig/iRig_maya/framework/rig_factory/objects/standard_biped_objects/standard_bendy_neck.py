from rig_factory.objects.standard_biped_objects.bendy_spline import BendySplineGuide, BendySpline
from rig_factory.objects.base_objects.properties import ObjectListProperty
import rig_factory.utilities.handle_utilities as handle_utils
import rig_factory.utilities.limb_utilities as limb_utils


class StandardBendyNeckGuide(BendySplineGuide):
    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center'
    )

    def __init__(self, **kwargs):
        super(StandardBendyNeckGuide, self).__init__(**kwargs)
        self.toggle_class = StandardBendyNeck.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['root_pivot_height_value'] = 0.0
        kwargs['eff_pivot_height_value'] = 0.0
        kwargs['handles_count'] = 3
        kwargs['root_name'] = 'neck'

        this = super(StandardBendyNeckGuide, cls).create(controller, **kwargs)

        return this


class StandardBendyNeck(BendySpline):

    primary_handles = ObjectListProperty(name='primary_handles')

    gimbal_handles = ObjectListProperty(name='gimbal_handles')

    def __init__(self, **kwargs):
        super(StandardBendyNeck, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['root_pivot_height_value'] = 0.0
        kwargs['eff_pivot_height_value'] = 0.0
        kwargs['handles_count'] = 3

        # Create a StandardSpine object
        this = super(StandardBendyNeck, cls).create(controller, **kwargs)

        primary_handles = this.primary_handles
        gimbal_handles = this.segment_chain.bendy_handles
        nurbs_curve = this.segment_chain.nurbs_curve
        bendy_joints = this.segment_chain.bendy_joints
        side = this.side

        # spline ik to stretchable
        limb_utils.create_stretchy_ik_joints(nurbs_curve, bendy_joints, side)

        # unlock attrs
        root = this.get_root()
        for handle in primary_handles + gimbal_handles:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])

        # connect handles, and their gimbals
        for primary, gimbal in zip(primary_handles, gimbal_handles):
            handle_utils.create_and_connect_gimbal_visibility_attr(primary, gimbal)

        # expose rotation order in channel box
        for handle in primary_handles + gimbal_handles:
            handle_utils.create_and_connect_rotation_order_attr(handle)

        this.primary_handles = primary_handles
        this.gimbal_handles = gimbal_handles

        return this
