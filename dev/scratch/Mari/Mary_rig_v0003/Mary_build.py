"""

# ==========================================================================================
# build rig
import maya.cmds as mc

import sys


ASSET_NAME = 'Mary'
VERSION = 'v0003'

paths = ["G:/Rigging/Shows/MAW",
         "Y:/MAW/assets/type/Character/{0}/work/rig/Maya/ehsanm/{0}_build_scripts/{0}_rig_{1}".format(ASSET_NAME, VERSION)]

for path in paths:
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)

import Mary_build
reload(Mary_build)

Mary_build.run()

# ==========================================================================================
# export sdk
import maya.cmds as mc

import sys
path = os.path.join("G:/Rigging/Shows/MAW")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

from maw_scripts import maw_utils
reload(maw_utils)

ASSET_NAME = 'Mary'
VERSION = 'v0003'

for ctlDrvr in mc.ls('*_ControlDriver'):
    sdkDataDir = 'Y:/MAW/assets/type/Character/{asset_name}/work/rig/Maya/ehsanm/build_scripts/{asset_name}_rig_{version}/data/sdk'
    sdkDataDir = sdkDataDir.format(asset_name=ASSET_NAME, version=VERSION)
    maw_utils.export_sdk(ctlDrvr, sdkDataDir)

"""
# python modules
import os
import itertools

# maya modules
import maya.cmds as mc

# iRig modules

from iRig_maya.lib import attrLib
from iRig_maya.lib import renderLib
from iRig_maya.lib import display
from iRig_maya.lib import connect
from iRig_maya.lib import crvLib
from iRig_maya.lib import space
from iRig_maya.lib import control
from iRig_maya.lib import deformLib
from iRig_maya.lib import pv
from iRig_maya.lib import trsLib
from iRig_maya.lib import decoratorLib
from iRig_maya.lib import renameLib

# MAW modules
from maw_scripts import eye_projection
from maw_scripts import cartoon_eyelid

# reload
reload(attrLib)
reload(renderLib)
reload(connect)
reload(crvLib)
reload(space)
reload(control)
reload(deformLib)
reload(pv)
reload(trsLib)
reload(decoratorLib)
reload(renameLib)
reload(eye_projection)
reload(cartoon_eyelid)

# show modules
from maw_scripts import maw_utils

# constants
ASSET_NAME = 'Mary'
print('{:.^50}'.format(ASSET_NAME))


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


index_dict = create_alpha_dictionary(depth=2)
letter_dict = {v: k for k, v in index_dict.items()}


def run():
    mc.file(new=True, f=True)
    import_puppet()
    import_model()
    import_skeleton()
    fix_model_issues()
    fix_hierarchy()
    rename_ctls_and_jnts()
    rename_spine_names()
    rename_spline_jnts()
    rename_LayeredRibbonSplineChain(rootName='01_EyeStalk')
    rename_LayeredRibbonSplineChain(rootName='02_EyeStalk')
    rename_LayeredRibbonSplineChain(rootName='Tail')
    rename_eyes()
    rename_arms()
    rename_gimbal()
    rename_ctl_parents()
    add_eye_gimbal()
    create_spaces()
    rename_attributes()
    # import_face()
    import_ctl_shapes()
    # fix_tongue_rig_hierarchy()
    # import_face_sdk()
    # fix_jaw_side_to_side_sdk()
    # maw_utils.createZipLip()
    # adjust_zip_lip()
    # fix_hand_rig()
    connect_gimbal_vis()
    setup_vis()
    assign_shaders()
    eye_projection.load_export_data()
    fix_export_data_names()
    eye_projection.check_and_update_export_data()
    eye_projection.eyeProjection_setup(
        eye_num=5,
        eye_root_names=['R_02', 'R_01', 'C_01', 'L_01', 'L_02'],
        model_eye_root_names=['A', 'B', 'C', 'D', 'E']
    )
    renameLib.fixShapeNames(objs=mc.ls('*Ctrl'))
    # reset_tongue_joint_orient()
    # setup_eyelids()
    import_skinclusters()
    # rig_body()
    # rig_glasses()
    # rig_face_upr()
    # rig_face_lwr()
    # reset_tongue_joint_orient()
    rig_eyes()
    rig_cross_eye()
    # skin_lattice()
    # lock_hide_attrs()
    maw_utils.set_arnold_settings()
    go_to_t_pose()
    # mimic_gimbal_shapes()


def fix_export_data_names():
    for node in mc.ls('*floatConstant1_ExportData'):
        new_name = node.replace('1_ExportData', '_ExportData')
        mc.rename(node, new_name)


def go_to_t_pose():
    trsLib.resetTRS('C_Spine_settings_Ctrl')


def rename_arms():
    rename_map = {
        '{side}_Arm_ik_wrist_Ctrl': '{side}_Arm_Wrist_Ik_Ctrl',
        '{side}_Arm_ik_elbow_Ctrl': '{side}_Arm_PoleVector_Ctrl',

        '{side}_Arm_fk_upper_Ctrl': '{side}_Arm_Shoulder_Fk_Ctrl',
        '{side}_Arm_fk_lower_Ctrl': '{side}_Arm_Elbow_Fk_Ctrl',
        '{side}_Arm_fk_wrist_Ctrl': '{side}_Arm_Wrist_Fk_Ctrl',

        '{side}_Arm_bendy_up_arm_Ctrl': '{side}_Arm_Top_Bend_Mid_Ctrl',
        '{side}_Arm_bendy_elbow_Ctrl': '{side}_Arm_Top_Bend_Bendy_Ctrl',
        '{side}L_Arm_bendy_forearm_Ctrl': '{side}_Arm_Btm_Bend_Mid_Ctrl',
    }
    for side in ['L', 'R']:
        for oldName, newName in rename_map.items():
            oldName = oldName.format(side=side)
            newName = newName.format(side=side)
            if mc.objExists(oldName):
                mc.rename(oldName, newName)


