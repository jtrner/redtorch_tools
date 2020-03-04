import os
import random

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

try:
    import mtoa.utils as mutils
except:
    print 'Could not find Arnold renderer!'

from . import fileLib
from . import trsLib
from . import attrLib
from ..general import workspace

reload(attrLib)
reload(fileLib)


def makeNotRenderable():
    objs = mc.ls(sl=True)
    renderAttrs = ["castsShadows",
                   "receiveShadows",
                   "motionBlur",
                   "primaryVisibility",
                   "visibleInReflections",
                   "visibleInRefractions",
                   "aiVisibleInDiffuse",
                   "aiVisibleInGlossy"]
    for obj in objs:
        for attr in renderAttrs:
            mc.setAttr(obj + '.' + attr, 0)


def fixShadingEngineNames():
    SG_nodes = mc.ls(type='shadingEngine')

    SG_nodes.remove('initialShadingGroup')
    SG_nodes.remove('initialParticleSE')

    for SG_node in SG_nodes:
        shader = mc.listConnections(SG_node + '.surfaceShader')

        if not shader:
            continue
        if 'MTL' in shader[0]:
            shader = mc.rename(shader[0], shader[0].split('MTL')[0] + 'MTL')
            mc.rename(SG_node, shader.replace('MTL', 'SG'))
        else:
            mc.rename(SG_node, shader[0] + '_SG')


def setResolution():
    # state = mm.eval('optionVar -q renderViewTestResolution;')
    mm.eval('setTestResolutionVar(1);')
    print 'render resolution set to %\ FULL'


def renderAndSave():
    mm.eval('renderWindowRender redoPreviousRender renderView')
    saveImage()


def saveImage():
    """
    reload(renderLib)
    renderLib.saveImage()
    """
    sceneName = mc.file(q=True, sceneName=True)
    if sceneName:
        sceneDir = os.path.dirname(sceneName)
        projDir = os.path.dirname(sceneDir)
        imageDir = os.path.join(projDir, 'images')

        fileFullName = os.path.basename(sceneName)
        fileName, ext = os.path.splitext(fileFullName)  # 'currentSceneName', 'mb'

        frame = '{:04d}'.format(int(mc.currentTime(q=True)))
        fileNameWithFrame = fileName + '.' + frame  # 'currentSceneName.0001'

        newSceneName = os.path.join(imageDir, fileNameWithFrame)
        newSceneName = newSceneName.replace('\\', '/')

        mm.eval('optionVar -intValue renderViewSaveMode 1;')
        mm.eval('renderWindowSaveImageCallback "renderView" "{}" "JPEG";'.format(newSceneName))
    else:
        mc.error('Please save the file first!')


def importLighting():
    filePath = 'E:/all_works/01_projects/template_project/assets/lookdev/outdoor/outdoor_lookdev_v0001.mb'
    highest = workspace.getHighestFile(filePath)
    mc.file(highest, i=True)


def deleteAllMaterials(ignoreList=None):
    """
    remove all shaders except lambert1

    :param ignoreList: list of objects we don't want their material to get deleted
    """
    objs = mc.ls(type='mesh')
    objs = [mc.listRelatives(x, p=True)[0] for x in objs]

    if ignoreList:
        objs = [x for x in objs if x not in ignoreList]

    mc.sets(objs, e=True, forceElement='initialShadingGroup')
    mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')


def deleteUnused():
    mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')


