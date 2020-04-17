import json
from functools import wraps


@wraps
def serializable_arguments(func):
    def temp_func(*args, **kwargs):
        json.dumps((args, kwargs))
        return func(*args, **kwargs)
    return temp_func


class JsonDict(dict):

    @serializable_arguments
    def __init__(self, *args, **kwargs):
        json.dumps(kwargs)
        super(JsonDict, self).__init__(*args, **kwargs)

    @serializable_arguments
    def __setitem__(self, key, value):
        json.dumps(key)
        json.dumps(value)
        return super(JsonDict, self).__setitem__(key, value)

    @serializable_arguments
    def update(self, *args, **kwargs):
        json.dumps((args, kwargs))
        json.dumps(kwargs)
        return super(JsonDict, self).update(*args, **kwargs)


