from __future__ import annotations
from . import *
from .abstraction import Space, Point, Lattice, Level, Group, Shift, Image, StructuringElement


# Lattices
class BooleanLevel(Level):
    def __init__(self, value: bool):
        super().__init__(value)

    def __le__(self, other: BooleanLevel) -> bool:
        assert isinstance(other, BooleanLevel)
        return self.value <= other.value

    def __add__(self, other: Level) -> Level:
        return other + self

    def __sub__(self, other: Level) -> Level:
        raise NotImplementedError

    def __str__(self):
        if self.value:
            return '1'
        else:
            return '0'


class BooleanLattice(Lattice):

    def __init__(self):
        super().__init__(BooleanLevel)

    @property
    def bot(self) -> Level:
        return self.level_type(False)

    @property
    def top(self) -> Level:
        return self.level_type(True)

    def __mul__(self, other: Lattice) -> Lattice:
        return other

    def infimum(self, a: Level, b: Level) -> Level:
        return BooleanLevel(a.value and b.value)

    def supremum(self, a: Level, b: Level) -> Level:
        return BooleanLevel(a.value or b.value)


class RhythmicLevel(Level):
    def __init__(self, value: int):
        super().__init__(value)

    def __add__(self, other: BooleanLevel) -> RhythmicLevel:
        if other.value:
            return self
        else:
            return RhythmicLevel(0)

    def __sub__(self, other: RhythmicLevel) -> BooleanLevel:
        if self >= other:
            return BooleanLevel(True)
        else:
            return BooleanLevel(False)

    def __le__(self, other: RhythmicLevel) -> bool:
        assert isinstance(other, RhythmicLevel)
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


class RhythmicLattice(Lattice):
    def __init__(self):
        super().__init__(RhythmicLevel)

    @property
    def bot(self) -> Level:
        return RhythmicLevel(0)

    @property
    def top(self) -> RhythmicLevel:
        return RhythmicLevel(2)

    def __mul__(self, other: Lattice) -> Lattice:
        if isinstance(other, RhythmicLattice):
            return BooleanLattice()
        else:
            raise NotImplementedError

    def __truediv__(self, other: RhythmicLattice) -> BooleanLattice:
        assert isinstance(other, RhythmicLattice)
        return BooleanLattice()

    @staticmethod
    def supremum(a: RhythmicLevel, b: RhythmicLevel) -> RhythmicLevel:
        assert isinstance(a, RhythmicLevel)
        assert isinstance(b, RhythmicLevel)
        return RhythmicLevel(max(a.value, b.value))

    @staticmethod
    def infimum(a: RhythmicLevel, b: RhythmicLevel) -> RhythmicLevel:
        assert isinstance(a, RhythmicLevel)
        assert isinstance(b, RhythmicLevel)
        return RhythmicLevel(min(a.value, b.value))

    @staticmethod
    def array_to_lattice(array: np.ndarray) -> np.ndarray:
        new_array = np.empty_like(array, dtype=object)
        for index in np.ndindex(*array.shape):
            new_array[index] = RhythmicLevel(array[index])
        return new_array


# Groups
class ZShift(Shift):

    def __init__(self, value: int):
        super().__init__(value)

    def __neg__(self) -> Shift:
        return ZShift(-self.value)

    def __str__(self):
        return '{0:+}'.format(self.value)


class Z(Group):

    def __init__(self, n: int):
        super().__init__(ZShift)
        self._n = n

    def __iter__(self) -> Iterator[Shift]:
        for i in range(self._n):
            element = self.shift_type(i)
            yield element

    def __mul__(self, other: Group) -> ProductGroup:
        assert isinstance(other, Group)
        return ProductGroup(self, other)

    def __getitem__(self, shift: ZShift) -> List[int]:
        assert isinstance(shift, ZShift)
        return [shift.value]


class TShift(Shift):

    def __init__(self, value: int):
        super().__init__(value % 12)

    def __neg__(self) -> TShift:
        return TShift(-self.value)

    def __str__(self):
        return '{0:+}'.format(self.value)


class T(Group):
    def __init__(self, n: int):
        super().__init__(TShift)
        self._n = n

    def __iter__(self) -> Iterator[TShift]:
        for i in range(self._n):
            yield self.shift_type(i)

    def __mul__(self, other: Group) -> ProductGroup:
        assert isinstance(other, Group)
        return ProductGroup(self, other)

    def __getitem__(self, shift: TShift) -> List[int]:
        assert isinstance(shift, TShift)
        return [shift.value]


