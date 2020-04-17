
class PartDataItem(object):

    def __init__(self, name, data=None, parent=None):
        super(PartDataItem, self).__init__()
        if parent is not None and not isinstance(parent, PartDataItem):
            raise Exception('Invalud parent type "%s"' % type(parent))
        self.data = data
        self.name = name
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def __repr__(self):
        return '%s(name="%s")' % (self.__class__.__name__, self.name)


class PartBlueprintItem(PartDataItem):

    def __init__(self, *args, **kwargs):
        super(PartBlueprintItem, self).__init__(*args, **kwargs)


class PartGroupBlueprintItem(PartDataItem):

    def __init__(self, *args, **kwargs):
        super(PartGroupBlueprintItem, self).__init__(*args, **kwargs)


class ContainerBlueprintItem(PartDataItem):

    def __init__(self, *args, **kwargs):
        super(ContainerBlueprintItem, self).__init__(*args, **kwargs)

