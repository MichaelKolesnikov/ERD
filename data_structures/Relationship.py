from data_structures.Attribute import Attribute
from data_structures.Cardinality import Cardinality


class Relationship:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.cardinalities = []
        self.attributes: list[Attribute] = []
        self.x = 0
        self.y = 0

    def add_attribute(self, attribute: Attribute):
        self.attributes.append(attribute)

    def add_cardinality(self, cardinality: Cardinality):
        self.cardinalities.append(cardinality)
