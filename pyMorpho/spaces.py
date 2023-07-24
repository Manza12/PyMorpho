from .abstraction import Space


class Euclidean(Space):
    def __init__(self, cardinal: int):
        self._cardinal = cardinal
