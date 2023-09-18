from __future__ import annotations
from . import *


class Shift:
    def __init__(self, value):
        if type(self) == Shift:
            raise NotImplementedError
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def __neg__(self) -> Shift:
        raise NotImplementedError


class Group(Iterable):
    def __init__(self, shift_type: Type[Shift]):
        if type(self) == Group:
            raise NotImplementedError('Group is an abstract class.')
        else:
            self.shift_type = shift_type

    def __iter__(self) -> Iterator[Shift]:
        raise NotImplementedError


class Point:
    def __init__(self, value):
        if type(self) == Point:
            raise NotImplementedError
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def __add__(self, other: Shift) -> Point:
        raise NotImplementedError


class Space(Iterable):
    def __init__(self, point_type: Type[Point]):
        if type(self) == Space:
            raise NotImplementedError('Space is an abstract class.')
        else:
            self.point_type = point_type

    def __iter__(self) -> Iterator[Point]:
        raise NotImplementedError

    class OutOfBoundsError(Exception):
        pass


class Level:
    def __init__(self, value):
        if type(self) == Level:
            raise NotImplementedError
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def __add__(self, other: Level) -> Level:
        raise NotImplementedError

    def __sub__(self, other: Level) -> Level:
        raise NotImplementedError

    def __le__(self, other: Level) -> bool:
        raise NotImplementedError

    def __lt__(self, other: Level) -> bool:
        return self <= other and self != other


class Lattice:
    def __init__(self, level_type: Type[Level]):
        if type(self) == Lattice:
            raise NotImplementedError('Lattice is an abstract class.')
        else:
            self.level_type = level_type

    @property
    def bot(self) -> Level:
        raise NotImplementedError

    @property
    def top(self) -> Level:
        raise NotImplementedError

    def __mul__(self, other: Lattice) -> Lattice:
        raise NotImplementedError

    def __truediv__(self, other: Lattice) -> Lattice:
        raise NotImplementedError

    def __le__(self, other: Lattice) -> bool:
        raise NotImplementedError

    @staticmethod
    def supremum(a: Level, b: Level) -> Level:
        raise NotImplementedError

    @staticmethod
    def infimum(a: Level, b: Level) -> Level:
        raise NotImplementedError


class Image:
    def __init__(self, array: np.ndarray, space: Space, lattice: Lattice):
        self.array = array
        self.space = space
        self.lattice = lattice

    def __getitem__(self, point: Point) -> Level:
        raise NotImplementedError

    def __setitem__(self, point: Point, value: Level):
        raise NotImplementedError


class StructuringElement:
    def __init__(self, array: np.ndarray, group: Group, lattice: Lattice):
        self.array = array
        self.group = group
        self.lattice = lattice

    def __getitem__(self, shift: Shift) -> Level:
        raise NotImplementedError


def dilation(image: Image, structuring_element: StructuringElement):
    lattice = image.lattice * structuring_element.lattice
    output = type(image)(np.empty_like(image.array), image.space, lattice)
    for point in image.space:
        val = lattice.bot
        for shift in structuring_element.group:
            try:
                tmp = image[point + (-shift)] + structuring_element[shift]
            except Space.OutOfBoundsError:
                continue
            val = lattice.supremum(tmp, val)
        output[point] = val
    return output


def erosion(image: Image, structuring_element: StructuringElement):
    lattice = image.lattice / structuring_element.lattice
    output = type(image)(np.empty_like(image.array), image.space, lattice)
    for point in image.space:
        val = lattice.top
        for shift in structuring_element.group:
            try:
                tmp = image[point + shift] - structuring_element[shift]
            except Space.OutOfBoundsError:
                continue
            val = lattice.infimum(tmp, val)
        output[point] = val
    return output
