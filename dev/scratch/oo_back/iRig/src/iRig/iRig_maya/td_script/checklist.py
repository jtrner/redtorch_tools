# import code
from maya import cmds
from functools import partial
import json
import os

defaultFilePath = 'G:/Rigging/Alex/checklist_tool.json'

def disable_cb(name, value):
    cmds.text(name, e=True, en=value)


def hideDescriptions(descriptions, cbValue):
    if not cbValue:
        for name in descriptions:
            cmds.text(name, e=True, l='')
    else:
        for item, name in zip(myDict['items'], descriptions):
            cmds.text(name, e=True, l=item['Description'])


def open_window():
    """
    Opens the Checklist window. The window gets garbage collected when closed in any fashion.
    :return: <bool> True for success.
    """
    with open(defaultFilePath, 'r') as file_object:
        myDict = json.load(file_object)
        for a in file_object:
            myDict = a
    cmds.window(title='Checklist')
    cmds.columnLayout()
    cmds.rowColumnLayout(nc=2)
    cmds.setParent('..')
    cmds.rowColumnLayout(nc=2)
    descriptions = []

    for i, item in enumerate(myDict['items']):
        cb_name = 'description' + str(i)
        cmds.checkBox(v=item['status'], label=item['Name'], cc=partial(disable_cb, cb_name))
        cmds.text(cb_name, l=item['Description'], en=item['status'], al='left')
        descriptions.append(cb_name)
    cmds.setParent('..')
    cmds.columnLayout()
    cmds.checkBox(l='Descriptions Visible', cc=partial(hideDescriptions, descriptions), v=True)
    cmds.showWindow()
    return True