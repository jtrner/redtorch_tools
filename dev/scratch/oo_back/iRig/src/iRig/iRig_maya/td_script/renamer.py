"""Provides an easy way to rename nodes based on selection in Maya."""

# import standard modules
import time

# import maya modules
from maya import OpenMaya as api0
from maya import OpenMayaAnim as apiAnim0
from maya import cmds

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "IL"
__version__ = "1.1.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"

# define global variables
API_MFN = api0.MFn
TRANSFORM_ID = {API_MFN.kIkHandle: 'IkHandle',
                API_MFN.kIkEffector: 'ikEff',
                API_MFN.kJoint: 'Bnd_Jnt'}

SHAPE_ID = {API_MFN.kMesh: 'Geo',
            API_MFN.kNurbsSurface: 'Srf',
            API_MFN.kNurbsCurve: 'Crv',
            API_MFN.kTransform: 'Offset_Transform_Grp',
            API_MFN.kLocator: 'Loc',
            API_MFN.kCluster: 'Cls',
            API_MFN.kFFD: 'Ffd',
            API_MFN.kLattice: 'Lattice',
            API_MFN.kBaseLattice: 'BaseLattice'}

DEFORMER_ID = {API_MFN.kSkinClusterFilter: 'Skin',
               API_MFN.kTweak: "Tweak",
               API_MFN.kClusterFilter: "Cls",
               API_MFN.kDeltaMush: "DeltaMush",
               API_MFN.kFFD: 'Ffd',
               API_MFN.kNonLinear: False
               }

HANDLE_ID = {API_MFN.kCluster: '_ClsHandle',
             API_MFN.kLattice: '_Lattice',
             API_MFN.kBaseLattice: '_BaseLattice',
             API_MFN.kDeformSquash: '_SquashHandle',
             API_MFN.kDeformBend: '_BendHandle',
             API_MFN.kDeformTwist: '_TwistHandle',
             API_MFN.kDeformFlare: '_FlareHandle',
             API_MFN.kDeformWave: '_WaveHandle',
             API_MFN.kDeformSine: '_SineHandle',
             API_MFN.kSoftMod: '_SoftHandle'}

MAYA_ID = {679: 'SkinCluster',
           345: 'Tweak',
           347: 'Cluster',
           350: 'DeltaMush',
           339: 'FFD',
           616: 'NonLinear',
           296: 'Mesh',
           267: 'NurbsCurve',
           294: 'NurbsSurface',
           279: 'Lattice',
           249: 'BaseLattice',
           618: 'Bend',
           620: 'Squash'}


def check_duplicate_names(select=False):
    """
    Find Transforms with Duplicate Names.
    :param select: <bool> selects all the duplicate transform nodes.
    :return: <dict> of the duplicates.
    """
    data = {}
    for trfm in cmds.ls(dag=True):
        if "|" in trfm:
            shape = cmds.listRelatives(trfm, s=1)
            if shape:
                shape_type = cmds.objectType(shape)
            if not shape:
                shape_type = cmds.objectType(trfm)
            if shape_type not in data:
                data[shape_type] = []
            data[shape_type].append(trfm)

    # selects all duplicate tranforms
    if select:
        cmds.select([a for b in data.values() for a in b])
    return data