def create_spaces():
    for side in 'LR':
        # shoulder fk
        drivers = {
            'drivers': [
                '{}_Arm_clavicle_Gimbal_Ctrl'.format(side),
                'Ground_Gimbal_Ctrl',
                'COG_Gimbal_Ctrl',
                'Root_Gimbal_Ctrl',
                'C_Spine_e_jnt'
            ],
            'attrNames': ['Clavicle', 'Ground', 'Cog', 'Root', 'Chest'],
            'dv': 0}
        space.orient(
            drivers=drivers,
            drivens=['{}_Arm_Shoulder_Fk_Ctrl_Drv_Grp'.format(side)],
            control='{}_Arm_Shoulder_Fk_Ctrl'.format(side),
            name='{}_Arm_Shoulder_Fk_follow'.format(side))

        # ik wrist
        drivers = {
            'drivers': [
                '{}_Arm_Wrist_Ik_Ctrl_Offset_Grp'.format(side),
                'C_Spine_e_jnt',
                'C_Spine_a_jnt',
                'COG_Gimbal_Ctrl',
                'Ground_Gimbal_Ctrl',
                'Root_Gimbal_Ctrl',
                'C_Head_Gimbal_Ctrl'
            ],
            'attrNames': ['Anim_Constraint', 'Chest', 'Hips', 'Cog', 'Ground', 'Root', 'Head'],
            'dv': 0}
        space.orient(
            drivers=drivers,
            drivens=['{}_Arm_Wrist_Ik_Ctrl_Drv_Grp'.format(side)],
            control='{}_Arm_Wrist_Ik_Ctrl'.format(side),
            name='{}_Arm_Wrist_Ik_follow'.format(side))

        # arm pole vector
        drivers = {
            'drivers': [
                '{}_Arm_Wrist_Ik_Gimbal_Ctrl'.format(side),
                'COG_Gimbal_Ctrl',
                'Ground_Gimbal_Ctrl',
                'Root_Gimbal_Ctrl'
            ],
            'attrNames': ['Wrist', 'Cog', 'Ground', 'Root'],
            'dv': 0}
        space.parent(
            drivers=drivers,
            drivens=['{}_Arm_PoleVector_Ctrl_Drv_Grp'.format(side)],
            control='{}_Arm_PoleVector_Ctrl'.format(side),
            name='{}_Arm_PoleVector_follow'.format(side))

    # head
    drivers = {
        'drivers': [
            'C_Neck_02_Gimbal_Ctrl',
            'Ground_Gimbal_Ctrl',
            'Root_Gimbal_Ctrl',
            'C_Spine_e_jnt'
        ],
        'attrNames': ['Neck', 'Ground', 'Root', 'Chest'],
        'dv': 0}
    space.orient(
        drivers=drivers,
        drivens=['C_Head_Ctrl_Drv_Grp'],
        control='C_Head_Ctrl',
        name='C_Head_follow')

    # eyeStalk point
    mc.parentConstraint(
        'C_01_EyeStalk_Ik_05_Ctrl',
        'C_01_EyeMain_Ctrl_Drv_Grp',
        sr=['x', 'y', 'z'],
        mo=True
    )

    # eyeStalk orient
    for side in ['C_01', 'L_01', 'L_02', 'R_01', 'R_02']:
        drivers = {
            'drivers': [
                '{}_EyeStalk_Ik_05_Ctrl'.format(side),
                'Head_Gimbal_Ctrl',
                'Ground_Gimbal_Ctrl'
            ],
            'attrNames': ['EyeStalk', 'Head', 'Ground'],
            'dv': 1}
        space.orient(
            drivers=drivers,
            drivens=['{}_EyeMain_Ctrl_Drv_Grp'.format(side)],
            control='{}_EyeMain_Ctrl'.format(side),
            name='{}_EyeMain_follow'.format(side))

    # tail orient only
    # mc.pointConstraint('C_fk_tailBase_b_jnt', 'C_Tail_Root_Ctrl_Offset_Grp', mo=True)
    drivers = {'drivers': ['C_Spine_a_jnt',
                           'COG_Gimbal_Ctrl',
                           'Ground_Gimbal_Ctrl'],
               'attrNames': ['Hip', 'Cog', 'Ground'],
               'dv': 1}
    space.orient(
        drivers=drivers,
        drivens=['C_BodyBase_Ctrl_Drv_Grp'],
        control='C_BodyBase_Ctrl',
        name='C_BodyBase_follow')

    # # eye
    # drivers = {'drivers': ['C_Jaw_Upr_Ctrl',
    #                        'Ground_Gimbal_Ctrl',
    #                        'COG_Gimbal_Ctrl'],
    #            'attrNames': ['Head', 'Cog', 'Ground'],
    #            'dv': 0}
    # space.parent(
    #     drivers=drivers,
    #     drivens=['C_Eye_Root_Ctrl_Drv_Grp'],
    #     control='C_Eye_Root_Ctrl',
    #     name='C_Eye_Root_Ctrl_follow')

    #
    # mc.parentConstraint('COG_Gimbal_Ctrl', 'Control_Ctrl_Offset_Grp', mo=True)
    mc.scaleConstraint('COG_Gimbal_Ctrl', 'Control_Ctrl_Offset_Grp', mo=True)


def fix_jaw_side_to_side_sdk():
    mc.disconnectAttr('Face_C_Jaw_Tweak_rotZ_Blend.output',
                      'Face_C_Jaw_Tweak_Ctrl_Drv_Grp.rotateZ')
    mc.connectAttr('Face_C_Jaw_Tweak_rotZ_Blend.output',
                   'Face_C_Jaw_Tweak_Ctrl_Offset_Grp.rotateZ')


