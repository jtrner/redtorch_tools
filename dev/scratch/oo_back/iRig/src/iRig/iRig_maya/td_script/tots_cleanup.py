"""Provides toolkit functions for prepping rigs prior publish."""

# import standard modules
from timeit import default_timer as timer

# import maya modules
from maya import cmds
from maya import mel
from maya import OpenMaya as api0
from maya import OpenMayaAnim as api0Anim

try:
    import facebake_manual
except ImportError:
    print('[Facebake Manual] :: Import Failure.')

try:
    import tots_fixDisplayColours
except ImportError:
    print('[Fix Display Colours] :: Import Failure.')

try:
    import tots_fix_exportDataReconnect
except ImportError:
    print('[Fix Export Data] :: Import Failure.')

# define global variables
GLOBAL_SCALE_NODE = 'RigScaleOffset_MD'

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Michael Taylor", "Alison Chan"]
__license__ = "Icon License"
__version__ = "1.1.1"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def _get_skin_fn(skin_str=''):
    """
    From skin cluster string provided, return a skin cluster fn object.
    :param skin_str: <str> Skin cluster node.
    """
    if not skin_str:
        return False
    m_sel = api0.MSelectionList()
    m_sel.add(skin_str)
    m_obj = api0.MObject()
    try:
        m_sel.getDependNode(0, m_obj)
    except RuntimeError:
        return False

    return api0Anim.MFnSkinCluster(m_obj)


def _get_mesh_from_skin(skin_str=''):
    """
    Gets the MFnMesh from the skinCluster string.
    :return: <MFnMesh> if successful, <bool> False if fail.
    """
    skin_fn = _get_skin_fn(skin_str)
    mfn_set = skin_fn.deformerSet()
    mesh_fn = False
    it_dg = api0.MItDependencyGraph(mfn_set, api0.MItDependencyGraph.kUpstream, api0.MItDependencyGraph.kPlugLevel)
    while not it_dg.isDone():
        cur_item = it_dg.thisNode()
        if cur_item.hasFn(api0.MFn.kMesh):
            mesh_fn = api0.MFnMesh(cur_item)
            break
        it_dg.next()

    return mesh_fn


def unlock_joints():
    """
    Unlocks all bind-type joints.
    :return: <bool> True for success.
    """
    bnd_jnts_ls = cmds.ls('*Bnd_Jnt.liw')
    if bnd_jnts_ls:
        for bnd_jnt in bnd_jnts_ls:
            cmds.setAttr(bnd_jnt, 0)

        mel.eval('catchQuiet(`artAttrSkinProperties`);')
    return True


def util_connect_attr(out_attr, in_attr):
    """
    Connects the attributes safely.
    :param out_attr: <str> outgoing node connection attribute.
    :param in_attr: <str> incoming node connection attribute.
    :return: <bool> True for success.
    """
    # check if there is something connected to the input attribute
    if cmds.listConnections(in_attr, s=1, d=0, plugs=1):
        return True
    # check the connection first before connecting to the input attr.
    if not cmds.isConnected(out_attr, in_attr):
        cmds.connectAttr(out_attr, in_attr, f=1)
    return True


def connect_tweaks_scale():
    """
    Scale connections for the tweak controllers + follicles.
    :return: <bool> True for success.
    """
    print 'connect tweak scale'
    follicles = cmds.ls('*_Pin_FlcShape', type='follicle')
    if not follicles:
        return True

    # add scale to follicles
    follicles_nodes = [cmds.listRelatives(x, p=1)[0] for x in follicles]
    for flc in follicles_nodes:
        # connect the follicle nodes
        util_connect_attr('RigScaleOffset_MD.outputX', flc + '.sx')
        util_connect_attr('RigScaleOffset_MD.outputY', flc + '.sy')
        util_connect_attr('RigScaleOffset_MD.outputZ', flc + '.sz')


    # add scales to pin controls
    pin_ctrl_offsets = cmds.ls('*_Flc_Pin_Ctrl_Offset_Grp')
    #R_Logo_Diaper_Geo_Ctrl_Offset_Grp_Flc_Pin_Ctrl_Offset_Grp

    for ea_pin_ctrl_offset in pin_ctrl_offsets:
        # add scale from follicle to pin control
        par_cnst = cmds.listConnections(ea_pin_ctrl_offset, destination=False, source=True, type='parentConstraint', plugs=0)[0]
        par_fol = cmds.listConnections(par_cnst, destination=False, source=True, plugs=0)[-2]
        scl_cnst = cmds.listConnections(ea_pin_ctrl_offset, destination=True, source=False, type='scaleConstraint', plugs=0)


        if not scl_cnst:
            cmds.scaleConstraint(par_fol, ea_pin_ctrl_offset, maintainOffset=True)


        # add scales from pin control to pinned control
        ea_pin_ctrl = ea_pin_ctrl_offset.replace('Flc_Pin_Ctrl_Offset_Grp', 'Flc_Pin_Ctrl')

        #check if control is affecting something first.
        if cmds.listConnections(ea_pin_ctrl, destination=True, source=False, type='parentConstraint', plugs=0):
            par_cnst = cmds.listConnections(ea_pin_ctrl, destination=True, source=False, type='parentConstraint', plugs=0)[0]
            ctrl_offset = cmds.listConnections(par_cnst, destination=True, source=False, plugs=0, type='transform')[-2]
            scl_cnst = cmds.listConnections(ctrl_offset, destination=True, source=False, type='scaleConstraint', plugs=0)
            if not scl_cnst:
                cmds.scaleConstraint(ea_pin_ctrl, ctrl_offset, maintainOffset=True)
        else:
            #delete if it's not being used
            cmds.delete(ea_pin_ctrl_offset)

    # remove scale from tweak groups
    if cmds.objExists('Tweak_Ctrls_Grp_scaleConstraint1'):
        cmds.delete('Tweak_Ctrls_Grp_scaleConstraint1')

    return True


