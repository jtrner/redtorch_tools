import os
import json
import PySignal
import rig_factory.utilities.face_utilities.face_utilities as ftl
from rig_factory.controllers.blendshape_controller import BlendshapeController
from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects import FaceNetwork
from rig_factory.controllers.sdk_controller import SDKController


class FaceController(BlendshapeController, SDKController):

    face_network_about_to_change_signal = PySignal.ClassSignal()
    face_network_finished_change_signal = PySignal.ClassSignal()
    face_group_changed_signal = PySignal.ClassSignal()
    face_group_created_signal = PySignal.ClassSignal()
    face_target_created_signal = PySignal.ClassSignal()
    face_group_about_to_be_deleted_signal = PySignal.ClassSignal()
    face_target_about_to_be_deleted_signal = PySignal.ClassSignal()
    face_warning_signal = PySignal.ClassSignal()
    face_groups_selected_signal = PySignal.ClassSignal()
    face_groups_deselected_signal = PySignal.ClassSignal()
    face_targets_selected_signal = PySignal.ClassSignal()
    face_targets_deselected_signal = PySignal.ClassSignal()

    face_progress_signal = PySignal.ClassSignal()

    def __init__(self):
        super(FaceController, self).__init__()
        self.locked_face_drivers = False
        self.face_network = None

    def deserialize_object(self, data, namespace=None):
        this = super(FaceController, self).deserialize_object(data, namespace=namespace)
        if isinstance(this, FaceNetwork):
            self.face_network = this
        return this

    def deserialize_properties(self, *args):
        for x in super(FaceController, self).deserialize_properties(*args):
            if isinstance(x, FaceNetwork):
                self.set_face_network(x)
            yield x

    def set_face_network(self, face_network):
        if not isinstance(face_network, FaceNetwork) and face_network is not None:
            raise Exception('Invalid type "%s"' % type(face_network))
        self.face_network_about_to_change_signal.emit()
        self.face_network = face_network
        self.face_network_finished_change_signal.emit(face_network)

    def set_face_group(self, face_group):
        if not isinstance(face_group, FaceGroup) and face_group is not None:
            raise Exception('Invalid type "%s"' % type(face_group))
        self.face_group_changed_signal.emit(face_group)

    def reset(self, *args):
        super(BlendshapeController, self).reset(*args)
        self.set_face_network(None)

    def create_network_from_handles(self, *handles, **kwargs):
        return ftl.create_network_from_handles(
            *handles,
            **kwargs
        )

    def create_from_face_network_data(self, data, target_namespace='face_blueprint', selected_handles=None):
        return ftl.create_from_face_network_data(
            self,
            data,
            target_namespace=target_namespace,
            selected_handles=selected_handles
        )

    def import_face(self, file_name, selected_handles=False):
        """
        Imports Alembic if exists
        Creates Face Network with json data
        Deletes Alembic objects
        """
        name_space = 'face_build'
        alembic_path = file_name.replace('.json', '.abc')
        if os.path.exists(alembic_path):
            if not self.scene.namespace(exists=':%s' % name_space):
                self.scene.namespace(add=name_space)
                self.scene.namespace(set=name_space)
            self.scene.AbcImport(alembic_path)
            self.scene.namespace(set=':')
        with open(file_name, mode='r') as f:
            face_network = self.create_from_face_network_data(
                json.loads(f.read()),
                target_namespace=name_space,
                selected_handles=selected_handles
            )
            self.set_face_network(face_network)

        self.scene.delete(self.scene.ls('%s:*' % name_space))
        if self.scene.namespace(exists=':%s' % name_space):
            self.scene.namespace(rm=name_space, mergeNamespaceWithRoot=True)
        return face_network

    def update_target_handles(self, face_target):
        ftl.update_target_handles(face_target)

    def update_target_selected_mesh(self, face_target, relative=True):
        ftl.update_target_selected_mesh(face_target, relative=relative)

    def update_target_meshs(self, face_target, meshs):
        ftl.update_target_meshs(face_target, meshs)

    def get_face_network_data(self, *args, **kwargs):
        return ftl.get_face_network_data(*args, **kwargs)

    def update_keyframe_group(self, face_target, isolate=True):
        if isinstance(face_target, FaceTarget):
            face_target.face_group.face_network.consolidate_handle_positions()
            super(FaceController, self).update_keyframe_group(face_target.keyframe_group, isolate=isolate)
        else:
            raise Exception('Invalid type "%s"' % type(face_target))

    """
    TODO: Move all functions below this point to FaceNetwork class
    """


    def set_face_plug_limits(self):
        for group in self.face_network.face_groups:
            driver_plug = group.driver_plug
            sorted_values = sorted([x.driver_value for x in group.face_targets])
            #import maya.cmds as mc
            #driver_node = driver_plug.get_node().get_selection_string()
            #if driver_plug.name in ['translateX', 'tx']:
            #    mc.transformLimits(
            #        driver_node,
            #        tx=[sorted_values[0],  sorted_values[-1]],
            #        etx=[True, True]
            #    )
            #if driver_plug.name in ['translateY', 'ty']:
            #    mc.transformLimits(
            #        driver_node,
            #        ty=[sorted_values[0],  sorted_values[-1]],
            #        ety=[True, True]
            #    )
            #if driver_plug.name in ['translateZ', 'tx']:
            #    mc.transformLimits(
            #        driver_node,
            #        tz=[sorted_values[0],  sorted_values[-1]],
            #        etz=[True, True]
            #    )

    def prune_driven_curves(self, range_threshold=0.0001):
        ftl.prune_driven_curves(
            self,
            range_threshold=range_threshold
        )

    def prune_driven_keys(self, range_threshold=0.0001):
        ftl.prune_driven_keys(
            self,
            range_threshold=range_threshold
        )

    def bake_shards(self):
        ftl.bake_shards(self)

    def mirror_face_groups(self, face_network, **kwargs):
        return ftl.mirror_face_groups(
            face_network,
            **kwargs
        )


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))

    #os.system('start %s' % file_name)
