__author__ = 'stevenb'

import icon_api.utils as i_utils
import maya.cmds as cmds
import rig_tools.frankenstein.utils as rig_frankenstein_utils
import icon_api.node as i_node

def reset():
    for each in cmds.ls(sl=1):
        for i in ['.tx','.ty','.tz','.rx','.ry','.rz']:
            attr = cmds.getAttr(each+'_Drv_Grp'+i)
            if attr != 0:
                cmds.setAttr(each+i,(attr*-1))
        for s in ['.sx','.sy','.sz']:
            attr = cmds.getAttr(each+'_Drv_Grp'+s)
            if attr != 1:
                cmds.setAttr(each+s,(1/attr))


def eyeFix():
    for lid in ['Upr_','Lwr_']:
        for each in ['In','Mid','Out']:
            cmds.parent('Face_R_Eye_Lid_'+lid+each+'_Ctrl_AutoFollow_Tfm',w=1)
        cmds.setAttr('Face_R_Eye_Lid_'+lid+'Ctrl_Offset_Grp.ry',180)
        for each in ['In','Mid','Out']:
            cmds.parent('Face_R_Eye_Lid_'+lid+each+'_Ctrl_AutoFollow_Tfm','Face_R_Eye_Lid_'+lid+'Ctrl_AutoFollow_Tfm')


def popFix():
    for each in cmds.ls('*Tweak*Anm'):
        my_key = cmds.keyframe(each, q=True, floatChange = True)
        if len(my_key) > 2:
            for key_val in my_key:
                true_keys = []
                for key_correct in [0.0,0.25,0.5,0.75,1.0]:
                    if key_val == key_correct:
                        true_keys.append(key_val)
                if true_keys == []:
                    cmds.cutKey(each,f=(key_val,key_val))

# Fix on Export Face Anim Curve Out of Range Error
def exportFix():
    # Find all the blend nodes
    selected = cmds.ls(sl=False, type='blendWeighted')

    # Remove the blend nodes that have no output
    for s in selected:
        if cmds.listConnections(s, source=False, skipConversionNodes=True):
            if len(cmds.listConnections(s, source=False, skipConversionNodes=True))==1 and cmds.listConnections(s, source=False, skipConversionNodes=True)[0]=='MayaNodeEditorSavedTabsInfo':
                cmds.delete(s)
        else:
            cmds.delete(s)

# selects all animcurves and tags them for export:
def exportTag():
    exportFix()

    manual_nodes = cmds.ls('*Tweak*Anm')
    manual_nodes_cnv = i_utils.convert_data(manual_nodes, to_generic=False)
    face_pack_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type": "Face"})
    i_node.connect_to_info_node(node=face_pack_info_node[0], info_attribute="build_objects", objects=manual_nodes_cnv)


def defaultClean():
    for animCurve in cmds.ls('*Tweak*Anm'):
        cmds.keyframe (animCurve,option='over', index=(0,0), absolute=1, valueChange = 0)


def forceMirror():
    driveAttrsDict = {}
    temp = 0

    #Find Driver attr percentages
    for faceDriver in cmds.listRelatives('Face_ControlDriver_Grp'):
        triggered_attrs = []
        faceDriver_attrs = cmds.listAttr(faceDriver,ud=1)
        for faceAttr in faceDriver_attrs:
            atQ = round(cmds.getAttr(faceDriver+'.'+faceAttr),3)
            if atQ != 0.0:
                if 'assetID' not in faceAttr:
                    if 'objectID' not in faceAttr:
                        if 'R_' not in faceAttr:
                            triggered_attrs.append(faceAttr)
        portion = 0
        for trigAttrs in triggered_attrs:
            atQ = cmds.getAttr(faceDriver+'.'+trigAttrs)
            portion = portion + float(atQ)
        for trigAttrs in triggered_attrs:
            atQ = cmds.getAttr(faceDriver+'.'+trigAttrs)
            per = atQ/portion
            driveAttrsDict[str(trigAttrs)] = round(per,3)
            if temp == 1:
                if 'L_' in trigAttrs:
                    Rat = cmds.getAttr(faceDriver+'.'+trigAttrs.replace('L_','R_'))
                    if Rat == atQ:
                        driveAttrsDict[str(trigAttrs.replace('L_','R_'))] = round(per,3)
                if 'Left' in trigAttrs:
                    driveAttrsDict[str(trigAttrs.replace('Left','Right'))] = round(per,3)

    for each_driver,init_percent in driveAttrsDict.iteritems():
        mirror_driver = None
        if 'Left' in each_driver:
            mirror_driver = each_driver.replace('Left','Right')
        if 'L_' in each_driver:
            mirror_driver = each_driver.replace('L_','R_')
        Anm_effected = cmds.ls(each_driver + '*Tweak*Anm')
        for animCurve in Anm_effected:
            my_key = cmds.keyframe(animCurve, q=True, valueChange = True)
            mirror_Val = 1
            for any in ['transX', 'rotY', 'rotZ']:
                if any in animCurve:
                    mirror_Val = -1
            R_curve = None
            if 'L_' in animCurve:
                R_curve = (animCurve.replace(each_driver, mirror_driver)).replace('L_','R_')
            elif 'R_' in animCurve:
                R_curve = (animCurve.replace(each_driver, mirror_driver)).replace('R_','L_')
            else:
                R_curve = animCurve.replace(each_driver, mirror_driver)
            for a in range(1, len(my_key)):
                if R_curve != None:
                    cmds.keyframe(R_curve, option='over', index=(a,a), absolute=1, valueChange = my_key[a]*mirror_Val)



