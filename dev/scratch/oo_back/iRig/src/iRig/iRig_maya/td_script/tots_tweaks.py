import pymel.core as pm
import maya.cmds as cmds
import icon_api.node as i_node
import icon_api.attr as i_attr
import skin_tools
import sys
pth = 'G:/Pipeline/pipeline_beta/maya/scripts/rig_tools/utils'
if pth not in sys.path:
   sys.path.append(pth)
import deformers

def createShirtJoints():
    grp = cmds.createNode('transform', name='Tweak_Jnts_Grp')

    cmds.joint(grp, name='C_Shirt_Tweak_Base_Jnt')
    hem = cmds.joint(grp, name='C_Shirt_Hem_Tweaks_Grp', position=(0, 40, 0))
    collar = cmds.joint(grp, name='C_Shirt_Collar_Tweaks_Grp', position=(0, 80, 0))

    cmds.joint(hem, name='C_Shirt_Hem_Tweak_01_Jnt', position=(0, 0, 10), orientation=(0, 0, 0), relative=True)
    cmds.joint(hem, name='C_Shirt_Hem_Tweak_02_Jnt', position=(0, 0, -10), orientation=(0, 180, 0), relative=True)
    cmds.joint(hem, name='L_Shirt_Hem_Tweak_01_Jnt', position=(7, 0, 7), orientation=(0, 45, 0), relative=True)
    cmds.joint(hem, name='L_Shirt_Hem_Tweak_02_Jnt', position=(10, 0, 0), orientation=(0, 90, 0), relative=True)
    cmds.joint(hem, name='L_Shirt_Hem_Tweak_03_Jnt', position=(7, 0, -7), orientation=(0, 135, 0), relative=True)
    cmds.joint(hem, name='R_Shirt_Hem_Tweak_01_Jnt')
    cmds.joint(hem, name='R_Shirt_Hem_Tweak_02_Jnt')
    cmds.joint(hem, name='R_Shirt_Hem_Tweak_03_Jnt')

    cmds.joint(collar, name='C_Shirt_Collar_Tweak_01_Jnt', position=(0, 0, 10), orientation=(0, 0, 0), relative=True)
    cmds.joint(collar, name='C_Shirt_Collar_Tweak_02_Jnt', position=(0, 0, -10), orientation=(0, 180, 0), relative=True)
    cmds.joint(collar, name='L_Shirt_Collar_Tweak_01_Jnt', position=(7, 0, 7), orientation=(0, 45, 0), relative=True)
    cmds.joint(collar, name='L_Shirt_Collar_Tweak_02_Jnt', position=(10, 0, 0), orientation=(0, 90, 0), relative=True)
    cmds.joint(collar, name='L_Shirt_Collar_Tweak_03_Jnt', position=(7, 0, -7), orientation=(0, 135, 0), relative=True)
    cmds.joint(collar, name='R_Shirt_Collar_Tweak_01_Jnt')
    cmds.joint(collar, name='R_Shirt_Collar_Tweak_02_Jnt')
    cmds.joint(collar, name='R_Shirt_Collar_Tweak_03_Jnt')

    for side in 'LR':
        sleeve = cmds.joint(grp, name=side+'_Shirt_Sleeve_Tweaks_Grp', position=(20, 60, 0), orientation=(0, 0, 0))

        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_01_Jnt', position=(0, 10, 0), orientation=(0, -90, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_02_Jnt', position=(0, 7.5, 5), orientation=(0, -45, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_03_Jnt', position=(0, 0, 5), orientation=(0, 0, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_04_Jnt', position=(0, -7.5, 5), orientation=(0, 45, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_05_Jnt', position=(0, -10, 0), orientation=(0, 90, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_06_Jnt', position=(0, -7.5, -5), orientation=(0, 135, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_07_Jnt', position=(0, 0, -5), orientation=(0, 180, -90), relative=True)
        cmds.joint(sleeve, name=side+'_Shirt_Sleeve_Tweak_08_Jnt', position=(0, 7.5, -5), orientation=(0, -135, -90), relative=True)

    jnts = ['L_Shirt_Hem_Tweak_01_Jnt', 'L_Shirt_Hem_Tweak_02_Jnt', 'L_Shirt_Hem_Tweak_03_Jnt', 'L_Shirt_Sleeve_Tweaks_Grp', 'L_Shirt_Collar_Tweak_01_Jnt', 'L_Shirt_Collar_Tweak_02_Jnt', 'L_Shirt_Collar_Tweak_03_Jnt',
            'L_Shirt_Sleeve_Tweak_01_Jnt', 'L_Shirt_Sleeve_Tweak_02_Jnt', 'L_Shirt_Sleeve_Tweak_03_Jnt', 'L_Shirt_Sleeve_Tweak_04_Jnt', 'L_Shirt_Sleeve_Tweak_05_Jnt', 'L_Shirt_Sleeve_Tweak_06_Jnt', 'L_Shirt_Sleeve_Tweak_07_Jnt',
            'L_Shirt_Sleeve_Tweak_08_Jnt']

    for j in jnts:
        if not 'Grp' in j:
            lJnt = j
            rJnt = lJnt.replace('L_', 'R_')
            rot = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '').replace('Jnt', 'Rot_Mult'))
            trans = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '').replace('Jnt', 'Trans_Mult'))
            cmds.setAttr(trans+'.input2X', -1)
            cmds.setAttr(rot+'.input2Y', -1)
            cmds.setAttr(rot+'.input2Z', -1)
            cmds.connectAttr(lJnt+'.rotate', rot+'.input1')
            cmds.connectAttr(rot+'.output', rJnt+'.rotate')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.output', rJnt+'.translate')
        else:
            lJnt = j
            rJnt = lJnt.replace('L_', 'R_')
            rot = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Rot_Mult')
            trans = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Trans_Mult')
            cmds.setAttr(trans+'.input2X', -1)
            cmds.setAttr(rot+'.input2Y', -1)
            cmds.setAttr(rot+'.input2Z', -1)
            cmds.connectAttr(lJnt+'.rotate', rot+'.input1')
            cmds.connectAttr(rot+'.output', rJnt+'.rotate')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.output', rJnt+'.translate')


    jnts = [u'C_Shirt_Hem_Tweak_01_Jnt', u'C_Shirt_Hem_Tweak_02_Jnt', u'L_Shirt_Hem_Tweak_01_Jnt', u'L_Shirt_Hem_Tweak_02_Jnt', u'L_Shirt_Hem_Tweak_03_Jnt', u'C_Shirt_Collar_Tweak_01_Jnt', u'C_Shirt_Collar_Tweak_02_Jnt',
            u'L_Shirt_Collar_Tweak_01_Jnt', u'L_Shirt_Collar_Tweak_02_Jnt', u'L_Shirt_Collar_Tweak_03_Jnt', u'L_Shirt_Sleeve_Tweak_01_Jnt', u'L_Shirt_Sleeve_Tweak_02_Jnt', u'L_Shirt_Sleeve_Tweak_03_Jnt', u'L_Shirt_Sleeve_Tweak_04_Jnt',
            u'L_Shirt_Sleeve_Tweak_05_Jnt', u'L_Shirt_Sleeve_Tweak_06_Jnt', u'L_Shirt_Sleeve_Tweak_07_Jnt', u'L_Shirt_Sleeve_Tweak_08_Jnt']

    for j in jnts:
        for a in 'XYZ':
            cmds.setAttr(j+'.rotate'+a, cmds.getAttr(j+'.jointOrient'+a))
            cmds.setAttr(j+'.jointOrient'+a, 0)

    jnts = [u'R_Shirt_Sleeve_Tweak_01_Jnt', u'R_Shirt_Sleeve_Tweak_02_Jnt', u'R_Shirt_Sleeve_Tweak_03_Jnt', u'R_Shirt_Sleeve_Tweak_04_Jnt', u'R_Shirt_Sleeve_Tweak_05_Jnt', u'R_Shirt_Sleeve_Tweak_06_Jnt', u'R_Shirt_Sleeve_Tweak_07_Jnt',
            u'R_Shirt_Sleeve_Tweak_08_Jnt', u'R_Shirt_Collar_Tweak_01_Jnt', u'R_Shirt_Collar_Tweak_02_Jnt', u'R_Shirt_Collar_Tweak_03_Jnt', u'R_Shirt_Hem_Tweak_01_Jnt', u'R_Shirt_Hem_Tweak_02_Jnt', u'R_Shirt_Hem_Tweak_03_Jnt']
    for j in jnts:
        for a in 'XYZ':
            cmds.setAttr(j+'.jointOrient'+a, 0)

