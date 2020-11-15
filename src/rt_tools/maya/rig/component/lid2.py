import maya.cmds as mc
from . import template
from ...lib import trsLib
from ...lib import attrLib
from ...lib import control
from ...lib import connect
from ...lib import strLib
from ...lib import crvLib
from ...lib import jntLib

reload(trsLib)
reload(attrLib)
reload(control)
reload(connect)
reload(strLib)
reload(crvLib)
reload(template)


class Lid2(template.Template):
    """Class for creating lid"""

    def __init__(self, side='L', prefix='lid',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix

        self.aliases = {'upStart':'upStart',
                        'upEnd':'upEnd',
                        'buttomStart':'buttomStart',
                        'buttomEnd':'buttomEnd'}

        super(Lid2, self).__init__(**kwargs)

    def createBlueprint(self):
        super(Lid2, self).createBlueprint()

        mult = [-1, 1][self.side == 'L']
        # this data will be used to initialize the class later
        self.blueprints['upStart'] = '{}_upStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['upStart'])
            mc.xform(self.blueprints['upStart'], ws=True, t=(mult, 20, 1))

        self.blueprints['upEnd'] = '{}_upEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['upEnd']):
            mc.joint(self.blueprints['upStart'], name=self.blueprints['upEnd'])
            mc.xform(self.blueprints['upEnd'], ws=True, t=(mult, 20.2, 1.3))

        self.blueprints['buttomStart'] = '{}_buttomStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomStart']):
            mc.joint(self.blueprintGrp, name=self.blueprints['buttomStart'])
            mc.xform(self.blueprints['buttomStart'], ws=True, t=(mult, 20, 1))

        self.blueprints['buttomEnd'] = '{}_buttomEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['buttomEnd']):
            mc.joint(self.blueprints['buttomStart'], name=self.blueprints['buttomEnd'])
            mc.xform(self.blueprints['buttomEnd'], ws=True, t=(mult, 19.8, 1.3))

        attrLib.addString(self.blueprintGrp, ln='blu_inputs', v=str(self.blueprints))

    def createJoints(self):

        # create upLid joint
        par = self.moduleGrp
        self.lidJnts = {'lidJnts': []}
        self.upLidJnts =  {'upLid': []}
        for alias, blu in self.blueprints.items():
            if not alias in ('upStart','upEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            par = jnt
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.upLidJnts['upLid'].append(jnt)

        # create buttomLid joint
        self.buttomLidJnts = {'buttomLid' : []}
        par = self.moduleGrp
        for alias, blu in self.blueprints.items():
            if not alias in ('buttomStart', 'buttomEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n = jnt)
            par = jnt
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space = 'world')
            self.joints[alias] = jnt
            self.buttomLidJnts['buttomLid'].append(jnt)

        mc.parent(self.upLidJnts['upLid'][-1], world=True)
        mc.parent(self.buttomLidJnts['buttomLid'][-1], world=True)

        self.lidJnts.update(self.upLidJnts)
        self.lidJnts.update(self.buttomLidJnts)

        self.orientJnts()

        self.setOut('joints', str(self.lidJnts))

    def orientJnts(self):
        inverseUpAxes = [True, False][self.side == 'L']
        mult = [1, -1][self.side == 'R']
        print(self.upLidJnts['upLid'][-1])
        self.upLidJnts['upLid'][-1]

        # orient joints in a way that path each other
        mc.delete(mc.aimConstraint(self.buttomLidJnts['buttomLid'][-1],
                                   self.upLidJnts['upLid'][-1],
                                   aimVector=[0,-1,0],
                                   upVector=[1,0,0],
                                   worldUpType="none"))
        tempLoc = mc.createNode('transform')
        trsLib.match(tempLoc,self.upLidJnts['upLid'][-1] )
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, tempLoc)
        mc.parent(upLoc, tempLoc)

        mc.delete(mc.pointConstraint(self.upLidJnts['upLid'][0], tempLoc))
        mc.setAttr(upLoc + '.ty', 10000)

        mc.delete(mc.aimConstraint(self.upLidJnts['upLid'][-1],
                                   self.upLidJnts['upLid'][0],
                                   aimVector=[0,0,1],
                                   upVector=[0,1,0],
                                   worldUpType="objectrotation",
                                   wu=[0, 1, 0],
                                   wuo=upLoc))

        mc.makeIdentity(self.upLidJnts['upLid'][0], apply = True, s = 1, r = 1, t = 1)

        mc.delete(mc.aimConstraint(self.upLidJnts['upLid'][-1],
                                   self.buttomLidJnts['buttomLid'][-1],
                                   aimVector=[0,1,0],
                                   upVector=[1,0,0],
                                   worldUpType="none"))

        trsLib.match(tempLoc,self.buttomLidJnts['buttomLid'][-1] )
        mc.delete(mc.pointConstraint(self.buttomLidJnts['buttomLid'][0], tempLoc))

        mc.delete(mc.aimConstraint(self.buttomLidJnts['buttomLid'][-1],
                                   self.buttomLidJnts['buttomLid'][0],
                                   aimVector=[0,0,1],
                                   upVector=[0,1,0],
                                   worldUpType="objectrotation",
                                   wu=[0, 1, 0],
                                   wuo= upLoc))

        mc.makeIdentity(self.buttomLidJnts['buttomLid'][0], apply = True, s = 1, r = 1, t = 1)

        mc.parent(self.upLidJnts['upLid'][-1], self.upLidJnts['upLid'][0])
        mc.parent(self.buttomLidJnts['buttomLid'][-1], self.buttomLidJnts['buttomLid'][0])

        mc.delete(upLoc, tempLoc)



    def build(self):

        super(Lid2, self).build()
        iconSize = trsLib.getDistance(self.joints['upStart'], self.joints['upEnd']) * 2

        # create upcontrols
        self.ctlZros = {'ctlZros':[]}
        self.ctls = {'ctls':[]}
        upCtl = control.Control(descriptor='{}_up'.format(self.prefix),
                              side=self.side,
                              color='cyan',
                              orient=[0, 0, 1],
                              moveShape=(0, 0, 0.3),
                              scale=[iconSize * 0.2] * 3,
                              lockHideAttrs=['s', 'v'],
                              parent=self.ctlGrp)
        self.ctlZros['ctlZros'].append(upCtl.zro)
        self.ctls['ctls'].append(upCtl.name)
        mc.delete(mc.parentConstraint(self.upLidJnts['upLid'][-1], self.ctlZros['ctlZros'][0]))

        # create buttomControl
        buttomCtl = control.Control(descriptor='{}_buttom'.format(self.prefix),
                              side=self.side,
                              color='cyan',
                              orient=[0, 0, 1],
                              moveShape=(0, 0, 0.3),
                              scale=[iconSize * 0.2] * 3,
                              lockHideAttrs=['s', 'v'],
                              parent=self.ctlGrp)

        self.ctlZros['ctlZros'].append(buttomCtl.zro)
        self.ctls['ctls'].append(buttomCtl.name)

        self.setOut('lidCtl', self.ctls)
        mc.delete(mc.parentConstraint(self.buttomLidJnts['buttomLid'][-1], self.ctlZros['ctlZros'][-1]))

        # connect upControl(temporary)
        self.remapUpCtl = connect.remapVal(self.ctls['ctls'][0] + '.ty', self.upLidJnts['upLid'][0] + '.rx', inputMin = -0.5,
                         name = self.name + '_upStart', inputMax = 0.5,outputMin = 70, outputMax = -70)

        # connect buttomControl(temperory)
        self.remapButtomCtl = connect.remapVal(self.ctls['ctls'][-1] + '.ty', self.buttomLidJnts['buttomLid'][0] + '.rx', inputMin = -0.5,
                         name = self.name + '_buttomStart', inputMax = 0.5,outputMin = 70, outputMax = -70)


    def connect(self):
        """
        connection of created nodes
        """
        super(Lid2, self).connect()

        # createNode for final rotation
        self.finalRotGrp = mc.createNode('transform', name = self.name + '_finalRotationGrp')
        mc.delete(mc.pointConstraint(self.buttomLidJnts['buttomLid'][0] ,self.finalRotGrp, mo = False ))

        self.finalGrp = mc.createNode('transform', name = 'C' + '_finalRotationGrp' )
        mc.delete(mc.pointConstraint(self.finalRotGrp, self.finalGrp, mo = False))
        mc.parent(self.finalRotGrp, self.finalGrp)

        # attach controls
        eyeJnt = self.getOut('eyeJnt')
        globalCtl = self.getOut('globalScale')
        connect.matrix(globalCtl, self.ctlGrp, world = True)
        connect.matrix(globalCtl, self.moduleGrp, world = True)

        # connect eye controls to the eye lid nodes
        fkCtl = self.getOut('fkCtl')
        mc.parentConstraint(fkCtl , self.finalRotGrp, mo = True)
        mc.parent(self.finalGrp,globalCtl )

        # add attrs on eye control
        self.aimCtl = self.getOut('aimCtl')
        attrLib.addFloat(self.aimCtl,ln = 'fleshyEyelids')
        attrLib.addFloat(self.aimCtl,ln = 'blink', min = 0, max = 1)
        attrLib.addFloat(self.aimCtl,ln = 'blinkPos', min = 0, max = 1)

        #create node for connecting the rotate of final rotation grp to it
        fleshyMul= mc.createNode('multiplyDivide', name = self.name + '_fleshy_on_off' + '_MDN')
        mc.connectAttr(self.finalRotGrp + '.rx', fleshyMul + '.input1X')
        mc.connectAttr(self.finalRotGrp + '.ry', fleshyMul + '.input1Y')
        mc.connectAttr(self.aimCtl + '.fleshyEyelids', fleshyMul + '.input2X')
        mc.connectAttr(self.aimCtl + '.fleshyEyelids', fleshyMul + '.input2Y')

        # create plusMinusAverage for sum of rotation of eye rotation and eyeLid control translation
        fkUpRotationPma = mc.createNode('plusMinusAverage' , name = self.name + '_up_fkRotation' + '_PMA')
        fkButtomRotationPma = mc.createNode('plusMinusAverage' , name = self.name + '_buttom_fkRotation' + '_PMA')

        # remap side movement of up ctl
        self.remapUpSideCtl = connect.remapVal(self.ctls['ctls'][0] + '.tx', fkUpRotationPma  + '.input3D[0].input3Dy', inputMin = -0.5,
                         name = self.name + '_upSide', inputMax = 0.5,outputMin = -40, outputMax = 40)

        self.remapUpSideFleshyCtl = connect.remapVal(fleshyMul  + '.outputY', fkUpRotationPma  + '.input3D[1].input3Dy', inputMin = -80,
                                    name = self.name + '_upSideFleshy', inputMax = 80,outputMin = -22.5, outputMax = 22.5)

        self.remapButtomSideCtl = connect.remapVal(self.ctls['ctls'][-1] + '.tx', fkButtomRotationPma  + '.input3D[0].input3Dy', inputMin = -0.5,
                         name = self.name + '_buttomSide', inputMax = 0.5,outputMin = -40, outputMax = 40)

        self.remapButtomSideFleshyCtl = connect.remapVal(fleshyMul  + '.outputY', fkButtomRotationPma  + '.input3D[1].input3Dy', inputMin = -80,
                         name = self.name + '_buttomSideFleshy', inputMax = 80,outputMin = -22.5, outputMax = 22.5)

        # connect the plus side movements to the rotation of the joints
        mc.connectAttr(fkUpRotationPma + '.output3Dy' , self.upLidJnts['upLid'][0] + '.ry')
        mc.connectAttr(fkButtomRotationPma + '.output3Dy' , self.buttomLidJnts['buttomLid'][0] + '.ry')


        # create remap value node for connecting fleshymul to them
        connect.remapVal(fleshyMul + '.outputX', fkUpRotationPma + '.input3D[1].input3Dx',
                         name =self.name + '_UpFkCtl', inputMin=-45, inputMax = 45,outputMin = -45, outputMax = 45)

        connect.remapVal(fleshyMul + '.outputX', fkButtomRotationPma + '.input3D[1].input3Dx',
                         name =self.name + '_buttomFkCtl',inputMin=-45, inputMax = 45,outputMin = -45, outputMax = 45)


        # connect remapValue of up ctl to the fkUpRotationPma
        mc.connectAttr(self.remapUpCtl + '.outValue', fkUpRotationPma + '.input3D[0].input3Dx')

        # connect remapValue of buttom ctl to the fkButtomRotationPma
        mc.connectAttr(self.remapButtomCtl  + '.outValue', fkButtomRotationPma + '.input3D[0].input3Dx')

        # create a plusminus for adding the  remapButtomCtl and remapUpCtl and subtract from final rotation for blinkAngle
        blinkAnglePma = mc.createNode('plusMinusAverage', name = self.name + '_blinkAnle' + '_PMA')
        mc.connectAttr(fkUpRotationPma + '.output3Dx', blinkAnglePma + '.input3D[1].input3Dx' )
        mc.connectAttr(fkButtomRotationPma + '.output3Dx', blinkAnglePma + '.input3D[0].input3Dx' )
        mc.setAttr(blinkAnglePma + '.input3D[2].input3Dx' , -70)
        mc.setAttr(blinkAnglePma + '.operation', 2 )

        # connect blink attr and blinkAnglePma to the mul for blink
        mulBlink = mc.createNode('multiplyDivide', name = self.name + '_blink' + '_MDN')
        mc.connectAttr(self.aimCtl + '.blink', mulBlink + '.input2X')
        mc.connectAttr(blinkAnglePma +'.output3Dx', mulBlink + '.input1X' )

        # create blend color node for upLid and buttomLid for the blinkPos
        upBlinkBlnd = mc.createNode("blendColors", n= self.name  + '_upLid_blink' +"_BLN")
        mc.connectAttr(self.aimCtl + '.blinkPos', upBlinkBlnd + '.blender')
        mc.connectAttr(mulBlink + '.outputX' , upBlinkBlnd + '.color2.color2R')
        mc.setAttr(upBlinkBlnd + '.color1.color1R', 0)

        buttomBlinkBlnd = mc.createNode("blendColors", n= self.name  + '_buttomLid_blink' +"_BLN")
        mc.connectAttr(self.aimCtl + '.blinkPos', buttomBlinkBlnd + '.blender')
        mc.connectAttr(mulBlink + '.outputX' , buttomBlinkBlnd + '.color1.color1R')

        # create plusminus for adding lid with blink and sum of all movement
        upWithBlinkPma = mc.createNode('plusMinusAverage', name = self.name + '_upWithBlink'+ '_PMA')
        mc.connectAttr(upBlinkBlnd + '.outputR', upWithBlinkPma + '.input3D[0].input3Dx')
        mc.connectAttr( fkUpRotationPma + '.output3Dx', upWithBlinkPma + '.input3D[1].input3Dx')

        buttomWithBlinkPma = mc.createNode('plusMinusAverage', name = self.name + '_buttomWithBlink'+ '_PMA')
        mc.connectAttr(buttomBlinkBlnd + '.outputR', buttomWithBlinkPma + '.input3D[1].input3Dx')
        mc.connectAttr(fkButtomRotationPma + '.output3Dx', buttomWithBlinkPma + '.input3D[0].input3Dx')
        mc.setAttr(buttomWithBlinkPma + '.operation', 2)

        # connect lowLidWithBlink pma to the lower lid joint rotation
        mc.connectAttr(buttomWithBlinkPma + '.output3Dx' ,self.buttomLidJnts['buttomLid'][0] + '.rx', force = True )

        # create clamp for limiting the rotation and finaly push mode for lid
        upLidClamp = mc.createNode('clamp', name = self.name + '_up' + '.CMP')
        mc.connectAttr(upWithBlinkPma + '.output3Dx' ,upLidClamp + '.inputR' )
        mc.setAttr(upLidClamp + '.minR', -70 )
        buttonLidLimPma = mc.createNode('plusMinusAverage', name = self.name + '_buttomLimit' + '_PMA')
        mc.setAttr(buttonLidLimPma +'.input3D[0].input3Dx', 70 )
        mc.connectAttr(self.buttomLidJnts['buttomLid'][0] + '.rx', buttonLidLimPma + '.input3D[1].input3Dx')
        mc.connectAttr(buttonLidLimPma + '.output3Dx', upLidClamp + '.maxR')
        mc.connectAttr(upLidClamp + '.outputR',self.upLidJnts['upLid'][0] + '.rx' , force = True)


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Lid2, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'out_eyeJnt', v=self.side + '_eye.jnt')
        attrLib.addString(self.blueprintGrp, 'out_aimCtl', v=self.side + '_eye.eyeAimCtl')
        attrLib.addString(self.blueprintGrp, 'out_fkCtl', v=self.side + '_eye.eyeCtl')
        attrLib.addString(self.blueprintGrp, 'blu_globalScale', v='C_neck.headCtl')

        attrLib.addString(self.blueprintGrp, 'lidCtls', v='', lock=True)
