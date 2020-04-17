# define maya imports
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import math
import os
import random

import maya_utils
import tex_utils
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO

window = ""
#conButt = ""

EYE_GEOS = ["Eye_Geo", "Eyeball_Geo"]

def do_it():
    # Tots eyes
    # def proxy_eyes_smo(eyes=None, dialog_error=False):
    """
    Create EAV-specific proxy eyes

    :param eyes: (list of iNodes/str, iNode, str) - Eye geos to create proxy setup on
    :param dialog_error: (bool) - Give popup when errors arise to alert user?

    :return: None
    """

    # Make a new window
    #

    if cmds.window('pupEyes', exists=True):
        cmds.deleteUI('pupEyes')

    window = cmds.window("pupEyes", title="TOTS Eye Projections", iconName='pupEyes', widthHeight=(200, 140))

    cmds.columnLayout("pupEyesLayout", adjustableColumn=True)

    cmds.button(label="Build", command=build, height=40)
    cmds.text("Position L_Eye_Proj_Jnt", height=20)
    cmds.button("conButt", label="Connect", command=connect, height=40, enable=False)

    cmds.setParent('..')

    if cmds.objExists("EyeProjections_Grp"):
        cmds.button("conButt", enable=True, parent="pupEyesLayout", edit=True)

    if cmds.objExists("EyeProjections_Grp"):
        if not cmds.getAttr("EyeProjections_Grp.eyesDone"):
            if not cmds.objExists("eyeScale_MD"):
                for side in ['L_', 'R_']:
                    proj = side+'Eye_Projection_3DPlace'
                    cons_grp = cmds.group(em=1, p=side+'Eye_Proj_Jnt', n=proj+'_Cons')
                    cmds.parent(proj, cons_grp)
                    cmds.setAttr(side+'Eye_Aim_Ctrl.r', ch=1, k=1, l=0)
                    cmds.setAttr(side+'Eye_Aim_Ctrl.s', ch=1, k=1, l=0)
                    for at in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
                        cmds.setAttr(side+'Eye_Aim_Ctrl'+at, ch=1, k=1, l=0)
                        cmds.connectAttr(side+'Eye_Aim_Ctrl'+at, cons_grp+at)
                    for bat in ['.rx', '.ry', '.sz']:
                        cmds.setAttr(side+'Eye_Aim_Ctrl'+bat, ch=0, k=0, l=1)
                    if 'R_' in side:
                        md = cmds.createNode('multiplyDivide', n='eyeScale_MD')
                        cmds.setAttr(md+'.input2X', -1)
                        cmds.connectAttr(side+'Eye_Aim_Ctrl.rz', md+'.input1X')
                        cmds.connectAttr(md+'.outputX', cons_grp+'.rz', f=1)
                    my_Export = (cmds.listConnections(proj+'.parentMatrix[0]')[0]).replace('_parentConstraint1', '')
                    cmds.scaleConstraint(proj, my_Export)

                cmds.confirmDialog(message="Eye scale connected.")
            else:
                cmds.confirmDialog(message="Eyes already done.")
                return
        else:
            cmds.showWindow(window)
    elif cmds.objExists("EyeProxys_Grp"):
        if not cmds.objExists("eyeScale_MD"):
            for side in ['L_', 'R_']:
                proj = side+'Eye_Projection_3DPlace'
                cons_grp = cmds.group(em=1, p=side+'Eye_Proxy_Jnt', n=proj+'_Cons')
                cmds.parent(proj, cons_grp)
                cmds.setAttr(side+'Eye_Aim_Ctrl.r', ch=1, k=1, l=0)
                cmds.setAttr(side+'Eye_Aim_Ctrl.s', ch=1, k=1, l=0)
                for at in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
                    cmds.setAttr(side+'Eye_Aim_Ctrl'+at, ch=1, k=1, l=0)
                    cmds.connectAttr(side+'Eye_Aim_Ctrl'+at, cons_grp+at)
                for bat in ['.rx', '.ry', '.sz']:
                    cmds.setAttr(side+'Eye_Aim_Ctrl'+bat, ch=0, k=0, l=1)
                if 'R_' in side:
                    md = cmds.createNode('multiplyDivide', n='eyeScale_MD')
                    cmds.setAttr(md+'.input2X', -1)
                    cmds.connectAttr(side+'Eye_Aim_Ctrl.rz', md+'.input1X')
                    cmds.connectAttr(md+'.outputX', cons_grp+'.rz', f=1)
                my_Export = (cmds.listConnections(proj+'.parentMatrix[0]')[0]).replace('_parentConstraint1', '')
                cmds.scaleConstraint(proj, my_Export)

            cmds.confirmDialog(message="Eye scale connected.")
        print "locking texture attr"
        cmds.setAttr("C_Eye_Root_Ctrl.Texture_Resolution", lock=False)
        cmds.setAttr("C_Eye_Root_Ctrl.Texture_Resolution", 1, lock=True, channelBox=False, keyable=False)

        cmds.confirmDialog(message="Eyes already done.")
        return
    else:
        cmds.showWindow(window)


