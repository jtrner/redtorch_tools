
#
# A UI utility to generate and drive corrective shapes. 
# 
# 10 Oct 2014 - Andy van Straten
#
# Usage:
#   - Make sure correctiveShapeBuilder.py is in your scripts directory. 
#   - Make sure cvShapeInverter plugin is loaded.
# 
#   Execute the following python commands: 

""" 

import correctiveShapeBuilder as csb
csb.ui().create()

"""

import maya.cmds as mc
import cvShapeInverter
from functools import partial

class ui():
    def __init__(self, winName="winTheWindow"):
        self.winTitle = "Corrective Shape and PSD builder - Andy van Straten"
        self.winName = winName
        
        self.shapeName = None
                
        print(self.winName)
    
    def setName(self, name):
        self.shapeName = name
    
    def getName(self):
        return self.shapeName
    
    def create(self):
        if mc.window(self.winName, exists=True):
            mc.deleteUI(self.winName)
        mc.window(self.winName, title=self.winTitle)
        mc.scrollLayout()
        mc.columnLayout( adjustableColumn=True  )
        mc.separator( style='none', height=10 )        
        
        mc.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 100), (2, 230), (3, 60), (4, 60)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10), (4, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right"), (4, "right")] )
        mc.text(label = 'Base Mesh: ')
        self.baseMesh_tf = mc.textField(text='None', editable=False)
        mc.button(label='Load', c=partial( updateBaseMeshAndUI, self, 'sel' ) )
        mc.button(label='Clear', c=partial( clearTextField, self.baseMesh_tf ) )
        mc.setParent('..')
        mc.separator( style='none', height=10 )
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 230), (3, 130)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right")])
        mc.text(label = 'Blendshape Node: ')
        self.blendNode_tf = mc.textField(text='None', editable=False)
        mc.button(label='Replace with selection', c=partial( updateBlendShapeNode, self ) )
        mc.setParent('..')
        mc.separator( style='none', height=10 )
        
        self.blendOrders_rcl = mc.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 100), (2, 380)], 
            columnSpacing=[(1, 10), (2, 10)], 
            columnAlign=[(1, "left"), (2, "left")] )
        mc.text(label = 'Target Weights: ')
        
        mc.setParent('..')
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 180)], 
            columnSpacing=[(1, 10), (2, 10)], 
            columnAlign=[(1, "left"), (2, "left")] )
        mc.text( label='' )
        mc.button(label='Refresh', c=partial( updateBaseMeshAndUI, self, 'current'  ) )
        mc.setParent('..')
        
        mc.separator( style='none', height=20 )
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 230), (3, 130)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right") ])
        mc.text(label = 'Intermediate Mesh: ')
        self.interMesh_tf = mc.textField(text='None', editable=False)
        mc.button(label='Generate and Connect', c=partial( generateAndConnect, self ) )
        mc.setParent('..')
        mc.separator( style='none', height=5 )
        
        mc.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 100), (2, 230), (3, 60), (4, 60)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10), (4, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right"), (4, "right")] )
        mc.text(label = 'Sculpt Mesh: ')
        self.sculptMesh_tf = mc.textField(text='None', editable=False)
        mc.button(label='Load', c=partial( updateTextField, self.sculptMesh_tf ) )
        mc.button(label='Clear', c=partial( clearTextField, self.sculptMesh_tf ) )
        mc.text( label = '' ) 
        mc.rowLayout()
        mc.button( label = 'Match sculpt to selected', w=150, c=partial(matchSculptToSelected, self ) )
        mc.setParent('..')
        mc.setParent('..')
        
        mc.separator( style='none', height=5 )
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 230), (3, 130)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right")] )
        mc.text(label = 'Drivers(s): ')
        self.drivers_tsl = mc.textScrollList(height=50, selectCommand= partial( updateDriverAttrs, self ) )
        mc.button(label='Load from selection', c=partial( updateDrivers, self ) )
        mc.setParent('..')
        mc.separator( style='none', height=5 )   

        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 230), (3, 130)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right")] )
        mc.text(label = 'Driver Attrs(s): ')
        self.driverAttrs_tsl = mc.textScrollList(height=100)
        mc.setParent('..')
        mc.separator( style='none', height=20 )         
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 120),(2, 230), (3, 10)], 
            columnAlign=[(2, "center")] )
        mc.text(label='')
        mc.button(label='Build PSD and Automatically Connect', c=partial( buildPSD, self ) )
        mc.text(label='')
        mc.text(label='')
        mc.text(label='OR: select PSD and connect', height=30)
        mc.setParent('..')
        
        mc.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 100), (2, 230), (3, 60), (4, 60)], 
            columnSpacing=[(1, 10), (2, 10), (3, 10), (4, 10)], 
            columnAlign=[(1, "left"), (2, "left"), (3, "right"), (4, "right")] )
        mc.text(label = 'PSD: ')
        self.psdMesh_tf = mc.textField(text='Select PSD', editable=False)
        mc.button(label='Load', c=partial(updateTextField, self.psdMesh_tf ) )
        mc.button(label='Clear')
        mc.setParent('..')
        mc.separator( style='none', height=10 )        
        
        mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 120),(2, 230), (3, 10)], 
            columnAlign=[(2, "center")] )
        mc.text(label='')
        mc.button(label='Connect', c=partial( connectWeight, self ) )
        mc.text(label='')        
                
        mc.showWindow( self.winName )
        mc.window( self.winName, edit=True, widthHeight=(540, 520) )

