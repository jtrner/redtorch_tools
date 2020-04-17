import sys
import inspect

def get_dependancies(module):
    dependancies = []
    for key in module.__dict__:
        member = module.__dict__[key]
        if inspect.isclass(member):
            klass = getattr(module, member.__name__)
            m = sys.modules[klass.__module__]
            if module != m:
                dependancies.append(m)
        if isinstance(member, str) and member in sys.modules:
            m = sys.modules[member]
            if module != m:
                dependancies.append(m)
    return dependancies


def find_dependancies(module):
    dependancies = get_dependancies(module)
    for x in dependancies:
        dependancies.extend(find_dependancies(x))
    dependancies = get_dependancies(module)
    return dependancies
