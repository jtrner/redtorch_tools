#Squash Joystick Head

#select vertices of Head to start
import maya.cmds as cmds
import icon_api.node as i_node
import icon_api.attr as i_attr
import maya.mel as mel
from math import pow,sqrt
import deform_utils
reload(deform_utils)


# make a function to make icon controls
def make_icon_controls(control_list, control_pos, ctrl_colour, ctrl_shape):
    for ctrl in control_list:
        i_control = i_node.create("control", name=ctrl, control_type=ctrl_shape, with_gimbal=False, color=ctrl_colour, size=5)
        ctrl_dag = i_control.control
        ctrl_offset_group = ctrl+'_Ctrl_Offset_Grp'
        cmds.xform(ctrl_offset_group, ws=True, t=control_pos)



def make_centerSquash():
    if cmds.objExists('pCube1'):
        #create lattice
        cmds.lattice("pCube1", name='HeadSquash_FFD', divisions=(2, 6, 2), objectCentered=True, ldivisions=(8, 8, 8), outsideLattice=1)

        lat = "HeadSquash_FFDLattice"
        ffd = "HeadSquash_FFD"
        base = "HeadSquash_FFDBase"
        set = "HeadSquash_FFDSet"

        #create cluster
        cmds.select(lat+".pt[0:1][2:3][0:1]")
        clus = cmds.cluster(name='HeadSquash_Center_Cls')
        clusHand = clus[1]

        cmds.select([lat+".pt[0:1][0:1][0:1]", lat+".pt[0:1][4:5][0:1]"])
        baseClus = cmds.cluster(name='HeadSquash_Base_Cls')
        baseClusHand = baseClus[1]

        pos = cmds.xform(clusHand, worldSpace=True, scalePivot=True, query=True)

        #create control
        ctrl = 'HeadSquash_Center'
        make_icon_controls([ctrl], pos, 'purple', '2D circle')
        ctrl = 'HeadSquash_Center_Ctrl'

        #scale control shape
        bounds = cmds.xform("pCube1", boundingBox=True, query=True)
        size = bounds[5]/10
        cmds.select(ctrl+".cv[0:7]")
        cmds.scale(size, scaleX=True, absolute=False)
        cmds.scale(size, scaleZ=True, absolute=False)

        #drive the cluster
        cmds.parentConstraint(ctrl, clusHand, maintainOffset=True)
        cmds.scaleConstraint(ctrl, clusHand, maintainOffset=True)

        #organize
        utils = "Squash_Deformers_Grp"
        if not cmds.objExists(utils):
            utils = cmds.group([clusHand, baseClusHand, lat, base], n="Squash_Deformers_Grp")
            cmds.parent(utils, "Utility_Grp")

        cmds.parent(ctrl+'_Offset_Grp', 'C_Head_Gimbal_Ctrl')
        cmds.parentConstraint('C_Head_Gimbal_Ctrl', base, maintainOffset=True)
        cmds.scaleConstraint('C_Head_Gimbal_Ctrl', base, maintainOffset=True)
        cmds.parentConstraint('C_Head_Gimbal_Ctrl', baseClusHand, maintainOffset=True)
        cmds.scaleConstraint('C_Head_Gimbal_Ctrl', baseClusHand, maintainOffset=True)

        #add geo to lattice
        geo = []
        maybeGeo = ["*:Body_Geo",
                    "L_Eye_Proxy_Fol_Geo",
                    "R_Eye_Proxy_Fol_Geo",
                    "L_Eye_Proj_Fol_Geo",
                    "R_Eye_Proj_Fol_Geo",
                    "*:L_Eye_Geo",
                    "*:R_Eye_Geo",
                    "*:EyeLash_Geo",
                    "*:EyeBrow_Geo",
                    "*:Tongue_Geo",
                    '*:Eyebrows_Geo',
                    '*:EyeBrows_Geo',
                    '*:Eyebrow_Geo',
                    '*:L_Eyebrow_Geo',
                    '*:R_Eyebrow_Geo',
                    '*:Eyebrows_L_Geo',
                    '*:Eyebrows_R_Geo',
                    '*:Eyelashes_Geo',
                    '*:Lower_Teeth_Geo',
                    '*:Upper_Teeth_Geo',
                    'Hat_Fol_Geo']

        for m in maybeGeo:
            if cmds.objExists(m):
                geo.append(m)

        cmds.lattice(ffd, edit=True, geometry=geo)

        # organize
        grp = 'Head_Squash_FFD_Grp'

        if not cmds.objExists(grp):
            grp = cmds.group([lat, ffd, base, clusHand, baseClusHand], n=grp)

        utils = "Squash_Deformers_Grp"
        if not cmds.objExists(utils):
            utils = cmds.group(grp, n="Squash_Deformers_Grp")
            cmds.parent(utils, "Utility_Grp")

        if cmds.listRelatives(grp, parent=True):
            if not cmds.listRelatives(grp, parent=True)[0] == utils:
                cmds.parent(grp, utils)
        else:
            cmds.parent(grp, utils)

        #clean scene
        cmds.delete("pCube1")
        cmds.select(ctrl)


