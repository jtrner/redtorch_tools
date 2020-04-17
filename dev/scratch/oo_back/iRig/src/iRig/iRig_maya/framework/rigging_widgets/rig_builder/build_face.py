from rig_factory.objects.face_objects.face import FaceGuide
from rig_factory.objects.face_objects.face_handle_array import FaceHandleArrayGuide
from rig_factory.objects.part_objects.part_group import PartGroupGuide
from rig_factory.objects.node_objects.mesh import Mesh


def test(controller, owner=None):

    if owner:
        guide = owner.create_part(
            FaceGuide,
            root_name='face'
        )
    else:
        guide = controller.create_object(
            FaceGuide,
            root_name='face'
        )
    if isinstance(guide, FaceGuide):
        guide.import_geometry('D:/rigging_library/rig_builder/ambassador.abc')
        #render_globals = controller.initialize_node('hardwareRenderingGlobals')
        #render_globals.plugs['lineAAEnable'].set_value(1)
        #render_globals.plugs['multiSampleEnable'].set_value(1)

        if 'MOB_headShapeDeformed' in guide.geometry:
            mob_head = guide.geometry['MOB_headShapeDeformed']
        else:
            mob_head = controller.create_object(Mesh, name='MOB_headShapeDeformed')

        size = 0.222222222222

        brow_group = guide.create_part(
                PartGroupGuide,
                root_name='brow',
                side='center',
                size=size
            )

        nose_group = guide.create_part(
                PartGroupGuide,
                root_name='nose',
                side='center',
                size=size
            )


        nose_bridge_array = nose_group.create_part(
            FaceHandleArrayGuide,
            root_name='nose_bridge',
            side='center',
            size=size,
            vertices=get_vertices(
                mob_head,
                1252, 1254, 1256, 1259, 1262
            )
        )

        nose_front_array = nose_group.create_part(
            FaceHandleArrayGuide,
            root_name='nose_front',
            side='center',
            mirror=True,
            size=size,
            vertices=get_vertices(
                mob_head,
                1265, 876, 814, 813, 812
            )
        )

        septum_array = nose_group.create_part(
            FaceHandleArrayGuide,
            root_name='septum',
            side='center',
            mirror=True,
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                1267, 1270
            )
        )

        nose_base = nose_group.create_part(
            FaceHandleArrayGuide,
            root_name='nose_base',
            side='center',
            mirror=True,
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                1272, 262, 242, 263, 380
            )
        )

        mouth_group = guide.create_part(
                PartGroupGuide,
                root_name='mouth',
                side='left',
                size=size
            )



        lip_up_array = mouth_group.create_part(
            FaceHandleArrayGuide,
            root_name='lip_up_stache',
            side='left',
            size=size,
            mirror=True,
            vertices=get_vertices(
                mob_head,
                1274, 919, 918, 934
            )
        )

        mouth_out_array = mouth_group.create_part(
            FaceHandleArrayGuide,
            root_name='mouth_out',
            side='center',
            size=size*0.5,
            mirror=True,
            vertices=get_vertices(
                mob_head,
                1276, 927, 928, 929, 930, 956, 933, 1038, 1044, 935, 953, 1032, 921, 932, 940, 939, 938, 937, 1324
            )
        )

        lip_down_array = mouth_group.create_part(
            FaceHandleArrayGuide,
            root_name='lip_down',
            side='center',
            size=size*0.5,
            mirror=True,
            vertices=get_vertices(
                mob_head,
                (1327, 1331),
                (981, 1066),
                (974, 1065),
                (980, 1067),
                (975, 1064),
                (995, 1063),
                (979, 1068),
                (1035, 1078),
                (1012, 1076)
            )
        )

        lip_up_array = mouth_group.create_part(
            FaceHandleArrayGuide,
            root_name='lip_up',
            side='center',
            size=size*0.5,
            mirror=True,
            vertices=get_vertices(
                mob_head,
                (1278, 1283),
                (989, 1054),
                (982, 1052),
                (993, 1053),
                (983, 1050),
                (1015, 1051),
                (997, 1055),
                (1042, 1079),
                (1047, 1077),
                (984, 1075)
            )
        )


        left_cheek_group = guide.create_part(
                PartGroupGuide,
                root_name='cheek',
                side='left',
                size=size
            )


        left_cheek_up_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_up',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                144, 152, 151, 153, 155, 531, 147, 210
            )
        )

        left_cheek_mid_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_mid',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                861, 872, 870, 131, 130, 533, 146, 208
            )
        )

        left_cheek_front_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_front',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                887, 885, 881, 819, 922, 917, 947, 936, 1031, 949, 378, 171
            )
        )

        left_cheek_a_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_a',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                575, 444, 589, 786, 376, 375, 373
            )
        )

        left_cheek_b_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_b',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                577, 446, 479, 578, 520
            )
        )

        left_cheek_c_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_c',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                534, 535, 537, 574, 298
            )
        )

        left_cheek_d_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_d',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                483, 482, 481, 196
            )
        )

        left_cheek_e_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_e',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                395, 447, 476
            )
        )

        left_cheek_f_array = left_cheek_group.create_part(
            FaceHandleArrayGuide,
            root_name='cheek_f',
            side='left',
            size=size,
            vertices=get_vertices(
                mob_head,
                569, 567, 565
            )
        )

        right_cheek_group = controller.mirror_part(left_cheek_group)


        left_lid_group = guide.create_part(
                PartGroupGuide,
                root_name='lid',
                side='left',
                size=size
            )

        left_up_lid_group = left_lid_group.create_part(
                PartGroupGuide,
                root_name='lid_up',
                side='left',
                size=size
            )

        left_down_lid_group = left_lid_group.create_part(
                PartGroupGuide,
                root_name='lid_down',
                side='left',
                size=size
            )

        brow_mid_array = brow_group.create_part(
            FaceHandleArrayGuide,
            root_name='brow_mid',
            side='center',
            mirror=True,
            size=size,
            vertices=get_vertices(
                mob_head,
                (1295, 1294),
                (42, 53),
                (50, 51),
                (73, 74),
                (27, 46),
                (26, 47),
                (24, 49),
                214
            )
        )


        brow_up_array = brow_group.create_part(
            FaceHandleArrayGuide,
            root_name='brow_up',
            side='center',
            mirror=True,
            size=size,
            vertices=get_vertices(
                mob_head,
                1297, 54, 76, 61, 62, 64, 449
            )
        )
        brow_head_array = brow_group.create_part(
            FaceHandleArrayGuide,
            root_name='brow_head',
            side='center',
            mirror=True,
            size=size,
            vertices=get_vertices(
                mob_head,
                1300, 36, 37, 39, 41, 439
            )
        )


        brow_down_array = brow_group.create_part(
            FaceHandleArrayGuide,
            root_name='brow_down',
            side='center',
            mirror=True,
            size=size,
            vertices=get_vertices(
                mob_head,
                1292, 44, 20, 71, 15, 17, 18, 216
            )
        )



        left_lid_up_a_array = left_up_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_up_a',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                329, 331, 332, 333, 334, 336, 350, 386
            )
        )

        left_lid_up_b_array = left_up_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_up_b',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                750, 751, 752, 753, 754, 755, 756, 757, 758, 773, 774, 775, 776, 777, 778, 779
            )
        )

        left_lid_up_c_array = left_up_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_up_c',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                1102, 1103, 1104, 1105, 1106, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131
            )
        )

        left_lid_down_a_array = left_down_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_down_a',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                133, 135, 136, 275, 326, 337, 339, 528
            )
        )

        left_lid_down_b_array = left_down_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_down_b',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772
            )
        )

        left_lid_down_c_array = left_down_lid_group.create_part(
            FaceHandleArrayGuide,
            root_name='lid_down_c',
            side='left',
            size=size*0.5,
            vertices=get_vertices(
                mob_head,
                1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120
            )
        )


        right_lid_group = controller.mirror_part(left_lid_group)


        controller.dg_dirty()


def get_vertices(mesh, *indices):
    vertices = []
    for x in indices:
        if isinstance(x, int):
            vertices.append(mesh.get_vertex_data(x))
        elif isinstance(x, (list, set, tuple)):
            vertices.append(mesh.get_vertex_data(*x))
        else:
            raise TypeError('Invalid index type %s' % type(x))
    return vertices
