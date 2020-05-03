class EqualityByType:
    def __eq__(self, other):
        return type(self) == type(other)


class EqualityByArgs:
    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):
        return self.args == other.args and type(self) == type(other)