def build(self):

    # Check for eyes
    eyes = []
    nodes = cmds.ls(long=False, type="transform")
    for n in nodes:
        for eye_name in EYE_GEOS:
            if "R_{}".format(eye_name) in n:
                eyes.append(n)
            if "L_{}".format(eye_name) in n:
                eyes.append(n)

    if len(eyes) > 2:
        cmds.confirmDialog(message="Eye projections already in scene")
        return False
        #i_utils.error("Eye proxys already in scene.", dialog=dialog_error)
    elif len(eyes) < 2:
        cmds.confirmDialog(message="Eye geo not in scene or named incorrectly. Looking for L_Eye_Geo, R_Eye_Geo.")
        return False
        # i_utils.error("Eye geo not in scene or named incorrectly.", dialog=dialog_error)

    if cmds.objExists("EyeProxys_Grp"):
        cmds.confirmDialog(message="Eye projections already in scene.")
        return
    elif cmds.objExists("EyeProjections_Grp"):
        cmds.confirmDialog(message="Eye projections already in scene.")
        return

    # Create eye group787
    eye_grp = i_node.create("group", eyes, n="Eye_Geo_Grp", r=True, use_existing=True)
    if eye_grp.existed:
        i_utils.error("SMO Eye proxy already in scene.", dialog=True)
        return False

    # Get shaders
    export_data = i_node.Node("ExportData")
    export_data_chldn = export_data.relatives(c=True)
    eye_geos = eye_grp.relatives(c=True)
    # - Get iris color to use
    iris_color_dict = {"blue": (0, 0.6, 0.85), "brown": (0.22, 0.1, 0), "green": (0, 0.675, 0), "gold": (0.65, 0.55, 0),
                       "purple": (0.35, 0.15, 0.65), "pink": (1, 0.25, 1)}
    iris_color = None
    for export_chld in export_data_chldn:
        for color in iris_color_dict.keys():
            if color in export_chld.name.lower():
                iris_color = color
                break
    iris_color_value = iris_color_dict.get(iris_color)
    if not iris_color_value:
        RIG_LOG.warn("No iris color found. Supported colors: %s" % sorted(iris_color_dict.keys()))

    # Dilate / Dialate
    dilate_name = "Dilate"
    if os.environ.get("TT_PROJCODE") in ["SMO", "EAV", "KNG"]:
        dilate_name = "Dialate"  # :note: Need to keep typo for consistency

    # Build on each side
    for side in ["L", "R"]:
        # - Add control attr
        aim_control = i_node.Node(side + "_Eye_Aim_Ctrl")
        control_dilate_attr = i_attr.create(aim_control, ln=dilate_name, k=True, at="long", min=0, max=100, dv=50)

        # - Place 2d
        placement_nd = i_node.create("place2dTexture", n=side + "_Eye_Proxy_2DPlace")
        placement_nd.wrapU.set(0)
        placement_nd.wrapV.set(0)

        # - Ramp
        ramp_nd = i_node.create("ramp", n=side + "_Eye_Ramp")
        ramp_nd.type.set(4)
        ramp_nd.interpolation.set(0)
        ramp_nd.attr("colorEntryList[1].position").set(0.305)

        # -- Color
        if iris_color_value:
            ramp_nd.attr("colorEntryList[1].color").set(iris_color_value)
        ramp_nd.attr("colorEntryList[2].position").set(0.647)
        ramp_nd.attr("colorEntryList[2].color").set([1, 1, 1])
        ramp_nd.attr("colorEntryList[3].position").set(0)
        ramp_nd.attr("colorEntryList[3].color").set([0, 0, 0])
        ramp_nd.defaultColor.set([1, 1, 1])

        # -- Add attrs
        ramp_ren_attr = i_attr.create_vis_attr(ramp_nd, ln="Render", as_enum=True, dv=0)
        ramp_dilate_attr = i_attr.create(ramp_nd, ln=dilate_name, k=True, at="long", min=0, max=100, dv=50)
        ramp_res_attr = i_attr.create(ramp_nd, ln="Texture_Resolution", k=False, cb=True, at="enum", en="Proxy:Texture")

        # - Remap
        remap_nd = i_node.create("remapValue", n=side + "_" + dilate_name + "_Ramp_Rmap")
        remap_nd.inputMax.set(100)
        remap_nd.outputMin.set(0.05)
        remap_nd.outputMax.set(0.56)

        # - UnitCon
        uttc_nd = i_node.create("unitToTimeConversion", n=side + "_EyeRamp_UC")
        uttc_nd.conversionFactor.set(250)

        # - Projection
        projection_nd = i_node.create("projection", n=side + "_Eye_Projection")

        # - Place 3d
        cube_prj_nd = i_node.create("place3dTexture", n=side + "_Eye_Projection_3DPlace")

        # - Anim Curves
        ramp_ac = i_node.create("animCurveTU", n=side + "_Eye_Ramp_Input_AnimCurve")
        ramp_ac.useCurveColor.set(1)
        ramp_ac.curveColor.set([1, 1, 0])
        proj_ac = i_node.create("animCurveTU", n=side + "_Eye_Projection_Resolution")
        proj_ac.useCurveColor.set(1)
        proj_ac.curveColor.set([0, 0, 0])

        side_shdr = tex_utils.create_shader(shader_name=side + "_Eye_Shdr", shader_type="lambert", use_existing=True)
        side_shdr = i_node.Node(side_shdr)

        # - Key
        file_export_data = i_utils.ls(side + "_*_DIFF_CLR_file_ExportData")
        if not file_export_data:
            i_utils.error("Nothing found with name '%s_*_DIFF_CLR_file_ExportData'" % side, dialog=True)
            # return
        file_export_data = file_export_data[0]
        frame_offset = file_export_data.frameOffset.get()
        for tv in [[0, 0], [50, frame_offset], [100, 100]]:
            ramp_ac.set_key(t=tv[0], v=tv[1], itt="linear", ott="linear")
        proj_ac.set_key(t=0, v=32, itt="auto", ott="step")
        proj_ac.set_key(t=1, v=64, itt="auto", ott="step")
        ramp_ac.key_tangent(e=True, wt=False)
        proj_ac.key_tangent(e=True, wt=False)

        # - Connect
        placement_nd.outUV.drive(ramp_nd.uvCoord)
        placement_nd.outUvFilterSize.drive(ramp_nd.uvFilterSize)
        remap_nd.outValue.drive(ramp_nd.attr("colorEntryList[1].position"))

        try:
            ramp_dilate_attr.drive(uttc_nd.input)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            ramp_nd.outColor.drive(projection_nd.image)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            cube_prj_nd.worldInverseMatrix[0].drive(projection_nd.placementMatrix)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            uttc_nd.output.drive(ramp_ac.input)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            ramp_ac.output.drive(remap_nd.inputValue)
            # attribute already connected
        except RuntimeError:
            pass

        try:
            ramp_res_attr.drive(proj_ac.input)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            projection_nd.outColor.drive(side_shdr.color)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            control_dilate_attr.drive(ramp_dilate_attr)
        except RuntimeError:
            # attribute already connected
            pass

        try:
            ramp_ac.output.drive(file_export_data.frameOffset)
        except RuntimeError:
            # attribute already connected
            pass

        # - Drive Place nodes
        diff_placement_nds = i_utils.ls(side + "_*_DIFF_CLR_place3dTexture_ExportData")
        if diff_placement_nds:
            diff_place_nd = diff_placement_nds[0]
            for trs in ["t", "r", "s"]:
                for axis in ["x", "y", "z"]:
                    cube_prj_nd.attr(trs + axis).set(diff_place_nd.attr(trs + axis).get())
            i_constraint.constrain(cube_prj_nd, diff_place_nd, mo=True, as_fn="parent")

        # - Assign shaders
        side_geos = []
        for e in eyes:
            for eye_name in EYE_GEOS:
                if side + "_{}".format(eye_name) in e:
                    side_geos.append(e)

            #   confirm eye skinning
            cmds.skinCluster(e, edit=True, unbind=True)
            cmds.skinCluster('C_Head_Base_Bnd_Jnt', e, toSelectedBones=True)

        tex_utils.apply_shader(shader_name=side_shdr.name, geo=side_geos)

    # Clear selection
    i_utils.select(cl=True)

    # Create projection utils
    projGrp = cmds.createNode('transform', name="EyeProjections_Grp", parent="Utility_Grp")
    cmds.addAttr(projGrp, shortName="eyesDone", attributeType="bool")
    cmds.setAttr(projGrp+".eyesDone", False)
    projPivotsGrp = cmds.createNode('transform', name="EyeProjectionsPivot_Grp", parent=projGrp)
    lPivot = cmds.joint(name="L_Eye_Proj_Jnt")
    rPivot = cmds.joint(name="R_Eye_Proj_Jnt")
    cmds.parent(rPivot, projPivotsGrp)
    cmds.parentConstraint("C_Head_Base_Bnd_Jnt", "EyeProjectionsPivot_Grp", maintainOffset=True)
    cmds.scaleConstraint("C_Head_Base_Bnd_Jnt", "EyeProjectionsPivot_Grp", maintainOffset=True)

    lPlane = cmds.nurbsPlane( name="L_Eye_Proj_Fol_Geo", degree=1, patchesU=1, patchesV=1, axis=(1, 0, 0) )[0]
    lPlaneMesh = cmds.listRelatives(lPlane, children=True, type='nurbsSurface')[0]
    #cmds.polyPlane(name="L_Eye_Proj_Fol_Geo", axis=(0, 0, 1), constructionHistory=True, width=1, height=1, subdivisionsX=1, subdivisionsY=1, createUVs=2)[0]
    tempCon = cmds.parentConstraint("L_Eye_Bnd_Jnt", lPlane, maintainOffset=False)
    cmds.delete(tempCon)
    cmds.setAttr(lPlane+'.rotateZ', 90)
    cmds.setAttr(lPlane+'.rotateY', -90)
    cmds.parent(lPlane, projGrp)

    rPlane = cmds.nurbsPlane( name="R_Eye_Proj_Fol_Geo", degree=1, patchesU=1, patchesV=1, axis=(0, 1, 0) )[0]
    rPlaneMesh = cmds.listRelatives(rPlane, c=True, type='nurbsSurface')[0]
    #cmds.polyPlane(name="R_Eye_Proj_Fol_Geo", axis=(0, 0, 1), constructionHistory=True, width=1, height=1, subdivisionsX=1, subdivisionsY=1, createUVs=2)[0]
    tempCon = cmds.parentConstraint("R_Eye_Bnd_Jnt", rPlane, maintainOffset=False)
    cmds.delete(tempCon)
    cmds.setAttr(rPlane+'.rotateZ', 90)
    cmds.parent(rPlane, projGrp)

    lFol = create_follicle("L_Eye_Proj_Fol", lPlaneMesh, parent=projGrp)[0]
    cmds.setAttr(lFol+".parameterU", .5)
    cmds.setAttr(lFol+".parameterV", .5)
    rFol = create_follicle("R_Eye_Proj_Fol", rPlaneMesh, parent=projGrp)[0]
    cmds.setAttr(rFol+".parameterU", .5)
    cmds.setAttr(rFol+".parameterV", .5)



    rev = cmds.shadingNode("multiplyDivide", asUtility=True, name="pupEyesProj_Pos_RevX_Mult")
    cmds.setAttr(rev+".input2X", -1)
    cmds.connectAttr(lPivot+".translateX", rev+".input1X")
    cmds.connectAttr(lPivot+".translateY", rev+".input1Y")
    cmds.connectAttr(lPivot+".translateZ", rev+".input1Z")
    cmds.connectAttr(rev+".outputX", rPivot+".translateX")
    cmds.connectAttr(rev+".outputY", rPivot+".translateY")
    cmds.connectAttr(rev+".outputZ", rPivot+".translateZ")


    tempCon = cmds.pointConstraint("L_Eye_Bnd_Jnt", "L_Eye_Proj_Jnt", maintainOffset=False)
    cmds.delete(tempCon)

    cmds.select(lPivot)
    cmds.confirmDialog(message="Place L_Eye_Proj_Jnt in a logical position behind the eye then press Connect.")

    cmds.button("conButt", enable=True, parent="pupEyesLayout", edit=True)


