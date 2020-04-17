from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects.face_target import FaceTarget
import rig_math.utilities as rmu

import weakref


def iseven(number):
    if (number % 2) == 0:
        return False
    else:
        return True


class FaceGroupDelegate(QItemDelegate):

    # Colors
    target_color = QColor(190, 190, 190)
    grey_color = QColor(130, 130, 130)
    hover_color = QColor(100, 100, 100)
    selected_color = QColor(126, 144, 153)
    target_selection_color = QColor(133, 170, 188)
    background_color = QColor(80, 80, 80)
    selected_background_color = QColor(93, 93, 93)
    hover_selected_color = target_selection_color.lighter(120)
    focus_color = target_selection_color
    slot_color = QColor(65, 65, 65)
    curser_color = QColor(244, 244, 244, 50)
    handle_color = target_selection_color.lighter(120)
    active_color = hover_selected_color
    black_color = QColor(0.0, 0.0, 0.0)
    red_color = QColor(200.0, 100.0, 100.0)
    blue_color = QColor(145.0, 145.0, 255.0)
    purple_color = QColor(175.0, 100.0, 255.0)
    # Pens
    grey_pen = QPen(grey_color)
    hover_pen = QPen(hover_color)
    hover_selected_group_pen = QPen(hover_selected_color)
    hover_selected_target_pen = QPen(hover_selected_color)
    red_pen = QPen(red_color)
    focus_group_pen = QPen(focus_color)
    focus_target_pen = QPen(focus_color)
    selected_pen = QPen(selected_color)
    target_selected_pen = QPen(target_selection_color)
    curser_pen = QPen(curser_color)
    insert_pen = QPen(grey_color)
    insert_pen.setStyle(Qt.DotLine)

    # Brushes
    selected_brush = QBrush(selected_color)
    target_brush = QBrush(target_color)
    background_brush = QBrush(background_color)
    slot_brush = QBrush(slot_color)
    grey_brush = QBrush(grey_color)
    hover_brush = QBrush(hover_color)
    hover_selected_brush = QBrush(hover_selected_color)
    selected_background_brush = QBrush(selected_background_color)
    curser_brush = QBrush(curser_color)
    handle_brush = QBrush(handle_color)
    active_brush = QBrush(active_color)
    black_brush = QBrush(black_color)
    red_brush = QBrush(red_color)
    blue_brush = QBrush(blue_color)
    purple_brush = QBrush(purple_color)


    def __init__(self, *args, **kwargs):
        super(FaceGroupDelegate, self).__init__(*args, **kwargs)
        self.controller = None
        self.clicked_groups = weakref.WeakKeyDictionary()
        self.min = -1.0
        self.max = 1.0
        self.start_point = None
        self.end_point = None
        self.disabled = False
        self.selected = False
        self.item_height = 60
        self.quarter_height = 0.0

    def paint(self, painter, option, index):
        if not self.disabled:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            column = index.column()
            view = option.styleObject
            rect = view.visualRect(index)
            if column == 1:
                item = view.get_source_item(index)
                if isinstance(item, FaceGroup):
                    face_group_name = item.name
                    initial_value = item.initial_value
                    self.selected = item in item.face_network.selected_face_groups
                    hovering_over_group = view.hover_item == face_group_name
                    hover_target = None
                    hover_item_driver_value = None
                    for x in item.face_targets:
                        if view.hover_item == x.name:
                            hover_target = x.name
                            hover_item_driver_value = x.driver_value
                    hovering_over_target = bool(hover_target)
                    selected_face_group_names = [x.name for x in item.face_network.selected_face_groups]
                    target_driver_values = []
                    blendshape_driver_values = []
                    sdk_driver_values = []
                    sdk_blendshape_driver_values = []

                    for target in item.face_targets:
                        target_driver_values.append(target.driver_value)
                        if target.blendshape_inbetween and target.keyframe_group:
                            sdk_blendshape_driver_values.append(target.driver_value)
                        elif target.blendshape_inbetween:
                            blendshape_driver_values.append(target.driver_value)
                        elif target.keyframe_group:
                            sdk_driver_values.append(target.driver_value)
                    selected_target_driver_values = [x.driver_value for x in item.face_network.selected_face_targets if x.face_group.name == face_group_name]
                    focus_items = view.focus_items
                    insert_value = view.insert_value

                    targets_in_focus = False
                    if focus_items and isinstance(
                        view.controller.named_objects.get(
                            focus_items[0],
                            None
                        ),
                        FaceTarget
                    ):
                        targets_in_focus = True
                    del item

                    self.min, self.max = view.calculate_slider_min_max(index)
                    self.start_point, self.end_point = view.get_end_points(index)
                    self.quarter_height = view.get_quarter_height(index)
                    mock_driver_value = view.mock_plug_values.get(face_group_name, initial_value)
                    #assert all([isinstance(x, str) for x in self.focus_items])
                    #assert self.start_point is not None
                    #assert self.end_point is not None
                    hover_driver_value = None
                    if view.x_value:
                        hover_driver_value = rmu.remap_value(
                            float(view.x_value),
                            self.start_point,
                            self.end_point,
                            self.min,
                            self.max
                        )
                    #print 'Done Getting Object info'
                    pen_width = self.get_outline_pen_width(rect)
                    half_pen_width = int(round(float(pen_width * 0.6)))
                    quarter_pen_width = int(round(float(half_pen_width * 0.5)))
                    self.selected_pen.setWidth(pen_width)
                    self.hover_pen.setWidth(pen_width)
                    self.grey_pen.setWidth(pen_width)
                    self.curser_pen.setWidth(quarter_pen_width)
                    self.focus_group_pen.setWidth(pen_width)
                    self.red_pen.setWidth(pen_width)
                    self.hover_selected_group_pen.setWidth(pen_width)
                    self.insert_pen.setWidth(half_pen_width)
                    target_pen_width = int(round(float(pen_width) * 0.8))
                    self.hover_selected_target_pen.setWidth(target_pen_width)
                    self.focus_target_pen.setWidth(target_pen_width)
                    driver_plug_active = mock_driver_value != initial_value

                    # Group outlines
                    painter.setBrush(Qt.BrushStyle())
                    if face_group_name in selected_face_group_names:
                        if face_group_name in focus_items:
                            if view.deleting_items:
                                outline_pen = self.red_pen
                            else:
                                outline_pen = self.focus_group_pen
                        elif focus_items and not targets_in_focus:
                            outline_pen = Qt.NoPen
                        elif hovering_over_group:
                            outline_pen = self.hover_selected_group_pen
                        else:
                            outline_pen = self.selected_pen
                    elif view.hover_item == face_group_name:
                        outline_pen = self.hover_pen
                    else:
                        outline_pen = Qt.NoPen
                    if hover_driver_value is not None and hovering_over_group and not view.drag_item:
                        painter.setPen(self.grey_pen)
                        painter.setBrush(Qt.BrushStyle())
                        self.paint_curser(painter, rect, hover_driver_value, padding=0.0, width_multiply=0.1)
                    painter.setPen(outline_pen)
                    painter.setBrush(Qt.BrushStyle())

                    # Slot
                    self.paint_slot(painter, rect)
                    self.paint_targets(target_driver_values, painter, rect, skip_zero=True)

                    # Curser
                    is_drag_item = view.drag_item == face_group_name
                    if not focus_items:
                        self.paint_curser(
                            painter,
                            rect,
                            view.mock_plug_values.get(face_group_name, initial_value),
                            padding=0.0,
                            width_multiply=0.33333
                        )
                    # Background
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(self.slot_brush)
                    inner_padding = int(round(float(self.quarter_height) / 30))
                    self.paint_slot(painter, rect, padding=inner_padding)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(self.slot_brush)
                    self.paint_targets(target_driver_values, painter, rect, padding=inner_padding, skip_zero=True)
                    self.grey_pen.setWidth(half_pen_width)
                    self.selected_pen.setWidth(half_pen_width)
                    self.hover_pen.setWidth(half_pen_width)
                    self.target_selected_pen.setWidth(half_pen_width)

                    target_padding = int(round(float(self.quarter_height) / 2.5))

                    # Hover Targets
                    if not focus_items:
                        painter.setPen(self.hover_pen)
                        painter.setBrush(Qt.BrushStyle())
                        #if driver_plug_active:
                        self.paint_hover_targets(painter, rect, hover_item_driver_value, padding=target_padding)

                    # Selected Targets
                    painter.setBrush(Qt.BrushStyle())
                    painter.setPen(Qt.NoPen)
                    if targets_in_focus and view.deleting_items:
                        painter.setPen(self.red_pen)
                    elif hovering_over_target:
                        painter.setPen(self.hover_selected_target_pen)
                    else:
                        painter.setPen(self.target_selected_pen)

                    self.paint_selected_targets(
                        selected_target_driver_values,
                        painter,
                        rect,
                        padding=target_padding
                    )


                    # SDK Targets
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(self.target_brush)
                    target_padding = int(round(float(self.quarter_height) / 1.1))
                    self.paint_targets(
                        sdk_driver_values,
                        painter,
                        rect,
                        padding=target_padding,
                        skip_zero=True
                    )
                    # Blendshape Targets

                    painter.setBrush(self.blue_brush)
                    self.paint_targets(
                        blendshape_driver_values,
                        painter,
                        rect,
                        padding=target_padding,
                        skip_zero=True
                    )

                    # Blendshape SDK Targets

                    painter.setBrush(self.blue_brush)
                    self.paint_targets(
                        sdk_blendshape_driver_values,
                        painter,
                        rect,
                        padding=target_padding,
                        skip_zero=True
                    )

                    if is_drag_item and not driver_plug_active:
                        painter.setBrush(self.hover_selected_brush)
                    else:
                        painter.setBrush(self.grey_brush)
                    self.paint_zero(initial_value, painter, rect, padding=0.0)
                    if view.insert_value is not None and view.insert_target_group == face_group_name:
                        painter.setBrush(self.slot_brush)
                        painter.setPen(self.insert_pen)
                        self.paint_target(
                            insert_value,
                            painter,
                            rect,
                            0.0
                        )

                    # Active Handle
                    if not focus_items and driver_plug_active:
                        painter.setBrush(self.handle_brush)
                        painter.setPen(self.hover_selected_target_pen)
                        self.paint_curser(
                            painter,
                            rect,
                            view.mock_plug_values.get(face_group_name, 0.0),
                            padding=0.0,
                            width_multiply=1.0
                        )

                    # Grabbed Handle
                    if view.drag_item == face_group_name and driver_plug_active and not focus_items:
                        painter.setBrush(self.handle_brush)
                        painter.setPen(self.hover_selected_target_pen)
                        self.paint_curser(
                            painter,
                            rect,
                            view.mock_plug_values.get(face_group_name, 0.0),
                            padding=0.0,
                            width_multiply=1.0
                        )


            else:
                super(FaceGroupDelegate, self).paint(painter, option, index)

    def paint_curser(self, painter, rect, driver_value, padding=-5.0, width_multiply=1.0):

        painter.save()
        center_y = rect.center().y()

        x_value = int(rmu.remap_value(
            float(driver_value),
            self.min,
            self.max,
            self.start_point,
            self.end_point
        ))

        if x_value < self.start_point:
            x_value = self.start_point
        elif x_value > self.end_point:
            x_value = self.end_point

        handle_height = round(float(rect.height() * 0.4))
        handle_width = int(round(handle_height * 0.3333) * width_multiply)
        roundness = int(handle_width * 0.25)
        handle_height = int(handle_height)
        painter.drawRoundedRect(
            QRect(
                QPoint(
                    x_value - handle_width + padding,
                    center_y - handle_height + padding
                ),
                QPoint(
                    x_value + handle_width - padding,
                    center_y + handle_height - padding
                )
            ),
            roundness, roundness
        )

    def set_controller(self, controller):
        if self.controller:
            self.controller.start_ownership_signal.disconnect(self.disable)
            self.controller.end_ownership_signal.disconnect(self.enable)
            self.controller.start_disown_signal.disconnect(self.disable)
            self.controller.end_disown_signal.disconnect(self.enable)

        self.controller = controller
        if self.controller:
            self.controller.start_ownership_signal.connect(self.disable)
            self.controller.end_ownership_signal.connect(self.enable)
            self.controller.start_disown_signal.connect(self.disable)
            self.controller.end_disown_signal.connect(self.enable)

    def enable(self, member, owner):
        if isinstance(member, FaceTarget):
            self.disabled = False

    def disable(self, member, owner):
        if isinstance(member, FaceTarget):
            self.disabled = True

    def paint_rect(self, painter, rect):
        painter.drawRect(
            rect
        )

    def get_slot_rect(self, rect, padding=0):
        quarter_height = self.quarter_height
        center_y = rect.center().y()
        return QRect(
            QPoint(self.start_point - padding - quarter_height, center_y - quarter_height + padding),
            QPoint(self.end_point + padding + quarter_height, center_y + quarter_height - padding)
        )

    def get_outline_pen_width(self, rect):
        width = int(round(float(rect.height()) / 7))
        if width < 3:
            width = 3
        return width

    def paint_slot(self, painter, rect, padding=0):
        slot_radius = int(round(float(rect.height()) / 8))
        painter.drawRoundedRect(
            self.get_slot_rect(rect, padding=padding),
            slot_radius, slot_radius
        )


    def paint_zero(self, initial_value, painter, rect, padding=0.0):

        center_y = rect.center().y()

        x_position = rmu.remap_value(
            initial_value,
            self.min,
            self.max,
            self.start_point,
            self.end_point
        )

        height = int(round(float(self.quarter_height) * 0.75))
        width = int(round(float(self.quarter_height) * 0.5))
        slot_radius = int(round(float(width) * 0.5))


        painter.drawRoundedRect(
            QRect(
                QPoint(
                    x_position - width + padding,
                    center_y - height + padding
                ),
                QPoint(
                    x_position + width - padding,
                    center_y + height - padding
                )
            ),
            slot_radius, slot_radius
        )

    def paint_target(self, driver_value, painter, rect, padding):
        center_y = rect.center().y()

        x_position = rmu.remap_value(
            driver_value,
            self.min,
            self.max,
            self.start_point,
            self.end_point
        )

        ellipse_radius = int(round(float(self.quarter_height) * 1.5))
        painter.drawEllipse(
            QRect(
                QPoint(
                    x_position - ellipse_radius + padding,
                    center_y - ellipse_radius + padding
                ),
                QPoint(
                    x_position + ellipse_radius - padding,
                    center_y + ellipse_radius - padding
                )
            )
        )

    def paint_targets(self, target_driver_values, painter, rect, padding=0, skip_zero=False):
        for driver_value in target_driver_values:
            if not skip_zero or not round(driver_value, 2) == 0.0:
                self.paint_target(driver_value, painter, rect, padding=padding)

    def paint_hover_targets(self, painter, rect, hover_driver_value, padding=0):
        if hover_driver_value is not None:
            center_y = rect.center().y()
            ellipse_radius = int(round(float(self.quarter_height) * 1.5))
            x_position = rmu.remap_value(
                hover_driver_value,
                self.min,
                self.max,
                self.start_point,
                self.end_point
            )
            painter.drawEllipse(
                QRect(
                    QPoint(
                        x_position - ellipse_radius + padding,
                        center_y - ellipse_radius + padding
                    ),
                    QPoint(
                        x_position + ellipse_radius - padding,
                        center_y + ellipse_radius - padding
                    )
                )
            )

    def paint_selected_targets(self, driver_values, painter, rect, padding=0):
        center_y = rect.center().y()
        for driver_value in driver_values:
            x_position = rmu.remap_value(
                driver_value,
                self.min,
                self.max,
                self.start_point,
                self.end_point
            )
            ellipse_radius = int(round(float(self.quarter_height) * 1.5))
            painter.drawEllipse(
                QRect(
                    QPoint(
                        x_position - ellipse_radius + padding,
                        center_y - ellipse_radius + padding
                    ),
                      QPoint(
                          x_position + ellipse_radius - padding,
                          center_y + ellipse_radius - padding
                      )
                )
            )

    def sizeHint(self, *args):
        size = super(FaceGroupDelegate, self).sizeHint(*args)
        size.setHeight(self.item_height)
        return size
