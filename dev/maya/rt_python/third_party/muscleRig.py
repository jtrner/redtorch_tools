# Muscle rigging with nCloth utilities
#
# Andrew van Straten - 1 Oct 2014

import maya.mel as mm
import maya.cmds as mc
import os


def makePointToSurfaceCosntraint():
    # will make and rename and parent a point to surface constraint. 

    sl = mc.ls(sl=True)
    obj_0 = sl[0][:sl[0].rfind('.')]
    obj_1 = sl[-1]
    
    constraintShape = mm.eval('createNConstraint pointToSurface 0;')[0]
    constraintParent = mc.listRelatives( constraintShape, parent=True)
    
    obj_0_parent = mc.listRelatives( obj_0, parent=True )
    constraintParent = mc.rename( constraintParent, obj_0 +'_'+ obj_1 +'_pointSurface')
    
    mc.parent( constraintParent, obj_0_parent )
    
def makeSlideOnSurfaceConstraint():
    # will make and rename and parent a slide on surface constraint. 
    
    sl = mc.ls(sl=True)
    obj_0 = sl[0][:sl[0].rfind('.')]
    obj_1 = sl[-1]
    
    constraintShape = mm.eval('createNConstraint slideOnSurface 0;')[0]
    constraintParent = mc.listRelatives( constraintShape, parent=True)
    
    obj_0_parent = mc.listRelatives( obj_0, parent=True )
    constraintParent = mc.rename( constraintParent, obj_0 +'_'+ obj_1 +'_slideOnSurface')
    
    mc.parent( constraintParent, obj_0_parent )
    
    mc.setAttr( constraintParent + '.strength', 1.0)
    
    
def writeConstraintData( directory ): 
    # to save out constraints so they can be rebuilt
    # select constraint and run
    
    name = mc.ls(sl=True)[0]
    mm.eval('dynamicConstraintMembership "select";')
    
    sl = mc.ls(sl=True, fl=True)
    
    f = open( directory + '/' + name + '.txt', 'w')
    for s in sl:
        f.write( s+'\n' )
    
    f.close()
       
    
def createNCloth( type='muscle' ):
    # Will create nCloth object for selected mesh and set attributes 
    # based on type.
    #
    
    sl = mc.ls( sl=True )[0]
    slParent = mc.listRelatives(sl, parent=True)    
    
    nClothShape = mm.eval('createNCloth 0')[0]
    nClothTransform = mc.listRelatives( nClothShape, parent=True )
    nClothTransform = mc.rename( nClothTransform, sl+'_nClothObj')
    nClothShape = mc.listRelatives( nClothTransform, shapes=True)[0]
    
    try: 
        mc.parent( nClothTransform, slParent )
    except:
        print 'Parent to world'
        pass
    
    
    if type == 'muscle':
        # set nCloth defaults for a muscle
    
        mc.setAttr( nClothShape + '.stretchResistance', 10 )
        mc.setAttr( nClothShape + '.compressionResistance', 10 )
        mc.setAttr( nClothShape + '.bendResistance', 5 )
        mc.setAttr( nClothShape + '.inputMeshAttract', 1 )
        mc.setAttr( nClothShape + '.pressureMethod', 1 )
        
        mc.setAttr( nClothShape + '.thickness', 0.01 )
        mc.setAttr( nClothShape + '.selfCollideWidthScale', 1 )
        mc.setAttr( nClothShape + '.inputAttractDamp', 0.1 )
        mc.setAttr( nClothShape + '.tangentialDrag', 2.0 )
        mc.setAttr( nClothShape + '.damp', 0.5 )
        mc.setAttr( nClothShape + '.stretchDamp', 0.4 )
        
                
    elif type == 'fascia':
        # set nCloth defaults for skin
    
        mc.setAttr( nClothShape + '.stretchResistance', 20 )
        mc.setAttr( nClothShape + '.compressionResistance', 20 )
        mc.setAttr( nClothShape + '.bendResistance', 2 )
        mc.setAttr( nClothShape + '.inputMeshAttract', 1 )
        mc.setAttr( nClothShape + '.pointMass', 0.7 )
        
        mc.setAttr( nClothShape + '.thickness', 0.01 )
        # mc.setAttr( nClothShape + '.selfCollideWidthScale', 1 )
        mc.setAttr( nClothShape + '.ignoreSolverGravity', 1 )
        mc.setAttr( nClothShape + '.friction', 0.0 )
        
        mc.setAttr( nClothShape + '.inputAttractDamp', 0.01 )
        mc.setAttr( nClothShape + '.tangentialDrag', 2.0 )
        mc.setAttr( nClothShape + '.damp', 2.0 )
        mc.setAttr( nClothShape + '.stretchDamp', 2.0 )
        mc.setAttr( nClothShape + '.selfCollide', 0 ) 
        
    
def connectAttractMeshToNcloth():
    # Connect the attract mesh to the nCloth object

    attractMesh = mc.ls( sl=True )[0]
    nClothObj = mc.ls( sl=True )[1]
    
    # get the right shape
    attractMeshShapes = mc.listRelatives( attractMesh, shapes=True, type='mesh' )
    attractMeshShape = None
    for ams in attractMeshShapes:
        if not mc.getAttr(ams +'.intermediateObject'):
            attractMeshShape = ams
    
    nClothShape = mc.listRelatives( nClothObj, shapes=True )[0]
    
    mc.connectAttr( attractMeshShape + '.worldMesh[0]', nClothShape +'.inputMesh', f=True)
    mc.connectAttr( attractMeshShape + '.worldMesh[0]', nClothShape +'.restShapeMesh', f=True)
    
    return 1
    

