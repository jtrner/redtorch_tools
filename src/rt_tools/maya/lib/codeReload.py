import os

mainModulePath = __file__
mainModuleName = __file__.split('\\')[-1]


def reload_(path=mainModulePath, moduleName=mainModuleName):
    """
    remarks 	reload a given module and its sub modules
    @path 		string	Path to the given module
    @moduleName string	name of the parent module
    """
    # Loop over the files and directories of a given path
    for root, dirs, fileNames in os.walk(path):

        # Ignore wip folder
        if "wip" in root:
            continue

        # parse all the fileNames of given path and reload python modules
        for fileName in fileNames:

            # Ignore files that are not python
            if not fileName.endswith(".py"):
                continue

            # Get the module name
            # if the file is __init__ the name of the module is the name of the directory
            if fileName == "__init__.py":
                subModuleName = moduleName
            else:
                subModuleName = moduleName + "." + fileName.split(".")[0]

            log("reload : %s" % subModuleName)

            # Try to reload the module
            # If there is a syntax error or the module can't be loaded we print the error message

            try:
                module = __import__(subModuleName, globals(), locals(), ["*"], -1)
                reload(module)

            except ImportError, e:
                for arg in e.args:
                    log(arg, c.siError)

            except Exception, e:
                for arg in e.args:
                    log(arg, c.siError)

        # Now reload sub modules
        for dirName in dirs:
            reload_(os.path.join(path, dirName), ".".join([moduleName, dirName]))
        break
