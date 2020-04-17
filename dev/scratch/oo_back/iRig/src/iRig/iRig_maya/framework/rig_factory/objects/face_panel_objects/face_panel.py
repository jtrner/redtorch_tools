from brow_slider import BrowSlider, BrowSliderGuide
from cheek_slider import CheekSlider, CheekSliderGuide
from eye_slider import EyeSlider, EyeSliderGuide
from closed_eye_slider import ClosedEyeSlider, ClosedEyeSliderGuide
from mouth_slider import MouthSlider, MouthSliderGuide
from nose_slider import NoseSliderGuide
from teeth_slider import TeethSliderGuide
from brow_waggle_slider import BrowWaggleSliderGuide
from blink_slider import BlinkSlider, BlinkSliderGuide
from jaw_overbite_slider import JawOverbiteSliderGuide
from lip_sync_slider import LipSyncSliderGuide
from squash_slider import SquashSliderGuide
from tongue_slider import TongueSliderGuide
from lip_curl_slider import LipCurlSliderGuide
from face_panel_main_slider import FacePanelMainGuide
from closed_blink_slider import ClosedBlinkSlider
from mouth_combo_slider import MouthComboSlider
from eyelid_slider import EyeLidSliderGuide
from rig_factory.objects.part_objects.part_array import PartArray, PartArrayGuide
import utilities as utl