def check_anim_unit_time(anim_node=''):
    """
    Checks if there is a unit to Time conversion node attached to the anim curve node.
    :param anim_node: <str> animation node to check connections from.
    :param anim_node: <list> if in a list format, check them all.
    :returns: <bool> if unitToTimeConversion node if found connected to the anim node.
    """
    unit_list = lambda an: cmds.listConnections(('{}.input').format(an), s=1, d=0, type='unitToTimeConversion')
    conversion_nodes = []
    if isinstance(anim_node, (tuple, list)):
        for an in anim_node:
            un = unit_list(an)
            if un:
                continue
            conversion_nodes.append(un)

    else:
        un = unit_list(anim_node)
        if un:
            conversion_nodes.append(un)
    return bool(conversion_nodes)


def prune_skin_weights(weight=0.001):
    """
    Prunes skin cluster mesh only weights by the float value provided.
    :param weight: <float> prune all skins at this weight value.
    """
    skins = cmds.ls(type='skinCluster')
    for skin in skins:
        mesh_obj = _get_mesh_from_skin(skin)
        if mesh_obj:
            cmds.skinPercent(skin, mesh_obj.name(), prw=0.01)

    return True


def remove_unused_skin_influences():
    """
    Removes joints with values of 0.0 on .
    :param ctrl_name: <str> if specified, removes all keyframes from this controller name.
    :return: <bool> True for success. <bool> False for failure.
    """
    skins = cmds.ls(type='skinCluster')
    if not skins:
        return False
    for skin in skins:
        try:
            rm_count = mel.eval(('removeUnusedForSkin("{}", 1)').format(skin))
            if rm_count:
                print ('[Remove Unused Skin Influences] :: <{}> {}').format(skin, rm_count)
        except RuntimeError:
            print ('[Remove Unused Skin Influences] :: Invalid skin object: {}').format(skin)

    return True


def delete_ctrl_keyframes(control_name=''):
    """
    Removes selected controller keyframes.
    :param ctrl_name: <str> if specified, removes all keyframes from this controller name.
    :return: <bool> True for success.
    """
    anim_nodes = []
    anim_curves = [
     'animCurveTL',
     'animCurveTU',
     'animCurveTA',
     'animCurveTT',
     'animCurveUL',
     'animCurveUA',
     'animCurveUT',
     'animCurveUU']
    if control_name:
        for anim_node in anim_curves:
            anim_ls = cmds.listConnections(control_name, s=1, d=0, type=anim_node)
            if not anim_ls:
                continue
            for anm in anim_ls:
                if not check_anim_unit_time(anm):
                    anim_nodes.append(anm)

        if anim_nodes:
            print ('[Deletes Keyframe Node] :: {} <<< <{}> {}').format(control_name, anim_node, anim_ls)
    else:
        for ctrl_name in cmds.ls('*_Ctrl'):
            for anim_node in anim_curves:
                anim_ls = cmds.listConnections(ctrl_name, s=1, d=0, type=anim_node)
                if not anim_ls:
                    continue
                for anm in anim_ls:
                    if not check_anim_unit_time(anm):
                        anim_nodes.append(anm)

    if anim_nodes:
        print anim_nodes
        for node in anim_nodes:
            cmds.delete(node)
    return True


def set_dynamic_settings():
    """
    Sets the dynamic settings for cleanup.
    :return: <bool> True for success.
    """
    dynamics_ctrl = 'Dynamic_Ctrl'
    if cmds.objExists(dynamics_ctrl):
        cmds.setAttr(('{}.DynamicsOnOff').format(dynamics_ctrl), 0)
        cmds.setAttr(('{}.DynamicsCtrl').format(dynamics_ctrl), 1)
        cmds.setAttr(('{}.Collider').format(dynamics_ctrl), 0)
    return True


def set_face_settings():
    """
    Sets the face settings for cleanup.
    :return: <bool> True for success.
    """
    face_panel = 'Face_Gui_Ctrl'
    if cmds.objExists(face_panel):
        face_attr = face_panel + '.OnFaceCtrlVis'
        if cmds.objExists(face_attr):
            cmds.setAttr(face_attr, 1)
        if all(map(cmds.objExists, ['Face_R_Eye_Lid_Lwr_Ctrl', 'Face_R_Eye_Lid_Upr_Ctrl'])):
            try:
                facebake_manual.eyeFix()
            except Exception as error:
                api0.MGlobal.displayError(('[Face Settings Error] :: Problem with eye mirrror, {}').format(error))

        if not cmds.objExists('Face_Ctrl_Grp_scaleConstraint1'):
            cmds.scaleConstraint('C_Head_Gimbal_Ctrl', 'Face_Ctrl_Grp')
        if not cmds.objExists('Follow_Drivers_Grp_scaleConstraint1'):
            cmds.scaleConstraint('Root_Ctrl', 'Follow_Drivers_Grp')
    return True


