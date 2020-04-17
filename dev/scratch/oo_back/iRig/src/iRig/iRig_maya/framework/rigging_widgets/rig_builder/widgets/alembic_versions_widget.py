from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.models.alembic_versions_model import AlembicVersionsModel


class AlembicVersionsWidget(QWidget):

    _controller = None
    _model = None

    def __init__(self, *args, **kwargs):
        super(AlembicVersionsWidget, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        refresh_button = QPushButton('refresh'.title())
        main_layout.addWidget(refresh_button)
        view = QListView()
        main_layout.addWidget(view)
        refresh_button.pressed.connect(self.refresh)
        self._model = model = AlembicVersionsModel()
        view.setModel(model)

    def refresh(self):
        self.controller = self.controller

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller
        self._model.controller = controller
        self._model.refresh_data()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    win = AlembicVersionsWidget()
    win.show()

    app.exec_()