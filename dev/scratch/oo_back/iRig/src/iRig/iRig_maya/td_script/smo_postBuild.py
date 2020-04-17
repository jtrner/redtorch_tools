import maya.cmds as mc
import maya.mel as mel

def _getNamespace():
    """Get namespace of selection """

    selection = mc.ls("*:Geo")[0]
    name_space = selection.split(":")[0]

    return name_space

def blendshapeMesh():
    """Blendshape selected face geo into final mesh """

    selection = mc.ls(sl=1)

    for i in selection:
        if not "Ctrl" in i:
        
            original_geo = i.split(":")[1]
            driven_geo = [x for x in mc.ls("*:" + original_geo, type="transform") if i not in x]
            #driven_geo = [x for x in mc.listRelatives("HiRes_Geo_Grp", ad=1, type="transform") if ":" + original_geo in x]
            
            if driven_geo:
                if mc.objExists(original_geo + "_BSH"):
                    mc.rename(original_geo + "_BSH", original_geo + "_BSH" + "_OLD")

                bsp = mc.blendShape(i, driven_geo, n=original_geo + "_BSH", foc=1)[0]
                mc.setAttr(bsp + "." + original_geo, 1)
                print("- " + i + " SUCCESSFULLY BLENDSHAPED")
            else:
                continue

def organiseFaceRig():
    """Parent new groups from face and move face panel """

    name_space = _getNamespace()

    if mc.objExists(name_space + ":Geo"):
        if mc.objExists(name_space + ":Face_Grp"): 
            if name_space + ":Geo" not in mc.listRelatives("Character"):
                mc.parent(name_space + ":Geo", "Character")
            if name_space + ":Face_Grp" not in mc.listRelatives("Character"):
                mc.parent(name_space + ":Face_Grp", "Character")

    # move and parent face panel
    face_panel = name_space + ":Facial_Ctrl"
    if mc.objExists(face_panel):
        if not mc.objExists("Facial_Ctrl_Offset_Grp"):
            posT = mc.xform(face_panel, q=1, t=1)
            posR = mc.xform(face_panel, q=1, ro=1)
            posS = mc.xform(face_panel, q=1, s=1, r=1)

            if mc.getAttr(face_panel + ".tx") == 0:
                no_trans = 1
            else:
                no_trans = 0

            mc.xform(face_panel, t=[0, 0, 0], ro=[0, 0, 0], s=[1, 1, 1])

            offset_group = mc.group(face_panel, n="Facial_Ctrl_Offset_Grp")

            if no_trans == 0:
                mc.xform(offset_group, t=posT, ro=posR, s=posS)
            else:
                head_pos = mc.getAttr("Head_Bnd.ty")
                mc.setAttr(offset_group + ".ty", head_pos)
                mc.setAttr(offset_group + ".tx", head_pos * 2)
                mc.setAttr(name_space + ":Facial_Ctrl.FaceCtrls", 0)

            if not [x for x in mc.listRelatives("Control_Ctrl") if offset_group in x]:
                mc.parent(offset_group, "Control_Ctrl")

    if mc.objExists(name_space + ":Skull_Ctrl_Offset_Grp"):
        if not [x for x in mc.listRelatives("Head_Gimbal_Ctrl") if name_space + ":Skull_Ctrl_Offset_Grp" in x]:
            mc.parent(name_space + ":Skull_Ctrl_Offset_Grp", "Head_Gimbal_Ctrl")

    print("")
    print("- SUCCESSFULLY PARENTED FACE RIG")

def makeFaceVis():
    """Add no inherit group to hierarchy """

    name_space = _getNamespace()
    
    if not mc.objExists("Character.FaceVis"):
        mc.addAttr("Character", at="bool", ln="FaceVis", k=1)

    if mc.objExists(name_space + ":Geo"):
        if not mc.listConnections(name_space + ":Geo" + ".v"):
            mc.connectAttr("Character.FaceVis", name_space + ":Geo.v", f=1)

    if mc.objExists(name_space + ":Face_Grp"):
        if not mc.listConnections(name_space + ":Face_Grp.v"):
            mc.connectAttr("Character.FaceVis", name_space + ":Face_Grp.v", f=1)

def cleanup():
    """Put extra transforms brought in by the face into the utility group """

    name_space = _getNamespace()

    # check if geo group is already parented
    if mc.objExists(name_space + ":Geo"):
        if not [x for x in mc.listRelatives("Character") if name_space + ":Geo" in x]:
	        mc.parent(name_space + ":Geo", "Character")

    if mc.objExists("Head_Utl_Grp"):
        mc.delete("Head_Utl_Grp")

    to_hide = name_space + ":Panel_Shape_Label_Offset_GRP"
    if mc.objExists(to_hide):
        mc.hide(to_hide)

def noInheritGrp():
    """Add no inherit group to hierarchy """

    jnt_grp = "Jnt_Grp"

    if mc.objExists(jnt_grp):
        if not mc.objExists("No_Inherit_Grp"):
            grp = mc.group(n="No_Inherit_Grp", em=1, p=jnt_grp)
            mc.setAttr(grp + ".inheritsTransform", 0)

