from exception.ERDiagramException import ERDiagramException


class ParsingException(ERDiagramException):
    def __init__(self, message):
        super().__init__(message)