class FacePanelGuide(PartArrayGuide):

    default_settings = dict(
        root_name='face_panel'
    )

    def __init__(self, **kwargs):
        super(FacePanelGuide, self).__init__(**kwargs)
        self.toggle_class = FacePanel.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FacePanelGuide, cls).create(controller, **kwargs)
        return this

    def create_members(self):
        root_name = self.root_name

        main_panel = self.create_part(
            FacePanelMainGuide,
            root_name='{0}_main'.format(root_name),
            side='center'
        )
        main_panel.handles[0].plugs['translate'].set_value([0.0, 0.0, 0.0])
        main_joint = main_panel.joints[0]

        waggle_brow = self.create_part(
            BrowWaggleSliderGuide,
            root_name='{0}_brow_waggle'.format(root_name),
            side='center'
        )
        waggle_brow.handles[0].plugs['translate'].set_value([-4.0, 4.25, 0.0])
        waggle_brow.set_parent_joint(main_joint)

        # LEFT side #################################################################
        left_brow = self.create_part(
            BrowSliderGuide,
            root_name='{0}_brow'.format(root_name),
            side='left'
        )
        left_brow.handles[0].plugs['translate'].set_value([-1.0, 5.0, 0.0])
        left_brow.set_parent_joint(main_joint)

        right_brow = self.create_part(
            BrowSliderGuide,
            root_name='{0}_brow'.format(root_name),
            side='right'
        )
        right_brow.handles[0].plugs['translate'].set_value([-7.0, 5.0, 0.0])
        right_brow.set_parent_joint(main_joint)

        left_eye = self.create_part(
            EyeSliderGuide,
            root_name='{0}_eye'.format(root_name),
            side='left'
        )
        left_eye.handles[0].plugs['translate'].set_value([-1.0, 2.0, 0.0])
        left_eye.set_parent_joint(main_joint)

        right_eye = self.create_part(
            EyeSliderGuide,
            root_name='{0}_eye'.format(root_name),
            side='right'
        )
        right_eye.handles[0].plugs['translate'].set_value([-7.0, 2.0, 0.0])
        right_eye.set_parent_joint(main_joint)

        nose = self.create_part(
            NoseSliderGuide,
            root_name='{0}_nose'.format(root_name),
            side='center'
        )
        nose.handles[0].plugs['translate'].set_value([-4.0, 0.0, 0.0])
        nose.set_parent_joint(main_joint)

        left_cheek = self.create_part(
            CheekSliderGuide,
            root_name='{0}_cheek'.format(root_name),
            side='left'
        )
        left_cheek.handles[0].plugs['translate'].set_value([1.5, -1.0, 0.0])
        left_cheek.set_parent_joint(main_joint)

        right_cheek = self.create_part(
            CheekSliderGuide,
            root_name='{0}_cheek'.format(root_name),
            side='right'
        )
        right_cheek.handles[0].plugs['translate'].set_value([-9.0, -1.0, 0.0])
        right_cheek.set_parent_joint(main_joint)

        mouth = self.create_part(
            MouthSliderGuide,
            root_name='{0}_mouth'.format(root_name),
            side='center'
        )
        mouth.handles[0].plugs['translate'].set_value([-4.0, -3.5, 0.0])
        mouth.set_parent_joint(main_joint)

        left_blink = self.create_part(
            BlinkSliderGuide,
            root_name='{0}_blink'.format(root_name),
            side='left'
        )
        left_blink.handles[0].plugs['translate'].set_value([-3.0, 7.5, 0.0])
        left_blink.set_parent_joint(main_joint)

        right_blink = self.create_part(
            BlinkSliderGuide,
            root_name='{0}_blink'.format(root_name),
            side='right'
        )
        right_blink.handles[0].plugs['translate'].set_value([-5.0, 7.5, 0.0])
        right_blink.set_parent_joint(main_joint)

        eyelid_slider = self.create_part(
            EyeLidSliderGuide,
            root_name='{0}_eyelids'.format(root_name),
            side='center'
        )
        eyelid_slider.handles[0].plugs['translate'].set_value([1.5, 2.0, 0.0])
        eyelid_slider.set_parent_joint(main_joint)

        # RIGHT side #################################################################
        jaw_overbite = self.create_part(
            JawOverbiteSliderGuide,
            root_name='{0}_jaw_overbite'.format(root_name),
            side='center'
        )
        jaw_overbite.handles[0].plugs['translate'].set_value([6.0, 6.0, 0.0])
        jaw_overbite.set_parent_joint(main_joint)

        lip_sync_slider = self.create_part(
            LipSyncSliderGuide,
            root_name='{0}_lip_sync'.format(root_name),
            side='center'
        )
        lip_sync_slider.handles[0].plugs['translate'].set_value([3.0, 1.0, 0.0])
        lip_sync_slider.set_parent_joint(main_joint)

        squash_slider = self.create_part(
            SquashSliderGuide,
            root_name='{0}_squash'.format(root_name),
            side='center'
        )
        squash_slider.handles[0].plugs['translate'].set_value([6.0, -6.0, 0.0])
        squash_slider.set_parent_joint(main_joint)

        tongue_slider = self.create_part(
            TongueSliderGuide,
            root_name='{0}_tongue'.format(root_name),
            side='center'
        )
        tongue_slider.handles[0].plugs['translate'].set_value([5.0, -4.5, 0.0])
        tongue_slider.set_parent_joint(main_joint)

        left_lip_curl_slider = self.create_part(
            LipCurlSliderGuide,
            root_name='{0}_lip_curl'.format(root_name),
            side='left'
        )
        left_lip_curl_slider.handles[0].plugs['translate'].set_value([5.0, 2.0, 0.0])
        left_lip_curl_slider.set_parent_joint(main_joint)

        right_lip_curl_slider = self.create_part(
            LipCurlSliderGuide,
            root_name='{0}_lip_curl'.format(root_name),
            side='right'
        )
        right_lip_curl_slider.handles[0].plugs['translate'].set_value([7.0, 2.0, 0.0])
        right_lip_curl_slider.set_parent_joint(main_joint)

        teeth = self.create_part(
            TeethSliderGuide,
            root_name='{0}_teeth'.format(root_name),
            side='center'
        )
        teeth.handles[0].plugs['translate'].set_value([6.0, -2.0, 0.0])
        teeth.set_parent_joint(main_joint)


