"""
name: splineIkStretch.py

Author: Ehsan Hassani Moghaddam

History:
    04/28/16 (ehassani)    clean up
    04/23/16 (ehassani)    PEP8 naming convention
    04/21/16 (ehassani)    first release!

To do:
    clusterize
"""

import maya.cmds as mc

from ...lib import crvLib
from ...lib import attrLib


def run(**kwargs):
    """
    synopsis :  makeSplineStretchy()
                makes the ik splines stretchy
    @param
                ik_curve(string) -> ik curve name
                volume(boolean) -> add volume options to joints?
    
    @return :   [curve_info, stretch_mdn, stretch_bln]
    """

    # inputs
    volume = kwargs.setdefault('volume', True)
    ik_curve = kwargs.setdefault('ik_curve')
    name = kwargs.setdefault('name', 'newStretchyIk')

    # create nodes and connections
    ik_curve_shape = crvLib.getShapes(ik_curve)[0]

    curve_info = mc.createNode("curveInfo", n=(name + "Stretch_CNF"))
    stretch_mdn = mc.createNode("multiplyDivide", n=(name + "Stretch_MDN"))
    stretch_bln = mc.createNode("blendTwoAttr", n=(name + "Stretch_BLN"))
    ikh = mc.listConnections(ik_curve_shape, type="ikHandle")
    joint_list = mc.ikHandle(ikh[0], q=True, jointList=True)

    # control
    attrLib.addFloat(ik_curve, ln="stretch", min=0, max=1, v=1)

    # connections
    mc.connectAttr(ik_curve_shape + ".worldSpace[0]", curve_info + ".inputCurve")
    arc_length = mc.getAttr(curve_info + ".arcLength")

    mc.connectAttr(curve_info + ".arcLength", stretch_mdn + ".input1X")
    mc.setAttr(stretch_mdn + ".input2X", arc_length)
    mc.setAttr(stretch_mdn + ".operation", 2)

    mc.connectAttr(stretch_mdn + ".outputX", stretch_bln + ".input[1]")
    mc.setAttr(stretch_bln + ".input[0]", 1)

    mc.connectAttr(ik_curve + ".stretch", stretch_bln + ".attributesBlender")

    for jnt in joint_list:
        mc.connectAttr(stretch_bln + ".output", jnt + ".scaleX")

    return curve_info, stretch_mdn, stretch_bln

    """
    #=================================================================================== 
    # create scale, sqrt and power nodes for keeping the volume using nodes instead of expression
    
    normScaleSqrt = mc.createNode ( "multiplyDivide" , n = "normScaleSqrt" )
    stretchedScale.outputX >> normScaleSqrt.input1X
    normScaleSqrt.operation.set( 3 )
    normScaleSqrt.input2X.set( 0.5 )

    sqrtMult = mc.createNode ( "multiplyDivide" , n = "sqrtMult" )
    sqrtMult.input1X.set( 1 )

    sqrtMult.operation.set( 2 )
    normScaleSqrt.outputX >> sqrtMult.input2X


    # find animCurve and disconnect if from spline curve.scalePower
    # we used scalePower just for creating the animCurve. Now that we have the anim curve we no longer need it
    animCurve = mc.listConnections( ik_curve.scalePower, d=True )[0]
    animCurve.output // ik_curve.scalePower    
    
    # but we can use curve.scalePower as a multiplyer to our auto valume result 
    volumeMultiplyer = mc.createNode ( "multiplyDivide" , n = "volume_multiplyer" )
    ik_curve.scalePower >> volumeMultiplyer.input1X
    animCurve.output >> volumeMultiplyer.input2X
    
    
    

    for k in range ( len(joint_list) ):
        
        cacheN = mc.createNode ( "frameCache" , n = (joint_list[k] + "_FCnode") )
        volumeMultiplyer.outputX >> cacheN.stream
        cacheN.varyTime.set( k + 1 )
        
        
        scaleMult = mc.createNode( "multiplyDivide" , n = (joint_list[k] + "_scale_mdn") )
        scaleMult.operation.set( 3 )

        sqrtMult.outputX        >>      scaleMult.input1X
        cacheN.varying          >>      scaleMult.input2X
        
        stretchedScale.outputX  >>      joint_list[k].scaleX
        scaleMult.outputX       >>      joint_list[k].scaleY
        scaleMult.outputX       >>      joint_list[k].scaleZ



    #=================================================================================== 
    # making the spine scalable by connecting the scale of the mian_ctrl to it's network


    if  stretch_switch==True :
        mc.addAttr (  ik_curve , ln = "stretch_switch"  , at = "double"  , keyable = True ,  min = 0 , max = 1 , dv = 1  )
        back_stretch_switch_bln = mc.createNode ("blendColors" , n = "back_stretch_switch_bln")

        back_stretch_switch_bln.color1R.set ( 1 )
        stretch_mdn.outputX     >>  back_stretch_switch_bln.color2R
        ik_curve.stretch_switch     >>  back_stretch_switch_bln.blender
        
        mc.connectAttr (  (back_stretch_switch_bln + ".outputR") , (stretchedScale + ".input2X") , f = True  )
    """