class ProductShift(Shift):
    def __init__(self, shift_1: Shift, shift_2: Shift):
        super().__init__((shift_1, shift_2))

    @property
    def shift_1(self):
        return self.value[0]

    @property
    def shift_2(self):
        return self.value[1]

    def __neg__(self) -> ProductShift:
        return ProductShift(-self.shift_1, -self.shift_2)

    def __str__(self):
        return '({0}, {1})'.format(self.shift_1, self.shift_2)


class ProductGroup(Group):
    def __init__(self, group_1: Group, group_2: Group):
        super().__init__(ProductShift)
        self._group_1 = group_1
        self._group_2 = group_2

    def __iter__(self) -> Iterator[ProductShift]:
        for shift_1 in self._group_1:
            for shift_2 in self._group_2:
                yield ProductShift(shift_1, shift_2)


# Spaces
class LinePoint(Point):

    def __init__(self, value: int):
        super().__init__(value)

    def __add__(self, other: ZShift) -> LinePoint:
        assert isinstance(other, ZShift)
        return LinePoint(self.value + other.value)

    def __str__(self):
        return str(self.value)


class Line(Space):
    def __init__(self, n: int):
        super().__init__(LinePoint)
        self._n = n

    def __iter__(self) -> Iterator[LinePoint]:
        for i in range(self._n):
            yield LinePoint(i)

    def __getitem__(self, point: LinePoint) -> List[int]:
        assert isinstance(point, LinePoint)
        if not 0 <= point.value < self._n:
            raise Space.OutOfBoundsError()
        return [point.value]

    def __mul__(self, other: Space) -> ProductSpace:
        assert isinstance(other, Space)
        return ProductSpace(self, other)


class CirclePoint(Point):
    def __init__(self, value: int):
        super().__init__(value % 12)

    def __add__(self, other: TShift) -> CirclePoint:
        assert isinstance(other, TShift)
        return CirclePoint(self.value + other.value)

    def __str__(self):
        return str(self.value)


class Circle(Space):

    def __init__(self, n: int):
        super().__init__(CirclePoint)
        self._n = n

    def __iter__(self) -> Iterator[CirclePoint]:
        for i in range(self._n):
            yield self.point_type(i)

    def __getitem__(self, point: CirclePoint) -> List[int]:
        assert isinstance(point, CirclePoint)
        return [point.value]

    def __mul__(self, other: Space) -> ProductSpace:
        assert isinstance(other, Space)
        return ProductSpace(self, other)


class ProductPoint(Point):
    def __init__(self, point_1: Point, point_2: Point):
        super().__init__((point_1, point_2))

    @property
    def point_1(self):
        return self.value[0]

    @property
    def point_2(self):
        return self.value[1]

    def __add__(self, other: ProductShift) -> ProductPoint:
        assert isinstance(other, ProductShift)
        return ProductPoint(self.point_1 + other.shift_1, self.point_2 + other.shift_2)

    def __str__(self):
        return '({0}, {1})'.format(self.point_1, self.point_2)


class ProductSpace(Space):
    def __init__(self, space_1: Space, space_2: Space):
        super().__init__(ProductPoint)
        self._space_1 = space_1
        self._space_2 = space_2

    def __iter__(self) -> Iterator[ProductPoint]:
        for point_1 in self._space_1:
            for point_2 in self._space_2:
                yield ProductPoint(point_1, point_2)


# Images
class ChromaRoll(Image):
    def __init__(self, array: np.ndarray, _, lattice: Lattice):
        assert len(array.shape) == 2
        assert array.shape[0] == 12
        super().__init__(array, Circle(12) * Line(array.shape[1]), lattice)

    def __getitem__(self, point: Point) -> Level:
        assert isinstance(point, ProductPoint)
        if not 0 <= point.point_1.value < 12:
            raise Space.OutOfBoundsError()
        elif not 0 <= point.point_2.value < self.array.shape[1]:
            raise Space.OutOfBoundsError()
        return self.array[point.point_1.value, point.point_2.value]

    def __setitem__(self, point: Point, value: Level):
        assert isinstance(point, ProductPoint)
        self.array[point.point_1.value, point.point_2.value] = value


class ChromaRollPattern(StructuringElement):
    def __init__(self, array: np.ndarray):
        assert len(array.shape) == 2
        assert array.shape[0] == 12
        super().__init__(array, T(12) * Z(array.shape[1]), RhythmicLattice())

    def __getitem__(self, shift: Shift) -> RhythmicLevel:
        assert isinstance(shift, ProductShift)
        return self.array[shift.shift_1.value, shift.shift_2.value]
