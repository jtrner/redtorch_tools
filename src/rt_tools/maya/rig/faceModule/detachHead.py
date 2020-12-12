import maya.cmds as mc

def DetachHead(geoName = '',edge = '',name = '', movement = 50):
    if edge:
        mc.select(edge)
    else:
        mc.ls(sl = True)
    mc.DetachComponent()
    mc.select(geoName)
    mc.polySeparate(n = name , ch = False)
    head = mc.duplicate(name)
    newName = mc.rename(head, 'head')
    mc.setAttr(newName + '.ty', movement)
    mc.select(name, r = True)
    mc.select(name + '1', add = True)
    mc.polyUnite(ch = False ,name = geoName, muv = 1)
    mc.select(geoName +'.vtx[:]')
    mc.polyMergeVertex(d = 0.01, am = True, ch = False)
    return newName, movement