## procedure to build psd by running bSpiritCorrectiveShape
def buildPSD( widget=None, args=None ):
    
    # check that user has specified controls
    ctrl = mc.textScrollList( widget.drivers_tsl, q=True, si=True )
    attr = mc.textScrollList( widget.driverAttrs_tsl, q=True, si=True )
    blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
    
    # first check if a controller has been selected. 
    if ctrl is not None: 
        # then check if attribute has been selected. 
        if attr is None:
            mc.error( 'correctiveShapeBuilder: No attribute selected.' )         
            return 0
        else: 
            # if there is an attribute, we check that there are values we can use. 
            attrVal = mc.getAttr( ctrl[0] + '.' + attr[0])
            if attrVal == 0.0:
                mc.error( 'correctiveShapeBuilder: Selected attribute needs a non-zero value to drive PSD' )
                return 0
    else: # if ctrl IS None, then we check first if there is actually a blendshape
          # and then if it has two weights
        if 'None' in blendNode:     
            mc.error( 'correctiveShapeBuilder: No drivers or existing blendshape weights to drive PSD' )
            return 0
        
        else: 
            weightCount = mc.blendShape( blendNode, q=True, weightCount=True )
            if weightCount < 2: 
                mc.error( 'correctiveShapeBuilder: Not enough blendshape weights to drive PSD' )
                return 0
                
    interMesh = mc.textField( widget.interMesh_tf, q=True, text=True )
    psdMeshName = interMesh + '_inverted'
    
    # window for renaming psd
    result = mc.promptDialog(
                title='Rename Object',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel', 
                text=psdMeshName)
    
    if result == 'OK':
    
        mc.select( cl=True )
                    
        # duplicate intermediate mesh (so we don't have to delete history )
        interDup = mc.duplicate( interMesh )
        
        # turn envelope on main bshape off before running bspirit
        blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
        if 'None' not in blendNode:
            mc.setAttr( blendNode + '.envelope', 0 )    
           
        mc.select( mc.textField( widget.baseMesh_tf, q=True, text=True ), r=True )
        mc.select( interDup, add=True )
        
        # replace BSpirit here with cvShapeInverter
        # psdMesh = mel.eval('BSpiritCorrectiveShape')
        
        psdMesh = cvShapeInverter.invert()
        mc.delete( interDup )            
        
        text = mc.promptDialog(query=True, text=True)
        psdMesh = mc.rename( psdMesh, text )
        widget.setName( text )
        
        # set the PSD portion of the UI to be the new bspiritshape product
        mc.textField( widget.psdMesh_tf, e=True, text=psdMesh )
        if 'None' not in blendNode:
            mc.setAttr( blendNode + '.envelope', 1 )    
        
        connectWeight( widget ) 
                          
                
