import pymel.core as pm
import maya.cmds as cmds


def do_it():
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
            cmds.connectAttr(rot+'.outputX', rJnt+'.rotateX')
            cmds.connectAttr(rot+'.outputY', rJnt+'.rotateY')
            cmds.connectAttr(rot+'.outputZ', rJnt+'.rotateZ')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.outputX', rJnt+'.translateX')
            cmds.connectAttr(trans+'.outputY', rJnt+'.translateY')
            cmds.connectAttr(trans+'.outputZ', rJnt+'.translateZ')
        else:
            lJnt = j
            rJnt = lJnt.replace('L_', 'R_')
            rot = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Rot_Mult')
            trans = cmds.createNode('multiplyDivide', name=lJnt.replace('L_', '')+'Trans_Mult')
            cmds.setAttr(trans+'.input2X', -1)
            cmds.setAttr(rot+'.input2Y', -1)
            cmds.setAttr(rot+'.input2Z', -1)
            cmds.connectAttr(lJnt+'.rotate', rot+'.input1')
            cmds.connectAttr(rot+'.outputX', rJnt+'.rotateX')
            cmds.connectAttr(rot+'.outputY', rJnt+'.rotateY')
            cmds.connectAttr(rot+'.outputZ', rJnt+'.rotateZ')
            cmds.connectAttr(lJnt+'.translate', trans+'.input1')
            cmds.connectAttr(trans+'.outputX', rJnt+'.translateX')
            cmds.connectAttr(trans+'.outputY', rJnt+'.translateY')
            cmds.connectAttr(trans+'.outputZ', rJnt+'.translateZ')

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