def snap( object, target ): 
    # snap object to target world space position. 

    pos = mc.xform( target, ws=True, t=True, q=True )
    rot = mc.xform( target, ws=True, ro=True, q=True )
    mc.setAttr( object + '.tx', pos[0] )
    mc.setAttr( object + '.ty', pos[1] )
    mc.setAttr( object + '.tz', pos[2] )

    mc.setAttr( object + '.rx', rot[0] )
    mc.setAttr( object + '.ry', rot[1] )
    mc.setAttr( object + '.rz', rot[2] )

    
def makeLocatorHeirarchy( name, parent, snapTarget, twist=False ):
    # select a parent (for general orientation) 
    # and two locators, a start and end

    # assumes muscle rig points down the x axis. 
    prntLoc = mc.spaceLocator( n=name+"Prnt_loc" )[0]
    mc.setAttr( prntLoc + '.rx', 0 )
    mc.setAttr( prntLoc + '.ry', 0 )
    mc.setAttr( prntLoc + '.rz', 0 )
    
    snap( prntLoc, snapTarget )
    rotLoc = mc.duplicate( prntLoc, n=name+"Rot_loc" )[0]
    upLoc = mc.duplicate( prntLoc, n=name+"Up_loc" )[0]
    
    heirarchyObjects = list()
        
    mc.parent( prntLoc, parent )
    mc.parent( rotLoc, prntLoc )
    mc.parent( upLoc, prntLoc )
    mc.setAttr( upLoc + '.tz', 1.0 )
    mc.select(cl=True)
    jnt = mc.joint( n=name + '_jnt', radius=0.5 )
    snap( jnt, rotLoc )
    mc.parent( jnt, rotLoc )
    mc.setAttr( jnt + '.rx', 0 )
    mc.setAttr( jnt + '.ry', 0 )
    mc.setAttr( jnt + '.rz', 0 )
    mc.setAttr( jnt + '.jointOrientX', 0 )
    mc.setAttr( jnt + '.jointOrientY', 0 )
    mc.setAttr( jnt + '.jointOrientZ', 0 )
    
    heirarchyObjects.append( prntLoc )
    heirarchyObjects.append( rotLoc )
    heirarchyObjects.append( upLoc )
    heirarchyObjects.append( jnt )
    
    
    if twist: 
        twistLoc = mc.spaceLocator( n=name+"Twist_loc" )[0]
        snap( twistLoc, rotLoc )
        mc.parent( twistLoc, rotLoc )
        mc.parent( jnt, twistLoc )
        heirarchyObjects.append( twistLoc )
    
    return heirarchyObjects

def makeAimConstraint( targetObj, rotationObj, upLoc, aimDir ):

    aimVec = [1, 0, 0]
    if aimDir == '-x' :
        aimVec = [-1, 0, 0]  
    
    mc.aimConstraint( [targetObj], rotationObj, aimVector=aimVec, 
                      upVector=[0, 0, 1], worldUpType="object", 
                      worldUpObject=upLoc  )
    
    
def createRig( prefix="default", numInbetweens=3, twist=False ):
    # Will create a small rig for the muscle objects.                         
    #
    # Usage: 
    #  Select a 'transform' which the rig will get parented under (usually an oriented joint)
    #  Select two further locators. These locators should be in the positions where you want
    #    the muscle attachments. upper, then lower. 
    #  Run. 
    #
    # Flags:
    #   prefix - The string added to the start of all the generated nodes. 
    #   numInbetweens - For more inbetween joints. 
    #   twist - Adds an extra 'twist' locator under each locator heirarchy. 
    #           The twist locator in the 'lower' heirarchy is the driver. 
        
    
    parentTransform = mc.ls( sl=True )[0]
    topTransform = mc.ls( sl=True )[1]
    btmTransform = mc.ls( sl=True )[2]
    
    nullTransform = mc.group( em=True, name=prefix+'Parent_grp' )
    snap( nullTransform, parentTransform )
    mc.parent( nullTransform, parentTransform )
       
    
    topHeirarchy = makeLocatorHeirarchy( prefix+"_top", nullTransform, topTransform, twist )
    btmHeirarchy = makeLocatorHeirarchy( prefix+"_btm", nullTransform, btmTransform, twist )
    makeAimConstraint( btmHeirarchy[0], topHeirarchy[1], topHeirarchy[2], "+x" )
    makeAimConstraint( topHeirarchy[0], btmHeirarchy[1], btmHeirarchy[2], "-x" )
    
    # Make inbetweens
    # Three inbetweens is four partitions
    inbetweenHeirarchies = list()
    
    partitions = numInbetweens+1
    for i in range( 1, partitions ): 
        newHeirarchy = makeLocatorHeirarchy( prefix+'_'+str(i)+'_', nullTransform, btmTransform, twist )
        inbetweenHeirarchies.append( newHeirarchy )
        
        blendColors = mc.createNode( 'blendColors' ) 
        mc.connectAttr( btmHeirarchy[0] +'.t', blendColors + '.color1' )
        mc.connectAttr( topHeirarchy[0] +'.t', blendColors + '.color2' )
        mc.connectAttr( blendColors + '.output', newHeirarchy[0] +'.t' )
        mc.setAttr( blendColors + '.blender', (1.0 / partitions)*i )
        makeAimConstraint( btmHeirarchy[0], newHeirarchy[1], newHeirarchy[2], "+x" )
        
    
    if twist: 
        for i, heirarchy in enumerate( inbetweenHeirarchies ) :
            md = mc.createNode( 'multiplyDivide' )
            weight = (1.0 / partitions)*(i+1)
            mc.connectAttr( btmHeirarchy[4]+'.rx', md+'.input1.input1X' )
            mc.setAttr( md + '.input2.input2X', weight )
            mc.connectAttr( md+'.outputX', heirarchy[4]+'.rx' )
    