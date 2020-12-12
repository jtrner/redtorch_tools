import os
import json
import shutil
import errno
from collections import OrderedDict

import maya.cmds as mc


def loadJson(path, ordered=True, error=True, asString=False):
    """
    imports json from path as dict or orderedDict

    usage:
        path = '/home/Documents/skin.json'
        test = fileLib.loadJson(path)

    :param path: path to json file
    :type path: string
    :param ordered: if True will return the json as orderedDict
    :type ordered: bool
    :param error: if True, errors on missing file else displays warning message
    :type error: bool
    :return: dict or orderedDct converted from given json file
    :type: dict or orderedDct
    """
    if not os.path.lexists(path):
        if error:
            mc.error('{!r} does not exist!'.format(str(path)))
        else:
            mc.warning('{!r} does not exist!'.format(str(path)))
            return

    with open(path, 'r') as f:
        if ordered:
            data = json.load(f, object_pairs_hook=OrderedDict)
        else:
            data = json.load(f)

    if asString:
        return json.dumps(data)

    return data


def saveJson(path, data):
    """
    export dict to path as json
    usage:
        data = {'l_ankle': {"hi": "hooy"}}
        path='/home/Documents/skin.json'
        fileLib.saveJson(path, data)
    """
    if not os.path.lexists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(data, f, sort_keys=False, indent=4)


def append_to_json(data,path, key = ""):

    with open(path, 'ab+') as f:
        f.seek(0, 2)  # Go to the end of file
        if f.tell() == 0:  # Check if file is empty
            f.write(json.dumps(data, indent=4).encode())  # If empty, write an array

    if checkJsonExists(path, key):
        a_file = open(path, "r")
        json_object = json.load(a_file)
        a_file.close()
        json_object[key] = data
        a_file = open(path, "w")
        json.dump(json_object[key], a_file, indent = 4)
        a_file.close()

    # else:
    #     with open(path, 'a') as f:
    #         str = json.dumps(data, indent = 4).replace('{', ',', 1)
    #         f.seek(-2, 2)
    #         f.write(str)
        # with open(path, 'a') as f:
        #     f.seek(0, 2)  # Go to the end of file
        #     if f.tell() == 0:  # Check if file is empty
        #         f.write(json.dumps(data, indent=4).encode())  # If empty, write an array
        #     else:
        #         f.seek(-1, 2)
        #         f.write(' , '.encode())  # Write the separator
        #         f.write(json.dumps(data , indent = 4).encode())  # Dump the dictionary

def checkJsonExists(path, key):
    a_file = open(path, "r")
    data = json.load(a_file)
    if not key in data.values()[:]:
        print('ueeeeeee')
        return True



def copy(src, dest, ignore=None):
    # ignore = shutil.ignore_patterns('*.py', '*.sh', 'specificfile.file')
    try:
        shutil.copytree(src, dest, ignore=ignore)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def appendToJson(path, data, ordered=True):

    old_data = loadJson(path, ordered=ordered, error=False)
    print old_data
    if old_data:
        for k, v in old_data.items():
            # overwrite older data if keys are the same
            if k in data:
                continue
            data[k] = v

    saveJson(path, data)

def dictToStr(data):
    data_as_str = ''
    for k, v in data.items():
        data_as_str += '{}: {}\n'.format(k, v)
    return data_as_str