def lock_hide_attrs():
    attrLib.lockHideAttrs('Control_Ctrl', attrs=['t', 'r', 's'])


def adjust_zip_lip():
    mc.setAttr("Face_L_Mouth_Lip_Upr_01_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", 0.7)
    mc.setAttr("Face_L_Mouth_Lip_Upr_02_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", 0.95)
    mc.setAttr("Face_C_Mouth_Lip_Upr_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", 0.1)
    mc.setAttr("Face_R_Mouth_Lip_Upr_01_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", 0.95)
    mc.setAttr("Face_R_Mouth_Lip_Upr_02_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", 0.7)

    mc.setAttr("Face_L_Mouth_Lip_Lwr_02_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", -0.7)
    mc.setAttr("Face_L_Mouth_Lip_Lwr_01_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", -0.95)
    mc.setAttr("Face_C_Mouth_Lip_Lwr_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", -0.1)
    mc.setAttr("Face_R_Mouth_Lip_Lwr_01_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", -0.95)
    mc.setAttr("Face_R_Mouth_Lip_Lwr_02_Tweak_Ctrl_Zip_Grp_parentConstraint1.target[1].targetOffsetTranslateY", -0.7)


def setup_eyelids():
    left_upr_lid_verts = [
        'face_Rig.vtx[4086]',
        'face_Rig.vtx[4087]',
        'face_Rig.vtx[4088]',
        'face_Rig.vtx[4089]',
        'face_Rig.vtx[4090]',
        'face_Rig.vtx[4091]',
        'face_Rig.vtx[4092]',
        'face_Rig.vtx[4093]',
        'face_Rig.vtx[4094]',
        'face_Rig.vtx[4095]',
        'face_Rig.vtx[4096]',
        'face_Rig.vtx[4097]',
        'face_Rig.vtx[4109]']
    left_lwr_lid_verts = [
        'face_Rig.vtx[4083]',
        'face_Rig.vtx[4097]',
        'face_Rig.vtx[4098]',
        'face_Rig.vtx[4099]',
        'face_Rig.vtx[4100]',
        'face_Rig.vtx[4101]',
        'face_Rig.vtx[4102]',
        'face_Rig.vtx[4103]',
        'face_Rig.vtx[4104]',
        'face_Rig.vtx[4106]',
        'face_Rig.vtx[4107]',
        'face_Rig.vtx[4108]',
        'face_Rig.vtx[4109]']
    left_inn_out_jnts = ['Face_L_Eye_Lid_Inner_Bnd_Jnt',
                         'Face_L_Eye_Lid_Outer_Bnd_Jnt']
    left_upr_jnts = ['Face_L_Eye_Lid_Upr_01_Bnd_Jnt',
                     'Face_L_Eye_Lid_Upr_02_Bnd_Jnt',
                     'Face_L_Eye_Lid_Upr_03_Bnd_Jnt']
    left_lwr_jnts = ['Face_L_Eye_Lid_Lwr_01_Bnd_Jnt',
                     'Face_L_Eye_Lid_Lwr_02_Bnd_Jnt',
                     'Face_L_Eye_Lid_Lwr_03_Bnd_Jnt']
    cartoon_eyelid.run(
        prefix='Face_L',
        eye_geo='eye_L_Geo',
        inn_out_jnts=left_inn_out_jnts,
        upr_jnts=left_upr_jnts,
        lwr_jnts=left_lwr_jnts,
        upr_lid_verts=left_upr_lid_verts,
        lwr_lid_verts=left_lwr_lid_verts)
    mc.parent('Face_L_eyelid_util_grp', 'Utility_Grp')

    right_upr_lid_verts = [
        'face_Rig.vtx[2050]',
        'face_Rig.vtx[2051]',
        'face_Rig.vtx[2052]',
        'face_Rig.vtx[2053]',
        'face_Rig.vtx[2054]',
        'face_Rig.vtx[2055]',
        'face_Rig.vtx[2056]',
        'face_Rig.vtx[2057]',
        'face_Rig.vtx[2058]',
        'face_Rig.vtx[2059]',
        'face_Rig.vtx[2060]',
        'face_Rig.vtx[2061]',
        'face_Rig.vtx[2073]']
    right_lwr_lid_verts = [
        'face_Rig.vtx[2061]',
        'face_Rig.vtx[2062]',
        'face_Rig.vtx[2063]',
        'face_Rig.vtx[2064]',
        'face_Rig.vtx[2065]',
        'face_Rig.vtx[2066]',
        'face_Rig.vtx[2067]',
        'face_Rig.vtx[2068]',
        'face_Rig.vtx[2069]',
        'face_Rig.vtx[2070]',
        'face_Rig.vtx[2071]',
        'face_Rig.vtx[2072]',
        'face_Rig.vtx[2073]']
    right_inn_out_jnts = ['Face_R_Eye_Lid_Inner_Bnd_Jnt',
                          'Face_R_Eye_Lid_Outer_Bnd_Jnt']
    right_upr_jnts = ['Face_R_Eye_Lid_Upr_01_Bnd_Jnt',
                      'Face_R_Eye_Lid_Upr_02_Bnd_Jnt',
                      'Face_R_Eye_Lid_Upr_03_Bnd_Jnt']
    right_lwr_jnts = ['Face_R_Eye_Lid_Lwr_01_Bnd_Jnt',
                      'Face_R_Eye_Lid_Lwr_02_Bnd_Jnt',
                      'Face_R_Eye_Lid_Lwr_03_Bnd_Jnt']
    cartoon_eyelid.run(
        prefix='Face_R',
        eye_geo='eye_R_Geo',
        inn_out_jnts=right_inn_out_jnts,
        upr_jnts=right_upr_jnts,
        lwr_jnts=right_lwr_jnts,
        upr_lid_verts=right_upr_lid_verts,
        lwr_lid_verts=right_lwr_lid_verts)
    mc.parent('Face_R_eyelid_util_grp', 'Utility_Grp')


