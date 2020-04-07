from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as mui

'''
Only works with guides that have three controls inside the group(A ctrl, B ctrl, and A Up ctrl).

Only have the A ctrls selected for the script to work.

For the place and expand function, position your A ctrl, and then hit place. From there, you can rotate the group using the
rotate function under it. After rotated, you can select your axis and set the size, then hit expand. The B ctrl and A Up ctrl
should translate on that axis. You will need to hit place again if you want to expand onto another axis though.

For the rotate function, there top group must not have any translate values in it. If there are values in it, you can build
the rig and go back to guide state and the values should be zeroed out(as of Oct 25, 2019).

If something doesn't work correctly, just try building and going back to guide state. If that doesn't fix it, then I guess
you can always do it by hand :^)
'''


class Orient_Guides():

    # window stuff
    def maya_main_window(self):
        main_window_pointer = mui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_pointer), QtWidgets.QWidget)

    # Define variables to use else where in the class
    def __init__(self):
        self.guide_b_option_X = None
        self.guide_b_option_Y = None
        self.guide_b_option_Z = None
        self.guide_b_reverse = None
        self.guide_a_up_option_X = None
        self.guide_a_up_option_Y = None
        self.guide_a_up_option_Z = None
        self.guide_a_up_reverse = None
        self.tweak_X = None
        self.tweak_Y = None
        self.tweak_Z = None
        self.set_size = None

    # Function to rotate the guide group
    # direction: depending on input, will rotate positive or negative
    def rotate_tweak(self, direction=''):
        # Create variables from scene and information from the window
        sel = cmds.ls(sl=True)
        rotate_x = self.tweak_X.text()
        rotate_y = self.tweak_Y.text()
        rotate_z = self.tweak_Z.text()
        # Loop through selection
        for ctrl in sel:
            # Check direction from button clicked
            if direction == 'positive':
                top_grp = cmds.listRelatives(ctrl, parent=True)[0]
                ctrl_pivot = cmds.xform(ctrl, query=True, translation=True, worldSpace=True)
                # Create variable for rotation value after tweak
                rotate_x_result = cmds.getAttr('{0}.rotateX'.format(top_grp))
                rotate_x_result += float(rotate_x)
                rotate_y_result = cmds.getAttr('{0}.rotateY'.format(top_grp))
                rotate_y_result += float(rotate_y)
                rotate_z_result = cmds.getAttr('{0}.rotateZ'.format(top_grp))
                rotate_z_result += float(rotate_z)
                # Rotate the top group with the pivot of the A joint
                cmds.xform(top_grp, rotation=[rotate_x_result, rotate_y_result, rotate_z_result], pivots=ctrl_pivot)
                # Reset the pivot of the top group back to the origin
                cmds.xform(top_grp, pivots=[0, 0, 0])
            if direction == 'negative':
                top_grp = cmds.listRelatives(ctrl, parent=True)[0]
                ctrl_pivot = cmds.xform(ctrl, query=True, translation=True, worldSpace=True)
                # Create variable for rotation value after tweak
                rotate_x_result = cmds.getAttr('{0}.rotateX'.format(top_grp))
                rotate_x_result -= float(rotate_x)
                rotate_y_result = cmds.getAttr('{0}.rotateY'.format(top_grp))
                rotate_y_result -= float(rotate_y)
                rotate_z_result = cmds.getAttr('{0}.rotateZ'.format(top_grp))
                rotate_z_result -= float(rotate_z)
                # Rotate the top group with the pivot of the A joint
                cmds.xform(top_grp, rotation=[rotate_x_result, rotate_y_result, rotate_z_result], pivots=ctrl_pivot)
                # Reset the pivot of the top group back to the origin
                cmds.xform(top_grp, pivots=[0, 0, 0])

    # Function to orient the guides to the settings
    def orient(self, function=''):
        # Create variable for user selection
        sel = cmds.ls(sl=True)
        # If button clicked is 'Place'
        if function == 'Place':
            # Loop through the selection
            for ctrl in sel:
                # Create variable for B ctrl and Up ctrl
                ctrl_b = ctrl[:-6] + 'b_Ctrl'
                up_ctrl = ctrl[:-6] + 'up_a_Ctrl'

                # Match transform of B ctrl and Up ctrl to A ctrl
                cmds.matchTransform(up_ctrl, ctrl, position=True, rotation=True)
                cmds.matchTransform(ctrl_b, ctrl, position=True, rotation=True)
        # If button clicked is 'Expand'
        if function == 'Expand':
            # Create variable for translation
            translate = self.set_size.text()
            # Loop through the selection
            for ctrl in sel:
                # Create variable for B ctrl and Up ctrl
                ctrl_b = ctrl[:-6] + 'b_Ctrl'
                up_ctrl = ctrl[:-6] + 'up_a_Ctrl'
                # Check which radio button is selected for B ctrl
                # If option X is checked
                if self.guide_b_option_X.isChecked():
                    # Check if reverse is checked
                    if self.guide_b_reverse.isChecked():
                        # Get translate value based on current ctrl_b position
                        expand_x_result = cmds.getAttr('{0}.translateX'.format(ctrl))
                        expand_x_result -= float(translate)
                        # Move ctrl_b
                        cmds.move(expand_x_result, ctrl_b, moveX=True, objectSpace=True)
                    else:
                        # Get translate value based on current ctrl_b position
                        expand_x_result = cmds.getAttr('{0}.translateX'.format(ctrl))
                        expand_x_result += float(translate)
                        # Move ctrl_b
                        cmds.move(expand_x_result, ctrl_b, moveX=True, objectSpace=True)
                # If option Y is checked
                if self.guide_b_option_Y.isChecked():
                    # Check if reverse is checked
                    if self.guide_b_reverse.isChecked():
                        # Get translate value based on current ctrl_b position
                        expand_y_result = cmds.getAttr('{0}.translateY'.format(ctrl))
                        expand_y_result -= float(translate)
                        # Move ctrl_b
                        cmds.move(expand_y_result, ctrl_b, moveY=True, objectSpace=True)
                    else:
                        # Get translate value based on current ctrl_b position
                        expand_y_result = cmds.getAttr('{0}.translateY'.format(ctrl))
                        expand_y_result += float(translate)
                        # Move ctrl_b
                        cmds.move(expand_y_result, ctrl_b, moveY=True, objectSpace=True)
                # If option Z is checked
                if self.guide_b_option_Z.isChecked():
                    # Check if reverse is checked
                    if self.guide_b_reverse.isChecked():
                        # Get translate value based on current ctrl_b position
                        expand_z_result = cmds.getAttr('{0}.translateZ'.format(ctrl))
                        expand_z_result -= float(translate)
                        # Move ctrl_b
                        cmds.move(expand_z_result, ctrl_b, moveZ=True, objectSpace=True)
                    else:
                        # Get translate value based on current ctrl_b position
                        expand_z_result = cmds.getAttr('{0}.translateZ'.format(ctrl))
                        expand_z_result += float(translate)
                        # Move ctrl_b
                        cmds.move(expand_z_result, ctrl_b, moveZ=True, objectSpace=True)

                # Check which radio button is selected for A Up Ctrl
                # If option X is checked
                if self.guide_a_up_option_X.isChecked():
                    # Check if reverse is checked
                    if self.guide_a_up_reverse.isChecked():
                        # Get translate value based on current up_ctrl position
                        expand_x_result = cmds.getAttr('{0}.translateX'.format(ctrl))
                        expand_x_result -= float(translate)
                        # Move up_ctrl
                        cmds.move(expand_x_result, up_ctrl, moveX=True, objectSpace=True)
                    else:
                        # Get translate value based on current up_ctrl position
                        expand_x_result = cmds.getAttr('{0}.translateX'.format(ctrl))
                        expand_x_result += float(translate)
                        # Move up_ctrl
                        cmds.move(expand_x_result, up_ctrl, moveX=True, objectSpace=True)
                # If option Y is checked
                if self.guide_a_up_option_Y.isChecked():
                    # Check if reverse is checked
                    if self.guide_a_up_reverse.isChecked():
                        # Get translate value based on current up_ctrl position
                        expand_y_result = cmds.getAttr('{0}.translateY'.format(ctrl))
                        expand_y_result -= float(translate)
                        # Move up_ctrl
                        cmds.move(expand_y_result, up_ctrl, moveY=True, objectSpace=True)
                    else:
                        # Get translate value based on current up_ctrl position
                        expand_y_result = cmds.getAttr('{0}.translateY'.format(ctrl))
                        expand_y_result += float(translate)
                        # Move up_ctrl
                        cmds.move(expand_y_result, up_ctrl, moveY=True, objectSpace=True)
                # If option Z is checked
                if self.guide_a_up_option_Z.isChecked():
                    # Check if reverse is checked
                    if self.guide_a_up_reverse.isChecked():
                        # Get translate value based on current up_ctrl position
                        expand_z_result = cmds.getAttr('{0}.translateZ'.format(ctrl))
                        expand_z_result -= float(translate)
                        # Move up_ctrl
                        cmds.move(expand_z_result, up_ctrl, moveZ=True, objectSpace=True)
                    else:
                        # Get translate value based on current up_ctrl position
                        expand_z_result = cmds.getAttr('{0}.translateZ'.format(ctrl))
                        expand_z_result += float(translate)
                        # Move up_ctrl
                        cmds.move(expand_z_result, up_ctrl, moveZ=True, objectSpace=True)

    # Function to zero out the tweak values in the text boxes
    def zero_out(self):
        self.tweak_X.setText('0.0')
        self.tweak_Y.setText('0.0')
        self.tweak_Z.setText('0.0')

    # Function to zero out the rotational values in the top group of the ctrls
    def zero_rotate(self):
        # Create variable for user selection
        sel = cmds.ls(sl=True)
        # Loop through the selection
        for ctrl in sel:
            # Create variable for the top group and ctrl pivot
            top_grp = cmds.listRelatives(ctrl, parent=True)[0]
            ctrl_pivot = cmds.xform(ctrl, query=True, translation=True, worldSpace=True)
            # Zero out rotational values
            cmds.xform(top_grp, rotation=[0, 0, 0], pivots=ctrl_pivot)

    # Create the window widget
    def window(self):
        print '..............', self
        print cmds

        window_name = 'Orient_Guides'

        # Check if window exists
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)

        if cmds.windowPref(window_name, exists=True):
            cmds.windowPref(window_name, remove=True)

        # Define window flags
        widget = QtWidgets.QWidget(parent=self.maya_main_window())
        widget.setWindowFlags(QtCore.Qt.Window)
        widget.setObjectName(window_name)
        widget.setWindowTitle(window_name.replace('_', ' '))
        widget.setMaximumSize(300, 180)
        widget.setMinimumSize(300, 180)

        # Define the layout of the window
        master_layout = QtWidgets.QVBoxLayout()
        widget.setLayout(master_layout)

        # Create columns for the window
        column_1 = QtWidgets.QHBoxLayout()
        column_2 = QtWidgets.QHBoxLayout()
        column_3 = QtWidgets.QHBoxLayout()
        column_4 = QtWidgets.QHBoxLayout()
        column_5 = QtWidgets.QHBoxLayout()
        column_6 = QtWidgets.QHBoxLayout()

        # Add columns to the layout
        master_layout.addLayout(column_1)
        master_layout.addLayout(column_2)
        master_layout.addLayout(column_3)
        master_layout.addLayout(column_4)
        master_layout.addLayout(column_5)
        master_layout.addLayout(column_6)

        # First column UI
        guide_b_label = QtWidgets.QLabel('B Jnt:')
        guide_b_option_group = QtWidgets.QButtonGroup(widget)
        self.guide_b_option_X = QtWidgets.QRadioButton()
        guide_b_option_X_label = QtWidgets.QLabel('X')
        self.guide_b_option_Y = QtWidgets.QRadioButton()
        guide_b_option_Y_label = QtWidgets.QLabel('Y')
        self.guide_b_option_Z = QtWidgets.QRadioButton()
        guide_b_option_Z_label = QtWidgets.QLabel('Z')
        self.guide_b_reverse = QtWidgets.QCheckBox()
        guide_b_reverse_label = QtWidgets.QLabel('Reverse')

        # Fix spacing in first column
        guide_b_label_spacer = QtWidgets.QSpacerItem(40, 0, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        guide_b_reverse_label_spacer = QtWidgets.QSpacerItem(30, 0, QtWidgets.QSizePolicy.Minimum,
                                                             QtWidgets.QSizePolicy.Expanding)

        # Add radio buttons to the button group
        guide_b_option_group.addButton(self.guide_b_option_X)
        guide_b_option_group.addButton(self.guide_b_option_Y)
        guide_b_option_group.addButton(self.guide_b_option_Z)

        # Add stuff to first column
        column_1.addItem(guide_b_label_spacer)
        column_1.addWidget(guide_b_label)
        column_1.addWidget(self.guide_b_option_X)
        column_1.addWidget(guide_b_option_X_label)
        column_1.addWidget(self.guide_b_option_Y)
        column_1.addWidget(guide_b_option_Y_label)
        column_1.addWidget(self.guide_b_option_Z)
        column_1.addWidget(guide_b_option_Z_label)
        column_1.addWidget(self.guide_b_reverse)
        column_1.addWidget(guide_b_reverse_label)
        column_1.addItem(guide_b_reverse_label_spacer)

        # Second column UI
        guide_a_up_label = QtWidgets.QLabel('A Up Ctrl:')
        guide_a_up_option_group = QtWidgets.QButtonGroup(widget)
        self.guide_a_up_option_X = QtWidgets.QRadioButton()
        guide_a_up_option_X_label = QtWidgets.QLabel('X')
        self.guide_a_up_option_Y = QtWidgets.QRadioButton()
        guide_a_up_option_Y_label = QtWidgets.QLabel('Y')
        self.guide_a_up_option_Z = QtWidgets.QRadioButton()
        guide_a_up_option_Z_label = QtWidgets.QLabel('Z')
        self.guide_a_up_reverse = QtWidgets.QCheckBox()
        guide_a_up_reverse_label = QtWidgets.QLabel('Reverse')

        # Fix spacing in second column
        guide_a_up_label_spacer = QtWidgets.QSpacerItem(18, 0, QtWidgets.QSizePolicy.Minimum,
                                                        QtWidgets.QSizePolicy.Expanding)
        guide_a_up_reverse_label_spacer = QtWidgets.QSpacerItem(30, 0, QtWidgets.QSizePolicy.Minimum,
                                                                QtWidgets.QSizePolicy.Expanding)

        # Add radio buttons to the button group
        guide_a_up_option_group.addButton(self.guide_a_up_option_X)
        guide_a_up_option_group.addButton(self.guide_a_up_option_Y)
        guide_a_up_option_group.addButton(self.guide_a_up_option_Z)

        # Add stuff to second column
        column_2.addItem(guide_a_up_label_spacer)
        column_2.addWidget(guide_a_up_label)
        column_2.addWidget(self.guide_a_up_option_X)
        column_2.addWidget(guide_a_up_option_X_label)
        column_2.addWidget(self.guide_a_up_option_Y)
        column_2.addWidget(guide_a_up_option_Y_label)
        column_2.addWidget(self.guide_a_up_option_Z)
        column_2.addWidget(guide_a_up_option_Z_label)
        column_2.addWidget(self.guide_a_up_reverse)
        column_2.addWidget(guide_a_up_reverse_label)
        column_2.addItem(guide_a_up_reverse_label_spacer)

        # Third column UI
        place = QtWidgets.QPushButton('Place')
        expand = QtWidgets.QPushButton('Expand')
        size = QtWidgets.QLabel('Size:')
        self.set_size = QtWidgets.QLineEdit('10')

        # Edit the interface
        self.set_size.setMaximumSize(50, 30)
        place.setMinimumSize(100, 20)
        expand.setMinimumSize(100, 20)

        # Add button to third column
        column_3.addWidget(place)
        column_3.addWidget(expand)
        column_3.addWidget(size)
        column_3.addWidget(self.set_size)

        # Connect function to button
        place.clicked.connect(lambda *args: self.orient('Place'))
        expand.clicked.connect(lambda *args: self.orient('Expand'))

        # Fourth column UI
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Add line separator to fourth column
        column_4.addWidget(line)

        # Fifth column UI
        tweak_label = QtWidgets.QLabel('Tweak:')
        self.tweak_X = QtWidgets.QLineEdit('0.0')
        self.tweak_Y = QtWidgets.QLineEdit('0.0')
        self.tweak_Z = QtWidgets.QLineEdit('0.0')
        zero_button = QtWidgets.QPushButton('Zero')

        # Add stuff to fifth column
        column_5.addWidget(tweak_label)
        column_5.addWidget(self.tweak_X)
        column_5.addWidget(self.tweak_Y)
        column_5.addWidget(self.tweak_Z)
        column_5.addWidget(zero_button)

        # Connecting function to button
        zero_button.clicked.connect(lambda *args: self.zero_out())

        # Sixth column UI
        rotate_plus_button = QtWidgets.QPushButton('Rotate +')
        rotate_minus_button = QtWidgets.QPushButton('Rotate -')
        rotate_zero = QtWidgets.QPushButton('Reset')

        # Connecting functions to button
        rotate_plus_button.clicked.connect(lambda *args: self.rotate_tweak('positive'))
        rotate_minus_button.clicked.connect(lambda *args: self.rotate_tweak('negative'))
        rotate_zero.clicked.connect(lambda *args: self.zero_rotate())

        # Add buttons to sixth column
        column_6.addWidget(rotate_plus_button)
        column_6.addWidget(rotate_minus_button)
        column_6.addWidget(rotate_zero)

        widget.show()


window = Orient_Guides()
window.window()