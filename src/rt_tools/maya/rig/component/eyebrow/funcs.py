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

def createCtl(parent = '',side = 'L',scale = [0.8, 0.8, 0.8]):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,0,1),
                          shape="square",
                          color=control.SECCOLORS[side],
                          scale=scale,
                          moveShape=[0,0,0.7],
                          matchTranslate=parent,
                          matchRotate= parent)


    return ctl.name,ctl.zro









