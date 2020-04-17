import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from functools import partial


class QCustomDelegate (QItemDelegate):
    signalNewPath = Signal(object)

    def __init__(self, *args, **kwargs):
        super(QCustomDelegate, self).__init__(*args, **kwargs)
        self.pixmap = QPixmap(
            'D:/pipeline/paxtong/dev/git_repo/rigging_framework/rigging_widgets/rig_builder/static/images/meta_cube.png').scaled(
            180, 180, Qt.KeepAspectRatio)

    def createEditor (self, parentQWidget, optionQStyleOptionViewItem, indexQModelIndex):
        column = indexQModelIndex.column()
        if column == 0:
            editorQWidget = QPushButton(parentQWidget)
            editorQWidget.released.connect(partial(self.requestNewPath, indexQModelIndex))
            return editorQWidget
        else:
            return QItemDelegate.createEditor(self, parentQWidget, optionQStyleOptionViewItem, indexQModelIndex)

    def setEditorData (self, editorQWidget, indexQModelIndex):
        column = indexQModelIndex.column()
        if column == 0:
            textQString = indexQModelIndex.model().data(indexQModelIndex, Qt.EditRole).toString()
            editorQWidget.setText(textQString)
        else:
            QItemDelegate.setEditorData(self, editorQWidget, indexQModelIndex)

    def setModelData (self, editorQWidget, modelQAbstractItemModel, indexQModelIndex):
        column = indexQModelIndex.column()
        if column == 0:
            textQString = editorQWidget.text()
            modelQAbstractItemModel.setData(indexQModelIndex, textQString, Qt.EditRole)
        else:
            QItemDelegate.setModelData(self, editorQWidget, modelQAbstractItemModel, indexQModelIndex)

    def updateEditorGeometry(self, editorQWidget, optionQStyleOptionViewItem, indexQModelIndex):
        column = indexQModelIndex.column()
        if column == 0:
            editorQWidget.setGeometry(optionQStyleOptionViewItem.rect)
        else:
            QItemDelegate.updateEditorGeometry(self, editorQWidget, optionQStyleOptionViewItem, indexQModelIndex)

    def requestNewPath (self, indexQModelIndex):
        self.signalNewPath.emit(indexQModelIndex)

    def paint (self, painterQPainter, optionQStyleOptionViewItem, indexQModelIndex):
        column = indexQModelIndex.column()
        if column == 0:
            textQString = str(indexQModelIndex.model().data(indexQModelIndex, Qt.EditRole))
            painterQPainter.drawPixmap (
                optionQStyleOptionViewItem.rect.x(),
                optionQStyleOptionViewItem.rect.y(),
                self.pixmap
            )
        else:
            QItemDelegate.paint(self, painterQPainter, optionQStyleOptionViewItem, indexQModelIndex)

class QCustomTreeWidget (QTreeWidget):
    def __init__(self, parent=None):
        super(QCustomTreeWidget, self).__init__(parent)
        self.setColumnCount(1)
        myQCustomDelegate = QCustomDelegate()
        self.setItemDelegate(myQCustomDelegate)
        myQCustomDelegate.signalNewPath.connect(self.getNewPath)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)

    def addMenu (self, parentQTreeWidgetItem = None):
        if parentQTreeWidgetItem == None:
            parentQTreeWidgetItem = self.invisibleRootItem()
        currentQTreeWidgetItem = QTreeWidgetItem(parentQTreeWidgetItem)
        #currentQTreeWidgetItem.setData(0, Qt.EditRole)
        currentQTreeWidgetItem.setFlags(currentQTreeWidgetItem.flags() | Qt.ItemIsEditable)
        for i in range(self.columnCount()):
            currentQSize = currentQTreeWidgetItem.sizeHint(i)
            currentQTreeWidgetItem.setSizeHint(i, QSize(currentQSize.width(), currentQSize.height() + 200))

    def getNewPath (self, indexQModelIndex):
        currentQTreeWidgetItem = self.itemFromIndex(indexQModelIndex)
        pathQStringList = QFileDialog.getOpenFileNames()
        if pathQStringList.count() > 0:
            textQString = pathQStringList.first()
            currentQTreeWidgetItem.setData(indexQModelIndex.column(), Qt.EditRole, textQString)
            print textQString

class QCustomQWidget (QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.myQCustomTreeWidget = QCustomTreeWidget(self)
        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.addWidget(self.myQCustomTreeWidget)
        self.setLayout(self.allQHBoxLayout)
        self.myQCustomTreeWidget.addMenu()
        self.myQCustomTreeWidget.addMenu()
        self.myQCustomTreeWidget.addMenu()
        self.myQCustomTreeWidget.addMenu()
        self.myQCustomTreeWidget.addMenu()
        self.myQCustomTreeWidget.addMenu()


app = QApplication([])
myQCustomQWidget = QCustomQWidget()
myQCustomQWidget.show()
sys.exit(app.exec_())