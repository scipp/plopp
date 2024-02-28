# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple

import numpy as np
import scipp as sc

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import merge_masks


def _none_min(*args: float) -> float:
    return min(x for x in args if x is not None)


def _none_max(*args: float) -> float:
    return max(x for x in args if x is not None)


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
            xmin=_none_min(self.xmin, other.xmin),
            xmax=_none_max(self.xmax, other.xmax),
            ymin=_none_min(self.ymin, other.ymin),
            ymax=_none_max(self.ymax, other.ymax),
        )


def axis_bounds(
    keys: Tuple[str, str],
    x: sc.DataArray,
    scale: Literal['linear', 'log'],
    pad=False,
) -> Dict[str, float]:
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
    bounds = {k: v for k, v in zip(keys, (val.value for val in values))}
    return bounds


def make_line_data(data: sc.DataArray, dim: str) -> dict:
    """
    Prepare data for plotting a line.
    This includes extracting the x and y values, and optionally the error bars and masks
    from the data array.
    This also handles the case where the data array is a histogram, in which case the
    first bin edge is repeated.

    Parameters
    ----------
    data:
        The data array to extract values from.
    dim:
        The dimension along which to extract values.
    """
    x = data.coords[dim]
    y = data.data
    hist = len(x) != len(y)
    error = None
    mask = {'x': x.values, 'y': np.full(y.shape, np.nan), 'visible': False}
    if data.variances is not None:
        error = {
            'x': sc.midpoints(x).values if hist else x.values,
            'y': y.values,
            'e': sc.stddevs(y).values,
        }
    if len(data.masks):
        one_mask = merge_masks(data.masks).values
        mask = {
            'x': x.values,
            'y': np.where(one_mask, y.values, np.nan),
            'visible': True,
        }
    if hist:
        y = sc.concat([y[0:1], y], dim=dim)
        if mask is not None:
            mask['y'] = np.concatenate([mask['y'][0:1], mask['y']])
    return {
        'values': {'x': x.values, 'y': y.values},
        'stddevs': error,
        'mask': mask,
        'hist': hist,
    }
