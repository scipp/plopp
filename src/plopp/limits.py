# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from scipp import scalar, Variable, log10, DType
import numpy as np
from typing import Tuple


def find_limits(x: Variable, scale: str = "linear") -> Tuple[Variable, ...]:
    """
    Find sensible limits, depending on linear or log scale.
    """
    v = x.values
    finite_vals = v[np.isfinite(v)]
    if scale == "log":
        finite_min = np.amin(finite_vals, initial=np.inf, where=finite_vals > 0)
    else:
        finite_min = np.amin(finite_vals)
    finite_max = np.amax(finite_vals)
    return (scalar(finite_min, unit=x.unit), scalar(finite_max, unit=x.unit))


def fix_empty_range(lims: Tuple[Variable, ...]) -> Tuple[Variable, ...]:
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
    return [lims[0] - dx, lims[1] + dx]


def delta(low, high, dx, scale):
    """
    Compute fractional delta from low and high value, using linear or log scaling.
    """
    if scale == "log":
        out = 10**(dx * log10(high / low))
    else:
        out = dx * (high - low)
    if low.dtype == DType.datetime64:
        out = scalar(np.int64(out.value), unit=out.unit)
    return out
