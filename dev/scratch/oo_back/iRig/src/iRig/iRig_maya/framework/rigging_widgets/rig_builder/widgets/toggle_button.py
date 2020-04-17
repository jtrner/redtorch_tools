import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


class ToggleButton(QWidget):

    toggled = Signal(bool)

    def __init__(self, parent):
        super(ToggleButton, self).__init__(parent)
        self.background_color = QColor(80, 80, 80)
        self.lit_background_color = QColor(90, 120, 130)

        self.knob_color = QColor(120, 120, 120)
        self.lit_knob_color = QColor(150, 190, 200)

        self.edge_color = QColor(110, 110, 110)
        self.lit_edge_color = QColor(135, 135, 135)

        #self.edge_pen = QPen(self.edge_color)
        #self.lit_edge_pen = QPen(self.lit_edge_color)
        #self.edge_pen.setWidth(2)
        #self.lit_edge_pen.setWidth(2)
        self.edge_pen = Qt.NoPen
        self.lit_edge_pen = Qt.NoPen

        self.width = 34
        self.height = 20
        self.padding = 2
        self.position = 0.0
        self.value = False

        app = QApplication
        screen_resolution = app.desktop().screenGeometry()
        self.size = 2.0
        if screen_resolution.height() > 1080:
            self.size = 4.0
        self.setMinimumHeight(self.height*self.size)
        self.setMinimumWidth(self.width*self.size)
        self.setMaximumHeight(self.height*self.size)
        self.setMaximumWidth(self.width*self.size)

    def mousePressEvent(self, event):
        self.set_value(not self.value)
        self.toggled.emit(self.value)

    def set_value(self, value):
        self.value = value
        if value:
            self.position = 1.0
        else:
            self.position = 0.0
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.position > 0.9:
            painter.setPen(self.lit_edge_pen)
            painter.setBrush(self.lit_background_color)

        else:
            painter.setPen(self.edge_pen)
            painter.setBrush(self.background_color)

        painter.save()
        rect = self.rect()
        rect.adjust(
            self.padding,
            self.padding,
            self.padding*-1,
            self.padding*-1
        )
        painter.drawRoundedRect(rect, rect.height()/2, rect.width()/2)
        painter.setPen(Qt.NoPen)

        if self.position > 0.9:
            painter.setBrush(self.lit_knob_color)
        else:
            painter.setBrush(self.knob_color)

        knob_rectangle = QRect(float(self.width*self.size - self.height*self.size) * self.position, 0, self.height*self.size, self.height*self.size)
        painter.drawEllipse(knob_rectangle)

        painter.restore()
