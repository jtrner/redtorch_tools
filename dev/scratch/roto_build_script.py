"""
import sys
path = os.path.join("G:/Rigging/Users/ehsanm/code_share/redtorch_tools/dev/scratch")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import roto_build_script
reload(roto_build_script)


roto_build_script.post_fix()
#roto_build_script.import_model()
#roto_build_script.create_packs()
#roto_build_script.save_pack_guides()
#roto_build_script.load_pack_guides()
#roto_build_script.create_bits()

"""
import os
import sys
import json

import maya.cmds as mc

for path in sys.path:
    print path
from rt_python.lib import renderLib
from rt_python.lib import connect
from rt_python.lib import attrLib
from rt_python.lib import crvLib
from rt_python.lib import space
from rt_python.lib import control
from rt_python.lib import skincluster
from rt_python.rig.command import pv

import iRigUtil

reload(iRigUtil)
reload(renderLib)
reload(control)

asset_name = 'Roto'
version = 'v0005'
user = 'ehsanm'
userDir = 'Y:/MAW/assets/type/Character/{}/work/rig/Maya/{}'.format(asset_name, user)
buildDir = '{}/{}_using_framework/{}/build'.format(userDir, asset_name, version)


def post_fix():
    importTail()
    import_model()
    assignShaders()
    fixSpine()
    fixPoleVectorPositions()
    setupVis()
    # hideExtraCtls()
    createSpaces()
    importSkinclusters()
    fixCtlPositions()
    matchCtlNamesToFrank()
    importCtlShapes()
    iRigUtil.connectGimbalVis()


def fixPoleVectorPositions():
    for limb in 'leg', 'backLeg':
        for side in 'LR':
            jnts = ['{}_{}_b_jnt'.format(side, limb),
                    '{}_{}_c_jnt'.format(side, limb),
                    '{}_{}_d_jnt'.format(side, limb)]
            pvPos = pv.Pv(jnts=jnts, distance=1.0)
            mc.xform('{}_{}_ik_knee_a_gp'.format(side, limb), ws=True, t=pvPos)


def importTail():
    tail_file = os.path.join(buildDir, 'data/tail.ma')
    mc.file(tail_file, i=True)
    mc.createNode('transform', n='C_tail', p='character_control_gp')
    mc.parent('C_tail_origin_GRP',
              'C_tail_control_GRP',
              'C_tail')
    mc.scaleConstraint('C_spine_e_jnt', 'C_tail_control_GRP')
    mc.setAttr('C_tail_origin_GRP.inheritsTransform', 0)
    mc.parent('C_tail_001_JNT', 'C_fk_tailBase_bind_b_jnt')
    mc.delete('C_tail_module_GRP')
    mc.rename('C_tail_base_CTL', 'C_Tail_Root_Ctrl')


def fixCtlPositions():
    mc.setAttr('C_eye_aim_handle_a_gp.translateZ', 30)


def matchCtlNamesToFrank():
    ctl_map_json = os.path.join(buildDir, 'data/frame_to_frank_control_map.json')
    with open(ctl_map_json, 'r') as f:
        ctl_map_data = json.load(f)

    for oldName, newName in ctl_map_data.items():
        # rename gimbal
        children = mc.listRelatives(oldName) or []
        for child in children:
            if 'gimbal' in child:
                gimbal_new_name = newName.replace('Ctrl', 'Gimbal_Ctrl')
                mc.rename(child, gimbal_new_name)
        # rename ctl
        mc.rename(oldName, newName)


def importSkinclusters():
    path = os.path.join(buildDir, 'data/skincluster')
    skincluster.importData(path)


def importCtlShapes():
    print buildDir
    path = os.path.join(buildDir, 'data/ctls.ma')
    control.Control.importCtls(path)


