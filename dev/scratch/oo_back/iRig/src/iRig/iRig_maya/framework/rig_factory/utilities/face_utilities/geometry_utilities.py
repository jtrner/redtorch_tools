from rig_factory.objects.face_objects.face_handle import FaceHandle
from rig_factory.objects.face_network_objects import FaceNetwork
from rig_factory.controllers.face_controller import FaceController


def snap_to_mesh(item, mesh):


    controller = item.controller
    if isinstance(controller, FaceController):

        if isinstance(item, FaceNetwork):
            for point in controller.get_control_points(item):
                controller.snap_to_mesh(point, mesh)

        elif isinstance(item, FaceHandle):
            vertices = [controller.get_mesh(mesh).get_vertex(x) for x in item.vertex_indices]
            matrix = controller.get_transformation_matrix(vertices)
            item.set_transformation_matrix(matrix)
        else:
            raise Exception('Could not get "snap_to_mesh". Invalid type "%s"' % type(item))
    else:
        raise Exception('Invalid controller type "%s' % type(controller))
