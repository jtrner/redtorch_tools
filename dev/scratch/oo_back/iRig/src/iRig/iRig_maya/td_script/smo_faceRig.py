import maya.cmds as mc
from functools import partial

#face template setup

#hide base joint style
def hide_base_style(style, *args):
    joints_hide = ['Jaw', 'Md_Lip', 'Upr_Lip', 'Lwr_Lip', 'BrowRoot', 'Skull', 'L_EyeSocket', 'R_EyeSocket', 'FaceBender']
    for jnt in joints_hide:
        mc.setAttr(jnt + '.drawStyle', style)    

#hide right jnts
def hide_right_joints(*args):
    vis_check = mc.getAttr('R_Cheek.visibility')
    joints_right = mc.ls('R_*', type='joint')
    if vis_check == True:        
        mc.hide(joints_right)
    else:
        mc.showHidden(joints_right)        
        
#move joints into position (base mesh)
def setup_joints(*args):
    bbx = mc.xform('*:*L_Eye_Geo', q=True, bb=True, ws=True)
    centerX = (bbx[0] + bbx[3]) / 2.0
    centerY = (bbx[1] + bbx[4]) / 2.0
    centerZ = (bbx[2] + bbx[5]) / 2.0
            
    mc.xform('Skull', t=[0, centerY, centerZ - 3] ,ws=True)
    mc.xform('Tounge_01', t=[0, centerY -10, centerZ + 7] ,ws=True)
    mc.xform('L_EyeSocket', t=[centerX + 1, centerY, centerZ + 5] ,ws=True)
    
    #resize template joints  
    #def resize_joints(*args):  
    joints_all = mc.ls(type='joint')
    joints_noChange = ['BrowRoot', 'FaceBender', 'Jaw', 'L_EyeSocket', 'Lwr_Lip', 'Md_Lip', 'R_EyeSocket', 'Skull', 'Upr_Lip'] 
    joints_brow = ['L_Brow_Extra_01', 'L_Brow_Extra_02', 'L_Brow_Extra_03', 'L_Brow_Extra_04', 'R_Brow_Extra_01', 'R_Brow_Extra_02', 'R_Brow_Extra_03', 'R_Brow_Extra_04']
    joints_cheek = ['L_Cheek', 'R_Cheek']
     
    joints_leftover = [] 
    for each in joints_all:
        if not each in (joints_noChange + joints_brow): 
            joints_leftover.append(each)   
    
    for jnt in joints_leftover:
        mc.setAttr(jnt +'.radius', 0.5)
    for jnt in joints_brow:
        mc.setAttr(jnt +'.radius', 0.25)    
    for jnt in joints_cheek:
        mc.setAttr(jnt +'.radius', 1) 

#For mirroring Face Joints#
def mirror_joints(*args):
    joints= mc.ls('L_*',type='joint')
    for jnt in joints :
        tr=mc.xform(jnt,q=1,os=1,t=1)
        rot=mc.xform(jnt,q=1,os=1,ro=1)
        mc.xform( jnt .replace('L_','R_'),os=1,t=[-tr[0],tr[1],tr[2]],ro=[rot[0],-rot[1],-rot[2]])

#Post-build setup#
def scale_ctrls():
    tongue_ctrls = ['Tounge_Fk_06_Ctrl', 'Tounge_Fk_05_Ctrl', 'Tounge_Fk_04_Ctrl', 'Tounge_Fk_03_Ctrl', 'Tounge_Fk_02_Ctrl', 'Tounge_Fk_01_Ctrl', 'Tounge_Root_Ctrl']
    tongue_ctrls = mc.ls(tongue_ctrls, long=True)
    for each in tongue_ctrls:
        cv = each + '.cv[*]'
        mc.scale(0.5, 0.5, 0.5, cv, objectCenterPivot=True, r=True )
    
    ctrl_all = mc.ls('*Ctrl', long=True)    
    ctrl = [i for i in ctrl_all if not 'Facial_Ctrl' in i]
    ctrl = [i for i in ctrl if not 'Tounge' in i]
    
    extra_ctrls = ['L_EyeSocket_Ctrl', 'R_EyeSocket_Ctrl', 'Skull_Ctrl', 'FaceBender_Ctrl', 'Jaw_Ctrl', 'Md_Lip_Ctrl', 'Upr_Lip_Ctrl', 'Lwr_Lip_Ctrl']
    extra_ctrls = mc.ls(extra_ctrls, long=True)
    
    for i in extra_ctrls:
        if i in ctrl:
            ctrl.remove(i)
    
    for i in ctrl:
        loc = mc.xform(i, q=True, ws=True, rp=True)
        shapes = mc.listRelatives(i, shapes=True)
        for shape in shapes:
            cv = shape + '.cv[*]'
            #mc.scale(2, 2, 2, cv, objectCenterPivot=True, r=True )  
            if "Brow_Extra" in shape:
                mc.scaleComponents(4, 4, 4, cv, pivot=loc ) 
            elif "Brow" in shape:   
                mc.scaleComponents(3, 3, 3, cv, pivot=loc )              
            else:
                mc.scaleComponents(2, 2, 2, cv, pivot=loc )    