def skin_lattice():
    # set body_Box skinCluster method to dualQuaternion and copy skin to lattice
    skin = deformLib.getSkinCluster('body_Box')
    lattice_skin = deformLib.copySkin('body_Box', 'body_FFD_Lattice')[0]

    mc.setAttr(skin + '.skinningMethod', 1)
    mc.setAttr(lattice_skin + '.skinningMethod', 1)


def create_follicle(surf, u=0.5, v=0.5, name='new_follicle'):
    shape = trsLib.getShapes(surf)[0]

    # create flc and connect to plane
    flcShape = mc.createNode('follicle')
    mc.connectAttr(shape + '.worldMatrix', flcShape + '.inputWorldMatrix')
    mc.connectAttr(shape + '.outMesh', flcShape + '.inputMesh')

    # driver flc transform using flc shape
    flc = mc.listRelatives(flcShape, p=True)[0]
    for j in 'tr':
        for k in 'xyz':
            mc.connectAttr(flcShape + '.o' + j + k, flc + '.' + j + k)

    # make follicle scalable
    for x in 'xyz':
        mc.connectAttr('Root_Ctrl.ScaleXYZ', flc + '.s' + x)

    # position flcs
    mc.setAttr(flcShape + '.parameterU', u)
    mc.setAttr(flcShape + '.parameterV', v)

    # rename flc
    flc = mc.rename(flc, name + '_Flc')

    #
    mc.parent(flc, 'Body_Lattice_Utility_Grp')

    return flc


def rig_body():
    #
    lattice_util_grp = 'Body_Lattice_Utility_Grp'
    if not mc.objExists(lattice_util_grp):
        mc.createNode('transform', n=lattice_util_grp, p='Utility_Grp')

    # add face rig as a blendshape to body
    mc.blendShape('face_Rig', 'body_Geo', n='body_Geo_Bls', w=(0, 1))

    # use body_Box transformation for lattice
    # body_Box is a polyCube that represents the shape and number of CVs on the lattice
    trs = trsLib.getTRS('body_Box')

    # put body is a lattice and skin that instead of skinning body
    geos = ['body_Geo']
    geos += mc.listRelatives('hair_Grp', ad=True, type='mesh')
    geos += mc.listRelatives('mouth_Grp', ad=True, type='mesh')
    ffd_node, lattice, ffdBase = deformLib.createLattice(
        geos=geos,
        name='body_FFD',
        divisions=(2, 20, 2),
        trs=trs,
        base_trs=trs,
        local=False,
        outsideLattice=1,
        outsideFalloffDist=1.0,
        objectCentered=False)

    #
    mc.parent(
        'Flc_Srf_Grp',
        'face_Rig',
        'body_Box',
        'C_hold_Jnt',
        lattice,
        ffdBase,
        lattice_util_grp)


def rig_glasses():
    driven_grp = 'C_Glasses_Ctrl_Drv_Grp'
    surf = driven_grp + '_Srf'

    # deform plane surface using body lattice
    ffd_set = mc.listConnections('body_FFD_LatticeNode.message')[0]
    mc.sets(surf, fe=ffd_set)

    # create a follicle on the plane surface
    flc = create_follicle(surf=surf, u=0.5, v=0.5, name='C_Glasses')

    # delete old constraint
    cns = mc.parentConstraint(driven_grp, q=True)
    if cns:
        mc.delete(cns)

    # drive group using follicle
    mc.parentConstraint(flc, driven_grp, mo=True)


def fix_tongue_rig_hierarchy():
    tongue_jnt_grp = mc.createNode(
        'transform',
        n='Face_Tongue_Joints_Grp',
        p='Face_Bind_Jnt_Grp')
    tongue_jnts = mc.ls('Face_C_Tongue_??_Bnd_Jnt')
    mc.parent(tongue_jnts, tongue_jnt_grp)
    mc.delete('No_Inherit_Face_Grp')

    # for jnt in tongue_jnts:
    #     mc.setAttr(jnt + '.jo', 0, 0, 0)


def rig_cross_eye():
    #
    eye_ctl = 'C_Eye_Root_Ctrl'
    eye_gimbal_ctl = 'C_Eye_Root_Gimbal_Ctrl'

    #
    cross_at = attrLib.addFloat(eye_ctl, 'CrossEye')

    #
    ofs_grps = mc.listRelatives(eye_gimbal_ctl)
    ofs_grps = [x for x in ofs_grps if x.endswith('Offset_Grp')]

    for ofs in ofs_grps:

        # find XEye_Grp is exists
        children = mc.listRelatives(ofs) or []
        x_grp = None
        for grp in children:
            if grp.endswith('XEye_Grp'):
                x_grp = grp
                continue

        # create XEye_Grp if it doesn't exist
        if not x_grp:
            x_grp = trsLib.insert(
                ofs,
                mode='child',
                search='Offset_Grp',
                replace='XEye_Grp'
            )[0]
            if children:
                mc.parent(children, x_grp)

        # get translate x or offset and use it for cross eye
        x_val = mc.getAttr(ofs + '.tx')

        #
        cross_neg = mc.createNode('multiplyDivide', name=ofs + '_CrossEye_Neg')
        mc.connectAttr(cross_at, cross_neg + '.i1x')
        mc.setAttr(cross_neg + '.i2x', x_val)
        mc.connectAttr(cross_neg + '.ox', x_grp + '.tx')


