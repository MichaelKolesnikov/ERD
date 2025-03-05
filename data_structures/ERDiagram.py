from data_structures.Entity import Entity
from data_structures.Relationship import Relationship
from exception.NotExistingEntityException import NotExistingEntityException


class ERDiagram:
    def __init__(self, entities: list[Entity], relationships: list[Relationship]):
        self.entities: list[Entity] = entities
        self.relationships: list[Relationship] = relationships

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        self.entities.remove(entity)

    def add_relationship(self, relationship: Relationship):
        for cardinality in relationship.cardinalities:
            if cardinality.entity not in self.entities:
                raise NotExistingEntityException(cardinality.entity)
        self.relationships.append(relationship)

    def remove_relationship(self, relationship: Relationship):
        self.relationships.remove(relationship)

    def __str__(self):
        description = ""
        for entity in self.entities:
            description += f"Entity({entity.name})({",".join([attr.name for attr in entity.attributes])})\n"
        for relationship in self.relationships:
            description += f"Relation({relationship.name})({",".join([str(card) for card in relationship.cardinalities])})({",".join([attr.name for attr in relationship.attributes])})"
        return description
