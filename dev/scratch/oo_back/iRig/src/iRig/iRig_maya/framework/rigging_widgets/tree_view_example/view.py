from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class MyView(QTreeView):

    def __init__(self, *args, **kwargs):
        super(MyView, self).__init__(*args, **kwargs)

        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.header().setStretchLastSection(True)


        try:
            self.header().setResizeMode(QHeaderView.ResizeToContents)
        except:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)