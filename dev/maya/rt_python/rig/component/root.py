"""
name: root.py

Author: Ehsan Hassani Moghaddam

History:
    04/23/16 (ehassani)     first release!

"""
import maya.cmds as mc

from ...lib import control
from ...lib import strLib
from ...lib import attrLib
from ...lib import connect
from ...lib import trsLib
from . import template

reload(control)
reload(strLib)
reload(attrLib)
reload(connect)
reload(template)
reload(trsLib)


class Root(template.Template):
    """
    class to create necessary upper groups of the rig
    """

    def __init__(self, prefix='root', **kwargs):
        kwargs['prefix'] = prefix
        super(Root, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Root, self).createBlueprint()

        # get name
        name = self.getName()

        # add blueprint attrs
        # this data will be used to initialize the class later
        self.blueprints['base'] = '{}_BLU'.format(name)
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

        # create input blueprints
        if not mc.objExists(self.blueprints['base']):
            mc.joint(self.blueprintGrp, name=self.blueprints['base'])
            mc.xform(self.blueprints['base'], ws=True, t=(0, 10, 0))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        self.joints['base'] = self.side + '_root_JNT'
        mc.joint(self.moduleGrp, n=self.joints['base'])
        trsLib.setTRS(self.joints['base'], self.blueprintPoses['base'])
        self.setOut('rootJnt', self.joints['base'])

    def build(self):
        super(Root, self).build()

        # group model group
        if mc.objExists('model_GRP') and mc.objExists('geometry_GRP'):
            try:
                mc.parent('model_GRP', 'geometry_GRP')
            except:
                pass

        # get size
        if mc.objExists('model_GRP'):
            # get size from geos under model_GRP
            objs = mc.listRelatives('model_GRP', ad=True, type='mesh')
            size = trsLib.getSizeFromBoundingBox(objs=objs)
        else:
            # use Y position of bluprint to calculate size of control
            size = self.blueprintPoses['base'][0][1] * 0.8

        # create controls
        mainCtl = control.Control(
            side="c",
            descriptor="main",
            shape="triangle",
            color="purple",
            scale=[size*0.1, size*0.1, size*0.1],
            parent=self.ctlGrp,
            lockHideAttrs=['v'],
            verbose=self.verbose).name
        self.setOut('mainCtl', mainCtl)

        bodyCtl = control.Control(
            side="c",
            descriptor="body",
            shape="square",
            scale=[size*0.6, size*0.6, size*0.6],
            trs=self.blueprintPoses['base'],
            lockHideAttrs=['s', 'v'],
            parent=mainCtl,
            verbose=self.verbose).name
        self.setOut('bodyCtl', bodyCtl)

        # drive joints with controls
        mc.parentConstraint(bodyCtl, self.joints['base'], mo=True)

    def connect(self):
        """
        connection of created nodes 
        """

        super(Root, self).connect()

        # get handle to outputs
        mainCtl = self.getOut('mainCtl')

        # global scale
        mc.connectAttr(mainCtl + ".scale", "setup_GRP.scale")

        if mc.objExists('C_main_CTL'):
            attrLib.addSeparator('C_main_CTL', 'extra')

            # geo visibility swtich
            a = attrLib.addFloat('C_main_CTL', 'uniformScale', min=0.01, dv=1)
            [attrLib.connectAttr(a, 'C_main_CTL.s'+x) for x in 'xyz']
            attrLib.lockHideAttrs('C_main_CTL', attrs=['s'])

            # geo visibility swtich
            a = attrLib.addEnum('C_main_CTL', 'geoVis', en=['off', 'on'], dv=1)
            mc.connectAttr(a, 'geometry_GRP.v')

            # rig visibility swtich
            a = attrLib.addEnum('C_main_CTL', 'rigVis', en=['off', 'on'], dv=1)
            mc.connectAttr(a, 'setup_GRP.v')

            # geo selectablity swtich
            a = attrLib.addEnum('C_main_CTL', 'geoSelectable', en=['off', 'on'])
            connect.reverse(a, "geometry_GRP.overrideEnabled")
            mc.setAttr("geometry_GRP.overrideDisplayType", 2)

            # rig selectablity swtich
            a = attrLib.addEnum('C_main_CTL', 'rigSelectable', en=['off', 'on'])
            connect.reverse(a, "setup_GRP.overrideEnabled")
            mc.setAttr("setup_GRP.overrideDisplayType", 2)

        # fit rig into viewport
        mc.viewFit(all=True)

    def createSettings(self):
        super(Root, self).createSettings()
