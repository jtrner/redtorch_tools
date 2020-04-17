import os
import re
from typing import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


__all__ = 'AlembicVersionsModel',


class AlembicVersionsModel(QAbstractItemModel):
    """
    Models versions of alembic data. Displays data differently
    depending on whether it is the newest version of that asset.
    """

    # Private Constant
    _re_file_version_number = re.compile(r'\d+(?=\.abc$)')

    # Private Dynamic
    _data = None
    _rows = None

    # Public Dynamic
    controller = None

    def __init__(self, *args, **kwargs):
        super(AlembicVersionsModel, self).__init__(*args, **kwargs)
        self._data = []
        self._rows = 0

    @property
    def DisplayIndex(self):
        return 0

    @property
    def FontIndex(self):
        return 1

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, self._data[row])

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._rows

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][self.DisplayIndex]
        if role == Qt.FontRole:
            return self._data[index.row()][self.FontIndex]

    @classmethod
    def get_version_number(cls, file_path):
        # type: (AnyStr) -> Union[int, None]
        """
        Returns the version number from a given alembic file path.
        Returns `None` if no number could be extracted.
        :param file_path:
            File path of the target alembic.
        :return:
            Integer representing the file names version.
            Or `None` if no file version could be extracted.
        """
        search = cls._re_file_version_number.search(file_path)
        return search and int(search.group(0)) or None

    def get_all_versions(self, file_path):
        # type: (AnyStr) -> list
        """
        Returns all versions of the given alembic asset path.
        :param file_path:
            File path of the target alembic.
        :return:
            All versions of the given alembic path.
        """
        directory, file_name = os.path.split(file_path)
        asset_name = self._re_file_version_number.sub('', file_name)
        return [
            os.path.join(directory, _file_name)
            for _file_name in os.listdir(directory)
            if self._re_file_version_number.sub('', _file_name) == asset_name
        ]

    def is_newest_version(self, file_path):
        # type: (AnyStr) -> bool
        """
        Returns whether the given alembic file path is the newest
        version of it's asset.
        :param file_path:
            File path of the target alembic.
        :return:
            Whether the given alembic file path is the newest
            version of it's asset.
        """
        return (
            self.get_version_number(file_path)
            == len(self.get_all_versions(file_path))
        )

    def refresh_data(self):
        """
        Rebuilds the model's data, and reloads the model/view.
        """

        self.beginResetModel()

        geometry_paths = (
            self.controller
            and self.controller.get_root()
            and self.controller.get_root().geometry_paths
            or []
        )

        self._data = []
        for file_path in geometry_paths:

            _, file_name = os.path.split(file_path)
            name, _ = os.path.splitext(file_name)

            if self.is_newest_version(file_path):
                self._data.append((
                    name,
                    QFont('', pointSize=11, italic=False)
                ))

            else:
                self._data.append((
                    '*' + name + '*',
                    QFont('', pointSize=11, italic=True)
                ))

        self._rows = len(self._data)
        self.endResetModel()
