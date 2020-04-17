"""Scales the face bake anim curves for the face joint control setup."""

# import standard modules
import re

# import maya modules
from maya import cmds

# global variables
find_num = lambda x: re.sub('[^\d.,]', '', x)

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev", "Sean Prosch"]
__license__ = "ICON LISENCE"
__version__ = "1.0.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def do_it():
    """
    Sets the scale by specified scale factor.
    :return: <bool> True for success. <bool> False for failure.
    """
    answer = False
    while not answer:
        result = cmds.promptDialog(
            title='Scale Anim Curves',
            message='<float>/<int> scale_factor, Enter Scale Value:                    ',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
        if result == 'OK':
            text = cmds.promptDialog(query=True, text=True)
            text = find_num(text)
            if not text:
                cmds.confirmDialog(
                    title="Error", icon='warning',
                    message="[Invalid Value] :: {}\nPlease enter a float or integer value. ".format(text))
            else:
                cmds.confirmDialog(title="Updated Curves Scale", message="Scale factor: " + text)
                answer = True
                return scale_face_curves(float(text))
        if result == 'Cancel':
            answer = True
    return False


def scale_face_curves(new_scale=1.00):
    """
    Scale the face curves by specified scale factor.
    :param new_scale: <float> scale factor.
    :return: <bool> True for success, <bool> False for failure.
    """
    if not new_scale:
        return False
    if not isinstance(new_scale, float):
        return False
    trans_anim_curves = cmds.ls('*trans*Anm')
    for anim_curve in trans_anim_curves:
        vals = cmds.keyframe(anim_curve, q=True, valueChange=True)
        ind = 0
        for val in vals:
            cmds.keyframe(anim_curve, option='over', index=(ind, ind), absolute=1, valueChange=val * new_scale)
            ind = ind + 1
    return True
