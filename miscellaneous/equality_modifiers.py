class EqualityByType:
    def __eq__(self, other):
        return type(self) == type(other)


class EqualityByArgs:
    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):
        return self.args == other.args and type(self) == type(other)


class Const(EqualityByArgs):
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value


def selective_inheritance(name, base_attributes):
    bases = [object]
    for base_object in base_attributes:
        if type(base_object) not in bases:
            bases.append(type(base_object))

    attributes = {}
    for base_object in base_attributes:
        attributes[base_attributes[base_object]] = getattr(base_object, base_attributes[base_object])
    x = type(name, (object,), attributes)
    return x

