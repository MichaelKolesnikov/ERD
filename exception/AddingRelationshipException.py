from exception.ERDiagramException import ERDiagramException


class AddingRelationshipException(ERDiagramException):
    def __init__(self, message: str):
        super().__init__(message)