def reset_mesh_display():
    """
    Parse through the referenced mesh and set the smoothness level.
    :return: <bool> True for success.
    """
    override_attr = '.overrideEnabled'
    template_attr = '.template'
    scene_node_gen = api0.MItDependencyNodes(api0.MFn.kMesh)
    while not scene_node_gen.isDone():
        m_obj = scene_node_gen.item()
        m_dag = api0.MDagPath.getAPathTo(m_obj)
        mesh_name = m_dag.partialPathName()
        m_sel = api0.MSelectionList()
        m_sel.add(mesh_name)
        m_node = api0.MObject()
        m_sel.getDependNode(0, m_node)
        m_dag_fn = api0.MFnDagNode(m_node)
        par_node = m_dag_fn.parent(0)
        m_par_dag = api0.MDagPath.getAPathTo(par_node)
        if m_par_dag.childCount() > 0:
            transform_name = m_par_dag.partialPathName()
            try:
                m_par_dag.extendToShape()
            except RuntimeError:
                pass
            else:
                try:
                    m_par_dag.extendToShapeDirectlyBelow(0)
                except RuntimeError:
                    pass

            shape_deformed_name = m_par_dag.partialPathName()
            if cmds.referenceQuery(mesh_name, isNodeReferenced=1):
                file_name = cmds.referenceQuery(mesh_name, filename=1)
                if file_name:
                    cmds.setAttr(mesh_name + override_attr, 0)
                    cmds.setAttr(mesh_name + template_attr, 0)
                    cmds.setAttr(transform_name + override_attr, 0)
                    cmds.setAttr(transform_name + template_attr, 0)
                    cmds.setAttr(shape_deformed_name + override_attr, 0)
                    cmds.setAttr(shape_deformed_name + template_attr, 0)
        scene_node_gen.next()

    return True


def set_mesh_smoothness(set_smooth=2):
    """
    Parse through the referenced mesh and set the smoothness level.
    :return: <bool> True for success.
    """
    if set_smooth not in (0, 1, 2):
        raise RuntimeError(('[Set Smooth Parameter Error] :: Value {}, Please use integers (0, 1, 2)').format(set_smooth))
    attribute = '.displaySmoothMesh'
    scene_node_gen = api0.MItDependencyNodes(api0.MFn.kMesh)
    while not scene_node_gen.isDone():
        m_obj = scene_node_gen.item()
        m_dag = api0.MDagPath.getAPathTo(m_obj)
        mesh_name = m_dag.partialPathName()
        m_sel = api0.MSelectionList()
        m_sel.add(mesh_name)
        m_node = api0.MObject()
        m_sel.getDependNode(0, m_node)
        m_dag_fn = api0.MFnDagNode(m_node)
        par_node = m_dag_fn.parent(0)
        m_par_dag = api0.MDagPath.getAPathTo(par_node)
        transform_name = m_par_dag.partialPathName()
        if cmds.referenceQuery(mesh_name, isNodeReferenced=1):
            file_name = cmds.referenceQuery(mesh_name, filename=1)
            if file_name:
                smooth_state = cmds.getAttr(mesh_name + attribute)
                if set_smooth == 2 and smooth_state != 2:
                    cmds.setAttr(mesh_name + attribute, set_smooth)
                    exec_str = 'displaySmoothness '
                    exec_str += '-divisionsU 3 '
                    exec_str += '-divisionsV 3 '
                    exec_str += '-pointsWire 16 '
                    exec_str += '-pointsShaded 4 '
                    exec_str += '-polygonObject 3 '
                    exec_str += ('{};').format(transform_name)
                    api0.MGlobal.executeCommand(exec_str)
                elif set_smooth == 1 and smooth_state != 1:
                    cmds.setAttr(mesh_name + attribute, set_smooth)
                    exec_str = 'displaySmoothness '
                    exec_str += '-divisionsU 1 '
                    exec_str += '-divisionsV 1 '
                    exec_str += '-pointsWire 8 '
                    exec_str += '-pointsShaded 2 '
                    exec_str += '-polygonObject 2 '
                    exec_str += ('{};').format(transform_name)
                    api0.MGlobal.executeCommand(exec_str)
                elif set_smooth == 0 and smooth_state != 0:
                    cmds.setAttr(mesh_name + attribute, set_smooth)
                    exec_str = 'displaySmoothness '
                    exec_str += '-divisionsU 0 '
                    exec_str += '-divisionsV 0 '
                    exec_str += '-pointsWire 4 '
                    exec_str += '-pointsShaded 1 '
                    exec_str += '-polygonObject 1 '
                    exec_str += ('{};').format(transform_name)
                    api0.MGlobal.executeCommand(exec_str)
        scene_node_gen.next()

    return True


def delete_inactive_skinclusters():
    """
    Parses through all skins and deletes the skincluster nodes that have no effect whatsoever.
    :return: <bool> True for success.
    """
    iter = api0.MItDependencyNodes(api0.MFn.kInvalid)
    while not iter.isDone():
        object = iter.item()
        if object.apiType() == api0.MFn.kSkinClusterFilter:
            skin_fn = api0Anim.MFnSkinCluster(object)
            skin_name = skin_fn.name()
            try:
                skin_fn.deformerSet()
            except RuntimeError:
                cmds.delete(skin_name)
        iter.next()
    return True


