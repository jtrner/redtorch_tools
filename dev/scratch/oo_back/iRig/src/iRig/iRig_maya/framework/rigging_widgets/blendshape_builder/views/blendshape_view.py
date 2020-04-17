import functools
import qtpy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.blendshape_builder.models.blendshape_model import BlendshapeModel
from rig_factory.controllers.blendshape_controller import BlendshapeController
import rigging_widgets.blendshape_builder.environment as env
from rig_factory.objects.blendshape_objects.blendshape import BlendshapeGroup


class BlendshapeView(QTreeView):

    items_selected_signal = Signal(list)
    create_part_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(BlendshapeView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.setModel(BlendshapeModel())
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.header().setStretchLastSection(True)
        if qtpy.__binding_version__.startswith('2.'):
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            self.header().setResizeMode(QHeaderView.ResizeToContents)

    def set_controller(self, controller):
        self.controller = controller
        model = self.model()
        if model:
            model.set_controller(self.controller)

    def setModel(self, model):
        super(BlendshapeView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def keyPressEvent(self, event):

        model = self.model()
        if model:
            key_object = event.key()
            if key_object == Qt.Key_Delete:
                self.delete_items([i for i in self.selectedIndexes() if i.column() == 0])
        super(BlendshapeView, self).keyPressEvent(event)


    def delete_items(self, indices):
        model = self.model()
        if model:
            items = []
            for index in indices:
                item = model.get_item(index)



    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                if event.button() == Qt.RightButton:
                    index = self.indexAt(event.pos())
                    node = model.get_item(index)
                    menu = QMenu(self)

                    if isinstance(node, BlendshapeGroup):
                        menu.addAction(
                            'Disconnect',
                            functools.partial(self.controller.disconnnect_targets, node)
                        )
                        menu.addAction(
                            'Connect',
                            functools.partial(self.controller.connect_targets, node)
                        )
                        menu.exec_(self.mapToGlobal(event.pos()))

            if event.button() == Qt.LeftButton:
                super(BlendshapeView, self).mousePressEvent(event)

    def select_mesh_positioons(self, handle):
        mesh = self.controller.root.geometry[handle.mesh_name]
        self.controller.select([mesh.get_vertex(x) for x in handle.vertex_indices])

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        filtered_items = []
        modifiers = QApplication.keyboardModifiers()

        self.items_selected_signal.emit(list(set(filtered_items)))


if __name__ == '__main__':
    import os
    import sys
    import maya.cmds as mc

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    app = QApplication(sys.argv)
    controller = BlendshapeController.get_controller(
        standalone=True
    )


    controller = BlendshapeController.get_controller(standalone=True)
    import maya.cmds as mc

    mc.loadPlugin('AbcImport')
    mc.loadPlugin('AbcExport')

    mc.AbcImport(
        r'D:\rigging_library\rig_builds\ambassador\ambassador.abc',
        mode='import'
    )

    base_mesh = controller.initialize_node('MOB_headShapeDeformed')

    blendshape = controller.create_blendshape(
        root_name='face'
    )
    blendshape.add_geometry(base_mesh)
    blendshape.create_blendshape_group(
        controller.initialize_node('mchr_ambassador_headShapeDeformed'),
        root_name='smile'
    )
    blendshape.create_blendshape_group(
        controller.initialize_node('shape_1ShapeDeformed'),
        root_name='frown'
    )
    blendshape.create_blendshape_group(
        controller.initialize_node('shape_2ShapeDeformed'),
        root_name='pucker'
    )
    blendshape.create_blendshape_group(
        controller.initialize_node('shape_3ShapeDeformed'),
        root_name='pout'
    )
    blendshape.create_blendshape_group(
        root_name='butts'
    )
    controller.set_root(blendshape)

    app.setStyleSheet(style_sheet)
    body_widget = BlendshapeView()
    body_widget.set_controller(controller)
    body_widget.show()
    body_widget.raise_()
    sys.exit(app.exec_())