#Lock Asset SMO
import maya.cmds as cmds

def do_it(): 
    type = ['Character', 'Prop', 'Set', 'Vehicle']
    
    asset = []
    for i in type:
        if cmds.ls(i):
            asset.append(i)
        
    if len(asset) == 1:
        asset = asset[0]
        
    attrs = cmds.listAttr(asset)
    
    if "ProxyVis" in attrs:
        cmds.setAttr(asset +".ProxyVis", 0)
    if "GeoVis" in attrs:
        cmds.setAttr(asset +".GeoVis", 1)
    if "GeoLock" in attrs:
        cmds.setAttr(asset +".GeoLock", 2)
    if "CtrlVis" in attrs:
        cmds.setAttr(asset +".CtrlVis", 1)
    if "JointVis" in attrs:
        cmds.setAttr(asset +".JointVis", 0)
    if "UtilityVis" in attrs:
        cmds.setAttr(asset +".UtilityVis", 0)

    if "PinkHelperVis" in attrs:
        cmds.setAttr(asset +".PinkHelperVis", 1)
    if "HelperVis" in attrs:
        cmds.setAttr(asset +".HelperVis", 1)
        
    if asset == 'Character':
        try:
            cmds.setAttr('Eye_Root_Ctrl.TextureResolution', 0)
        except:
            cmds.setAttr('Eye_Root_Ctrl.Texture_Resolution', 0)
        finally:
            pass              

    dyn = cmds.listRelatives(asset)    
    if "Dynamic_Grp" in dyn:
        if "DynamicVis" in attrs:
            cmds.setAttr(asset +".DynamicVis", 0)
        cmds.setAttr("Dynamic_Ctrl.DynamicsOnOff", 0)