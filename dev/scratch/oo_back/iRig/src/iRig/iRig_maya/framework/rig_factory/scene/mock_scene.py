import PySignal
import string
import random


class MockScene(object):

    pre_file_new_or_opened_signal = PySignal.ClassSignal()
    selection_changed_signal = PySignal.ClassSignal()
    after_save_signal = PySignal.ClassSignal()
    before_save_signal = PySignal.ClassSignal()
    after_open_signal = PySignal.ClassSignal()

    tangents = {
        'auto': None,
        'clamped': None,
        'fast': None,
        'fixed': None,
        'flat': None,
        'global': None,
        'linear': None,
        'plateau': None,
        'slow': None,
        'smooth': None,
        'step': None,
        'step_next': None,
    }

    curve_types = {
        'time_to_angular': None,
        'time_to_linear': None,
        'time_to_time': None,
        'time_to_unitless': None,
        'unitless_to_angular': None,
        'unitless_to_linear': None,
        'unitless_to_time': None,
        'unitless_to_unitless': None,
        'unknown': None
    }

    infinity_types = {
        'constant': None,
        'linear': None,
        'cycle': None,
        'cycle_relative': None,
        'oscilate': None,

    }

    maya_version = 0.0
    mock_selection_list = []

    def __init__(self):
        super(MockScene, self).__init__()
        self.standalone = False
        self.mock = True

    def flip_blendshape_weights(self, *args, **kwargs):
        pass

    @staticmethod
    def get_file_info():
        pass

    @staticmethod
    def update_file_info(**kwargs):
        pass

    def create_dag_node(self, *args):
        pass

    def create_depend_node(self, *args):
        pass

    def create_keyframe(self, curve, *args):
        pass

    def create_ik_handle(self, start_joint, end_effector, solver='ikSCsolver', name=None, parent=None):
        pass

    def create_transform(self, *args, **kwargs):
        pass

    def create_constraint(self, constraint_type, *transforms, **kwargs):
        pass

    @staticmethod
    def draw_nurbs_curve(positions, degree, form, name, parent):
        pass

    def create_shader(self, node_type, name):
        pass

    def create_shading_group(self, name):
        pass

    def connect_plugs(self, plug_1, plug_2):
        pass

    def disconnect_plugs(self, plug_1, plug_2):
        pass

    def namespace(self, *args, **kwargs):
        pass

    def AbcImport(self, path):
        pass

    def AbcExport(self, path, *roots):
        pass

    def objExists(self, *args, **kwargs):
        return True

    def get_bounding_box_center(self, *nodes):
        return [0.0, 0.0, 0.0]

    def get_selection_string(self, item):
        return create_random_string(33)

    def select(self, *items, **kwargs):
        if kwargs.get('cl', None) or kwargs.get('clear', None):
            self.mock_selection_list = []
        elif kwargs.get('r', None) or kwargs.get('replace', None):
            self.mock_selection_list = [str(x) for x in items]
        else:
            self.mock_selection_list.extend([str(x) for x in items])

    def reorderDeformers(self, *args, **kwargs):
        pass

    def reorder_deformers_by_type(self, *args, **kwarsg):
        pass

    def copy_mesh(self, *args, **kwargs):
        pass

    def get_selected_attribute_names(self):
        pass

    def get_selected_nodes(self):
        return []

    def initialize_plug(self, owner, key):
        pass

    def create_animation_curve(self, *args, **kwargs):
        pass

    def delete_connection(self, connection):
        pass

    def delete_object(self, item):
        pass

    def get_plug_locked(self, plug):
        pass

    def set_plug_locked(self, plug, value):
        pass

    def get_plug_hidden(self, plug):
        pass

    def set_plug_hidden(self, plug, value):
        pass

    def set_plug_value(self, plug, value):
        pass

    def get_plug_value(self, plug, *args):
        if args:
            return args[0]
        else:
            return 1.0

    def unparent(self, child):
        pass

    def parent(self, *args, **kwargs):
        pass

    def rename(self, node, name):
        pass

    def create_plug(self, owner, key, **kwargs):
        pass

    def get_m_object(self, node_name):
        pass

    def get_m_object_type(self, m_object):
        pass

    def is_dag_node(self, m_object):
        pass

    def xform(self, *args, **kwargs):
        if 'q' in kwargs or 'query' in kwargs:
            if any([x in kwargs for x in ['matrix', 'm']]):
                return (
                    1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0
                )
            if any([x in kwargs for x in ['translate', 'rotate', 'scale', 't', 'ro', 's']]):
                return (
                    0.0, 0.0, 0.0
                )

    def assign_shading_group(self, shading_group, *nodes):
        pass

    def listAttr(self, *args, **kwargs):
        return

    def plug_exists(self, node, plug_name):
        pass

    def delete_plug(self, plug):
        pass

    def new_scene(self):
        pass

    def file(self, *args, **kwargs):
        pass

    def get_curve_data(self, node):
        pass

    def listRelatives(self, *args, **kwargs):
        return [create_random_string(12) for x in range(3)]

    def list_selected_vertices(self):
        pass

    def polyListComponentConversion(self, *args, **kwargs):
        pass

    def get_selected_mesh_names(self):
        return ['Body_main_Geo_OriginShape']

    def get_selected_mesh_objects(self):
        return ['Body_main_Geo_OriginShape']

    def get_mesh_objects(self, object):
        pass

    def convert_selection(self, **kwargs):
        pass

    def get_selected_vertex_indices(self):
        pass

    def refresh(self):
        pass

    def dg_dirty(self):
        pass

    def lock_node(self, *nodes, **kwargs):
        pass

    def set_deformer_weights(self, m_deformer, weights):
        pass

    def get_deformer_weights(self, m_deformer):
        pass

    def create_nonlinear_deformer(self, deformer_type, geometry, **kwargs):
        pass

    def add_deformer_geometry(self, deformer, geometry):
        pass

    def remove_deformer_geometry(self, deformer, geometry):
        pass

    def delete(self, *args):
        pass

    def import_geometry(self, path):
        pass

    def lock_all_plugs(self):
        pass

    def find_skin_cluster(self, node):
        pass

    def get_skin_data(self, node):
        pass

    def create_from_skin_data(self, data):
        pass

    def get_skin_weights(self, node):
        pass

    def set_skin_weights(self, node, weights):
        pass

    def get_skin_influences(self, node):
        pass

    def set_skin_as(self, skin_cls=None, target_objects=""):
        pass

    def skinCluster(self, *args, **kwargs):
        pass

    def get_closest_vertex_index(self, mesh, position):
        pass

    def get_closest_face_index(self, mesh, position):
        pass

    def get_meshs(self, node_name):
        pass

    def create_shard_mesh(self, mesh_name, parent_m_object):
        pass

    def load_plugin(self, plugin_name):
        pass

    def getAttr(self, *args, **kwargs):
        pass

    def setAttr(self, *args, **kwargs):
        pass

    def ls(self, *args, **kwargs):
        if kwargs.get('sl', None) or kwargs.get('selected', None):
            return self.mock_selection_list

    def listConnections(self, *args, **kwargs):
        return [create_random_string(12) for x in range(3)]

    def create_blendshape_target(self, *args, **kwargs):
        pass

    def get_bounding_box(self, *args, **kwargs):
        return [-1.0, -1.0, -1.0, 1.0, 1.0, 1.0]

    def clear_blendshape_group_targets(self, *args, **kwargs):
        pass

    def create_blendshape(self, *args, **kwargs):
        pass

    def addAttr(self, *args, **kwargs):
        pass

    def sets(self, *args, **kwargs):
        pass

    def keyTangent(self, *args, **kwargs):
        pass

    def setKeyframe(self, *args, **kwargs):
        pass

    def parentConstraint(self, *args, **kwargs):
        pass

    def scaleConstraint(self, *args, **kwargs):
        pass

    def aimConstraint(self, *args, **kwargs):
        pass

    def disconnectAttr(self, *args, **kwargs):
        pass

    def connectAttr(self, *args, **kwargs):
        pass

    def create_driven_curve(self, *args, **kwargs):
        pass

    def set_xray_panel(self, *args, **kwargs):
        pass

    def create_ik_spline_handle(self, *args, **kwargs):
        pass

    def create_loft_ribbon(self, *args, **kwargs):
        pass

    def create_extrude_ribbon(self, *args, **kwargs):
        pass

    def create_text_curve(self, *args, **kwargs):
        return [None]

    def set_plug_keyable(self, *args, **kwargs):
        pass

    def change_keyframe(self, *args, **kwargs):
        pass

    def delete_unused_nodes(self, *args, **kwargs):
        pass

    def set_xray_joints_panel(self, *args, **kwargs):
        pass

    def create_lattice(self, *args, **kwargs):
        return [None, None, None, None, None, None]

    def create_wire_deformer(self, curve, *args, **kwargs):
        return [None, None, None, None]

    def rebuildSurface(self, *args, **kwargs):
        pass

    def get_selected_node_names(self, *args, **kwargs):
        return []

    def undoInfo(self, *args, **kwargs):
        pass

    def get_next_avaliable_plug_index(self, *args):
        return 0

    def selectKey(self, *args, **kwargs):
        pass

    def cutKey(self, *args, **kwargs):
        pass

    def create_curve_from_vertices(self, *args):
        pass

    def get_animation_curve_value_at_index(self, *args):
        return 0.0

    def select_keyframes(self, *args, **kwargs):
        pass

    def keyframe(self, *args, **kwargs):
        pass

    def deisolate(self, *args, **kwargs):
        pass

    def get_blendshape_weight_index_list(self, *args, **kwargs):
        return []

    def get_reverse_index_lists(self, *args, **kwargs):
        return []

    def create_mirrored_geometry(self, *args, **kwargs):
        return dict()

    def autoKeyframe(self, *args, **kwargs):
        pass

    def attributeQuery(self, *args, **kwargs):
        pass

    def get_constraint_data(self, *args, **kwargs):
        pass

def create_random_string(count):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(count))