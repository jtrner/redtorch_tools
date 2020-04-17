import itertools

side_prefixes = dict(
    left='L',
    right='R',
    center='C'
)


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


index_dictionary = create_alpha_dictionary()


def create_name_string(*args, **kwargs):
    name = kwargs.get('root_name', None)
    if name:
        if not isinstance(name, basestring):
            raise Exception('Keyword argument "root_name" should be string.')
        side = kwargs.get('side', None)
        index = kwargs.get('index', None)
        if side in side_prefixes:
            name = '%s_%s' % (side_prefixes[side], name)
        else:
            raise NameError('Invalid Side: %s' % side)
        if index is not None:
            if not isinstance(index, int):
                raise Exception('Keyword argument "index" should be an int.')
            name = '%s_%s' % (name, index_dictionary[index])
        return name