## Procedure to generate intermediate AND sculpt mesh from current pose.
def generateAndConnect( widget=None, args=None ):
    baseMesh = mc.textField( widget.baseMesh_tf, q=True, text=True )
    blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
                
    #check that user has specified a basemesh
    if baseMesh is not None:
        # set envelope on main blendShape node to 0 before duplicating intermediate mesh
        # so that we make sure we duplicate object + skin deformations only. 
        if 'None' not in blendNode:
            mc.setAttr( blendNode + '.envelope', 0 )
        interMesh = mc.duplicate( baseMesh )[0]
        interMesh = mc.rename( interMesh, baseMesh + '_inter' )
        mc.textField( widget.interMesh_tf, e=True, text=interMesh )
                
        # set envelope on main blendshape node back to 1 for the sculpt mesh
        if 'None' not in blendNode:
            mc.setAttr( blendNode + '.envelope', 1 )
        sculptMesh = mc.duplicate( baseMesh )[0]
        sculptMesh = mc.rename( sculptMesh, baseMesh + '_sculpt' )
        mc.textField( widget.sculptMesh_tf, e=True, text=sculptMesh )
        
        # hide base mesh and inter mesh while user is sculpting. 
        mc.setAttr( baseMesh + '.v', 0 )
        mc.setAttr( interMesh + '.v', 0 )
        
        # create a blendshape on the intermediate mesh with orig and sculpt as targets
        interBlendShape = mc.blendShape( baseMesh, sculptMesh, interMesh, n='inter_blendShape' )[0]
        # set baseMesh target to negative 1. what this does is subtracts the existing blendshape information
        # from the intermediate shape. 
        # because the sculpt mesh target is set to 1 what we are left with the difference between the existing 
        # vertex positions (derived from existing blendshapes) and the sculpt mesh.
        # we want this because an order 2 blendshape for example is correcting or adding to an order 1
        mc.setAttr( interBlendShape + '.' + baseMesh, -1 )
        mc.setAttr( interBlendShape + '.' + sculptMesh, 1 )
        
    else:
        mc.error( 'correctiveShapeBuilder: No base mesh specified.' )
        
# Procedure to build nodes that connect drivers to a blendshape weight
def connectWeight( widget=None, args=None ):
        
    # add the blendshape target and connect the clamp to the blendshape weight
    psdMesh = mc.textField( widget.psdMesh_tf, q=True, text=True )
    baseMesh = mc.textField( widget.baseMesh_tf, q=True, text=True )
    blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
    
    # if there is no blendshape in the list, create one. 
    # the reason I just go ahead and build one instead of asking the user first is 
    # because the script automatically detects any blendshapes in the history of the baseMesh
    # when it is loaded in.
    if 'None' in blendNode:
        blendNode = mc.blendShape( psdMesh, baseMesh, n=baseMesh + '_psds', frontOfChain=True )[0]
    else:
        index = mc.blendShape( blendNode, q=True, weightCount=True )
        mc.blendShape( blendNode, edit=True, t=( baseMesh, index, psdMesh, 1.0 ) )
    
    #unhide things that were hidden and turn on blendshapes
    mc.setAttr( baseMesh + '.v', 1 )
    mc.setAttr( blendNode + '.envelope', 1 ) 
    sculptMesh = mc.textField( widget.sculptMesh_tf, q=True, text=True )
    if 'None' not in sculptMesh:
        mc.setAttr( sculptMesh + '.v', 0 )
        workingName = widget.getName()
        sculptMesh = mc.rename( sculptMesh, workingName + '_sculpt' )
        
        # mc.delete( sculptMesh )
        # mc.textField( widget.sculptMesh_tf, e=True, text='None' )
        
    interMesh = mc.textField( widget.interMesh_tf, q=True, text=True )
    if 'None' not in interMesh:
        mc.delete( interMesh )
        mc.textField( widget.interMesh_tf, e=True, text='None' )
    
    mc.setAttr( psdMesh + '.v', 0 )
    # attach an order attribute on to the blendshape node corresponding to the weight
    mc.addAttr( blendNode, ln= psdMesh + '_order', at='long', keyable=False )
    
    # find out which blendshapes are turned on and what the highest order is
    blendWeights = mc.listAttr( blendNode + '.w', multi=True )
    highOrder = 1
    for bw in blendWeights:
        # if the weight is turned on, get its order
        if round( mc.getAttr( blendNode + '.' + bw ), 2 ) > 0:
            if mc.attributeQuery( bw + '_order', node=blendNode, exists=True ):
                order = mc.getAttr( blendNode + '.' + bw + '_order' )
                if order >= highOrder:
                    highOrder = order + 1
                
    mc.setAttr( blendNode + '.' + psdMesh + '_order', highOrder )
    mc.setAttr( blendNode + '.' + psdMesh, 1 )
    
    
    
    ## ---------- now do the connecting to the built PSD shape ---------------------- ##
    
    
    ctrl = mc.textScrollList( widget.drivers_tsl, q=True, si=True )
    if ctrl is not None: 
        #already validated this data in caller function
        attr = mc.textScrollList( widget.driverAttrs_tsl, q=True, si=True )  
        ctrl = ctrl[0]
        attr = attr[0]
        keyVal = mc.getAttr( ctrl + '.' + attr )
        
        #setDrivenKeyframe( [objects] , [attribute=string], [controlPoints=boolean], [currentDriver=string], [driven=boolean], [driver=boolean], [driverValue=float], [hierarchy=string], [inTangentType=string], [insert=boolean], [insertBlend=boolean], [outTangentType=string], [shape=boolean], [value=float]) 
        mc.setDrivenKeyframe( blendNode + '.' + psdMesh, 
                              currentDriver = ctrl + '.' + attr )
        mc.setDrivenKeyframe( blendNode + '.' + psdMesh, value = 0.0, 
                              currentDriver = ctrl + '.' + attr, driverValue = 0.0 )                                
        
        
    else:    
        blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
        # we are going to use the blendshape activations to drive the corrective
        # first need to test there is actually a blendshape, and if there is anything
        # activated. if not, its not an order 2 shape anyways. skip!
        
        if 'None' not in blendNode:
            targets = mc.aliasAttr( blendNode, q=True )     
            driverWeights = list()
            # get the names of the 2 targets. these will be our drivers
            # get the two targets with values higher than zero
            for i in xrange(0,len(targets),2):
                if len( driverWeights ) < 2:
                    val = mc.getAttr( blendNode + '.' + targets[i] )
                    if val > 0:
                        driverWeights.append(targets[i])
            
            if len(driverWeights) == 2:
                md = mc.createNode('multiplyDivide')
                mc.connectAttr( blendNode + '.' + driverWeights[0], md + '.input1X' )
                mc.connectAttr( blendNode + '.' + driverWeights[1], md + '.input2X' )
                output = md + '.outputX'
                mc.connectAttr( output, blendNode + '.' + psdMesh )    
        
    
    mc.select( baseMesh )
    
    #update the UI with the new blendshape information
    updateBaseMeshAndUI( widget, 'sel' )
          
            