def add_eye_gimbal():
    # add gimbal to eye root
    ctl = control.Control(
        side='C',
        shape='square',
        color='cyan',
        descriptor='Eye_Root_Gimbal',
        matchTranslate='C_Eye_Root_Ctrl',
        matchRotate='C_Eye_Root_Ctrl'
    )

    mc.parent(ctl.zro, 'C_Eye_Root_Ctrl')
    mc.parent('L_01_Eye_Aim_Ctrl_Offset_Grp',
              'L_02_Eye_Aim_Ctrl_Offset_Grp',
              'R_01_Eye_Aim_Ctrl_Offset_Grp',
              'R_02_Eye_Aim_Ctrl_Offset_Grp',
              'C_01_Eye_Aim_Ctrl_Offset_Grp',
              ctl.name)

    attrLib.addInt('C_Eye_Root_Ctrl', 'GimbalVis', min=0, max=1)


def rig_eyes():
    # make eye aim control scalable
    for x in 'xyz':
        mc.connectAttr(
            'Root_Ctrl.ScaleXYZ',
            'C_Eye_Root_Ctrl_Drv_Grp.s' + x
        )


def import_puppet():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data', 'puppet.ma')
    mc.file(path, i=True)


def import_skeleton():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data', 'skeleton.ma')
    mc.file(path, i=True)


def export_face():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data/face.ma')
    mc.group('Face_Ctrl_Grp',
             'Face_Gui_Controls_Grp',
             'Face_Utl_Grp',
             'Face_Bind_Jnt_Grp',
             n='Face_extracted_grp',
             w=True)

    mc.delete('Character')
    mc.select('Face_extracted_grp')
    mc.file(path, force=True, options="v=0;",
            type="mayaAscii", pr=False, exportSelected=True)
    print('Face exported here: {}'.format(path))


def import_face():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data/face.ma')
    mc.file(path, i=True, type="mayaAscii", ignoreVersion=True)

    if mc.objExists('character_control_gp'):
        mc.parent('Face_Gui_Controls_Grp', 'character_control_gp')
        mc.parent('Face_Utl_Grp', 'character_control_gp')

    if mc.objExists('C_Head_Gimbal_Ctrl'):
        mc.parent('Face_Ctrl_Grp', 'C_Head_Gimbal_Ctrl')

    if mc.objExists('character_deform_gp'):
        mc.parent('Face_Bind_Jnt_Grp', 'character_deform_gp')

    if mc.objExists('Jnt_Grp'):
        mc.parent('Face_Bind_Jnt_Grp', 'Jnt_Grp')

    if mc.objExists('Ctrl_Grp'):
        mc.parent('Face_Gui_Controls_Grp', 'Ctrl_Grp')

    if mc.objExists('Utility_Grp'):
        mc.parent('Face_Utl_Grp', 'Utility_Grp')

    if mc.objExists('Bind_Jnt_Grp'):
        mc.parent('Face_Bind_Jnt_Grp', 'Bind_Jnt_Grp')

    if mc.objExists('Face_extracted_grp'):
        mc.delete('Face_extracted_grp')

    # Turn off tweakers
    mc.setAttr("Face_Gui_Ctrl.OnFaceCtrlVis", 0)

    # face gui should be driven by head
    trsLib.setTRS('Face_Gui_Controls_Grp', ([36, 197, 12], [0, 0, 0], [2.3, 2.3, 2.3]))
    mc.parentConstraint('COG_Gimbal_Ctrl', 'Face_Gui_Controls_Grp', mo=True)
    mc.scaleConstraint('COG_Gimbal_Ctrl', 'Face_Gui_Controls_Grp', mo=True)

    # lid control should drive sub lid controls using AutoFollow_Tfm
    for side in 'LCR':
        for position in 'In', 'Mid', 'Out':
            for location in 'Upr', 'Lwr':
                ofs = 'Face_{}_Eye_Lid_{}_{}_Ctrl_Offset_Grp'
                ofs = ofs.format(side, location, position)
                auto = ofs.replace('Offset_Grp', 'AutoFollow_Tfm')
                if mc.objExists(ofs) and mc.objExists(auto):
                    mc.pointConstraint(auto, ofs)

    # brow control should drive sub brow controls using AutoFollow_Tfm
    for side in 'LCR':
        for position in 'In', 'Mid', 'Out':
            ofs = 'Face_{}_Brow_{}_Ctrl_Offset_Grp'
            ofs = ofs.format(side, position)
            auto = ofs.replace('Offset_Grp', 'AutoFollow_Tfm')
            if mc.objExists(ofs) and mc.objExists(auto):
                mc.pointConstraint(auto, ofs)

    # lips control should drive sub lips controls using AutoFollow_Tfm
    for side in 'LCR':
        for position in 'In', 'Mid', 'Out':
            for location in 'Upr', 'Lwr':
                ofs = 'Face_{}_Mouth_Lip{}_Ctrl_Offset_Grp'
                ofs = ofs.format(side, location, position)
                auto = ofs.replace('Offset_Grp', 'AutoFollow_Tfm')
                if mc.objExists(ofs) and mc.objExists(auto):
                    mc.pointConstraint(auto, ofs)

    # some tweakers are not driving scale of joints
    face_jnts = mc.ls('Face_*_Bnd_Jnt')
    for jnt in face_jnts:
        cns = mc.parentConstraint(jnt, q=True)
        if not cns:
            continue
        drvr = mc.parentConstraint(cns, q=True, targetList=True)[0]
        mc.scaleConstraint(drvr, jnt, mo=True)


