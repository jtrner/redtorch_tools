import sys
import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from standalone_blueprint_widget import BlueprintWidget
import resources



def run():
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    app = QApplication(sys.argv)
    widget = BlueprintWidget()
    app.setStyleSheet(style_sheet)
    widget.show()
    widget.raise_()
    widget.resize(500, 800)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()