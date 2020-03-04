import os

# get a list of all files in the same folder as this file exists
# we can then use from util import * and it will import all the modules
currentDirPath = __path__[0]
fileList = os.listdir(currentDirPath)
__all__ = [module.replace(".py", "") for module in fileList if module.endswith(".py") and module != "__init__.py"]
