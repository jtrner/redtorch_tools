# define private variables
__author__ = "Alexei Gaidachev"
__vendor__ = "ICON"
__version__ = "1.0.0"

# define standard imports
import os
import posixpath

# define maya imports
from maya import cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaAnim as OpenMayaAnim

# define custom imports
from rig_tools import RIG_LOG
import rig_tools.utils.deformers as rig_deformers
import fileTools.default as ft
import tex_utils

# define global variables
TEXTURE_PATH = os.path.join(ft.ez.path('elems'), 'textures', 'Proxy_Texture')


def create_texture_path():
    """
    Creates Proxy_Texture directory path.
    :return: <bool> True if successful. <bool> False if fail.
    """
    if not os.path.isdir(TEXTURE_PATH):
        try:
            os.mkdir(TEXTURE_PATH)
        except IOError:
            RIG_LOG.error("[Directory Creation Error] :: Could not create directory: {}".format(TEXTURE_PATH))
            return False
    return True


def get_mesh_fn(node_name):
    """
    Grabs the MFnMesh of the specified node.
    :param node_name: <str> node name.
    :return: <MFnMesh> if successful, <bool> False if fail.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(node_name)
    result = sel.getDagPath(0)
    mesh_fn = OpenMaya.MFnMesh(result)
    if not mesh_fn:
        return False
    return mesh_fn


def get_skin_fn(node):
    """
    Gets the MFnSkinCluster from the MObject specified.
    :param node: <MObject> node to look at.
    :return: <MFnSkinCluster> if successful, <bool> False if fail.
    """
    skin_fn = False
    it_dg = OpenMaya.MItDependencyGraph(node,
                                        OpenMaya.MItDependencyGraph.kDownstream,
                                        OpenMaya.MItDependencyGraph.kPlugLevel)
    while not it_dg.isDone():
        cur_item = it_dg.currentNode()
        if cur_item.hasFn(OpenMaya.MFn.kSkinClusterFilter):
            skin_fn = OpenMayaAnim.MFnSkinCluster(cur_item)
            break
        it_dg.next()
    return skin_fn


def get_skin_cluster(obj_name):
    """
    Gets the skin cluster name from the object specified.
    :param obj_name: <str> object name to find the skinCluster from.
    :return: <str> skinCluster object name if successful, <bool> False if fail.
    """
    o_mesh = get_mesh_fn(obj_name)
    o_path = o_mesh.dagPath()
    o_node = o_path.node()
    skin_fn = get_skin_fn(o_node)
    if skin_fn:
        return skin_fn.name()
    else:
        return False


def create_sampler_file(source_obj, target_obj):
    """
    Creates a sample file for transfer process.
    :param source_obj:
    :param target_obj:
    :return: <str> path-to-dds-file for success, <bool> False if fail.
    :note:
        surfaceSampler
            -target Proxy_L_eye_GeoShapeDeformed
            -uvSet map1 -searchOffset 0
            -maxSearchDistance 0
            -searchCage ""
            -source L_eye_GeoShapeDeformed
            -mapOutput diffuseRGB
            -mapWidth 512
            -mapHeight 512
            -max 1
            -mapSpace tangent
            -mapMaterials 1
            -shadows 1
            -filename "Y:/SMO/assets/type/Character/Vida_Mom/work/elems/textures/Proxy_Texture/Proxy_L_eye"
            -fileFormat "dds"
            -superSampling 1
            -filterType 0
            -filterSize 3
            -overscan 1
            -searchMethod 0
            -useGeometryNormals 1
            -ignoreMirroredFaces 0
            -flipU 0
            -flipV 0
    """
    RIG_LOG.info("[Creating Sampler File] :: {} >> {}.".format(source_obj, target_obj))
    file_path = os.path.join(TEXTURE_PATH, target_obj.rpartition('_')[0]).replace(os.sep, posixpath.sep)

    # find the shapeDeformed mesh to use for map transfer
    source_mesh = get_mesh_fn(source_obj).dagPath().fullPathName().rpartition('|')[-1]
    target_mesh = get_mesh_fn(target_obj).dagPath().fullPathName().rpartition('|')[-1]

    cmds.surfaceSampler(mapOutput='diffuseRGB',
                        filename=file_path,
                        fileFormat='dds',
                        source=source_mesh,
                        target=target_mesh,
                        uv='map1',
                        maxSearchDistance=0,
                        searchCage='',
                        mapWidth=512,
                        mapHeight=512,
                        mapSpace='tangent',
                        searchOffset=0,
                        ss=2,
                        flipU=0,
                        flipV=0,
                        useGeometryNormals=1,
                        filterType=0,
                        filterSize=3,
                        overscan=1,
                        ignoreMirroredFaces=0)
    return file_path + '.dds'


def apply_texture_to_geo(mesh_obj, side_name="L", texture_file=""):
    """
    Applies the texture to the mesh object.
    :param mesh_obj: <str> mesh object transform.
    :param side_name: <str> the side name to prefix the shader name.
    :param texture_file: <str> the texture file name to use in the shader.
    :return: <bool> True if successful, <bool> False if failure.
    """
    os_split = os.sep
    pos_split = posixpath.sep
    try:
        lambert = tex_utils.apply_shader(shader_name="{}_Proxy_Texture".format(side_name),
                                         rgb=None, geo=mesh_obj, shader_type='lambert')
    except Exception as error:
        RIG_LOG.error("[Apply Shader Error] :: {}".format(error))

    if os_split in texture_file:
        file_node_name = texture_file.rpartition(os_split)[-1]

    if pos_split in texture_file:
        file_node_name = texture_file.rpartition(pos_split)[-1]
    file_node_name = file_node_name.replace('.', '_')

    cmds.createNode('file', name=file_node_name)
    cmds.setAttr(file_node_name + '.fileTextureName', texture_file, type='string')
    if not cmds.isConnected(file_node_name + '.outColor', lambert + '.color'):
        cmds.connectAttr(file_node_name + '.outColor', lambert + '.color', force=True)
    return True


def attach_eye_to_bend_set(deformer_obj="", surface_obj=""):
    """
    Attaches the bend deformer to the head squash.
    :param deformer_obj: <str> find the set on this deformer object.
    :param surface_obj: <str> and attach it to this surface object.
    :return: <bool> True for success, <bool> False for failure.
    """
    head_squash = cmds.ls(deformer_obj)
    if not head_squash:
        RIG_LOG.info('[No Head Squash] :: No head squash found, no need to attach to set.')
        return False

    # get the squash object set
    squash_set_ls = cmds.listConnections(head_squash, d=1, s=1, type='objectSet')
    prox_cvs_ls = cmds.ls(surface_obj + '.cv[*][*]')

    # attach the cvs to the squash set
    cmds.sets(prox_cvs_ls[0], fe=squash_set_ls[0])
    return True


def do_it():
    """
    Fixes the eye texture and proxy texture transfer and follicle attachment. SkinCluster apply disabled by default.
    :return: <bool> True for success, <bool> False for failure.
    """
    RIG_LOG.info("[Eye Fix] :: Begin.")

    # define variables
    head_bnd_jnt = 'Head_Bnd'
    bend_deformer = 'HeadSquash_Y1'
    eye_bnd_str = '{}_Eye_Bnd'
    foll_str = 'Proxy_{}_Eye_Foll'
    eye1_str = '*:{}_eye_Geo'
    eye2_str = '*:{}_Eye_Geo'
    eye_prox1_str = 'Proxy_{}_eye_Geo*'
    eye_prox2_str = 'Proxy_{}_Eye_Geo*'
    srf_str = "Proxy_{}_Eye_Srf"
    projection_str = '{}_Eye_Projection_3DPlace'
    proxy_follicle_grp = 'Proxy_Follicle_Grp'

    # create the texture path
    create_texture_path()

    # side loop
    for side in ('L', 'R'):
        # finalize variables
        eye_jnt = eye_bnd_str.format(side)
        foll_name = foll_str.format(side)
        eye_geo1 = eye1_str.format(side)
        eye_geo2 = eye2_str.format(side)
        eye_prx1 = eye_prox1_str.format(side)
        eye_prx2 = eye_prox2_str.format(side)
        srf_name = srf_str.format(side)
        projection_name = projection_str.format(side)

        if cmds.objExists(foll_name) and cmds.objExists(srf_name):
            RIG_LOG.warning('[Already Installed] :: No need to create again, eye fix already in place.'
                            ''.format(projection_name))
            return False

        # check to see if relevant objects exist in scene
        if not cmds.objExists(projection_name):
            RIG_LOG.error('[No 3DPlacement] :: No projection planes found: {}!'.format(projection_name))
            return False

        if not cmds.objExists(eye_jnt):
            RIG_LOG.error('[No Joint] :: No eye joints found: {}!'.format(eye_jnt))
            return False

        # find the eye geos and apply skinCluster
        eye_geos = cmds.ls(eye_geo1) or cmds.ls(eye_geo2)
        if not eye_geos:
            RIG_LOG.error('[No Geos] :: No Eye Geos Found!')
            return False

        eye_geo = [o for o in eye_geos if cmds.objectType(o) == 'transform']
        geo_skin_clusters = map(get_skin_cluster, eye_geo)
        if not all(geo_skin_clusters):
            RIG_LOG.info('[Eye SkinCluster] :: applying skinCluster on {}.'.format(eye_geo))
            cmds.skinCluster(head_bnd_jnt, eye_geo, tsb=1, name=eye_geo[0]+'_Skin')

        # find the eye proxies and apply skinCluster.
        eye_proxies = cmds.ls(eye_prx1) or cmds.ls(eye_prx2)

        if not eye_proxies:
            RIG_LOG.error('[No Proxies] :: No Eye Proxies Found!')
            return False

        eye_proxy_geo = [o for o in eye_proxies if cmds.objectType(o) == 'transform']
        proxy_skin_clusters = map(get_skin_cluster, eye_proxy_geo)
        if not all(proxy_skin_clusters):
            RIG_LOG.info('[Eye SkinCluster] :: applying skinCluster on {}.'.format(eye_proxy_geo))
            cmds.skinCluster(eye_jnt, eye_proxy_geo, tsb=1, name=eye_proxy_geo[0]+'_Skin')

        # create a sampler texture on geo
        tex_file = create_sampler_file(eye_geo[0], eye_proxy_geo[0])

        # apply the texture to the proxy eye geos
        apply_texture_to_geo(eye_proxy_geo[0], side_name=side, texture_file=tex_file)

        # check if there is a constraint already on the 3DProjection
        if not cmds.listConnections(projection_name + '.tx', type='parentConstraint', d=0, s=1):
            # create the follicle and the surface geometry for squash and stretch
            if not cmds.objExists(srf_name):
                plane_srf = cmds.nurbsPlane(name=srf_name, ax=(0.0, 0.0, 1.0), ch=0)[0]
            else:
                plane_srf = srf_name

            follicle_grp, follicle_obj = rig_deformers.create_follicles(surface=plane_srf, name=foll_name)

            # parent the follicle system into utilities
            if not cmds.objExists(proxy_follicle_grp):
                cmds.createNode('transform', name=proxy_follicle_grp)
                cmds.parent(proxy_follicle_grp, 'Utility_Grp')
            cmds.parent([plane_srf, follicle_grp, proxy_follicle_grp])

            attach_eye_to_bend_set(deformer_obj=bend_deformer, surface_obj=plane_srf)

            # constrain the plane surface and the projection to follow the head.
            cmds.parentConstraint(eye_jnt, plane_srf, mo=0)
            cmds.scaleConstraint(eye_jnt, plane_srf, mo=0)
            cmds.parentConstraint(follicle_obj, projection_name, mo=1)
            cmds.scaleConstraint(follicle_obj, projection_name, mo=1)
        else:
            RIG_LOG.info("[3DPlaceTexture Already Connected] :: {}.".format(projection_name))

        RIG_LOG.info("[Completed] :: {}.".format(eye_geos))
    RIG_LOG.info("[Finished] :: Done.")
    return True

