import os
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.node_objects.mesh import Mesh


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


def import_geometry(controller, rig, path, parent=None):
    """
    Now that controller node_objects are kept track of by name, it is possible to just look them up directly instead of pinning to the rig container
    """
    if rig.parent is None:
        if parent is None:
            parent = rig.geometry_group
        rig.geometry_paths.append(path)
        container_paths = list(rig.geometry_paths)
        container_paths.append(path)
        container_paths = list(set(container_paths))

        existing_paths = []
        for x in container_paths:
            if os.path.exists(x):
                existing_paths.append(x)

        rig.geometry_paths = existing_paths
        root_nodes = controller.scene.import_geometry(path)
        if root_nodes:
            new_geometry = dict()
            for geometry_root in [controller.initialize_node(x, parent=parent) for x in root_nodes]:
                # initialize_node does not set parent so we must set it after
                #controller.scene.parent(
                #    geometry_root.get_selection_string(),
                #    rig.geometry_group.get_selection_string()
                #)
                shapes = get_shape_descendants(controller, geometry_root)
                new_geometry.update(dict((x.name, x) for x in shapes if isinstance(x, Mesh)))
                #controller.root_changed_signal.emit(rig)
                controller.scene.select(cl=True)
            rig.geometry.update(new_geometry)
            if isinstance(rig, ContainerGuide):
                for mesh in new_geometry.values():
                    mesh.assign_shading_group(rig.shaders[None].shading_group)
            #controller.root_changed_signal.emit(controller.root)
            controller.scene.fit_view(rig.geometry.keys())
            controller.scene.select(cl=True)
            return new_geometry
        else:
            print 'Warning ! No geometry roots found in %s' % path
    else:
        print '%s has a parent. unable to import geometry' % rig


def import_utility_geometry(rig, path):
    controller = rig.controller
    """
    Now that controller node_objects are kept track of by name, it is possible to just look them up directly instead of pinning to the rig container
    """
    if rig.parent is None:
        container_paths = list(set(rig.utility_geometry_paths))
        existing_paths = []
        for x in container_paths:
            if os.path.exists(x):
                existing_paths.append(x)
        rig.utility_geometry_paths = list(existing_paths)
        root_nodes = controller.scene.import_geometry(path)
        if root_nodes:
            new_geometry = dict()
            for geometry_root in [controller.initialize_node(x, parent=rig.utility_geometry_group) for x in root_nodes]:
                shapes = get_shape_descendants(controller, geometry_root)
                new_geometry.update(dict((x.name, x) for x in shapes if isinstance(x, Mesh)))
                controller.root_changed_signal.emit(rig)
                controller.scene.select(cl=True)
            rig.geometry.update(new_geometry)
            if isinstance(rig, ContainerGuide):
                for mesh in new_geometry.values():
                    mesh.assign_shading_group(rig.shaders[None].shading_group)
            #controller.root_changed_signal.emit(controller.root)
            controller.scene.fit_view(rig.geometry.keys())
            controller.scene.select(cl=True)
            return new_geometry
        else:
            print 'Warning ! No geometry roots found in %s' % path
    else:
        print '%s has a parent. unable to import geometry' % rig


def gather_mesh_children(transform):
    mesh_children = []
    for child in transform.children:
        if isinstance(child, Mesh):
            mesh_children.append(child)
        else:
            mesh_children.extend(gather_mesh_children(child))
    return mesh_children