def normalize_skins(mode=1):
    """
    Parses through the scene graph and normalizes all skinClusters.
    :param mode: <int> 1: None, 2: Interactive, 3: Post.
    :return: <bool> True for success.
    """
    iter = api0.MItDependencyNodes(api0.MFn.kInvalid)
    problem_skins = []
    while not iter.isDone():
        m_object = iter.item()
        if m_object.apiType() == api0.MFn.kSkinClusterFilter:
            skin_fn = api0Anim.MFnSkinCluster(m_object)
            skin_name = skin_fn.name()
            mfn_set = None
            try:
                mfn_set = api0.MFnSet(skin_fn.deformerSet())
            except RuntimeError:
                api0.MGlobal.displayError(('{}').format('[Normalize Skin Invalid Skin] :: %s' % skin_name))
                problem_skins.append(skin_name)

            if mfn_set:
                # after a successful normalization, set the settings
                cmds.setAttr(skin_name + '.normalizeWeights', mode)

                mfn_set_members = api0.MSelectionList()
                mfn_set.getMembers(mfn_set_members, False)
                dag_path = api0.MDagPath()
                m_comp_obj = api0.MObject()
                try:
                    cmds.skinCluster(skin_name, edit=True, forceNormalizeWeights=True)
                    cmds.setAttr(skin_name+".normalizeWeights", 1)

                    '''
                    geo_skin_name = ''
                    if mfn_set_members.length() == 1:
                        mfn_set_members.getDagPath(0, dag_path, m_comp_obj)
                        geo_skin_name = dag_path.fullPathName()
                        # force weight normalization

                    else:
                        api0.MGlobal.displayWarning(('{}').format('[Could Not Find Correct Geo] :: %s --> %s' % (
                                                    skin_name, geo_skin_name)))
                    '''
                except RuntimeError:
                    api0.MGlobal.displayError(('{}').format('[Normalize Skin Failure] :: %s --> %s' % (
                                              skin_name, geo_skin_name)))
                    problem_skins.append(skin_name)
            else:
                cmds.warning('[Normalize Skin] :: {} has no functioning set.'.format(skin_name))
        iter.next()
    # evaluate the tool panel settings window
    mel.eval('catchQuiet(`artAttrSkinProperties`);')
    return problem_skins

def ngSkinTools_cleanup():
    # delete ngSkinToolsData node

    dataNodes = cmds.ls('ngSkinToolsData*')

    if dataNodes:
        for d in dataNodes:
            cmds.delete(d)

def check_delta_mush_scale_connections():
    """
    connects the delta mush scale attribute if it isn't already.
    :return: <bool> True for success.
    """
    if cmds.objExists(GLOBAL_SCALE_NODE):
        delta_mush_nodes = cmds.ls(type='deltaMush')
        for d_node in delta_mush_nodes:
            for axis in 'XYZ':
                out_attr = GLOBAL_SCALE_NODE + '.output' + axis
                in_attr = d_node + '.scale' + axis
                if not cmds.isConnected(out_attr, in_attr):
                    try:
                        cmds.connectAttr(out_attr, in_attr, f=1)
                    except RuntimeError:
                        cmds.warning('[Delta Mush] :: Unable to connect {}.scale{}'.format(d_node, axis))
                        continue
    return True

def unlock_Geo():
    topRootNode = [t for t in ['Character', 'Set', 'Prop', 'Vehicle'] if cmds.objExists(t)]
    if not topRootNode:
        return False
    topRootNode = topRootNode[0]

    GeoLock = topRootNode+'.GeoLock'
    if cmds.objExists(GeoLock):
        cmds.setAttr(GeoLock, 0)

def unlock_Utils():
    topRootNode = [t for t in ['Character', 'Set', 'Prop', 'Vehicle'] if cmds.objExists(t)]
    if not topRootNode:
        return False
    topRootNode = topRootNode[0]

    UtilsLock = topRootNode+'.UtilityVis'
    print 'Unlock Utility vis.'
    if cmds.objExists(UtilsLock):
        cmds.setAttr(UtilsLock, 1)

def unlock_Jnts():
    topRootNode = [t for t in ['Character', 'Set', 'Prop', 'Vehicle'] if cmds.objExists(t)]
    if not topRootNode:
        return False
    topRootNode = topRootNode[0]

    JntsLock = topRootNode+'.JointVis'
    print 'Unlock Joitns vis.'
    if cmds.objExists(JntsLock):
        cmds.setAttr(JntsLock, 1)

def makeVisKeyable():
    ctrl = 'Control_Ctrl'
    if not cmds.objExists(ctrl):
        return False

    attrs = cmds.listAttr(ctrl, channelBox=True, keyable=False)
    if attrs:
        for a in attrs:
            if 'Vis' in a:
                cmds.setAttr(ctrl+'.'+a, keyable=True)

def unlock_asset():
    """
    Finalize the asset for publish.
    :return: <bool> True for success. False for fail.
    """
    start_time = timer()
    topRootNode = [ t for t in ['Character', 'Set', 'Prop', 'Vehicle'] if cmds.objExists(t) ]
    if not topRootNode:
        return False
    topRootNode = topRootNode[0]
    ProxyVis = topRootNode + '.ProxyVis'
    GeoVis = topRootNode + '.GeoVis'
    JointVis = topRootNode + '.JointVis'
    UtilityVis = topRootNode + '.UtilityVis'
    GeoLock = topRootNode + '.GeoLock'
    PinkHelperVis = topRootNode + '.PinkHelperVis'
    Face_Rig_Vis = topRootNode + '.Face_Rig_Vis'
    CtrlVis = topRootNode + '.CtrlVis'
    Root_Ctrl = 'Root_Ctrl.Root_Ctrl'
    scale_xyz = 'Root_Ctrl.ScaleXYZ'
    if cmds.objExists(scale_xyz):
        if cmds.getAttr(scale_xyz, settable=1):
            cmds.setAttr(scale_xyz, 1.0)
    if cmds.objExists(ProxyVis):
        cmds.setAttr(ProxyVis, 0)
    if cmds.objExists(GeoVis):
        cmds.setAttr(GeoVis, 1)
    if cmds.objExists(JointVis):
        cmds.setAttr(JointVis, 1)
    if cmds.objExists(UtilityVis):
        cmds.setAttr(UtilityVis, 1)
    if cmds.objExists(GeoVis):
        cmds.setAttr(GeoVis, 1)
    if cmds.objExists(GeoLock):
        cmds.setAttr(GeoLock, 0)
    if cmds.objExists(Face_Rig_Vis):
        cmds.setAttr(Face_Rig_Vis, 0)
    if cmds.objExists(PinkHelperVis):
        cmds.setAttr(PinkHelperVis, 0)
    if cmds.objExists(CtrlVis):
        cmds.setAttr(CtrlVis, 1)
    if cmds.objExists(Root_Ctrl):
        cmds.setAttr(Root_Ctrl, 1)
    for gimbalAttr in cmds.ls('*.GimbalVis') + cmds.ls('*.Gimbal'):
        try:
            cmds.setAttr(gimbalAttr, 1)
        except RuntimeError:
            continue
    facebake_manual.mirrorMovementOn()
    end_time = timer()
    print ('[Cleanup] :: Un-Locked in {} seconds.').format(end_time - start_time)
    return True


