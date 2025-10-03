# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc

from ..core.typing import FigureLike, Plottable
from .slicer import Slicer


def superplot(
    obj: Plottable,
    keep: str | None = None,
    *,
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    coords: list[str] | None = None,
    enable_player: bool = False,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    legend: bool | tuple[float, float] = True,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_color: str = 'black',
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
    Plot a multi-dimensional object as a one-dimensional line, slicing all but one
    dimension. This will produce one slider per sliced dimension, below the figure.
    In addition, a tool for saving the currently displayed line is added on the right
    hand side of the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The single dimension to be kept, all remaining dimensions will be sliced.
        This should be a single string. If no dim is provided, the last/inner dim will
        be kept.
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes/colormap if ``True``.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    enable_player:
        If ``True``, add a play button to the sliders to automatically step through
        the slices.
    errorbars:
        Show errorbars in 1d plots if ``True``.
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    mask_color:
        Color of masks in 1d plots.
    norm:
        Set to ``'log'`` for a logarithmic y-axis. Legacy, prefer ``logy`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
        Legacy, prefer ``logx`` instead.
    title:
        The figure title.
    vmax:
        Upper bound for data to be displayed (y-axis). Legacy, prefer ``ymax`` instead.
    vmin:
        Lower bound for data to be displayed (y-axis). Legacy, prefer ``ymin`` instead.
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
        Additional arguments forwarded to the underlying plotting library.

    Returns
    -------
    :
        A :class:`widgets.Box` which will contain a :class:`graphics.FigLine`, slider
        widgets and a tool to save/delete lines.
    """
    from ..widgets import LineSaveTool

    slicer = Slicer(
        obj,
        keep=keep,
        aspect=aspect,
        autoscale=autoscale,
        coords=coords,
        enable_player=enable_player,
        errorbars=errorbars,
        figsize=figsize,
        grid=grid,
        legend=legend,
        logx=logx,
        logy=logy,
        mask_color=mask_color,
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
    slicer.figure.right_bar.add(
        LineSaveTool(
            data_node=slicer.slice_nodes[0],
            slider_node=slicer.slider_node,
            fig=slicer.figure,
        )
    )
    return slicer.figure
