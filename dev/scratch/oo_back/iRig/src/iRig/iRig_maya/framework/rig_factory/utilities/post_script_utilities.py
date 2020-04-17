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
                        '%s/post_scripts' % controller.buuld_directory,
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
                                controller.raise_warning('Post Script Error :  %s.py' % script_path)
                                print traceback.format_exc()
                                print e.message
                                print 'Error executing :  %s' % script_path

    else:

        log.critical('"controller" argument is None')


def run_finalize_scripts(controller, log=None):
    if controller is not None:
        container = controller.root
        if isinstance(container, obs.Container):
            log = log_tools.access(log)
            if container.finalize_scripts:
                for script_name in container.finalize_scripts:
                    script_path = '%s/%s.py' % (
                        '%s/finalize_scripts' % controller.buuld_directory,
                        script_name
                    )
                    if not os.path.exists(script_path):
                        log.critical('Finalize script not found : %s' % script_path)
                    else:
                        with open(script_path, mode='r') as f:
                            try:
                                log.info('Executing Finalize Script : %s' % script_path)
                                exec (f.read(), dict(controller=controller))
                                log.info('Executed Finalize Script : %s' % script_path)
                            except Exception, e:
                                log.critical(
                                    'run_finalize_scripts: Error executing :  %s.py' % script_path
                                )
                                controller.raise_warning('Finalize Script Error :  %s.py' % script_path)
                                print traceback.format_exc()
                                print e.message
                                print 'Error executing :  %s' % script_path

    else:

        log.critical('"controller" argument is None')

