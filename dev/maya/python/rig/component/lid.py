"""
name: lid.py

Author: Ehsan Hassani Moghaddam

History:
    05/13/17 (ehassani)    first release!

"""
import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import control
from ...lib import connect
from ...lib import strLib
from ...lib import crvLib
from . import template

reload(trsLib)
reload(attrLib)
reload(control)
reload(connect)
reload(strLib)
reload(crvLib)
reload(template)


class Lid(template.Template):
    """Class for creating lid"""

    def __init__(self, side='L', prefix='lid', numJnts=10, eyeJnt='', lidUpCrv='', lidLoCrv='', upVec='', **kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.numJnts = numJnts
        self.eyeJnt = eyeJnt
        self.lidUpCrv = lidUpCrv
        self.lidLoCrv = lidLoCrv
        self.upVec = upVec
        super(Lid, self).__init__(**kwargs)
        if self.verbose:
            strLib.printBigTitle(mode="info", message='Creating Lid, "{}"'.format(prefix), separator="=",
                                 repeatation=100)

    def create(self):
        """
        creates lid locators for user to change
        their positions in Maya before building the rig
        """
        super(Lid, self).create()

        # get name
        name = self.getName()

        if self.verbose:
            print '\tlid.create(), "{}"'.format(name)

        # prevent method from running more than once
        if mc.getAttr(self.isCreated):
            return

        # create groups
        self.createGrp(name + "Module_GRP", parent="module_GRP")
        self.createGrp(name + "Control_GRP", parent="control_GRP")
        self.createGrp(name + "Origin_GRP", parent="origin_GRP")
        self.createGrp(name + "Starter_GRP", parent="starter_GRP")

        # this attribute on asset node will show us create method is run
        mc.setAttr(self.isCreated, True)

    def build(self):
        """
        building necessary nodes
        """
        super(Lid, self).build()

        name = self.getName()

        if self.verbose:
            print '\tlid.build(), "{}"'.format(name)

        if mc.getAttr(self.isBuilt):
            return

        ctlGrp = name + "Control_GRP"
        moduleGrp = name + "Module_GRP"
        origGrp = name + "Origin_GRP"

        eyeJnt = self.getOut('___eyeJnt')

        # try to find lid up curve if they're not given
        if not self.lidUpCrv:
            self.lidUpCrv = mc.ls(name + 'Up_CRV')
        if self.lidUpCrv:
            if not isinstance(self.lidUpCrv, basestring):
                self.lidUpCrv = self.lidUpCrv[0]
            attrLib.setAttr(self.asset + '.___lidUpCrv', self.lidUpCrv)
            mc.parent(self.lidUpCrv, origGrp)
        else:
            mc.error('Could not find lid cruve, "{0}" is not valid!'.format(name + 'Up_CRV'))

        # try to find lid low curve if they're not given
        if not self.lidLoCrv:
            self.lidLoCrv = mc.ls(name + 'Lo_CRV')
        if self.lidLoCrv:
            if not isinstance(self.lidLoCrv, basestring):
                self.lidLoCrv = self.lidLoCrv[0]
            attrLib.setAttr(self.asset + '.___lidLoCrv', self.lidLoCrv)
            mc.parent(self.lidLoCrv, origGrp)
        else:
            mc.error('Could not find lid cruve, "{0}" is not valid!'.format(name + 'Lo_CRV'))

        # try to find lid low curve if they're not given
        if not self.upVec:
            self.upVec = mc.ls(name + '_UPV')
        if self.upVec:
            if not isinstance(self.upVec, basestring):
                self.upVec = self.upVec[0]
            attrLib.setAttr(self.asset + '.___upVec', self.upVec)
        else:
            mc.error('Could not find lid upVec, "{0}" is not valid!'.format(name + '_UPV'))

        # create srts (these will be parents for iks that will drive lid jnts)
        srts = {}
        for p, crv in zip(['Up', 'Lo'], [self.lidUpCrv, self.lidLoCrv]):
            srts[p] = []
            grp = mc.createNode('transform', n='{0}{1}Srt_GRP'.format(name, p))
            for i in xrange(self.numJnts):
                n = '{0}{1}%02d_SRT'.format(name, p) % (i + 1)
                srt = mc.createNode('transform', n=n, p=grp)
                crvLib.attachToCurve(node=srt, curve=crv, uParam=1.0 / (self.numJnts - 1) * i)
                srts[p].append(srt)
            mc.parent(grp, origGrp)

        # create jnts
        eyePos = mc.xform(eyeJnt, q=True, ws=True, t=True)
        jnts = {}
        endJnts = {}
        for p in ['Up', 'Lo']:
            jnts[p] = []
            endJnts[p] = []
            grp = mc.createNode('transform', n='{0}{1}Jnts_GRP'.format(name, p))
            for i in xrange(self.numJnts):
                mc.select(grp)
                n = '{0}{1}%02dBase_JNT'.format(name, p) % (i + 1)
                jnt = mc.joint(p=eyePos, n=n)
                pos = mc.xform(srts[p][i], q=True, ws=True, t=True)
                endJnt = mc.joint(p=pos, n=n.replace('Base_JNT', '_JNT'))
                jnts[p].append(jnt)
                endJnts[p].append(endJnt)
            mc.parent(grp, moduleGrp)

        # jnts must aim to locs
        for p in ['Up', 'Lo']:
            for i in xrange(self.numJnts):
                n = '{0}{1}%02d_AIM'.format(name, p) % (i + 1)
                mc.aimConstraint(srts[p][i],
                                 jnts[p][i],
                                 wut='object',
                                 wuo=self.upVec,
                                 mo=True,
                                 n=n)
        # create controls
        iconSize = trsLib.getDistance(srts[p][0], srts[p][-1])
        ctls = {}
        for p in ['Up', 'Lo']:
            ctls[p] = []
            grp = mc.createNode('transform', n='{0}{1}Ctls_GRP'.format(name, p))
            for i in xrange(5):  # curves must have 5 CVs

                # find ctl pos
                id1 = self.numJnts / 4.0 * i
                if not id1 == int(id1):  # ctl in between two jnts
                    id1 = int(id1)
                    id2 = int(id1) + 1
                    pos = trsLib.getPoseBetween(srts[p][id1], srts[p][id2])
                else:
                    id1 = int(id1)
                    if id1 == self.numJnts:  # last joint
                        id1 -= 1  # to prevent index out of range error
                    pos = mc.xform(srts[p][id1], q=True, ws=True, t=True)

                # create ctl
                ctl = control.Control(
                    descriptor='{0}{1}%02d'.format(self.prefix, p) % (i + 1),
                    side=self.side,
                    parent=grp,
                    # shape="cube",
                    scale=[iconSize * 0.2, iconSize * 0.2, iconSize * 0.2],
                    translate=pos,
                    orient=[0, 0, 1],
                    moveShape=[0, 0, iconSize * 0.2],
                    lockHideAttrs=['s', 'v'],
                    verbose=self.verbose
                )
                ctls[p].append(ctl.name)
            mc.parent(grp, ctlGrp)

        # merge controls (there are two controls for each corner, one is enough)
        for i in [0, -1]:  # do it for first and last ctls
            mc.delete(ctls['Lo'][i].replace('_CTL', 'Ctl_ZRO'))  # delete ctl
            ctls['Lo'][i] = ctls['Up'][i]  # use Up ctl for Lo too

        # clusters
        for p, crv in zip(['Up', 'Lo'], [self.lidUpCrv, self.lidLoCrv]):
            grp = mc.createNode('transform', n='{0}{1}Clss_GRP'.format(name, p))
            clss = crvLib.clusterize(curve=crv, name=name + p)
            mc.hide(clss)
            mc.parent(clss, grp)
            mc.parent(grp, moduleGrp)
            for i, c in enumerate(clss):
                mc.parentConstraint(ctls[p][i], c, mo=True)

        # keep 2nd and 4th ctls between 1st, 3rd and 5th ctls
        for p in ['Up', 'Lo']:
            # 2nd ctl
            zro = ctls[p][1].replace('_CTL', 'Ctl_ZRO')
            mc.parentConstraint(ctls[p][0], ctls[p][2], zro, mo=True)
            # 4th ctl
            zro = ctls[p][3].replace('_CTL', 'Ctl_ZRO')
            mc.parentConstraint(ctls[p][2], ctls[p][4], zro, mo=True)

        # # add controls
        # lidCtls = fk.Fk(
        #                   joints=newJnts,
        #                   parent=ctlGrp,
        #                   shape='sphere',
        #                   scale=[0.5, 0.5, 0.5],
        #                   hideLastCtl=False,
        #                   connectGlobalScale=True
        #                  )

        # # keep in asset node for later use
        # lidCtls = [x.name for x in lidCtls]
        # attribute.setAttr(self.asset+'.__lidCtls', lidCtls)

        # this attribute on asset node will show us build method is run
        mc.setAttr(self.isBuilt, True)

    def connect(self):
        """
        connection of created nodes 
        """
        super(Lid, self).connect()

        name = self.getName()

        if self.verbose:
            print '\tlid.connect(), "{}"'.format(name)

        if mc.getAttr(self.isConnected):
            return

        # attach controls
        globalCtl = self.getOut('___globalScale')
        connect.matrix(globalCtl, name + "Module_GRP")
        connect.matrix(globalCtl, name + "Control_GRP")

        # this attribute on asset node will show us connect method is run
        mc.setAttr(self.isConnected, True)

    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Lid, self).createSettings()

        attrLib.addInt(self.asset, '___numJnts', v=self.numJnts)
        attrLib.addString(self.asset, '___eyeJnt', v=self.side + '_eye.jnt')
        attrLib.addString(self.asset, '___lidUpCrv', v=self.lidUpCrv or '')
        attrLib.addString(self.asset, '___lidLoCrv', v=self.lidLoCrv or '')
        attrLib.addString(self.asset, '___upVec', v=self.upVec or '')
        attrLib.addString(self.asset, '___globalScale', v='C_neck.headCtl')

        attrLib.addString(self.asset, '__lidCtls', v='', lock=True)
