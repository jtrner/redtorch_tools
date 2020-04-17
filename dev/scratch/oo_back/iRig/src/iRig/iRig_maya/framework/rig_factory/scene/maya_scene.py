import os
import warnings
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
from maya_tools.utilities.decorators import flatten_args, m_object_arg
import maya_tools.utilities.nurbs_utils as ctl
import maya_tools.utilities.ik_handle_utilities as itl
import maya_tools.utilities.mesh_utilities as mtl
import maya_tools.utilities.plug_utilities as ptl
import maya_tools.deformer_utilities.blendshape as btl
import maya_tools.utilities.animation_curve_utils as atl
import maya_tools.utilities.selection_utilities as stl
import maya_tools.deformer_utilities.skin_cluster as sku
import maya_tools.deformer_utilities.delta_mush as dmu
import maya_tools.deformer_utilities.wrap as wru
import maya_tools.deformer_utilities.general as dtl
import maya_tools.deformer_utilities.non_linear as ntl
import maya_tools.utilities.ribbon_utilities as rtl
import maya_tools.utilities.skin_utils as sss
import maya_tools.utilities.nurbs_surface_utilities as nsl
import maya_tools.deformer_utilities.lattice as lut
import maya_tools.deformer_utilities.wire as wir

NURBS_CURVE_FORMS = [
    om.MFnNurbsCurve.kOpen,
    om.MFnNurbsCurve.kClosed,
    om.MFnNurbsCurve.kPeriodic
]
NURBS_SURFACE_FORMS = [
    om.MFnNurbsSurface.kOpen,
    om.MFnNurbsSurface.kClosed,
    om.MFnNurbsSurface.kPeriodic,
    om.MFnNurbsSurface.kLast
]

CURVE_FUNCTIONS = oma.MFnAnimCurve

try:
    mc.setAttr('hardwareRenderingGlobals.lineAAEnable', 1)
    mc.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)
except:
    pass


