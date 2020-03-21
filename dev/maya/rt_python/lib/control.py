"""
name: control.py

Author: Ehsan Hassani Moghaddam

History:
    04/23/16 (ehassani)     PEP8 and clean up
    04/21/16 (ehassani)     first release!

"""
import os

import maya.cmds as mc

from . import crvLib
from . import display
from . import trsLib
from . import strLib
from . import attrLib

reload(crvLib)
reload(attrLib)


COLORS = {'C': 'yellow',
          'L': 'blue',
          'R': 'red'}

SECCOLORS = {'C': 'brown',
             'L': 'cyan',
             'R': 'pink'}


class Control(object):
    """
    class for creating control objects
    """

    def __init__(self,
                 descriptor="new",
                 side="C",
                 parent=None,
                 createOffsetGrp=True,
                 shape="circle",
                 size=1.0,
                 scale=(1, 1, 1),
                 orient=(0, 1, 0),
                 moveShape=(0, 0, 0),
                 rotateShape=(0, 0, 0),
                 translate=None,
                 rotate=None,
                 matchTranslate="",
                 matchRotate="",
                 matchScale="",
                 trs=((0, 0, 0), (0, 0, 0), (1, 1, 1)),
                 color=None,
                 useSecondaryColors=False,
                 suffix="CTL",
                 lockHideAttrs=['v'],
                 verbose=False):

        self.verbose = verbose
        self.side = side.upper()
        self.suffix = suffix.upper()
        self._name = self.side + "_" + descriptor + "_" + self.suffix
        self.fullName = self._name  # eg: "|rig_GRP|control_GRP|mainOffset_GRP|C_new_CTL"
        self.parent = parent
        self.scale = [scale[0] * size, scale[1] * size, scale[2] * size]
        self.orient = orient
        self.moveShape = moveShape
        self.rotateShape = rotateShape
        self.shape = shape
        self.zro = ""
        self.zroFullName = ""
        self.createOffsetGrp = createOffsetGrp
        self.matchTranslate = matchTranslate
        self.matchRotate = matchRotate
        self.matchScale = matchScale
        self.translate = translate
        self.rotate = rotate
        self.trs = trs
        self.color = color

        # if flip:
        #     self.orient[1] *= -1 

        # guess color from side if color is not given by user
        if not self.color:
            if useSecondaryColors:
                self.color = SECCOLORS[self.side]
            else:
                self.color = COLORS[self.side]

        # create control
        self.name, self.shape = self.create()

        # set color
        display.setColor(self.shape, self.color)

        # lock and hide attrs
        attrLib.lockHideAttrs(self.fullName, attrs=lockHideAttrs)

    @staticmethod
    def exportCtls(path):
        """
        export all controls from current scene

        usage:
            filePath = "C:/Users/Ehsan/Desktop/ctls.ma"
            control.Control.exportCtls(filePath)
        """
        print('from rt_python.lib import control\ncontrol.Control.exportCtls({})'.format(path))

        # get all controls in the scene
        ctls = mc.ls('*_CTL', '*_Ctl', '*_ctl', '*_CTRL', '*_Ctrl', '*_ctrl', long=True)

        # group all new controls
        grp = mc.createNode('transform', n='control_GRP_temp')

        # tmpCtls = []
        for ctl in ctls:
            # if curve shape has incoming connection, break it
            shapes = crvLib.getShapes(ctl, fullPath=True) or []
            mc.delete(shapes, ch=True)

            # duplicate control
            tmpCtl = mc.duplicate(ctl, name=ctl.split('|')[-1] + '_temp')[0]

            # delete non shape children
            all_children = mc.listRelatives(tmpCtl, fullPath=True) or []
            crv_shape_children = crvLib.getShapes(tmpCtl, fullPath=True) or []
            [mc.delete(x) for x in all_children if x not in crv_shape_children]

            # add _temp to end of shape names
            ctl_shapes = crvLib.getShapes(ctl, fullPath=True) or []
            tmpCtl_shapes = crvLib.getShapes(tmpCtl, fullPath=True) or []
            for s, tmpS in zip(ctl_shapes, tmpCtl_shapes):
                mc.rename(tmpS, s.split('|')[-1] + '_temp')

            #
            attrLib.unlock(tmpCtl, ['t', 'r', 's'])
            mc.parent(tmpCtl, grp)

            # delete children under duplicated controls
            children = mc.listRelatives(tmpCtl, ad=True, fullPath=True, type="nurbsCurve") or []
            for child in children:
                if not mc.nodeType(child) == 'nurbsCurve':
                    try:
                        mc.delete(child)
                    except:
                        pass

        # export all temp controls
        mc.select(grp)
        mc.file(path, f=True, op="v=0;", typ="mayaAscii", es=True)

        mc.delete(grp)
        print('Controls exported successfully!')

    @staticmethod
    def importCtls(path):
        """
        import all controls from current scene
        
        usage:
            filePath = "C:/Users/Ehsan/Desktop/ctls.ma"
            control.Control.importCtls(filePath)
        """
        print('from rt_python.lib import control\ncontrol.Control.importCtls({})'.format(path))

        if not os.path.isfile(path):
            mc.warning('Control shape file "{0}" can not be found, skipped!'.format(path))
            return
        mc.file(path, i=True)
        newCrvsShapes = mc.listRelatives('control_GRP_temp', ad=True, type='nurbsCurve', fullPath=True) or []
        newCrvs = list(set([mc.listRelatives(x, p=True)[0] for x in newCrvsShapes]))

        for newCrv in newCrvs:
            # find old crv
            oldCrv = newCrv.split('|')[-1].replace('_temp', '')
            if not mc.objExists(oldCrv):
                mc.warning('Control "{0}" does not exist , skipped!'.format(oldCrv))
                continue

            old_shapes = crvLib.getShapes(oldCrv, fullPath=True) or []
            new_shapes = crvLib.getShapes(newCrv, fullPath=True) or []

            #
            # mc.delete(old_shapes, ch=True)
            [attrLib.disconnectAttr(x + '.create') for x in old_shapes]

            #
            if old_shapes:
                displaySettings = crvLib.getDisplaySettings(newCrv)

            #
            crvLib.copyShape(newCrv, oldCrv)

            #
            if old_shapes:
                crvLib.setDisplaySettings(oldCrv, *displaySettings)

            # # delete extra old shapes
            # old_shapes = crvLib.getShapes(oldCrv, fullPath=True) or []
            # if len(old_shapes) > len(new_shapes):
            #     mc.delete(old_shapes[len(new_shapes):])

        mc.delete('control_GRP_temp')

        print('Controls imported successfully!')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value == self._name:
            return
        unique_name = strLib.getUniqueName(value)
        self.n = value
        self._rename(unique_name)

    def _getUniqueName(self, value):
        return strLib.getUniqueName(value)

    def _rename(self, value):
        mc.rename(self.fullName, value)  # rename ctl
        self.fullName = self.fullName.replace(self._name, value)  # update ctl.fullName
        self._name = value  # update ctl.name
        if mc.objExists(self.zroFullName):
            zro_new_name = value.replace('CTL', 'ZRO')  # find a name for zro
            mc.rename(self.zroFullName, zro_new_name)  # rename zro
            self.zroFullName = self.zroFullName.replace(self.zro, zro_new_name)
            self.zro = zro_new_name  # update ctl.zro

    def setParent(self, par=""):
        """
        keeps zroFullName and fullName up to date after re parenting
        """

        if par == "world":
            if not trsLib.getParent(self.zro):  # already under world
                return
            mc.parent(self.zro, world=True)
            self.zroFullName = self.zro
            self.fullName = self.zroFullName + "|" + self.name
            self.parent = ''

        if mc.objExists(par):
            parent_fullName = mc.ls(par, long=True)[0][1:]  # remove first "|" to make the fullNames more flexible
            curPar = trsLib.getParent(self.zro, fullPath=True)
            if curPar == parent_fullName:  # already under given parent
                return
            mc.parent(self.zro, parent_fullName)
            self.zroFullName = parent_fullName + "|" + self.zro
            self.fullName = self.zroFullName + "|" + self.name
            self.parent = parent_fullName

        else:
            mc.error('Given parent "{0}" does not exist!'.format(par))

    def setCtlParent(self, parent=""):
        """
        keeps fullName up to date after re parenting
        """
        if mc.objExists(parent):
            parent_fullName = mc.ls(parent, long=True)[0]
            par = mc.listRelatives(self.fullName, parent=True, fullPath=True)
            if par and par[0] == parent_fullName:
                return
            mc.parent(self.fullName, parent_fullName)
            self.fullName = parent_fullName + "|" + self.name

    def addOfsGrp(self):
        """
        create offset group
        """
        n = self.name.replace('CTL', 'ZRO')
        self.zro = mc.group(empty=True, name=n)
        self.zroFullName = "|" + self.zro
        trsLib.match(self.zro, all=self.fullName)
        self.setCtlParent(self.zro)

        if self.parent:
            self.setParent(self.parent)

    def create(self):
        """
        create control with given settings
        returns transform and shape of newly created control
        """
        if self.verbose:
            print('\t\t\tCreating "{}" control'.format(self.name))

        if not mc.objExists(self._name):
            trans, shape = crvLib.create(
                shape=self.shape,
                name=self._name,
                scale=self.scale,
                orient=self.orient,
                move=self.moveShape,
                rotate=self.rotateShape
            )

            # match pose (first trs, then match, then translate - usually only one is enough)
            if self.trs:
                trsLib.setTRS(self.name, self.trs)

            trsLib.match(self.name,
                         t=self.matchTranslate,
                         r=self.matchRotate,
                         s=self.matchScale)
            if self.translate:
                trsLib.setTranslation(self.name, translation=self.translate)
            if self.rotate:
                mc.xform(self.name, worldSpace=True, ro=self.rotate)

            # offset group
            if self.createOffsetGrp:
                self.addOfsGrp()

            # make rotate order keyable and visible in channelbox
            attrLib.lockHideAttrs(self._name, ['rotateOrder'], lock=0, hide=0)
        else:
            trans = self._name
            shape = trsLib.getShapes(self._name)[0]
            mc.warning('"{0}" already exists, skipped!'.format(self._name))
        return trans, shape


def setBorderSize():
    nodes = mc.ls(sl=True)
    for node in nodes:
        line = node.replace('CTL', 'LIN')
        mc.move(1, 0, 0, line + '.cv[0]', r=True, os=True)
        mc.move(1, 0, 0, line + '.cv[1]', r=True, os=True)
        mc.move(1, 0, 0, line + '.cv[5]', r=True, os=True)
