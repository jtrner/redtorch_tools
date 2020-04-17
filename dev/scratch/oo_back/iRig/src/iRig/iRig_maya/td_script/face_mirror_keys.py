# define standard imports
from functools import partial

# define PySide/ PyQt imports
from QtCompat import QtCore, QtWidgets

# define maya imports
import shiboken2
from maya import OpenMayaUI
from maya import cmds

# define custom imports
from rig_tools.utils import misc as rig_misc
from rig_tools import RIG_LOG

# initialize legacy rigging tools
rig_misc.legacy_load_g_rigging()
import InterfaceTools as int_t
import FaceTools as face_t


def do_it():
    """
    Mirrors the anim keys of the Watson face rig.
    :return: <bool> True for success. <bool> False for failure.
    """
    window_name = 'FaceTool'

    # get the current auto-keyframe state
    auto_key_state = cmds.autoKeyframe(state=1, q=1)

    # enable the autokey to True
    cmds.autoKeyframe(state=1)

    # define the button window
    button_dict = {
        '9 Make Half': {'Command':'import FaceTools as face_t\nface_t.MakeHalf()',
                        'Color':[.5, .5, .5],
                        'Help':'Reduce all Controls to Half'},
        '8 Flip Pose': {'Command':'import FaceTools as face_t\nface_t.Flip()',
                        'Color':[.5, .6, .6],
                        'Help':'Flip Pose'},
        '1 Split Left Hard': {'Command':'import FaceTools as face_t\nface_t.S00(Side = "L_")',
                              'Color':[.4, .5, .4],
                              'Help':'Hard Split Left, Zero out the Right with NO blend'},
        '7 Mirror': {'Command':'import FaceTools as face_t\nface_t.MakeMirror()',
                     'Color':[.6, .5, .6],
                     'Help':'Make Pose Mirror'},
        '6 Split Right Soft': {'Command':'import FaceTools as face_t\nface_t.S02(Side = "R_")',
                               'Color':[.7, .6, .6],
                               'Help':'Soft Split Right, Zero out the Left with a blend'},
        '4 Split Right': {'Command':'import FaceTools as face_t\nface_t.S01(Side = "R_")',
                          'Color':[.6, .5, .5],
                          'Help':'Split Right, Zero out the Left with a quick blend'},
        '3 Split Left': {'Command':'import FaceTools as face_t\nface_t.S01(Side = "L_")',
                         'Color':[.5, .6, .5],
                         'Help':'Split Left, Zero out the Right with a quick blend'},
        '2 Split Right Hard': {'Command':'import FaceTools as face_t\nface_t.S00(Side = "R_")',
                               'Color':[.5, .4, .4],
                               'Help':'Soft Split Right, Zero out the Left with NO blend'},
        '5 Split Left Soft': {'Command':'import FaceTools as face_t\nface_t.S02(Side = "L_")',
                              'Color':[.6, .7, .6],
                              'Help':'Soft Split Left, Zero out the Right with a blend'}
    }

    # call the button window
    int_t.ButtonWindow(ID=window_name,
                       Title='Face Pose',
                       Columns=2,
                       ButtonWidth=100,
                       ButtonHight=50,
                       WindowColor=[.2, .2, .2], Dict=button_dict)

    def close_event(win):
        """
        Operate the closeEvent to reset the autoKeyframe state.
        :param win: <QtCore.QWidget> this window name.
        :return: <True> for success.
        """
        RIG_LOG.info("[Auto Key] :: Set previous autoKeyframe setting of {}.".format(auto_key_state))
        cmds.autoKeyframe(state=auto_key_state)
        win.deleteLater()
        win.destroy()
        return True

    # install the close event call
    face_win_ptr = OpenMayaUI.MQtUtil.findWindow(window_name + 'Win')
    if face_win_ptr:
        face_window = shiboken2.wrapInstance(long(face_win_ptr), QtWidgets.QMainWindow)
        face_window.connect(QtCore.SIGNAL('destroyed()'), partial(close_event, face_window))
    return True


if __name__ == "__main__":
    do_it()