def import_model(version='latest'):
    # delete geo coming from framework
    if mc.objExists('character_root_geometry_gp'):
        mc.delete('character_root_geometry_gp')

    # import latest model
    model_dir = 'Y:/MAW/assets/type/Character/{}/products/model'.format(ASSET_NAME)
    if version == 'latest':
        model_file = sorted(os.listdir(model_dir))[-1]
    else:
        model_file = '{}/{}_model_{}.ma'.format(model_dir, ASSET_NAME, version)
    model_path = os.path.abspath(os.path.join(model_dir, model_file))
    mc.file(model_path, i=True)

    #
    if mc.objExists('Character'):
        character = 'Character'
        mc.parent('Geo_Grp', 'Character')
    else:
        character = 'character'
        mc.parent('Geo_Grp', world=True)
    mc.delete('Character_Grp')

    # fix normals
    geos = mc.ls(type='mesh')
    [mc.setAttr(x + '.displayColors', 0) for x in geos]
    mc.select(geos)
    mc.UnlockNormals()
    [mc.polySoftEdge(x, a=180, ch=False) for x in geos]
    mc.delete(geos, ch=True)

    # add model version as metadata to Character
    attrLib.addString(character, 'model_file', v=model_path, lock=True)


def import_skinclusters():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data', 'skincluster')
    deformLib.importSkin(path)


def import_face_sdk():
    dirname = os.path.dirname(__file__)
    for ctlDrvr in mc.ls('*_ControlDriver'):
        sdkDataDir = os.path.join(dirname, 'data/sdk')
        sdkDataPath = os.path.join(sdkDataDir, ctlDrvr + '.json')
        maw_utils.import_sdk(sdkDataPath)


def fix_model_issues():
    mc.blendShape('t_pose', 'body_Geo', w=(0, 1))
    mc.delete('body_Geo', ch=True)
    mc.delete('t_pose')


def fix_hierarchy():
    mc.parent('character_utility_gp', 'character_utilities_gp')
    mc.parent('Geo_Grp', 'character')
    mc.parent('character_settings_a_gp', 'COG_gimbal_Ctrl')


def titlize(value):
    """
    capitalizes first letter of given word
    eg: helloWorld -> HelloWorld
    """
    if len(value) > 1:
        return value[0].title() + value[1:]
    return value.title()


def numerize(value, start_num=1):
    """
    converts letters to numbers.
    eg: a -> 01
        b -> 02
    """
    if value in letter_dict:
        return '{:02d}'.format(int(letter_dict[value]) + start_num)
    return value.title()


def rename_spine_names():
    # fk
    old_name_wildcard = 'C_Spine_fk_?_Ctrl'
    for old_name in mc.ls(old_name_wildcard):
        tokens = old_name.split('_')
        side = titlize(tokens[0])
        rootName = titlize(tokens[1])
        functionality = titlize(tokens[2])
        segment = numerize(tokens[3], start_num=0)
        suffix = titlize(tokens[4])
        new_name = '{}_{}_{}_{}_{}'.format(
            side, rootName, functionality, segment, suffix)
        mc.rename(old_name, new_name)

    # ik
    mc.rename('C_Spine_ik_lower_torso_Ctrl', 'C_Spine_Hips_Ctrl')
    mc.rename('C_Spine_ik_upper_torso_Ctrl', 'C_Spine_Chest_Ctrl')
    mc.rename('C_Spine_ik_c_Ctrl', 'C_Spine_Ik_01_Ctrl')

    print('rename_spine_names done')


def rename_spline_jnts():
    old_name_wildcard = 'C_*_spline_bind_*_jnt'
    for old_name in mc.ls(old_name_wildcard):
        tokens = old_name.split('_')
        side = titlize(tokens[0])
        rootName = tokens[1]
        segment = numerize(tokens[4])
        new_name = '{}_{}_{}_Bnd_Jnt'.format(
            side, rootName, segment)
        mc.rename(old_name, new_name)
    print('rename_spline_jnts done')


def rename_LayeredRibbonSplineChain(rootName='Tentacle'):
    # fk controls, eg: c_01_EyeStalk_a_ctrl -> C_01_EyeStalk_Fk_01_Ctrl
    old_name_wildcard = '?_{}_?_Ctrl'.format(rootName)
    for old_name in mc.ls(old_name_wildcard):
        side_, _segment_suffix = old_name.split(rootName)
        side = titlize(side_[0])
        functionality = 'Fk'
        _, segment, suffix = _segment_suffix.split('_')
        segment = numerize(segment)
        suffix = titlize(suffix)
        new_name = '{}_{}_{}_{}_{}'.format(
            side, rootName, functionality, segment, suffix)
        mc.rename(old_name, new_name)

    # ik controls, eg: c_01_EyeStalk_a_a_ctrl -> C_01_EyeStalk_Ik_01_Ctrl
    old_name_wildcard = '?_{}_a_?_Ctrl'.format(rootName)
    for old_name in mc.ls(old_name_wildcard):
        tokens = old_name.split('_')
        side = titlize(tokens[0])
        functionality = 'Ik'
        segment = numerize(tokens[-2])
        suffix = titlize(tokens[-1])
        new_name = '{}_{}_{}_{}_{}'.format(
            side, rootName, functionality, segment, suffix)
        mc.rename(old_name, new_name)

    # SubIk controls, eg: c_01_EyeStalk_b_a_ctrl -> C_01_EyeStalk_SubIk_01_Ctrl
    old_name_wildcard = '?_{}_b_?_Ctrl'.format(rootName)
    for old_name in mc.ls(old_name_wildcard):
        tokens = old_name.split('_')
        side = titlize(tokens[0])
        functionality = 'SubIk'
        segment = numerize(tokens[-2])
        suffix = titlize(tokens[-1])
        new_name = '{}_{}_{}_{}_{}'.format(
            side, rootName, functionality, segment, suffix)
        mc.rename(old_name, new_name)

    # rename joints, eg: C_01_EyeStalk_bind_a_jnt -> C_01_EyeStalk_01_Bnd_Jnt
    old_name_wildcard = '?_{}_bind_*_jnt'.format(rootName)
    for old_name in mc.ls(old_name_wildcard):
        tokens = old_name.split('_')
        side = titlize(tokens[0])
        segment = numerize(tokens[-2])
        new_name = '{}_{}_{}_Bnd_Jnt'.format(
            side, rootName, segment)
        mc.rename(old_name, new_name)

    print('rename_LayeredRibbonSplineChain done')


