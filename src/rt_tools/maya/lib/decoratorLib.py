"""
decoratorLib.py

Author: Ehsan Hassani Moghaddam

"""

# python modules
import json
from datetime import datetime

# Maya modules
import maya.cmds as mc
import maya.mel as mm


def timeIt(obj):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = obj(*args, **kwargs)
        time_elapsed = datetime.now() - start_time
        print('"{}" took {}'.format(obj.__name__, str(time_elapsed).split('.')[0]))
        return result

    return wrapper


def undoChunk(obj):
    """
    undochunk wrapper
    """

    def wrapper(*args, **kwargs):
        mc.undoInfo(st=1)
        mc.undoInfo(openChunk=1)
        try:
            return obj(*args, **kwargs)
        except Exception:
            raise
        finally:
            mc.undoInfo(closeChunk=1)

    return wrapper


def viewPort(obj):
    """
    viewPort wrapper
    """

    def wrapper(*args, **kwargs):
        disableViewPorts()
        try:
            return obj(*args, **kwargs)
        except Exception:
            raise
        finally:
            enableViewPorts()

    return wrapper


def disableViewPorts():
    """
    Isolate all viewports
    """
    mm.eval("paneLayout -e -manage false $gMainPane")


def enableViewPorts():
    """
    Un-Isolate all viewports
    """
    mm.eval("paneLayout -e -manage true $gMainPane")


def repeatable_cmd(function):
    """
    special repeat which works with exec("YOUR_PYTHON_COMMAND")
    """
    def wrapper(cmd_string):
        # print executed code
        print('-' * 80)
        print(cmd_string)
        print('-' * 80)

        # make it repeatable for later
        cmd_string_flatten = json_dumps(cmd_string)
        if cmd_string_flatten is not None:
            try:
                # make commanad repeatable
                commandToRepeat = 'python({})'.format(cmd_string_flatten)
                mc.repeatLast(ac=commandToRepeat, acl=function.__name__)

                # run the command
                exec(cmd_string, globals(), globals())

            except Exception as e:
                raise e

        # if given cmd is a callable function instead of a string
        else:
            cmd_string()

    return wrapper


def json_dumps(cmd_string):
    try:
        return json.dumps(cmd_string)
    except:
        return None
