from equality_modifiers import EqualityByArgs


class Location(EqualityByArgs):
    def __init__(self, *coords):
        super().__init__(*coords)

