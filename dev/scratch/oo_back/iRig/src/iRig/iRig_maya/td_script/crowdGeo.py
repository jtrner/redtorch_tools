import maya.cmds as cmds

Inputt = ['R_armUpFk_aimJoint','L_armUpFk_aimJoint','R_loleg2_joint','R_upleg2_joint','L_loleg2_joint','L_upleg2_joint','R_loarm2_joint',
         'R_uparm3_joint','L_loarm2_joint',
         'L_uparm3_joint','R_loleg2_joint',
         'L_loleg2_joint','R_upleg2_joint',
         'L_upleg2_joint','R_loarm2_joint',
         'L_loarm2_joint','R_uparm2_joint',
         'L_uparm2_joint','R_toe_fk_ctrl',
         'R_loLeg2_ctrl','L_toe_fk_ctrl',
         'L_loLeg2_ctrl',
          'hair01_jnt01', 'hair01_jnt02','hair01_jnt03','hair01_jnt04','hair01_jnt05','hair02_jnt01','hair02_jnt02','hair02_jnt03','hair02_jnt04',
         'L_upLeg0_joint','R_upLeg0_joint',
         'L_loLeg0_joint','R_loLeg0_joint',
         'L_upArm0_joint','R_upArm0_joint',
         'L_loArm0_joint','R_loArm0_joint',
         'head_joint',
          'spine0_joint','spine1_joint','spine2_joint','spine3_joint','spine4_joint','spine5_joint','spine6_joint','spine7_joint','spine8_joint',
         'L_hand_influence', 'L_index_1_ctrl','L_index_2_ctrl', 'L_index_3_ctrl', 'L_index_base_ctrl', 'L_loArm4_joint', 'L_middle_1_ctrl',
         'L_middle_2_ctrl', 'L_middle_3_ctrl', 'L_middle_base_ctrl', 'L_pinky_1_ctrl','L_pinky_2_ctrl','L_pinky_3_ctrl','L_pinky_base_ctrl',
         'L_ring_1_ctrl','L_ring_2_ctrl','L_ring_3_ctrl','L_ring_base_ctrl','L_thumb_1_ctrl','L_thumb_2_ctrl','L_thumb_base_ctrl',
         'R_hand_influence','R_index_1_ctrl','R_index_2_ctrl','R_index_3_ctrl','R_index_base_ctrl','R_loArm4_joint','R_middle_1_ctrl',
         'R_middle_2_ctrl','R_middle_3_ctrl','R_middle_base_ctrl','R_pinky_1_ctrl','R_pinky_2_ctrl','R_pinky_3_ctrl','R_pinky_base_ctrl',
         'R_ring_1_ctrl','R_ring_2_ctrl','R_ring_3_ctrl','R_ring_base_ctrl','R_thumb_1_ctrl','R_thumb_2_ctrl','R_thumb_base_ctrl']


def ArcProxy(Input = Inputt, *args):
    import random
    Input1 = []
    if not Input:
        Input = Inputt
    for e in Input:
        if cmds.objExists(e):
            Input1.append(e)
    #Find all bind joints
    if Input == None:
        BindJoints = cmds.ls('*_Bnd',typ='joint')
    else:
        BindJoints = Input1
    PrxList = []
    #For each make a proxy object
    for each in BindJoints:
        if not cmds.objExists(each+'_PRX'):
            PRX = cmds.polyCylinder(n=each+'_PRX', r=1, h = 2, sx = 10, sy = 2, sz = 1, ch = False)
            cmds.setAttr(PRX[0]+'.castsShadows',0)
            cmds.setAttr(PRX[0]+ '.receiveShadows', 0)
            cmds.setAttr(PRX[0] + '.motionBlur', 0)
            cmds.setAttr(PRX[0] + '.primaryVisibility', 0)
            cmds.setAttr(PRX[0]+ '.visibleInReflections', 0)
            cmds.setAttr(PRX[0]+ '.visibleInRefractions', 0)
            cmds.setAttr(PRX[0]+ '.doubleSided', 0)
            cmds.setAttr(PRX[0] + '.smoothShading', 0)
            cmds.parentConstraint(each, PRX, mo = False)
            cmds.scaleConstraint(each, PRX, mo = False)
            PrxList.append(str(PRX[0]))
        else:
            print(each + ' Already Made')
    if not cmds.objExists('PRX_Grp'):
        cmds.group(PrxList, n = 'PRX_Grp', p = 'md')
    else:
        cmds.parent(PrxList,'PRX_Grp')
    Prx = cmds.ls('*_PRX')
    if not cmds.objExists('PRX_Shdr'):
        PrxShdr = cmds.shadingNode('lambert', asShader=True, name = 'PRX_Shdr')
    else:
        PrxShdr = 'PRX_Shdr'
    cmds.select(Prx)
    cmds.hyperShade( assign=PrxShdr )
    cmds.select( cl=True )
    cmds.setAttr(PrxShdr+'.color', random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0))
    Heads = cmds.ls('*Head*PRX')
    for each in Heads:
        if not cmds.objExists(each):
            flare = each.replace('PRX','A_Flare')
            print(flare + ' Connected to '+each)
            if cmds.objExists(flare):
                cmds.deformer( flare, e=True, g=each )
            twist = each.replace('PRX','B_Twist')
            print(twist + ' Connected to '+each)
            if cmds.objExists(twist):
                cmds.deformer( twist, e=True, g=each )
            wire = each.replace('PRX','C_Wire')
            print(wire + ' Connected to '+each)
            if cmds.objExists(wire):
                cmds.deformer( wire, e=True, g=each )
    chan = ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz','.v']
    for p in PrxList:
        for c in chan:
            cmds.setAttr(p + c, lock = True, keyable = False, channelBox = False)
        if cmds.objExists('*End_PRX'):
            cmds.delete('*End_PRX')
    cmds.select('root*')
    cmds.addAttr(longName='Geo_Res', at='enum', en='Proxy:Render', k=True)
    cmds.connectAttr('*.Geo_Res','MTM_model.v')
    Reverse = cmds.createNode('reverse')
    cmds.rename(Reverse,'GeoResVis_Reverse')
    cmds.connectAttr('*.Geo_Res','GeoResVis_Reverse.input.inputX')
    cmds.connectAttr('GeoResVis_Reverse.output.outputX','PRX_Grp.v')