def assignDefaultShaders(ignoreList=None):
    """
    create and assign default materials to all objects
    in the sence which are in "shaders" dictionary
    
    :param ignoreList: list of objects we don't want to assign materials to
    """

    # dictionary holding name of objs as keys and their material settings as values
    shaders = {
        'body': {'color': [0.85, 0.65, 0.45],
                 'eccentricity': [0.4],
                 'specularColor': [0.15, 0.15, 0.15]},

        'mouth': {'color': [0.55, 0.35, 0.30],
                  'eccentricity': [0.15],
                  'specularColor': [0.4, 0.4, 0.4]},

        'tongue': {'color': [0.5, 0.3, 0.25],
                   'eccentricity': [0.15],
                   'specularColor': [0.4, 0.4, 0.4]},

        'teeth': {'color': [0.7, 0.7, 0.6],
                  'eccentricity': [0.4],
                  'specularColor': [0.2, 0.2, 0.2]},

        'spike': {'color': [0.7, 0.7, 0.6],
                  'eccentricity': [0.4],
                  'specularColor': [0.2, 0.2, 0.2]},

        'horn': {'color': [0.65, 0.45, 0.3],
                 'eccentricity': [0.4],
                 'specularColor': [0.2, 0.2, 0.2]},

        'Crust': {'color': [0.7, 0.55, 0.4],
                  'eccentricity': [0.4],
                  'specularColor': [0.2, 0.2, 0.2]},

        'claw': {'color': [0.65, 0.55, 0.45],
                 'eccentricity': [0.3],
                 'specularColor': [0.35, 0.35, 0.35]},

        'eyeball': {'color': [0.8, 0.8, 0.8],
                    'eccentricity': [0.1],
                    'specularColor': [0.8, 0.8, 0.8]},

        'cornea': {'color': [0.1, 0.1, 0.1],
                   'transparency': [0.8, 0.8, 0.8],
                   'eccentricity': [0.1],
                   'specularColor': [0.8, 0.8, 0.8]},

        'pupil': {'color': [0, 0, 0],
                  'specularColor': [0, 0, 0]},

        'iris': {'color': [0.1, 0.1, 0.1],
                 'specularColor': [0.2, 0.2, 0.2]},

        'Skl': {'color': [0.7, 0.7, 0.6],
                'eccentricity': [0.4],
                'specularColor': [0.1, 0.1, 0.1]},

        'fascia': {'color': [1.0, 0.75, 0.25],
                   'eccentricity': [0.1],
                   'specularColor': [0.15, 0.15, 0.15]}
    }

    # assign shaders using shaders dictionary
    for shd, settings in shaders.items():

        # get objects
        loObjs = mc.ls('*%s_???_lo' % shd)
        midObjs = mc.ls('*%s_???_mid' % shd)
        objs = loObjs + midObjs

        if not objs:
            continue

        if ignoreList:
            objs = [x for x in objs if x not in ignoreList]

        assignShader(objs, name=shd + '_mtl', **settings)


def assignShader(nodes, type='blinn', name='newMaterial', **kwargs):
    """
    Create and assign a material to given nodes.

    Note: all the arguments must be in form of list even if there is one argument
    
    ie: assignShader('pCube1',
                     color=[0.6, 0.3, 0.3],
                     eccentricity=[0.2],
                     specularColor=[0.2, 0.2, 0.2],
                     name='newMaterial')
    
    :param nodes: name of object(s) to assign new material to
    :type nodes: string or list

    """

    # create material
    if not mc.objExists(name):
        mat = mc.shadingNode(type, asShader=True, name=name)
        # set material settings
        for setting, value in kwargs.items():
            mc.setAttr(mat + '.' + setting, *value)
    else:
        mat = name

    # assign materials
    applyMtl(mat, nodes)

    return mat


def removeAllColorSets():
    meshes = mc.ls(type='mesh')
    for x in meshes:
        try:
            mc.polyColorSet(x, delete=True, acs=True)
        except:
            pass


def assignMtlUsingJson(mtl_config, mode='anim'):
    """
    reload(renderLib)
    mtl_config = 'E:/all_works/01_projects/cartoonGirlA/02_Assets/Textures/mtl_data.json'
    renderLib.assignMtlUsingJson(mtl_config)
    mc.setAttr(mc.ls("C_eye_MTL_Bump_tif_BMP*.bumpDepth")[-1], -0.1)

    :param mode: anim or render
    """
    textureDir = os.path.join(os.path.dirname(mtl_config), mode)

    mtl_data = fileLib.loadJson(mtl_config)

    if not mtl_data:
        mc.error('{} is not a valid material config file.'.format(mtl_config))

    for mtl, data in mtl_data.items():
        geos = data.pop('geos', 'noName')
        mtlType = data.pop('type', 'lambert')

        if mtlType == 'aiStandardSurface':
            assignArnoldMtl5(nodes=geos, textureDir=textureDir, name=mtl, **data)

        else:
            assignMaterial(nodes=geos, textureDir=textureDir, name=mtl, mtlType=mtlType, **data)