def rename_selected(name_str=''):
    """
    Use OpenMaya to rename selected objects.
    :return: <bool> True for success. <bool> False for failure.
    """
    # get user input
    if not name_str:
        name_str = raw_input()

        if not name_str:
            return False

    titled_str = name_str.title()

    selection = api0.MSelectionList()
    api0.MGlobal.getActiveSelectionList(selection)
    selection_iter = api0.MItSelectionList(selection)
    m_dag_mod = api0.MDagModifier()
    obj = api0.MObject()
    idx = 0
    while not selection_iter.isDone():
        selection_iter.getDependNode(obj)
        m_dag = api0.MDagPath.getAPathTo(obj)
        renamed = False
        # if the transform is a dag node itself, name it accordingly.
        for transform_fn, transfom_name in TRANSFORM_ID.items():
            if not m_dag.hasFn(transform_fn):
                continue
            nice_name = titled_str + '_{}_{}'.format(str(idx).zfill(2), transfom_name)
            m_dag_mod = api0.MDagModifier()
            m_dag_mod.renameNode(obj, nice_name)
            m_dag_mod.doIt()
            renamed = True

        if not renamed:
            # get the shape node
            m_dag_fn = api0.MFnDagNode(m_dag)
            child_count = m_dag_fn.childCount()
            if child_count:
                child_node = m_dag_fn.child(0)
                m_par_dag = api0.MDagPath.getAPathTo(child_node)
                for k_shape, shape_name in SHAPE_ID.items():
                    if not m_par_dag.hasFn(k_shape):
                        continue
                    nice_name = titled_str + '_{}_{}'.format(str(idx).zfill(2), shape_name)
                    m_dag_mod.renameNode(obj, nice_name)
                    m_dag_mod.doIt()
            else:
                m_dag_mod.renameNode(obj, titled_str + '{}_{}'.format(str(idx).zfill(2), 'Grp'))
                m_dag_mod.doIt()

        # continue with the next item in selection
        selection_iter.next()
        idx += 1


def get_set_name(node):
    """
    From a deformer node specified, find the deformer set associeated.
    :return: <bool> True for success.
    """
    set_obj = None
    geom_filter = None
    try:
        geom_filter = apiAnim0.MFnGeometryFilter(node)
        set_obj = geom_filter.deformerSet()
    except RuntimeError:
        pass

    if node.hasFn(API_MFN.kSkin):
        skin_fn = apiAnim0.MFnSkinCluster(node)
        set_obj = skin_fn.deformerSet()

    if node.hasFn(API_MFN.kCluster):
        cls_fn = apiAnim0.MFnWeightGeometryFilter(node)
        set_obj = cls_fn.deformerSet()

    if not set_obj:
        return False

    if set_obj.isNull():
        return False

    return api0.MFnDependencyNode(set_obj).name()


def get_attached_mesh_name(node, first_item=0, m_objects=1):
    """
    Gets the MFnSkinCluster from the MObject specified.
    :param node: <MObject> node to look at.
    :param first_item: <bool> stops at first item in node connections.
    :param m_objects: <bool> returns a list of MObjects instead.
    :return: <MFnMeshType> if successful, <bool> False if fail.
    """
    it_dg = api0.MItDependencyGraph(node,
                                    api0.MItDependencyGraph.kDownstream,
                                    api0.MItDependencyGraph.kPlugLevel)
    cur_item = None
    mesh_items = []
    lattice_items = []
    nurbs_items = []
    curve_items = []
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        cur_name = api0.MFnDependencyNode(cur_item).name()
        if cur_item.hasFn(API_MFN.kMesh):
            if m_objects:
                mesh_items.append(cur_item)
            else:
                mesh_items.append(get_parent_name(cur_name))
            if first_item:
                break
        if cur_item.hasFn(API_MFN.kLattice):
            if m_objects:
                lattice_items.append(cur_item)
            else:
                lattice_items.append(cur_name)
            if first_item:
                break
        if cur_item.hasFn(API_MFN.kNurbsSurface):
            if m_objects:
                nurbs_items.append(cur_item)
            else:
                nurbs_items.append(get_parent_name(cur_name))
            if first_item:
                break
        if cur_item.hasFn(API_MFN.kNurbsCurve):
            if m_objects:
                curve_items.append(cur_item)
            else:
                curve_items.append(get_parent_name(cur_name))
            if first_item:
                break
        it_dg.next()

    if not cur_item:
        return None

    node_items = {}
    if mesh_items:
        node_items[API_MFN.kMesh] = mesh_items
    if lattice_items:
        node_items[API_MFN.kLattice] = lattice_items
    if nurbs_items:
        node_items[API_MFN.kNurbsSurface] = nurbs_items
    if curve_items:
        node_items[API_MFN.kNurbsCurve] = curve_items
    return node_items


