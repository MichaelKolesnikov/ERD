class Attribute:
    def __init__(self, name: str, is_primary: bool=False):
        self.name: str = name
        self.is_primary: bool = is_primary