def rename_gimbal():
    old_name_wildcard = '*_gimbal_*Ctrl'
    for old_name in mc.ls(old_name_wildcard):
        par = mc.listRelatives(old_name, p=True)[0]
        if not par.endswith('Ctrl'):
            continue
        gimbal_new_name = par.replace('Ctrl', 'Gimbal_Ctrl')
        mc.rename(old_name, gimbal_new_name)
    print('rename_gimbal done')


def rename_ctl_parents():
    old_name_wildcard = '*_Ctrl'
    for ctl in mc.ls(old_name_wildcard):
        # rename Cns grp
        grp = mc.listRelatives(ctl, p=True)
        if grp and grp[0].endswith('_c_gp'):
            grp = mc.rename(grp[0], ctl + '_Cns_Grp')

        # rename Drv grp
        grp = mc.listRelatives(grp, p=True)
        if grp and grp[0].endswith('_b_gp'):
            grp = mc.rename(grp[0], ctl + '_Drv_Grp')

        # rename Offset grp
        grp = mc.listRelatives(grp, p=True)
        if grp and grp[0].endswith('_a_gp'):
            grp = mc.rename(grp[0], ctl + '_Offset_Grp')

        # rename Offset grp
        grp = mc.listRelatives(grp, p=True)
        if grp and grp[0].endswith('_spt'):
            mc.rename(grp[0], ctl + '_Follicle_Grp')
    print('rename_ctl_parents done')


def rename_ctls_and_jnts():
    rename_map = {
        # groups
        'character': 'Character',
        'character_control_gp': 'Ctrl_Grp',
        'character_settings_Ctrl': 'Control_Ctrl',
        'character_utilities_gp': 'Utility_Grp',
        'character_deform_gp': 'Jnt_Grp',

        # main
        'C_Main_ground_Ctrl': 'Ground_Ctrl',
        'C_Main_root_Ctrl': 'Root_Ctrl',
        'COG_Ctrl': 'COG_Ctrl',

        # neck
        'C_Neck_fk_b_Ctrl': 'C_Neck_01_Ctrl',
        'C_Neck_fk_c_Ctrl': 'C_Neck_02_Ctrl',
        'C_Neck_fk_head_Ctrl': 'C_Head_Ctrl',

        # head squash
        'C_HeadSquash_fk_b_Ctrl': 'C_HeadSquash_01_Ctrl',
        'C_HeadSquash_fk_c_Ctrl': 'C_HeadSquash_02_Ctrl',
        'C_HeadSquash_fk_head_Ctrl': 'C_HeadSquash_Ctrl'
    }

    for side in 'LR':
        for oldName, newName in rename_map.items():
            oldName = oldName.format(side=side)
            newName = newName.format(side=side)
            if mc.objExists(oldName):
                mc.rename(oldName, newName)


def rename_eyes():
    rename_map = {
        '{side}_eye': '{side}_Eye',
        'C_EyesRoot_aim_Ctrl': 'C_Eye_Root_Ctrl',
        '{side}_eye_aim_handle_Ctrl': '{side}_Eye_Aim_Ctrl',
        '{side}_eye_joints_bind_a_jnt': '{side}_Eye_Bnd_Jnt',
        '{side}_eye_joints_lid_bind_a_jnt': '{side}_EyelidFollow_Bnd_Jnt',
    }
    for side in ['L_01', 'L_02', 'C_01', 'R_01', 'R_02']:
        for oldName, newName in rename_map.items():
            oldName = oldName.format(side=side)
            newName = newName.format(side=side)
            if mc.objExists(oldName):
                mc.rename(oldName, newName)


def rename_attributes():
    attr_name_map = {
        '.ik_switch': 'FKIKSwitch',
        '.gimbal_visibility': 'GimbalVis',
        '.rock': 'Bank',
        '.dilate': 'Dilate',
        '.spaceOrient': 'Follow',
        '.parentSpace': 'Follow'
    }
    for oldName, newName in attr_name_map.items():
        if '.' not in oldName:
            continue
        ctls = mc.ls('*' + oldName)
        for ctl in ctls:
            mc.renameAttr(ctl, newName)


def import_ctl_shapes():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data', 'ctls.ma')
    control.Control.importCtls(path)


def mimic_gimbal_shapes(nodes=None):
    if nodes:
        all_gimbal_vis_attrs = [mc.ls(x + '.gimbal_visibility') for x in nodes]
        all_gimbal_vis_attrs += [mc.ls(x + '.GimbalVis') for x in nodes]
        all_gimbal_vis_attrs = mc.ls(*[x for x in all_gimbal_vis_attrs if x])
    else:
        all_gimbal_vis_attrs = mc.ls('*.gimbal_visibility', '*.GimbalVis')

    for attr in all_gimbal_vis_attrs:
        ctl = attr.split('.')[0]
        if any(x in ctl for x in ['Root', 'Ground']):
            pass
        gimbal = getGimbal(ctl)
        if not gimbal:
            continue
        mimic_shape(target=gimbal, source=ctl, scale_by=0.9)

        oldShape = crvLib.getShapes(ctl, fullPath=True)
        color = display.getColor(oldShape[0])
        newCrvShape = crvLib.getShapes(gimbal, fullPath=True)
        display.setColor(newCrvShape, color)


