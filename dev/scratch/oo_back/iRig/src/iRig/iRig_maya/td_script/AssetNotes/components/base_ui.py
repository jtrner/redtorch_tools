import QtCompat.QtWidgets as QtWidgets
import QtCompat.QtCore as QtCore

from AssetNotes.components import note_view
reload(note_view)


class AssetNoteseBase(QtWidgets.QMainWindow):
    def __init__(self):
        super(AssetNoteseBase, self).__init__()
        self.window_setup()

        self.episode_dropdown = QtWidgets.QComboBox()
        self.asset_list = QtWidgets.QListWidget()
        self.note_tree = note_view.IconNoteTreeView()

        self.list_layout = QtWidgets.QHBoxLayout()
        self.list_layout.addWidget(self.asset_list, 2)
        self.list_layout.addWidget(self.note_tree, 8)

        self.main_layout.addWidget(self.episode_dropdown)
        self.main_layout.addLayout(self.list_layout)

    def window_setup(self):
        self.window_width = 1400
        self.window_height = 650
        self.title = "Asset Notes"

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.resize(self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle(self.title)

        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QtWidgets.QVBoxLayout(self.main_widget)
