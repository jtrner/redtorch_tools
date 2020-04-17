import os
import traceback
import rig_factory.objects as obs
import log_tools


def run_post_scripts(controller, log=None):
    if controller is not None:
        container = controller.root
        if isinstance(container, obs.Container):
            log = log_tools.access(log)
            if container.post_scripts:
                for script_name in container.post_scripts:
                    script_path = '%s/%s.py' % (
                        controller.workflow.get_post_scripts_directory(),
                        script_name
                    )
                    if not os.path.exists(script_path):
                        log.critical('Post script not found : %s' % script_path)
                    else:
                        with open(script_path, mode='r') as f:
                            try:
                                log.info('Executing Post Script : %s' % script_path)
                                exec (f.read(), dict(controller=controller))
                                log.info('Executed Post Script : %s' % script_path)
                            except Exception, e:
                                log.critical(
                                    'run_post_scripts: Error executing :  %s.py' % script_path
                                )
                                print traceback.format_exc()
                                print e.message
    else:

        log.critical('"controller" argument is None')