# Procedure to match the current sculpt mesh to another pre sculpted mesh
def matchSculptToSelected( widget=None, args=None):
    sl = mc.ls(sl=True)
    if len(sl) == 1:
        sculptMesh = mc.textField( widget.sculptMesh_tf, q=True, text=True ) 
        if sculptMesh is not None:
            bShape = mc.blendShape( sl, sculptMesh  )[0]
            mc.setAttr( bShape + '.w[0]', 1 )
            mc.delete( sculptMesh, ch=True )

            
## Procedure that updates the UI with a blendshape from a manual selection 
## rather than from automatically detecting. 
def updateBlendShapeNode( widget=None, args=None ):
    blendShape = None
    sl = mc.ls( sl = True )
    if len(sl) < 1:
        mc.error( 'correctiveShapeBuilder: Nothing selected.' )
        mc.textField( widget.blendNode_tf, edit=True, text='None' )
    elif len(sl) >= 1:
        for item in sl:
            if 'blendShape' in mc.nodeType( item ):
                blendShape = item
        if blendShape == None:
            mc.error( 'No blendShape nodes in selection.' )
        else:
            mc.textField( widget.blendNode_tf, edit=True, text=blendShape )
            listWeightOrder( widget, blendShape )

## Procedure to return the name of the blendshape node that appears in an objects construction
## history. Returns 'None' if no blendshape detected.    
def detectBlendShape(object=None, args=None):
    history = mc.listHistory( object )
    blendShapeNodes = []
    for item in history:
        if 'blendShape' in mc.nodeType( item ):
            blendShapeNodes.append( item )
            
    if len(blendShapeNodes) == 0:
        return 'None'
    else:
        return blendShapeNodes[0]
    
## Procdure to update given text field with selected object
def updateBaseMeshAndUI( widget=None, mode=None, args=None ):
    
    
    if mode == 'sel':
    
        # clear everything first. 
        mc.textField( widget.baseMesh_tf, edit=True, text='None' )
        mc.textField( widget.blendNode_tf, edit=True, text='None' )
        mc.textField( widget.interMesh_tf, edit=True, text='None' )
        mc.textField( widget.sculptMesh_tf, edit=True, text='None' )
        
        sl = mc.ls(sl=True)
        if len(sl) == 1:
            mc.textField( widget.baseMesh_tf, edit=True, text=sl[0] )        
            blendNode = detectBlendShape( sl[0] )

            mc.textField( widget.blendNode_tf, edit=True, text=blendNode )
            if blendNode is not None:
                listWeightOrder( widget, blendNode )
                        
        elif len(sl) >1:
            mc.error( 'correctiveShapeBuilder: More than one object selected.' )
            
        elif len(sl) < 1:
            mc.error( 'correctiveShapeBuilder: Nothing selected.' )
    
    elif mode == 'current':
        blendNode = mc.textField( widget.blendNode_tf, q=True, text=True )
        listWeightOrder( widget, blendNode )

