import maya.cmds as cmds
import icon_api.node as i_node

def build_extra_forarm_guides():

    main_grp = cmds.group(n="forearm_guides_Grp", em=1)
    #extra_loc = ["Clavicle", "Scapula", "Carpus"]
    extra_loc = ["Clavicle", "Scapula"]

    for i in extra_loc:
        left_loc = cmds.spaceLocator(n="L_{}_Guide".format(i))[0]
        right_loc = cmds.spaceLocator(n="R_{}_Guide".format(i))[0]
        mult = cmds.createNode("multiplyDivide", n="Guide_{}_Mdn".format(i))

        cmds.parent(left_loc, right_loc, main_grp)
        cmds.setAttr(mult + ".input2X", -1)
        cmds.connectAttr(left_loc + ".t", mult + ".input1")
        cmds.connectAttr(mult + ".output", right_loc + ".t")

        for x in [".overrideEnabled", ".overrideDisplayType"]:
            cmds.setAttr(right_loc + "Shape" + x, 1)

        cmds.addAttr(left_loc, at="bool", ln="ForelegGuide")
        cmds.addAttr(right_loc, at="bool", ln="ForelegGuide")

    print("---------- ADDITIONAL FOREARM GUIDES COMPLETE --------")

def build_extra_forarm_rig():

    components = {}
    arm_guides = cmds.ls("*.ForelegGuide")

    # position joints
    for i in arm_guides:

        item = i.split(".")[0]
        pos = cmds.xform(item, q=1, t=1)
        item_component = item.split("_")[0] + item.split("_")[1]
        cmds.select(cl=1)
        jnt = cmds.joint(n=item.replace("Guide", "Bnd_Jnt"))

        components[item_component] = jnt

        # flip joint if on right side
        if "R" in i:
            cmds.xform(jnt, t=pos)
            cmds.setAttr(jnt + ".rx", 180)
        else:
            cmds.xform(jnt, t=pos)

    # organise joints into hierarchy
    for i in "LR":

        if i == "L":
            col = "blue"
        else:
            col = "red"

        # grab current transforms needed to perform setup
        main_control_grp = i + "_FrontHip_Grp"
        main_control = i + "_FrontHip_Ctrl"
        main_offset_grp = i + "_FrontHip_Ctrl_Offset_Grp"
        ankle_bind = i + "_FrontLeg_Ankle_Jnt"
        knee_bnd = i + "_FrontLeg_Knee_Jnt"
        ankle_control = [i + "_FrontLeg_Foot_Ik_Ctrl", i + "_FrontLeg_Foot_Ik_Gimbal_Ctrl"]
        hip_pivot_control = i + "_FrontLeg_HipPoint_Ctrl"
        clavicle = components[i + "Clavicle"]
        scapula = components[i + "Scapula"]
        #carpus = components[i + "Carpus"]
        parentFrontLeg = i + "_FrontLeg_Rig_Jnt_Grp"
        SS_node = i + "_FrontLeg_Knee_Stretch_IkFk_Blend_Blc"
        knee_Fk_space_switch = i + "_FrontLeg_Knee_Fk_Ctrl_Follow_Driver_Orient_Tfm"
        main_switch_control = i + "_FrontFoot_IKFKSwitch_Ctrl"
        kneeFk_Control = i + "_FrontLeg_Knee_Fk_Ctrl"
        ankleFk_Offset = i + "_FrontLeg_Ankle_Fk_Ctrl_Offset_Grp"
        clavicle_grp = cmds.group(clavicle, n=i + "_ForeLeg_Rig_Jnt_Grp", p="Rig_Jnt_Grp")

        cmds.parent(parentFrontLeg, clavicle)
        cmds.parent(scapula, clavicle)

        # gather all necessary transforms to snap to later on
        clav_pos = cmds.xform(clavicle, q=1, ws=1, matrix=1)
        scapula_pos = cmds.xform(scapula, q=1, ws=1, matrix=1)
        #carpus_pos = cmds.xform(carpus, q=1, ws=1, matrix=1)
        hip_pos = cmds.xform(hip_pivot_control, q=1, ws=1, matrix=1)
        ankle_pos = cmds.xform(ankle_bind, q=1, ws=1, matrix=1)
        knee_pos = cmds.xform(knee_bnd, q=1, ws=1, matrix=1)

        # create controllers
        clavicle_control = clavicle.replace("Bnd_Jnt", "Ctrl")
        i_node.create("control", name=clavicle_control, with_gimbal=False, control_type="2d Circle", color=col, size=2)
        clavicle_grp = cmds.listRelatives(clavicle_control, p=1)[0]
        clavicle_offset =  cmds.listRelatives(clavicle_grp, p=1)[0]
        cmds.parent(clavicle_offset, main_control_grp)

        scap_control = scapula.replace("Bnd_Jnt", "Ctrl")
        i_node.create("control", name=scap_control, with_gimbal=False, control_type="2d Circle", color=col, size=1)
        scap_grp = cmds.listRelatives(scap_control, p=1)[0]
        scap_offset = cmds.listRelatives(scap_grp, p=1)[0]
        cmds.parent(scap_offset, main_control_grp)

        scap_aim_control = scapula.replace("Bnd_Jnt", "Aim_Ctrl")
        i_node.create("control", name=scap_aim_control, with_gimbal=False, control_type="2d Arrow Single", color=col, size=1)
        scap_aim_grp = cmds.listRelatives(scap_aim_control, p=1)[0]
        scap_aim_offset = cmds.listRelatives(scap_aim_grp, p=1)[0]
        cmds.parent(scap_aim_offset, main_control_grp)

        '''
        carpusFK_control = carpus.replace("_Jnt", "_Fk_Ctrl")
        i_node.create("control", name=carpusFK_control, with_gimbal=False, control_type="3D Cube", color=col, size=1)
        carpusFK_grp = cmds.listRelatives(carpusFK_control, p=1)[0]
        carpusFK_offset = cmds.listRelatives(carpusFK_grp, p=1)[0]
        cmds.parent(carpusFK_offset, main_control_grp)
        
        carpusIK_control = carpus.replace("_Jnt", "_Ik_Ctrl")
        i_node.create("control", name=carpusIK_control, with_gimbal=False, control_type="2d Circle", color=col, size=1)
        carpusIK_grp = cmds.listRelatives(carpusIK_control, p=1)[0]
        carpusIK_offset = cmds.listRelatives(carpusIK_grp, p=1)[0]
        cmds.parent(carpusIK_offset, main_control_grp)
        
        cmds.xform(carpusFK_offset, ws=1, matrix=carpus_pos)
        cmds.xform(carpusIK_offset, ws=1, matrix=carpus_pos)
        '''
        cmds.xform(clavicle_offset, ws=1, matrix=clav_pos)
        cmds.parent(main_offset_grp, clavicle_control)

        # add attributes
        cmds.addAttr(main_control, ln="ScapulaPush", at="float", k=1)
        cmds.addAttr(main_control, ln="ShoulderFollow", at="float", dv=0.2, min=0, max=1, k=1)
        cmds.addAttr(main_control, ln="ScapulaFollow", at="float", dv=.5, min=0, max=1, k=1)

        # create scapula aim setup
        scap_setup_grp = cmds.group(n=i+"_Scapula_Setup_Grp", p=main_control_grp, em=1)
        origin_loc = cmds.spaceLocator(n=scapula.replace("Bnd_Jnt", "Origin_Loc"))
        aim_loc = cmds.spaceLocator(n=scapula.replace("Bnd_Jnt", "Aim_Loc"))
        insertion_loc = cmds.spaceLocator(n=scapula.replace("Bnd_Jnt", "Insertion_Loc"))
        cmds.xform(origin_loc, ws=1, matrix=hip_pos)
        cmds.xform(aim_loc, ws=1, matrix=scapula_pos)
        cmds.xform(insertion_loc, ws=1, matrix=scapula_pos)
        cmds.aimConstraint(aim_loc, origin_loc, aimVector=[0, 1, 0], worldUpVector=[0, 1, 0])
        to_del = cmds.aimConstraint(origin_loc, insertion_loc, aimVector=[0, -1, 0], worldUpVector=[0, 1, 0])
        cmds.pointConstraint(hip_pivot_control, origin_loc, mo=1)
        cmds.parent(origin_loc, aim_loc, scap_setup_grp)
        cmds.parent(insertion_loc, origin_loc)
        cmds.delete(to_del)

        scap_new_pos = cmds.xform(insertion_loc, q=1, ws=1, matrix=1)
        cmds.xform(scap_offset, ws=1, matrix=scap_new_pos)
        cmds.xform(scap_aim_offset, ws=1, matrix=scap_new_pos)
        cmds.setAttr(scap_aim_grp + ".ty", 2)
        cmds.parent(scap_offset, clavicle_control)

        cmds.connectAttr(main_control + ".ScapulaPush", insertion_loc[0] + ".ty")
        scap_parent = cmds.parentConstraint(insertion_loc, scap_offset, mo=1)
        cmds.parentConstraint(clavicle_control, scap_offset, mo=1)
        cmds.parentConstraint(scap_control, scapula, mo=1)
        cmds.parentConstraint(clavicle_control, clavicle, mo=1)
        cmds.parentConstraint(scap_aim_control, aim_loc, mo=1)
        #cmds.parentConstraint(knee_bnd, carpusIK_offset, mo=1)

        # connect foot to hip follow attribute
        hip_mult = cmds.createNode("multiplyDivide", n=main_control.replace("_Ctrl", "_Follow_Mdn"))
        hip_negate = cmds.createNode("multiplyDivide", n=main_control.replace("_Ctrl", "_Negate_Mdn"))
        hip_pma = cmds.createNode("plusMinusAverage", n=main_control.replace("_Ctrl", "_Follow_Pma"))

        # connect attrs from the hip control to specific transforms pivots
        for x in "XYZ":
            cmds.connectAttr(main_control + ".ShoulderFollow", hip_mult + ".input1" + x)
        cmds.connectAttr(ankle_control[0] + ".t", hip_pma + ".input3D[0]")
        cmds.connectAttr(ankle_control[1] + ".t", hip_pma + ".input3D[1]")
        cmds.connectAttr(hip_pma + ".output3D", hip_mult + ".input2")
        cmds.connectAttr(hip_mult + ".output", hip_negate + ".input1")
        cmds.connectAttr(hip_negate + ".output", clavicle_grp + ".t")

        if i =='R':
            hip_rev = cmds.createNode("multiplyDivide", n=main_control.replace("_Ctrl", "_Reverse_Mda"))
            cmds.connectAttr(hip_negate+'.output', hip_rev+'.input1')
            cmds.setAttr(hip_rev+'.input2Y', -1)
            cmds.setAttr(hip_rev+'.input2Y', -1)
            cmds.connectAttr(hip_rev+'.output', clavicle_grp + ".t", force=True)

        '''
        cmds.parentConstraint(ankle_control[1], clavicle_offset, maintainOffset=True)
        cmds.parentConstraint(main_control_grp, clavicle_offset, maintainOffset=True)
        cmds.connectAttr(main_control + ".ShoulderFollow", clavicle_offset + "._pointConstraint1.{}W0".format(ankle_control[1]))
        cmds.connectAttr(main_control + ".ShoulderFollow", clavicle_offset + "._pointConstraint1.{}W1".format(main_control_grp))
        '''

        cmds.connectAttr(main_control + ".ScapulaFollow", scap_parent[0] + ".{}W0".format(insertion_loc[0]))
        scap_follow_rev = cmds.createNode("reverse", n=scap_control.replace("_Ctrl", "_Follow_Rev"))
        cmds.connectAttr(main_control + ".ScapulaFollow", scap_follow_rev + ".inputX")
        cmds.connectAttr(scap_follow_rev + ".outputX", scap_parent[0] + ".{}W1".format(clavicle_control))

        '''
        # intergate the carpus joint setup
        carpus_offset_grp = cmds.joint(n=carpus.replace("Carpus_Bnd_Jnt", "Bottom_Offset"))
        cmds.select(cl=1)
        carpus_top_offset_grp = cmds.joint(n=carpus.replace("Carpus_Bnd_Jnt", "Top_Offset"))
        cmds.select(cl=1)
        
        # turn off their draw style as we dont need to see them
        cmds.setAttr(carpus_offset_grp + ".drawStyle", 2)
        cmds.setAttr(carpus_top_offset_grp + ".drawStyle", 2)
        
        # reorganise hierarchy to arrange pivots for the insertion of the new Carpus joint
        cmds.xform(carpus, ws=1, matrix=carpus_pos)
        cmds.parent(carpus_offset_grp, carpus)
        cmds.xform(carpus_offset_grp, ws=1, matrix=knee_pos)
        cmds.xform(carpus_top_offset_grp, ws=1, matrix=ankle_pos)
        cmds.parent(carpus_top_offset_grp, knee_bnd)
        cmds.parent(carpus, carpus_top_offset_grp)
        cmds.parent(ankle_bind, carpus_offset_grp)
    
        # set this to avoid right leg being misaligned 
        if i == "R":
            cmds.setAttr(carpus + ".jointOrientX", cmds.getAttr(carpus + ".jointOrientX") + 180)
            cmds.setAttr(hig_negate + ".input2Y", -1)
            cmds.setAttr(hig_negate + ".input2Z", -1)
        
        cmds.parent(carpusFK_offset, kneeFk_Control)
        cmds.parent(ankleFk_Offset, carpusFK_control)
        cmds.connectAttr(carpusIK_control + ".r", carpus + ".r")
        
        Or_con = [x for x in cmds.listConnections(knee_Fk_space_switch, s=1) if "Orient" in x]
        if Or_con:
            cmds.delete(Or_con)
        cmds.orientConstraint(carpusFK_control, knee_Fk_space_switch, mo=1)
        
        # connect IKFK switch
        rev = cmds.createNode("reverse")
        cmds.connectAttr(main_switch_control + ".FKIKSwitch", carpusIK_offset + ".v")
        cmds.connectAttr(main_switch_control + ".FKIKSwitch", rev + ".inputX")
        cmds.connectAttr(rev + ".outputX", carpusFK_offset + ".v")
        
        '''
    if cmds.objExists('forearm_guides_Grp'):
        cmds.delete('forearm_guides_Grp')

    print("")
    print("---------- ADDITIONAL FOREARM COMPONENTS COMPLETE --------")

# addtional functions not added by desirable:
# control for ankle and ball in IK










