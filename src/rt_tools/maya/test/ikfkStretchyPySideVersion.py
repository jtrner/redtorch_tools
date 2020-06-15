"""
import sys


path = 'D:/all_works/redtorch_tools/src/rt_tools/maya/test'

while path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import ikfkStretchyPySideVersion
reload(ikfkStretchyPySideVersion)


ikfkStretchyPySideVersion.launch()

"""
from math import floor

import maya.cmds as mc
import maya.mel as mm
from PySide2 import QtCore, QtWidgets


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class IKFK(QtWidgets.QDialog):

    def __init__(self):
        super(IKFK, self).__init__(parent=getMayaWindow())

        self.setWindowTitle("ik & fk")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(100, 100)

        self.rig_button = QtWidgets.QPushButton("Rig")
        self.rig_button.clicked.connect(self.FKAutoRig)

        self.color_grp = QtWidgets.QGroupBox("select top joint ")
        self.color_grp.setMinimumSize(50, 50)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

        main_layout.addStretch()
        main_layout.addWidget(self.color_grp)

        main_layout.addWidget(self.rig_button)

    def FKAutoRig(self):
        if not mc.ls(sl=True):
            QtWidgets.QMessageBox.critical(self, "Error", "you should select at least one joint.")
        elif mc.nodeType(mc.ls(sl=True)) != "joint":
            QtWidgets.QMessageBox.critical(self, "Error", "you should select joint.")
            return
        else:

            # Original Joint List
            # Also fills the list with everything below the selection
            mc.SelectHierarchy()
            OJL = mc.ls(sl=True)
            # FK Joint List
            FKJL = []
            IKJL = []
            count = 0
            FKHndleRatio = .5
            IKHndleRatio = 1
            anklIndex = 2  # assumes the third joint will be the ankle
            # Extra variables to make scaling the tool easier
            skipLastJoint = False
            addConstraints = True

            # Create IK/FK switch Controller
            mc.circle(name="IK_FK_Switch", nr=(0, 1, 0), c=(0, 0, 0), r=1)
            mc.color(rgb=(0, 1, 1))
            mc.pointConstraint(str(OJL[0]), "IK_FK_Switch")
            mc.delete("IK_FK_Switch_pointConstraint1")
            mc.makeIdentity("IK_FK_Switch", apply=True, t=True, r=True, s=True, n=False, pn=True)
            mc.move(10, 0, 0)
            # Lock channels
            mc.setAttr("IK_FK_Switch.sx", channelBox=False, lock=True, keyable=False)
            mc.setAttr("IK_FK_Switch.sy", channelBox=False, lock=True, keyable=False)
            mc.setAttr("IK_FK_Switch.sz", channelBox=False, lock=True, keyable=False)
            mc.setAttr("IK_FK_Switch.rx", channelBox=False, lock=True, keyable=False)
            mc.setAttr("IK_FK_Switch.ry", channelBox=False, lock=True, keyable=False)
            mc.setAttr("IK_FK_Switch.rz", channelBox=False, lock=True, keyable=False)
            # Add IK and FK attributes
            mc.addAttr(ln="Streatch_Tolerance", at="float", dv=0)  # AddStreatchy Offset
            mc.setAttr("IK_FK_Switch.Streatch_Tolerance", channelBox=True, l=False)
            mc.setAttr("IK_FK_Switch.Streatch_Tolerance", k=True)
            mc.addAttr(ln="IK_mode", at="float", min=0, max=1, dv=0)  # AddIK
            mc.setAttr("IK_FK_Switch.IK_mode", channelBox=True, l=False)
            mc.setAttr("IK_FK_Switch.IK_mode", k=True)
            mc.addAttr(ln="FK_mode", at="float", min=0, max=1, dv=1)  # AddFK
            mc.setAttr("IK_FK_Switch.FK_mode", channelBox=True, l=False)
            mc.setAttr("IK_FK_Switch.FK_mode", k=True)

            # Creates new FK Skeleton identicle to the original skeleton
            mc.JointTool()
            for jnt in OJL:
                rad = str(mc.joint(OJL[count], q=True, rad=True)).replace("[", "")
                newrad = rad.replace("]", "")
                mc.joint(p=mc.xform(jnt, q=True, t=True, ws=True), rad=float(newrad))
                FKJL.append(mc.ls(sl=True))
                count += 1
            count = 0
            mm.eval("escapeCurrentTool;")

            # Renames, orients and colors the new FK skeleton
            for jnt in FKJL:
                FKJL[count] = mc.rename(jnt, str(OJL[count] + "_FK_CTRL"))
                mc.orientConstraint(str(OJL[count]), str(OJL[count] + "_FK_CTRL"))
                mc.pointConstraint(str(OJL[count]), str(OJL[count] + "_FK_CTRL"))
                mc.delete(OJL[count] + "_FK_CTRL_orientConstraint1", OJL[count] + "_FK_CTRL_pointConstraint1")
                mc.select(OJL[count] + "_FK_CTRL")
                mc.makeIdentity(apply=True, t=True, r=True, s=True, n=False, pn=True)  # Freze transforms
                mc.color(rgb=(0, 0, 1))
                # Sets up handles on the new FK skeleton and preps it for use
                if count > 0:
                    mc.setAttr(FKJL[count] + ".tx", channelBox=False, lock=True, keyable=False)
                    mc.setAttr(FKJL[count] + ".ty", channelBox=False, lock=True, keyable=False)
                    mc.setAttr(FKJL[count] + ".tz", channelBox=False, lock=True, keyable=False)
                mc.setAttr(FKJL[count] + ".sx", channelBox=False, lock=True, keyable=False)
                mc.setAttr(FKJL[count] + ".sy", channelBox=False, lock=True, keyable=False)
                mc.setAttr(FKJL[count] + ".sz", channelBox=False, lock=True, keyable=False)
                mc.setAttr(FKJL[count] + ".radi", channelBox=False, lock=True, keyable=False)
                # Adds Constraints
                if addConstraints == True:
                    mc.orientConstraint(FKJL[count], OJL[count], mo=True)
                    if count < 1:
                        mc.scaleConstraint(FKJL[count], OJL[count], mo=False)
                        # Adds Curves
                if count < len(
                        FKJL) - 1 and skipLastJoint == False:  # Skips the final joint as it shouldn't need a controll
                    rad = mc.xform(OJL[count + 1], q=True, t=True, r=True)[0] * FKHndleRatio
                    mc.circle(name="crv_" + str(count), nr=(1, 0, 0), c=(0, 0, 0), r=rad)
                    mc.select("crv_" + str(count) + "Shape", r=True)
                    mc.select(str(OJL[count] + "_FK_CTRL"), tgl=True)
                    mc.parent(r=True, s=True)
                    mc.select("crv_" + str(count) + "Shape", r=True)
                    mc.rename("FK_" + OJL[count] + "Shape")
                    mc.color(rgb=(0, 0, 1))
                    mc.select("crv_" + str(count), r=True)
                    mc.delete()
                    mc.select(cl=True)
                elif count < len(FKJL) and skipLastJoint == True:
                    rad = mc.xform(OJL[count + 1], q=True, t=True, r=True)[0] * FKHndleRatio
                    mc.circle(name="crv_" + str(count), nr=(1, 0, 0), c=(0, 0, 0), r=rad)
                    mc.select("crv_" + str(count) + "Shape", r=True)
                    mc.select(str(OJL[count] + "_FK_CTRL"), tgl=True)
                    mc.parent(r=True, s=True)
                    mc.select("crv_" + str(count), r=True)
                    mc.delete()
                    mc.select(cl=True)
                count += 1

            # Creates new FK Skeleton identicle to the original skeleton
            count = 0
            mc.JointTool()
            for jnt in OJL:
                rad = str(mc.joint(OJL[count], q=True, rad=True)).replace("[", "")
                newrad = rad.replace("]", "")
                mc.joint(p=mc.xform(jnt, q=True, t=True, ws=True), rad=float(newrad))
                IKJL.append(mc.ls(sl=True))
                count += 1
            count = 0
            mm.eval("escapeCurrentTool;")

            # Creates IK controller
            mc.spaceLocator(p=mc.xform(OJL[0], q=True, t=True, ws=True))
            mc.rename("loc1")
            mc.pointConstraint(OJL[anklIndex], "loc1")
            locPos = mc.xform("loc1", q=True, t=True, ws=True)
            IKRad = locPos[0] + locPos[1] + locPos[2]
            IKRad = IKRad * IKHndleRatio
            mc.delete("loc1")
            mc.circle(name="Leg_IK_Main_CTRL", nr=(0, 1, 0), c=(0, 0, 0), r=IKRad)
            mc.color(rgb=(1, 0, 0))
            mc.pointConstraint(OJL[anklIndex], "Leg_IK_Main_CTRL")
            mc.delete("Leg_IK_Main_CTRL_pointConstraint1")
            mc.makeIdentity("Leg_IK_Main_CTRL", apply=True, t=True, r=True, s=True, n=False, pn=True)
            # Renames, orients and colors the new FK skeleton
            for jnt in IKJL:
                IKJL[count] = mc.rename(jnt, str(OJL[count] + "_IK_CTRL"))
                mc.orientConstraint(str(OJL[count]), str(OJL[count] + "_IK_CTRL"))
                mc.pointConstraint(str(OJL[count]), str(OJL[count] + "_IK_CTRL"))
                mc.delete(OJL[count] + "_IK_CTRL_orientConstraint1", OJL[count] + "_IK_CTRL_pointConstraint1")
                mc.select(OJL[count] + "_IK_CTRL")
                mc.makeIdentity(apply=True, t=True, r=True, s=True, n=False, pn=True)  # Freze transforms
                mc.color(rgb=(1, 0, 0))
                # Preps IK skeliton for use
                if count > 0:
                    mc.setAttr(IKJL[count] + ".tx", channelBox=False, lock=True, keyable=False)
                    mc.setAttr(IKJL[count] + ".ty", channelBox=False, lock=True, keyable=False)
                    mc.setAttr(IKJL[count] + ".tz", channelBox=False, lock=True, keyable=False)
                # mc.setAttr(IKJL[count]+".sx", channelBox=False, lock=True, keyable=False)
                # mc.setAttr(IKJL[count]+".sy", channelBox=False, lock=True, keyable=False)
                # mc.setAttr(IKJL[count]+".sz", channelBox=False, lock=True, keyable=False)
                mc.setAttr(IKJL[count] + ".radi", channelBox=False, lock=True, keyable=False)
                # Adds constraints
                if addConstraints == True:
                    mc.orientConstraint(IKJL[count], OJL[count], mo=True)
                    mc.scaleConstraint(IKJL[count], OJL[count], mo=False)
                count += 1

            # Creates IK solver and moves it under IK controller
            IKH = mc.ikHandle(n="IKLeg", sj=IKJL[0], ee=IKJL[anklIndex])[0]
            mc.parent("IKLeg", "Leg_IK_Main_CTRL")
            mc.ikHandle(n="IKFoot", sj=IKJL[anklIndex], ee=IKJL[anklIndex + 1])
            mc.parent("IKFoot", "Leg_IK_Main_CTRL")

            polloc = mc.spaceLocator()[0]
            mc.delete(mc.parentConstraint(IKJL[0], IKJL[2], polloc, mo=False))

            mc.delete(mc.aimConstraint(IKJL[1],
                                       polloc,
                                       aim=(1, 0, 0),
                                       upVector=(0, 1, 0),
                                       worldUpType='objectrotation',
                                       worldUpVector=(0, 1, 0),
                                       mo=False))

            polloc2 = mc.spaceLocator()[0]
            mc.parent(polloc2, polloc)
            mc.setAttr(polloc2 + '.t', 6, 0, 0)
            mc.setAttr(polloc2 + '.r', 0, 0, 0)

            polgroup = mc.group(n='polGRP', em=True)
            mc.delete(mc.parentConstraint(polloc2, polgroup, mo=False))
            polcontrol = mc.circle(n='polvec')[0]
            mc.parent(polcontrol, polgroup)
            mc.setAttr(polcontrol + '.t', 0, 0, 0)
            mc.setAttr(polcontrol + '.r', 0, 0, 0)
            mc.poleVectorConstraint(polcontrol, IKH)

            # Outliner cleanup
            # IK
            mc.group(em=True, name=OJL[0] + "_IK_GRP")
            mc.parent(str(IKJL[0]), OJL[0] + "_IK_GRP")
            mc.parent("Leg_IK_Main_CTRL", OJL[0] + "_IK_GRP")
            # FK
            mc.group(em=True, name=OJL[0] + "_FK_GRP")
            mc.parent(str(FKJL[0]), OJL[0] + "_FK_GRP")
            # Move switch in outliner
            mc.reorder("IK_FK_Switch", r=2)
            # Hide Bound Chain
            mc.setAttr(OJL[0] + ".visibility", 0)

            # Connects constraints to IK_FK_Switch
            count = 0
            for jnt in OJL:
                mc.connectAttr("IK_FK_Switch.IK_mode", jnt + "_orientConstraint1." + jnt + "_IK_CTRLW1")
                mc.connectAttr("IK_FK_Switch.FK_mode", jnt + "_orientConstraint1." + jnt + "_FK_CTRLW0")
                if count < 1:
                    mc.connectAttr("IK_FK_Switch.IK_mode", jnt + "_scaleConstraint1." + jnt + "_IK_CTRLW1")
                    mc.connectAttr("IK_FK_Switch.FK_mode", jnt + "_scaleConstraint1." + jnt + "_FK_CTRLW0")
                count += 1
            mc.connectAttr("IK_FK_Switch.FK_mode", OJL[0] + "_FK_GRP.visibility")
            mc.connectAttr("IK_FK_Switch.IK_mode", OJL[0] + "_IK_GRP.visibility")

            # Creates 1-x relationship in IK/FK switch controller
            mc.expression(s="IK_FK_Switch.FK_mode = 1-IK_FK_Switch.IK_mode", o="IK_FK_Switch", ae=1, uc="all")
            mc.setAttr("IK_FK_Switch.FK_mode", k=False, cb=False)

            # Set up Streatchy joints
            mc.spaceLocator(n=str(OJL[0] + "_LOCATOR"))  # Locator 1
            mc.pointConstraint(str(IKJL[0]), OJL[0] + "_LOCATOR")
            mc.spaceLocator(n=str(OJL[anklIndex] + "_LOCATOR"))  # Locator2
            mc.pointConstraint("Leg_IK_Main_CTRL", OJL[anklIndex] + "_LOCATOR")
            mc.parent(OJL[0] + "_LOCATOR", OJL[anklIndex] + "_LOCATOR", OJL[0] + "_IK_GRP")

            # Get max offset distance (Streatch Tolerance)
            length1 = mc.getAttr(OJL[1] + ".translateX")
            length2 = mc.getAttr(OJL[2] + ".translateX")
            distance = length1 + length2
            distance = distance * 100
            distance = floor(distance)  # Floor to stop snapping.
            distance = distance / 100
            mc.setAttr("IK_FK_Switch.Streatch_Tolerance", distance)
            mc.createNode("distanceBetween", n=OJL[0] + "_distanceBetween")  # DistanceBetween
            mc.connectAttr(OJL[0] + "_LOCATOR.translate", OJL[0] + "_distanceBetween.point1")
            mc.connectAttr(OJL[anklIndex] + "_LOCATOR.translate", OJL[0] + "_distanceBetween.point2")

            # Create condition logic
            mc.createNode("condition", n=OJL[0] + "_streatchCondition")  # Create <= Condition
            mc.setAttr(OJL[0] + "_streatchCondition.operation", 3)
            mc.connectAttr(OJL[0] + "_distanceBetween.distance", OJL[0] + "_streatchCondition.firstTerm")
            mc.connectAttr(OJL[0] + "_distanceBetween.distance", OJL[0] + "_streatchCondition.colorIfTrueR")
            mc.setAttr(OJL[0] + "_streatchCondition.secondTerm", distance)
            mc.setAttr(OJL[0] + "_streatchCondition.colorIfFalseR", distance)

            # Create streatch fraction
            mc.createNode("multiplyDivide", n=OJL[0] + "_streatchFraction")
            mc.connectAttr(OJL[0] + "_streatchCondition.outColorR", OJL[0] + "_streatchFraction.input1X")
            mc.setAttr(OJL[0] + "_streatchFraction.input2X", distance)
            mc.setAttr(OJL[0] + "_streatchFraction.operation", 2)

            # Create inverse fraction
            mc.createNode("multiplyDivide", n=OJL[0] + "_inverseFraction")
            mc.connectAttr(OJL[0] + "_streatchFraction.outputX", OJL[0] + "_inverseFraction.input2X")
            mc.setAttr(OJL[0] + "_inverseFraction.input1X", 1)
            mc.setAttr(OJL[0] + "_inverseFraction.operation", 2)

            # Connect first 2 joints
            count = 0
            while count < anklIndex:
                mc.connectAttr(OJL[0] + "_streatchFraction.outputX", IKJL[count] + ".scaleX")
                mc.connectAttr(OJL[0] + "_inverseFraction.outputX", IKJL[count] + ".scaleY")
                mc.connectAttr(OJL[0] + "_inverseFraction.outputX", IKJL[count] + ".scaleZ")
                count += 1

            print "rig is ready!"


def launch():
    global b
    try:
        b.close()
        b.deleteLater()
    except:
        pass
    b = IKFK()
    b.show()
