import functools
from rig_factory.objects.base_objects.weak_list import WeakList
import rigging_widgets.blendshape_builder.environment as env

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rig_factory.objects.node_objects.mesh import Mesh

class TargetGroupWidget(QFrame):

    edit_inbetween_signal = Signal(object)

    '''
    background_brush = QBrush(QColor(100, 100, 100))
    foreground_brush = QBrush(QColor(160, 160, 160))
    highlight_brush = QBrush(QColor(255, 200, 200))
    highlight_pen = QPen(QColor(255, 200, 200))
    bright_pen = QPen(QColor(200, 200, 200))
    dark_pen = QPen(QColor(120, 120, 120))
    transparent_brush = QBrush(QColor(180, 180, 180, 80))
    transparent_pen = QPen(QColor(180, 180, 180, 80))
    red_brush = QBrush(QColor(169, 95, 95))
    red_pen = QPen(QColor(169, 95, 95))
    text_label_pen = QPen(QColor(200, 200, 200, 35))
    hover_brush = QBrush(QColor(180, 180, 180, 75))
    hover_pen = QPen(QColor(180, 180, 180, 75))

    foreground_pen = QPen(QColor(200, 200, 200))
    key_brush = QBrush(QColor(145, 100, 100))
    key_pen = QPen(QColor(210, 100, 100))
    key_pen.setWidth(3)
    grey_brush = QBrush(QColor(89, 89, 89))
    selected_brush = QBrush(QColor(225, 45, 45))
    selected_pen = QPen(QColor(225, 45, 45))
    slider_pen = QPen(QColor(130, 130, 130))
    slider_pen.setWidth(0.1)
    '''

    outline_pen = QPen(QColor(130, 130, 130))
    outline_pen.setWidth(3)
    primary_selection_brush = QBrush(QColor(89, 146, 255))
    secondary_selection_brush = QBrush(QColor(150, 150, 150))
    inbetween_brush = QBrush(QColor(255, 255, 255))
    slider_brush = QBrush(QColor(75, 75, 75))
    draw_height = 35
    slider_height = 22
    outside_x_padding = 15
    outside_y_padding = 0
    weight_decimal_rounding = 3
    inbetween_radius = 4
    inbetween_base_size = 6

    def __init__(self, *args, **kwargs):
        super(TargetGroupWidget, self).__init__(*args, **kwargs)

        # Object_pointers
        self.target_group = None
        self.selected_inbetweens = WeakList()

        # Instance properties

        self.triangle_pixmap = QPixmap('%s/triangle.png' % env.images_directory)
        self.inbetween_pixmap = QPixmap('%s/inbetween.png' % env.images_directory)
        self.inbetween_ghost_pixmap = QPixmap('%s/inbetween_ghost.png' % env.images_directory)
        self._mouse_hover = False
        self._min_weight = -1.0
        self._max_weight = 1.0
        self._mouse_button_pressed = False
        self._current_weights = []
        # Widget setup
        self.setAttribute(Qt.WA_Hover)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(self.draw_height)
        self.setMaximumHeight(self.draw_height)
        self.selection_brush = self.primary_selection_brush
        '''
        self.big_font = QFont('arial', 0, True)
        self.big_font.setBold(True)
        self.small_font = QFont('', 5, False)
        self.giant_font = QFont('arial', 15, False)
        self.marker_height = 10
        self.text_height = 10
        self.text_width = 20

        self.knob_height = 40
        self.knob_width = 20
        self.position = None
        self.mouse_button = False

        self.hover_weight = None
        self.current_weight = 0.0
        self.keyframes = []

        #self.setMinimumWidth(300)

        '''

    def paint_outline(self, painter):

        painter.setPen(self.outline_pen)
        slider_rect = QRect(
            QPoint(self.outside_x_padding-5, self.slider_height + 8),
            QPoint(self.rect().right() - self.outside_x_padding + 5, self.slider_height - 8)
            )
        painter.drawRoundedRect(
            slider_rect,
            5.0, 5.0
        )

        for weight in self._current_weights:
            x_value = self.weight_to_x_position(weight)
            ellipse_radius = self.inbetween_radius + self.inbetween_base_size
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paint_base(self, painter):

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.slider_brush)
        slider_rect = QRect(
            QPoint(self.outside_x_padding-5, self.slider_height + 8),
            QPoint(self.rect().right() - self.outside_x_padding + 5, self.slider_height - 8)
            )
        painter.drawRoundedRect(
            slider_rect,
            5.0, 5.0
        )

        for weight in self._current_weights:

            x_value = self.weight_to_x_position(weight)
            ellipse_radius = self.inbetween_radius + self.inbetween_base_size
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paint_selected_inbetweens(self, painter):

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.selection_brush)

        for inbetween in self.selected_inbetweens:
            x_value = self.weight_to_x_position(inbetween.weight)
            ellipse_radius = self.inbetween_radius + self.inbetween_base_size - 2
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paint_inbetweens(self, painter):

        painter.setPen(Qt.NoPen)

        for inbetween in self.target_group.target_inbetweens:
            if inbetween in self.selected_inbetweens:
                painter.setBrush(self.slider_brush)
                x_value = self.weight_to_x_position(inbetween.weight)
                ellipse_radius = self.inbetween_radius + 2
                painter.drawEllipse(
                    QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                          QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
                )
            painter.setBrush(self.inbetween_brush)
            x_value = self.weight_to_x_position(inbetween.weight)
            ellipse_radius = self.inbetween_radius
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paintEvent(self, event):

        if self.target_group:

            painter = QPainter(self)
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            self._current_weights = [x.weight for x in self.target_group.target_inbetweens]

            if self._mouse_hover:
                self.paint_outline(painter)
            self.paint_base(painter)
            self.paint_selected_inbetweens(painter)

            self.paint_inbetweens(painter)
            painter.restore()

        '''
        painter.setPen(self.bright_pen)
        #painter.drawRect(widget_rect)
        painter.setPen(self.text_label_pen)
        painter.setBrush(self.transparent_brush)
        painter.setFont(self.giant_font)
        #painter.drawText(widget_rect, Qt.AlignHCenter, self.target_group.pretty_name.title())
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.slider_brush)
        painter.drawRoundedRect(QRect(
            QPoint(self.outside_x_padding-5, self.slider_height + 8),
            QPoint(widget_rect.right() - self.outside_x_padding + 5, self.slider_height - 8)
            ),
            5.0, 5.0
        )
        painter.setFont(self.big_font)
        painter.setFont(self.small_font)
        painter.setPen(self.foreground_pen)
        inbetween_weights = []
        if self.target_group:
            inbetween_weights = [x.weight for x in self.target_group.target_inbetweens]
        for i in range(int(self.min_weight), int(self.max_weight) +1):
            marker_weight = float(i)
            if marker_weight not in inbetween_weights and marker_weight != self.current_weight:
                if self.hover_weight is None or self.hover_weight < marker_weight - 0.02 or self.hover_weight > marker_weight + 0.02:
                    painter.setPen(self.transparent_pen)
                    painter.setBrush(self.transparent_brush)
                    x_value = self.weight_to_x_position(marker_weight)
                    marker_radius = 2
                    painter.drawEllipse(
                        QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                        QPoint(x_value + marker_radius, self.slider_height + marker_radius))
                    )
                    marker_radius = 2

                    if self.hover_weight is not None and marker_weight != self.current_weight:

                            text_rect = QRect(
                                x_value - 5,
                                int(self.slider_height - marker_radius - (self.text_height + 10)),
                                100,
                                100
                            )
                            painter.drawText(text_rect, str(marker_weight))

        # Current weight plug value
        if self.hover:

            x_value = self.weight_to_x_position(self.current_weight)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.bright_brush)
            marker_radius = 4
            painter.drawEllipse(
                QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                      QPoint(x_value + marker_radius, self.slider_height + marker_radius))
            )
            painter.setPen(self.bright_pen)
            painter.setFont(self.big_font)
            text_rect = QRect(x_value - marker_radius, self.slider_height - 25, 50,50)
            painter.drawText(text_rect, str(self.current_weight))

        # Current hover value

        if not self.mouse_button:
            painter.setPen(self.hover_pen)
            painter.setBrush(self.hover_brush)
            if self.hover_weight is not None:
                x_value = self.weight_to_x_position(self.hover_weight)
                marker_radius = 4
                painter.drawEllipse(
                    QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                          QPoint(x_value + marker_radius, self.slider_height + marker_radius))
                )


        if self.target_group:

            #painter.setBrush(self.grey_brush)
            #for inbetween in self.target_group.target_inbetweens:
            #    weight = inbetween.weight
            #    x_value = self.weight_to_x_position(weight)
            #    marker_radius = 15
            #    painter.drawEllipse(
            #        QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
            #              QPoint(x_value + marker_radius, self.slider_height + marker_radius))
            #    )
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.slider_brush)
            for inbetween in self.target_group.target_inbetweens:
                weight = inbetween.weight
                x_value = self.weight_to_x_position(weight)
                marker_radius = 12
                painter.drawEllipse(
                    QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                          QPoint(x_value + marker_radius, self.slider_height + marker_radius))
                )

            for inbetween in self.target_group.target_inbetweens:
                if inbetween in self.selected_inbetweens:
                    painter.setBrush(self.red_brush)
                    painter.setPen(self.red_pen)

                else:
                    painter.setBrush(self.foreground_brush)
                    painter.setPen(self.foreground_pen)

                weight = inbetween.weight
                x_value = self.weight_to_x_position(weight)
                painter.setPen(Qt.NoPen)
                marker_radius = 7
                painter.drawEllipse(
                    QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                          QPoint(x_value + marker_radius, self.slider_height + marker_radius))
                )
                painter.setFont(self.big_font)
                text_rect = QRect(x_value - marker_radius, self.slider_height - 25, 50,50)
                painter.drawText(text_rect, str(weight))


        '''

    #def set_current_target_group(self, target_group):
    #    if not isinstance(target_group, fob.FaceGroup):
    #        raise Exception('Invalid Type : %s' % target_group)
    #    if self.target_group == target_group:
    #        self.selection_brush = self.primary_selection_brush
    #    else:
    #        self.selection_brush = self.secondary_selection_brush

    #def set_target_group(self, target_group):
    #    if not isinstance(target_group, fob.FaceGroup):
    #        raise Exception('Invalid Type : %s' % target_group)
    #    if self.target_group:
    #        self.target_group.controller.target_group_changed.disconnect(self.set_current_target_group)
    #    self.target_group = target_group
    #    if self.target_group:
    #        self.target_group.controller.target_group_changed.connect(self.set_current_target_group)
    #    blendshape = target_group.blendshape
    #    group_index = blendshape.target_groups.index(target_group)
    #    self.repaint()

    def get_timeline_width(self):
        return self.rect().width() - (self.outside_x_padding * 2)

    def weight_to_percentage(self, weight):
        return (weight - self._min_weight) / (self._max_weight - self._min_weight)

    def weight_to_x_position(self, weight):
        return (weight - self._min_weight) / (self._max_weight - self._min_weight) * self.get_timeline_width() + self.outside_x_padding

    def percentage_to_weight(self, percentage):
        value = round((self._max_weight - self._min_weight) * percentage + self._min_weight, self.weight_decimal_rounding)
        if value < self._min_weight:
            return self._min_weight
        elif value > self._max_weight:
            return self._max_weight
        return value

    def x_position_to_weight(self, x_position):
        return self.percentage_to_weight(float((x_position - self.outside_x_padding)) / self.get_timeline_width())

    def mouseReleaseEvent(self, event):
        self._mouse_button_pressed = False
        super(TargetGroupWidget, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.hover_weight != 0:
            if self.target_group:
                inbetween = self.get_inbetween_at(event)
                if not inbetween:
                    blendshape = self.target_group.blendshape
                    group_index = blendshape.target_groups.index(self.target_group)
                    blendshape.plugs['weight'].element(group_index).set_value(self.hover_weight)
                    self.target_group.create_inbetween(weight=self.hover_weight)
                    self.repaint()
                else:
                    controller = inbetween.controller
                    controller.fit_view(inbetween.mesh_group)

        super(TargetGroupWidget, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self._mouse_button_pressed = True

        if self.target_group:
            controller = self.target_group.controller
            controller.set_blendshape_group(self.target_group)
            target_inbetween = self.get_inbetween_at(event)
            blendshape = self.target_group.blendshape
            base_geometry = blendshape.base_geometry
            modifiers = QApplication.keyboardModifiers()
            x_position = event.pos().x()
            self.hover_weight = round(self.x_position_to_weight(x_position), 1)
            self.set_weight_plug()
            if not modifiers == Qt.ShiftModifier:
                for i in range(len(self.selected_inbetweens)):
                    self.selected_inbetweens.pop(0)
            if target_inbetween in self.selected_inbetweens:
                self.selected_inbetweens.remove(target_inbetween)
            elif target_inbetween:
                self.selected_inbetweens.append(target_inbetween)
                if target_inbetween.mesh_group:
                    controller.select(target_inbetween.mesh_group)
            self.repaint()

            if event.button() == Qt.RightButton:
                menu = QMenu(self)
                if target_inbetween:
                    targets = get_mesh_children(target_inbetween.mesh_group)
                    if len(base_geometry) == 1:
                        menu.addAction('Apply selected', functools.partial(
                            controller.copy_selected_mesh_shape,
                            targets[0]
                        ))
                    else:
                        apply_menu = menu.addMenu('Apply selected to...')

                        for i in range(len(base_geometry)):
                            apply_menu.addAction(
                                base_geometry[i].get_selection_string().split('|')[-1],
                                functools.partial(
                                    controller.copy_selected_mesh_shape,
                                    targets[i]
                                )
                            )

                menu.exec_(self.mapToGlobal(event.pos()))
        super(TargetGroupWidget, self).mousePressEvent(event)


    def get_inbetween_at(self, event):
        if self.target_group:
            x_position = event.pos().x()
            y_position = event.pos().y()
            click_radius = self.inbetween_radius + self.inbetween_base_size
            if y_position > self.slider_height - click_radius and y_position < self.slider_height + click_radius:
                for inbetween in self.target_group.target_inbetweens:
                    inbetween_x_position = self.weight_to_x_position(inbetween.weight)
                    if x_position > inbetween_x_position - click_radius and x_position < inbetween_x_position + click_radius:
                        return inbetween

    def keyPressEvent(self, event):
        if self.target_group:
            key_object = event.key()
            if key_object == Qt.Key_Delete:
                if self.target_group:
                    for i in range(len(self.selected_inbetweens)):
                        self.selected_inbetweens.pop(0).delete()
        self.repaint()
        #super(TargetGroupWidget, self).keyPressEvent(event)

    def enterEvent(self, event):
        self._mouse_hover = True
        self.repaint()
        super(TargetGroupWidget, self).enterEvent(event)

    def leaveEvent(self, event):
        self._mouse_hover = False
        self.hover_weight = None
        self.current_weight = 0.0
        blendshape = self.target_group.blendshape
        group_index = blendshape.target_groups.index(self.target_group)
        blendshape.plugs['weight'].element(group_index).set_value(0.0)
        self.repaint()
        super(TargetGroupWidget, self).leaveEvent(event)

    def moveEvent(self, event):
        super(TargetGroupWidget, self).moveEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.hover_weight = self.x_position_to_weight(event.pos().x())
        else:
            self.hover_weight = round(self.x_position_to_weight(event.pos().x()), 1)
        if self._mouse_button_pressed:
            self.set_weight_plug()
        for i in range(int(self._min_weight), int(self._max_weight) + 1):
            marker_weight = float(i)
            if self.hover_weight < marker_weight + 0.02 and self.hover_weight > marker_weight - 0.02:
                self.hover_weight = marker_weight
        self.repaint()

        super(TargetGroupWidget, self).mouseMoveEvent(event)

    def get_weight_plug(self):
        if self.target_group:
            blendshape = self.target_group.blendshape
            group_index = blendshape.target_groups.index(self.target_group)
            self.current_weight = round(blendshape.plugs['weight'].element(group_index).get_value(), 3)
        self.repaint()

    def set_weight_plug(self):
        if self.target_group:
            blendshape = self.target_group.blendshape
            group_index = blendshape.target_groups.index(self.target_group)
            blendshape.plugs['weight'].element(group_index).set_value(self.hover_weight)
            self.current_weight = self.hover_weight
        self.repaint()

    #def wheelEvent(self, event):
    #    target_group = self.target_group
    #    if target_group:
    #        blendshape = target_group.blendshape
    #        group_index = blendshape.target_groups.index(target_group)
    #        if event.delta() > 0:
    #            self.current_weight = self.current_weight + 0.1
    #        if event.delta() < 0:
    #            self.current_weight = self.current_weight - 0.1

    #        blendshape = target_group.blendshape
    #        group_index = blendshape.target_groups.index(target_group)
    #        blendshape.plugs['weight'].element(group_index).set_value(self.current_weight)

    #    self.repaint()
    #    super(TargetGroupWidget, self).wheelEvent(event)

    def set_highlited(self, value):
        self._mouse_hover = value
        self.repaint()



def get_mesh_children(node):
    meshs = []
    for child in node.children:
        if isinstance(child, Mesh):
            meshs.append(child)
        else:
            meshs.extend(get_mesh_children(child))
    return meshs

def test(standalone=False, mock=False):
    import os
    import sys
    from rig_factory.controllers.blendshape_controller import BlendshapeController

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(blendshape_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone or mock:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        controller = BlendshapeController.get_controller(standalone=True, mock=mock)
        controller.load_from_json_file()
        target_group_widget = TargetGroupWidget()
        target_group_widget.show()
        target_group_widget.raise_()
        import maya.cmds as mc
        sphere, mesh = mc.polySphere(name='poly')
        mc.select(sphere, mesh)
        sys.exit(app.exec_())

    else:
        import sdk_builder.widgets.maya_dock as mdk

        target_group_widget = mdk.create_maya_dock(TargetGroupWidget)
        target_group_widget.setObjectName('target_group_widget')
        target_group_widget.setDockableParameters(width=507)
        target_group_widget.setWindowTitle('Target Group test')
        target_group_widget.show(dockable=True, area='left', floating=False, width=507)
        target_group_widget.setStyleSheet(style_sheet)

        target_group_widget.show()
        target_group_widget.raise_()
        return target_group_widget


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    os.system('start %s' % file_name)



if __name__ == '__main__':
    test(standalone=True)


if __name__ == '__main__':
    test()
