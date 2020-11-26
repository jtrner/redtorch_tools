import maya.cmds as mc

from . import template
from ...lib import attrLib
from ...lib import crvLib
from ...lib import trsLib
from ...lib import jntLib
from ...lib import control
from ...lib import connect
from ...lib import display
from ..command import fk
from ..command import splineIkTwist
from ..command import splineIkStretch

reload(splineIkStretch)
reload(display)
reload(fk)
reload(splineIkTwist)
reload(connect)
reload(control)
reload(jntLib)
reload(trsLib)
reload(crvLib)
reload(attrLib)
reload(template)

class SpineB(template.Template):

    def __init__(self, side = 'C' , prefix = 'spine', numJnts = 6, **kwargs):


        kwargs['side'] = side
        kwargs['prefix'] = prefix

        self.numJnts = numJnts


        super(SpineB, self).__init__(**kwargs)

    def createBlueprint(self):
        super(SpineB, self).createBlueprint()

        self.blueprints['start'] = '{}_start_BLU'.format(self.name)
        self.blueprints['mid'] = '{}_mid'.format(self.name)
        self.blueprints['end'] = '{}_end_BLU'.format(self.name)

        print(self.blueprints['start'])
        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))


        if not mc.objExists(self.blueprints['start']):
            mc.joint(self.blueprintGrp, name = self.blueprints['start'])
            mc.xform(self.blueprints['start'], ws = True, t = (0, 10.5, 0))

        if not mc.objExists(self.blueprints['mid']):
            mc.joint(self.blueprintGrp, name = self.blueprints['mid'])
            mc.xform(self.blueprints['mid'], ws = True, t = (0, 13, 0))

        if not mc.objExists(self.blueprints['end']):
            mc.joint(self.blueprintGrp, name = self.blueprints['end'])
            mc.xform(self.blueprints['end'], ws = True, t = (0, 16, 0))


    def createJoints(self):
        print('aaa')


        blueprints = self.blueprints['start'], self.blueprints['mid'], self.blueprints['end']

        crv = crvLib.fromJnts(jnts = blueprints, degree = 1, fit = False)[0]
        mc.rebuildCurve(crv, degree = 3, spans = 2)

        self.joints['baseJnt'] = mc.joint(self.moduleGrp, n = self.name + '_base_JNT')
        trsLib.setTRS(self.joints['baseJnt'], self.blueprintPoses['start'],space = 'world')
        mc.move(0, -0.01, 0, self.joints['baseJnt'], ws = True, r = True)


        self.joints['spineJnts'] = []
        jnts = jntLib.create_on_curve(curve = crv, numOfJoints = self.numJnts, parent = True)
        mc.parent(jnts[0], self.joints['baseJnt'])

        for i in range(self.numJnts):
            jnt = '{}_{:02}_JNT'.format(self.name, i + 1)
            jnt = mc.rename(jnts[i], jnt)
            self.joints['spineJnts'].append(jnt)
            self.joints['spineJnts'].append(jnt)

        mc.delete(crv)



    def build(self):
        super(SpineB, self).build()


        # create curve for ikspline
        ikCrvTemp= crvLib.fromJnts(jnts = self.joints['spineJnts'], degree = 3, fit = False)[0]
        ikCrv = mc.rebuildCurve(ikCrvTemp, ch = 1, rpo = 1, rt = 0, end = 1, kr = 0,kcp = 0,
                                kep = 1, kt = 0, s =  1, d = 3, tol = 0.01,)


        mc.rename(ikCrvTemp, 'spineCurve')

        #create ikspline
        ikHand = mc.ikHandle(sj = self.joints['spineJnts'][0] ,ee = self.joints['spineJnts'][-1],
                             name = 'C_spineIkHandle',solver = 'ikSplineSolver',
                             c = 'spineCurve', ccv = False)[0]

        mc.parent(ikHand, self.moduleGrp)


        iconSize = trsLib.getDistance(self.joints['spineJnts'][0], self.joints['spineJnts'][-1])

        # create ik controls
        conss = self.ctlGrp
        self.ctls = {'ikCtls': []}
        ct = []
        for i in range(3):
            ctl = control.Control(descriptor='{}_ik_{}'.format(self.prefix, i + 1),
                                  side=self.side,
                                  color='cyan',
                                  orient=[0, 1, 0],
                                  scale=[iconSize * 1.3] * 3,
                                  lockHideAttrs=['s', 'v'],
                                  parent=conss)
            pos = 1.0 / (2 + 1) * (i + 1)

            ct.append(ctl.zro)
            conss = ctl.name
            self.ctls['ikCtls'].append(ctl.name)
            if i > 0:
                mc.parent(ctl.zro, self.ctlGrp)

        # Move ik controls positions
        counter = 0
        for i,c in enumerate(ct):
            for j in (0, 5, -1):
                if counter < 3:

                    startcon = connect.weightConstraint(self.joints['spineJnts'][j],
                                                        ct[counter + i],
                                                        type='pointConstraint',
                                                        weights=[1 - pos, pos])
                    mc.delete(startcon)
                counter += 1

        
        # advance twist for ik spline
        splineIkTwist.run(ik_handle="C_spineIkHandle", 
                          base_control=self.ctls['ikCtls'][0], 
                          end_control=self.ctls['ikCtls'][-1], 
                          method="advanced",
                          up_axis="z", up_vector1=(1, 0, 0), up_vector2=(1, 0, 0))
        mc.setAttr("C_spineIkHandle.dForwardAxis", 2)

        n = ct[1] + '_POC'
        # parent mid control between start and end
        mc.pointConstraint(self.ctls['ikCtls'][0], self.ctls['ikCtls'][-1], ct[1], 
                            mo  = True , skip = ['x', 'z'], name = n)

        # clustrize
        specificCvs = {'cvStart': [],'cvMid': [],'cvEnd': []}

        cv_list = crvLib.getCVs('spineCurve')

        specificCvs['cvStart'] = (cv_list[0])
        specificCvs['cvMid'] = (cv_list[1:-1])
        specificCvs['cvEnd'] = (cv_list[-1])

        cls_list = []

        counter = 0
        for i in specificCvs['cvStart'] ,specificCvs['cvMid'],specificCvs['cvEnd']:
            print(i)
            cls = mc.cluster(i, name="{}{}_CLS".format(self.name, counter))[1]
            cls = mc.rename(cls, "{}{}_CLH".format(self.name, counter))
            cls_list.append(cls)
            counter += 1

        counter = 0
        for i in cls_list:
            mc.parent(i,self.ctls['ikCtls'][counter])
            counter += 1

        # create spine joints
        fkJnts = trsLib.duplicate(self.joints['spineJnts'][0],search = 'JNT', 
                                  replace = 'fk_JNT', hierarchy = True)


        # create spine fk controls
        fkCons = self.ctlGrp
        self.ctls.update({'fkCtls': []})
        ctList = []
        for i in range(2):
            cts = control.Control(descriptor='{}_fk_{}'.format(self.prefix, i + 1),
                                  side=self.side,
                                  color='pink',
                                  orient=[0, 1, 0],
                                  scale=[iconSize * 1] * 3,
                                  lockHideAttrs=['s', 'v'],
                                  parent=fkCons)
            pos = 1.0 / (2 + 1) * (i + 1)

            ctList.append(cts.zro)
            fkCons = cts.name
            self.ctls['fkCtls'].append(fkCons)


        # move fk controls positions
        counter = 0
        for i,c in enumerate(ct):
            for j in (0,4):
                if counter < 2:

                    startcon = connect.weightConstraint(fkJnts[j],
                                                        ctList[counter + i],
                                                        type='pointConstraint',
                                                        weights=[1 - pos, pos])
                    mc.delete(startcon)
                counter += 1


        connect.direct(self.ctls['fkCtls'][0], fkJnts[0], attrs=['r'])
        connect.direct(self.ctls['fkCtls'][-1], fkJnts[4], attrs=['r'])

        mc.pointConstraint(fkJnts[1],ct[-1], mo = True )

        #rename stuff
        chestCtl = mc.rename(self.ctls['ikCtls'][-1], self.side + '_chest_CTL')
        self.chestCtl_zro = mc.rename(ct[-1], self.side + '_chest_ZRO')
        midCtl = mc.rename(self.ctls['ikCtls'][1], self.name + '_mid_CTL')
        self.midCtl_zro = mc.rename(ct[1], self.name + '_mid_ZRO')
        hipCtl = mc.rename(self.ctls['ikCtls'][0], self.side + '_hip_CTL')
        self.hipCtl_zro  = mc.rename(ct[0], self.side + '_hip_ZRO')
        spineFkStart = mc.rename(self.ctls['fkCtls'][0], self.name+ '_fk_start_CTL')
        self.spineFkStart_zro = mc.rename(ctList[0], self.name + '_fk_start_ZRO')
        spineFkMid =mc.rename(self.ctls['fkCtls'][-1], self.name+ '_fk_mid_CTL')
        self.spineFkMid_zro = mc.rename(ctList[-1], self.name + '_fk_mid_ZRO')

        # edit shapes and colors and set out controls
        crvLib.editShape(hipCtl, shape = 'cube')
        display.setColor(hipCtl, 'yellow')
        crvLib.scaleShape(hipCtl, [iconSize, iconSize * 0.5, iconSize])
        attrLib.lockHideAttrs(hipCtl, attrs=['s', 'v','rz', 'rx'])
        self.setOut('hipCtl', hipCtl)

        crvLib.editShape(chestCtl, shape = 'cube')
        display.setColor(chestCtl, 'yellow')
        crvLib.scaleShape(chestCtl, [iconSize, iconSize * 0.5 , iconSize])
        attrLib.lockHideAttrs(chestCtl, attrs=['s', 'v',])
        self.setOut('chestCtl', chestCtl)

        crvLib.editShape(midCtl, shape = 'circle')
        display.setColor(midCtl, 'redDark')
        crvLib.scaleShape(midCtl, [iconSize * 1.5, iconSize , iconSize * 1.5])
        attrLib.lockHideAttrs(midCtl, attrs=['s', 'v','r'])
        self.setOut('midCtl', midCtl)

        crvLib.editShape(spineFkStart, shape = 'circle')
        display.setColor(spineFkStart, "cyan")
        crvLib.scaleShape(spineFkStart, [iconSize * 1.2 , iconSize , iconSize * 1.2 ])
        attrLib.lockHideAttrs(spineFkStart, attrs=['s', 'v','t'])
        self.setOut('spineFkStart', spineFkStart)

        crvLib.editShape(spineFkMid, shape = 'circle')
        display.setColor(spineFkMid, "cyan")
        crvLib.scaleShape(spineFkMid, [iconSize * 1.2 , iconSize , iconSize * 1.2 ])
        attrLib.lockHideAttrs(spineFkMid, attrs=['s', 'v','t'])
        self.setOut('spineFkMid', spineFkMid)

        # make curve ik stretchy
        splineIkStretch.run(ik_curve = 'spineCurve',volume = True, scale = 'scaleY')

        # clean up outliner
        print(cls_list)
        for i in cls_list:
            mc.setAttr(i + '.v', 0)

        mc.setAttr(fkJnts[0] + '.v', 0)

        mc.setAttr(ikHand + '.v', 0)


        mc.parent('spineCurve',self.settingGrp)
        mc.setAttr('spineCurve' + '.v', 0)

        mc.parentConstraint(hipCtl, self.joints['baseJnt'],
                            mo=True, st=('x', 'y', 'z'))


        # pevlis jnt
        guessed = 'C_pelvis_JNT'
        self.hipJnt = mc.ls(guessed)
        if self.hipJnt:
            self.hipJnt = self.hipJnt[0]
            self.setOut('hipJnt', self.hipJnt)



        # use child of last jnt as chest jnt
        chestJnt = self.joints['spineJnts'][-1]
        [attrLib.disconnectAttr(chestJnt + '.' + a) for a in ('r', 'rx', 'ry', 'rz')]
        mc.orientConstraint(chestCtl, chestJnt, mo=True, name=chestJnt + '_ORI')
        self.setOut('chestJnt', chestJnt)


    def connect(self):
        """
        connection of created nodes
        """
        super(SpineB, self).connect()

        # get handle to outputs
        ctlParent = self.getOut('ctlParent')

        # outliner clean up
        connect.matrix(ctlParent, self.moduleGrp)
        connect.matrix(ctlParent, self.ctlGrp)

        mc.parent(self.hipCtl_zro, ctlParent)
        mc.parent(self.spineFkStart_zro, ctlParent)


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(SpineB, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_root.bodyCtl')
        attrLib.addInt(self.blueprintGrp, 'blu_numOfJnts', v=self.numJnts or 6)






















