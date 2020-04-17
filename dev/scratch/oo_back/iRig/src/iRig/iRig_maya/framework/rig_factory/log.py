import logging
from os.path import expanduser

logger = logging.getLogger('RigFactoryLog')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh = logging.handlers.RotatingFileHandler(
#    '%s/shot_controller.log' % expanduser("~"),
#    maxBytes=10240,
#    backupCount=5
#)
#fh.setFormatter(formatter)
#logger.addHandler(fh)
#logger.propagate = False