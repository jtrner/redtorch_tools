"""
name: tail.py

Author: Ehsan Hassani Moghaddam

"""
import maya.cmds as mc

from ...lib import connect
from ...lib import strLib
from ...lib import attrLib
from ...lib import trsLib
from ...lib import jntLib
from ..command import rope
from . import template

reload(connect)
reload(strLib)
reload(attrLib)
reload(trsLib)
reload(jntLib)
reload(rope)
reload(template)


class Tail(template.Template):
    """
    class for creating tail rig for biped characters
    """

    def __init__(self, side="C", prefix="tail", numOfJnts=6, hasMidCtl=True, addSpaces=True, **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.hasMidCtl = hasMidCtl
        self.numOfJnts = numOfJnts
        self.addSpaces = addSpaces

        super(Tail, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Tail, self).createBlueprint()

        # create input blueprints
        par = self.blueprintGrp
        for i in range(self.numOfJnts):
            blu = '{}_{:03d}_BLU'.format(self.name, i + 1)
            self.blueprints['{:03d}'.format(i + 1)] = blu
            if not mc.objExists(blu):
                mc.joint(par, name=blu)
                mc.xform(blu, ws=True, t=(0, 10, (i + 1) * -1))
            par = blu

        self.orientJnts(self.blueprints.values())

        # delete extra blueprint joints
        all_blueprints = mc.ls('{}_???_BLU'.format(self.name))
        if len(all_blueprints) > self.numOfJnts:
            mc.error('tail.py: numOfJnts value is less than number of found blueprint joints!')
            # to_del = []
            # for blu in all_blueprints:
            #     if blu not in self.blueprints.values():
            #         to_del.append(blu)
            # mc.warning('numOfJnts is less than found blueprints: ', to_del)
            # #mc.delete(to_del)
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

    def createJoints(self):
        """
        create joints from blueprint poses
        :return:
        """
        self.joints['chainJnts'] = []
        par = self.moduleGrp
        for i in range(self.numOfJnts):
            jnt = '{}_{:03d}_JNT'.format(self.name, i + 1)
            mc.joint(par, name=jnt)
            trsLib.setTRS(jnt, self.blueprintPoses['{:03d}'.format(i + 1)], space='world')
            par = jnt
            self.joints['chainJnts'].append(jnt)

        self.orientJnts(self.joints['chainJnts'])

    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='y')
        mc.delete(upLoc)

    def build(self):
        super(Tail, self).build()

        # tail
        baseCtl, crvGrp, rsltGrp, ctls = rope.run(
            jnts=self.joints['chainJnts'],
            numCtls=self.numOfJnts,
            guides=None,
            numJnts=None,
            addSpaces=self.addSpaces,
            description=self.prefix,
            matchOrientation=True)
        baseCtlGrp = mc.listRelatives(baseCtl, p=1)[0]
        mc.parent(baseCtlGrp, self.ctlGrp)
        mc.parent(crvGrp, rsltGrp, self.originGrp)

    def connect(self):
        """
        connection of created nodes
        """
        super(Tail, self).connect()

        # outliner clean up
        hipCtl = self.getOut('hipCtl')
        connect.matrix(hipCtl, self.moduleGrp)
        connect.matrix(hipCtl, self.ctlGrp)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Tail, self).createSettings()

        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numOfJnts)
        attrLib.addString(self.blueprintGrp, 'blu_bodyCtl', v='C_root.bodyCtl')
        attrLib.addString(self.blueprintGrp, 'blu_hipCtl', v='C_spine.hipCtl')
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_root.mainCtl')

        attrLib.addString(self.blueprintGrp, 'blu_tailOrient',
                          v={'drivers': ['C_spine.hipCtl',
                                         'C_root.bodyCtl',
                                         'C_root.mainCtl'],
                             'dv': 0})