def connect(self):
    # pup projection eyes bind

    if cmds.objExists("pupEyesProj_Pos_RevX_Mult"):
        jnt_matrix = cmds.xform("R_Eye_Proj_Jnt", q=True, ws=True, m=True)
        cmds.delete("pupEyesProj_Pos_RevX_Mult")
        cmds.xform("R_Eye_Proj_Jnt", ws=True, m=jnt_matrix)

    if cmds.objExists("EyeProjections_Grp"):
        for side in ['L_', 'R_']:

            fol = side + "Eye_Proj_Fol_flc"
            pivot = side + "Eye_Proj_Jnt"
            proj = side+'Eye_Projection_3DPlace'
            ctrl = side+'Eye_Aim_Ctrl'

            cmds.pointConstraint(fol, pivot, maintainOffset=True)
            cmds.orientConstraint(fol, pivot, maintainOffset=True)

            cmds.skinCluster(side+'Eye_Bnd_Jnt', side + "Eye_Proj_Fol_Geo", toSelectedBones=True)

            zero_grp = cmds.group(em=1, p=pivot, n=proj+'_Zero')
            temp = cmds.orientConstraint(proj, zero_grp, mo=False)
            cmds.delete(temp)
            cons_grp = cmds.group(em=1, p=zero_grp, n=proj+'_Cons')
            cmds.parent(proj, cons_grp)
            cmds.setAttr(ctrl+'.r', ch=1, k=1, l=0)
            cmds.setAttr(ctrl+'.s', ch=1, k=1, l=0)
            for at in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
                cmds.setAttr(ctrl+at, ch=1, k=1, l=0)
                cmds.connectAttr(ctrl+at, cons_grp+at)
            for bat in ['.rx', '.ry', '.sz']:
                cmds.setAttr(ctrl+bat, ch=0, k=0, l=1)
            if 'R_' in side:
                md = cmds.createNode('multiplyDivide', n='eyeScale_MD')
                cmds.setAttr(md+'.input2X', -1)
                cmds.connectAttr(ctrl+'.rz', md+'.input1X')
                cmds.connectAttr(md+'.outputX', cons_grp+'.rz', f=1)
            my_Export = (cmds.listConnections(proj+'.parentMatrix[0]')[0]).replace('_parentConstraint1', '')
            cmds.scaleConstraint(proj, my_Export)


        cmds.setAttr("EyeProjections_Grp.eyesDone", True)
        cmds.select("C_Eye_Root_Ctrl")
    else:
        cmds.confirmDialog(message="Eyes not built yet.")


