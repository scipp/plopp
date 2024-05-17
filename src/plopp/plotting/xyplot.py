# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


import scipp as sc
from numpy import ndarray

from ..core import Node
from ..core.typing import FigureLike
from ..graphics import linefigure
from .common import to_variable


def _make_data_array(x: sc.Variable, y: sc.Variable) -> sc.DataArray:
    """
    Make a data array from the supplied variables, using ``x`` as the coordinate and
    ``y`` as the data.

    Parameters
    ----------
    x:
        The variable to use as the coordinate.
    y:
        The variable to use as the data.
    """
    return sc.DataArray(data=y, coords={x.dim: x})


def xyplot(
    x: sc.Variable | ndarray | list | Node,
    y: sc.Variable | ndarray | list | Node,
    **kwargs,
) -> FigureLike:
    """
    Make a one-dimensional plot of one variable ``y`` as a function of another ``x``.

    .. versionadded:: 23.10.0

    Parameters
    ----------
    x:
        The variable to use as the coordinates for the horizontal axis.
        Must be one-dimensional.
    y:
        The variable to use as the data for the vertical axis. Must be one-dimensional.
    **kwargs:
        See :py:func:`plopp.plot`.
    """
    x = Node(to_variable, x)
    y = Node(to_variable, y)
    dim = x().dim
    if dim != y().dim:
        raise sc.DimensionError("Dimensions of x and y must match")
    return linefigure(Node(_make_data_array, x=x, y=y), **kwargs)
