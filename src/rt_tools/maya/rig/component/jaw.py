import maya.cmds as mc

from . import template
from ...lib import strLib
from ...lib import attrLib
from ...lib import trsLib
from ...lib import jntLib
from ...lib import control
from ...lib import connect
from ...lib import crvLib
from ...lib import display


reload(display)
reload(crvLib)
reload(connect)
reload(control)
reload(jntLib)
reload(trsLib)
reload(attrLib)
reload(template)
reload(template)



class Jaw(template.Template):

    def __init__(self, side = 'C', prefix = 'jaw',  **kwargs ):
        kwargs['side'] = side
        kwargs['prefix'] = prefix

        self.aliases = {'startJaw': 'startJaw',
                        'midJaw':'midJaw',
                        'endJaw':'endJaw'}

        super(Jaw, self).__init__(**kwargs)

    def createBlueprint(self):

        super(Jaw, self).createBlueprint()

        par = self.blueprintGrp

        self.blueprints['startJaw'] = '{}_startJaw_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['startJaw']):
            mc.joint(self.blueprintGrp, name = self.blueprints['startJaw'])
            mc.xform(self.blueprints['startJaw'], ws = True, t = (0, 20, 0))
        par = self.blueprints['startJaw']

        self.blueprints['midJaw'] = '{}_midJaw_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['midJaw']):
            mc.joint(self.blueprints['startJaw'], name = self.blueprints['midJaw'])
            mc.xform(self.blueprints['midJaw'], ws = True, t = (0, 19, 0.5))

        self.blueprints['endJaw'] = '{}_endJaw_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['endJaw']):
            mc.joint(self.blueprints['midJaw'], name=self.blueprints['endJaw'])
            mc.xform(self.blueprints['endJaw'], ws=True, t=(0, 19, 2))

        attrLib.addString(self.blueprintGrp, ln = 'blu_inputs', v = self.blueprints)

    def createJoints(self):

        par = self.moduleGrp
        self.jawJnts = []
        for alias, blu in self.blueprints.items():
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt)
            par = jnt
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            self.jawJnts.append(jnt)

        self.orientJnts(self.jawJnts)

        self.setOut('joints', str(self.joints))

    def orientJnts(self, jnts):
        print(jnts)
        upLoc = mc.createNode('transform')
        print(jnts[0])
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.setOrientToWorld(jnts[0])
        for i,s in enumerate(jnts):
            if i != 0:
                jntLib.orientUsingAim(jnts=jnts[i], upAim=upLoc,
                                      aimAxes='x', upAxes='y')
        mc.delete(upLoc)

    def build(self):

        super(Jaw, self).build()

        mult = [1, -1][self.side == 'R']
        self.size = trsLib.getDistance(self.joints['startJaw'], self.joints['endJaw'])
        jawCtl = control.Control(descriptor=self.prefix ,
                                     side=self.side,
                                     parent=self.ctlGrp,
                                     shape="circle",
                                     color=control.SECCOLORS[self.side],
                                     scale=[self.size / 1 * mult, self.size / 1, self.size / 1],
                                     moveShape=[0, 0, 0],
                                     lockHideAttrs=['s'],
                                     matchTranslate=self.joints['startJaw'])

        mc.parentConstraint(jawCtl.name,self.joints['startJaw'], mo = True )

        self.setOut('ctl', jawCtl.name)

    def connect(self):

        super(Jaw, self).connect()

        par = self.getOut('globalScale')
        if par:
            connect.matrix(par, self.ctlGrp, world=True)
            connect.matrix(par, self.moduleGrp, world=True)


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Jaw, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_neck.headCtl')