def make_headSquash():
    selected = cmds.ls(sl=True, flatten=True)

    pivot = cmds.exactWorldBoundingBox(selected)
    top_pos = ((pivot[0]+pivot[3]) / 2, pivot[4], (pivot[2]+pivot[5]) / 2)
    bot_pos = ((pivot[0]+pivot[3]) / 2, pivot[1], (pivot[2]+pivot[5]) / 2)

    non_linear_def = (('Head_Squash', 'squash'), ('Head_Flare', 'flare'), ('Head_Twist', 'twist'), ('Head_BendX', 'bend'), ('Head_BendZ', 'bend'))

    deformer_list = []
    deformer_handle_list = []

    for lin in non_linear_def:
        # make and rename the non linears
        deformer_name = lin[0]
        deformer_type = lin[1]

        linear_parts = cmds.nonLinear(selected, name=deformer_name, type=deformer_type)
        lin_set = cmds.rename(linear_parts[0]+'Set', deformer_name+'Set')
        lin_def = cmds.rename(linear_parts[0], deformer_name)
        lin_handle = cmds.rename(linear_parts[1], deformer_name+"_Handle")

        deformer_list.append(lin_def)
        deformer_handle_list.append(lin_handle)

        # move and set attributes for the non-linears
        cmds.xform(lin_handle, ws=True, t=bot_pos)
        cmds.setAttr(lin_def+".lowBound", 0)
        cmds.setAttr(lin_def+".highBound", 2)

    squash_lin_ctrl_names = ["Head_Squash"]
    ctrl_colour = "aqua"
    ctrl_shape = "3d Sphere"
    make_icon_controls(squash_lin_ctrl_names, top_pos, ctrl_colour, ctrl_shape)

    # connect bits
    Head_squash = deformer_list[0]
    Head_flare = deformer_list[1]
    Head_twist = deformer_list[2]
    Head_bend_x = deformer_list[3]
    Head_bend_z = deformer_list[4]

    # rotate bendz handle
    cmds.setAttr(deformer_handle_list[4]+".rotateY", -90)

    squash_md = cmds.createNode('multiplyDivide', n="Head_Squash_MD")
    twist_md = cmds.createNode('multiplyDivide', n="Head_Twist_MD")
    bend_md = cmds.createNode('multiplyDivide', n="Head_Bend_MD")

    # Head controller name:
    Head_squash_control = 'Head_Squash_Ctrl'

    # connect MD nodes
    cmds.connectAttr(Head_squash_control+".translateY", squash_md+".input1Y")
    cmds.connectAttr(squash_md+".outputY", Head_squash+".factor")
    cmds.setAttr(squash_md+".input2Y", 0.025)

    cmds.connectAttr(Head_squash_control+".rotateY", twist_md+".input1Y")
    cmds.connectAttr(twist_md+".outputY", Head_twist+".endAngle")
    cmds.setAttr(twist_md+".input2Y", -1)

    cmds.connectAttr(Head_squash_control+".translateX", bend_md+".input1X")
    cmds.connectAttr(bend_md+".outputX", Head_bend_x+".curvature")
    cmds.connectAttr(Head_squash_control+".translateZ", bend_md+".input1Z")
    cmds.connectAttr(bend_md+".outputZ", Head_bend_z+".curvature")

    cmds.connectAttr(Head_squash_control+".scaleX", Head_flare+".endFlareX")
    cmds.connectAttr(Head_squash_control+".scaleZ", Head_flare+".endFlareZ")

    # organize
    grp = 'Head_Squash_Deformers_Grp'
    if not cmds.objExists(grp):
        cmds.group(deformer_handle_list, n=grp)

    utils = "Squash_Deformers_Grp"
    if not cmds.objExists(utils):
        utils = cmds.group(grp, n="Squash_Deformers_Grp")
        cmds.parent(utils, "Utility_Grp")

    if cmds.listRelatives(grp, parent=True):
        if not cmds.listRelatives(grp, parent=True)[0]==utils:
            cmds.parent(grp, utils)
    cmds.parentConstraint('C_Head_Gimbal_Ctrl', grp, maintainOffset=True)
    cmds.scaleConstraint('C_Head_Gimbal_Ctrl', grp, maintainOffset=True)
    cmds.parent(Head_squash_control+'_Offset_Grp', 'C_Head_Gimbal_Ctrl')

    geo = []
    maybeGeo = ["L_Eye_Proxy_Fol_Geo", "R_Eye_Proxy_Fol_Geo", "L_Eye_Proj_Fol_Geo", "R_Eye_Proj_Fol_Geo", 'Hat_Fol_Geo']

    for m in maybeGeo:
        if cmds.objExists(m):
            geo.append(m)

    cmds.deformer(Head_squash, edit=True, geometry=geo)
    cmds.deformer(Head_flare, edit=True, geometry=geo)
    cmds.deformer(Head_twist, edit=True, geometry=geo)
    cmds.deformer(Head_bend_x, edit=True, geometry=geo)
    #cmds.deformer(Head_bend_z, edit=True, geometry=geo)

    cmds.select(Head_squash_control)



