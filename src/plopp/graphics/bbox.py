# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

# import numpy as np
import scipp as sc

from ..core.limits import find_limits, fix_empty_range

# from ..core.utils import merge_masks


def _none_reduce(*args: float, op: Callable) -> float:
    elems = [x for x in args if x is not None]
    if not elems:
        return None
    return op(elems)


# def _none_max(*args: float) -> float:
#     return max(x for x in args if x is not None)


@dataclass
class BoundingBox:
    """
    A bounding box in 2D space.
    """

    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None
    zmin: float | None = None
    zmax: float | None = None

    def union(self, other: BoundingBox) -> BoundingBox:
        """
        Return the union of this bounding box with another one.
        """

        return BoundingBox(
            xmin=_none_reduce(self.xmin, other.xmin, op=min),
            xmax=_none_reduce(self.xmax, other.xmax, op=max),
            ymin=_none_reduce(self.ymin, other.ymin, op=min),
            ymax=_none_reduce(self.ymax, other.ymax, op=max),
            zmin=_none_reduce(self.zmin, other.zmin, op=min),
            zmax=_none_reduce(self.zmax, other.zmax, op=max),
        )


def axis_bounds(
    keys: tuple[str, str],
    x: sc.DataArray,
    scale: Literal['linear', 'log'],
    pad=False,
) -> dict[str, float]:
    """
    Find sensible limits for an axis, depending on linear or log scale.

    Parameters
    ----------
    keys:
        The keys to use for constructing a bounding box. The keys should be
        ``('xmin', 'xmax')`` for the horizontal axis, and ``('ymin', 'ymax')`` for the
        vertical axis.
    x:
        The data array to find limits for.
    scale:
        The scale of the axis (linear or log).
    pad:
        Whether to pad the limits.
    """
    values = fix_empty_range(find_limits(x, scale=scale, pad=pad))
    bounds = dict(zip(keys, (val.value for val in values), strict=True))
    return bounds
