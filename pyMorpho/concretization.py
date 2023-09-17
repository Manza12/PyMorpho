from __future__ import annotations
from . import *
from .abstraction import Space, Lattice, Group


# Lattices
class BooleanLattice(Lattice):

    def __init__(self):
        super().__init__()

    class Level(Lattice.Level):

        def __init__(self, value: bool):
            super().__init__()
            self._value = value

        @property
        def value(self):
            return self._value

        def __le__(self, other: BooleanLattice.Level) -> bool:
            assert isinstance(other, BooleanLattice.Level)
            return self.value <= other.value

        def __add__(self, other: Lattice.Level) -> Lattice.Level:
            return other + self

        def __sub__(self, other: Lattice.Level) -> Lattice.Level:
            raise NotImplementedError

        def __str__(self):
            if self.value:
                return '1'
            else:
                return '0'

    @property
    def bot(self) -> BooleanLattice.Level:
        return BooleanLattice.Level(False)

    @property
    def top(self) -> BooleanLattice.Level:
        return BooleanLattice.Level(True)

    def __mul__(self, other: Lattice) -> Lattice:
        return other


class RhythmicLattice(Lattice):
    def __init__(self):
        super().__init__()

    class Level(Lattice.Level):
        def __init__(self, value: int):
            super().__init__()
            self._value = value

        @property
        def value(self):
            return self._value

        def __add__(self, other: BooleanLattice.Level) -> RhythmicLattice.Level:
            if other.value:
                return self
            else:
                return RhythmicLattice.Level(0)

        def __sub__(self, other: RhythmicLattice.Level) -> BooleanLattice.Level:
            if self >= other:
                return BooleanLattice.Level(True)
            else:
                return BooleanLattice.Level(False)

        def __le__(self, other: RhythmicLattice.Level) -> bool:
            assert isinstance(other, RhythmicLattice.Level)
            return self.value <= other.value

        def __str__(self):
            if self.value == 0:
                return '-'
            elif self.value == 1:
                return '·'
            elif self.value == 2:
                return 'x'
            else:
                raise ValueError

    @property
    def bot(self) -> RhythmicLattice.Level:
        return RhythmicLattice.Level(0)

    @property
    def top(self) -> RhythmicLattice.Level:
        return RhythmicLattice.Level(2)

    def __mul__(self, other: Lattice) -> Lattice:
        if isinstance(other, RhythmicLattice):
            return BooleanLattice()
        else:
            raise NotImplementedError

    @staticmethod
    def array_to_lattice(array: np.ndarray) -> np.ndarray:
        new_array = np.empty_like(array, dtype=object)
        for i in range(array.size):
            new_array.flat[i] = RhythmicLattice.Level(array.flat[i])
        return new_array


# Groups
class Z(Group):

    def __init__(self, n: int):
        super().__init__()
        self._n = n

    class Shift(Group.Shift):

        def __init__(self, value: int):
            super().__init__()
            self._value = value

        @property
        def value(self):
            return self._value

        def __neg__(self) -> Group.Shift:
            return Z.Shift(-self.value)

        def __str__(self):
            return '{0:+}'.format(self.value)

    def __iter__(self) -> Iterator[Group.Shift]:
        for i in range(self._n):
            yield Z.Shift(i)

    def __mul__(self, other: Group) -> GroupProduct:
        assert isinstance(other, Group)
        return GroupProduct(self, other)

    def __getitem__(self, shift: Z.Shift) -> List[int]:
        assert isinstance(shift, Z.Shift)
        return [shift.value]


class T(Group):
    def __init__(self, n: int):
        super().__init__()
        self._n = n

    class Shift(Group.Shift):

        def __init__(self, value: int):
            super().__init__()
            self._value = value % 12

        @property
        def value(self):
            return self._value

        def __neg__(self) -> Group.Shift:
            return T.Shift(-self.value)

        def __str__(self):
            return '{0:+}'.format(self.value)

    def __iter__(self) -> Iterator[Group.Shift]:
        for i in range(self._n):
            yield T.Shift(i)

    def __mul__(self, other: Group) -> GroupProduct:
        assert isinstance(other, Group)
        return GroupProduct(self, other)

    def __getitem__(self, shift: T.Shift) -> List[int]:
        assert isinstance(shift, T.Shift)
        return [shift.value]


