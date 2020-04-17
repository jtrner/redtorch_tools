import pymel.core as pm
import maya.cmds as cmds


def do_it():
    for side in ['L', 'R']:
        for end in ['Upr', 'Lwr']:

            ctrl = 'Face_'+side+'_Eye_Lid_'+end+'_Ctrl'
            tfm = 'Face_'+side+'_Eye_Lid_'+end+'_Ctrl_AutoFollow_Tfm'
            anm = 'Face_'+side+'_Eye_Lid_'+end+'_Rot_Mid_Anm'
            remap = 'Face_'+side+'_Eye_Lid_'+end+'_Ctrl_AutoFollow_Remap'

            if not cmds.objExists(remap):
                cmds.shadingNode('remapValue', asUtility=True, name=remap)
                if end=='Lwr':
                    cmds.setAttr(remap+'.outputMin', -45)
                    cmds.setAttr(remap+'.outputMax', 45)
                else:
                    cmds.setAttr(remap+'.outputMin', 45)
                    cmds.setAttr(remap+'.outputMax', -45)
                cmds.setAttr(remap+'.inputMin', -.5)
                cmds.setAttr(remap+'.inputMax', .5)
                cmds.connectAttr(ctrl+'.translateX', remap+'.inputValue', force=True)
                cmds.connectAttr(remap+'.outColorR', tfm+'.rotateZ', force=True)

        if cmds.objExists(anm):
            cmds.delete(anm)



    for end in ['Upr', 'Lwr']:
        side = 'C'
        ctrl = 'Face_'+side+'_Mouth_Lip'+end+'_Move_Ctrl'
        tfm = 'Face_'+side+'_Mouth_Lip'+end+'_Move_Ctrl_AutoFollow_Tfm'
        anm = 'Face_'+side+'_Mouth_Lip'+end+'_Move_Rot_Mid_Anm'
        remap = 'Face_'+side+'_Mouth_Lip'+end+'_Move_Ctrl_AutoFollow_Remap'

        if not cmds.objExists(remap):
            cmds.shadingNode('remapValue', asUtility=True, name=remap)
            if end=='Lwr':
                cmds.setAttr(remap+'.outputMin', -45)
                cmds.setAttr(remap+'.outputMax', 45)
            else:
                cmds.setAttr(remap+'.outputMin', 45)
                cmds.setAttr(remap+'.outputMax', -45)
            cmds.setAttr(remap+'.inputMin', -.5)
            cmds.setAttr(remap+'.inputMax', .5)
            cmds.connectAttr(ctrl+'.translateX', remap+'.inputValue', force=True)
            cmds.connectAttr(remap+'.outColorR', tfm+'.rotateZ', force=True)

        if cmds.objExists(anm):
            cmds.delete(anm)

