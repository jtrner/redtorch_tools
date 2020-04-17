import traceback
import PySignal
import rig_factory.scene as scn
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.plug import Plug
from rig_math.matrix import Matrix
import rig_factory.utilities.node_utilities.node_utilities as ntl
import rig_factory.utilities.node_utilities.name_utilities as nal
from rig_factory.controllers.object_controller import ObjectController
import uuid


class NodeController(ObjectController):

    selection_changed_signal = PySignal.ClassSignal()

    @classmethod
    def get_controller(cls, standalone=False, mock=False):
        this = super(NodeController, cls).get_controller()
        this.name_function = nal.create_name_string
        this.scene = scn.get_scene(
            standalone=standalone,
            mock=mock
        )
        return this

    def __del__(self):
        self.deleted_signal.emit()

    def __init__(self):
        super(NodeController, self).__init__()
        self.scene = None
        self.uuid = str(uuid.uuid4())

    def save_uuid_to_root(self, *args):
        if self.root:
            uuid_plug = self.root.plugs['serialization_uuid']
            if self.scene.objExists(uuid_plug):
                uuid_plug.set_locked(False)
                uuid_plug.set_value(self.uuid)
                uuid_plug.set_locked(True)
            else:
                print 'Warning: The plug %s.serialization_uuid did not exist.' % self.root

    def get_skin_weights(self, node):
        return self.scene.get_skin_weights(node)

    def get_skin_blend_weights(self, node):
        return self.scene.get_skin_blend_weights(node)

    def get_skin_influences(self, node):
        return self.scene.get_skin_influences(node)

    def set_skin_weights(self, node, weights):
        self.scene.set_skin_weights(node, weights)

    def set_skin_blend_weights(self, node, weights):
        self.scene.set_skin_blend_weights(node, weights)

    def skin_as(self, skin_cluster, mesh):
        return self.scene.skin_as(skin_cluster, mesh)

    def set_matrix(self, transform, matrix, world_space=True):
        if not isinstance(transform, Transform):
            raise TypeError('Invalid object type "%s"' % transform.__class__.__name__)
        self.scene.xform(
            transform.get_selection_string(),
            ws=world_space,
            m=list(matrix)
        )

    def get_matrix(self, transform, world_space=True):
        if not isinstance(transform, Transform):
            raise TypeError('Invalid object type "%s"' % transform.__class__.__name__)
        matrix = self.scene.xform(
            transform.get_selection_string(),
            ws=world_space,
            m=True,
            q=True
        )
        if matrix:
            return Matrix(*matrix)

        return Matrix()

    def zero_joint_rotation(self, joint):
        ntl.zero_joint_rotation(joint)

    def initialize_node(self, node_name, **kwargs):
        return ntl.initialize_node(self, node_name, **kwargs)

    def get_curve_data(self, nurbs_curve):
        return self.scene.get_curve_data(nurbs_curve.m_object)

    def get_surface_data(self, nurbs_surface):
        return self.scene.get_surface_data(nurbs_surface.m_object)

    def get_plug_value(self, plug, *args):
        return self.scene.get_plug_value(plug.m_plug, *args)

    def set_plug_value(self, plug, value):
        self.scene.set_plug_value(plug.m_plug, value)

    def connect_plug(self, plug_1, plug_2):
        return plug_1.connect_to(plug_2)

    def unparent(self, child):
        super(NodeController, self).unparent(child)

    def set_parent(self, child, parent):
        super(NodeController, self).set_parent(child, parent)
        self.scene.parent(child, parent)

    def set_name(self, item, name):
        if '.' in name or ' ' in name or '|' in name:
            raise Exception('Invalid name characters "%s"' % name)
        super(NodeController, self).set_name(item, name)
        self.scene.rename(item, name)

    def assign_shading_group(self, shading_group, *nodes):
        for node in nodes:
            node.shader = shading_group
        self.scene.assign_shading_group(shading_group, *nodes)

    def plug_exists(self, node, plug_name):
        return self.scene.objExists('{0}.{1}'.format(node, plug_name))

    def delete_plug(self, plug):
        return self.scene.plug_exists(plug)

    def lock_plugs(self, *nodes):
        self.scene.lock_plugs(*nodes)

    def set_plug_locked(self, plug, value):
        self.scene.set_plug_locked(plug, value)

    def get_plug_locked(self, plug):
        return self.scene.get_plug_locked(plug)

    def set_plug_hidden(self, plug, value):
        self.scene.set_plug_hidden(plug, value)

    def get_plug_hidden(self, plug):
        return self.scene.get_plug_hidden(plug)

    def new_scene(self):
        self.reset()
        self.scene.file(new=True, f=True)

    def save_to_json_file(self, *args, **kwargs):
        self.save_uuid_to_root()

    def load_from_json_file(self, *args, **kwargs):
        pass

    def serialize_object(self, item):
        data = super(NodeController, self).serialize_object(item)
        if isinstance(item, DependNode):
            data['selection_string'] = item.get_selection_string()
        return data

    def deserialize(self, data, namespace=None):
        root_uuid = data['root']
        object_data = data['objects']
        self.progress_signal.emit(
            message='Instantiating Objects',
            maximum=len(object_data),
            value=0
        )
        all_objects = []
        i = 0
        if object_data:
            for x in self.deserialize_iterator(object_data, namespace=namespace):
                self.progress_signal.emit(
                    value=i
                )
                all_objects.append(x)
                i += 1
            self.set_root(self.objects.get(root_uuid, None))
        else:
            print 'WARNING:  object_data field was empty'
        return all_objects

    def deserialize_iterator(self, data, namespace=None):
        depend_nodes = []
        failed_objects = 0
        failed_object_data = []
        tracebacks = []
        for x in data:
            try:
                new_object = self.deserialize_object(
                    x, namespace=namespace)
                yield new_object
            except StandardError, e:
                if self.strict_deserialization:
                    raise
                else:
                    failed_objects += 1
                    if failed_objects < 20:
                        failed_object_data.append(x)
                        tracebacks.append(traceback.format_exc())

        if failed_objects:
            print '%s objects failed to deserialize.  ' \
                  'The rig may need to be published with up to date source code' % failed_objects
            print 'The following are the first 20 kwarg sets that failed:'
            for k in range(len(failed_object_data)):
                print failed_object_data[k]
                print tracebacks[k]

        for x in self.deserialize_properties(data):
            if isinstance(x, DependNode):
                depend_nodes.append(x)
        for depend_node in depend_nodes:
            self.get_m_plugs(depend_node)

    def get_m_plugs(self, item):
        if isinstance(item, Plug):
            parent = item.parent
            if isinstance(parent, Plug):
                item.m_plug = self.scene.initialize_plug(
                    parent.m_plug,
                    item.index
                )
            else:
                item.m_plug = self.scene.initialize_plug(
                    parent.m_object,
                    item.root_name
                )
            for child in item.child_plugs.values():
                self.get_m_plugs(child)
            for element in item.elements.values():
                self.get_m_plugs(element)
        elif isinstance(item, DependNode):
            for plug in item.existing_plugs.values():
                self.get_m_plugs(plug)
        else:
            raise Exception('invalid plug type "%s"' % item.__class__)

    def deserialize_object(self, data, namespace=None):
        if namespace:
            data['values']['name'] = '%s:%s' % (namespace, data['values']['name'])
        item = super(NodeController, self).deserialize_object(data)
        if isinstance(item, DependNode):
            selection_string = data['selection_string']
            if namespace:
                selection_string = '%s:%s' % (namespace, data['selection_string'])
            item.m_object = self.scene.get_m_object(selection_string)
        return item

    def raise_warning(self, message):
        if not self.disable_warnings:
            self.raise_warning_signal.emit(message)

    def raise_error(self, message):
        self.raise_error_signal.emit(message)

    def list_selected_vertices(self):
        return self.scene.list_selected_vertices()

    def list_selected_edges(self, *args, **kwargs):
        return self.scene.polyListComponentConversion(*args, **kwargs)

    def get_selected_nodes(self):
        return [self.initialize_node(x) for x in self.scene.get_selected_nodes()]

    def get_selected_mesh_names(self):
        return self.scene.get_selected_mesh_names()

    def get_selected_mesh_objects(self):
        return self.scene.get_selected_mesh_objects()

    def get_selected_transform_names(self):
        return self.scene.get_selected_transform_names()

    def get_selected_transforms(self):
        return self.scene.get_selected_transforms()

    def get_selected_plugs(self):
        plugs = []
        for node in self.get_selected_nodes():
            for attr in self.scene.get_selected_attribute_names():
                plugs.append(node.plugs[attr])
        return plugs

    def get_selected_plug_strings(self):
        plugs_strings = []
        for node in self.scene.get_selected_node_names():
            for attr in self.scene.get_selected_attribute_names():
                plugs_strings.append('%s.%s' % (node, attr))
        return plugs_strings

    def isolate(self, *objects):
        self.scene.isolate(*[x.get_selection_string() for x in objects])

    def deisolate(self, *objects):
        self.scene.deisolate(*[x.get_selection_string() for x in objects])

    def get_bounding_box_center(self, *nodes):
        return self.scene.get_bounding_box_center(*nodes)

    def get_bounding_box(self, *nodes):
        return self.scene.get_bounding_box(*nodes)

    def hide(self, *objects):
        self.scene.hide(*objects)

    def showHidden(self, *objects):
        self.scene.showHidden(*objects)

    def listRelatives(self, *args, **kwargs):
        return self.scene.listRelatives(*args, **kwargs)

    def getAttr(self, *args, **kwargs):
        return self.scene.getAttr(*args, **kwargs)

    def setAttr(self, *args, **kwargs):
        return self.scene.setAttr(*args, **kwargs)

    def objExists(self, *args, **kwargs):
        return self.scene.objExists(*args, **kwargs)

    def delete_connection(self, connection):
        self.scene.delete_connection(connection)

    def get_file_info(self):
        return self.scene.get_file_info()

    def update_file_info(self, **kwargs):
        self.scene.update_file_info(**kwargs)

    def file(self, *args, **kwargs):
        self.scene.file(*args, **kwargs)

    def select(self, *items, **kwargs):
        self.scene.select(*[x.get_selection_string() for x in items if isinstance(x, DependNode)], **kwargs)

    def fit_view(self, *args):
        self.scene.fit_view(*args)

    def refresh(self):
        self.scene.refresh()

    def dg_dirty(self):
        self.scene.dg_dirty()

    def lock_node(self, *nodes, **kwargs):
        self.scene.lock_node(*nodes, **kwargs)

    def get_dag_path(self, node):
        return str(self.scene.get_dag_path(node.m_object).fullPathName())

    def rename(self, node, name):
        """
        Renaming objects after creation is NOT a preferred workflow..
        It should only be used when pipe demands a specific name for a node
        """
        self.named_objects.pop(node.name, None)
        node.name = name
        self.scene.rename(node.get_selection_string(), name)
        self.named_objects[name] = node

    def listConnections(self, *args, **kwargs):
        return self.scene.listConnections(*args, **kwargs)

    def disconnectAttr(self, *args, **kwargs):
        return self.scene.disconnectAttr(*args, **kwargs)

    def connectAttr(self, *args, **kwargs):
        return self.scene.connectAttr(*args, **kwargs)

    def load_plugin(self, plugin_name):
        self.scene.loadPlugin(plugin_name)

    def check_visibility(self, node):
        return self.scene.check_visibility(node)
