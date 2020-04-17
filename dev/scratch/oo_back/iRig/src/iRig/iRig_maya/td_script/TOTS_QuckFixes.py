__author__ = 'stevenb'


def fix_toeStretch()
    import maya.cmds as cmds
    for side in ['L_','R_']:
        cmds.parent(side+'Foot_Ball_Ik_Ctrl_Offset_Grp',w=1)
        my_point = cmds.pointConstraint(side+'Foot_ToeTip_Ik_Ctrl',side+'Foot_Ball_Toe_Pivot_Offset_Grp',mo=0)
        cmds.delete(my_point)
        cmds.parent(side+'Foot_Ball_Ik_Ctrl_Offset_Grp',side+'Foot_Ball_Toe_Pivot_Cns_Grp')


def fix_eyeMirror():
    import maya.cmds as cmds
    for lid in ['Upr_','Lwr_']:
        for each in ['In','Mid','Out']:
            cmds.parent('Face_R_Eye_Lid_'+lid+each+'_Ctrl_AutoFollow_Tfm',w=1)
        cmds.setAttr('Face_R_Eye_Lid_'+lid+'Ctrl_Offset_Grp.ry',180)
        for each in ['In','Mid','Out']:
            cmds.parent('Face_R_Eye_Lid_'+lid+each+'_Ctrl_AutoFollow_Tfm','Face_R_Eye_Lid_'+lid+'Ctrl_AutoFollow_Tfm')


def hookup_eyeScale():
    import maya.cmds as cmds
    for side in ['L_','R_']:
        proj = side + 'Eye_Projection_3DPlace'
        cons_grp = cmds.group(em=1,p=proj+'_Offset',n=proj+'_Cons')
        cmds.parent(proj, cons_grp)
        cmds.setAttr(side+'Eye_Aim_Ctrl.r',ch=1,k=1,l=0)
        cmds.setAttr(side+'Eye_Aim_Ctrl.s',ch=1,k=1,l=0)
        for at in ['.rx','.ry','.rz','.sx','.sy','.sz']:
            cmds.setAttr(side+'Eye_Aim_Ctrl'+at,ch=1,k=1,l=0)
            cmds.connectAttr(side+'Eye_Aim_Ctrl'+at,cons_grp+at)
        for bat in ['.rx','.ry','.sz']:
            cmds.setAttr(side+'Eye_Aim_Ctrl'+bat,ch=0,k=0,l=1)
        if 'R_' in side:
            md = cmds.createNode('multiplyDivide',n='eyeScale_MD')
            cmds.setAttr(md+'.input2X', -1)
            cmds.connectAttr(side+'Eye_Aim_Ctrl.rz',md+'.input1X')
            cmds.connectAttr(md+'.outputX',cons_grp+'.rz',f=1)
        my_Export = (cmds.listConnections(proj+'.parentMatrix[0]')[0]).replace('_parentConstraint1','')
        cmds.scaleConstraint(proj, my_Export)



