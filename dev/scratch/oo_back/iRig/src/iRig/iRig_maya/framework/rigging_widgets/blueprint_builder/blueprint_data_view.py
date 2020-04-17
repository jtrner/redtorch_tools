import os
import subprocess
import json
import tempfile
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from blueprint_data_model import BlueprintDataModel
from rigging_widgets.blueprint_builder.blueprint_items import PartDataItem
import rig_factory.objects as obs
obs.register_classes()


class BlueprintDataView(QTableView):

    def __init__(self, *args, **kwargs):
        super(BlueprintDataView, self).__init__(*args, **kwargs)

        self.setIconSize(QSize(30, 30))
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(False)
        self.horizontalHeader().setStretchLastSection(True)

        try:
            self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        except StandardError:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.god_mode = False

    def set_god_mode(self, value):
        self.god_mode = value
        model = self.model()
        if model:
            self.load_items(model.parts_data)

    def load_items(self, parts_data):
        model_data = []
        keys = []
        for part_data in parts_data:
            part_data.pop('name', None)
            part_data.pop('pretty_name', None)
            object_type = part_data['klass']
            part_class = obs.classes[object_type]
            if not self.god_mode:
                model_data.append(['klass', part_data['klass']])
                PartDataItem(
                    'klass',
                    data=object_type,
                )
            for key in part_data:
                if key not in keys:
                    if self.god_mode or key in part_class.default_settings :
                        keys.append(key)
                        model_data.append([key, part_data[key]])
        model = BlueprintDataModel(model_data)
        model.parts_data = parts_data
        self.setModel(model)

    def mouseDoubleClickEvent(self, event):
        model = self.model()
        index = self.indexAt(event.pos())
        item_set = model.get_item(index)
        item_name, item_data = item_set
        if type(item_data) in (list, dict):
            data = edit_data_in_notepad(item_data)
            item_set[1] = data
        else:
            self.edit(index)


def edit_data_in_notepad(data):
    script_path = '{0}/BLUEPRINT_TEMP_VAR_EDIT.json'.format(tempfile.gettempdir())
    with open(script_path, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    open_in_notepad(script_path)
    with open(script_path, mode='r') as f:
        return json.load(f)


def open_in_notepad(path):
    print 'Opening: %s' % path
    if os.path.exists('C:/Program Files (x86)/Notepad++/notepad++.exe'):
        prc = subprocess.Popen(
            '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % path)
        prc.wait()
    elif os.path.exists('C:/Program Files/Notepad++/notepad++.exe'):
        prc = subprocess.Popen(
            '"C:/Program Files/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % path)
        prc.wait()
    else:
        raise Exception('Failed to find the application "Notepad++"')

