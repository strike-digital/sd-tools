from __future__ import annotations

import math
from typing import Any

from mathutils import Vector as V


def clamp(value, min=0.0, max=1.0):
    """Clamp the value to between the specified min and max"""
    if value < min:
        value = min
    elif value > max:
        value = max
    return value


def round_increment(x: float, increment: int) -> int:
    return increment * round(x / increment)


def roundup(x: float, increment: int) -> int:
    """Round x up to the nearest specified increment"""
    return int(math.ceil(x / increment)) * int(increment)


def lerp(a, b, fac):
    """Linear interpolation between a and b."""
    return a + (b - a) * fac


def inv_lerp(a: float, b: float, fac: float) -> float:
    """Inverse Linear Interpolation from a and b"""
    return (fac - a) / (b - a)


def map_range(i_min: float, i_max: float, o_min: float, o_max: float, fac: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    """
    return lerp(inv_lerp(i_min, i_max, fac), o_min, o_max)


def vec_lerp(a, b, fac):
    """Linear interpolation between vectors a and b"""
    return V(lerp(i, j, fac) for i, j in zip(a, b))


def vec_divide(a, b) -> V:
    """Elementwise divide for two vectors"""
    return V(e1 / e2 if e2 != 0 else 0 for e1, e2 in zip(a, b))


def vec_multiply(a, b) -> V:
    """Elementwise multiply for two vectors"""
    return V(e1 * e2 for e1, e2 in zip(a, b))


def vec_min(a, b) -> V:
    """Elementwise minimum for two vectors"""
    return V(min(e) for e in zip(a, b))


def vec_max(a, b) -> V:
    """Elementwise maximum for two vectors"""
    return V(max(e) for e in zip(a, b))


def pad_list(a: list, length: int, value: Any = None):
    """Pad a list with the given value to the given length"""
    a = list(a)
    a.extend([value] * (length - len(a)))
    return a


class Line:
    def __init__(self, start: V = (0, 0), end: V = (0, 0)):
        self.start = V(start)
        self.end = V(end)

    def __bool__(self):
        return bool(self.start.x + self.start.y + self.end.x + self.end.y)

    def __str__(self):
        return f"Line(({self.start.x}, {self.start.y}), ({self.end.x}, {self.end.y}))"

    def __add__(self, other: V):
        return Line(self.start + other, self.end + other)

    def __sub__(self, other: V):
        return Line(self.start - other, self.end - other)

    def __mul__(self, other: V):
        return Line(self.start * other, self.end * other)

    def __div__(self, other: V):
        return Line(self.start / other, self.end / other)

    def __iadd__(self, other: V):
        self.start += other
        self.end += other
        return self

    def __isub__(self, other: V):
        self.start -= other
        self.end -= other
        return self

    def __imul__(self, other: V):
        self.start *= other
        self.end *= other
        return self

    def __idiv__(self, other: V):
        self.start /= other
        self.end /= other
        return self

    def __iter__(self):
        yield self.start
        yield self.end

    @property
    def x(self):
        return self.start.x

    @x.setter
    def x(self, value: float):
        self.start.x = value
        self.end.x = value

    @property
    def y(self):
        return self.start.y

    @y.setter
    def y(self, value: float):
        self.start.y = value
        self.end.y = value

    @property
    def size(self):
        return self.end - self.start

    @property
    def length(self):
        return (self.end - self.start).length


class Rectangle:
    """Helper class to represent a rectangle"""

    __slots__ = ["min", "max"]

    def __init__(self, min_co=(0, 0), max_co=(0, 0)):
        min_co = V(min_co)
        max_co = V(max_co)

        self.min = min_co
        self.max = max_co

    # alternate getter syntax
    minx = property(fget=lambda self: self.min.x)
    miny = property(fget=lambda self: self.min.y)
    maxx = property(fget=lambda self: self.max.x)
    maxy = property(fget=lambda self: self.max.y)

    @property
    def width(self):
        return self.max.x - self.min.x

    @property
    def height(self):
        return self.max.y - self.min.y

    @property
    def coords(self):
        """Return coordinates for drawing"""
        coords = [
            (self.minx, self.miny),
            (self.maxx, self.miny),
            (self.maxx, self.maxy),
            (self.minx, self.maxy),
        ]
        return coords

    @property
    def indices(self):
        return [(0, 1, 2), (0, 2, 3)]

    @property
    def size(self):
        return self.max - self.min

    # FIXME: This can just be changed to using vec_mean of the min and max
    @property
    def center(self):
        return self.min + vec_divide(self.max - self.min, V((2, 2)))

    # return the actual min/max values. Needed because the class does not check
    # if the min and max values given are actually min and max at init.
    # I could fix it, but a bunch of stuff is built on it already, and I can't really be bothered
    @property
    def true_min(self):
        return vec_min(self.min, self.max)

    @property
    def true_max(self):
        return vec_max(self.min, self.max)

    @property
    def midpoint(self):
        return (self.min + self.max) / 2

    def __str__(self):
        return f"Rectangle(V({self.minx}, {self.miny}), V({self.maxx}, {self.maxy}))"

    def __repr__(self):
        return self.__str__()

    def __mul__(self, value):
        if not isinstance(value, V):
            value = V((value, value))
        return Rectangle(self.min * value, self.max * value)

    def __add__(self, value) -> Rectangle:
        if not isinstance(value, V):
            value = V((value, value))
        return Rectangle(self.min + value, self.max + value)

    def copy(self):
        return Rectangle(self.min.copy(), self.max.copy())

    def translate(self, offset: V):
        self.min += offset
        self.max += offset

    def isinside(self, point) -> bool:
        """Check if a point is inside this rectangle"""
        point = point
        min = self.true_min
        max = self.true_max
        return min.x <= point[0] <= max.x and min.y <= point[1] <= max.y

    def as_lines(self, individual=False):
        """Return a list of lines that make up this rectangle"""
        lines = []
        add = lines.append if individual else lines.extend
        coords = self.coords
        for i, coord in enumerate(coords):
            add((coord, coords[i - 1]))
        return lines

    def crop(self, rectangle):
        """Crop this rectangle to the inside of another one"""
        self.min = vec_max(self.min, rectangle.min)
        self.max = vec_min(self.max, rectangle.max)
        # prevent min/max overspilling on other side
        self.min = vec_min(self.min, rectangle.max)
        self.max = vec_max(self.max, rectangle.min)

    def combine(self, rectangle: Rectangle):
        """Combine this rectangle with another rectangle, giving the bounding box of both of them."""
        self.min = vec_min(self.min, rectangle.min)
        self.max = vec_max(self.max, rectangle.max)

    def expand(self, amount: float | V):
        if not isinstance(amount, V):
            amount = V((amount, amount))
        self.min -= amount
        self.max += amount
