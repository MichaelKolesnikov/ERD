from data_structures.Entity import Entity
from exception.ERDiagramException import ERDiagramException


class NotExistingEntityException(ERDiagramException):
    def __init__(self, entity: Entity):
        super().__init__(f"Entity {entity.name} doesn't exist")