def get_parent_name(node):
    """
    Get the Handle transform from shape provided
    :return: <str> transform node.
    """
    if isinstance(node, (str, unicode)):
        sel = api0.MSelectionList()
        sel.add(node)
        m_dag = api0.MDagPath()
        sel.getDagPath(0, m_dag)

    else:
        if node.hasFn(API_MFN.kDagNode):
            m_dag = api0.MDagPath()
            # returns a full path name of the affecting shape node.
            api0.MDagPath.getAPathTo(node, m_dag)

    # get the parent node.
    m_dag_fn = api0.MFnDagNode(m_dag)
    par_node = m_dag_fn.parent(0)
    m_node = api0.MFnDependencyNode(par_node)

    return m_node.name()


def get_attached_deformer(node):
    """
    From the node provided, aquire the attached deformer node.
    :param node: <MObject> Maya's Shape node.
    :return: <MObject> deformer node.
    """
    m_node = api0.MFnDependencyNode(node)
    check_node_name = m_node.name()
    it_dg = api0.MItDependencyGraph(node,
                                    api0.MItDependencyGraph.kDownstream,
                                    api0.MItDependencyGraph.kDepthFirst,
                                    api0.MItDependencyGraph.kNodeLevel)
    defomer_nodes = []
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        for deformer_node_id in DEFORMER_ID:
            if cur_item.hasFn(deformer_node_id):
                m_node = api0.MFnDependencyNode(cur_item)
                defomer_nodes.append({check_node_name: {'name': m_node.name(),
                                                        'type_name': m_node.typeName(),
                                                        'm_depend_node': m_node,
                                                        'm_obj': cur_item,
                                                        'type_id': cur_item.apiType()}})
                break
        it_dg.next()
    return defomer_nodes


def get_deformer_name_data(multi_mesh_deformers=False):
    """
    Retrieves all the deformer information inside the Maya scene.
    :return: <dict> name data for all the nodes in the scene.
    """
    name_data = {}

    # collect the deformer node names
    deform_data = {}
    multi_mesh_data = {}
    for deformer_type, suffix_name in DEFORMER_ID.items():
        d_type_name = MAYA_ID[deformer_type]
        deform_data[d_type_name] = []
        node_it = api0.MItDependencyNodes(deformer_type)
        while not node_it.isDone():
            m_node = api0.MFnDependencyNode(node_it.item())
            node_name = m_node.name()
            m_obj = node_it.item()
            mesh_data = get_attached_mesh_name(m_obj, first_item=1)

            # get the mesh name in the order or priority
            if API_MFN.kMesh in mesh_data:
                mesh_name = mesh_data[API_MFN.kMesh]
            elif API_MFN.kNurbsCurve in mesh_data:
                mesh_name = mesh_data[API_MFN.kNurbsCurve]
            elif API_MFN.kNurbsSurface in mesh_data:
                mesh_name = mesh_data[API_MFN.kNurbsSurface]
            elif API_MFN.kLattice in mesh_data:
                mesh_name = mesh_data[API_MFN.kLattice]

            # get the deformer set object name
            set_name = get_set_name(m_obj)

            if set_name:
                if mesh_name:
                    if isinstance(mesh_name, (tuple, list)):
                        if len(mesh_name) > 1:
                            if node_name not in multi_mesh_data:
                                multi_mesh_data[node_name] = []
                            multi_mesh_data[node_name].extend(map(get_parent_name, mesh_name))
                        else:
                            mesh_name = get_parent_name(mesh_name[0])
                            if type(mesh_name) is api0.MObject:
                                mesh_name = api0.MFnDependencyNode(mesh_name).name()
                            if ':' in mesh_name:
                                mesh_name = mesh_name.rpartition(':')[-1]

                            if mesh_name not in name_data:
                                name_data[mesh_name] = []

                            name_data[mesh_name].append({
                                suffix_name: {'deformer': node_name,
                                              'deformer_type': m_node.typeName(),
                                              'deformer_set': set_name,
                                              'deformer_id': m_obj.apiType()}
                            })
            node_it.next()

    if not multi_mesh_deformers:
        return name_data
    else:
        return multi_mesh_data


