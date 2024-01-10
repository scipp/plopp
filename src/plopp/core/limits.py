# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import numpy as np

import scipp as sc

from .utils import merge_masks


@dataclass
class BoundingBox:
    """
    A bounding box in 2D space.
    """

    xmin: Optional[float] = None
    xmax: Optional[float] = None
    ymin: Optional[float] = None
    ymax: Optional[float] = None

    def union(self, other: BoundingBox) -> BoundingBox:
        """
        Return the union of this bounding box with another one.
        """
        return BoundingBox(
            xmin=min(self.xmin or np.inf, other.xmin or np.inf),
            xmax=max(self.xmax or np.NINF, other.xmax or np.NINF),
            ymin=min(self.ymin or np.inf, other.ymin or np.inf),
            ymax=max(self.ymax or np.NINF, other.ymax or np.NINF),
        )


def find_limits(
    x: sc.DataArray, scale: Literal['linear', 'log'] = 'linear', pad: bool = False
) -> Tuple[sc.Variable, sc.Variable]:
    """
    Find sensible limits, depending on linear or log scale.
    If there are no finite values in the array, raise an error.
    If there are no positive values in the array, and the scale is log, fall back to
    some sensible default values.
    """
    if x.masks:
        x = sc.where(merge_masks(x.masks), sc.scalar(np.NaN, unit=x.unit), x.data)
    v = x.values
    finite_inds = np.isfinite(v)
    if np.sum(finite_inds) == 0:
        raise ValueError("No finite values were found in array. Cannot compute limits.")
    finite_vals = v[finite_inds]
    finite_max = None
    if scale == "log":
        positives = finite_vals > 0
        if np.sum(positives) == 0:
            finite_min = 0.1
            finite_max = 1.0
        else:
            initial = (np.finfo if v.dtype.kind == 'f' else np.iinfo)(v.dtype).max
            finite_min = np.amin(finite_vals, initial=initial, where=finite_vals > 0)
    else:
        finite_min = np.amin(finite_vals)
    if finite_max is None:
        finite_max = np.amax(finite_vals)
    if pad:
        delta = 0.05
        if scale == 'log':
            p = (finite_max / finite_min) ** delta
            finite_min /= p
            finite_max *= p
        else:
            p = (finite_max - finite_min) * delta
            finite_min -= p
            finite_max += p
    return (sc.scalar(finite_min, unit=x.unit), sc.scalar(finite_max, unit=x.unit))


def fix_empty_range(
    lims: Tuple[sc.Variable, sc.Variable]
) -> Tuple[sc.Variable, sc.Variable]:
    """
    Range correction in case xmin == xmax
    """
    if lims[0].value != lims[1].value:
        return lims
    if lims[0].value == 0.0:
        dx = sc.scalar(0.5, unit=lims[0].unit)
    else:
        # We decompose value and unit to avoid operation exceptions when unit is None.
        dx = sc.scalar(0.5 * abs(lims[0].value), unit=lims[0].unit)
    return (lims[0] - dx, lims[1] + dx)
