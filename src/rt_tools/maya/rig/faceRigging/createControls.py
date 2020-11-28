import maya.cmds as mc
from ...lib import connect
reload(connect)

def run(radius='1', grpJntOnly=False, isControllerCircle=True,
                   controlMethod='parent', consType='parent', scaleCons=True):
    selection = mc.ls(sl=True)
    controllersList = []

    jntFix = "_JNT"
    ctlFix = "_CTL"
    locFix = "_LOC"
    ControllerGrpList = []
    locators = []

    for item in selection:
        nameBase = item.replace(jntFix, "").replace("_bind", "").replace("_drv", "")
        controllerName = nameBase + ctlFix
        locatorName = nameBase + locFix
        groupName = nameBase + "_GRP"
        ControllerGrpList.append(groupName)

        # determine the control users want to use:
        if grpJntOnly == False:

            # We have to Create Controller, fisrt check controller type and create controller:
            if isControllerCircle:
                controller = mc.circle(n=controllerName, r=radius)
            else:
                controller = mc.sphere(n=controllerName, r=radius)

                # create other elements:
            mc.spaceLocator(n=locatorName)
            mc.setAttr(locatorName + "Shape.visibility", 0)
            mc.parent(controllerName, locatorName)
            mc.select(locatorName, r=True)
            mc.group(n=groupName)
            mc.matchTransform(groupName, item)

            # now determine how we control the joints
            if controlMethod == "constraint":
                # user want to only constraint joint, we do constraints
                if consType == "point":
                    mc.pointConstraint(controllerName, item)
                if consType == "parent":
                    mc.parentConstraint(controllerName, item)
                if consType == "orient":
                    mc.orientConstraint(controllerName, item)
                if scaleCons:
                    mc.scaleConstraint(controllerName, item)
            elif controlMethod == "parent":
                # user wants to parent the joint we parent the joint to the controller
                mc.parent(item, controllerName)
            else:
                # user want's to do connection:
                connect.connectAllChannel(controllerName, item)
            controllersList.append(controllerName)

        else:
            # we only need to group joint
            mc.spaceLocator(n=locatorName)
            mc.select(locatorName, r=True)
            mc.group(n=groupName)
            mc.matchTransform(groupName, item)
            mc.parent(item, locatorName)
    return ControllerGrpList, controllersList