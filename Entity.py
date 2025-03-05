from Attribute import Attribute


class Entity:
    def __init__(self, name):
        self.name = name
        self.attributes: list[Attribute] = []
        self.x = 0
        self.y = 0