def renameGimbalAttrs():
    """Rename gimbal space switche attrs to work with old naming convention """

    controls = mc.ls("*Ctrl", type="transform")
    for i in controls:
        gimbal_attrs = [x for x in mc.listAttr(i) if "_Gimbal_" in x]
        for j in gimbal_attrs:
            connections = mc.listConnections(i + "." + j, d=1)
            if "Constraint" in mc.objectType(connections[0]):
                if not mc.objExists(i + "." + j.replace("_Gimbal", "")):
                    mc.renameAttr(i + "." + j, j.replace("_Gimbal", ""))

    if controls:

        print("")
        print("- RENAMED GIMBAL ATTRS")

def fkControlFix():
    """Add fk vis attr and hide IK controls by default """

    ctrl = "Spine_Root_Ctrl"

    if not mc.objExists(ctrl + ".FkCtrls"):   
        if mc.objExists(ctrl + ".IkCtrls"):  
            mc.setAttr(ctrl + ".IkCtrls", 0)
            mc.addAttr(ctrl, ln="FkCtrls", k=1, at="enum", en="Hide:Active:Inactive", dv=1)
            rev = mc.createNode("reverse")
            mc.connectAttr(ctrl + ".FkCtrls", rev + ".inputX")
        
            for i in range(1, 3):
                mc.connectAttr(ctrl + ".FkCtrls", "Spine_Fk_0{}_CtrlShape.lodVisibility".format(i))
                mc.connectAttr(rev + ".outputX", "Spine_Fk_0{}_CtrlShape.template".format(i))

        print("")
        print("- ADDED FK ATTR AND HID IK CONTROLS")

def hideRootAttrs():
    """Hide transforms on root control """

    if mc.objExists('Spine_Root_Ctrl'):
        for i in "xyz":
            mc.setAttr('Spine_Root_Ctrl.t' + i, k=0, l=1)
            mc.setAttr('Spine_Root_Ctrl.r' + i, k=0, l=1)
            mc.setAttr('Spine_Root_Ctrl.s' + i, k=0, l=1)

def renameAttrs():
    """Rename some attributes to preferred animator naming convention """

    if mc.objExists("Character.PinkHelperVis"):
        mc.renameAttr("Character.PinkHelperVis", "HelperVis")

    if mc.objExists("Eye_Root_Ctrl.Texture_Resolution"):
     mc.renameAttr("Eye_Root_Ctrl.Texture_Resolution", "TextureResolution")

def changeControlColours():

    if mc.objExists("COG_Ctrl"):
        mc.setAttr("COG_CtrlShape.overrideEnabled", 1)
        mc.setAttr("COG_CtrlShape.overrideColor", 17)
        mc.setAttr("COG_Gimbal_CtrlShape.overrideEnabled", 1)
        mc.setAttr("COG_Gimbal_CtrlShape.overrideColor", 21)

def fixReference():
    """Fixes conflicting shapeDeformed issues arising from referencing in a face with deformers """

    print("")
    
    name_space = _getNamespace()

    non_ref_geo = []
    ref_geo = []

    corrupt_geo = []          
    for x in mc.listRelatives(name_space + ":Geo", ad=1, type="transform"): 
        for i in mc.listRelatives(x):
            if len(mc.listRelatives(x)) > 2:
                if "Deformed" in i and mc.referenceQuery(i, isNodeReferenced=True ):
                    corrupt_geo.append(x)
        
    for x in corrupt_geo:
        print(x + " has more than 1 shape. Trying to fix...")
        for i in mc.listRelatives(x):
            if [j for j in mc.listConnections(i, d=1) if "BSH" in j]:
                blendshapes = [j for j in mc.listConnections(i, d=1) if "BSH" in j]
            if mc.referenceQuery(i, isNodeReferenced=True ) == 0:
                non_ref_geo = i
            else:
                ref_geo = i
                    
        if mc.objExists("HeadSquash_Y1"):
            mc.nonLinear("HeadSquash_Y1", e=1, g=ref_geo, foc=1)
        if mc.objExists("HeadBend_X1"):
            mc.nonLinear("HeadBend_X1", e=1, g=ref_geo, foc=1)
        if mc.objExists("HeadBend_Z1"):
            mc.nonLinear("HeadBend_Z1", e=1, g=ref_geo, foc=1)
        
        ref_skin = mel.eval("findRelatedSkinCluster " + ref_geo)
        mc.reorderDeformers("HeadBend_Z1", ref_skin, ref_geo)
        if blendshapes:
            mc.connectAttr(ref_geo + '.worldMesh[0]', blendshapes[0] + '.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget', f=1)
        mc.delete(non_ref_geo)

def complete():

	print("")
	print("----- POSTBUILD COMPLETE")

def do_it(renameGimbals = True):
    """Run desired function in module """

    if mc.ls(sl=1):

        blendshapeMesh()
        
    organiseFaceRig()
    makeFaceVis()
    cleanup()
    noInheritGrp()
    
    if renameGimbals == True:
        renameGimbalAttrs()

    fkControlFix()
    hideRootAttrs()
    renameAttrs()
    changeControlColours()
    fixReference()
    complete()