def hand_Override():
    for side in ['L_','R_']:
        cmds.addAttr(side+'Arm_IKFKSwitch_Ctrl',ln = 'Hand_Override', at = 'enum',k=1, en = 'Wing:Hand')
        rev = cmds.createNode('reverse',n=side+'hand_Override_Rev')
        cmds.connectAttr(side+'Arm_IKFKSwitch_Ctrl.Hand_Override',rev+'.inputX')
        for feath in ['01_','02_','03_','04_','05_']:
            offsets = cmds.ls(side+'Wing_Feather'+feath+'*Ctrl_Offset_Grp')
            cns = cmds.ls(side+'Wing_Feather'+feath+'*Ctrl_Cns_Grp')
            for i in range(len(offsets)):
                bcT = cmds.createNode('blendColors',n=(offsets[i].replace('_Fk_Tweak_Ctrl_Offset_Grp','_Trans_Blend')))
                bcR = cmds.createNode('blendColors',n=(offsets[i].replace('_Fk_Tweak_Ctrl_Offset_Grp','_Rot_Blend')))
                cmds.connectAttr(rev+'.outputX', bcT+'.blender')
                cmds.connectAttr(rev+'.outputX', bcR+'.blender')
                my_jnt = offsets[i].replace('_Fk_Ctrl_Offset_Grp','_Jnt')
                cmds.connectAttr(my_jnt+'.t',bcT+'.color1')
                cmds.connectAttr(my_jnt+'.r',bcR+'.color1')
                pbt = cmds.getAttr(bcT+'.color1')
                pbr = cmds.getAttr(bcR+'.color1')
                cmds.setAttr(bcT+'.color2',round(pbt[0][0],3),round(pbt[0][1],3),round(pbt[0][2],3))
                cmds.setAttr(bcR+'.color2',round(pbr[0][0],3),round(pbr[0][1],3),round(pbr[0][2],3))
                cmds.connectAttr(bcT+'.output',offsets[i]+'.t',f=1)
                cmds.connectAttr(bcR+'.output',cns[i]+'.r',f=1)
        hand_off = cmds.group(em=1,n=side+'Hand_Offset_Grp',p=side+'Wing_BaseOffset_4_Ctrl')
        cmds.parent(hand_off,side+'Wing_FkCtrl_Grp')
        hand_cns = cmds.group(em=1,n=side+'Hand_Cons_Grp',p=hand_off)
        hand_xtra = cmds.group(em=1,n=side+'Hand_Xtra_Grp')
        cmds.parent(hand_xtra,hand_cns)
        for each_grp in ['01','02','03','04','05']:
            cmds.parent(side+'Wing_Feather'+each_grp+'_Start_Fk_Ctrl_Offset_Grp',hand_xtra)
        cmds.parentConstraint(side+'Wing_BaseOffset_4_Ctrl',hand_cns,mo=0)
        cmds.connectAttr(side+'Arm_IKFKSwitch_Ctrl.Hand_Override',side+'Hand_Cons_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_CtrlW0')

        bcTip = cmds.createNode('blendColors',n=side+'WingFeathers_Tip_Blend')
        bcBase = cmds.createNode('blendColors',n=side+'WingFeathers_Base_Blend')
        cmds.connectAttr(rev+'.outputX', bcTip+'.blender')
        cmds.connectAttr(rev+'.outputX', bcBase+'.blender')
        cmds.setAttr(bcTip+'.color1R',0.8)
        cmds.setAttr(bcTip+'.color1G',0.8)
        cmds.setAttr(bcTip+'.color1B',0.8)
        cmds.setAttr(bcTip+'.color2R',0)
        cmds.setAttr(bcTip+'.color2G',0)
        cmds.setAttr(bcTip+'.color2B',0)
        cmds.setAttr(bcBase+'.color1R',0.167)
        cmds.setAttr(bcBase+'.color1G',0.333)
        cmds.setAttr(bcBase+'.color1B',0.5)
        cmds.setAttr(bcBase+'.color2R',0)
        cmds.setAttr(bcBase+'.color2G',0)
        cmds.setAttr(bcBase+'.color2B',0)
        cmds.connectAttr(bcTip+'.outputR',side+'Wing_FeatherTip_Foll_7_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_CtrlW0')
        cmds.connectAttr(bcTip+'.outputG',side+'Wing_FeatherTip_Foll_8_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_CtrlW0')
        cmds.connectAttr(bcTip+'.outputB',side+'Wing_FeatherTip_Foll_9_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_CtrlW0')
        if 'L_' in side:
            cmds.connectAttr(bcBase+'.outputR',side+'Wing_FeatherBase_Foll_12_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW1')
            cmds.connectAttr(bcBase+'.outputG',side+'Wing_FeatherBase_Foll_13_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW1')
            cmds.connectAttr(bcBase+'.outputB',side+'Wing_FeatherBase_Foll_14_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW1')
        if 'R_' in side:
            cmds.connectAttr(bcBase+'.outputR',side+'Wing_FeatherBase_Foll_12_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW0')
            cmds.connectAttr(bcBase+'.outputG',side+'Wing_FeatherBase_Foll_13_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW0')
            cmds.connectAttr(bcBase+'.outputB',side+'Wing_FeatherBase_Foll_14_ClsHandle_Offset_Grp_parentConstraint1.'+side+'Wing_BaseOffset_4_NullW0')