import pymel.core as pm
import maya.cmds as cmds


def createDiaperJoints():
    grp = cmds.createNode('transform', name='Tweak_Jnts_Grp')

    cmds.joint(grp, name='C_Diaper_Tweak_Base_Jnt', radius=.5)
    Waist = cmds.joint(grp, name='C_Diaper_Waist_Tweaks_Grp', position=(0, 5, -5), radius=.5)
    Tail = cmds.joint(grp, name='C_Diaper_Tail_Tweaks_Grp', position=(0, 5, -15), radius=.5)

    cmds.joint(Waist, name='C_Diaper_Waist_Tweak_01_Jnt', position=(0, 5, 0), orientation=(90, 0, 180), relative=True, radius=.5)
    cmds.joint(Waist, name='C_Diaper_Waist_Tweak_02_Jnt', position=(0, -5, 0), orientation=(90, 0, 0), relative=True, radius=.5)
    cmds.joint(Waist, name='L_Diaper_Waist_Tweak_01_Jnt', position=(2.5, 2.5, 0), orientation=(90, 0, 135), relative=True, radius=.5)
    cmds.joint(Waist, name='L_Diaper_Waist_Tweak_02_Jnt', position=(5, 0, 0), orientation=(90, 0, 90), relative=True, radius=.5)
    cmds.joint(Waist, name='L_Diaper_Waist_Tweak_03_Jnt', position=(2.5, -2.5, 0), orientation=(90, 0, 45), relative=True, radius=.5)
    cmds.joint(Waist, name='R_Diaper_Waist_Tweak_01_Jnt', radius=.5)
    cmds.joint(Waist, name='R_Diaper_Waist_Tweak_02_Jnt', radius=.5)
    cmds.joint(Waist, name='R_Diaper_Waist_Tweak_03_Jnt', radius=.5)

    cmds.joint(Tail, name='C_Diaper_Tail_Tweak_01_Jnt', position=(0, 5, 0), orientation=(90, 180, 180), relative=True, radius=.5)
    cmds.joint(Tail, name='C_Diaper_Tail_Tweak_02_Jnt', position=(0, -5, 0), orientation=(90, 180, 0), relative=True, radius=.5)
    cmds.joint(Tail, name='L_Diaper_Tail_Tweak_01_Jnt', position=(2.5, 2.5, 0), orientation=(90, 180, 135), relative=True, radius=.5)
    cmds.joint(Tail, name='L_Diaper_Tail_Tweak_02_Jnt', position=(5, 0, 0), orientation=(90, 180, 90), relative=True, radius=.5)
    cmds.joint(Tail, name='L_Diaper_Tail_Tweak_03_Jnt', position=(2.5, -2.5, 0), orientation=(90, 180, 45), relative=True, radius=.5)
    cmds.joint(Tail, name='R_Diaper_Tail_Tweak_01_Jnt', radius=.5)
    cmds.joint(Tail, name='R_Diaper_Tail_Tweak_02_Jnt', radius=.5)
    cmds.joint(Tail, name='R_Diaper_Tail_Tweak_03_Jnt', radius=.5)

    for side in 'LR':
        Leg = cmds.joint(grp, name=side+'_Diaper_Leg_Tweaks_Grp', position=(4, 3, -9), orientation=(0, 0, 0), radius=.5)

        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_01_Jnt', position=(0, 3, 0), orientation=(0, -90, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_02_Jnt', position=(0, 3, 3), orientation=(0, -45, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_03_Jnt', position=(0, 0, 3), orientation=(0, 0, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_04_Jnt', position=(0, -3, 3), orientation=(0, 45, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_05_Jnt', position=(0, -3, 0), orientation=(0, 90, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_06_Jnt', position=(0, -3, -3), orientation=(0, 135, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_07_Jnt', position=(0, 0, -3), orientation=(0, 180, -90), relative=True, radius=.5)
        cmds.joint(Leg, name=side+'_Diaper_Leg_Tweak_08_Jnt', position=(0, 3, -3), orientation=(0, -135, -90), relative=True, radius=.5)

    jnts = ['L_Diaper_Waist_Tweak_01_Jnt', 'L_Diaper_Waist_Tweak_02_Jnt', 'L_Diaper_Waist_Tweak_03_Jnt', 'L_Diaper_Leg_Tweaks_Grp', 'L_Diaper_Tail_Tweak_01_Jnt', 'L_Diaper_Tail_Tweak_02_Jnt', 'L_Diaper_Tail_Tweak_03_Jnt',
            'L_Diaper_Leg_Tweak_01_Jnt', 'L_Diaper_Leg_Tweak_02_Jnt', 'L_Diaper_Leg_Tweak_03_Jnt', 'L_Diaper_Leg_Tweak_04_Jnt', 'L_Diaper_Leg_Tweak_05_Jnt', 'L_Diaper_Leg_Tweak_06_Jnt', 'L_Diaper_Leg_Tweak_07_Jnt',
            'L_Diaper_Leg_Tweak_08_Jnt']

    for j in jnts:
        if not 'Grp' in j:
            lJnt = j
            rJnt = lJnt.replace('L_', 'R_')
            rot = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '').replace('Jnt', 'Rot_Mult'))
            trans = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '').replace('Jnt', 'Trans_Mult'))
            cmds.setAttr(trans+'.input2X', -1)
            cmds.setAttr(rot+'.input2Y', -1)
            cmds.setAttr(rot+'.input2Z', -1)
            cmds.connectAttr(lJnt+'.rotate', rot+'.input1')
            cmds.connectAttr(rot+'.output', rJnt+'.rotate')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.output', rJnt+'.translate')
        else:
            lJnt = j
            rJnt = lJnt.replace('L_', 'R_')
            rot = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Rot_Mult')
            trans = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Trans_Mult')
            cmds.setAttr(trans+'.input2X', -1)
            cmds.setAttr(rot+'.input2Y', -1)
            cmds.setAttr(rot+'.input2Z', -1)
            cmds.connectAttr(lJnt+'.rotate', rot+'.input1')
            cmds.connectAttr(rot+'.output', rJnt+'.rotate')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.output', rJnt+'.translate')

    jnts = [u'C_Diaper_Waist_Tweak_01_Jnt', u'C_Diaper_Waist_Tweak_02_Jnt', u'L_Diaper_Waist_Tweak_01_Jnt', u'L_Diaper_Waist_Tweak_02_Jnt', u'L_Diaper_Waist_Tweak_03_Jnt', u'C_Diaper_Tail_Tweak_01_Jnt', u'C_Diaper_Tail_Tweak_02_Jnt',
            u'L_Diaper_Tail_Tweak_01_Jnt', u'L_Diaper_Tail_Tweak_02_Jnt', u'L_Diaper_Tail_Tweak_03_Jnt', u'L_Diaper_Leg_Tweak_01_Jnt', u'L_Diaper_Leg_Tweak_02_Jnt', u'L_Diaper_Leg_Tweak_03_Jnt', u'L_Diaper_Leg_Tweak_04_Jnt',
            u'L_Diaper_Leg_Tweak_05_Jnt', u'L_Diaper_Leg_Tweak_06_Jnt', u'L_Diaper_Leg_Tweak_07_Jnt', u'L_Diaper_Leg_Tweak_08_Jnt']

    for j in jnts:
        for a in 'XYZ':
            cmds.setAttr(j+'.rotate'+a, cmds.getAttr(j+'.jointOrient'+a))
            cmds.setAttr(j+'.jointOrient'+a, 0)

    jnts = [u'R_Diaper_Leg_Tweak_01_Jnt', u'R_Diaper_Leg_Tweak_02_Jnt', u'R_Diaper_Leg_Tweak_03_Jnt', u'R_Diaper_Leg_Tweak_04_Jnt', u'R_Diaper_Leg_Tweak_05_Jnt', u'R_Diaper_Leg_Tweak_06_Jnt', u'R_Diaper_Leg_Tweak_07_Jnt',
            u'R_Diaper_Leg_Tweak_08_Jnt', u'R_Diaper_Tail_Tweak_01_Jnt', u'R_Diaper_Tail_Tweak_02_Jnt', u'R_Diaper_Tail_Tweak_03_Jnt', u'R_Diaper_Waist_Tweak_01_Jnt', u'R_Diaper_Waist_Tweak_02_Jnt', u'R_Diaper_Waist_Tweak_03_Jnt']
    for j in jnts:
        for a in 'XYZ':
            cmds.setAttr(j+'.jointOrient'+a, 0)


