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
        # make it repeatable for later
        try:

            # create a string from given command to make it repeatable
            cmd_string_flatten = json.dumps(cmd_string)
            commandToRepeat = 'python({})'.format(cmd_string_flatten)

            try:
                # make commanad repeatable
                mc.repeatLast(ac=commandToRepeat, acl=function.__name__)

                # run the command
                exec(cmd_string, globals(), globals())

            except Exception as e:
                raise e

        except:
            cmd_string()

        # execute it
        return function(cmd_string)

    return wrapper
