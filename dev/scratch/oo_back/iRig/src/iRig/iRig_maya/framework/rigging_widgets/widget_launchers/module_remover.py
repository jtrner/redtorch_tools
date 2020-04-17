import sys
import copy


def remove_modules():
    removeList = []
    sys_copy = copy.copy(sys.modules)
    for modKey, mod in sys_copy.iteritems():
        if sys.modules[modKey]:
            if hasattr(mod, '__file__'):
                if 'rigging_framework' in sys.modules[modKey].__file__:
                    removeList.append(modKey)
    for mod in removeList:
        sys.modules.pop(mod)

