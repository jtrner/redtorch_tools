"""
Author: Ehsan HM ( hm.ehsan@yahoo.com )

Script Name: ExportImportAnim()

Version: 1.0

What does this do: exports and imports animation of selected objects.

Usage:
import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

from python.anim import exportImportAnim
reload(exportImportAnim)

animUI = exportImportAnim.ExportImportAnim()
animUI.UI()

animUI.importAnim( nameSpace=None, replaceString=None)

"""

import maya.cmds as mc
import sys

from ..lib import fileLib

uad = mc.internalVar(uad=True)
import maya.cmds as mc
from functools import partial


class ExportImportAnim():

    def __init__(self, *args, **kwargs):

        if args or kwargs:
            self.importAnim(*args, **kwargs)
        else:
            self.UI()

    def UI(self):

        # create window
        if mc.window('ehm_ImportAnim_UI', exists=True):
            mc.deleteUI('ehm_ImportAnim_UI')
        mc.window('ehm_ImportAnim_UI', title='Export Import Animatom', w=350, h=40, mxb=False, mnb=True, sizeable=False)

        # main layout
        # mainLayout = mc.rowColumnLayout()
        formLayout = mc.formLayout(w=350, h=40)
        # frameLayout = mc.frameLayout(borderStyle='etchedIn', labelVisible=False)
        mc.setParent(formLayout)

        # buttons
        self.exportButton = mc.button(label='Export', h=30, c=self.exportAnim)
        self.importButton = mc.button(label='Import', h=30, c=lambda: self.importAnim())

        # place buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.exportButton, 'left', 4, 0))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.exportButton, 'right', 2, 50))
        mc.formLayout(formLayout, edit=True, attachForm=(self.exportButton, 'bottom', 5))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.importButton, 'left', 2, 50))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.importButton, 'right', 4, 100))
        mc.formLayout(formLayout, edit=True, attachForm=(self.importButton, 'bottom', 5))

        # show window
        mc.showWindow('ehm_ImportAnim_UI')

    # get character name from selection and write it in character name text field
    def getCharacterName(self, obj, *args):
        if not obj:
            objs = mc.ls(sl=True)
            if objs:
                obj = objs[-1]
        else:
            obj = mc.ls(obj)[-1]
        mc.textField(self.exportModeRBG, e=True, text=self.getNameSpace(obj))

    # get name spaces
    def getNameSpace(self, obj, *args):
        if not obj:
            return None
        try:
            objName = obj
        except:
            objName = obj
        if len(objName.split(':')) > 1:
            return objName.split(':')[0]
        else:
            None

    # check if object's name is unique
    def hasUniqueName(self, obj, *args):
        try:
            objName = obj
        except:
            objName = obj
        if len(objName.split('|')) > 1:
            return False
        else:
            return True

    def importAnim(self, nameSpace=None, replaceString=None, *args):

        successState = True

        #  *.json file
        filePath = mc.fileDialog2(caption='Read Animation', fileMode=1, startingDirectory=uad,
                                  fileFilter="Anim Files (*.json)")

        if not filePath:
            mc.warning('Read animation cancelled.')
            return None

        # read anim info from file
        animInfos = fileLib.loadJson(filePath[0], ordered=True)

        # we can replace some parts of file to use animations on other objects. 
        # for example, replace 'L' with 'R' copy animation from left side to right side. 

        # # replaceString = ('L','R')
        # animInfosSearchAndReplaced = {}
        # if replaceString:
        #     for k, v in animInfos.items():
        #         kk = k.replace(replaceString[0], replaceString[1])
        #         vv = v.replace(replaceString[0], replaceString[1])
        #         animInfosSearchAndReplaced[kk] = vv
        #     animInfos = animInfosSearchAndReplaced

        for obj in animInfos.keys():
            attrs = animInfos[obj].keys()

            for attr in attrs:
                animCurveInfos = animInfos[obj][attr]
                times = animCurveInfos['times']
                values = animCurveInfos['values']
                outWeights = animCurveInfos['outWeights']
                outAngles = animCurveInfos['outAngles']
                inWeights = animCurveInfos['inWeights']
                inAngles = animCurveInfos['inAngles']

                for i in range(len(animCurveInfos['times'])):
                    if nameSpace:
                        attrNode = nameSpace + ':' + attr
                    else:
                        attrNode = attr
                    if not mc.objExists(attrNode):
                        successState = False
                        continue

                    mc.setKeyframe(attrNode, time=times[i], value=values[i])
                    mc.keyTangent(attrNode, e=True, index=(i, i), outWeight=outWeights[i],
                                  outAngle=outAngles[i], inWeight=inWeights[i], inAngle=inAngles[i])
        if successState:
            sys.stdout.write('Animation was successfully imported.')
        else:
            mc.warning('Animation was imported. Not all objects or attributes'
                       ' were the same. So, animation was not applied to them.')

    def exportAnim(self, *args):
        objs = mc.ls(sl=True)
        successState = True

        filePath = mc.fileDialog2(caption='Save Animation', startingDirectory=uad, fileFilter="Anim Files (*.json)")

        if not filePath:
            sys.stdout.write('Save animation cancelled.')
            return None

        animInfos = {}  # dictionary containing dictionaries of every object's animations
        for obj in objs:

            if not (self.hasUniqueName(obj)):  # if object'n name is not unique, doesn't save animation for it
                successState = False
                mc.warning("Object %s's name is not unique. skipped" % obj)
                continue

            nameSpace = self.getNameSpace(obj)
            if nameSpace:
                objName = obj.split(':')[1]
            else:
                objName = obj

            # find all anim curves on the object
            curves = mc.findKeyframe(obj, curve=True)

            if not curves:  # jump to next object if no anim curve found
                continue

            animInfo = {}  # dictionary containing one object's animations

            for curve in curves:  # for each curve, find where it's connected to, keys' times, values and tangents
                attr = mc.listConnections('%s.output' % curve, plugs=True)[0]
                if nameSpace:
                    attrName = attr.split(':')[1]
                else:
                    attrName = attr
                times = mc.keyframe(attr, q=True, timeChange=True)
                values = mc.keyframe(attr, q=True, valueChange=True)
                outWeights = mc.keyTangent(attr, q=True, outWeight=True)
                outAngles = mc.keyTangent(attr, q=True, outAngle=True)
                inWeights = mc.keyTangent(attr, q=True, inWeight=True)
                inAngles = mc.keyTangent(attr, q=True, inAngle=True)
                animInfo[attrName] = {'times': times, 'values': values, 'outWeights': outWeights,
                                      'outAngles': outAngles, 'inWeights': inWeights, 'inAngles': inAngles}

            animInfos[objName] = animInfo

        # write anim info to file
        fileLib.saveJson(filePath[0], animInfos)

        if successState:
            sys.stdout.write('Animation was successfully exported.')
        else:
            mc.warning('Some objects animtions were not saved due to multiple'
                       ' object with the same name, check script editor for more info.')
