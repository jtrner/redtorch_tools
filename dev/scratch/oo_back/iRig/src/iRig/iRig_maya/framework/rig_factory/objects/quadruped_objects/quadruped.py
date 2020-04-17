
import copy
from rig_factory.objects.part_objects.main import MainGuide
from rig_factory.objects.quadruped_objects.quadruped_neck import QuadrupedNeckGuide
from rig_factory.objects.quadruped_objects.quadruped_spine import QuadrupedSpineGuide
from rig_factory.objects.quadruped_objects.quadruped_bendy_back_leg import QuadrupedBendyBackLegGuide
from rig_factory.objects.part_objects.container_array import ContainerArray, ContainerArrayGuide
from rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.positions as pos


class QuadrupedMixin(object):

    main = ObjectProperty(
        name='main'
    )
    spine = ObjectProperty(
        name='spine'
    )
    neck = ObjectProperty(
        name='neck'
    )
    left_arm = ObjectProperty(
        name='left_arm'
    )
    right_arm = ObjectProperty(
        name='right_arm'
    )
    left_leg = ObjectProperty(
        name='left_leg'
    )
    right_leg = ObjectProperty(
        name='right_leg'
    )
    left_hand = ObjectProperty(
        name='left_hand'
    )
    right_hand = ObjectProperty(
        name='right_hand'
    )
    extra_parts = ObjectListProperty(
        name='extra_parts'
    )
    face_shape_network = ObjectProperty(
        name='face_shape_network'
    )


class QuadrupedGuide(ContainerArrayGuide, QuadrupedMixin):

    default_settings = dict(
        root_name='biped'
    )

    def __init__(self, **kwargs):
        super(QuadrupedGuide, self).__init__(**kwargs)
        self.toggle_class = Quadruped.__name__

    def post_create(self, **kwargs):
        super(QuadrupedGuide, self).post_create(**kwargs)

    def create_members(self):
        super(QuadrupedGuide, self).create_members()
        controller = self.controller

        controller.progress_signal.emit(
            message='Building Biped Member: Spine',
            maximum=7,
            value=0
        )
        main = self.create_part(
            MainGuide,
            root_name='main',
            size=15.0
        )

        spine = self.create_part(
            QuadrupedSpineGuide,
            root_name='spine',
            size=15.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Neck',
            value=1
        )
        neck = self.create_part(
            QuadrupedNeckGuide,
            root_name='neck',
            size=5.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Left Arm',
            value=2
        )

        left_leg = self.create_part(
            QuadrupedBendyBackLegGuide,
            root_name='back_leg',
            side='left',
            size=4.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Right Leg',
            value=5
        )
        right_leg = self.create_part(
            QuadrupedBendyBackLegGuide,
            root_name='back_leg',
            side='right',
            size=4.0
        )

        left_front_leg = self.create_part(
            QuadrupedBendyBackLegGuide,
            root_name='front_leg',
            side='left',
            size=4.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Right Leg',
            value=5
        )
        right_front_leg = self.create_part(
            QuadrupedBendyBackLegGuide,
            root_name='front_leg',
            side='right',
            size=4.0
        )

        spine.set_parent_joint(main.joints[-1])
        neck.set_parent_joint(spine.joints[-1])
        left_leg.set_parent_joint(spine.joints[0])
        right_leg.set_parent_joint(spine.joints[0])
        left_front_leg.set_parent_joint(spine.joints[-1])
        right_front_leg.set_parent_joint(spine.joints[-1])
        self.set_handle_positions(copy.copy(pos.QUADRUPED_POSITIONS))

        controller.progress_signal.emit(
            done=True
        )


class Quadruped(ContainerArray, QuadrupedMixin):

    mocap_joints = ObjectListProperty(
        name='mocap_joints'
    )
    character_node = ObjectProperty(
        name='character_node'
    )

    def __init__(self, **kwargs):
        super(Quadruped, self).__init__(**kwargs)

    # def finish_create(self, **kwargs):
    #
    #     secondary_handle_plug = self.settings_handle.create_plug(
    #         'bendy_vis',
    #         k=True,
    #         at='long',
    #         min=0,
    #         max=1,
    #         dv=1
    #     )
    #
    #     secondary_handles = WeakList()
    #     parts = self.get_parts()
    #     for part in parts:
    #         secondary_handles.extend(part.secondary_handles)
    #
    #     for handle in secondary_handles:
    #         secondary_handle_plug.connect_to(handle.plugs['visibility'])
    #
    #     self.add_plugs([secondary_handle_plug])
    #     super(Quadruped, self).finish_create(**kwargs)

    def finalize(self):
        super(Quadruped, self).finalize()