def set_controller_default_zero():
    """
    Zeroes out all the controllers in the maya scene.
    :return: <bool> True for succeess.
    """
    print 'Locking ctrls.'
    controllers = cmds.ls('*_Ctrl', type='transform') + cmds.ls('*:*_Ctrl', type='transform')
    exceptions = ['R_Back_Door_01_Ctrl', 'L_Back_Door_Bot_01_Ctrl', 'L_Inner_Lower_Eye_Ctrl', 'R_Inner_Lower_Eye_Ctrl']
    for ctrl in controllers:
        if ctrl not in exceptions:
            for trs_attr in ('tx', 'tz', 'ty', 'rx', 'rz', 'ry', 'sx', 'sz', 'sy'):
                ctrl_attr = ('{}.{}').format(ctrl, trs_attr)
                if cmds.getAttr(ctrl_attr, l=1):
                    continue
                if not cmds.objExists(ctrl_attr):
                    continue
                if cmds.listConnections(ctrl_attr, s=1, d=0):
                    continue
                if trs_attr in ('sx', 'sz', 'sy'):
                    cmds.setAttr(ctrl_attr, 1.0)
                else:
                    cmds.setAttr(ctrl_attr, 0.0)
    return True


def set_control_attributes():
    """
    A tertiary step to finalize the asset by setting certain controller attributes.
    :return: <bool> True for success.
    """
    foot_data = {
       u'BallRoll': 0.0,
       u'HeelPivot': 0.0, 
       u'HeelRoll': 0.0, 
       u'HipSquetch': 1.0, 
       u'KneeSquetch': 1.0, 
       u'MidDirection': 0.0, 
       u'RollBreak': 30.0, 
       u'SoftIK': 0.0, 
       u'ToePivot': 0.0, 
       u'ToeRoll': 0.0, 
       u'ToeSide': 0.0, 
       u'ToeTwist': 0.0, 
       u'ToeUpDown': 0.0, 
       u'VolumeLong': 1.0, 
       u'VolumeWide': 1.0}
    fkik_data = {u'BendyTweakVis': 0.0, u'TweakCtrlsVis': 0.0, 
        u'BendyVis': 0.0,
        u'FKIKSwitch': 1.0,
        u'UpperTwist': 0.0,
        u'Feather_0_TweaksVis': 0,
        u'Feather_1_TweaksVis': 0,
        u'Feather_2_TweaksVis': 0,
        u'Feather_3_TweaksVis': 0,
        u'Feather_4_TweaksVis': 0,
        u'Feather_5_TweaksVis': 0,
        u'Feather_6_TweaksVis': 0,
        u'Feather_7_TweaksVis': 0,
        u'Feather_8_TweaksVis': 0,
        u'Feather_9_TweaksVis': 0,
        u'Feather_10_TweaksVis': 0,
        u'Feather_11_TweaksVis': 0}

    feet_ctrls = cmds.ls('*.RollBreak')
    fkik_ctrls = cmds.ls('*.FKIKSwitch')
    if feet_ctrls:
        for f_ctrl in feet_ctrls:
            f_ctrl = f_ctrl.split('.')[0]
            for attr, val in foot_data.items():
                ctrl_attr = f_ctrl + '.' + attr
                if not cmds.objExists(ctrl_attr):
                    continue
                if not cmds.listConnections(ctrl_attr, s=1, d=0):
                    try:
                        cmds.setAttr(ctrl_attr, val)
                    except RuntimeError:
                        print ('[Set Custom Attrs Error] :: Could not set foot attribute, {}').format(ctrl_attr)

    if fkik_ctrls:
        for f_ctrl in fkik_ctrls:
            f_ctrl = f_ctrl.split('.')[0]
            for attr, val in fkik_data.items():
                if 'FKIKSwitch' in attr:
                    if 'Arm' in f_ctrl:
                        val = 0.0
                ctrl_attr = f_ctrl + '.' + attr
                if not cmds.objExists(ctrl_attr):
                    continue
                if not cmds.listConnections(ctrl_attr, s=1, d=0):
                    try:
                        cmds.setAttr(ctrl_attr, val)
                    except RuntimeError:
                        print ('[Set Custom Attrs Error] :: Could not set FKIK attribute, {}').format(ctrl_attr)


    head_squash_ctrls = [
     'C_Head_Ctrl', 'C_Neck_End_Ctrl']
    for head_ctrl in head_squash_ctrls:
        ffd_squash_ctrl_attr = cmds.ls(('{}.SquashControls').format(head_ctrl)) + cmds.ls(('{}.Squash_Controls').format(head_ctrl))
        squash_ctrl_atttr = cmds.ls(('{}.Squash').format(head_ctrl))
        if ffd_squash_ctrl_attr:
            try:
                cmds.setAttr(ffd_squash_ctrl_attr[0], 0.0)
            except RuntimeError:
                pass

        if squash_ctrl_atttr:
            try:
                cmds.setAttr(squash_ctrl_atttr[0], 0.0)
            except RuntimeError:
                pass

    # set the default value for all instances of elbow flip attribute
    elbow_flip_ctrls = cmds.ls('*.ElbowFlip')
    if elbow_flip_ctrls:
        for ea_attr in elbow_flip_ctrls:
            if cmds.getAttr(ea_attr):
                cmds.setAttr(ea_attr, 0)

    # set the default value for all instances of Extra Vis attribute
    extras_vis_ctrls = cmds.ls('*.ExtrasVis')
    if extras_vis_ctrls:
        for ea_attr in extras_vis_ctrls:
            if cmds.getAttr(ea_attr):
                cmds.setAttr(ea_attr, 0)

    # set default follow attributes
    arm_follow = cmds.ls('*Arm*_Ctrl.Follow')
    leg_follow = cmds.ls('*Leg_*_Ik_Ctrl.Follow') + cmds.ls('?_Leg_PoleVector_Ctrl.Follow')
    others_follow = cmds.ls('?_Clavicle_Ctrl.Follow') + cmds.ls('?_*Hip_Ctrl.Follow')
    head_follow = cmds.ls('C_Head_Ctrl.Follow')
    shoulder_follow = cmds.ls('?_Arm_Shoulder_Fk_Ctrl.Follow')
    foot_autoaim = cmds.ls('*.Foot_AutoAim')
    tweak_ctrl_attrs = cmds.ls('*Clavicle_Ctrl.TweakCtrlsVis', '*Hip_Ctrl.TweakCtrlsVis', 'C_Neck_??_Ctrl.TweakVis')

    if shoulder_follow:
        # set to ground follow
        for s_ctrl in shoulder_follow:
            try:
                cmds.setAttr(s_ctrl, 2)
            except RuntimeError:
                continue

    if head_follow:
        # set to ground follow
        for h_ctrl in head_follow:
            try:
                cmds.setAttr(h_ctrl, 1)
            except RuntimeError:
                continue

    if tweak_ctrl_attrs:
        for ctrl_twk in tweak_ctrl_attrs:
            try:
                cmds.setAttr(ctrl_twk, 0)
            except RuntimeError:
                continue

    if arm_follow:
        for arm_ik in arm_follow:
            try:
                cmds.setAttr(arm_ik, 0)
            except RuntimeError:
                continue

    if leg_follow:
        for leg_ik in leg_follow:
            # get the leg enum attributes
            node, attribute = leg_ik.split('.')
            enums = cmds.attributeQuery(attribute, n=node, listEnum=1)
            ground_index = 4
            if enums:
                try:
                    ground_index = enums[0].split(':').index('Ground')
                except ValueError:
                    pass
            try:
                cmds.setAttr(leg_ik, ground_index)
            except RuntimeError:
                continue

    if others_follow:
        for other_ik in others_follow:
            try:
                cmds.setAttr(other_ik, 0)
            except RuntimeError:
                continue

    if foot_autoaim:
        for hip_ctrl in foot_autoaim:
            try:
                cmds.setAttr(hip_ctrl, 0)
            except RuntimeError:
                continue


    return True