def get_handle_name_data(multi_mesh_deformers=False):
    """
    Retrieves all the deformer information inside the Maya scene.
    :return: <dict> name data for all the nodes in the scene.
    """
    name_data = {}
    multi_mesh_data = {}

    # get all the handle transform data with their respective relationship with the deformer
    for handle_type, suffix_type in HANDLE_ID.items():
        node_it = api0.MItDependencyNodes(handle_type)
        while not node_it.isDone():
            m_obj = node_it.item()
            node_name = api0.MFnDependencyNode(m_obj).name()
            transform_name = get_parent_name(m_obj)
            deformer_data = get_attached_deformer(m_obj)
            try:
                deform_obj = deformer_data[0][node_name]['m_obj']
                deform_name = deformer_data[0][node_name]['name']
                deform_type = deformer_data[0][node_name]['type_name']
                deform_id = deformer_data[0][node_name]['type_id']
            except IndexError:
                print("Rename Handles Error] :: {}, {}".format(node_name, deformer_data))
                raise RuntimeError("Renaming Halted")
            mesh_data = get_attached_mesh_name(deform_obj, m_objects=0)

            # get the mesh name in the order or priority
            if API_MFN.kMesh in mesh_data:
                mesh_name = mesh_data[API_MFN.kMesh]
            elif API_MFN.kNurbsCurve in mesh_data:
                mesh_name = mesh_data[API_MFN.kNurbsCurve]
            elif API_MFN.kNurbsSurface in mesh_data:
                mesh_name = mesh_data[API_MFN.kNurbsSurface]
            elif API_MFN.kLattice in mesh_data:
                mesh_name = mesh_data[API_MFN.kLattice]

            # get the deformer set object name
            set_name = get_set_name(deform_obj)

            if set_name:
                if isinstance(mesh_name, (tuple, list)):
                    if len(mesh_name) > 1:
                        if not deform_name in multi_mesh_data:
                            multi_mesh_data[deform_name] = []
                        multi_mesh_data[deform_name].extend(mesh_name)

                    if len(mesh_name) == 1:
                        mesh_name = mesh_name[0]
                        if mesh_name not in name_data:
                            name_data[mesh_name] = []
                        name_data[mesh_name].append({
                            suffix_type: {'deformer': deform_name,
                                          'shape': node_name,
                                          'transform': transform_name,
                                          'deformer_type': deform_type,
                                          'deformer_set': set_name,
                                          'deformer_id': deform_id,
                                          }
                        })
            node_it.next()
    if not multi_mesh_deformers:
        return name_data
    else:
        return multi_mesh_data