def assignMaterial(nodes=None, mtlType='blinn', name='newMaterial', textureDir=None, **kwargs):
    """
        txrPath = 'E:/all_works/01_projects/seagull/texture/bodyFeather.tif'
        assignMaterial(['C_body_GEO', 'C_head_GEO'],
                                color={'fileTextureName': txrPath,
                                       'uvSet': 'utilitiesFace',
                                       'outAttr': 'outColor',
                                       'innAttr': None},
                                eccentricity=[0.2],
                                specularColor=[0.2, 0.2, 0.2],
                                name='head_mat')
    """
    # delete material if already exists
    if mc.objExists(name):
        try:
            mc.delete(name)
        except:
            pass

    # create material
    mat = mc.shadingNode(mtlType, asShader=True, name=name)

    # set material settings
    for setting, value in kwargs.items():
        if isinstance(value, dict):  # value is a texture path
            # get texture path and uvSet
            filePath = value['fileTextureName']

            textureName = value.get('fileTextureName', None)
            if textureDir and textureName:
                filePath = os.path.join(textureDir, textureName)

            if setting == 'normalCamera':
                bmp = mc.createNode('bump2d', name=textureName + '_BMP')
                mc.setAttr(bmp + '.bumpInterp', 1)
                mc.setAttr(bmp + '.aiFlipG', 0)
                mc.setAttr(bmp + '.aiFlipR', 0)
                f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
                mc.setAttr(f + '.fileTextureName', textureName, type="string")
                mc.setAttr(f + '.colorSpace', 'Raw', type='string')
                mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
                # mc.connectAttr(bmp+'.outNormal', mat+'.normalCamera')
                f = bmp
                outAttr = value.get('outAttr', 'outNormal')
                innAttr = value.get('innAttr', 'normalCamera')

            elif setting == 'bump':
                bmp = mc.createNode('bump2d', name=textureName + '_BMP')
                f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
                mc.setAttr(f + '.fileTextureName', textureName, type="string")
                mc.setAttr(f + '.colorSpace', 'Raw', type='string')
                mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
                # mc.connectAttr(bmp+'.outNormal', mat+'.normalCamera')
                f = bmp
                outAttr = value.get('outAttr', 'outNormal')
                innAttr = value.get('innAttr', 'normalCamera')

            else:
                # create texture and connect to shader
                f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=mat + '_FLE')
                mc.setAttr(f + '.fileTextureName', filePath, type="string")

                outAttr = value.get('outAttr', 'outColor')
                innAttr = value.get('innAttr', setting)

            if not isinstance(innAttr, basestring):
                for inn in innAttr:
                    mc.connectAttr(f + '.' + outAttr, mat + '.' + inn)
            else:
                mc.connectAttr(f + '.' + outAttr, mat + '.' + innAttr)

            uvSet = value.get('uvSet', 'map1')

            # assign given uvSet to texture file
            if not uvSet == 'map1':
                uv = mc.createNode('uvChooser')
                mc.connectAttr(uv + ".outVertexCameraOne", f + ".vertexCameraOne")
                mc.connectAttr(uv + ".outVertexUvThree", f + ".vertexUvThree")
                mc.connectAttr(uv + ".outVertexUvTwo", f + ".vertexUvTwo")
                mc.connectAttr(uv + ".outVertexUvOne", f + ".vertexUvOne")
                mc.connectAttr(uv + ".outUv", f + ".uvCoord")

                for i, n in enumerate(nodes):
                    index = getIndexOfUVset(n, uvSet)
                    mc.connectAttr(n + ".uvSet[%s].uvSetName" % index, uv + ".uvSets[%s]" % i)
        else:
            attrLib.setAttr(mat + '.' + setting, value)

    # assign materials
    applyMtl(mat, nodes)

    return mat


def assignRandomShaders(nodes=None, applyToAll=False, colorRange=(0, 1), mtlType='lambert'):
    """
    :usage:
        from rt_python.lib import renderLib
        renderLib.assignRandomShaders(applyToAll=True, colorRange=(0.1, 0.8))
    """
    if applyToAll:
        nodes = list(set([mc.listRelatives(x, p=1)[0] for x in mc.ls(type='mesh')]))
    else:
        nodes = mc.ls(nodes)

    for node in nodes:
        color = (random.uniform(*colorRange),
                 random.uniform(*colorRange),
                 random.uniform(*colorRange))
        assignMaterial(nodes=node,
                       mtlType=mtlType,
                       name='{}_random_MTL'.format(node),
                       color=color)


def assignArnoldMtl(nodes, name='new_MTL', **kwargs):
    """
    txrPath = 'E:/all_works/01_projects/seagull/texture/bodyFeather.tif'
    renderLib.assignArnoldMtl(['feather'],
                                color={'fileTextureName': txrPath},
                                opacity={'fileTextureName': txrPath,
                                         'outAttr': 'outAlpha',
                                         'innAttr': ['opacity.opacityR',
                                                     'opacity.opacityG',
                                                     'opacity.opacityB']},
                                name='head_mat')
    """
    mat = assignMaterial(nodes, mtlType='aiStandard', name=name, **kwargs)
    return mat


def assignArnoldMtl5(nodes, name='new_MTL', **kwargs):
    """
    txrPath = 'E:/all_works/01_projects/seagull/texture/bodyFeather.tif'
    renderLib.assignArnoldMtl5(['feather'],
                                color={'fileTextureName': txrPath},
                                opacity={'fileTextureName': txrPath,
                                         'outAttr': 'outAlpha',
                                         'innAttr': ['opacity.opacityR',
                                                     'opacity.opacityG',
                                                     'opacity.opacityB']},
                                name='head_mat')
    """
    mat = assignMaterial(nodes, mtlType='aiStandardSurface', name=name, **kwargs)
    return mat


def assignShadersFromScene(namespace=''):
    materials = mc.ls('*_MTL')
    for mat in materials:
        node = namespace + ':' + mat.replace('_MTL', '_GEO')
        if mc.objExists(node):
            applyMtl(mat, node)