# Replace soft ik anim curve on control with remap
def ikSoftFix():
    for side in ['L', 'R']:
        for part in ['Arm', 'Leg', 'FrontLeg', 'BackLeg']:
            for loc in ['Wrist', 'Ankle', 'Foot']:
                ctrl = side+'_'+part+'_'+loc+'_Ik_Ctrl'

                if cmds.objExists(ctrl):
                    if cmds.attributeQuery('SoftIK', node=ctrl, exists=True):

                        anm = side+'_'+part+'_Ctrl_D_Soft'
                        remap = side+'_'+part+'_Ctrl_D_Soft_Remap'

                        if not cmds.objExists(remap):
                            if cmds.objExists(anm):
                                cmds.shadingNode('remapValue', asUtility=True, name=remap)
                                vals = cmds.keyframe(anm, query=True, index=(0, 1), relative=True, valueChange=True)
                                cmds.setAttr(remap+'.outputMin', vals[0])
                                cmds.setAttr(remap+'.outputMax', vals[1])
                                cmds.setAttr(remap+'.inputMin', 0)
                                cmds.setAttr(remap+'.inputMax', 20)
                                cmds.connectAttr(ctrl+'.SoftIK', remap+'.inputValue', force=True)
                                cmds.connectAttr(remap+'.outColorR', ctrl+'.D_Soft', force=True)


                                if cmds.attributeQuery('D_Soft', node=ctrl+'_Offset_Grp', exists=True):
                                    cmds.connectAttr(ctrl+'.D_Soft', ctrl+'_Offset_Grp.D_Soft', force=True )
                                else:
                                    print 'cannot find D_Soft on '+ctrl+'_Offset_Grp'
                                cmds.delete(anm)

                        else:
                            if not cmds.isConnected(ctrl+'.SoftIK', remap+'.inputValue'):
                                cmds.connectAttr(ctrl+'.SoftIK', remap+'.inputValue', force=True)
                            if not cmds.isConnected(remap+'.outColorR', ctrl+'.D_Soft'):
                                cmds.connectAttr(remap+'.outColorR', ctrl+'.D_Soft', force=True)
                            if cmds.objExists(anm):
                                cmds.delete(anm)
                            if cmds.attributeQuery('D_Soft', node=ctrl+'_Offset_Grp', exists=True):
                                if not cmds.isConnected(ctrl+'.D_Soft', ctrl+'_Offset_Grp.D_Soft'):
                                    cmds.connectAttr(ctrl+'.D_Soft', ctrl+'_Offset_Grp.D_Soft', force=True)
                                else:
                                    print ctrl+'.D_Soft, is already connected to '+ctrl+'_Offset_Grp.D_Soft'
                            else:
                                print ctrl+'_Offset_Grp.D_Soft, does not exist'