def rename_handlers(rename=1, verbose=1):
    """
    Renames the deformers based on their connection to the controlling mesh.
    :param rename: <bool> Renames the deformer handler nodes.
    :param verbose: <bool> Prints the renaming states.
    :return: <bool> True for success.
    """
    start_time = time.time()
    handle_name_data = get_handle_name_data()

    deformer_renamed = 0
    handler_renamed = 0
    set_renamed = 0

    for mesh_name, names_ls in handle_name_data.items():
        for idx, d_data in enumerate(names_ls):
            # {'_ClsHandle': {'deformer_type': u'cluster',
            #                 'deformer_set': u'C_Spine_07_ClsSet',
            #                 'deformer': u'C_Spine_07_Cls',
            #                 'deformer_id': 347}}
            handle_suffix_name = d_data.keys()[0]

            old_shape_name = d_data[handle_suffix_name]['shape']
            old_transform_name = d_data[handle_suffix_name]['transform']
            old_deformer_name = d_data[handle_suffix_name]['deformer']
            old_set_name = d_data[handle_suffix_name]['deformer_set']

            deformer_suffix_name = DEFORMER_ID[d_data[handle_suffix_name]['deformer_id']]
            number_str = '{}'.format(idx).zfill(2)
            if not deformer_suffix_name:
                deformer_suffix_name = handle_suffix_name.split('Handle')[0]

            if ':' in mesh_name:
                mesh_name = mesh_name.rpartition(':')[0]

            deformer_name = '{}_{}_{}'.format(mesh_name, number_str, deformer_suffix_name)
            deformer_handle_name = '{}_{}_{}'.format(mesh_name, number_str, handle_suffix_name)
            deformer_set_name = '{}Set'.format(deformer_name)

            deformer_renamed = 0
            handler_renamed = 0
            set_renamed = 0

            if not old_deformer_name.endswith(deformer_suffix_name):
                if rename:
                    try:
                        cmds.rename(old_deformer_name, deformer_name)
                    except RuntimeError as error:
                        print('[Rename Error] :: {}\n{}'.format(old_deformer_name, error))
                deformer_renamed = 1

            if not deformer_handle_name.endswith(handle_suffix_name):
                if rename:
                    try:
                        cmds.rename(old_transform_name, deformer_handle_name)
                    except RuntimeError as error:
                        print('[Rename Error] :: {}\n{}'.format(old_transform_name, error))
                handler_renamed = 1

            if old_set_name != deformer_set_name:
                if rename:
                    try:
                        cmds.rename(old_set_name, deformer_set_name)
                    except RuntimeError as error:
                        print('[Rename Error] :: {}\n{}'.format(old_set_name, error))
                set_renamed = 1

            # print the results
            if sum([deformer_renamed, handler_renamed, set_renamed]) > 1 and verbose:
                print("\n\n---- Renaming -----")
                if deformer_renamed:
                    print('Deformer: {} -- > {}'.format(old_deformer_name, deformer_name))
                if handler_renamed:
                    print('Handle (Transform): {} -- > {}'.format(old_transform_name, deformer_handle_name))
                if set_renamed:
                    print('Set: {} -- > {}'.format(old_set_name, deformer_set_name))
                print("-------------------")

    end_time = time.time()
    if sum([deformer_renamed, handler_renamed, set_renamed]) > 1:
        print("[Rename Deformers] :: Deformer Handlers renamed in {} seconds.".format((end_time - start_time) % 60))
    else:
        print("[Rename Deformers] :: Nothing to rename.")
    return True


def rename_deformers(rename=1, verbose=1):
    """
    Renames the deformers based on their connection to the controlling mesh.
    :param rename: <bool> Renames the deformer handler nodes.
    :param verbose: <bool> Prints the renaming states.
    :return: <bool> True for success.
    """
    start_time = time.time()
    deformer_name_data = get_deformer_name_data()

    deformer_renamed = 0
    set_renamed = 0

    for mesh_name, names_ls in deformer_name_data.items():
        for idx, d_data in enumerate(names_ls):
            if False in d_data:
                # skip the nonLinear deformers
                continue
            handle_suffix_name = d_data.keys()[0]

            old_deformer_name = d_data[handle_suffix_name]['deformer']
            old_set_name = d_data[handle_suffix_name]['deformer_set']

            deformer_suffix_name = DEFORMER_ID[d_data[handle_suffix_name]['deformer_id']]
            number_str = '{}'.format(idx).zfill(2)

            deformer_name = '{}_{}_{}'.format(mesh_name, number_str, deformer_suffix_name)
            deformer_set_name = '{}Set'.format(deformer_name)

            deformer_renamed = 0
            set_renamed = 0

            if not old_deformer_name.endswith(deformer_suffix_name):
                if rename:
                    cmds.rename(old_deformer_name, deformer_name)
                deformer_renamed = 1

            if old_set_name != deformer_set_name:
                if rename:
                    cmds.rename(old_set_name, deformer_set_name)
                set_renamed = 1

            # print the results
            if sum([deformer_renamed, set_renamed]) > 1 and verbose:
                print("\n\n---- Renaming -----")
                if deformer_renamed:
                    print('Deformer: {} -- > {}'.format(old_deformer_name, deformer_name))
                if set_renamed:
                    print('Set: {} -- > {}'.format(old_set_name, deformer_set_name))
                print("-------------------")

    end_time = time.time()
    if sum([deformer_renamed, set_renamed]) > 1:
        print("[Rename Deformers] :: Deformer Nodes renamed in {} seconds.".format((end_time - start_time) % 60))
    else:
        print("[Rename Deformers] :: Nothing to rename.")
    return True