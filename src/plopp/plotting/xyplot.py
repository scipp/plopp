# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Union

import scipp as sc
from numpy import ndarray

from ..core import Node
from ..graphics import figure1d
from .common import to_variable


def xyplot(
    x: Union[sc.Variable, ndarray, list, Node],
    y: Union[sc.Variable, ndarray, list, Node],
    **kwargs,
):
    """
    Make a one-dimensional plot of one variable ``y`` as a function of another ``x``.

    .. versionadded:: <TODO:VERSION>

    Parameters
    ----------
    x:
        The variable to use as the coordinates for the horizontal axis. Must be one-dimensional.
    y:
        The variable to use as the data for the vertical axis. Must be one-dimensional.
    **kwargs:
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
