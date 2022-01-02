import maya.cmds as mc

def findBindJnts(list):
    bindJntList = []
    for item in list:
        children = mc.listRelatives(item, ad=True) or []
        print children

        joints = ['JNT', 'bind']
        for child in children:
            for i in joints:
                if i in child:
                    # need uniqueness
                    if not child in bindJntList:
                        bindJntList.append(child)

    return bindJntList

def searchAndReplaceNames(objList, serachFor="L_", replaceWith="R_", hierachy=True):
    for item in objList:
        children = mc.listRelatives(item, ad=True, f=True) or []
        objList = objList + children

    objList.sort(key=len, reverse=True)
    newObjList = []
    for item in objList:
        itemShortName = item.split("|")[-1]
        itemNewName = itemShortName.replace(serachFor, replaceWith)

        mc.rename(item, itemNewName)

        newObjList.append(itemNewName)

    return newObjList

def mirrorListToOtherSide(list, side="YZ"):
    mc.group(n="mirrorGrp", w=True, em=True)
    mc.parent(list, "mirrorGrp")
    if side == "YZ":
        mc.setAttr("mirrorGrp.sx", -1)
    elif side == "XY":
        mc.setAttr("mirrorGrp.sz", -1)
    else:
        mc.setAttr("mirrorGrp.sy", -1)

    mc.ungroup("mirrorGrp")

def duplicateList(list):
    #duplicate special first
    """
    settings will be
    duplicate input graph
    will return the top node dupilcated
    """
    mc.select(list, r = True)
    duplication = mc.duplicate(rr = True, un = True, renameChildren = True)
    return duplication

def printList(listToPrint):
    for item in listToPrint:
        print
        item


def run(ctrl = '', skin = '', direction = 'YZ', mirrorInverse = True):
    if len(ctrl) == 0:
        mirrorList = mc.ls(sl=True)
    else:
        mirrorList = ctrl.split(", ")
    # add mirror at the back of the nameing so we dont get wired clashing:
    for index in range(0, len(mirrorList)):
        item = mirrorList[index]
        mc.rename(item, item + "_mirror")
        mirrorList[index] = item + "_mirror"

    duplication = duplicateList(mirrorList)

    MirrorList = []
    for item in duplication:
        #if "CTL" in item or "LOC" in item or "CRV" in item:
        MirrorList.append(item)
    mirrorListToOtherSide(MirrorList, side = direction)

    # rename first to make evryting unique

    newNames = searchAndReplaceNames(duplication)
    newNames = searchAndReplaceNames(newNames, "L_", "R_")

    # bind new jnts to skin and mirror weight from the other side
    if len(skin) > 0:
        bindJnts = findBindJnts(newNames)
        # get skin cluster name:
        skinHistoryList = mc.listHistory(skin)
        if bindJnts:
            for item in skinHistoryList:
                if mc.nodeType(item) == "skinCluster":
                    skinClusterName = item

            printList(bindJnts)
            for jnt in bindJnts:
                mc.skinCluster(skinClusterName, e=True, lw=True, wt=0, ai=jnt)
            mc.copySkinWeights(ss=skinClusterName, ds=skinClusterName, mirrorMode=direction,
                               mirrorInverse=not mirrorInverse)

    # rename everything back:
    for item in mirrorList:
        oldname = item[:-7]
        mc.rename(item, oldname)

    for item in duplication:
        mirroredName = item.replace("l_", "r_").replace("L_", "R_")
        print mirroredName
        newName = mirroredName[:-8]
        mc.rename(mirroredName, newName)