def make_jawSquash():
    selected = cmds.ls(sl=True, flatten=True)

    pivot = cmds.exactWorldBoundingBox(selected)
    top_pos = ((pivot[0]+pivot[3]) / 2, pivot[4], (pivot[2]+pivot[5]) / 2)
    bot_pos = ((pivot[0]+pivot[3]) / 2, pivot[1], (pivot[2]+pivot[5]) / 2)

    non_linear_def = (('Jaw_Squash', 'squash'), ('Jaw_Flare', 'flare'), ('Jaw_Twist', 'twist'), ('Jaw_BendX', 'bend'), ('Jaw_BendZ', 'bend'))

    deformer_list = []
    deformer_handle_list = []

    for lin in non_linear_def:
        # make and rename the non linears
        deformer_name = lin[0]
        deformer_type = lin[1]

        linear_parts = cmds.nonLinear(selected, name=deformer_name, type=deformer_type)
        lin_set = cmds.rename(linear_parts[0]+'Set', deformer_name+'Set')
        lin_def = cmds.rename(linear_parts[0], deformer_name)
        lin_handle = cmds.rename(linear_parts[1], deformer_name+"_Handle")

        deformer_list.append(lin_def)
        deformer_handle_list.append(lin_handle)

        # move and set attributes for the non-linears
        cmds.xform(lin_handle, ws=True, t=top_pos)
        cmds.setAttr(lin_def+".lowBound", 0)
        cmds.setAttr(lin_def+".highBound", 2)

    squash_lin_ctrl_names = ["Jaw_Squash"]
    ctrl_colour = "watermelon"
    ctrl_shape = "3d Sphere"
    Jaw_control = make_icon_controls(squash_lin_ctrl_names, bot_pos, ctrl_colour, ctrl_shape)

    # connect bits
    Jaw_squash = deformer_list[0]
    Jaw_flare = deformer_list[1]
    Jaw_twist = deformer_list[2]
    Jaw_bend_x = deformer_list[3]
    Jaw_bend_z = deformer_list[4]

    # rotate bendz handle
    cmds.setAttr(deformer_handle_list[4]+".rotateY", -90)

    squash_md = cmds.createNode('multiplyDivide', n="Jaw_Squash_MD")
    twist_md = cmds.createNode('multiplyDivide', n="Jaw_Twist_MD")
    bend_md = cmds.createNode('multiplyDivide', n="Jaw_Bend_MD")

    # Jaw controller name:
    Jaw_squash_control = 'Jaw_Squash_Ctrl'

    # connect MD nodes
    cmds.connectAttr(Jaw_squash_control+".translateY", squash_md+".input1Y")
    cmds.connectAttr(squash_md+".outputY", Jaw_squash+".factor")
    cmds.setAttr(squash_md+".input2Y", 0.025)

    cmds.connectAttr(Jaw_squash_control+".rotateY", twist_md+".input1Y")
    cmds.connectAttr(twist_md+".outputY", Jaw_twist+".endAngle")
    cmds.setAttr(twist_md+".input2Y", -1)

    cmds.connectAttr(Jaw_squash_control+".translateX", bend_md+".input1X")
    cmds.connectAttr(bend_md+".outputX", Jaw_bend_x+".curvature")
    cmds.connectAttr(Jaw_squash_control+".translateZ", bend_md+".input1Z")
    cmds.connectAttr(bend_md+".outputZ", Jaw_bend_z+".curvature")

    cmds.connectAttr(Jaw_squash_control+".scaleX", Jaw_flare+".endFlareX")
    cmds.connectAttr(Jaw_squash_control+".scaleZ", Jaw_flare+".endFlareZ")

    # organize
    grp = 'Jaw_Squash_Deformers_Grp'
    if not cmds.objExists(grp):
        cmds.group(deformer_handle_list, n=grp)

    utils = "Squash_Deformers_Grp"
    if not cmds.objExists(utils):
        utils = cmds.group(grp, n="Squash_Deformers_Grp")
        cmds.parent(utils, "Utility_Grp")

    if cmds.listRelatives(grp, parent=True):
        if not cmds.listRelatives(grp, parent=True)[0]==utils:
            cmds.parent(grp, utils)
    else:
        cmds.parent(grp, utils)

    # re-orient for jaw
    cmds.setAttr(Jaw_squash+'_Handle.rotateX', -180)
    cmds.setAttr(Jaw_flare+'_Handle.rotateX', -180)
    cmds.setAttr(Jaw_twist+'_Handle.rotateX', -180)
    cmds.setAttr(Jaw_bend_x+'_Handle.rotateX', -180)
    cmds.setAttr(Jaw_bend_z+'_Handle.rotateX', -180)
    cmds.setAttr(Jaw_bend_z+'_Handle.rotateY', 90)
    cmds.parentConstraint('C_Head_Gimbal_Ctrl', grp, maintainOffset=True)
    cmds.scaleConstraint('C_Head_Gimbal_Ctrl', grp, maintainOffset=True)
    cmds.parent(Jaw_squash_control+'_Offset_Grp', 'C_Head_Gimbal_Ctrl')
    cmds.setAttr(Jaw_squash_control+'_Offset_Grp.rotateX', -180)

    cmds.select(Jaw_squash_control)


# copy deformer weights from one deformer to another within the same geo
def copy_Def_Weights(geo, src_def_name, targ_def_name):
    geo_vtx_list = cmds.ls(geo+'.vtx[*]', flatten=True)
    vtx_weights = {}
    vtx_list = []

    set = deform_utils.util_find_deformer_set(deformer=src_def_name)
    print geo
    print targ_def_name

    for v in geo_vtx_list:
        if cmds.sets(v, isMember=set):
            vtx_list.append(v)

    for vtx in vtx_list:

        val = cmds.percent(src_def_name, vtx, value=True, query=True)[0]
        #if val > 0:
        cmds.percent(targ_def_name, vtx, value=val)


def copy_deformerWeights():
    defs = ['_Flare', '_Twist', '_BendX', '_BendZ']
    type = ['Head', 'Jaw']
    selected = cmds.ls(sl=True, flatten=True)
    for s in selected:
        for t in type:
            if cmds.objExists(t+'_Squash'):
                for d in defs:
                    # geo = '*:Body_Geo'
                    # print t+'_Squash'
                    copy_Def_Weights(s, t+'_Squash', t+d)