def mimic_shape(target, source, scale_by=0.9):
    """
    have gimbal controls mimic parent controls.
    Currently affects all gimbal controls in the rig
    """

    crvLib.copyShape(src=source, dst=target)
    target_cvs = mc.ls(target + '.cv[*]', flatten=True)
    mc.scale(scale_by, scale_by, scale_by, target_cvs, componentSpace=True)


def connect_gimbal_vis():
    all_gimbal_vis_attrs = mc.ls('*.gimbal_visibility', '*Ctrl.GimbalVis')

    for attr in all_gimbal_vis_attrs:
        ctl = attr.split('.')[0]
        gimbal = getGimbal(ctl)
        shapes = crvLib.getShapes(gimbal, fullPath=True)
        [attrLib.connectAttr(attr, x + '.v') for x in shapes]


def getGimbal(ctl):
    gimbal = ctl.replace('_Ctrl', '_Gimbal_Ctrl')
    if not mc.objExists(gimbal):
        children = mc.listRelatives(ctl) or []
        for child in children:
            if '_gimbal_' in child:
                gimbal = child
    if mc.objExists(gimbal):
        return gimbal


def setup_vis():
    mainCtl = 'Character'
    rootCtl = 'Root_Ctrl'
    geoGrp = 'Geo_Grp'
    rigGrp = 'Jnt_Grp'
    ctlGrp = 'Ctrl_Grp'
    utilGrp = 'Utility_Grp'

    # delete useless attributes
    mc.deleteAttr('Control_Ctrl', attribute='utility_geometry_vis')
    mc.deleteAttr('Control_Ctrl', attribute='geometry_vis')
    mc.deleteAttr('Control_Ctrl', attribute='bendy_vis')
    mc.deleteAttr('Control_Ctrl', attribute='geometry_display')
    mc.deleteAttr('Control_Ctrl', attribute='EyeGlassOpacity')

    # global scale
    a = attrLib.addFloat(rootCtl, 'ScaleXYZ', dv=1, min=0.001)
    [mc.connectAttr(a, rootCtl + '.s' + x) for x in 'xyz']
    attrLib.lockHideAttrs(rootCtl, attrs=['s'])

    # geo vis
    a = attrLib.addFloat(mainCtl, 'GeoVis', dv=1, min=0, max=1)
    mc.connectAttr(a, geoGrp + '.v')

    # GeoLock
    a = attrLib.addEnum(mainCtl, 'GeoLock', en=['Normal', 'Template', 'Reference'], dv=2)
    mc.setAttr(geoGrp + '.overrideEnabled', True)
    mc.connectAttr(a, geoGrp + '.overrideDisplayType')

    # ctl vis
    a = attrLib.addFloat(mainCtl, 'CtrlVis', dv=1, min=0, max=1)
    mc.connectAttr(a, ctlGrp + '.v')

    # joint vis
    a = attrLib.addFloat(mainCtl, 'JointVis', min=0, max=1)
    mc.connectAttr(a, rigGrp + '.v')

    # utility vis
    a = attrLib.addFloat(mainCtl, 'UtilityVis', min=0, max=1)
    mc.connectAttr(a, utilGrp + '.v')

    #
    nodes = mc.listRelatives('Jnt_Grp', ad=True, type='transform')
    for node in nodes:
        mc.setAttr(node + '.overrideEnabled', 0)


def assign_shaders():
    #
    renderLib.assignShader('body_Geo',
                           color=[0.2227, 0.3929, 0.238],
                           eccentricity=[0.5],
                           diffuse=[1],
                           specularColor=[0.2, 0.2, 0.2],
                           name='body_proxy_mtl')

    #
    renderLib.assignShader(['eyelashes_Geo'],
                           color=[0.1, 0.1, 0.1],
                           name='hair_proxy_mtl')

    #
    renderLib.assignShader(mc.ls('teeth_*_Geo'),
                           color=[0.8, 0.8, 0.8],
                           name='teeth_proxy_mtl')

    #
    renderLib.assignShader(mc.ls('leg_?_00?_Geo'),
                           color=[0.1, 0.1, 0.1],
                           eccentricity=[0.15],
                           specularColor=[0.2, 0.2, 0.2],
                           name='leg_proxy_mtl')

    #
    renderLib.assignShader(mc.ls('gums_*_Geo', 'tongue_Geo'),
                           color=[0.7254, 0.2154, 0.1707],
                           eccentricity=[0.2],
                           specularColor=[0.5, 0.5, 0.5],
                           name='tongue_proxy_mtl')

    #
    # eye_mtl = renderLib.assignShader(mc.ls('eye_?_Geo', 'eye_cornea_?_Geo'),
    #                                  color=[0.8, 0.8, 0.8],
    #                                  diffuse=[1],
    #                                  eccentricity=[0.15],
    #                                  specularColor=[0.5, 0.5, 0.5],
    #                                  name='eye_proxy_mtl')
    #
    # ramp, place2d = renderLib.createEyeRamp(name='eye_mtl')
    #
    # mc.setAttr(ramp + '.colorEntryList[1].position', 0.12)
    # mc.setAttr(ramp + '.colorEntryList[2].position', 0.19)
    # mc.setAttr(ramp + '.colorEntryList[3].position', 0.21)
    # mc.setAttr(ramp + '.colorEntryList[1].color', 0.0948, 0.6987, 0.0952)
    # mc.setAttr(ramp + '.colorEntryList[2].color', 0.0200192, 0.097561, 0.0200192)
    # # mc.setAttr(place2d + '.translateFrameU', - 0.2)
    # # mc.setAttr(place2d + '.translateFrameV', - 0.2)
    #
    # mc.connectAttr(ramp + '.outColor', eye_mtl + '.color')
