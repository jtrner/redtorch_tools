import copy
import rig_math.utilities as rmu
from rig_factory.objects.biped_objects.biped_finger import BipedFingerGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.part_objects.part_array import PartArrayGuide, PartArray
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_math.matrix import Matrix
import rig_factory.positions as pos


class BipedHandGuide(PartArrayGuide):

    default_settings = {
        'root_name': 'hand',
        'size': 1.0,
        'side': 'left'
    }

    def __init__(self, **kwargs):
        super(BipedHandGuide, self).__init__(**kwargs)
        self.toggle_class = BipedHand.__name__

    def create_members(self):
        super(BipedHandGuide, self).create_members()

        self.create_part(
            BipedFingerGuide,
            side=self.side,
            size=self.size,
            root_name='thumb',
            count=4
        )

        for index_name in ['pointer', 'middle', 'ring', 'pinky']:
            self.create_part(
                BipedFingerGuide,
                side=self.side,
                size=self.size,
                root_name='finger_' + index_name
            )

        self.set_handle_positions(copy.copy(pos.BIPED_POSITIONS))


class BipedHand(PartArray):

    def post_create(self, **kwargs):
        """
        Runs after hand and fingers have been created
        Creates a pin_handle that controls these hand positions:
            - splay
            - bend
            - fist
            - spread
            - fold
            - pinch
        """

        root = self.get_root()
        side = self.side
        size = self.size
        root_name = self.root_name
        handles = self.get_handles()
        controller = self.controller
        handle_groups = [handle.groups[-2] for handle in handles]
        settings_handle_size = 2 * size
        shape_matrix = Matrix()
        hand_length = settings_handle_size * 4

        settings_handle = self.create_handle(
            parent=self.joint_group,
            group_count=1,
            root_name=root_name + '_settings',
            shape='fist',
            axis='z',
            matrix=(
                [0.0, hand_length * -1.0, 0.0]
                if side == 'right' else
                [0.0, hand_length, 0.0]
            ),
        )

        if side == 'right':
            shape_matrix.set_scale([
                settings_handle_size,
                settings_handle_size,
                settings_handle_size
            ])
        else:
            shape_matrix.set_scale([
                settings_handle_size * -1,
                settings_handle_size * -1,
                settings_handle_size
            ])

        settings_handle.plugs['shape_matrix'].set_value(list(shape_matrix))

        splay_fingers_plug = self.create_plug(
            'splay',
            at='double',
            dv=0.0,
            keyable=False
        )

        splay_thumb_plug = self.create_plug(
            'splay_thumb',
            at='double',
            dv=0.0,
            keyable=False
        )

        spread_fingers_plug = self.create_plug(
            'spread',
            at='double',
            dv=0.0,
            keyable=False
        )

        spread_thumb_plug = self.create_plug(
            'spread_thumb',
            at='double',
            dv=0.0,
            keyable=False
        )

        curl_fingers_plug = self.create_plug(
            'curl_fingers',
            at='double',
            dv=0.0
        )

        curl_thumb_plug = self.create_plug(
            'curl_thumb',
            at='double',
            dv=0.0,
            keyable=False
        )

        bend_fingers_plug = self.create_plug(
            'bend_fingers',
            at='double',
            dv=0.0,
            keyable=False
        )

        bend_thumb_plug = self.create_plug(
            'bend_thumb',
            at='double',
            dv=0.0,
            keyable=False
        )

        thumb_mute_attr = settings_handle.create_plug(
            'mute_thumb',
            k=True,
            at='float',
            dv=0,
            min=0.0,
            max=1.0,
        )

        # Attributes

        settings_handle.plugs['rx'].connect_to(bend_fingers_plug)
        settings_handle.plugs['rz'].connect_to(curl_fingers_plug)
        settings_handle.plugs['ry'].connect_to(splay_fingers_plug)
        settings_handle.plugs['sz'].connect_to(spread_fingers_plug)

        thumb_mute_blend = controller.create_object(
            DependNode,
            node_type='blendColors',
            side=side,
            root_name=root_name + '_thumb_mute'
        )

        thumb_mute_blend_2 = controller.create_object(
            DependNode,
            node_type='blendColors',
            side=side,
            root_name=root_name + '_thumb_mute_2'
        )

        thumb_mute_blend_3 = controller.create_object(
            DependNode,
            node_type='blendColors',
            side=side,
            root_name=root_name + '_thumb_mute_3'
        )

        thumb_mute_blend.plugs['color1R'].set_value(0)
        thumb_mute_blend.plugs['color1G'].set_value(0)
        thumb_mute_blend.plugs['color1B'].set_value(0)
        thumb_mute_blend_2.plugs['color1R'].set_value(0)
        thumb_mute_blend_2.plugs['color1G'].set_value(1.0)
        thumb_mute_blend_2.plugs['color1B'].set_value(0)
        thumb_mute_blend_3.plugs['color1R'].set_value(0)
        thumb_mute_blend_3.plugs['color1G'].set_value(0.0)
        thumb_mute_blend_3.plugs['color1B'].set_value(0)

        curl_fingers_plug.connect_to(thumb_mute_blend.plugs['color2G'])
        bend_fingers_plug.connect_to(thumb_mute_blend.plugs['color2B'])
        splay_fingers_plug.connect_to(thumb_mute_blend_2.plugs['color2R'])
        spread_fingers_plug.connect_to(thumb_mute_blend_2.plugs['color2G'])

        thumb_mute_blend.plugs['outputG'].connect_to(curl_thumb_plug)
        thumb_mute_blend.plugs['outputB'].connect_to(bend_thumb_plug)
        thumb_mute_blend_2.plugs['outputR'].connect_to(splay_thumb_plug)
        thumb_mute_blend_2.plugs['outputG'].connect_to(spread_thumb_plug)

        thumb_mute_attr.connect_to(thumb_mute_blend.plugs['blender'])
        thumb_mute_attr.connect_to(thumb_mute_blend_2.plugs['blender'])
        thumb_mute_attr.connect_to(thumb_mute_blend_3.plugs['blender'])

        # Sdks

        sdk_network = controller.create_object(
            SDKNetwork,
            root_name=root_name,
            side=side
        )
        sdk_network.initialize_driven_plugs(
            handle_groups,
            ['rx', 'ry', 'rz']
        )

        all_handles = []
        finger_handles = []
        first_finger_handles = []
        base_finger_handles = []
        thumb_handles = []
        for finger in self.parts:
            part_handles = list(finger.get_handles())
            if 'thumb' in finger.root_name.lower():
                thumb_handles = part_handles
                all_handles.append(part_handles)
            else:
                all_handles.append(part_handles)
                finger_handles.append(part_handles)
                base_finger_handles.append(part_handles[0].groups[-1])
                first_finger_handles.append(part_handles[1].groups[-1])

        if self.parts:
            controller.create_matrix_parent_constraint(
                self.parts[0].joint_group,
                settings_handle.groups[0]
            )

            # Curl

            sdk_group = sdk_network.create_group(
                driver_plug=curl_fingers_plug,
                root_name='{0}_curl'.format(root_name),
                side=side,
                lock_curves=False
            )

            sdk_group.create_keyframe_group(
                in_value=0.0
            ).set_keyframe_tangents('smooth')

            for handle_array in finger_handles:
                if handle_array[0] not in thumb_handles:
                    for handle in handle_array[1:]:
                        handle.groups[-2].plugs['rx'].set_value(90.0)

            sdk_group.create_keyframe_group(
                in_value=-90.0
            ).set_keyframe_tangents('smooth')
            controller.dg_dirty()

            # Bend

            sdk_group = sdk_network.create_group(
                driver_plug=bend_fingers_plug,
                root_name='{0}_bend'.format(root_name),
                side=side
            )

            sdk_group.create_keyframe_group(
                in_value=0.0
            ).set_keyframe_tangents('smooth')

            for handle_array in finger_handles:
                if handle_array[0] not in thumb_handles:
                    for handle in handle_array[1:]:
                        handle.groups[-2].plugs['rz'].set_value(90.0)

            sdk_group.create_keyframe_group(
                in_value=90.0
            ).set_keyframe_tangents('smooth')
            controller.dg_dirty()

            # Finger_splay

            splay_values = list(reversed(list(rmu.decimal_range(
                -90.0,
                90.0,
                len(all_handles)
            ))))

            sdk_group = sdk_network.create_group(
                driver_plug=splay_fingers_plug,
                root_name='{0}_finger_splay'.format(root_name),
                side=side
            )

            sdk_group.create_keyframe_group(
                in_value=0.0
            ).set_keyframe_tangents('smooth')

            for i, value in enumerate(splay_values):
                if all_handles[i][1] not in thumb_handles:
                    all_handles[i][1].groups[-2].plugs['rx'].set_value(value)
                    all_handles[i][0].groups[-2].plugs['rx'].set_value(value * 0.5)

            sdk_group.create_keyframe_group(
                in_value=90.0
            ).set_keyframe_tangents('smooth')

            controller.dg_dirty()

            # Finger Spread

            sdk_group = sdk_network.create_group(
                driver_plug=spread_fingers_plug,
                root_name='{0}_finger_spread'.format(root_name),
                side=side
            )

            sdk_group.create_keyframe_group(
                in_value=1.0
            ).set_keyframe_tangents('smooth')

            for i, value in enumerate(splay_values):
                if all_handles[i][1] not in thumb_handles:
                    all_handles[i][1].groups[-2].plugs['rz'].set_value(value)
                    all_handles[i][0].groups[-2].plugs['rz'].set_value(value * 0.5)

            sdk_group.create_keyframe_group(
                in_value=4.0
            ).set_keyframe_tangents('smooth')

            controller.dg_dirty()

            # Thumb Handles


            if thumb_handles:

                # Curl

                sdk_group = sdk_network.create_group(
                    driver_plug=curl_thumb_plug,
                    root_name='{0}_thumb_curl'.format(root_name),
                    side=side
                )

                sdk_group.create_keyframe_group(
                    in_value=0.0
                ).set_keyframe_tangents('smooth')

                for handle in thumb_handles[1:]:
                    handle.groups[-2].plugs['rx'].set_value(45.0)

                sdk_group.create_keyframe_group(
                    in_value=-90.0
                ).set_keyframe_tangents('smooth')
                controller.dg_dirty()

                # Bend

                sdk_group = sdk_network.create_group(
                    driver_plug=bend_thumb_plug,
                    root_name='{0}_thumb_bend'.format(root_name),
                    side=side
                )

                sdk_group.create_keyframe_group(
                    in_value=0.0
                ).set_keyframe_tangents('smooth')

                for handle in thumb_handles[1:]:
                    handle.groups[-2].plugs['rz'].set_value(45.0)

                sdk_group.create_keyframe_group(
                    in_value=90.0
                ).set_keyframe_tangents('smooth')
                controller.dg_dirty()

                # Thumb Splay

                sdk_group = sdk_network.create_group(
                    driver_plug=splay_thumb_plug,
                    root_name='{0}_thumb_splay'.format(root_name),
                    side=side
                )

                sdk_group.create_keyframe_group(
                    in_value=0.0
                ).set_keyframe_tangents('smooth')

                thumb_handles[1].groups[-2].plugs['rx'].set_value(splay_values[0] * 0.25)
                thumb_handles[0].groups[-2].plugs['rx'].set_value(splay_values[0] * 0.5)

                sdk_group.create_keyframe_group(
                    in_value=90.0
                ).set_keyframe_tangents('smooth')

                controller.dg_dirty()

                # Thumb Spread

                sdk_group = sdk_network.create_group(
                    driver_plug=spread_thumb_plug,
                    root_name='{0}_thumb_splay'.format(root_name),
                    side=side
                )

                sdk_group.create_keyframe_group(
                    in_value=1.0
                ).set_keyframe_tangents('smooth')

                thumb_handles[0].groups[-2].plugs['rz'].set_value(splay_values[0] * 1.0)
                thumb_handles[1].groups[-2].plugs['rx'].set_value(splay_values[0] * -1.0)
                thumb_handles[0].groups[-2].plugs['rx'].set_value(splay_values[0] * -0.5)

                sdk_group.create_keyframe_group(
                    in_value=4.0
                ).set_keyframe_tangents('smooth')

                controller.dg_dirty()

        root.add_plugs([
            settings_handle.plugs['rx'],
            settings_handle.plugs['ry'],
            settings_handle.plugs['rz'],
            settings_handle.plugs['sz'],
            settings_handle.plugs['mute_thumb']
        ])
