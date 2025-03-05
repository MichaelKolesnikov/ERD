from Attribute import Attribute


class Relationship:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.cardinalities = []
        self.attributes: list[Attribute] = []
        self.x = 0
        self.y = 0
