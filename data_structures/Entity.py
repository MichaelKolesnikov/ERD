from data_structures.Attribute import Attribute


class Entity:
    def __init__(self, name):
        self.name = name
        self.attributes: list[Attribute] = []
        self.x = 0
        self.y = 0

    def add_attribute(self, attribute: Attribute):
        self.attributes.append(attribute)
