# =================================================================================
"""
Script Name: poser

Author: Ehsan HM - hm.ehsan@yahoo.com

What does it do?
	helps to select all animatable controls of characters. Mirror, Flip or resetAll poses

How does it work?
	select at least one control on your character, then try UI buttons.
	
"""
# =================================================================================


import maya.cmds as mc
from functools import partial

# from codes.python.util.transform import matchTransform
#
# MatchTransform = matchTransform.MatchTransform


class Poser():
    # list of node types that if are connected as input to our attributes, we can still change the attributes' values
    alterableInputTypes = mc.nodeType('animCurve', derived=True, isTypeName=True)
    alterableInputTypes.append('character')

    def __init__(self, UI=True, *args, **kwargs):

        if UI:
            self.UI()

    def UI(self):

        # create window
        if mc.window('ehm_Poser_UI', exists=True):
            mc.deleteUI('ehm_Poser_UI')
        mc.window('ehm_Poser_UI', title='Pose Tools', w=400, h=235, mxb=False, mnb=True, sizeable=True)

        # main layout
        # mainLayout = mc.rowColumnLayout()
        formLayout = mc.formLayout(w=400, h=235)
        frameLayout = mc.frameLayout(borderStyle='etchedIn', labelVisible=False)
        mc.setParent(formLayout)

        # select and default buttons
        self.selectAndDefaultText = mc.text(label='Selection: ', align='right')
        self.selectAllButton = mc.button(label='Select All', h=30, backgroundColor=[0.5, 0.7, 0.5],
                                         c=self.selectAllControls)
        self.setDefaultButton = mc.button(label='Set Default Pose', h=30, backgroundColor=[0.5, 0.7, 0.5],
                                          c=self.setDefaultPose)

        # reset buttons
        self.resetText = mc.text(label='Resets: ', align='right')
        self.resetAllButton = mc.button(label='Reset All Attributes', h=30, backgroundColor=[0.7, 0.5, 0.5],
                                        c=self.resetAllAttributes)
        self.resetSRTButton = mc.button(label='Reset SRT', h=30, backgroundColor=[0.7, 0.5, 0.5],
                                        c=self.resetTransformAttributes)

        # reset and mirror mode separator
        self.resetMirrorSEP = mc.separator(style='out')

        # mirror mode radio buttons
        self.mirrorModeText = mc.text(label='Mirror Mode: ', align='right')
        self.mirrorModeRC = mc.radioCollection()
        self.behaviorRB = mc.radioButton(label="Behavior", select=True)
        self.orientationRB = mc.radioButton(label="Orientation")
        self.hybridRB = mc.radioButton(label="Hybrid")

        # flip and mirror buttons
        self.mirrorText = mc.text(label='Mirror: ', align='right')
        self.flipButton = mc.button(label='Flip', h=30, backgroundColor=[0.5, 0.5, 0.7],
                                    c=partial(self.flip_pose, True))
        self.mirrorButton = mc.button(label='Mirror', h=30, backgroundColor=[0.5, 0.5, 0.7],
                                      c=partial(self.mirror_pose, True))

        # match fk ik separator
        self.matchfkikSEP = mc.separator(style='out')

        # match fk ik buttons
        self.matchfkikText = mc.text(label='Match fk ik: ', align='right')
        self.matchfkikButton = mc.button(label='fk <---> ik   ,   ik <---> fk', h=30, backgroundColor=[0.4, 0.3, 0.6],
                                         c=self.matchfkik)

        # place frame layout
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'left', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'right', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'top', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'bottom', 3))

        # place select and default buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.selectAndDefaultText, 'right', 0, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.selectAndDefaultText, 'top', 30))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.selectAllButton, 'left', 2, 30))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.selectAllButton, 'right', 2, 65))
        mc.formLayout(formLayout, edit=True, attachForm=(self.selectAllButton, 'top', 20))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.setDefaultButton, 'left', 2, 65))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.setDefaultButton, 'right', 8, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.setDefaultButton, 'top', 20))

        # palce reset buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetText, 'right', 0, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.resetText, 'top', 65))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetAllButton, 'left', 2, 30))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetAllButton, 'right', 2, 65))
        mc.formLayout(formLayout, edit=True, attachForm=(self.resetAllButton, 'top', 55))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetSRTButton, 'left', 2, 65))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetSRTButton, 'right', 8, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.resetSRTButton, 'top', 55))

        # place reset and mirror mode separator
        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetMirrorSEP, 'left', 2, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.resetMirrorSEP, 'right', 2, 99))
        mc.formLayout(formLayout, edit=True, attachForm=(self.resetMirrorSEP, 'top', 105))

        # place mirror mode radio buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.mirrorModeText, 'right', 0, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.mirrorModeText, 'top', 115))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.behaviorRB, 'left', 2, 30))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.behaviorRB, 'right', 2, 55))
        mc.formLayout(formLayout, edit=True, attachForm=(self.behaviorRB, 'top', 115))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.orientationRB, 'left', 2, 55))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.orientationRB, 'right', 8, 80))
        mc.formLayout(formLayout, edit=True, attachForm=(self.orientationRB, 'top', 115))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.hybridRB, 'left', 2, 80))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.hybridRB, 'right', 8, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.hybridRB, 'top', 115))

        # palce mirror buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.mirrorText, 'right', 0, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.mirrorText, 'top', 145))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.flipButton, 'left', 2, 30))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.flipButton, 'right', 2, 65))
        mc.formLayout(formLayout, edit=True, attachForm=(self.flipButton, 'top', 135))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.mirrorButton, 'left', 2, 65))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.mirrorButton, 'right', 8, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.mirrorButton, 'top', 135))

        #  place match fkik separator
        mc.formLayout(formLayout, edit=True, attachPosition=(self.matchfkikSEP, 'left', 2, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.matchfkikSEP, 'right', 2, 99))
        mc.formLayout(formLayout, edit=True, attachForm=(self.matchfkikSEP, 'top', 180))

        # place match fk ik buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.matchfkikText, 'right', 2, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.matchfkikText, 'top', 200))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.matchfkikButton, 'left', 2, 30))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.matchfkikButton, 'right', 8, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.matchfkikButton, 'top', 195))

        # show window
        mc.showWindow('ehm_Poser_UI')

    # set default values for all selected objects' attributes
    def resetAllAttributes(self, *args):

        objs = mc.ls(sl=True)

        for obj in objs:

            allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
            userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

            for attr in allAttrs:

                # if attribute has incomming connections, go to next attribute, unless incomming connections is comming from character set
                inConnections = mc.listConnections(obj.attr(attr), d=False, s=True)
                if inConnections:
                    if not (self.alterableInputTypes):
                        continue

                if attr not in userAttrs:  # match main attributes
                    try:
                        if attr == 'visibility':
                            pass
                        elif ('scale' in attr.lower()):
                            obj.attr(attr).set(1)
                        else:
                            obj.attr(attr).set(0)
                    except:
                        mc.warning(
                            "ehm_tools...resetAllPose: Could not resetAll some of transform attributes, skipped! \t %s" % obj)
                else:  # find and resetAll user defined attributes
                    try:
                        # pass typed attributes
                        typed = mc.addAttr(obj.attr(attr), q=True, attributeType=True)
                        if typed == 'typed':
                            continue
                        # get default value and set it
                        value = mc.addAttr(obj.attr(attr), q=True, defaultValue=True)
                        obj.attr(attr).set(value)
                    except:
                        mc.warning(
                            "ehm_tools...resetAllPose: Could not resetAll some of user defined attributes, skipped! \t %s" % obj)

    # set default values for all selected objects' attributes
    def resetTransformAttributes(self, *args):

        objs = mc.ls(sl=True)

        for obj in objs:

            allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
            userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

            for attr in allAttrs:

                # if attribute has incomming connections, go to next attribute, unless incomming connections is comming from character set
                inConnections = mc.listConnections(obj.attr(attr), d=False, s=True)
                if inConnections:
                    if not (self.alterableInputTypes):
                        continue

                if attr not in userAttrs:  # match main attributes
                    try:
                        if attr == 'visibility':
                            pass
                        elif ('scale' in attr.lower()):
                            obj.attr(attr).set(1)
                        else:
                            obj.attr(attr).set(0)
                    except:
                        mc.warning(
                            "ehm_tools...resetAllPose: Could not resetAll some of transform attributes, skipped! \t %s" % obj)
                else:  # do not reset user defined attributes
                    continue

    # get top parent
    def topParent(self, obj, *args):
        tempFather = obj.getParent()
        father = None
        while tempFather:
            father = tempFather
            tempFather = tempFather.getParent()
        return father

    # get all name spaces
    def getNameSpace(self, obj, *args):
        objName = obj.name()
        if len(objName.split(':')) > 1:
            return objName.split(':')[0]
        else:
            return None

    # find and select all animatable controls based on selected object
    def selectAllControls(self, objs=None, method='hierarchy', suffix='ctrl', *args):

        suffixes = ['ctrl', 'Ctrl', 'CTRL', 'anim', 'Anim']

        if not objs:
            objs = mc.ls(sl=True)
        else:
            objs = mc.ls(objs)

        objList = []
        if method == 'reference':  # select all animatable control and joints in the same referenced character
            for obj in objs:
                # guess control suffix accoriding to selection, else uses 'ctrl' suffix
                guessedSuffix = obj.name()[-4:]
                if guessedSuffix in suffixes:
                    suffix = guessedSuffix

                character = self.getNameSpace(obj)
                if character:
                    objList.append(mc.ls(('%s:*_%s' % (character, suffix)), type=['transform', 'joint']))
                # objList.append( mc.ls( ( '%s:*_%s'%(character,suffix[0].lower(),suffix[1:]) ), type=['transform', 'joint'] ) )
                else:
                    objList.append(obj)

        elif method == 'hierarchy':  # select all animatable control and joints in the same hierarchy of selected object
            fathers = []
            for obj in objs:
                # guess control suffix accoriding to selection, else uses 'ctrl' suffix
                guessedSuffix = obj.name()[-4:]
                if guessedSuffix in suffixes:
                    suffix = guessedSuffix

                father = self.topParent(obj)
                if not father:  # if selected object is the same as top parent, take it as top parent
                    father = obj
                if father not in fathers:  # don't loop through same character over and over
                    neighbours = mc.listRelatives(father, ad=True, type=['transform', 'joint'])
                    neighbours.append(father)
                    for neighbour in neighbours:
                        if neighbour.name().rpartition(suffix)[-2] == suffix and not \
                        neighbour.name().rpartition(suffix)[-1]:  # find '*suffix' not '*suffix*'
                            objList.append(neighbour)
                        else:
                            objList.append(obj)
                    fathers.append(father)  # don't loop through same character over and over
        mc.select(objList)

    # find object's mirrored object, if None found, return object itself
    def findMirror(self, obj, *args):
        prefixes = {'L_': 'R_', 'Lf': 'Rt'}

        nameSpaceAndName = obj.name().split(":")
        if len(nameSpaceAndName) > 1:
            objNameSpace = nameSpaceAndName[0]
            objName = nameSpaceAndName[1]
        else:
            objName = obj.name()

        name = None
        for i in prefixes:  # If prefix 'L_', finds 'R_'. If prefix 'Lf', finds 'Rt' and so on
            if objName[:2] == i and mc.objExists(obj.name().replace(i, prefixes[i])):
                name = obj.name().replace(i, prefixes[i])
            elif objName[:2] == prefixes[i] and mc.objExists(obj.name().replace(prefixes[i], i)):
                name = obj.name().replace(prefixes[i], i)
            if name:
                break
        if not name:
            # name = obj.name()
            return None

        return name

    # create a locator under given object and resets it's transforms
    def createChildLoc(self, father, *args):
        loc = mc.spaceLocator()
        mc.parent(loc, father)
        loc.translate.set(0, 0, 0)
        loc.rotate.set(0, 0, 0)
        return loc

    # takes current values from user defined attributes and sets it as the default value for them.
    def setDefaultPose(self, *args):

        objs = mc.ls(sl=True)

        for obj in objs:

            allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
            userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

            for attr in allAttrs:
                if mc.connectionInfo(obj.attr(attr), isDestination=True):
                    pass
                if attr in userAttrs:  # match main attributes
                    try:
                        value = obj.attr(attr).get()
                        mc.addAttr(obj.attr(attr), e=True, dv=value)
                    except:
                        mc.warning(
                            "ehm_tools...setDefaultPose: Could not set some of user defined attributes, skipped! \t %s" % obj)

    def matchfkik(self, objs=None, *args):
        objs = mc.ls(sl=True)

        for obj in objs:
            name = obj.name()

            # find out whether "fk" and "ik" in control names is lower case or upper case
            if ('ik' in name) or ('fk' in name):
                ik = 'ik'
                fk = 'fk'
            elif ('ik' in name) or ('fk' in name):
                ik = 'ik'
                fk = 'fk'
            else:
                mc.warning("Make sure your controls have 'ik' or 'fk' in their name")
                continue

            if ik in name:  # iktofk
                try:
                    MatchTransform(folower=obj, lead=mc.PyNode(name.replace(ik, fk)))
                except:
                    pass  # mc.error( "The only difference between ik and fk control names must be 'ik' and 'fk', for example: 'L_hand_ik_ctrl' and 'L_hand_fk_ctrl'." )

            elif fk in name:  # fktoik
                try:
                    obj.rotate.set(mc.PyNode(name.replace('fk_ctrl', 'ik_jnt')).rotate.get())
                    obj.scale.set(mc.PyNode(name.replace('fk_ctrl', 'ik_jnt')).scale.get())
                except:
                    try:
                        obj.rotate.set(mc.PyNode(name.replace('fk_ctrl', 'ik_jnt')).rotate.get())
                        obj.length.set(mc.PyNode(name.replace('fk_ctrl', 'ik_jnt')).scaleX.get())
                    except:
                        mc.error(
                            "The only difference between fk control and ik joint names must be 'fk_ctrl' and 'ik_jnt', for example: 'L_hand_fk_ctrl' and 'L_hand_ik_jnt'.")

    def mirror_pose(self, mirrorMode='behavior', *args):

        try:
            selectedItem = mc.radioCollection(self.mirrorModeRC, q=True, select=True)
            mirrorModeInUI = (mc.radioButton(selectedItem, q=True, label=True)).lower()
        except:
            pass

        objs = mc.ls(sl=True)

        for obj in objs:
            name = self.findMirror(obj)  # find mirrored object's name

            if not name:
                continue

            mirrorMode = mirrorModeInUI
            mirrorModeAttrExists = mc.attributeQuery('mirrorMode', node=obj, exists=True)
            if mirrorModeAttrExists:
                mirrorMode = obj.mirrorMode.get()

            # get object's attributes
            allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
            userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

            for attr in allAttrs:
                if mc.connectionInfo(mc.PyNode(name).attr(attr), isDestination=True):
                    pass
                if attr not in userAttrs:  # match main attributes
                    try:
                        value = obj.attr(attr).get()

                        if attr == 'visibility':  # no need to mirror visibility
                            pass

                        elif attr == 'translateX':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)

                        elif attr == 'translateY':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)

                        elif attr == 'translateZ':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)

                        elif attr == 'rotateX':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)

                        elif attr == 'rotateY':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(value)

                        elif attr == 'rotateZ':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)

                        else:
                            mc.PyNode(name).attr(attr).set(value)

                    except:
                        mc.error('ehm_tools...mirrorPose: Mirror failed on main attributes!')

                for userAttr in userAttrs:  # find and match user defined attributes
                    try:
                        value = obj.attr(userAttr).get()
                        mc.PyNode(name).attr(userAttr).set(value)
                    except:
                        mc.error('ehm_tools...mirrorPose: Mirror failed on user defined attributes!')

    def flip_pose(self, mirrorMode=True, *args):

        try:
            selectedItem = mc.radioCollection(self.mirrorModeRC, q=True, select=True)
            mirrorModeInUI = (mc.radioButton(selectedItem, q=True, label=True)).lower()
        except:
            pass

        objs = mc.ls(sl=True)

        flippedObjs = []  # list of objects already flipped

        for obj in objs:

            mirrorMode = mirrorModeInUI
            mirrorModeAttrExists = mc.attributeQuery('mirrorMode', node=obj, exists=True)
            if mirrorModeAttrExists:
                mirrorMode = obj.mirrorMode.get()

            name = self.findMirror(obj)  # find mirrored object's name

            if name in flippedObjs:  # prevent object to get flipped twice
                continue
            flippedObjs.append(obj)

            # get object's attributes
            allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
            userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

            if not name:  # if mirror not found go to next object

                # 1. create 3 locators representing Position, aimVector and upVector
                pos = self.createChildLoc(obj)
                aim = self.createChildLoc(obj)
                upv = self.createChildLoc(obj)

                # 2. get the flip plane from our control object, default is YZ. place aim and up vectors accordingly
                try:
                    flipPlane = obj.mirrorPlane.get()
                except:
                    flipPlane = 'YZ'

                if flipPlane == 'YZ':
                    aim.translateZ.set(1)
                    upv.translateY.set(1)

                elif flipPlane == 'XZ':
                    aim.translateX.set(1)
                    upv.translateZ.set(1)

                elif flipPlane == 'XY':
                    aim.translateX.set(1)
                    upv.translateY.set(1)

                # 3. parent locators under control's parent. They should be in the same group as our control object we want to flip

                try:
                    controlParent = obj.getParent()
                except:
                    controlParent = None

                if controlParent:
                    mc.parent(pos, controlParent)
                    mc.parent(aim, controlParent)
                    mc.parent(upv, controlParent)

                # 4. group all locators and scale the group according to our flip plane

                grp = mc.group(pos, aim, upv)
                mc.xform(grp, os=True, piv=(0, 0, 0))

                if flipPlane == 'YZ':
                    grp.scaleX.set(-1)
                elif flipPlane == 'XZ':
                    grp.scaleY.set(-1)
                elif flipPlane == 'XY':
                    grp.scaleZ.set(-1)

                # 5. create point and aim constraints to achieve the pose on a null object and apply the values to our control

                result = mc.group(empty=True)

                result.rotateOrder.set(obj.rotateOrder.get())

                if controlParent:
                    mc.parent(result, controlParent)
                mc.pointConstraint(pos, result)

                if flipPlane == 'YZ':
                    mc.aimConstraint(aim, result, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType="object",
                                     worldUpObject=upv)
                elif flipPlane == 'XZ':
                    mc.aimConstraint(aim, result, aimVector=[1, 0, 0], upVector=[0, 0, 1], worldUpType="object",
                                     worldUpObject=upv)
                elif flipPlane == 'XY':
                    mc.aimConstraint(aim, result, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="object",
                                     worldUpObject=upv)

                result.scale.set(obj.scale.get())

                # get object's attributes
                allAttrs = mc.listAttr(obj, keyable=True, unlocked=True)
                userAttrs = mc.listAttr(obj, ud=True, unlocked=True)

                for attr in allAttrs:
                    try:
                        obj.attr(attr).set(result.attr(attr).get())
                    except:
                        continue

                # 6. delete extra nodes
                mc.delete(grp, result)
                continue

            for attr in allAttrs:
                if mc.connectionInfo(mc.PyNode(name).attr(attr), isDestination=True):
                    pass
                if attr not in userAttrs:  # match main attributes
                    try:
                        otherValue = mc.PyNode(name).attr(attr).get()
                        value = obj.attr(attr).get()
                        if attr == 'visibility':  # no need to mirror visibility
                            pass

                        elif attr == 'translateX':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)

                        elif attr == 'translateY':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)

                        elif attr == 'translateZ':  # translate x is always reversed
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)

                        elif attr == 'rotateX':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)

                        elif attr == 'rotateY':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)

                        elif attr == 'rotateZ':
                            if mirrorMode == 'behavior':
                                mc.PyNode(name).attr(attr).set(value)
                                obj.attr(attr).set(otherValue)
                            elif mirrorMode == 'orientation':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)
                            elif mirrorMode == 'hybrid':
                                mc.PyNode(name).attr(attr).set(-value)
                                obj.attr(attr).set(-otherValue)

                        else:
                            mc.PyNode(name).attr(attr).set(value)
                            obj.attr(attr).set(otherValue)

                    except:
                        mc.error('ehm_tools...mirrorPose: Flip failed on main attributes!')


                else:  # match user defined attributes
                    try:
                        otherValue = mc.PyNode(name).attr(attr).get()
                        value = obj.attr(attr).get()
                        mc.PyNode(name).attr(attr).set(value)
                        obj.attr(attr).set(otherValue)
                    except:
                        mc.error('ehm_tools...mirrorPose: Flip failed on user defined attributes!')

        mc.select(objs)
