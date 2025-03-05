import re

from data_structures.Attribute import Attribute
from data_structures.Cardinality import Cardinality
from data_structures.ERDiagram import ERDiagram
from data_structures.Entity import Entity
from data_structures.Relationship import Relationship


def parse_description_to_er_diagram(description: str) -> ERDiagram:
    entities: dict[str, Entity] = {}
    relationships: dict[str, Relationship] = {}

    entity_pattern = re.compile(r'Entity\(([^)]+)\)\(([^}]+)\)')
    relation_pattern = re.compile(r'Relation\(([^)]+)\)\(([^}]+)\)\(([^}]+)\)')
    cardinality_pattern = re.compile(r'(\w+)\[(\w+):(\w+)]')

    lines = description.strip().split('\n')

    for line in lines:
        if line.startswith("Entity"):
            match = entity_pattern.match(line)
            if match:
                entity_name = match.group(1).strip()
                attributes_str = match.group(2).strip()
                attributes = [Attribute(attr.strip()) for attr in attributes_str.split(',')]
                entities[entity_name] = Entity(entity_name, *attributes)

        elif line.startswith("Relation"):
            match = relation_pattern.match(line)
            if match:
                relation_name = match.group(1).strip()
                entities_str = match.group(2).strip()
                attributes_str = match.group(3).strip()

                cardinalities = []
                for entity_card_str in entities_str.split(','):
                    card_match = cardinality_pattern.match(entity_card_str)
                    if card_match:
                        entity_name = card_match.group(1)
                        min_card = card_match.group(2)
                        max_card = card_match.group(3)
                        cardinalities.append(Cardinality(entities[entity_name], min_card, max_card))

                attributes = [Attribute(attr.strip()) for attr in attributes_str.split(',')]
                relationships[relation_name] = Relationship(relation_name, cardinalities, *attributes)

    return ERDiagram(
        [entities[entity_str] for entity_str in entities],
        [relationships[relation_str] for relation_str in relationships]
    )