def mirrorMovementOn():
    #mirror functionality of TOTS face panel controls for use during setup

    attrs = [".translateX", ".translateY", ".translateZ", ".rotateX", ".rotateY", ".rotateZ"]

    faceLeftCtrls = ['Face_L_Mouth_LipLwr_Ctrl', 'Face_L_Mouth_Corner_Ctrl', 'Face_L_Mouth_CornerPinch_Ctrl', 'Face_L_Mouth_LipUpr_Ctrl', 'Face_L_Cheek_Ctrl', 'Face_L_Squint_Ctrl', 'Face_L_Nostril_Ctrl', 'Face_L_Eye_Lid_Lwr_Out_Ctrl', 'Face_L_Eye_Lid_Lwr_In_Ctrl', 'Face_L_Eye_Lid_Lwr_Mid_Ctrl', 'Face_L_Eye_Lid_Upr_Mid_Ctrl', 'Face_L_Eye_Lid_Upr_In_Ctrl', 'Face_L_Eye_Lid_Upr_Out_Ctrl', 'Face_L_Brow_In_Ctrl', 'Face_L_Brow_Mid_Ctrl', 'Face_L_Brow_Out_Ctrl']

    for c in faceLeftCtrls:
        if cmds.objExists(c):
            rightCtrl = c.replace("_L_", "_R_")
            for a in attrs:
                if cmds.getAttr(c+a, lock=True) == False:
                    incoming = cmds.listConnections(rightCtrl+a, destination=False, source=True)
                    if incoming:
                        if incoming[0] != c:
                            cmds.connectAttr(c+a, rightCtrl+a, force=True)
                    else:
                        cmds.connectAttr(c+a, rightCtrl+a, force=True)



def mirrorMovementOff():
    #break mirror functionality of TOTS face panel controls for use during setup

    attrs = [".translateX", ".translateY", ".translateZ", ".rotateX", ".rotateY", ".rotateZ"]

    faceLeftCtrls = ['Face_L_Mouth_LipLwr_Ctrl', 'Face_L_Mouth_Corner_Ctrl', 'Face_L_Mouth_CornerPinch_Ctrl', 'Face_L_Mouth_LipUpr_Ctrl', 'Face_L_Cheek_Ctrl', 'Face_L_Squint_Ctrl', 'Face_L_Nostril_Ctrl', 'Face_L_Eye_Lid_Lwr_Out_Ctrl', 'Face_L_Eye_Lid_Lwr_In_Ctrl', 'Face_L_Eye_Lid_Lwr_Mid_Ctrl', 'Face_L_Eye_Lid_Upr_Mid_Ctrl', 'Face_L_Eye_Lid_Upr_In_Ctrl', 'Face_L_Eye_Lid_Upr_Out_Ctrl', 'Face_L_Brow_In_Ctrl', 'Face_L_Brow_Mid_Ctrl', 'Face_L_Brow_Out_Ctrl']

    for c in faceLeftCtrls:
        if cmds.objExists(c):
            rightCtrl = c.replace("_L_", "_R_")
            for a in attrs:
                if cmds.getAttr(c+a, lock=True) == False:
                    incoming = cmds.listConnections(rightCtrl+a, destination=False, source=True)
                    if incoming:
                        if incoming[0] == c:
                            cmds.disconnectAttr(c+a, rightCtrl+a)




