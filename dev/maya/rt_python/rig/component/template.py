"""
name: template.py

Author: Ehsan Hassani Moghaddam

History:

04/26/16 (ehassani)     first release!

"""
import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib

reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Template(object):
    """
    base class of all templates
    """

    def __init__(self, side='C', prefix='template', verbose=False, **kwargs):
        """
        underlines are used to decide if attributes should be visible to user before
        building the rigs.
        blueprint attrs starting with 3 underlines means user can changes them.
        attrs starting with 2 underlines are hidden from user

        :param prefix: name of the root
        :type prefix: string

        :param verbose: if True prints info as rig is being created
        :type verbose: bool
        """
        self.blueprintGrp = side + '_' + prefix + '_blueprint_GRP'
        self.blueprints = OrderedDict()
        self.blueprintPoses = OrderedDict()
        self.joints = OrderedDict()
        self.controls = OrderedDict()
        self.__side = side
        self.__prefix = prefix
        self.name = side + '_' + prefix
        self.verbose = verbose

        if self.verbose:
            strLib.printBigTitle(mode="info",
                                 message='Creating {}, "{}_{}"'.format(self.__class__.__name__, side, prefix),
                                 separator="=",
                                 repeatation=100)

        # create blueprint
        self.createBlueprint()

        # settings that will be shown to user in rigCreator window
        self.createSettings()

    @staticmethod
    def getLastTemplateNumber():
        bluGrps = mc.ls('*blueprint_GRP')
        orders = []
        for x in bluGrps:
            order = attrLib.getAttr(x + '.blu_order', verbose=False) or 0
            orders.append(order)
        return max(orders)

    @staticmethod
    def createGrp(name="empty_GRP", parent="", pivot_matrix=None, forceRecreate=True):
        """
        create groups and parent them
        :return: full path to the newly created group
        """

        if mc.objExists(name):
            if forceRecreate:
                mc.delete(name)
            else:
                return name

        grp = mc.createNode('transform', n=name, p=parent)

        if pivot_matrix:
            trsLib.setMatrix(grp, pivot_matrix)

        return grp

    @staticmethod
    def outToName(out):
        """
        if given string has "." it means it's pointing to another nodes's value
        so get that value and return it, but if it's a hardcoded string without "."
        then, return that string

        eg: outToName('root.mainCtl') -> 'C_main_CTL'
            outToName('C_body_CTL') -> 'C_body_CTL'
        """
        if not isinstance(out, basestring):
            return out

        tokens = out.split('.')

        if len(tokens) == 2:  # value is the output of another component
            node = tokens[0] + '_blueprint_GRP'
            a = 'out_' + tokens[1]
            if mc.attributeQuery(a, node=node, exists=True):
                value = mc.getAttr(node + '.' + a)
            else:
                logger.warning('"{}.{}" does not exist!'.format(node, a))
                return None

        else:  # value is hardcoded
            value = out

        return value

    def createGrps(self):
        # create main groups
        self.createGrp(name="rig_GRP", forceRecreate=False)
        self.createGrp(name="geometry_GRP", parent="rig_GRP", forceRecreate=False)
        # self.createGrp(name="proxy_model_GRP", parent="geometry_GRP", forceRecreate=False)
        # self.createGrp(name="anim_model_GRP", parent="geometry_GRP", forceRecreate=False)
        # self.createGrp(name="render_model_GRP", parent="geometry_GRP", forceRecreate=False)
        self.createGrp(name="control_GRP", parent="rig_GRP", forceRecreate=False)
        self.createGrp(name="setup_GRP", parent="rig_GRP", forceRecreate=False)
        self.createGrp(name="origin_GRP", parent="setup_GRP", forceRecreate=False)
        self.createGrp(name="module_GRP", parent="setup_GRP", forceRecreate=False)
        self.createGrp(name="setting_GRP", parent="setup_GRP", forceRecreate=False)
        mc.setAttr("origin_GRP.inheritsTransform", 0)

        # create sub groups
        name = self.getName()
        self.ctlGrp = self.createGrp(name + '_control_GRP', parent='control_GRP')
        self.moduleGrp = self.createGrp(name + '_module_GRP', parent='module_GRP')
        self.originGrp = self.createGrp(name + '_origin_GRP', parent='origin_GRP')
        self.settingGrp = self.createGrp(name + '_setting_GRP', parent='setting_GRP')

    def getName(self, v=None):
        """
        creates and returns a name based on self.__side, self.__prefix and given value
        eg: getName('hello')
            # result: "c_root_hello"
        """
        # get name based on side and prefix
        n = self.__side + '_' + self.__prefix
        if v:
            n = n + '_' + v
        return n

    def createBlueprint(self):
        if self.verbose:
            print '\t# {}.createBlueprint(), "{}"'.format(self.__class__.__name__, self.__prefix)

        if not mc.objExists('blueprint_GRP'):
            mc.createNode('transform', n='blueprint_GRP')
        if not mc.objExists(self.blueprintGrp):
            mc.createNode('transform', n=self.blueprintGrp, p='blueprint_GRP')

    def findBlueprints(self):
        """
        find location of blueprints, this will error if blueprints don't exist.
        """
        for alias, blueprint in self.blueprints.items():
            self.blueprintPoses[alias] = trsLib.getTRS(blueprint, space='world')

    def createJoints(self):
        pass

    def deleteOldRig(self):
        self.createGrps()
        oldRig = mc.ls(self.ctlGrp, self.moduleGrp, self.originGrp, self.settingGrp)
        if oldRig:
            mc.delete(oldRig)

    def build(self):
        """
        step 2 for creating rigs, this is the main function of template class
        which creates the rig based on user inputs and blueprints
        """

        if self.verbose:
            print '\t# {}.build(), "{}_{}"'.format(self.__class__.__name__, self.__side, self.__prefix)

        # read attrs from blueprint group
        self.getAttrsFromBlueprint()

        self.createGrps()

        self.findBlueprints()

        self.createJoints()

    def connect(self):
        """
        connection of created nodes
        """
        if self.verbose:
            print '\t# {}.connect(), "{}_{}"'.format(self.__class__.__name__, self.__side, self.__prefix)

        name = self.getName()
        controlGrp = name + '_control_GRP'

        # read attrs from blueprint group
        self.getAttrsFromBlueprint()

        # copy blueprint attributes on control group
        attrs = mc.listAttr(self.blueprintGrp, st='blu_*') or []
        for attr in attrs:
            attrLib.duplicateAttr(source=self.blueprintGrp + '.' + attr, target=controlGrp)

    def getAttrsFromBlueprint(self):
        """
        read attrs from blueprint group
        """
        # get all the attributes that have 2 or more underlines from blueprint group
        # and store them in class instance so they're available using self
        attrs = mc.listAttr(self.blueprintGrp, st='blu_*') or []
        for attr in attrs:

            # get attr value
            classAttr = attr.split('blu_')[-1]
            v = self.getOut(classAttr)
            self.__dict__[classAttr] = v

    def setOut(self, attr, value):
        """
        used when we want things from this component be available to other components
        """
        attrLib.addString(self.blueprintGrp, 'out_' + attr, lock=True)
        attrLib.setAttr(self.blueprintGrp + '.out_' + attr, value)

    def getOut(self, attr, error=True):
        """
        used to get access to things from other components
        """
        if mc.attributeQuery('out_' + attr, node=self.blueprintGrp, exists=True):
            attr = 'out_' + attr
        elif mc.attributeQuery('blu_' + attr, node=self.blueprintGrp, exists=True):
            attr = 'blu_' + attr
        elif error:
            mc.error('Could not find "..._{0}" on "{1}"'.format(
                attr, self.blueprintGrp))
        else:
            mc.warning('Could not find "..._{0}" on "{1}"'.format(
                attr, self.blueprintGrp))
            return

        v = mc.getAttr(self.blueprintGrp + '.' + attr)
        if not v:
            return

        at = attrLib.getAttrType(self.blueprintGrp + '.' + attr)

        if at == 'string':
            if v.startswith('{'):  # value is a dict
                vDict = eval(v)
                values = {}
                for key, val in vDict.items():
                    if isinstance(val, basestring):  # value of current key is a string
                        values[key] = self.outToName(val)
                    elif isinstance(val, list):  # value of current key is a list
                        values[key] = [self.outToName(x) for x in val]
                    else:  # value is a number probably
                        values[key] = val

            elif v.startswith('['):  # value is a list
                values = [self.outToName(x) for x in eval(v)]

            else:  # value is one string
                values = self.outToName(v)

        elif at == 'enum':
            v = mc.getAttr(self.blueprintGrp + '.' + attr, asString=True)
            values = self.outToName(v)
        else:
            values = self.outToName(v)
        return values

    def createSettings(self):
        """
        returns the list of attributes that will be displayed
        in the rigCreator UI so user can change settings. Only
        attributes that start 3 underlines will be displayed in the UI
        """
        attrLib.addString(self.blueprintGrp, 'blu_type', v=self.__class__.__name__, lock=True)
        attrLib.addInt(self.blueprintGrp, 'blu_order', lock=True)
        attrLib.addBool(self.blueprintGrp, 'blu_verbose', v=self.verbose)
        attrLib.addString(self.blueprintGrp, 'blu_side', v=self.__side)
        attrLib.addString(self.blueprintGrp, 'blu_prefix', v=self.__prefix)

        attrLib.setAttr(self.blueprintGrp + '.blu_order', self.getLastTemplateNumber() + 1)

    @property
    def side(self):
        return self.__side

    @side.setter
    def side(self, val):
        # update instance properties
        self.__side = val
        self.name = self.getName()

        # rename bluprint group
        self.blueprintGrp = mc.rename(self.blueprintGrp, val + self.blueprintGrp[1:])

        # rename bluprints
        for obj in mc.listRelatives(self.blueprintGrp, ad=True):
            mc.rename(obj, val + obj[1:])

        # update blueprint attributes in Maya
        attrLib.setAttr(self.blueprintGrp + '.blu_side', val)
        self.updateInputVal()

        # update bluprint dictionary
        self.createBlueprint()

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, val):
        # update instance properties
        self.__prefix = val
        self.name = self.getName()

        # rename bluprint group
        tokens = self.blueprintGrp.split('_')
        newName = '_'.join([self.name] + tokens[2:])
        self.blueprintGrp = mc.rename(self.blueprintGrp, newName)

        # rename bluprints
        for obj in mc.listRelatives(self.blueprintGrp, ad=True):
            tokens = obj.split('_')
            newName = '_'.join([self.name] + tokens[2:])
            mc.rename(obj, newName)

        # update blueprint attributes in Maya
        attrLib.setAttr(self.blueprintGrp + '.blu_prefix', val)
        self.updateInputVal()

        # update bluprint dictionary
        self.createBlueprint()

    def renameBluprint(self, search, replace):

        objs = mc.listRelatives(self.blueprintGrp, ad=True)
        for obj in objs:
            mc.rename(obj, obj.replace(search, replace, 1))

        self.blueprintGrp = mc.rename(self.blueprintGrp, obj.replace(search, replace))

    def updateInputVal(self):
        for k, v in self.blueprints.items():
            tokens = v.split('_')
            newName = '_'.join([self.name] + tokens[2:])
            self.blueprints[k] = newName
        attrLib.setAttr(self.blueprintGrp + '.blu_inputs', self.blueprints)