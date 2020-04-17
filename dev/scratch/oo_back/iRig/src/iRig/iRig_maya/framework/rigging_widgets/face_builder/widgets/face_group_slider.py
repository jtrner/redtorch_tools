import functools
import traceback
import weakref
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.base_objects.weak_list import WeakList
import rigging_widgets.face_builder.environment as env
from rig_factory.objects.face_network_objects.face_target import FaceTarget
import rig_factory.utilities.face_utilities.face_utilities as fut


class FaceGroupSlider(QFrame):

    edit_inbetween_signal = Signal(object)
    enter_sculpt_mode_signal = Signal(object)

    outline_pen = QPen(QColor(130, 130, 130))
    outline_pen.setWidth(3)
    primary_selection_brush = QBrush(QColor(89, 146, 255))
    secondary_selection_brush = QBrush(QColor(150, 150, 150))
    primary_selection_pen = QPen(QColor(89, 146, 255))
    secondary_selection_pen = QPen(QColor(150, 150, 150))
    white_brush = QBrush(QColor(255, 255, 255))
    transparent_brush = QBrush(QColor(255, 255, 255, 100))

    slider_brush = QBrush(QColor(75, 75, 75))
    draw_height = 35
    slider_height = 22
    outside_x_padding = 15
    outside_y_padding = 0
    decimal_rounding = 3
    target_radius = 4
    target_base_size = 6

    def __init__(self, *args, **kwargs):
        super(FaceGroupSlider, self).__init__(*args, **kwargs)
        # Object_pointers
        self._face_group = None
        self.selected_targets = WeakList()
        # Instance properties
        self.triangle_pixmap = QPixmap('%s/triangle.png' % env.images_directory)
        self.target_pixmap = QPixmap('%s/inbetween.png' % env.images_directory)
        self.inbetween_ghost_pixmap = QPixmap('%s/inbetween_ghost.png' % env.images_directory)
        self._mouse_hover = False
        self._min_value = -1.0
        self._max_value = 1.0
        self._mouse_enter_driver_value = None
        self.middle_mouse_pressed = False
        self._current_weights = []
        self.hover_driver_value = None
        # Widget setup
        self.setAttribute(Qt.WA_Hover)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(self.draw_height)
        self.setMaximumHeight(self.draw_height)
        self.selection_brush = self.primary_selection_brush
        self.selection_pen = self.primary_selection_pen

    @property
    def face_group(self):
        if self._face_group:
            return self._face_group()

    @face_group.setter
    def face_group(self, face_group):
        if face_group:
            self._face_group = weakref.ref(face_group)
        else:
            self._face_group = None

    def build_context_menu(self, event):
        controller = self.face_group.controller
        controller.set_face_group(self.face_group)
        face_network = self.face_group.face_network
        face_geometry = face_network.geometry
        face_target = self.get_face_target_at(event)
        #if self.face_group.blendshape_group:
        #    controller = face_target.controller
        #    controller.fit_view(*face_target.target_meshs)
        menu = QMenu()

        if not face_target:
            menu.addAction(
                'Create target',
                self.create_face_target_from_handle_positions
            )
            menu.addAction(
                'Create target (Selected Mesh)',
                functools.partial(
                    self.create_face_target_from_selected,
                    event
                )
            )

            # This can cause zombie SculptGroup node!
            #menu.addAction(
            #    'Create target ( Sculpt Mode )',
            #    self.create_face_target_from_sculpt_mode
            #)
        else:
            if face_target.keyframe_group:

                menu.addAction(
                    'Update target',
                    functools.partial(
                        self.update_target_handles,
                        face_target
                    )
                )
                menu.addAction(
                    'Update target ( Selected Mesh )',
                    functools.partial(
                        self.update_target_selected_mesh,
                        face_target
                    )
                )
                menu.addAction(
                    'Update target ( Selected Mesh Absolute)',
                    functools.partial(
                        self.update_target_selected_mesh,
                        face_target,
                        relative=False
                    )
                )
                menu.addAction(
                    'Update target ( Sculpt Mode )',
                    functools.partial(
                        self.enter_sculpt_mode,
                        face_target
                    )
                )

                tangent_menu = menu.addMenu('Set tangent(s)')
                for tangent_type in ['global', 'clamped', 'slow', 'fast', 'plateau', 'flat',
                                     'step_next', 'linear', 'shared2', 'auto', 'step', 'smooth', 'fixed']:
                    tangent_menu.addAction(
                        tangent_type,
                        functools.partial(
                            face_target.keyframe_group.set_keyframe_tangents,
                            tangent_type
                        )
                    )


                menu.addAction(
                    'Go to',
                    functools.partial(
                        self.go_to_target,
                        face_target
                    )
                )
        menu.addAction(
            'Select Driver',
            functools.partial(
                self.face_group.controller.select,
                self.face_group.driver_plug.get_node()
            )
        )

        delete_menu = menu.addMenu('Delete')

        delete_menu.addAction(
            'Selected FaceTaget(s)',
            self.delete_selected_targets
        )


        delete_menu.addAction(
            'face Group (%s)' % self.face_group,
            self.delete_group
        )

        menu.exec_(self.mapToGlobal(event.pos()))

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
            x_value = self.driver_value_to_x_position(weight)
            ellipse_radius = self.target_radius + self.target_base_size
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

            x_value = self.driver_value_to_x_position(weight)
            ellipse_radius = self.target_radius + self.target_base_size
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paint_selected_targets(self, painter):

        for inbetween in self.selected_targets:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.selection_brush)
            x_value = self.driver_value_to_x_position(inbetween.driver_value)
            ellipse_radius = self.target_radius + self.target_base_size - 2
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )
            painter.setPen(self.selection_pen)
            text_rect = QRect(x_value - 2, self.slider_height - 25, 50, 50)
            painter.drawText(text_rect, str(inbetween.driver_value))

    def paint_targets(self, painter):

        painter.setPen(Qt.NoPen)
        for face_target in self.face_group.face_targets:
            if face_target in self.selected_targets:
                painter.setBrush(self.slider_brush)
                x_value = self.driver_value_to_x_position(face_target.driver_value)
                ellipse_radius = self.target_radius + 2
                painter.drawEllipse(
                    QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                          QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
                )
            painter.setBrush(self.white_brush)
            x_value = self.driver_value_to_x_position(face_target.driver_value)
            ellipse_radius = self.target_radius
            painter.drawEllipse(
                QRect(QPoint(x_value - ellipse_radius, self.slider_height - ellipse_radius),
                      QPoint(x_value + ellipse_radius, self.slider_height + ellipse_radius))
            )

    def paint_curser(self, painter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.transparent_brush)

        x_value = self.driver_value_to_x_position(self.hover_driver_value)
        marker_radius = 2
        painter.drawEllipse(
            QRect(QPoint(x_value - marker_radius, self.slider_height - marker_radius),
                  QPoint(x_value + marker_radius, self.slider_height + marker_radius))
        )
        painter.setPen(self.outline_pen)
        text_rect = QRect(x_value - marker_radius, self.slider_height - 25, 50, 50)
        painter.drawText(text_rect, str(self.hover_driver_value))

    def paintEvent(self, event):

        if self.face_group:
            driver_values = [target.driver_value for target in self.face_group.face_targets]
            if len(driver_values) > 1:
                sorted_values = sorted(driver_values)
                self._min_value = sorted_values[0]
                self._max_value = sorted_values[-1]
            else:
                self._min_value = -1.0
                self._max_value = 1.0

            painter = QPainter(self)
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            self._current_weights = [x.driver_value for x in self.face_group.face_targets]

            if self._mouse_hover:
                self.paint_outline(painter)

            self.paint_base(painter)
            self.paint_selected_targets(painter)

            self.paint_targets(painter)

            if self._mouse_hover:
                if self.hover_driver_value is not None:
                    self.paint_curser(painter)

            painter.restore()

    def set_current_face_group(self, face_group):
        if self.face_group == face_group:
            self.selection_brush = self.primary_selection_brush
            self.selection_pen = self.primary_selection_pen
        else:
            self.selection_brush = self.secondary_selection_brush
            self.selection_pen = self.secondary_selection_pen

    def set_face_group(self, face_group):
        if self.face_group:
            self.face_group.controller.face_group_changed_signal.disconnect(self.set_current_face_group)
            self.face_group.controller.face_target_created_signal.disconnect(self.ownership_ended)
            self.face_group.controller.face_target_about_to_be_deleted_signal.disconnect(self.delete_face_target)
        self.face_group = face_group
        if self.face_group:
            self.face_group.controller.face_group_changed_signal.connect(self.set_current_face_group)
            self.face_group.controller.face_target_created_signal.connect(self.ownership_ended)
            self.face_group.controller.face_target_about_to_be_deleted_signal.connect(self.delete_face_target)

        self.repaint()

    #def start_disown(self, member, owner):

    #    if owner == self.face_group:
    #        self.setUpdatesEnabled(False);

    #def end_disown(self, member, owner):
    #    if owner == self.face_group:
    #        self.setUpdatesEnabled(True)
    #        self.repaint()

    def delete_face_target(self, target):
        if target.face_group == self.face_group:
            if target in self.selected_targets:
                self.selected_targets.remove(target)
            self.repaint()
            QApplication.processEvents()

    def ownership_ended(self, target):
        if target.face_group == self.face_group:
            self.repaint()
            QApplication.processEvents()

    def get_timeline_width(self):
        return self.rect().width() - (self.outside_x_padding * 2)

    def weight_to_percentage(self, weight):
        return (weight - self._min_value) / (self._max_value - self._min_value)

    def driver_value_to_x_position(self, weight):

        return (weight - self._min_value) / (self._max_value - self._min_value) * self.get_timeline_width() + self.outside_x_padding

    def percentage_to_weight(self, percentage):
        value = round((self._max_value - self._min_value) * percentage + self._min_value, self.decimal_rounding)
        if value < self._min_value:
            return self._min_value
        elif value > self._max_value:
            return self._max_value
        return value

    def x_position_to_driver_value(self, x_position):
        return self.percentage_to_weight(float((x_position - self.outside_x_padding)) / self.get_timeline_width())

    def mouseReleaseEvent(self, event):
        self.middle_mouse_pressed = False
        super(FaceGroupSlider, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.hover_driver_value != 0:
            if self.face_group:
                face_target = self.get_face_target_at(event)
                face_target.controller.fit_view(face_target.target_meshs)
        super(FaceGroupSlider, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if self.face_group:
            self.middle_mouse_pressed = False
            controller = self.face_group.controller
            controller.set_face_group(self.face_group)
            if event.button() == Qt.MiddleButton:
                self.middle_mouse_pressed = True
            elif event.button() == Qt.LeftButton:
                self.handle_selection(event)
            elif event.button() == Qt.RightButton:
                self.build_context_menu(event)
            self.repaint()
        super(FaceGroupSlider, self).mousePressEvent(event)

    def handle_selection(self, event):
        controller = self.face_group.controller
        controller.set_face_group(self.face_group)
        face_target = self.get_face_target_at(event)
        modifiers = QApplication.keyboardModifiers()
        if not modifiers == Qt.ShiftModifier:
            for i in range(len(self.selected_targets)):
                self.selected_targets.pop(0)
        if face_target in self.selected_targets:
            self.selected_targets.remove(face_target)
        elif face_target:
            self.selected_targets.append(face_target)
        controller.select(cl=True)
        if self.selected_targets:
            controller.select(self.selected_targets)
        else:
            controller.select(self.face_group)

    def create_face_target_from_sculpt_mode(self):
        face_target = self.create_face_target_from_handle_positions()
        if face_target:
            self.enter_sculpt_mode_signal.emit(face_target)

    def enter_sculpt_mode(self, face_target):
        if not face_target.target_meshs:
            raise Exception('face target has no target meshs')
        self.go_to_target(face_target)
        if self.check_driver_value(self.face_group.driver_plug, face_target.driver_value):
            self.enter_sculpt_mode_signal.emit(face_target)

    def go_to_target(self, face_target):
        fut.go_to_target(face_target)
        self._mouse_enter_driver_value = face_target.driver_value

    def update_target_handles(self, face_target):
        try:
            if self.check_driver_value(
                    self.face_group.driver_plug,
                    face_target.driver_value
            ):
                face_target.controller.update_target_handles(face_target)
        except Exception, e:
            print traceback.format_exc()
            self.raise_warning(e.message)

    def update_target_selected_mesh(self, face_target, relative=True):
        try:
            if self.check_driver_value(self.face_group.driver_plug, face_target.driver_value):
                face_target.controller.update_target_selected_mesh(face_target, relative=relative)
        except Exception, e:
            print traceback.format_exc()
            self.raise_warning(e.message)

    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()


    def create_face_target_from_selected(self, event):
        try:
            new_driver_value, success = QInputDialog.getDouble(
                self,
                'Create face target from selected',
                'Enter a driver-value',
                value=round(
                    self.face_group.driver_plug.get_value(),
                    self.decimal_rounding
                ),
                min=-10000.0,
                max=10000.0,
                decimals=self.decimal_rounding

            )
            if success:
                if self.check_driver_value(self.face_group.driver_plug, new_driver_value):
                    controller = self.face_group.controller
                    face_target = self.face_group.create_face_target(
                        *controller.get_selected_mesh_names(),
                        driver_value=new_driver_value
                    )
                    self.selected_targets.append(face_target)
            self.repaint()
        except Exception, e:
            print traceback.format_exc()
            self.raise_warning(e.message)

    def check_driver_value(self, plug, value):
        if plug.get_value() != value:
            reply = QMessageBox.question(
                self,
                "Plug value doesnt match driver value",
                'The plug "%s" is not currently set to the driver value "%s".\nWould you like to continue anyway?' % (
                    plug,
                    value
                ),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True

    def create_face_target_from_handle_positions(self):
        new_driver_value, success = QInputDialog.getDouble(
            self,
            'Create face target',
            'Enter a driver-value',
            value=round(
                self.face_group.driver_plug.get_value(),
                self.decimal_rounding
            ),
            min=-10000.0,
            max=10000.0,
            decimals=self.decimal_rounding

        )
        if success:
            if self.check_driver_value(self.face_group.driver_plug, new_driver_value):
                face_target = self.face_group.create_face_target(
                    driver_value=new_driver_value
                )
                self.selected_targets.append(face_target)
                return face_target
        self.repaint()

    def change_target_driver_value(self, face_target):
        """
        Turns out this is more complicated than it seems..
        Will need to have keys swap places when range exceeds neighbors..
        :param face_target:
        :return:
        """
        new_driver_value, success = QInputDialog.getDouble(
            self,
            'Set Driver Value for %s' % face_target,
            'Enter a driver-value',
            value=face_target.driver_value,
            min=-10000.0,
            max=10000.0
        )
        if success:
            face_target.set_driver_value(new_driver_value)
            self.repaint()

    def get_face_target_at(self, event):
        if self.face_group:
            x_position = event.pos().x()
            y_position = event.pos().y()
            click_radius = self.target_radius + self.target_base_size
            if y_position > self.slider_height - click_radius and y_position < self.slider_height + click_radius:
                for face_target in self.face_group.face_targets:
                    inbetween_x_position = self.driver_value_to_x_position(face_target.driver_value)
                    if x_position > inbetween_x_position - click_radius and x_position < inbetween_x_position + click_radius:
                        return face_target

    def delete_selected_targets(self):
        controller = self.face_group.controller
        controller.delete_objects([x for x in self.selected_targets if x.driver_value != 0.0])

    def delete_group(self):
        controller = self.face_group.controller
        controller.delete_objects([self.face_group])

    def enterEvent(self, event):
        if self.face_group and self.face_group.driver_plug:
            self._mouse_enter_driver_value = self.face_group.driver_plug.get_value()
            self.middle_mouse_pressed = False
            self._mouse_hover = True
            self.repaint()
        super(FaceGroupSlider, self).enterEvent(event)

    def leaveEvent(self, event):
        self.middle_mouse_pressed = False
        self._mouse_hover = False
        self.hover_driver_value = None
        #try:
        #    self.face_group.driver_plug.set_value(self._mouse_enter_driver_value)
        #except:
        #    print 'Unable to set attribute "%s"' % self.face_group.driver_plug
        self.repaint()
        super(FaceGroupSlider, self).leaveEvent(event)

    def moveEvent(self, event):
        super(FaceGroupSlider, self).moveEvent(event)

    def mouseMoveEvent(self, event):
        if self.middle_mouse_pressed:
            value = self.x_position_to_driver_value(event.pos().x())
            try:
                self.face_group.driver_plug.set_value(value)
            except:
                print 'Unable to set attribute "%s"' % self.face_group.driver_plug
            self.repaint()
        self.handle_hover_value(event)
        self.repaint()

        super(FaceGroupSlider, self).mouseMoveEvent(event)

    def handle_hover_value(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            hover_driver_value = self.x_position_to_driver_value(event.pos().x())
        else:
            hover_driver_value = round(self.x_position_to_driver_value(event.pos().x()), 2)
        if hover_driver_value == -0.0:
            hover_driver_value = 0.0
        self.hover_driver_value = hover_driver_value

    def wheelEvent(self, event):
        face_group = self.face_group
        #if face_group:
        #    if self.hover_driver_value
        #    if event.delta() > 0:
        #        self.hover_driver_value += 0.05
        #    if event.delta() < 0:
        #        self.hover_driver_value -= 0.05
            #self.face_group.driver_plug.set_value(self.hover_driver_value)

        self.repaint()
        super(FaceGroupSlider, self).wheelEvent(event)

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
    from rig_factory.controllers.face_controller import FaceController

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(face_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone or mock:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        controller = FaceController.get_controller(standalone=True, mock=mock)
        controller.load_from_json_file()
        target_group_widget = FaceGroupSlider()
        target_group_widget.show()
        target_group_widget.raise_()
        import maya.cmds as mc
        sphere, mesh = mc.polySphere(name='poly')
        mc.select(sphere, mesh)

        sys.exit(app.exec_())


    else:
        import sdk_builder.widgets.maya_dock as mdk

        target_group_widget = mdk.create_maya_dock(FaceGroupSlider)
        target_group_widget.setObjectName('target_group_widget')
        target_group_widget.setDockableParameters(width=507)
        target_group_widget.setWindowTitle('Target Group test')
        target_group_widget.show(dockable=True, area='left', floating=False, width=507)
        target_group_widget.setStyleSheet(style_sheet)

        target_group_widget.show()
        target_group_widget.raise_()
        return target_group_widget


if __name__ == '__main__':
    test(standalone=True)
