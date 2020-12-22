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

def locOnCrv(name = '', parent = '', numLocs = 3, crv = '',
             upCurve = '', paramStart = 0.5,paramEnd = 0.5, upAxis = 'y', posJnts = '',translate = False):
    param = paramStart
    tempList = []
    for i in range(numLocs):
        loc = mc.createNode('transform', name = name + '{}'.format(i), p = parent)
        pos = mc.xform(posJnts[i-1], q=True, ws=True, t=True)
        mc.setAttr(loc + '.t', *pos)
        crvLib.attach(node = loc, curve = crv, upCurve = upCurve,param = param, upAxis = upAxis,translate = translate)
        param -= paramEnd
        tempList.append(loc)
    return tempList

def cheekRaiseHierarchy(name = '',parent = '',side = 'L', position= ''):
    cheekJntZ = mc.createNode('transform', name = side + '_cheeckRaiseJntZ',p = parent)
    cheekJntOri = mc.createNode('transform', name = side + '_cheekRaiseJntOri', p = cheekJntZ)
    trsLib.match(cheekJntOri, position)
    cheekJntMod = mc.createNode('transform', name = side + 'cheeckRaiseJntMod', p = cheekJntOri)
    return cheekJntMod,cheekJntZ

def sharpJntsHierarchy(name = '', parent = '',joint = '',middle = False):
    if middle:
        oriGrp = mc.createNode('transform', name = name + '_ori_GRP',p = parent)
        trsLib.match(oriGrp, joint)
        modGrp = mc.createNode('transform', name = name + '_mod_GRP', p = oriGrp)
        makroGrp = mc.createNode('transform', name = name + '_makro_GRP', p = modGrp)
        mc.parent(joint, makroGrp)
        makroGrp = makroGrp.split('|')[-1]
        return modGrp,makroGrp
    else:
        oriGrp = mc.createNode('transform', name = name + '_ori_GRP',p = parent)
        trsLib.match(oriGrp, joint)
        modGrp = mc.createNode('transform', name = name + '_mod_GRP', p = oriGrp)
        mc.parent(joint, modGrp)
        modGrp = modGrp.split('|')[-1]
        return modGrp

def createMiddleCtls(parent = '',side = 'L'):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,0,1),
                          shape="square",
                          color=control.SECCOLORS[side],
                          scale=[1, 0.2, 0.3],
                          moveShape=[0,0,0.5],
                          lockHideAttrs=['s'],
                          matchTranslate=parent,
                          matchRotate= parent)

    mc.parent(ctl.zro, parent)

    return ctl.name,ctl.zro

def createSecondaryCtls(parent = '',side = 'L',ctlPose = ''):
    mult = [-1, 1][side == 'L']
    ctl = control.Control(descriptor='',
                          side=side,
                          orient=(0,0,1),
                          shape="triangle",
                          color=control.COLORS[side],
                          scale=[0.04, 0.04, 0.04],
                          moveShape=[0,0,0.3],
                          lockHideAttrs=['s'],
                          matchTranslate=ctlPose ,
                          matchRotate= ctlPose )


    mc.parent(ctl.zro, parent)

    return ctl.name,ctl.zro







