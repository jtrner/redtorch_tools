from rig_factory.objects.node_objects.mesh import Mesh


def import_geometry(controller, path, parent=None):
    root_nodes = controller.scene.import_geometry(path)
    if root_nodes:
        new_geometry = dict()
        for geometry_root in [controller.initialize_node(x, parent=parent) for x in root_nodes]:
            shapes = get_shape_descendants(controller, geometry_root)
            new_geometry.update(dict((x.name, x) for x in shapes if isinstance(x, Mesh)))
            controller.scene.select(cl=True)
        return new_geometry
    else:
        print 'Warning ! No geometry roots found in %s' % path


def get_shape_descendants(controller, node):
    mesh_relatives = controller.scene.listRelatives(
        node,
        c=True,
        type='mesh',
        f=True
    )
    nurbs_relatives = controller.scene.listRelatives(
        node,
        c=True,
        type='nurbsSurface',
        f=True
    )
    descendants = []
    if mesh_relatives:
        descendants = [controller.initialize_node(x, parent=node) for x in mesh_relatives]
    if nurbs_relatives:
        descendants = [controller.initialize_node(x, parent=node) for x in nurbs_relatives]
    transform_relatives = controller.scene.listRelatives(
        node,
        c=True,
        type='transform',
        f=True
    )
    if transform_relatives:
        transforms = [controller.initialize_node(x, parent=node) for x in transform_relatives]
        for transform in transforms:
            descendants.extend(controller.get_shape_descendants(transform))
    return descendants
