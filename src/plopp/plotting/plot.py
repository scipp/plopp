# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Literal

import scipp as sc

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import input_to_nodes, preprocess, raise_multiple_inputs_for_2d_plot_error


def categorize_args(
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    cbar: bool = True,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_color: str = 'black',
    nan_color: str | None = None,
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
) -> dict:
    common_args = {
        'aspect': aspect,
        'autoscale': autoscale,
        'figsize': figsize,
        'grid': grid,
        'logx': logx,
        'logy': logy,
        'norm': norm,
        'scale': scale,
        'title': title,
        'vmax': vmax,
        'vmin': vmin,
        'xlabel': xlabel,
        'xmax': xmax,
        'xmin': xmin,
        'ylabel': ylabel,
        'ymax': ymax,
        'ymin': ymin,
        **kwargs,
    }
    return {
        "1d": {
            'errorbars': errorbars,
            'mask_color': mask_color,
            'legend': legend,
            **common_args,
        },
        "2d": {
            'cbar': cbar,
            'cmap': cmap,
            'cmin': cmin,
            'cmax': cmax,
            'clabel': clabel,
            'logc': logc,
            'nan_color': nan_color,
            **common_args,
        },
    }


def plot(
    obj: PlottableMulti,
    *,
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    cbar: bool = True,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    coords: list[str] | None = None,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    ignore_size: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_color: str = 'black',
    nan_color: str | None = None,
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
    """Plot a Scipp object.

    Parameters
    ----------
    obj:
        The object to be plotted.
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes/colormap on updates if ``True``.
    cbar:
        Show colorbar in 2d plots if ``True``.
    clabel:
        Label for colorscale (2d plots only).
    cmap:
        The colormap to be used for the colorscale (2d plots only).
    cmax:
        Upper limit for colorscale (2d plots only).
    cmin:
        Lower limit for colorscale (2d plots only).
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
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
    logc:
        If ``True``, use logarithmic scale for colorscale (2d plots only).
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    mask_color:
        Color of masks in 1d plots.
    nan_color:
        Color to use for NaN values in 2d plots.
    norm:
        Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots). Legacy, prefer ``logy`` and ``logc`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'time': 'log'}`` if you want log-scale for the ``time`` dimension.
        Legacy, prefer ``logx`` and ``logy`` instead.
    title:
        The figure title.
    vmax:
        Upper limit for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymax`` and ``cmax`` instead.
    vmin:
        Lower limit for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymin`` and ``cmin`` instead.
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
        All other kwargs are forwarded to the underlying plotting library.

    Returns
    -------
    :
        A figure.
    """

    args = categorize_args(
        aspect=aspect,
        autoscale=autoscale,
        cbar=cbar,
        clabel=clabel,
        cmap=cmap,
        cmax=cmax,
        cmin=cmin,
        errorbars=errorbars,
        figsize=figsize,
        grid=grid,
        legend=legend,
        logc=logc,
        logx=logx,
        logy=logy,
        mask_color=mask_color,
        nan_color=nan_color,
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

    nodes = input_to_nodes(
        obj, processor=partial(preprocess, ignore_size=ignore_size, coords=coords)
    )

    ndims = set()
    for n in nodes:
        ndims.add(n().ndim)
    if len(ndims) > 1:
        raise ValueError(
            'All items given to the plot function must have the same '
            f'number of dimensions. Found dimensions {ndims}.'
        )
    ndim = ndims.pop()
    if ndim == 1:
        return linefigure(*nodes, **args['1d'])
    elif ndim == 2:
        if len(nodes) > 1:
            raise_multiple_inputs_for_2d_plot_error(origin='plot')
        return imagefigure(*nodes, **args['2d'])
    else:
        raise ValueError(
            'The plot function can only plot 1d and 2d data, got input '
            f'with {ndim} dimensions'
        )
