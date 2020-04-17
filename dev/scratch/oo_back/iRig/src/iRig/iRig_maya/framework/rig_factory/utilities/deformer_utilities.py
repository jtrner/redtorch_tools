
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.object_set import ObjectSet
from rig_factory.objects.deformer_objects.nonlinear import NonLinear
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster
from rig_factory.objects.deformer_objects.lattice import Lattice
from rig_factory.objects.deformer_objects.wire import Wire


def get_deformer_data(rig):
    data = []
    for deformer in rig.deformers:
        if not isinstance(deformer, SkinCluster):
            deformer_data = dict(
                klass=deformer.__class__.__name__,
                module=deformer.__module__,
                root_name=deformer.root_name,
                side=deformer.side,
                size=deformer.size,
                index=deformer.index,
                weights=deformer.get_weights(),
                geometry=[str(x) for x in deformer.deformer_set.members]
            )
            data.append(deformer_data)
    return data


def create_lattice(controller, parent, *geometry, **kwargs):

    root_name = kwargs.pop('root_name', None)
    kwargs['parent'] = parent

    this = Lattice(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    lattice = Transform(
        controller=controller,
        root_name='%s_lattice' % root_name,
        **kwargs
    )
    lattice_shape = DagNode(
        controller=controller,
        node_type='lattice',
        root_name='%s_lattice' % root_name,
        **kwargs
    )

    base_lattice = Transform(
        controller=controller,
        root_name='%s_lattice_base' % root_name,
        **kwargs
    )
    lattice_base_shape = DagNode(
        controller=controller,
        root_name='%s_lattice_base' % root_name,
        **kwargs
    )

    deformer_set = ObjectSet(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    m_objects = controller.scene.create_lattice(*geometry)
    (
        this.m_object,
        lattice.m_object,
        base_lattice.m_object,
        lattice_shape.m_object,
        lattice_base_shape.m_object,
        deformer_set.m_object,
    ) = m_objects

    parent_name = controller.scene.get_selection_string(parent.m_object)
    controller.scene.parent(
        controller.scene.get_selection_string(lattice.m_object),
        parent_name,
    )
    controller.scene.parent(
        controller.scene.get_selection_string(base_lattice.m_object),
        parent_name,
    )

    this.deformer_set = deformer_set
    this.lattice = lattice
    this.lattice_shape = lattice_shape
    this.base_lattice = base_lattice
    this.base_lattice_shape = lattice_base_shape

    deformer_set.members = list(geometry)
    for x in geometry:
        x.deformers.append(this)

    controller.register_item(this)
    controller.register_item(lattice)
    controller.register_item(lattice_shape)
    controller.register_item(base_lattice)
    controller.register_item(lattice_base_shape)
    controller.register_item(deformer_set)

    def rename_node(node):
        controller.rename(
            node,
            controller.name_function(
                node.__class__.__name__,
                root_name=node.root_name,
                **kwargs
            )
        )
    rename_node(this)
    rename_node(lattice)
    rename_node(lattice_shape)
    rename_node(base_lattice)
    rename_node(lattice_base_shape)
    rename_node(deformer_set)

    return this


def create_wire_deformer(controller, curve, *geometry, **kwargs):

    root_name = kwargs.pop('root_name', None)

    this = Wire(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    base_wire = Transform(
        controller=controller,
        root_name='%s_base_wire' % root_name,
        **kwargs
    )
    base_wire_shape = DagNode(
        controller=controller,
        root_name='%s_base_wire' % root_name,
        **kwargs
    )

    deformer_set = ObjectSet(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    m_objects = controller.scene.create_wire_deformer(curve, *geometry)
    (
        this.m_object,
        base_wire.m_object,
        base_wire_shape.m_object,
        deformer_set.m_object,
    ) = m_objects

    this.deformer_set = deformer_set
    this.base_wire = base_wire
    this.base_wire_shape = base_wire_shape

    deformer_set.members = list(geometry)
    for x in geometry:
        x.deformers.append(this)

    def get_name(node):

        return controller.name_function(
            node.__class__.__name__,
            root_name=node.root_name,
            **kwargs
        )

    items = (
        this,
        base_wire,
        base_wire_shape,
        deformer_set
    )
    for item in items:

        controller.register_item(item)
        controller.rename(item, get_name(item))

    return this


def create_nonlinear_deformer(controller, deformer_type, geometry, parent, **kwargs):

    if not geometry:
        raise Exception('you must provide the deformer type as the first argument')
    if isinstance(deformer_type, basestring):
        if deformer_type in __dict__:
            deformer_type = __dict__[deformer_type]
    if not issubclass(deformer_type, NonLinear):
        raise Exception('The deformer type provided was invalid "%s".' % deformer_type)

    kwargs['parent'] = parent

    this = deformer_type(
        controller=controller,
        **kwargs
    )

    handle = Transform(
        controller=controller,
        **kwargs
    )
    handle_shape = DagNode(
        controller=controller,
        node_type=this.handle_type,
        **kwargs
    )

    deformer_set = ObjectSet(
        controller=controller,
        **kwargs
    )

    m_objects = controller.scene.create_nonlinear_deformer(
        this.deformer_type,
        geometry
    )

    (
        this.m_object,
        handle.m_object,
        handle_shape.m_object,
        deformer_set.m_object
    ) = m_objects

    parent_name = controller.scene.get_selection_string(parent.m_object)
    controller.scene.parent(
        controller.scene.get_selection_string(handle.m_object),
        parent_name,
    )

    this.handle = handle
    this.handle_shape = handle_shape
    this.deformer_set = deformer_set
    deformer_set.members = list(geometry)

    for x in geometry:
        x.deformers.append(this)
    controller.register_item(this)
    controller.register_item(handle)
    controller.register_item(handle_shape)
    controller.register_item(deformer_set)

    controller.rename(
        deformer_set,
        controller.name_function(
            deformer_set.__class__.__name__,
            **kwargs
        )
    )
    controller.rename(
        this,
        controller.name_function(
            this.__class__.__name__,
            **kwargs
        )
    )
    controller.rename(
        handle,
        controller.name_function(
            handle.__class__.__name__,
            **kwargs
        )
    )
    controller.rename(
        handle_shape,
        controller.name_function(
            handle_shape.__class__.__name__,
            **kwargs
        )
    )

    return this


def create_skin_cluster(controller, geometry, influences, **kwargs):
    return controller.scene.create_from_skin_data(
        dict(
            geometry=geometry,
            joints=influences,
            weights=dict()
        )
    )


def get_skin_cluster_data(controller, rig):
    data = []
    for key in rig.geometry:
        skin_cluster = controller.find_skin_cluster(rig.geometry[key])
        if skin_cluster:
            data.append(controller.scene.get_skin_data(skin_cluster))
    return data


def set_skin_cluster_data(controller, rig, data):
    if data:
        controller.progress_signal.emit(
            message='Building Skin Clusters...',
            maximum=len(data or []),
            value=0
        )
        all_missing_joints = []
        missing_geometry = []

        for i, skin_data in enumerate(data or []):
            controller.progress_signal.emit(
                message='Building Skincluster : \n%s' % skin_data['geometry'],
                value=i
            )
            missing_joints = []
            for joint in skin_data['joints']:
                if not controller.objExists(joint):
                    missing_joints.append(joint)
            if missing_joints:
                all_missing_joints.extend(missing_joints)
                continue
            if not controller.objExists(skin_data['geometry']):
                missing_geometry.append(skin_data['geometry'])
                continue
            try:
                controller.scene.create_from_skin_data(skin_data)
            except StandardError, e:
                print e.message

        all_missing_joints = [all_missing_joints[x] for x in range(len(all_missing_joints)) if x < 8]
        missing_geometry = [missing_geometry[x] for x in range(len(missing_geometry)) if x < 8]

        if all_missing_joints:
            controller.raise_warning_signal.emit(
                'Failed skin report: missing joints:\n%s' % '\n'.join(all_missing_joints)
            )
        if missing_geometry:
            controller.raise_warning_signal.emit(
                'Failed Skin report: missing geometry:\n%s' % '\n'.join(missing_geometry)
            )
        controller.progress_signal.emit(
            done=True
        )


def initialize_deformers(mesh):
    controller = mesh.controller
    scene = controller.scene
    mesh_history = mesh.controller.scene.listHistory(mesh)
    deformers = []
    if mesh_history:
        for deformer_name in [x for x in mesh_history if 'geometryFilter' in scene.nodeType(x, inherited=True)]:
            deformer_type = scene.nodeType(deformer_name)
            if deformer_type == 'skinCluster':
                m_object = scene.get_m_object(deformer_name)
                skin_cluster = SkinCluster(m_object=m_object)
                deformers.append(skin_cluster)
    return deformers