def createSpaces():
    # left back leg pole vector
    drivers = {'drivers': ['C_spine_a_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['hip', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['L_backLeg_ik_knee_b_gp'],
        control='L_backLeg_ik_knee_Ctrl',
        name='L_backLeg_ik_knee_follow')

    # right back leg pole vector
    drivers = {'drivers': ['C_spine_a_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['hip', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['R_backLeg_ik_knee_b_gp'],
        control='R_backLeg_ik_knee_Ctrl',
        name='R_backLeg_ik_knee_follow')

    # left front leg pole vector
    drivers = {'drivers': ['C_spine_e_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['chest', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['L_leg_ik_knee_b_gp'],
        control='L_leg_ik_knee_Ctrl',
        name='L_leg_ik_knee_follow')

    # right front leg pole vector
    drivers = {'drivers': ['C_spine_e_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['chest', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['R_leg_ik_knee_b_gp'],
        control='R_leg_ik_knee_Ctrl',
        name='R_leg_ik_knee_follow')

    # left back leg
    drivers = {'drivers': ['C_spine_a_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['hip', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['L_backLeg_ik_ankle_b_gp'],
        control='L_backLeg_ik_ankle_Ctrl',
        name='L_backLeg_ik_ankle_follow')

    # right back leg
    drivers = {'drivers': ['C_spine_a_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['hip', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['R_backLeg_ik_ankle_b_gp'],
        control='R_backLeg_ik_ankle_Ctrl',
        name='R_backLeg_ik_ankle_follow')

    # left front leg
    drivers = {'drivers': ['C_spine_e_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['chest', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['L_leg_ik_ankle_b_gp'],
        control='L_leg_ik_ankle_Ctrl',
        name='L_leg_ik_ankle_follow')

    # right front leg
    drivers = {'drivers': ['C_spine_e_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['chest', 'cog', 'ground'],
               'dv': 2}
    space.parent(
        drivers=drivers,
        drivens=['R_leg_ik_ankle_b_gp'],
        control='R_leg_ik_ankle_Ctrl',
        name='R_leg_ik_ankle_follow')

    # tail orient only
    mc.pointConstraint('C_fk_tailBase_b_jnt', 'C_tail_base_ZRO', mo=True)
    drivers = {'drivers': ['C_fk_tailBase_b_jnt',
                           'C_spine_a_jnt',
                           'COG_gimbal_Ctrl',
                           'C_main_ground_gimbal_Ctrl'],
               'attrNames': ['tailBase', 'hip', 'cog', 'ground'],
               'dv': 3}
    space.orient(
        drivers=drivers,
        drivens=['C_tail_base_ZRO'],
        control='C_Tail_Root_Ctrl',
        name='C_tail_base_follow')

    #
    mc.parentConstraint('COG_gimbal_Ctrl', 'character_settings_a_gp', mo=True)


def hideExtraCtls():
    ctls = ['C_tail_root_handle_Ctrl']
    for ctl in ctls:
        shapes = crvLib.getShapes(ctl)
        [mc.setAttr(x + '.v', 0) for x in shapes]


def setupVis():
    mainCtl = 'character_settings_Ctrl'
    geoGrp = 'Geo_Grp'
    rigGrp = 'character_deform_gp'

    #
    mc.deleteAttr(mainCtl, attribute='utility_geometry_vis')
    mc.deleteAttr(mainCtl, attribute='geometry_vis')

    # geo visibility swtich
    a = attrLib.addEnum(mainCtl, 'geoVis', en=['off', 'on'], dv=1)
    mc.connectAttr(a, geoGrp + '.v')

    # rig visibility swtich
    a = attrLib.addEnum(mainCtl, 'rigVis', en=['off', 'on'], dv=1)
    mc.connectAttr(a, rigGrp + '.v')

    # geo selectablity swtich
    a = attrLib.addEnum(mainCtl, 'geoSelectable', en=['off', 'on'])
    connect.reverse(a, geoGrp + '.overrideEnabled')
    mc.setAttr(geoGrp + '.overrideDisplayType', 2)

    # rig selectablity swtich
    a = attrLib.addEnum(mainCtl, 'rigSelectable', en=['off', 'on'])
    connect.reverse(a, rigGrp + '.overrideEnabled')
    mc.setAttr(rigGrp + '.overrideDisplayType', 2)

    #
    nodes = mc.listRelatives('character_deform_gp', ad=True, type='transform')
    for node in nodes:
        mc.setAttr(node + '.overrideEnabled', 0)


def fixSpine():
    aim_nodes = mc.ls('C_spine_ik_upper_torso_gimbal_Ctrl_C_spine_ik_lower_aim_gp_acn',
                      'C_spine_ik_c_Ctrl_C_spine_ik_b_jnt_acn')
    for aim in aim_nodes:
        mc.setAttr(aim + '.rotate', 0, 0, 0)
        mc.setAttr(aim + '.worldUpVector', 0, 1, 0)


def import_model():
    model_dir = 'Y:/MAW/assets/type/Character/{}/products/model'.format(asset_name)
    model_path = sorted(os.listdir(model_dir))[-1]
    mc.file(os.path.join(model_dir, model_path), i=True)

    #
    if mc.objExists('character'):
        mc.parent('Geo_Grp', 'character')
    else:
        mc.parent('Geo_Grp', world=True)
    mc.delete('Character_Grp')

    # fix modeling shit
    mc.setAttr('Model_A_Grp.tx', -20.175)

    #
    mc.hide(mc.ls('character_utilities_gp', 'Model_B_Grp'))

    # # put fur in a template
    # for geo in mc.listRelatives('Model_A_Grp'):
    #     mc.setAttr(geo + '.overrideEnabled', True)
    #     mc.setAttr(geo + '.overrideDisplayType', 2)


def assignShaders():
    #
    renderLib.assignShader('body_Geo',
                           color=[0.8, 0.45, 0.8],
                           eccentricity=[0.5],
                           diffuse=[1],
                           specularColor=[0.2, 0.2, 0.2],
                           name='body_proxy_mtl')

    #
    furOpacityAt = attrLib.addFloat('character_settings_Ctrl', 'furOpacity', min=0, max=1, dv=0.8)
    furMtl = renderLib.assignShader('fur_groom_volume_Geo',
                           color=[0.8, 0.45, 0.8],
                           transparency=[0.25, 0.25, 0.25],
                           diffuse=[1],
                           specularColor=[0, 0, 0],
                           name='fur_proxy_mtl')
    [mc.connectAttr(furOpacityAt, furMtl + '.transparency' + x) for x in 'RGB']

    renderLib.assignShader(['horn_L_Geo', 'horn_R_Geo'],
                           color=[0.88, 0.46, 0.6],
                           name='horn_proxy_mtl')

    renderLib.assignShader(['teeth_upper_Geo', 'teeth_lower_Geo'],
                           color=[0.8, 0.8, 0.8],
                           name='teeth_proxy_mtl')

    #
    eye_mtl = renderLib.assignShader('eye_Geo',
                                     color=[0.8, 0.8, 0.8],
                                     diffuse=[1],
                                     eccentricity=[0.15],
                                     specularColor=[0.5, 0.5, 0.5],
                                     name='eye_proxy_mtl')

    ramp, place2d = renderLib.createEyeRamp(name='eye_mtl')
    mc.setAttr(ramp + '.colorEntryList[1].position',  0.12)
    mc.setAttr(ramp + '.colorEntryList[2].position',  0.19)
    mc.setAttr(ramp + '.colorEntryList[3].position',  0.21)
    mc.setAttr(place2d + '.translateFrameU',  - 0.2)
    mc.setAttr(place2d + '.translateFrameV',  - 0.2)

    mc.connectAttr(ramp+'.outColor', eye_mtl + '.color')
