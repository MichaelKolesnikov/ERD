from data_structures.Entity import Entity


class Cardinality:
    def __init__(self, entity: Entity, min_card, max_card):
        self.entity: Entity = entity
        self.min_card = min_card
        self.max_card = max_card

    def __str__(self):
        return f"{self.entity.name}[{self.min_card}:{self.max_card}]"