def substanceToArnold5(textureDir):
    """
    reload(renderLib)
    textureDir = 'E:/all_works/01_projects/hound/04_Assets/Textures'
    renderLib.substanceToArnold5(textureDir)
    renderLib.assignShadersFromScene()
    renderLib.renameShadingGroups()
    renderLib.importLighting()
    """
    textures = [x for x in os.listdir(textureDir) if
                os.path.isfile(os.path.join(textureDir, x))]

    attrsAndTextures = {}
    for texture in textures:
        shader, _, attrInfo = texture.rpartition('_')
        shader = shader + '_MTL'
        attr, extension = attrInfo.split('.')
        if extension not in ('jpg', 'png'):
            continue
        if shader not in attrsAndTextures:
            attrsAndTextures[shader] = {}
        attrsAndTextures[shader][attr.lower()] = os.path.join(textureDir, texture)

    for shader, shaderData in attrsAndTextures.items():
        data = {'baseColor': shaderData.get('basecolor', None),
                'metalness': shaderData.get('metalness', None),
                'specularRoughness': shaderData.get('metalness',
                                                    shaderData.get('roughness', None)),
                'specularColor': shaderData.get('specularcolor', None),
                'subsurfaceColor': shaderData.get('subsurfacecolor',
                                                  shaderData.get('scatter', None)),
                'transmission': shaderData.get('transmission', None)}
        # displacementShader = shaderData.get('height',
        #                                     shaderData.get('DM', None))
        normalCamera = shaderData.get('normal',
                                      shaderData.get('NM', None))
        bump = shaderData.get('bump', None)

        # delete shading engine if already exists
        if mc.objExists(shader):
            try:
                connections = [x for x in mc.listConnections(shader) if x != 'defaultShaderList1']
                if connections:
                    try:
                        SGs = mc.ls(connections, type='shadingEngine')
                        if SGs:
                            for sg in SGs:
                                geos = mc.listConnections(sg + '.dagSetMembers', type='mesh') or []
                                geos += mc.listConnections(sg + '.dagSetMembers', type='nurbsSurface') or []
                                if geos:
                                    applyMtl('lambert1', geos)
                        mc.delete(connections)
                    except:
                        pass
                try:
                    mc.delete(shader)
                except:
                    pass
            except:
                pass

        # create material
        mat = mc.shadingNode('aiStandardSurface', asShader=True, name=shader)

        mc.setAttr(mat + '.base', 1)
        mc.setAttr(mat + '.specular', 1)

        if data['subsurfaceColor']:
            mc.setAttr(mat + '.subsurface', 1)

        for attr, texture in data.items():
            if not texture:
                continue
            textureName = os.path.splitext(os.path.basename(texture))[0]
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', texture, type="string")

            if attr.lower().endswith('color'):
                mc.setAttr(f + '.colorSpace', 'sRGB', type='string')
            else:
                mc.setAttr(f + '.colorSpace', 'Raw', type='string')

            try:
                mc.connectAttr(f + '.outColor', mat + '.' + attr)
            except:
                mc.connectAttr(f + '.outAlpha', mat + '.' + attr)
                mc.setAttr(f + '.alphaIsLuminance', 1)

        if normalCamera:
            textureName = normalCamera.split(os.path.sep)[-1].split('.')[0]
            bmp = mc.createNode('bump2d', name=textureName + '_BMP')
            mc.setAttr(bmp + '.bumpInterp', 1)
            mc.setAttr(bmp + '.aiFlipG', 0)
            mc.setAttr(bmp + '.aiFlipR', 0)
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', normalCamera, type="string")
            mc.setAttr(f + '.colorSpace', 'Raw', type='string')
            mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
            mc.connectAttr(bmp + '.outNormal', mat + '.normalCamera')

        elif bump:
            textureName = bump.split(os.path.sep)[-1].split('.')[0]
            bmp = mc.createNode('bump2d', name=textureName + '_BMP')
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', bump, type="string")
            mc.setAttr(f + '.colorSpace', 'Raw', type='string')
            mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
            mc.connectAttr(bmp + '.outNormal', mat + '.normalCamera')


def getIndexOfUVset(node, uvSet):
    indices = mc.polyUVSet(node, query=True, allUVSetsIndices=True)
    for i in indices[:]:
        name = mc.getAttr(node + ".uvSet[" + str(i) + "].uvSetName")
        if name == uvSet:
            return i
    mc.error('uvSet "{0}" was not found on node "{1}"'.format(uvSet, node))


def getAvailUVchooseIndex(uvChoose):
    """ get first available index of uvChoose.uvSets[x]"""
    i = 0
    while True:
        index = mc.listConnections('{0}.uvSets[{1}]'.format(uvChoose, i))
        if not index:
            return i
        i += 1


