import json
import os
import sys
from inspect import getmembers, isfunction
from rig_factory.objects.biped_objects.jaw import Jaw
from rig_factory.objects.face_objects.face import Face
from rig_factory.objects.face_network_objects import FaceNetwork
from rig_math.vector import Vector
import maya.cmds as mc
namespace = 'face_recycle'

def recycle(controller, data_path):

    """
    This is messy business because Elena has no standardization
    """
    rig_root = controller.root

    with open(data_path, mode='r') as f:
        data = json.loads(f.read())

    if rig_root:
        for x in recycle_rig(
            rig_root,
            data
        ):
            yield x
    else:
        for x in recycle_blendshape(
            controller,
            data
        ):
            yield x


def get_base_meshs(controller):

    if os.environ['TT_PROJCODE'] == 'EAV':
        if mc.objExists('shape_link'):
            get_blendshapes = mc.listConnections(
                'shape_link',
                d=True,
                s=False,
                type='blendShape'
            )
            if not get_blendshapes:
                raise Exception('no blendshapes found')
            get_blendshape = list(set(get_blendshapes))
            geometry = []
            for blendshape in get_blendshape:
                get_geometry = mc.blendShape(
                    blendshape,
                    q=True,
                    g=True
                    )
                if get_geometry:
                    geometry.extend(get_geometry)
            return geometry

        else:
            raise Exception('shape_link did not exist')
    else:
        selected_mesh_names = controller.get_selected_mesh_names()
        print selected_mesh_names


def get_blendshape(mesh):
    blendshapes = [x for x in mc.listHistory(mesh) if mc.nodeType(x) == 'blendShape']
    if blendshapes:
        return blendshapes[0]


def duplicate_meshs(meshs, tag):
    top_group = mc.createNode('transform', name='%s_geometry_gp' % tag)
    new_meshs = []
    for mesh in meshs:
        duplicate_geo = mc.duplicate(mesh, name='%s_%s' % (tag, mesh.replace('Shape', '')))
        mc.parent(duplicate_geo, top_group)
        duplicate_mesh = mc.listRelatives(duplicate_geo, c=True, type='mesh')[0]
        new_meshs.append(duplicate_mesh)
    return top_group, new_meshs


def recycle_blendshape(controller, data):

    for x in mc.lsUI(windows=True):
        if x not in ['ConsoleWindow', 'MayaWindow', 'ColorEditor']:
            mc.deleteUI(x)

    reference_geometry = get_base_meshs(controller)

    controller.face_progress_signal.emit(
        message='Recycling Face',
        maximum=len(data['face_groups']),
        value=0
    )

    base_group, base_geometry = duplicate_meshs(reference_geometry, 'recycle_base')
    face_network = controller.create_object(
        FaceNetwork,
        *base_geometry,
        root_name='face'
    )

    new_blendshape_name = face_network.blendshape.get_selection_string()

    old_blendshapes = []
    #for reference_mesh in reference_geometry:
    #    reference_blendshapes = [x for x in mc.listHistory(reference_mesh) if mc.nodeType(x) == 'blendShape' and x != new_blendshape_name]
    #    if reference_blendshapes:
    #        old_blendshapes.append(reference_blendshapes[0])
    #        print new_blendshape_name, reference_blendshapes[-1], reference_mesh
    #        controller.scene.reorderDeformers(
    #            new_blendshape_name,
    #            reference_blendshapes[-1],
    #            reference_mesh
    #        )

    for g, face_group_data in enumerate(data['face_groups']):
        controller.face_progress_signal.emit(
            message='Creating:\n %s' % (
                face_group_data['name'].title()
            ),
            value=g
        )
        node_name, plug_name = face_group_data['driver_plug'].split('.')

        if controller.scene.objExists(node_name):

            driver_plug = controller.initialize_node(node_name, parent=face_network).plugs[plug_name]
            name = face_group_data['name']
            original_value = round(driver_plug.get_value())
            incoming_plugs = mc.listConnections(driver_plug, s=True, d=False, scn=True, p=True)
            if incoming_plugs:
                mc.disconnectAttr(incoming_plugs[0], driver_plug)
            driver_plug.set_value(0.0)

            face_group = controller.face_network.create_group(
                driver_plug=driver_plug,
                pretty_name=name,
                root_name=name
            )
            for driver_value in face_group_data['driver_values']:
                rounded_value = round(driver_value, 3)
                driver_plug.set_value(rounded_value)

                [mc.setAttr('%s.envelope' % x, 1.0) for x in old_blendshapes]
                face_network.blendshape.plugs['envelope'].set_value(0.0)
                target_group, target_geometry = duplicate_meshs(
                    reference_geometry,
                    'target'
                 )

                [mc.setAttr('%s.envelope' % x, 0.0) for x in old_blendshapes]

                face_group.create_face_target(
                    *target_geometry,
                    driver_value=rounded_value
                )
                [mc.setAttr('%s.envelope' % x, 1.0) for x in old_blendshapes]
                face_network.blendshape.plugs['envelope'].set_value(1.0)

                mc.delete(target_group)

            driver_plug.set_value(original_value)
            if incoming_plugs:
                mc.connectAttr(incoming_plugs[0], driver_plug)
            for group in face_network.face_groups:
                try:
                    group.driver_plug.set_value(group.initial_value)
                except Exception, e:
                    print e.message
        yield g
    if old_blendshapes:
        mc.delete(old_blendshapes)

    controller.face_progress_signal.emit()