def create_follicle(name, surface, parent=None):

    """
    :param name: string to use for node naming
    :param surface: string name of nurbsSurface or Mesh shape
    :param parent: string name of parent transform, or None
    :return: string name of follicle and follicle shape (tuple)
    """

    # Argument checks

    surface_type = cmds.nodeType(surface)
    if surface_type not in ['mesh', 'nurbsSurface']:
        raise Exception('%s is not a valid type for follicle surface' % surface_type)
    if not isinstance(name, basestring):
        raise Exception('%s is not a valid type for name argument. Try a string instead.' % type(name))
    if not isinstance(parent, basestring) and parent is not None:
        raise Exception('%s is not a valid type for parent argument. Try a string instead.' % type(name))

    # Nodes
    follicle = cmds.createNode(
        'transform',
        name='%s_flc' % name,
        parent=parent
    )
    follicle_shape = cmds.createNode(
        'follicle', name='%s_flcShape' % name,
        parent=follicle
    )

    # Attributes
    cmds.connectAttr(
        '%s.outRotate' % follicle_shape,
        '%s.rotate' % follicle
    )
    cmds.connectAttr(
        '%s.outTranslate' % follicle_shape,
        '%s.translate' % follicle
    )
    if surface_type == 'mesh':
        cmds.connectAttr(
            '%s.outMesh' % surface,
            '%s.inputMesh' % follicle_shape
        )
    if surface_type == 'nurbsSurface':
        cmds.connectAttr(
            '%s.local' % surface,
            '%s.inputSurface' % follicle_shape
        )
    cmds.connectAttr(
        '%s.worldMatrix[0]' % surface,
        '%s.inputWorldMatrix' % follicle_shape
    )

    return follicle, follicle_shape