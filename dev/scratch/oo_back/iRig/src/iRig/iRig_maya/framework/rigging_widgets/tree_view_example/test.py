import sys
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from model import TreemModel
from item import Item
from view import MyView

data = [
  {
    "name": "Parent 1",
    "children": [
      {
        "name": "Child 1",
        "children": [
          {
            "name": "Grandchild 1",
          },
          {
            "name": "Grandchild 2",
          }
        ]
      },
      {
        "name": "Child 2",
      }
    ]
  },
  {
    "name": "Parent 2",
  }
]


def build_items(data_list, parent=None):
    for data_dict in data_list:
        new_item = Item(
            name=data_dict['name'],
            parent=parent
        )
        if 'children' in data_dict:
            build_items(
                data_dict['children'], 
                parent=new_item
            )


def run():
    app = QApplication(sys.argv)
    tree_view = MyView()
    root = Item(name='root')
    build_items(data, parent=root)
    tree_view.setModel(TreemModel(root))
    tree_view.show()
    tree_view.raise_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()