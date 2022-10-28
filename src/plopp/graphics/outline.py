# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import value_to_string

import pythreejs as p3
import numpy as np
from matplotlib import ticker
from scipp import Variable
from typing import List, Tuple


def _get_delta(x: Variable, axis: int) -> float:
    """
    Compute the difference between two bounds along a given axis.
    """
    return (x[axis][1] - x[axis][0]).value


def _get_offsets(limits: Tuple[Variable, Variable, Variable], axis: int,
                 ind: int) -> np.ndarray:
    """
    Compute offsets for 3 dimensions, along the edges of the box.
    """
    offsets = np.array([limits[i][ind].value for i in range(3)])
    offsets[axis] = 0
    return offsets


def _make_geometry(limits: Tuple[Variable, Variable, Variable]) -> p3.EdgesGeometry:
    """
    Make a geometry to represent the edges of a cubic box.
    """
    return p3.EdgesGeometry(
        p3.BoxBufferGeometry(width=_get_delta(limits, axis=0),
                             height=_get_delta(limits, axis=1),
                             depth=_get_delta(limits, axis=2)))


def _make_sprite(string: str,
                 position: Tuple[float, float, float],
                 color: str = "black",
                 size: float = 1.0) -> p3.Sprite:
    """
    Make a text-based sprite for axis tick.
    """
    sm = p3.SpriteMaterial(map=p3.TextTexture(string=string,
                                              color=color,
                                              size=300,
                                              squareTexture=True),
                           transparent=True)
    return p3.Sprite(material=sm, position=position, scale=[size, size, size])


class Outline(p3.Group):
    """
    Create an object that draws a rectangular outline, given some limits for the XYZ
    dimensions. Along the lower edges of the cube are added some tick labels and axes
    labels, according to the dimension extents, dimension names, and units given in
    the limits.

    Parameters
    ----------
    limits:
        A tuple of variables, each of length 2, which contain the lower and upper bounds
        for the outline. Each variable also has a dimension, which is to be used as the
        dimension for that direction, as well as a unit, which will be used to label
        the corresponding axis.
    tick_size:
        A number to scale the tick size.
    """

    def __init__(self,
                 limits: Tuple[Variable, Variable, Variable],
                 tick_size: float = None):

        center = [var.mean().value for var in limits]
        if tick_size is None:
            tick_size = 0.05 * np.mean([_get_delta(limits, axis=i) for i in range(3)])

        self.box = p3.LineSegments(geometry=_make_geometry(limits),
                                   material=p3.LineBasicMaterial(color='#000000'),
                                   position=center)

        self.ticks = self._make_ticks(limits=limits, tick_size=tick_size)
        self.labels = self._make_labels(limits=limits,
                                        center=center,
                                        tick_size=tick_size)

        super().__init__()
        for obj in (self.box, self.ticks, self.labels):
            self.add(obj)

    def _make_ticks(self, limits: Tuple[Variable, Variable, Variable],
                    tick_size: float) -> p3.Group:
        """
        Create tick labels on outline edges
        """
        ticks_group = p3.Group()
        iden = np.identity(3, dtype=np.float32)
        ticker_ = ticker.MaxNLocator(5)
        for axis in range(3):
            ticks = ticker_.tick_values(limits[axis][0].value, limits[axis][1].value)
            for tick in ticks:
                if limits[axis][0].value <= tick <= limits[axis][1].value:
                    tick_pos = iden[axis] * tick + _get_offsets(limits, axis, 0)
                    ticks_group.add(
                        _make_sprite(string=value_to_string(tick, precision=1),
                                     position=tick_pos.tolist(),
                                     size=tick_size))
        return ticks_group

    def _make_labels(self, limits: Tuple[Variable, Variable, Variable],
                     center: List[float], tick_size: float) -> p3.Group:
        """
        Create axes labels (coord dimension and unit) on outline edges
        """
        labels_group = p3.Group()
        for axis in range(3):
            axis_label = f'{limits[axis].dim} [{limits[axis].unit}]'
            # Offset labels 5% beyond axis ticks to reduce overlap
            delta = 0.05
            labels_group.add(
                _make_sprite(string=axis_label,
                             position=(np.roll([1, 0, 0], axis) * center[axis] +
                                       (1.0 + delta) * _get_offsets(limits, axis, 0) -
                                       delta * _get_offsets(limits, axis, 1)).tolist(),
                             size=tick_size * 0.3 * len(axis_label)))

        return labels_group
