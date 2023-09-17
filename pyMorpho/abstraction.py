from __future__ import annotations
from . import *


class Space(Iterable):
    def __init__(self):
        if type(self) == Space:
            raise NotImplementedError('Space is an abstract class.')

    class Point:
        def __init__(self):
            if type(self) == Space.Point:
                raise NotImplementedError

        def __add__(self, other: Group.Shift) -> Space.Point:
            raise NotImplementedError

    def __iter__(self) -> Iterator[Point]:
        raise NotImplementedError

    def __getitem__(self, point: Space.Point) -> List[int]:
        raise NotImplementedError

    class OutOfBoundsError(Exception):
        pass


class Group(Iterable):
    def __init__(self):
        if type(self) == Group:
            raise NotImplementedError('Group is an abstract class.')

    class Shift:
        def __init__(self):
            if type(self) == Group.Shift:
                raise NotImplementedError

        def __neg__(self) -> Group.Shift:
            raise NotImplementedError

    def __iter__(self) -> Iterator[Group.Shift]:
        raise NotImplementedError

    def __getitem__(self, shift: Group.Shift) -> List[int]:
        raise NotImplementedError


class Lattice:
    def __init__(self):
        if type(self) == Lattice:
            raise NotImplementedError('Lattice is an abstract class.')

    class Level:
        def __init__(self):
            if type(self) == Lattice.Level:
                raise NotImplementedError

        def __add__(self, other: Lattice.Level) -> Lattice.Level:
            raise NotImplementedError

        def __sub__(self, other: Lattice.Level) -> Lattice.Level:
            raise NotImplementedError

        def __le__(self, other: Lattice.Level) -> bool:
            raise NotImplementedError

        def __lt__(self, other: Lattice.Level) -> bool:
            return self <= other and self != other

    @property
    def bot(self) -> Level:
        raise NotImplementedError

    @property
    def top(self) -> Level:
        raise NotImplementedError

    def __mul__(self, other: Lattice) -> Lattice:
        raise NotImplementedError


class Image:
    def __init__(self, array: np.ndarray, space: Space, lattice: Lattice):
        self.array = array
        self.space = space
        self.lattice = lattice

    def __getitem__(self, point: Space.Point) -> Lattice.Level:
        return self.array[tuple(self.space[point])]

    def __setitem__(self, point: Space.Point, value: Lattice.Level):
        self.array[tuple(self.space[point])] = value

    def empty_like(self, lattice: Lattice):
        array = np.empty_like(self.array, dtype=object)
        return type(self)(array, self.space, lattice)


class StructuringElement:
    def __init__(self, array: np.ndarray, group: Group, lattice: Lattice):
        self.array = array
        self.group = group
        self.lattice = lattice

    def __getitem__(self, shift: Group.Shift) -> Lattice.Level:
        return self.array[tuple(self.group[shift])]

    @classmethod
    def bottom_like(cls, structuring_element: StructuringElement):
        array = np.empty_like(structuring_element.array)
        for i in range(array.size):
            array.flat[i] = structuring_element.lattice.bot
        return cls(array, structuring_element.group, structuring_element.lattice)


def dilation(image: Image, structuring_element: StructuringElement):
    new_lattice = image.lattice * structuring_element.lattice
    output = image.empty_like(new_lattice)
    for point in image.space:
        val = new_lattice.bot
        for shift in structuring_element.group:
            try:
                tmp = image[point + (-shift)] + structuring_element[shift]
            except Space.OutOfBoundsError:
                continue
            val = max(tmp, val)
        output[point] = val
    return output


def erosion(image: Image, structuring_element: StructuringElement):
    new_lattice = image.lattice * structuring_element.lattice
    output = image.empty_like(new_lattice)
    for point in image.space:
        val = new_lattice.top
        for shift in structuring_element.group:
            try:
                tmp = image[point + shift] - structuring_element[shift]
            except Space.OutOfBoundsError:
                continue
            val = min(tmp, val)
        output[point] = val
    return output