# make a function to make icon controls
def make_icon_controls(ctrl, control_pos, control_rot, ctrl_colour, ctrl_shape):
    i_control = i_node.create("control", name=ctrl, control_type=ctrl_shape, with_gimbal=False, color=ctrl_colour, size=5)
    ctrl_dag = i_control.control
    ctrl_offset_group = ctrl+'_Ctrl_Offset_Grp'
    cmds.xform(ctrl_offset_group, ws=True, translation=control_pos)
    cmds.xform(ctrl_offset_group, ws=True, rotation=control_rot)

    return ctrl+'_Ctrl'


# Create zero node
def zero(nodes):
    for n in nodes:
        if n:
            zero = cmds.createNode('transform', name=n+'_Zero')
            const = cmds.parentConstraint(n, zero, maintainOffset=False)
            cmds.delete(const)
            prnt = cmds.listRelatives(n, parent=True)

            if prnt:
                cmds.parent(zero, prnt)
            cmds.parent(n, zero)


# Zero out joint orient
def jntOr(nodes):
    attrs = ["jointOrientX", "jointOrientY", "jointOrientZ"]

    for a in attrs:
        for n in nodes:
            cmds.setAttr(n+"."+a, 0)






def buildTweaks(type):
    if type=='Shirt':
        parts = ['Collar', 'Hem', 'Sleeve']
    elif type=='Diaper':
        parts = ['Waist', 'Tail', 'Leg']

    jnts = []
    for part in parts:
        jnts = cmds.ls('*'+type+'_'+part+'_Tweak_*_Jnt')

        # break mirroring connections
        for j in jnts:
            if not cmds.objExists(j.replace('Jnt', 'Ctrl')):
                attrs = ['translate', 'rotate']
                for a in attrs:
                    if cmds.connectionInfo(j+'.'+a, isDestination=True):
                        src = cmds.connectionInfo(j+'.'+a, sourceFromDestination=True)
                        if src:
                            cmds.disconnectAttr(src, j+'.'+a)

        # zero out joints
        for j in jnts:
            if not cmds.objExists(j.replace('Jnt', 'Ctrl')):
                zero([j])
                jntOr([j])

                attrs = ['rx', 'ry', 'rz']
                print j
                for a in attrs:
                    cmds.setAttr(j+'.'+a, 0)

                # Create controls
                pos = cmds.xform(j, worldSpace=True, scalePivot=True, query=True)
                rot = cmds.xform(j, rotation=True, worldSpace=True, query=True)

                ctrl = make_icon_controls(j[:-4], pos, rot, 'aqua', '3D Sphere')
                offset = ctrl+'_Offset_Grp'

                attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
                for a in attrs:
                    cmds.connectAttr(ctrl+'.'+a, j+'.'+a)

                # Organize
                grp = 'Tweak_Ctrls_Grp'

                if not cmds.objExists(grp):
                    grp = cmds.createNode('transform', n="Tweak_Ctrls_Grp")
                    cmds.parent(grp, "Ctrl_Grp")

                if cmds.listRelatives(offset, parent=True):
                    if not cmds.listRelatives(offset, parent=True)[0]==grp:
                        cmds.parent(offset, grp)
                else:
                    cmds.parent(offset, grp)

    # Wrap Geo
    wrapGeo = type+'_Wrap_Geo'
    if cmds.objExists(wrapGeo):
        if not cmds.listRelatives(wrapGeo, parent=True):
            # clean history
            cmds.delete(wrapGeo, constructionHistory=True)

            # skin geo
            jnts = cmds.ls('*'+type+'_*_Tweak_*_Jnt')
            jnts.append('C_'+type+'_Tweak_Base_Jnt')
            cmds.skinCluster(wrapGeo, jnts, toSelectedBones=True)

            # Organize
            utils = 'Tweak_Utils_Grp'
            if not cmds.objExists(utils):
                utils = cmds.createNode('transform', n=utils)
                cmds.parent(wrapGeo, utils)

            grps = ['Tweak_Utils_Grp']

            for g in grps:
                if cmds.objExists(g):
                    if cmds.listRelatives(g, parent=True):
                        if not cmds.listRelatives(g, parent=True)[0]=='Utility_Grp':
                            cmds.parent(g, 'Utility_Grp')
                    else:
                        cmds.parent(g, 'Utility_Grp')

    else:
        print 'Wrap geo does not exist, please create a simplified geo of the '+type+' called '+type+'_Wrap_Geo and re-run.'

    # Fol Geo
    folGeo = type+'_Wrap_Fol_Geo'
    if cmds.objExists(folGeo):
        if not cmds.listRelatives(folGeo, parent=True):
            # clean history
            cmds.polyNormalPerVertex(folGeo, unFreezeNormal=True)
            cmds.polyTriangulate(folGeo)
            cmds.delete(folGeo, constructionHistory=True)

            # define geo to skin from
            skinned = ''
            if type=='Shirt':
                skinned = '*:Uniform_Geo'
            elif type=='Diaper':
                skinned = '*:Diaper_Geo'

            # skin geo
            if skinned:
                if cmds.objExists(skinned):
                    cmds.select([skinned, folGeo])
                    skin_tools.bind_like()

                else:
                    print 'Cannot find skinned geo to drive follicles, please manually skin '+folGeo

            # drive controls
            offsets = cmds.ls('*'+type+'_*_Tweak_*_Ctrl_Offset_Grp')


            offsets.append(folGeo)
            cmds.select(offsets)
            deformers.follicle_attach_sel()

            # Organize
            utils = 'Tweak_Utils_Grp'
            if not cmds.objExists(utils):
                utils = cmds.createNode('transform', n=utils)
            cmds.parent(folGeo, utils)

            grps = ['Tweak_Utils_Grp', 'Flc_Pin_Flc_Grp', 'Flc_Pin_Ctrl_Grp']

            for g in grps:
                if cmds.objExists(g):
                    if cmds.listRelatives(g, parent=True):
                        if not cmds.listRelatives(g, parent=True)[0]=='Utility_Grp':
                            cmds.parent(g, 'Utility_Grp')
                    else:
                        cmds.parent(g, 'Utility_Grp')

    else:
        print 'Fol geo does not exist, please create a simplified geo of the '+type+' called '+type+'_Wrap_Geo and re-run.'

    # Organize
    grps = ['Tweak_Jnts_Grp']

    for g in grps:
        if cmds.objExists(g):
            if cmds.listRelatives(g, parent=True):
                if cmds.listRelatives(g, parent=True)[0]=='Utility_Grp':
                    cmds.parent(g, 'Jnt_Grp')
            cmds.parent(g, 'No_Inherit_Grp')

    # Create wraps
    if type=='Shirt':
        print '*******'
        print 'Building wraps'
        for g in ['Uniform_Geo', 'Button_Fol_Geo']:
            if cmds.objExists('*:'+g):
                print g
                cmds.select(['*:'+g, 'Shirt_Wrap_Geo'])
                cmds.deformer(type='wrap', name=g+'_Wrap', frontOfChain=True)
            elif cmds.objExists(g):
                print g
                cmds.select([g, 'Shirt_Wrap_Geo'])
                cmds.deformer(type='wrap', name=g+'_Wrap', frontOfChain=True)
            else:
                print "didn't find any geo to wrap"
    elif type=='Diaper':
        print '*******'
        print 'Building wraps'
        for g in ['Diaper_Geo']:
            if cmds.objExists('*:'+g):
                print g
                cmds.select(['*:'+g, 'Diaper_Wrap_Geo'])
                cmds.deformer(type='wrap', name=g+'_Wrap', frontOfChain=True)
            elif cmds.objExists(g):
                print g
                cmds.select([g, 'Diaper_Wrap_Geo'])
                cmds.deformer(type='wrap', name=g+'_Wrap', frontOfChain=True)
            else:
                print "didn't find any geo to wrap"