def bake():

    driveAttrsDict = {}
    conAttrsDict = {}

    #Find Driver attr percentages
    for faceDriver in cmds.listRelatives('Face_ControlDriver_Grp'):
        triggered_attrs = []
        faceDriver_attrs = cmds.listAttr(faceDriver,ud=1)
        for faceAttr in faceDriver_attrs:
            atQ = round(cmds.getAttr(faceDriver+'.'+faceAttr),3)
            if atQ != 0.0:
                if 'assetID' not in faceAttr:
                    if 'objectID' not in faceAttr:
                        if 'R_' not in faceAttr:
                            triggered_attrs.append(faceAttr)
        portion = 0
        for trigAttrs in triggered_attrs:
            atQ = cmds.getAttr(faceDriver+'.'+trigAttrs)
            portion = portion + float(atQ)
        for trigAttrs in triggered_attrs:
            atQ = cmds.getAttr(faceDriver+'.'+trigAttrs)
            per = atQ/portion
            driveAttrsDict[str(trigAttrs)] = round(per,3)
            if 'L_' in trigAttrs:
                Rat = cmds.getAttr(faceDriver+'.'+trigAttrs.replace('L_','R_'))
                if Rat == atQ:
                    driveAttrsDict[str(trigAttrs.replace('L_','R_'))] = round(per,3)
            if 'Left' in trigAttrs:
                driveAttrsDict[str(trigAttrs.replace('Left','Right'))] = round(per,3)
    #Find control attr values
    controls = []
    driven = cmds.listRelatives('Face_Ctrl_Grp',ad=1,type='transform')
    for child in driven:
        if cmds.objExists(child + '?Shape'):
            controls.append(child)
    triggered_controls = []
    for each_con in controls:
        if 'L_' not in each_con:
            if 'R_' not in each_con:
                if 'C_' not in each_con:
                    print each_con
        Vals = []
        for con_attr in ['.tx','.ty','.tz','.rx','.ry','.rz']:
            attrVal = round(cmds.getAttr(each_con+con_attr),3)
            if attrVal != 0.0:
                Vals.append(attrVal)
        for con_attr in ['.sx','.sy','.sz']:
            attrVal = round(cmds.getAttr(each_con+con_attr),3)
            if attrVal != 1.0:
                Vals.append(attrVal)
        if Vals != []:
            triggered_controls.append(each_con)
    for trigCon in triggered_controls:
        attrVals = []
        driveLoc = cmds.spaceLocator(n='driveX')
        ctrlLoc = cmds.spaceLocator(n='ctrlX')
        par1 = cmds.parentConstraint(trigCon.replace('Ctrl','Ctrl_Drv_Grp'),driveLoc)
        par2 = cmds.parentConstraint(trigCon,ctrlLoc)
        cmds.delete(par1)
        cmds.delete(par2)
        parentCtrl = cmds.listRelatives(cmds.listRelatives(cmds.listRelatives(trigCon,p=1)[0],p=1)[0],p=1)[0]
        parentLoc = None
        if 'Ctrl' in parentCtrl:
            parentLoc = cmds.spaceLocator(n='parX')[0]
            par3 = cmds.parentConstraint(parentCtrl,parentLoc)
            par4 = cmds.scaleConstraint(parentCtrl,parentLoc)
            cmds.delete(par3)
            cmds.delete(par4)
            cmds.parent(driveLoc,parentLoc)
            cmds.parent(ctrlLoc,parentLoc)
        driveTX = cmds.xform(driveLoc,q=1,t=1)
        ctrlTX = cmds.xform(ctrlLoc,q=1,t=1)
        driveRX = cmds.xform(driveLoc,q=1,ro=1)
        ctrlRX = cmds.xform(ctrlLoc,q=1,ro=1)
        cmds.delete(driveLoc)
        cmds.delete(ctrlLoc)
        if parentLoc != None:
            cmds.delete(parentLoc)
        for X in [[driveTX,ctrlTX],[driveRX,ctrlRX]]:
            for i in [0,1,2]:
                attrVal = round(X[1][i],3) - round(X[0][i],3)
                attrVals.append(round(attrVal,3))
        for trigAttr in ['.sx','.sy','.sz']:
            attrVal = round(cmds.getAttr(trigCon+trigAttr),3)
            attrVals.append(attrVal)
        conAttrsDict[str(trigCon)] = attrVals

    print driveAttrsDict
    print conAttrsDict

    #Bake
    for each_driver,init_percent in driveAttrsDict.iteritems():
        for each_control,these_values in conAttrsDict.iteritems():
            my_drivers = [each_driver]
            my_controls = [each_control]
            if 'L_' in each_control:
                my_controls = [each_control,each_control.replace('L_','R_')]
            if 'R_' in each_control:
                my_controls = None
            invert = False
            Rinvert = True
            this_percent = init_percent
            if 'L_' in each_driver:
                if 'L_' in each_control:
                    my_controls = [each_control,each_control.replace('L_','R_')]
                    Rinvert = True
                if 'R_' in each_control:
                    my_controls = None
                if not 'L_' in each_control:
                    if not 'R_' in each_control:
                        my_controls = [each_control]
                        this_percent = init_percent*0.5
                        my_drivers = [each_driver,each_driver.replace('L_','R_')]
            if 'R_' in each_driver:
                my_controls = None
            if 'Left' in each_driver:
                my_controls = [each_control]
                Rinvert = False
            if 'Right' in each_driver:
                Rinvert = False
                if 'L_' in each_control:
                    my_controls = [each_control.replace('L_','R_')]
                    invert = True
                if 'R_' in each_control:
                    my_controls = [each_control.replace('R_','L_')]
                    invert = True
                if not 'L_' in each_control:
                    if not 'R_' in each_control:
                        my_controls = [each_control]
                        invert = True
            if my_controls != None:
                for this_driver in my_drivers:
                    for driverCheck in cmds.listRelatives('Face_ControlDriver_Grp'):
                        if cmds.objExists(driverCheck + '.' + this_driver):
                            faceDriver = driverCheck
                    for this_control in my_controls:
                        if invert == True:
                            inv = -1
                        if invert == False:
                            inv = 1
                        if Rinvert == True:
                            if 'R_' in this_control:
                                this_driver = this_driver.replace('L_','R_')
                                inv = -1
                        valsDict = {'.translateX':round(these_values[0]*this_percent*inv,3),'.translateY':round(these_values[1]*this_percent,3),'.translateZ':round(these_values[2]*this_percent,3),
                        '.rotateX':round(these_values[3]*this_percent,3),'.rotateY':round(these_values[4]*this_percent*inv,3),'.rotateZ':round(these_values[5]*this_percent*inv,3),
                        '.scaleX':round((these_values[6]-1)*this_percent,3),'.scaleY':round((these_values[7]-1)*this_percent,3),'.scaleZ':round((these_values[8]-1)*this_percent,3)}
                        for this_attr,this_value in valsDict.iteritems():
                            if 'trans' or 'rot' in this_attr:
                                spec_val = 0.0
                            if 'scale' in this_attr:
                                spec_val = 1.0
                            if this_value != 0.0:
                                driven_null = this_control.replace('Ctrl','Ctrl_Drv_Grp')+this_attr
                                connector = cmds.listConnections(driven_null,scn=1)
                                if connector != None:
                                    connector = connector[0]
                                    animCurve = this_driver + '_to_' + connector.replace('_Blend','_Anm')
                                    myIndex = round(cmds.getAttr(faceDriver+'.'+this_driver),3)
                                    if myIndex == 0.0:
                                        try:
                                            myIndex = round(cmds.getAttr(faceDriver+'.'+this_driver.replace('Right','Left')),3)
                                        except:
                                            pass
                                    if cmds.objExists(animCurve) == True:
                                        for_key = cmds.listConnections(animCurve+'.output',p=1)
                                        if not for_key:
                                            cmds.warning("[Face Bake Error] :: {} has no output.".format(animCurve))
                                            continue
                                        driverKeys = cmds.keyframe(animCurve, q=True, floatChange=True)
                                        driverDict = {}
                                        for i in range(len(driverKeys)):
                                            driverDict[i] = round(driverKeys[i],3)
                                        oldVal = 0.0
                                        indexReq = 0
                                        match = False
                                        for keyIndex,indexValue in driverDict.iteritems():
                                            if indexValue == myIndex:
                                                match = True
                                                indexReq = keyIndex
                                        if match == False:
                                            cmds.setKeyframe(for_key,f=myIndex)
                                            newKeys = cmds.keyframe(animCurve, q=True, floatChange=True)
                                            newDriverDict = {}
                                            for i in range(len(newKeys)):
                                                newDriverDict[i] = round(newKeys[i],3)
                                            for newKeyIndex,newIndexValue in newDriverDict.iteritems():
                                                if newIndexValue == myIndex:
                                                    indexReq = newKeyIndex
                                        my_key = cmds.keyframe (animCurve, q=True, valueChange = True)
                                        oldVal = round(my_key[indexReq],3)
                                        newVal = oldVal + this_value
                                        cmds.keyframe (animCurve,option='over', index=(indexReq,indexReq), absolute=1, valueChange = newVal)
                                        if match == False:
                                            cmds.keyTangent(animCurve,index=(indexReq,indexReq),inTangentType='linear',outTangentType='linear')
                                    if cmds.objExists(animCurve) == False:
                                        freshAnimCurve = cmds.createNode('animCurveUA',n=animCurve)
                                        cmds.connectAttr(faceDriver+'.'+this_driver,freshAnimCurve+'.input')
                                        cur = (cmds.getAttr(connector+'.current'))+1
                                        connectors = cmds.listConnections(connector,c=1)
                                        my_ins = []
                                        in_num = 0
                                        for conec in connectors:
                                            if 'input[' in conec:
                                                my_ins.append(conec)
                                        if my_ins != []:
                                            in_num = int(my_ins[-1].split('[')[-1].replace(']',''))+1
                                        new_inputBlend = connector+'.input['+str(in_num)+']'
                                        test = cmds.getAttr(new_inputBlend)
                                        if test != 0:
                                            new_inputBlend = connector+'.input['+str(in_num+1)+']'
                                        cmds.connectAttr(freshAnimCurve+'.output',new_inputBlend)
                                        cmds.setAttr(connector+'.current',cur)
                                        cmds.setKeyframe(new_inputBlend,f=0,v=0)
                                        cmds.setKeyframe(new_inputBlend,f=myIndex,v=this_value)
                                        cmds.keyTangent(freshAnimCurve,index=(0,0),inTangentType='linear',outTangentType='linear')
                                        cmds.keyTangent(freshAnimCurve,index=(1,1),inTangentType='linear',outTangentType='linear')
                                if connector == None:
                                    channel = this_attr.replace('.','')
                                    if 'trans' in this_attr:
                                        channel = channel.replace('translate','trans')
                                    if 'rot' in this_attr:
                                        channel = channel.replace('rotate','rot')
                                    cur = 3.0 + spec_val
                                    freshAnimCurve = cmds.createNode('animCurveUA',n=this_driver + '_to_' + this_control.replace('Ctrl',channel)+'_Anm')
                                    cmds.connectAttr(faceDriver+'.'+this_driver,freshAnimCurve+'.input')
                                    myIndex = round(cmds.getAttr(faceDriver+'.'+this_driver),3)
                                    if myIndex == 0.0:
                                        try:
                                            myIndex = round(cmds.getAttr(faceDriver+'.'+this_driver.replace('Right','Left')),3)
                                        except:
                                            pass
                                    cmds.setAttr(driven_null,l=0,k=1)
                                    freshBlend = cmds.createNode('blendWeighted',n=this_control.replace('Ctrl',channel)+'_Blend')
                                    cmds.setAttr(freshBlend+'.current',cur)
                                    init = '0'
                                    cmds.connectAttr(freshAnimCurve+'.output',freshBlend+'.input['+init+']')
                                    if 'scale' in this_attr:
                                        cmds.disconnectAttr(freshAnimCurve+'.output',freshBlend+'.input['+init+']')
                                        cmds.setAttr(freshBlend+'.input['+init+']',1)
                                        init = '1'
                                        cmds.connectAttr(freshAnimCurve+'.output',freshBlend+'.input['+init+']')
                                    cmds.connectAttr(freshBlend+'.output',driven_null)
                                    cmds.setKeyframe(freshBlend+'.input['+init+']',f=0,v=0)
                                    cmds.setKeyframe(freshBlend+'.input['+init+']',f=myIndex,v=this_value)
                                    cmds.keyTangent(freshAnimCurve,index=(0,0),inTangentType='linear',outTangentType='linear')
                                    cmds.keyTangent(freshAnimCurve,index=(1,1),inTangentType='linear',outTangentType='linear')
                                    cmds.setAttr(driven_null,l=1)
                            if not cmds.getAttr(this_control+this_attr, settable=True):  # AUTO-1453
                                print "OH NO!", this_control+this_attr, "is not settable. Cannot set it to", spec_val
                                continue
                            
                            cmds.setAttr(this_control+this_attr,spec_val)













