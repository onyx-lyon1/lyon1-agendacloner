import copy


class Dir:
    def __init__(self, name="", children=None, identifier=-1, opened=False):
        self.children = []
        self.children = children
        self.name = name
        self.identifier = identifier
        self.opened = opened

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class SmallDir:
    def __init__(self, name="", children=None, identifier=-1):
        if children is None:
            children = []
        self.children = children
        self.name = name
        self.identifier = identifier

    def from_dir(self, directory):
        # function to import data from a Dir object
        self.name = directory.name
        self.identifier = directory.identifier
        if directory.children is not None:
            for child in directory.children:
                self.children.append(copy.deepcopy(SmallDir().from_dir(child)))
        else:
            self.children = directory.children
        return self