class GroupProduct(Group):
    def __init__(self, group_1: Group, group_2: Group):
        super().__init__()
        self._group_1 = group_1
        self._group_2 = group_2

    class Shift(Group.Shift):

        def __init__(self, shift_1: Group.Shift, shift_2: Group.Shift):
            super().__init__()
            self._shift_1 = shift_1
            self._shift_2 = shift_2

        @property
        def shift_1(self):
            return self._shift_1

        @property
        def shift_2(self):
            return self._shift_2

        def __neg__(self) -> Group.Shift:
            return GroupProduct.Shift(-self.shift_1, -self.shift_2)

        def __str__(self):
            return '({0}, {1})'.format(self.shift_1, self.shift_2)

    def __iter__(self) -> Iterator[Group.Shift]:
        for shift_1 in self._group_1:
            for shift_2 in self._group_2:
                yield GroupProduct.Shift(shift_1, shift_2)

    def __getitem__(self, shift: GroupProduct.Shift) -> List[int]:
        assert isinstance(shift, GroupProduct.Shift)
        return self._group_1[shift.shift_1] + self._group_2[shift.shift_2]


# Spaces
class Line(Space):

    def __init__(self, n: int):
        super().__init__()
        self._n = n

    class Point(Space.Point):

        def __init__(self, value: int):
            super().__init__()
            self._value = value

        @property
        def value(self):
            return self._value

        def __add__(self, other: Z.Shift) -> Line.Point:
            assert isinstance(other, Z.Shift)
            return Line.Point(self.value + other.value)

        def __str__(self):
            return str(self.value)

    def __iter__(self) -> Iterator[Line.Point]:
        for i in range(self._n):
            yield Line.Point(i)

    def __getitem__(self, point: Line.Point) -> List[int]:
        assert isinstance(point, Line.Point)
        if not 0 <= point.value < self._n:
            raise Space.OutOfBoundsError()
        return [point.value]

    def __mul__(self, other: Space) -> SpaceProduct:
        assert isinstance(other, Space)
        return SpaceProduct(self, other)


class Circle(Space):

    def __init__(self, n: int):
        super().__init__()
        self._n = n

    class Point(Space.Point):

        def __init__(self, value: int):
            super().__init__()
            self._value = value % 12

        @property
        def value(self):
            return self._value

        def __add__(self, other: T.Shift) -> Circle.Point:
            assert isinstance(other, T.Shift)
            return Circle.Point(self.value + other.value)

        def __str__(self):
            return str(self.value)

    def __iter__(self) -> Iterator[Circle.Point]:
        for i in range(self._n):
            yield self.Point(i)

    def __getitem__(self, point: Circle.Point) -> List[int]:
        assert isinstance(point, Circle.Point)
        return [point.value]

    def __mul__(self, other: Space) -> SpaceProduct:
        assert isinstance(other, Space)
        return SpaceProduct(self, other)


class SpaceProduct(Space):
    def __init__(self, space_1: Space, space_2: Space):
        super().__init__()
        self._space_1 = space_1
        self._space_2 = space_2

    class Point(Space.Point):

        def __init__(self, point_1: Space.Point, point_2: Space.Point):
            super().__init__()
            self._point_1 = point_1
            self._point_2 = point_2

        @property
        def point_1(self):
            return self._point_1

        @property
        def point_2(self):
            return self._point_2

        def __add__(self, other: GroupProduct.Shift) -> SpaceProduct.Point:
            assert isinstance(other, GroupProduct.Shift)
            return SpaceProduct.Point(self._point_1 + other.shift_1, self._point_2 + other.shift_2)

        def __str__(self):
            return '({0}, {1})'.format(self.point_1, self.point_2)

    def __iter__(self) -> Iterator[Group.Shift]:
        for point_1 in self._space_1:
            for point_2 in self._space_2:
                yield SpaceProduct.Point(point_1, point_2)

    def __getitem__(self, point: SpaceProduct.Point) -> List[int]:
        assert isinstance(point, SpaceProduct.Point)
        return self._space_1[point.point_1] + self._space_2[point.point_2]
