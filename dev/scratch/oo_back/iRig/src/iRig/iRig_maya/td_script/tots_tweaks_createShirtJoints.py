import pymel.core as pm
import maya.cmds as cmds


def do_it():
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