# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

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
    if x.ndim != 1 or y.ndim != 1:
        raise sc.DimensionError(
            f'Expected 1 dimension, got {x.ndim} for x and {y.ndim} for y.'
        )
    dim = x.dim
    return sc.DataArray(
        data=sc.array(dims=[dim], values=y.values, variances=y.variances, unit=y.unit)
        if y.dim != dim
        else y,
        coords={dim: x},
    )


def xyplot(
    x: sc.Variable | ndarray | list | Node,
    y: sc.Variable | ndarray | list | Node,
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    ignore_size: bool = False,
    legend: bool | tuple[float, float] = True,
    logx: bool | None = None,
    logy: bool | None = None,
    norm: Literal['linear', 'log', None] = None,
    scale: dict[str, str] | None = None,
    title: str | None = None,
    vmax: sc.Variable | float | None = None,
    vmin: sc.Variable | float | None = None,
    xlabel: str | None = None,
    xmax: sc.Variable | float | None = None,
    xmin: sc.Variable | float | None = None,
    ylabel: str | None = None,
    ymax: sc.Variable | float | None = None,
    ymin: sc.Variable | float | None = None,
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
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes on updates if ``True``.
    errorbars:
        Show errorbars in 1d plots if ``True``.
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    ignore_size:
        If ``True``, skip the check that prevents the rendering of very large data.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    norm:
        Set to ``'log'`` for a logarithmic y-axis. Legacy, prefer ``logy`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'time': 'log'}`` if you want log-scale for the ``time`` dimension.
        Legacy, prefer ``logx`` instead.
    title:
        The figure title.
    vmax:
        Upper limit for data to be displayed (y-axis). Legacy, prefer ``ymax`` instead.
    vmin:
        Lower limit for data to be displayed (y-axis). Legacy, prefer ``ymin`` instead.
    xlabel:
        Label for x-axis.
    xmax:
        Upper limit for x-axis.
    xmin:
        Lower limit for x-axis.
    ylabel:
        Label for y-axis.
    ymax:
        Upper limit for y-axis.
    ymin:
        Lower limit for y-axis.
    **kwargs:
        All other kwargs are forwarded the underlying plotting library.
    """
    x = Node(to_variable, x)
    y = Node(to_variable, y)
    return linefigure(
        Node(_make_data_array, x=x, y=y),
        aspect=aspect,
        autoscale=autoscale,
        errorbars=errorbars,
        figsize=figsize,
        grid=grid,
        ignore_size=ignore_size,
        legend=legend,
        logx=logx,
        logy=logy,
        norm=norm,
        scale=scale,
        title=title,
        vmax=vmax,
        vmin=vmin,
        xlabel=xlabel,
        xmax=xmax,
        xmin=xmin,
        ylabel=ylabel,
        ymax=ymax,
        ymin=ymin,
        **kwargs,
    )
