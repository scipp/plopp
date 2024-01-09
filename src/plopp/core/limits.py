# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Tuple, Union

import numpy as np
from scipp import DataArray, Variable, scalar, stddevs

from .utils import merge_masks


def find_limits(
    x: Union[Variable, DataArray], scale: Literal['linear', 'log'] = 'linear'
) -> Tuple[Variable, ...]:
    """
    Find sensible limits, depending on linear or log scale.
    If there are no finite values in the array, raise an error.
    If there are no positive values in the array, and the scale is log, fall back to
    some sensible default values.
    """
    m = np.ones_like(x.values, dtype='bool')
    if isinstance(x, DataArray) and len(x.masks):
        m &= ~merge_masks(x.masks).values
    if not np.any(m):
        m = np.ones_like(x.values, dtype='bool')

    v = x.values[m]
    s = (
        stddevs(x).values
        if x.variances is not None
        else np.zeros_like(x.values, dtype='bool')
    )[m]
    v = np.concatenate((v, v - s, v + s))

    v = v[np.isfinite(v)]
    if len(v) == 0:
        raise ValueError("No finite values were found in array. Cannot compute limits.")
    finite_max = None
    if scale == "log":
        if not np.any(v > 0):
            finite_min = 0.1
            finite_max = 1.0
        else:
            initial = (np.finfo if v.dtype.kind == 'f' else np.iinfo)(v.dtype).max
            finite_min = np.amin(v, initial=initial, where=v > 0)
    else:
        finite_min = np.amin(v)
    if finite_max is None:
        finite_max = np.amax(v)
    print(finite_min, finite_max)
    return (scalar(finite_min, unit=x.unit), scalar(finite_max, unit=x.unit))


def fix_empty_range(lims: Tuple[Variable, Variable]) -> Tuple[Variable, Variable]:
    """
    Range correction in case xmin == xmax
    """
    if lims[0].value != lims[1].value:
        return lims
    if lims[0].value == 0.0:
        dx = scalar(0.5, unit=lims[0].unit)
    else:
        # We decompose value and unit to avoid operation exceptions when unit is None.
        dx = scalar(0.5 * abs(lims[0].value), unit=lims[0].unit)
    return (lims[0] - dx, lims[1] + dx)