class FacePanel(PartArray):

    def __init__(self, **kwargs):
        super(FacePanel, self).__init__(**kwargs)

    def post_create(self, **blueprint):
        left_brow = None
        left_eye = None
        right_brow = None
        right_eye = None
        center_eye = None
        mouth = None
        left_blink = None
        right_blink = None
        center_blink = None
        left_squint = None
        right_squint = None
        mouth_combo_slider = None
        for part in self.parts:
            if isinstance(part, BrowSlider):
                if part.side == 'left':
                    left_brow = part
                if part.side == 'right':
                    right_brow = part
            if isinstance(part, EyeSlider):
                if part.side == 'left':
                    left_eye = part
                if part.side == 'right':
                    right_eye = part
                if part.side == 'center':
                    center_eye = part
            if isinstance(part, (BlinkSlider, ClosedBlinkSlider)):
                if part.side == 'left':
                    left_blink = part
                if part.side == 'right':
                    right_blink = part
                if part.side == 'center':
                    center_blink = part
            if isinstance(part, CheekSlider):
                if part.side == 'left':
                    left_squint = part
                if part.side == 'right':
                    right_squint = part
            if isinstance(part, MouthComboSlider):
                mouth_combo_slider = part
            if isinstance(part, MouthSlider):
                mouth = part
        if left_eye and left_blink:
            left_blink.plugs['up_blink_shape_driver'].connect_to(left_eye.plugs['up_lid_blink_driver'])
            left_blink.plugs['down_blink_shape_driver'].connect_to(left_eye.plugs['down_lid_blink_driver'])
            left_blink.handles[0].plugs['tx'].connect_to(left_eye.plugs['up_lid_choke'])
            left_blink.handles[0].plugs['tx'].connect_to(left_eye.plugs['down_lid_choke'])
        if right_eye and right_blink:
            right_blink.plugs['up_blink_shape_driver'].connect_to(right_eye.plugs['up_lid_blink_driver'])
            right_blink.plugs['down_blink_shape_driver'].connect_to(right_eye.plugs['down_lid_blink_driver'])
            right_blink.handles[0].plugs['tx'].connect_to(right_eye.plugs['up_lid_choke'])
            right_blink.handles[0].plugs['tx'].connect_to(right_eye.plugs['down_lid_choke'])
        if center_eye and center_blink:
            center_blink.plugs['up_blink_shape_driver'].connect_to(center_eye.plugs['up_lid_blink_driver'])
            center_blink.plugs['down_blink_shape_driver'].connect_to(center_eye.plugs['down_lid_blink_driver'])
            center_blink.handles[0].plugs['tx'].connect_to(center_eye.plugs['up_lid_choke'])
            center_blink.handles[0].plugs['tx'].connect_to(center_eye.plugs['down_lid_choke'])
        if mouth_combo_slider and mouth:
            mouth.main_handle.plugs['ty'].connect_to(mouth_combo_slider.plugs['vertical_input'])
            mouth.main_handle.plugs['tx'].connect_to(mouth_combo_slider.plugs['horizontal_input'])

        if left_eye and left_brow:

            utl.create_corrective_driver(
                left_eye.plugs['up_in_lid_vertical'],
                left_brow.plugs['brow_in_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=left_eye.side,
                root_name='brow_in_down_blink'
            )
            utl.create_corrective_driver(
                left_eye.plugs['up_mid_lid_vertical'],
                left_brow.plugs['brow_mid_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=left_eye.side,
                root_name='brow_mid_down_blink'
            )
            utl.create_corrective_driver(
                left_eye.plugs['up_out_lid_vertical'],
                left_brow.plugs['brow_out_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=left_eye.side,
                root_name='brow_out_down_blink'
            )

        if right_eye and right_brow:

            utl.create_corrective_driver(
                right_eye.plugs['up_in_lid_vertical'],
                right_brow.plugs['brow_in_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=right_eye.side,
                root_name='brow_in_down_blink'
            )
            utl.create_corrective_driver(
                right_eye.plugs['up_mid_lid_vertical'],
                right_brow.plugs['brow_mid_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=right_eye.side,
                root_name='brow_mid_down_blink'
            )
            utl.create_corrective_driver(
                right_eye.plugs['up_out_lid_vertical'],
                right_brow.plugs['brow_out_vertical'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=right_eye.side,
                root_name='brow_out_down_blink'
            )

        if left_eye and left_squint:

            utl.create_corrective_driver(
                left_eye.plugs['down_in_lid_vertical'],
                left_squint.handles[1].plugs['ty'],
                0.5, 1.0,
                1.0, 1.0,
                side=right_eye.side,
                root_name='squint_blink_in'
            )
            utl.create_corrective_driver(
                left_eye.plugs['down_mid_lid_vertical'],
                left_squint.handles[1].plugs['ty'],
                0.5, 1.0,
                1.0, 1.0,
                side=right_eye.side,
                root_name='squint_blink_mid'
            )
            utl.create_corrective_driver(
                left_eye.plugs['down_out_lid_vertical'],
                left_squint.handles[1].plugs['ty'],
                0.5, 1.0,
                1.0, 1.0,
                side=right_eye.side,
                root_name='squint_blink_out'
            )


