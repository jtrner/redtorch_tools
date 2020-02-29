"""
name: globalScale.py

Author: Ehsan Hassani Moghaddam

History:
    05/24/16 (ehassani)     first release!
    
"""
import maya.cmds as mc

from ...lib import trsLib

# reload all imported modules from dev
import types
for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('dev'):
            reload(val)


def run(dist=None, globalScaleAttr=None, name="unknown") :
    """
    makes given node globally scalable
    """
    if mc.nodeType( dist ) == 'multiplyDivide':
        outAttr = 'outputX'
        distShape = dist
    else:
        outAttr = 'distance'
        if dist.type() == 'transform': # if transform node of distance node is selected, then select it's shape
            distShape = trsLib.getShapes(node=dist)[0]
        else:
            distShape = dist
    
    distShapeOuts = mc.listConnections(distShape ,s=False, p=True)
    if not distShapeOuts:
        return
    
    globalScale_mdn = mc.createNode("multiplyDivide" , n = name+"GlobalScale_MDN")
    mc.connectAttr(distShape+"."+outAttr, globalScale_mdn+".input1X")
    mc.connectAttr(globalScaleAttr, globalScale_mdn+".input2X")
    mc.setAttr(globalScale_mdn+".operation", 2)
    
    for out in distShapeOuts:
        mc.connectAttr(globalScale_mdn+".outputX", out, f=True)