import pymel.core as pm
import maya.cmds as cmds

# __author__: Michael Taylor
def label():
    # label joints

    jointNames = ("_JNT", "_joint", "_bnd", "_Bnd", "_BND", "_Jnt", "_ctrl")

    joints = cmds.ls(long=False, type='joint')
    bnd = []
    for j in joints:
        for jn in jointNames:
            if jn in j:
                bnd.append(j)

    for b in bnd:
        splitted = b.split("_")

        side = splitted[0]

        label = b
        if side == "R" or side == "r":
            cmds.setAttr(b + ".side", 2)

            label = ""
            for s in splitted:
                if s != side:
                    label = label + "_" + s

        elif side == "L" or side == "l":
            cmds.setAttr(b + ".side", 1)

            label = ""
            for s in splitted:
                if s != side:
                    label = label + "_" + s
        elif side == "Face":
            side = splitted[1]

            if side == "R" or side == "r":
                cmds.setAttr(b + ".side", 2)

                label = ""
                for s in splitted:
                    if s != side:
                        label = label + "_" + s

            elif side == "L" or side == "l":
                cmds.setAttr(b + ".side", 1)

                label = ""
                for s in splitted:
                    if s != side:
                        label = label + "_" + s

        cmds.setAttr(b + ".type", 18)
        cmds.setAttr(b + ".otherType", label, type="string")