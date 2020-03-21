"""
name: strLib.py

Author: Ehsan Hassani Moghaddam

History:

04/29/16 (ehassani)     first release!

Usage:
path = os.path.join("E:", os.path.sep, "all_works", "redtorch_tools", "dev", "maya")
if path not in sys.path:
    sys.path.insert(0, path)
import python.lib.strLib as strLib
reload(strLib)
strLib.fixDuplicateNames()

"""
import re

import maya.cmds as mc


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def fixDuplicateNames():
    all = mc.ls()
    non_unique = [x for x in all if '|' in x]
    renamed = []
    for x in non_unique:
        if not mc.objExists(x):
            continue
        unique_name = getUniqueName(x.split('|')[-1])
        mc.rename(x, unique_name)
        renamed.append([x, unique_name])
    if renamed:
        print "Renamed duplicate names:"
        for x in renamed:
            print '{}\t--->\t{}'.format(x[0], x[1])


def getName(name="", ignoreConvention=False):
    """
    convert full path to name of object and merges the suffix
    @return    string    shorten and merged name
    """
    if ignoreConvention:
        return name
    return mergeSuffix(getShortName(name))


def hasEndNumber(name=""):
    if name[-1].isdigit():
        return True


def isUniqueName(name=""):
    if not mc.objExists(name):
        return True


def removeEndNumbers(name=""):
    return re.split('(\d+)$', name)[0]


def removeFromEnd(name, endString):
    """
    removes a endString from name if name ends with endString
    """
    if name.endswith(endString):
        return name[:-len(endString)]
    return name


def getUniqueName(name=""):
    """
    generates a unique name for the given object's name
    by checking if it exists in the scene
    """
    while not isUniqueName(name):
        name = incrementEndNumber(name)
    return name


def incrementEndNumber(name="", hasSuffix=False):
    """
    if name ends with digit increment that digit
    else add "1" to the end of name
    hasSuffix: if True, will ignore the suffix and applies number to descriptor.
               ie: C_head_JNT -> C_head1_JNT
               if False, adds number in the end. ie: C_head_JNT -> C_head_JNT1
    """
    if hasSuffix:
        suffix = getSuffix(name)
        name = removeSuffix(name)

    if hasEndNumber(name):
        name_no_number = removeEndNumbers(name)
        num = getEndNumber(name) + 1
        name = name_no_number + str(num)
    else:
        name = name + "1"

    if hasSuffix:
        name = name + "_" + suffix

    return name


def getEndNumber(name=""):
    """
    if name ends with digit returns it as int
    else returns "0"
    """
    name_no_number = removeEndNumbers(name)
    num = name.replace(name_no_number, "")
    return int(num)


def replaceDescriptor(name="", descriptor=""):
    old_descriptor = getDescriptor(name)
    return name.replace(old_descriptor, descriptor)


def getDescriptor(name=""):
    """
    @return    string    
                        get descriptor of the name   eg: "L_thumb_CTL" -> "thumb"
    """
    if "|" in name:
        name = name.split("|")[-1]
    if hasDescriptor(name):
        return name[2:].rsplit("_", 1)[0]


def hasDescriptor(name=""):
    if "|" in name:
        name = name.split("|")[-1]
    if "_" not in name:
        return False
    parts = name.split("_")
    if len(parts[1]):
        return True


def getOtherSide(string=""):
    """
    get other side prefix based on given side
    eg:    get_other_side(string="L")  #result: "R"
    @param    
                string    string
    @return    
                string    other side prefix
    """
    if string == "L":
        return "R"
    elif string == "R":
        return "L"
    elif string == "C":
        return "C"
    elif string == "l":
        return "r"
    elif string == "r":
        return "l"
    elif string == "c":
        return "c"
    else:
        raise Exception('"{}" is a wrong side. Right values are "L" or "R"'.format(string))


def camelCase(string=""):
    parts = string.split("_")
    result = ""
    for part in parts:
        result += part.title()
    return makeFirstLower(result)


def makeFirstLower(string=""):
    return string[0].lower() + string[1:]


def pathValidate(path=""):
    pass


def getShortName(name=""):
    return name.split("|")[-1]


def printBigTitle(message="no message", separator="=", mode="info", repeatation=100):
    print "\n"
    print lineOf(separator, repeatation)
    print message
    print lineOf(separator, repeatation)  # , "\n"


def lineOf(string="-", number_of_repeatation=100):
    return string * number_of_repeatation


def getNumbers(string=""):
    return [int(s) for s in re.findall(r'\b\d+\b', string)]


def hasPrefix(name=""):
    if "_" not in name:
        return False
    prefix = name.split("_")[0]
    if not (len(prefix) == 1 and prefix.isupper()):
        return False
    return True


def getPrefix(name=""):
    if hasPrefix(name):
        return name.split("_")[0]


def hasSuffix(name=""):
    if "_" not in name:
        return False
    suffix = name.split("_")[-1]
    if not (len(suffix) == 3 and suffix.isupper()):
        return False
    return True


def getSuffix(name=""):
    if hasSuffix(name):
        return name.split("_")[-1]


def removeSuffix(name=""):
    if hasSuffix(name):
        return "_".join(name.split("_")[:-1])
    return name


def mergeSuffix(name=""):
    name = getShortName(name)  # use name instead of full path
    if name.endswith("Shape"):
        name = name.split("Shape")[0]
    return removeSuffix(name) + (getSuffix(name).title())


def fullNameToName(string=""):
    """
    converts a full path name to the object name
         eg: "|root|group|obj" -> "obj"   
    @return     string     name of the object 
    """
    if "|" not in string:
        return string
    return string.split("|")[-1]


def addSuffix(nodes, suffix):
    """
    strLib.addSuffix(mc.ls(sl=True), "JNT")
    """
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        mc.rename(node, node + '_' + suffix.upper())


def rename(nodes, prefix='L', description='box', number=False, padding=4, startNumber=1, suffix='GEO'):
    """
    import python.lib.strLib as strLib
    reload(strLib)
    strLib.rename(mc.ls(sl=1), prefix='C', description='box',
                  number=True, padding=4, startNumber=1, suffix='GEO')
    :param nodes:
    :param prefix:
    :param description:
    :param number:
    :param padding:
    :param startNumber:
    :param suffix:
    :return:
    """
    existingNames = []
    for i, n in enumerate(nodes):
        num = str(startNumber + i).zfill(padding)
        newName = '{}_{}_{}'.format(prefix, description, suffix)
        if number:
            newName = '{}_{}_{}_{}'.format(prefix, description, num, suffix)

        while mc.objExists(newName):
            i += 1
            num = str(startNumber + i).zfill(padding)
            newName = '{}_{}_{}_{}'.format(prefix, description, num, suffix)
            existingNames.append(newName)
            continue

        mc.rename(n, newName)
    if existingNames:
        mc.warning('Rename faild on some nodes as generated name already existed in the scene!')