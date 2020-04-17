import maya.OpenMayaUI as apiUI
maya_version = float(mc.about(version=True))

if maya_version < 2017.0:
    from shiboken import wrapInstance

elif maya_version > 2016.0:
    from shiboken2 import wrapInstance
else:
    raise Exception('No Shiboken Found')

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

view = apiUI.M3dView()
apiUI.M3dView.getM3dViewFromModelPanel('modelPanel4', view)
viewWidget = wrapInstance(long(view.widget()), QWidget)


global myBtn
myBtn = QPushButton(viewWidget)
myBtn.setText('testing!')
myBtn.move(5, 5) #Relative to top-left corner of viewport
myBtn.show()