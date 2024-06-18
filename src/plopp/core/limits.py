# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

import numpy as np
import scipp as sc

from .utils import merge_masks


def find_limits(
    x: sc.DataArray,
    scale: Literal['linear', 'log'] = 'linear',
    pad: bool = False,
) -> tuple[sc.Variable, sc.Variable]:
    """
    Find sensible limits, depending on linear or log scale.
    If there are no finite values in the array, raise an error.
    If there are no positive values in the array, and the scale is log, fall back to
    some sensible default values.
    """
    is_datetime = x.dtype == sc.DType.datetime64
    # Computing limits for string arrays is not supported, so we convert them to
    # dummy numerical arrays.
    if x.dtype == sc.DType.string:
        x = x.copy(deep=False)
        x.data = sc.arange(x.dim, float(len(x)), unit=x.unit)
    if x.masks:
        x = sc.where(
            merge_masks(x.masks),
            sc.scalar(np.nan, unit=x.unit),
            x.data.to(dtype='float64'),
        )
    v = x.values
    finite_inds = np.isfinite(v)
    if np.sum(finite_inds) == 0:
        raise ValueError("No finite values were found in array. Cannot compute limits.")
    finite_vals = v[finite_inds]
    finite_max = None
    if scale == "log":
        if is_datetime:
            finite_min = np.amin(finite_vals)
        else:
            positives = finite_vals > 0
            if np.sum(positives) == 0:
                finite_min = 0.1
                finite_max = 1.0
            else:
                initial = (np.finfo if v.dtype.kind == 'f' else np.iinfo)(v.dtype).max
                finite_min = np.amin(
                    finite_vals, initial=initial, where=finite_vals > 0
                )
    else:
        finite_min = np.amin(finite_vals)
    if finite_max is None:
        finite_max = np.amax(finite_vals)
    if pad:
        delta = 0.05
        if (scale == 'log') and (not is_datetime):
            p = (finite_max / finite_min) ** delta
            finite_min /= p
            finite_max *= p
        if scale == 'linear':
            p = (finite_max - finite_min) * delta
            finite_min -= p
            finite_max += p
    return (sc.scalar(finite_min, unit=x.unit), sc.scalar(finite_max, unit=x.unit))


def fix_empty_range(
    lims: tuple[sc.Variable, sc.Variable],
) -> tuple[sc.Variable, sc.Variable]:
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
