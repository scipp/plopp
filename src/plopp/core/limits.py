# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Tuple

import numpy as np
from scipp import Variable, scalar


def find_limits(x: Variable,
                scale: Literal['linear', 'log'] = 'linear') -> Tuple[Variable, ...]:
    """
    Find sensible limits, depending on linear or log scale.
    If there are no finite values in the array, return NaN for both min and max values.
    """
    v = x.values
    finite_inds = np.isfinite(v)
    if np.sum(finite_inds) == 0:
        raise ValueError("No finite values were found in array. Cannot compute limits.")
    finite_vals = v[finite_inds]
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
    return (lims[0] - dx, lims[1] + dx)