def fixWingUpperRotation():
    for side in 'LR':
        '''
        loc = side+'_Arm_Top_Bend_Start_Ctrl_Ik_Xtra_Loc'
        prnt = side+'_Arm_Top_Bend_Start_Ctrl_Ik_Xtra_Grp'
        chest = 'C_Spine_Chest_Gimbal_Ctrl'
        offset = side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp'

        if not cmds.objExists(loc):
            if cmds.objExists(offset):
                cmds.createNode('transform', name=loc, parent=prnt)

                temp = cmds.orientConstraint(chest, loc, maintainOffset=False)
                cmds.delete(temp)

                cmds.delete(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_parentConstraint1')
                cmds.delete(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_scaleConstraint1')

                cmds.setAttr(offset+'.rotateOrder', 4)

                cnst = cmds.parentConstraint(loc, offset, maintainOffset=True)[0]
                cmds.parentConstraint(chest, offset, maintainOffset=True)

                cmds.scaleConstraint(loc, offset, maintainOffset=True)
                cmds.scaleConstraint(chest, offset, maintainOffset=True)

                cmds.setAttr(cnst+'.interpType', 0)
        '''
        if cmds.objExists(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_parentConstraint1'):
            cmds.setAttr(side+'_Wing_BaseOffset_1_Ctrl_Cns_Grp_parentConstraint1.interpType', 2)

def makeShoulderRotateOrderKeyable():
    for side in 'LR':
        if cmds.objExists(side+'_Arm_Shoulder_Fk_Ctrl'):
            cmds.setAttr(side+'_Arm_Shoulder_Fk_Ctrl.rotateOrder', keyable=True)

def fixHeadSquashCenterInfluence():
    if cmds.objExists('HeadSquash_FFD'):
        cmds.setAttr('HeadSquash_FFD.outsideLattice', 1)

def fixSetCOG():
    if cmds.objExists('Set'):
        print "here"
        cmds.setAttr('COG_Ctrl.translate', lock=False)
        cmds.setAttr('COG_Ctrl.translateX', keyable=True, lock=False)
        cmds.setAttr('COG_Ctrl.translateY', keyable=True, lock=False)
        cmds.setAttr('COG_Ctrl.translateZ', keyable=True, lock=False)
        cmds.setAttr('COG_Ctrl.rotate', lock=False)
        cmds.setAttr('COG_Ctrl.rotateX', keyable=True, lock=False)
        cmds.setAttr('COG_Ctrl.rotateY', keyable=True, lock=False)
        cmds.setAttr('COG_Ctrl.rotateZ', keyable=True, lock=False)

        cmds.setAttr('COG_Gimbal_Ctrl.translate', lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.translateX', keyable=True, lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.translateY', keyable=True, lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.translateZ', keyable=True, lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.rotate', lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.rotateX', keyable=True, lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.rotateY', keyable=True, lock=False)
        cmds.setAttr('COG_Gimbal_Ctrl.rotateZ', keyable=True, lock=False)


def lock_asset():
    """
    Finalize the asset for publish.
    :return: <bool> True for success. False for fail.
    """
    start_time = timer()
    topRootNode = [t for t in ['Character', 'Set', 'Prop', 'Vehicle'] if cmds.objExists(t)]
    if not topRootNode:
        return False
    topRootNode = topRootNode[0]
    ProxyVis = topRootNode + '.ProxyVis'
    GeoVis = topRootNode + '.GeoVis'
    JointVis = topRootNode + '.JointVis'
    UtilityVis = topRootNode + '.UtilityVis'
    GeoLock = topRootNode + '.GeoLock'
    PinkHelperVis = topRootNode + '.PinkHelperVis'
    Face_Rig_Vis = topRootNode + '.Face_Rig_Vis'
    CtrlVis = topRootNode + '.CtrlVis'
    Root_Ctrl = 'Root_Ctrl.Root_Ctrl'
    scale_xyz = 'Root_Ctrl.ScaleXYZ'
    if cmds.objExists(scale_xyz):
        if cmds.getAttr(scale_xyz, settable=1):
            cmds.setAttr(scale_xyz, 1.0)
    if cmds.objExists(ProxyVis):
        cmds.setAttr(ProxyVis, 0)
    if cmds.objExists(GeoVis):
        cmds.setAttr(GeoVis, 1)
    if cmds.objExists(JointVis):
        cmds.setAttr(JointVis, 0)
    if cmds.objExists(UtilityVis):
        cmds.setAttr(UtilityVis, 0)
    if cmds.objExists(GeoVis):
        cmds.setAttr(GeoVis, 1)
    if cmds.objExists(GeoLock):
        cmds.setAttr(GeoLock, 2)
    if cmds.objExists(Face_Rig_Vis):
        cmds.setAttr(Face_Rig_Vis, 0)
    if cmds.objExists(PinkHelperVis):
        cmds.setAttr(PinkHelperVis, 0)
    if cmds.objExists(CtrlVis):
        cmds.setAttr(CtrlVis, 1)
    if cmds.objExists(Root_Ctrl):
        cmds.setAttr(Root_Ctrl, 1)

    mel.eval('MLdeleteUnused;')

    delete_ctrl_keyframes()
    illuminati_ctrl = 'Control_Ctrl'
    if cmds.objExists(illuminati_ctrl):
        for attr_name in ['Show_Global_Ctrl', 'Show_Root_Ctrl']:
            attr_full_name = illuminati_ctrl + '.' + attr_name
            if not cmds.objExists(attr_full_name):
                cmds.addAttr(illuminati_ctrl, ln=attr_name, at='enum', en='Off:On', dv=1)
                cmds.setAttr(attr_full_name, cb=1)
                cmds.setAttr(attr_full_name, k=1)
                if 'Show_Global_Ctrl' in attr_name:
                    cmds.connectAttr(attr_full_name, 'COG_CtrlShape.lodVisibility')
                    cmds.connectAttr(attr_full_name, 'COG_Gimbal_CtrlShape.lodVisibility')
                if 'Show_Root_Ctrl' in attr_name:
                    cmds.connectAttr(attr_full_name, 'Root_CtrlShape.lodVisibility')
                    cmds.connectAttr(attr_full_name, 'Root_Gimbal_CtrlShape.lodVisibility')
                    cmds.connectAttr(attr_full_name, 'Ground_Gimbal_CtrlShape.lodVisibility')
                    cmds.connectAttr(attr_full_name, 'Ground_CtrlShape.lodVisibility')

    for gimbalAttr in cmds.ls('*.GimbalVis') + cmds.ls('*.Gimbal'):
        try:
            cmds.setAttr(gimbalAttr, 0)
        except RuntimeError:
            continue

    try:
        set_control_attributes()
    except RuntimeError:
        cmds.warning('[Controller Attributes] :: Failure.')
        pass

    try:
        facebake_manual.mirrorMovementOff()
    except RuntimeError:
        cmds.warning('[Face Bake Mirror] :: Failure.')
        pass

    problem_skins = []
    try:
        problem_skins = normalize_skins()
    except RuntimeError:
        cmds.warning('[Normalize Skins] :: Failure.')
    except TypeError as error:
        cmds.warning('[Normalize Skins] :: {}.'.format(error))

    try:
        unlock_joints()
    except RuntimeError:
        cmds.warning('[Unlock Joints] :: Failure.')
        pass

    try:
        set_controller_default_zero()
    except RuntimeError:
        cmds.warning('[Controller Defaults] :: Failure.')

    try:
        set_mesh_smoothness(0)
    except RuntimeError as error:
        cmds.warning('[Mesh Smoothness] :: Failure.')
    except TypeError as error:
        cmds.warning('[Mesh Smoothness] :: {}.'.format(error))

    try:
        reset_mesh_display()
    except RuntimeError:
        cmds.warning('[Mesh Display] :: Failure.')
    except TypeError as error:
        cmds.warning('[Mesh Display] :: {}.'.format(error))

    try:
        set_face_settings()
    except RuntimeError:
        cmds.warning('[Face Settings] :: Failure.')
    except TypeError as error:
        cmds.warning('[Face Settings] :: {}.'.format(error))

    try:
        set_dynamic_settings()
    except RuntimeError:
        cmds.warning('[Dynamic Settings] :: Failure.')
    except TypeError as error:
        cmds.warning('[Dynamic Settings] :: {}.'.format(error))

    '''
    try:
        check_delta_mush_scale_connections()
    except RuntimeError:
        cmds.warning('[Delta Mush Connections] :: Failure.')
    except TypeError as error:
        cmds.warning('[Delta Mush Connections] :: {}.'.format(error))
    '''

    try:
        connect_tweaks_scale()
    except RuntimeError:
        cmds.warning('[Tweak Scale Connnections] :: Failure.')
    except TypeError as error:
        cmds.warning('[Connect Tweak Scale] :: {}.'.format(error))

    #fix display colours
    try:
        reload(tots_fixDisplayColours)
        tots_fixDisplayColours.do_it()
    except RuntimeError:
        cmds.warning('[Fix Display Colours] :: Failure.')
    except TypeError as error:
        cmds.warning('[Fix Display Colours] :: {}.'.format(error))

    # Replace soft ik anim curve on control with remap
    try:
        ikSoftFix()
    except RuntimeError:
        cmds.warning('[Soft Ik Fix] :: Failure.')

    # Reconnect Export Data
    try:
        reload(tots_fix_exportDataReconnect)
        tots_fix_exportDataReconnect.do_it()
    except RuntimeError:
        cmds.warning('[Export Data Reconnect] :: Failure.')

    # Make all Vis Switches Keyable
    try:
        makeVisKeyable()
    except RuntimeError:
        cmds.warning('[Make Vis Switches Keyable] :: Failure.')

    # Fix bird wing issue
    try:
        fixWingUpperRotation()
    except RuntimeError:
        cmds.warning('[Bird Wing Fix] :: Failure.')

    # Make shoulder rotate order attr keyable
    try:
        makeShoulderRotateOrderKeyable()
    except RuntimeError:
        cmds.warning('[Shoulder Rotate Order Keyable] :: Failure.')

    # Fix headsquash lattice influence
    try:
        fixHeadSquashCenterInfluence()
    except RuntimeError:
        cmds.warning('[Lattice Influence Fix] :: Failure.')

    try:
        fixSetCOG()
    except RuntimeError:
        cmds.warning('[Set COG Fix] :: Failure.')

    # remove skins that do nothing
    if problem_skins:
        api0.MGlobal.displayInfo(('{}').format('[Deleting Skins] :: %s' % problem_skins))
        cmds.delete(problem_skins)

    # delete ngSkin Tools Data nodes to bake to maya skins
    try:
        ngSkinTools_cleanup()
    except RuntimeError:
        cmds.warning('[ngSkinTools Cleanup] :: Failure.')

    cmds.select(cl=1)
    end_time = timer()
    print ('[Cleanup] :: Locked in {} seconds.').format(end_time - start_time)
    return True