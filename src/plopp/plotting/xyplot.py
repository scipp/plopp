# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import scipp as sc

from .common import to_variable
from ..core import Node
from ..graphics import figure1d


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
    x = Node(to_variable, x)
    y = Node(to_variable, y)
    dim = x().dim
    if dim != y().dim:
        raise sc.DimensionError(f"Dimensions of x and y must match")
    da = Node(lambda x, y: sc.DataArray(data=y, coords={dim: x}), x=x, y=y)
    da.name = 'Make DataArray'
    return figure1d(da, **kwargs)