def recycle_rig(root, data):

    for x in mc.lsUI(windows=True):
        if x not in ['ConsoleWindow', 'MayaWindow', 'ColorEditor']:
            mc.deleteUI(x)
    controller = root.controller
    reference_mesh = get_base_meshs()[0]
    face_network = controller.face_network
    if not face_network:
        face_network = controller.create_network_from_handles(root)
    jaw_group = None
    jaw_vertices = None
    face_rig = None
    jaw_handle = None
    for part in root.get_parts():
        if isinstance(part, Jaw):
            jaw_handle = part.handles[1]
            jaw_vertices = part.guide_vertices
            jaw_group = jaw_handle.groups[-1]
        if isinstance(part, Face):
            face_rig = part
    controller.face_progress_signal.emit(
        message='Recycling Face',
        maximum=len(data['face_groups']),
        value=0
    )
    current_group = 0
    if jaw_handle:
        face_network.add_driven_handle(
            jaw_handle.get_selection_string(),
            root_name='%s_driven' % jaw_handle.root_name,
            index=jaw_handle.index,
            attributes=['rx', 'ry', 'rz']
        )
    for face_group_data in data['face_groups']:
        controller.refresh()
        controller.face_progress_signal.emit(
            message='Creating:\n %s' % (
                face_group_data['name'].title()
            ),
            value=current_group
        )
        current_group += 1
        node_name, plug_name = face_group_data['driver_plug'].split('.')
        if controller.scene.objExists(node_name):
            driver_plug = controller.initialize_node(node_name, parent=face_network).plugs[plug_name]
            name = face_group_data['name']
            original_value = round(driver_plug.get_value())
            incoming_plugs = mc.listConnections(driver_plug, s=True, d=False, scn=True, p=True)
            if incoming_plugs:
                mc.disconnectAttr(incoming_plugs[0], driver_plug)
            driver_plug.set_value(0.0)
            face_group = controller.face_network.create_group(
                driver_plug=driver_plug,
                pretty_name=name,
                root_name=name
            )
            for driver_value in face_group_data['driver_values']:
                rounded_value = round(driver_value, 3)
                driver_plug.set_value(rounded_value)
                if jaw_vertices:
                    positions = []
                    for jv in jaw_vertices:
                        if jv:
                            positions.append(Vector(controller.get_bounding_box_center(
                                ['%s.vtx[%s]' % (reference_mesh, y[-1]) for y in jv]
                            )))
                    z_vector = positions[2] - positions[0]
                    y_vector = positions[1] - positions[0]
                    x_vector = z_vector.cross_product(y_vector)
                    z_vector = x_vector.cross_product(y_vector)
                    jaw_matrix = []
                    jaw_matrix.extend(x_vector.normalize().data)
                    jaw_matrix.append(0.0)
                    jaw_matrix.extend(y_vector.normalize().data)
                    jaw_matrix.append(0.0)
                    jaw_matrix.extend(z_vector.normalize().data)
                    jaw_matrix.append(0.0)
                    jaw_matrix.extend(positions[0].data)
                    jaw_matrix.append(1.0)
                    mc.xform(jaw_group, m=jaw_matrix, ws=True)

                face_group.create_face_target(
                    reference_mesh,
                    driver_value=rounded_value
                )

            driver_plug.set_value(original_value)
            if incoming_plugs:
                mc.connectAttr(incoming_plugs[0], driver_plug)
            for group in face_network.face_groups:
                try:
                    group.driver_plug.set_value(group.initial_value)
                except Exception, e:
                    print e.message


    # Connect Tongue shapes

    tongue_handle_names = [
        #'C_fk_tongue_b_Ctrl',
        #'C_fk_tongue_c_Ctrl',
        'C_fk_tongue_d_Ctrl',
        'C_fk_tongue_e_Ctrl',
        'C_fk_tongue_f_Ctrl',
        'C_fk_tongue_g_Ctrl'
    ]

    if all([controller.scene.objExists(x) for x in tongue_handle_names]):
        for tongue_handle_name in tongue_handle_names:
            face_network.add_driven_handle(
                tongue_handle_name,
                attributes=['rx', 'ry', 'rz']
            )

        tongue_control = controller.initialize_node('TGBase_ctrl', parent=face_network)

        # Tongue Vertical

        translate_y_plug = tongue_control.plugs['ty']
        tongue_vertical_group = face_network.create_group(
            driver_plug=translate_y_plug,
            root_name='tongue_vertical'
        )
        for handle_name in tongue_handle_names:
            mc.setAttr('%s.rx' % handle_name, -45.0)
        tongue_vertical_group.create_face_target(
            driver_value=1.0
        )
        translate_y_plug.set_value(0.0)
        for handle_name in tongue_handle_names:
            mc.setAttr('%s.rx' % handle_name, 45.0)
        tongue_vertical_group.create_face_target(
            driver_value=-1.0
        )
        translate_y_plug.set_value(0.0)

        # Tongue Horizontal
        translate_x_plug = tongue_control.plugs['tx']
        tongue_horizontal_group = face_network.create_group(
            driver_plug=translate_x_plug,
            root_name='tongue_horizontal'
        )
        for handle_name in tongue_handle_names:
            mc.setAttr('%s.rz' % handle_name, -45.0)
        tongue_horizontal_group.create_face_target(
            driver_value=1.0
        )
        translate_x_plug.set_value(0.0)

        for handle_name in tongue_handle_names:
            mc.setAttr('%s.rz' % handle_name, 45.0)
        tongue_horizontal_group.create_face_target(
            driver_value=-1.0
        )
        translate_x_plug.set_value(0.0)

        if mc.objExists('Xtra_Face_Ctrls'):
            mc.delete('Xtra_Face_Ctrls')

    # Deformations on the base mesh should now be handled by the face system
    mc.delete(reference_mesh, ch=True)

    # Connect new face rig to base mesh of old face system
    mc.connectAttr('%s.outMesh' % face_network.geometry[0], '%s.inMesh' % reference_mesh)

    if face_rig and mc.objExists('Head_Ctrl'):
        mc.parent(face_rig, 'Head_Ctrl')

    post_script_path = 'Y:/%s/assets/type/Character/%s/elems/Pipeline/post_scripts/recycle_post_script.py' % (
        os.environ['TT_PROJCODE'],
        os.environ['TT_ENTNAME']
    )
    if os.path.exists(post_script_path):
        post_script_directory = os.path.dirname(post_script_path)
        sys.path.append(post_script_directory)
        module = __import__('recycle_post_script')
        for function in [o[1] for o in getmembers(module) if isfunction(o[1])]:
            function(controller)

    #if mc.objExists('body') and mc.objExists('Utility_Grp'):
    #    mc.parent('body', 'Utility_Grp')

    #if blendshapes:
    #    mc.delete(blendshapes[0])
    controller.face_progress_signal.emit()


