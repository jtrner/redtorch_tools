import maya.cmds as mc

from ....lib import crvLib
from ....lib import jntLib
from ....lib import connect
from ....lib import attrLib
from ....lib import trsLib
from ....lib import strLib
from ....lib import deformLib
from ....lib import control
from ....lib import keyLib


reload(keyLib)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)

def detachHead(geoName = '',edge = '',name = '', movement = 50):
    if edge:
        mc.select(edge)
    else:
        mc.ls(sl = True)
    mc.DetachComponent()
    mc.select(geoName)
    mc.polySeparate(n = name , ch = False)
    head = mc.duplicate(name)
    mc.select(name, r = True)
    mc.select(name + '1', add = True)
    mc.polyUnite(ch = False ,name = geoName, muv = 1)
    mc.select(geoName +'.vtx[:]')
    mc.polyMergeVertex(d = 0.01, am = True, ch = False)
    mc.select(cl = True)
    newName = mc.rename(head, name)
    mc.setAttr(newName + '.ty', movement)
    return newName

def createCtl(parent = '',side = 'L',scale = [1, 1, 1]):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,1,0),
                          shape="square",
                          color=control.SECCOLORS[side],
                          scale=scale,
                          moveShape=[0,0,0.7],
                          matchTranslate=parent,
                          matchRotate= parent)


    return ctl.name,ctl.zro




