from __future__ import annotations
from collections import Iterable
from typing import Iterator
import numpy as np


class Shift:
    def __neg__(self) -> Shift:
        raise NotImplementedError


class Point:
    def __add__(self, other: Shift) -> Point:
        raise NotImplementedError


class Space(Iterable):
    def __iter__(self) -> Iterator[Point]:
        raise NotImplementedError

    @property
    def dimension(self):
        raise NotImplementedError

    @property
    def sizes(self):
        raise NotImplementedError


class Group(Iterable):
    def __iter__(self) -> Iterator[Shift]:
        raise NotImplementedError

    @property
    def identity(self) -> Shift:
        raise NotImplementedError

    @property
    def dimension(self):
        raise NotImplementedError

    @property
    def sizes(self):
        raise NotImplementedError


class Level:
    def __add__(self, other: Level) -> Level:
        raise NotImplementedError

    def __sub__(self, other: Level) -> Level:
        raise NotImplementedError


class Lattice:
    @property
    def bot(self) -> Level:
        raise NotImplementedError

    @property
    def top(self) -> Level:
        raise NotImplementedError

    @staticmethod
    def supremum(a: Level, b: Level) -> Level:
        raise NotImplementedError

    @staticmethod
    def infimum(a: Level, b: Level) -> Level:
        raise NotImplementedError


class Image:
    def __init__(self, array: np.ndarray, space: Space, lattice: Lattice):
        # Check dimension
        assert len(array.shape) == space.dimension, 'Array and space should share dimension.'

        # Check sizes
        for size_a, size_s in zip(array.shape, space.sizes):
            assert size_a == size_s, 'Sizes should coincide between array and space'

        # Check lattice
        for value in array.flat:
            assert isinstance(value, type(lattice.bot)), 'Array should contain lattice values.'

        self.array = array
        self.space = space
        self.lattice = lattice

    def __getitem__(self, point: Point) -> Level:
        raise NotImplementedError

    def __setitem__(self, point: Point, value: Level):
        raise NotImplementedError

    @classmethod
    def bottom_like(cls, image: Image):
        array = np.empty_like(image.array)
        for i in range(array.size):
            array.flat[i] = image.lattice.bot
        return cls(array, image.space, image.lattice)

    @classmethod
    def top_like(cls, image: Image):
        array = np.empty_like(image.array)
        for i in range(array.size):
            array.flat[i] = image.lattice.top
        return cls(array, image.space, image.lattice)


class StructuringElement:
    def __init__(self, array: np.ndarray, group: Group, lattice: Lattice):
        # Check dimension
        assert len(array.shape) == group.dimension, 'Array and group should share dimension.'

        # Check sizes
        for size_a, size_g in zip(array.shape, group.sizes):
            assert size_a == size_g, 'Sizes should coincide between array and group.'

        # Check lattice
        for value in array.flat:
            assert isinstance(value, type(lattice.bot)), 'Array should contain lattice values.'

        self.array = array
        self.group = group
        self.lattice = lattice

    def __getitem__(self, shift: Shift) -> Level:
        raise NotImplementedError

    @classmethod
    def bottom_like(cls, structuring_element: StructuringElement):
        array = np.empty_like(structuring_element.array)
        for i in range(array.size):
            array.flat[i] = structuring_element.lattice.bot
        return cls(array, structuring_element.group, structuring_element.lattice)


def dilation(image: Image, structuring_element: StructuringElement):
    output = type(image).bottom_like(image)
    for point in image.space:
        val = image.lattice.bot
        for shift in structuring_element.group:
            tmp = image[point + (-shift)] + structuring_element[shift]
            val = image.lattice.supremum(tmp, val)
        output[point] = val
    return output


def erosion(image: Image, structuring_element: StructuringElement):
    output = type(image).top_like(image)
    for point in image.space:
        val = image.lattice.top
        for shift in structuring_element.group:
            try:
                tmp = image[point + shift] - structuring_element[shift]
            except AssertionError:
                continue
            val = image.lattice.infimum(tmp, val)
        output[point] = val
    return output
