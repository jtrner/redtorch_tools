from os.path import expanduser
import os
import rig_factory.objects as obs
from rig_factory.controllers.rig_controller import RigController

import subprocess
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

obs.register_classes()

def launch_action_in_notepad(file_name):
    prc = subprocess.Popen(
        '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % file_name)
    prc.wait()


def new_post_script():
    input_text, success = QInputDialog.getText(None, 'New Post Script', 'Enter a name for the new post script')
    if success:
        script_path = '%s/%s.py' % (expanduser("~"), input_text)
        if not os.path.exists(script_path):
            with open(script_path, mode='w') as f:
                f.write('# use the variable "controller" to refer to the current RigController')
        launch_action_in_notepad(script_path)


def run_post_scripts(container):
    for script_name in container.post_scripts:
        script_path = '%s/%s.py' % (expanduser("~"), script_name)
        if not os.path.exists(script_path):
            raise Exception('post script not found : %s' % script_path)
        with open(script_path, mode='r') as f:
            exec(f.read(), dict(controller=container.controller))


controller = RigController.get_controller()
controller.post_script_signal.connect(run_post_scripts)
controller.root = controller.create_object(
    obs.ContainerGuide,
    root_name='body'
)
controller.root.post_scripts = ['do_the_things']
controller.toggle_state()




