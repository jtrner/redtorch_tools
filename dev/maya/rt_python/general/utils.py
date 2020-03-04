from datetime import datetime

import maya.cmds as mc
import maya.mel as mm


def timeIt(obj):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = obj(*args, **kwargs)
        time_elapsed = datetime.now() - start_time
        # funcName = inspect.stack()[0][3]
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
