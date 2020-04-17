from dag_node import DagNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class Mesh(DagNode):

    deformers = ObjectListProperty(
        name='deformers'
    )

    def __init__(self, **kwargs):
        super(Mesh, self).__init__(**kwargs)
        self.node_type = 'mesh'

    def vertex_count(self):
        return self.controller.scene.get_vertex_count(self.m_object)

    def get_closest_vertex_index(self, point):
        return self.controller.scene.get_closest_vertex_index(self.m_object, point)

    def get_closest_vertex_uv(self, point):
        return self.controller.scene.get_closest_vertex_uv(self.m_object, point)

    def get_vertices(self, *indices):
        return [self.get_vertex(x) for x in flatten_integers(indices)]

    def get_vertex(self, index):
        if not isinstance(index, int):
            raise Exception('Cannot get vertex with index of type "%s"' % type(index))
        vertex_name = '%s.vtx[%s]' % (self.name, index)
        if vertex_name in self.controller.named_objects:
            return self.controller.named_objects[vertex_name]
        else:
            return self.create_child(
                MeshVertex,
                index=index,
                name=vertex_name,
                mesh=self
            )

    def get_face(self, index):
        if not isinstance(index, int):
            raise Exception('Cannot get face with index of type "%s"' % type(index))
        face_name = '%s.f[%s]' % (self.name, index)
        if face_name in self.controller.named_objects:
            return self.controller.named_objects[face_name]
        else:
            return self.create_child(
                MeshFace,
                index=index,
                name=face_name,
                mesh=self
            )

    def redraw(self):
        self.controller.scene.update_mesh(self.m_object)


def flatten_integers(*args):
    integers = []
    for arg in args:
        if isinstance(arg, int):
            integers.append(arg)
        elif isinstance(arg, (list, tuple, set)):
            integers.extend(flatten_integers(*arg))
    return integers


class MeshVertex(BaseNode):

    mesh = ObjectProperty(
        name='mesh'
    )

    def __init__(self, **kwargs):

        super(MeshVertex, self).__init__(**kwargs)

    def get_translation(self):
        return self.controller.xform(self.get_selection_string(), q=True, ws=True, t=True)

    def get_selection_string(self):
        return '%s.vtx[%s]' % (self.mesh.get_selection_string(), self.index)


class MeshFace(BaseNode):

    mesh = ObjectProperty(
        name='mesh'
    )

    def __init__(self, **kwargs):

        super(MeshFace, self).__init__(**kwargs)

    def get_translation(self):
        return self.controller.xform(self.get_selection_string(), q=True, ws=True, t=True)

    def get_selection_string(self):
        return '%s.f[%s]' % (self.mesh.get_selection_string(), self.index)