def makeTransparent(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    else:
        nodes = mc.ls(nodes)
    meshes = [trsLib.getShapeOfType(x, type="mesh", fullPath=True)[0] for x in nodes]
    for mesh in meshes:
        mc.setAttr(mesh + '.aiOpaque', 0)


def makeTexturesRaw():
    files = mc.ls(type='file')

    for f in files:
        if f.endswith('DM_TEX') or f.endswith('oughness_TEX') or f.endswith('ormal_TEX'):
            attrLib.setAttr(f + '.colorSpace', 'Raw')
            attrLib.lockHideAttrs(f, attrs=['colorSpace'], lock=True)


def addGamma(value=0.4545):
    files = mc.ls(type='file')

    for f in files:
        outs = mc.listConnections(f + '.outColor', plugs=True)
        if not outs:
            continue
        for out in outs:
            outNode, outAttr = out.split('.')
            if mc.nodeType(outNode) == 'aiStandard':
                if outAttr == 'KsColor' or outAttr == 'color':
                    mc.setAttr(f + '.colorSpace', 'Raw', type='string')
                    gamma = mc.createNode('gammaCorrect', n=f.replace('_TEX', '_GAM'))
                    mc.setAttr(gamma + '.gamma', value, value, value)
                    mc.connectAttr(f + '.outColor', gamma + '.value')
                    mc.connectAttr(gamma + '.outValue', out, f=True)


def fixTextureNodeNames():
    files = mc.ls(type='file')

    for f in files:
        # rename file
        fileName = mc.getAttr(f + '.fileTextureName')
        name = os.path.splitext(os.path.basename(fileName))[0]
        newName = mc.rename(f, name + '_TEX')
        # rename place2dTexture
        p2d = mc.listConnections(newName, type='place2dTexture')
        if p2d:
            mc.rename(p2d[0], newName.replace('_TEX', '_P2D'))
        # rename displacementShader
        disp = mc.listConnections(newName, type='displacementShader')
        if disp:
            mc.rename(disp[0], newName.replace('_TEX', '_DSP'))


def replaceTextureDir(newDir, useSelection=False, ignorePaintedTextures=False):
    """
    reload(renderLib)
    newDir = 'D:/all_works/01_projects/ehsan_projects/asset/cartoonGirlB/product/texture/v0002/render'
    renderLib.replaceTextureDir(newDir)
    """
    for f in mc.ls(sl=useSelection, type='file'):
        fileName = mc.getAttr(f + '.fileTextureName')
        name = os.path.basename(fileName)
        fullPath = os.path.join(newDir, name)

        #
        if ignorePaintedTextures and '3dPaintTextures' in f:
            continue

        #
        colorSpaceVal = mc.getAttr(f + '.colorSpace')
        colorLocked = mc.getAttr(f + '.colorSpace', lock=True)
        if colorLocked:
            mc.setAttr(f + '.colorSpace', lock=False)

        #
        mc.setAttr(f + '.fileTextureName', fullPath, type='string')

        #
        mc.setAttr(f + '.colorSpace', colorSpaceVal, type='string')
        if colorLocked:
            mc.setAttr(f + '.colorSpace', lock=True)


def create3PointLighting(scale=10):
    for node in ['key_light', 'fill_light', 'rim_light', 'ThreePointLighting_GRP']:
        if mc.objExists(node):
            mc.delete(node)

    key = mutils.createLocator("aiAreaLight", asLight=True)
    fill = mutils.createLocator("aiAreaLight", asLight=True)
    rim = mutils.createLocator("aiAreaLight", asLight=True)

    mc.setAttr(key[0] + '.exposure', scale)
    mc.setAttr(fill[0] + '.exposure', scale)
    mc.setAttr(rim[0] + '.exposure', scale)

    key = mc.rename(key[1], "key_light")
    fill = mc.rename(fill[1], "fill_light")
    rim = mc.rename(rim[1], "rim_light")

    mc.setAttr(key + '.t', 5, 1, 5)
    mc.setAttr(key + '.r', 0, 45, 0)

    mc.setAttr(fill + '.t', -5, 1, 5)
    mc.setAttr(fill + '.r', 0, -45, 0)

    mc.setAttr(rim + '.t', 0, 1, -5)
    mc.setAttr(rim + '.r', 0, 180, 0)

    mc.createNode('transform', n='ThreePointLighting_GRP')
    mc.parent(key, fill, rim, 'ThreePointLighting_GRP')

    if mc.objExists('lignht_GRP'):
        mc.parent('ThreePointLighting_GRP', 'light_GRP')

    mc.setAttr('ThreePointLighting_GRP.s', scale, scale, scale)


def makeTexturePathsRelative(useSelection=True):
    if useSelection:
        files = mc.ls(sl=True, type='file')
    else:
        files = mc.ls(type='file')

    for f in files:
        # rename file
        fileName = mc.getAttr(f + '.fileTextureName')
        name = os.path.basename(fileName)
        attrLib.lockHideAttrs(f, attrs=['colorSpace', 'fileTextureName'], lock=False)
        attrLib.setAttr(f + '.fileTextureName', name)

    makeTexturesRaw()


def getCurrentCamera():
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    return camPath


def prepareCameraForPlayblast():
    cam = getCurrentCamera()
    data = {'displayFilmGate': 0,
            'displayResolution': 0,
            'overscan': 1}
    old_data = {}
    for attr, value in data.items():
        old_data[attr] = mc.getAttr(cam + '.' + attr)
        mc.setAttr(cam + '.' + attr, value)
    return old_data


def restoreCameraAfterPlayblast(data):
    cam = getCurrentCamera()
    for attr, value in data.items():
        mc.setAttr(cam + '.' + attr, value)


def playblast(name=None, extension='tga', resolution=(2220, 1220), video=False, blastDir=None):
    """
    reload(renderLib)
    # playblast image
    renderLib.playblast(name='viewport_subdivL2', extension='tga', resolution=[1480, 800])
    # playblast video
    renderLib.playblast(resolution=[960, 540], video=True)
    """
    sceneName = mc.file(q=True, sceneName=True)
    if not sceneName:
        mc.error('Please save the file first!')

    fileFullName = os.path.basename(sceneName)
    fileName, ext = os.path.splitext(fileFullName)  # 'currentSceneName', 'mb'
    if not name:
        name = fileName

    if video:
        if not blastDir:
            blastDir = os.path.join(sceneName.split('maya')[0], 'maya', 'movies')
        output = os.path.abspath(os.path.join(blastDir, name))
        try:
            imageDir = mc.playblast(format='qt', filename=output, sequenceTime=0, clearCache=1,
                                    viewer=0, showOrnaments=0, offScreen=1, fp=4, percent=100,
                                    compression='H.264', quality=100, widthHeight=resolution)
        except:
            imageDir = mc.playblast(format='avi', filename=output, sequenceTime=0, clearCache=1,
                                    viewer=1, showOrnaments=0, offScreen=True, fp=4, percent=100,
                                    compression="MS-CRAM", quality=100, widthHeight=(960, 540))
    else:
        if not blastDir:
            blastDir = os.path.join(sceneName.split('maya')[0], 'maya', 'images', name)
        output = os.path.abspath(os.path.join(blastDir, name))
        imageDir = mc.playblast(format='image', filename=output, sequenceTime=0, clearCache=1,
                                viewer=0, showOrnaments=0, offScreen=1, fp=4, percent=100,
                                compression=extension, quality=100, widthHeight=resolution)

    print imageDir


def uvSnapshot(name='uv', extension='tga', resolution=(1024, 1024)):
    """
    reload(renderLib)
    renderLib.uvSnapshot(name='uv', extension='tga', resolution=[1024, 1024])
    """
    sceneName = mc.file(q=True, sceneName=True)
    if sceneName:
        fileFullName = os.path.basename(sceneName)
        fileName, ext = os.path.splitext(fileFullName)  # 'currentSceneName', 'mb'

        if not name:
            name = fileName
        sceneDir = os.path.join(sceneName.split('Scenefiles')[0], 'Export', name)

        objs = mc.ls(sl=True)
        for obj in objs:
            if not os.path.exists(sceneDir):
                os.makedirs(sceneDir)
            output = os.path.join(sceneDir, obj + '.' + extension)
            output = output.replace('\\', '/')
            mc.select(obj)
            mc.uvSnapshot(n=output, aa=1, xr=resolution[0],
                          yr=resolution[1], r=255, g=255, b=255, o=1, ff=extension)
    else:
        mc.error('Please save the file first!')


def getAllMaterials():
    ignoreList = ['lambert1']
    sgs = mc.ls(type='shadingEngine')
    validMats = []
    for sg in sgs:
        mat = mc.listConnections(sg + '.surfaceShader')
        if not mat or mat[0] in ignoreList:
            continue
        validMats.append(mat[0])
    return validMats


def getAllSGs():
    return mc.ls(type='shadingEngine')


def getShaderNetwork(node, node_data=None):
    if not node_data:
        node_data = {}

    nodeType = mc.nodeType(node)
    node_data[node] = {'type': nodeType, 'connection': {}}

    changedAttrsAndVals_data = attrLib.getChangedAttrsAndTheirVals(node)
    node_data[node].update(changedAttrsAndVals_data)

    # find geos  and displacement if node is material
    if mc.attributeQuery('outColor', node=node, exists=True):
        SGs = mc.listConnections(node + '.outColor', s=False, d=True) or []
        SGs = [x for x in SGs if mc.nodeType(x) == 'shadingEngine']
        for SG in SGs:
            geos = mc.listConnections(SG + '.dagSetMembers') or []
            if 'geos' not in node_data[node]:
                node_data[node]['geos'] = []
            node_data[node]['geos'].extend(geos)
            disp = mc.listConnections(SG + '.displacementShader')
            if disp:
                node_data[node]['displacementShader'] = disp[0]
                getShaderNetwork(disp[0], node_data)

    # changed attributes
    for attr, v in changedAttrsAndVals_data.items():
        node_data[node][attr] = v

    # attributes with incoming connection
    ignoreNodesList = ('place2dTexture', 'colorManagementGlobals')
    for attr, inn in attrLib.getAttrsWithIncomingConnection(
            node=node, ignoreNodesList=ignoreNodesList).items():
        node_data[node]['connection'][attr] = inn
        node_data = getShaderNetwork(inn.split('.')[0], node_data)

    return node_data


def exportMaterials(path):
    mat_data = {}
    for mat in getAllMaterials():
        mat_data.update(getShaderNetwork(mat))
    fileLib.saveJson(path, mat_data)


def importMaterials(path, ns=''):
    nodeNetwork = fileLib.loadJson(path)

    # create node
    for node, data in nodeNetwork.items():
        if mc.objExists(node):
            try:
                mc.delete(node)
            except:
                pass
        typ = data.pop('type')
        if 'geos' in data:
            mc.shadingNode(typ, asShader=True, n=node)
        elif typ == 'file':
            mc.shadingNode(typ, asTexture=True, n=node)
        else:
            mc.createNode(typ, n=node)

        # set attributes
        for attr, v in data.items():
            if attr in ('displacementShader', 'connection', 'geos'):
                continue
            else:
                attrLib.setAttr(node + '.' + attr, v)

    # connect nodes
    for node, data in nodeNetwork.items():
        for attr, attr_data in data.items():
            if attr == 'connection':
                for at, inputPlug in attr_data.items():
                    mc.connectAttr(inputPlug, node + '.' + at)

    # assign materials
    allInvalidGeos = []
    for node, data in nodeNetwork.items():
        if 'geos' not in data:
            continue
        geos = data['geos']
        validGeos = []
        invalidGeos = []
        for geo in geos:
            validGeo = mc.ls(ns + ':' + geo)
            if validGeo:
                validGeos.append(validGeo)
            else:
                invalidGeos.append(geo)
        if invalidGeos:
            allInvalidGeos.append(invalidGeos)
        sg = applyMtl(node, validGeos)

        if 'displacementShader' in data:
            disp = data['displacementShader']
            mc.connectAttr(disp + '.displacement', sg + '.displacementShader')

    if allInvalidGeos:
        for geo in allInvalidGeos:
            print geo
        mc.warning('Materials imported successfully, but missing some geos [ see script editor ]')

    makeTexturesRaw()

    return allInvalidGeos


def importRenderSetup(filePath):
    highest = workspace.getHighestFile(filePath)
    if mc.objExists('renderSetup_GRP'):
        mc.delete('renderSetup_GRP')
    mc.file(highest, i=True)


def deleteExtraRenderLayers():
    rls = mc.ls(type='renderLayer')
    for rl in rls:
        try:
            mc.delete(rl)
        except:
            pass


def applyMtl(mat, geos):
    if isinstance(geos, basestring):
        geos = mc.ls(geos)

    # find or create shading engine
    if not mc.ls(mat):
        return
    SGs = mc.listConnections(mat + '.outColor', s=False, d=True) or []
    SGs = [x for x in SGs if mc.nodeType(x) == 'shadingEngine']
    if not SGs:
        sg = mat.replace('_MTL', '') + '_SG'
        sg = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
        mc.connectAttr(mat + '.outColor', sg + '.surfaceShader')
    else:
        sg = SGs[0]

    # connect geo to shading engine
    for g in geos:
        shapes = mc.listRelatives(g, s=True, ni=True)
        if not shapes:
            continue
        attr = shapes[0] + '.instObjGroups'
        oldSGs = mc.listConnections(attr, type='shadingEngine', s=False, d=True, plugs=True)
        if oldSGs:
            attrLib.disconnectAttr(oldSGs[0])
        mc.connectAttr(attr, sg + '.dagSetMembers', nextAvailable=True, f=True)

    return sg


def substanceToMayaSoftware(textureDir):
    """
    """
    textures = [x for x in os.listdir(textureDir) if
                os.path.isfile(os.path.join(textureDir, x))]

    attrsAndTextures = {}
    for texture in textures:
        shader, _, attrInfo = texture.rpartition('_')
        shader = shader + '_MTL'
        attr, extension = attrInfo.split('.')
        if extension not in ('jpg', 'png'):
            continue
        if shader not in attrsAndTextures:
            attrsAndTextures[shader] = {}
        attrsAndTextures[shader][attr.lower()] = os.path.join(textureDir, texture)

    for shader, shaderData in attrsAndTextures.items():
        data = {'color': shaderData.get('basecolor', None),
                'specularColor': shaderData.get('metalness',
                                                shaderData.get('roughness',
                                                               shaderData.get('SpecularColor', None)))}
        normalCamera = shaderData.get('normal',
                                      shaderData.get('NM', None))
        bump = shaderData.get('bump', None)

        # delete shading engine if already exists
        if mc.objExists(shader):
            try:
                connections = [x for x in mc.listConnections(shader) if x != 'defaultShaderList1']
                if connections:
                    try:
                        SGs = mc.ls(connections, type='shadingEngine')
                        if SGs:
                            for sg in SGs:
                                geos = mc.listConnections(sg + '.dagSetMembers', type='mesh') or []
                                geos += mc.listConnections(sg + '.dagSetMembers', type='nurbsSurface') or []
                                if geos:
                                    applyMtl('lambert1', geos)
                        mc.delete(connections)
                    except:
                        pass
                try:
                    mc.delete(shader)
                except:
                    pass
            except:
                pass

        # create material
        mat = mc.shadingNode('blinn', asShader=True, name=shader)

        mc.setAttr(mat + '.diffuse', 1)

        for attr, texture in data.items():
            if not texture:
                continue
            textureName = texture.split(os.path.sep)[-1].split('.')[0]
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', texture, type="string")
            if attr.lower().endswith('color'):
                mc.setAttr(f + '.colorSpace', 'sRGB', type='string')
            else:
                mc.setAttr(f + '.colorSpace', 'Raw', type='string')
            try:
                mc.connectAttr(f + '.outColor', mat + '.' + attr)
            except:
                mc.connectAttr(f + '.outAlpha', mat + '.' + attr)
                mc.setAttr(f + '.alphaIsLuminance', 1)

        if normalCamera:
            textureName = normalCamera.split(os.path.sep)[-1].split('.')[0]
            bmp = mc.createNode('bump2d', name=textureName + '_BMP')
            mc.setAttr(bmp + '.bumpInterp', 1)
            mc.setAttr(bmp + '.aiFlipG', 0)
            mc.setAttr(bmp + '.aiFlipR', 0)
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', normalCamera, type="string")
            mc.setAttr(f + '.colorSpace', 'Raw', type='string')
            mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
            mc.connectAttr(bmp + '.outNormal', mat + '.normalCamera')

        elif bump:
            textureName = bump.split(os.path.sep)[-1].split('.')[0]
            bmp = mc.createNode('bump2d', name=textureName + '_BMP')
            f = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=textureName + '_FLE')
            mc.setAttr(f + '.fileTextureName', bump, type="string")
            mc.setAttr(f + '.colorSpace', 'Raw', type='string')
            mc.connectAttr(f + '.outAlpha', bmp + '.bumpValue')
            mc.connectAttr(bmp + '.outNormal', mat + '.normalCamera')


