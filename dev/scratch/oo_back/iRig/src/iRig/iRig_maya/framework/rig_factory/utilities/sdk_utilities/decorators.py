
def flatten_args(func):
    def flatten(*args, **kwargs):
        return func(*flatten_items(*args), **kwargs)
    return flatten


def flatten_items(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            nodes.extend(flatten_items(*arg))
        else:
            nodes.append(arg)
    return nodes