#colour curves on the panel and face rig
def colour_curves(side=''):
    
    joints= mc.ls('L_*',type='joint')
    
    curves_side_all = mc.ls(side, type='nurbsCurve')
    curves_transform = []
    for curves in curves_side_all:
        if not curves in curves_transform:
            #parent = mc.listRelatives( curves, parent=True )
            curves_transform.append( curves )            
    
    curves_side = []
    for curves in curves_transform:
        if mc.getAttr(curves + '.overrideDisplayType') == 0:
            curves_side.append(curves)
    
    for curves in curves_side:
        if side == 'L_*':
            mc.setAttr(curves +'.overrideColor', 14) 
        elif side == 'R_*':
            mc.setAttr(curves +'.overrideColor', 13) 
 
def group_ctrls():
    temp_ctrls_all = mc.ls('Temp*', type='transform')
    temp_ctrls = []
    for i in temp_ctrls_all:
        parent_check = mc.listRelatives(i, parent=True)
        if not parent_check:
            temp_ctrls.append(i)
    
    offset_group = mc.group(temp_ctrls, n='Panel_Shape_Label_Offset_GRP')
    move_group = mc.group(temp_ctrls, n='Panel_Shape_Label_Move_GRP')
    mc.parent(offset_group, 'Facial_Ctrl')  
    mc.select(cl=True)
    mc.move(-2, 19, 0, offset_group)    
    mc.scale(2, 2, 2, offset_group)
    mc.setAttr(move_group +'.translate', 8, 4, 5)  
    
def setup_ctrls(*args):
    colour_curves(side='L_*')
    colour_curves(side='R_*')
    scale_ctrls()
    group_ctrls()
    mc.currentTime(-84)

def sel_bind_jnts(*args):
    joints_all = mc.ls(type='joint')
    joints_no_bind = ['BrowRoot', 'FaceBender', 'L_EyeSocket', 'Lwr_Lip', 'Md_Lip', 'R_EyeSocket', 'Upr_Lip', 'Lwr_Teeth', 'Upr_Teeth'] 
    joints_tongue = ['Tounge_01_Bnd', 'Tounge_02_Bnd', 'Tounge_03_Bnd', 'Tounge_04_Bnd', 'Tounge_05_Bnd', 'Tounge_06_Bnd', 
                    'Tounge_07_Bnd', 'Tounge_Base_Bnd', 'Tounge_Tip_Bnd']
        
    joints_leftover = [] 
    for each in joints_all:
        if not each in (joints_no_bind + joints_tongue): 
            if not 'Driver' in each and not 'Drv' in each:
                joints_leftover.append(each)
     
    mc.select(joints_leftover, r=True)   

def smo_faceRig_window():
    # window creation
    if mc.window("faceWin", ex=True) == True:
        mc.deleteUI("faceWin")

    mc.window("faceWin", t="SMO Face Setup", w=300)
    mc.columnLayout(adj=True, rowSpacing=4)
    mc.text('-------------------------- Face Rig Setup --------------------------', font="boldLabelFont")
    mc.text('1. "Face Template - SMO" from Face Icon on Panel', font="boldLabelFont")
    mc.button("setupJoints", l="2. Set Up Joints", h=50, c=setup_joints, backgroundColor=(0.3, 0.7, 0.5))
    mc.text('3. Position joints manually', font="boldLabelFont")
    mc.button("mirrorJoints", l="4. Mirror Joints", h=50, c=mirror_joints, backgroundColor=(0.3, 0.7, 0.5))
    mc.text('5. "Build Watson Face" from Face Icon on Panel', font="boldLabelFont")
    mc.text('------------------------ Face Rig Post-Build -----------------------', font="boldLabelFont")
    mc.button("setupCtrls", l="6. Set Up Controls", h=50, c=setup_ctrls, backgroundColor=(0.3, 0.7, 0.5))
    mc.text('7. "Control Scale Up" from Face Icon on Panel', font="boldLabelFont")
    mc.button("selBindJnts", l="8. Select Bind Joints", h=50, c=sel_bind_jnts, backgroundColor=(0.3, 0.7, 0.5))
    mc.text('9. Bind face geo to joints', font="boldLabelFont")
    mc.text('10. Import Face animation clip', font="boldLabelFont")
    mc.text('11. Paint weights + Create shapes', font="boldLabelFont")
    mc.text('-------------------------------------------------------------------------', font="boldLabelFont")
    mc.text('--------------------------- Template Tools --------------------------', font="boldLabelFont")
    mc.button("toggleRight", l="Toggle Vis - Right Joints", h=50, c=hide_right_joints)
    mc.text('Style of Joints')
    mc.rowLayout(adj=True, nc=3)
    mc.button("boneStyle", l="Joint - Bones", h=50, command=partial(hide_base_style, 0))
    mc.button("boxStyle", l="Joint - Box", h=50, command=partial(hide_base_style, 1))
    mc.button("hiddenStyle", l="Joint - Hidden", h=50, command=partial(hide_base_style, 2))
    mc.setParent("..")
    mc.setParent("..")
    mc.showWindow("faceWin")