

class Item(object):

    def __init__(self, parent=None, name=None):
        super(Item, self).__init__()
        self.name = name
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def __repr__(self):
        return self.name
