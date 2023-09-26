# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import scipp as sc

from .common import to_variable
from .plot import plot


def xyplot(x: sc.Variable, y: sc.Variable, **kwargs):
    """
    Make a one-dimensional plot of one variable ``y`` as a function of another ``x``.

    .. versionadded:: <TODO:VERSION>

    Parameters
    ----------
    x:
        The variable to use as the coordinates for the horizontal axis.
    y:
        The variable to use as the data for the vertical axis.
    **kwargs
        See :py:func:`plopp.plot`.
    """
    x = to_variable(x)
    y = to_variable(y)
    if x.dim != y.dim:
        raise sc.DimensionError(f"Dimensions of x ({x.dim}) and y ({y.dim}) must match")
    da = sc.DataArray(data=y, coords={x.dim: x})
    return plot(da, **kwargs)