# Procedure to collect weights of given blendShapeNode and present them in the UI.
# Will distribute weights according to their 'order' into the UI.    
#
def listWeightOrder( widget=None, blendNode=None, args=None ):
    
    if 'None' in blendNode: 
        uiChildren = mc.rowColumnLayout( widget.blendOrders_rcl, q=True, childArray=True )
        if uiChildren is not None:
            for uiChild in uiChildren:
                mc.deleteUI( uiChild )
    
    if 'None' not in blendNode:
        blendWeights = mc.listAttr( blendNode + '.w', multi=True )
        
        uiChildren = mc.rowColumnLayout( widget.blendOrders_rcl, q=True, childArray=True )
        if uiChildren is not None:
            for uiChild in uiChildren:
                mc.deleteUI( uiChild )
        
                
        order_frameLayouts = []
        order_rowColumnLayouts = []
        
        mc.setParent( widget.blendOrders_rcl )
        mc.text( label= 'Target weights:' )
        order_frameLayouts.append( mc.frameLayout(label="Unresolved", collapsable=True, collapse=False) )
        order_rowColumnLayouts.append( mc.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 280), (2, 80)], 
                                    columnSpacing=[(1, 10), (2, 10)], 
                                    columnAlign=[(1, "left"), (2, "left")] ) )
        highestOrder = 0
        for i in range(0, len(blendWeights)):
            # test if the object has an order attribute, 
            # if not put it in the unresolved_rcl
            # if so, test if its higher than the current highest order
            # if not, put it in the rcl that corresponds with that order
            # if so, create a higher order rcl and put it in that rcl
            if mc.objExists( blendNode + '.' + blendWeights[i] + '_order' ):
                order = mc.getAttr(  blendNode + '.' + blendWeights[i] + '_order' )
                if order > highestOrder:
                    mc.setParent( widget.blendOrders_rcl )
                    mc.text( label = '' )
                    order_frameLayouts.append( mc.frameLayout(label="Order " + str(order) + " Shapes", collapsable=True, collapse=False) )
                    order_rowColumnLayouts.append( mc.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 280), (2, 80)], 
                                    columnSpacing=[(1, 10), (2, 10)], 
                                    columnAlign=[(1, "left"), (2, "left")] ) )
                    mc.text( label = blendWeights[i] )
                    weightVal = mc.getAttr( blendNode + '.w[' + str(i) + ']' )
                    weightVal = round( weightVal, 2 )
                    
                    mc.text( label = weightVal )
                    
                    highestOrder = order
                else:
                    mc.setParent( order_rowColumnLayouts[order] )
                    mc.text( label = blendWeights[i] )
                    mc.text( label = mc.getAttr( blendNode + '.w[' + str(i) + ']' ) )
            else:
                mc.setParent( order_rowColumnLayouts[0] )
                mc.text( label = blendWeights[i] )
                mc.text( label = mc.getAttr( blendNode + '.w[' + str(i) + ']' ) )

#procedure to update the drivers section of the UI with current selection
def updateDrivers( widget=None, args=None ):
    #clear text scroll list first
    mc.textScrollList( widget.drivers_tsl, edit=True, removeAll=True )
    sl = mc.ls(sl=True)
    for item in sl:
        mc.textScrollList( widget.drivers_tsl, edit=True, append=item )
    
    allItems = mc.textScrollList( widget.drivers_tsl, query=True, ai=True )
    if allItems != None:
        mc.textScrollList( widget.drivers_tsl, edit=True, sii=1 )
    updateDriverAttrs( widget )        

def updateDriverAttrs( widget=None, args=None ):
    # build list of attrs based on selected driver in tsl
    driver = mc.textScrollList( widget.drivers_tsl, q=True, si=True )
    mc.textScrollList( widget.driverAttrs_tsl, edit=True, removeAll=True )
    if driver != None:
        driver = driver[0]
        attrs = mc.listAttr( driver, keyable=True )
        
        if attrs != None:
            for item in attrs:
                mc.textScrollList( widget.driverAttrs_tsl, edit=True, append=item )
            
            
def clearTextField( widget_tf=None, args=None ):
    mc.textField( widget_tf, edit=True, text='None' )

# Procedure to update any text field with one selected object.    
def updateTextField( tf=None, args=None ):
    sl = mc.ls(sl=True)
    if len(sl) == 1:
        mc.textField( tf, edit=True, text=sl[0] )        
    elif len(sl) > 1:
        mc.error( 'correctiveShapeBuilder: More than one object selected.' )
    elif len(sl) < 1:
        mc.error( 'correctiveShapeBuilder Nothing selected.' )




