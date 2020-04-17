from rig_factory.objects.blendshape_objects.blendshape import BlendshapeInbetween
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_math.utilities as rmu
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
import rig_factory


class FaceTarget(Transform):

    attribute_values = DataProperty(
        name='attribute_values'
    )
    driver_value = DataProperty(
        name='driver_value'
    )
    face_group = ObjectProperty(
        name='face_group'
    )
    keyframe_group = ObjectProperty(
        name='keyframe_group'
    )
    blendshape_inbetween = ObjectProperty(
        name='blendshape_inbetween'
    )
    target_meshs = ObjectListProperty(
        name='target_meshs'
    )
    deformed_meshs = ObjectListProperty(
        name='deformed_meshs'
    )
    result_meshs = ObjectListProperty(
        name='result_meshs'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        geometry = list(kwargs.pop('geometry', []))
        face_group = kwargs.pop('face_group', None)
        root_name = kwargs.get('root_name', None)
        snap_to_mesh = kwargs.get('snap_to_mesh', None)

        if not root_name:
            if face_group.index is None:
                kwargs['root_name'] = face_group.root_name
            else:
                kwargs['root_name'] = '%s_%s' % (face_group.root_name, rig_factory.index_dictionary[face_group.index])
        if not face_group:
            raise Exception('You must provide a "face_group" keyword argument')
        driver_value = round(kwargs.get('driver_value', 0.0), 3)
        if driver_value in [x.driver_value for x in face_group.face_targets]:
            raise Exception(
                'A face target with the driver value "%s" already exists' % driver_value
            )
        if not isinstance(driver_value, float):
            raise Exception(
                'you must provide a "driver_value" keyword argument of type(float) to create a %s' % Plug
            )

        face_network = face_group.face_network
        kwargs.setdefault(
            'index',
            face_group.get_next_avaliable_index()
        )
        kwargs['side'] = face_group.side
        kwargs['face_group'] = face_group
        kwargs['driver_value'] = driver_value
        if controller.locked_face_drivers:
            kwargs['attribute_values'] = face_network.get_altered_driver_values()

        kwargs.setdefault('parent', face_group)

        if geometry and snap_to_mesh:
            face_network.snap_to_mesh(*list(geometry))
        face_network.consolidate_handle_positions()
        controller.start_ownership_signal.emit(
            None,
            face_group
        )
        this = super(FaceTarget, cls).create(
            controller,
            **kwargs
        )

        face_group.face_targets.append(this)
        controller.end_ownership_signal.emit(
            this,
            face_group
        )
        sdk_group = face_group.sdk_group

        if sdk_group:
            this.keyframe_group = sdk_group.create_keyframe_group(
                in_value=driver_value,
                isolate=True,
                parent=this
            )
            controller.dg_dirty()

        if geometry:
            this.create_blendshape_inbetween(*geometry)

        return this

    def create_blendshape_inbetween(self, *geometry):

        controller = self.controller
        face_group = self.face_group
        face_network = face_group.face_network
        blendshape = face_network.blendshape
        blendshape_group = face_group.blendshape_group

        if not blendshape:
            raise Exception('The FaceNetwork has no blendshape')
        if not blendshape_group:
            raise Exception('The FaceGroup has no blendshape group')
        if not geometry:
            if not face_network.geometry:
                raise Exception('The FaceNetwork had no base geometry set')
            else:
                geometry = face_network.geometry
        driver_value = self.driver_value

        blendshape_group = face_group.blendshape_group
        if blendshape_group and driver_value != 0.0:
            blendshape = blendshape_group.blendshape

            targets = create_target_geometry(self, *geometry)
            controller.disconnnect_targets(blendshape_group)
            index = self.index
            root_name = blendshape_group.root_name
            controller.start_ownership_signal.emit(
                None,
                blendshape_group
            )

            blendshape_inbetween = controller.create_object(
                BlendshapeInbetween,
                index=index,
                root_name=root_name,
                parent=face_group.blendshape_group
            )

            blendshape_inbetween.blendshape_group = blendshape_group
            blendshape_group.blendshape_inbetweens.append(blendshape_inbetween)
            controller.end_ownership_signal.emit(
                blendshape_inbetween,
                blendshape_group
            )
            self.blendshape_inbetween = blendshape_inbetween
            controller.register_item(blendshape_inbetween)
            for g in range(len(blendshape.base_geometry)):
                blendshape_inbetween.create_blendshape_target(
                    targets[g]
                )
            min_driver_value, min_weight, max_driver_value, max_weight = face_group.calculate_driver_values()
            for face_target in face_group.face_targets:
                if face_target.driver_value != 0.0:
                    if face_target.blendshape_inbetween:
                        if face_target.driver_value > 0.0:
                            weight = rmu.remap_value(
                                face_target.driver_value,
                                0.0,
                                max_driver_value,
                                0.0,
                                1.0
                            )
                        else:
                            weight = rmu.remap_value(
                                face_target.driver_value,
                                min_driver_value,
                                0.0,
                                -1.0,
                                0.0
                            )
                        weight = round(weight, 3)
                        face_target.blendshape_inbetween.weight = weight
            controller.connect_targets(blendshape_group)
            face_group.create_driver_curve()
            for mesh in blendshape.base_geometry:
                mesh.redraw()

    def __init__(self, **kwargs):
        super(FaceTarget, self).__init__(**kwargs)
        self.controller.face_target_created_signal.emit(self)

    def teardown(self):
        nodes_to_delete = WeakList()
        if self.keyframe_group:
            nodes_to_delete.append(self.keyframe_group)
        if self.blendshape_inbetween:
            nodes_to_delete.append(self.blendshape_inbetween)
        self.controller.delete_objects(
            nodes_to_delete,
            collect=self.controller.garbage_collection
        )
        face_group = self.face_group
        self.controller.start_disown_signal.emit(self, face_group)
        face_group.face_targets.remove(self)
        self.face_group = None
        self.controller.end_disown_signal.emit(self, face_group)
        #face_group.create_driver_curve()
        #face_group.controller.face_group_changed_signal.emit(face_group)
        super(FaceTarget, self).teardown()


def create_target_geometry(face_target, *geometry):

    """
    Builds blendshape Corrective target geometry

    :param face_target:
    :param geometry:  Mesh shapes
    :return:
    """

    if isinstance(face_target, FaceTarget):
        face_group = face_target.face_group
        face_network = face_group.face_network
        blendshape = face_network.blendshape
        blendshape_group = face_group.blendshape_group
        if face_target.driver_value == 0.0:
            raise Exception('Cannot create_face_target_geometry with driver value of 0.0')
        if not blendshape_group:
            raise Exception('blendshape_group not found')
        controller = face_target.controller
        similar_geometry = dict()
        for input_geo in geometry:
            similar_mesh = controller.find_similar_mesh(input_geo, blendshape.base_geometry)
            if similar_mesh:
                similar_geometry[similar_mesh.name] = input_geo
            else:
                raise Exception('No similar geometry fornd for : %s' % input_geo)
        face_group = face_target.face_group
        face_network = face_group.face_network
        blendshape_group_index = blendshape_group.index
        main_group = controller.create_object(
            Transform,
            root_name=face_group.root_name,
            parent=face_target,
            side=face_target.side,
            index=face_target.index,
        )
        connections = controller.listConnections(
            face_group.driver_plug,
            s=True,
            d=False,
            p=True,
            scn=True
        )
        if connections:
            controller.disconnectAttr(connections[0], face_group.driver_plug)
        face_group.driver_plug.set_value(face_target.driver_value)
        for g in range(len(face_network.geometry)):
            base_geometry = face_network.geometry[g]
            target_base_name = '%s_%s' % (
                face_target.root_name,
                rig_factory.index_dictionary[face_target.index]
            )
            target_parent = main_group.create_child(
                Transform,
                root_name='%s_target' % target_base_name,
                index=g,
                side=face_target.side
            )
            deformed_parent = main_group.create_child(
                Transform,
                root_name='%s_deform' % target_base_name,
                index=g,
                side=face_target.side

            )
            result_parent = main_group.create_child(
                Transform,
                root_name='%s_result' % target_base_name,
                index=g,
                side=face_target.side
            )
            result_mesh = controller.copy_mesh(
                face_network.base_geometry[g].get_selection_string(),
                result_parent
            )
            weight_plug = face_group.blendshape_group.get_weight_plug()
            weight_value = weight_plug.get_value()
            face_group.driver_plug.set_value(face_target.driver_value)
            base_geometry_name = base_geometry.get_selection_string()
            if base_geometry.name in similar_geometry:
                input_mesh = similar_geometry[base_geometry.name]
                geo_name = str(input_mesh)
                existing_geometry = controller.scene.ls(geo_name)
                if len(existing_geometry) > 1:
                    raise Exception('Duplicate geometry name : "%s"' % geo_name)
                target_mesh = controller.copy_mesh(
                    geo_name,
                    target_parent
                )
                weight_plug.set_value(0.0)
                deform_mesh = controller.copy_mesh(
                    base_geometry_name,
                    deformed_parent
                )
            else:
                target_mesh = controller.copy_mesh(
                    base_geometry_name,
                    target_parent
                )
                weight_plug.set_value(0.0)
                deform_mesh = controller.copy_mesh(
                    base_geometry_name,
                    deformed_parent
                )
            weight_plug.set_value(weight_value)
            difference_blendshape = controller.create_blendshape(
                result_mesh,
                parent=result_mesh,
                root_name='%s_%s_difference' % (g, main_group.root_name),
                side=face_target.side,
                index=face_target.index
            )
            difference_target_group = difference_blendshape.create_group(
                target_mesh,
                root_name='%s_%s_target' % (g, main_group.root_name),
                side=face_target.side
            )
            difference_deform_group = difference_blendshape.create_group(
                deform_mesh,
                root_name='%s_%s_deform' % (g, main_group.root_name),
                side=face_target.side
            )
            difference_target_group.get_weight_plug().set_value(1.0)
            difference_deform_group.get_weight_plug().set_value(-1.0)
            face_target.target_meshs.append(target_mesh)
            face_target.deformed_meshs.append(deform_mesh)
            face_target.result_meshs.append(result_mesh)
            controller.assign_shading_group(
                face_network.sculpt_shader.shading_group,
                target_mesh
            )
            result_parent.plugs['v'].set_value(False)
            deformed_parent.plugs['v'].set_value(False)
        if connections:
            controller.connectAttr(connections[0], face_group.driver_plug)
        bounding_box = controller.get_bounding_box([x.get_selection_string() for x in face_network.base_geometry])
        top = bounding_box[4]
        bottom = bounding_box[1]
        left = bounding_box[0]
        right = bounding_box[3]
        if right - left < 0.01:
            raise Exception('Mesh is too tiny!')
        x_spacing = 0.1
        y_spacing = 0.1
        x_position = (right - left + x_spacing) * (blendshape_group_index + 1)
        y_position = (top - bottom + y_spacing) * face_target.index
        main_group.plugs['tx'].set_value(x_position)
        main_group.plugs['ty'].set_value(y_position)
        return face_target.result_meshs

    else:
        raise Exception('Cannot create_face_group_geometry on a %s' % type(face_target))
