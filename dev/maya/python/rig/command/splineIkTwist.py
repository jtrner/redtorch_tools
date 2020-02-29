"""
name: splineIkTwist.py

Author: Ehsan Hassani Moghaddam

History:
    04/28/16 (ehassani)     first release!
    
"""

import maya.cmds as mc

from ...lib import strLib

from ...lib import trsLib


def run(ik_handle="", base_control="", end_control="", method="advanced",
        up_axis="z", up_vector1=(1, 0, 0), up_vector2=(1, 0, 0)):
    """
    twist calculator for spline ik handle
    @param    
                ik_handle      string    spline ik handle to control twist for
                base_control   string    start twist control
                end_control    string    end twist control
                method         string    "advanced" or "directConnection"
                up_axis        string    "y", "-y", "z" or "-z"
                up_vector1     vector3   start up vector 
                up_vector2     vector3   end up vector 
    @return    
                None
    """

    if method == "directConnection":
        print "directConnection is not implemented yet."

    if method == "advanced":
        mc.setAttr(ik_handle + ".dTwistControlEnable", 1)
        mc.setAttr(ik_handle + ".dWorldUpType", 4)
        mc.setAttr(ik_handle + ".dWorldUpVector", up_vector1[0], up_vector1[1], up_vector1[2])
        mc.setAttr(ik_handle + ".dWorldUpVectorEnd", up_vector2[0], up_vector2[1], up_vector2[2])

        up = 0  # up_axis==+y
        if up_axis == "-y":
            up = 1
        elif up_axis == "z":
            up = 3
        elif up_axis == "-z":
            up = 4
        mc.setAttr(ik_handle + ".dWorldUpAxis", up)

        try:
            mc.connectAttr(base_control + ".worldMatrix[0]", ik_handle + ".dWorldUpMatrix")
            mc.connectAttr(end_control + ".worldMatrix[0]", ik_handle + ".dWorldUpMatrixEnd")
        except:
            raise ValueError(
                'can\'t set "{}" and "{}" as twist controls for {}'.format(base_control, end_control, ik_handle))