def renderSequence(frames, melCmd='', resolution=[1280, 720], renderer='arnold', sample=3):
    """
    from rt_python.lib import renderLib
    reload(renderLib)
    frames = [1, 10, 20, 45, 81]
    renderLib.renderSequence(frames=frames,
                             melCmd='xgmPreview',
                             resolution=[960, 540],
                             #resolution=[1920, 1080],
                             sample=4)
    """
    mc.optionVar(iv=('renderSequenceAllCameras', 1))

    for f in frames:
        mc.currentTime(f)
        mm.eval(melCmd)
        setRenderSetings(start=f, end=f, resolution=resolution,
                         renderer=renderer, sample=sample)

        mm.eval('renderSequence;')


def setRenderSetings(resolution=[1280, 720], start=1, end=1, renderer='arnold', sample=3):
    # mc.setAttr('defaultRenderGlobals.imageFilePrefix', '<Scene>/<RenderLayer>/<RenderLayer>', type='string')
    mc.setAttr('defaultRenderGlobals.imageFormat', 40)  # exr
    mc.setAttr('defaultRenderGlobals.animation', 1)
    mc.setAttr('defaultRenderGlobals.animationRange', 0)

    mc.setAttr('defaultRenderGlobals.startFrame', start)
    mc.setAttr('defaultRenderGlobals.endFrame', end)

    mc.setAttr('defaultResolution.width', resolution[0])
    mc.setAttr('defaultResolution.height', resolution[1])

    mc.setAttr('defaultRenderGlobals.currentRenderer', renderer, type='string')
    if renderer == 'arnold':
        mc.setAttr('defaultArnoldDriver.halfPrecision', 1)

        mc.setAttr('defaultArnoldRenderOptions.AASamples', sample)
        mc.setAttr('defaultArnoldRenderOptions.ignoreDisplacement', 0)
        mc.setAttr('defaultArnoldRenderOptions.ignoreSubdivision', 0)