class MayaScene(object):

    tangents = {
        'auto': CURVE_FUNCTIONS.kTangentAuto,
        'clamped': CURVE_FUNCTIONS.kTangentClamped,
        'fast': CURVE_FUNCTIONS.kTangentFast,
        'fixed': CURVE_FUNCTIONS.kTangentFixed,
        'flat': CURVE_FUNCTIONS.kTangentFlat,
        'global': CURVE_FUNCTIONS.kTangentGlobal,
        'linear': CURVE_FUNCTIONS.kTangentLinear,
        'plateau': CURVE_FUNCTIONS.kTangentPlateau,
        'slow': CURVE_FUNCTIONS.kTangentSlow,
        'smooth': CURVE_FUNCTIONS.kTangentSmooth,
        'step': CURVE_FUNCTIONS.kTangentStep,
        'step_next': CURVE_FUNCTIONS.kTangentStepNext,
    }

    curve_types = {
        'time_to_angular': CURVE_FUNCTIONS.kAnimCurveTA,
        'time_to_linear': CURVE_FUNCTIONS.kAnimCurveTL,
        'time_to_time': CURVE_FUNCTIONS.kAnimCurveTT,
        'time_to_unitless': CURVE_FUNCTIONS.kAnimCurveTU,
        'unitless_to_angular': CURVE_FUNCTIONS.kAnimCurveUA,
        'unitless_to_linear': CURVE_FUNCTIONS.kAnimCurveUL,
        'unitless_to_time': CURVE_FUNCTIONS.kAnimCurveUT,
        'unitless_to_unitless': CURVE_FUNCTIONS.kAnimCurveUU,
        'unknown': CURVE_FUNCTIONS.kAnimCurveUnknown
    }

    infinity_types = {
        'constant': CURVE_FUNCTIONS.kConstant,
        'linear': CURVE_FUNCTIONS.kLinear,
        'cycle': CURVE_FUNCTIONS.kCycle,
        'cycle_relative': CURVE_FUNCTIONS.kCycleRelative,
        'oscilate': CURVE_FUNCTIONS.kOscillate,
    }

    def __init__(self):
        super(MayaScene, self).__init__()
        self.standalone = False
        self.mock = False
        self.loaded_plugins = []
        self.maya_version = mc.about(version=True)


    @staticmethod
    def get_file_info():
        """
        Get info stored in the scene
        :return: dict
        """
        def chunks(l, n):
            """
            splits a list into chunks
            """
            for i in range(0, len(l), n):
                yield l[i:i + n]

        data = dict()
        for chunk in chunks(mc.fileInfo(q=True), 2):
            data[chunk[0]] = chunk[1]
        return data

    @staticmethod
    def update_file_info(**kwargs):
        for key in kwargs:
            mc.fileInfo(key, kwargs[key])

    def select(self, *items, **kwargs):
        mc.select(*items, **kwargs)

    def reorderDeformers(self, *args, **kwargs):
        mc.reorderDeformers(*args, **kwargs)

    def reorder_deformers_by_type(self, nodes, deformer_level):
        """
        Reorders history for the given geometries. Reordering is based
        on each deformers type.
        :param nodes:
            Names of geometries to reorder history for.
        :param deformer_level:
            Specifies how soon each deformer type should appear in the
            stack. The lower the value the sooner {TYPE: LEVEL}.
        """

        for node in mc.ls(*nodes):
            deformers = mc.listHistory(
                node,
                pruneDagObjects=True,
                interestLevel=2,
            )

            deformer_stack = []
            for deformer in deformers:

                node_type = mc.nodeType(deformer)
                if node_type not in deformer_level:
                    continue

                stack_level = deformer_level[node_type]
                deformer_stack.append((stack_level, deformer))

            deformer_stack.sort(
                key=lambda x: x[0],
                reverse=True,
            )

            upper_lower = zip(
                deformer_stack[:-1],
                deformer_stack[1:],
            )
            for (_, upper), (_, lower) in upper_lower:
                mc.reorderDeformers(upper, lower, node)

    def keyframe(self, *args, **kwargs):
        return mc.keyframe(*args, **kwargs)

    def select_keyframes(self, curve_names, in_value=None):
        self.select(*curve_names, add=True)
        if in_value is not None:
            mc.selectKey(curve_names, replace=False, add=True, f=(in_value,))
        else:
            mc.selectKey(curve_names, replace=False, add=True)

    def create_ik_spline_handle(self, start_joint, end_joint, curve, solver, parent=None):
        return itl.create_ik_spline_handle(
            start_joint,
            end_joint,
            solver,
            curve,
            parent=parent
        )

    def fit_view(self, *args):
        try:
            if args:
                self.select(*args)
            mc.viewFit()
        except Exception, e:
            print e.message

    def get_selected_attribute_names(self):
        get_channelbox = mc.channelBox(
            'mainChannelBox',
            q=True,
            selectedMainAttributes=True
        )
        if not get_channelbox:
            return []
        return [str(x) for x in get_channelbox]

    def get_selected_nodes(self):
        nodes = []
        selection_list = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection_list)
        for i in range(0, selection_list.length()):
            m_object = om.MObject()
            selection_list.getDependNode(i, m_object)
            nodes.append(m_object)
        return nodes

    def get_selected_node_names(self):
        return [self.get_selection_string(x) for x in self.get_selected_nodes()]

    def get_dag_path(self, dag_node):
        return om.MDagPath.getAPathTo(dag_node)

    def delete(self, *args, **kwargs):
        mc.delete(*args, **kwargs)

    def initialize_plug(self, owner, name):
        return ptl.initialize_plug(owner, name)

    def create_plug(self, owner, key, **kwargs):
        return ptl.create_plug(owner, key, **kwargs)

    def get_plug_locked(self, plug):
        return plug.m_plug.isLocked()

    def set_plug_keyable(self, plug, value):
        mc.setAttr(plug, keyable=value)

    def get_plug_keyable(self, plug):
        return mc.getAttr(plug, keyable=True)

    def set_plug_locked(self, plug, value):
        mc.setAttr(plug, lock=value)

    def get_plug_hidden(self, plug):
        return mc.getAttr(plug, keyable=True)

    def set_plug_hidden(self, plug, value):
        if value is True:
            mc.setAttr(plug, keyable=False, channelBox=False)
        else:
            mc.setAttr(plug, keyable=True)

    def set_plug_value(self, plug, value):
        ptl.set_plug_value(plug, value)

    def get_plug_value(self, plug, *args):
        return ptl.get_plug_value(plug)

    def get_next_avaliable_plug_index(self, plug):
        return ptl.get_next_avaliable_plug_index(plug)

    def listHistory(self, *objects):
        return mc.listHistory(*objects)

    def hide(self, *objects):
        mc.hide(*objects)

    def showHidden(self, *objects):
        mc.showHidden(*objects)

    def parent(self, *args, **kwargs):
        mc.parent(*args, **kwargs)

    def rename(self, *args, **kwargs):
        return mc.rename(*args, **kwargs)

    def get_m_object(self, node_name):
        if isinstance(node_name, om.MObject):
            return node_name
        selection_list = om.MSelectionList()
        selection_list.add(node_name)
        m_object = om.MObject()
        selection_list.getDependNode(0, m_object)
        return m_object

    def create_loft_ribbon(self, positions, vector, parent, degree=2):
        return rtl.create_loft_ribbon(positions, vector, parent, degree=degree)

    def create_extrude_ribbon(self, positions, vector, parent, degree=2):
        return rtl.create_extrude_ribbon(positions, vector, parent, degree=degree)

    def get_m_object_type(self, m_object):
        dependency_node = om.MFnDependencyNode(m_object)
        return str(dependency_node.typeName())

    def is_dag_node(self, m_object):
        if 'dagNode' in mc.nodeType(self.get_selection_string(m_object), inherited=True):
            return True
        return False

    def nodeType(self, *args, **kwargs):
        return mc.nodeType(*args, **kwargs)

    def xform(self, *args, **kwargs):
        return mc.xform(*args, **kwargs)

    def assign_shading_group(self, shading_group_name, *node_names):
        for node_name in node_names:
            mc.sets(
                node_name,
                e=True,
                forceElement=shading_group_name
            )

    def sets(self, *args, **kwargs):
        mc.sets(*args, **kwargs)

    def deleteAttr(self, plug, **kwargs):
        mc.deleteAttr(plug, **kwargs)

    def listAttr(self, *args, **kwargs):
        return mc.listAttr(*args, **kwargs)

    def ls(self, *args, **kwargs):
        return mc.ls(*args, **kwargs)

    def file(self, *args, **kwargs):
        return mc.file(*args, **kwargs)

    def keyTangent(self, *args, **kwargs):
        return mc.keyTangent(*args, **kwargs)

    def parentConstraint(self, *args, **kwargs):
        mc.parentConstraint(*args, **kwargs)

    def scaleConstraint(self, *args, **kwargs):
        mc.scaleConstraint(*args, **kwargs)

    def aimConstraint(self, *args, **kwargs):
        mc.aimConstraint(*args, **kwargs)

    def setKeyframe(self, *args, **kwargs):
        return mc.setKeyframe(*args, **kwargs)

    def get_curve_data(self, node):
        return ctl.get_shape_data(node)

    def get_surface_data(self, node):
        return ctl.get_surface_shape_data(node)


    def listRelatives(self, *args, **kwargs):
        return mc.listRelatives(*args, **kwargs)

    def addAttr(self, *args, **kwargs):
        return mc.addAttr(*args, **kwargs)

    def get_selected_mesh_names(self):
        mesh_names = [self.get_selection_string(x) for x in self.get_selected_mesh_objects()]
        mesh_transforms = [mc.listRelatives(x, p=True)[0] for x in mesh_names]
        valid_mesh_names = []
        for transform in mesh_transforms:
            mesh_children = mc.listRelatives(transform, c=True, type='mesh')
            meshs = [x for x in mesh_children if not mc.getAttr('%s.intermediateObject' % x)]
            if len(meshs) == 1:
                valid_mesh_names.append(meshs[0])
        return valid_mesh_names

    def get_selected_nurbs_surface_names(self):
        surface_names = [self.get_selection_string(x) for x in self.get_selected_nurbs_surface_objects()]
        surface_transforms = [mc.listRelatives(x, p=True)[0] for x in surface_names]
        valid_surface_names = []
        for transform in surface_transforms:
            surface_children = mc.listRelatives(transform, c=True, type='nurbsSurface')
            surfaces = [x for x in surface_children if not mc.getAttr('%s.intermediateObject' % x)]
            if len(surfaces) == 1:
                valid_surface_names.append(surfaces[0])
        return valid_surface_names


    def convert_selection(self, **kwargs):
        mc.select(mc.polyListComponentConversion(mc.ls(sl=1), **kwargs))

    def namespace(self, *args, **kwargs):
        return mc.namespace(*args, **kwargs)

    def refresh(self):
        mc.refresh()

    def dg_dirty(self):
        mel.eval('dgdirty -a')

    def lock_node(self, *nodes, **kwargs):
        mc.lockNode(*nodes, **kwargs)

    def set_deformer_weights(self, m_deformer, weights):
        dtl.set_deformer_weights(m_deformer, weights)

    def get_deformer_weights(self, m_deformer):
        return dtl.get_deformer_weights(m_deformer)

    def create_nonlinear_deformer(self, deformer_type, geometry, **kwargs):
        return ntl.create_nonlinear_deformer(deformer_type, geometry, **kwargs)

    def add_deformer_geometry(self, deformer, geometry):
        for g in geometry:
            mc.deformer(deformer, e=True, g=g)

    def remove_deformer_geometry(self, deformer, geometry):
        for g in geometry:
            mc.deformer(deformer, e=True, g=g, rm=True)

    def find_skin_cluster(self, node):
        for history_node in mc.listHistory(self.get_selection_string(node)):
            if mc.nodeType(history_node) == 'skinCluster':
                return self.get_m_object(history_node)

    def get_skin_weights(self, node):
        return sss.getWeights(node)

    def set_skin_weights(self, node, weights):
        return sss.setWeights(node, weights)

    def get_skin_influences(self, node):
        return sss.get_skin_influences(node)

    def set_skin_as(self, skin_cls=None, target_objects=""):
        return sss.skin_as(skin_cls=skin_cls, target_objects=target_objects)

    @flatten_args
    def skinCluster(self, *args, **kwargs):
        return mc.skinCluster(*[str(x) for x in args], **kwargs)

    @flatten_args
    def rebuildSurface(self, *args, **kwargs):
        return mc.rebuildSurface(*[str(x) for x in args], **kwargs)

    def create_corrective_geometry(self, *args, **kwargs):
        return mtl.create_corrective_geometry(*args, **kwargs)

    def get_closest_vertex_index(self, mesh, point):
        return mtl.get_closest_vertex_index(mesh, om.MPoint(*point))

    def get_closest_vertex_uv(self, mesh, point):
        return mtl.get_closest_vertex_uv(mesh, om.MPoint(*point))

    def get_closest_face_index(self, mesh, position):
        return mtl.get_closest_face_index(mesh, position)

    def get_vertex_count(self, mesh):
        return mtl.get_vertex_count(mesh)

    def get_meshs(self, node_name):
        return mtl.get_meshs(node_name)

    def create_shard_mesh(self, mesh_name, parent_m_object):
        if not mesh_name:
            raise Exception('you must provide a name for the mesh')
        return mtl.create_shard_mesh(mesh_name, parent_m_object)

    def flip_blendshape_weights(self, *args, **kwargs):
        btl.flip_blend_shape_weights(*args, **kwargs)

    def get_blendshape_target_index_list(self, blendshape, mesh, index):
        funcs = oma.MFnBlendShapeDeformer(blendshape)
        result = om.MIntArray()
        funcs.targetItemIndexList(index, mesh, result)
        return [result[x] for x in range(result.length())]

    def get_blendshape_weight_index_list(self, blendshape):
        funcs = oma.MFnBlendShapeDeformer(blendshape)
        result = om.MIntArray()
        funcs.weightIndexList(result)
        return [result[x] for x in range(result.length())]

    def create_blendshape(self, *geometry, **kwargs):
        return btl.create_blendshape(*geometry, **kwargs)

    def add_blendshape_base_geometry(self, blendshape, *geometry):
        return btl.add_base_geometry(blendshape, *geometry)

    def create_blendshape_target(self, *args):
        btl.add_target(*args)

    def remove_blendshape_target(self, *args):
        btl.remove_target(*args)

    def clear_blendshape_group_targets(self, *args):
        btl.clear_group_targets(*args)

    def clear_blendshape_targets(self, *args):
        btl.clear_targets(*args)

    def list_selected_vertices(self):
        component_selection = mc.filterExpand(sm=(31, 32, 34))
        if component_selection:
            return mc.ls(mc.polyListComponentConversion(
                component_selection,
                toVertex=True),
                fl=True
            )
        return []

    def polyListComponentConversion(self, *args, **kwargs):
        return mc.polyListComponentConversion(*args, **kwargs)

    def get_selected_mesh_objects(self):
        return mtl.get_selected_mesh_objects()

    def get_selected_nurbs_surface_objects(self):
        return nsl.get_selected_nurbs_surface_objects()

    def get_nurbs_surface_objects(self, x):
        return nsl.get_nurbs_surface_objects(x)

    def get_selected_transform_names(self):
        return stl.get_selected_transform_names()

    def get_selected_transforms(self):
        return stl.get_selected_transforms()

    def get_mesh_objects(self, x):
        return mtl.get_mesh_objects(x)

    def copy_selected_mesh_shape(self, mesh):
        mesh_functions = om.MFnMesh(mesh)
        mesh_points = om.MFloatPointArray()
        mesh_functions.getPoints(mesh_points)
        for selected_mesh in self.get_selected_mesh_objects():
            source_mesh_functions = om.MFnMesh(selected_mesh)
            source_points = om.MFloatPointArray()
            source_mesh_functions.getPoints(source_points)
            if mesh_points.length() == source_points.length():
                self.copy_mesh_shape(selected_mesh, mesh)

    def copy_mesh_shape(self, mesh_1, mesh_2):
        mesh_1_name = self.get_selection_string(mesh_1)
        mesh_2_name = self.get_selection_string(mesh_2)
        mc.connectAttr('%s.outMesh' % mesh_1_name, '%s.inMesh' % mesh_2_name)
        self.refresh()
        mc.disconnectAttr('%s.outMesh' % mesh_1_name, '%s.inMesh' % mesh_2_name)
        self.refresh()

    def update_mesh(self, mesh):
        mesh_functions = om.MFnMesh(mesh)
        mesh_functions.updateSurface()

    def copy_mesh_in_place(self, mesh_1, mesh_2):
        mesh_functions_2 = om.MFnMesh(mesh_2)
        mesh_functions_2.copyInPlace(mesh_1)
        mesh_functions_2.updateSurface()

    def get_skin_data(self, node):
        node_name = self.get_selection_string(node)
        return dict(
            geometry=mc.skinCluster(node_name, geometry=True, q=True)[0],
            joints=mc.skinCluster(node_name, influence=True, q=True),
            weights=self.get_skin_weights(node)
        )

    def set_delta_mush_data(self, data):
        return dmu.set_delta_mush_data(data)

    def get_delta_mush_data(self, node):
        return dmu.get_delta_mush_data(node)

    def find_deformer_node(self, *args, **kwargs):
        return dtl.find_deformer_node(*args, **kwargs)

    def get_wrap_data(self, node):
        return wru.get_wrap_data(node)

    def create_wrap(self, data):
        return wru.create_wrap(data)

    def export_alembic(self, path, *roots):
        self.loadPlugin('AbcExport')
        mc.AbcExport(j="-frameRange 1 1 %s -file %s" % (
            ' '.join(['-root %s' % x for x in roots]),
            path,

        ))

    def AbcImport(self, path):
        self.loadPlugin('AbcImport')
        mc.AbcImport(
            path,
            mode='import'
        )

    def AbcExport(self, path, *roots):
        self.loadPlugin('AbcExport')
        mc.AbcExport(j="-frameRange 1 1 %s -file %s" % (
            ' '.join(['-root %s' % x for x in roots]),
            path,

        ))

    def import_geometry(self, path, namespace=None):
        """
        Maybe this is no longer needed ???
        """
        if namespace is None:
            name_space = 'import_alembic'
        if not mc.namespace(exists=':%s' % name_space):
            mc.namespace(add=name_space)
        mc.namespace(set=name_space)
        if not os.path.exists(path):
            raise IOError('Geometry file does not exist: %s' % path)
        if path.endswith('.abc'):
            self.loadPlugin('AbcImport')
            mc.AbcImport(
                path,
                mode='import'
            )
        else:
            mc.file(path, i=True)
        mc.namespace(set=':')
        assemblies = mc.ls('%s:*' % name_space, assemblies=True)
        if len(assemblies) < 1:
            mc.delete(mc.ls('%s:*' % name_space))
            raise Exception('Import import contained no assemblies')
        root_m_objects = [self.get_m_object(x) for x in assemblies]
        if mc.namespace(exists=':%s' % name_space):
            mc.namespace(rm=name_space, mergeNamespaceWithRoot=True)
        return [self.get_selection_string(x) for x in root_m_objects]

    def create_from_skin_data(self, data):
        geometry_name = data['geometry']
        existing_skin = mel.eval('findRelatedSkinCluster %s' % geometry_name)
        if existing_skin:
            skin_name = existing_skin
        else:
            skin_name = mc.skinCluster(
                data['geometry'],
                data['joints'],
                tsb=True
            )[0]
        m_object = self.get_m_object(skin_name)
        weights = data.get('weights', None)
        if weights:

            # TEMP UNTILL WE SWITCH OVER TO NEW WEIGHT FORMAT
            def setWeights(skin_name, weights):

                geometry = mc.skinCluster(skin_name, q=True, geometry=True)
                influences = mc.skinCluster(skin_name, q=True, influence=True)
                if geometry:
                    for itr in range(len(geometry)):
                        # poly mesh and skinCluster name
                        shapeName = geometry[itr]
                        # unlock influences used by skincluster
                        for influence in influences:
                            mc.setAttr('%s.liw' % influence, False)
                        # normalize needs turned off for the prune to work
                        skinNorm = mc.getAttr('%s.normalizeWeights' % skin_name)
                        if skinNorm != 0:
                            mc.setAttr('%s.normalizeWeights' % skin_name, 0)
                        mc.skinPercent(skin_name, shapeName, nrm=False, prw=100)
                        # restore normalize setting
                        if skinNorm != 0:
                            mc.setAttr('%s.normalizeWeights' % skin_name, skinNorm)
                        for vertId, weightData in weights[itr].items():
                            wlAttr = '%s.weightList[%s]' % (skin_name, vertId)
                            for infIndex, infValue in weightData.items():
                                wAttr = '.weights[%s]' % infIndex
                                mc.setAttr(wlAttr + wAttr, infValue)
            setWeights(skin_name, weights)
        return m_object

    def find_related_skin_cluster(self, geometry_name):
        existing_skin = mel.eval('findRelatedSkinCluster %s' % geometry_name)
        if existing_skin:
            return existing_skin

    def get_selected_vertex_indices(self, *args):
        return mtl.get_selected_vertex_indices(*args)


    def get_key_value(self, animation_curve, in_value):
        anim_curve_functions = oma.MFnAnimCurve(animation_curve)
        index_utility = om.MScriptUtil()
        index_utility.createFromInt(0)
        index_pointer = index_utility.asUintPtr()
        anim_curve_functions.find(in_value, index_pointer)
        index = om.MScriptUtil.getUint(index_pointer)
        return anim_curve_functions.value(index)

    def get_animation_curve_value_at_index(self, animation_curve, current_in_value):
        return atl.get_value_at_index(
            animation_curve,
            current_in_value
        )

    def change_keyframe(self, animation_curve, current_in_value, **kwargs):
        atl.change_keyframe(animation_curve, current_in_value, **kwargs)

    def delete_keyframe(self, animation_curve, in_value):
        atl.delete_keyframe(animation_curve, in_value)

    def add_keyframe(self, animation_curve, in_value, out_value, **kwargs):
        atl.add_keyframe(animation_curve, in_value, out_value, **kwargs)

    def selectKey(self, *args, **kwargs):
        mc.selectKey(*args, **kwargs)

    def cutKey(self, *args, **kwargs):
        return mc.cutKey(*args, **kwargs)

    def aliasAttr(self, *args, **kwargs):
        return mc.aliasAttr(*args, **kwargs)

    def create_animation_curve(self, m_plug, **kwargs):
        return atl.create_animation_curve(m_plug, **kwargs)

    def create_dag_node(self, *args):
        m_object = om.MFnDagNode().create(*args)
        return m_object

    def create_depend_node(self, *args):
        return om.MFnDependencyNode().create(*args)

    def create_keyframe(self, curve, *args):
        animation_curve = oma.MFnAnimCurve(curve)
        animation_curve.addKey(*args)

    def create_ik_handle(self, start_joint, end_effector, solver='ikSCsolver', name=None, parent=None):
        return itl.create_ik_handle(
            start_joint,
            end_effector,
            solver=solver,
            name=name,
            parent=parent
        )

    #@m_object_arg
    def get_constrained_node(self, constraint):
        constraint_string = constraint
        constraint_type = self.nodeType(constraint_string)

        if constraint_type == 'pointConstraint':
            out_attributes = [
                'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ'
            ]
        elif constraint_type == 'parentConstraint':
            out_attributes = [
                'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ',
                'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'
            ]
        elif constraint_type == 'orientConstraint':
            out_attributes = [
                'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'
            ]
        elif constraint_type == 'scaleConstraint':
            out_attributes = [
                'constraintScaleX', 'constraintScaleY', 'constraintScaleZ'
            ]
        else:
            raise StandardError('Unsupported constraint type "%s"' % constraint_type)

        connected_nodes = set()
        for attribute in out_attributes:
            nodes = self.listConnections('%s.%s' % (constraint_string, attribute), d=True, s=False, scn=True, p=False)
            if nodes:
                connected_nodes.update(nodes)

        if len(connected_nodes) > 1:
            raise StandardError('Multiple constrained nodes not supported.')

        if len(connected_nodes) < 1:
            raise StandardError('No node was controlled by the constraint')

        return list(connected_nodes)[0]

    #@m_object_arg
    def get_constraint_data(self, constraint):
        #consraint_name = self.get_selection_string(constraint)
        consraint_name = constraint
        constraint_type = self.nodeType(consraint_name)
        parent=None
        get_parent = mc.listRelatives(consraint_name, p=True)
        if get_parent:
            parent = get_parent[0]
        if constraint_type == 'pointConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.pointConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'parentConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.parentConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'orientConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.orientConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'scaleConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.scaleConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        else:
            print 'Warning: Constraint type "%s" not supported. skipping...' % constraint_type

    def create_constraint(self, constraint_type, *transforms, **kwargs):
        name = kwargs.pop('name', None)
        parent = kwargs.pop('parent', None)
        targets = [self.get_selection_string(x) for x in transforms]
        clean_kwargs = dict()
        for key in kwargs:
            clean_kwargs[str(key)] = kwargs[key]
        short_name = mc.__dict__[constraint_type](
            *targets,
            **clean_kwargs
        )[-1]
        long_names = mc.ls(short_name, long=True)
        constraint_name = long_names[-1]
        m_object = self.get_m_object(constraint_name)
        constraint_name = mc.rename(constraint_name, name)
        if parent:
            parent_name = self.get_selection_string(parent)
            if mc.listRelatives(constraint_name, p=True)[0] != parent_name:
                mc.parent(
                    constraint_name,
                    parent_name
                )
        return m_object

    @staticmethod
    def draw_nurbs_surface(positions, knots_u, knots_v, degree_u, degree_v, form_u, form_v, name, parent):
        create_2d = False
        rational = False
        point_array = om.MPointArray()
        knots_array_u = om.MDoubleArray()
        knots_array_v = om.MDoubleArray()
        for p in positions:
            point_array.append(om.MPoint(*p))
        for k in knots_u:
            knots_array_u.append(k)
        for k in knots_v:
            knots_array_v.append(k)
        args = [
            point_array,
            knots_array_u,
            knots_array_v,
            degree_u,
            degree_v,
            form_u,
            form_v,
            rational,
            parent
        ]
        m_object = om.MFnNurbsSurface().create(*args)
        om.MFnDependencyNode(m_object).setName(name)
        return m_object

    @staticmethod
    def draw_nurbs_curve(positions, degree, form, name, parent):
        create_2d = False
        rational = False
        spans = len(positions) - degree
        point_array = om.MPointArray()
        knots_array = om.MDoubleArray()
        for p in positions:
            point_array.append(om.MPoint(*p))
        for k in calculate_knots(spans, degree, form):
            knots_array.append(k)
        args = [
            point_array,
            knots_array,
            degree,
            NURBS_CURVE_FORMS[form],
            create_2d,
            rational,
            parent
        ]
        m_object = om.MFnNurbsCurve().create(*args)
        om.MFnDependencyNode(m_object).setName(name)
        return m_object

    def create_shader(self, node_type, name):
        node_name = mc.shadingNode(
            node_type,
            name=name,
            asShader=True
        )
        return self.get_m_object(node_name)

    def create_shading_group(self, name):
        node_name = mc.sets(
            name=name,
            empty=True,
            renderable=True,
            noSurfaceShader=True
        )
        return self.get_m_object(node_name)

    def connect_plugs(self, plug_1, plug_2):
        graph_modifier = om.MDGModifier()
        graph_modifier.connect(
            plug_1,
            plug_2
        )
        graph_modifier.doIt()

    def disconnect_plugs(self, plug_1, plug_2):
        graph_modifier = om.MDGModifier()
        graph_modifier.disconnect(
            plug_1,
            plug_2
        )
        graph_modifier.doIt()

    @flatten_args
    def get_bounding_box_center(self, *nodes):
        bbox = mc.exactWorldBoundingBox(*[str(x) for x in nodes])
        center_x = (bbox[0] + bbox[3]) / 2.0
        center_y = (bbox[1] + bbox[4]) / 2.0
        center_z = (bbox[2] + bbox[5]) / 2.0
        return round(center_x, 5), round(center_y, 5), round(center_z, 5)

    @flatten_args
    def get_bounding_box(self, *nodes):
        return mc.exactWorldBoundingBox(*[str(x) for x in nodes])

    def get_selection_string(self, item):
        if isinstance(item, basestring):
            item = self.get_m_object(item)
        if isinstance(item, om.MObject):
            m_object = item
            selection_list = om.MSelectionList()
            selection_list.add(m_object)
            selection_strings = []
            selection_list.getSelectionStrings(0, selection_strings)
            return selection_strings[0]
        else:
            raise Exception('Cannot get_selection_string for type: "%s"' % type(item))

    def set_xray_panel(self, value):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                if value:
                    mc.modelEditor(p, jointXray=True, e=True)
                    mel.eval('setXrayOption true %s' % p)
                else:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=False, e=True)

        else:
            print 'No panels to isolate'

    def set_xray_joints_panel(self, value):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                if value:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=True, e=True)
                else:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=False, e=True)

        else:
            print 'No panels to isolate'

    def isolate(self, *objects):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            mc.select(*objects)
            for p in panels:
                mel.eval('enableIsolateSelect %s 1' % p)
            mel.eval('fitPanel - selectedNoChildren;')

        else:
            print 'No panels to isolate'

    def deisolate(self):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                mc.isolateSelect(p, state=0)
        else:
            print 'No panels to deisolate'

    def get_reverse_index_lists(self, meshs):
        return mtl.get_reverse_index_lists(meshs)

    def create_mirrored_geometry(self, target_meshs, base_meshs, reverse_index_lists=None):
        return mtl.create_mirrored_geometry(
            target_meshs,
            base_meshs,
            reverse_index_lists=reverse_index_lists
        )

    def copy_mesh(self, mesh, parent_transform):
        return om.MFnMesh().copy(mesh, parent_transform)

    def attributeQuery(self, *args, **kwargs):
        return mc.attributeQuery(*args, **kwargs)

    def getAttr(self, *args, **kwargs):
        return mc.getAttr(*args, **kwargs)

    def setAttr(self, *args, **kwargs):
        return mc.setAttr(*args, **kwargs)

    def objExists(self, *args, **kwargs):
        return mc.objExists(*args, **kwargs)

    def listConnections(self, *args, **kwargs):
        return mc.listConnections(*args, **kwargs)

    def disconnectAttr(self, *args, **kwargs):
        return mc.disconnectAttr(*args, **kwargs)

    def connectAttr(self, *args, **kwargs):
        return mc.connectAttr(*args, **kwargs)

    def loadPlugin(self, plugin_name):
        if plugin_name not in self.loaded_plugins:
            mc.loadPlugin(plugin_name)
            self.loaded_plugins.append(plugin_name)

    def check_visibility(self, node):
        """
        check if obj is a dagNode
        check if obj is visible by...
        --visible attribute of item and it's ancestors
        --item's display layer's visibility
        --checks if panels' Show>Polygons is checked on or off
        """
        visible_status = False
        try:
            if mc.objectType(node, isAType='dagNode'):
                visible_status = mc.getAttr(str(node) + '.visibility')
                if mc.getAttr(str(node) + '.overrideEnabled'):
                    visible_status = visible_status and mc.getAttr(str(node) + '.overrideVisibility')
                if (mc.listRelatives(node, parent=True)[0] is not None) is True:
                    node_parent = mc.listRelatives(node, parent=True)[0]
                    visible_status = visible_status and self.check_visibility(node_parent)
                panels = mc.getPanel(type='modelPanel')
                if panels:
                    panel_polymesh_list = []
                    for panel_name in panels:
                        visible_status = visible_status and mc.modelEditor(panel_name, q=True, polymeshes=True)
                        panel_polymesh_list.append(visible_status)
                    visible_status = visible_status and any(panel_polymesh_list)
        except Exception, e:
            warnings.warn(e.message, DeprecationWarning)
        return visible_status

    def lock_all_plugs(self, node, skip=None):
        get_keyable = mc.listAttr(node, keyable=True)
        if get_keyable:
            for attr in get_keyable:
                plug_string = node + '.' + attr
                if not skip or plug_string not in skip:
                    if mc.objExists(plug_string):
                        mc.setAttr(
                            plug_string,
                            lock=True,
                            keyable=False,
                            channelBox=False
                        )

    def set_skincluster_influence_weights(self, node, index, weights, **kwargs):
        return sku.set_influence_weights(
            node,
            index,
            weights,
            **kwargs
        )

    def get_skincluster_influence_weights(self, node, index, **kwargs):
        return sku.get_influence_weights(
            node,
            index,
            **kwargs
        )

    def get_skincluster_weights(self, node, **kwargs):
        return sku.get_weights(
            node,
            **kwargs
        )

    def set_skincluster_weights(self, node, weights, **kwargs):
        return sku.set_weights(
            node,
            weights,
            **kwargs
        )

    @staticmethod
    def create_text_curve(*args):
        return ctl.create_text_curve(*args)

    @staticmethod
    def get_closest_surface_uv(surface, point):
        return nsl.get_closest_uv(surface, point)

    @staticmethod
    def get_closest_surface_point(surface, point):
        point = nsl.get_closest_point(surface, point)
        return point[0], point[1], point[2]

    @staticmethod
    def get_closest_mesh_uv(mesh, point):
        return mtl.get_closest_mesh_uv(mesh, point)

    def delete_unused_nodes(self):
        try:
            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        except StandardError, e:
            print e

    def create_lattice(self, *args, **kwargs):
        return lut.create_lattice(*args, **kwargs)

    def create_wire_deformer(self, curve, *geometry, **kwargs):
        return wir.create_wire_deformer(curve, *geometry, **kwargs)

    def undoInfo(self, *args, **kwargs):
        mc.undoInfo(*args, **kwargs)

    def create_curve_from_vertices(self, curve_from_surface):

        """
        This can all be done from create function using objects..
        doesnt need to use scene, cmds or OpenMaya
        """
        parent = curve_from_surface.parent
        vertices = curve_from_surface.vertices
        points = [component.split('.')[-1] for component in vertices]
        mesh_name = curve_from_surface.mesh_name

        poly_edge_to_curve_name = mc.createNode('polyEdgeToCurve')
        nurbs_curve_name = mc.createNode('nurbsCurve', parent=parent)

        connections = [
            (
                mesh_name + '.displaySmoothMesh',
                poly_edge_to_curve_name + '.displaySmoothMesh',
            ), (
                mesh_name + '.outMesh',
                poly_edge_to_curve_name + '.inputPolymesh',
            ), (
                mesh_name + '.outSmoothMesh',
                poly_edge_to_curve_name + '.inputSmoothPolymesh',
            ), (
                mesh_name + '.smoothLevel',
                poly_edge_to_curve_name + '.smoothLevel',
            ), (
                mesh_name + '.worldMatrix[0]',
                poly_edge_to_curve_name + '.inputMat',
            ), (
                poly_edge_to_curve_name + '.outputcurve',
                nurbs_curve_name + '.create',
            ),
        ]
        for connection in connections:
            mc.connectAttr(*connection)

        mc.setAttr(
            poly_edge_to_curve_name + '.inputComponents',
            len(points),
            *points,
            type='componentList'
        )

        mc.setAttr(poly_edge_to_curve_name + '.form', curve_from_surface.form)
        mc.setAttr(poly_edge_to_curve_name + '.degree', curve_from_surface.degree)

        m_object = self.get_m_object(nurbs_curve_name)
        construction_history = self.get_m_object(poly_edge_to_curve_name)

        om.MFnDependencyNode(m_object).setName(
            curve_from_surface.name,
        )
        om.MFnDependencyNode(construction_history).setName(
            curve_from_surface.name + 'polyEdgeToCurve',
        )

        curve_from_surface.m_object = m_object
        curve_from_surface.construction_history = [construction_history]

    def createNode(self, *args, **kwargs):
        return mc.createNode(*args, **kwargs)

    def autoKeyframe(self, *args, **kwargs):
        return mc.autoKeyframe(*args, **kwargs)


def calculate_knots(spans, degree, form):

    knots = []
    knot_count = spans + 2*degree -1

    if form == 2:
        pit = (degree-1)*-1
        for itr in range(knot_count):
            knots.append(pit)
            pit += 1
        return knots

    for itr in range(degree):
        knots.append(0)
    for itr in range(knot_count - (degree*2)):
        knots.append(itr+1)
    for kit in range(degree):
        knots.append(itr+2)
    return knots