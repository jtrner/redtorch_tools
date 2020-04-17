import QtCompat.QtWidgets as QtWidgets
import QtCompat.QtGui as QtGui
import QtCompat.QtCore as QtCore

import os
import shotgun
SG = shotgun.connect()

#----------------------------------------------------------------------------------------------------------------------- Globals

NOTES_EXPANDED = False

NOTE_HEADER_TITLES = ["Subject", "Note", "Author"]
SUBJECT_COL, CONTENT_COL, AUTHOR_COL = range(3)

INVALID_NOTE_PHRASES = ["Automatic rename", ]

#----------------------------------------------------------------------------------------------------------------------- IconNoteVersionItem

class IconNoteItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super(IconNoteItem, self).__init__(*args, **kwargs)
        self.setEditable(False)

#----------------------------------------------------------------------------------------------------------------------- IconNoteTreeView

class IconNoteTreeView(QtWidgets.QTreeView):
    def __init__(self):
        super(IconNoteTreeView, self).__init__()
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setWordWrap(True)
        self.setUniformRowHeights(False)
        self.setRootIsDecorated(False)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setAlternatingRowColors(True)

        self.note_model = IconNoteItemModel(0, 3, self)
        self.setModel(self.note_model)

        self.adjust_spacing()

    def add_notes(self, notes):
        self.note_model.removeRows(0, self.note_model.rowCount())
        for note in notes:
            self.add_item(note)

    def add_item(self, note):
        self.note_model.add_item(note)

    def adjust_spacing(self):
        self.setColumnWidth(SUBJECT_COL, 180)
        self.setColumnWidth(CONTENT_COL, 750)
        self.setColumnWidth(AUTHOR_COL, 85)

#----------------------------------------------------------------------------------------------------------------------- IconNoteItemModel

class IconNoteItemModel(QtGui.QStandardItemModel):
    def __init__(self, rows, columns, parent):
        super(IconNoteItemModel, self).__init__(rows, columns, parent)
        self.bad_child_count = 0

        self.header_setup()

    def header_setup(self):
        for index, title in enumerate(NOTE_HEADER_TITLES):
            self.setHeaderData(index, QtCore.Qt.Horizontal, title)

    def add_item(self, note):
        if not self.valid_note(note):
            return
        self.insertRow(0)
        self.add_subject(note["subject"])
        self.add_content(note["content"])
        self.add_author(note["user.HumanUser.name"])

    def add_subject(self, subject):
        subject_item = IconNoteItem(subject)
        self.setItem(0, SUBJECT_COL, subject_item)

    def add_content(self, content):
        content_item = IconNoteItem(content)
        if content:
            if "there were errors" in content.lower():
                content_item.setForeground(QtGui.QColor(225, 153, 153))
        self.setItem(0, CONTENT_COL, content_item)

    def add_author(self, author):
        author_item = IconNoteItem(author)
        self.setItem(0, AUTHOR_COL, author_item)

    def valid_note(self, note):
        if any([invalid_phrase in note for invalid_phrase in INVALID_NOTE_PHRASES]):
            return False
        return True
